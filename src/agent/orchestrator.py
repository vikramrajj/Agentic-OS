import asyncio
import json
import httpx
from typing import AsyncGenerator, Any
from src.core.config import settings
from src.core.logger import logger
from src.tools.linux_diagnostics import diagnostics, ToolExecutionResult
from src.rag.hybrid_retriever import hybrid_retriever, RetrievalResult
from src.agent.router import router, RoutingDecision


class AgentOrchestrator:
    """Coordinates Intent Routing, Safe Tool Execution, Hybrid Retrieval, and Synthesis."""

    def __init__(self):
        self.router = router
        self.retriever = hybrid_retriever
        self.diagnostics = diagnostics
        self._http_client: httpx.AsyncClient | None = None

    def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create reusable HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def close(self):
        """Clean up HTTP client resources."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    async def _call_ollama(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        """Stream tokens from local Ollama instance with timeout handling."""
        url = f"{settings.ollama_base_url}/api/generate"
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": 0.2
            }
        }

        client = self._get_http_client()
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                raise RuntimeError(f"Ollama returned status code {response.status_code}")

            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

    def _generate_deterministic_synthesis(
        self,
        query: str,
        tool_results: list[ToolExecutionResult],
        retrieved_docs: list[RetrievalResult]
    ) -> str:
        """Fallback deterministic synthesis if LLM server is offline or unavailable."""
        lines = []

        lines.append("## 🔍 Linux Diagnostic Analysis\n")
        lines.append(f"**Query**: {query}\n")

        # 1. Live telemetry
        if tool_results:
            lines.append("### 📊 Live System Observations\n")
            for tr in tool_results:
                lines.append(f"**Tool: `{tr.tool_name}`** (Exit Code: `{tr.exit_code}`)")
                clean_out = tr.output[:800] if len(tr.output) > 800 else tr.output
                lines.append(f"```text\n{clean_out}\n```\n")

        # 2. Knowledge base findings
        if retrieved_docs:
            top_doc = retrieved_docs[0].doc
            lines.append(f"### 🎯 Root Cause: {top_doc.title}\n")
            lines.append(f"{top_doc.root_cause}\n")

            lines.append("### 🛠️ Recommended Remediation Steps\n")
            for i, cmd in enumerate(top_doc.remediation_commands, 1):
                lines.append(f"{i}. Run the following command:")
                lines.append(f"```bash\n{cmd}\n```")

            lines.append("\n### 🔬 Diagnostic & Verification Steps\n")
            for step in top_doc.diagnostic_steps:
                lines.append(f"- {step}")

        else:
            lines.append("### ℹ️ Analysis\n")
            lines.append("No exact runbook matched. Please review the live system telemetry above to identify the issue.")

        return "\n".join(lines)

    async def stream_chat(self, query: str) -> AsyncGenerator[dict[str, Any], None]:
        """Execute the full Self-RAG loop and yield SSE streaming events."""

        # Step 1: Routing
        yield {
            "type": "thought",
            "content": f"Analyzing query intent and selecting diagnostic tools for: '{query}'..."
        }

        decision: RoutingDecision = self.router.route(query)
        yield {
            "type": "thought",
            "content": f"Classified intent as '{decision.intent}'. Tools to execute: {[t[0] for t in decision.tools_to_run]}"
        }

        # Step 2: Safe Tool Execution
        tool_results: list[ToolExecutionResult] = []
        if settings.allow_system_inspection and decision.tools_to_run:
            for tool_name, kwargs in decision.tools_to_run:
                yield {
                    "type": "tool_call",
                    "tool": tool_name,
                    "args": kwargs
                }

                tool_fn = getattr(self.diagnostics, tool_name, None)
                if tool_fn:
                    try:
                        res: ToolExecutionResult = await asyncio.to_thread(tool_fn, **kwargs)
                        tool_results.append(res)
                        yield {
                            "type": "tool_result",
                            "tool": tool_name,
                            "success": res.success,
                            "exit_code": res.exit_code,
                            "output": res.output[:500] + ("..." if len(res.output) > 500 else "")
                        }
                    except Exception as e:
                        logger.error(f"Error calling tool {tool_name}: {e}")
                        yield {
                            "type": "tool_result",
                            "tool": tool_name,
                            "success": False,
                            "output": str(e)
                        }

        # Step 3: Hybrid Retrieval
        yield {
            "type": "thought",
            "content": f"Retrieving Linux runbooks using Dense + BM25 search for '{decision.search_query}'..."
        }

        retrieved = await asyncio.to_thread(self.retriever.retrieve, decision.search_query, top_k=settings.top_k_retrieval)
        yield {
            "type": "thought",
            "content": f"Retrieved {len(retrieved)} relevant runbooks: {[r.doc.title for r in retrieved]}"
        }

        # Step 4: Context Assembly
        system_prompt = (
            "You are an expert Linux Systems Administrator and DevOps Diagnostic Assistant. "
            "Your job is to analyze system state, explain root causes, and provide exact, safe, copy-pasteable shell commands. "
            "Format your response in clean Markdown with clear headings, bullet points, and code blocks."
        )

        context_parts = []
        if tool_results:
            context_parts.append("=== LIVE SYSTEM OBSERVATIONS ===")
            for tr in tool_results:
                context_parts.append(f"[{tr.tool_name}]:\n{tr.output}")

        if retrieved:
            context_parts.append("\n=== RETRIEVED RUNBOOKS ===")
            for r in retrieved:
                doc = r.doc
                context_parts.append(
                    f"Title: {doc.title}\n"
                    f"Category: {doc.category}\n"
                    f"Symptoms: {', '.join(doc.symptoms)}\n"
                    f"Root Cause: {doc.root_cause}\n"
                    f"Diagnostics: {' '.join(doc.diagnostic_steps)}\n"
                    f"Remediation: {' '.join(doc.remediation_commands)}"
                )

        full_prompt = (
            f"User Problem: {query}\n\n"
            f"{chr(10).join(context_parts)}\n\n"
            "Provide a comprehensive diagnosis. Include: 1) Root Cause, 2) Evidence from Live Telemetry (if available), "
            "3) Step-by-Step Remediation Commands with explanations, 4) Verification Commands."
        )

        # Step 5: Streaming Token Synthesis
        yield {
            "type": "thought",
            "content": "Synthesizing step-by-step diagnostic and remediation response..."
        }

        llm_success = False
        try:
            async for token in self._call_ollama(full_prompt, system_prompt):
                llm_success = True
                yield {
                    "type": "token",
                    "content": token
                }
        except Exception as e:
            logger.warning(f"Ollama generation unavailable or failed: {e}. Falling back to deterministic synthesis.")

        if not llm_success:
            fallback_text = self._generate_deterministic_synthesis(query, tool_results, retrieved)
            for token in fallback_text.split(" "):
                yield {
                    "type": "token",
                    "content": token + " "
                }

        # Step 6: Complete
        yield {
            "type": "done",
            "metadata": {
                "intent": decision.intent,
                "tools_executed": [tr.tool_name for tr in tool_results],
                "retrieved_count": len(retrieved),
                "matched_runbooks": [r.doc.title for r in retrieved]
            }
        }


# Global instance
orchestrator = AgentOrchestrator()
