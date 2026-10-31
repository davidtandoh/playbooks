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

Compute every agent SLI from OpenTelemetry (OTel) traces, aggregated per task
and session rather than per span.

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
| Turns per task | Agent turns per `gen_ai.conversation.id` |
| Tokens and cost per task | Token usage summed per session, for successful tasks |
| Loop suspects | Sessions with the same tool call repeated several times in a row |
| Stuck sessions | Time between turns above a threshold |

## Decision guide

- If a tool runs over MCP, then record `mcp.method.name` on client and server
  spans. If the tool result reports `isError`, then set `error.type` to
  `tool_error` even though the protocol call succeeded.
- If an agent call crosses an MCP boundary, then propagate trace context in
  `params._meta` as `traceparent`, `tracestate`, and `baggage`.
- If you need a session key, then use `gen_ai.conversation.id`. Do not
  synthesise it from a trace id or a content hash.
- If infrastructure spans drown agent spans, then filter them at the collector
  but always keep error spans.
- If prompts or tool payloads would leave your trust boundary, then redact
  before export. Content capture stays opt-in.

## Checklist

- [ ] Every agent turn has one root span, and every task has a stable session key.
- [ ] Spans carry agent, model, task, and consequence-tier attributes.
- [ ] Prompt, model, skill, and tool-schema versions are recorded on spans.
- [ ] Tool error rate is computed from `error.type`, not by parsing payloads.
- [ ] SLIs are computed per task, not per span.
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
