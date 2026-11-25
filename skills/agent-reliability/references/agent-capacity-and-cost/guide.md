# Capacity and Cost for Agent Workloads

Know the limits before an incident finds them, and price each successful task.

## When to use

- Host memory or CPU pressure, or adding a new agent host.
- Provider rate-limit (HTTP 429) or unavailable (HTTP 503) errors.
- Pricing an AI product or setting a monthly budget.

## Principles

- Queue work rather than overload a host or a provider.
- Count retries in cost. A failed attempt still costs money.
- Cost per successful task is a unit-economics metric and an SLI.
- Find quotas in a plan, not in an incident.

## Workflow

1. Model demand: concurrent agents x tokens per turn x turns per task, for
   peak and for average load.
2. Track resource SLIs: start latency, queue wait, memory and swap, provider
   429 and 503 rates, and quota headroom.
3. Set admission control: a maximum number of concurrent agents per host and
   per provider key; queue the rest.
4. Define degraded modes: a cheaper model, deferral of non-urgent work, or
   reduced context size.
5. Track `cost_per_task`: all spend, including failed and retried attempts,
   divided by successful tasks. Alert on drift from the agreed budget.
6. Load-test a new host with a realistic mix of agent work before moving
   production work to it.
7. Recheck when the model, the prompt size or the agent count changes.

## Decision guide

| If | Then |
| --- | --- |
| Memory pressure stays high | Lower the concurrency cap, then add a host |
| 429 errors rise | Add backoff and a per-key cap before adding keys |
| Cost per task rises, success is flat | Look for retries, loops and context growth |
| Demand peaks are predictable | Schedule background work off-peak |
| A provider has no fallback | Add a second provider or a degraded mode |

## Output template

```text
Workload: <name>   Peak agents: <n>   Tokens/task: <n>   Tasks/day: <n>
Host caps: <agents per host>   Provider caps: <requests and tokens per minute>
Quota headroom: <n>%   Degraded mode: <behaviour>
Cost per successful task: <amount> (budget <amount>)
Alerts: <signal, threshold, duration>
```

## Example

```text
One host: cap 4 concurrent agents. A second host takes background work.
Alert when memory pressure or swap stays above 80% for 10 minutes.
```

## Anti-patterns

- Unbounded parallel agents.
- Ignoring retries in cost.
- Discovering quotas during an incident.

## Related skills

`agent-slo-design`, `tool-blast-radius`, `agent-incident-response`,
`agentic-product-reliability-review`.

## Authority boundary

Advisory. Read usage data, billing exports and host metrics the user names.
Write only the requested capacity or cost plan. Do not change caps, quotas,
keys or spend limits; the budget owner decides.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
