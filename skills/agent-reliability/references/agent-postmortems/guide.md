# Blameless Postmortems for Agent Systems

Explain why the wrong action looked right at the time, and turn each lesson
into a test that would catch it next time.

## When to use

- After any agent incident.
- An agent repeats the same mistake.
- A task spec or assignment sent an agent the wrong way.
- A single incident used more than 20% of an error budget.

## Principles

- Blameless for humans and agents alike. "The model got it wrong" is not a
  cause.
- Build the timeline from traces, not memory.
- Use one taxonomy every month so patterns are comparable.
- Every postmortem adds at least one permanent regression case.

## Workflow

1. Build the timeline from traces, transcripts, tool outputs and approvals.
2. For each decision, ask what information made the action look correct.
3. List contributing factors across: task spec, skill or prompt, model, tool,
   memory or context, envelope, observability gap, and human approval.
4. Classify the security-relevant factors with the OWASP Top 10 for Agentic
   Applications (2026): goal hijack, tool misuse, identity and privilege
   abuse, agentic supply chain, unexpected code execution, memory and context
   poisoning, insecure inter-agent communication, cascading failures,
   human-agent trust exploitation, and rogue agents.
5. Produce three outputs: a regression eval case labelled as gold data, a
   skill or spec fix, and, if needed, an autonomy or envelope change.
6. Give each action item an owner and a due date. Review patterns monthly.

## Decision guide

| If the main factor is | Then the primary fix is |
| --- | --- |
| Task spec or assignment | Spec checklist plus a coverage eval |
| Skill or prompt | Skill change released through `eval-gated-releases` |
| Model behaviour | Regression case plus a model-version pin |
| Tool or memory | Envelope or inventory change in `tool-blast-radius` |
| Approval gate | Gate SLI review in `agent-autonomy-levels` |
| Missing signal | New SLI or trace field in `trace-based-slis` |

## Output template

```text
Title: <what users experienced>   Date: <date>   Severity: <n>
Summary: <two sentences>
Timeline: <time, actor, action, evidence link>
Why it looked right: <information the actor had>
Contributing factors: <category>: <factor> (OWASP <id> if any)
Gold eval case: <id, input, expected outcome>
Action items: <item>, owner <role>, due <date>, priority <n>
```

## Example

```text
An agent's task spec covered only part of an agreed plan, so a known defect
stayed open. Factor: the spec was written from one list, not the full plan.
Actions: add a spec checklist item "covers every agreed step"; add an eval
that compares spec coverage with the plan.
```

## Anti-patterns

- Blaming the model.
- A postmortem with no new eval case.
- Action items without owners.
- A new cause list for every postmortem.

## Related skills

`agent-incident-response`, `eval-gated-releases`,
`drift-and-quality-monitoring`, `tool-blast-radius`, `agent-autonomy-levels`.

## Authority boundary

Advisory. Read incident records, traces and transcripts the user names.
Write only the requested postmortem draft and proposed eval cases. Do not
change skills, envelopes or autonomy levels; owners apply action items.

## Sources

See [PROVENANCE.md](PROVENANCE.md). Concepts are cited; wording is original.
