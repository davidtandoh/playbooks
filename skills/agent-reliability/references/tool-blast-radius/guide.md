# Blast-Radius Limits for Tool Use

Make the limits on what an agent can touch deterministic and enforced outside
the model.

## When to use

- Adding a tool, MCP connector, credential or memory store to an agent.
- Giving an agent computer-use or browser control.
- An agent that can spend money or send messages to people.

## Principles

- Authorization lives downstream of the model, not in the prompt.
- Each agent has its own identity. No shared or developer credentials.
- Every mutation can be previewed, limited, stopped and attributed.
- Memory and inter-agent channels are inputs an attacker can write to.

## Workflow

1. Inventory every capability: tools, credentials, memory and context stores,
   and channels to other agents. Record read or write, reversible or not,
   external reach, and data reached. Map each to a consequence tier.
2. Give each agent a distinct, authenticated identity with scoped,
   short-lived permissions granted on demand. Log every action against it.
3. Require a dry run. Every mutating tool supports a preview mode, and the
   agent calls it first for any L2 or higher action.
4. Set hard envelopes per task: token and cost budget, maximum tool calls,
   wall-clock limit, and maximum delegation depth.
5. Add a circuit breaker per agent. It opens after a set number of consecutive
   failures (5 is a common default) and closes only by a human reset.
6. Provide a fleet stop control with three separate actions: pause in-flight
   actions, block new actions, and revoke L3 permissions. Keep the trace.
7. Break the lethal trifecta: never combine private data, untrusted content
   and an external send path in one unattended agent.
8. Enforce protected zones in code: password managers, banking, two-factor
   screens, and other users' windows or sessions.

## Decision guide

| If the capability | Then |
| --- | --- |
| Reads private data and ingests untrusted content | Remove external send, or require L1 approval for sends |
| Mutates state with no preview mode | Wrap it in a preview, or keep it at L1 |
| Writes to shared memory | Add expiry, provenance tags and a review path |
| Talks to another agent | Authenticate the channel and cap delegation depth |
| Needs a credential | Issue a per-agent, scoped, expiring token |

## Output template

```text
Capability: <name>  Type: tool | credential | memory | channel  Tier: <n>
Identity: <agent principal>  Scope: <resources>  Expiry: <duration>
Dry run: yes | no   Envelope: <tokens>, <calls>, <wall clock>, <depth>
Breaker: opens after <n> failures, reset by <role>
Stop control: pause | block | revoke tested on <date>
```

## Example

```text
Worker envelope: 2M tokens, 4 hours, branch-only Git writes, no network
sends, delegation depth 2 or less. Exceeding any limit pauses the worker and
notifies the owner. Five failed tool calls in a row open its breaker.
```

## Anti-patterns

- One all-powerful token shared across agents.
- Guardrails written only in the system prompt.
- Unlimited loops against a paid model.
- A single kill switch that cannot separate pausing from revoking.

## Related skills

`agent-autonomy-levels`, `agent-incident-response`, `agent-capacity-and-cost`,
`agentic-product-reliability-review`.

## Authority boundary

Advisory. Read tool definitions, permission configuration and traces the user
names. Write only the requested inventory or envelope document. Do not issue,
revoke or rotate credentials, and do not change permissions. The capability
owner applies every change.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
