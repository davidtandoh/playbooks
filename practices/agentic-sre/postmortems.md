---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - reliability
  - evals
  - governance
---
# Postmortems for agent incidents

Run blameless postmortems where contributing factors include prompts, models,
tools, envelopes, and approval gates. Every postmortem changes an eval, a
skill or task specification, or an envelope.

Skill: `agent-postmortems` (see the [skill index](README.md#skills)).

## Sources

- [Google SRE book: Postmortem culture](https://sre.google/sre-book/postmortem-culture/)
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [Google SRE: AI in SRE, engineering reliable operations](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)
- [SRE Workbook: Example error budget policy](https://sre.google/workbook/error-budget-policy/)

## At a glance

| Output | Why |
| --- | --- |
| Timeline from traces | Memory is not evidence |
| Contributing factors | Task specification, skill or prompt, model, tool, envelope, observability gap, human approval |
| Risk category | One of the OWASP agentic risk categories, so months can be compared |
| Regression eval case | The failure cannot silently return |
| Specification or skill fix | The next agent receives better instructions |
| Autonomy or envelope change | Only when the evidence supports it |

## Decision guide

- If one incident consumes a large share of the error budget, then require a
  postmortem with a top-priority action. The SRE Workbook's example policy
  uses 20% of the budget as the threshold.
- If the cause looks like "the model got it wrong", then ask what made the
  action look right to the agent. Look at the task specification, context, and
  tool output.
- If the same failure appears in several postmortems, then raise it in the
  monthly review and consider an autonomy or envelope change.
- If engineers corrected the agent during the incident, then record each
  correction as a human-verified eval case.

## Checklist

- [ ] The timeline is built from traces.
- [ ] Contributing factors cover every layer in the table above.
- [ ] The failure is tagged with an agentic risk category.
- [ ] A regression eval case is added (see [Releases](releases.md)).
- [ ] Action items have owners and are tracked to closure.
- [ ] Patterns are reviewed monthly.

## Rules of thumb

- Stay blameless for humans and agents alike.
- A postmortem without a new eval case is incomplete.
- Action items without owners do not close.
- The quick failure-mode table in
  [Building Reliable Agents §7](../../building-reliable-agents.md#7-failure-mode--mitigation-quick-reference)
  is a useful prompt for the contributing-factors step.

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
