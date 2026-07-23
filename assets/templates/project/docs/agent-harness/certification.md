# Harness-Ready Certification

The bundled verifier can issue the bounded claim `harness-ready`. It checks the complete 31-row repository contract, local structure, HMAC record consistency, freshness, the project-native gate, and the Git source/attestation boundary. When every required check passes without an error or warning, `certify` emits `CERT000` and exits zero. This result says that the inspected repository harness is current for one source/direct-child attestation pair and one evidence window; it does not say that the application was released, deployed, or independently certified for production. Installation, scaffolding, documentation presence, an arbitrary caller-selected key, or a local-only assertion is not certification. Keep [`certification.json`](certification.json) at `claim: "harness-ready"`.

## Convergence owner and command

- Owner: <!-- TODO(harness): durable role or team -->
- Project-native gate: <!-- TODO(harness): exact repository command; do not depend on the installed skill path -->
- Authorized safe repair command or procedure: <!-- TODO(harness): bounded repository-native convergence path and trigger -->
- Evidence record issuer: <!-- TODO(harness): local/CI process that observes harness checks; this field is not externally authenticated -->
- Evidence HMAC key custody: <!-- TODO(harness): secret-store owner and CI policy; never record the key -->
- Optional production verifier: <!-- TODO(harness): provider-specific asymmetric verifier or explicitly unavailable/N/A -->
- Escalation boundary: <!-- TODO(harness): production, secret, human-approval, destructive, external-write, and product-judgment blockers -->

Missing project commands, current evidence, or source-control authority blocks `harness-ready`. Missing production access, approval, rollback exercise, or provider authority blocks only an explicitly requested `--require-production-attestation` result unless the corresponding canonical capability is otherwise applicable. Never replace external authority with a template, default, inferred pass, local self-attestation, fabricated artifact, or self-selected HMAC key.

## Source and attestation commits

Commit all implementation, project commands, CI, and maintenance behavior as source commit `S`. Every HMAC-consistent evidence record and `certification.json.repository_commit` names `S`.

Create direct-child attestation commit `A` only after the harness checks were observed and recorded. `A` may change exactly the configured coverage matrix, configured certification manifest, one referenced HMAC JSON file for every `verified` or justified `N/A` row, and the named project-gate and maintenance files. When the production-authority row is `verified`, it also includes the named approval and rollback records; when that row is justified `N/A`, all three `production_authority` fields are `null` and no approval or rollback record belongs in the overlay. `A` must contain no implementation change. The certification check receives trusted current `A` as `--commit`; `A` must be clean `HEAD` and have `S` as its only parent. Any next commit invalidates `harness-ready`.

## Continuous invalidation

Run the project-native harness gate on pull requests, pushes, and a schedule no longer than the manifest's `max_age_hours`. Fail closed when routing, commands, records, declared applicability or authority, behavior, or the [`coverage matrix`](coverage-matrix.md) drifts. An explicitly authorized repository-native maintenance trigger may repair only safe drift within existing repository and user authority. A successful recovery produces fresh evidence and a new `CERT000` result; it cannot invent production authority.

## Evidence rules

Store exact-schema v2 JSON evidence records beneath the manifest's `evidence_root`. Each record contains `schema_version`, `repository_commit`, `repository_identity`, `deployment_target_id`, `capabilities`, `environment`, `command`, `exit_code`, `observed_at`, `result`, `artifacts`, `issuer`, `key_id`, and `signature` exactly once. For schema compatibility, `deployment_target_id` names the stable harness evaluation target: the repository, package, service, deployment target, or other concrete subject whose evidence is being evaluated. It is not necessarily a production deployment. `repository_identity` and `deployment_target_id` exactly match the concrete values in the manifest. Link every `verified` and justified `N/A` status cell to one matching record. V1 records are invalid.

The caller supplies an absolute owner-only HMAC key file outside the repository. It must be a non-symlinked regular file with one hard link, 32–4096 raw bytes, and no group or world permission. `key_id` is lowercase SHA-256 of those raw bytes. `signature` is lowercase HMAC-SHA256 over `harness-engineering-evidence-v2\x00` followed by UTF-8 canonical JSON of every field except `signature`, using sorted keys, ASCII escaping, no whitespace separators, and no non-finite numbers.

For `verified`, require `result: "passed"` and the exact integer `exit_code: 0`. For justified `N/A`, require `result: "not-applicable"` and `exit_code: null`. Record substantive immutable artifact IDs. HMAC validity checks consistency with the caller-supplied key; it does not authenticate `issuer`, validate an artifact URL, prove a provider event, or establish human, deployment, rollback, or production authority. That limitation narrows the result to `harness-ready`; it does not prevent ordinary repository-harness certification.

## Production-authority applicability

Ordinary certification may use a fresh justified `N/A` for the exact coverage row `Release, deployment, and production actions require repository-local authority` when the repository has no such action. In that case, keep the exact `production_authority` object in the v2 manifest but set `owner`, `approval_evidence`, and `rollback_evidence` to `null`.

When that row is `verified`, name a substantive durable owner and provide fresh HMAC-consistent approval and rollback observation records. Those local records verify the repository contract but still do not authenticate a production provider. Populate them with `environment: "production"` only when the observations actually occurred in production or the optional stricter profile is requested.

## Optional production attestation

Add `--require-production-attestation` only when independent production evidence is explicitly required. This stricter request requires the manifest environment to be `production`, forbids `N/A` for the production-authority coverage row, and requires provider-authenticated repository and production-target identity, approval, rollback authority, artifact provenance, freshness, and revocation.

The bundled package currently has no provider-specific asymmetric verifier with an independently provisioned trust root. Therefore ordinary valid certification returns `CERT000`, while an explicit `--require-production-attestation` request returns nonzero `CERT015` until such a verifier is configured. The manifest claim remains `harness-ready`; changing it to `production-ready` is rejected with `CERT003` and does not simulate production proof.

<!-- TODO(harness): Record the repository-native CI job, explicitly authorized scheduled maintenance mechanism, harness-gate consumer, failure notification, and one observed invalidate-and-recover trace. -->
