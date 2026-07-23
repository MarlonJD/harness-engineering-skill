#!/usr/bin/env python3
"""Read-only audit and validation for a repository-local coding-agent harness."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import html
from html.entities import html5 as HTML5_ENTITIES
from html.parser import HTMLParser
import json
import os
import re
import stat
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence
from urllib.parse import unquote


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "templates" / "project"
MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_INDEX_ROWS = 25_000
MAX_COVERAGE_ROWS = 5_000
MAX_MARKDOWN_LINK_NESTING = 64
MARKDOWN_LINK_NESTING_SENTINEL = "\ue103HARNESS_LINK_NESTING_LIMIT\ue104"
CONFIG_REL = "docs/agent-harness/config.json"
CERTIFICATION_REL = "docs/agent-harness/certification.json"
CODEX_PROJECT_CONFIG_REL = ".codex/config.toml"
DEFAULT_PROJECT_DOC_MAX_BYTES = 32 * 1024
MAX_CERTIFICATION_AGE_HOURS = 168
PROJECT_GATE_CAPABILITY = "project-native-harness-gate"
MAINTENANCE_CAPABILITY = "continuous-harness-maintenance"
PRODUCTION_APPROVAL_CAPABILITY = "production-authority-approval"
PRODUCTION_ROLLBACK_CAPABILITY = "production-rollback-readiness"

STANDARD_FILES = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/index.md",
    "docs/PLANS.md",
    "docs/SECURITY.md",
    "docs/RELIABILITY.md",
    "docs/agent-harness/index.md",
    CONFIG_REL,
    "docs/agent-harness/registry.md",
    "docs/agent-harness/operating-loop.md",
    "docs/agent-harness/environment-contract.md",
    "docs/agent-harness/output-contract.md",
    "docs/agent-harness/verification-matrix.md",
    "docs/agent-harness/entropy-cleanup-checklist.md",
    "docs/agent-harness/coverage-matrix.md",
    "docs/agent-harness/certification.md",
    CERTIFICATION_REL,
    "docs/agent-harness/evidence/.gitkeep",
    "docs/exec-plans/index.md",
    "docs/exec-plans/plan-template.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/exec-plans/active/.gitkeep",
    "docs/exec-plans/completed/.gitkeep",
    "docs/design-docs/index.md",
    "docs/design-docs/core-beliefs.md",
    "docs/product-specs/index.md",
    "docs/generated/index.md",
    "docs/references/index.md",
)

FULL_ONLY_FILES = (
    "docs/DESIGN.md",
    "docs/FRONTEND.md",
    "docs/PRODUCT_SENSE.md",
    "docs/QUALITY_SCORE.md",
)

MANAGED_DIRS = (
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
)

DEFAULT_AUTHORITIES = {
    "instructions": "AGENTS.md",
    "architecture": "ARCHITECTURE.md",
    "planning": "docs/PLANS.md",
    "exec_plan_index": "docs/exec-plans/index.md",
    "registry": "docs/agent-harness/registry.md",
    "environment": "docs/agent-harness/environment-contract.md",
    "verification": "docs/agent-harness/verification-matrix.md",
    "coverage": "docs/agent-harness/coverage-matrix.md",
    "certification": CERTIFICATION_REL,
}

ROUTER_CANDIDATES = (
    "AGENTS.md",
    "docs/index.md",
    "docs/agent-harness/index.md",
    "docs/agent-harness/coverage-matrix.md",
    "docs/agent-harness/certification.md",
    "docs/exec-plans/index.md",
    "docs/exec-plans/plan-template.md",
)

HARNESS_INDEX_TARGETS = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/index.md",
    "docs/PLANS.md",
    "docs/SECURITY.md",
    "docs/RELIABILITY.md",
    "docs/agent-harness/config.json",
    "docs/agent-harness/registry.md",
    "docs/agent-harness/operating-loop.md",
    "docs/agent-harness/environment-contract.md",
    "docs/agent-harness/output-contract.md",
    "docs/agent-harness/verification-matrix.md",
    "docs/agent-harness/entropy-cleanup-checklist.md",
    "docs/agent-harness/coverage-matrix.md",
    "docs/agent-harness/certification.md",
    CERTIFICATION_REL,
    "docs/exec-plans/index.md",
    "docs/exec-plans/tech-debt-tracker.md",
)

REQUIRED_PLAN_HEADINGS = (
    "Purpose / Big Picture",
    "Progress",
    "Surprises & Discoveries",
    "Decision Log",
    "Outcomes & Retrospective",
    "Context and Orientation",
    "Plan of Work",
    "Concrete Steps",
    "Validation and Acceptance",
    "Idempotence and Recovery",
    "Artifacts and Notes",
    "Interfaces and Dependencies",
    "Revision History",
)

ACTIVE_START = "<!-- harness:plans:active:start -->"
ACTIVE_END = "<!-- harness:plans:active:end -->"
COMPLETED_START = "<!-- harness:plans:completed:start -->"
COMPLETED_END = "<!-- harness:plans:completed:end -->"
PLAN_SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
H1_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
H2_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")
CHECKBOX_RE = re.compile(
    r"(?m)^([ \t]*)([-*+]|\d{1,9}[.)])([ \t]+)\[([ xX])\]"
    r"(?:[ \t]+(.*?))?[ \t]*$"
)
TIMESTAMP_PREFIX_RE = re.compile(
    r"^\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}Z)\)\s+(.+)$"
)
PLACEHOLDER_RE = re.compile(
    r"^[ \t]*(?:TODO|TBD)[ \t]*$|"
    r"^[ \t]*(?:#{1,6}[ \t]+|[-*+][ \t]+|[A-Za-z][\w -]*:[ \t]*)(?:TODO|TBD)[ \t]*$|"
    r"TODO\(harness\)|\b(?:TODO|TBD)\s*:|"
    r"\b(?:TODO|TBD)\s+(?:replace|fill|describe|add|record)\b|"
    r"<replace|<YYYY|<Short|<role|"
    r"<!--\s*(?:Describe|Explain|Name|Define|State|Keep)",
    re.IGNORECASE | re.MULTILINE,
)
TEMPLATE_PHRASES = (
    "Not completed. Compare the final result",
    "Observation: None yet.",
    "Use the approach described in this initial plan.",
    "Replace with repository-specific reasoning",
    "Establish the first independently verifiable milestone.",
)

UNRESOLVED_MARKER_RE = re.compile(
    r"(?im)^[ \t]*(?:#{1,6}[ \t]+|[-*+][ \t]+|\d{1,9}[.)][ \t]+|"
    r"[A-Za-z][\w -]*:[ \t]*)?\\*(?:TODO|TBD)\b|"
    r"\b(?:remains?|is|still|currently|marked|status(?:\s+is)?)\s+(?:TODO|TBD)\b|"
    r"\b(?:TODO|TBD)\s+(?:for|by|pending|until|replace|fill|describe|add|record|"
    r"implement|finish|complete|verify|decide|resolve|investigate)\b|"
    r"\b(?:TODO|TBD)\b[.!?]?[ \t]*$|"
    r"\b(?:evidence|verification|implementation|follow-up|outcome|owner|reason|status)"
    r"[ \t]*:[ \t]*(?:pending|unknown|none yet|not recorded)\b|"
    r"\b(?:TODO|TBD)\s*:|TODO\(harness\)|<replace|<YYYY|<Short|<role",
)


class SafeRefusal(RuntimeError):
    """Raised when a requested root or managed path is unsafe."""


class ArgumentParseFailure(RuntimeError):
    """Raised instead of printing an unstructured argparse error."""


class HarnessArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ArgumentParseFailure(message)


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    path: str
    message: str
    remediation: str


@dataclass
class Report:
    command: str
    root: str
    findings: list[Finding] = field(default_factory=list)
    actions: list[dict[str, str]] = field(default_factory=list)

    def add(
        self,
        finding_id: str,
        severity: str,
        path: str,
        message: str,
        remediation: str,
    ) -> None:
        self.findings.append(
            Finding(finding_id, severity, path, message, remediation)
        )

    def normalized(self) -> "Report":
        unique: list[Finding] = []
        seen: set[tuple[str, str, str, str, str]] = set()
        for item in self.findings:
            identity = (
                item.id,
                item.severity,
                item.path,
                item.message,
                item.remediation,
            )
            if identity not in seen:
                seen.add(identity)
                unique.append(item)
        self.findings = unique
        order = {"error": 0, "warning": 1, "info": 2}
        self.findings.sort(
            key=lambda item: (order.get(item.severity, 9), item.path, item.id, item.message)
        )
        self.actions.sort(key=lambda item: (item.get("path", ""), item.get("action", "")))
        return self

    def summary(self) -> dict[str, int]:
        return {
            "errors": sum(item.severity == "error" for item in self.findings),
            "warnings": sum(item.severity == "warning" for item in self.findings),
            "info": sum(item.severity == "info" for item in self.findings),
        }

    def payload(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "command": self.command,
            "root": self.root,
            "summary": self.summary(),
            "findings": [asdict(item) for item in self.findings],
            "actions": self.actions,
        }


def files_for_profile(profile: str) -> tuple[str, ...]:
    if profile == "adaptive":
        return ()
    if profile == "standard":
        return STANDARD_FILES
    if profile == "full":
        return STANDARD_FILES + FULL_ONLY_FILES
    raise SafeRefusal(f"Unknown profile: {profile}")


def scaffold_comment_fingerprints(text: str) -> set[str]:
    fingerprints: set[str] = set()
    for match in re.finditer(r"<!--(.*?)-->", text, flags=re.DOTALL):
        body = re.sub(r"\s+", " ", match.group(1).strip()).casefold()
        body = re.sub(r"^todo\(harness\):?\s*", "", body)
        if not body or body.startswith(("harness:plans:", "harness-plan:v1")):
            continue
        fingerprints.add(body)
    return fingerprints


def has_scaffold_placeholder(relative_path: str, text: str) -> bool:
    if relative_path == "docs/exec-plans/plan-template.md":
        return False
    if has_unresolved_marker(mask_inline_code_spans(text)):
        return True
    if re.search(r"<!--\s*TODO\(harness\)\b", text, re.IGNORECASE):
        return True
    if re.search(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]+|[-*+][ \t]+|"
        r"[A-Za-z][\w -]*:[ \t]*)?(?:TODO|TBD)[ \t]*$",
        text,
    ):
        return True
    template = TEMPLATE_ROOT / relative_path
    if not template.is_file():
        return False
    template_comments = scaffold_comment_fingerprints(
        template.read_text(encoding="utf-8")
    )
    return bool(template_comments & scaffold_comment_fingerprints(text))


def configured_authority_keys(root: Path) -> set[str]:
    config_path = safe_target(root, CONFIG_REL)
    if not config_path.is_file():
        return set()
    try:
        payload = json.loads(read_text_safe(root, config_path))
    except (json.JSONDecodeError, OSError, SafeRefusal):
        return set()
    configured = payload.get("authorities") if isinstance(payload, dict) else None
    return set(configured) if isinstance(configured, dict) else set()


def resolve_safe_directory(raw_root: str | Path) -> Path:
    unresolved = Path(raw_root).expanduser()
    if unresolved.exists() and unresolved.is_symlink():
        raise SafeRefusal(f"Repository root may not be a symlink: {unresolved}")
    root = unresolved.resolve()
    if not root.exists() or not root.is_dir():
        raise SafeRefusal(f"Repository root is not a directory: {root}")
    filesystem_root = Path(root.anchor).resolve()
    if root == filesystem_root:
        raise SafeRefusal("Refusing to operate on the filesystem root")
    try:
        home = Path.home().resolve()
    except RuntimeError:
        home = None
    if home is not None and root == home:
        raise SafeRefusal("Refusing to operate on the user home directory")
    return root


def resolve_root(raw_root: str, allow_non_git: bool) -> Path:
    root = resolve_safe_directory(raw_root)
    if not allow_non_git and not (root / ".git").exists():
        raise SafeRefusal(
            f"No .git directory or worktree file at {root}; pass --allow-non-git explicitly"
        )
    return root


def normalize_rel(raw: str) -> PurePosixPath:
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in raw):
        raise SafeRefusal(f"Unsafe managed path contains a control character: {raw!r}")
    rel = PurePosixPath(raw)
    if rel.is_absolute() or not rel.parts or any(
        part in ("", ".", "..") for part in rel.parts
    ):
        raise SafeRefusal(f"Unsafe managed path: {raw}")
    return rel


def safe_target(root: Path, raw_rel: str) -> Path:
    root = root.resolve()
    rel = normalize_rel(raw_rel)
    current = root
    for index, part in enumerate(rel.parts):
        current = current / part
        if current.is_symlink():
            raise SafeRefusal(f"Managed path contains a symlink: {current}")
        if current.exists() and index < len(rel.parts) - 1 and not current.is_dir():
            raise SafeRefusal(f"Managed path ancestor is not a directory: {current}")
    target = root.joinpath(*rel.parts)
    try:
        resolved_parent = target.parent.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise SafeRefusal(f"Managed path cannot be resolved safely: {raw_rel!r}") from exc
    try:
        common = Path(os.path.commonpath((str(root), str(resolved_parent))))
    except ValueError as exc:
        raise SafeRefusal(f"Managed path escapes repository: {raw_rel}") from exc
    if common != root:
        raise SafeRefusal(f"Managed path escapes repository: {raw_rel}")
    return target


def read_bytes_safe(root: Path, path: Path) -> bytes:
    """Read one regular repository file through no-follow directory descriptors."""
    root = root.resolve()
    path = path if path.is_absolute() else root / path
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise SafeRefusal(f"Refusing to read outside repository: {path}") from exc
    if not relative.parts or any(part in ("", ".", "..") for part in relative.parts):
        raise SafeRefusal(f"Unsafe repository read path: {path}")

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    supports_openat = os.open in getattr(os, "supports_dir_fd", set()) and directory_flag
    directory_fd: int | None = None
    file_fd: int | None = None
    try:
        if supports_openat:
            directory_fd = os.open(root, os.O_RDONLY | directory_flag | nofollow | cloexec)
            for part in relative.parts[:-1]:
                next_fd = os.open(
                    part,
                    os.O_RDONLY | directory_flag | nofollow | cloexec,
                    dir_fd=directory_fd,
                )
                os.close(directory_fd)
                directory_fd = next_fd
            file_fd = os.open(
                relative.parts[-1],
                os.O_RDONLY | nofollow | cloexec | nonblock,
                dir_fd=directory_fd,
            )
        else:
            if path.is_symlink():
                raise SafeRefusal(f"Refusing to read symlink: {path}")
            file_fd = os.open(path, os.O_RDONLY | nofollow | cloexec | nonblock)

        file_stat = os.fstat(file_fd)
        if not stat.S_ISREG(file_stat.st_mode):
            raise SafeRefusal(f"Managed text path is not a regular file: {path}")
        if file_stat.st_size > MAX_TEXT_BYTES:
            raise SafeRefusal(f"Managed text file exceeds {MAX_TEXT_BYTES} bytes: {path}")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(file_fd, min(65536, MAX_TEXT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_TEXT_BYTES:
                raise SafeRefusal(f"Managed text file exceeds {MAX_TEXT_BYTES} bytes: {path}")
        return b"".join(chunks)
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)


def read_text_safe(root: Path, path: Path) -> str:
    data = read_bytes_safe(root, path)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SafeRefusal(f"Managed file is not valid UTF-8: {path}") from exc


def is_markdown_blank_line(value: str) -> bool:
    """Match CommonMark blank lines: ASCII spaces/tabs plus an optional line ending."""
    return re.fullmatch(r"[ \t]*(?:\r\n|\n|\r)?", value) is not None


def has_markdown_content(value: str) -> bool:
    return re.search(r"[^ \t\r\n]", value) is not None


def markdown_source_lines(value: str, *, keepends: bool = False) -> list[str]:
    """Split only on CommonMark line endings, not Unicode line separators."""
    if not value:
        return []
    lines = re.split(r"(?<=\n)|(?<=\r)(?!\n)", value)
    if lines and not lines[-1]:
        lines.pop()
    if keepends:
        return lines
    return [re.sub(r"(?:\r\n|\n|\r)$", "", line) for line in lines]


def effective_instruction_path(
    root: Path, fallback_filenames: Sequence[str] = ()
) -> Path:
    candidates = ("AGENTS.override.md", "AGENTS.md", *fallback_filenames)
    for relative in candidates:
        candidate = safe_target(root, relative)
        if not candidate.is_file():
            continue
        try:
            if has_markdown_content(read_text_safe(root, candidate)):
                return candidate
        except (OSError, SafeRefusal):
            return candidate
    return safe_target(root, "AGENTS.md")


def project_instruction_fallbacks(root: Path, report: Report) -> tuple[str, ...]:
    """Read repository-local Codex fallback filenames conservatively."""
    try:
        config_path = safe_target(root, CODEX_PROJECT_CONFIG_REL)
    except SafeRefusal as exc:
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            f"Codex project config path is unsafe: {exc}",
            "Use a regular repository-local .codex/config.toml file.",
        )
        return ()
    if not config_path.exists():
        return ()
    if not config_path.is_file() or config_path.is_symlink():
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            "Codex project config is not a regular file.",
            "Replace it with a regular repository-local UTF-8 TOML file.",
        )
        return ()
    try:
        payload = tomllib.loads(read_text_safe(root, config_path))
    except (OSError, SafeRefusal, tomllib.TOMLDecodeError) as exc:
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            f"Codex project config could not be read safely: {exc}",
            "Repair the UTF-8 TOML file before relying on project instruction settings.",
        )
        return ()
    value = payload.get("project_doc_fallback_filenames")
    if value is None:
        return ()
    if not isinstance(value, list):
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            "project_doc_fallback_filenames must be a non-empty array of safe filenames.",
            "Use repository-root filenames without parent traversal or control characters.",
        )
        return ()
    if not value:
        return ()
    fallbacks: list[str] = []
    for item in value:
        try:
            rel = normalize_rel(item) if isinstance(item, str) else None
        except SafeRefusal:
            rel = None
        if rel is None or len(rel.parts) != 1:
            report.add(
                "CODEXCFG001",
                "error",
                CODEX_PROJECT_CONFIG_REL,
                "project_doc_fallback_filenames contains an unsafe or non-filename value.",
                "Use plain repository-root filenames in Codex discovery order.",
            )
            return ()
        fallbacks.append(rel.as_posix())
    report.add(
        "CODEXCFG003",
        "info",
        CODEX_PROJECT_CONFIG_REL,
        "Configured project instruction fallbacks are included in static root discovery.",
        "Confirm at runtime that the repository is trusted and no higher-precedence CLI, user, profile, or system config changes the effective chain.",
    )
    return tuple(fallbacks)


def project_instruction_budget(root: Path, report: Report) -> int:
    """Return a conservative repository-local AGENTS byte budget."""
    budget = DEFAULT_PROJECT_DOC_MAX_BYTES
    try:
        config_path = safe_target(root, CODEX_PROJECT_CONFIG_REL)
    except SafeRefusal as exc:
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            f"Codex project config path is unsafe: {exc}",
            "Use a regular repository-local .codex/config.toml file.",
        )
        return budget
    if config_path.is_symlink():
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            "Codex project config is a symlink.",
            "Replace it with a regular repository-local TOML file.",
        )
        return budget
    if not config_path.exists():
        return budget
    if not config_path.is_file():
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            "Codex project config is not a regular file.",
            "Replace it with a regular UTF-8 TOML file.",
        )
        return budget
    try:
        payload = tomllib.loads(read_text_safe(root, config_path))
    except (OSError, SafeRefusal, tomllib.TOMLDecodeError) as exc:
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            f"Codex project config could not be read safely: {exc}",
            "Repair the UTF-8 TOML file before relying on project instruction settings.",
        )
        return budget
    value = payload.get("project_doc_max_bytes")
    if value is None:
        return budget
    if type(value) is not int or value <= 0:
        report.add(
            "CODEXCFG001",
            "error",
            CODEX_PROJECT_CONFIG_REL,
            "project_doc_max_bytes must be a positive integer.",
            "Use a positive byte count or remove the setting to use Codex's 32 KiB default.",
        )
        return budget
    if value > budget:
        report.add(
            "CODEXCFG002",
            "info",
            CODEX_PROJECT_CONFIG_REL,
            f"The repository declares a {value}-byte instruction budget; static validation remains conservative at {budget} bytes.",
            "Verify trust, user/profile layers, CLI overrides, and the effective root-to-working-directory instruction chain at runtime before relying on the larger value.",
        )
        return budget
    return value


def read_instruction_prefix(root: Path, path: Path, budget: int) -> tuple[str, int]:
    """Read valid UTF-8 instructions and return only the statically trusted prefix."""
    data = read_bytes_safe(root, path)
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SafeRefusal(f"Managed file is not valid UTF-8: {path}") from exc
    prefix = data[:budget]
    return prefix.decode("utf-8", errors="ignore"), len(data)


def relative_display(root: Path, path: Path) -> str:
    root = root.resolve()
    path = path.resolve(strict=False)
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def validate_iso_date(value: str) -> date | None:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def load_authorities(root: Path, report: Report) -> dict[str, str]:
    authorities = dict(DEFAULT_AUTHORITIES)
    config_path = safe_target(root, CONFIG_REL)
    if not config_path.exists():
        return authorities
    if not config_path.is_file():
        report.add(
            "CONFIG001",
            "error",
            CONFIG_REL,
            "Harness config is not a regular file.",
            "Replace it with a UTF-8 JSON file or remove the mapping.",
        )
        return authorities
    try:
        payload = json.loads(read_text_safe(root, config_path))
    except (json.JSONDecodeError, OSError, SafeRefusal) as exc:
        report.add(
            "CONFIG001",
            "error",
            CONFIG_REL,
            f"Harness config could not be parsed: {exc}",
            "Use an object with schema_version 1 and string authority paths.",
        )
        return authorities
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        report.add(
            "CONFIG001",
            "error",
            CONFIG_REL,
            "Harness config must be an object with schema_version 1.",
            "Correct the schema before relying on configured authorities.",
        )
        return authorities
    configured = payload.get("authorities")
    if not isinstance(configured, dict):
        report.add(
            "CONFIG001",
            "error",
            CONFIG_REL,
            "Harness config authorities must be an object.",
            "Map authority names to repository-relative paths.",
        )
        return authorities
    for key, value in configured.items():
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            report.add(
                "CONFIG002",
                "error",
                CONFIG_REL,
                "Every authority key and path must be a non-empty string.",
                "Remove invalid entries or provide a safe repository-relative path.",
            )
            continue
        if key not in DEFAULT_AUTHORITIES:
            report.add(
                "CONFIG004",
                "error",
                CONFIG_REL,
                f"Unknown authority key {key!r}.",
                f"Use one of: {', '.join(sorted(DEFAULT_AUTHORITIES))}.",
            )
            continue
        if key == "instructions" and value != "AGENTS.md":
            report.add(
                "CONFIG005",
                "error",
                CONFIG_REL,
                "The canonical instructions authority must remain root AGENTS.md.",
                "Keep AGENTS.md as the concise map; when AGENTS.override.md exists, route the same authorities from that higher-precedence entry point.",
            )
            continue
        try:
            safe_target(root, value)
        except SafeRefusal as exc:
            report.add(
                "CONFIG002",
                "error",
                CONFIG_REL,
                f"Configured authority {key!r} is unsafe: {exc}",
                "Use a normalized repository-relative path without symlinks or parent traversal.",
            )
            continue
        authorities[key] = value
    for key, rel in authorities.items():
        try:
            target = safe_target(root, rel)
        except SafeRefusal:
            continue
        valid_target = target.is_file() or (key == "architecture" and target.is_dir())
        if key in configured and configured.get(key) == rel and not valid_target:
            report.add(
                "CONFIG003",
                "error",
                CONFIG_REL,
                f"Configured authority {key!r} does not resolve to a regular file.",
                f"Create or correct {rel} before treating it as canonical.",
            )
    return authorities


def markdown_link_title_is_valid(raw: str) -> bool:
    if re.search(r"\r?\n[ \t]*\r?\n", raw):
        return False
    value = raw.strip(" \t\r\n")
    if not value or value[0] not in {"\"", "'", "("}:
        return False
    closer = ")" if value[0] == "(" else value[0]
    cursor = 1
    while cursor < len(value):
        if value[cursor] == "\\":
            cursor += 2
            continue
        if value[cursor] == closer:
            return not value[cursor + 1 :].strip(" \t\r\n")
        cursor += 1
    return False


def normalized_link_destination(raw: str) -> str | None:
    """Parse one CommonMark inline/reference destination and optional title."""
    if re.search(r"\r?\n[ \t]*\r?\n", raw):
        return None
    value = raw
    leading = re.match(r"\A[ \t]*(?:\r?\n[ \t]*)?", value)
    trailing = re.search(r"(?:[ \t]*\r?\n)?[ \t]*\Z", value)
    assert leading is not None and trailing is not None
    if leading.end() > trailing.start():
        return ""
    value = value[leading.end() : trailing.start()]
    if not value:
        return ""
    remainder = ""
    if value.startswith("<"):
        cursor = 1
        while cursor < len(value):
            character = value[cursor]
            if character in "\r\n" or (character == "<" and not is_escaped(value, cursor)):
                return None
            if character == ">" and not is_escaped(value, cursor):
                break
            cursor += 1
        if cursor >= len(value):
            return None
        destination = value[1:cursor]
        remainder = value[cursor + 1 :]
        if remainder and remainder[0] not in " \t\r\n":
            return None
    else:
        cursor = 0
        parenthesis_depth = 0
        while cursor < len(value) and value[cursor] not in " \t\r\n":
            if ord(value[cursor]) < 0x20 or ord(value[cursor]) == 0x7F:
                return None
            if value[cursor] == "\\":
                cursor += 2
                continue
            if value[cursor] == "(":
                parenthesis_depth += 1
                if parenthesis_depth > 32:
                    return None
            elif value[cursor] == ")":
                if parenthesis_depth == 0:
                    return None
                parenthesis_depth -= 1
            cursor += 1
        if parenthesis_depth:
            return None
        destination = value[:cursor]
        remainder = value[cursor:]
    if remainder.strip(" \t\r\n") and not markdown_link_title_is_valid(remainder):
        return None
    return destination


MARKDOWN_ESCAPABLE = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def markdown_unescape(value: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        if (
            value[index] == "\\"
            and index + 1 < len(value)
            and value[index + 1] in MARKDOWN_ESCAPABLE
        ):
            output.append(value[index + 1])
            index += 2
            continue
        output.append(value[index])
        index += 1
    return "".join(output)


def commonmark_unescape_entities(value: str) -> str:
    entity_re = re.compile(
        r"&(?:#[xX][0-9A-Fa-f]{1,6}|#[0-9]{1,7}|[A-Za-z][A-Za-z0-9]+);"
    )

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        body = token[1:-1]
        if body.startswith("#"):
            return html.unescape(token)
        return HTML5_ENTITIES.get(body + ";", token)

    return entity_re.sub(replace, value)


class _VisibleHTMLTextParser(HTMLParser):
    """Collect rendered text while ignoring hidden and non-content HTML regions."""

    _VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }
    _NON_CONTENT_TAGS = {"head", "script", "style", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.stack: list[tuple[str, bool]] = []
        self.hidden_depth = 0

    @staticmethod
    def _is_hidden(tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        values = {name.casefold(): (value or "") for name, value in attrs}
        style = re.sub(r"\s+", "", values.get("style", "").casefold())
        return (
            tag in _VisibleHTMLTextParser._NON_CONTENT_TAGS
            or "hidden" in values
            or values.get("aria-hidden", "").strip().casefold() == "true"
            or "display:none" in style
            or "visibility:hidden" in style
        )

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized = tag.casefold()
        hidden = self.hidden_depth > 0 or self._is_hidden(normalized, attrs)
        if normalized not in self._VOID_TAGS:
            self.stack.append((normalized, hidden))
            if hidden:
                self.hidden_depth += 1

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        return

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        matching = next(
            (
                index
                for index in range(len(self.stack) - 1, -1, -1)
                if self.stack[index][0] == normalized
            ),
            None,
        )
        if matching is None:
            return
        for _, hidden in self.stack[matching:]:
            if hidden:
                self.hidden_depth = max(0, self.hidden_depth - 1)
        del self.stack[matching:]

    def handle_data(self, data: str) -> None:
        if self.hidden_depth == 0:
            self.parts.append(data)


def visible_html_text(value: str) -> str:
    parser = _VisibleHTMLTextParser()
    parser.feed(value)
    parser.close()
    return "".join(parser.parts)


def strip_markdown_link_markup(value: str) -> str:
    """Keep rendered labels/alt text while discarding Markdown link destinations."""
    def render_segment(text: str, depth: int) -> str:
        if depth > 64:
            # Excessive nesting is not useful lifecycle evidence; fail closed.
            return "TODO(harness)"
        bracket_text = mask_inline_code_spans(text)
        bracket_text = mask_spans(bracket_text, inline_html_tag_spans(text))
        output: list[str] = []
        cursor = 0
        while cursor < len(text):
            opening = bracket_text.find("[", cursor)
            while opening >= 0 and is_escaped(text, opening):
                opening = bracket_text.find("[", opening + 1)
            if opening < 0:
                output.append(text[cursor:])
                break
            is_image = (
                opening > 0
                and text[opening - 1] == "!"
                and not is_escaped(text, opening - 1)
            )
            prefix_end = opening - 1 if is_image else opening
            output.append(text[cursor:prefix_end])
            closing = closing_square_bracket(bracket_text, opening)
            if closing < 0:
                output.append(text[prefix_end:])
                break
            label = text[opening + 1 : closing]
            following = closing + 1
            end = following
            if following < len(text) and text[following] == "(":
                link_end = closing_inline_link_parenthesis(text, following)
                if link_end >= 0:
                    end = link_end + 1
            elif following < len(text) and text[following] == "[":
                reference_end = closing_square_bracket(text, following)
                if reference_end >= 0:
                    end = reference_end + 1
            output.append(render_segment(label, depth + 1))
            cursor = end
        return "".join(output)

    return render_segment(value, 0)


def rendered_placeholder_source(value: str) -> str:
    """Expose unresolved markers after CommonMark entity and escape rendering."""
    rendered = transform_html_comments(value, collapse=True)
    rendered = strip_markdown_link_markup(rendered)
    rendered = visible_html_text(rendered)
    rendered = re.sub(r"[`*_~]", "", rendered)
    return markdown_unescape(commonmark_unescape_entities(rendered))


def has_unresolved_marker(value: str) -> bool:
    rendered = rendered_placeholder_source(value)
    return bool(
        PLACEHOLDER_RE.search(value)
        or UNRESOLVED_MARKER_RE.search(value)
        or PLACEHOLDER_RE.search(rendered)
        or UNRESOLVED_MARKER_RE.search(rendered)
    )


def rendered_link_destination(raw: str) -> str | None:
    """Return the destination after CommonMark escapes and entities are resolved."""
    normalized = normalized_link_destination(raw)
    if normalized is None:
        return None
    return commonmark_unescape_entities(markdown_unescape(normalized))


def local_link_value(raw: str) -> str | None:
    value = rendered_link_destination(raw)
    if value is None:
        return None
    if not value:
        return None
    lowered = value.lower()
    if value.startswith("//") or re.match(r"^[a-z][a-z0-9+.-]*:", lowered):
        return None
    path = value.split("#", 1)[0].split("?", 1)[0]
    return unquote(path)


def local_link_anchor(raw: str) -> str | None:
    value = rendered_link_destination(raw)
    if (
        value is None
        or not value
    ):
        return None
    lowered = value.lower()
    if (
        value.startswith("//")
        or re.match(r"^[a-z][a-z0-9+.-]*:", lowered)
        or "#" not in value
    ):
        return None
    anchor = unquote(value.split("#", 1)[1].strip())
    return anchor or None


def mask_same_shape(text: str) -> str:
    return "".join("\n" if character == "\n" else " " for character in text)


def valid_html_comment_spans(text: str) -> list[tuple[int, int]]:
    """Return closed inline comments and unclosed block-start HTML comments."""
    spans: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(text):
        start = text.find("<!--", cursor)
        if start < 0:
            break
        if is_escaped(text, start):
            cursor = start + 1
            continue
        line_start = text.rfind("\n", 0, start) + 1
        block_start = re.fullmatch(r" {0,3}", text[line_start:start]) is not None
        close = text.find("-->", start + 4)
        if close >= 0:
            content = text[start + 4 : close]
            valid = block_start or not (
                content.startswith((">", "->"))
                or content.endswith("-")
                or "--" in content
            )
            if valid:
                spans.append((start, close + 3))
                cursor = close + 3
                continue
            cursor = start + 4
            continue
        if block_start:
            spans.append((start, len(text)))
            break
        cursor = start + 4
    return spans


def transform_html_comments(text: str, *, collapse: bool = False) -> str:
    spans = valid_html_comment_spans(text)
    if not spans:
        return text
    pieces: list[str] = []
    cursor = 0
    for start, end in spans:
        pieces.append(text[cursor:start])
        pieces.append("" if collapse else mask_same_shape(text[start:end]))
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


HTML_BLOCK_TAGS = {
    "address", "article", "aside", "base", "basefont", "blockquote", "body",
    "caption", "center", "col", "colgroup", "dd", "details", "dialog", "dir",
    "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form",
    "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hr", "html", "iframe", "legend", "li", "link", "main", "menu",
    "menuitem", "nav", "noframes", "ol", "optgroup", "option", "p", "param",
    "search", "section", "summary", "table", "tbody", "td", "tfoot", "th",
    "thead", "title", "tr", "track", "ul",
}

CONTAINER_BOUNDARY = "\ue100HARNESS_CONTAINER_BOUNDARY\ue101"
INLINE_CODE_BOUNDARY = "\ue102"

INLINE_HTML_TAG_RE = re.compile(
    r"""(?:
        <[A-Za-z][A-Za-z0-9-]*
        (?:[ \t\r\n]+[A-Za-z_:][A-Za-z0-9_.:-]*
           (?:[ \t\r\n]*=[ \t\r\n]*
              (?:[^\s\"'=<>`]+|'[^']*'|\"[^\"]*\")
           )?
        )*
        [ \t\r\n]*/?>
        |
        </[A-Za-z][A-Za-z0-9-]*[ \t\r\n]*>
    )""",
    re.VERBOSE | re.DOTALL,
)


def mask_inline_code_spans(text: str) -> str:
    """Mask CommonMark backtick code spans, including multiline spans."""
    output = list(text)
    cursor = 0
    while cursor < len(text):
        opening = text.find("`", cursor)
        if opening < 0:
            break
        opening_end = opening
        while opening_end < len(text) and text[opening_end] == "`":
            opening_end += 1
        if is_escaped(text, opening):
            cursor = opening + 1
            continue
        width = opening_end - opening
        search = opening_end
        closing_end = -1
        while search < len(text):
            closing = text.find("`", search)
            if closing < 0:
                break
            run_end = closing
            while run_end < len(text) and text[run_end] == "`":
                run_end += 1
            if run_end - closing == width:
                between = text[opening_end:closing]
                if re.search(r"\r?\n[ \t]*\r?\n", between) or re.search(
                    r"\r?\n {0,3}(?:#{1,6}(?:[ \t]|$)|>[ \t]?|"
                    r"(?:[-+*]|1[.)])[ \t]+|`{3,}|~{3,}|"
                    r"(?:={3,}|-{3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})[ \t]*$|"
                    r"<!--|<\?|<!\[CDATA\[|<![A-Za-z]|"
                    r"</?(?:script|pre|style|textarea)(?:\s|>|$))",
                    between,
                    flags=re.MULTILINE | re.IGNORECASE,
                ):
                    break
                closing_end = run_end
                break
            search = run_end
        if closing_end < 0:
            cursor = opening_end
            continue
        for index in range(opening, closing_end):
            if output[index] not in {"\n", "\r"}:
                output[index] = " "
        cursor = closing_end
    return "".join(output)


def mark_inline_code_spans_for_boundaries(text: str) -> str:
    """Preserve inline-code paragraph presence without exposing nested syntax."""
    masked = mask_inline_code_spans(text)
    output = list(masked)
    for index, (source, rendered) in enumerate(zip(text, masked)):
        if source != rendered and rendered not in {"\n", "\r"}:
            output[index] = INLINE_CODE_BOUNDARY
    return "".join(output)


def mask_raw_html_blocks(
    text: str, *, type_one_only: bool = False, mask_comments: bool = True
) -> str:
    output: list[str] = []
    mode: str | None = None
    terminator: str | None = None
    previous_blank = True
    for line in markdown_source_lines(text, keepends=True):
        stripped_line = line.rstrip("\r\n")
        if stripped_line == CONTAINER_BOUNDARY:
            mode = None
            terminator = None
            output.append("\n" if line.endswith("\n") else "")
            previous_blank = True
            continue
        lowered = stripped_line.casefold()
        if mode is not None:
            if mode == "blank" and is_markdown_blank_line(stripped_line):
                mode = None
                terminator = None
                output.append(line)
                previous_blank = True
                continue
            output.append(mask_same_shape(line))
            if mode == "terminator" and terminator and terminator in lowered:
                mode = None
                terminator = None
            previous_blank = False
            continue

        prefix = re.match(r"^ {0,3}(.*)$", stripped_line)
        candidate = prefix.group(1) if prefix else stripped_line
        lowered_candidate = candidate.casefold()
        type_one = re.match(r"<(script|pre|style|textarea)(?:\s|>|$)", lowered_candidate)
        if type_one:
            terminator = f"</{type_one.group(1)}>"
            output.append(mask_same_shape(line))
            if terminator not in lowered_candidate:
                mode = "terminator"
            previous_blank = False
            continue
        if type_one_only:
            output.append(line)
            previous_blank = is_markdown_blank_line(stripped_line)
            continue
        if mask_comments and candidate.startswith("<!--"):
            output.append(mask_same_shape(line))
            if "-->" not in candidate:
                mode = "terminator"
                terminator = "-->"
            previous_blank = False
            continue
        special_terminator: str | None = None
        if candidate.startswith("<?"):
            special_terminator = "?>"
        elif candidate.startswith("<![CDATA["):
            special_terminator = "]]" + ">"
        elif re.match(r"<![A-Za-z]", candidate):
            special_terminator = ">"
        if special_terminator is not None:
            output.append(mask_same_shape(line))
            if special_terminator.casefold() not in lowered_candidate:
                mode = "terminator"
                terminator = special_terminator.casefold()
            previous_blank = False
            continue
        block_tag = re.match(r"</?([A-Za-z][A-Za-z0-9:-]*)(?:\s|/?>|$)", candidate)
        type_six = block_tag and block_tag.group(1).casefold() in HTML_BLOCK_TAGS
        previous_is_block = bool(
            output
            and re.match(
                r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|"
                r"(?:={3,}|-{3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})[ \t]*$)",
                output[-1].rstrip("\r\n"),
            )
        )
        type_seven = (previous_blank or previous_is_block) and INLINE_HTML_TAG_RE.fullmatch(
            candidate.rstrip(" \t")
        )
        if type_six or type_seven:
            output.append(mask_same_shape(line))
            mode = "blank"
            previous_blank = False
            continue
        output.append(line)
        previous_blank = is_markdown_blank_line(stripped_line)
    return "".join(output)


def mask_markdown_code(
    text: str,
    *,
    mask_comments: bool = True,
    mask_indented: bool = True,
    mask_html_blocks: bool = True,
) -> str:
    """Mask Markdown code and optionally comments while preserving line structure."""
    output: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in markdown_source_lines(text, keepends=True):
        if line.rstrip("\r\n") == CONTAINER_BOUNDARY:
            fence_character = None
            fence_length = 0
            output.append(line)
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        if marker and marker.group(1).startswith("`") and "`" in marker.group(2):
            marker = None
        if fence_character is None and marker:
            token = marker.group(1)
            fence_character = token[0]
            fence_length = len(token)
            output.append(mask_same_shape(line))
            continue
        if fence_character is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*$",
                line.rstrip("\r\n"),
            )
            if closing:
                fence_character = None
                fence_length = 0
            output.append(mask_same_shape(line))
            continue
        if mask_indented and re.match(r"^(?: {4}|\t)", line):
            output.append(mask_same_shape(line))
            continue
        output.append(line)
    result = "".join(output)
    if mask_html_blocks:
        result = mask_raw_html_blocks(result, mask_comments=mask_comments)
    result = mask_inline_code_spans(result)
    if mask_comments:
        result = transform_html_comments(result)
    return result


def starts_markdown_block(content: str) -> bool:
    candidate_match = re.match(r"^ {0,3}(.*)$", content)
    if candidate_match is None:
        return False
    candidate = candidate_match.group(1)
    lowered = candidate.casefold()
    fence = re.match(r"(`{3,}|~{3,})([^\r\n]*)", candidate)
    if fence and not (
        fence.group(1).startswith("`") and "`" in fence.group(2)
    ):
        return True
    if re.match(r"#{1,6}(?:[ \t]|$)", candidate):
        return True
    if re.match(r"<(script|pre|style|textarea)(?:\s|>|$)", lowered):
        return True
    if candidate.startswith(("<?", "<![CDATA[")) or re.match(r"<![A-Za-z]", candidate):
        return True
    if candidate.startswith(">"):
        return True
    block_tag = re.match(r"</?([A-Za-z][A-Za-z0-9:-]*)(?:\s|/?>|$)", candidate)
    return bool(
        (block_tag and block_tag.group(1).casefold() in HTML_BLOCK_TAGS)
        or INLINE_HTML_TAG_RE.fullmatch(candidate.rstrip(" \t"))
    )


def normalize_list_container_indentation(text: str) -> str:
    """Expose list-item child blocks at their container-relative indentation."""
    output: list[str] = []
    containers: list[tuple[int, int]] = []
    item_re = re.compile(r"^([ \t]*)([-*+]|\d{1,9}[.)])([ \t]+)(.*)$")

    for line in markdown_source_lines(text, keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        if is_markdown_blank_line(body):
            output.append(line)
            continue
        leading_match = re.match(r"^[ \t]*", body)
        leading = leading_match.group(0) if leading_match else ""
        indentation = len(leading.expandtabs(4))
        item = item_re.match(body)
        if item:
            popped = False
            while containers and indentation < containers[-1][1]:
                containers.pop()
                popped = True
            while containers and indentation <= containers[-1][0]:
                containers.pop()
                popped = True
            if popped:
                output.append(CONTAINER_BOUNDARY + "\n")
            parent_base = containers[-1][1] if containers else 0
            marker = item.group(2)
            spacing = item.group(3)
            content = item.group(4)
            marker_columns = len((leading + marker).expandtabs(4))
            content_columns = len((leading + marker + spacing).expandtabs(4))
            spacing_columns = content_columns - marker_columns
            task = (
                1 <= spacing_columns <= 4
                and re.match(r"^\[[ xX]\](?:[ \t]+|$)", content) is not None
            )
            if task:
                output.append(
                    " " * max(0, indentation - parent_base)
                    + marker
                    + spacing
                    + content
                    + ending
                )
            elif starts_markdown_block(content):
                output.append(
                    " " * max(0, content_columns - parent_base) + content + ending
                )
            else:
                output.append(
                    " " * max(0, indentation - parent_base)
                    + marker
                    + spacing
                    + content
                    + ending
                )
            containers.append((indentation, content_columns))
            continue
        popped = False
        while containers and indentation < containers[-1][1]:
            containers.pop()
            popped = True
        if popped:
            output.append(CONTAINER_BOUNDARY + "\n")
        base = containers[-1][1] if containers else 0
        output.append(
            " " * max(0, indentation - base) + body[len(leading) :] + ending
        )
    return "".join(output)


def normalize_blockquote_container_indentation(text: str) -> str:
    """Expose explicitly marked blockquote children without joining containers."""
    output: list[str] = []
    previous_depth = 0
    for line in markdown_source_lines(text, keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        remainder = body
        depth = 0
        while True:
            quote = re.match(r"^ {0,3}>[ \t]?", remainder)
            if quote is None:
                break
            remainder = remainder[quote.end() :]
            depth += 1
        if depth != previous_depth and (depth or previous_depth):
            output.append(CONTAINER_BOUNDARY + "\n")
        output.append(remainder + ending)
        previous_depth = depth
    return "".join(output)


def normalize_markdown_containers(text: str) -> str:
    """Normalize list and explicit blockquote containers for code-aware scans."""
    listed = normalize_list_container_indentation(text)
    unquoted = normalize_blockquote_container_indentation(listed)
    return normalize_list_container_indentation(unquoted)


def mask_explicit_blockquote_lines(text: str) -> str:
    """Mask blockquoted source lines when only root-level structure is valid."""
    output: list[str] = []
    for line in markdown_source_lines(text, keepends=True):
        if re.match(r"^ {0,3}>", line):
            output.append(mask_same_shape(line))
        else:
            output.append(line)
    return "".join(output)


def quoted_container_content(line: str) -> tuple[str, int]:
    """Return content and explicit quote depth for alternating quote/list prefixes."""
    remainder = line.rstrip("\r\n")
    quote_depth = 0
    while remainder:
        quote = re.match(r"^ {0,3}>[ \t]?", remainder)
        if quote is not None:
            quote_depth += 1
            remainder = remainder[quote.end() :]
            continue
        item = re.match(
            r"^ {0,3}(?:[-*+]|\d{1,9}[.)])[ \t]{1,4}(.*)$",
            remainder,
        )
        if item is None:
            break
        remainder = item.group(1)
    return remainder, quote_depth


def mask_explicit_quoted_fences(text: str) -> str:
    """Mask fenced code nested through explicit blockquote/list prefixes."""
    output: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    opening_quote_depth = 0
    for line in markdown_source_lines(text, keepends=True):
        content, quote_depth = quoted_container_content(line)
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)", content)
        if marker and marker.group(1).startswith("`") and "`" in marker.group(2):
            marker = None
        if fence_character is not None and quote_depth < opening_quote_depth:
            fence_character = None
            fence_length = 0
            opening_quote_depth = 0
        if fence_character is None and quote_depth > 0 and marker:
            token = marker.group(1)
            fence_character = token[0]
            fence_length = len(token)
            opening_quote_depth = quote_depth
            output.append(mask_same_shape(line))
            continue
        if fence_character is not None:
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*",
                content,
            )
            output.append(mask_same_shape(line))
            if closing:
                fence_character = None
                fence_length = 0
                opening_quote_depth = 0
            continue
        output.append(line)
    return "".join(output)


def markdown_task_items(text: str) -> list[tuple[str, str]]:
    """Return live task-list items while excluding fenced and root indented code."""
    normalized = normalize_markdown_containers(
        mask_inline_code_spans(mask_explicit_quoted_fences(text))
    )
    structural = mask_markdown_code(normalized)
    tasks: list[tuple[str, str]] = []
    paragraph_open = False
    normalized_lines = markdown_source_lines(normalized)
    structural_lines = markdown_source_lines(structural)
    for normalized_line, line in zip(normalized_lines, structural_lines):
        if normalized_line.strip() == CONTAINER_BOUNDARY:
            continue
        task_match = CHECKBOX_RE.match(line)
        spacing_columns = 0
        if task_match:
            before_spacing = task_match.group(1) + task_match.group(2)
            through_spacing = before_spacing + task_match.group(3)
            spacing_columns = len(through_spacing.expandtabs(4)) - len(
                before_spacing.expandtabs(4)
            )
        if (
            task_match
            and len(task_match.group(1).expandtabs(4)) <= 3
            and 1 <= spacing_columns <= 4
        ):
            ordered = re.match(r"^[ \t]*(\d{1,9})[.)][ \t]+", line)
            interrupts_paragraph = (
                ordered is not None
                and ordered.group(1) != "1"
                and paragraph_open
            )
            if not interrupts_paragraph:
                tasks.append((task_match.group(4), task_match.group(5) or ""))
                paragraph_open = False
            continue
        if is_markdown_blank_line(line):
            paragraph_open = not is_markdown_blank_line(normalized_line)
            continue
        list_item = re.match(
            r"^[ \t]*(?:[-*+]|(\d{1,9})[.)])[ \t]+", line
        )
        if list_item is not None:
            number = list_item.group(1)
            if number is None or number == "1" or not paragraph_open:
                paragraph_open = False
            continue
        paragraph_open = True
    return tasks


def mask_index_markdown(text: str) -> str:
    """Mask code/comments while retaining only the four exact lifecycle markers."""
    markers = (ACTIVE_START, ACTIVE_END, COMPLETED_START, COMPLETED_END)
    protected = mask_markdown_code(text, mask_comments=False)
    sentinels: dict[str, str] = {}
    for index, marker in enumerate(markers):
        sentinel = f"\ue000HARNESS_LIFECYCLE_MARKER_{index}\ue001"
        while sentinel in protected:
            sentinel += "\ue002"
        sentinels[sentinel] = marker
        comment_spans = valid_html_comment_spans(protected)

        def protect(match: re.Match[str]) -> str:
            nested = any(
                start <= match.start() < end
                and (start < match.start() or end > match.end())
                for start, end in comment_spans
            )
            return match.group(0) if nested else sentinel

        protected = re.sub(
            rf"(?m)^{re.escape(marker)}[ \t]*$", protect, protected
        )
    masked = transform_html_comments(protected)
    for sentinel, marker in sentinels.items():
        masked = masked.replace(sentinel, marker)
    return masked


def is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def normalize_reference_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def valid_reference_label(value: str) -> str | None:
    label = normalize_reference_label(value)
    if not label or len(label) > 999:
        return None
    return label


def closing_square_bracket(text: str, opening: int) -> int:
    depth = 1
    cursor = opening + 1
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == "[":
            depth += 1
        elif text[cursor] == "]":
            depth -= 1
            if depth == 0:
                return cursor
        cursor += 1
    return -1


def closing_inline_link_parenthesis(text: str, opening: int) -> int:
    """Return the first closing parenthesis that yields valid inline-link content."""
    start = opening + 1
    cursor = start
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == ")":
            if normalized_link_destination(text[start:cursor]) is not None:
                return cursor
        cursor += 1
    return -1


def inline_html_tag_spans(text: str) -> list[tuple[int, int]]:
    """Return inline raw-HTML and autolink spans where Markdown is inert."""
    spans = [
        match.span()
        for match in INLINE_HTML_TAG_RE.finditer(text)
        if not is_escaped(text, match.start())
    ]
    token_patterns = (
        r"<\?.*?\?>",
        r"<!\[CDATA\[.*?\]\]>",
        r"<![A-Za-z][^>]*>",
        r"<[A-Za-z][A-Za-z0-9+.-]{1,31}:[^<>\x00-\x20]*>",
        r"<[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+>",
    )
    for pattern in token_patterns:
        spans.extend(
            match.span()
            for match in re.finditer(pattern, text, re.DOTALL)
            if not is_escaped(text, match.start())
        )
    merged: list[tuple[int, int]] = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def mask_spans(text: str, spans: Iterable[tuple[int, int]]) -> str:
    output = list(text)
    for start, end in spans:
        for index in range(start, min(end, len(output))):
            if output[index] not in {"\n", "\r"}:
                output[index] = " "
    return "".join(output)


def line_has_blockquote_container(line: str) -> bool:
    remainder = line.rstrip("\r\n")
    for _ in range(64):
        quote = re.match(r"^ {0,3}>", remainder)
        if quote is not None:
            return True
        item = re.match(
            r"^ {0,3}(?:[-*+]|\d{1,9}[.)])[ \t]{1,4}(.*)$",
            remainder,
        )
        if item is None:
            return False
        remainder = item.group(1)
    return True


def mask_navigation_blockquotes(text: str) -> str:
    output: list[str] = []
    lazy_paragraph = False
    for line in markdown_source_lines(text, keepends=True):
        body = line.rstrip("\r\n")
        if line_has_blockquote_container(line):
            output.append(mask_same_shape(line))
            content, quote_depth = quoted_container_content(line)
            lazy_paragraph = bool(
                quote_depth
                and not is_markdown_blank_line(content)
                and not starts_markdown_block(content)
            )
            continue
        if lazy_paragraph:
            if is_markdown_blank_line(body):
                lazy_paragraph = False
                output.append(line)
                continue
            interrupting_item = re.match(
                r"^ {0,3}(?:[-*+]|1[.)])[ \t]{1,4}(\S.*)$", body
            )
            thematic_break = re.match(
                r"^ {0,3}(?:={3,}|-{3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})[ \t]*$",
                body,
            )
            if starts_markdown_block(body) or interrupting_item or thematic_break:
                lazy_paragraph = False
                output.append(line)
                continue
            output.append(mask_same_shape(line))
            continue
        output.append(line)
    return "".join(output)


def reference_definition_candidate(
    lines: Sequence[str], index: int
) -> tuple[str, str, int] | None:
    """Parse one CommonMark reference definition spanning at most three lines."""
    match = re.fullmatch(r" {0,3}\[([^\]\r\n]+)\]:[ \t]*(.*)", lines[index])
    if match is None:
        return None
    label = valid_reference_label(match.group(1))
    if label is None:
        return None
    remainder = match.group(2)
    candidates: list[tuple[str, int]] = []
    if remainder:
        if (
            index + 1 < len(lines)
            and re.match(r"^ {0,3}[\"'(]", lines[index + 1])
        ):
            candidates.append((remainder + "\n" + lines[index + 1], 2))
        candidates.append((remainder, 1))
    elif index + 1 < len(lines) and re.match(r"^ {0,3}\S", lines[index + 1]):
        destination_line = lines[index + 1]
        if (
            index + 2 < len(lines)
            and re.match(r"^ {0,3}[\"'(]", lines[index + 2])
        ):
            candidates.append(
                (destination_line + "\n" + lines[index + 2], 3)
            )
        candidates.append((destination_line, 2))
    for raw_destination, consumed in candidates:
        destination = normalized_link_destination(raw_destination)
        if destination is not None:
            return label, raw_destination, consumed
    return None


def markdown_line_ends_paragraph(line: str) -> bool:
    """Return whether a live CommonMark block line leaves no open paragraph."""
    if starts_markdown_block(line):
        return True
    return bool(
        re.fullmatch(
            r" {0,3}(?:={2,}|-{2,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})[ \t]*",
            line,
        )
    )


def markdown_bracket_nesting_exceeds(text: str, limit: int) -> bool:
    """Bound live square-bracket nesting before recursive inline parsing."""
    depth = 0
    for index, character in enumerate(text):
        if character == "[" and not is_escaped(text, index):
            depth += 1
            if depth > limit:
                return True
        elif character == "]" and not is_escaped(text, index):
            depth = max(0, depth - 1)
    return False


def scan_markdown_links(
    text: str,
    *,
    include_images: bool = True,
    _depth: int = 0,
) -> tuple[list[str], list[str]]:
    """Extract inline/reference links and unresolved reference labels."""
    if _depth >= MAX_MARKDOWN_LINK_NESTING:
        return [], [MARKDOWN_LINK_NESTING_SENTINEL]
    prepared = mask_explicit_quoted_fences(text)
    normalized = normalize_markdown_containers(mask_inline_code_spans(prepared))
    boundary_source = normalize_markdown_containers(
        mark_inline_code_spans_for_boundaries(prepared)
    )
    text = mask_markdown_code(normalized)
    bracket_source = mask_spans(text, inline_html_tag_spans(text))
    if markdown_bracket_nesting_exceeds(
        bracket_source, MAX_MARKDOWN_LINK_NESTING
    ):
        return [], [MARKDOWN_LINK_NESTING_SENTINEL]
    normalized_lines = markdown_source_lines(boundary_source)
    structural_lines = markdown_source_lines(text)
    line_chunks = markdown_source_lines(text, keepends=True)
    line_offsets: list[int] = []
    offset = 0
    for chunk in line_chunks:
        line_offsets.append(offset)
        offset += len(chunk)
    definitions: dict[str, str] = {}
    definition_spans: list[tuple[int, int]] = []
    paragraph_open = False
    line_index = 0
    while line_index < min(len(normalized_lines), len(structural_lines)):
        source_line = normalized_lines[line_index]
        structural_line = structural_lines[line_index]
        if structural_line.strip() == CONTAINER_BOUNDARY:
            paragraph_open = False
            line_index += 1
            continue
        if is_markdown_blank_line(structural_line):
            if is_markdown_blank_line(source_line):
                paragraph_open = False
            elif INLINE_CODE_BOUNDARY in source_line:
                # A line containing only inline code is still paragraph content.
                paragraph_open = True
            else:
                # Fenced/indented code, HTML blocks, and comments are leaf blocks.
                paragraph_open = False
            line_index += 1
            continue
        if not paragraph_open:
            parsed = reference_definition_candidate(structural_lines, line_index)
            if parsed is not None:
                label, raw_destination, consumed = parsed
                definitions.setdefault(label, raw_destination)
                start = line_offsets[line_index]
                end_line = line_index + consumed
                end = line_offsets[end_line] if end_line < len(line_offsets) else len(text)
                definition_spans.append((start, end))
                paragraph_open = False
                line_index += consumed
                continue
        paragraph_open = not markdown_line_ends_paragraph(structural_line)
        line_index += 1
    if definition_spans:
        pieces: list[str] = []
        cursor = 0
        for start, end in definition_spans:
            pieces.append(text[cursor:start])
            pieces.append(mask_same_shape(text[start:end]))
            cursor = end
        pieces.append(text[cursor:])
        text = "".join(pieces)

    html_spans = inline_html_tag_spans(text)
    bracket_text = mask_spans(text, html_spans)
    html_index = 0
    destinations: list[str] = []
    missing_references: list[str] = []
    index = 0
    while index < len(text):
        open_bracket = text.find("[", index)
        if open_bracket < 0:
            break
        while html_index < len(html_spans) and html_spans[html_index][1] <= open_bracket:
            html_index += 1
        if (
            html_index < len(html_spans)
            and html_spans[html_index][0] <= open_bracket < html_spans[html_index][1]
        ):
            index = html_spans[html_index][1]
            continue
        if is_escaped(text, open_bracket):
            index = open_bracket + 1
            continue
        is_image = (
            open_bracket > 0
            and text[open_bracket - 1] == "!"
            and not is_escaped(text, open_bracket - 1)
        )
        close_bracket = closing_square_bracket(bracket_text, open_bracket)
        if close_bracket < 0:
            break
        link_text = text[open_bracket + 1 : close_bracket]
        if re.search(r"\r?\n[ \t]*\r?\n", link_text):
            index = open_bracket + 1
            continue
        nested_navigation: list[str] = []
        nested_missing: list[str] = []
        nested_all: list[str] = []
        if not is_image:
            nested_navigation, nested_missing = scan_markdown_links(
                link_text, include_images=False, _depth=_depth + 1
            )
            nested_all = nested_navigation
            if include_images:
                nested_all, nested_missing_all = scan_markdown_links(
                    link_text, include_images=True, _depth=_depth + 1
                )
                nested_missing = list(dict.fromkeys(nested_missing + nested_missing_all))
        if nested_all:
            destinations.extend(nested_all)
        if nested_missing:
            missing_references.extend(nested_missing)
        nested_link = bool(nested_navigation or nested_missing)
        following = close_bracket + 1
        if following < len(text) and text[following] == "(":
            closing = closing_inline_link_parenthesis(text, following)
            if closing >= 0:
                raw_destination = text[following + 1 : closing]
                if (
                    not nested_link
                    and
                    normalized_link_destination(raw_destination) is not None
                    and (include_images or not is_image)
                ):
                    destinations.append(raw_destination)
                index = closing + 1
            else:
                index = open_bracket + 1
            continue
        if following < len(text) and text[following] == "[":
            reference_end = closing_square_bracket(bracket_text, following)
            if reference_end >= 0:
                raw_label = text[following + 1 : reference_end] or link_text
                label = valid_reference_label(raw_label)
                if (
                    not nested_link
                    and label is not None
                    and label in definitions
                    and (include_images or not is_image)
                ):
                    destinations.append(definitions[label])
                elif (
                    not nested_link
                    and label is not None
                    and label not in definitions
                    and (include_images or not is_image)
                ):
                    missing_references.append(raw_label)
                index = reference_end + 1
                continue
        label = valid_reference_label(link_text)
        if (
            not nested_link
            and label is not None
            and label in definitions
            and (include_images or not is_image)
        ):
            destinations.append(definitions[label])
        index = close_bracket + 1
    return destinations, missing_references


def markdown_link_destinations(text: str) -> list[str]:
    return scan_markdown_links(text)[0]


def markdown_navigation_destinations(text: str) -> list[str]:
    return scan_markdown_links(
        mask_navigation_blockquotes(text), include_images=False
    )[0]


def missing_markdown_references(text: str) -> list[str]:
    return scan_markdown_links(text)[1]


def valid_utc_timestamp(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%MZ")
    except ValueError:
        return False
    return True


def has_valid_utc_timestamp(text: str) -> bool:
    for value in re.findall(r"\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}Z)\)", text):
        if valid_utc_timestamp(value):
            return True
    return False


def revision_history_is_structured(text: str) -> bool:
    entry_start = re.compile(
        r"^[ \t]{0,3}[-*+]\s+"
        r"\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}Z)\)\s+"
        r"Change:\s*(.*)$"
    )
    entries: list[tuple[str, list[str]]] = []
    current_timestamp: str | None = None
    current_lines: list[str] = []

    for line in markdown_source_lines(text):
        start = entry_start.match(line)
        if start:
            if current_timestamp is not None:
                entries.append((current_timestamp, current_lines))
            current_timestamp = start.group(1)
            current_lines = [start.group(2)]
            continue
        if is_markdown_blank_line(line):
            if current_timestamp is not None:
                current_lines.append("")
            continue
        if current_timestamp is None or not line.startswith((" ", "\t")):
            return False
        current_lines.append(line.strip())

    if current_timestamp is not None:
        entries.append((current_timestamp, current_lines))
    if not entries:
        return False
    for timestamp, lines in entries:
        body = "\n".join(lines).strip()
        if "Reason:" not in body:
            return False
        change, reason = body.split("Reason:", 1)
        if (
            not valid_utc_timestamp(timestamp)
            or substantive_length(change) < 8
            or substantive_length(reason) < 8
        ):
            return False
    return True


def markdown_heading_slug(value: str) -> str:
    value = transform_html_comments(value, collapse=True)
    value = re.sub(
        r"</?[A-Za-z][A-Za-z0-9-]*(?:[ \t]+[^<>]*)?/?>",
        "",
        value,
    )
    value = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"!?\[([^\]]+)\]\[[^\]]*\]", r"\1", value)
    value = re.sub(r"!?\[([^\]]+)\]", r"\1", value)
    value = commonmark_unescape_entities(markdown_unescape(value))
    value = re.sub(r"[`*_~]", "", value).strip().casefold()
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return re.sub(r"[ \t]+", "-", value)


def markdown_anchors(text: str) -> set[str]:
    normalized = normalize_markdown_containers(text)
    structural = mask_markdown_code(normalized)
    anchor_source = mask_raw_html_blocks(
        mask_markdown_code(normalized, mask_html_blocks=False),
        type_one_only=True,
    )
    anchors: set[str] = set()
    counts: Counter[str] = Counter()
    for match in re.finditer(
        r"(?m)^[ \t]{0,3}#{1,6}\s+(.+?)\s*#*\s*$", structural
    ):
        base = markdown_heading_slug(match.group(1))
        if not base:
            continue
        number = counts[base]
        counts[base] += 1
        anchors.add(base if number == 0 else f"{base}-{number}")
    for tag in INLINE_HTML_TAG_RE.finditer(anchor_source):
        if is_escaped(anchor_source, tag.start()):
            continue
        attributes = tag.group(0)
        name_match = re.match(r"(?is)<([a-z][a-z0-9:-]*)\b", attributes)
        if name_match is None:
            continue
        tag_name = name_match.group(1).casefold()
        names = ("id", "name") if tag_name == "a" else ("id",)
        for attribute in names:
            match = re.search(
                rf"(?is)(?:\s){attribute}\s*=\s*(?:"
                rf"\"([^\"]+)\"|'([^']+)'|([^\s\"'=<>`]+))",
                attributes,
            )
            if match:
                anchors.add(
                    html.unescape(match.group(1) or match.group(2) or match.group(3))
                )
    return anchors


def resolve_markdown_link(root: Path, source: Path, raw: str) -> tuple[Path | None, str | None]:
    root = root.resolve()
    source = source.resolve(strict=False)
    value = local_link_value(raw)
    if value is None:
        return None, None
    if not value:
        candidate = source
    else:
        candidate = root / value.lstrip("/") if value.startswith("/") else source.parent / value
    try:
        resolved = candidate.resolve(strict=False)
        common = Path(os.path.commonpath((str(root), str(resolved))))
    except (OSError, ValueError) as exc:
        return None, str(exc)
    if common != root:
        return None, "link escapes the repository"
    return resolved, None


def markdown_files(root: Path, report: Report | None = None) -> Iterable[Path]:
    excluded = {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "vendor",
        "Pods",
        "DerivedData",
        ".dart_tool",
        ".next",
        "dist",
        "build",
        "target",
    }
    discovered: list[Path] = []

    def walk_error(error: OSError) -> None:
        if report is None:
            return
        path = Path(error.filename) if error.filename else root
        report.add(
            "LINK000",
            "error",
            relative_display(root, path),
            f"Repository Markdown traversal could not read a path: {error}.",
            "Restore read permission or explicitly exclude the path through project policy.",
        )

    for current, directories, files in os.walk(
        root,
        followlinks=False,
        onerror=walk_error,
    ):
        current_path = Path(current)
        directories[:] = sorted(
            name
            for name in directories
            if name not in excluded and not (current_path / name).is_symlink()
        )
        for name in sorted(files):
            path = current_path / name
            if (
                Path(name).suffix.casefold() in {".md", ".markdown"}
                and not path.is_symlink()
                and path.is_file()
            ):
                discovered.append(path)
    yield from sorted(discovered)


def check_text_links(
    report: Report,
    root: Path,
    source: Path,
    text: str,
    finding_id: str = "LINK001",
    virtual_exists: Iterable[Path] = (),
    virtual_missing: Iterable[Path] = (),
    anchor_cache: dict[Path, tuple[set[str] | None, str | None]] | None = None,
) -> None:
    if anchor_cache is None:
        anchor_cache = {}
    source_resolved = source.resolve(strict=False)
    virtual = {item.resolve(strict=False) for item in virtual_exists}
    missing = {item.resolve(strict=False) for item in virtual_missing}
    destinations, missing_references = scan_markdown_links(text)
    for label in missing_references:
        if label == MARKDOWN_LINK_NESTING_SENTINEL:
            report.add(
                "LINK002",
                "error",
                relative_display(root, source),
                f"Markdown link labels exceed the {MAX_MARKDOWN_LINK_NESTING}-level nesting limit.",
                "Flatten nested link/image labels so routing and link validation remain bounded and reviewable.",
            )
            continue
        report.add(
            finding_id,
            "error",
            relative_display(root, source),
            f"Markdown reference link has no definition: {label!r}",
            "Add the reference definition or use a resolving inline link.",
        )
    for raw in destinations:
        target, error = resolve_markdown_link(root, source, raw)
        if error:
            report.add(
                finding_id,
                "error",
                relative_display(root, source),
                f"Unsafe local Markdown link {raw!r}: {error}.",
                "Use a repository-contained relative link.",
            )
            continue
        if target is None:
            continue
        target = target.resolve(strict=False)
        if target in missing or (target not in virtual and not target.exists()):
            report.add(
                finding_id,
                "error",
                relative_display(root, source),
                f"Local Markdown link does not resolve: {raw}",
                "Create the target or correct/remove the link.",
            )
            continue
        anchor = local_link_anchor(raw)
        if anchor is None or target.suffix.lower() not in {".md", ".markdown"}:
            continue
        if target not in anchor_cache:
            try:
                target_text = text if target == source_resolved else read_text_safe(root, target)
                anchor_cache[target] = (markdown_anchors(target_text), None)
            except (OSError, SafeRefusal) as exc:
                anchor_cache[target] = (None, str(exc))
        anchors, anchor_error = anchor_cache[target]
        if anchor_error is not None:
            report.add(
                finding_id,
                "error",
                relative_display(root, source),
                f"Anchor target could not be read safely: {raw!r}: {anchor_error}",
                "Restore the target as a regular UTF-8 Markdown file.",
            )
            continue
        if anchors is not None and anchor not in anchors:
            report.add(
                finding_id,
                "error",
                relative_display(root, source),
                f"Markdown anchor does not resolve: {raw}",
                "Correct the fragment or add the intended target heading/id.",
            )


def check_links(report: Report, root: Path, files: Iterable[Path]) -> None:
    anchor_cache: dict[Path, tuple[set[str] | None, str | None]] = {}
    for path in files:
        try:
            text = read_text_safe(root, path)
        except (OSError, SafeRefusal) as exc:
            report.add(
                "LINK000",
                "error",
                relative_display(root, path),
                f"Markdown file could not be read safely: {exc}",
                "Restore a regular UTF-8 file within the repository.",
            )
            continue
        check_text_links(report, root, path, text, anchor_cache=anchor_cache)


def region_lines(text: str, start: str, end: str) -> list[str] | None:
    starts = list(re.finditer(rf"(?m)^{re.escape(start)}[ \t]*$", text))
    ends = list(re.finditer(rf"(?m)^{re.escape(end)}[ \t]*$", text))
    if len(starts) != 1 or len(ends) != 1:
        return None
    start_at = starts[0].start()
    start_end = starts[0].end()
    end_at = ends[0].start()
    if start_at >= end_at:
        return None
    body = text[start_end:end_at]
    return [
        line.rstrip()
        for line in markdown_source_lines(body)
        if not is_markdown_blank_line(line)
    ]


@dataclass(frozen=True)
class IndexRow:
    target: str
    title: str
    cells: tuple[str, ...]


@dataclass(frozen=True)
class CoverageRow:
    identity: str
    status_cell: str
    line: int


def split_markdown_table_row(line: str) -> tuple[str, ...] | None:
    if not line.startswith("|") or not line.endswith("|"):
        return None
    content = line[1:-1]
    cells: list[str] = []
    buffer: list[str] = []
    index = 0
    while index < len(content):
        character = content[index]
        if character == "\\" and index + 1 < len(content) and content[index + 1] == "|":
            buffer.append("|")
            index += 2
            continue
        if character == "|":
            cells.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(character)
        index += 1
    cells.append("".join(buffer).strip())
    return tuple(cells)


def visible_markdown_cell(value: str) -> str:
    value = transform_html_comments(value, collapse=True)
    value = strip_markdown_link_markup(value)
    value = visible_html_text(value)
    value = rendered_placeholder_source(value)
    value = re.sub(r"[`*_~]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def contains_raw_html_markup(value: str) -> bool:
    if any(not is_escaped(value, match.start()) for match in INLINE_HTML_TAG_RE.finditer(value)):
        return True
    return bool(re.search(r"(?is)<!--|<\?|<!\[CDATA\[|<![A-Z]", value))


def is_substantive_lifecycle_fact(value: str, *, minimum_alnum: int = 2) -> bool:
    """Reject empty, punctuation-only, and sentinel lifecycle facts."""
    visible = visible_markdown_cell(value)
    if not visible or has_unresolved_marker(value) or contains_raw_html_markup(value):
        return False
    normalized = re.sub(r"\s+", " ", visible.casefold()).strip()
    sentinel_phrases = (
        r"(?:none|no one|nobody)(?: (?:assigned|available|named))?",
        r"(?:no|not|without) (?:(?:current|named|assigned|available) )?"
        r"(?:owner|team|assignee|milestone)(?: yet)?",
        r"(?:none|not) assigned(?: yet)?",
        r"(?:unassigned|unowned)(?: (?:owner|team|role|milestone))?",
        r"(?:awaiting|pending) (?:(?:owner|team|role|milestone) )?"
        r"(?:assignment|confirmation|selection|decision)",
        r"(?:to be|yet to be) (?:assigned|confirmed|determined|decided|named|selected)",
    )
    if any(re.fullmatch(pattern, normalized) for pattern in sentinel_phrases):
        return False
    compact = re.sub(r"[^a-z0-9]+", "", visible.casefold())
    if compact in {
        "na",
        "nil",
        "none",
        "noneyet",
        "noowner",
        "nomilestone",
        "nomilestoneyet",
        "notapplicable",
        "notavailable",
        "notassigned",
        "notyet",
        "notrecorded",
        "notset",
        "null",
        "pending",
        "tba",
        "tbd",
        "tbc",
        "todo",
        "tobeassigned",
        "tobedetermined",
        "awaitingassignment",
        "awaitingowner",
        "awaitingownerassignment",
        "unknown",
        "unassigned",
        "unowned",
        "unset",
    }:
        return False
    return len(re.findall(r"[\w]", visible, flags=re.UNICODE)) >= minimum_alnum


def is_substantive_owner(value: str) -> bool:
    """Require an assigned durable role/team, not a pending-assignment phrase."""
    if not is_substantive_lifecycle_fact(value):
        return False
    normalized = re.sub(r"\s+", " ", visible_markdown_cell(value).casefold()).strip()
    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    if tokens & {
        "awaiting",
        "forthcoming",
        "none",
        "nobody",
        "null",
        "pending",
        "tba",
        "tbd",
        "todo",
        "unassigned",
        "unknown",
        "unowned",
    }:
        return False
    absence_patterns = (
        r"\bnot\b.*\b(?:assign(?:ed|ment)?|selected|named|confirmed|determined)\b",
        r"\bno\b.*\b(?:owner|assignee|team|role|assign(?:ed|ment)?)\b",
        r"\bwithout\b.*\b(?:owner|assignee|team|role)\b",
        r"\b(?:owner|assignee|team|role)\b.*\bto be assigned\b",
        r"\bto be (?:assigned|confirmed|determined|named|selected)\b",
        r"\b(?:to|yet to) assign\b",
        r"\bneeds?\b.*\bassign(?:ed|ment)?\b",
        r"\bassign(?:ed|ment)?\b.*\blater\b",
    )
    return not any(re.search(pattern, normalized) for pattern in absence_patterns)


def semantic_review_attestation_is_valid(text: str) -> bool:
    """Validate the local durable completion-review attestation."""
    pattern = re.compile(
        r"^[ \t]+Semantic-Review:[ \t]*"
        r"reviewer=([^;\r\n]+);[ \t]*"
        r"reviewed-at=([^;\r\n]+);[ \t]*"
        r"evidence=(.+)$",
        re.IGNORECASE,
    )
    for line in markdown_source_lines(text):
        match = pattern.fullmatch(line)
        if match is None:
            continue
        reviewer, reviewed_at, evidence = (part.strip() for part in match.groups())
        if (
            is_substantive_owner(reviewer)
            and valid_utc_timestamp(reviewed_at)
            and substantive_length(evidence) >= 80
            and not has_unresolved_marker(evidence)
            and not contains_raw_html_markup(evidence)
        ):
            return True
    return False


def normalize_coverage_identity(value: str) -> str:
    return visible_markdown_cell(value).casefold()


def coverage_table_rows(
    text: str,
) -> tuple[list[CoverageRow], int, list[int], bool]:
    """Parse live four-column coverage tables and bound adversarial row counts."""
    raw_lines = markdown_source_lines(text)
    structural_lines = markdown_source_lines(mask_markdown_code(text))
    rows: list[CoverageRow] = []
    table_count = 0
    malformed_lines: list[int] = []
    truncated = False
    index = 0
    while index + 1 < min(len(raw_lines), len(structural_lines)):
        raw_header = split_markdown_table_row(raw_lines[index].rstrip())
        structural_header = split_markdown_table_row(structural_lines[index].rstrip())
        raw_separator = split_markdown_table_row(raw_lines[index + 1].rstrip())
        structural_separator = split_markdown_table_row(
            structural_lines[index + 1].rstrip()
        )
        header = tuple(visible_markdown_cell(cell).casefold() for cell in (raw_header or ()))
        valid_separator = (
            structural_separator is not None
            and len(structural_separator) == 4
            and all(
                re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))
                for cell in structural_separator
            )
        )
        recognized = (
            raw_header is not None
            and structural_header is not None
            and raw_separator is not None
            and len(raw_header) == 4
            and len(structural_header) == 4
            and len(raw_separator) == 4
            and valid_separator
            and "status" in header[-1]
            and ("reason" in header[-1] or "evidence" in header[-1])
        )
        if not recognized:
            index += 1
            continue
        table_count += 1
        index += 2
        while index < min(len(raw_lines), len(structural_lines)):
            raw_line = raw_lines[index].rstrip()
            structural_line = structural_lines[index].rstrip()
            if not raw_line.strip():
                break
            if not structural_line.startswith("|") or not structural_line.endswith("|"):
                break
            cells = split_markdown_table_row(raw_line)
            if cells is None or len(cells) != 4:
                malformed_lines.append(index + 1)
                index += 1
                continue
            if len(rows) >= MAX_COVERAGE_ROWS:
                truncated = True
                break
            rows.append(CoverageRow(cells[0], cells[3], index + 1))
            index += 1
        if truncated:
            break
    return rows, table_count, malformed_lines, truncated


def parse_coverage_status(value: str) -> tuple[str | None, str]:
    if has_unresolved_marker(value) or contains_raw_html_markup(value):
        return None, ""
    visible = visible_markdown_cell(value)
    match = re.fullmatch(
        r"(?is)(verified|candidate|blocked|n\s*/\s*a)"
        r"(?:\s*(?:—|–|-|:)\s*|\s+)(.+)",
        visible,
    )
    if match is None:
        return None, ""
    status = match.group(1).replace(" ", "").casefold()
    status = "n/a" if status == "n/a" else status
    detail = match.group(2).strip()
    if substantive_length(detail) < 8 or has_unresolved_marker(detail):
        return None, detail
    return status, detail


def validate_coverage(
    report: Report,
    root: Path,
    coverage_path: Path,
    *,
    require_canonical_rows: bool,
) -> None:
    root = resolve_safe_directory(root)
    original_path = coverage_path
    if original_path.is_symlink():
        return
    try:
        relative = original_path.resolve(strict=False).relative_to(root)
        coverage_path = safe_target(root, relative.as_posix())
    except (OSError, ValueError, SafeRefusal):
        return
    rel = relative_display(root, coverage_path)
    if not coverage_path.is_file() or coverage_path.is_symlink():
        return
    try:
        text = read_text_safe(root, coverage_path)
    except (OSError, SafeRefusal) as exc:
        report.add(
            "COVERAGE001",
            "warning",
            rel,
            f"Coverage authority could not be read safely: {exc}",
            "Restore a regular UTF-8 coverage matrix and rerun the canonical gate.",
        )
        return
    rows, table_count, malformed_lines, truncated = coverage_table_rows(text)
    if table_count == 0:
        report.add(
            "COVERAGE001",
            "warning",
            rel,
            "No live four-column coverage table with a Status and reason/evidence column was found.",
            "Record every capability in a real Markdown table with an explained status.",
        )
    for line in malformed_lines[:25]:
        report.add(
            "COVERAGE001",
            "warning",
            rel,
            f"Coverage row at line {line} is not a four-column Markdown row.",
            "Restore the declared four-column table shape.",
        )
    if len(malformed_lines) > 25:
        report.add(
            "COVERAGE001",
            "warning",
            rel,
            f"Coverage matrix has {len(malformed_lines) - 25} additional malformed rows.",
            "Repair all malformed rows before claiming adoption complete.",
        )
    if truncated:
        report.add(
            "COVERAGE001",
            "warning",
            rel,
            f"Coverage matrix exceeds the {MAX_COVERAGE_ROWS:,}-row safety limit.",
            "Split or reduce the matrix before rerunning the gate.",
        )

    identities: list[str] = []
    for row in rows:
        identity = normalize_coverage_identity(row.identity)
        if not identity:
            report.add(
                "COVERAGE001",
                "warning",
                rel,
                f"Coverage row at line {row.line} has no capability identity.",
                "Name the source principle or project capability.",
            )
            continue
        identities.append(identity)
        status, _ = parse_coverage_status(row.status_cell)
        if status is None:
            report.add(
                "COVERAGE001",
                "warning",
                rel,
                f"Coverage row at line {row.line} has an unknown, placeholder, or unexplained status.",
                "Start with verified, candidate, blocked, or N/A and add concrete evidence or a reason.",
            )
        elif status in {"candidate", "blocked"}:
            report.add(
                "COVERAGE002",
                "warning",
                rel,
                f"Coverage row at line {row.line} remains {status}; adoption is incomplete.",
                "Exercise and mark it verified, or use N/A only with a genuine inapplicability reason.",
            )

    counts = Counter(identities)
    for identity, count in sorted(counts.items()):
        if count > 1:
            report.add(
                "COVERAGE003",
                "warning",
                rel,
                f"Coverage capability appears {count} times: {identity}.",
                "Keep one authoritative status and evidence row per capability.",
            )
    if require_canonical_rows:
        try:
            template_text = read_text_safe(SKILL_ROOT, TEMPLATE_ROOT / "docs/agent-harness/coverage-matrix.md")
        except (OSError, SafeRefusal) as exc:
            report.add(
                "COVERAGE001",
                "warning",
                rel,
                f"Bundled canonical coverage inventory could not be read: {exc}",
                "Repair the skill package before claiming canonical-profile adoption.",
            )
            return
        required_rows, _, _, _ = coverage_table_rows(template_text)
        required = {
            normalize_coverage_identity(row.identity)
            for row in required_rows
            if normalize_coverage_identity(row.identity)
        }
        for identity in sorted(required - set(counts)):
            report.add(
                "COVERAGE003",
                "warning",
                rel,
                f"Canonical harness capability is missing: {identity}.",
                "Restore the capability row and record its repository-specific status and evidence.",
            )


def parse_certification_instant(value: object) -> datetime | None:
    if (
        not isinstance(value, str)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value) is None
    ):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def substantive_certification_string(value: object, minimum: int = 8) -> bool:
    return (
        isinstance(value, str)
        and substantive_length(value) >= minimum
        and not has_unresolved_marker(value)
        and not contains_raw_html_markup(value)
    )


def certification_json_object(
    root: Path,
    path: Path,
) -> tuple[dict[str, object] | None, str | None]:
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        payload = json.loads(
            read_text_safe(root, path),
            object_pairs_hook=unique_object,
        )
    except (ValueError, OSError, SafeRefusal) as exc:
        return None, f"could not be read as safe JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "must be a JSON object"
    return payload, None


def certification_evidence_target(
    root: Path,
    evidence_root: Path,
    raw_path: object,
) -> tuple[Path | None, str | None]:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, "evidence path must be a non-empty repository-relative string"
    try:
        target = safe_target(root, raw_path)
    except SafeRefusal as exc:
        return None, str(exc)
    try:
        target.relative_to(evidence_root)
    except ValueError:
        return None, "evidence path is outside the declared evidence_root"
    if not target.is_file() or target.is_symlink():
        return None, "evidence path is not a regular repository file"
    return target, None


def evidence_record_issue(
    root: Path,
    path: Path,
    *,
    expected_capability: str,
    expected_status: str,
    expected_commit: str,
    now: datetime,
    not_after: datetime,
    max_age_hours: int,
    required_environment: str | None = None,
    expected_command: str | None = None,
) -> str | None:
    payload, issue = certification_json_object(root, path)
    if issue is not None or payload is None:
        return issue
    required_keys = {
        "schema_version",
        "repository_commit",
        "capabilities",
        "environment",
        "command",
        "exit_code",
        "observed_at",
        "result",
        "artifacts",
    }
    if set(payload) != required_keys:
        return "evidence record keys do not exactly match the v1 schema"
    if payload.get("schema_version") != 1:
        return "evidence record schema_version is not 1"
    commit = payload.get("repository_commit")
    if not isinstance(commit, str) or commit.casefold() != expected_commit.casefold():
        return "evidence record is not bound to the certified commit"
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        return "evidence record capabilities must be a non-empty array"
    normalized_capabilities = {
        normalize_coverage_identity(value)
        for value in capabilities
        if isinstance(value, str)
    }
    if normalize_coverage_identity(expected_capability) not in normalized_capabilities:
        return "evidence record does not name the covered capability"
    environment = payload.get("environment")
    if not substantive_certification_string(environment, 2):
        return "evidence record environment is missing or non-substantive"
    if (
        required_environment is not None
        and isinstance(environment, str)
        and environment.casefold() != required_environment.casefold()
    ):
        return f"evidence record environment is not {required_environment}"
    command = payload.get("command")
    if not substantive_certification_string(command):
        return "evidence record command or review procedure is missing"
    if expected_command is not None and command != expected_command:
        return "evidence record command does not match the certification manifest"
    observed_at = parse_certification_instant(payload.get("observed_at"))
    if observed_at is None:
        return "evidence record observed_at is not a UTC RFC3339 instant"
    age_seconds = (now - observed_at).total_seconds()
    if age_seconds < 0:
        return "evidence record observed_at is in the future"
    if observed_at > not_after:
        return "evidence record was observed after the certificate was issued"
    if age_seconds > max_age_hours * 3600:
        return "evidence record is older than the certification freshness window"
    result = payload.get("result")
    exit_code = payload.get("exit_code")
    expected_result = "passed" if expected_status == "verified" else "not-applicable"
    if result != expected_result:
        return f"evidence record result must be {expected_result}"
    if expected_status == "verified" and exit_code != 0:
        return "verified evidence must record exit_code 0"
    if expected_status == "n/a" and exit_code is not None:
        return "not-applicable evidence must record a null exit_code"
    artifacts = payload.get("artifacts")
    if (
        not isinstance(artifacts, list)
        or not artifacts
        or not all(substantive_certification_string(item) for item in artifacts)
    ):
        return "evidence record artifacts must contain substantive immutable IDs, paths, or URLs"
    return None


def linked_certification_evidence(
    root: Path,
    coverage_path: Path,
    evidence_root: Path,
    row: CoverageRow,
    *,
    status: str,
    expected_commit: str,
    now: datetime,
    not_after: datetime,
    max_age_hours: int,
    required_environment: str | None = None,
) -> tuple[Path | None, list[str]]:
    issues: list[str] = []
    for destination in markdown_navigation_destinations(row.status_cell):
        resolved, resolution_issue = resolve_markdown_link(root, coverage_path, destination)
        if resolution_issue is not None or resolved is None:
            issues.append(resolution_issue or "link is not repository-local")
            continue
        try:
            relative = resolved.relative_to(root)
            target = safe_target(root, relative.as_posix())
            target.relative_to(evidence_root)
        except (ValueError, SafeRefusal) as exc:
            issues.append(str(exc) or "link is outside evidence_root")
            continue
        if not target.is_file() or target.is_symlink():
            issues.append("linked evidence is not a regular repository file")
            continue
        issue = evidence_record_issue(
            root,
            target,
            expected_capability=row.identity,
            expected_status=status,
            expected_commit=expected_commit,
            now=now,
            not_after=not_after,
            max_age_hours=max_age_hours,
            required_environment=required_environment,
        )
        if issue is None:
            return target, issues
        issues.append(issue)
    if not issues:
        issues.append("status cell has no repository-local evidence link")
    return None, issues


def validate_named_certification_evidence(
    report: Report,
    root: Path,
    evidence_root: Path,
    raw_path: object,
    *,
    label: str,
    capability: str,
    expected_commit: str,
    now: datetime,
    not_after: datetime,
    max_age_hours: int,
    required_environment: str | None = None,
    expected_command: str | None = None,
) -> None:
    target, issue = certification_evidence_target(root, evidence_root, raw_path)
    if issue is None and target is not None:
        issue = evidence_record_issue(
            root,
            target,
            expected_capability=capability,
            expected_status="verified",
            expected_commit=expected_commit,
            now=now,
            not_after=not_after,
            max_age_hours=max_age_hours,
            required_environment=required_environment,
            expected_command=expected_command,
        )
    if issue is not None:
        report.add(
            "CERT008",
            "error",
            str(raw_path) if isinstance(raw_path, str) else CERTIFICATION_REL,
            f"{label} evidence is invalid: {issue}.",
            "Record a fresh v1 evidence JSON file inside evidence_root and bind it to the certified commit.",
        )


def validate_certification(
    report: Report,
    root: Path,
    authorities: dict[str, str],
    profile: str,
    expected_commit: str,
    *,
    now: datetime | None = None,
) -> None:
    root = resolve_safe_directory(root)
    now = now or datetime.now(timezone.utc)
    certification_path = safe_target(root, authorities["certification"])
    rel = relative_display(root, certification_path)
    if not certification_path.is_file() or certification_path.is_symlink():
        report.add(
            "CERT001",
            "error",
            rel,
            "Production certification manifest is missing or unsafe.",
            "Create and tailor the configured v1 certification manifest before making a production-ready claim.",
        )
        return
    payload, issue = certification_json_object(root, certification_path)
    if issue is not None or payload is None:
        report.add(
            "CERT001",
            "error",
            rel,
            f"Production certification manifest {issue}.",
            "Restore a regular UTF-8 JSON v1 manifest.",
        )
        return
    required_keys = {
        "schema_version",
        "claim",
        "profile",
        "repository_commit",
        "environment",
        "issued_at",
        "expires_at",
        "coverage_sha256",
        "evidence_root",
        "project_native_gate",
        "maintenance",
        "production_authority",
    }
    if set(payload) != required_keys or payload.get("schema_version") != 1:
        report.add(
            "CERT002",
            "error",
            rel,
            "Certification manifest does not exactly match the v1 top-level schema.",
            "Keep every required v1 field once and remove unknown top-level fields.",
        )
        return
    if payload.get("claim") != "production-ready":
        report.add(
            "CERT003",
            "error",
            rel,
            "Certification claim is not production-ready.",
            "Use candidate-only until every certification gate has fresh evidence.",
        )
    if payload.get("profile") != profile:
        report.add(
            "CERT003",
            "error",
            rel,
            "Certification profile does not match the invoked profile.",
            "Run the declared profile or update and re-evidence the manifest deliberately.",
        )
    commit = payload.get("repository_commit")
    if (
        not isinstance(commit, str)
        or re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", commit) is None
        or commit.casefold() != expected_commit.casefold()
    ):
        report.add(
            "CERT004",
            "error",
            rel,
            "Certification is not bound to the trusted current commit assertion.",
            "Pass the trusted CI commit to --commit and regenerate all evidence for that exact revision.",
        )
        return
    if payload.get("environment") != "production":
        report.add(
            "CERT003",
            "error",
            rel,
            "A production-ready certificate must target the production environment.",
            "Keep local or staging evidence scoped to its literal label; certify production separately.",
        )
    issued_at = parse_certification_instant(payload.get("issued_at"))
    expires_at = parse_certification_instant(payload.get("expires_at"))
    if (
        issued_at is None
        or expires_at is None
        or issued_at > now
        or expires_at <= now
        or expires_at <= issued_at
    ):
        report.add(
            "CERT005",
            "error",
            rel,
            "Certification timestamps are invalid, future-issued, or expired.",
            "Use UTC RFC3339 instants and issue a fresh bounded certificate after rerunning evidence.",
        )

    maintenance = payload.get("maintenance")
    maintenance_keys = {"command", "triggers", "max_age_hours", "evidence"}
    max_age_hours = 0
    if not isinstance(maintenance, dict) or set(maintenance) != maintenance_keys:
        report.add(
            "CERT006",
            "error",
            rel,
            "Maintenance contract does not exactly match the v1 schema.",
            "Declare command, pull-request/push/schedule triggers, max_age_hours, and evidence.",
        )
    else:
        raw_age = maintenance.get("max_age_hours")
        if not isinstance(raw_age, int) or isinstance(raw_age, bool) or not 1 <= raw_age <= MAX_CERTIFICATION_AGE_HOURS:
            report.add(
                "CERT006",
                "error",
                rel,
                f"Maintenance max_age_hours must be between 1 and {MAX_CERTIFICATION_AGE_HOURS}.",
                "Choose a bounded freshness window and schedule re-certification within it.",
            )
        else:
            max_age_hours = raw_age
            if issued_at is not None and expires_at is not None and (expires_at - issued_at).total_seconds() > raw_age * 3600:
                report.add(
                    "CERT005",
                    "error",
                    rel,
                    "Certification lifetime exceeds the declared maintenance freshness window.",
                    "Expire the certificate no later than max_age_hours after issuance.",
                )
        triggers = maintenance.get("triggers")
        if not isinstance(triggers, list) or not {"pull_request", "push", "schedule"}.issubset(
            {item for item in triggers if isinstance(item, str)}
        ):
            report.add(
                "CERT006",
                "error",
                rel,
                "Continuous maintenance is not triggered on pull requests, pushes, and a schedule.",
                "Wire the project-native gate to all three triggers so drift invalidates the claim.",
            )
        if not substantive_certification_string(maintenance.get("command")):
            report.add(
                "CERT006",
                "error",
                rel,
                "Maintenance command is missing or unresolved.",
                "Record the exact repository-native convergence or certification command.",
            )

    evidence_root_value = payload.get("evidence_root")
    evidence_root: Path | None = None
    if isinstance(evidence_root_value, str):
        try:
            evidence_root = safe_target(root, evidence_root_value)
        except SafeRefusal:
            evidence_root = None
    if evidence_root is None or not evidence_root.is_dir() or evidence_root.is_symlink():
        report.add(
            "CERT007",
            "error",
            rel,
            "Declared evidence_root is missing, unsafe, or not a repository directory.",
            "Use a regular repository-relative directory containing commit-bound evidence records.",
        )
        return
    if max_age_hours == 0:
        return
    evidence_not_after = issued_at or now

    coverage_path = safe_target(root, authorities["coverage"])
    if not coverage_path.is_file() or coverage_path.is_symlink():
        report.add(
            "CERT007",
            "error",
            relative_display(root, coverage_path),
            "Configured coverage matrix is missing or unsafe.",
            "Restore the complete canonical inventory before certifying production readiness.",
        )
        return
    try:
        coverage_bytes = read_bytes_safe(root, coverage_path)
        coverage_text = coverage_bytes.decode("utf-8")
    except (UnicodeDecodeError, OSError, SafeRefusal) as exc:
        report.add(
            "CERT007",
            "error",
            relative_display(root, coverage_path),
            f"Coverage matrix cannot be bound safely: {exc}.",
            "Restore a regular UTF-8 matrix and rerun certification.",
        )
        return
    digest = payload.get("coverage_sha256")
    actual_digest = hashlib.sha256(coverage_bytes).hexdigest()
    if not isinstance(digest, str) or digest.casefold() != actual_digest:
        report.add(
            "CERT007",
            "error",
            rel,
            "coverage_sha256 does not match the configured coverage matrix.",
            "Rerun every affected capability and bind the certificate to the current matrix digest.",
        )
    rows, _, _, _ = coverage_table_rows(coverage_text)
    production_identity = normalize_coverage_identity(
        "Release, deployment, and production actions require repository-local authority"
    )
    for row in rows:
        status, _ = parse_coverage_status(row.status_cell)
        if status not in {"verified", "n/a"}:
            continue
        identity = normalize_coverage_identity(row.identity)
        if identity == production_identity and status != "verified":
            report.add(
                "CERT009",
                "error",
                relative_display(root, coverage_path),
                "The release/deployment/production authority capability cannot be N/A for a production-ready claim.",
                "Exercise the project-specific authority, rollback, and audit path and mark it verified.",
            )
            continue
        required_environment = "production" if identity == production_identity else None
        evidence, issues = linked_certification_evidence(
            root,
            coverage_path,
            evidence_root,
            row,
            status=status,
            expected_commit=commit,
            now=now,
            not_after=evidence_not_after,
            max_age_hours=max_age_hours,
            required_environment=required_environment,
        )
        if evidence is None:
            report.add(
                "CERT009",
                "error",
                relative_display(root, coverage_path),
                f"Coverage row {row.line} has no valid fresh commit-bound evidence: {'; '.join(issues[:3])}.",
                "Link its status cell to a matching v1 evidence record inside evidence_root.",
            )

    project_gate = payload.get("project_native_gate")
    project_gate_keys = {"command", "evidence"}
    if not isinstance(project_gate, dict) or set(project_gate) != project_gate_keys or not substantive_certification_string(project_gate.get("command")):
        report.add(
            "CERT010",
            "error",
            rel,
            "Project-native gate does not exactly declare a substantive command and evidence path.",
            "Implement a durable repository-native gate; the installed skill path may not be the CI dependency.",
        )
    else:
        validate_named_certification_evidence(
            report,
            root,
            evidence_root,
            project_gate.get("evidence"),
            label="Project-native gate",
            capability=PROJECT_GATE_CAPABILITY,
            expected_commit=commit,
            now=now,
            not_after=evidence_not_after,
            max_age_hours=max_age_hours,
            expected_command=project_gate.get("command"),
        )
    if isinstance(maintenance, dict) and substantive_certification_string(maintenance.get("command")):
        validate_named_certification_evidence(
            report,
            root,
            evidence_root,
            maintenance.get("evidence"),
            label="Continuous maintenance",
            capability=MAINTENANCE_CAPABILITY,
            expected_commit=commit,
            now=now,
            not_after=evidence_not_after,
            max_age_hours=max_age_hours,
            expected_command=maintenance.get("command"),
        )

    authority = payload.get("production_authority")
    authority_keys = {"owner", "approval_evidence", "rollback_evidence"}
    if not isinstance(authority, dict) or set(authority) != authority_keys or not is_substantive_owner(str(authority.get("owner", ""))):
        report.add(
            "CERT011",
            "error",
            rel,
            "Production authority does not exactly declare a substantive owner and approval/rollback evidence.",
            "Name the durable production owner and record both exercised authority and rollback evidence.",
        )
    else:
        validate_named_certification_evidence(
            report,
            root,
            evidence_root,
            authority.get("approval_evidence"),
            label="Production approval",
            capability=PRODUCTION_APPROVAL_CAPABILITY,
            expected_commit=commit,
            now=now,
            not_after=evidence_not_after,
            max_age_hours=max_age_hours,
            required_environment="production",
        )
        validate_named_certification_evidence(
            report,
            root,
            evidence_root,
            authority.get("rollback_evidence"),
            label="Production rollback",
            capability=PRODUCTION_ROLLBACK_CAPABILITY,
            expected_commit=commit,
            now=now,
            not_after=evidence_not_after,
            max_age_hours=max_age_hours,
            required_environment="production",
        )


def certify_repository(root: Path, profile: str, expected_commit: str) -> Report:
    report = audit_repository(root, profile, "certify")
    authorities = load_authorities(root, report)
    validate_certification(report, root, authorities, profile, expected_commit)
    if not any(item.severity in {"error", "warning"} for item in report.findings):
        report.add(
            "CERT000",
            "info",
            authorities["certification"],
            "Production-ready certification is current for the asserted commit and bounded freshness window.",
            "Keep project-native pull-request, push, and scheduled maintenance gates active; any drift requires re-certification.",
        )
    return report.normalized()


def index_has_table(
    text: str,
    heading: str,
    marker: str,
    expected_header: tuple[str, ...],
) -> bool:
    heading_match = re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text)
    marker_at = text.find(marker)
    if heading_match is None or marker_at < heading_match.end():
        return False
    lines = [
        line.rstrip()
        for line in markdown_source_lines(text[heading_match.end() : marker_at])
    ]
    for index in range(len(lines) - 1):
        header = split_markdown_table_row(lines[index])
        separator = split_markdown_table_row(lines[index + 1])
        if header != expected_header or separator is None or len(separator) != len(expected_header):
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in separator):
            return True
    return False


def parse_index_region(
    report: Report,
    root: Path,
    index_path: Path,
    lines: list[str],
    state: str,
) -> list[IndexRow]:
    rel_index = relative_display(root, index_path)
    if len(lines) > MAX_INDEX_ROWS:
        report.add(
            "INDEX007",
            "error",
            rel_index,
            f"The {state} region exceeds the {MAX_INDEX_ROWS:,}-row safety limit.",
            "Archive or split historical registry data before rerunning the checker.",
        )
        lines = lines[:MAX_INDEX_ROWS]
    if lines == ["_None._"] or not lines:
        return []
    if "_None._" in lines:
        report.add(
            "INDEX002",
            "error",
            rel_index,
            f"The {state} region mixes _None._ with plan rows.",
            "Use _None._ only when the region has no rows.",
        )
    expected_columns = 5 if state == "active" else 4
    rows: list[IndexRow] = []
    for line in lines:
        if line == "_None._":
            continue
        cells = split_markdown_table_row(line)
        if cells is None:
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"Malformed {state} index row: {line}",
                "Use the declared Markdown table shape inside the lifecycle markers.",
            )
            continue
        if len(cells) != expected_columns:
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"The {state} row has {len(cells)} columns; expected {expected_columns}.",
                "Restore the exact registry table column count.",
            )
            continue
        link_match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", cells[0])
        if not link_match:
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"The first {state} cell is not one exact Markdown plan link.",
                "Use [Plan title](active-or-completed/slug.md).",
            )
            continue
        title, raw_target = link_match.groups()
        target, error = resolve_markdown_link(root, index_path, raw_target)
        if error or target is None:
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"Unsafe {state} plan link {raw_target!r}: {error or 'not local'}.",
                "Point to a repository-contained lifecycle plan.",
            )
            continue
        expected_parent = (index_path.parent / state).resolve(strict=False)
        if target.parent != expected_parent or target.suffix != ".md":
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"The {state} row points outside its {state}/ directory: {raw_target}",
                f"Point the row to {state}/<slug>.md beside the configured index.",
            )
        date_cell = cells[3] if state == "active" else cells[1]
        if validate_iso_date(date_cell) is None:
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"The {state} row date is not YYYY-MM-DD: {date_cell!r}",
                "Record a valid UTC calendar date.",
            )
        if state == "active" and cells[2] not in {"planning", "implementing", "blocked"}:
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"Invalid active state: {cells[2]!r}",
                "Use planning, implementing, or blocked.",
            )
        if state == "active" and not is_substantive_owner(cells[1]):
            report.add(
                "INDEX002",
                "error",
                rel_index,
                "The active row does not assign a substantive owner.",
                "Name a durable role or team that owns the plan.",
            )
        if state == "active" and not is_substantive_lifecycle_fact(
            cells[4], minimum_alnum=3
        ):
            report.add(
                "INDEX002",
                "error",
                rel_index,
                "The active row does not state a substantive current milestone or blocker.",
                "Describe the current milestone or blocker with a concrete lifecycle fact.",
            )
        if any(
            not visible_markdown_cell(cell) or has_unresolved_marker(cell)
            for cell in cells
        ):
            report.add(
                "INDEX002",
                "error",
                rel_index,
                f"The {state} row contains an empty or template-only cell.",
                "Replace every cell with current lifecycle facts.",
            )
        rows.append(IndexRow(relative_display(root, target), title, cells))
    return rows


def parse_plan_metadata(text: str) -> dict[str, str] | None:
    match = re.match(
        r"\A<!-- harness-plan:v1\r?\n(.*?)\r?\n-->\s*", text, re.DOTALL
    )
    if not match:
        return None
    metadata: dict[str, str] = {}
    allowed = {"id", "status", "created", "updated", "completed", "owner"}
    for line in markdown_source_lines(match.group(1)):
        if ":" not in line:
            return None
        key, value = line.split(":", 1)
        key = key.strip()
        if not key or key not in allowed or key in metadata:
            return None
        metadata[key] = value.strip()
    return metadata


def section_map(
    text: str,
    source_text: str | None = None,
) -> tuple[dict[str, str], list[str]]:
    source = text if source_text is None else source_text
    if len(source) != len(text):
        raise ValueError("Structural and source Markdown must have identical shape")
    matches = list(H2_RE.finditer(text))
    sections: dict[str, str] = {}
    order: list[str] = []
    for index, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[name] = source[start:end].strip()
        order.append(name)
    return sections, order


def substantive_length(text: str) -> int:
    without_comments = transform_html_comments(text, collapse=True)
    without_links = strip_markdown_link_markup(without_comments)
    visible = visible_html_text(without_links)
    without_markup = re.sub(r"[`#*_|>\[\]()]", " ", visible)
    without_markup = commonmark_unescape_entities(markdown_unescape(without_markup))
    return len(re.sub(r"\s+", " ", without_markup).strip())


def lifecycle_path(root: Path, index_path: Path, state: str) -> Path:
    try:
        relative_parent = index_path.parent.resolve(strict=False).relative_to(root.resolve())
    except ValueError as exc:
        raise SafeRefusal("Configured ExecPlan lifecycle escapes the repository") from exc
    return safe_target(root, (relative_parent / state).as_posix())


def plan_path_for_state(root: Path, index_path: Path, state: str, slug: str) -> Path:
    directory = lifecycle_path(root, index_path, state)
    relative = directory.resolve(strict=False).relative_to(root.resolve()) / f"{slug}.md"
    return safe_target(root, relative.as_posix())


def validate_plan_semantics(
    report: Report,
    root: Path,
    plan_path: Path,
    expected_state: str,
    planning_path: Path,
    completion_gate: bool,
    semantic_review: bool,
    simulate_completed_location: bool = False,
) -> None:
    rel = relative_display(root, plan_path)
    try:
        text = read_text_safe(root, plan_path)
    except (OSError, SafeRefusal) as exc:
        report.add(
            "PLAN001",
            "error",
            rel,
            f"Plan could not be read safely: {exc}",
            "Restore a regular UTF-8 plan file.",
        )
        return
    structural_text = mask_markdown_code(mask_explicit_blockquote_lines(text))
    metadata = parse_plan_metadata(text)
    required_keys = {"id", "status", "created", "updated", "completed", "owner"}
    if metadata is None or not required_keys.issubset(metadata):
        report.add(
            "PLAN002",
            "error",
            rel,
            "Plan metadata is missing or malformed.",
            "Use the harness-plan:v1 metadata block with every required key.",
        )
        metadata = {}
    else:
        if metadata["status"] != expected_state:
            report.add(
                "PLAN002",
                "error",
                rel,
                f"Metadata status {metadata['status']!r} does not match {expected_state!r}.",
                "Make lifecycle location and metadata agree.",
            )
        expected_id = plan_path.stem
        if metadata["id"] != expected_id or not PLAN_SLUG_RE.fullmatch(metadata["id"]):
            report.add(
                "PLAN002",
                "error",
                rel,
                "Plan id is unsafe or does not match the filename.",
                "Use the same lowercase hyphenated slug in metadata and filename.",
            )
        created = validate_iso_date(metadata["created"])
        updated = validate_iso_date(metadata["updated"])
        completed = validate_iso_date(metadata["completed"]) if metadata["completed"] else None
        invalid_dates = created is None or updated is None
        if expected_state == "active" and metadata["completed"]:
            invalid_dates = True
        if expected_state == "completed" and completed is None:
            invalid_dates = True
        if not invalid_dates and created and updated and created > updated:
            invalid_dates = True
        if not invalid_dates and created and updated and completed:
            if created > completed or completed > updated:
                invalid_dates = True
        if invalid_dates:
            report.add(
                "PLAN002",
                "error",
                rel,
                "Plan lifecycle dates are invalid or out of order.",
                "Use YYYY-MM-DD with created <= completed <= updated; active plans leave completed blank.",
            )
        if not is_substantive_owner(metadata["owner"]):
            report.add(
                "PLAN002",
                "error" if completion_gate else "warning",
                rel,
                "Plan owner is not assigned.",
                "Name a durable role or team before completion.",
            )

    h1_matches = list(H1_RE.finditer(structural_text))
    first_h2 = H2_RE.search(structural_text)
    if (
        len(h1_matches) != 1
        or (first_h2 is not None and h1_matches[0].start() > first_h2.start())
    ):
        report.add(
            "PLAN003",
            "error",
            rel,
            "Plan must have exactly one H1 title before every H2 section.",
            "Keep one short action-oriented H1 before the strict section sequence.",
        )
    elif (
        substantive_length(h1_matches[0].group(1)) < 3
        or has_unresolved_marker(h1_matches[0].group(1))
    ):
        report.add(
            "PLAN003",
            "error",
            rel,
            "Plan H1 has no durable rendered title.",
            "Use one short action-oriented title with repository-specific text.",
        )
    sections, order = section_map(structural_text, text)
    missing = [heading for heading in REQUIRED_PLAN_HEADINGS if heading not in sections]
    if missing:
        report.add(
            "PLAN003",
            "error",
            rel,
            f"Plan is missing required local sections: {', '.join(missing)}.",
            "Use the repository's selected plan template or intentionally migrate its schema.",
        )
    if order != list(REQUIRED_PLAN_HEADINGS):
        report.add(
            "PLAN003",
            "error",
            rel,
            "Plan H2 sections are extra, out of order, or duplicated.",
            "Use exactly the thirteen ordered H2 sections in the local strict schema; use H3 for subdivisions.",
        )
    container_source = mask_explicit_blockquote_lines(text)
    container_source = normalize_list_container_indentation(container_source)
    container_source = mask_explicit_blockquote_lines(container_source)
    container_structural = mask_markdown_code(container_source)
    container_h1: list[str] = []
    container_h2: list[str] = []
    for line in markdown_source_lines(container_structural):
        content, _ = quoted_container_content(line)
        h1 = re.fullmatch(r" {0,3}#\s+(.+?)\s*", content)
        h2 = re.fullmatch(r" {0,3}##\s+(.+?)\s*", content)
        if h1:
            container_h1.append(h1.group(1).strip())
        if h2:
            container_h2.append(h2.group(1).strip())
    root_h1 = [match.group(1).strip() for match in h1_matches]
    container_lines = markdown_source_lines(container_structural)
    has_setext_heading = any(
        re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", container_lines[index])
        and not is_markdown_blank_line(container_lines[index - 1])
        for index in range(1, len(container_lines))
    )
    if container_h1 != root_h1 or container_h2 != order or has_setext_heading:
        report.add(
            "PLAN003",
            "error",
            rel,
            "Plan contains H1/H2 structure nested in a list or indented away from the strict root schema.",
            "Keep the single title and thirteen managed H2 sections at column zero; use H3 or prose inside lists.",
        )

    structural_lines = re.split(r"\r\n|\n|\r", structural_text)
    source_lines = re.split(r"\r\n|\n|\r", text)
    missing_heading_blank = any(
        re.match(r"^ {0,3}#{1,6}(?:[ \t]+|$)", line)
        and (
            index + 1 >= len(source_lines)
            or not is_markdown_blank_line(source_lines[index + 1])
        )
        for index, line in enumerate(structural_lines)
    )
    if missing_heading_blank:
        report.add(
            "PLAN003",
            "error",
            rel,
            "A live plan heading is not followed by one blank line.",
            "Leave one blank line after every heading (two newline characters; CRLF is accepted).",
        )

    progress = sections.get("Progress", "")
    checkboxes = markdown_task_items(progress)
    if not checkboxes:
        report.add(
            "PLAN004",
            "error",
            rel,
            "Progress has no granular checkbox item.",
            "Add at least one independently verifiable progress item.",
        )
    for marker, body in checkboxes:
        timestamp = TIMESTAMP_PREFIX_RE.fullmatch(body) if marker in {"x", "X"} else None
        if marker in {"x", "X"} and (
            timestamp is None
            or not valid_utc_timestamp(timestamp.group(1))
            or substantive_length(timestamp.group(2)) < 8
            or has_unresolved_marker(timestamp.group(2))
        ):
            report.add(
                "PLAN004",
                "error" if completion_gate else "warning",
                rel,
                "A completed Progress item lacks a valid timestamp or substantive rendered task description.",
                "Start checked items with (YYYY-MM-DD HH:MMZ) and name the observed work.",
            )
        elif marker == " " and (
            substantive_length(body) < 8 or has_unresolved_marker(body)
        ):
            report.add(
                "PLAN004",
                "error" if completion_gate else "warning",
                rel,
                "An unchecked Progress item has no substantive rendered task description.",
                "Name the remaining independently verifiable work.",
            )
    if completion_gate and any(marker == " " for marker, _ in checkboxes):
        report.add(
            "PLAN005",
            "error",
            rel,
            "Completion gate found unchecked Progress work, including nested work.",
            "Finish it or record it as explicit remaining debt before completion.",
        )
    outside_progress_parts: list[str] = []
    outside_cursor = 0
    section_matches = list(H2_RE.finditer(structural_text))
    for index, match in enumerate(section_matches):
        if match.group(1).strip() != "Progress":
            continue
        section_end = (
            section_matches[index + 1].start()
            if index + 1 < len(section_matches)
            else len(structural_text)
        )
        outside_progress_parts.append(text[outside_cursor : match.start()])
        outside_progress_parts.append(
            mask_same_shape(text[match.start() : section_end])
        )
        outside_cursor = section_end
    outside_progress_parts.append(text[outside_cursor:])
    outside_progress = "".join(outside_progress_parts)
    if markdown_task_items(outside_progress):
        report.add(
            "PLAN006",
            "error",
            rel,
            "Checklist syntax appears outside Progress.",
            "Keep granular checkboxes only in Progress and use prose for milestones.",
        )

    resolved_policy = False
    for raw in markdown_navigation_destinations(text):
        target, error = resolve_markdown_link(root, plan_path, raw)
        if error is None and target == planning_path.resolve(strict=False):
            resolved_policy = True
            break
    if not resolved_policy:
        report.add(
            "PLAN007",
            "error",
            rel,
            "Plan does not contain a resolving link to the configured planning authority.",
            f"Link directly to {relative_display(root, planning_path)}.",
        )

    placeholder_source = rendered_placeholder_source(text)
    has_template_phrase = any(
        phrase.casefold() in placeholder_source.casefold() for phrase in TEMPLATE_PHRASES
    )
    if has_unresolved_marker(text) or has_template_phrase:
        report.add(
            "PLAN008",
            "error" if completion_gate else "warning",
            rel,
            "Plan contains unresolved template text.",
            "Replace placeholders with current repository facts and observed evidence.",
        )
    if completion_gate:
        for heading, minimum in (
            ("Surprises & Discoveries", 60),
            ("Decision Log", 80),
            ("Outcomes & Retrospective", 100),
            ("Validation and Acceptance", 100),
            ("Idempotence and Recovery", 60),
        ):
            if substantive_length(sections.get(heading, "")) < minimum:
                report.add(
                    "PLAN009",
                    "error",
                    rel,
                    f"{heading} lacks substantive completion evidence.",
                    "Record observed outcomes, exact scoped evidence, remaining gaps, and recovery facts.",
                )
        revision = sections.get("Revision History", "")
        if not revision_history_is_structured(revision):
            report.add(
                "PLAN010",
                "error",
                rel,
                "Revision History contains no entries or at least one malformed entry.",
                "Make every revision a list item with a valid UTC timestamp, Change:, and Reason:.",
            )
        if not semantic_review_attestation_is_valid(revision):
            report.add(
                "PLAN016",
                "error",
                rel,
                "Completion has no valid persistent semantic-review attestation.",
                "Add an indented Revision History continuation using Semantic-Review: reviewer=<role-or-team>; reviewed-at=<YYYY-MM-DD HH:MMZ>; evidence=<substantive observed review evidence>.",
            )
        if not semantic_review:
            report.add(
                "PLAN013",
                "error",
                rel,
                "Semantic completion review was not asserted.",
                "Review self-containment, milestones, observable behavior, recovery, and evidence; then pass --semantic-review.",
            )

    anchor_cache: dict[Path, tuple[set[str] | None, str | None]] = {}
    check_text_links(
        report,
        root,
        plan_path,
        text,
        finding_id="PLAN015",
        anchor_cache=anchor_cache,
    )
    if simulate_completed_location:
        destination = plan_path.parent.parent / "completed" / plan_path.name
        check_text_links(
            report,
            root,
            destination,
            text,
            finding_id="PLAN014",
            virtual_exists=(destination,),
            virtual_missing=(plan_path,),
            anchor_cache=anchor_cache,
        )


def validate_index(
    report: Report,
    root: Path,
    index_path: Path,
    planning_path: Path,
    *,
    required: bool = False,
) -> None:
    rel_index = relative_display(root, index_path)
    if not index_path.exists() or not index_path.is_file():
        if required:
            report.add(
                "INDEX001",
                "error",
                rel_index,
                "The configured ExecPlan index is missing or not a regular file.",
                "Restore the configured index before validating lifecycle membership.",
            )
        return
    try:
        text = read_text_safe(root, index_path)
    except (OSError, SafeRefusal) as exc:
        report.add(
            "INDEX001",
            "error",
            rel_index,
            f"ExecPlan index could not be read safely: {exc}",
            "Restore a regular UTF-8 index file.",
        )
        return
    structural_index = mask_index_markdown(text)
    active_lines = region_lines(structural_index, ACTIVE_START, ACTIVE_END)
    completed_lines = region_lines(structural_index, COMPLETED_START, COMPLETED_END)
    if active_lines is None or completed_lines is None:
        report.add(
            "INDEX001",
            "error",
            rel_index,
            "ExecPlan index markers are missing, duplicated, or reversed.",
            "Restore exactly one ordered marker pair for Active and Completed regions.",
        )
        return
    h1_titles = [match.group(1).strip() for match in H1_RE.finditer(structural_index)]
    heading_matches = list(H2_RE.finditer(structural_index))
    headings = [match.group(1).strip() for match in heading_matches]
    active_heading_at = next(
        (match.start() for match in heading_matches if match.group(1).strip() == "Active"),
        -1,
    )
    completed_heading_at = next(
        (
            match.start()
            for match in heading_matches
            if match.group(1).strip() == "Completed"
        ),
        -1,
    )
    structure_valid = (
        h1_titles == ["ExecPlan Registry"]
        and headings.count("Active") == 1
        and headings.count("Completed") == 1
        and headings.index("Active") < headings.index("Completed")
        and active_heading_at
        < structural_index.index(ACTIVE_START)
        < structural_index.index(ACTIVE_END)
        < completed_heading_at
        < structural_index.index(COMPLETED_START)
        < structural_index.index(COMPLETED_END)
        and index_has_table(
            structural_index,
            "Active",
            ACTIVE_START,
            ("Plan", "Owner", "State", "Updated (UTC)", "Current milestone or blocker"),
        )
        and index_has_table(
            structural_index,
            "Completed",
            COMPLETED_START,
            ("Plan", "Completed (UTC)", "Outcome", "Verification"),
        )
    )
    if not structure_valid:
        report.add(
            "INDEX001",
            "error",
            rel_index,
            "ExecPlan index headings or lifecycle table headers are missing or malformed.",
            "Restore the canonical H1, Active/Completed H2 headings, and declared tables.",
        )
    active_rows = parse_index_region(report, root, index_path, active_lines, "active")
    completed_rows = parse_index_region(
        report, root, index_path, completed_lines, "completed"
    )
    all_targets = [row.target for row in active_rows + completed_rows]
    duplicates = sorted(
        target for target, count in Counter(all_targets).items() if count > 1
    )
    for target in duplicates:
        report.add(
            "INDEX003",
            "error",
            rel_index,
            f"Plan is indexed more than once or in both lifecycle regions: {target}",
            "Keep exactly one state-appropriate row per plan.",
        )

    row_identity_states: dict[str, set[str]] = {}
    for state, rows in (("active", active_rows), ("completed", completed_rows)):
        for row in rows:
            row_identity_states.setdefault(Path(row.target).stem, set()).add(state)
    for identity, states in sorted(row_identity_states.items()):
        if len(states) > 1:
            report.add(
                "INDEX003",
                "error",
                rel_index,
                f"Plan id {identity!r} is indexed in both active and completed states.",
                "Keep one lifecycle state and one registry row for each plan id.",
            )

    row_sets = {
        "active": {row.target for row in active_rows},
        "completed": {row.target for row in completed_rows},
    }

    for state, rows in (("active", active_rows), ("completed", completed_rows)):
        for row in rows:
            plan_path = root / row.target
            if not plan_path.is_file() or plan_path.is_symlink():
                continue
            try:
                plan_text = read_text_safe(root, plan_path)
            except (OSError, SafeRefusal):
                continue
            metadata = parse_plan_metadata(plan_text) or {}
            title_match = H1_RE.search(mask_markdown_code(plan_text))
            title = title_match.group(1).strip() if title_match else ""
            mismatches: list[str] = []
            if row.title != title:
                mismatches.append("title")
            if state == "active":
                if row.cells[1] != metadata.get("owner"):
                    mismatches.append("owner")
                if row.cells[3] != metadata.get("updated"):
                    mismatches.append("updated date")
            elif row.cells[1] != metadata.get("completed"):
                mismatches.append("completed date")
            if mismatches:
                report.add(
                    "INDEX006",
                    "error",
                    rel_index,
                    f"Registry row disagrees with {row.target}: {', '.join(mismatches)}.",
                    "Synchronize the navigational row with the plan title and lifecycle metadata.",
                )
    file_identity_states: dict[str, set[str]] = {}
    for state in ("active", "completed"):
        try:
            directory = lifecycle_path(root, index_path, state)
        except (SafeRefusal, ValueError) as exc:
            report.add(
                "INDEX004",
                "error",
                rel_index,
                f"The configured {state} lifecycle path is unsafe: {exc}",
                "Use a regular repository-contained directory beside the configured index.",
            )
            continue
        file_targets: set[str] = set()
        if not directory.exists() or not directory.is_dir() or directory.is_symlink():
            report.add(
                "INDEX004",
                "error",
                relative_display(root, directory),
                f"The {state} lifecycle path is missing or not a regular directory.",
                "Restore a non-symlink directory beside the configured index.",
            )
            continue
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            report.add(
                "INDEX004",
                "error",
                relative_display(root, directory),
                f"The {state} lifecycle directory could not be enumerated: {exc}.",
                "Restore read permission before treating the lifecycle as empty or complete.",
            )
            continue
        for entry in entries:
            if entry.name == ".gitkeep":
                continue
            path = directory / entry.name
            try:
                regular = entry.is_file(follow_symlinks=False)
                nested_directory = entry.is_dir(follow_symlinks=False)
            except OSError:
                regular = False
                nested_directory = False
            if entry.is_symlink() or nested_directory:
                report.add(
                    "INDEX004",
                    "error",
                    relative_display(root, path),
                    "Lifecycle directories may contain only direct regular lowercase .md plans.",
                    "Remove nested or symlinked entries and keep one direct plan file per lifecycle item.",
                )
                continue
            suffix = path.suffix
            if suffix.casefold() in {".md", ".markdown"} and suffix != ".md":
                report.add(
                    "INDEX004",
                    "error",
                    relative_display(root, path),
                    "Lifecycle plan filenames must use the exact lowercase .md extension.",
                    "Rename the plan to <lowercase-hyphenated-slug>.md and index that exact path.",
                )
                continue
            if suffix != ".md":
                continue
            if not regular:
                report.add(
                    "INDEX004",
                    "error",
                    relative_display(root, path),
                    "Lifecycle entries must be regular Markdown files.",
                    "Replace special-file entries with repository files.",
                )
                continue
            file_targets.add(relative_display(root, path.resolve(strict=False)))
            file_identity_states.setdefault(path.stem, set()).add(state)
            validate_plan_semantics(
                report,
                root,
                path,
                state,
                planning_path,
                completion_gate=state == "completed",
                semantic_review=True,
            )
        for target in sorted(file_targets - row_sets[state]):
            report.add(
                "PLAN011",
                "error",
                target,
                f"{state.capitalize()} plan is missing from the configured index.",
                "Add one exact state-appropriate registry row.",
            )
        for target in sorted(row_sets[state] - file_targets):
            report.add(
                "INDEX005",
                "error",
                rel_index,
                f"Indexed {state} plan does not exist: {target}",
                "Remove the stale row or restore the authoritative plan file.",
            )
    for identity, states in sorted(file_identity_states.items()):
        if len(states) > 1:
            report.add(
                "INDEX003",
                "error",
                rel_index,
                f"Plan id {identity!r} exists in both active and completed directories.",
                "Resolve the lifecycle state and retain only one authoritative plan file.",
            )


def detect_stale_authority_links(
    report: Report,
    root: Path,
    authorities: dict[str, str],
    all_markdown: Iterable[Path],
) -> None:
    changed = {
        key: default
        for key, default in DEFAULT_AUTHORITIES.items()
        if authorities.get(key, default) != default
    }
    if not changed:
        return
    router_paths = set(ROUTER_CANDIDATES)
    router_paths.update(
        rel for rel in authorities.values() if PurePosixPath(rel).suffix.lower() == ".md"
    )
    lifecycle_parents: set[Path] = set()
    try:
        index_path = safe_target(root, authorities["exec_plan_index"])
        lifecycle_parents = {
            lifecycle_path(root, index_path, "active").resolve(strict=False),
            lifecycle_path(root, index_path, "completed").resolve(strict=False),
        }
    except (SafeRefusal, ValueError):
        pass
    for path in all_markdown:
        resolved = path.resolve(strict=False)
        if path.name in {"AGENTS.md", "AGENTS.override.md"} or resolved.parent in lifecycle_parents:
            router_paths.add(relative_display(root, path))
    for rel in sorted(router_paths):
        try:
            path = safe_target(root, rel)
        except SafeRefusal:
            continue
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        try:
            text = read_text_safe(root, path)
        except (OSError, SafeRefusal):
            continue
        for raw in markdown_navigation_destinations(text):
            target, error = resolve_markdown_link(root, path, raw)
            if error or target is None:
                continue
            for key, fallback in changed.items():
                fallback_target = safe_target(root, fallback).resolve(strict=False)
                if target == fallback_target:
                    report.add(
                        "ROUTE001",
                        "error",
                        relative_display(root, path),
                        f"Router still links fallback {fallback!r} although {key!r} maps to {authorities[key]!r}.",
                        "Update the Markdown route to the configured authority; config.json is not a dynamic redirect.",
                    )


def validate_authority_reachability(
    report: Report,
    root: Path,
    authorities: dict[str, str],
    instruction_budget: int,
    instruction_entry: Path,
) -> None:
    """Require authorities to be reachable from Codex's effective root entry point."""
    entry = instruction_entry
    entry_rel = relative_display(root, entry)
    if not entry.is_file():
        if safe_target(root, CONFIG_REL).is_file():
            report.add(
                "ROUTE002",
                "error",
                "AGENTS.md",
                "A harness authority map exists without a root AGENTS.md or AGENTS.override.md router.",
                "Create a concise root AGENTS.md that routes every existing configured authority.",
            )
        return
    reachable: set[Path] = {entry.resolve(strict=False)}
    visited: set[Path] = set()
    queue = deque([entry])
    while queue and len(visited) < 5000:
        source = queue.popleft().resolve(strict=False)
        if source in visited:
            continue
        visited.add(source)
        try:
            if source == entry.resolve(strict=False):
                text, _ = read_instruction_prefix(root, source, instruction_budget)
            else:
                text = read_text_safe(root, source)
        except (OSError, SafeRefusal):
            continue
        for raw in markdown_navigation_destinations(text):
            target, error = resolve_markdown_link(root, source, raw)
            if error or target is None:
                continue
            target = target.resolve(strict=False)
            reachable.add(target)
            if target.suffix.lower() == ".md" and target.is_file() and target not in visited:
                queue.append(target)
    if queue:
        report.add(
            "ROUTE003",
            "error",
            entry_rel,
            "Authority routing exceeded the 5,000-document traversal limit.",
            "Reduce cyclic or overly broad documentation routing and keep the entry map concise.",
        )
    for key, rel in sorted(authorities.items()):
        if key == "instructions":
            continue
        try:
            target = safe_target(root, rel).resolve(strict=False)
        except SafeRefusal:
            continue
        if not target.exists() or target in reachable:
            continue
        report.add(
            "ROUTE002",
            "error",
            rel,
            f"Configured authority {key!r} is not reachable from {entry_rel}.",
            f"Add a direct or progressive-disclosure Markdown route from {entry_rel}.",
        )


def validate_full_profile_navigation(report: Report, root: Path) -> None:
    docs_index = safe_target(root, "docs/index.md")
    if not docs_index.is_file():
        return
    try:
        text = read_text_safe(root, docs_index)
    except (OSError, SafeRefusal):
        return
    targets: set[Path] = set()
    for raw in markdown_navigation_destinations(text):
        target, error = resolve_markdown_link(root, docs_index, raw)
        if not error and target is not None:
            targets.add(target.resolve(strict=False))
    for rel in FULL_ONLY_FILES:
        expected = safe_target(root, rel).resolve(strict=False)
        if expected not in targets:
            report.add(
                "ROUTE004",
                "error",
                "docs/index.md",
                f"Full-profile authority is not linked from the documentation map: {rel}.",
                "Merge and tailor assets/templates/fragments/docs-index.full.md into docs/index.md.",
            )


def validate_harness_index_navigation(report: Report, root: Path) -> None:
    """Require the standard harness index to route every operational authority."""
    harness_index = safe_target(root, "docs/agent-harness/index.md")
    if not harness_index.is_file() or harness_index.is_symlink():
        return
    try:
        text = read_text_safe(root, harness_index)
    except (OSError, SafeRefusal):
        return
    targets: set[Path] = set()
    for raw in markdown_navigation_destinations(text):
        target, error = resolve_markdown_link(root, harness_index, raw)
        if error is None and target is not None:
            targets.add(target.resolve(strict=False))
    for rel in HARNESS_INDEX_TARGETS:
        expected = safe_target(root, rel).resolve(strict=False)
        if expected not in targets:
            report.add(
                "ROUTE005",
                "error",
                "docs/agent-harness/index.md",
                f"Agent-harness index does not directly route required authority: {rel}.",
                "Restore a direct task-oriented link from the harness index to the authority.",
            )


def discover_capabilities(
    report: Report,
    root: Path,
    authorities: dict[str, str],
    instruction_entry: Path,
) -> None:
    instructions = instruction_entry
    if instructions.is_file():
        report.add(
            "CAP001",
            "info",
            relative_display(root, instructions),
            "A repository-level agent instruction entry point is discoverable.",
            "Keep it concise and verify that it routes to current authorities.",
        )
    else:
        report.add(
            "CAP001",
            "warning",
            authorities["instructions"],
            "No repository-level agent instruction entry point was found.",
            "Add a concise root AGENTS.md that routes agents to the configured authorities.",
        )

    architecture_candidates: list[Path] = []
    for rel in (authorities["architecture"], "docs/adr", "docs/architecture"):
        try:
            architecture_candidates.append(safe_target(root, rel))
        except SafeRefusal:
            continue
    architecture = next((item for item in architecture_candidates if item.exists()), None)
    if architecture:
        report.add(
            "CAP002",
            "info",
            relative_display(root, architecture),
            "An architecture source of truth or decision collection is discoverable.",
            "Preserve its authority and add only missing navigation or system context.",
        )
    else:
        report.add(
            "CAP002",
            "warning",
            authorities["architecture"],
            "No architecture source or decision collection was discovered.",
            "Add a proportional system map when the repository has meaningful boundaries.",
        )

    planning_candidates: list[Path] = []
    for rel in (authorities["planning"], "PLANS.md", "planning/PLAN_POLICY.md"):
        try:
            planning_candidates.append(safe_target(root, rel))
        except SafeRefusal:
            continue
    planning = next((item for item in planning_candidates if item.is_file()), None)
    if planning:
        report.add(
            "CAP003",
            "info",
            relative_display(root, planning),
            "A planning policy is discoverable.",
            "Use one canonical policy and add a managed lifecycle only when complex work needs it.",
        )
    else:
        report.add(
            "CAP003",
            "info",
            authorities["planning"],
            "No planning authority was discovered.",
            "Create one only when long-running or risky work needs restartable continuity.",
        )

    verification_candidates = (
        "tests",
        "test",
        "spec",
        "package.json",
        "pyproject.toml",
        "Makefile",
        "Cargo.toml",
        "go.mod",
    )
    safe_verification: list[Path] = []
    for rel in verification_candidates:
        try:
            candidate = safe_target(root, rel)
        except SafeRefusal:
            continue
        if candidate.exists():
            safe_verification.append(candidate)
    verification = next(iter(safe_verification), None)
    if verification:
        report.add(
            "CAP004",
            "info",
            relative_display(root, verification),
            "Potential executable verification surfaces are discoverable.",
            "Confirm exact commands and expected signals rather than inferring them from filenames.",
        )
    else:
        report.add(
            "CAP004",
            "warning",
            ".",
            "No obvious executable verification surface was discovered.",
            "Document or add the narrowest deterministic behavior check.",
        )


def audit_repository(root: Path, profile: str, command: str) -> Report:
    root = resolve_safe_directory(root)
    report = Report(command=command, root=str(root))
    authorities = load_authorities(root, report)
    instruction_budget = project_instruction_budget(root, report)
    instruction_fallbacks = (
        project_instruction_fallbacks(root, report) if profile == "adaptive" else ()
    )
    instructions_path = effective_instruction_path(root, instruction_fallbacks)
    if profile == "adaptive":
        discover_capabilities(report, root, authorities, instructions_path)
    else:
        severity = "warning" if command == "audit" else "error"
        for rel in files_for_profile(profile):
            target = safe_target(root, rel)
            if not target.exists() or not target.is_file():
                report.add(
                    "PATH001",
                    severity,
                    rel,
                    f"The selected {profile} profile artifact is missing.",
                    "Standard/full are exact-layout profiles: create and tailor this path, or use adaptive checking with configured equivalents.",
                )
            else:
                try:
                    text = read_text_safe(root, target)
                except (OSError, SafeRefusal) as exc:
                    report.add(
                        "PATH002",
                        "error",
                        rel,
                        f"Managed artifact cannot be read safely: {exc}",
                        "Restore a regular UTF-8 file.",
                    )
                    continue
                if has_scaffold_placeholder(rel, text):
                    report.add(
                        "DOC001",
                        "warning",
                        rel,
                        "Managed artifact still contains scaffold placeholders.",
                        "Replace every scaffold placeholder with repository facts or an explicit N/A reason; retain generic fields only in the plan template.",
                    )
        for rel in MANAGED_DIRS:
            target = safe_target(root, rel)
            if not target.exists() or not target.is_dir() or target.is_symlink():
                report.add(
                    "PATH001",
                    severity,
                    rel,
                    f"The selected {profile} profile lifecycle directory is missing or unsafe.",
                    "Create a regular repository directory or select a smaller profile.",
                )

    override_path = safe_target(root, "AGENTS.override.md")
    if override_path.is_file():
        try:
            override_text = read_text_safe(root, override_path)
        except (OSError, SafeRefusal):
            override_text = ""
        if has_markdown_content(override_text) and has_scaffold_placeholder(
            "AGENTS.override.md", override_text
        ):
            report.add(
                "DOC001",
                "warning",
                "AGENTS.override.md",
                "The effective override still contains scaffold placeholders.",
                "Replace the placeholder with repository-specific routes and constraints.",
            )

    if instructions_path.is_file():
        try:
            instructions_text, instruction_size = read_instruction_prefix(
                root, instructions_path, instruction_budget
            )
            line_count = len(markdown_source_lines(instructions_text))
        except (OSError, SafeRefusal) as exc:
            line_count = 0
            instruction_size = 0
            report.add(
                "DOC003",
                "error",
                relative_display(root, instructions_path),
                f"The effective instruction entry point could not be read safely: {exc}",
                "Restore a regular UTF-8 AGENTS.md or AGENTS.override.md within the repository.",
            )
        if instruction_size > instruction_budget:
            report.add(
                "DOC003",
                "error",
                relative_display(root, instructions_path),
                f"The effective instruction entry point is {instruction_size} bytes and exceeds the conservative {instruction_budget}-byte load budget.",
                "Keep the root entry map within the budget; for a larger or nested-chain budget, record trusted runtime effective-config and instruction-load evidence.",
            )
        if line_count > 200:
            report.add(
                "DOC002",
                "warning",
                relative_display(root, instructions_path),
                f"Instruction entry point is {line_count} lines long.",
                "Keep it as a map and move explanations into linked versioned documents.",
            )

    all_markdown = list(markdown_files(root, report))
    detect_stale_authority_links(report, root, authorities, all_markdown)
    validate_authority_reachability(
        report, root, authorities, instruction_budget, instructions_path
    )
    if profile in {"standard", "full"}:
        validate_harness_index_navigation(report, root)
    if profile == "full":
        validate_full_profile_navigation(report, root)
    explicit_authorities = configured_authority_keys(root)
    if profile in {"standard", "full"} or "exec_plan_index" in explicit_authorities:
        index_path = safe_target(root, authorities["exec_plan_index"])
        planning_path = safe_target(root, authorities["planning"])
        if not planning_path.is_file() or planning_path.is_symlink():
            report.add(
                "PLAN007",
                "error",
                relative_display(root, planning_path),
                "The strict ExecPlan lifecycle has no regular planning authority.",
                "Create or map the repository's ExecPlan authoring contract before adopting the managed lifecycle.",
            )
        validate_index(report, root, index_path, planning_path)
    if profile in {"standard", "full"}:
        coverage_path = safe_target(root, DEFAULT_AUTHORITIES["coverage"])
        validate_coverage(
            report,
            root,
            coverage_path,
            require_canonical_rows=True,
        )
        if authorities["coverage"] != DEFAULT_AUTHORITIES["coverage"]:
            validate_coverage(
                report,
                root,
                safe_target(root, authorities["coverage"]),
                require_canonical_rows=True,
            )
    elif "coverage" in explicit_authorities:
        validate_coverage(
            report,
            root,
            safe_target(root, authorities["coverage"]),
            require_canonical_rows=True,
        )
    check_links(report, root, all_markdown)
    report.add(
        "MANUAL001",
        "info",
        CONFIG_REL,
        "Semantic quality, runtime observability, architecture correctness, and safe autonomy require project-specific review.",
        "Use the assessment rubric and record real commands and observable evidence.",
    )
    return report.normalized()


def scaffold_preview(root: Path, profile: str) -> Report:
    root = resolve_safe_directory(root)
    report = Report(command="scaffold", root=str(root))
    for rel in files_for_profile(profile):
        source = TEMPLATE_ROOT / rel
        target = safe_target(root, rel)
        if not source.is_file():
            report.add(
                "TEMPLATE001",
                "error",
                rel,
                "Bundled template is missing.",
                "Repair the skill package before applying this profile.",
            )
        if target.exists() and not target.is_file():
            report.add(
                "PATH002",
                "error",
                rel,
                "Target collides with a non-file path.",
                "Resolve the collision before applying a template.",
            )
        report.actions.append(
            {"action": "preserve" if target.is_file() else "would-create", "path": rel}
        )
    for rel in MANAGED_DIRS:
        target = safe_target(root, rel)
        if target.exists() and (not target.is_dir() or target.is_symlink()):
            report.add(
                "PATH002",
                "error",
                rel,
                "Lifecycle target collides with a non-directory or symlink.",
                "Resolve the collision before creating the lifecycle directory.",
            )
        report.actions.append(
            {"action": "preserve-dir" if target.is_dir() else "would-create-dir", "path": rel}
        )
    if profile == "full":
        fragment = SKILL_ROOT / "assets" / "templates" / "fragments" / "docs-index.full.md"
        if not fragment.is_file():
            report.add(
                "TEMPLATE001",
                "error",
                "assets/templates/fragments/docs-index.full.md",
                "The full-profile navigation fragment is missing.",
                "Repair the skill package before applying the full profile.",
            )
        report.actions.append({"action": "would-merge", "path": "docs/index.md"})
    return report.normalized()


def validate_plan_command(
    root: Path,
    slug: str,
    state: str,
    completion: bool,
    semantic_review: bool,
) -> Report:
    root = resolve_safe_directory(root)
    report = Report(command="validate-plan", root=str(root))
    if not PLAN_SLUG_RE.fullmatch(slug):
        raise SafeRefusal("Plan slug must use lowercase ASCII letters, digits, and single hyphens")
    if completion and state != "active":
        raise SafeRefusal("--completion validates an active plan before its move")
    authorities = load_authorities(root, report)
    index_path = safe_target(root, authorities["exec_plan_index"])
    planning_path = safe_target(root, authorities["planning"])
    validate_index(
        report,
        root,
        index_path,
        planning_path,
        required=True,
    )
    plan_path = plan_path_for_state(root, index_path, state, slug)
    if not plan_path.is_file():
        report.add(
            "PLAN001",
            "error",
            relative_display(root, plan_path),
            "Requested lifecycle plan does not exist.",
            "Correct the slug/state or create the plan through the controlled skill workflow.",
        )
        return report.normalized()
    validate_plan_semantics(
        report,
        root,
        plan_path,
        state,
        planning_path,
        completion_gate=completion or state == "completed",
        semantic_review=semantic_review,
        simulate_completed_location=completion,
    )
    return report.normalized()


def print_report(report: Report, output_format: str) -> None:
    report.normalized()
    if output_format == "json":
        print(json.dumps(report.payload(), indent=2, sort_keys=True))
        return
    summary = report.summary()
    print(
        f"{report.command}: {summary['errors']} error(s), "
        f"{summary['warnings']} warning(s), {summary['info']} info item(s)"
    )
    for item in report.findings:
        print(f"[{item.severity}] {item.id} {item.path}: {item.message}")
        print(f"  Remedy: {item.remediation}")
    for action in report.actions:
        print(f"[{action['action']}] {action['path']}")


def add_root_options(
    parser: argparse.ArgumentParser,
    *,
    include_profile: bool = True,
) -> None:
    parser.add_argument("--root", default=".", help="Repository root (default: current directory)")
    parser.add_argument(
        "--allow-non-git",
        action="store_true",
        help="Explicitly allow a non-Git project root",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    if include_profile:
        parser.add_argument(
            "--profile",
            choices=("adaptive", "standard", "full"),
            default="adaptive",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = HarnessArgumentParser(
        description="Read-only audit and validation for a repository agent harness"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Read-only gap report; findings do not fail")
    add_root_options(audit)

    check = subparsers.add_parser("check", help="CI-style read-only deterministic validation")
    add_root_options(check)
    check.add_argument("--warnings-as-errors", action="store_true")

    certify = subparsers.add_parser(
        "certify",
        help="Fail-closed production-readiness validation bound to a trusted commit",
    )
    add_root_options(certify)
    certify.add_argument(
        "--commit",
        required=True,
        help="Trusted current Git commit from the invoking CI or source-control context",
    )

    scaffold = subparsers.add_parser(
        "scaffold", help="Read-only manifest preview for a deliberately selected profile"
    )
    add_root_options(scaffold, include_profile=False)
    scaffold.add_argument("--profile", choices=("standard", "full"), required=True)

    validate = subparsers.add_parser(
        "validate-plan", help="Read-only structural or completion validation for one plan"
    )
    add_root_options(validate, include_profile=False)
    validate.add_argument("--slug", required=True)
    validate.add_argument("--state", choices=("active", "completed"), required=True)
    validate.add_argument("--completion", action="store_true")
    validate.add_argument(
        "--semantic-review",
        action="store_true",
        help="Assert that a human or agent performed the documented semantic review",
    )
    return parser


def raw_option_value(arguments: Sequence[str], name: str, default: str) -> str:
    value = default
    prefix = f"{name}="
    for index, argument in enumerate(arguments):
        if argument.startswith(prefix):
            value = argument[len(prefix) :]
        elif argument == name and index + 1 < len(arguments):
            value = arguments[index + 1]
    return value


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    parser = build_parser()
    try:
        args = parser.parse_args(raw_argv)
    except ArgumentParseFailure as exc:
        output_format = raw_option_value(raw_argv, "--format", "text")
        if output_format not in {"text", "json"}:
            output_format = "text"
        command = raw_argv[0] if raw_argv else "parse"
        root = raw_option_value(raw_argv, "--root", ".")
        report = Report(command=command, root=root)
        report.add(
            "CLI000",
            "error",
            ".",
            f"Invalid command arguments: {exc}",
            "Use --help and provide one supported command with valid option values.",
        )
        print_report(report, output_format)
        return 2
    try:
        root = resolve_root(args.root, args.allow_non_git)
        if args.command == "audit":
            report = audit_repository(root, args.profile, "audit")
            print_report(report, args.format)
            return 0
        if args.command == "check":
            report = audit_repository(root, args.profile, "check")
            print_report(report, args.format)
            summary = report.summary()
            if summary["errors"] or (args.warnings_as_errors and summary["warnings"]):
                return 1
            return 0
        if args.command == "certify":
            report = certify_repository(root, args.profile, args.commit)
            print_report(report, args.format)
            summary = report.summary()
            return 1 if summary["errors"] or summary["warnings"] else 0
        if args.command == "scaffold":
            report = scaffold_preview(root, args.profile)
            print_report(report, args.format)
            return 1 if report.summary()["errors"] else 0
        if args.command == "validate-plan":
            report = validate_plan_command(
                root,
                args.slug,
                args.state,
                args.completion,
                args.semantic_review,
            )
            print_report(report, args.format)
            return 1 if report.summary()["errors"] else 0
        raise SafeRefusal(f"Unknown command: {args.command}")
    except (OSError, SafeRefusal) as exc:
        report = Report(command=args.command, root=str(getattr(args, "root", ".")))
        report.add(
            "CLI001",
            "error",
            ".",
            str(exc),
            "Select a safe repository root and normalized repository-relative paths.",
        )
        print_report(report, getattr(args, "format", "text"))
        return 2


if __name__ == "__main__":
    sys.exit(main())
