# Trace-Based SLIs

Compute reliability from what agents did, recorded in standard spans, not
from what they reported.

## When to use

- Building or fixing tracing through SDK instrumentation or a collector.
- Defining a metric for a recurring trace review.
- Noise in traces hides the signal.

## Principles

- Count tasks by an explicit task id, or by the root agent invocation span.
  Never count by span, conversation id or session id.
- Use the OpenTelemetry GenAI semantic conventions so any backend can read
  the data.
- Message content capture is opt-in. Redact before export.
- Keep error spans even when you drop noise.

## Workflow

1. Instrument with the GenAI conventions: `invoke_agent`, `invoke_workflow`,
   `plan`, `chat` and `execute_tool` operations with `gen_ai.*` attributes.
   See the [attribute reference](references/otel-genai-attributes.md).
2. Record an explicit task id on the root `invoke_agent` span, and count
   tasks by it. Set `gen_ai.conversation.id` to the real conversation id to
   group turns; one conversation can hold several tasks. Do not synthesize
   either id from a random UUID, trace id or content hash.
3. Tag agent, harness, model, worker id, task id, repository and consequence
   tier, and the artifact versions from `eval-gated-releases`.
4. For MCP tool calls, record `mcp.method.name`, `mcp.session.id`, and
   `error.type = tool_error` when a tool result reports an error. Carry trace
   context in the MCP request metadata.
5. Compute SLIs named in the `agent-slo-design` catalogue: tool error rate,
   retries per turn, turns per task, tokens and cost per task, loop suspects
   (same tool and arguments repeated N times), gaps between turns (stalled
   sessions), and delegation depth.
6. Filter infrastructure-only traces at the collector. Always keep error
   spans.
7. Redact before export. Reliability data must not become a data-leak path.

## Decision guide

| If | Then |
| --- | --- |
| Most spans are infrastructure | Drop all-infrastructure traces at the collector, keep errors |
| Tool error rate needs payload parsing | Use `error.type = tool_error` instead |
| Sessions split across traces | Fix the task id and `gen_ai.conversation.id`, not the query |
| Content is needed for debugging | Enable capture for a sample in a restricted backend |

## Output template

```text
SLI: <catalogue name>
Spans: <operation names>   Filter: <attributes>
Group by: <task id>, <tags>
Formula: <good> / <valid>   Window: <duration>
Redaction: <fields removed>   Backend: <any OpenTelemetry backend>
```

## Example

```text
Daily, per harness:
tool_error_rate = execute_tool spans with error.type / all execute_tool spans
loop_suspects   = tasks with 5 or more identical tool calls in a row
cost_per_task   = sum(tokens x price) over all attempts, failed and retried
                  included / count(task id where outcome = success)
```

## Anti-patterns

- Measuring spans instead of tasks.
- Letting infrastructure spans drown agent spans.
- Exporting unredacted prompts to a shared backend.
- A different session key in every service.

## Related skills

`agent-slo-design`, `drift-and-quality-monitoring`, `eval-gated-releases`,
`agent-incident-response`.

## Authority boundary

Advisory. Read instrumentation code, collector configuration and sample
traces the user names. Write only the requested SLI definitions or queries.
Do not change collectors, exporters or retention, and do not export trace
content; the observability owner applies changes.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
