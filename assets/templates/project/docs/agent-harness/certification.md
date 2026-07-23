# Harness Production Certification

This repository claims production-ready harness adoption only when [`certification.json`](certification.json) and the project-native gate pass for the trusted current commit. Installation, scaffolding, documentation presence, or a local-only check is not certification.

## Convergence owner and command

- Owner: <!-- TODO(harness): durable role or team -->
- Project-native gate: <!-- TODO(harness): exact repository command; do not depend on the installed skill path -->
- Safe automatic repair command or procedure: <!-- TODO(harness): bounded convergence path -->
- Escalation boundary: <!-- TODO(harness): production, secret, destructive, external-write, and approval blockers -->

## Continuous invalidation

Run the project-native gate on pull requests, pushes, and a schedule no longer than the manifest's `max_age_hours`. Fail closed when routing, commands, evidence, authority, production behavior, or the [`coverage matrix`](coverage-matrix.md) drifts. Automatic repair may operate only within existing repository and user authority.

## Evidence rules

Store commit-bound v1 JSON evidence records beneath the manifest's `evidence_root`. Link every `verified` and justified `N/A` status cell in the coverage matrix to its matching record. Require current production approval and rollback records; do not reuse local or staging evidence as production proof.

<!-- TODO(harness): Record the repository-native CI job, scheduled maintenance mechanism, certificate consumer, failure notification, and one observed invalidate-and-recover trace. -->
