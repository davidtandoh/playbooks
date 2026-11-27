---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - evals
  - delivery-gates
  - reliability
applies_when:
  - changing a model, system prompt, skill, tool schema, or agent framework version
signals:
  - model id
  - system prompt
  - prompt versioning
  - agent skill release
  - tool schema
  - canary
  - agent evaluation
path_globs:
  - "**/system_prompts/**"
  - "**/model_config.*"
  - "**/eval_suites/**"
  - "**/agent_canary/**"
key_rules:
  - Version prompts, skills, model ids, tool schemas, and harness versions, and record each on every trace. (#at-a-glance)
  - Gate each release per slice against the last known-good baseline. (#at-a-glance)
  - Canary on one worker pool or a small share of traffic and compare SLIs per version. (#at-a-glance)
  - Abort on quality regression even when infrastructure looks healthy. (#at-a-glance)
  - Do not swap models in one big step. (#rules-of-thumb)
  - Add incident cases to the eval set so it does not go stale. (#rules-of-thumb)
skills:
  - agent-reliability/eval-gated-releases
---
# Eval-gated releases and canaries

Ship prompt, model, skill, tool-schema, and harness changes as versioned
releases. Gate each one on evals per slice against a known-good baseline, then
canary it against live SLIs.

Skill: `agent-reliability`, topic `eval-gated-releases` (see the
[skill index](README.md#skills)).

## Sources

- [Anthropic: Scaling Managed Agents](https://www.anthropic.com/research/managed-agents):
  a model-specific context-reset workaround became unnecessary after an upgrade.
- [Stack Overflow Blog: Evals as a deployment gate, and how to know when they drift](https://stackoverflow.blog/2026/10/07/evals-as-a-deployment-gate-and-how-to-know-when-they-drift)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [SRE Workbook: Canarying releases](https://sre.google/workbook/canarying-releases/)
- [Clark et al.: SREGym](https://arxiv.org/abs/2605.07161)
- [Microsoft Agent SRE Governance 1.0](https://microsoft.github.io/agent-governance-toolkit/specs/AGENT-SRE-GOVERNANCE-1.0/)

## At a glance

1. Version the release artefacts: prompts, skills, model ids, tool schemas,
   and harness versions. Record each version on every trace.
2. Run the offline gate per slice, against the last known-good baseline.
3. Canary on one worker pool or a small share of traffic. Compare SLIs per
   version from traces.
4. Bake long enough to see multi-turn and long-session failures.
5. Abort on quality regression even when infrastructure looks healthy.

## Decision guide

- If a global score passes, then still check each slice. The Stack Overflow
  article notes that a 99% overall score can hide a 70% slice.
- If a metric moved, then compare it with the last known-good baseline, not
  only with a fixed floor. Re-baseline only after you validate a new
  known-good release. Never re-baseline automatically.
- If you fixed a bug, then keep its case as a permanent regression case.
- If the grader is new or changed, then add a test that proves the grader
  fails a wrong answer.
- If the change raises an operations agent's autonomy, then qualify it first on
  injected faults. Benchmarks such as SREGym inject faults across several
  layers and score diagnosis and mitigation.
- If you run chaos experiments on agents, then clamp the blast radius and
  define abort conditions before the run starts.
- When a model or harness changes, trial removing one obsolete workaround at a
  time against the unchanged known-good baseline. Keep authorization,
  isolation, privacy and audit controls outside the experiment.
- Keep a removal only after per-slice quality, safety, cost and latency checks
  pass; retain the evidence and a reversible configuration. For deployed
  service behaviour, use
  [post-deploy outcome checks](../engineering-standards/secure-reliable-systems.md#safe-rollout-and-rollback).

## Checklist

- [ ] Each workaround-removal trial changes one workaround, preserves mandatory controls and records baseline comparison and recovery.
- [ ] Every release artefact is versioned and recorded on traces.
- [ ] The golden eval set comes from real traces, including postmortem failures.
- [ ] Graders are binary, and each grader has a sensitivity test.
- [ ] Each slice has its own gate.
- [ ] The baseline is the last validated release.
- [ ] Shadow evals score a deterministic, hash-based sample of live tasks off the request path, and failures go to a review queue.
- [ ] Rollback to the previous configuration is one command.

## Rules of thumb

- Do not swap models in one big step.
- An eval set that never gains cases from incidents goes stale.
- The regression and capability suite split is in
  [Building Reliable Agents §3](../../building-reliable-agents.md#two-eval-suites-two-targets).
  Pinning and versioning configs together is in
  [§5](../../building-reliable-agents.md#5-the-rest-of-the-blind-spots-practice--research-thin-capture-and-revisit).

## Claim review

- [x] Workaround removal is a controlled experiment informed by a public example, not evidence that every workaround is obsolete.
- [x] Every figure traces to a cited source or is labelled Own experience.
- [x] Every factual claim stays within the cited evidence.
- [x] Evidence limits and qualifiers remain explicit.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private-repository material.
- [x] No trace material.
- [x] No transcript material.
