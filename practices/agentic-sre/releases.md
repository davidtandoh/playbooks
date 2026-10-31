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
---
# Eval-gated releases and canaries

Ship prompt, model, skill, tool-schema, and harness changes as versioned
releases. Gate each one on evals per slice against a known-good baseline, then
canary it against live SLIs.

Skill: `eval-gated-releases` (see the [skill index](README.md#skills)).

## Sources

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

## Checklist

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

- [x] Every figure traces to a cited source or is labelled Own experience.
- [x] Every factual claim stays within the cited evidence.
- [x] Evidence limits and qualifiers remain explicit.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private-repository material.
- [x] No trace material.
- [x] No transcript material.
