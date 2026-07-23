# Harness Candidate Integrity and Production Certification Blocker

The bundled verifier can validate only a `candidate-only` harness. It checks local structure, HMAC record consistency, freshness, and the Git source/attestation boundary, then always emits `CERT015` and exits nonzero because no provider-specific external production-authority verifier is implemented. Installation, scaffolding, documentation presence, an arbitrary caller-selected key, or a local-only assertion is not certification. Keep [`certification.json`](certification.json) at `claim: "candidate-only"`.

## Convergence owner and command

- Owner: <!-- TODO(harness): durable role or team -->
- Project-native gate: <!-- TODO(harness): exact repository command; do not depend on the installed skill path -->
- Authorized safe repair command or procedure: <!-- TODO(harness): bounded repository-native convergence path and trigger -->
- Candidate record issuer: <!-- TODO(harness): local/CI process that observes candidate checks; this field is not externally authenticated -->
- Candidate HMAC key custody: <!-- TODO(harness): secret-store owner and CI policy; never record the key -->
- Required external verifier: provider-specific, pre-provisioned asymmetric repository/deployment/approval/rollback verifier — unavailable in this package
- Escalation boundary: <!-- TODO(harness): production, secret, human-approval, destructive, external-write, and product-judgment blockers -->

Missing project commands, issuer, secret, production access, approval, rollback exercise, or source-control authority is `blocked`. Even when those local candidate fields are present, `CERT015` remains the required blocker. Never replace external authority with a template, default, inferred pass, local self-attestation, fabricated artifact, or self-selected HMAC key.

## Source and attestation commits

Commit all implementation, project commands, CI, and maintenance behavior as source commit `S`. Every HMAC-consistent candidate record and `certification.json.repository_commit` names `S`.

Create direct-child attestation commit `A` only after the candidate checks were observed and recorded. `A` may change exactly the configured coverage matrix, configured certification manifest, one referenced HMAC JSON file for every `verified` or justified `N/A` row, and the named project-gate, maintenance, approval, and rollback candidate files. It must contain no implementation change. The candidate check receives trusted current `A` as `--commit`; `A` must be clean `HEAD` and have `S` as its only parent. Any next commit invalidates the candidate.

## Continuous invalidation

Run the project-native candidate gate on pull requests, pushes, and a schedule no longer than the manifest's `max_age_hours`. Fail closed when routing, commands, records, claimed authority, behavior, or the [`coverage matrix`](coverage-matrix.md) drifts. An explicitly authorized repository-native maintenance trigger may repair only safe drift within existing repository and user authority. It cannot remove `CERT015`.

## Evidence rules

Store exact-schema v2 JSON candidate records beneath the manifest's `evidence_root`. Each record contains `schema_version`, `repository_commit`, `repository_identity`, `deployment_target_id`, `capabilities`, `environment`, `command`, `exit_code`, `observed_at`, `result`, `artifacts`, `issuer`, `key_id`, and `signature` exactly once. `repository_identity` and `deployment_target_id` exactly match the concrete provider-scoped values in the manifest. Link every `verified` and justified `N/A` status cell to one matching record. Candidate approval and rollback records use `environment: "production"`, but the label and HMAC do not make them production proof. V1 records are invalid.

The caller supplies an absolute owner-only candidate HMAC key file outside the repository. It must be a non-symlinked regular file with one hard link, 32–4096 raw bytes, and no group or world permission. `key_id` is lowercase SHA-256 of those raw bytes. `signature` is lowercase HMAC-SHA256 over `harness-engineering-evidence-v2\x00` followed by UTF-8 canonical JSON of every field except `signature`, using sorted keys, ASCII escaping, no whitespace separators, and no non-finite numbers.

For `verified`, require `result: "passed"` and the exact integer `exit_code: 0`. For justified `N/A`, require `result: "not-applicable"` and `exit_code: null`. Record substantive immutable artifact IDs. HMAC validity checks consistency with the caller-supplied key; it does not authenticate `issuer`, validate an artifact URL, prove a provider event, or establish human, deployment, rollback, or production authority.

## External verifier blocker

The current verifier accepts `claim: "candidate-only"` for all structural and integrity checks, then returns only `CERT015` when no other gate fails. It rejects `claim: "production-ready"` with `CERT003` while the provider verifier is unavailable. Do not edit the claim to simulate success.

Removing `CERT015` requires a code change that integrates a provider-specific asymmetric verifier whose trust root is pre-provisioned independently of the repository and invocation. That verifier must independently bind repository identity, deployment target, source/attestation commits, approval authority, rollback authority, artifact provenance, freshness, and revocation. Until that implementation and its tests exist, the literal outcome is `candidate-only` and `blocked`.

<!-- TODO(harness): Record the repository-native CI job, explicitly authorized scheduled maintenance mechanism, candidate-gate consumer, failure notification, and one observed invalidate-and-recover trace. -->
