---
title: A governed delivery loop for coding agents
summary: A practical method for letting coding agents change repositories while keeping evidence, review, and delivery authority outside the agent's own judgement.
audience:
  - platform-engineering-lead
buyer_question: How can our coding agents deliver repository changes without approving their own work?
status: draft
created: 2026-09-28
published: null
updated: 2026-09-28
evidence:
  - title: NIST Secure Software Development Framework 1.1
    url: https://doi.org/10.6028/NIST.SP.800-218
  - title: GitHub Docs - About protected branches
    url: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
  - title: SLSA 1.2 - Provenance
    url: https://slsa.dev/spec/v1.2/provenance
claim_review: pending
privacy_review: pending
---

# A governed delivery loop for coding agents

## Start here

This guide is for engineering and platform leads who need coding agents to
change repositories without letting those agents approve their own work. Use it
when an agent can write useful code, but the team still owns scope, risk,
quality, and delivery.

The outcome is a change that a human can assess from recorded evidence. The
agent receives approved intent, works inside a bounded scope, runs deterministic
gates, submits its work to independent review, and hands the delivery decision
back to an accountable human.

Do not use this guide as a substitute for repository-specific tests, continuous
integration, security controls, or human review. Do not use an autonomous loop
for a change when the team cannot define the allowed scope, observe the result,
or recover from failure.

## System map

```mermaid
flowchart LR
    H["Human sponsor<br/>intent and authority"] -->|approved task| M
    subgraph W["Write boundary"]
        M["Maker agent<br/>bounded change"]
    end
    M -->|change + test evidence| G["Deterministic gates"]
    G -->|passing evidence| R["Independent reviewer<br/>read-only findings"]
    R -->|findings, not approval| D["Accountable human<br/>delivery decision"]
    G -->|gate record| D
    D -->|explicit grant| P["Repository delivery path"]
```

Takeaway: the maker can write, the gates can verify fixed rules, the reviewer
can find defects, and only the accountable human can authorise delivery.

The trust boundaries are deliberate. The maker has write access only to the
approved workspace. The reviewer receives read-only access and cannot approve
or merge. The delivery path accepts a recorded human grant, not the maker's
self-report.

## Decision points

| Decision | Alternatives | Cost | Evidence that changes the choice |
|---|---|---|---|
| Risk tier | Low, standard, high, or critical | Higher tiers add review, gate, and rollback work | Credentials, permissions, security boundaries, persisted state, public interfaces, destructive actions, migrations, and uncertainty raise the tier |
| Implementation boundary | One coherent slice or a wider change | A narrow slice can require later work; a wider change increases review and recovery cost | Acceptance criteria that cannot be verified independently may require a different slice; new outcomes require new approval |
| Gate scope | Focused tests, repository aggregate gate, or both | More gate coverage costs time and compute | Executable behaviour, shared contracts, dependencies, generated truth, and integration behaviour require the applicable aggregate gate |
| Review strength | Same-harness check, independent read-only review, or human specialist review | Independence adds latency and setup | A different harness with read-only tools supports a stronger independence claim; unavailable independence must be recorded, not hidden |
| Delivery authority | Local commit, pushed branch, pull request, merge, or deployment | Each step increases external impact and recovery cost | Proceed only to the highest action covered by a current, specific human grant |

Treat unknown risk as a stop condition. A small diff is not proof of low risk.
A one-line permission change can matter more than a large internal refactor.

## Procedure

1. **Record approved intent.** Write the outcome, acceptance criteria, non-goals,
   allowed paths, maximum delivery action, and grant source. Record assumptions
   and unresolved decisions.
   **Stop if:** a material requirement or authority boundary is missing.
   **Observable result:** a reviewer can tell what success means and what the
   agent must not do.

2. **Classify risk before implementation.** Assess security, credentials,
   permissions, filesystem access, dependencies, persisted state, public
   interfaces, destructive operations, and migrations. Select a review and
   verification level that matches those factors.
   **Stop if:** a risk factor is unknown or the required control is unavailable.
   **Observable result:** the task has a named risk tier and required gates,
   review, and recovery evidence.

3. **Make a traceable plan.** Map each acceptance criterion to one owning
   component, one proposed change, and one verification method. Identify reuse,
   recovery, and explicit non-goals.
   **Stop if:** the plan changes an unapproved interface, trust boundary, or
   outcome.
   **Observable result:** every planned edit exists for a stated criterion.

4. **Implement the smallest coherent change.** Work on an isolated branch or
   worktree. Keep edits inside the approved paths. Preserve unrelated user work.
   **Stop if:** implementation needs credentials, production access, destructive
   action, or wider scope.
   **Observable result:** the diff contains one explainable change and no
   unrelated cleanup.

5. **Run focused tests.** Test observable behaviour and credible failure modes
   at the lowest practical layer. For a defect, first reproduce it with a
   regression test when practical.
   **Stop if:** a test fails for a reason caused by the change.
   **Observable result:** focused test output links each criterion to a checked
   result.

6. **Run the applicable aggregate gate.** Use the repository's complete
   relevant lint, type, test, build, and security checks. Do not weaken an
   assertion or silently skip an applicable check to obtain a pass.
   **Stop if:** the gate is red or its scope cannot be determined.
   **Observable result:** a reproducible command and its result are recorded.

