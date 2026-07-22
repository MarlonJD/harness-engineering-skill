# Execution Plans (ExecPlans)

Use an ExecPlan for work that is cross-cutting, risky, multi-hour, uncertainty-heavy, or likely to cross a context or contributor boundary. A narrow mechanical change may use a lightweight plan unless more local instructions require an ExecPlan.

## How to use an ExecPlan

Read this file completely before authoring or executing a plan. Resolve `exec_plan_index` from `docs/agent-harness/config.json`; its sibling `active/` and `completed/` directories form the lifecycle. The bundled default is `docs/exec-plans/`. Keep the selected index synchronized and move a plan only after the completion gate passes.

Keep the plan self-contained. Assume the next contributor has the current working tree and the plan file but no prior conversation. Continue through ordinary milestones without asking for the next step, while still honoring approval, destructive-action, Git, release, production, and external-write boundaries.

Embed the project knowledge needed to execute the plan instead of outsourcing essential context to unversioned chats or external pages. Link checked-in canonical documents where useful, but repeat the assumptions required to resume safely.

## Requirements

- Explain the user-visible purpose and how to observe success.
- Name repository-relative paths, relevant symbols, working directories, and exact commands.
- Define repository-specific terms in plain language.
- Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` current.
- Use independently verifiable milestones that produce working increments.
- Describe milestones narratively as goal, work, result, and proof; keep granular state tracking separate in `Progress`.
- Use additive prototypes or parallel implementations when they are the safest way to resolve meaningful uncertainty, and define promotion or removal criteria.
- When difficult requirements depend on upstream behavior, inspect available library source or an authoritative checked-in contract, record the evidence, and use independent spikes when several unknowns can be tested separately.
- Include expected outputs, relevant error messages, recovery paths, and concise evidence so a novice can distinguish success from failure.
- Explain why selected dependencies and interfaces are appropriate; name the exact required types, interfaces or traits, function signatures, services, and stable paths when applicable.
- Record a revision note whenever the plan changes.
- Propagate each revision across every affected section before recording what changed and why.

The OpenAI Cookbook sample advises frequent commits while executing a plan. This repository contract does not itself grant Git write authority: create commits or other source-control checkpoints only when current user and repository instructions authorize them. Otherwise, keep the plan and working tree sufficient for restart.

## Formatting

- Keep a standalone plan as ordinary Markdown without an outer code fence.
- Leave one blank line after every heading (two newline characters; CRLF is acceptable).
- Use prose-first narrative. Use checkboxes only in `Progress`.
- Use UTC timestamps in completed progress entries and revision notes.
- Show commands and short transcripts as indented blocks when needed.

## Metadata contract

Every managed plan starts with the `harness-plan:v1` HTML comment block from the template and contains each field exactly once:

| Field | Active plan | Completed plan |
| --- | --- | --- |
| `id` | Lowercase hyphenated slug equal to the filename stem | Unchanged |
| `status` | `active` | `completed` |
| `created` | Valid `YYYY-MM-DD` creation date | Unchanged |
| `updated` | Valid current `YYYY-MM-DD`, not before `created` | Completion date or later |
| `completed` | Empty | Valid `YYYY-MM-DD`, with `created <= completed <= updated` |
| `owner` | Assigned durable role or team | Assigned durable role or team |

At completion, update `status`, `updated`, and `completed` in the same controlled edit that moves the file and replaces its index row. Do not change `id` or `created`.

## Lifecycle

1. Create a lowercase hyphenated plan in the configured index's sibling `active/` directory and add one Active index entry. Preserve the exact registry title, Active/Completed headings, table headers, and lifecycle markers from the selected index so navigation remains mechanically verifiable.
2. Update progress, discoveries, decisions, validation evidence, and revision history at every stopping point.
3. Keep blocked or paused plans in `active/` with an explicit blocker and recovery condition.
4. Before completion, run applicable acceptance checks, resolve placeholders, write the retrospective, and account for remaining work.
5. Record the final semantic review as an indented continuation of the last structured Revision History entry: `Semantic-Review: reviewer=<role-or-team>; reviewed-at=<YYYY-MM-DD HH:MMZ>; evidence=<substantive observed review evidence>`. This is the repository-local durable attestation; it is not a built-in Codex protocol.
6. Run the active completion gate with `--semantic-review`, move the same file to the configured index's sibling `completed/` directory, and update the index in the same change.
7. Validate the completed state again with `--semantic-review` and run the repository-native check. Completed location never substitutes for the explicit assertion or recorded attestation.

## Completion gate

- The behavior promised in `Purpose / Big Picture` is observable.
- Required progress has no unchecked item.
- `Validation and Acceptance` records exact scoped evidence.
- `Outcomes & Retrospective` compares the result with the original purpose and names remaining gaps.
- `Idempotence and Recovery` reflects the final implementation.
- No unresolved marker such as `TODO(harness)`, `TODO:`, `TBD:`, `<replace>`, or bundled template-only prose remains, including inside command or code examples.
- Internal links resolve after the move.
- A semantic reviewer confirms that the plan is self-contained, `owner` identifies a real durable role or team, milestones are meaningful, behavior is observable, and evidence is sufficient; structural validation rejects known placeholders and sentinels but cannot prove natural-language meaning.
- The final Revision History entry persists that review with the exact local `Semantic-Review:` continuation format above, and both active and completed `validate-plan` invocations pass `--semantic-review` explicitly.

## Repository-local strict schema

This repository chooses the following local managed schema. Copy the selected repository plan template and use exactly these H2 headings in order; use H3 or lower for plan-specific subdivisions:

1. Purpose / Big Picture
2. Progress
3. Surprises & Discoveries
4. Decision Log
5. Outcomes & Retrospective
6. Context and Orientation
7. Plan of Work
8. Concrete Steps
9. Validation and Acceptance
10. Idempotence and Recovery
11. Artifacts and Notes
12. Interfaces and Dependencies
13. Revision History

OpenAI's Cookbook presents a customizable ExecPlan pattern and identifies the four living sections above in its sample contract. The exact thirteen-heading schema, metadata, folders, index, owner field, and completion process here are repository-local conventions, not built-in Codex behavior.
