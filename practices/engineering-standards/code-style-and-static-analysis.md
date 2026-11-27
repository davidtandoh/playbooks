---
status: published
published: 2026-11-26
claim_review: complete
privacy_review: complete
category: AI-assisted engineering & software factories
topics:
  - architecture
  - verification
  - delivery-gates
  - cost
applies_when:
  - adding or changing formatters, linters, type checks, or compiler diagnostics
  - wiring static analysis into editor hooks, agent hooks, Git hooks, or CI
  - adopting static checks in a repository with existing diagnostic debt
signals:
  - code style
  - static analysis
  - lint
  - formatter
  - typecheck
  - pre-commit
  - lint-on-edit
  - suppression
  - clippy
  - clang-tidy
  - RuboCop
path_globs:
  - "eslint.config.*"
  - "**/eslint.config.*"
  - ".prettierrc*"
  - "**/.prettierrc*"
  - "ruff.toml"
  - "**/ruff.toml"
  - ".golangci.*"
  - "**/.golangci.*"
  - "clippy.toml"
  - "**/clippy.toml"
  - ".clang-tidy"
  - "**/.clang-tidy"
  - ".rubocop.yml"
  - "**/.rubocop.yml"
  - "analysis_options.yaml"
  - "**/analysis_options.yaml"
  - ".clippy.toml"
  - "**/.clippy.toml"
  - "rustfmt.toml"
  - "**/rustfmt.toml"
  - ".rustfmt.toml"
  - "**/.rustfmt.toml"
  - ".clang-format"
  - "**/.clang-format"
  - ".editorconfig"
  - "**/.editorconfig"
  - "mypy.ini"
  - "**/mypy.ini"
  - ".mypy.ini"
  - "**/.mypy.ini"
  - "pyrightconfig.json"
  - "**/pyrightconfig.json"
  - ".scalafmt.conf"
  - "**/.scalafmt.conf"
  - ".swiftlint.yml"
  - "**/.swiftlint.yml"
  - ".swift-format"
  - "**/.swift-format"
  - ".shellcheckrc"
  - "**/.shellcheckrc"
  - ".markdownlint*"
  - "**/.markdownlint*"
  - ".sqlfluff"
  - "**/.sqlfluff"
  - "eslint-suppressions.json"
  - "**/eslint-suppressions.json"
  - ".rubocop_todo.yml"
  - "**/.rubocop_todo.yml"
  - "detekt.yml"
  - "**/detekt.yml"
  - "checkstyle.xml"
  - "**/checkstyle.xml"
  - ".pre-commit-config.yaml"
  - ".githooks/**"
