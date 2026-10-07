# 📚 Project Documentation Hub

Welcome to the centralized documentation hierarchy for the **Agentic RAG Assistant** (formerly known as SAT / Agentic Tech Support). This directory consolidates the knowledge base, implementation guides, integration references, and historical development logs from over 90+ legacy markdown documents into an organized, high-density reference structure.

---

## 🗂️ Documentation Hierarchy

| Document | Topic | Description |
|---|---|---|
| [**`ARCHITECTURE.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/ARCHITECTURE.md) | **System Architecture & Self-RAG** | Core system design, FastAPI service, Agent Orchestrator, Hybrid Retrieval (FAISS + BM25 via Reciprocal Rank Fusion), and safe diagnostic sandbox. |
| [**`AUTOMATION_INTEGRATIONS.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/AUTOMATION_INTEGRATIONS.md) | **Web & Desktop Automation** | Integration guides for Web Automation (`browser-use`), Windows Automation (`windows-use`), Gemini Flash wrappers, and quota management. |
| [**`SMART_ROUTING.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/SMART_ROUTING.md) | **Intent Routing & Dispatch** | Query classification, service extraction (`nginx`, `docker`, `postgres`), port extraction, error pattern detection, and tool dispatching. |
| [**`UI_AND_MULTIMODAL.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/UI_AND_MULTIMODAL.md) | **Frontend & Multimodal Interaction** | Terminal-inspired DevOps web UI, Server-Sent Events (SSE) streaming, real-time thought cards, and Voice Input / Text-to-Speech (TTS). |
| [**`API_AND_TESTING.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/API_AND_TESTING.md) | **API Reference & Verification** | Endpoints (`/api/chat/stream`, `/api/tools/run`, `/health`), request/response schemas, tool arguments, and the automated Pytest test suite. |
| [**`HISTORICAL_CHANGELOG.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/HISTORICAL_CHANGELOG.md) | **Evolution & Sprint History** | Consolidated changelog tracing the project evolution from the MSc Dissertation SAT prototype to the production Linux OS Agentic Assistant. |
| [**`CODE_INDEX.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/CODE_INDEX.md) | **Codebase Index & Symbols** | Exhaustive structural index and symbol breakdown for all active files, modules, classes, and endpoints. |
| [**`REFACTORING_MAPPING.md`**](file:///home/vikram/Documents/VS%20code/Agentic%20RAG%20/docs/REFACTORING_MAPPING.md) | **Refactoring & Legacy Mapping** | Detailed itemized mapping of all removed legacy files (95 markdown, 38 Python, 17 test scripts) and their modern replacements. |

---

## 🧭 Repository Context

* **Primary Repository**: [`https://github.com/vikramrajj/RAG-Agent`](https://github.com/vikramrajj/RAG-Agent) (configured as `origin`)
* **Upstream Base**: [`https://github.com/Aashapura/RAG-Agent`](https://github.com/Aashapura/RAG-Agent) (configured as `upstream`)
* **Core Philosophy**: Autonomous, safe, and verifiable troubleshooting combining dense and sparse retrieval with sandboxed system inspection.
