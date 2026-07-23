---
name: apply-harness-engineering
description: Audit, adopt, repair, converge, continuously maintain, or evaluate certification blockers for an explicit OpenAI-style repository harness with concise AGENTS.md routing, versioned knowledge, managed ExecPlans, verification and observability contracts, mechanical guardrails, production evidence, and entropy maintenance. Use for requests that explicitly mention harness engineering, an agent-first or agent-readable repository, repository knowledge maps, docs/agent-harness, production-ready harness adoption, continuous harness maintenance, managed docs/exec-plans lifecycle, or authoring, executing, resuming, migrating, and completing an ExecPlan under that lifecycle. Do not use for ordinary feature work, one-off informal planning, generic CI/testing, generic documentation cleanup, or code review unless the user also asks to establish or use the repository harness.
---

# Apply Harness Engineering

Build the smallest project-specific system that lets an agent discover intent, execute work, observe behavior, prove outcomes, and leave durable knowledge behind. Treat directory creation as scaffolding; treat reliable feedback loops and enforced invariants as the outcome.

## Respect the installation boundary

- Installing this package only makes the skill available to Codex. Installation does not inspect, execute, modify, monitor, schedule work for, or certify any repository.
- Begin repository work only after the user explicitly invokes `$apply-harness-engineering` for a named repository. `agents/openai.yaml` disables implicit invocation, so a natural-language request that does not invoke this skill does not start its workflow. If the request is only to install the skill, stop after installation and report that no adoption occurred.
- Do not treat installation, skill discovery, a scaffold preview, copied templates, or the helper's presence as repository evidence.
- Installing or invoking the skill grants no deployment credential, secret, production access, human approval, product judgment, destructive-action permission, merge authority, or external-write authority. A required capability that depends on missing authority is `blocked`; never fabricate, default, infer, or self-attest that evidence.
- `certify` proves that the documented repository-level harness is complete for one inspected source commit and its clean direct-child attestation commit. It does not claim that the product was deployed. Add the optional `--require-production-attestation` flag only when the user explicitly asks for provider-backed production attestation; without such an integration that stricter check fails closed with `CERT015`.

## Select the operation

- For an assessment, inspect and report gaps without modifying the repository.
- For a bootstrap or repair, audit first, propose the target shape, then make additive project-specific changes.
- For a complex implementation, create or resume an ExecPlan and keep it current while working.
- For plan lifecycle work, resolve the configured ExecPlan index first; create plans in its sibling `active/` directory and move verified plans to its sibling `completed/` directory. The bundled default is `docs/exec-plans/`.
- For sustained hardening, add mechanical checks, agent-readable runtime signals, documentation gardening, and entropy cleanup in risk-appropriate increments.
- For fully adopted harness requests, use the explicitly authorized convergence loop in [certification-and-convergence.md](references/certification-and-convergence.md). Continue through project-specific implementation, evidence capture, the project-native gate, CI wiring, invalidation, and recovery; do not stop at installation or scaffolding.
- For an existing harness-ready claim, validate its trusted source and direct-child attestation commits, v2 evidence-integrity records and freshness, project-native maintenance gate, coverage, and release/rollback contract when applicable. Treat drift or expiry as a failed claim, never historical proof.

## Execute the workflow

1. Discover the repository before designing the harness.
   - Read every applicable `AGENTS.override.md`, `AGENTS.md`, `CLAUDE.md`, `UI_RULES.md`, and repository-local skill completely. At repository root, treat `AGENTS.override.md` as the higher-precedence Codex entry point when present and verify that it preserves routes to the canonical authorities inside Codex's effective instruction byte budget.
   - Codex defaults `project_doc_max_bytes` to 32 KiB and composes project instructions from the root toward the working directory. The static helper checks the effective root entry against the smaller of 32 KiB and a valid repository-declared value; it never trusts a larger value by itself. For larger budgets, nested instruction/config layers, or completeness claims, record runtime evidence of the trusted effective configuration and loaded instruction chain.
   - Inspect the working tree, project manifests, build and test entry points, CI, architecture, existing docs, and generated artifacts.
   - Preserve unrelated work and existing conventions. Do not create or change branches unless explicitly asked.
2. Establish a baseline.
   - Run `python3 <skill-dir>/scripts/harness.py audit --root <repo>` in adaptive mode.
   - Treat missing files as evidence, not as permission to overwrite existing guidance.
   - Read [assessment-rubric.md](references/assessment-rubric.md) to classify capability gaps and maturity.
