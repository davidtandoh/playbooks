# Playbooks

David Tandoh's working playbooks — distilled, opinionated guides for building things well.
Each playbook synthesizes primary sources into a checklist-driven reference I can actually
execute against.

## Index

The index groups playbooks by category without moving existing root files. The
category and topic vocabulary below is now controlled here. Existing playbook
front matter will adopt it in a separate change.

### AI-assisted engineering & software factories

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Testing in agentic engineering](testing-in-agentic-engineering.md) | `verification` `delivery-gates` `evals` `reliability` `cost` | A test portfolio for agent-written code, what agents over-produce (mocks, debug scripts, tampered assertions) and how to trim it, rules for fewer and better agent tests, property-based and mutation testing, and software tests versus agent evals |
| [CI for agentic engineering](ci-for-agentic-engineering.md) | `delivery-gates` `verification` `security-and-privacy` `cost` `reliability` | Local gate first with hosted merge proof, staged test selection, caching and merge queues, flaky-test governance, rounded-minute cost per merge, and trust boundaries for actions, secrets and runners |
| [API design](practices/engineering-standards/api-design.md) | `architecture` `delivery-gates` `verification` `security-and-privacy` | One default per HTTP API design question, enforced by a Spectral ruleset and an oasdiff breaking-change check: naming, versioning, RFC 9457 errors, pagination, idempotency, auth, rate limits, long-running operations, webhooks and events |
| [Observability](practices/engineering-standards/observability.md) | `observability` `reliability` `cost` `verification` | User-outcome SLIs and SLOs, budget-burn alerts, golden signals, RED and USE, correlated telemetry, OpenTelemetry propagation, cardinality and sampling budgets, data-pipeline indicators, runbooks and toil |
| [Performance and memory](practices/engineering-standards/performance-and-memory.md) | `architecture` `memory` `verification` `delivery-gates` `cost` | Data structures and complexity, allocation and copying, runtime costs, resource budgets, bounded memory, and hot-path regression gates |
| [Domain-driven design](practices/engineering-standards/domain-driven-design.md) | `architecture` `reliability` `verification` `delivery-gates` | Model business rules and ownership with bounded contexts, small aggregates, explicit events, ports and adapters, architecture tests, and ADRs |

### Agent systems

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Building AI Agents](building-ai-agents.md) | `architecture` `orchestration` `tools-and-context` `reliability` | When to build an agent, the ReAct loop, single-agent tool/context design, multi-agent orchestration, failure handling |
| [Building Reliable Agents](building-reliable-agents.md) | `observability` `cost` `evals` `security-and-privacy` | Observability (OTel GenAI), token cost and economics, reliability engineering and evals, security and prompt injection, and production blind spots |
| [Persistent agents (draft)](drafts/20261123-persistent-agents.md) | `architecture` `orchestration` `memory` `reliability` `governance` `evals` | What an always-on, proactive agent needs: task versus goal, wake triggers and a wake contract, durable state and recovery, notes-then-curated memory, governance at tool and model choke points, and evals for acting versus staying silent |
| [Agentic SRE practices](practices/agentic-sre/README.md) | `reliability` `observability` `evals` `governance` `security-and-privacy` `delivery-gates` `cost` | Nine operating practices for agent systems: SLOs and error budgets, autonomy and approval gates, blast radius, observability, eval-gated releases, drift, incidents, postmortems, and launch review |

### Enterprise AI platform

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Contextual Retrieval](contextual-retrieval.md) | `retrieval` `evals` `cost` | When to add chunk context, combine embeddings with BM25, and test reranking |

<!-- playbook-taxonomy:v1:begin -->
### Categories
- AI-assisted engineering & software factories
- Agent systems
- Enterprise AI platform

### Topics
- architecture
- orchestration
- tools-and-context
- memory
- retrieval
- evals
- observability
- reliability
- security-and-privacy
- cost
- delivery-gates
- verification
- knowledge-capture
- governance
- model-serving
- gateways
<!-- playbook-taxonomy:v1:end -->

