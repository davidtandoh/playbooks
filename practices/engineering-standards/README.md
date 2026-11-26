# Engineering standards

Standards for building and changing software. Each page puts its standard into
an automatic check first, and keeps prose only to explain the check and to
point at it. When a page and its check disagree, the check wins.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.
3. Read [Domain-driven design](domain-driven-design.md) when business rules or
   ownership boundaries need a model, then enforce dependencies and invariants.

## Practices

| Practice | Status | Check | What it covers |
| --- | --- | --- | --- |
| [API design](api-design.md) | Published | Spectral ruleset, oasdiff, Schemathesis | Resource naming, versioning, RFC 9457 errors, pagination, idempotency keys, auth and rate limits, long-running operations, webhooks and events, OpenAPI-first delivery |
| [Domain-driven design](domain-driven-design.md) | Published | Architecture tests, invariant tests, persistence and event contract tests | Language, bounded contexts, context maps, aggregates, entities and values, events, repositories, ports and adapters, ADRs |

## Credits

Each page lists its own primary sources. All wording is original.