3. Design a proportional target.
   - Read [source-boundaries.md](references/source-boundaries.md) when explaining the source material or deciding whether an OpenAI case-study choice applies.
   - Read [repository-contract.md](references/repository-contract.md) before creating or reorganizing documentation.
   - Read [exec-plans.md](references/exec-plans.md) before changing `docs/PLANS.md` or an ExecPlan.
   - Read [enforcement-and-feedback.md](references/enforcement-and-feedback.md) before adding CI gates, architecture rules, observability, or recurring cleanup.
   - Reuse and link existing authoritative documents. Avoid duplicate sources of truth.
   - If equivalent authorities already exist, map them in `docs/agent-harness/config.json`, update every router or plan link that still presents a fallback path as canonical, and add only missing capabilities. The config is an authority declaration, not a dynamic Markdown redirect. Its `exec_plan_index` key opts into this skill's strict managed index and plan schema; do not point it at an incompatible existing lifecycle. Do not run a wholesale scaffold that would create competing documents.
4. Decide whether the work itself needs an ExecPlan.
   - Use one for multi-hour work, significant refactors, migrations, cross-cutting changes, risky operations, or work that must survive context loss.
   - Keep small, low-risk changes on a lightweight plan unless local instructions require otherwise.
5. Apply changes incrementally.
   - Preview the bundled scaffold with `python3 <skill-dir>/scripts/harness.py scaffold --root <repo> --profile <standard|full>` only after choosing that profile deliberately.
   - The helper is intentionally read-only. After reviewing the preview, inspect each selected template and add or merge it with the controlled repository editing mechanism; never overwrite or bulk-copy an existing authority.
   - Replace every scaffold placeholder in adopted documentation with facts learned from the repository. The only retained generic fields belong to the reusable ExecPlan template and must be replaced when a plan is instantiated. Remove or mark genuinely inapplicable sections explicitly; never present template text as completed documentation.
   - When `AGENTS.md` already exists, preserve it and merge only a tailored portion of `assets/templates/fragments/AGENTS.harness.md` where routing is missing.
   - Choose the full profile only when all four full-profile authorities apply. Merge and tailor all of `assets/templates/fragments/docs-index.full.md` into the canonical documentation map so each authority is reachable; otherwise use the standard or adaptive profile.
   - Promote repeated mistakes or critical invariants from prose into executable checks with actionable failure messages.
6. Close the feedback loop.
   - Give agents deterministic commands for setup, testing, linting, type checking, security checks, UI verification, and runtime inspection when those capabilities exist.
   - Register repository-local scripts or skills and authorized source-control, review, and CI context entry points so agents can gather evidence directly instead of relying on copied chat context.
   - Prefer stable, composable, inspectable dependencies. Record contracts, adapters, fixtures, or checked-in references for behavior that would otherwise remain opaque to an agent; do not reimplement upstream code without a project-specific tradeoff decision.
   - Make evidence observable: expected outputs, screenshots, logs, metrics, traces, or reproducible user flows.
   - Record discoveries and decisions in the active ExecPlan and durable architectural knowledge in the relevant canonical document.
7. Verify and report literally.
   - Run project-native checks and `python3 <skill-dir>/scripts/harness.py check --root <repo>`. Any adoption-complete claim must add `--warnings-as-errors`: use `--profile <standard|full>` for an adopted canonical profile, or adaptive checking with explicitly mapped authorities for a custom shape. A custom shape also requires its project-native checker and a mapped coverage matrix that retains every bundled capability inventory row; paths may vary, capability coverage may not be silently omitted. Never infer full adoption from an adaptive zero-error discovery report alone.
   - Distinguish `verified locally`, `not run`, `blocked`, `harness-ready`, `release pending`, and an actually observed production deployment.
   - For a harness-ready request, read [certification-and-convergence.md](references/certification-and-convergence.md). Commit the implementation as source commit `S`, create HMAC-consistent v2 evidence records bound to concrete repository and harness-target identities, and create one direct-child attestation commit `A` containing only certification, coverage, and referenced records. Obtain current `A` from trusted source-control or CI context and run `python3 <skill-dir>/scripts/harness.py certify --root <repo> --profile <adaptive|standard|full> --commit <trusted-attestation-commit-A> --attestation-key-file <absolute-evidence-integrity-key-path>`. A zero exit with `CERT000` certifies the repository harness for that bounded snapshot. It does not assert that the product was deployed.
   - Report changed artifacts, verification evidence, remaining gaps, and the next highest-leverage harness improvement.

