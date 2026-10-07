import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.logger import logger
from src.agent.orchestrator import orchestrator
from src.tools.linux_diagnostics import diagnostics
from src.rag.hybrid_retriever import hybrid_retriever

ALLOWED_TOOLS = {
    "get_system_overview",
    "check_service_status",
    "check_network_ports",
    "check_journal_errors",
    "check_disk_inodes",
    "check_oom_events"
}

app = FastAPI(
    title="Linux OS Agentic Troubleshooting Assistant",
    description="Production-grade Agentic RAG assistant for Linux OS diagnostics, systemd, and DevOps troubleshooting.",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).resolve().parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User troubleshooting prompt or query")


class ToolRunRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the safe diagnostic tool")
    args: dict = Field(default_factory=dict, description="Tool keyword arguments")


@app.get("/")
async def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Linux OS Agentic Assistant API running. Static UI not found."}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "embedding_model": settings.embedding_model,
        "ollama_model": settings.ollama_model,
        "retriever_docs": len(hybrid_retriever.docs)
    }


@app.get("/api/tools")
async def list_tools():
    return {
        "available_tools": [
            {
                "name": "get_system_overview",
                "description": "Inspect CPU load, memory utilization, disk usage, and kernel info.",
                "args": {}
            },
            {
                "name": "check_service_status",
                "description": "Inspect systemctl status and recent journal logs for a service.",
                "args": {"service_name": "string"}
            },
            {
                "name": "check_network_ports",
                "description": "List listening TCP/UDP sockets and bound processes via ss/netstat.",
                "args": {"filter_term": "string (optional)"}
            },
            {
                "name": "check_journal_errors",
                "description": "Retrieve recent critical and error logs from systemd journal.",
                "args": {"lines": "int (default: 30)"}
            },
            {
                "name": "check_disk_inodes",
                "description": "Check filesystem inode capacity (df -i) for inode exhaustion.",
                "args": {}
            },
            {
                "name": "check_oom_events",
                "description": "Scan kernel logs and journal for Out Of Memory killer events.",
                "args": {}
            }
        ]
    }


@app.post("/api/tools/run")
async def run_tool(req: ToolRunRequest):
    if req.tool_name not in ALLOWED_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{req.tool_name}' not found or not allowed.")

    tool_fn = getattr(diagnostics, req.tool_name, None)
    if not callable(tool_fn):
        raise HTTPException(status_code=400, detail=f"Tool '{req.tool_name}' is not callable.")

    try:
        result = await asyncio.to_thread(tool_fn, **req.args)
        return {
            "tool_name": result.tool_name,
            "success": result.success,
            "exit_code": result.exit_code,
            "output": result.output,
            "error": result.error
        }
    except Exception as e:
        logger.error(f"Failed to execute tool {req.tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Server-Sent Events (SSE) streaming endpoint for agent thoughts, tool calls, and tokens."""
    async def event_generator():
        try:
            async for event in orchestrator.stream_chat(req.message):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/chat")
async def chat_sync(req: ChatRequest):
    """Non-streaming endpoint aggregating the full agent response."""
    thoughts = []
    tool_calls = []
    tokens = []
    metadata = {}

    async for event in orchestrator.stream_chat(req.message):
        ev_type = event.get("type")
        if ev_type == "thought":
            thoughts.append(event["content"])
        elif ev_type == "tool_call":
            tool_calls.append(event)
        elif ev_type == "tool_result":
            # Attach result to matching call
            if tool_calls:
                tool_calls[-1]["result"] = event
        elif ev_type == "token":
            tokens.append(event["content"])
        elif ev_type == "done":
            metadata = event.get("metadata", {})

    return {
        "query": req.message,
        "thoughts": thoughts,
        "tool_calls": tool_calls,
        "response": "".join(tokens),
        "metadata": metadata
    }
