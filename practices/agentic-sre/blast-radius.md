---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - security-and-privacy
  - reliability
  - governance
---
# Blast radius for agent tools

Limit the damage an agent's tools can do before the agent uses them. Put the
limits in deterministic code downstream of the model, not in the prompt.

Skill: `tool-blast-radius` (see the [skill index](README.md#skills)).

## Sources

- [Google SRE: AI in SRE, engineering reliable operations](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)
- [Microsoft Agent SRE Governance 1.0](https://microsoft.github.io/agent-governance-toolkit/specs/AGENT-SRE-GOVERNANCE-1.0/)
- [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [Simon Willison: The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [Building Secure and Reliable Systems](https://google.github.io/building-secure-and-reliable-systems/)

## At a glance

| Control | What it does |
| --- | --- |
| Tool inventory | Lists each tool, memory store, and inter-agent channel with read or write, reversibility, external reach, and data reached |
| Distinct identity | Gives each agent its own short-lived, scoped credentials; no shared or developer credentials |
| Hard envelope | Caps tokens, cost, tool calls, wall-clock time, and delegation depth per task |
| Dry run | Predicts the effect of a mutating call before production state changes |
| Circuit breaker | Stops an agent after repeated consecutive failures |
| Emergency stop | Pauses in-flight actions, blocks new actions, and revokes L3 permissions fleet-wide |

## Decision guide

- If a tool can mutate state, then require a `dry_run` mode and call it first
  for every L2 or higher action. Google requires this of systems meant for
  agent use.
- If one agent could combine private data, untrusted content, and an external
  send, then split the capability. Do not run that combination unattended.
- If an agent fails several calls in a row, then open its circuit breaker and
  require a manual reset. Microsoft's spec defaults to five consecutive
  failures and manual recovery.
- If an outage is fleet-wide, then use the emergency stop. Keep pause, block,
  and revoke as three separate actions so that you can use the smallest one.
- If a credential is shared across agents, then replace it before you raise any
  agent's autonomy level.

## Checklist

- [ ] Every tool, memory store, and inter-agent channel is in the inventory with a consequence tier.
- [ ] Each agent has its own identity and least-privilege, short-lived credentials.
- [ ] Per-task envelopes are enforced in code, and exceeding one pauses the task and notifies the owner.
- [ ] Mutating tools support dry run.
- [ ] Circuit breakers and the three-action emergency stop exist and have been exercised.
- [ ] Protected zones (password managers, payments, second-factor screens) are blocked in code where possible.
- [ ] A stopped agent keeps its trace for the postmortem.

## Rules of thumb

- Authorization lives downstream of the model. A system prompt is not a
  control.
- Cap loops that call a paid model. An unlimited loop is a cost incident.
- Environment-layer containment, prompt-injection defences, and egress
  controls are covered in
  [Building Reliable Agents §4](../../building-reliable-agents.md#4-security--prompt-injection--the-dominant-agent-risk).
  This page adds the operating envelope and stop controls.

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