key_rules:
  - Give each static-check responsibility one repository-owned definition with pinned tools and explicit scope. (#define-the-repository-contract)
  - Use edit feedback, staged-snapshot checks, and the full gate as separate enforcement layers. (#use-three-enforcement-layers)
  - Bound edit-check latency, output, and concurrency; report deferred or timed-out checks as incomplete. (#budget-the-fast-path)
  - Preserve unstaged work and partial staging; keep commit and CI checks non-mutating. (#format-safely)
  - Reject new baseline debt and remove resolved allowances through a reviewed ratchet. (#ratchet-debt-and-exceptions)
  - Propagate checker failures and fail on missing tools, invalid configuration, or crashes. (#preserve-failure-contracts)
  - Run the same full static-check definition locally and in required CI checks, with source and scope evidence. (#prove-ci-parity)
skills: none
---
# Code style and static analysis: enforce the rules early

Style and type defects should reach the author before expensive review.
Put the rules in repository-owned commands, return quick feedback after edits,
and reject failing source snapshots before delivery.

Audience: engineers and technical leads setting standards for maintained code,
including code written by agents.

Skill: none yet.

This page defines engineering policy. Tool choices are recommended defaults;
keep justified existing choices. Timing targets are adoption targets, not
measured results. This page supplies no hook implementation and claims no
production outcomes. All examples are synthetic.

## Sources

Primary documentation consulted on 2026-11-26. Check the documentation and help
for the pinned tool version before copying a command.

- [Ruff linting, rule selection, fixes, and suppressions](https://docs.astral.sh/ruff/linter/).
- [Ruff formatter compatibility](https://docs.astral.sh/ruff/formatter/),
  [unused suppressions](https://docs.astral.sh/ruff/rules/unused-noqa/),
  [mypy CLI](https://mypy.readthedocs.io/en/stable/command_line.html), and
  [Pyright configuration](https://microsoft.github.io/pyright/#/configuration).
- [Prettier and linters](https://prettier.io/docs/integrating-with-linters)
  and [ESLint CLI](https://eslint.org/docs/latest/use/command-line-interface).
- [TypeScript CLI and project options](https://www.typescriptlang.org/docs/handbook/compiler-options.html).
- [TypeScript project references](https://www.typescriptlang.org/docs/handbook/project-references.html)
  and [5.6 build behaviour](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-6.html).
- [pre-commit](https://pre-commit.com/): staged-file checks and temporary
  handling of unstaged changes. A manager still needs installation and testing.
- [Detekt baselines](https://detekt.dev/docs/introduction/baseline/),
  [Scalafmt](https://scalameta.org/scalafmt/docs/installation),
  [Scalafix](https://scalacenter.github.io/scalafix/), and
  [google-java-format](https://github.com/google/google-java-format).
- [ktlint](https://github.com/pinterest/ktlint),
  [Checkstyle](https://checkstyle.org/), and [Error Prone flags](https://errorprone.info/docs/flags).
- [Clippy usage](https://doc.rust-lang.org/clippy/usage.html),
  [gofmt](https://pkg.go.dev/cmd/gofmt), and [go vet](https://pkg.go.dev/cmd/vet).
- [rustfmt](https://rust-lang.github.io/rustfmt/),
  [Clippy configuration](https://doc.rust-lang.org/clippy/configuration.html),
  [Rust lint levels](https://doc.rust-lang.org/rustc/lints/levels.html),
  [Staticcheck](https://staticcheck.dev/docs/), and
  [golangci-lint CLI](https://golangci-lint.run/docs/configuration/cli/).
- [ClangFormat](https://clang.llvm.org/docs/ClangFormat.html) and
  [Clang-Tidy](https://clang.llvm.org/extra/clang-tidy/).
- [swift-format](https://github.com/swiftlang/swift-format),
  [SwiftLint](https://realm.github.io/SwiftLint/index.html),
  [.NET formatting](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format),
  and [RuboCop CLI](https://docs.rubocop.org/rubocop/latest/usage/cli_reference.html).
- [.NET analyzer and build enforcement](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview).
- [Biome linting](https://biomejs.dev/linter/) and
  [Oxlint](https://oxc.rs/docs/guide/usage/linter.html): alternatives to evaluate
  against existing rule and plugin requirements.
- [Dart formatting](https://dart.dev/tools/dart-format),
  [Astro checking](https://docs.astro.build/en/reference/cli-reference/#astro-check),
  [ShellCheck](https://www.shellcheck.net/), and
  [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2).
- [Dart analyzer severities](https://dart.dev/tools/dart-analyze),
  [shfmt](https://pkg.go.dev/mvdan.cc/sh/v3/cmd/shfmt),
  [actionlint](https://github.com/rhysd/actionlint), and [zizmor](https://docs.zizmor.sh/).
- [SQLFluff](https://docs.sqlfluff.com/en/stable/),
  [Terraform validation](https://developer.hashicorp.com/terraform/cli/commands/validate),
  and [Buf lint](https://buf.build/docs/lint/).
- *Software Engineering at Google*,
  [Chapter 20: Static Analysis](https://abseil.io/resources/swe-book/html/ch20.html):
  developer trust, useful diagnostics, and workflow integration.
- Distefano, Fähndrich, Logozzo, and O'Hearn,
  [Scaling Static Analyses at Facebook](https://discovery.ucl.ac.uk/id/eprint/10084236/),
  *Communications of the ACM*, 2019. The author archive provides an accessible
  copy of the study linked from the
  [research publication page](https://research.facebook.com/publications/scaling-static-analyses-at-facebook/).
- [OASIS SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html):
  a standard diagnostic interchange format.
- [ESLint bulk suppressions](https://eslint.org/docs/latest/use/suppressions)
  and [Git blame revision exclusions](https://git-scm.com/docs/git-blame).
- [Terraform recursive format checks](https://developer.hashicorp.com/terraform/cli/commands/fmt).

## At a glance

```mermaid
flowchart TB
    RULES["Repository: pinned tools, rules, scope"] --> EDIT["Edit: quick file feedback"]
    RULES --> COMMIT["Commit: check staged snapshot"]
    RULES --> GATE["Full static gate: local and CI"]
    EDIT --> COMMIT
    COMMIT --> GATE
    GATE --> REVIEW["Review: behaviour and design"]
```

Takeaway: the repository owns the rules; each layer checks a declared scope,
and the full gate covers edits that bypass hooks.

| Check | Question it answers | Limit |
| --- | --- | --- |
| Formatter | Does layout match the chosen style? | Does not prove correctness |
| Linter | Does code violate selected static rules? | Only enabled rules and inspected files are covered |
| Type or compile check | Is code consistent with types and build context? | Does not prove runtime behaviour |
| Architecture check | Do dependencies obey component boundaries? | Needs explicit boundary rules |
| Test | Does executed behaviour meet the contract? | Static checks remain necessary |

## Decision guide

### Define the repository contract

Record the following beside the repository's gate instructions:

| Field | Required detail |
| --- | --- |
| Owner | Who reviews rule changes, exclusions, and exceptions |
| Tools | One owner per formatting, linting, and typing responsibility; compatible pinned versions |
| Runtime | Supported language, SDK, compiler, and operating-system versions |
| Commands | Explicit repair command, fast check, staged check, and full non-mutating static gate |
| Scope | Maintained source, tests, scripts, hooks, configuration, and nested packages |
| Exclusions | Generated, vendor, build output, and immutable files; name their validation owner |
| Severity | Which diagnostics block delivery, including warnings |
| Debt | Reviewed baseline mechanism, owner, reason, and review date |

Preserve working tools and the existing hook manager. A manager schedules
commands; it does not define another set of rules. Keep formatting rules out
of a linter when they conflict with the formatter. Pin plugins and build
integrations as well as the executable. Bootstrap dependencies explicitly
before enabling offline hooks.

A configuration file is insufficient evidence of enforcement. Verify the
invocation, inspected scope, exit status, hook activation, and required CI
result. A script named `lint` needs a working configuration and a caller.

Prefer manifest-owned lint levels when supported. Rust workspaces can define
`[workspace.lints.clippy]`; member packages must opt into inheritance with
`[lints] workspace = true`. Keep thresholds and the minimum supported Rust
version (MSRV) in the appropriate Clippy configuration. Set the MSRV so
supported checks avoid suggestions requiring a newer runtime.

The matching paths above cover dedicated check configurations at the root
and in nested packages. General manifests such as `pyproject.toml`,
`Cargo.toml`, and `tsconfig.json` also contain unrelated settings, so they
are not automatic path triggers here. Review their static-check changes
under this page's `applies_when` criteria.

#### Keep diagnostics useful

Measure the effective false-positive rate: the share of reviewed diagnostics
authors judge unhelpful or unactionable, including technically valid findings
with unclear value. Sample author decisions per rule; distinguish justified
exceptions from misunderstandings and inspect recurring suppressions.

As an initial policy, target below 10% per review-time rule and below 5%
overall, drawing on Google's deployment experience. These are adoption
targets, not universal tool accuracy guarantees. Security triage can use a
separate reviewed tolerance for high-impact findings. Demote or repair noisy
rules before making them blocking. Explain the risk and give a concrete
repair or safe suggestion with each diagnostic; an opaque rule ID is insufficient.

### Choose a language baseline

**Required** means deterministic formatting and zero unsuppressed diagnostics
at the chosen blocking severity. **Ratchet** permits reviewed existing debt,
rejects new debt, and requires removal of resolved allowances. **Selective**
means enabling rules with demonstrated value for the maintained code.
These levels can apply to different parts of the same language policy.

| Language or artifact | Formatter | Lint or analysis | Type or compile check | Strictness |
| --- | --- | --- | --- | --- |
| Python | Ruff format | Ruff check with `E4,E7,E9,F,I,B,UP,RUF100`, adjusted for runtime | One of mypy or Pyright with project configuration | Required format/lint; strict new packages; ratchet legacy types |
| TypeScript / TSX | Prettier | ESLint recommended TypeScript/React rules; type-aware rules at project scope | `tsc --noEmit` or build mode for project references | Required `strict`; ratchet additional unchecked-index and optional-property checks |
| JavaScript / Astro / MDX / CSS | Prettier with required parsers/plugins | ESLint JS/React/Astro where applicable; deliberate CSS/prose rules | Astro checker for `.astro`; TypeScript for typed modules; selective `checkJs` | Required configured checks; selective JS typing |
| Kotlin / Gradle Kotlin DSL | ktlint | Detekt standard bug/coroutine rules and selected complexity/domain rules | Kotlin compilation through the build | Required new-code style; ratchet legacy debt; warnings as errors after inventory |
| Java | google-java-format or palantir-java-format | Checkstyle for non-conflicting style rules and selected Error Prone compile-time bug checks | Project compilation; selected compiler warnings with `-Werror` after measuring debt | Required formatter/compiler; selective complementary analysis; ratchet warnings |
| Scala | scalafmt | Selected Scalafix semantic rules | Scala compiler through the supported build | Required formatting/types; selective semantic rules without forced compiler upgrades |
| Rust | rustfmt | Clippy | Clippy includes type/borrow checking; `cargo check` for additional target/feature combinations | Required formatting and selected Clippy warnings as errors; ratchet legacy debt |
| Go | gofmt or configured golangci-lint formatters | `go vet` plus staticcheck, or golangci-lint configured to own both | `go build` for supported packages/targets | Required formatting/vet/build; selective extra rules |
| C / C++ | clang-format | clang-tidy with the real compilation database | Supported compiler/build targets | Required format/build; selective tidy rules and warnings; ratchet legacy debt |
| Swift | Bundled `swift format` on Swift 6+, or pinned standalone swift-format | SwiftLint with overlapping format rules disabled | Swift package or Xcode project build | Required format/build; selected blocking lint; ratchet debt |
| C# / .NET | `dotnet format` | Roslyn analyzers configured in the project and `.editorconfig` | `dotnet build` with reviewed warnings as errors | Required formatting/build; ratchet existing warnings before enforcing the chosen set |
| Ruby | RuboCop layout rules | RuboCop lint and selected style rules | `ruby -c` checks syntax; keep an existing Sorbet/Steep check if adopted | Required selected cops and syntax; Ruby syntax is not static typing |
| Dart / Flutter | `dart format` | `dart analyze --fatal-infos` or `flutter analyze` with explicit `analysis_options.yaml` | Analyzer plus target build where required | Required diagnostics including selected info-level lints; ratchet only with a reviewed mechanism |
| Shell | shfmt | ShellCheck after shell syntax check | `bash -n` for Bash; use the declared shell for other dialects | Required errors/warnings; narrow reasoned suppressions |
| Markdown | Existing formatter optional | markdownlint-cli2; narrow prose and link checks | Not applicable | Required structural rules; selective line length and HTML exceptions |
| JSON / YAML / workflows | Existing formatter | Schema validation; actionlint and authorized offline zizmor for workflows | Real consumer validation where practical | Required syntax/schema; selected security rules |
| SQL | SQLFluff with actual dialect and templater | SQLFluff parse/basic rules; selected style rules | Existing schema/migration validation | Required parse/basic rules; applied migrations stay immutable |
| Terraform | `terraform fmt -check -recursive` | `terraform validate` per maintained module; optional configured TFLint | Validation after explicit dependency preparation | Required native checks; selective provider rules |
| OpenAPI / GraphQL | Existing formatter | Adopted Spectral/Redocly rules; GraphQL schema/document validation | Existing generated-contract and drift checks | Required contract validity and drift checks |
| Protocol Buffers | Adopted formatter or Buf format | Selected Buf lint rules for owned schemas | Existing protoc and generated-binding checks | Required owned contract checks; compatibility only for real consumer promises |

Operational scripts and hooks need deliberate coverage. Set Python's target
version to the oldest supported interpreter. Exclude generated code from
hand-formatting; retain generator validation and drift checks. Do not force
strict typing onto generated JavaScript merely to match maintained sources.

Keep Ruff's indentation rules (`E111`, `E114`, `E117`) disabled when Ruff
format owns layout. Add `E501` only as a deliberate policy: the formatter
cannot wrap every long comment or string. If Prettier and ESLint exceed the
edit budget, evaluate alternatives such as Biome or Oxlint against the
required parser, plugin, and rule coverage before replacing working tools.
A faster executable does not establish equivalent coverage.

#### Separate file feedback from project checks

The examples below assume pinned dependencies are already available. Paths,
project names, build tasks, and executables are synthetic placeholders to
replace with repository-owned selections. A “full gate” cell lists operations
the repository's static command must perform; semicolons separate operations
in prose, not a fail-safe shell implementation. No row is an install recipe.

| Language | Fast per-file feedback | Full gate operations |
| --- | --- | --- |
| Python | `ruff format --check src/sample.py`; `ruff check src/sample.py` | Ruff format/check on maintained roots; configured mypy or Pyright project |
| TypeScript / JavaScript | `prettier --check src/sample.ts`; `eslint --max-warnings 0 src/sample.ts` when warnings block | Prettier and ESLint with the same warning policy on maintained roots; `tsc --noEmit -p tsconfig.json` or configured reference build; `astro check --minimumFailingSeverity warning` when warnings block |
| Kotlin | Pinned `ktlint src/Sample.kt` in check mode | Build-owned ktlint check and Detekt tasks; affected compilation and dependency closure, full required modules in CI |
| Java | `google-java-format --dry-run --set-exit-if-changed src/Sample.java` | Formatter on maintained Java; configured Checkstyle/Error Prone tasks; build-owned compiler with reviewed `-Xlint` and `-Werror` policy |
| Scala | Pinned `scalafmt --test src/Sample.scala` | `sbt scalafmtCheckAll scalafmtSbtCheck`; configured Scalafix check and compile tasks; supported `scalafmtCheckRepo` for scripts outside build roots |
| Rust | `rustfmt --check --edition <project-edition> src/sample.rs`, replacing the placeholder with the configured edition | `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --locked --offline -- -D warnings`; `cargo check` only for additional supported target/feature combinations |
| Go | `gofmt -l sample.go`; wrapper rejects nonempty output | gofmt with nonempty-output rejection, `go vet ./...`, and `staticcheck ./...`; alternatively configured `golangci-lint fmt --diff` and `golangci-lint run`; `go build ./...` |
| C / C++ | `clang-format --dry-run --Werror src/sample.cpp`; `clang-tidy -p build --warnings-as-errors='*' src/sample.cpp` if within budget | clang-format checks on maintained sources/headers; `run-clang-tidy -p build` with configured `WarningsAsErrors` and owned-header coverage; configured build targets |
| Swift | `swift format lint --strict Sources/Sample.swift`; `swiftlint lint --strict Sources/Sample.swift` for the pinned CLI | `swift format lint --strict --recursive Sources Tests`; configured `swiftlint lint --strict`; `swift build` or the required Xcode build |
| C# / .NET | `dotnet format whitespace App.sln --include src/Sample.cs --verify-no-changes --no-restore` if within budget | `dotnet format App.sln --verify-no-changes --no-restore --severity info` when info-level rules block; `dotnet build App.sln --no-restore -warnaserror` with configured Roslyn analyzers and style enforcement |
| Ruby | `bundle exec rubocop --raise-cop-error lib/sample.rb`; `ruby -c lib/sample.rb` | `bundle exec rubocop --raise-cop-error --report-unused-todo-entries`; syntax checks for maintained Ruby; existing project type checker if present |
| Dart | `dart format --output=none --set-exit-if-changed lib/sample.dart` | Same format check on maintained roots; project `dart analyze --fatal-infos` or `flutter analyze` with its default fatal-info policy retained |
| Shell | `bash -n scripts/sample.sh`; `shfmt -d scripts/sample.sh`; `shellcheck -x -S warning scripts/sample.sh` for blocking warnings/errors | Syntax, shfmt and source-aware ShellCheck with the same severity policy on maintained scripts and declared shell dialects |

File formatters need the same configuration as the full gate. A standalone
Rust formatter must use the project edition and configuration; it is not a
substitute for workspace checking. Select supported Cargo feature combinations
and targets explicitly. Do not enable every feature when features conflict.
clang-tidy needs the real include paths, defines, and compiler flags from
`compile_commands.json`; header changes expand to affected translation units.
Set `HeaderFilterRegex` or `--header-filter` to include owned headers. The
warnings-as-errors setting changes severity; it does not enable missing
checks. Bound the worker count for `run-clang-tidy` to the gate's resource budget.

For TypeScript project references, keep the solution's supported build
configuration. Do not append `--noEmit` to `tsc -b` without checking the pinned
compiler's support and reference constraints. Reference consumers may require
dependency declarations. When declaration-only builds are appropriate, set
`emitDeclarationOnly` in project configuration and route declarations and
`.tsbuildinfo` to ignored output directories or run in an isolated snapshot.
TypeScript 5.6+ build mode writes build information even without an explicit
incremental setting. Here, non-mutating checks preserve maintained and staged
source; declared scratch build outputs are allowed and must stay untracked.

On Swift toolchains without bundled `swift format`, use the compatible pinned
`swift-format` executable with `lint --strict --recursive` for directories.
The SwiftLint positional-path example requires version 0.56 or later; check
older CLI syntax before copying it. For .NET, pin `AnalysisLevel`, enable
`<EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>`, and configure selected IDE style diagnostics as
warnings/errors for build enforcement. `dotnet format` defaults to warning
severity; include `--severity info` when those rules belong to the gate.

Use a tested google-java-format launcher, native binary, or build plugin for
the pinned Java Development Kit (JDK). JDK 16+ module encapsulation can require
the documented `--add-exports` options when the launcher does not provide them.
Checkstyle and Error Prone cover different concerns; select complementary
rules without repeating the formatter's layout policy.

`gofmt -l` reports filenames; the wrapper must convert nonempty output into
failure and also preserve tool errors. `go fmt` mutates files, so it is not
the gate's check command. For Go, Swift, .NET, and other tools that can resolve
dependencies implicitly, prepare dependencies separately and enforce offline
execution in hooks. A command that needs missing dependencies defers or fails
explicitly according to its layer.

For golangci-lint v2, use the `version: "2"` configuration schema and keep
`fmt --diff` separate from `run`. If it owns `govet` and `staticcheck`, do not
repeat the standalone checks. Prepare Terraform modules with
`terraform init -backend=false` before `terraform validate` in a secretless
validation environment. Dependency preparation may need network access;
keep it outside edit hooks. Validate each maintained module explicitly.

### Use three enforcement layers

1. **After an edit:** a trusted adapter calls the repository's formatter and
   quick linter for touched files. Return the path, rule, location, and repair
   command. Missing repository opt-in produces one actionable setup notice;
   it never claims that lint passed. Do not guess tools from extensions or
   execute discovered scripts in untrusted directories.
2. **Before a commit:** check formatting and lint against the staged snapshot.
   Run types once per affected project or module and its dependency closure.
   Use the existing Git hook manager. A failure rejects the commit and names
   the repair command. A whole-project check is safer than an unproven scope.
3. **Before delivery:** run one non-mutating static command near the start of
   the aggregate local gate, before expensive tests and automated review.
   CI calls the same definition with its full required scope. Preserve tests,
   security checks, architecture checks, and generation validation.

Project typing requires project context. Passing staged TypeScript filenames
to `tsc` can bypass `tsconfig.json`; use the configured project instead.
Mypy, Kotlin, Scala, Clippy, Roslyn, and compilation checks also need their
import, package, or build context. A file lint result cannot claim those checks.

Harness adapters must verify the installed version's event and feedback
contract. Prove loading, firing, extraction of every touched path, diagnostic
visibility, timeout behaviour, and recursion prevention in isolated fixtures.
A successful shell exit or stdout line does not establish model-visible
feedback. If a harness cannot inject diagnostics after edits, use a documented
supported feedback channel or report that limitation. Do not claim coverage
from a configuration entry alone.

Shell writes and external tools can bypass file-tool events. Git hooks can
also be absent or bypassed. Check the resulting snapshot in the full gate,
and require the CI result before merge.

Deliver actionable findings while the author is editing or reviewing the
change. The Facebook study reports better uptake from diff-time integration
than from batch reporting. Use batch scans for inventories and deeper checks,
then route findings to an owner; do not rely on an unattended dashboard.
For legacy adoption, a reviewed changed-code policy may block new findings
on a pull-request diff while reporting the remaining debt separately.
For example, `golangci-lint run --new-from-rev=<base>` needs an explicit,
available base commit. Avoid its `--new` shortcut in CI, where working-tree
state can affect selection. Such filtering is narrower evidence than a full
ratchet and must not replace it without an explicit adoption decision.

### Budget the fast path

Start with these policy targets, then measure representative cold and warm
runs before setting project timeouts:

| Layer | Initial target | Bounds and fallback |
| --- | --- | --- |
| Edit | Warm p95 below two seconds | One active checker per workspace; bounded pending work and diagnostics; no network, installation, or full build |
| Common scoped commit | Warm completion below 30 seconds | Project-aware checks with prepared dependencies; expand uncertain scope |
| Full gate | Project-owned time and peak-memory budgets | Complete required static scope with bounded workers and explicit resource limits |

Record cold startup separately. Coalesce repeated events without losing the
latest file state. Cap pending paths and fall back to a declared broader check
when the queue limit is reached. Report omitted diagnostic counts and a command
to obtain the complete result. Keep full diagnostics in a bounded artifact.

If a semantic check cannot meet the edit budget, defer it to the staged or
full gate and say so. If compilation exceeds the commit budget, retain it as
a required full-gate check and label the commit result's narrower scope.
A timeout is incomplete evidence. Kill and reap the task-owned checker;
do not leave accumulating background processes. Measure latency and peak
memory as described in [Performance and memory](performance-and-memory.md).

### Format safely

- Use one formatter owner for each file type. Permit only reviewed safe
  formatting fixes after an edit; semantic auto-fixes need separate review.
  Tool safety labels guide selection, but inspect diffs and verify behaviour.
  Ruff's `--fix` excludes unsafe fixes by default; `--unsafe-fixes` expands
  that scope. RuboCop distinguishes `-a` from the broader `-A`. Keep unsafe
  rewrites and `cargo clippy --fix` behind an explicit repair command and
  review. ESLint suggestions also need deliberate selection.
- Keep commit and CI checks non-mutating. Never auto-stage files or re-stage
  whole files after formatting. Preserve partially staged and unstaged work.
- Validate the index snapshot through an isolated snapshot or a tested hook
  manager that preserves unstaged work. Test restoration on failure as well
  as success; checking the working tree alone is insufficient.
- Validate paths against the authorized repository. Handle multi-file patches,
  spaces, renames, deletions, nested packages, and generated/vendor exclusions.
- Prevent formatter-triggered recursion. Before applying delayed formatting,
  compare the current file digest with the event's digest; discard stale work.
  Serialize writes so an older result cannot overwrite a newer edit.
- Keep applied migrations immutable. Validate them without rewriting their
  bytes; apply formatting policy to new migrations before application.
- Isolate bulk formatter adoption in formatting-only commits. Record their
  full commit identifiers in `.git-blame-ignore-revs` and document
  `git config blame.ignoreRevsFile .git-blame-ignore-revs` for contributors.
  This lets Git omit those revisions when tracing line history; it does not
  guarantee perfect authorship reconstruction across arbitrary rewrites.

### Ratchet debt and exceptions

Store reviewed allowances by stable diagnostic fingerprint with occurrence
count, rule, owner, reason, and review date. Prefer native baselines when they
can meet the policy; add a small comparator only when needed. Avoid line-number
identity alone, which changes under unrelated edits.

The gate rejects new fingerprints and increased counts. It also rejects stale
allowances: remove an entry or reduce its count when a defect is fixed. A
comparator that only rejects increases leaves an allowance available for a
later reintroduction. Prove the comparator with add, duplicate, fix, and
reintroduce cases.

Use a narrow rule suppression at the relevant location when possible. Record
its reason and owner. Broad file or directory exclusions need a scope rationale
and a separate validation owner. Never regenerate a baseline just to turn a
failure green. Tool upgrades and intentional rule changes require a reviewed
diagnostic diff; baseline churn must not conceal new debt.

Verify the installed tool's staleness behaviour. Detekt's baseline does not
by itself reject resolved entries; add a comparison against a freshly
generated candidate in scratch space. Fail on drift without replacing the
reviewed baseline. ESLint bulk suppressions fail on unpruned allowances by
default; run `--prune-suppressions` as an explicit repair, never bypass with
`--pass-on-unpruned-suppressions` in the gate. RuboCop's
`--report-unused-todo-entries` rejects unnecessary TODO exclusions without
absorbing new offenses. Exercise these mechanisms with the pinned version.

Remove stale inline suppressions too. Enable Ruff `RUF100`, mypy
`--warn-unused-ignores`, or Pyright `reportUnnecessaryTypeIgnoreComment`.
Configure ESLint unused-disable reporting as an error, for example with
`--report-unused-disable-directives-severity error`. On supported Rust
versions, prefer `#[expect(lint_name, reason = "...")]` for expected
exceptions and deny `unfulfilled_lint_expectations`. Verify the expectation
fails when the underlying violation disappears. A permanent `allow` does
not provide the same staleness assertion.

### Preserve failure contracts

Required checks fail on violations, missing tools, invalid configuration,
unsupported runtimes, crashes, and incomplete execution. Preserve nonzero
statuses through pipelines and aggregate runners. Report “no applicable files”
separately from “configured scope unexpectedly empty.” The latter is a setup
failure when source is expected.

Keep empty-pattern escape flags out of the full gate. ESLint's
`--no-error-on-unmatched-pattern` and `--pass-on-no-patterns` can hide an
incorrect maintained-source root. Scoped wrappers may handle an intentional
empty selection explicitly; record that outcome without claiming a pass
over files that were never checked.

Do not wrap mandatory checks in `|| true`, `|| echo`, optional-script flags,
or unconditional success exits. A reminder to run lint does not reject a
defect. Set an explicit warning policy; if selected warnings block delivery,
configure the tool or wrapper to fail on them. A new warning policy needs a
debt inventory before compiler-wide warnings as errors are enabled.

Verify warning exits against deliberate diagnostics. The command table uses
`--fatal-infos` for Dart, `--max-warnings 0` for blocking ESLint warnings,
`--warnings-as-errors` for selected clang-tidy checks, strict Swift linting,
and Astro's minimum failing severity. RuboCop's `--raise-cop-error` makes
internal cop exceptions fail explicitly. .NET style enforcement needs the
build property and diagnostic severities as well as the build's warning policy.

Prove failure propagation with a deliberate formatting defect, a selected lint
violation, a type/compile defect, a missing executable, and a checker crash.
Run these in isolated synthetic fixtures. Each must produce the expected
nonzero gate status; remove deliberate defects before publication.

### Prove CI parity

Use the same pinned tools, configuration, exclusions, and static-check owner
locally and in CI. CI checks the complete maintained scope required by policy.
Expand local selection when configuration, lockfiles, compiler flags, schemas,
or shared dependencies change. Unknown scope falls back to full static checks.

Record source identity or digest, configuration and lockfile digests, tool
versions, scope, duration, and exit status. Invalidate cached evidence when
any relevant input changes. A scoped fast result must not be reused as proof
of full analysis. Confirm required forge checks actually block merge; a green
optional workflow alone does not establish that policy.

When multiple analyzers feed annotations or debt comparisons, prefer
Static Analysis Results Interchange Format (SARIF) 2.1.0 where supported.
For example, Ruff can emit `--output-format=sarif`. Keep a readable bounded
summary for immediate feedback. Validate report shape and completeness;
preserve rule IDs, locations, and supplied fingerprints. SARIF fields alone
do not guarantee stable identity across tool upgrades or refactors.
Verify any converter before using its output for a ratchet. Bound artifact
size and retention, remove private payloads and paths, and keep upload
permissions separate from read-only analysis. SARIF reporting does not replace
the check's blocking exit status.

Keep pull-request validation read-only and secretless. Linting can load plugins
and build configuration, so repository trust still matters. Follow
[Secure and reliable systems](secure-reliable-systems.md) for dependency and
execution boundaries, and [CI for agentic engineering](../../ci-for-agentic-engineering.md)
for the canonical gate, independent merge evidence, caching, and CI permissions.

### Adoption procedure

1. Inventory maintained languages, existing tool configuration, actual callers,
   hook activation, exclusions, and CI failure propagation. Stop short of
   choosing a tool for a source tree that has not been inspected.
2. Choose one owner per responsibility. Preserve compatible existing choices,
   pin versions, and document runtime and generated-code boundaries.
3. Run the full checks without changing source. Inventory diagnostics and
   measure cold/warm duration and peak memory. Select blocking rules.
4. Fix defects or approve a bounded debt baseline with owner and review date.
   Prove that the baseline shrinks and rejects reintroduced defects.
   Isolate bulk formatting and record blame exclusions. If adopting a
   temporary diff-only policy, document its uninspected debt and exit criteria.
5. Add the repository-owned static command to the existing gate and CI.
   Exercise deliberate failure fixtures and verify required forge checks.
6. Enable staged checks. Prove correct scope and preservation of partial
   staging and unstaged work on success, failure, and interruption.
7. Enable per-edit adapters after native-event fixtures prove activation and
   visible feedback. Measure the budget; defer expensive semantic work clearly.
8. Compare deterministic failures caught before review and later repair commits
   by cause over a representative batch. Record scope and workload differences.
   The goal is fewer avoidable repair rounds; no reduction is promised here.

Completion means the failure fixtures reject defects, clean fixtures pass,
local and CI definitions agree, and hooks meet their stated scope and budgets.
If a tool or feedback channel is unavailable, record the gap and retain the
required full-gate check before claiming adoption complete.

## Checklist

- [ ] Every maintained language has an owner, pinned tools, configuration, and scope.
- [ ] Formatting, linting, typing, architecture checks, and tests have distinct roles.
- [ ] Fast commands and full commands share rules and report their actual scope.
- [ ] Project type/compile checks retain dependency and build context.
- [ ] Edit checks bound latency, memory, output, concurrency, and pending work.
- [ ] Timeouts and deferred checks remain incomplete evidence.
- [ ] Hook installation and model-visible feedback are demonstrated.
- [ ] Staged checks validate the index and preserve unstaged work.
- [ ] Commit and CI checks do not mutate or stage files.
- [ ] Generated/vendor exclusions and immutable migration policy are explicit.
- [ ] Baselines reject new debt and require removal of resolved allowances.
- [ ] Unused inline suppressions fail when their diagnostic disappears.
- [ ] Diagnostics explain the issue and repair; noisy rules have an owner and review target.
- [ ] Tool-specific severity switches and directory recursion cover the declared scope.
- [ ] Bulk formatting commits have blame exclusions and no behavioural edits.
- [ ] Mandatory check failures, setup errors, and crashes propagate nonzero.
- [ ] Full local and required CI checks use the same static definition.
- [ ] Failure fixtures and clean fixtures prove the enforcement path.

## Rules of thumb

Keep one rule owner and several callers. A result proves only the source
snapshot and scope it checked. Fixes should reduce the accepted debt.

### Anti-patterns

| Pattern | Repair |
| --- | --- |
| Tool installed or configured but never called | Trace the caller and prove a deliberate defect fails |
| Reminder presented as enforcement | Return visible diagnostics and reject failing snapshots |
| Lint script with missing configuration | Fail with an actionable setup error |
| Compiler called on filenames without project context | Check the configured project and dependency closure |
| Timeout or missing tool treated as success | Report incomplete evidence or reject at the required layer |
| Baseline refreshed to admit new failures | Review the diagnostic diff and remove resolved allowances |
| Whole-tree formatting and re-staging at commit | Use check-only staged validation and an explicit repair command |
| Fast local lint presented as full CI evidence | Record scope and run the full required definition |

### Related material

- [CI for agentic engineering](../../ci-for-agentic-engineering.md): local
  gate structure and independent merge evidence.
- [Testing in agentic engineering](../../testing-in-agentic-engineering.md):
  behavioural evidence beyond static checks.
- [Domain-driven design](domain-driven-design.md#ports-adapters-and-architecture-tests):
  enforce component boundaries with architecture tests.
- [Performance and memory](performance-and-memory.md): budgets and measurement.
- [Secure and reliable systems](secure-reliable-systems.md): safe dependency
  execution and supply-chain controls.

## Claim review

- [x] Recommendations and timing targets are labelled as policy.
- [x] Tool mechanics link to primary documentation; commands need pinned-version verification.
- [x] No project results, measured speedups, or complete hook integrations are claimed.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private repository identifiers, counts, paths, or source snapshots.
- [x] No trace material.
- [x] No transcript material.
- [x] All examples are synthetic.
