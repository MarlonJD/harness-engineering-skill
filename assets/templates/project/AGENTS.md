# Repository Agent Guide

Use this file as a map. Keep detailed explanations in the linked canonical documents.

## Start here

- Repository documentation map: [`docs/index.md`](docs/index.md)
- Current architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- ExecPlan contract: [`docs/PLANS.md`](docs/PLANS.md)
- Active and completed work: [`docs/exec-plans/index.md`](docs/exec-plans/index.md)
- Agent capabilities and verification: [`docs/agent-harness/index.md`](docs/agent-harness/index.md)

## Repository orientation

<!-- TODO(harness): Name the main packages, services, applications, and generated areas. -->

## Working contract

- Read the most local instruction file before editing a subtree.
- Preserve unrelated user changes and follow existing repository conventions.
- Use an ExecPlan for cross-cutting, risky, long-running, or context-loss-sensitive work.
- Keep active ExecPlans current while implementing; record decisions and observed evidence.
- Validate behavior with the narrowest reliable command first, then run broader required checks.
- Do not perform external writes, releases, deployments, destructive operations, or branch changes without the authority required by repository and user instructions.

## Commands

| Intent | Command | Expected evidence |
| --- | --- | --- |
| Install or bootstrap | <!-- TODO(harness): exact command --> | <!-- TODO(harness): success signal --> |
| Focused test | <!-- TODO(harness): exact command --> | <!-- TODO(harness): success signal --> |
| Full test | <!-- TODO(harness): exact command --> | <!-- TODO(harness): success signal --> |
| Lint or format check | <!-- TODO(harness): exact command --> | <!-- TODO(harness): success signal --> |
| Type or build check | <!-- TODO(harness): exact command or N/A with reason --> | <!-- TODO(harness): success signal --> |

## Definition of done

<!-- TODO(harness): State the repository-specific minimum verification, documentation, generated-artifact, and review requirements. -->

## Durable constraints

<!-- TODO(harness): List only proven constraints and link to the detailed source of truth. -->
