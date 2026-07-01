# Playbook: Building AI Agents

A practical, opinionated guide for going from "I want an agent" to a system that ships
real output without someone shepherding every step.

**Sources this synthesizes**
- MindStudio — [The ReAct Loop: AI Agent Reasoning](https://www.mindstudio.ai/blog/what-is-react-loop-ai-agent-reasoning)
- MindStudio — [How to Build a Multi-Agent Workflow](https://www.mindstudio.ai/blog/how-to-build-multi-agent-workflow)
- Anthropic agent-design guidance (tool-surface design, context management, the "should I build an agent" gate)

> **Governing principle (memorize this):** *the system controls the agent, not the agent
> controls the workflow.* Everything below is in service of keeping fixed structure around
> autonomous decision-making at defined points.

---

## 0. The four-line summary

1. Don't build an agent until a simpler tier fails (single call → workflow → agent).
2. The atomic unit of every agent is the **ReAct loop**: Thought → Action → Observation, repeat until a real stop condition.
3. What kills long-running agents is **context**, not intelligence — manage it deliberately.
4. Go multi-agent only when a single loop bogs down; then use an **orchestrator + narrow workers** talking through a **task queue**, never direct hand-offs.

---

## 1. Gate: should you even build an agent?

Before writing a loop, check all four. A "no" on any one means drop to a simpler tier.

| Criterion | Question |
|---|---|
| **Complexity** | Is the task multi-step and hard to fully specify up front? ("turn this doc into a PR" ✅ vs "extract the title from this PDF" ❌) |
| **Value** | Does the outcome justify higher cost + latency? |
| **Viability** | Is the model actually capable at this task type? |
| **Cost of error** | Can mistakes be caught and recovered (tests, review, rollback)? |

**Tier ladder — start at the lowest that works:**

```
Single LLM call      → classification, extraction, summarization, Q&A
Workflow (you loop)  → multi-step, code-orchestrated, deterministic control flow
Agent (model loops)  → open-ended, model decides its own trajectory
```

Most "agent" ideas are actually workflows. A workflow where *you* own the control flow
(loops, branches, retries in your code) is more reliable and cheaper than a model-driven
loop — reach for a true agent only when the trajectory genuinely can't be pre-specified.

---

## 2. The atomic unit: the ReAct loop

**ReAct = Reasoning + Acting** (Princeton/Google, 2022). The agent alternates internal
reasoning with external tool calls instead of one-shot answering. One iteration:

- **Thought** — assess the situation, decide what's needed next. Explicit reasoning
  prevents pattern-match shortcuts.
- **Action** — one *bounded, specific* tool call (search, file op, DB query, API call,
  code exec, or delegate to a sub-agent). Call the tool and *wait* — don't guess the result.
- **Observation** — the tool's result (or error) feeds back into context for the next Thought.

Repeat until task completion or a stop condition.

**Why it beats single-shot:**
- **External grounding** — actions connect the model to real, current data instead of confident guessing.
- **Error correction** — a failed/surprising observation feeds back into reasoning, so the agent can notice and adjust. This self-correction is the whole point.

**Claude mapping (the loop in practice):**

```python
messages = [{"role": "user", "content": task}]
while True:
    resp = client.messages.create(model="claude-opus-4-8", tools=tools, messages=messages, max_tokens=16000)
    if resp.stop_reason == "end_turn":        # agent is done (Thought → finish)
        break
    if resp.stop_reason == "tool_use":         # agent wants an Action
        messages.append({"role": "assistant", "content": resp.content})
        results = [run(tc) for tc in resp.content if tc.type == "tool_use"]  # Observation
        messages.append({"role": "user", "content": results})   # feed back, loop
```

Loop control derives from `stop_reason` — **never** from parsing the model's prose to
guess "is it done." (See anti-patterns.)

### Loop failure modes + mitigations

| Failure | What it looks like | Mitigation |
|---|---|---|
| **Infinite loop** | Retrying variations with no progress | Max-step cap + fallback behavior (a backstop, *not* the primary stop mechanism) |
| **Hallucinated tool calls** | Model invents a non-existent tool/param | Strict schemas, validate inputs, return a *structured error* (not an exception) so it can recover |
| **Over-planning** | Excessive reasoning / re-verifying trivia before acting | Lower effort / prompt for decisive action; don't re-derive settled facts |
| **Context overflow** | Accumulated Thoughts/Observations blow the window | Context editing, compaction, memory (see §4) |

---

## 3. Single-agent architecture

### Tool surface design (the highest-leverage decision)

Claude emits tool calls; **your harness** handles them. The *shape* of the tool call
determines what the harness can do with it.

- **Bash / broad tool** → maximum leverage for the model, but the harness only sees an
  opaque command string. Start here for breadth.
- **Dedicated tool** (`send_email`, `edit_file`) → typed arguments the harness can
  intercept, gate, render, audit, or parallelize.

**Promote an action from bash to a dedicated tool when you need to:**
- **Gate it** — hard-to-reverse actions (send, delete, external POST) behind confirmation.
- **Enforce an invariant** — e.g. reject a write if the file changed since last read.
- **Render it** — custom UI (a question tool that renders as a modal and blocks the loop).
- **Parallelize it** — mark read-only tools parallel-safe; the harness can't tell a safe
  `grep` from an unsafe `git push` if both go through bash.

Rule of thumb: **start with bash for breadth; promote to dedicated tools to gate, render,
audit, or parallelize.**

### Write tools the model will actually use well
- Descriptive names (`get_current_weather`, not `weather`).
- Descriptions that say **when to call it**, not just what it does — "Call this when the
  user asks about current prices or recent events." Newer models reach for tools more
  conservatively, so trigger conditions in the description give measurable lift.
- `enum` for fixed-value params; mark only *truly* required params required.
- Structured errors with `is_error: true` and an informative message so the agent adapts.

---

## 4. Context management — what actually kills long-running agents

Not intelligence. Context. Three levers, plus caching:

| Lever | What it does | Use when |
|---|---|---|
| **Context editing** | *Prunes* stale tool results / thinking blocks (removes them) | Old observations no longer relevant; keep the transcript lean |
| **Compaction** | *Summarizes* earlier history server-side into a compaction block | Conversation approaching the context-window limit |
| **Memory** | Persists state to files *across* sessions | State must survive process restarts |
| **Prompt caching** | Reuses a stable prefix at ~0.1× cost | Large fixed context reused across many turns |

Editing and compaction work *within* a session (prune vs summarize); memory is *cross*-session.
Long agents often use all three. For caching, keep the stable prefix frozen (frozen system
prompt, deterministic tool order) and put volatile content last — a single byte change in
the prefix invalidates everything after it.

---

## 5. Going multi-agent

**When:** a single loop bogs down under long context, loses track of constraints, can't
parallelize, or has to restart from scratch when it fails midway. Otherwise stay single-agent.

### Core shape: orchestrator + workers

**Orchestrator (project manager):** receives the top-level goal, decomposes it into tasks,
assigns them, tracks status (done / in-progress / blocked), handles failures and
reassignments, assembles final output. Needs a clear structured view of what's done, in
progress, and blocked.

**Workers (specialists):** narrow-purpose. Each needs a **bounded task description,
the required tools, a structured output format, and a defined success condition.**
Narrower scope → better output. Don't give every agent every tool.

> On Claude specifically this is the coordinator–subagent pattern: subagents run their own
> isolated ReAct loop and **do not inherit** the coordinator's conversation history — the
> coordinator must pass needed context explicitly in the delegated message.

### Pick a coordination pattern

| Pattern | How it works | Use when |
|---|---|---|
| **Sequential pipeline** | Each agent finishes before the next starts | Later stages need the full prior output |
| **Parallel fan-out** | Router dispatches independent chunks at once; merger collects | Task partitions cleanly; you want lower wall-clock |
| **Conditional branching** | Orchestrator routes based on results | Real-world variance — *most production workflows need this* |
| **Iterative loop** | Output reviewed; if insufficient, loop back (pending → in-progress → review → done) | Quality bar must be met before "done" |

### Communicate through a task queue, not direct hand-offs

Direct agent-to-agent passing isn't resumable or debuggable. Instead:

- **Task queue** — structured task objects `{id, type, input, status, assigned_agent, priority}`;
  statuses: pending / in-progress / blocked / complete / failed.
- **Shared state** — accumulates results as the workflow runs. Keep it **structured** —
  "a flat blob of text isn't queryable."

This gives you resumability and full traces: *when a run fails, you can pull the trace and
see exactly where it went wrong.*

### Tools by agent type (match tools to the job)

| Agent | Tools |
|---|---|
| Research | web search, document retrieval, API access |
| Planning | task decomposition, calendar, constraint checking |
| Coding | code execution, filesystem I/O, package managers, git |
| Testing | test runners, log access, diff tools |
| Review | code analysis, output validators, rubric evaluation |

### Add a review layer

One agent evaluates another's work. *A critic that reviews a coding agent's output before
tests run catches more than any single-agent system.* Patterns: pass/fail gating, scored
evaluation across dimensions, comparative selection (N candidates → reviewer picks best),
human escalation for low-confidence output.

### Design for failure (assume every step can fail)

| Failure | Handling |
|---|---|
| Agent timeout | Per-task timeouts + retry/escalation policy |
| Bad output | Validate format *and* content; review layer catches it |
| Dependency failure | Propagate `blocked`; cleanly halt dependents |
| Hallucinated tool call | Return a structured error, not an exception |
| Partial completion | Checkpoint; make operations idempotent so retries are safe |

---

## 6. Making it autonomous

Trigger workflows without a human kicking each run:
- **Scheduled** (cron) for regular tasks
- **Event-based** — external events fire the workflow
- **Threshold-based** — a metric crossing a line initiates action
- **Polling** — agents periodically check for new work

---

## 7. Anti-patterns (memorize these — they're also exam bait)

- **Parsing prose to decide loop termination.** Use the structured stop signal
  (`stop_reason`), not "the assistant said it's finished."
- **Iteration cap as the *primary* stop mechanism.** The cap is a backstop; real
  completion is a proper stop condition.
- **Checking for assistant text as a completion indicator.** Same trap.
- **Too much agent autonomy too early.** Add structure first, loosen later.
- **No validation at hand-offs.** Errors cascade silently across stages.
- **Over-complicated orchestration.** *If you can't explain the flow in a paragraph, simplify it.*
- **Ignoring inference cost of parallel execution.** Fan-out multiplies spend.
- **No rollback for bad outputs.**
- **Giving every agent every tool.** Narrow the surface per agent.

---

## 8. Build checklist

- [ ] Confirmed an agent is warranted (passed the §1 gate; a workflow wouldn't do)
- [ ] Wrote the system diagram *before* code: stages, dependencies, parallel opportunities, per-stage I/O
- [ ] Chose a coordination pattern (sequential / parallel / conditional / iterative)
- [ ] Loop control keys off `stop_reason`, with a max-step backstop
- [ ] Tool surface designed: bash for breadth, dedicated tools where gating/rendering/auditing/parallelism is needed
- [ ] Tools have when-to-call descriptions, strict schemas, structured errors
- [ ] Task queue + structured shared state (no direct agent-to-agent passing)
- [ ] Context plan: editing / compaction / memory / caching as needed
- [ ] Review layer in place (gating, scoring, comparative, or human escalation)
- [ ] Failure handling: timeouts, validation, blocked-state propagation, checkpoints, idempotency
- [ ] Full logging/traces: task dispatch, results, retries
- [ ] Agents stateless where possible; agent/prompt/tool configs versioned
- [ ] Autonomy triggers wired if needed (schedule / event / threshold / poll)

---

## 9. Key insights to carry forward

- **ReAct's self-correction** — grounding + error feedback — is what separates an agent from a fancy autocomplete.
- **Structured coordination with autonomous execution at each step** is the sweet spot: fixed structure, agentic decisions at defined points.
- **The system controls the agent, not the other way around.**
