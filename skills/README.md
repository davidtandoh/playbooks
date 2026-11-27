# Skills

Agent skills that put the playbooks in this repository into practice. A skill
is a folder with a `SKILL.md` entry point that a coding agent loads when a
task matches its description.

| Skill | Puts into practice |
| --- | --- |
| [`agent-reliability`](agent-reliability/SKILL.md) | [Agentic SRE practices](../practices/agentic-sre/README.md), plus parts of [Building AI Agents](../building-ai-agents.md) and [Building Reliable Agents](../building-reliable-agents.md) |

See the [repository conventions](../README.md#conventions) for how pages
declare and display skills and where public summaries are maintained.

## Where these copies come from

Each folder here is a one-way export from the author's private source
repository. Do not edit a copy here: the next export overwrites it. To
propose a change, open an issue or pull request. The author applies an
accepted change at the source and exports the skill again.

| Skill | Exported from source commit | Exported on |
| --- | --- | --- |
| `agent-reliability` | `dcc1848fb59aa7990f6ac478d9de863e1a632e63` | 2026-11-27 |

Export normalization: the drift-monitoring output template uses `old value;
new value` in place of the source arrow placeholder to pass this repository's
ASCII-diagram check.

Every export passes a manual privacy review and the repository's private-term
scan before it is published.

## License and provenance

The skills are original work by David Tandoh, released under this
repository's [MIT license](../LICENSE). Each topic folder in
`agent-reliability/references/` has a `PROVENANCE.md` that lists its sources
and their licenses. The section shape follows
[mawero83/google-sre-skills](https://github.com/mawero83/google-sre-skills)
(MIT); no text from that project is reproduced.
