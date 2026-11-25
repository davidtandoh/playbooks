# Runbook Contract for Agent Execution

An agent may draft or review a runbook. A human approves it before execution.
This skill does not authorize execution. An executor needs a separate grant.

## YAML schema

The schema uses JSON Schema Draft 2020-12, serialized as YAML. Parse the schema
and runbook as YAML mappings, then validate with a Draft 2020-12 validator.
Reject unknown fields. Schema validation checks structure, not command safety
or authority. The reviewer must verify those before approval.

```yaml
$schema: https://json-schema.org/draft/2020-12/schema
type: object
additionalProperties: false
required: [id, trigger, scope, diagnostics, actions, max_retries, escalation, stop_conditions]
properties:
  id: {$ref: '#/$defs/text'}
  trigger: {$ref: '#/$defs/text'}
  scope: {$ref: '#/$defs/text'}
  diagnostics:
    type: array
    minItems: 1
    items:
      type: object
      additionalProperties: false
      required: [command, read_only, expected]
      properties:
        command: {$ref: '#/$defs/text'}
        read_only: {const: true}
        expected: {$ref: '#/$defs/text'}
  actions:
    type: array
    minItems: 1
    items:
      type: object
      additionalProperties: false
      required: [id, command, risk_tier, approval, dry_run, retry_if, verification, rollback]
      properties:
        id: {$ref: '#/$defs/text'}
        command: {$ref: '#/$defs/text'}
        risk_tier: {type: integer, enum: [0, 1, 2]}
        approval: {const: human_incident_commander}
        dry_run: {$ref: '#/$defs/text'}
        retry_if: {$ref: '#/$defs/text'}
        verification:
          type: object
          additionalProperties: false
          required: [query, expected, observed, wait_seconds]
          properties:
            query: {$ref: '#/$defs/text'}
            expected: {$ref: '#/$defs/text'}
            observed:
              anyOf:
                - {$ref: '#/$defs/text'}
                - {type: 'null'}
            wait_seconds: {type: integer, minimum: 1}
        rollback: {$ref: '#/$defs/text'}
  max_retries: {const: 1}
  escalation:
    type: object
    additionalProperties: false
    required: [contact, conditions]
    properties:
      contact: {$ref: '#/$defs/text'}
      conditions: {$ref: '#/$defs/conditions'}
  stop_conditions: {$ref: '#/$defs/conditions'}
$defs:
  text: {type: string, minLength: 1}
  conditions:
    type: array
    minItems: 1
    items: {$ref: '#/$defs/text'}
```

`risk_tier` means 0 read-only, 1 reversible mutation, or 2 external or
irreversible mutation. Every incident action requires commander approval.
`retry_if` states the only outcome safe to retry; use `never` for actions that
cannot be repeated safely. `observed: null` means verification is pending.
Replace it with the actual observation after each attempt in the execution
record. Preserve prior observations and approval receipts in that record.

## Example

Commands below are hypothetical interfaces. Replace them with reviewed,
scoped commands before approval. This example is a draft, not a live command.

```yaml
id: pause-worker-intake
trigger: Worker error rate exceeds the incident threshold for five minutes
scope: Intake for worker group example in the incident environment only
diagnostics:
  - command: workerctl intake status --group example
    read_only: true
    expected: Intake is enabled and worker failures are increasing
actions:
  - id: pause-intake
    command: workerctl intake pause --group example
    risk_tier: 1
    approval: human_incident_commander
    dry_run: workerctl intake pause --group example --dry-run
    retry_if: A transient timeout occurred; status confirms intake is still enabled and repeating pause is safe
    verification:
      query: workerctl intake status --group example
      expected: Intake is paused and no new tasks are accepted
      observed: null
      wait_seconds: 30
    rollback: After separate commander approval, run workerctl intake resume --group example and verify intake is enabled
max_retries: 1
escalation:
  contact: Human incident commander
  conditions:
    - First failure does not match retry_if
    - Retry fails or verification cannot confirm the expected state
    - Approval is absent or a pre-flight check fails
stop_conditions:
  - An observation is unexpected and does not match retry_if
  - A safety boundary is breached or the command is ambiguous
  - The initial attempt and one retry both fail
```

## Execution rules

1. Validate the runbook. Run all read-only diagnostics before any action.
   Stop and escalate if diagnostics differ from expectations.
2. Use one actuation path. Check scope, concurrency, dry-run output and
   commander approval before each attempt, including a retry. Tier-2 actions
   require explicit approval of their external or irreversible effects.
3. After each attempt, wait the specified time. Run the verification query
   and record expected versus observed state, result and approver.
4. If verification succeeds, continue. Otherwise allow one retry only when
   `retry_if` holds, repetition is safe, and all pre-flight checks pass again.
   Never retry after an unknown outcome without confirming the current state.
5. After the retry fails, stop and escalate. If any stop condition occurs or
   the retry condition is unmet, stop and escalate immediately. Do not add,
   skip or reorder actions. The retry count persists across executor restarts.
6. Run rollback only with separate approval through the same actuation path.
   If reversal is impossible, state that in `rollback` and escalate instead.

## Roles and sources

The author drafts, an independent reviewer checks safety and authority, and
the executor follows the approved steps. Review does not grant execution.
This split follows medzin/sre-runbook-agent-skills (MIT). Read-only
investigation and a single actuation path follow Google's public "AI in SRE"
practices. See [PROVENANCE.md](../PROVENANCE.md). Wording is original.
