# 📑 Codebase Index & Symbol Reference

This document provides a comprehensive structural index of all active source files, exported classes, functions, and endpoints in the **Agentic RAG Assistant** codebase.

---

## 🗂️ High-Level Directory Layout

```
.
├── docs/                        # Consolidated documentation hierarchy
│   ├── ARCHITECTURE.md          # System architecture and Self-RAG design
│   ├── AUTOMATION_INTEGRATIONS.md # Web & Desktop automation reference
│   ├── CODE_INDEX.md            # Structural code and symbol index (this file)
│   ├── HISTORICAL_CHANGELOG.md  # Sprint history and evolution
│   ├── README.md                # Documentation hub navigation
│   ├── REFACTORING_MAPPING.md   # Complete legacy removal & replacement mapping
│   ├── SMART_ROUTING.md         # Intent classification & query routing
│   └── UI_AND_MULTIMODAL.md     # UI layout, SSE streaming & voice features
├── src/                         # Core Python application
│   ├── __init__.py
│   ├── agent/                   # Agent routing & orchestration
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Self-RAG execution loop & LLM streaming
│   │   └── router.py            # Intent & entity classification
│   ├── api/                     # FastAPI web service
│   │   ├── __init__.py
│   │   └── server.py            # REST & SSE streaming endpoints
│   ├── core/                    # Core configuration and logging
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings & environment variables
│   │   └── logger.py            # Structured logging setup
│   ├── knowledge/               # JSON troubleshooting runbooks
│   │   ├── memory_disk_issues.json
│   │   ├── network_troubleshooting.json
│   │   ├── permissions_security.json
│   │   └── systemd_services.json
│   ├── rag/                     # Hybrid Dense + Sparse retrieval engine
│   │   ├── __init__.py
│   │   ├── hybrid_retriever.py  # FAISS + BM25Okapi via Reciprocal Rank Fusion
│   │   └── knowledge_loader.py  # JSON runbook loader & RunbookDoc model
│   └── tools/                   # Sandboxed system inspection tools
│       ├── __init__.py
│       └── linux_diagnostics.py # Read-only Linux telemetry collection
├── static/                      # Web UI static assets
│   ├── app.js                   # SSE parser, DOM rendering, Web Speech API
│   ├── index.html               # Terminal dark-mode interface
│   └── style.css                # Monospace DevOps styling
├── tests/                       # Automated Pytest suite
│   ├── __init__.py
│   ├── test_api.py              # API endpoint status & streaming tests
│   ├── test_knowledge_loader.py # Runbook schema & category tests
│   ├── test_linux_diagnostics.py# Sandboxed execution & input sanitization tests
│   └── test_router.py           # Intent routing & entity extraction tests
├── AGENTS.md                    # Agent guidelines & engineering standards
├── pyrightconfig.json           # Type checking configuration
├── pytest.ini                   # Pytest test runner configuration
├── README.md                    # Project README and quickstart
├── requirements.txt             # Production dependencies
└── skills-lock.json             # Agent skills lockfile
```

---

## 🔍 Module & Symbol Details

### 1. Core Subsystem (`src/core/`)

| File | Symbol | Type | Description |
|---|---|---|---|
| [`src/core/config.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/core/config.py) | `Settings` | Class | Pydantic BaseSettings loading `.env` and environment defaults. |
| [`src/core/config.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/core/config.py) | `settings` | Instance | Global application settings singleton. |
| [`src/core/logger.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/core/logger.py) | `setup_logger` | Function | Configures standardized stream logger with timestamp formatting. |
| [`src/core/logger.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/core/logger.py) | `logger` | Instance | Pre-configured application logger instance. |

### 2. Diagnostics & Tools (`src/tools/`)

