# Linux OS Agentic Troubleshooting Assistant 🐧

A production-grade, autonomous **Agentic RAG Assistant** designed for Linux OS administration, DevOps diagnostics, and system troubleshooting. Built with FastAPI, Hybrid Search (Dense FAISS + Sparse BM25 via Reciprocal Rank Fusion), and safe, sandboxed system inspection tools.

---

## 🚀 Key Capabilities

- **Autonomous Self-RAG Workflow**: Dynamically classifies intent, executes safe read-only Linux diagnostic tools, retrieves verified troubleshooting runbooks, and synthesizes step-by-step remediation commands.
- **Safe Read-Only System Inspection**: Inspects live CPU/memory load, systemd service status (`systemctl` / `journalctl`), active port bindings (`ss`), inode capacity (`df -i`), and kernel OOM events without modifying system state.
- **Hybrid Retrieval (Dense + BM25 + RRF)**: Combines semantic vector search (`all-MiniLM-L6-v2`) with sparse keyword matching (`BM25Okapi`) using Reciprocal Rank Fusion (RRF) for pinpoint accuracy on exact error codes (e.g. `status=203/EXEC`, `ECONNREFUSED`, `100%`).
- **Real-Time SSE Streaming**: Streams live agent reasoning thoughts, tool execution cards with stdout/stderr outputs, and markdown token responses via Server-Sent Events.
- **Deterministic Expert Fallback**: Functions flawlessly even if local Ollama or cloud LLMs are offline, synthesizing expert guidance directly from live system telemetry and verified runbooks.
- **Modern DevOps UI**: Dark-mode terminal-inspired web interface with quick-action diagnostic chips and one-click copyable bash commands.

---

## 🏗️ Architecture

```
User / Web UI (SSE Stream)
       │
       ▼
 FastAPI Server (src/api/server.py)
       │
       ▼
 Agent Orchestrator (src/agent/orchestrator.py)
  ├── 1. Intent Router ──► Safe Linux Tools (src/tools/linux_diagnostics.py)
  │                          (systemctl, journalctl, ss, df, free, dmesg)
  │
  ├── 2. Hybrid Retriever ──► Linux Runbook Knowledge Base (src/knowledge/*.json)
  │      ├── Dense Vector Search (FAISS)
  │      └── Sparse Keyword Search (BM25Okapi)
  │            └── Reciprocal Rank Fusion (RRF)
  │
  └── 3. LLM / Fallback Synthesizer
         ├── Ollama Streaming (llama3.2 / mistral / qwen2.5)
         └── Deterministic Telemetry & Runbook Synthesis
```

---

## 📚 Project Documentation

Comprehensive documentation has been consolidated into the [`docs/`](docs/) directory:

- [**System Architecture & Self-RAG**](docs/ARCHITECTURE.md) - Deep dive into FastAPI, Agent Orchestrator, and Hybrid FAISS+BM25 RRF search.
- [**Web & Desktop Automation**](docs/AUTOMATION_INTEGRATIONS.md) - Guides for `browser-use` and `windows-use` integrations with Gemini.
- [**Smart Routing & Intent Classification**](docs/SMART_ROUTING.md) - Query classification, entity extraction, and tool dispatching.
- [**Frontend UI & Multimodal Interactions**](docs/UI_AND_MULTIMODAL.md) - Terminal UI, SSE event streaming, Voice Input, and Text-to-Speech (TTS).
- [**Historical Changelog & Evolution**](docs/HISTORICAL_CHANGELOG.md) - Development roadmap and legacy sprint consolidation.
- [**Codebase Symbol Index**](docs/CODE_INDEX.md) - Structural breakdown of all active classes, methods, and endpoints.
- [**Refactoring & Legacy Mapping**](docs/REFACTORING_MAPPING.md) - Complete file-by-file legacy removal and replacement audit.

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Linux OS (Ubuntu, Debian, Fedora, Arch, RHEL, or WSL2)
- (Optional) [Ollama](https://ollama.ai/) for local LLM inference

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vikramrajj/RAG-Agent.git
   cd "RAG-Agent"
   ```

2. **Create a virtual environment & install dependencies**:
   Using `uv` (recommended, 10x faster):
   ```bash
   uv venv .venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
   Or using standard `python3 -m venv`:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment (Optional)**:
   Create a `.env` file to customize settings:
   ```env
   HOST=127.0.0.1
   PORT=8000
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ALLOW_SYSTEM_INSPECTION=true
   ```

4. **Start the Assistant**:
   ```bash
   uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Open in your browser**:
   Navigate to **http://127.0.0.1:8000** to access the web interface.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status and knowledge base statistics |
| `GET` | `/api/tools` | List all available safe diagnostic tools |
| `POST` | `/api/tools/run` | Execute a specific diagnostic tool manually |
| `POST` | `/api/chat/stream` | Server-Sent Events (SSE) streaming chat endpoint |
| `POST` | `/api/chat` | Non-streaming JSON chat response |

---

## 🧪 Running Tests

Run the automated test suite with pytest:
```bash
pytest -v tests/
```

---

## 📚 Adding Custom Runbooks

You can extend the knowledge base by adding JSON files in `src/knowledge/`:
```json
[
  {
    "id": "my_custom_issue",
    "title": "Custom Service Crash",
    "category": "systemd",
    "symptoms": ["my_service failed"],
    "root_cause": "Detailed explanation of the issue.",
    "diagnostic_steps": ["systemctl status my_service"],
    "remediation_commands": ["sudo systemctl restart my_service"]
  }
]
```
The hybrid retriever automatically indexes all JSON runbooks in `src/knowledge/` on startup.

---

## 🔒 Safety & Security

- **Strictly Read-Only**: The agent executes only safe informational commands (`systemctl status`, `journalctl`, `ss`, `df`, `free`, `dmesg`).
- **No Command Injection**: All system commands use explicit argument vectors with regex sanitization — no shell string interpolation (`shell=False`).
- **User Confirmation**: The agent **never** automatically runs destructive or state-changing commands (`rm`, `kill`, `chmod`, `systemctl restart`). All remediation commands are provided for the user to review and execute.
