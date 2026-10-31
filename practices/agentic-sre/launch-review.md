---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - reliability
  - governance
  - delivery-gates
---
# Launch review for agentic products

Review reliability before you build and again before you launch. The review
pulls the other practice pages into one sign-off.

Skill: `agentic-product-reliability-review` (see the
[skill index](README.md#skills)).

## Sources

- [Google SRE book: Reliable product launches at scale](https://sre.google/sre-book/reliable-product-launches/)
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [AWS Well-Architected Agentic AI Lens: AGENTPERF01-BP01](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf01-bp01.html)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## At a glance

| Review step | Practice page |
| --- | --- |
| Critical user journeys and what correct means | This page |
| SLIs, targets, and error budget | [SLOs and error budgets](slos-and-error-budgets.md) |
| Autonomy level per action type | [Autonomy and approval gates](autonomy-and-approval.md) |
| Tool inventory and envelopes | [Blast radius](blast-radius.md) |
| Eval plan and release gates | [Releases](releases.md) |
| Tracing plan | [Observability](observability.md) |
| Drift monitoring | [Drift](drift.md) |
| Incident roles and runbooks | [Incidents](incidents.md) |
| Failure-mode table, rollback, degraded modes | This page |

## Decision guide

- If a hard user constraint exists, then enforce it with a deterministic check
  after the model, and treat a violation as high-consequence with a target of
  zero.
- If the model provider can fail, then define a degraded mode without the
  model, such as cached or rule-based results.
- If the product raises an operations agent above L2, then require
  fault-injection evidence from [Releases](releases.md).
- If the failure-mode table has no entry for a risk category, then add one or
  record why it does not apply.

## Checklist

- [ ] Each critical user journey states what a correct result means.
- [ ] SLOs, autonomy levels, and envelopes are agreed.
- [ ] The eval plan and release gates exist before launch.
- [ ] The tracing plan follows the OpenTelemetry GenAI conventions.
- [ ] The failure-mode table covers hallucination, wrong tool, loops, cost blowout, provider outage, prompt injection, data leak, memory poisoning, and inter-agent communication.
- [ ] Rollback and a degraded mode without the model are tested.
- [ ] An owner signs off the launch checklist.

## Rules of thumb

- Reliability added after launch costs more than reliability designed in.
- Every agent feature needs a fallback without the model.
- The full build-time checklist is in
  [Building Reliable Agents §6](../../building-reliable-agents.md#6-master-reliable-agent-checklist).
  Use it alongside this review.

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
