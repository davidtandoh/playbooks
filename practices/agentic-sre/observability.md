---
status: published
published: 2026-10-31
claim_review: complete
privacy_review: complete
category: Agent systems
topics:
  - observability
  - reliability
---
# Observability: SLIs from traces

Compute agent service level indicators (SLIs) from OpenTelemetry (OTel) traces.
Aggregate task metrics by task identity and session metrics by session identity.

Skill: `trace-based-slis` (see the [skill index](README.md#skills)).

## Sources

- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/README.md)
- [OpenTelemetry GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
- [OpenTelemetry semantic conventions for MCP](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/mcp.md)
- [OpenTelemetry blog: GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/)
- [Honeycomb: LLMs demand observability-driven development](https://www.honeycomb.io/blog/llms-demand-observability-driven-development)

## At a glance

Span conventions, attribute names, content capture, and backend choice are in
[Building Reliable Agents §1](../../building-reliable-agents.md#1-observability--you-cant-fix-what-you-cant-see).
This page adds what to compute from those spans and the Model Context Protocol
(MCP) attributes that make tool errors countable.

| SLI | Computed from |
| --- | --- |
| Tool error rate | `execute_tool` spans with `error.type` set, over all `execute_tool` spans |
| Retries per turn | Repeated tool spans with the same name and arguments inside one turn |
| Turns per task | Agent turns counted by task id, including retries |
| Tokens per task | Token usage summed by task id, including failed and retried attempts |
| Cost per successful task | All task spend, including failed and retried attempts, divided by the number of successful tasks in the measurement window |
| Loop suspects | Sessions with the same tool call repeated several times in a row |
| Stuck sessions | Time between turns above a threshold |

## Decision guide

- Give each task an explicit task id attribute. If one agent invocation span
  represents the whole task, its span id can serve as the task id. Associate
  all turns, retries, token usage, and spend with that task id.
- Use `gen_ai.conversation.id` only for session grouping. If a session holds
  several tasks, count each task by its task id. Do not synthesise a session
  key from a trace id or a content hash.
- Sum spend by task id before calculating cost per successful task. Include
  failed tasks in total spend. If no task succeeds, report the ratio as
  undefined and show total spend and zero successes.
- If a tool runs over MCP, then record `mcp.method.name` on client and server
  spans. If the tool result reports `isError`, then set `error.type` to
  `tool_error` even though the protocol call succeeded.
- If an agent call crosses an MCP boundary, then propagate trace context in
  `params._meta` as `traceparent`, `tracestate`, and `baggage`.
- If infrastructure spans drown agent spans, then filter them at the collector
  but always keep error spans.
- If prompts or tool payloads would leave your trust boundary, then redact
  before export. Content capture stays opt-in.

## Checklist

- [ ] Every task has a stable task id, distinct from session grouping.
- [ ] Spans carry agent, model, task, and consequence-tier attributes.
- [ ] Prompt, model, skill, and tool-schema versions are recorded on spans.
- [ ] Tool error rate is computed from `error.type`, not by parsing payloads.
- [ ] Turns, tokens, and spend are aggregated by task id.
- [ ] Cost per successful task includes spend from failed and retried attempts.
- [ ] Redaction runs before export.

## Rules of thumb

- Measure tasks, not spans.
- The GenAI and MCP conventions have Development status. Pin the version you
  implement and recheck it before an upgrade.
- Reliability data must not become a data-leak path.

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
