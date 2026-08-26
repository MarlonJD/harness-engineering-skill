# Agent Capability Registry

List only capabilities that an agent can actually discover or invoke. Keep exact commands in one authoritative location and link to longer runbooks.

| Capability | Entry point or command | Purpose | Expected signal | Owner or update trigger | Status |
| --- | --- | --- | --- | --- | --- |
| Repository setup | <!-- TODO(harness): exact command --> | Prepare a local working environment | <!-- observed signal --> | <!-- role/trigger --> | <!-- verified/candidate/blocked/N/A --> |
| Focused tests | <!-- TODO(harness): exact command --> | Verify a narrow change quickly | <!-- observed signal --> | <!-- role/trigger --> | <!-- status --> |
| Full validation | <!-- TODO(harness): exact command --> | Exercise required repository checks | <!-- observed signal --> | <!-- role/trigger --> | <!-- status --> |
| Project-native harness gate | <!-- TODO(harness): exact repository command; never the installed skill path --> | Fail closed on stale routing, incomplete required coverage, missing runtime checks, or unsafe repository drift | <!-- native command and observable result --> | <!-- role plus manual task-completion trigger; add PR/push/schedule only when explicitly requested --> | <!-- status --> |
| Strict harness attestation (optional; off by default) | <!-- TODO(harness): exact certify command/procedure or N/A --> | Bind the complete 31-row contract to a source/direct-child attestation pair and fresh evidence only when explicitly requested | <!-- `not used` by default; `CERT000` only when enabled --> | <!-- role/escalation trigger --> | <!-- status --> |
| Safe harness convergence | <!-- TODO(harness): repair command/procedure or blocked --> | Repair authorized repository-local drift and rerun the native gate; refresh strict records only when that profile is enabled | <!-- restored native gate and, when applicable, current `CERT000` --> | <!-- role/escalation trigger --> | <!-- status --> |
| Optional production attestation | <!-- TODO(harness): provider-backed verifier command or N/A --> | Add independent production repository, target, approval, rollback, artifact, freshness, and revocation evidence only when explicitly required | <!-- provider-authenticated result, or CERT015 when the requested verifier is unavailable --> | <!-- production authority and trigger --> | <!-- status --> |
| Model/provider/snapshot configuration | <!-- TODO(harness): runtime contract or N/A --> | Make model selection and reasoning settings reproducible | <!-- config and migration baseline --> | <!-- role/trigger --> | <!-- status --> |
| Agent evaluation suite | <!-- TODO(harness): eval command or N/A --> | Compare task success, evidence, latency, tokens, and cost on representative tasks | <!-- run/trace/report ID --> | <!-- role/trigger --> | <!-- status --> |
| Tool/MCP permission contract | <!-- TODO(harness): tool catalog and policy or N/A --> | Bound data scope, side effects, approval, retry, and error behavior | <!-- tool trace and policy result --> | <!-- role/trigger --> | <!-- status --> |
| State, compaction, and resume | <!-- TODO(harness): state/replay command or N/A --> | Preserve IDs, outcomes, blockers, and next goal across long runs | <!-- resume trace --> | <!-- role/trigger --> | <!-- status --> |
| Programmatic or multi-agent routing | <!-- TODO(harness): bounded route or N/A --> | Use PTC only for deterministic bounded processing and multi-agent only for independent branches | <!-- route benchmark and synthesis result --> | <!-- role/trigger --> | <!-- status --> |
| Repository-local tools or skills | <!-- TODO(harness): script, skill, or N/A --> | Reuse project-specific context and workflows | <!-- discovered/invoked result --> | <!-- role/trigger --> | <!-- status --> |
| Source-control, review, or CI context | <!-- TODO(harness): authorized CLI/query path or N/A --> | Gather current work and feedback without copied chat context | <!-- observed status/finding --> | <!-- role/trigger --> | <!-- status --> |
| Dependency or API references | <!-- TODO(harness): checked-in contract, adapter, fixture, reference, or N/A --> | Make important upstream behavior inspectable | <!-- resolved contract/test --> | <!-- role/trigger --> | <!-- status --> |
| Runtime start | <!-- TODO(harness): exact command or N/A --> | Launch an inspectable instance | <!-- URL/process/log signal --> | <!-- role/trigger --> | <!-- status --> |
| Runtime reset | <!-- TODO(harness): exact command or N/A --> | Restore deterministic state | <!-- observed signal --> | <!-- role/trigger --> | <!-- status --> |
| UI or API exercise | <!-- TODO(harness): tool/command or N/A --> | Prove user-visible behavior | <!-- screenshot/response/log --> | <!-- role/trigger --> | <!-- status --> |
| Logs, metrics, or traces | <!-- TODO(harness): query path or N/A --> | Diagnose runtime behavior | <!-- query result --> | <!-- role/trigger --> | <!-- status --> |

## Status meanings

- `verified`: exercised locally with recorded evidence.
- `candidate`: documented but not yet proven in the current environment.
- `blocked`: a named dependency prevents verification.
- `N/A`: intentionally absent with a reason.

`harness-ready` is an optional bounded repository-level attestation result, not a capability-row status and not a claim that the application has been deployed or is universally production-ready. Certification is not used by default; the native project gate is the normal completion proof. The bundled verifier emits `CERT000` only after the complete 31-row strict contract and current evidence pass. Use `--require-production-attestation` only when an independently provisioned provider verifier and the required production authority are explicitly in scope; if that requested verifier is unavailable, report `CERT015`.
