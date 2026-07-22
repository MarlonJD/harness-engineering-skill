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

## Rules

- Remove rows that are genuinely inapplicable or mark them `N/A` with a reason.
- Prefer a narrow deterministic check before an expensive broad suite.
- Record environment assumptions and cleanup for stateful checks.
- Treat flaky, unavailable, or untrusted checks as a harness gap rather than a pass.
