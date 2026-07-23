# Harness Engineering Assessment Rubric

Use this rubric to diagnose capabilities, not to reward file count. Record evidence and the next useful improvement for each dimension.

## Maturity levels

| Level | Meaning |
| --- | --- |
| 0 — Invisible | Knowledge or feedback exists only in people, chats, or undocumented tools. |
| 1 — Discoverable | A repository-local document or command exposes the capability. |
| 2 — Repeatable | An agent can follow a deterministic path and obtain expected evidence. |
| 3 — Enforced | CI, structural tests, schemas, or runtime checks prevent known drift. |
| 4 — Self-maintaining | Scheduled or event-driven loops detect decay, propose repairs, and preserve evidence. |

A future production-ready claim would be stricter than level 4: it would additionally require a trusted source/direct-child attestation commit binding, fresh provider-authenticated evidence per capability, exercised production approval and rollback authority, and a fail-closed project-native gate. The bundled verifier checks only HMAC-consistent candidate records and always returns nonzero `CERT015`; maturity scoring never implies production readiness.

## Dimensions

1. **Orientation and knowledge routing**
   - Check whether a concise `AGENTS.md` points to authoritative, versioned sources.
   - Check that the effective `AGENTS.override.md`/`AGENTS.md` routes occur before the instruction byte cutoff and that relevant root-to-working-directory chains fit the trusted effective `project_doc_max_bytes` configuration.
   - Check whether architecture, product intent, operational constraints, and decisions are discoverable without external conversation history.
   - Check whether repository-local scripts or skills and authorized source-control, review, and CI context are directly invocable and documented.
2. **Planning and continuity**
   - Check whether complex work uses self-contained living ExecPlans with progress, discoveries, decisions, outcomes, commands, and acceptance evidence.
   - Check whether active, completed, and technical-debt states are indexed and unambiguous.
3. **Executable verification**
   - Check for deterministic setup, build, test, lint, type, security, and end-to-end commands.
   - Check whether success is observable as behavior rather than inferred from code changes alone.
4. **Agent-readable runtime**
   - Check whether agents can start an isolated instance, reproduce failures, inspect UI or API state, and query useful logs, metrics, or traces.
   - Score only signals the project actually needs; do not require a browser or telemetry stack for a static library.
5. **Mechanical architecture and quality boundaries**
   - Check whether important dependency directions, schemas, naming rules, file limits, security boundaries, and reliability constraints are executable.
   - Check whether failures explain how to recover.
   - Check whether important upstream behavior is inspectable through stable APIs, adapters, fixtures, or checked-in references rather than hidden assumptions.
6. **Feedback capture and entropy control**
   - Check whether repeated review findings, incidents, flaky tests, stale docs, and duplicated patterns feed back into docs or tooling.
   - Check for a small, recurring cleanup loop and a visible quality or debt register.
7. **Safe autonomy and recovery**
   - Check whether agents can validate their own work, obtain review, handle failures, retry safely, and escalate judgment calls.
   - Keep destructive, production, release, merge, and external-write authority separate from local implementation capability.

## Prioritization rule

Fix the earliest broken feedback loop before adding higher autonomy. Prefer this order:

1. Make intent and commands discoverable.
2. Make verification deterministic.
3. Make runtime behavior observable.
4. Mechanize proven invariants.
5. Capture decisions and recurring failures.
6. Automate maintenance.
7. Expand autonomy within explicit authority.

Treat missing production, real-device, release, or external approval evidence as a scoped gap, not as proof that ordinary local work failed. For any requested production-ready claim, however, every required external authority and production proof is a hard blocker and cannot be replaced by a local assertion, default value, caller-selected HMAC key, or justified `N/A`. The current bundle reports that blocker as `CERT015`.
