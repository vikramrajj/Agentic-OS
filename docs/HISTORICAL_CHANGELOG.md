# 📜 Historical Changelog & Evolution

This document consolidates the development trajectory, sprint milestones, and bugfix logs previously recorded across 90+ individual markdown files.

---

## 🏛️ Phase 1: Prototype Inception & Academic Research (Sep 2025)

* **Origin**: MSc Dissertation research by **Vikram Rajpurohit** (ID: 240375096) titled:  
  *"Agentic Tech Support LLM: A Screen-Sharing and Feedback-Driven Autonomous Support System"*.
* **Core Proposal**: Combining multimodal perception (screen captures, logs) and autonomous agents to diagnose and resolve software configuration faults.
* **Initial Stack**: Python 3.10+, PyTorch, Flask, LangChain, and FAISS.

---

## 🚀 Phase 2: Feature Expansion & SAT Sprints (Oct 2025)

### Sprint 1: Outlook & Office Diagnostics
- Built FAISS semantic retriever (`rag_loader.py`, `outlook_index.faiss`) for Office 365 troubleshooting.
- Added automated OWA (Outlook Web App) URL generation and issue diagnosis.

### Sprint 2: Web Automation Integration (`browser-use`)
- Integrated `browser-use` library and Gemini 2.0 Flash API (`browser_use_wrapper.py`).
- Added persistent Chrome profile support, natural language web navigation, and automated form interaction.
- Implemented daily API quota tracking to handle free tier limits.

### Sprint 3: Desktop Automation Integration (`windows-use`)
- Integrated `windows-use` library (`windows_use_wrapper.py`) for desktop automation.
- Supported direct invocation of Windows settings, File Explorer, Calculator, and system utilities.

### Sprint 4: Smart Routing & Multi-Model Switching
- Introduced `smart_router.py` to route queries between Web Automation, Desktop Automation, RAG Knowledge Base, and general LLM reasoning.
- Added runtime switching between Mistral, Llama 3, and Gemini.

### Sprint 5: SAT UI Redesign & Multimodal Audio
- Developed modern web interfaces (`sat_ui.html`, `sat_ui_improved.html`) with model selection chips.
- Added browser-native Text-to-Speech (TTS) for voice playback of remediation instructions.
- Implemented Web Speech API voice input for hands-free troubleshooting.

---

## 🐧 Phase 3: Production Linux OS Self-RAG Assistant (Oct 2026)

### Architecture Modernization
- **FastAPI Core**: Replaced legacy Flask server with asynchronous, non-blocking FastAPI backend (`src/api/server.py`).
- **Standardized Directory Layout**: Structured cleanly into `src/core/`, `src/tools/`, `src/rag/`, `src/agent/`, and `src/api/`.
- **Hybrid Retrieval**: Upgraded from dense-only vector search to a Hybrid Retrieval engine combining Dense FAISS embeddings (`all-MiniLM-L6-v2`) with Sparse BM25 keyword matching (`BM25Okapi`) using Reciprocal Rank Fusion (RRF).

### Safe Linux Inspection Sandbox
- Implemented read-only system diagnostics (`src/tools/linux_diagnostics.py`) with strict `shell=False` execution, argument regex sanitization, and execution timeouts.
- Automated collection of live telemetry for systemd services, listening ports (`ss`), inode saturation (`df -i`), memory pressure (`free`), and kernel OOM killer events (`journalctl`/`dmesg`).

### Verification & Documentation Cleanup
- Engineered an automated Pytest test suite (`tests/`) verifying APIs, diagnostic security, intent routing, and runbook schema integrity (16/16 tests passing).
- Consolidated 95 legacy sprint/fix markdown files into a clean, maintainable `docs/` hierarchy.
