# Engineering standards

Standards for building and changing software. Each page defines checks for
its standard. A page can supply reusable tooling or specify checks to implement
against the selected products. When a page supplies an automatic check and
its prose disagrees with that check, the check wins.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.
3. Read [Observability](observability.md) when defining service or data-platform telemetry and alerts.
4. Read [Performance and memory](performance-and-memory.md) before building a
   service, job, or data pipeline. Record its budgets in the spec and add the
   hot-path benchmark to the gate.
5. Read [Data-intensive systems](data-intensive-systems.md) before choosing
   storage guarantees or building a data pipeline; implement its workload and
   failure checks against your selected products.
6. Read [Domain-driven design](domain-driven-design.md) when business rules or
   ownership boundaries need a model, then enforce dependencies and invariants.

## Practices

| Practice | Status | Check | What it covers |
| --- | --- | --- | --- |
| [API design](api-design.md) | Published | Spectral ruleset, oasdiff, Schemathesis | Resource naming, versioning, RFC 9457 errors, pagination, idempotency keys, auth and rate limits, long-running operations, webhooks and events, OpenAPI-first delivery |
| [Observability](observability.md) | Published | [Checks to implement in the service repository](observability.md#checklist) | Golden signals, RED and USE, SLIs and SLOs, error budgets, correlated logs and traces, OpenTelemetry, telemetry cost, data-pipeline indicators, runbooks and toil |
| [Performance and memory](performance-and-memory.md) | Published | Project hot-path benchmark and budget comparison in the gate | Data structures, complexity, allocation, layout, I/O, concurrency, and language notes; resource budgets, bounded memory, and regression margins |
| [Data-intensive systems](data-intensive-systems.md) | Published | Workload, compatibility, concurrency, fault-injection and replay checks | Storage models and engines, schema evolution, replication, partitioning, isolation, retries, batch and streams, CDC and derived views |
| [Domain-driven design](domain-driven-design.md) | Published | Architecture tests, invariant tests, persistence and event contract tests | Language, bounded contexts, context maps, aggregates, entities and values, events, repositories, ports and adapters, ADRs |

## Credits

Each page lists its own primary sources. All wording is original.
