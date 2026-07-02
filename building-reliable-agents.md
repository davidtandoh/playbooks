# Playbook: Building Reliable Agents

Everything between a demo agent and one you'd run in production: observability, token
economics, reliability engineering, security, and the blind spots that bite at scale.
Companion to [Building AI Agents](building-ai-agents.md) — that one is *how to build one*,
this one is *how to keep it working and affordable*.

**How to read the confidence tags.** This playbook was assembled from a verified research
pass. Claims are tagged:
- **[verified]** — from a primary source that passed 3-vote adversarial verification (cited inline).
- **[practice]** — standard engineering practice the research corpus left thin; sound, but not from a verified primary source in this pass. Treat as default-good, not gospel.
- **[Claude]** — Claude/Anthropic-specific number or mechanism; re-check before porting to another provider.

> **Governing principle:** reliability is *designed in at the boundary*, not prompted in at
> the model. Deterministic controls (caps, sandboxes, validators, schemas) wrap probabilistic
> behavior — because the model layer is never 100%.

---

## 0. The rules, in one screen

1. **Don't reach for an agent by default.** Start with the simplest thing (often one optimized LLM call + retrieval); add autonomy only when it demonstrably improves outcomes — autonomy compounds errors. **[verified]**
2. **Context is a finite, degrading resource.** Every token spent costs money *and* erodes recall ("context rot"). Curate, don't fill. **[verified]**
3. **Instrument for cost-per-task, not just accuracy.** Token count, tool-call count, runtime, and tool errors per task are the raw signals. **[verified]**
4. **Grade outcomes, not paths.** Agents find valid routes you didn't anticipate; asserting an exact tool sequence gives brittle tests. **[verified]**
5. **Contain at the environment layer first, steer at the model layer second.** **[verified]**
6. **The system controls the agent, not the reverse** (carried over from the agents playbook).

---

## 1. Observability — you can't fix what you can't see

Agent failures are non-deterministic and multi-step; without traces you're debugging blind.

### Instrument on a vendor-neutral standard: OpenTelemetry GenAI

Use the [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/) so telemetry is portable across backends. **[verified]** Core span attributes:

| Attribute | Captures | Why it matters |
|---|---|---|
| `gen_ai.request.model` | Which model served the call | Routing/cost attribution |
| `gen_ai.usage.input_tokens` | Prompt tokens | The dominant cost driver in agents |
| `gen_ai.usage.output_tokens` | Completion tokens | Output cost |
| `gen_ai.response.finish_reasons` | Why generation stopped | Detect truncation / tool-use / refusal |
| `gen_ai.usage.cache_creation.input_tokens` | Tokens **written** to cache | Cache-write spend |
| `gen_ai.usage.cache_read.input_tokens` | Tokens **served** from cache | Cache-read savings — proves caching is working |

> Note: these are the *current* names — `input_tokens`/`output_tokens` replaced the older
> `prompt_tokens`/`completion_tokens`. The conventions are still marked experimental
> ("Development" stability) and may evolve. **[verified]**

**Minimum-viable span identity** — bind every span with these three so you can reconstruct a run: **[verified]**
- `gen_ai.conversation.id` — ties all spans in one run together
- `gen_ai.agent.name` — which agent (critical in multi-agent systems)
- `gen_ai.operation.name` — `chat` / `invoke_agent` / `execute_tool`

### Content capture is privacy-by-default OPT-IN

By default, GenAI telemetry records **only metadata** (model, token counts, durations) — **not**
prompt content or tool arguments, which can carry PII/secrets. Enabling capture
(`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`, default `false`) is what populates full
messages, system prompts, tool schemas, arguments, and results. This is both an observability
knob *and* a security control — turn it on deliberately, scoped, never blanket in production. **[verified]**

### Backend

