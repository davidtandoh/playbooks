# Engineering standards

Standards for building and changing software. Each page defines a standard and
the automatic checks a project must run. Pages link to shared checks where
available; project-specific checks belong in the consuming repository.

## Start here

1. Read [API design](api-design.md) before you add or change an HTTP API.
2. Copy its Spectral ruleset into your repository and run it in CI.

| [Secure and reliable systems](secure-reliable-systems.md) | Published | Authorization and policy tests, parser fuzzing, artifact verification, recovery rehearsals in the service repository | Least privilege, safe construction, isolation, credentials, supply chain, overload, rollout and incident readiness |
