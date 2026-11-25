# Drift and Quality Monitoring

Find quality loss that no alert fires for, and turn it into labelled data.

## When to use

- The daily or weekly trace review.
- A provider changed a model without notice.
- Users report that outputs are worse.

## Principles

- Infrastructure health does not prove output quality.
- A judge is a model too. Calibrate it against human labels and recheck it.
- Grade reasoning with a judge and the final action deterministically.
- The cheapest gold labels come from people already reviewing agent work.

## Workflow

1. Sample production tasks with a deterministic hash of the task id, off the
   request path. Send failures to a review queue as candidate eval cases.
2. Grade with a hybrid: a binary LLM judge for reasoning quality, and a
   deterministic check for the final action or output.
3. Tier labels: bronze (heuristic), silver (judge calibrated against gold),
   gold (human-verified). Capture gold labels by recording whether a person
   accepts, modifies or rejects each agent suggestion.
4. Run nightly evals on the previous day's tasks or incidents in an isolated
   environment. Compare per-slice pass^k repeated-run consistency, cost and
   time variance, perturbation robustness (tool faults, tool-interface
   changes, rewording), and `calibration_delta` with the known-good baseline.
   Alert on agreed limits; report safety separately.
5. Monitor task types, tokens per task, tool mix, refusal rate and turns.
6. Pin model versions and record them on traces. Alert on an unexpected
   version change.
7. Check memory and context stores for stale or unverified entries.
8. Recalibrate each judge against fresh gold labels on a schedule. Feed
   confirmed failures to `eval-gated-releases`.

## Decision guide

| If | Then |
| --- | --- |
| Pass rate drops and the model version changed | Treat as a model change; run the release gate |
| Pass rate drops and the input mix changed | Add the new task type as a slice |
| Judge and human labels disagree on more than 10% | Stop using the judge until recalibrated |
| Refusals rise | Check prompt and policy changes before the model |
| A memory entry has no source or has expired | Quarantine it from retrieval |

## Output template

```text
Review: <date>   Agent / version: <id>   Sample: <n> tasks (hash rule <rule>)
Pass rate: <n>% (week-on-week <delta>)   Judge agreement: <n>%
Reliability: pass^k <n>; cost/time variance <n>; robustness <n>;
  calibration_delta <n>; per-slice deltas <results>; safety <separate result>
Distribution shifts: <metric: old -> new>
New gold labels: <n> accepted, <n> modified, <n> rejected
Candidate eval cases: <ids>   Actions: <owner, item>
```

## Example

Daily review: 50 sampled tasks per version. Alert if pass rate drops more
than 5 points week-on-week or a reliability-profile limit is exceeded.

## Anti-patterns

- Trusting judges without human calibration.
- Only offline evals, never production samples.
- Sampling by hand, which picks interesting cases instead of typical ones.

## Related skills

`eval-gated-releases`, `trace-based-slis`, `agent-postmortems`,
`agent-slo-design`.

## Authority boundary

Advisory. Read sampled traces, labels and eval results the user names. Write
only the requested review report and candidate eval cases. Do not change
judges, baselines or model pins; the workflow owner decides.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
