# OpenTelemetry GenAI and MCP Attributes for SLIs

The GenAI semantic conventions moved to
`open-telemetry/semantic-conventions-genai` (Apache-2.0). Their status is
Development, so names can change. Check the repository before you depend on
a name. Attribute names below are quoted from that repository.

## Operations (`gen_ai.operation.name`)

| Value | Span covers |
| --- | --- |
| `invoke_agent` | One agent invocation |
| `invoke_workflow` | A workflow that coordinates agents or steps |
| `plan` | A planning step |
| `chat` | One model call |
| `execute_tool` | One tool call, including MCP tool calls |

## Attributes used by SLIs

| Attribute | Use |
| --- | --- |
| `gen_ai.conversation.id` | Conversation key that groups turns. Do not synthesize it. Count tasks by an explicit task id, not by this key. |
| `gen_ai.request.model`, `gen_ai.response.model` | Model pinning and drift checks |
| `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` | Cost per task |
| `gen_ai.agent.name`, `gen_ai.agent.id` | Per-agent SLIs |
| `gen_ai.tool.name` | Tool error rate and loop detection |
| `error.type` | Error classification; `tool_error` for MCP tool results that report an error |

## MCP conventions

| Attribute or metric | Use |
| --- | --- |
| `mcp.method.name` | Required on MCP spans, for example `tools/call` |
| `mcp.session.id` | Group calls in one MCP session |
| Trace context in request `params._meta` | Carries `traceparent`, `tracestate` and `baggage` across the MCP boundary |
| `mcp.client.operation.duration`, `mcp.server.operation.duration` | Tool latency |
| `mcp.client.session.duration`, `mcp.server.session.duration` | Session length |

## Content capture

These attributes are opt-in because they can hold user data:
`gen_ai.input.messages`, `gen_ai.output.messages`,
`gen_ai.tool.call.arguments` and `gen_ai.tool.call.result`. Keep them off by
default. Enable them only for a sample, in a restricted backend, with
redaction.
