# Convergence, Candidate Integrity, and the Production Blocker

Use this contract when the requested outcome is a fully adopted or production-ready harness rather than a bounded audit or scaffold.

## Guarantee boundary

Installing this skill is inert: it does not inspect or modify a repository, run project commands, add CI, schedule maintenance, watch for drift, or certify anything. Start the workflow below only after the user explicitly invokes `$apply-harness-engineering` for the named repository; implicit invocation is disabled. Do not claim that installing a skill changes an uninspected repository.

A future production-ready claim, after the required provider verifier exists, may cover only one source commit and its clean direct-child attestation commit, the declared production environment, and a non-expired evidence window. It would require every canonical capability to be independently resolved, every applicable capability to have fresh observed evidence, every inapplicable capability to have a fresh applicability record, and a project-native mechanism to continuously invalidate stale claims.

The workflow does not create deployment credentials, secrets, production access, human approval, production authority, product intent, or irreversible-action permission. Missing authority is a real `blocked` state and prevents a production-ready result. Do not weaken the candidate gate, invent an artifact, or treat a local self-assertion as external evidence to avoid it.

The bundled verifier has no provider-specific external production-authority integration. Its caller supplies the HMAC key, repository identity, deployment target ID, and evidence files, so a coherent HMAC record proves candidate integrity only. `certify` therefore emits `CERT015` and exits nonzero even when every local structural and integrity check passes. Keep the claim `candidate-only`. Production success requires a future, provider-specific asymmetric verifier with a pre-provisioned trust root that independently verifies repository identity, deployment target, approval, rollback authority, and artifact provenance.

## Explicitly authorized convergence loop

For an explicit, authorized `$apply-harness-engineering` adoption request, continue this loop until every achievable local candidate check is resolved and `CERT015` or another concrete external-authority blocker is reported:

1. Discover the actual stack, authorities, environments, CI provider, runtime surfaces, release path, and production boundary.
2. Create or resume an ExecPlan that inventories all 31 canonical coverage rows and every additional project-specific surface.
3. Run the adaptive audit, select the proportional target, and preserve existing canonical authorities.
4. Implement missing repository-native commands, routing, verification, observability, isolation, recovery, review, and maintenance behavior. Do not stop after copying templates.
5. Exercise each capability through its real project or external boundary. Store one v2 HMAC candidate-integrity record under the configured evidence root and link exactly one record from that coverage row's status cell. Do not treat its locally supplied issuer or key as external authority.
6. Implement a repository-native fail-closed gate in the project's own language or existing tooling. Do not make CI depend on the installed skill path.
7. Wire the native gate to pull requests, pushes, and a bounded schedule. When drift is safe and authorized to repair, rerun this convergence loop; otherwise fail the gate and expose the blocker.
8. Record candidate approval and rollback artifacts without upgrading their authority. Commit the implementation as source commit `S`; then create one direct-child attestation commit `A` containing only the coverage matrix, certification manifest, and every referenced HMAC record. Run the bundled read-only `certify` command against trusted current commit `A`.
9. Re-run project-native tests, the full harness check, the candidate-integrity gate, and a clean-session agent evaluation. Report `blocked`, not `production-ready`, when `CERT015` confirms that the external asymmetric authority verifier is unavailable.

Routine reversible repository edits and tests remain inside an authorized adoption request. External writes, secrets, human approvals, destructive actions, merge, release, deployment, and production operations still require the authority declared by the user and repository. When any such authority is absent, record the blocker and stop the production-ready claim.

## Candidate-integrity record v2

Every linked evidence file is a JSON object with exactly these fields:

```json
{
  "schema_version": 2,
  "repository_commit": "0123456789abcdef0123456789abcdef01234567",
  "repository_identity": "scm://provider.example/immutable-repository-id",
  "deployment_target_id": "deploy://provider.example/immutable-production-target-id",
  "capabilities": ["Exact coverage-row identity"],
  "environment": "ci",
  "command": "project-native exact command or named review procedure",
  "exit_code": 0,
  "observed_at": "2026-07-23T09:30:00Z",
  "result": "passed",
  "artifacts": ["immutable job, trace, approval, screenshot, or repository evidence ID"],
  "issuer": "ci-candidate-observer",
  "key_id": "<lowercase-sha256-of-raw-candidate-key-bytes>",
  "signature": "<lowercase-hmac-sha256>"
}
```