7. **Request independent review.** Give a reviewer the acceptance criteria and
   diff without the maker's persuasive narrative. Prefer a different harness
   with read-only tools. The reviewer returns findings, not approval.
   **Stop if:** required review is unavailable. Record weaker separation as a
   limitation and route the decision to a human reviewer.
   **Observable result:** a review record states the reviewer, access level,
   independence achieved, and findings.

8. **Verify findings and repair within bounds.** Check each material finding
   against the repository and classify it as accepted, rejected, deferred, or
   inconclusive. Repair only accepted in-scope findings. Rerun focused tests and
   any gate invalidated by the repair.
   **Stop if:** repair changes the approved intent, does not converge, or needs
   more than the allowed repair rounds.
   **Observable result:** every material finding has a disposition and evidence.

9. **Return the decision to a human.** Present the intent, criterion status,
   diff explanation, gate results, review record, finding dispositions,
   recovery path, and residual risk. The human decides whether to revise,
   deliver, or stop.
   **Stop if:** the requested action exceeds the recorded grant.
   **Observable result:** the next action and its accountable owner are explicit.

10. **Create the handoff record.** Record the exact commit, commands run,
    results, review limitations, unresolved risks, and resume boundary. Keep
    planned work separate from completed work.
    **Stop if:** a completion claim has no supporting artifact.
    **Observable result:** another engineer can reproduce the checks and continue
    without trusting the agent's memory.

## Failure modes

| Failure | Detection | Recovery | Residual risk |
|---|---|---|---|
| Vague intent lets the agent choose the outcome | Criteria cannot map to observable results | Stop and obtain a bounded task with explicit non-goals | Written criteria can still encode the wrong business decision |
| Scope expands during implementation | Diff contains paths or interfaces absent from the plan | Revert the out-of-scope work and request a new decision | Hidden coupling can appear only during integration |
| A green focused test hides a system failure | Aggregate gate or integration check fails | Fix within scope, or stop and escalate the boundary | No finite suite proves absence of defects |
| The maker reviews its own assumptions | Review uses the same context, write access, or maker narrative | Use a read-only independent reviewer or record the limitation for human review | Different tools can still share the same blind spot |
| Review findings become automatic instructions | A proposed fix is applied without repository evidence | Verify and disposition each finding before repair | Human reviewers can also make incorrect judgements |
| Authority grows by implication | A local implementation grant is treated as permission to push, merge, or deploy | Stop at the recorded maximum action and request a specific grant | A forged or stale grant needs separate identity and policy controls |
| Evidence is incomplete or stale | The handoff omits a commit, command, result, or unresolved risk | Rerun the check or mark the claim unproved | External systems can change after evidence is captured |
| Repairs loop without convergence | The same finding returns or new repairs break prior checks | Stop after the bounded repair allowance and reassess the plan or risk tier | The task may require a wider redesign and new approval |

## Evidence

The claim classes in this draft are:

- `sourced`: a public primary source supports the stated control. This class is
  not an implementation outcome claim.
- `practice`: an operating preference in this guide. A team must validate it in
  its own environment.
- `proposal`: an option to evaluate. It is not represented as implemented.

| Claim | Class | Evidence |
|---|---|---|
| Use approved intent, bounded implementation, deterministic gates, independent review, human authority, and an evidence-backed handoff as one delivery loop | `practice` | This guide synthesises the sourced controls below. The public sources do not define or demonstrate the complete agent loop. |
| Protect code with least-privilege access and have a code owner review and approve changes made by others | `sourced` | [NIST SSDF 1.1, PS.1.1, page 9](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=17) |
| Perform review or automated analysis under organisational policy, then record and triage findings and recommended repairs | `sourced` | [NIST SSDF 1.1, PW.7.1 and PW.7.2, pages 14-15](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=22) |
| Required reviews and status checks can gate a protected branch, and a repository can require approval from someone other than the latest contributor | `sourced` | [GitHub Docs: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) |
| Scope, design, perform, and document testing; retain regression tests for previously reported vulnerabilities | `sourced` | [NIST SSDF 1.1, PW.8.2, page 15](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf#page=23) |
| A provenance record can identify where, when, and how a software artifact was produced | `sourced` | [SLSA 1.2: Provenance](https://slsa.dev/spec/v1.2/provenance) |
| Use an isolated branch or worktree and keep one coherent change per delivery record | `practice` | This guide's operating recommendation; validate it against local repository and deployment controls |
| Teams can encode the risk decision and evidence ledger as repository checks after the manual loop is stable | `proposal` | Evaluate only after repeated use identifies a deterministic rule with acceptable maintenance and false-positive cost |

## Limits

The public sources support individual controls in this guide. They do not prove
that the combined loop has been implemented or that it improves production
reliability, throughput, scale, customer outcomes, or regulatory compliance.

The evidence section cites only public sources. Claim review and privacy review
remain pending. A human must complete both reviews before publication.

Your team must verify local branch protection, reviewer separation, gate
coverage, credential boundaries, rollback, continuous integration, and the
identity and scope of each human grant. If a local control cannot produce the
evidence described here, narrow the automation or keep the decision manual.

## Apply it

Use the broader [platform engineering approach](/platform) to place this loop
within your system's security, observability, and operating boundaries.

For a technical call, bring one proposed repository change, its highest-risk
boundary, and the gate you trust least. The call can map that concrete task to
an approval boundary, review plan, and evidence-backed handoff.