## Which playbook applies

Match the work in front of you to a published page. Each published page lists
in its front matter when it applies (`applies_when`), the file or keyword
hints that suggest it (`signals`), and three to seven checkable rules drawn
from the page (`key_rules`). Each rule ends with a citation to a heading
in that page, in the form `(#anchor)`. Agents read rule text and source links from
[`index.json`](index.json). Drafts stay out of this list until they are
published.

<!-- playbook-index:v1:begin -->
<!-- Generated by scripts/playbook_index.py. Do not edit by hand. -->

**[Building AI Agents](building-ai-agents.md)**

- Applies when: deciding whether a task needs an agent, a workflow, or a single model call; building or changing an agent loop, its tools, or its context handling; splitting work across multiple agents.
- Signals: `agent`, `tool use`, `stop_reason`, `orchestrator`, `multi-agent`, `system prompt`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`tool-blast-radius`, `agentic-product-reliability-review`), `system-design-assessment`.
- Key rules:
  1. Build an agent only when the task passes all four gate criteria; otherwise use a single call or a workflow. ([source](building-ai-agents.md#1-gate-should-you-even-build-an-agent))
  2. Key loop termination off the structured stop signal; keep the iteration cap as a backstop only. ([source](building-ai-agents.md#2-the-atomic-unit-the-react-loop))
  3. Give each agent a narrow tool surface; do not give every agent every tool. ([source](building-ai-agents.md#core-shape-orchestrator--workers))
  4. Give tools when-to-call descriptions, strict schemas, and structured errors. ([source](building-ai-agents.md#8-build-checklist))
  5. Coordinate multiple agents through a task queue and structured shared state, never direct hand-offs. ([source](building-ai-agents.md#communicate-through-a-task-queue-not-direct-hand-offs))
  6. Validate output at every hand-off and keep a rollback for bad outputs. ([source](building-ai-agents.md#7-anti-patterns-memorize-these--theyre-also-exam-bait))

**[Building Reliable Agents](building-reliable-agents.md)**

- Applies when: taking an agent or LLM feature to production; adding observability, cost controls, evals, or security to an agent; handling untrusted input or prompt injection in an agent.
- Signals: `opentelemetry`, `gen_ai`, `prompt caching`, `eval`, `guardrail`, `sandbox`, `token budget`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md), `context-efficient-session`, `service-observability`.
- Key rules:
  1. Start with the simplest thing and add autonomy only when it demonstrably improves outcomes. ([source](building-reliable-agents.md#0-the-rules-in-one-screen))
  2. Treat context as finite and degrading; curate it instead of filling it. ([source](building-reliable-agents.md#the-core-mental-model-context-is-finite-and-degrading))
  3. Instrument cost per task, not just accuracy. ([source](building-reliable-agents.md#measure-cost-per-task-not-just-accuracy))
  4. Grade outcomes, not paths. ([source](building-reliable-agents.md#grade-the-outcome-not-the-path))
  5. Contain at the environment layer first and steer at the model layer second. ([source](building-reliable-agents.md#0-the-rules-in-one-screen))
  6. Keep prompt and response content capture opt-in. ([source](building-reliable-agents.md#content-capture-is-privacy-by-default-opt-in))

**[CI for agentic engineering](ci-for-agentic-engineering.md)**

- Applies when: adding or changing a CI workflow, a local gate script, or pre-commit and pre-push hooks; coding agents open many small pull requests and hosted CI cost or queue time grows; choosing test selection, caching, sharding, or a merge queue; handling flaky tests, workflow permissions, secrets, or self-hosted runners.
- Signals: `.github/workflows`, `github actions`, `workflow`, `ci`, `merge queue`, `merge_group`, `runner`, `flaky`, `actionlint`, `zizmor`.
- Skills: `apply-playbooks`, `spec-delivery-loop`, [`correct`](https://github.com/cursor/plugins/tree/main/pstack/skills/correct).
- Key rules:
  1. Run one canonical gate script locally before pushing, and use hosted CI only for independent merge evidence. ([source](ci-for-agentic-engineering.md#1-gate-locally-prove-independently))
  2. Select tests in stages and fail closed to the full suite when a change cannot be classified. ([source](ci-for-agentic-engineering.md#2-select-tests-in-stages))
  3. Restore caches on pull requests and save them only from trusted default-branch runs. ([source](ci-for-agentic-engineering.md#3-caching-sharding-and-merge-queues))
  4. Add merge_group triggers and a merge queue once concurrent agent pull requests break the default branch. ([source](ci-for-agentic-engineering.md#merge-queues-for-parallel-agent-work))
  5. Track flakiness per test, cap retries, and quarantine chronic flakes with an owner and a deadline. ([source](ci-for-agentic-engineering.md#4-govern-flaky-tests))
  6. Count cost per merged pull request in rounded job minutes across every attempt. ([source](ci-for-agentic-engineering.md#5-cost-per-merge-time-budgets-and-honest-baselines))
  7. Keep pull request validation secretless and read-only, pin third-party actions to full commit SHAs, and lint workflows with actionlint and zizmor. ([source](ci-for-agentic-engineering.md#6-trust-boundaries-and-agent-specific-ci-controls))

**[Contextual Retrieval](contextual-retrieval.md)**

- Applies when: building or changing a retrieval-augmented generation pipeline; chunked documents lose context needed to retrieve them; deciding whether to add BM25, reranking, or full-context prompting.
- Signals: `rag`, `retrieval`, `embedding`, `bm25`, `rerank`, `chunk`, `vector store`.
- Skills: none yet.
- Key rules:
  1. Test putting the whole knowledge base in a cached prompt before building retrieval when it is under 200,000 tokens. ([source](contextual-retrieval.md#1-start-with-the-simplest-prompt-that-fits))
  2. Generate context from the complete document and one target chunk, and prepend it before both the embedding and BM25 indexes. ([source](contextual-retrieval.md#2-generate-context-once-per-chunk))
  3. Build a local eval set before choosing the embedding model, fusion settings, chunk shape, or reranker. ([source](contextual-retrieval.md#3-evaluate-the-combined-retriever))
  4. Add reranking only when the quality gain justifies the added latency and cost. ([source](contextual-retrieval.md#4-add-reranking-only-when-the-trade-off-works))
  5. Treat the published preprocessing cost as a dated estimate under stated assumptions. ([source](contextual-retrieval.md#5-price-preprocessing-with-the-source-assumptions-visible))

**[Autonomy and approval gates](practices/agentic-sre/autonomy-and-approval.md)**

- Applies when: granting an agent a new power such as merge, send, spend, or deploy; adding or removing a human approval gate; supervising agents takes more time than the work.
- Signals: `approval`, `auto-merge`, `permissions`, `autonomy`, `human-in-the-loop`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`agent-autonomy-levels`, `agent-toil-budget`).
- Key rules:
  1. Grant no agent full access on day one. ([source](practices/agentic-sre/autonomy-and-approval.md#rules-of-thumb))
  2. Record the autonomy level per action type, not one level per agent. ([source](practices/agentic-sre/autonomy-and-approval.md#rules-of-thumb))
  3. Start at L2 for critical operations and L3 for minor incidents. ([source](practices/agentic-sre/autonomy-and-approval.md#at-a-glance))
  4. Write measurable promotion criteria and wire automatic demotion to live risk signals. ([source](practices/agentic-sre/autonomy-and-approval.md#checklist))
  5. Count approval clicks, re-prompts, and clean-up of agent output as toil. ([source](practices/agentic-sre/autonomy-and-approval.md#rules-of-thumb))

**[Blast radius for agent tools](practices/agentic-sre/blast-radius.md)**

- Applies when: giving an agent a tool, credential, memory store, or external channel; an agent can write, spend, or reach outside systems.
- Signals: `credentials`, `api key`, `service account`, `mcp server`, `tool definition`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`tool-blast-radius`).
- Key rules:
  1. Keep authorization downstream of the model; a system prompt is not a control. ([source](practices/agentic-sre/blast-radius.md#rules-of-thumb))
  2. Give each agent its own short-lived, scoped credentials; no shared or developer credentials. ([source](practices/agentic-sre/blast-radius.md#at-a-glance))
  3. Cap tokens, cost, tool calls, wall-clock time, and delegation depth per task. ([source](practices/agentic-sre/blast-radius.md#at-a-glance))
  4. Dry-run mutating calls before production state changes. ([source](practices/agentic-sre/blast-radius.md#at-a-glance))
  5. Stop an agent with a circuit breaker after repeated consecutive failures. ([source](practices/agentic-sre/blast-radius.md#at-a-glance))
  6. Keep an emergency stop that pauses in-flight actions, blocks new ones, and revokes L3 permissions fleet-wide. ([source](practices/agentic-sre/blast-radius.md#at-a-glance))

**[Drift and silent quality decay](practices/agentic-sre/drift.md)**

- Applies when: monitoring production quality of an agent or AI feature; a model, prompt, tool, or input mix changes under a running system; trusting an old eval or a model judge.
- Signals: `llm-as-judge`, `sampling`, `eval`, `model version`, `quality dashboard`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`drift-and-quality-monitoring`).
- Key rules:
  1. Do not trust a judge that has never been compared with human labels. ([source](practices/agentic-sre/drift.md#rules-of-thumb))
  2. Offline evals alone do not detect drift. ([source](practices/agentic-sre/drift.md#rules-of-thumb))
  3. Watch input mix, model version, tool errors, tokens per task, judge agreement, and calibration. ([source](practices/agentic-sre/drift.md#at-a-glance))
  4. Tier labels as bronze, silver, and gold. ([source](practices/agentic-sre/drift.md#at-a-glance))
  5. Read traces until you stop learning new failure types. ([source](practices/agentic-sre/drift.md#rules-of-thumb))

**[Incident response for agent systems](practices/agentic-sre/incidents.md)**

- Applies when: an agent takes a harmful action or a group of agents stalls; a model provider fails during operation; an AI product gives harmful output.
- Signals: `incident`, `outage`, `runbook`, `on-call`, `kill switch`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`agent-incident-response`).
- Key rules:
  1. A human is the incident commander, never an agent. ([source](practices/agentic-sre/incidents.md#at-a-glance))
  2. Agents investigate read-only and propose; the incident commander decides. ([source](practices/agentic-sre/incidents.md#at-a-glance))
  3. Make every change through one actuation path with pre-flight checks. ([source](practices/agentic-sre/incidents.md#at-a-glance))
  4. Mitigate first; do not root-cause while damage continues. ([source](practices/agentic-sre/incidents.md#rules-of-thumb))
  5. Do not lose transcripts before analysis. ([source](practices/agentic-sre/incidents.md#rules-of-thumb))

**[Launch review for agentic products](practices/agentic-sre/launch-review.md)**

- Applies when: designing or launching an agent-backed product or feature; signing off reliability before build or before launch.
- Signals: `launch`, `design review`, `readiness review`, `go-live`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`agentic-product-reliability-review`).
- Key rules:
  1. Define the critical user journeys and what correct means for each. ([source](practices/agentic-sre/launch-review.md#checklist))
  2. Give every agent feature a fallback without the model. ([source](practices/agentic-sre/launch-review.md#rules-of-thumb))
  3. Review SLOs, autonomy, blast radius, evals, tracing, drift, and incident roles together. ([source](practices/agentic-sre/launch-review.md#at-a-glance))
  4. Keep a failure-mode table, a rollback, and degraded modes. ([source](practices/agentic-sre/launch-review.md#checklist))
  5. Design reliability in before launch; adding it later costs more. ([source](practices/agentic-sre/launch-review.md#rules-of-thumb))

**[Observability: SLIs from traces](practices/agentic-sre/observability.md)**

- Applies when: adding tracing or metrics to an agent; computing reliability indicators from agent traces.
- Signals: `opentelemetry`, `gen_ai`, `execute_tool`, `span`, `trace`, `mcp`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`trace-based-slis`).
- Key rules:
  1. Measure tasks, not spans. ([source](practices/agentic-sre/observability.md#rules-of-thumb))
  2. Compute tool error rate from execute_tool spans with error.type set. ([source](practices/agentic-sre/observability.md#at-a-glance))
  3. Include failed and retried attempts in tokens and cost per task. ([source](practices/agentic-sre/observability.md#at-a-glance))
  4. Pin the GenAI and MCP convention version you implement and recheck it before an upgrade. ([source](practices/agentic-sre/observability.md#rules-of-thumb))
  5. Do not let reliability data become a data-leak path. ([source](practices/agentic-sre/observability.md#rules-of-thumb))

**[Postmortems for agent incidents](practices/agentic-sre/postmortems.md)**

- Applies when: writing up an agent incident or a notable bad output.
- Signals: `postmortem`, `incident review`, `retrospective`, `root cause`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`agent-postmortems`).
- Key rules:
  1. Stay blameless for humans and agents alike. ([source](practices/agentic-sre/postmortems.md#rules-of-thumb))
  2. Build the timeline from traces, not memory. ([source](practices/agentic-sre/postmortems.md#at-a-glance))
  3. Classify each incident with one OWASP agentic risk category. ([source](practices/agentic-sre/postmortems.md#at-a-glance))
  4. Add a regression eval case; a postmortem without one is incomplete. ([source](practices/agentic-sre/postmortems.md#rules-of-thumb))
  5. Give every action item an owner. ([source](practices/agentic-sre/postmortems.md#rules-of-thumb))

**[Eval-gated releases and canaries](practices/agentic-sre/releases.md)**

- Applies when: changing a model, system prompt, skill, tool schema, or agent framework version.
- Signals: `model id`, `prompt`, `skill`, `tool schema`, `canary`, `eval`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`eval-gated-releases`).
- Key rules:
  1. Version prompts, skills, model ids, tool schemas, and harness versions, and record each on every trace. ([source](practices/agentic-sre/releases.md#at-a-glance))
  2. Gate each release per slice against the last known-good baseline. ([source](practices/agentic-sre/releases.md#at-a-glance))
  3. Canary on one worker pool or a small share of traffic and compare SLIs per version. ([source](practices/agentic-sre/releases.md#at-a-glance))
  4. Abort on quality regression even when infrastructure looks healthy. ([source](practices/agentic-sre/releases.md#at-a-glance))
  5. Do not swap models in one big step. ([source](practices/agentic-sre/releases.md#rules-of-thumb))
  6. Add incident cases to the eval set so it does not go stale. ([source](practices/agentic-sre/releases.md#rules-of-thumb))

**[SLOs and error budgets for agents](practices/agentic-sre/slos-and-error-budgets.md)**

- Applies when: launching or reviewing an agent and defining how reliable it must be; choosing SLIs, SLO targets, error budgets, or burn-rate alerts; planning agent capacity, provider quotas, or cost.
- Signals: `slo`, `sli`, `error budget`, `burn rate`, `alerting`, `quota`.
- Skills: [`agent-reliability`](skills/agent-reliability/SKILL.md) (`agent-slo-design`, `agent-capacity-and-cost`).
- Key rules:
  1. Uptime alone is not an SLO for an agent. ([source](practices/agentic-sre/slos-and-error-budgets.md#rules-of-thumb))
  2. Use pass or fail indicators, not one-to-ten judge scores. ([source](practices/agentic-sre/slos-and-error-budgets.md#rules-of-thumb))
  3. Set targets per consequence tier and alert on burn rate over two windows. ([source](practices/agentic-sre/slos-and-error-budgets.md#checklist))
  4. Count retries in cost. ([source](practices/agentic-sre/slos-and-error-budgets.md#rules-of-thumb))
  5. Discover provider quotas in a load test, not in an incident. ([source](practices/agentic-sre/slos-and-error-budgets.md#rules-of-thumb))

**[API design: one default per question, enforced by a linter](practices/engineering-standards/api-design.md)**

- Applies when: adding or changing an HTTP API or its OpenAPI document; designing webhooks or event payloads consumed by another service.
- Signals: `openapi`, `openapi.yaml`, `spectral`, `oasdiff`, `endpoint`, `webhook`, `asyncapi`.
- Skills: none yet.
- Key rules:
  1. Commit the OpenAPI document and lint it with the shared Spectral ruleset on every pull request. ([source](practices/engineering-standards/api-design.md#openapi-first-with-spectral-and-oasdiff))
  2. Fail CI on breaking changes with oasdiff; break the contract only with a new major path version. ([source](practices/engineering-standards/api-design.md#versioning))
  3. Return RFC 9457 problem details with a stable type for every error. ([source](practices/engineering-standards/api-design.md#errors-with-rfc-9457))
  4. Paginate every list with page_size, page_token, and next_page_token from the first release. ([source](practices/engineering-standards/api-design.md#pagination))
  5. Accept an Idempotency-Key on every POST. ([source](practices/engineering-standards/api-design.md#idempotency-keys))
  6. Declare security on every operation and deny by default. ([source](practices/engineering-standards/api-design.md#auth-and-rate-limits))

**[Domain-driven design: model rules, ownership, and consistency](practices/engineering-standards/domain-driven-design.md)**

- Applies when: modelling business rules and ownership in data platforms, ML platforms, or services; defining bounded contexts, aggregates, domain events, or ports and adapters; separating domain logic from persistence frameworks and external systems.
- Signals: `domain-driven design`, `bounded context`, `aggregate`, `ubiquitous language`, `domain event`, `repository`, `hexagonal`, `ports and adapters`.
- Skills: `apply-playbooks`, `system-design-assessment`.
- Key rules:
  1. Define terms per bounded context and record the owner and contract of every context relationship. ([source](practices/engineering-standards/domain-driven-design.md#language-and-context-boundaries))
  2. Size aggregates around immediate invariants and test concurrent writes against real persistence. ([source](practices/engineering-standards/domain-driven-design.md#aggregates-and-invariants))
  3. Keep value objects immutable and enforce entity state changes through domain operations. ([source](practices/engineering-standards/domain-driven-design.md#entities-and-value-objects))
  4. Publish integration events only from committed state and make consumers safe under duplicate delivery. ([source](practices/engineering-standards/domain-driven-design.md#domain-events-and-integration-events))
  5. Keep domain decisions in the domain and transaction orchestration in application services. ([source](practices/engineering-standards/domain-driven-design.md#repositories-and-application-services))
  6. Fail the delivery gate on forbidden imports and cycles across domain, application, and adapters. ([source](practices/engineering-standards/domain-driven-design.md#ports-adapters-and-architecture-tests))
  7. Record costly boundary and consistency decisions in ADRs with alternatives and consequences. ([source](practices/engineering-standards/domain-driven-design.md#record-decisions-as-adrs))

**[Observability: measure user outcomes, then explain failures](practices/engineering-standards/observability.md)**

- Applies when: adding or reviewing logs, metrics, tracing, or alerts for a service or data platform; defining service or data-pipeline SLIs, SLOs, and error-budget policy; controlling telemetry cardinality, sampling, retention, or collector resource use.
- Signals: `observability`, `telemetry`, `opentelemetry`, `tracing`, `structured logging`, `metrics`, `alerting`, `golden signals`, `burn rate`, `slo`, `sli`, `freshness`, `cardinality`, `sampling`, `collector`.
- Skills: none yet.
- Key rules:
  1. Define good and valid events per user journey before choosing an SLO target. ([source](practices/engineering-standards/observability.md#slis-slos-and-error-budgets))
  2. Page on user-visible symptoms and require both windows of each burn-rate condition. ([source](practices/engineering-standards/observability.md#alerts-that-protect-the-budget))
  3. Correlate structured logs and spans with trace and request identity; keep those identifiers out of metric labels. ([source](practices/engineering-standards/observability.md#logs-metrics-and-traces))
  4. Propagate context across HTTP and queues and route telemetry through an OpenTelemetry Collector. ([source](practices/engineering-standards/observability.md#instrumentation-and-propagation))
  5. Bound cardinality, buffers, sampling state, and retention; test exporter failure under load. ([source](practices/engineering-standards/observability.md#cardinality-sampling-and-cost))
  6. Measure data freshness, completeness, correctness, and lateness at the consumer boundary. ([source](practices/engineering-standards/observability.md#data-pipeline-indicators))
  7. Link every paging alert to an owned runbook and test the alert rule before release. ([source](practices/engineering-standards/observability.md#dashboards-runbooks-and-toil))

**[Performance and memory: budgets before building](practices/engineering-standards/performance-and-memory.md)**

- Applies when: building or changing a service, job, or data pipeline with latency, throughput, or memory constraints; reviewing a hot path, resource limit, benchmark, or performance regression.
- Signals: `performance`, `latency`, `throughput`, `memory`, `benchmark`, `profile`, `profiling`, `hot path`, `data structure`, `allocation`, `garbage collection`, `coordinated omission`, `jmh`, `metaspace`, `aqe`, `kryo`, `event loop`, `optimisation`, `optimization`.
- Skills: none yet.
- Key rules:
  1. Choose data structures by access pattern and complexity; measure allocation, copying, I/O, and concurrency costs. ([source](practices/engineering-standards/performance-and-memory.md#write-efficient-code))
  2. Write latency, throughput, and peak-memory budgets in the spec before building. ([source](practices/engineering-standards/performance-and-memory.md#set-budgets-before-building))
  3. Attach a reproducible benchmark or profile for hot-path changes and compare results with the budget. ([source](practices/engineering-standards/performance-and-memory.md#measure-before-optimising))
  4. Stream data and bound every queue, cache, batch, and in-memory collection. ([source](practices/engineering-standards/performance-and-memory.md#bound-memory-by-default))
  5. Set explicit memory limits for every service and job, including runtime overhead and worker concurrency. ([source](practices/engineering-standards/performance-and-memory.md#set-service-and-job-limits))
  6. Choose the simplest structure that meets the budget and optimise only measured misses. ([source](practices/engineering-standards/performance-and-memory.md#choose-the-simplest-structure))
  7. Gate hot paths against absolute budgets and an agreed regression margin. ([source](practices/engineering-standards/performance-and-memory.md#gate-performance-regressions))

**[Testing in agentic engineering](testing-in-agentic-engineering.md)**

- Applies when: a coding agent writes or changes tests, or writes code and tests together; reviewing, trimming, or deduplicating a test suite that agents have grown; deciding which tests a change needs, or whether to use mocks, properties, snapshots, or end-to-end tests; choosing between software tests and agent evals for a system that contains an agent.
- Signals: `test`, `tests/`, `pytest`, `unittest`, `mock`, `fixture`, `hypothesis`, `mutation testing`, `coverage`, `snapshot`.
- Skills: `apply-playbooks`, `spec-delivery-loop`, [`diagnosing-bugs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs).
- Key rules:
  1. Give the agent the map of existing tests that cover the code it will change before it writes new tests. ([source](testing-in-agentic-engineering.md#3-rules-that-make-agents-write-fewer-better-tests))
  2. Trace every new test to a named requirement, boundary, invariant, contract, or bug reproduction. ([source](testing-in-agentic-engineering.md#3-rules-that-make-agents-write-fewer-better-tests))
  3. Prefer real collaborators or fakes over mocks, and delete tests that assert only mock calls. ([source](testing-in-agentic-engineering.md#2-detect-and-trim-what-agents-over-produce))
  4. Use a property-based test when a function obeys an invariant such as a round trip, ordering, or idempotency. ([source](testing-in-agentic-engineering.md#1-shape-the-test-portfolio))
  5. Judge test quality with mutation testing on changed code, not with raw line coverage. ([source](testing-in-agentic-engineering.md#1-shape-the-test-portfolio))
  6. Keep acceptance tests read-only or held out from the agent, and review every deleted or weakened assertion. ([source](testing-in-agentic-engineering.md#2-detect-and-trim-what-agents-over-produce))
  7. Test deterministic code with software tests and agent behaviour with evals; do not substitute one for the other. ([source](testing-in-agentic-engineering.md#4-software-tests-versus-agent-evals))
<!-- playbook-index:v1:end -->

## Conventions

- Keep each published standalone playbook in one Markdown file at the repo root.
  Practice pages stay in their practice set, as described below.
- Every playbook cites its primary sources up top.
- Favor tables, checklists, and rules-of-thumb over prose — these are references, not essays.
- Draw every diagram in a `mermaid` fence, not as ASCII art, and put a
  one-line `Takeaway:` below it. The site renders Mermaid to images when it
  builds. CI fails on an ASCII diagram in a `text` fence.
- Update the index above when adding a playbook.
- Give every published page `applies_when`, `signals`, and `key_rules` front
  matter, then run `python3 scripts/playbook_index.py` to regenerate
  `index.json`, the "Which playbook applies" section, and root playbooks'
  skills sections. Run `python3 scripts/playbook_index.py --check` to check
  for drift without writing files. CI fails when any generated content is stale.
- Name the agent skills that put a published page into practice in its
  `skills` front matter: one `<id>` or `<id>/<topic>` per item, or
  `skills: none`. Every id must appear in
  [`skills-public.json`](skills-public.json), the authoritative source for each
  skill's public summary, optional public link, and allowed topic ids. For a
  skill without a public copy, publish only its id and that summary. A root
  playbook that declares skills also needs the `playbook-skills:v1:begin` and
  `playbook-skills:v1:end` HTML comment markers where the generated "Skills
  that put this into practice" section goes. Practice pages keep their
  `Skill:` line instead of a generated section. Published skill copies live
  in [`skills/`](skills/README.md).
- Keep standalone playbook drafts under `drafts/`. A separate reviewed change
  promotes a standalone draft to the root. Draft practice pages stay in their
  practice set as described below.
- Keep operating practices under `practices/<set>/`. Each set has a `README.md` index,
  and each practice page carries publication front matter, a category, and topics.
  A practice page that is still a draft says `status: draft` in its front matter.
  Practice pages link to playbook sections instead of repeating them.

## Private-term check

With Python 3 and pre-commit available, run `pre-commit install` in your clone
to enable the configured commit hook. Run `python3 scripts/private_terms.py scan`
for a manual check. A match produces a file and line number and a nonzero exit
status; the output omits the matched text.

Keep private terms out of repository files, including tests and comments.
To extend the denylist, run `python3 scripts/private_terms.py add '<term>'`
locally and add only the printed digest to `DENIED_DIGESTS`. Use synthetic
terms in tests. See [the scanner's module documentation](scripts/private_terms.py)
for normalization, phrase limits, and scan scope.

## License

[MIT](LICENSE). Each playbook and practice credits its sources; quoted or adapted
third-party material keeps its own license.
