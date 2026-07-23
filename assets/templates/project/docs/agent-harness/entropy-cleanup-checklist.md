# Entropy Cleanup Checklist

Run this sweep at a cadence justified by repository change rate. Keep the process read-only until a finding is verified; use an ExecPlan for broad remediation.

The cadence must be implemented by an explicitly authorized repository-native runner. Installing the external skill does not schedule this sweep or grant repair, pull-request, merge, release, or production authority.

## Documentation and navigation

- [ ] Check local Markdown links and indexes.
- [ ] Compare documented commands with current manifests and CI.
- [ ] Find architecture or product docs that disagree with current behavior.
- [ ] Find abandoned active plans and completed plans with unchecked work.

## Code and architecture

- [ ] Find duplicated helpers, divergent conventions, and bypassed shared boundaries.
- [ ] Check dependency direction and cross-boundary imports against current architecture.
- [ ] Check growing files, modules, generated diffs, suppressions, flags, and ownerless TODOs.
- [ ] Identify a repeated review or incident pattern that should become a test or linter.

## Verification and runtime

- [ ] Exercise registry commands that are marked verified.
- [ ] Check flaky tests, stale fixtures, inaccessible logs, and nondeterministic setup/reset paths.
- [ ] Confirm UI, API, migration, or operational evidence still matches the verification matrix.
- [ ] Check isolation and cleanup for concurrent or long-running agent work.
- [ ] Confirm every completed coverage status links to one fresh HMAC-consistent v2 certification record for the source commit; do not describe the HMAC as external authentication.
- [ ] Confirm an explicitly authorized project-native harness gate runs on its declared pull-request, push, and schedule triggers; exercise one invalidate-and-recover path and restore `CERT000`.
- [ ] Expire harness-ready when its source/attestation commits, repository or evaluation-target identity, coverage digest, record signature, or freshness window no longer matches. When `--require-production-attestation` is in use, also expire it on any approval, rollback, provider, artifact, or revocation mismatch and report `CERT015` if the required provider verifier is unavailable.

## Triage

| Finding | Evidence | Impact | Action | Destination | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| <!-- TODO(harness): observed drift --> | <!-- command/link --> | <!-- concrete consequence --> | <!-- small repair or planned refactor --> | <!-- direct fix/debt/ExecPlan --> | <!-- role --> | <!-- candidate/confirmed/resolved --> |

## Cadence and escalation

<!-- TODO(harness): Define the trigger or cadence, responsible role, report location, and conditions that require human judgment. Do not enable automated writes or merges without explicit authority. -->

## Automation decision

OpenAI's case study scheduled Codex maintenance that updated quality grades and opened targeted repair pull requests. Treat that as an explicit repository policy choice, not a default created by this checklist.

| Runner and cadence | Scan/repair scope | Read or write mode | Pull-request and merge authority | Rollback and escalation | Evidence and status |
| --- | --- | --- | --- | --- | --- |
| <!-- TODO(harness): task/agent or N/A --> | <!-- docs, quality grades, code entropy --> | <!-- report-only/propose/write --> | <!-- explicit boundaries --> | <!-- safe recovery --> | <!-- observed trace plus verified/candidate/blocked/N/A --> |
