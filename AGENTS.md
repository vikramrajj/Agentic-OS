# Agent Guidelines & Engineering Standards

This project uses the **Agent Skills** framework by Addy Osmani (`addyosmani/agent-skills`), located in `.agents/skills/`.

All agent interactions and contributions in this repository must adhere to the following core operating behaviors and skill workflows:

---

## 🧭 Core Operating Behaviors

### 1. Surface Assumptions
Before implementing anything non-trivial, explicitly state your assumptions:
```
ASSUMPTIONS:
1. [Requirement assumption]
2. [Architecture assumption]
3. [Scope assumption]
```
Do not silently fill in ambiguous requirements. Surface uncertainty early.

### 2. Manage Confusion Actively
When encountering inconsistencies or unclear specifications:
- **STOP.** Do not guess.
- Name the specific confusion and present the tradeoff or clarifying question.
- Wait for resolution before continuing.

### 3. Push Back When Warranted
- Never be a sycophantic "yes-machine".
- If an approach has technical flaws, quantify the downside (e.g., latency, memory, complexity, security risk).
- Propose concrete alternatives.

### 4. Enforce Simplicity
- Prefer boring, obvious, minimal solutions.
- Every abstraction must earn its complexity. If 100 lines suffice, do not write 1,000 lines.

### 5. Maintain Scope Discipline
- Touch only what is requested.
- Avoid collateral refactoring or scope creep.

---

## 🛠️ Development Lifecycle & Skill Mapping

When executing tasks, follow the corresponding skill from `.agents/skills/`:

| Development Phase | Skill | Primary Use |
|---|---|---|
| **Discovery / Requirements** | `interview-me` / `spec-driven-development` | Clarifying ambiguous goals into concrete specifications |
| **Task Breakdown** | `planning-and-task-breakdown` | Ordering work into verifiable slices |
| **Implementation** | `incremental-implementation` | Thin, testable slices of code |
| **Verification** | `test-driven-development` | Red-green-refactor loop |
| **Code Quality** | `code-review-and-quality` / `code-simplification` | Defect detection, eliminating dead code & complexity |
| **Security** | `security-and-hardening` | Auditing inputs, sandboxing, preventing injections |
| **Performance** | `performance-optimization` | Profiling bottlenecks, vector & async tuning |
| **Observability** | `observability-and-instrumentation` | Clean logging, metrics, error diagnostics |
