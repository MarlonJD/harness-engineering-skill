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
| Repository harness authority, evidence records, and maintenance | <!-- TODO(harness): native focused certification gate --> | <!-- bundled harness certification check --> | Trusted source/direct-child attestation commits, all 31 coverage rows, and fresh HMAC-consistent v2 records | Fail closed on any harness error or warning; require `CERT000` for harness-ready | <!-- durable role plus every relevant change; CI only when explicitly requested --> |
| Optional production attestation | <!-- TODO(harness): provider verifier or N/A --> | `certify --require-production-attestation` when explicitly required | Provider-authenticated repository, production target, approval, rollback, artifact, freshness, and revocation evidence | Report `CERT015` when the explicitly requested provider verifier is unavailable; do not infer production readiness from harness-ready | <!-- production authority plus every relevant change --> |

## Rules

- Remove rows that are genuinely inapplicable or mark them `N/A` with a reason.
- Prefer a narrow deterministic check before an expensive broad suite.
- Record environment assumptions and cleanup for stateful checks.
- Treat flaky, unavailable, or untrusted checks as a harness gap rather than a pass.
- Rebuild and recheck harness certification before task completion and after every relevant change. Use a bounded schedule only when CI automation was explicitly requested. An expired or mismatched certification is a failure, not historical proof. Ordinary certification must recover to `CERT000`; production-attestation evidence is additionally invalidated when that optional profile is in use.
