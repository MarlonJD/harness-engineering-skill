# Convergence and Production Certification

Use this contract when the requested outcome is a fully adopted or production-ready harness rather than a bounded audit or scaffold.

## Guarantee boundary

Do not claim that installing a skill changes an uninspected repository. Claim production readiness only for one repository commit, the declared production environment, and a non-expired evidence window. The guarantee means that every canonical capability was independently resolved, every applicable capability has fresh observed evidence, every inapplicable capability has a fresh applicability record, and the repository continuously invalidates stale claims.

The guarantee does not create deployment credentials, production authority, product intent, or irreversible-action permission. Missing authority is a real `blocked` state. Do not weaken the certificate to avoid it.

## Automatic convergence loop

For an authorized harness-adoption request, continue this loop until certification passes or a concrete external authority blocks progress:

1. Discover the actual stack, authorities, environments, CI provider, runtime surfaces, release path, and production boundary.
2. Create or resume an ExecPlan that inventories all 31 canonical coverage rows and every additional project-specific surface.
3. Run the adaptive audit, select the proportional target, and preserve existing canonical authorities.
4. Implement missing repository-native commands, routing, verification, observability, isolation, recovery, review, and maintenance behavior. Do not stop after copying templates.
5. Exercise each capability. Store a v1 evidence record under the repository's configured evidence root and link it from that coverage row's status cell.
6. Implement a repository-native fail-closed gate in the project's own language or existing tooling. Do not make CI depend on the installed skill path.
7. Wire the native gate to pull requests, pushes, and a bounded schedule. When drift is safe and authorized to repair, rerun this convergence loop; otherwise fail the gate and expose the blocker.
8. Record exercised production approval and rollback evidence. Then bind `certification.json` to the trusted current commit and run the bundled read-only `certify` command as an independent cross-check.
9. Re-run project-native tests, the full harness check, the certificate gate, and a clean-session agent evaluation before reporting production readiness.

Routine reversible repository edits and tests remain inside an authorized adoption request. External writes, secrets, destructive actions, merge, release, deployment, and production operations still require the authority declared by the user and repository.

## Evidence record v1

Every linked evidence file is a JSON object with exactly these fields:

```json
{
  "schema_version": 1,
  "repository_commit": "0123456789abcdef0123456789abcdef01234567",
  "capabilities": ["Exact coverage-row identity"],
  "environment": "ci",
  "command": "project-native exact command or named review procedure",
  "exit_code": 0,
  "observed_at": "2026-07-23T09:30:00Z",
  "result": "passed",
  "artifacts": ["immutable job, trace, approval, screenshot, or repository evidence ID"]
}
```

For a justified `N/A`, use `result: "not-applicable"`, `exit_code: null`, a current applicability-review procedure in `command`, and a durable decision artifact. The `capabilities` entry must match the coverage-row identity. Verified production authority and rollback evidence must use `environment: "production"`.

The project-native gate, continuous-maintenance trace, production approval, and rollback evidence use the same schema with these capability identities:

- `project-native-harness-gate`
- `continuous-harness-maintenance`
- `production-authority-approval`
- `production-rollback-readiness`

## Certificate validity

The read-only command is:

```text
python3 <skill-dir>/scripts/harness.py certify --root <repo> --profile <adaptive|standard|full> --commit <trusted-current-commit>
```

The caller must obtain `--commit` from a trusted CI or source-control context, not from the manifest being checked. Certification fails on any error or warning and requires:

- the exact 31-row canonical inventory plus any project-specific rows;
- only `verified` or justified `N/A` states, each linked to fresh commit-bound evidence;
- a verified release/deployment/production-authority row;
- an exact digest of the configured coverage matrix;
- a project-native gate and a maintenance trace;
- pull-request, push, and scheduled triggers;
- a maximum freshness window of seven days;
- exercised production approval and rollback evidence;
- no unresolved structural, routing, link, plan, coverage, or semantic warning.

A source change, evidence change, expired timestamp, missing trigger, failed project-native gate, or changed coverage digest invalidates the certificate. Continuous maintenance can restore the claim by producing new evidence; it cannot make a historical certificate permanently true.
