# Agent Harness

This directory is the progressive-disclosure entry point for capabilities that help coding agents work reliably in this repository.

Root [`AGENTS.md`](../../AGENTS.md) is the canonical instruction map. If root `AGENTS.override.md` exists, Codex loads that higher-precedence entry point instead, and it must preserve routes to the same authorities before the effective `project_doc_max_bytes` cutoff. Codex defaults that budget to 32 KiB and combines project instructions from root toward the working directory. `config.json` declares downstream authorities but does not make an arbitrary instruction filename auto-loadable or change Codex configuration.

## Capability map

| Need | Source of truth |
| --- | --- |
| Available commands and tools | [`registry.md`](registry.md) |
| Adopted authority paths | [`config.json`](config.json) |
| End-to-end human/agent workflow | [`operating-loop.md`](operating-loop.md) |
| Local isolation and runtime observability | [`environment-contract.md`](environment-contract.md) |
| Required completion evidence | [`output-contract.md`](output-contract.md) |
| Change-to-verification mapping | [`verification-matrix.md`](verification-matrix.md) |
| Recurring drift cleanup | [`entropy-cleanup-checklist.md`](entropy-cleanup-checklist.md) |
| Source-principle coverage | [`coverage-matrix.md`](coverage-matrix.md) |
| Production certification and continuous invalidation | [`certification.md`](certification.md) and [`certification.json`](certification.json) |
| Long-running work | [`../exec-plans/index.md`](../exec-plans/index.md) |

## Route by task

| Task | Read first | Continue with |
| --- | --- | --- |
| Understand the repository | [`../../AGENTS.md`](../../AGENTS.md) | [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) and [`../index.md`](../index.md) |
| Start or resume complex work | [`../PLANS.md`](../PLANS.md) | [`../exec-plans/index.md`](../exec-plans/index.md) and the matching active plan |
| Implement and verify a change | [`operating-loop.md`](operating-loop.md) | [`registry.md`](registry.md), [`verification-matrix.md`](verification-matrix.md), and [`output-contract.md`](output-contract.md) |
| Reproduce UI, API, or runtime behavior | [`environment-contract.md`](environment-contract.md) | The relevant capability in [`registry.md`](registry.md) and row in [`verification-matrix.md`](verification-matrix.md) |
| Change an architecture boundary | [`../../ARCHITECTURE.md`](../../ARCHITECTURE.md) | [`../design-docs/index.md`](../design-docs/index.md) and an ExecPlan when cross-cutting |
| Handle review feedback or a recurring failure | [`output-contract.md`](output-contract.md) | Add context, a test, an enforceable rule, or a debt item according to the evidence |
| Sweep drift and technical debt | [`entropy-cleanup-checklist.md`](entropy-cleanup-checklist.md) | [`../exec-plans/tech-debt-tracker.md`](../exec-plans/tech-debt-tracker.md) or a new active plan |
| Prepare security, reliability, release, or external work | [`output-contract.md`](output-contract.md) | [`../SECURITY.md`](../SECURITY.md), [`../RELIABILITY.md`](../RELIABILITY.md), and applicable approval rules |
| Audit whether the harness is complete | [`coverage-matrix.md`](coverage-matrix.md) | Verify every applicable row with a repository artifact and observed evidence |
| Converge and certify production readiness | [`certification.md`](certification.md) | Resolve every coverage row, run the project-native gate, and validate [`certification.json`](certification.json) for the trusted commit |

## Operating loop

Follow this loop: discover intent, select or create a plan, implement an observable increment, run the mapped verification, review the evidence, update durable knowledge, and clean up drift. Escalate judgment, destructive actions, external writes, releases, and production operations according to repository and user authority.

## Current maturity

| Dimension | State | Evidence | Next useful increment |
| --- | --- | --- | --- |
| Knowledge routing | <!-- TODO(harness): discoverable/repeatable/enforced/self-maintaining --> | <!-- link or observation --> | <!-- bounded improvement --> |
| Planning continuity | <!-- TODO(harness) --> | <!-- evidence --> | <!-- improvement --> |
| Executable verification | <!-- TODO(harness) --> | <!-- evidence --> | <!-- improvement --> |
| Agent-readable runtime | <!-- TODO(harness) --> | <!-- evidence or N/A --> | <!-- improvement --> |
| Mechanical boundaries | <!-- TODO(harness) --> | <!-- evidence --> | <!-- improvement --> |
| Entropy control | <!-- TODO(harness) --> | <!-- evidence --> | <!-- improvement --> |
| Safe autonomy | <!-- TODO(harness) --> | <!-- evidence --> | <!-- improvement --> |

Do not infer maturity from documents alone. Require a repeatable command or observable result for repeatable and higher states.
