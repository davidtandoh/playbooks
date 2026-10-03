# Playbooks

David Tandoh's working playbooks — distilled, opinionated guides for building things well.
Each playbook synthesizes primary sources into a checklist-driven reference I can actually
execute against.

## Index

The index groups playbooks by category without moving existing root files. The
category and topic vocabulary below is now controlled here. Existing playbook
front matter will adopt it in a separate change.

### AI-assisted engineering & software factories

No indexed playbooks yet.

### Agent systems

| Playbook | Topics | What it covers |
| --- | --- | --- |
| [Building AI Agents](building-ai-agents.md) | `architecture` `orchestration` `tools-and-context` `reliability` | When to build an agent, the ReAct loop, single-agent tool/context design, multi-agent orchestration, failure handling |
| [Building Reliable Agents](building-reliable-agents.md) | `observability` `cost` `evals` `security-and-privacy` | Observability (OTel GenAI), token cost and economics, reliability engineering and evals, security and prompt injection, and production blind spots |

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

- One playbook per Markdown file at the repo root.
- Every playbook cites its primary sources up top.
- Favor tables, checklists, and rules-of-thumb over prose — these are references, not essays.
- Update the index table above when adding a playbook.
- Keep drafts under `drafts/`. A separate reviewed change promotes a draft to the root.
