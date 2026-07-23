# Human and Agent Operating Loop

Use this loop to turn human intent into a verified, durable repository change. Keep authority boundaries explicit at every stage.

Run this loop only after an explicit repository-scoped request or an already-authorized repository-native trigger. Installing the external skill does not start the loop, grant authority, or schedule future runs.

## Responsibilities

| Role | Owns |
| --- | --- |
| Human | Priorities, user intent, risk tolerance, product judgment, exceptional approvals, and final acceptance where required |
| Agent | Repository discovery, planning, implementation, local verification, self-review, evidence capture, and durable documentation updates within granted authority; explicit blockers when authority is missing |
| Mechanical harness | Deterministic setup, tests, lint, structural boundaries, schemas, CI feedback, and observable runtime signals |

<!-- TODO(harness): Name repository-specific roles and decisions that always require human judgment. -->

## Task loop

1. Read the applicable instructions and authoritative repository knowledge.
2. Inspect the current tree and working state; preserve unrelated changes.
3. Reproduce the reported behavior or establish a measurable baseline when applicable.
4. Create or resume an ExecPlan when the scope requires continuity.
5. Implement the smallest independently verifiable increment.
6. Run focused checks, then the broader checks required by the verification matrix.
7. Observe user-visible or operational behavior through the environment contract.
8. Review the diff, test coverage, generated artifacts, failure modes, and recovery path.
9. Request additional agent or human review when available and justified; address findings and repeat verification.
10. Update the ExecPlan, architecture, product knowledge, registry, debt, or enforcement rule that changed.
11. Refresh affected HMAC-consistent v2 candidate records and rerun the project-native candidate gate for a new trusted source/direct-child attestation pair, or invalidate the candidate. Keep any requested production-ready outcome blocked by nonzero `CERT015`; local maintenance cannot supply the missing provider verifier.
12. Hand off with literal evidence labels from the output contract.

## Review policy decision

OpenAI's case study used local and cloud agent reviewers in a loop until they were satisfied and made human review optional. Do not inherit that policy implicitly. Record the repository's independent decision:

| Change surface | Local self-review | Independent or cloud review | Stop condition | Human review required? | Failure/escalation path | Owner and evidence |
| --- | --- | --- | --- | --- | --- | --- |
| <!-- TODO(harness): surface or N/A --> | <!-- command/process --> | <!-- reviewer/process or N/A --> | <!-- explicit condition --> | <!-- always/risk-based/optional --> | <!-- action --> | <!-- role plus exercised trace --> |

## Review and recovery loop

| Signal | Immediate response | Durable feedback |
| --- | --- | --- |
| Focused test failure | Diagnose and correct the current increment | Add or improve the reproducing fixture when it exposes a gap |
| CI-only failure | Reproduce the job or isolate the environment difference | Make the command and environment discoverable |
| Repeated review finding | Fix the current change and inspect nearby occurrences | Promote a stable rule into docs, a test, linter, or structural check |
| User-facing defect | Capture a reproducible path and validate the repair | Add acceptance evidence and update product or reliability knowledge |
| Agent cannot proceed | Identify the missing tool, context, signal, or permission | Improve the registry/harness or escalate the judgment boundary |
| Candidate gate or scheduled maintenance failure | Repair only safe explicitly authorized drift, refresh affected candidate records, and keep the candidate failed until every local gate passes; preserve `CERT015` | Add the reproducer, update coverage, and preserve the invalidation/recovery trace |

## Escalation boundaries

<!-- TODO(harness): Define project-specific escalation for destructive changes, migrations, secrets, security findings, external writes, merge, release, deployment, and production operations. -->

Never interpret continuous execution as broader authority. Continue through ordinary milestones, but stop when a required judgment or approval lies outside the granted scope.
