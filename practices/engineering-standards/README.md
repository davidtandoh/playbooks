# Engineering standards

Standards for building and changing software. Each page identifies checks to
run in the adopting repository. Some pages supply check configuration; others
specify checks the adopter must implement. When a page and its implemented
check disagree, the check wins.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.
3. Read [Observability](observability.md) when defining service or data-platform telemetry and alerts.
4. Read [Performance and memory](performance-and-memory.md) before building a
   service, job, or data pipeline. Record its budgets in the spec and add the
   hot-path benchmark to the gate.

## Practices

| Practice | Status | Check | What it covers |
| --- | --- | --- | --- |
| [API design](api-design.md) | Published | Spectral ruleset, oasdiff, Schemathesis | Resource naming, versioning, RFC 9457 errors, pagination, idempotency keys, auth and rate limits, long-running operations, webhooks and events, OpenAPI-first delivery |
| [Observability](observability.md) | Published | [Checks to implement in the service repository](observability.md#checklist) | Golden signals, RED and USE, SLIs and SLOs, error budgets, correlated logs and traces, OpenTelemetry, telemetry cost, data-pipeline indicators, runbooks and toil |
| [Performance and memory](performance-and-memory.md) | Published | Project hot-path benchmark and budget comparison in the gate | Data structures, complexity, allocation, layout, I/O, concurrency, and language notes; resource budgets, bounded memory, and regression margins |

## Credits

Each page lists its own primary sources. All wording is original.
