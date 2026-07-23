# Agent Capability Registry

List only capabilities that an agent can actually discover or invoke. Keep exact commands in one authoritative location and link to longer runbooks.

| Capability | Entry point or command | Purpose | Expected signal | Owner or update trigger | Status |
| --- | --- | --- | --- | --- | --- |
| Repository setup | <!-- TODO(harness): exact command --> | Prepare a local working environment | <!-- observed signal --> | <!-- role/trigger --> | <!-- verified/candidate/blocked/N/A --> |
| Focused tests | <!-- TODO(harness): exact command --> | Verify a narrow change quickly | <!-- observed signal --> | <!-- role/trigger --> | <!-- status --> |
| Full validation | <!-- TODO(harness): exact command --> | Exercise required repository checks | <!-- observed signal --> | <!-- role/trigger --> | <!-- status --> |
| Project-native candidate-integrity gate | <!-- TODO(harness): exact repository command; never the installed skill path --> | Fail closed on stale routing, coverage, HMAC-consistent candidate records, source/attestation binding, or missing declared inputs; preserve `CERT015` | <!-- trusted source and direct-child attestation commits plus non-expired candidate result and CERT015 --> | <!-- role plus explicitly authorized PR/push/schedule trigger --> | <!-- status --> |
| Safe harness convergence | <!-- TODO(harness): repair command/procedure or blocked --> | Repair authorized repository-local drift and regenerate candidate records | <!-- restored native candidate gate; production remains blocked by CERT015 --> | <!-- role/escalation trigger --> | <!-- status --> |
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

`production-ready` is not a registry status and is unavailable from the bundled verifier. Keep the manifest `candidate-only` and report nonzero `CERT015`. Only a future independently provisioned provider verifier that validates every required production authority and project-native gate could justify that output label.
