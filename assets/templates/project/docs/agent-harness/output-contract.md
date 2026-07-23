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
| `candidate-only` | The harness change or command is plausible but still lacks evidence required by the bounded repository contract. |
| `harness-ready` | The current source/direct-child attestation pair, complete 31-row coverage, project-native gate, and fresh HMAC-consistent evidence passed with `CERT000`. This does not grant release, deployment, or production authority. |
| `release pending` | Local work is complete, but release or deployment evidence does not exist. |
| `production-ready` | Use only when `--require-production-attestation` was explicitly requested and an independently provisioned provider verifier authenticated repository and production-target identity, source/direct-child attestation commits, every coverage row, the project-native gate, production approval, rollback authority, artifact provenance, freshness, and revocation. Without that requested verifier, report `CERT015`; never infer this label from `harness-ready`, installation, templates, local checks, an arbitrary HMAC key, or self-asserted artifacts. |

## Handoff shape

- Outcome: <!-- TODO(harness): project-specific expectation -->
- Changed: <!-- paths or surfaces -->
- Verification: <!-- exact command and result -->
- Not verified: <!-- omitted or blocked surfaces and reason -->
- Remaining work: <!-- explicit debt, follow-up plan, or none -->

<!-- TODO(harness): Add repository-specific generated-file, migration, security, accessibility, observability, release, or reviewer evidence requirements. -->
