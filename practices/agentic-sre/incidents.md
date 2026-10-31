---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - reliability
  - governance
---
# Incident response for agent systems

Mitigate first, keep a human as incident commander, and let agents do the
searching. Separate read-only investigation from every action that changes
state.

Skill: `agent-incident-response` (see the [skill index](README.md#skills)).

## Sources

- [Google SRE: AI in SRE, engineering reliable operations](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)
- [Google SRE book: Managing incidents](https://sre.google/sre-book/managing-incidents/)
- [medzin/sre-runbook-agent-skills](https://github.com/medzin/sre-runbook-agent-skills)
- [Anthropic cookbook: The SRE incident response agent](https://platform.claude.com/cookbook/claude-agent-sdk-03-the-site-reliability-agent)
- [AI Incident Database](https://incidentdatabase.ai/)

## At a glance

| Role | Who | Notes |
| --- | --- | --- |
| Incident commander | Human | Decides. Never an agent. |
| Investigation | Agent or human | Read-only: correlate traces, logs, recent changes, and prior postmortems |
| Operations | Human, or an agent at L1 or L2 | Every change goes through one actuation path with pre-flight checks |
| Communications | Human | Owns status updates |

Google runs its alert-enrichment agent read-only and gives actuation to a
separate agent behind pre-flight checks. Use the same split.

## Decision guide

- If damage continues, then mitigate before root cause: pause agents, roll back
  the prompt, model, or configuration, flip a feature flag, or switch provider.
- If a standard remediation did not help after one attempt, then escalate to a
  human. Do not let an agent retry the same fix in a loop.
- If many changes landed in quick succession, then prefer a feature flag or a
  fix forward over a rollback to the last known-good version. Google calls
  this the intervening pull request problem: the rollback can remove needed
  fixes.
- If observed state diverges from the runbook, then the agent stops and hands
  back to the incident commander.

## Checklist

- [ ] The incident is declared early and the three human roles are named.
- [ ] Investigation agents have read-only access.
- [ ] Runbooks state trigger, read-only diagnostics, risk-tiered actions, expected result after each step, rollback, escalation, and a stop rule.
- [ ] Traces, prompts, tool outputs, and transcripts are preserved, redacted, before analysis.
- [ ] The cause is classified: model behaviour, prompt or skill, tool, infrastructure, human approval, or provider.
- [ ] The incident exits with a state document and a [postmortem](postmortems.md).

## Rules of thumb

- Agents propose; the incident commander decides.
- Do not root-cause while damage continues.
- Do not lose transcripts before analysis.
- Use the emergency stop from [Blast radius](blast-radius.md) when the
  incident is fleet-wide.
- Retry and timeout mechanics belong to the build, not the incident. See
  [Building Reliable Agents §3](../../building-reliable-agents.md#3-reliability-engineering--surviving-non-determinism).

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
