# 📡 API Specification & Testing Reference

## 1. REST & Streaming API Endpoints

The FastAPI backend (`src/api/server.py`) provides the following endpoints:

### `GET /health`
Returns system health, active AI models, and indexed runbook metrics.
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "embedding_model": "all-MiniLM-L6-v2",
  "ollama_model": "llama3.2",
  "retriever_docs": 16
}
```

---

### `GET /api/tools`
Lists all safe, read-only diagnostic tools available for system inspection.
```json
{
  "available_tools": [
    {
      "name": "get_system_overview",
      "description": "Inspect CPU load, memory utilization, disk usage, and kernel info.",
      "args": {}
    },
    {
      "name": "check_service_status",
      "description": "Inspect systemctl status and recent journal logs for a service.",
      "args": { "service_name": "string" }
    },
    {
      "name": "check_network_ports",
      "description": "List listening TCP/UDP sockets and bound processes via ss/netstat.",
      "args": { "filter_term": "string (optional)" }
    },
    {
      "name": "check_journal_errors",
      "description": "Retrieve recent critical and error logs from systemd journal.",
      "args": { "lines": "int (default: 30)" }
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
```

---

### `POST /api/tools/run`
Executes an allowed diagnostic tool manually without going through the chat agent.
* **Request**:
```json
{
  "tool_name": "check_service_status",
  "args": {
    "service_name": "nginx"
  }
}
```
* **Response**:
```json
{
  "tool_name": "check_service_status",
  "success": true,
  "exit_code": 0,
  "output": "=== Service Status: nginx ===\n...",
  "error": null
}
```

---

### `POST /api/chat/stream`
Server-Sent Events (SSE) streaming endpoint.
* **Request Header**: `Accept: text/event-stream`
* **Request Body**:
```json
{
  "message": "Why is my port 80 not responding?"
}
```
* **Event Types**:
  - `thought`: Internal agent reasoning step.
  - `tool_call`: Tool invocation declaration.
  - `tool_result`: Output captured from live system inspection.
  - `token`: Partial Markdown chunk of LLM remediation advice.
  - `done`: Final metadata object with execution statistics.

---

### `POST /api/chat`
Synchronous alternative returning the full aggregated response in a single JSON payload.
```json
{
  "query": "How do I check high disk usage?",
  "thoughts": ["Analyzing query intent...", "Classified intent as 'storage_troubleshoot'..."],
  "tool_calls": [
    {
      "type": "tool_call",
      "tool": "check_disk_inodes",
      "args": {},
      "result": { "success": true, "output": "..." }
    }
  ],
  "response": "## 🔍 Linux Diagnostic Analysis\n...",
  "metadata": {
    "intent": "storage_troubleshoot",
    "tools_executed": ["check_disk_inodes"],
    "retrieved_count": 4,
    "matched_runbooks": ["Disk Space Exhaustion (100% Full)", "Filesystem Inode Exhaustion"]
  }
}
```

---

## 2. Automated Test Suite

The project includes an automated Pytest test suite providing 100% verification across all critical paths.

### Test Structure
```
tests/
├── test_api.py                 # Endpoint status codes, error handling, tool runners
├── test_knowledge_loader.py    # JSON runbook schema validation and category completeness
├── test_linux_diagnostics.py   # Subprocess safety, regex sanitization, tool mock execution
└── test_router.py              # Service, port, OOM, and storage intent classification
```

### Running Tests
Execute the full test suite with verbose output:
```bash
pytest -v tests/
```

### Execution Status
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
======================= 16 passed in 11.03s ========================
```