## Converge within explicit authority

- After an explicit `$apply-harness-engineering` adoption request, treat that request as authority for ordinary reversible repository-local discovery, implementation, testing, evidence capture, and maintenance wiring. Do not infer permission for external writes or privileged operations. Infer stack-specific choices from existing manifests, commands, CI, and architecture; preserve existing authorities and conventions.
- Create or resume an ExecPlan, then iterate `audit -> implement -> exercise -> evidence -> project-native gate -> certify` until `CERT000` confirms the current harness snapshot or a concrete implementation/authority blocker remains.
- Implement the durable checker and CI/scheduled triggers inside the target repository using its native language and tooling. The bundled helper remains an independent read-only bootstrap and cross-check; the target CI must not depend on the skill installation path.
- Repair safe detected drift only when an explicitly authorized repository-native maintenance trigger or current user request permits it. Installation itself creates no trigger. Fail closed and expose the exact blocker when remediation needs a secret, human approval, destructive action, external write, merge, release, deployment, production access, or product judgment.
- Bind every evidence record and the manifest to one trusted source commit plus concrete repository and harness-target identities, bind the check to its direct-child attestation commit and named evidence environment, expire it within seven days, and rerun convergence after relevant changes. Use production-scoped evidence only for capabilities actually exercised there.

## Use the repository contract

Aim for this navigable shape, adapting names only when the repository already has an equivalent source of truth:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── index.md
├── PLANS.md
├── SECURITY.md
├── RELIABILITY.md
├── DESIGN.md (full profile, when applicable)
├── FRONTEND.md (full profile, when applicable)
├── PRODUCT_SENSE.md (full profile, when applicable)
├── QUALITY_SCORE.md (full profile)
├── agent-harness/
│   ├── index.md
│   ├── config.json
│   ├── registry.md
│   ├── operating-loop.md
│   ├── environment-contract.md
│   ├── output-contract.md
│   ├── verification-matrix.md
│   ├── entropy-cleanup-checklist.md
│   ├── coverage-matrix.md
│   ├── certification.md
│   ├── certification.json
│   └── evidence/
├── exec-plans/
│   ├── index.md
│   ├── plan-template.md
│   ├── tech-debt-tracker.md
│   ├── active/
│   └── completed/
├── design-docs/
├── product-specs/
├── generated/
└── references/
```

Keep `AGENTS.md` a concise map: repository orientation, canonical links, commands, constraints, and definition of done. Put explanations and histories in linked documents. Keep every critical route before the effective `project_doc_max_bytes` cutoff, and count the root-to-working-directory instruction chain when local instruction files exist. Apply more local `AGENTS.md` files only when a subtree genuinely needs different instructions.

## Manage ExecPlans

- Resolve `exec_plan_index` from `docs/agent-harness/config.json`; its sibling `active/` and `completed/` directories form the lifecycle. The default template lives at `assets/templates/project/docs/exec-plans/plan-template.md` and the default repository index is `docs/exec-plans/index.md`.
- Create a lowercase-hyphenated plan from the selected repository template, tailor every field, link directly to the configured planning authority, and add exactly one Active index row in the same controlled edit. Run `python3 <skill-dir>/scripts/harness.py validate-plan --root <repo> --slug <slug> --state active` afterward.
- Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` current at every stopping point.
- Make each plan self-contained, outcome-focused, restartable from the file alone, explicit about commands and expected evidence, and safe to retry.
- Before completion, perform the semantic review and persist its exact-content SHA-256 as the single visible indented `Semantic-Review:` continuation in the final `Revision History` entry using [exec-plans.md](references/exec-plans.md). Then run `python3 <skill-dir>/scripts/harness.py validate-plan --root <repo> --slug <slug> --state active --completion --semantic-review`. Only after that read-only gate passes, update lifecycle metadata, move the same plan to `completed/`, and replace its Active row with exactly one Completed row in the same controlled edit. After the move, rerun both `validate-plan --state completed --semantic-review` and the repository check. This unsigned digest detects stale local review text but does not authenticate a reviewer or prove human, external, or production approval.
- Keep unresolved follow-up work in the plan or `tech-debt-tracker.md`; do not hide it by marking the plan complete.

## Bound the adoption

