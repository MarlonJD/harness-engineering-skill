# Source Boundaries

Use these sources to distinguish transferable harness principles from repository-specific examples.

## Primary sources

- OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (11 February 2026). Use this as the case study for agent legibility, repository knowledge, mechanical boundaries, feedback loops, and entropy control.
- OpenAI Cookbook, [Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans) (7 October 2025). Use this as the source for ExecPlan content and living-document behavior.
- Current Codex documentation, [AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced), and [Build skills](https://learn.chatgpt.com/docs/build-skills). Use current product docs for Codex loading, scope, and skill behavior.

## Transferable principles

- Keep the automatically loaded instruction entry point concise and route deeper context to versioned repository documents. Codex selects at most one instruction file per directory, composes the chain from project root toward the working directory, and stops at `project_doc_max_bytes` (32 KiB by default); project config layers are trust- and precedence-dependent.
- Make complex work restartable through self-contained, living plans.
- Give agents direct, deterministic ways to run, observe, verify, review, and recover work.
- Expose repository-local tools and authorized source-control, review, and CI context through directly invocable paths rather than manual copy/paste.
- Prefer stable, composable, well-understood technology; make important dependency behavior inspectable through checked-in contracts, adapters, fixtures, or references.
- Encode critical or repeated invariants mechanically with corrective failure messages.
- Convert failures and human judgment into durable docs, tests, tools, or tracked debt.
- Control documentation and code entropy continuously in small increments.
- Expand autonomy only after feedback and recovery loops are observable.

The Cookbook's sample contract also says to commit frequently while executing a plan. Treat that as authority-gated workflow advice, not permission created by the ExecPlan format; current user and repository Git instructions control whether a commit may be made.

## Case-study choices, not universal requirements

- Zero human-authored code and the reported throughput or size metrics.
- Local and cloud agent-review loops that make human review optional.
- A specific layered domain architecture or dependency sequence.
- Chrome DevTools Protocol, Victoria telemetry components, or a particular query language.
- Per-worktree application and observability stacks when another isolation model suffices.
- Reimplementing dependencies locally.
- Scheduled documentation-gardening or quality-scoring agents that open repair pull requests.
- Minimally blocking merge gates, automated merge, and agent-authored release tooling.

Require a repository-specific decision and evidence for each applicable capability. Record an explicit `N/A` or `blocked` reason rather than silently omitting it.

## Source-section traceability

| Harness Engineering section | Skill implementation route |
| --- | --- |
| Starting from an empty repository | Discovery and proportional scaffold workflow in `SKILL.md`; setup and tool evidence in the capability registry |
| Redefining the engineer's role | Human/agent responsibilities and reusable task loop in `operating-loop.md`; continuity through ExecPlans |
| Making the application legible | Isolation, lifecycle, UI/API/CLI, logs, metrics, traces, cleanup, and concurrency in `environment-contract.md` and `verification-matrix.md` |
| Repository knowledge as the record | Concise `AGENTS.md`, configured authorities, repository knowledge contract, indexes, generated/reference provenance, and link checks |
| Agent legibility as a goal | Direct tool/context access plus inspectable dependency and abstraction contracts in `registry.md`, architecture, fixtures, and references |
| Enforcing architecture and taste | Project-specific invariants, structural tests, actionable failures, and staged enforcement in `enforcement-and-feedback.md` |
| Throughput and merge philosophy | Independent case-study decision rows plus risk-appropriate CI and merge gates; release, deployment, and production authority remains a separate repository-local decision |
| What agent-generated and increasing autonomy mean | End-to-end review/recovery loop, literal output evidence, explicit authority, and graduated autonomy levels |
| Entropy and memory cleanup | Recurring gardening checklist, quality/debt evidence, and promotion of repeated failures into durable rules |
| What remains uncertain | Periodic maturity and coverage review; no claim of universal stack, permanent architecture, or unbounded autonomy |
