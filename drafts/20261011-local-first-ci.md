---
status: draft
published: false
claim_review: pending
privacy_review: pending
category: AI-assisted engineering & software factories
topics:
  - delivery-gates
  - verification
  - security-and-privacy
  - cost
---
<!-- playbook-capture:fingerprint=9a291d8b897261148de82815bf8d83a7107b2e43a826e582a7d06392aa0465ec -->
# Local-first CI with hosted acceptance

Assign one tool to each continuous integration (CI) job, validate changes
locally, and reserve hosted execution for independent evidence that local
tools cannot produce. This playbook separates local workflow emulation, Git
hooks, static workflow security checks, dependency updates, and runner
infrastructure, because they solve different jobs and fail in different ways.

## Approval and scope

The captain's exact approval was "approve the playbook and fix the bridge errors".
The approved interpretation authorizes playbook capture only. It does not
authorize GuideX implementation, including fixing the Bridge workflow errors,
or any merge. Publication requires separately established repository authority.

## Sources

All external sources were accessed on **2026-10-11**. Version numbers,
advisory states, pricing, and documented limits describe that date. Recheck
them before acting on a version-sensitive claim.

- [act: unsupported functionality](https://nektosact.com/not_supported.html),
  [usage](https://nektosact.com/usage/index.html),
  [runner images](https://nektosact.com/usage/runners.html)
- [pre-commit: supported Git hooks](https://pre-commit.com/#supported-git-hooks)
- [Lefthook](https://lefthook.dev/)
- [actionlint checks](https://github.com/rhysd/actionlint/blob/main/docs/checks.md)
- [zizmor audit rules](https://docs.zizmor.sh/audits/),
  [usage](https://docs.zizmor.sh/usage/)
- [GitHub Actions workflow syntax: paths and paths-ignore](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushpull_requestpull_request_targetpathspaths-ignore),
  [Git diff comparisons](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#git-diff-comparisons)
- [dorny/paths-filter README](https://github.com/dorny/paths-filter#readme),
  [GHSA-7hc6-8hq5-9q2m](https://github.com/dorny/paths-filter/security/advisories/GHSA-7hc6-8hq5-9q2m)
- [tj-actions/changed-files advisory GHSA-mrrh-fwg8-r2c3](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)
- [pinact README](https://github.com/suzuki-shunsuke/pinact#readme),
  [check semantics](https://github.com/suzuki-shunsuke/pinact/blob/main/docs/check.md)
- [Ratchet README](https://github.com/sethvargo/ratchet#readme)
- [GitHub Actions secure use: keeping actions secure and up to date](https://docs.github.com/en/actions/reference/security/secure-use#keeping-the-actions-in-your-workflows-secure-and-up-to-date),
  [hardening for self-hosted runners](https://docs.github.com/en/actions/reference/security/secure-use#hardening-for-self-hosted-runners)
- [Dependabot on Actions: runner options](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-on-actions#runner-options),
  [Dependabot alerts: limitations](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts#limitations),
  [Dependabot options: target branch](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#target-branch-)
- [Renovate: GitHub Actions manager](https://docs.renovatebot.com/modules/manager/github-actions/),
  [running Renovate](https://docs.renovatebot.com/getting-started/running/)
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions),
  [runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)
- [Self-hosted runners](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners),
  [ephemeral runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners#ephemeral-runners-for-autoscaling),
  [compromised runners](https://docs.github.com/en/actions/concepts/security/compromised-runners)
- [Dagger README](https://github.com/dagger/dagger#readme),
  [GitHub Actions integration](https://docs.dagger.io/0.21/getting-started/ci-integrations/github-actions/),
  [pricing](https://dagger.io/pricing/)
- Internal case evidence: *GuideX CI/CD tooling: Bridge-first recommendation*,
  firstmate research report, 11 October 2026, with its linked budget audit,
  billing diagnosis, and signing-log audit. The underlying internal research
  report is not public and is held outside this repository under the captain's
  approved privacy-preserving exception: "approve the CI playbook internal
  source note". The supporting reports are also not public. The sanitized,
  dated [case study](#case-study-guidex-bridge-11-october-2026) summarizes what
  they support without linking or copying the private reports.

## At a glance

| Question | Rule |
| --- | --- |
| Where do I catch most defects? | Locally, with the project's own test commands and existing policy gate. Hosted runs are for evidence that only GitHub can produce. |
| Can a local emulator prove a workflow is safe to merge? | No. act documents that it does not emulate concurrency, job permissions, timeouts, environments, or OpenID Connect ([act](https://nektosact.com/not_supported.html)). |
| Which two workflow checks pair well? | A syntax and type checker (actionlint) and a security auditor (zizmor). They overlap on injection and differ elsewhere. |
| Should I add a hook framework? | Not when a working policy gate already owns hook composition. A hook manager installs tools. It does not define policy. |
| How do I skip irrelevant jobs? | Native `paths` filters for a whole optional workflow. A selector action only when a required aggregate must always report. |
| Does a full SHA pin make an action safe? | No. A SHA pins one commit. Review provenance and advisories separately. GitHub Actions alerts do not cover SHA-pinned references ([GitHub](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts#limitations)). |
| Is a private repository enough to make a self-hosted runner safe? | No. Private visibility is not a sandbox. Separate admission, isolation, identity, persistence, and recovery. |
| How do I count hosted cost? | Sum rounded job durations across all attempts. Never credit a saving unless a comparable run was actually avoided. |

## Start here

```text
Policy/test command -> workflow lint -> optional local emulation
                                           |
                                  hosted acceptance
                                           |
                             measured cost and defect evidence
```

Takeaway: use cheap local feedback without claiming it proves GitHub's
security or merge controls.

The flow has four stages. Each has one owner and one kind of evidence.

1. **Policy and test command.** The repository's own test runner and its
   existing pre-push or pre-commit policy gate. Catches application defects
   and policy violations before a push.
2. **Workflow lint.** actionlint and zizmor read workflow YAML without running
   it. Catches invalid expressions, obsolete action runtimes, excessive
   permissions, unsafe triggers, and unpinned references.
3. **Optional local emulation.** act runs one allowlisted, secretless Linux job
   to debug shell, setup, and test wiring. It cannot certify authorization.
4. **Hosted acceptance.** A small GitHub-hosted job that proves event routing,
   permissions, required-check names, and cancellation behave as intended.
   This is the only stage that spends hosted minutes.

Stages 1 to 3 run before a reviewer sees the change. Stage 4 runs once per
reviewed change. Measurement wraps all four: count defects caught locally,
hosted retries avoided, and rounded job minutes spent.

## Choose by job

Pick one tool for each job. Do not install two tools for the same job.

| Job | Default | Alternative | Choose the alternative when |
| --- | --- | --- | --- |
| Run application tests | Direct project commands (Gradle, npm, pytest) | act on one allowlisted job | You need to debug action setup or shell wiring, not test logic. Local test exit codes are the success criterion, not cloud-auth parity. |
| Run a GitHub Actions job locally | act, one explicit workflow and job, synthetic event payload | runner.server / Runner.Client | A specific act incompatibility blocks a valuable workflow. It adds a .NET server lifecycle, and its experimental packaging notes macOS arm64 crashes. |
| Run checks before commit or push | The existing policy gate and hook composition | pre-commit or Lefthook, never both | You are maintaining many individual tool environments and that is a measured problem. Prove intermediate-commit, multiple-ref, stdin, and exit-code behavior before switching. |
| Validate workflow syntax | actionlint, offline, ShellCheck and Pyflakes integrations optional | None in this set | Not applicable. |
| Audit workflow security | zizmor, offline by default, online audit recorded when run | None in this set | Not applicable. Offline success cannot claim online advisory coverage. |
| Skip a whole optional workflow | Native `paths` and `paths-ignore` | dorny/paths-filter, booleans only, patched version | A required aggregate must always report while expensive children skip. A natively skipped required workflow can stay pending. |
| Pin action references before merge | pinact, write mode constrained to reviewed paths | Ratchet | You run a mixed CI estate (CircleCI, GitLab CI, Tekton) and need its broader format support. |
| Keep accepted pins current | Dependabot, Actions ecosystem only, weekly group, no auto-merge | Renovate | You need cross-ecosystem policy, custom extraction, or grouping beyond the native service. Do not run both on the same manifests. |
| Run jobs on your own hardware | Hosted Linux runner, bounded | Disposable isolated Linux VM runner, one job per guest | A separate security and capacity case is approved. A persistent runner in an operator account is rejected. |
| Make pipelines portable | Project commands plus a shell dispatcher | Dagger | Measured duplication between local and CI pipelines justifies owning pipeline code. It is not YAML emulation. |

### act versus direct commands

act consumes existing workflow YAML and accepts synthetic event payloads. Its
default invocation can select every push workflow, so require an explicit file
and job. Its images differ from GitHub-hosted machines. On macOS, Linux
containers need a container runtime, and amd64 parity may need emulation. Never
map a Linux job onto a credential-bearing host as a convenience
([act usage](https://nektosact.com/usage/index.html),
[runner images](https://nektosact.com/usage/runners.html)).

Direct project commands remain the lowest-cost loop for code changes. They do
not test event routing or action setup. A hosted Linux job remains the
reference for GitHub behavior.

### pre-commit versus Lefthook versus an existing gate

A hook manager and a policy implementation are separate responsibilities.
pre-commit provides reusable hook definitions, isolated language environments,
multiple hook stages, and all-files execution
([pre-commit](https://pre-commit.com/#supported-git-hooks)). Lefthook is a Go
binary that runs configured commands with file selection and parallel
execution ([Lefthook](https://lefthook.dev/)). Neither supplies an
outgoing-history, ticket, or digest policy. If a repository already owns that
policy through its own gate, adding a manager adds an installer at an already
composed hook boundary. If you adopt one later, call the canonical policy
entrypoint from it. Do not assume a `pre-push` stage alone preserves a range
gate's semantics.

## Trust boundaries

Each row names one boundary and one rule. Treat a rule as a stop condition
during review, not a suggestion.

| Boundary | Rule | Why |
| --- | --- | --- |
| Workflow code | Lint for syntax and audit for security. A workflow can be syntactically correct and still unsafe. | actionlint and zizmor check different properties ([actionlint](https://github.com/rhysd/actionlint/blob/main/docs/checks.md), [zizmor](https://docs.zizmor.sh/audits/)). Neither proves application tests are meaningful. |
| Third-party actions | Treat a file-selection action as an executable dependency. Use reviewed patched commits. Prefer boolean outputs. Keep filenames out of shell-source interpolation. | A high-severity paths-filter advisory affected filename shell escaping; patched versions are 3.0.4 and 4.0.3 ([GHSA-7hc6-8hq5-9q2m](https://github.com/dorny/paths-filter/security/advisories/GHSA-7hc6-8hq5-9q2m)). The separate tj-actions/changed-files compromise shows a selector is supply-chain input; it is not evidence that dorny's project was compromised ([GHSA-mrrh-fwg8-r2c3](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)). |
| Local host credentials | Run local emulation in a disposable workspace with no ambient cloud or GitHub credentials, SSH agent, or operator-home mount. | act executes workflow steps. A convenience mount turns a workflow defect into a credential exposure. |
| Secrets and output | Review secret creation, use, output, and cleanup. `${{ secrets.* }}` references and log masking do not prove a generated file is safe to print. | The [case study](#case-study-guidex-bridge-11-october-2026) records a workflow that printed a generated secret-bearing file while using valid secret references. |
| Pins | A full SHA pins one commit. Review owner, repository, release-to-commit correspondence, and advisory status. | pinact's offline check verifies SHA shape, not provenance or vulnerabilities ([pinact check](https://github.com/suzuki-shunsuke/pinact/blob/main/docs/check.md)). GitHub Actions alerts cover semantic versions, not SHA versions ([GitHub](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts#limitations)). |
| Update actors | One preparation tool and one recurring update owner. Never two automated writers on the same manifests. Never auto-merge action updates. | pinact prepares new references before merge; a bot maintains accepted references ([GitHub](https://docs.github.com/en/actions/reference/security/secure-use#keeping-the-actions-in-your-workflows-secure-and-up-to-date)). Dependabot security updates use the default branch even when version updates target another branch ([GitHub](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#target-branch-)). |
| Caches and artifacts | Separate trusted and untrusted caches. Never promote an unreviewed cache or artifact into a privileged job. | A compromised job can poison what a later privileged job consumes ([GitHub](https://docs.github.com/en/actions/concepts/security/compromised-runners)). |
| Self-hosted runners | Reject a persistent runner in an operator account. If a runner is later approved, use the design below. | Private visibility is not a sandbox. Environment approval controls secret release but does not remove persistence left by an earlier job ([GitHub](https://docs.github.com/en/actions/reference/security/secure-use#hardening-for-self-hosted-runners)). |

### Self-hosted runner design, if one is ever approved

These are proposed controls derived from the threat model. GitHub does not
provide them automatically. GitHub's ephemeral mode handles one-job
registration; infrastructure cleanup remains the operator's responsibility
([GitHub](https://docs.github.com/en/actions/reference/runners/self-hosted-runners#ephemeral-runners-for-autoscaling)).

| Boundary | Required design |
| --- | --- |
| Admission | One repository initially. Trusted reviewed commit SHAs. Explicitly approved validation workflows. No public, fork, or arbitrary pull-request execution. No privileged `pull_request_target` checkout. Labels route jobs; they are not an authorization boundary. |
| Isolation | One disposable VM per job with a distinct unprivileged guest account. No operator home, keychain, SSH agent, cloud CLI profile, Docker socket, sibling checkout, or shared workspace mounts. No production or private service network access. A container sharing the host daemon is not this boundary. |
| OS and architecture | Match the hosted target. GitHub requires Linux for Docker container actions and services. Confirm amd64 versus arm64 dependencies and emulation cost. |
| Identity | Short-lived, least-privilege job token. No deployment secrets or `id-token: write` for validation. Keep registration and control credentials outside the guest. |
| Persistence | Register an ephemeral or just-in-time runner. Destroy the guest after one job. Deregistration alone does not erase disk or memory. |
| Operation | Capacity reservation, one job initially, a named patch and image owner, bounded queue and timeout, sanitized external logs, a tested rebuild procedure. Update runners within GitHub's allowed window. |
| Recovery | Stop scheduling to the pool. Isolate guest and host. Preserve bounded evidence. Revoke reachable credentials and registrations. Invalidate affected caches and artifacts. Rebuild from a verified image. Review produced outputs. Only then restore service. Host escape requires host rebuild and broader credential review, not just deleting a work directory. |

Current GitHub billing documentation says self-hosted runner use is free. It
does not make hardware, storage, patching, or incident response free
([GitHub](https://docs.github.com/en/billing/concepts/product-billing/github-actions)).

## Spend only on useful evidence

### Filter events and jobs

Native `paths` filters add no action dependency and can avoid runner
allocation entirely. Include every actual input: build files and wrappers,
containers, resources, tests, contract inputs, and the workflow file itself.
Do not exclude all Markdown mechanically if a file affects an artifact.

GitHub documentation accessed on 2026-10-11 states that push diffs use two
dots and pull requests three. Pushes with more than 1,000 commits and diff
timeouts run unconditionally. A matching file beyond the first 3,000 returned
files can be missed
([GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#git-diff-comparisons)).
Recheck these dated limits before changing filters.

### Respect required-check semantics

A required workflow skipped by native event filters can remain pending and
block the merge
([GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushpull_requestpull_request_targetpathspaths-ignore)).
Inventory required checks first. Use native filters only on workflows that are
not required. When a required aggregate must always report while expensive
children skip, use conditional children and a fail-closed aggregate. The
aggregate must fail if selection fails, if a required child fails or cancels,
or if an expected child never ran.

### Cancel superseded work

Cancel obsolete validation runs on pull-request branches. Do not cancel runs on
the default branch. Give every validation job a hard timeout.

### Count rounded job minutes

Use the sum of rounded job durations, including all attempts, not workflow
wall time. GitHub rounds each job up to a whole minute
([GitHub](https://docs.github.com/en/billing/reference/actions-runner-pricing)).
Report consumption separately from paid amount. A free-allowance job still
consumes capacity. Zero paid amount is not zero consumption.

### Keep baselines honest

Separate three quantities before claiming a saving:

| Quantity | How to count it | Common error |
| --- | --- | --- |
| Observed use | Rounded job minutes actually consumed in the period | Using workflow wall time, or omitting failed attempts |
| Avoided retries | Minutes of a comparable hosted run that a local check demonstrably prevented | Crediting a historical run size without an actual avoided run |
| Already-paused work | Minutes of heavy workflows that were already disabled before the change | Counting the pause as a new saving from the new tooling |

Worked scenario from the case study, using that repository's historical rounded
durations: a test workflow run of about 24.5 minutes, a mutation run of 34, a
deployment of 10. If 20 optional workflow-quality events cost 40 minutes and
local checks prevent two otherwise-needed test retries, the modeled net is
49 − 40 = 9 minutes saved. If no retries are avoided, the net is 40 minutes
added. The numbers are a scenario, not an observed rate. Deployment retries
are never a pilot experiment.

Dependabot update generation on standard hosted runners does not consume
included Actions minutes. Workflows triggered by its changes still do. Larger
Dependabot runners are billed
([GitHub](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-on-actions#runner-options)).
Weekly grouping bounds routine frequency; rebases, security updates, and edits
can add runs. Grouping is a control, not a guaranteed saving.

## Pilot one repository

Run the pilot in one repository on its integration branch. Keep every heavy
workflow pause in place. Each step has a stop condition and an observable
result.

1. **Freeze the baseline.** Record branch heads, workflow states and triggers,
   runner labels, pause states, tool versions, hooks, current required checks,
   and rounded minutes for the prior period.
   **Stop if:** you cannot read required checks or rulesets. Local tool
   preparation can continue; filtering and enforcement changes cannot.
   **Observable result:** a dated baseline another engineer can diff against.

2. **Establish local failure evidence.** Run every workflow through actionlint
   and zizmor. Resolve or explicitly disposition each finding. Keep a
   negative fixture for each class: invalid expression, excessive permission,
   unsafe trigger or checkout, unpinned action, secret interpolation, obsolete
   action runtime. Prove the checker fails nonzero, does not fix files
   automatically, and never emits a real secret. Shell scripts receive
   `bash -n` before behavior checks.
   **Stop if:** a finding needs a blanket ignore to pass.
   **Observable result:** a checker command, its exit codes on fixtures, and a
   findings ledger with one disposition each.

3. **Keep the existing policy gate working.** Verify the installed range gate
   on clean, secret-added-then-removed, tracked-lock, new-branch, and
   multiple-ref cases in isolated temporary repositories. Reuse canonical
   fixtures rather than writing a second policy test suite. Change no global
   Git settings or operator hooks.
   **Stop if:** hook chaining or exit semantics change.
   **Observable result:** the gate's existing fixtures still pass.

4. **Exercise one local execution path.** Run direct tests first. Then, if
   useful, allowlist one workflow, one job, and one module in act with a
   synthetic `workflow_dispatch` payload and a reviewed pinned Linux image.
   Inspect the selected job graph before running. Use a disposable workspace
   with no ambient credentials. Do not run deployment, publishing, mutation, or
   a full matrix through a default act invocation.
   **Stop if:** the job needs a secret or a credential-bearing mount.
   **Observable result:** local test exit and report match the hosted result
   for the same commit.

5. **Run bounded hosted acceptance.** Validate four change types: ordinary
   source, workflow or tool, docs-only, and a rapid superseding update.
   Existing required checks must still report. The optional quality job runs
   only for its inputs and cancels obsolete runs. Docs-only changes must not
   start application builds or deployment. Confirm permissions and check names
   in GitHub; act cannot prove them. Cap the initial pilot at about four events
   with a hard timeout of a few minutes each. Keep negative fixtures local; do
   not buy hosted failures to retest parser behavior.
   **Stop if:** an unexpected deployment, privileged token or secret exposure,
   missing required check, ambiguous filter result, changed trust boundary, or
   unexplained billing appears.
   **Observable result:** rounded job minutes per event and the check names
   GitHub reported.

6. **Evaluate, then decide rollout.** Collect two active weeks or at least ten
   relevant changes. If activity is lower, label the evidence insufficient
   rather than manufacturing traffic. Review findings caught locally, failed
   hosted retries, rounded minutes, developer latency, required-check behavior,
   and baseline drift. Target a median of 1 to 2 rounded minutes for the
   optional job; investigate a p95 above 3.
   **Stop if:** any missed required check, extra deployment, or secret exposure
   occurred. These are hard acceptance failures.
   **Observable result:** a decision record with the measured quantities from
   the honest-baselines table.

7. **Activate an update service only after its own gate.** The configuration
   must be effective on the GitHub default branch while version changes target
   the agreed integration branch. If the default branch triggers production
   deployment on push, prepare an exact promotion plan first. Account for
   default-branch security updates and the SHA-alert gap.
   **Stop if:** activation requires merging configuration to a
   deployment-triggering branch as a convenience.
   **Observable result:** one weekly grouped update with a bounded open-change
   count and no auto-merge.

### Rollback

Revert only the pilot-owned checker, configuration, and workflow. Preserve the
existing policy gate and every heavy pause. If an update bot causes churn,
pause its configuration through its owner; do not disable unrelated security
checks. Keep safe reviewed pins and runtime fixes unless evidence requires a
specific rollback. Never restore a secret-printing command as part of a blanket
revert. A runner incident uses the recovery row in the runner design table,
not this workflow rollback.

## Revisit conditions

These are conditions, not an installation queue.

| Tool or change | Revisit when |
| --- | --- |
| pre-commit or Lefthook | Maintaining many individual tool environments is a measured problem, and the manager can call the canonical policy entrypoint without changing its semantics. |
| dorny/paths-filter | A required aggregate must stay reporting while expensive children skip, and the patched commit is reviewed and pinned. |
| runner.server | A specific act incompatibility blocks a valuable workflow. |
| Renovate | Cross-ecosystem dependency policy, custom extraction, or grouping exceeds the native service. Review its copyleft licence and hosting model first. |
| Disposable self-hosted runner | A separate security and capacity case is approved, with the design table above as the minimum. |
| Dagger | Measured duplication between local and CI pipeline code justifies owning a pipeline abstraction. Its cloud services are optional and separately priced; running it on a hosted runner still consumes that runner's time ([Dagger](https://dagger.io/pricing/)). |
| Consolidating the optional quality job into a canonical gate | The pilot shows stable findings and a cross-repository rollout is separately scoped. |

## Case study: GuideX Bridge, 11 October 2026

This section records dated observations from one small estate. The source is
the internal research report named under [Sources](#sources). The report is
not public and is held outside this repository under the captain's approved
privacy-preserving exception: "approve the CI playbook internal source note".
This sanitized, dated case study does not link or copy the private report.
The observations are labeled `observation`. They are not product facts about
any tool, and they do not claim that the estate deployed the recommended tooling.

**Context.** Bridge is a Gradle-based service repository in a small
multi-repository estate. A meta repository distributes one canonical policy
gate (GX-007) to consumer hooks and CI. The gate checks secrets, tracked locks,
digests, ticket references, and merge markers on the outgoing commit range.
Heavy hosted workflows for tests, mutation testing, and deployment were
manually paused at the time of the report.

| Observation | What it supports | What it does not support |
| --- | --- | --- |
| Zero-job startup failures across several repositories traced to an administrative billing restriction, diagnosed from run annotations and account records. | Diagnose administrative rejection independently of source defects. A run that starts no job is not evidence of defective YAML, zero demand, or a runner migration requirement. | Any claim about the current billing state, or that self-hosting would bypass an account-level restriction. |
| actionlint 1.7.12 on five downloaded workflows reported two errors: an obsolete `setup-gcloud@v1` action runtime, twice in the deployment workflow. ShellCheck and Pyflakes were disabled. | Static lint finds real defects the billing diagnosis could not. The two defects are separate from the billing rejection. They warrant a reviewed runtime update and pin. | Full shell or Python validation of those workflows. The capture of this playbook did not fix the workflows. |
| A mobile signing workflow printed a generated key properties file. Several returned runs used that command and built successfully. | Secret references and log masking do not prove generated files are safe to print. Review secret creation, use, output, and cleanup. | Unmasked disclosure or key compromise. Neither was established. No rotation conclusion is drawn here. |
| Ruleset and branch-protection reads returned insufficient permissions. | Hosted merge enforcement must be read by an authorized operator before filtering or enforcement changes. | That merge enforcement exists or does not exist. |
| The integration branch's gate workflow ran on pull-request events with a read-only token, a short timeout, and cancellation. The default branch's copy remained manual-only and triggered production deployment on push. | Branches are not interchangeable. Update-bot default-branch semantics need a promotion plan first. | Any branch retirement or default-branch change. |
| Historical rounded job durations: tests about 24.5 minutes per run, mutation 34, deployment 10. | The scenario arithmetic in [Keep baselines honest](#keep-baselines-honest). Current heavy pauses already provide the avoidance; a new tool cannot claim it again. | New benchmarks or savings from installing any tool. |

**Recommended starting set for that estate, as proposed, not implemented:**
keep GX-007 and direct Gradle tests; add actionlint and zizmor behind one
repository-owned command; use pinact in reviewed preparation mode; allowlist
one secretless act job as an optional diagnostic; add one short optional
hosted workflow-quality job filtered by native `paths`. Defer Dependabot
activation until the default-branch and promotion boundary is handled. Defer
hook-framework migration, runner infrastructure, and Dagger.

**Limits of this case.** The report was a read-only scout. No candidate tool
except the already installed actionlint was executed against project code.
No workflow was dispatched. No billing was settled, no monitor verified, no
secret path repaired, and no required-check enforcement proved. The estate's
canonical harness is internal code; nothing here grants a licence to reuse it.

## Evidence

Claim classes:

- `sourced`: a public primary source supports the claim. The source date is
  2026-10-11 unless stated.
- `practice`: an operating recommendation in this playbook. Validate it in
  your own environment.
- `proposal`: an option to evaluate. It is not represented as implemented.
- `observation`: dated internal case evidence from one estate. Not a general
  product fact.

| Claim | Class | Evidence |
| --- | --- | --- |
| Local workflow emulation cannot certify all GitHub controls | `sourced` | act documents missing concurrency, permissions, timeout, environment, and OIDC behavior ([act](https://nektosact.com/not_supported.html)). Do not generalize to every emulator. |
| A hook manager and a policy implementation are separate responsibilities | `practice` | Supported by [pre-commit stages](https://pre-commit.com/#supported-git-hooks) and [Lefthook](https://lefthook.dev/) capabilities, and by the case study's canonical gate. Not a claim that one manager is best. |
| Syntax checking and workflow security auditing are complementary | `sourced` + `practice` | [actionlint checks](https://github.com/rhysd/actionlint/blob/main/docs/checks.md), [zizmor audits](https://docs.zizmor.sh/audits/). Recommend both when findings justify the maintenance cost. |
| Native path filters can skip a whole run but can leave a required check pending | `sourced` | [GitHub path semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushpull_requestpull_request_targetpathspaths-ignore). See [Filter events and jobs](#filter-events-and-jobs) for the dated diff limits. |
| File-selection actions are executable dependencies; filenames are untrusted input | `sourced` + `practice` | [paths-filter README](https://github.com/dorny/paths-filter#readme), [GHSA-7hc6-8hq5-9q2m](https://github.com/dorny/paths-filter/security/advisories/GHSA-7hc6-8hq5-9q2m), [GHSA-mrrh-fwg8-r2c3](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3). The two incidents are distinct. |
| Pinning and updating solve different parts of dependency control | `practice` | Grounded in [pinact](https://github.com/suzuki-shunsuke/pinact#readme), [Ratchet](https://github.com/sethvargo/ratchet#readme), [Renovate](https://docs.renovatebot.com/modules/manager/github-actions/), and [GitHub](https://docs.github.com/en/actions/reference/security/secure-use#keeping-the-actions-in-your-workflows-secure-and-up-to-date). A full SHA can pin a vulnerable commit. |
| Dependabot updating SHA references does not give alert coverage for those pins | `sourced` | [Dependabot alert limitations](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts#limitations). Do not weaken pinning to obtain alerts. |
| Update generation and update-triggered CI are different costs | `sourced` + inference | [Dependabot compute](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-on-actions#runner-options), [billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions). Measure resulting workflow jobs. |
| Private repositories do not make persistent self-hosted runners safe | `sourced` + `proposal` | [Runner hardening](https://docs.github.com/en/actions/reference/security/secure-use#hardening-for-self-hosted-runners), [compromised runners](https://docs.github.com/en/actions/concepts/security/compromised-runners), [ephemeral runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners#ephemeral-runners-for-autoscaling). The design table is proposed controls. |
| Pipeline portability requires a pipeline abstraction, not YAML emulation | `sourced` + `practice` | [Dagger](https://github.com/dagger/dagger#readme), [GitHub integration](https://docs.dagger.io/0.21/getting-started/ci-integrations/github-actions/). No automatic cost-saving claim. |
| Diagnose administrative startup rejection independently of source defects | `observation` | Case study, billing diagnosis and local actionlint result. Captures the method, not payment detail. |
| Secret references and log masking do not prove generated files are safe to print | `observation` | Case study, signing-log audit. "Unsafe output found; unmasked disclosure not established." |
| Savings must separate observed use, avoided retries, and already-paused work | `practice` + `observation` | [Runner rounding](https://docs.github.com/en/billing/reference/actions-runner-pricing), case study durations. Zero paid amount is not zero consumption. |
| The recommended starting set for the case estate | `proposal` | Case study. Not implemented by this capture. |

## Limits

This playbook does not prove that any tool reduces hosted minutes, defect
rates, or developer latency in your repository. Every saving must be measured
against the honest-baselines table.

Version numbers, advisory patch levels, pricing tiers, and documented limits
describe 2026-10-11. The [appendix](#appendix-observed-versions-and-licences-2026-10-11)
is a dated snapshot, not a current-version claim.

The case study is one estate's read-only scout. It does not establish that the
estate adopted any tool, settled billing, repaired secret output, rotated keys,
enabled a monitor, or enforces required checks. It contains no logs, secret
values, identifiers, billing records, or access lists, and it links no private
repository.

This playbook is not a production runbook. It contains no runner registration
commands, identity and access changes, key rotation procedure, or deployment
authority. Each of those needs its own scoped decision.

Claim review and privacy review remain pending. A human must complete both
before promotion from `drafts/`.

## Maintenance

- **Owner:** the repository owner, as for every playbook here.
- **Review triggers:** a major release of act, actionlint, or zizmor; a change
  to GitHub's path-filter, required-check, Dependabot alert, or runner pricing
  documentation; a new advisory against any action named here; or new case
  evidence that contradicts an `observation` row.
- **On review:** reaccess every source, update the access date, refresh the
  appendix, and move any superseded claim to the Limits section rather than
  deleting its history.

## Checklist

- [ ] Inventory required checks and rulesets before any filtering change.
- [ ] Run actionlint and zizmor offline on every workflow; record whether an online audit ran.
- [ ] Keep one negative fixture per finding class; prove nonzero exit and no auto-fix.
- [ ] Keep the existing policy gate and its fixtures unchanged.
- [ ] Allowlist one explicit act workflow and job; never a default invocation.
- [ ] Run emulation in a disposable workspace with no ambient credentials.
- [ ] Review each pin's owner, release-to-commit correspondence, and advisories, not just SHA shape.
- [ ] Assign one preparation tool and one update owner; no auto-merge.
- [ ] Use native `paths` only on non-required workflows.
- [ ] Count rounded job minutes across all attempts; separate observed, avoided, and already-paused.
- [ ] Give every validation job a hard timeout; cancel superseded pull-request runs only.
- [ ] Reject persistent runners in operator accounts.

## Rules of thumb

- Catch defects locally. Keep hosted proof for GitHub-specific behavior.
- One tool per job. Two tools for one job is a maintenance debt, not redundancy.
- A green emulator run proves wiring, not authorization.
- A full SHA is a pin, not a safety review.
- A skipped required check is a blocked merge, not a saved minute.
- A paused workflow is not a saving you get to count twice.
- A private repository is not a sandbox.
- Diagnose the platform before you blame the YAML, then lint the YAML anyway.

## Appendix: observed versions and licences, 2026-10-11

Repository metadata read on 2026-10-11. None of the upstream repositories was
archived or disabled. Release recency is a maintenance signal, not a security
warranty. Licence identifiers are repository metadata; dependencies and service
terms need their own review. The disposition column is the case study's
proposal for one estate, not a general ranking.

| Candidate | Latest release observed | Licence | Case-study disposition |
| --- | --- | --- | --- |
| [act](https://github.com/nektos/act/releases/tag/v0.2.89) | v0.2.89, 2026-06-01 | MIT | Adopt as optional diagnostic, one selected secretless job |
| [runner.server](https://github.com/ChristopherHX/runner.server/releases/tag/v3.14.0) | v3.14.0, 2026-01-24 | MIT | Defer |
| [pre-commit](https://github.com/pre-commit/pre-commit/releases/tag/v4.6.2) | v4.6.2, 2026-08-10 | MIT | Defer |
| [Lefthook](https://github.com/evilmartians/lefthook/releases/tag/v2.2.1) | v2.2.1, 2026-10-08 | MIT | Defer |
| [actionlint](https://github.com/rhysd/actionlint/releases/tag/v1.7.12) | v1.7.12, 2026-03-30 | MIT | Adopt |
| [zizmor](https://github.com/zizmorcore/zizmor/releases/tag/v1.30.1) | v1.30.1, 2026-09-09 | MIT | Adopt |
| [paths-filter](https://github.com/dorny/paths-filter/releases/tag/v4.0.3) | v4.0.3, 2026-08-05 | MIT | Conditional, patched commit, booleans only |
| [pinact](https://github.com/suzuki-shunsuke/pinact/releases/tag/v5.0.0) | v5.0.0, 2026-09-12 | MIT | Adopt for reviewed preparation |
| [Ratchet](https://github.com/sethvargo/ratchet/releases/tag/v0.12.0) | v0.12.0, 2026-07-18 | Apache-2.0 | Reject from initial set as duplicate |
| [Renovate](https://github.com/renovatebot/renovate/releases/tag/44.149.3) | 44.149.3, 2026-10-10 | AGPL-3.0 | Defer; review copyleft and hosting model |
| [Dependabot core](https://github.com/dependabot/dependabot-core/releases/tag/v0.399.0) | v0.399.0, 2026-10-05 | MIT; hosted service separate | Preferred update service, deferred activation |
| [GitHub runner](https://github.com/actions/runner/releases/tag/v2.338.0) | v2.338.0, 2026-10-06 | MIT; hosted control plane separate | Hosted use kept bounded; self-hosting deferred |
| [Dagger](https://github.com/dagger/dagger/releases/tag/v0.21.10) | v0.21.10, 2026-09-30 | Apache-2.0; cloud separate | Defer |

pinact v5 documentation requires `--fix=false` together with `--no-api` for
the offline shape check ([pinact](https://github.com/suzuki-shunsuke/pinact#readme)).
Dagger's pricing page listed a free individual early-access tier and a USD 50
per month team tier for up to ten users on the access date
([Dagger](https://dagger.io/pricing/)). That is a service quote, not the cost
of execution.
