# Reliability Review for Agentic Products

Decide before launch what "correct" means, how you will know, and what
happens when it fails.

## When to use

- A product idea is moving to build.
- Pre-launch sign-off.
- Explaining reliability to users, buyers or regulators.

## Principles

- Reliability is designed in before launch, not added after.
- Every AI path has a degraded mode that works without the model.
- Deterministic checks enforce hard constraints after the model.
- One complete failure-mode list beats a list of recent surprises.

## Workflow

1. Define the critical user journeys and what "correct" means for each.
2. Run `agent-slo-design`, `agent-autonomy-levels` and `tool-blast-radius`.
   Use the named SLIs and the class-specific latency indicator.
3. Write the eval plan and release gates, and plan fault-environment and
   chaos runs before any L3 action (see `eval-gated-releases`).
4. Plan tracing with the OpenTelemetry GenAI conventions (`trace-based-slis`).
5. Fill the [failure-mode table](references/failure-modes.md): every row gets a
   control, a detection signal and an owner, or a written acceptance.
6. Define rollback and degraded modes, including a path without AI.
7. Record the launch checklist sign-off.

## Decision guide

| If | Then |
| --- | --- |
| A hard user constraint exists | Enforce it with a deterministic checker; tier 2, target 0 |
| The feature acts for users | Start at L1; measure acceptance before promotion |
| No path works without the model | Block launch until a degraded mode exists |
| A failure-mode row has no control | Accept it in writing or block launch |
| The feature uses memory or other agents | Add poisoning and inter-agent rows explicitly |

## Output template

```text
Product: <name>   Review date: <date>   Reviewers: <roles>
Journeys: <journey: correct means>
SLOs: <link>   Autonomy: <link>   Envelope: <link>
Eval plan: <suites, gates>   Fault testing: <plan>
Failure modes: <link to completed table>
Degraded mode: <behaviour without AI>   Rollback: <method>
Decision: launch | launch with conditions | block   Conditions: <list>
```

## Example

```text
Recommendation app. Journey: output respects the user's hard constraints.
A constraint violation is tier 2 with target 0, enforced by a deterministic
checker after the model. SLO: 90% user acceptance. If the model provider is
down, serve cached or rule-based results.
```

## Anti-patterns

- Reliability added after launch.
- No path that works without the model.
- A failure-mode table without owners.

## Related skills

`agent-slo-design`, `agent-autonomy-levels`, `tool-blast-radius`,
`eval-gated-releases`, `trace-based-slis`, `agent-capacity-and-cost`.

## Authority boundary

Advisory. Read design documents, configuration and evidence the user names.
Write only the requested review record. Do not approve a launch; the
accountable product owner signs off.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
