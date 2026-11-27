# Incident Response for Agent Systems

Stop harmful actions first. Keep investigation read-only and decisions
and mutations with a human.

## When to use

- An agent took a wrong or irreversible action.
- Many agents stall at once, for example after a host runs out of memory.
- A model provider outage or a storm of rate-limit errors.
- An AI product returns harmful output to users.

## Principles

- A human is the incident commander. An agent never holds that role.
- Investigation is read-only. Mutations go through one actuation path with
  pre-flight checks.
- Mitigate before you find the root cause.
- Evidence is preserved before anyone cleans up.
- Independently check each leading hypothesis for disconfirming evidence.
  Record the competing explanation and the observation that would reject it
  before recommending remediation.
- Keep operational memory notes unverified until verified utility or explicit
  human review earns `Activated` status. Move contradicted notes to
  `Quarantined`; exclude them from investigation context until revalidated.
  Use the existing incident record or memory store, not a parallel store.
- Keep incident assistance quiet by default. Escalate an unanswered question,
  a stakeholder joining without context, an unproved claim of mitigation, or
  a proposed risky action without a rollback plan. Escalation grants no
  mutation authority.

## Workflow

1. Declare early. Name the incident commander (human), operations lead (an
   agent may assist at L1 or L2), and communications lead.
2. Mitigate with the stop control: pause in-flight actions, block new ones,
   revoke L3 permissions. Then roll back configuration or model, switch a
   feature flag, or switch provider.
3. Run agents read-only to correlate traces, logs, recent changes and past
   postmortems. Agents propose; the commander decides.
4. Send every approved mutation through the single actuation path. Its
   pre-flight checks run a dry run, record the justification, and check
   concurrency with other changes.
5. Attempt the approved remediation, then allow at most one retry through
   the same actuation path if the runbook permits it and pre-flight checks
   and approval pass again. After a failed retry, stop and escalate. Unsafe
   state or an unmet retry condition requires immediate escalation.
6. Follow a runbook when one exists. Use the
   [runbook contract](references/runbook-contract.md) for new runbooks.
7. Preserve traces, transcripts, prompts and tool outputs, redacted.
8. Classify the cause: model behaviour, prompt or skill, tool, infrastructure,
   human approval, or provider. Exit with a state summary and a postmortem.

## Decision guide

| If | Then |
| --- | --- |
| The agent is still acting | Pause and block first, investigate second |
| One agent is affected | Open its circuit breaker and keep others running |
| Many agents behave the same wrong way | Suspect a shared change: model, prompt, tool or provider |
| Rollback would remove needed fixes | Prefer a feature flag or a fix forward |
| Observed state diverges from the runbook | Retry only for the declared retryable outcome; otherwise stop |

## Output template

```text
Incident: <id>  Severity: <n>  Commander: <human>  Started: <time>
Impact: <users, actions, data>
Mitigation: <stop actions taken>, <rollback or flag>
Investigation: <agent findings with evidence links>
Mutations: <action>, approved by <role>, dry run <result>
Cause class: model | prompt/skill | tool | infra | approval | provider
Next: postmortem owner <role>, due <date>
```

## Example

Hypothetical Sev2: memory pressure prevents workers from starting. The
commander pauses new work and approves a restart through the runbook.

## Anti-patterns

- Letting an agent act as incident commander.
- Root-causing while the damage continues.
- Agents mutating production from their investigation session.
- Losing transcripts before the analysis.

## Related skills

`agent-postmortems`, `tool-blast-radius`, `agent-autonomy-levels`,
`trace-based-slis`, `agent-capacity-and-cost`.

## Authority boundary

Advisory and read-only. Read traces, logs and change history the commander
names. Write only the requested incident record or runbook draft. Do not run
mitigations or mutations; the incident commander approves and executes them.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
