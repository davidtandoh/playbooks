# Playbooks

David Tandoh's working playbooks — distilled, opinionated guides for building things well.
Each playbook synthesizes primary sources into a checklist-driven reference I can actually
execute against.

## Index

The index groups playbooks by category without moving existing root files. The
category and topic vocabulary below is now controlled here. Existing playbook
front matter will adopt it in a separate change.

### AI-assisted engineering & software factories

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Testing in agentic engineering](testing-in-agentic-engineering.md) | `verification` `delivery-gates` `evals` `reliability` `cost` | A test portfolio for agent-written code, what agents over-produce (mocks, debug scripts, tampered assertions) and how to trim it, rules for fewer and better agent tests, property-based and mutation testing, and software tests versus agent evals |
| [CI for agentic engineering](ci-for-agentic-engineering.md) | `delivery-gates` `verification` `security-and-privacy` `cost` `reliability` | Local gate first with hosted merge proof, staged test selection, caching and merge queues, flaky-test governance, rounded-minute cost per merge, and trust boundaries for actions, secrets and runners |
| [API design](practices/engineering-standards/api-design.md) | `architecture` `delivery-gates` `verification` `security-and-privacy` | One default per HTTP API design question, enforced by a Spectral ruleset and an oasdiff breaking-change check: naming, versioning, RFC 9457 errors, pagination, idempotency, auth, rate limits, long-running operations, webhooks and events |

**[Secure and reliable systems: make the safe path the default](practices/engineering-standards/secure-reliable-systems.md)**

- Applies when: designing or changing trust boundaries in a data platform, ML platform, or service; adding dependency access, credentials, recovery paths, or deployment controls; reviewing overload behaviour, resilience tests, or incident readiness.
- Signals: `least privilege`, `zero trust`, `threat model`, `untrusted input`, `secret rotation`, `supply chain`, `provenance`, `retry`, `backoff`, `load shedding`, `rollback`, `recovery`, `incident readiness`.
- Skills: none yet.
- Key rules:
  1. Authenticate each caller and authorize each resource operation with least privilege; deny by default. ([source](practices/engineering-standards/secure-reliable-systems.md#least-privilege-and-zero-trust))
  2. Parse untrusted input into validated domain types and enforce safe defaults through shared APIs. ([source](practices/engineering-standards/secure-reliable-systems.md#safe-construction-and-untrusted-input))
  3. Bound tenant resource use and isolate failure domains with independent controls. ([source](practices/engineering-standards/secure-reliable-systems.md#defence-in-depth-and-blast-radius))
  4. Use short-lived credentials and prove rotation and revocation without exposing secrets. ([source](practices/engineering-standards/secure-reliable-systems.md#secrets-and-rotation))
  5. Pin build inputs and verify artifact provenance against an explicit deployment policy. ([source](practices/engineering-standards/secure-reliable-systems.md#supply-chain-security))
  6. Bound retries by deadlines and budgets; make replay safe before enabling retries. ([source](practices/engineering-standards/secure-reliable-systems.md#recovery-and-overload))
  7. Rehearse recovery, canary aborts, and incident access before release. ([source](practices/engineering-standards/secure-reliable-systems.md#verification-and-incident-readiness))
