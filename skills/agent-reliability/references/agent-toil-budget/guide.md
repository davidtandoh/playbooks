# Agent Toil Budget

Count the human attention that agents consume, and spend it on purpose.

## When to use

- Supervising agents takes more time than doing the work.
- People relay results between sessions or tools by hand.
- Planning which work to automate next.

## Principles

- Toil is manual, repetitive, automatable, without lasting value, and grows
  with load. Keep it under about half of working time.
- Human attention is a cost. Measure it like spend.
- Remove the need for an intervention before automating it.
- Cheaper work raises demand. Keep the attention budget explicit.

## Workflow

1. List classic toil and agent toil: re-prompts per task, manual relays
   between agents, approval clicks, reviews of low-value changes, repairs of
   state that agents left behind, and chasing stalled sessions.
2. Measure from session data: human interventions per completed task,
   interrupt rate, auto-approve rate, and agent-initiated stops to ask.
3. Rank causes by total time spent.
4. Fix in this order: remove the need (better spec or skill), automate with
   an agent at L2 or higher, batch approvals, then accept and record it.
5. Re-measure the next week. Report the trend, not one week.

## Decision guide

| If | Then |
| --- | --- |
| The same re-prompt repeats | Fix the skill or task spec |
| Approvals are almost always granted | Batch them or promote the action one level |
| Agents stop to ask often, and answers are routine | Add the answer to the spec |
| Results are visible only inside one session | Send status to one shared channel |
| Fixing it costs more than a year of the toil | Accept it and record why |

## Output template

```text
Week: <date>   Completed tasks: <n>   Interventions/task: <n> (target <n>)
Interrupt rate: <n>%   Auto-approve rate: <n>%   Agent stops to ask: <n>
Top causes: <cause: minutes>
Fixes: <cause, fix type, owner, due>
```

## Example

```text
Weekly: 3.4 human interventions per merged change (target below 1.5). Top
cause: agent results were visible only inside their own sessions. Fix: send
status to one notification channel.
```

## Anti-patterns

- Automating toil by adding more supervision toil.
- Not counting human attention as a cost.
- Measuring once and never again.

## Related skills

`agent-autonomy-levels`, `trace-based-slis`, `agent-capacity-and-cost`,
`agent-postmortems`.

## Authority boundary

Advisory. Read session data, traces and time records the user names. Write
only the requested toil report. Do not change approval settings or automate
work; the user decides which fixes to fund.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
