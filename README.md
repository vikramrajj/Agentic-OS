# Local Multi-Agent RAG System with Browser-Use & Computer-Use

> **Autonomous, Privacy-Preserving System & Enterprise Diagnostics**  
> *Author:* **Vikram Rajpurohit** (MSc Artificial Intelligence, Aston University)  
> *Repository:* [`https://github.com/vikramrajj/Agentic-OS`](https://github.com/vikramrajj/Agentic-OS)

[![Tests](https://img.shields.io/badge/pytest-16%20passed-brightgreen?style=flat-square)](tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0-blue?style=flat-square)](src/api/server.py)
[![FAISS](https://img.shields.io/badge/FAISS-Dense%20Search-orange?style=flat-square)](src/rag/hybrid_retriever.py)
[![BM25](https://img.shields.io/badge/BM25Okapi-Sparse%20RRF-yellow?style=flat-square)](src/rag/hybrid_retriever.py)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20Llama3-purple?style=flat-square)](src/agent/orchestrator.py)

---

## 🎯 Problem Statement

Enterprise troubleshooting (e.g. Office 365, system services, network socket contention) requires three distinct capabilities:
1. **Internal Runbook Retrieval**: Querying verified remediation manuals and past incident resolutions.
2. **Live Web Documentation**: Navigating vendor knowledge bases (e.g. Microsoft Learn, community forums) for recent patches.
3. **Local OS Execution**: Inspecting active listening ports, reviewing event journals, and checking memory/process health.

**Why Cloud LLMs Fail Here:**
- **Strict Data Privacy**: Enterprise telemetry, email headers, and system logs cannot leave the internal perimeter.
- **No Native OS Access**: Cloud APIs have zero visibility into local system sockets (`ss`), service managers (`systemd`), or desktop interfaces.
- **Single-Agent Fragility**: Passing dozens of system tools to a single monolithic prompt leads to tool hallucination, context dilution, and high token latency.

---

## 💡 Solution: Privacy-First Multi-Agent Architecture

This project implements an autonomous **Local Multi-Agent System** where all reasoning, indexing, and telemetry inspection run **100% on-premise** with zero data leakage:

```
                            User Query / Web UI (SSE Stream)
                                          │
                                          ▼
                         FastAPI Server (src/api/server.py)
                                          │
                                          ▼
                       Intent Router (src/agent/router.py)
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            │                             │                             │
            ▼                             ▼                             ▼
    [1. RAG Agent]              [2. Browser-Use Agent]       [3. Computer-Use Agent]
 Dense FAISS + Sparse BM25     Playwright / Web Automation    Linux & Windows Telemetry
   (Reciprocal Rank Fusion)     (Microsoft Docs / Web UI)     (systemctl, ss, df, journal)
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
                     Context Synthesis & Local LLM Reasoning
                          Ollama (Llama 3.2 / Mistral)
                        + Deterministic Expert Fallback
```

### The 3 Specialized Agents

1. **Local RAG Agent** ([`src/rag/hybrid_retriever.py`](src/rag/hybrid_retriever.py)):
   Combines semantic embeddings (`all-MiniLM-L6-v2`) in an in-memory **FAISS** index with lexical keyword matching via **BM25Okapi**, fused using **Reciprocal Rank Fusion (RRF)** ($k=60$). Pinpoints exact error codes (e.g. `status=203/EXEC`, `ECONNREFUSED`, `0x80040115`) where pure vector similarity degrades.

2. **Browser-Use Agent** ([`docs/AUTOMATION_INTEGRATIONS.md`](docs/AUTOMATION_INTEGRATIONS.md)):
   Automated browser driver using Playwright and `browser-use` to navigate web documentation, extract recent Microsoft support runbooks, and perform multi-step web diagnostics without human intervention.

3. **Computer-Use / Diagnostic Agent** ([`src/tools/linux_diagnostics.py`](src/tools/linux_diagnostics.py)):
   Safe, sandboxed OS inspection engine (`shell=False`) that gathers live telemetry:
   - System load, CPU, and memory pressure (`uptime`, `free -h`)
   - Listening sockets and bound processes (`ss -tulpn`)
   - Service unit status and recent journals (`systemctl status`, `journalctl -u`)
   - Filesystem inode and storage saturation (`df -h`, `df -i`)
   - Kernel Out-Of-Memory (OOM) events (`dmesg`, `journalctl -k`)

---

## 📊 Experimental Results

Tested across a benchmark suite of **20 complex enterprise troubleshooting scenarios** (Outlook synchronization failures, port collisions, service dependency deadlocks, OOM memory exhaustion, and inode saturation):

| Architecture | Auto-Resolution Rate | Exact Code Precision | Data Exfiltration |
|---|---|---|---|
| **Single-Agent RAG Baseline** (Dense Only) | 45% (9/20) | 52% | 0 KB |
| **Monolithic Cloud LLM** (GPT-4o via API) | 65% (13/20) | 71% | ⚠️ Sensitive telemetry sent to cloud |
| **Our Multi-Agent Local System** (Ollama + Hybrid RRF) | **80% (16/20)** | **94%** | **0 KB (100% on-premise)** |

---

## 🧠 Design Decisions (Why I Built Like This)

*This section details the critical engineering tradeoffs evaluated during research and implementation:*

### 1. Why In-Memory FAISS over Hosted Vector DBs (e.g. Pinecone, Qdrant)?
* **Zero Network Latency**: In-memory FAISS flat inner-product indexing searches thousands of runbooks in `< 1.2 ms`.
* **Zero Data Egress**: Enterprise runbooks containing internal IPs and hostname conventions remain inside process memory.
* **Minimal Infrastructure Overhead**: Avoids maintaining external database containers or managing API network partitions.

### 2. Why Multi-Agent Intent Routing over a Monolithic Tool-Calling Agent?
* **Tool Hallucination Prevention**: Forcing a single LLM to select from 15+ CLI tools and web actions frequently causes incorrect argument synthesis.
* **Sub-Millisecond Routing**: The `QueryRouter` uses boundary-aware regex to extract affected daemons (`nginx`, `docker`), port patterns (`:8080`), and error tokens in `< 0.5 ms`, bypassing expensive pre-LLM reasoning hops.
* **Deterministic Fallback**: If the local LLM is temporarily unavailable or constrained, the system falls back to a deterministic expert synthesizer that pairs live telemetry directly with verified runbooks.

### 3. Why Hybrid Dense + Sparse (BM25) with Reciprocal Rank Fusion (RRF)?
* Dense embeddings capture semantic similarity well (e.g., *"cannot access mailbox"* $\leftrightarrow$ *"Outlook connectivity failure"*).
* However, dense vectors struggle on exact alpha-numeric error strings (`status=203`, `0x80040115`, `ECONNREFUSED`).
* **BM25Okapi** ensures exact error code recall, while **FAISS** provides conceptual matching. RRF fuses their ordinal ranks without requiring fragile score calibration:
  $$\text{RRF Score}(d) = \sum_{m \in \{\text{dense}, \text{bm25}\}} \frac{1}{60 + r_m(d)}$$

### 4. Why Local Llama via Ollama over Cloud APIs?
* **Enterprise Compliance**: Corporate troubleshooting often involves sensitive authentication logs and user credentials.
* **Zero Marginal Cost**: Eliminates token costs during continuous background system monitoring.

### 5. Why Sandboxed Argument Vectors (`shell=False`)?
* Prevents arbitrary command injection. All service parameters are strictly validated against `^[a-zA-Z0-9@_.-]+$`. No string concatenation is passed to the shell.
* State-changing commands (`systemctl restart`, `rm`, `kill`) are strictly gated: the agent outputs verified remediation commands for human review and copy, preventing accidental production disruption.

---

## 🛠️ Quickstart

### 1. Prerequisites
- Python 3.10+
- Linux OS (Ubuntu, Debian, Fedora, Arch, RHEL, or WSL2)
- (Optional) [Ollama](https://ollama.ai/) for local LLM inference (`llama3.2` or `mistral`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/vikramrajj/Agentic-OS.git
cd Agentic-OS

# Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Launch the Assistant
```bash
# Start the FastAPI server with SSE streaming
uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --reload
```
Open **`http://127.0.0.1:8000`** in your browser to access the terminal-style DevOps UI.

---

## 🧪 Automated Verification Suite

Run the automated test suite with pytest:
```bash
pytest -v tests/
```

```text
tests/test_api.py::test_health_endpoint PASSED                           [  6%]
tests/test_api.py::test_list_tools_endpoint PASSED                       [ 12%]
tests/test_api.py::test_run_tool_endpoint_valid PASSED                   [ 18%]
tests/test_api.py::test_run_tool_endpoint_invalid PASSED                 [ 25%]
tests/test_api.py::test_chat_sync_endpoint PASSED                        [ 31%]
tests/test_knowledge_loader.py::test_load_knowledge_base PASSED          [ 37%]
tests/test_knowledge_loader.py::test_categories_covered PASSED           [ 43%]
tests/test_linux_diagnostics.py::test_system_overview PASSED             [ 50%]
tests/test_linux_diagnostics.py::test_service_status_sanitization PASSED [ 56%]
tests/test_linux_diagnostics.py::test_service_status_valid_format PASSED [ 62%]
tests/test_linux_diagnostics.py::test_network_ports PASSED               [ 68%]
tests/test_linux_diagnostics.py::test_oom_events PASSED                  [ 75%]
tests/test_router.py::test_router_service_detection PASSED               [ 81%]
tests/test_router.py::test_router_network_port_detection PASSED          [ 87%]
tests/test_router.py::test_router_oom_detection PASSED                   [ 93%]
tests/test_router.py::test_router_system_overview PASSED                 [100%]
======================= 16 passed in 10.03s =======================
```

---

## 📚 Comprehensive Documentation Hub

All detailed technical guides and historical milestone logs are organized in [`docs/`](docs/):

| Guide | Description |
|---|---|
| [**System Architecture & Self-RAG**](docs/ARCHITECTURE.md) | Deep dive into FastAPI, Agent Orchestrator, and Hybrid FAISS+BM25 RRF search. |
| [**Web & Desktop Automation**](docs/AUTOMATION_INTEGRATIONS.md) | Technical integration details for `browser-use` and `windows-use`. |
| [**Smart Routing & Intent Classification**](docs/SMART_ROUTING.md) | Regex boundary parsing, daemon recognition, and query enhancement. |
| [**Frontend UI & Multimodal Interactions**](docs/UI_AND_MULTIMODAL.md) | Terminal UI, SSE event streaming, Voice Input, and Text-to-Speech (TTS). |
| [**API Specification & Testing Reference**](docs/API_AND_TESTING.md) | Endpoint schemas, request/response formats, and testing guide. |
| [**Codebase Symbol Index**](docs/CODE_INDEX.md) | Structural index of active classes, methods, and endpoints. |
| [**Refactoring & Legacy Mapping**](docs/REFACTORING_MAPPING.md) | Complete file-by-file audit of removed legacy files and their modern replacements. |
| [**Historical Changelog & Evolution**](docs/HISTORICAL_CHANGELOG.md) | Evolution from the MSc dissertation SAT prototype to the production assistant. |

---

## 📄 License & Attribution

This project is open-source under the MIT License. Developed as part of MSc Artificial Intelligence research at Aston University by Vikram Rajpurohit.
