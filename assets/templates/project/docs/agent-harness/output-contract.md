# Agent Output Contract

Use this contract for implementation handoffs. More local or risk-specific instructions may add requirements.

## Required outcome

1. Lead with the behavior or artifact delivered.
2. Name the material files or systems changed.
3. Report exact verification commands and scoped outcomes.
4. Separate remaining gaps, deferred debt, and approval-dependent work.
5. State destructive, external, release, production, or real-device work only when it actually occurred with the required authority.

## Evidence labels

| Label | Meaning |
| --- | --- |
| `verified locally` | The stated command or behavior was exercised in the local task environment. |
| `not run` | The check was intentionally not executed; include the reason. |
| `blocked` | A named condition prevented required progress or verification. |
| `candidate-only` | The change or command is plausible but lacks required evidence. |
| `release pending` | Local work is complete, but release or deployment evidence does not exist. |
| `production-ready` | The non-expired commit-bound certification, every coverage row, the project-native gate, production authority, and rollback evidence all pass; do not infer this from installation or local checks. |

## Handoff shape

- Outcome: <!-- TODO(harness): project-specific expectation -->
- Changed: <!-- paths or surfaces -->
- Verification: <!-- exact command and result -->
- Not verified: <!-- omitted or blocked surfaces and reason -->
- Remaining work: <!-- explicit debt, follow-up plan, or none -->

<!-- TODO(harness): Add repository-specific generated-file, migration, security, accessibility, observability, release, or reviewer evidence requirements. -->
