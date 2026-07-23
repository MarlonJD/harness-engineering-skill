# Enforcement and Feedback Loops

Build feedback loops in stages. Prefer a small reliable loop over a broad noisy platform.

## Mechanize stable boundaries

Promote a rule from prose into code when at least one condition holds:

- it protects correctness, security, privacy, reliability, or data integrity;
- agents or people have repeated the same mistake;
- architectural drift compounds downstream work;
- the rule is deterministic enough to produce an actionable failure.

Enforce dependency direction, boundary validation, schema ownership, structured logging, generated-file provenance, or platform reliability only when relevant to the project. Keep implementation choices flexible inside the enforced boundary.

Stage new checks as `documented -> runnable -> report-only -> blocking`. Record baseline noise and remediation before making a check block CI.

## Expose runtime behavior

Choose the cheapest observable proof for each surface:

| Surface | Useful evidence |
| --- | --- |
| Library | Focused tests, examples, type checks, benchmarks |
| CLI | Exit code, stdout/stderr contract, fixture-driven invocation |
| API/service | Health check, request/response transcript, structured logs, traces |
| Web UI | Isolated boot, browser-driven flow, DOM state, screenshot or video, console/network logs |
| Mobile/desktop | Simulator or test device flow, accessibility tree, screenshot/video, application logs |
| Data pipeline | Fixture input, deterministic output, lineage, reconciliation metrics |

Prefer per-task or per-worktree isolation when concurrent agents can collide. Document startup, reset, seed, teardown, port allocation, and log locations.

Do not install OpenAI's example observability stack by default. Reuse the project's telemetry and add only the query paths an agent needs to diagnose and verify relevant behavior.

## Capture human judgment

After a review correction, incident, or user-facing failure, classify the lesson:

- Update a canonical document for durable context or rationale.
- Add a fixture or test for reproducible behavior.
- Add a linter or structural test for a stable invariant.
- Add a runbook or recovery command for operational knowledge.
- Add a debt item when the fix is known but deliberately deferred.

Avoid copying entire review conversations. Preserve the decision, rationale, evidence, and affected boundary.

## Control entropy

Run a lightweight recurring sweep for:

- stale or broken links and indexes;
- docs that disagree with commands or code;
- duplicated helpers or divergent patterns;
- growing files, modules, dependency edges, or flaky tests;
- unchecked completed plans and abandoned active plans;
- expired suppressions, temporary flags, or TODOs without owners;
- verification surfaces whose commands no longer run.

Prefer small targeted repairs. Update the quality score or debt tracker with evidence. Escalate broad refactors into an ExecPlan.

## Expand autonomy safely

Increase agent responsibility only when the previous level is observable and recoverable:

1. Discover context and propose work.
2. Modify code and run focused checks.
3. Reproduce and verify end-to-end behavior.
4. Self-review and respond to review feedback.
5. Handle CI failures and safe retries.
6. Prepare external changes for approval.
7. Merge, release, or operate production only with explicit authority and project-specific gates.

High throughput does not justify weakening a gate when failures are expensive, irreversible, regulated, or difficult to detect.

## Maintain a production-ready claim

For a repository that requests full production certification, implement a project-native gate and run it on pull requests, pushes, and a bounded schedule. Bind evidence and the certificate to the current commit. Expire the claim within seven days or sooner, and immediately invalidate it when a required command, authority, coverage row, evidence record, production signal, or rollback path changes or fails.

Automatic maintenance may repair safe repository-local drift within existing authority. It must fail closed and escalate when repair requires secrets, destructive actions, external writes, merge, release, deployment, production access, or product judgment. Re-certification is proof of recovery; suppressing or extending a failed certificate is not.
