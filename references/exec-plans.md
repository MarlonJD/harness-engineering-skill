# ExecPlan Contract and Lifecycle

Base the plan format on OpenAI's [Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans). Treat that Cookbook article as a customizable pattern, not a built-in Codex protocol. Preserve its principles when adapting an existing repository's declared plan schema.

## Official pattern principles

Make every ExecPlan:

- self-contained and usable by a contributor with no prior conversation context;
- a living document that remains accurate after each update;
- focused on demonstrably working user behavior;
- explicit about repository paths, commands, expected observations, and recovery;
- explicit about expected outputs and relevant failure/error messages so a novice can distinguish success from failure;
- written in plain language with repository-specific terms defined;
- safe to resume from the plan file alone.
- independent of unversioned external context: embed the knowledge needed to execute the plan, while allowing references to relevant checked-in repository documents;
- explicit about narrative milestones as goal/work/result/proof, while using granular checkboxes separately for current progress;
- willing to use additive, independently testable prototypes or parallel implementations when meaningful uncertainty must be reduced.
- prescriptive about selected dependencies and final interfaces: explain why they are chosen and name required types, interfaces/traits, function signatures, services, and stable paths when applicable.
- grounded in direct dependency evidence when difficult requirements turn on upstream behavior: inspect available library source or an authoritative contract, record what was learned, and use isolated spikes when several unknowns can be tested independently.

The Cookbook's supplied `PLANS.md` contract explicitly treats `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` as non-optional living sections. The article also says teams may customize the contract.

## This skill's local strict schema

When a repository chooses this skill's managed lifecycle, maintain these sections in order:

1. `Purpose / Big Picture`
2. `Progress`
3. `Surprises & Discoveries`
4. `Decision Log`
5. `Outcomes & Retrospective`
6. `Context and Orientation`
7. `Plan of Work`
8. `Concrete Steps`
9. `Validation and Acceptance`
10. `Idempotence and Recovery`
11. `Artifacts and Notes`
12. `Interfaces and Dependencies`
13. `Revision History`

The exact thirteen-heading set and order, metadata block, `Revision History` heading, and path conventions below are local schema choices. Do not add other H2 sections; use H3 or lower for plan-specific subdivisions. Adopting or configuring this managed lifecycle is an explicit schema choice. If an incompatible existing schema must remain, do not map it as this skill's `exec_plan_index`; keep its repository-native policy and validator, or intentionally migrate it first. Use timestamped checkboxes only in `Progress`, keep narrative sections prose-first, and include user-visible proof rather than compilation alone.

For the managed schema, use valid ATX Markdown headings and leave one blank line after every heading (two newline characters, with CRLF accepted). A standalone plan file is not wrapped in an outer fence; use indented examples for commands, transcripts, diffs, or code.

The local `harness-plan:v1` metadata contains `id`, `status`, `created`, `updated`, `completed`, and `owner` exactly once. The `id` equals the lowercase-hyphenated filename stem. Active plans use `status: active`, leave `completed` empty, assign an owner, and keep `created <= updated`. Completed plans use `status: completed`, populate `completed`, retain the same `id` and `created`, and keep `created <= completed <= updated`.

The managed lifecycle is valid only when its configured planning authority exists as a regular repository file. Owners must be substantive roles or teams rather than sentinel values such as `none`, `N/A`, `unknown`, or punctuation. Every Active registry row must likewise name a substantive current milestone or blocker.

## Local lifecycle extension

1. Resolve the configured ExecPlan index. Create a lowercase hyphenated filename in its sibling `active/` directory; the bundled default is `docs/exec-plans/active/`.
2. Keep the exact registry title, Active/Completed headings, table headers, and lifecycle markers from the selected index template; add the plan to the Active table with owner, status, and update date.
3. Update the four living sections at every stopping point. Split partially completed progress into explicit done and remaining parts.
4. Record design changes in `Decision Log` at the moment they occur. Record unexpected behavior with concise evidence.
5. Before completion, run every applicable acceptance command and replace placeholders with observed evidence.
6. Move unresolved non-blocking follow-up work into the plan outcome or `tech-debt-tracker.md` with impact and next action.
7. Persist the final semantic review as an indented continuation of the last structured Revision History entry: `Semantic-Review: reviewer=<role-or-team>; reviewed-at=<YYYY-MM-DD HH:MMZ>; evidence=<substantive observed review evidence>`. This is a local durable attestation, not an OpenAI ExecPlan requirement. Run the active completion command with `--semantic-review`; the flag is an explicit current-run assertion and does not replace the recorded attestation.
8. Move the file to the index's sibling `completed/` directory only when all required progress is checked and the retrospective states achieved behavior, remaining gaps, and evidence.
9. Update the index atomically with the move. Keep completed plans immutable except for corrections or supersession notes. Validate the completed state with `--semantic-review` and rerun the repository-native check; the completed directory never asserts review automatically.

When revising a plan, propagate the change through every affected section so the document remains internally consistent, then record what changed and why in `Revision History`. The Cookbook sample advises frequent commits, but that sentence does not grant source-control write authority: create commits or other Git checkpoints only when current user and repository instructions authorize them; otherwise use the living plan and working tree as the restart record.

## Completion checks

- Reject a completion with unchecked progress items.
- Reject a completion with unresolved placeholders such as `TODO` or `<replace>`.
- Reject a completion with an empty `Outcomes & Retrospective` section.
- Ensure every local Markdown link resolves.
- Ensure the plan links to the planning authority declared in `docs/agent-harness/config.json`.
- Ensure every revision records what changed and why.
- Verify that commands and outcomes reflect the current tree, not an earlier milestone.
- Require a semantic review of self-containment, whether `owner` names a real durable role or team, milestone quality, observable behavior, recovery, and evidence; the structural checker rejects known placeholders and sentinel phrases but cannot prove natural-language meaning.
- Require both the explicit `--semantic-review` assertion and the durable `Semantic-Review:` Revision History continuation described above. Reject completed plans that have only one of them.

Do not treat moving a file as proof of completion. Treat the recorded behavior and evidence as proof.