| File | Symbol | Type | Description |
|---|---|---|---|
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `ToolExecutionResult` | Dataclass | Standardized tool output container (`tool_name`, `success`, `output`, `error`, `exit_code`). |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `LinuxDiagnostics` | Class | Safe, read-only system inspection manager. |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `_run_command` | Method | Executes commands safely with `subprocess.run(shell=False)` and timeout. |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `get_system_overview` | Method | Gathers uptime, CPU load, memory (`free -h`), disk (`df -h`), and kernel info. |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `check_service_status` | Method | Checks `systemctl status` and recent `journalctl` entries with regex sanitization. |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `check_network_ports` | Method | Lists active listening sockets via `ss -tulpn` or `netstat -tuln` with optional filtering. |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `check_journal_errors` | Method | Retrieves recent critical error messages from systemd journal (`journalctl -p err..emerg`). |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `check_disk_inodes` | Method | Audits filesystem inode utilization (`df -i`) to detect inode exhaustion. |
| [`src/tools/linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/tools/linux_diagnostics.py) | `check_oom_events` | Method | Scans kernel buffer and journal for Out Of Memory killer invocations. |

### 3. Knowledge Base & Hybrid Retrieval (`src/rag/`)

| File | Symbol | Type | Description |
|---|---|---|---|
| [`src/rag/knowledge_loader.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/rag/knowledge_loader.py) | `RunbookDoc` | Dataclass | Structured runbook representation with property `searchable_text`. |
| [`src/rag/knowledge_loader.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/rag/knowledge_loader.py) | `load_knowledge_base` | Function | Loads and validates all runbooks from `src/knowledge/*.json`. |
| [`src/rag/hybrid_retriever.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/rag/hybrid_retriever.py) | `RetrievalResult` | Dataclass | Result item with `doc`, `score`, and `matched_by` tag (`dense`, `bm25`, `hybrid`). |
| [`src/rag/hybrid_retriever.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/rag/hybrid_retriever.py) | `HybridRetriever` | Class | Implements Dense FAISS + Sparse BM25 fused via Reciprocal Rank Fusion (RRF). |
| [`src/rag/hybrid_retriever.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/rag/hybrid_retriever.py) | `initialize` | Method | Builds FAISS inner product index and BM25 tokenized corpus. |
| [`src/rag/hybrid_retriever.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/rag/hybrid_retriever.py) | `retrieve` | Method | Ranks documents by RRF score `1 / (60 + rank)` and returns top-k matches. |

### 4. Agent Routing & Orchestration (`src/agent/`)

| File | Symbol | Type | Description |
|---|---|---|---|
| [`src/agent/router.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/router.py) | `RoutingDecision` | Dataclass | Routing metadata container (`intent`, `target_service`, `target_port`, `tools_to_run`, `search_query`). |
| [`src/agent/router.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/router.py) | `QueryRouter` | Class | Pattern-matching classifier for services, ports, and diagnostic categories. |
| [`src/agent/router.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/router.py) | `route` | Method | Categorizes user prompts and builds the diagnostic tool execution plan. |
| [`src/agent/orchestrator.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/orchestrator.py) | `AgentOrchestrator` | Class | Coordinates Intent Routing, Tool Execution, Retrieval, and LLM Synthesis. |
| [`src/agent/orchestrator.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/orchestrator.py) | `stream_chat` | Async Gen | Main Self-RAG loop yielding SSE events (`thought`, `tool_call`, `tool_result`, `token`, `done`). |
| [`src/agent/orchestrator.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/orchestrator.py) | `_call_ollama` | Async Gen | Streams tokens from local Ollama endpoint (`/api/generate`). |
| [`src/agent/orchestrator.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/agent/orchestrator.py) | `_generate_deterministic_synthesis` | Method | High-quality offline fallback synthesizing guidance from telemetry and runbooks. |

### 5. API Layer (`src/api/`)

| File | Symbol | Type | Description |
|---|---|---|---|
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `app` | Instance | FastAPI application instance with CORS middleware and static asset mount. |
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `root` | Endpoint (`GET /`) | Serves `static/index.html`. |
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `health_check` | Endpoint (`GET /health`) | Returns health status, active models, and retriever document count. |
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `list_tools` | Endpoint (`GET /api/tools`) | Returns list and argument schemas of allowed diagnostic tools. |
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `run_tool` | Endpoint (`POST /api/tools/run`) | Directly invokes a safe diagnostic tool via thread pool. |
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `chat_stream` | Endpoint (`POST /api/chat/stream`) | Server-Sent Events (SSE) streaming endpoint for real-time agent output. |
| [`src/api/server.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/src/api/server.py) | `chat_sync` | Endpoint (`POST /api/chat`) | Non-streaming endpoint aggregating full thoughts, tool calls, and response. |

---

## 🧪 Automated Test Suite (`tests/`)

| Test File | Test Functions | Focus Area |
|---|---|---|
| [`tests/test_api.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/tests/test_api.py) | `test_health_endpoint`, `test_list_tools_endpoint`, `test_run_tool_endpoint_valid`, `test_run_tool_endpoint_invalid`, `test_chat_sync_endpoint` | Endpoints response codes, JSON schemas, 404 on disallowed tools, and full chat pipeline. |
| [`tests/test_linux_diagnostics.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/tests/test_linux_diagnostics.py) | `test_system_overview`, `test_service_status_sanitization`, `test_service_status_valid_format`, `test_network_ports`, `test_oom_events` | Subprocess security, rejection of command injection strings (`;`, `\|`, `&`), and safe execution. |
| [`tests/test_router.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/tests/test_router.py) | `test_router_service_detection`, `test_router_network_port_detection`, `test_router_oom_detection`, `test_router_system_overview` | Intent mapping, service name extraction, port parsing, and tool attachment. |
| [`tests/test_knowledge_loader.py`](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/tests/test_knowledge_loader.py) | `test_load_knowledge_base`, `test_categories_covered` | JSON schema validation and coverage across `systemd`, `network`, `memory`, `storage`, and `permissions`. |
