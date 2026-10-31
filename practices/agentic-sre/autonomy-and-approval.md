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
# Autonomy and approval gates

Decide how much an agent may do without a human, one action type at a time.
Agents earn a higher level with evidence and lose it automatically when risk
rises.

Skills: `agent-autonomy-levels`, `agent-toil-budget` (see the
[skill index](README.md#skills)).

## Sources

- [Google SRE: AI in SRE, engineering reliable operations](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)
- [Knight First Amendment Institute: Levels of autonomy for AI agents](https://knightcolumbia.org/content/levels-of-autonomy-for-ai-agents-1)
- [Anthropic: Measuring agent autonomy](https://www.anthropic.com/research/measuring-agent-autonomy)
- [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [Google SRE book: Eliminating toil](https://sre.google/sre-book/eliminating-toil/)

## At a glance

Google's public autonomy ladder, in summary:

| Level | Who investigates | Who acts | Approval |
| --- | --- | --- | --- |
| L0 manual | Human | Human | Not applicable |
| L1 assisted | System | Human | Human approves and acts |
| L2 partial | System | System | Human approves each plan |
| L3 high | System | System | None, for well-defined scenarios only |
| L4 full | System | System | None, end to end, including rollback |

Google reports that its AI Operator runs at L2 for critical operations and at
L3 for minor incidents. Use that split as a starting default.

## Decision guide

- If an action is irreversible or reaches outside your system (merge, send,
  pay, deploy), then keep it at L2 or lower until it has an undo path.
- If an agent asks for a new permission, then grant it to one action type, not
  to the agent as a whole.
- If an agent has completed enough tasks at its current level with the error
  budget intact and no high-consequence policy breach, then consider one
  promotion. Write the evidence threshold down before the trial starts.
- If production is anomalous, an incident is open, a deployment is in flight,
  or the error budget burns fast, then demote L3 requests to L2 automatically
  and route them to a human.
- If humans approve almost every request without changes, then the gate has
  become a rubber stamp. Either promote the action with evidence or make each
  request carry more context.

## Checklist

- [ ] Each action type has a recorded level and an owner.
- [ ] Every action above L1 has an undo path or stays behind approval.
- [ ] Promotion criteria are written and measurable.
- [ ] Automatic demotion triggers are wired to live risk signals.
- [ ] The approval gate has its own indicators: approval latency, approve-without-change rate, and interrupt rate.
- [ ] Human attention per completed task is measured as toil, not ignored.

## Rules of thumb

- Grant no agent full access on day one.
- One global trust level per agent is too coarse. Record the level per action
  type.
- Count approval clicks, re-prompts, and clean-up of agent output as toil.
  Classic SRE guidance caps toil at about half of an engineer's time.
- Fix toil in this order: remove the need, automate it at L2 or higher, batch
  approvals, then accept what remains.
- Approval gates for high-stakes actions are already a build-time rule in
  [Building Reliable Agents §5](../../building-reliable-agents.md#5-the-rest-of-the-blind-spots-practice--research-thin-capture-and-revisit).
  This page adds the operating side: levels, promotion, and demotion.

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
