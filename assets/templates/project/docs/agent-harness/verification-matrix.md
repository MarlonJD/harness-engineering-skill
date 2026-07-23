# Verification Matrix

Map a change category to the minimum reliable proof. Use exact repository commands and observable signals; do not invent passing counts.

| Change surface | Fast check | Broader check | Behavioral evidence | Fallback or blocker | Owner/update trigger |
| --- | --- | --- | --- | --- | --- |
| Documentation only | <!-- TODO(harness): link/lint command --> | <!-- broader docs check or N/A --> | Links and examples resolve | <!-- fallback --> | <!-- role/trigger --> |
| Library or core logic | <!-- TODO(harness): focused test --> | <!-- full suite --> | Fixture/example output | <!-- fallback --> | <!-- role/trigger --> |
| API or service | <!-- TODO(harness): focused test --> | <!-- integration suite --> | Request/response plus useful logs/traces | <!-- fallback --> | <!-- role/trigger --> |
| Web UI | <!-- TODO(harness): component check --> | <!-- browser/e2e check --> | DOM state and screenshot/video | <!-- fallback --> | <!-- role/trigger --> |
| Mobile or desktop | <!-- TODO(harness): unit/UI check --> | <!-- simulator/device suite --> | Accessibility tree and screenshot/video | <!-- fallback --> | <!-- role/trigger --> |
| Data or migration | <!-- TODO(harness): fixture/dry run --> | <!-- reconciliation/rollback check --> | Before/after counts or invariant | <!-- fallback --> | <!-- role/trigger --> |
| CI or build system | <!-- TODO(harness): config validation --> | <!-- representative job --> | Expected job graph/artifact | <!-- fallback --> | <!-- role/trigger --> |
| Security-sensitive boundary | <!-- TODO(harness): focused test/scan --> | <!-- threat-specific validation --> | Reproduction fails after fix | <!-- fallback --> | <!-- role/trigger --> |
| Harness authority, candidate records, CI, release, or production boundary | <!-- TODO(harness): native focused candidate gate --> | <!-- bundled candidate-integrity check plus future provider-verifier check when implemented --> | Trusted source/direct-child attestation commits and HMAC-consistent v2 candidate records; any future production claim additionally needs provider-authenticated repository, target, approval, rollback, artifact, freshness, and revocation evidence | Fail closed with `CERT015`; do not emit or retain a production-ready claim | <!-- durable role plus every relevant change --> |

## Rules

- Remove rows that are genuinely inapplicable or mark them `N/A` with a reason.
- Prefer a narrow deterministic check before an expensive broad suite.
- Record environment assumptions and cleanup for stateful checks.
- Treat flaky, unavailable, or untrusted checks as a harness gap rather than a pass.
- Rebuild and recheck the candidate after every relevant change and on the explicitly authorized bounded schedule; an expired or mismatched candidate is a failure, not historical proof, and a locally valid candidate still ends in nonzero `CERT015`.
