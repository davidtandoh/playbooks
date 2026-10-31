---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - evals
  - observability
  - reliability
---
# Drift and silent quality decay

Sample production regularly, grade it with calibrated judges, and watch the
distributions that move when inputs, models, tools, or judges change.

Skill: `drift-and-quality-monitoring` (see the [skill index](README.md#skills)).

## Sources

- [Google SRE: AI in SRE, engineering reliable operations](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/)
- [Stack Overflow Blog: Evals as a deployment gate, and how to know when they drift](https://stackoverflow.blog/2026/10/07/evals-as-a-deployment-gate-and-how-to-know-when-they-drift)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [Rabanser et al.: Towards a science of AI agent reliability](https://arxiv.org/abs/2602.16666)

## At a glance

| Drift source | Signal to watch |
| --- | --- |
| Input mix | Task types and turns per task |
| Model update | Model version on traces; refusal rate |
| Tool or API change | Tool mix and tool error rate |
| Cost | Tokens per task |
| Judge drift | Judge agreement with human labels |
| Calibration | Gap between stated confidence and observed success |

Google grades with a hybrid: a model judge for reasoning quality and
deterministic scoring for the final action. It tiers labels as bronze
(heuristic), silver (calibrated against gold), and gold (human-verified).

## Decision guide

- If you need gold labels cheaply, then record whether people accept, modify,
  or reject each agent suggestion during normal work.
- If a provider can update a model without notice, then pin versions, record
  them on traces, and alert on an unexpected change.
- If a metric drops, then confirm that the signal is real, localize it to a
  slice, find the cause, and fix it through the normal change process.
- If a judge has not been checked against human labels recently, then
  recalibrate it before you trust its trend.

## Checklist

- [ ] Production traces are sampled and graded on a fixed schedule, such as nightly against the last day's tasks.
- [ ] Judges are binary and calibrated against human labels.
- [ ] Distributions in the table above are monitored per agent and model version.
- [ ] Model versions are pinned and recorded on traces.
- [ ] Confirmed failures become eval cases (see [Releases](releases.md)).

## Rules of thumb

- Do not trust a judge that has never been compared with human labels.
- Offline evals alone do not detect drift.
- Read traces until you stop learning new failure types.
- Judge calibration and isolated rubrics are covered in
  [Building Reliable Agents §3](../../building-reliable-agents.md#3-reliability-engineering--surviving-non-determinism).
  Memory staleness and poisoning are listed in
  [§5](../../building-reliable-agents.md#5-the-rest-of-the-blind-spots-practice--research-thin-capture-and-revisit).

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