`schema_version` is the exact integer `2`; v1 evidence is invalid. `repository_commit` is source commit `S`, not attestation commit `A`. `repository_identity` and `deployment_target_id` must exactly match the concrete provider-scoped values in the manifest; placeholders such as `default`, `repository`, `production`, `prod`, and `unknown` are invalid. These locally declared identities prevent accidental cross-target reuse but are not provider authentication. `capabilities` is a non-empty list of non-empty strings and must name the exact covered capability. A verified candidate record uses `result: "passed"` and the exact integer `exit_code: 0`. For a justified `N/A`, use `result: "not-applicable"`, `exit_code: null`, a current applicability-review procedure in `command`, and a durable decision artifact. Candidate production approval and rollback records use `environment: "production"`.

The caller supplies an absolute `--attestation-key-file`. The key file must be outside the repository, non-symlinked, regular, single-linked, 32–4096 raw bytes, and inaccessible to group and world. `key_id` is lowercase SHA-256 of those exact raw bytes. These controls prevent simple repository-key substitution and accidental tampering, but the verifier does not pin the key to an external provider identity. A caller can generate another compliant key and matching records, so HMAC validation cannot establish production authority.

Compute `signature` as HMAC-SHA256 over the domain bytes `harness-engineering-evidence-v2\x00` followed by UTF-8 canonical JSON of every evidence field except `signature`. Canonical JSON uses ASCII escaping, sorted keys, no whitespace separators, and rejects non-finite numbers. Store the lowercase hexadecimal digest. The helper checks record consistency but does not authenticate `issuer`, independently dereference artifact IDs, verify a provider event, or prove the truth of an observation. Never present a valid HMAC as human approval, deployment authority, rollback proof, or production certification.

The project-native gate, continuous-maintenance trace, production approval, and rollback evidence use the same schema with these capability identities:

- `project-native-harness-gate`
- `continuous-harness-maintenance`
- `production-authority-approval`
- `production-rollback-readiness`

## Candidate validity and required production blocker

The read-only command is:

```text
python3 <skill-dir>/scripts/harness.py certify --root <repo> --profile <adaptive|standard|full> --commit <trusted-attestation-commit-A> --attestation-key-file <absolute-candidate-key-path>
```

The v2 `candidate-only` manifest's `repository_commit` field is source commit `S`. The caller must obtain `--commit` as attestation commit `A` from a trusted CI or source-control context, not from the manifest. `A` must be the clean current `HEAD` and the direct single-parent child of `S`. The exact `S..A` changed-path set must contain only the configured certification path, configured coverage path, exactly one referenced HMAC-consistent JSON file for each `verified` or justified `N/A` row, and the named gate, maintenance, approval, and rollback candidate files. All other project changes belong in `S`, never in the attestation overlay.

Candidate validation fails on any error or warning and checks:

- the exact 31-row canonical inventory plus any project-specific rows;
- only `verified` or justified `N/A` states, each linked to one fresh HMAC-consistent v2 record bound to `S`, the declared repository identity, and the declared deployment target;
- a locally complete release/deployment/production-authority row whose HMAC record still does not authenticate the declared authority;
- an exact digest of the configured coverage matrix;
- a project-native gate and a maintenance trace;
- pull-request, push, and scheduled triggers;
- a maximum freshness window of seven days;
- candidate records for declared production approval and rollback observations, without treating them as provider-authenticated proof;
- no unresolved structural, routing, link, plan, coverage, or semantic warning.

The template manifest stays `candidate-only`. The current bundled verifier has no code path that can issue `CERT000`; a structurally complete production-ready attempt still receives `CERT015` and a nonzero exit. Do not change the claim or suppress this error. Adaptive validation still requires the complete canonical inventory. Non-Git projects cannot satisfy the source/attestation binding.

Any commit after `A`, source change, evidence change, expired timestamp, missing trigger, failed project-native gate, or changed coverage digest invalidates the candidate. Continuous maintenance can restore candidate integrity by selecting the new source state, refreshing records, and producing a new direct-child attestation commit. It cannot remove `CERT015`, establish external authority, or make a historical claim permanently true.
