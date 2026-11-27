---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - reliability
  - governance
applies_when:
  - an agent takes a harmful action or a group of agents stalls
  - a model provider fails during operation
  - an AI product gives harmful output
signals:
  - incident
  - outage
  - runbook
  - on-call
  - kill switch
path_globs:
  - "**/runbooks/agent*/**"
  - "**/runbooks/*agent*.md"
  - "**/agent_incidents/**"
key_rules:
  - A human is the incident commander, never an agent. (#at-a-glance)
  - Agents investigate read-only and propose; the incident commander decides. (#at-a-glance)
  - Make every change through one actuation path with pre-flight checks. (#at-a-glance)
  - Mitigate first; do not root-cause while damage continues. (#rules-of-thumb)
  - Do not lose transcripts before analysis. (#rules-of-thumb)
skills:
  - agent-reliability/agent-incident-response
---
# Incident response for agent systems

Mitigate first, keep a human as incident commander, and let agents do the
searching. Separate read-only investigation from every action that changes
state.

Skill: `agent-reliability`, topic `agent-incident-response` (see the
[skill index](README.md#skills)).

## Sources

- [The Pragmatic Engineer: AI SRE](https://newsletter.pragmaticengineer.com/p/ai-sre): public sections 1–3
  describe independent verification and operational-memory validation; the paid
  accuracy section is not used.
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

### Disconfirm hypotheses and validate memory

For each leading hypothesis, name a predicted observation and a check that
could refute it. Use a separate read-only verification pass to examine the
underlying evidence and at least one credible alternative. Keep missing evidence
and unresolved contradictions explicit. Each recommendation names its expected
effect, risks, recovery path and the observation that would show it failed.
The incident commander keeps decision authority.

Keep new incident notes provisional in the existing incident or memory record.
Promote a note to `Activated` only after its claim is validated or its usefulness
is verified. Mark a contradicted or stale note `Quarantined`; exclude it from
causal claims and retrieval used to guide action until revalidation. Preserve
its source, date, exclusion reason and superseding evidence. These are two
operational states for reusable notes, not a new memory store or a claim that
provisional notes are verified facts.

Keep assistance quiet by default. Surface evidence when someone claims
“mitigated” without an outcome check, or announces a risky action without a
rollback or recovery plan. Route the concern to the incident commander. Quiet
assistance never suppresses pages, delays critical or unknown alerts, or grants
permission to act.

## Checklist

- [ ] A separate verification pass records disconfirming checks, a credible alternative and unknowns.
- [ ] Reusable notes have validated Activated or excluded Quarantined status; new notes remain provisional.
- [ ] Unproved mitigation and risky actions without recovery plans reach the commander without suppressing alerts.
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

- [x] Hypothesis and memory controls adapt the public AI SRE examples; they make no incident-accuracy claim.
- [x] Every figure traces to a cited source or is labelled Own experience.
- [x] Every factual claim stays within the cited evidence.
- [x] Evidence limits and qualifiers remain explicit.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private-repository material.
- [x] No trace material.
- [x] No transcript material.
