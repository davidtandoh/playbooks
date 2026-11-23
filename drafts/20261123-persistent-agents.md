---
title: Persistent agents
summary: What an always-on, proactive agent needs beyond a chat loop — wake triggers, durable state, memory curation, governed tools, and evals that test when it should stay silent — as a build and launch checklist.
audience:
  - platform-engineering-lead
buyer_question: What does it take to run an agent that stays on, acts on its own triggers, and still stays inside limits a human approved?
category: Agent systems
topics:
  - architecture
  - orchestration
  - memory
  - reliability
  - governance
  - evals
status: draft
created: 2026-11-23
published: null
updated: 2026-11-23
claim_review: pending
privacy_review: pending
applies_when:
  - building an agent that runs on schedules or events instead of only user requests
  - giving an agent a standing goal, long-lived memory, or several human users
  - deciding which actions an always-on agent may take without a human
signals:
  - persistent agent
  - always-on
  - proactive
  - cron
  - event listener
  - durable execution
  - agent memory
key_rules:
  - Build a persistent agent only for a standing responsibility with a measurable outcome. (#1-decide-whether-you-need-persistence)
  - Enforce limits at tool, network, and model choke points, never in the prompt. (#2-requirements-checklist)
  - Give every wake source an owner, a frequency cap, a busy policy, and a cheap quiet outcome. (#3-the-wake-contract)
  - Let running agents write notes freely and promote them to shared memory only through a scheduled curator. (#4-memory-notes-first-curated-later)
  - Evaluate both acting when it should and staying silent when it should. (#5-launch-checklist)
---
<!-- playbook-capture:fingerprint=16b0100c57c15f52a3c9d7928bf1c3a4828b96325a154eb5e091b49976b7b159 -->

# Persistent agents

## Sources

- Primary source: LangChain, "The Future of Agents with Harrison Chase", webinar, 2026-11-21, 45:52:
  <https://www.youtube.com/watch?v=GojQtxCT3dg>. Vendor talk; product claims
  about LangSmith are omitted here and only the architecture is used.
- [Agentic SRE practices](../practices/agentic-sre/README.md) in this
  repository.
- [Building Reliable Agents](../building-reliable-agents.md) in this
  repository.

## Start here

This guide is for platform and engineering leads asked to build an agent that
does not wait to be asked. A persistent agent owns a goal, wakes on events and
schedules, remembers what it did, and works next to several people at once.

Use this guide before you build one. It lists what must exist around the model
for the agent to stay useful and safe over weeks, not minutes. It links to the
[Agentic SRE practices](../practices/agentic-sre/README.md) for the operating
detail instead of repeating it.

Do not use it for a task agent that runs once per request and stops. Most of
this machinery is cost you only need when the agent must keep going without a
person in the chat.

**How to read the tags.**

- **[talk mm:ss]** — said or shown in the primary source webinar, at that
  timestamp. Timestamps come from a machine transcript; treat quotes as close
  paraphrase.
- **[practice]** — standard engineering practice this guide adds where the talk
  is thin. Default-good, not sourced.

## At a glance

A persistent agent is three systems, not one prompt **[talk 20:50–25:56]**:

| Layer | Question it answers | What lives there |
| --- | --- | --- |
| Runtime | What should the agent do? (intended behaviour) | Goal prompt, harness, scheduler, queue, durable state, memory |
| Improvement loop | What did it actually do? (observed behaviour) | Traces, online and offline evals, failure-to-test-case loop |
| Governance | What may it never do? (governed behaviour) | Identity, policy and approval at tool and model choke points, audit log |

Takeaway: the prompt states intent, traces show behaviour, and only governance
enforces limits.

## The map

```text
  events, schedules,        +------------------- agent runtime -------------------+
  user messages,     -----> | front door --> queue --> execution (agent+harness) |
  agent self-reminders      |  (policy:      (one turn    |   state restored,     |
                            |   reject,       at a time)  |   progress saved      |
                            |   queue,                    v                       |
                            |   steer)            durable session state           |
                            |  recovery: crashed work goes back in the queue      |
                            +---------------------------|-------------------------+
                                                        |
                         tool gateway / model gateway <-+  (identity, policy,
                                                        |   approval, audit, cost)
                                                        v
                                                 traces --> evals --> fixes
```

Takeaway: every wake enters through one front door, runs one turn at a time,
and leaves through governed choke points that emit traces.

The runtime shape above follows the agent-runtime diagram shown in the talk
**[talk 16:52–18:10]**.

## 1. Decide whether you need persistence

The talk's core distinction is task versus goal **[talk 05:02–05:49]**:

| Task | Goal |
| --- | --- |
| "Write this email" | "Maintain inbox zero" |
| Bounded action, then done | Ongoing outcome, never done |
| Brute-force completion is fine | Needs memory of past attempts and new approaches |

Build a persistent agent only when the work is a standing responsibility with an
outcome you can measure. If a cron job plus a single model call would do, use
that **[practice]**; see
[Building Reliable Agents](../building-reliable-agents.md) rule 1.

**Design the goal around feedback.** The hardest input for a persistent agent is
human feedback, so shape goals around the unit people find natural to correct.
The talk's example reorganised per-account sales agents into per-stage agents
because customers could teach "how to do outbound" across accounts more easily
than one account at a time **[talk 05:57–07:37]**.

## 2. Requirements checklist

Each row is one requirement area. "Talk" records what the source says; "Default"
is this guide's recommendation.

| Area | Talk | Default |
| --- | --- | --- |
| **Goal and alignment** | Prompt for the goal and for creativity; a goal such as "remove all bugs" can be met by deleting the code base, so alignment matters more when no one watches **[talk 12:33–13:22, 38:54–39:09]** | Write the goal with explicit non-goals and forbidden shortcuts, and enforce the forbidden ones in governance, not the prompt **[practice]** |
| **Triggers and scheduling** | Crons set by the developer, the user, or the agent itself; event listeners (new email, new chat message); agent tools to manage its own reminders **[talk 13:42–14:26]** | Keep a written inventory of every wake source with its owner and maximum frequency **[practice]** |
| **Queueing and steering** | A busy agent receives new messages mid-run; decide whether to reject, queue, or let them steer the current run **[talk 14:30, 17:28]** | One turn at a time per session; declare the policy per wake source **[talk 16:52–18:10]** |
| **State and checkpointing** | Durable session state (conversation, progress, history) readable by the app and the agent; checkpoints **[talk 17:36–17:50, 19:00]** | Persist progress after every step that has side effects **[practice]** |
| **Failure recovery** | Durable execution: a run that fails halfway resumes from where it failed; recovery puts crashed work back in the queue **[talk 17:08–17:18]** | Make every side-effecting tool call idempotent so a replayed step is safe **[practice]** |
| **Memory** | Decide whether the agent writes memory directly or writes notes to a buffer that a background "dreaming" curator merges later; storage format matters less than what to remember and keeping it fresh **[talk 14:58–15:39]** **[talk 37:05–37:29]** | Let the agent always take notes; promote notes to shared memory only through a curator on a schedule **[talk 42:23–43:03]** |
| **Identity and permissions** | Permissions depend on who is acting, what action, and which surface; a shared channel must not inherit one person's private access **[talk 15:39–15:55, 24:45–25:04]** | Give the agent its own identity and carry the requesting human's identity through every tool call **[practice]**; see [Blast radius](../practices/agentic-sre/blast-radius.md) |
| **Governance and oversight** | Do not put limits in a prompt; enforce policy, identity, and approval at choke points — tool calls, network calls, model calls **[talk 24:03–24:45]**; tool policy can allow, deny, or require human approval, with an audit log of every action **[talk 37:47–38:52]** | Assign an autonomy level per action type, not per agent; see [Autonomy and approval gates](../practices/agentic-sre/autonomy-and-approval.md) |
| **Observability** | Trace every step; traces are the system of record for spotting error patterns **[talk 39:48–39:56]**; mask trace inputs and outputs by default and grant access by group and metadata **[talk 28:45–30:28]** | Instrument with OpenTelemetry GenAI spans; see [Observability](../practices/agentic-sre/observability.md) |
| **Cost control** | Model gateway for cost control, model access, and fallbacks **[talk 27:21]**; compute for sandboxes is the main capacity squeeze **[talk 36:35–36:53]** | Set a budget per wake and per day; a wake that finds nothing to do should cost almost nothing **[practice]** |
| **Evaluation** | Test tool calls, messages, and state edits; grade full traces and end state against rubrics, online and offline; test that the agent acts when worth acting and stays silent otherwise; turn production failures into regression cases **[talk 21:32–22:18, 23:35]** **[talk 22:48–23:12]** | Track noise and missed opportunities as two separate rates **[practice]**; see [Releases](../practices/agentic-sre/releases.md) |
| **Multiplayer and multi-surface** | Works with several people at once across chat, desktop, and web; state and event streams must resume across surfaces **[talk 08:34–09:04, 18:00–18:06]** | Start with one surface; add more only when state and permissions already work per surface **[practice]** |

## 3. The wake contract

Every wake source needs the same five answers before launch **[practice]**:

1. **Source.** Event, schedule, or self-reminder, and who owns it.
2. **Frequency cap.** The most times per hour it may wake the agent.
3. **Busy policy.** Reject, queue, or steer when a run is already active.
4. **Quiet outcome.** What "nothing worth doing" looks like, and proof it is
   cheap.
5. **Escalation.** Which outcomes notify a human, and through which surface.

The talk's warning case is an agent that wakes every 30 minutes and messages the
user every time: correct in each run, spam in aggregate **[talk 21:49]**.

## 4. Memory: notes first, curated later

```text
  run --> notes buffer --(scheduled curator)--> shared memory --> next run
            ^                    |
            +-- traces ----------+  (procedural memory: skills)
```

Takeaway: running agents write notes freely; only a curator changes what every
future run believes.

| Memory type | Best source | Form |
| --- | --- | --- |
| Procedural (how to do things) | Agent traces | Skills **[talk 41:52–42:17]** |
| Factual (what is true) | Traces plus other work systems | Markdown, wiki, or graph **[talk 41:52–42:17]** |

Also give the agent search across its own past conversations, whether it uses
one long thread or many **[talk 44:12–45:08]**.

## 5. Launch checklist

- [ ] The goal names an outcome metric, non-goals, and forbidden shortcuts.
- [ ] Every wake source has a filled wake contract (section 3).
- [ ] A crash mid-run resumes from the last checkpoint without repeating a
      side effect.
- [ ] Notes and curated memory are separate; the curator runs on a schedule.
- [ ] Every tool and model call passes a gateway that checks identity and policy
      and writes an audit record.
- [ ] Each action type has an autonomy level and a named human approver where
      required.
- [ ] Traces are masked by default and access is granted by group.
- [ ] Evals cover "acted when it should" and "stayed silent when it should".
- [ ] Every production failure becomes a regression eval before its fix ships.
- [ ] There is a per-wake and per-day cost budget and an emergency stop.

## 6. Worked example: a proactive fraud-research agent

A fraud team wants an agent that improves detection without touching live
decisions **[practice]**.

| Requirement | Choice |
| --- | --- |
| Goal | Reduce cost-weighted fraud loss of the champion detection policy, measured by pre-registered experiments |
| Wakes | Drift alarm on score or feature distributions; new confirmed-fraud labels; alert-queue backlog over threshold; weekly schedule |
| May do alone | Open a hypothesis, build candidate features or rules on a branch, run a pre-registered backtest, write an evidence report |
| Needs a human | Promote a challenger, change live policy or thresholds, contact a customer |
| Never | Decide or block a live payment |
| Quiet outcome | "No drift, no new label pattern" closes the wake with a one-line log entry and no message |

Takeaway: the agent is persistent in research and has no authority over the
payment path.

## Capture record

- Capture proposal `pbp-20261123-16b0100c`, approved by the accountable
  reviewer on 2026-11-23; type `checklist`, claim class `sourced`.
- Evidence pointers: this repository at
  `3cfe48abb00b1d1ba4c739e335a4a52dd4989bc3` —
  `practices/agentic-sre/autonomy-and-approval.md`,
  `practices/agentic-sre/blast-radius.md`,
  `practices/agentic-sre/observability.md`,
  `practices/agentic-sre/releases.md`, and `building-reliable-agents.md`.
- Open review question: the primary source is a video, so reviewers must check
  the `[talk mm:ss]` timestamps against the recording before publication.
