---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - reliability
  - observability
  - cost
---
# SLOs and error budgets for agents

Measure agent reliability as a profile of binary, outcome-verified indicators.
Set targets per consequence tier and alert on burn rate over two windows.

Skills: `agent-slo-design`, `agent-capacity-and-cost` (see the
[skill index](README.md#skills)).

## Sources

- [Microsoft Agent SRE Governance 1.0](https://microsoft.github.io/agent-governance-toolkit/specs/AGENT-SRE-GOVERNANCE-1.0/)
- [Rabanser et al.: Towards a science of AI agent reliability](https://arxiv.org/abs/2602.16666)
- [SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [SRE Workbook: Example error budget policy](https://sre.google/workbook/error-budget-policy/)
- [AWS Well-Architected Agentic AI Lens: AGENTPERF01-BP01](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf01-bp01.html)
- [Arthur: Agent reliability SLAs](https://www.arthur.ai/column/agent-reliability-slas-how-to-set-slos-for-probabilistic-systems)
- [Google SRE book: Handling overload](https://sre.google/sre-book/handling-overload/)

## At a glance

Service level indicators (SLIs) to start from. The first eight are the
built-in SLIs in Microsoft's spec.

| SLI | Measures |
| --- | --- |
| `TaskSuccessRate` | Tasks that reach the verified outcome |
| `ToolCallAccuracy` | Tool calls that are correct and succeed |
| `ResponseLatency` | Latency for the agent class (see below) |
| `CostPerTask` | Spend per task, retries included |
| `PolicyCompliance` | Actions within policy |
| `DelegationChainDepth` | Depth of sub-agent delegation |
| `HallucinationRate` | Outputs with unsupported claims |
| `CalibrationDeltaSLI` | Gap between stated confidence and observed success |
| False completion | Agent claims done without evidence |
| No progress | Loops and stuck sessions |
| Human repair | Tasks a human had to fix |

## Decision guide

- If the agent streams to a user, then the primary latency indicator is time
  to first token. If it completes tasks, then use end-to-end completion time.
  If it runs in batch, then lead with cost per task. AWS's lens makes the same
  class split.
- If a failure is high-consequence (external or irreversible), then set a
  target of zero and keep it out of any averaged indicator.
- If consistency matters, then measure success over repeated runs of the same
  task, not one run. The reliability paper also measures robustness under
  injected faults and prompt rewording.
- If you page, then require both a long window and a short window to burn.
  The SRE Workbook's example for a 99.9% target pages at about 14x over one
  hour and 6x over six hours, and tickets at 1x over three days. It sets each
  short window to about one twelfth of its long window.
- If the budget is exhausted, then apply the written policy: freeze prompt,
  model, and harness changes for that workflow and spend the effort on
  reliability.

## Checklist

- [ ] Each indicator is defined per user journey, not per model.
- [ ] Every indicator is pass or fail with evidence, and comes from traces, not from the agent's self-report.
- [ ] Targets are set per consequence tier.
- [ ] The error-budget window and burn thresholds are written down. Microsoft's defaults are a 30-day window, warning at 2x, and critical at 10x.
- [ ] The error-budget policy names exemptions and exhaustion actions.
- [ ] Capacity indicators cover queue wait, host memory pressure, and provider rate-limit errors.
- [ ] Admission control queues work instead of overloading a host or a provider quota.

## Rules of thumb

- Uptime alone is not an SLO for an agent.
- Do not use one-to-ten judge scores as indicators. Use pass or fail.
- Rare, severe failures disappear when averaged with common, minor ones.
- The pass@k and pass^k definitions and cost-per-task instrumentation are in
  [Building Reliable Agents §3](../../building-reliable-agents.md#measure-reliability-with-the-right-metric)
  and [§2](../../building-reliable-agents.md#measure-cost-per-task-not-just-accuracy).
- Count retries in cost. Discover provider quotas in a load test, not in an
  incident.

## Claim review

- [x] Every figure traces to a cited source or is labelled Own experience.
- [x] Every factual claim stays within the cited evidence.
- [x] Evidence limits and qualifiers remain explicit.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private-repository material.
- [x] No trace material.
- [x] No transcript material.
