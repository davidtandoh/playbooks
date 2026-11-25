# SLI Catalogue for Agent Workflows

Use these stable names so dashboards, traces and SLO documents agree. Names
marked (MS) come from the Microsoft Agent SRE Governance 1.0 specification
(MIT). Names marked (R) follow the reliability dimensions in Rabanser et al.,
"Towards a Science of AI Agent Reliability" (CC BY 4.0). Other names are
original to this pack.

Count every task by an explicit task id, or by its root agent invocation
span. Do not count tasks by conversation id or session id.

| Dimension | SLI | Definition |
| --- | --- | --- |
| Success | `task_success_rate` (MS) | Tasks whose outcome is verified by evidence / tasks started |
| Success | `false_completion_rate` | Tasks reported done without evidence / tasks reported done |
| Success | `no_progress_rate` | Tasks that loop or stall past the wall-clock limit / tasks started |
| Success | `human_repair_rate` | Tasks a human had to fix after completion / completed tasks |
| Success | `tool_call_accuracy` (MS) | Tool calls with valid arguments and expected effect / tool calls |
| Consistency (R) | `pass_k` | Tasks that pass on all k repeated runs / tasks in the suite |
| Consistency (R) | `cost_variance`, `time_variance` | Spread of cost and duration across repeated runs |
| Robustness (R) | `fault_success_rate` | Success with an injected tool fault or schema change / runs |
| Robustness (R) | `paraphrase_success_rate` | Success with a reworded instruction / runs |
| Predictability (R) | `calibration_delta` (MS) | Gap between stated confidence and observed success |
| Latency | `response_latency_p95` (MS) | 95th percentile of the class-specific latency indicator |
| Efficiency | `cost_per_task` (MS) | All spend, including failed and retried attempts / successful tasks |
| Safety | `policy_compliance` (MS) | Actions inside policy / actions; tier 2 target is 100% |
| Safety | `hallucination_rate` (MS) | Outputs with an unsupported factual claim / graded outputs |
| Safety | `scope_chain_depth` (MS) | Maximum absolute delegation depth reached; lower is better; default maximum 3 |

## Consistency arithmetic

pass@k counts a task as passed if any of k runs succeeds. pass^k requires all
k runs to succeed. With independent runs, a 75% per-run success rate gives
about 42% pass^3 (0.75 cubed). Only about 42% of tasks succeed on all three
repeated runs (Anthropic, "Demystifying Evals for AI Agents").

## Latency budgets by phase

The AWS Well-Architected Agentic AI Lens (AGENTPERF01-BP01) groups agent
performance into latency, throughput, quality and efficiency. Split the
end-to-end latency budget into retrieval, model inference, tool calls and
coordination between agents, so a regression points at one phase.