- Do not copy OpenAI's exact stack or merge policy without repository-specific evidence. Treat worktree isolation, browser control, full telemetry stacks, agent review loops, and reduced merge blocking as capability options, not universal defaults.
- Do not add CI gates before the underlying command is deterministic and reasonably fast. Introduce high-noise checks in report-only mode, then enforce after the baseline is clean.
- Do not encode taste as a hard rule after one preference. Mechanize repeated errors, correctness boundaries, security constraints, or proven conventions.
- Do not claim autonomy that the repository cannot verify. Increase autonomy only after reproduction, validation, review, recovery, and escalation paths are observable.
- Keep external chat or document knowledge out of the repository unless authorized to copy it. When authorized, distill decisions and rationale into versioned project documents rather than pasting entire conversations.

## Use bundled resources

- Run the read-only `scripts/harness.py` for deterministic structure, link, routing, ExecPlan, evidence-integrity, and certification checks. Use `audit` for a non-blocking report, `check` for CI-style failure on errors, `--warnings-as-errors` for every adoption-complete gate (canonical or mapped custom), `certify` for the warning-intolerant source/attestation-bound harness gate that returns `CERT000` only when the current repository harness is complete, `scaffold` only as a manifest preview, and `validate-plan` as a structural/relocation completion gate. Add `--require-production-attestation` only for an explicitly requested provider-backed production check. The helper never creates, edits, moves, executes project-defined commands, or deletes repository files; `certify` uses fixed, non-shell, read-only Git queries with explicit parent-side time/output and commit-object limits. Git child parsing still depends on operating-system resource limits, so run adversarial repositories inside an OS-level memory/CPU sandbox.
- Build a release archive only when packaging is requested: `python3 <skill-dir>/scripts/build_release_zip.py --root <skill-dir> --output <path-outside-skill-dir-with-existing-parent>`. The builder packages only regular tracked blobs from a clean Git `HEAD`, requires the tracked skill markers, preserves tracked `100644`/`100755` modes as `0644`/`0755`, uses the fixed `apply-harness-engineering/` prefix, and rejects tracked symlinks, gitlinks, special modes, extra worktree entries (including ignored paths), unsafe or colliding portable names, output inside the worktree or Git metadata directories, and any overwrite. The output parent must already exist. It requires POSIX dirfd/no-follow filesystem primitives and fails closed when they are unavailable. Archive construction validates snapshot integrity, not the skill schema; run the separate metadata and package tests before release. Git child tree parsing is not an OS memory sandbox, so package untrusted repositories only under explicit process memory/CPU limits. Building an archive does not publish or install it.
- Add `--allow-non-git` to non-certification operations only when the user intentionally places a non-Git project in scope; never infer a broad root. The harness `certify` operation requires the Git source/attestation commit boundary.
- Use Python 3.11+ when the target contains `.codex/config.toml`. On older Python, the helper can start but cannot parse that TOML layer and emits fail-closed `CODEXCFG001` findings.
- Treat the bundled script as explicitly invoked assessment, adoption, and maintenance cross-check tooling. Do not make a repository's CI depend on the skill installation path; implement and register a project-native durable checker before claiming mechanical or CI enforcement.
- Apply from `assets/templates/project/` only after the scaffold preview and target inspection. Tailor every selected artifact through the controlled repository editing mechanism.
- Use the configured coverage authority (bundled default: `docs/agent-harness/coverage-matrix.md`) as the inventory gate: every row must be `verified`, `candidate`, `blocked`, or a justified `N/A`. Treat adoption as complete only when every applicable row is `verified`, every inapplicable row has a justified `N/A`, and every completed status links to one fresh HMAC-consistent v2 evidence record; `candidate` and `blocked` remain explicit incomplete states.
- Use [assessment-rubric.md](references/assessment-rubric.md) for sequencing and maturity scoring.
- Use [source-boundaries.md](references/source-boundaries.md) to distinguish transferable principles from case-study-specific technology and policy.
- Use [repository-contract.md](references/repository-contract.md) for artifact ownership and update triggers.
- Use [exec-plans.md](references/exec-plans.md) for official ExecPlan principles and the separate local active/completed lifecycle.
- Use [enforcement-and-feedback.md](references/enforcement-and-feedback.md) for guardrails, observability, entropy control, and staged autonomy.
- Use [certification-and-convergence.md](references/certification-and-convergence.md) for authority-bounded convergence, HMAC evidence-integrity records, continuous invalidation, source/attestation binding, harness-ready certification, and the optional production-attestation profile.
