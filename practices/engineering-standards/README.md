# Engineering standards

Standards for building and changing software. Each page defines its requirements
and verification guidance. The table below identifies the checks for each
practice; each page specifies which checks to implement in your repository.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.
3. Read [Performance and memory](performance-and-memory.md) before building a
   service, job, or data pipeline. Record its budgets in the spec and add the
   hot-path benchmark to the gate.
4. Read [Secure and reliable systems](secure-reliable-systems.md) before changing trust boundaries or recovery paths.

## Practices

| Practice | Status | Check | What it covers |
| --- | --- | --- | --- |
| [API design](api-design.md) | Published | Spectral ruleset, oasdiff, Schemathesis | Resource naming, versioning, RFC 9457 errors, pagination, idempotency keys, auth and rate limits, long-running operations, webhooks and events, OpenAPI-first delivery |
| [Performance and memory](performance-and-memory.md) | Published | Project hot-path benchmark and budget comparison in the gate | Data structures, complexity, allocation, layout, I/O, concurrency, and language notes; resource budgets, bounded memory, and regression margins |
| [Secure and reliable systems](secure-reliable-systems.md) | Published | Authorization and policy tests, parser fuzzing, artifact verification, recovery rehearsals in the service repository | Least privilege, safe construction, isolation, credentials, supply chain, overload, rollout and incident readiness |

## Credits

Each page lists its own primary sources. All wording is original.
