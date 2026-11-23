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
| [Local-first CI with hosted acceptance (draft)](drafts/20261011-local-first-ci.md) | `delivery-gates` `verification` `security-and-privacy` `cost` | One tool per CI job, local workflow lint and emulation limits, trust boundaries for actions and runners, required-check and rounded-minute cost rules, and a bounded one-repository pilot |
| [API design (draft)](practices/engineering-standards/api-design.md) | `architecture` `delivery-gates` `verification` `security-and-privacy` | One default per HTTP API design question, enforced by a Spectral ruleset and an oasdiff breaking-change check: naming, versioning, RFC 9457 errors, pagination, idempotency, auth, rate limits, long-running operations, webhooks and events |

### Agent systems

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Building AI Agents](building-ai-agents.md) | `architecture` `orchestration` `tools-and-context` `reliability` | When to build an agent, the ReAct loop, single-agent tool/context design, multi-agent orchestration, failure handling |
| [Building Reliable Agents](building-reliable-agents.md) | `observability` `cost` `evals` `security-and-privacy` | Observability (OTel GenAI), token cost and economics, reliability engineering and evals, security and prompt injection, and production blind spots |
| [Persistent agents (draft)](drafts/20261123-persistent-agents.md) | `architecture` `orchestration` `memory` `reliability` `governance` `evals` | What an always-on, proactive agent needs: task versus goal, wake triggers and a wake contract, durable state and recovery, notes-then-curated memory, governance at tool and model choke points, and evals for acting versus staying silent |
| [Agentic SRE practices](practices/agentic-sre/README.md) | `reliability` `observability` `evals` `governance` `security-and-privacy` `delivery-gates` `cost` | Nine operating practices for agent systems: SLOs and error budgets, autonomy and approval gates, blast radius, observability, eval-gated releases, drift, incidents, postmortems, and launch review |

### Enterprise AI platform

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Contextual Retrieval (draft)](drafts/20261003-contextual-retrieval.md) | `retrieval` `evals` `cost` | When to add chunk context, combine embeddings with BM25, and test reranking |

<!-- playbook-taxonomy:v1:begin -->
### Categories
- AI-assisted engineering & software factories
- Agent systems
- Enterprise AI platform

### Topics
- architecture
- orchestration
- tools-and-context
- memory
- retrieval
- evals
- observability
- reliability
- security-and-privacy
- cost
- delivery-gates
- verification
- knowledge-capture
- governance
- model-serving
- gateways
<!-- playbook-taxonomy:v1:end -->

## Conventions

- Keep each published playbook in one Markdown file at the repo root.
- Every playbook cites its primary sources up top.
- Favor tables, checklists, and rules-of-thumb over prose — these are references, not essays.
- Update the index above when adding a playbook.
- Keep standalone playbook drafts under `drafts/`. A separate reviewed change
  promotes a standalone draft to the root. Draft practice pages stay in their
  practice set as described below.
- Keep operating practices under `practices/<set>/`. Each set has a `README.md` index,
  and each practice page carries publication front matter, a category, and topics.
  A practice page that is still a draft says `status: draft` in its front matter.
  Practice pages link to playbook sections instead of repeating them.

## License

[MIT](LICENSE). Each playbook and practice credits its sources; quoted or adapted
third-party material keeps its own license.
