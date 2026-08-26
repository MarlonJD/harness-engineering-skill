# Package Architecture

This package has four intentionally separate layers:

| Layer | Owns | Boundary |
| --- | --- | --- |
| Skill contract | [`SKILL.md`](SKILL.md) and [`agents/openai.yaml`](agents/openai.yaml) | Defines invocation, authority, adoption, and reporting behavior; it does not mutate target repositories. |
| Target templates | [`assets/templates/project/`](assets/templates/project/) and [`assets/templates/fragments/`](assets/templates/fragments/) | Provides adaptable repository documents. Fragments are merge inputs, not standalone package documentation. |
| Guidance | [`references/`](references/) | Explains source boundaries, plans, assessment, feedback loops, runtime/eval extensions, and the optional, disabled-by-default attestation overlay. |
| Read-only tooling | [`scripts/harness.py`](scripts/harness.py) and [`scripts/build_release_zip.py`](scripts/build_release_zip.py) | Validates or packages a clean snapshot without applying target-project changes. |

The test suite under [`scripts/tests/`](scripts/tests/) exercises parser behavior, structured-input hardening, certification integrity, and release packaging. Target repositories must provide their own native runtime, evaluation, and maintenance gates.
