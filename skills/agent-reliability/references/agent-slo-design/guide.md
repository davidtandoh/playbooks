# Agent SLOs and Error Budgets

Define outcome-verified indicators, targets per consequence tier, and a
policy for exhausted error budgets.

## When to use

- A new agent, worker type, or AI product feature is about to launch.
- An existing agent fails often and nobody can say how often.
- Before agreeing an autonomy level (see `agent-autonomy-levels`).

## Principles

- Measure the user journey, not the model. One SLO per workflow slice.
- Use binary, evidence-checked indicators. A 1-10 judge score is not an SLI.
- Reliability is a profile: success, consistency, robustness, predictability
  and safety. Never average safety into the other four.
- The agent's own report is not evidence. Source every SLI from traces.

## Workflow

1. Name the journey per slice, for example "coding agent lands a change that
   passes checks" or "support agent resolves the ticket without escalation".
2. Choose SLIs from the [SLI catalogue](references/sli-catalogue.md). Include
   success, consistency (pass^k, cost and time variance over repeated runs),
   robustness (faults, tool-interface changes, rewording), and predictability
   (`calibration_delta`). Track safety separately.
3. Pick the primary latency indicator by agent class: time to first token for
   streaming assistants and end-to-end completion time for task and batch
   agents. Measure durations in seconds; track cost per task separately.
4. Set targets per consequence tier: tier 0 read-only, tier 1 reversible
   writes, tier 2 external or irreversible actions. Tier-2 policy breaches
   have a target of zero.
5. Define the error budget as 1 minus the target over a rolling 28 to 30 day
   window. Alert with two windows per threshold, as the
   [burn-rate reference](references/burn-rate-alerting.md) describes.
6. Write the error-budget policy from the template in the same reference,
   including exemptions and the single-incident postmortem rule.
7. Hand each SLI definition to `trace-based-slis` for computation.

## Decision guide

| Situation | Choose |
| --- | --- |
| One success is enough (search, drafting) | pass@k for capability; pass^1 for the SLO |
| Every run must succeed (payments, deploys) | pass^k with k equal to expected daily repeats |
| Low traffic, under 100 tasks per window | Longer window or synthetic probes; do not page on one failure |
| Tier-2 action involved | Separate zero-tolerance policy SLI with immediate page |
| Indicator needs a human label | Sample and label weekly; do not alert on it |

## Output template

```text
Journey: <slice and user outcome>
Class: streaming | task | batch       Tier: 0 | 1 | 2
SLI: <catalogue name> = <good events> / <valid events>, source: <trace query>
Target: <n>% over <window>            Budget: <1 - target>
Alerts: page <burn>x over <long>/<short>; ticket <burn>x over <long>/<short>
Policy: <link to signed budget policy>  Owner: <role>
```

## Example

Journey: task agent completes verified changes without reverts in 7 days
Targets: task_success_rate 85% over 28 days; false_completion_rate below 2%
Latency: response_latency_p95 below 600 seconds; cost tracked separately
Safety: policy_compliance 100% for required approvals

## Anti-patterns

- Uptime-only SLOs for an LLM feature.
- One threshold with no window, which pages on noise and recovers slowly.
- Averaging rare high-severity failures into a pool of low-impact ones.
- Freezing changes with no written policy, so nobody agrees when it ends.

## Related skills

`trace-based-slis`, `agent-autonomy-levels`, `eval-gated-releases`,
`agentic-product-reliability-review`, `agent-capacity-and-cost`.

## Authority boundary

Advisory. Read the workflow description, traces and metrics the user names.
Write only the requested SLO document. Do not create alerts, change
dashboards or freeze releases. Targets and the budget policy are decisions
for the service owner; hand them back for sign-off.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
