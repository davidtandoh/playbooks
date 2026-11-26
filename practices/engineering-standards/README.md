# Engineering standards

Standards for building and changing software. Each page defines a standard and
the automatic checks a project must run. Pages link to shared checks where
available; project-specific checks belong in the consuming repository.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.
3. Read [Performance and memory](performance-and-memory.md) before building a
   service, job, or data pipeline. Record its budgets in the spec and add the
   hot-path benchmark to the gate.

## Practices

| Practice | Status | Check | What it covers |
| --- | --- | --- | --- |
| [API design](api-design.md) | Published | Spectral ruleset, oasdiff, Schemathesis | Resource naming, versioning, RFC 9457 errors, pagination, idempotency keys, auth and rate limits, long-running operations, webhooks and events, OpenAPI-first delivery |
| [Performance and memory](performance-and-memory.md) | Published | Project hot-path benchmark and budget comparison in the gate | Latency, throughput, and peak-memory budgets; measurement evidence; bounded data and concurrency; service and job memory limits; regression margins |

## Credits

Each page lists its own primary sources. All wording is original.
