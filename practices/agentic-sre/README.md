# Agentic SRE practices

Site reliability engineering (SRE) practices for running products that use AI
agents or large language models. Each page is a short, link-heavy operating
practice. The build-time guidance lives in
[Building Reliable Agents](../../building-reliable-agents.md); these pages
link to its sections instead of repeating them.

## Start here

1. Read [SLOs and error budgets](slos-and-error-budgets.md) to decide what
   "working" means.
2. Read [Autonomy and approval gates](autonomy-and-approval.md) and
   [Blast radius](blast-radius.md) to decide what an agent may do.
3. Use [Launch review](launch-review.md) as the sign-off that pulls the other
   pages together.

## Map

```text
Before launch        Change            Operate              Learn
-------------        ------            -------              -----
Launch review   ->   Releases     ->   Observability   ->   Postmortems
  SLOs                 (eval gate,       Drift                 |
  Autonomy              canary)          Incidents             |
  Blast radius                                                 |
      ^                                                        |
      +---------- new eval cases, envelope and level changes --+
```

Takeaway: postmortems feed evals and autonomy decisions back into the next
release.

## Practices

| Practice | Skills | What it covers |
| --- | --- | --- |
| [Autonomy and approval gates](autonomy-and-approval.md) | `agent-autonomy-levels`, `agent-toil-budget` | L0 to L4 levels per action type, promotion with evidence, automatic demotion, approval toil |
| [Blast radius](blast-radius.md) | `tool-blast-radius` | Tool inventory, distinct identities, envelopes, dry run, circuit breakers, emergency stop |
| [SLOs and error budgets](slos-and-error-budgets.md) | `agent-slo-design`, `agent-capacity-and-cost` | Named SLIs, consequence tiers, multiwindow burn-rate alerting, budget policy, capacity |
| [Observability](observability.md) | `trace-based-slis` | SLIs computed from OpenTelemetry GenAI and MCP spans |
| [Releases](releases.md) | `eval-gated-releases` | Per-slice eval gates, baselines, shadow evals, canaries, fault qualification |
| [Drift](drift.md) | `drift-and-quality-monitoring` | Sampling, calibrated judges, label tiers, drift signals |
| [Incidents](incidents.md) | `agent-incident-response` | Human commander, read-only investigation, runbook contract, mitigation first |
| [Postmortems](postmortems.md) | `agent-postmortems` | Blameless factors across prompts, models, tools, and gates; every postmortem adds an eval |
| [Launch review](launch-review.md) | `agentic-product-reliability-review` | Pre-build and pre-launch sign-off across all practices |

## Skills

Each practice names one or more agent skills by id. A skill is the
agent-executable form of a practice. The canonical copy of each skill lives in
Personal Agent Kit at `skills/<id>/SKILL.md`, which is published separately
from this repository.

| Skill id | Personal Agent Kit path | Practice |
| --- | --- | --- |
| `agent-autonomy-levels` | `skills/agent-autonomy-levels/` | [Autonomy and approval gates](autonomy-and-approval.md) |
| `agent-capacity-and-cost` | `skills/agent-capacity-and-cost/` | [SLOs and error budgets](slos-and-error-budgets.md) |
| `agent-incident-response` | `skills/agent-incident-response/` | [Incidents](incidents.md) |
| `agent-postmortems` | `skills/agent-postmortems/` | [Postmortems](postmortems.md) |
| `agent-slo-design` | `skills/agent-slo-design/` | [SLOs and error budgets](slos-and-error-budgets.md) |
| `agent-toil-budget` | `skills/agent-toil-budget/` | [Autonomy and approval gates](autonomy-and-approval.md) |
| `agentic-product-reliability-review` | `skills/agentic-product-reliability-review/` | [Launch review](launch-review.md) |
| `drift-and-quality-monitoring` | `skills/drift-and-quality-monitoring/` | [Drift](drift.md) |
| `eval-gated-releases` | `skills/eval-gated-releases/` | [Releases](releases.md) |
| `tool-blast-radius` | `skills/tool-blast-radius/` | [Blast radius](blast-radius.md) |
| `trace-based-slis` | `skills/trace-based-slis/` | [Observability](observability.md) |

## Credits

- The skill format follows
  [mawero83/google-sre-skills](https://github.com/mawero83/google-sre-skills)
  (MIT). No text from that project is reproduced here.
- Concepts draw on Google's
  [SRE books](https://sre.google/books/) and the
  [AI in SRE](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)
  page. This work is not affiliated with Google.
- SRE Workbook content is licensed CC BY-NC-ND 4.0. These pages restate its
  figures as facts in original wording and cite the source.
- Each page lists its own primary sources. All wording is original.
