# Engineering standards

Standards for building and changing software. Each page defines its requirements
and verification guidance. The table below identifies the checks for each
practice; each page specifies which checks to implement in your repository.
When a page supplies an automatic check and its prose disagrees with that
check, the check wins.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.
3. Read [Performance and memory](performance-and-memory.md) before building a
   service, job, or data pipeline. Record its budgets in the spec and add the
   hot-path benchmark to the gate.
4. Read [Data-intensive systems](data-intensive-systems.md) before choosing
   storage guarantees or building a data pipeline; implement its workload and
   failure checks against your selected products.
5. Read [Domain-driven design](domain-driven-design.md) when business rules or
   ownership boundaries need a model, then enforce dependencies and invariants.
6. Read [Secure and reliable systems](secure-reliable-systems.md) before changing
   trust boundaries or recovery paths.
7. Read [Code style and static analysis](code-style-and-static-analysis.md)
   when choosing static checks or enforcing them through hooks and gates.

## Practices

| Practice | Status | Check | What it covers |
| --- | --- | --- | --- |
| [API design](api-design.md) | Published | Spectral ruleset, oasdiff, Schemathesis | Resource naming, versioning, RFC 9457 errors, pagination, idempotency keys, auth and rate limits, long-running operations, webhooks and events, OpenAPI-first delivery |
| [Performance and memory](performance-and-memory.md) | Published | Project hot-path benchmark and budget comparison in the gate | Data structures, complexity, allocation, layout, I/O, concurrency, and language notes; resource budgets, bounded memory, and regression margins |
| [Data-intensive systems](data-intensive-systems.md) | Published | Workload, compatibility, concurrency, fault-injection and replay checks | Storage models and engines, schema evolution, replication, partitioning, isolation, retries, batch and streams, CDC and derived views |
| [Domain-driven design](domain-driven-design.md) | Published | Architecture tests, invariant tests, persistence and event contract tests | Language, bounded contexts, context maps, aggregates, entities and values, events, repositories, ports and adapters, ADRs |
| [Secure and reliable systems](secure-reliable-systems.md) | Published | Authorization and policy tests, parser fuzzing, artifact verification, recovery rehearsals in the service repository | Least privilege, safe construction, isolation, credentials, supply chain, overload, rollout and incident readiness |
| [Code style and static analysis](code-style-and-static-analysis.md) | Published | Repository-owned format, lint, and type/compile checks; staged-snapshot and full-gate failure fixtures | Language baselines, edit feedback, staged checks, CI parity, safe formatting, shrinking debt baselines, and failure propagation |

## Credits

Each page lists its own primary sources. All wording is original.
