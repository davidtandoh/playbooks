# Failure-Mode Table for Agentic Products

Fill one row per failure mode. Each row needs a control, a detection signal
and an owner, or a written acceptance of the risk.

## Reliability failure modes

| Failure mode | Typical control | Detection signal |
| --- | --- | --- |
| Unsupported output (hallucination) | Grounding, deterministic checks | `hallucination_rate` |
| Wrong tool or wrong arguments | Schemas, dry run | `tool_call_accuracy` |
| Loop or stall | Envelope limits, breaker | Loop suspects, gaps between turns |
| Cost overrun | Per-task budget | `cost_per_task` |
| Provider outage or rate limiting | Fallback provider, degraded mode | Provider error rate |
| False completion | Evidence-checked outcomes | `false_completion_rate` |
| Silent quality drift | Production sampling | Pass-rate trend |

## Security failure modes

The categories below are the OWASP Top 10 for Agentic Applications for 2026
(OWASP GenAI Security Project, published 2025-12-09). Names are cited as
category labels; descriptions are original.

| Category | Ask |
| --- | --- |
| Agent goal hijack | Can untrusted content change what the agent is trying to do? |
| Tool misuse | Can a permitted tool be used for an unintended purpose? |
| Identity and privilege abuse | Does the agent act with more privilege than its task needs? |
| Agentic supply chain | Are tools, skills, prompts and models from verified sources? |
| Unexpected code execution | Can the agent run code it generated or received? |
| Memory and context poisoning | Can someone write to memory the agent later trusts? |
| Insecure inter-agent communication | Are messages between agents authenticated? |
| Cascading failures | Can one agent's failure spread to others? |
| Human-agent trust exploitation | Can the agent persuade a person to approve a bad action? |
| Rogue agents | Can an agent act outside its envelope without detection? |

## Row format

```text
<failure mode> | control: <control> | signal: <SLI or alert> | owner: <role> | accepted: <no | yes, by role, date>
```
