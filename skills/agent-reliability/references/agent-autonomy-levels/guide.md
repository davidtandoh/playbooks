# Autonomy Levels and Approval Gates

Grant autonomy per action type, earn it with evidence, and take it back
automatically when risk rises.

## When to use

- An agent requests a new permission.
- Deciding whether an agent may merge, send, spend or deploy without asking.
- Designing an AI product feature that acts for its users.

## Principles

- Autonomy is set per action type, not per agent.
- No action runs without an undo path. Irreversible actions stay behind a
  human approval gate.
- An approval gate is a reliability control with its own SLIs.
- Autonomy is earned with evidence and removed without debate.

## Workflow

1. Assign each action type one level:

   | Level | Name | Who acts |
   | --- | --- | --- |
   | L0 | Manual | A human investigates and acts. |
   | L1 | Assisted | The agent investigates and recommends; a human acts. |
   | L2 | Partial | The agent acts after a human approves each plan. |
   | L3 | High | The agent acts without approval inside bounded scenarios. |
   | L4 | Full | The agent runs multi-step work end to end inside an envelope. |

2. Measure each gate: approval latency, interrupt rate, auto-approve or
   rubber-stamp rate, and the rate at which the agent stops itself to ask.
3. Promote one level only with evidence: a minimum count of tasks at the
   current level with the error budget intact, zero tier-2 violations, and,
   for operations agents, a passing run in a fault environment (see
   `eval-gated-releases`).
4. Demote automatically. Downgrade an L3 request to L2 when risk is elevated:
   an active incident, a fast error-budget burn, a deployment in flight, or a
   change-freeze window.
5. Record the level, the evidence and the approver for each action type.

## Decision guide

| If the action is | Then start at |
| --- | --- |
| Read-only investigation | L1, promote to L3 quickly |
| Reversible write (branch, draft, staging change) | L2 |
| External or irreversible (merge to production, send, spend) | L1 or L2; L3 only with a signed budget policy |
| A user-facing action taken for a customer | L1 until user acceptance is measured |
| Unchanged after a model or harness swap | Re-qualify; do not carry the old level over |

## Output template

```text
Action type: <verb on resource>     Tier: 0 | 1 | 2
Current level: L<n>   Proposed: L<n>   Approver: <role>
Evidence: <tasks at level>, <budget status>, <tier-2 violations>, <fault-run result>
Demotion triggers: <incident | burn rate | deploy in flight | freeze>
Gate SLIs: approval latency <p95>, auto-approve rate <n>%
```

## Example

```text
Merge policy: L3 for changes to low-risk repositories once checks pass;
L2 for production configuration and infrastructure; drops to L2 for all
repositories while an incident is open. Sending email for a user stays L1.
```

## Anti-patterns

- Full access on the first day.
- One global trust level for every action.
- Approval prompts so frequent that people approve without reading.
- Promotion based on how capable the model seems rather than on measured runs.

## Related skills

`tool-blast-radius`, `agent-slo-design`, `eval-gated-releases`,
`agent-toil-budget`, `agent-incident-response`.

## Authority boundary

Advisory. Read the action inventory, traces and SLO status the user names.
Write only the requested autonomy record. Do not grant, revoke or change
permissions. The accountable owner approves every level change.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
