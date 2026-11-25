---
name: agent-reliability
description: "Apply site reliability engineering (SRE) practice to agents and AI products: SLOs, trace SLIs, autonomy, tool blast radius, eval-gated releases, drift, incidents, postmortems, capacity, toil, launch reviews. Use when a task designs, launches, gates, scopes, monitors or recovers an agent."
---

# Agent Reliability

Advisory guidance for running agents and AI products with SRE practice. This
entrypoint routes to one topic guide. Each guide writes only the document the
task asks for and hands decisions back to the accountable owner.

## Route to one topic

Read the guide whose row matches the task, and only that guide. Read a second
guide only when the first one names it as the next step.

| Topic | Use when the task | Guide |
| --- | --- | --- |
| `agentic-product-reliability-review` | Designs or launches an agent-backed product or a persistent agent | [guide](references/agentic-product-reliability-review/guide.md) |
| `agent-slo-design` | Defines SLIs, SLOs, burn-rate alerts or an error-budget policy for an agent workflow | [guide](references/agent-slo-design/guide.md) |
| `trace-based-slis` | Turns OpenTelemetry GenAI or MCP traces into task-level SLIs | [guide](references/trace-based-slis/guide.md) |
| `agent-autonomy-levels` | Grants an agent a new power such as merge, send, spend or deploy | [guide](references/agent-autonomy-levels/guide.md) |
| `tool-blast-radius` | Chooses credentials for an agent or unattended worker, or adds a tool or MCP server with write access | [guide](references/tool-blast-radius/guide.md) |
| `eval-gated-releases` | Changes a model, prompt, skill, tool schema or harness version | [guide](references/eval-gated-releases/guide.md) |
| `drift-and-quality-monitoring` | Builds or runs a recurring trace or quality review, or relies on an old eval | [guide](references/drift-and-quality-monitoring/guide.md) |
| `agent-incident-response` | Handles an active incident: a harmful agent action, a stalled fleet, a provider failure | [guide](references/agent-incident-response/guide.md) |
| `agent-postmortems` | Writes the review after an agent incident or a notable bad output | [guide](references/agent-postmortems/guide.md) |
| `agent-capacity-and-cost` | Adds agents or hosts, or responds to rising cost, quota or latency | [guide](references/agent-capacity-and-cost/guide.md) |
| `agent-toil-budget` | Measures or reduces the human time spent supervising agents | [guide](references/agent-toil-budget/guide.md) |

The guides refer to each other by these topic names. A topic name is a row in
this table, not a separate skill.

For backend service logging, metrics and service SLOs, use
`service-observability` instead.

## Authority

The guides are advisory. They write the requested document only. They do not
change autonomy grants, credentials, alerts or release gates; the accountable
owner decides and applies each change.

## Provenance

Each topic directory has a `PROVENANCE.md` that credits its sources and the
MIT-licensed [google-sre-skills](https://github.com/mawero83/google-sre-skills)
section shape.