[Langfuse](https://langfuse.com/integrations/native/opentelemetry) works as an OTel-native
backend: ingest traces at its OTLP HTTP endpoint (`/api/public/otel`, HTTP/JSON or
HTTP/protobuf — **not gRPC yet**), Basic-Auth with base64 keys; it maps incoming `gen_ai.*`
spans to its model. LangSmith is the LangChain-native alternative. Any OTel-compatible backend
works — that's the point of standardizing on the convention. **[verified, medium confidence — single-vendor source]**

### Observability checklist
- [ ] Every LLM call and tool call emits an OTel GenAI span
- [ ] Spans carry conversation id, agent name, operation name
- [ ] Token usage (incl. cache read/write) recorded per call
- [ ] `finish_reasons` logged (catch truncation/refusal early)
- [ ] Content capture off by default; on only where scoped and justified
- [ ] Traces land in a backend you can query per-run ("pull the trace, see where it broke")

---

## 2. Token cost & economics — where the money actually goes

### The core mental model: context is finite and degrading

Every token added **depletes the attention budget** and, as context grows, **recall drops
("context rot")** — corroborated across 18 frontier models in Chroma's study. So a bloated
context costs you *twice*: per-token spend **and** worse answers. Curate the smallest
high-signal token set. **[verified]**

### Where tokens go in an agent loop

The expensive part of agents is usually **input tokens, re-billed every turn** — the whole
conversation history is re-sent on each step, so cost scales super-linearly with loop length.
Tool-call chatter (verbose tool outputs re-entering context) and multi-agent fan-out multiply
it further. Instrument first, optimize the top driver. **[practice — directional; exact multipliers in the corpus were unverified blog figures]**

### Controls (highest-leverage first)

| Control | What to do | Source |
|---|---|---|
| **Cap tool outputs** | Bound tool responses; build in pagination, range selection, filtering, truncation with sane defaults. Claude Code caps tool responses at **25,000 tokens** by default. **[verified][Claude]** | [writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) |
| **Concise response formats** | Expose a `response_format` (concise vs detailed); concise can use **~⅓ the tokens** (illustrative, one worked example — treat as order-of-magnitude). **[verified]** | same |
| **Compaction** | Near the limit, summarize and reinitiate a fresh window with the summary. Build the compaction prompt by **maximizing recall first, then improving precision**. **[verified][Claude]** | [context-engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| **Prompt caching** | Reuse a stable prefix across turns (see economics below). **[Claude]** | Anthropic prompt caching |
| **Model routing / tiering** | Route by task difficulty — cheap model for simple, mid-tier for most, frontier for the hardest (Anthropic's own guidance). Cascade/router architectures make it systematic: **FrugalGPT** matches GPT-4 at up to **98% lower cost**; **RouteLLM** cuts cost **~85% at 95% of GPT-4 quality** (MT-Bench). See mechanics below. **[verified]** | [FrugalGPT](https://arxiv.org/pdf/2305.05176), [RouteLLM](https://github.com/lm-sys/RouteLLM), [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| **Batching** | Non-urgent, high-volume work → Batch API at **50% off both input and output** tokens (e.g. Opus 4.8 $5/$25 → $2.50/$12.50 per MTok). Stacks with prompt caching. **[verified][Claude]** | [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| **Hard caps** | Turn/step limits and token budgets as a runaway backstop. **[practice]** | — |

### Model routing & cascades (the mechanics) **[verified]**

Two paradigms for spending frontier-model money only where it's needed:
- **Routing** — pick one model per query up front.
- **Cascading** — run cheap→expensive in sequence, stopping when the output is good enough. An LLM cascade scores each answer with a generation-scoring function `g(q,a) → [0,1]` and escalates to the next model only when the score is below a threshold τ. ([FrugalGPT](https://arxiv.org/pdf/2305.05176))
- **Cascade routing** unifies both into one budget-aware strategy — select on a cost-quality score `q̂(x) − λĉ(x)` under a fixed cost budget B — and empirically beats routing-only or cascading-only (up to ~14% on SWE-Bench). ([cascade routing](https://arxiv.org/abs/2410.10347))

Rule of thumb: default to a mid-tier model; cascade up to frontier only when a scorer says the cheap answer isn't good enough. Reported savings are large (**85–98%**) but workload-dependent — measure on your own eval set, don't assume the headline number.

### Prompt-caching economics (the numbers) **[verified][Claude]** — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

- **Cache read ≈ 0.1×** base input price; **cache write = 1.25×** (5-min TTL) or **2×** (1-hour TTL).
- **Break-even:** pays off after **1 cache read** (5-min write) or **2 cache reads** (1-hour write). Multipliers **stack** with the Batch discount and data residency.
- **Default TTL 5 min, refreshed on each read;** 1-hour optional for bursty traffic with gaps.
- **Minimum cacheable prefix is model-dependent** (e.g. ~4096 tokens on Opus 4.8 / Haiku 4.5; ~1024 on Sonnet 4.5). Below it, nothing caches — silently.
- Keep the cached prefix **byte-stable** (frozen system prompt, deterministic tool order); put volatile content last. One byte change in the prefix invalidates everything after it.
- **Verify it's working:** the OTel `cache_read.input_tokens` attribute should be non-zero across repeated identical-prefix requests. Zero = a silent invalidator (timestamp/UUID in the prefix, unsorted JSON, varying tool set). *This is where §1 observability pays for §2 economics.*

### Measure cost-per-task, not just accuracy

Collect, per task: **total token consumption, total tool-call count, per-call and per-task
runtime, and tool errors.** These four are exactly what you need to compute cost-per-outcome and
find the agent/tool/loop burning budget. **[verified]**

> **Bosun tie-in:** the 35M-token OpenRouter burn is the textbook case — total spend told you
> *that* it happened; per-agent / per-task attribution (which worker, which loop, which model)
> is what tells you *where*. Instrument attribution before scaling any fleet.

### Token-economics checklist
- [ ] Tool outputs capped + paginated/filtered with sane defaults
- [ ] Concise-vs-detailed response modes where output is bulky
- [ ] Compaction wired for long conversations (recall-first prompt)
- [ ] Prompt caching on stable prefixes; `cache_read` tokens verified non-zero
- [ ] Cheap/frontier model routing where step difficulty varies
- [ ] Cost-per-task dashboard: tokens, tool calls, runtime, errors per run
- [ ] Hard turn/token budget backstop against runaways

---

## 3. Reliability engineering — surviving non-determinism

### Measure reliability with the right metric

Agents are stochastic; a single success proves nothing. Use two metrics: **[verified]**
- **pass@k** — probability of ≥1 success in k attempts. Use where **one success suffices** (a retrieval tool).
- **pass^k** — probability **all** k trials succeed. Use where **consistency is essential** (an autonomous agent). Sobering math: 75% per-trial → pass^3 ≈ **42%**.

### Grade the outcome, not the path

Grade the final state/artifact the agent produced, **not** a prescribed tool-call sequence.
Agents "regularly find valid approaches eval designers didn't anticipate," so path-asserting
tests are brittle. Keep transcript review as a **debugging aid**, not the pass/fail gate. **[verified]**

### Grader stack — pick per dimension

| Grader | Strengths | Weaknesses |
|---|---|---|
| **Code-based** | Fast, cheap, objective, reproducible, debuggable | Brittle to valid variations |
| **Model / LLM-as-judge** | Flexible, scalable, captures nuance | Non-deterministic, costly, **needs calibration** |
| **Human** | Gold standard | Expensive, slow |

Discipline for LLM-as-judge: **calibrate against human experts** before trusting at scale; give
the judge an **escape hatch** (return "Unknown") to curb hallucinated verdicts; grade **each
dimension with its own isolated rubric** rather than one judge scoring everything at once. **[verified]**

### Two eval suites, two targets

- **Regression evals** — "does it still handle everything it used to?" → keep near **100% pass**; catches backsliding. **[verified]**
- **Capability evals** — target tasks it struggles with → start at a **low pass rate** to preserve improvement signal. An eval at 100% saturation tracks regressions but gives no room to climb. **[verified]**

### Failure handling mechanics **[verified]** — [AWS: backoff & jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), [AWS Builders' Library: timeouts, retries & backoff](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

| Concern | Pattern |
|---|---|
| **Transient tool/API failure** | Exponential backoff **with jitter** — backoff alone keeps clients clustered at the same intervals; jitter spreads them to a near-constant call rate and cuts retry volume by **>half**. **Full Jitter** is the sane default. Cap attempts. |
| **Retry amplification** | Retry at **a single layer** only. Independent retries at each tier multiply — a 5-deep stack × 3 retries = **243× load** on the bottom dependency, which then can't recover. |
| **Limiting retry load** | Prefer a **local token bucket** (retry freely while tokens last, then at a fixed rate) — AWS's SDK default since 2016 — over a hard trip. A circuit breaker (open → half-open → closed) is still fine for isolating a flaky *dependency*. |
| **Idempotency** | Side-effecting calls are **not safe to retry unless idempotent**. Attach a client-generated **idempotency key** (cf. EC2 `RunInstances`) so a retry can't double-send/charge. A timeout does **not** mean the side effect didn't happen. |
| **Timeouts** | Per-tool and per-task deadlines; don't let one hung call wedge the run. **[practice]** |
| **Bad output** | Validate **format and content** at every hand-off; a review layer catches what schemas miss. **[verified — see §3 grading]** |
| **Hallucinated tool call** | Return a **structured error**, not an exception — let the agent recover. **[verified — see §2 tools]** |
| **Partial completion** | Checkpoint; make operations idempotent so a resumed run doesn't redo work. |

### Long-running agents: state scaffolding + known failure modes **[verified][Claude]**

Compaction alone is insufficient for long horizons — even a frontier model "falls short given
only a high-level prompt." Bridge state across context windows with durable external scaffolding
(from Anthropic's [long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) case study):
- **Progress log file** (`claude-progress.txt`) — what's been done
- **Descriptive git commits** — so bad changes can be reverted
- **Structured JSON feature registry** (`passes: true/false`) — models are less likely to rewrite JSON than prose

And design the harness against the recurring failure modes:
- **Over-ambitious execution** → force **one feature at a time**
- **Premature "done" claims** → verified pass/fail list; **never delete or edit tests**
- **Broken environment left behind** → run a **basic end-to-end smoke test at each session start**

### Reliability checklist
- [ ] Reliability tracked with pass^k (consistency-critical) or pass@k (one-success)
- [ ] Evals grade produced outcome/state, not tool-call path
- [ ] Grader chosen per dimension; LLM judges calibrated + "Unknown" escape + per-dimension rubric
- [ ] Separate regression (~100%) and capability (low-pass) suites
- [ ] Retries use backoff **with jitter**, retry at a **single layer**, token-bucket cap; idempotency keys on side-effecting calls
- [ ] Per-tool/per-task timeouts; circuit breaker / token bucket on flaky dependencies
- [ ] Format + content validation at every hand-off
- [ ] Structured errors (not exceptions) back to the agent
- [ ] Long-running: progress log + git + JSON feature registry + start-of-session smoke test

---

## 4. Security & prompt injection — the dominant agent risk

### Defense-in-depth, in this order

Build **containment at the deterministic environment layer FIRST** — sandboxes, VMs, syscall
filters, container runtimes, egress controls — **then** steer behavior at the probabilistic
model layer. Rationale: *the model layer is never 100%.* Layers should overlap so that when one
is unavailable the other picks up the slack. **[verified]** ([how-we-contain-claude](https://www.anthropic.com/engineering/how-we-contain-claude))

### Prompt injection specifically **[practice]**

Untrusted content the agent reads — web pages, emails, file contents, **tool outputs** — can
carry instructions that hijack it. Defenses:
- **Treat tool output as data, not instructions.** Never let retrieved content silently become commands.
- **Least-privilege tool scopes** — each agent/tool gets only the permissions its job needs; narrow the blast radius.
- **Gate irreversible actions** (send, delete, pay, deploy) behind confirmation or a human approval step.
- **Allowlists** for domains/hosts/commands over blocklists.
- **Egress controls** — constrain where a compromised agent could exfiltrate to.

### Security checklist
- [ ] Tools run in a sandbox/VM with egress controls (environment layer first)
- [ ] Tool output treated as data; not interpolated as instructions
- [ ] Least-privilege scopes per tool/agent
- [ ] Irreversible actions gated (confirmation / HITL)
- [ ] Allowlists + egress restrictions in place
- [ ] Content-capture telemetry scoped (no blanket PII capture)

---

## 5. The rest of the blind spots **[practice — research-thin; capture and revisit]**

The verified corpus was thin here (the research explicitly flagged these as open). Treat as a
checklist to reason through per project, not settled doctrine.

- **Determinism boundaries** — decide explicitly where you *force* structure (schemas, validators, deterministic control flow) vs. let the model decide. Reliable agents are "structured coordination with autonomous execution at defined points," not free-for-alls.
- **Human-in-the-loop** — explicit escalation criteria, confidence-based routing, approval gates for high-stakes/irreversible actions. Concrete mechanism: **LangGraph `interrupt()`** pauses graph execution by raising a special exception, persists state via a checkpointer, and waits indefinitely; you resume by passing **`Command(resume=…)`**, whose value is delivered back to the `interrupt()` call so the node continues — approval gates then route on that value. **[verified]** ([LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)) ⚠️ On resume the node re-runs from its start, so any side effect *before* the interrupt must be idempotent (ties back to §3). **[practice — errored on session limit, unverified]**
- **Latency & UX** — stream output, show progress on long runs, set timeouts. A correct answer that arrives silently after 4 minutes reads as broken.
- **Deployment & versioning** — pin and version model + prompt + tool configs together; support rollback; stage rollouts. Log which config version ran each task so a regression is traceable to a change.
- **Memory hygiene** — decide what persists across sessions, guard against staleness, and prevent a poisoned memory store from corrupting future runs. Verify memory facts (files, flags) still exist before acting on them.
- **Idempotency & recovery** — checkpoint so a mid-run failure resumes rather than restarts, and a retry doesn't repeat a side effect.

---

## 6. Master "reliable agent" checklist

**Before you ship:**
- [ ] An agent is actually warranted (simplest-tier gate passed)
- [ ] OTel GenAI spans on every LLM + tool call; queryable per-run traces
- [ ] Cost-per-task telemetry (tokens, tool calls, runtime, errors)
- [ ] Tool outputs capped; compaction + caching where they pay off; caching verified via `cache_read` tokens
- [ ] pass^k / pass@k reliability metric chosen and measured
- [ ] Outcome-based evals; regression (~100%) + capability suites; calibrated graders
- [ ] Retries + idempotency + timeouts + circuit breakers on side-effecting/flaky paths
- [ ] Validation at every hand-off; structured errors back to the agent
- [ ] Environment-layer sandbox + egress + least-privilege before model-layer steering
- [ ] Tool output treated as data; irreversible actions gated
- [ ] Config (model/prompt/tools) versioned + rollbackable
- [ ] Long-running: state scaffolding + start-of-session smoke test
- [ ] Content-capture telemetry scoped (privacy-by-default)

---

## 7. Failure mode → mitigation (quick reference)

| Failure | Mitigation |
|---|---|
| Runaway loop / cost blowout | Turn+token budget backstop; cost-per-task alerting; circuit breaker |
| Context rot / degraded recall | Curate context; compaction (recall-first); cap tool outputs |
| Silent cache misses | Byte-stable prefix; verify `cache_read` tokens non-zero |
| Brittle evals | Grade outcome not path; per-dimension calibrated graders |
| Regression on a change | Regression suite near 100%; versioned configs; trace to config version |
| Prompt injection | Tool output as data; sandbox + egress; gate irreversible actions |
| Double side-effects on retry | Idempotency keys; checkpointing |
| Premature "done" / broken env (long runs) | JSON feature registry; never edit tests; start-of-session smoke test |
| Hung tool call | Per-tool timeouts; circuit breaker |
| PII leak via telemetry | Content capture off by default; scope when enabled |

---

## 8. Sources & confidence

**Primary sources (passed 3-vote adversarial verification):**
- Anthropic — [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- Anthropic — [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- Anthropic — [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Anthropic — [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Anthropic — [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Anthropic — [How We Contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)
- OpenTelemetry — [GenAI semantic conventions (spans)](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/) and [GenAI observability blog](https://opentelemetry.io/blog/2026/genai-observability/)
- Langfuse — [OpenTelemetry integration](https://langfuse.com/integrations/native/opentelemetry) *(single-vendor, medium confidence)*

**Added in the second research pass (failure-handling, routing, HITL):**
- AWS — [Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- AWS Builders' Library — [Timeouts, Retries and Backoff with Jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [FrugalGPT (arXiv 2305.05176)](https://arxiv.org/pdf/2305.05176) · [Cascade Routing (arXiv 2410.10347)](https://arxiv.org/abs/2410.10347) · [RouteLLM](https://github.com/lm-sys/RouteLLM)
- Anthropic — [Pricing (Batch discount, model tiering, cache economics)](https://platform.claude.com/docs/en/about-claude/pricing)
- LangChain — [LangGraph interrupts (HITL pause/resume)](https://docs.langchain.com/oss/python/langgraph/interrupts)

**Known caveats (from the research pass):**
- Source base skews Anthropic/Claude — principles are provider-agnostic, but specific numbers (25k tool-cap, the long-running-harness patterns) are Claude-anchored case-study defaults, not universal laws.
- The "~⅓ tokens for concise" figure is one worked example, not an averaged ratio.
- OTel GenAI conventions are experimental ("Development" stability) — attribute names are current but may still change.

**Now verified (second pass):** retries/backoff+jitter, retry amplification, token-bucket retry limiting, idempotency keys, model routing/cascades, Batch economics, and the LangGraph HITL pause/resume mechanism — all upgraded above with citations.

**What the research still could NOT confirm (open questions — verify before relying):**
- Exact token-cost multipliers for agent loops (blog figures like "O(N²)" / "10–100×" did not survive verification — directional only).
- The specific jitter formulas (Full/Equal/Decorrelated) — **refuted** as stated (0-3); use the named strategies, not memorized formulas.
- **OWASP least-privilege / permission scoping**, **memory hygiene** (staleness, poisoning defenses, expiry), **deployment/versioning & canarying**, **multi-agent fan-out cost control**, and the broader **LangGraph HITL approval-gate patterns** (approve/edit/review) — these verifications **errored on an account session limit**, not on merit. The `[practice]` items covering them are standard engineering, not yet primary-sourced. A re-run after the limit resets would likely confirm most.
