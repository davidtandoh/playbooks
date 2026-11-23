---
status: published
published: 2026-11-23
claim_review: complete
privacy_review: complete
category: AI-assisted engineering & software factories
topics:
  - architecture
  - delivery-gates
  - verification
  - security-and-privacy
applies_when:
  - adding or changing an HTTP API or its OpenAPI document
  - designing webhooks or event payloads consumed by another service
signals:
  - openapi
  - openapi.yaml
  - spectral
  - oasdiff
  - endpoint
  - webhook
  - asyncapi
key_rules:
  - Commit the OpenAPI document and lint it with the shared Spectral ruleset on every pull request. (#openapi-first-with-spectral-and-oasdiff)
  - Fail CI on breaking changes with oasdiff; break the contract only with a new major path version. (#versioning)
  - Return RFC 9457 problem details with a stable type for every error. (#errors-with-rfc-9457)
  - Paginate every list with page_size, page_token, and next_page_token from the first release. (#pagination)
  - Accept an Idempotency-Key on every POST. (#idempotency-keys)
  - Declare security on every operation and deny by default. (#auth-and-rate-limits)
---
# API design: one default per question, enforced by a linter

Design HTTP APIs contract-first. Keep one default answer for each recurring
design question, and let a linter and a breaking-change check enforce those
answers, so that neither a reviewer nor a coding agent has to remember them.

**The Spectral ruleset is the source of truth.** This page explains why each
rule exists. When the page and the ruleset disagree, the ruleset wins and the
page is the bug. A convention that no check enforces is a candidate for a new
rule, not for a longer page.

## Sources

All external sources were accessed on 2026-11-23. The IETF documents marked
draft can still change; recheck them before relying on a header name.

API guidelines:

- [Google API Improvement Proposals (AIPs)](https://google.aip.dev/):
  [AIP-121 resource-oriented design](https://google.aip.dev/121),
  [AIP-122 resource names](https://google.aip.dev/122),
  [AIP-131 to AIP-135 standard methods](https://google.aip.dev/131),
  [AIP-132 list methods](https://google.aip.dev/132),
  [AIP-136 custom methods](https://google.aip.dev/136),
  [AIP-151 long-running operations](https://google.aip.dev/151),
  [AIP-155 request identification](https://google.aip.dev/155),
  [AIP-158 pagination](https://google.aip.dev/158),
  [AIP-160 filtering](https://google.aip.dev/160),
  [AIP-180 backwards compatibility](https://google.aip.dev/180),
  [AIP-185 versioning](https://google.aip.dev/185),
  [AIP-193 errors](https://google.aip.dev/193)
- [Zalando RESTful API and Event Guidelines](https://opensource.zalando.com/restful-api-guidelines/):
  API first, naming, problem JSON, pagination, compatibility, and events
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
  and the
  [Azure REST API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md):
  long-running operations with `Operation-Location`, conditional requests,
  and versioning

Standards:

- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
  (status codes, `ETag`, `If-Match`, `Retry-After`)
- [RFC 6585: Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585) (429)
- [RFC 6750: OAuth 2.0 Bearer Token Usage](https://www.rfc-editor.org/rfc/rfc6750)
  and [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [RFC 7396: JSON Merge Patch](https://www.rfc-editor.org/rfc/rfc7396)
- [RFC 9745: The Deprecation HTTP Response Header Field](https://www.rfc-editor.org/rfc/rfc9745)
  and [RFC 8594: The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594)
- IETF HTTPAPI drafts:
  [The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
  (draft-ietf-httpapi-idempotency-key-header-09)
  and [RateLimit header fields for HTTP](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
  (draft-ietf-httpapi-ratelimit-headers-12)
- [Standard Webhooks](https://www.standardwebhooks.com/),
  [CloudEvents](https://cloudevents.io/), and
  [AsyncAPI](https://www.asyncapi.com/)

Tools:

- [Spectral](https://github.com/stoplightio/spectral) lints OpenAPI and
  AsyncAPI documents against a ruleset.
- [oasdiff](https://github.com/oasdiff/oasdiff) compares two OpenAPI
  documents and reports breaking changes.
- [Schemathesis](https://schemathesis.io/) generates test requests from an
  OpenAPI document and checks the running API against it.

## At a glance

```text
Pull request changes the API
        |
        v
OpenAPI document (committed, or exported from code and snapshot-tested)
        |
        +--> Spectral lint ------> design rules on this page   --> fail CI
        +--> oasdiff breaking ---> diff against the base branch --> fail CI
        +--> Schemathesis -------> running app versus the spec  --> fail CI
```

Takeaway: the contract is a file, and three checks guard it before any
reviewer reads the code.

| Question | Default |
| --- | --- |
| Contract | OpenAPI 3.1, committed in the repository |
| Resources | Plural kebab-case nouns, opaque string ids, standard methods; `:verb` custom methods only when no standard method fits |
| Versioning | Major version in the path (`/v1`); bump it only for a breaking change, and avoid breaking changes |
| Errors | `application/problem+json` (RFC 9457) with a stable `type` per error kind |
| Pagination | Cursor pagination on every list from day one |
| Idempotency | Every `POST` accepts `Idempotency-Key` |
| Auth | Bearer tokens in the `Authorization` header; deny by default |
| Rate limits | 429 with `Retry-After` |
| Long-running work | `202 Accepted` and an operation resource |
| Webhooks and events | Standard Webhooks signatures; CloudEvents envelopes described in AsyncAPI |

## Decision guide

### Resource modelling and naming

- If you are adding an endpoint, then model the resource first and expose
  standard methods on it: `GET` to list and get, `POST` to create, `PATCH` to
  update, and `DELETE` (AIP-121, AIP-131 to AIP-135).
- If no standard method fits, then add a custom method as
  `POST /invoices/{invoice_id}:send`, not a verb segment such as
  `/invoices/{invoice_id}/send` (AIP-136).
- If you are naming a path segment, then use a plural kebab-case noun
  (`/credit-notes`), and keep sub-resource nesting to two levels (a local
  default; Zalando rule 147 allows up to three).
- If you are naming a JSON property, then use `snake_case`. Name timestamps
  `*_at` (one of the two conventions in Zalando rule 235) and send RFC 3339
  `date-time` strings in UTC.
- If you are designing an id, then make it an opaque string. Clients must
  not parse it (Zalando rule 174).
- If you are choosing a partial-update format, then use JSON Merge Patch
  (RFC 7396). AIP-134 uses a field mask instead; this page picks Merge Patch
  because it needs no extra parameter for JSON clients.

Checks: `paths-kebab-case`, `paths-no-verbs`, `properties-snake-case`, and
`timestamps-date-time` in the ruleset.

### Versioning

- If a change only adds optional fields, new resources, or new methods, then
  it is not breaking. Do not bump the version (AIP-180).
- If a change removes, renames, or retypes a field, makes an optional field
  required, or adds a required request field, then it is breaking (AIP-180;
  Zalando compatibility rules).
- If you must break the contract, then publish a new major version in the
  path (`/v2`) and run it side by side with the old one (AIP-185). Mark the
  old version with the `Deprecation` (RFC 9745) and `Sunset` (RFC 8594)
  response headers.
- The guidelines disagree on where the version goes. Zalando avoids
  versioning and rejects URL versions, and Azure uses an `api-version` query
  parameter. This page follows AIP-185 because a path version is visible in
  every log line and route table.
- Clients ignore unknown fields (the tolerant reader rule in Zalando's
  compatibility guidance), which is what lets additive changes stay
  non-breaking.

Check: `oasdiff breaking` against the base branch, with `--fail-on ERR`.
`--fail-on ERR` ignores WARN-level changes, such as removing a request
parameter; use `--fail-on WARN` to block them too.

### Errors with RFC 9457

- If a request fails, then return `application/problem+json` with the RFC
  9457 members `type`, `title`, `status`, `detail`, and `instance`. Define
  these as required properties of the shared `components.schemas.Problem`
  object: `status` is an integer; the other four members are strings.
  Error response schemas must declare the same required members and types;
  reference the shared schema with `$ref` to avoid repeating the definition.
- If the failure is a validation error, then add an `errors` extension member
  that lists each invalid field. RFC 9457 allows extension members.
- If the error kind is stable, then give it a stable `type` URI and treat that
  URI as part of the contract, as AIP-193 treats its machine-readable error
  reason. Clients branch on `type`, never on `detail` text.
- If you have a trace or request id, then add it as a `trace_id` extension
  member so a caller can quote it in a support request.
- Never return a stack trace, a SQL fragment, or an internal host name in
  `detail` (Zalando: MUST not expose stack traces).
- Use a small fixed set of status codes: 400 validation, 401 unauthenticated,
  403 forbidden, 404 not found, 409 conflict, 412 precondition failed, 422
  idempotency-key reuse with a different body, 428 precondition required when
  `If-Match` is missing, 429 rate limited, 500, and 503 with `Retry-After`
  (RFC 9110; RFC 6585). The set itself is a local choice; the RFCs define the
  codes, not which ones an API uses.
- If the caller must not learn that a resource exists, then return 404
  instead of 403. RFC 9110 allows a server to hide a resource this way.

Zalando requires problem JSON. Google (AIP-193) and Microsoft define their
own error bodies; this page uses RFC 9457 because it is the IETF standard
and needs no vendor-specific client code.

Checks: `problem-schema-defined`, `errors-use-problem-json`, and
`status-codes-allowed`. A contract test asserts the shape of one real 400 and
one real 500 response.

### Pagination

- If an endpoint returns a list, then paginate it with a cursor from the first
  release: request `page_size` and `page_token`, respond with
  an object with a required string `next_page_token`, which is empty on the
  last page (AIP-158; Zalando prefers cursors). Include `next_page_token` in
  the response schema's `required` array so every page carries the token.
- Our default `page_size` is 50 with a maximum of 500. That is a local choice,
  not a figure from the sources.
- If a client asks for a total count, then add it as a separate, explicitly
  requested field. Counting an unbounded collection on every page is
  expensive.
- Do not use offset pagination on an unbounded collection: inserts shift the
  pages under the reader.
- If a list needs filtering or ordering, then use `filter` and `order_by`
  query parameters with a small documented grammar (AIP-160, AIP-132).

Checks: `collections-paginated` and `collections-return-next-page-token`.

### Idempotency keys

- If an operation is a `POST` (a create or a custom method), then accept an
  `Idempotency-Key` request header carrying a client-generated unique value
  (IETF Idempotency-Key draft; AIP-155 describes the same idea as a
  `request_id` field).
- Store the key, a fingerprint of the request, and the response. Our default
  retention is 24 hours; the draft asks servers to publish their own expiry
  policy.
- If the same key arrives with the same request, then return the stored
  response without repeating the side effect.
- If the same key arrives with a different request body, then return 422. If
  the first request with that key is still running, then return 409. Both
  follow the IETF draft.
- `GET`, `PUT`, and `DELETE` are idempotent by HTTP definition (RFC 9110) and
  need no key.

Check: `post-idempotency-key`. A contract test sends one request twice and
asserts a single side effect.

### Concurrency

- If a resource can be updated by two clients, then return an `ETag` on reads,
  require `If-Match` on `PATCH` and `PUT`, and return 412 on a mismatch (RFC
  9110; Azure guidelines on conditional requests). Requiring `If-Match` is a
  local choice; Azure says to honour it.

Check: `updates-if-match`.

### Auth and rate limits

- If a user calls the API, then authenticate with an OAuth 2.0 bearer token in
  the `Authorization` header. Never accept bearer tokens in a query string,
  because URLs end up in logs (RFC 6750 §2.3; RFC 9700). Apply the same rule
  to API keys.
- If one service calls another, then use workload identity or short-lived
  service tokens, not shared long-lived secrets.
- Authorize per resource and deny by default. An operation without a declared
  security requirement fails the lint unless it is tagged `public`. This
  check covers GET, PUT, POST, PATCH, DELETE, HEAD, OPTIONS, and TRACE. Every
  security alternative must name at least one scheme; an empty requirement
  object permits anonymous access and fails unless the operation is public.
- If a client exceeds its limit, then return 429 with `Retry-After`. RFC 6585
  makes `Retry-After` optional; this page requires it. Advertise the limit with the `RateLimit` and `RateLimit-Policy`
  fields from the IETF draft once your gateway supports them.
- If the service is overloaded or in maintenance, then return 503 with
  `Retry-After` (RFC 9110).

Checks: `operations-secured`, `operations-declare-429`, and
`retry-after-on-429-and-503`. A static-analysis rule in the service code can
flag a route handler that skips the auth dependency.

### Long-running operations

- If work can outlast a request timeout, then return `202 Accepted` with an
  `Operation-Location` (Azure) or `Location` header that points at
  `/operations/{operation_id}`.
- The operation resource carries `done`, and on completion either `error` (a
  problem details object; AIP-151 uses `google.rpc.Status`) or `response`
  (AIP-151).
- Clients poll the operation with backoff and honour `Retry-After`. A webhook
  can notify completion, but polling stays the contract.

Check: `accepted-has-location`, plus a shared `Operation` schema in
`components`.

### Webhooks and events

- If you send webhooks, then follow Standard Webhooks: sign each delivery with
  the `webhook-id`, `webhook-timestamp`, and `webhook-signature` headers. The
  symmetric `v1` scheme is HMAC-SHA256 over `id.timestamp.body`. The spec
  also defines an asymmetric ed25519 scheme (`v2a`) and prefers it when you
  do not control both ends.
- Receivers verify the signature, reject a timestamp outside a short
  tolerance window (the spec leaves the window open; the reference Python
  library uses five minutes), and
  de-duplicate by `webhook-id`, because senders retry with backoff and a
  receiver will see repeats.
- If you publish events to a broker, then describe the channels and messages
  in an AsyncAPI document and wrap each event in a CloudEvents envelope: the
  required `specversion`, `id`, `source`, and `type`, the optional `time` and
  `subject`, and the payload in `data`.
- Name event types in reverse-DNS form with a version, such as
  `com.example.invoice.paid.v1`. An event states a fact in the past tense.
  CloudEvents says `type` SHOULD use a reverse-DNS prefix; the `.v1` suffix
  and the past tense are local conventions.
- Treat event schemas as an API: the same compatibility rules apply as for
  HTTP (Zalando event guidelines).

Checks: Spectral lints AsyncAPI documents with its built-in AsyncAPI
ruleset. A receiver contract test asserts that a bad signature gets 401 and a
replayed `webhook-id` is a no-op.

### OpenAPI-first with Spectral and oasdiff

- If the API is new, then write the OpenAPI document first and review it
  before the code (Zalando API first).
- If a framework generates the document from code, then export it in CI and
  fail on any unreviewed difference from the committed copy (a snapshot test).
- Lint the document with the ruleset below on every pull request.
- Run `oasdiff breaking <base.yaml> <revision.yaml> --fail-on ERR` against
  the base branch. A pull request that must break the contract bumps the
  major version and says why. `--fail-on ERR` ignores WARN-level changes,
  such as removing a request parameter; use `--fail-on WARN` to block them.
- Run Schemathesis against the running app so the implementation cannot
  drift from the document.
- If a frontend or another service calls the API, then generate its client
  types from the document and fail CI if regeneration leaves a dirty diff.

The ruleset below is the example the checks above refer to. It extends
Spectral's recommended OpenAPI rules. Keep it as `.spectral.yaml` at the
repository root and change the rules there, not on this page.
Operation-wide rules cover GET, PUT, POST, PATCH, DELETE, HEAD, OPTIONS, and
TRACE. Method-specific rules apply only to the methods they name.

```yaml
# API design ruleset. This file is the source of truth for the conventions;
# the playbook only explains why each rule exists.
extends: [["spectral:oas", recommended]]

rules:
  # Resources: plural kebab-case nouns, snake_case path parameters, an
  # optional camelCase custom method after a colon, as in AIP-136
  # (/invoices/{invoice_id}:cancel, /invoices/{invoice_id}:markPaid).
  paths-kebab-case:
    description: Path segments are kebab-case nouns or {snake_case} parameters.
    severity: error
    given: $.paths
    then:
      field: "@key"
      function: pattern
      functionOptions:
        match: "^(/([a-z0-9]+(-[a-z0-9]+)*|\\{[a-z][a-z0-9_]*\\}))+(:[a-z]+([A-Z][a-z0-9]*)*)?$"

  paths-no-verbs:
    description: Use a standard method or a :verb custom method, not a verb segment.
    severity: error
    given: $.paths
    then:
      field: "@key"
      function: pattern
      functionOptions:
        notMatch: "/(get|list|create|update|delete|remove|fetch|set|send|cancel|approve|archive|publish)(-[a-z0-9-]+)?(/|$)"

  properties-snake-case:
    description: JSON property names are snake_case.
    severity: error
    given: $..properties[*]~
    then:
      function: casing
      functionOptions:
        type: snake

  timestamps-date-time:
    description: Properties named *_at are RFC 3339 date-time strings.
    severity: error
    given: $..properties[?(@property.match(/_at$/))]
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          required: [type, format]
          properties: {type: {const: string}, format: {const: date-time}}

  # Errors: RFC 9457 problem details on every 4xx and 5xx response.
  problem-schema-defined:
    description: components.schemas.Problem holds the shared problem details schema.
    severity: error
    given: $
    then:
      field: components.schemas.Problem
      function: schema
      functionOptions:
        schema: &problem-schema
          type: object
          required: [type, required, properties]
          properties:
            type: {const: object}
            required:
              type: array
              allOf:
                - contains: {const: type}
                - contains: {const: title}
                - contains: {const: status}
                - contains: {const: detail}
                - contains: {const: instance}
            properties:
              type: object
              required: [type, title, status, detail, instance]
              properties:
                type: &string-property
                  type: object
                  required: [type]
                  properties: {type: {const: string}}
                title: *string-property
                status:
                  type: object
                  required: [type]
                  properties: {type: {const: integer}}
                detail: *string-property
                instance: *string-property

  errors-use-problem-json:
    description: Every 4xx and 5xx response declares the required problem details shape.
    severity: error
    given: $.paths[*][get,put,post,patch,delete,head,options,trace].responses[?(@property.match(/^[45]/))]
    then:
      field: content
      function: schema
      functionOptions:
        schema:
          type: object
          required: ["application/problem+json"]
          properties:
            application/problem+json:
              type: object
              required: [schema]
              properties:
                schema: *problem-schema

  status-codes-allowed:
    description: Use only the agreed status codes.
    severity: error
    given: $.paths[*][get,put,post,patch,delete,head,options,trace].responses
    then:
      field: "@key"
      function: enumeration
      functionOptions:
        values: ["200", "201", "202", "204", "400", "401", "403", "404",
                 "409", "412", "422", "428", "429", "500", "503"]

  # Pagination: every collection GET takes page_size and page_token and
  # returns next_page_token. A collection path ends in a plain segment.
  collections-paginated:
    description: Collection GETs accept page_size and page_token.
    severity: error
    given: $.paths[?(!@property.match(/[}:][^/]*$/))].get
    then:
      field: parameters
      function: schema
      functionOptions:
        schema:
          type: array
          allOf:
            - contains:
                type: object
                properties: {name: {const: page_size}, in: {const: query}}
                required: [name, in]
            - contains:
                type: object
                properties: {name: {const: page_token}, in: {const: query}}
                required: [name, in]

  collections-return-next-page-token:
    description: Collection GETs require a string next_page_token in every response.
    severity: error
    given: $.paths[?(!@property.match(/[}:][^/]*$/))].get
    then:
      field: responses
      function: schema
      functionOptions:
        schema:
          type: object
          required: ["200"]
          properties:
            "200":
              type: object
              required: [content]
              properties:
                content:
                  type: object
                  required: [application/json]
                  properties:
                    application/json:
                      type: object
                      required: [schema]
                      properties:
                        schema:
                          type: object
                          required: [type, properties, required]
                          properties:
                            type: {const: object}
                            required:
                              type: array
                              contains: {const: next_page_token}
                            properties:
                              type: object
                              required: [next_page_token]
                              properties:
                                next_page_token: *string-property

  # Idempotency and concurrency.
  post-idempotency-key:
    description: Every POST accepts an Idempotency-Key header.
    severity: error
    given: $.paths[*].post
    then:
      field: parameters
      function: schema
      functionOptions:
        schema:
          type: array
          contains:
            properties: {name: {const: Idempotency-Key}, in: {const: header}}
            required: [name, in]

  updates-if-match:
    description: PATCH and PUT require an If-Match header.
    severity: error
    given: $.paths[*][patch,put]
    then:
      field: parameters
      function: schema
      functionOptions:
        schema:
          type: array
          contains:
            type: object
            properties:
              name: {const: If-Match}
              in: {const: header}
              required: {const: true}
            required: [name, in, required]

  # Auth and rate limits.
  operations-secured:
    description: Every operation declares security unless it is tagged public.
    severity: error
    given: $.paths[*][get,put,post,patch,delete,head,options,trace]
    then:
      function: schema
      functionOptions:
        schema:
          anyOf:
            - required: [security]
              properties:
                security:
                  type: array
                  minItems: 1
                  items: {type: object, minProperties: 1}
            - required: [tags]
              properties: {tags: {contains: {const: public}}}

  operations-declare-429:
    description: Every operation declares a 429 response.
    severity: error
    given: $.paths[*][get,put,post,patch,delete,head,options,trace].responses
    then:
      field: "429"
      function: truthy

  retry-after-on-429-and-503:
    description: 429 and 503 responses carry Retry-After.
    severity: error
    given: $.paths[*][get,put,post,patch,delete,head,options,trace].responses[429,503]
    then:
      field: headers.Retry-After
      function: truthy

  # Long-running operations.
  accepted-has-location:
    description: A 202 response points at the operation resource.
    severity: error
    given: $.paths[*][get,put,post,patch,delete,head,options,trace].responses.202
    then:
      field: headers
      function: schema
      functionOptions:
        schema:
          type: object
          anyOf:
            - required: [Location]
            - required: [Operation-Location]
```

Run it with `npx @stoplight/spectral-cli@6 lint openapi.yaml`. Known limits of
this example: `operations-secured` checks operation-level `security` only, so
an API that relies on a root-level `security` block needs the rule adjusted;
`collections-paginated` reads operation-level parameters, not path-level
ones; the timestamp rule checks property names, not every date field; and
the problem rules check resolved schemas with explicit object properties and
required members, so composed schemas must expose that shape directly.

## Checklist

For a new or changed endpoint:

- [ ] The OpenAPI change is in the same pull request as the code.
- [ ] Spectral passes with the shared ruleset.
- [ ] oasdiff reports no breaking change, or the pull request bumps the major
      version and says why.
- [ ] Schemathesis runs against the app.
- [ ] If the document is generated from code, a snapshot test proves it
      matches the committed one.
- [ ] Problem details, pagination, idempotency, security, and rate-limit
      responses are declared in the document, not described in prose.
- [ ] Generated client types are regenerated and committed.

## Rules of thumb

- If an agent or reviewer has to remember a convention, it belongs in the
  Spectral ruleset, not on this page.
- Prefer a non-breaking addition over a new major version, every time.
- Do not add hypermedia links, field masks, or partial responses until a
  client asks for them.
- Internal APIs follow the same rules. They become external faster than
  anyone plans.
- Pick one OpenAPI linter per repository. Spectral and Redocly CLI both work;
  running both duplicates findings.

## Claim review

- [x] Every figure traces to a cited source or is labelled as a local default.
- [x] Every factual claim stays within the cited evidence.
- [x] Evidence limits and qualifiers remain explicit.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private-repository material.
- [x] No trace material.
- [x] No transcript material.
