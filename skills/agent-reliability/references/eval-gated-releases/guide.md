# Eval-Gated Releases and Canaries

Detect immediate and gradual regressions before a change reaches all traffic.

## When to use

- Swapping a model or model version, or changing a system prompt or skill.
- Upgrading the agent framework, harness or orchestration layer.
- Shipping an AI feature in a product.

## Principles

- Prompts, skills, model ids, tool schemas and harness versions are release
  artifacts. Version and sign them, and tag every trace with the versions.
- Gate each slice separately. A high global score can hide a failing slice.
- Compare with the last known-good baseline, not only an absolute floor.
- Quality regressions abort a release even when infrastructure is healthy.

## Workflow

1. Record artifact versions and signatures on every trace.
2. Keep two suites. The regression suite stays near 100% and holds every
   fixed failure permanently. The capability suite starts low; move a case to
   regression when it passes reliably.
3. Include a scorer sensitivity test: prove each grader fails a known wrong
   answer.
4. Offline gate: compare each slice with the last known-good baseline. Gate
   pass^k repeated-run consistency, cost and time variance, perturbation
   robustness (tool faults, tool-interface changes, rewording), and
   `calibration_delta` against agreed limits. Gate safety separately; allow
   no tier-2 safety regression.
5. Never rebaseline automatically. A human approves a new baseline.
6. Shadow: evaluate the candidate on a deterministic-hash sample of live
   task ids, off the request path. Isolate candidate side effects and keep
   candidate outputs from users. Record the hash rule and sample size. Apply
   the offline per-slice gates against the baseline before any canary.
7. Canary: route a small traffic share to the candidate. Compare version SLIs.
8. Observe multi-turn and long-session failures before promotion. Qualify
   operations agents in a fault environment before L3; see the
   [chaos reference](references/chaos-experiments.md).
9. Roll back with one command. If rollback would remove needed fixes made by
   later changes, prefer a feature flag or a fix forward.

## Decision guide

| If | Then |
| --- | --- |
| Global score passes, one slice fails | Block the release |
| Score is within margin of the floor but below baseline for 3 releases | Block and investigate gradual regression |
| Grader passes a known wrong answer | Fix the grader before trusting the gate |
| Canary infrastructure is green, task success drops | Abort and roll back |
| Many changes landed after the bad one | Disable by flag or fix forward |

- Trial removing one model-specific workaround at a time against the unchanged
  known-good baseline. Keep authorization, isolation, privacy and audit controls
  outside the experiment.
- Retain a removal only after per-slice quality, safety, cost and latency checks
  pass. Record evidence and a reversible configuration. Verify deployed service
  outcomes with the
  [safe rollout guidance](../../../../practices/engineering-standards/secure-reliable-systems.md#safe-rollout-and-rollback).

## Output template

```text
Change: <artifact and version>   Baseline: <version>
Offline: regression <n>/<n>; per slice <slice: score vs baseline>;
  pass^k <n>; cost/time variance <n>; robustness <n>; calibration_delta <n>
Safety: <separate result>   Scorer sensitivity: pass | fail
Shadow: <hash rule>, <n> tasks; per-slice deltas <results>; pass | fail
Canary: <pool or share>, <duration>; SLI deltas <name: delta>
Decision: promote | hold | roll back   Approver: <role>
```

## Example

Framework upgrade: pass offline and shadow gates, then canary for 24 hours.
Roll back if start success drops by more than 5 points from the baseline.

## Anti-patterns

- Replacing a model for all traffic at once.
- Evals that never gain cases from incidents.
- Versions not recorded on traces.
- Rebaselining to make a failing gate pass.

## Related skills

`agent-slo-design`, `drift-and-quality-monitoring`, `agent-postmortems`,
`agent-autonomy-levels`, `trace-based-slis`.

## Authority boundary

Advisory. Read eval results, traces and release configuration the user names.
Write only the requested gate report or eval-case proposals. Do not deploy,
promote, roll back or change a baseline; the release owner decides.

## Sources

- [Anthropic: Scaling Managed Agents](https://www.anthropic.com/research/managed-agents):
  an obsolete model-specific context-reset workaround.

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
