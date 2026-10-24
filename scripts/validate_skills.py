#!/usr/bin/env python3
"""Validate the skills in this repository.

Checks, for every skills/**/SKILL.md:

  * frontmatter parses and contains the required fields
  * ``name`` is kebab-case and matches its directory
  * ``description`` is within the length the README allows
  * ``version`` is semver and ``last-reviewed`` is an ISO date that is neither
    in the future nor stale
  * relative links resolve, and heading anchors exist in their targets
  * files referenced in backticks (``references/x.md``) actually exist
  * the skill is listed in ``SKILLS.md``
  * no two skills share a name

It also checks relative links in ``README.md`` and ``SKILLS.md``, because a dead
link in the routing table is as damaging as a dead link in a skill.

Usage:
    python scripts/validate_skills.py [--root PATH]

Requires PyYAML:  python -m pip install pyyaml
Exit codes: 0 clean (warnings allowed), 1 errors found, 2 environment problem.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not content
    print(
        "error: PyYAML is required. Install it with 'python -m pip install pyyaml'.",
        file=sys.stderr,
    )
    sys.exit(2)


FRONTMATTER_DELIM = "---"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# The README asks for "under ~700 characters". Past 1024 a description is
# truncated by some agents, so that is a hard failure rather than a warning.
DESCRIPTION_WARN = 700
DESCRIPTION_MAX = 1024

# The README treats stale adapters as unreliable at 90 days; for prose skills a
# review every six months is enough to catch drift without nagging.
STALE_DAYS = 180

CHECKED_EXTENSIONS = (
    ".md",
    ".py",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".csv",
    ".ts",
    ".js",
)

REQUIRED_FIELDS = ("name", "description")
VERSIONED_FIELDS = ("version", "last-reviewed")

LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HREF_PATTERN = re.compile(r"""(?:href|src)=["']([^"']+)["']""")
BACKTICK_PATTERN = re.compile(r"`([^`\n]+)`")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclasses.dataclass
class Finding:
    level: str  # "error" | "warning"
    path: str
    line: int
    message: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:  # pragma: no cover - exotic content
        raise SystemExit(f"error: {path} is not valid UTF-8: {exc}")


def slugify(heading: str) -> str:
    """Approximate GitHub's heading anchors."""
    text = re.sub(r"<[^>]+>", "", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").replace("*", "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def heading_anchors(text: str) -> set[str]:
    return {slugify(match.group(2)) for match in HEADING_PATTERN.finditer(text)}


def strip_code(text: str) -> str:
    """Blank out fenced blocks and inline code so links inside them are ignored.

    Line count is preserved, so findings keep accurate line numbers.
    """
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            lines.append("")
            continue
        lines.append("" if in_fence else re.sub(r"`[^`]*`", "", line))
    return "\n".join(lines)


def parse_frontmatter(text: str) -> tuple[dict | None, str, int, str | None]:
    """Return (data, body, body_start_line, error)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return None, text, 1, "file must start with a '---' frontmatter block"

    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_DELIM:
            raw = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError as exc:
                detail = str(exc).replace("\n", " ")
                return None, body, index + 2, f"frontmatter is not valid YAML: {detail}"
            if not isinstance(data, dict):
                return None, body, 1, "frontmatter must be a mapping of fields"
            return data, body, index + 2, None

    return None, text, 1, "frontmatter block is never closed with '---'"


def is_external(target: str) -> bool:
    return bool(re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", target, re.IGNORECASE))


def looks_like_path(token: str) -> bool:
    if not token.endswith(CHECKED_EXTENSIONS):
        return False
    if any(ch in token for ch in (" ", "<", ">", "*", "|", "{", "}", "$", "#", '"', "'")):
        return False
    if is_external(token) or token.startswith(("/", "~")):
        return False
    return "/" in token or token in {"SKILL.md", "SKILLS.md", "README.md", "LICENSE"}


def check_links(path: Path, root: Path, findings: list[Finding]) -> None:
    text = read_text(path)
    scan = strip_code(text)
    rel = path.relative_to(root).as_posix()
    anchors = heading_anchors(text)

    for line_no, line in enumerate(scan.splitlines(), start=1):
        targets = [m.group(1) for m in LINK_PATTERN.finditer(line)]
        targets += [m.group(1) for m in HREF_PATTERN.finditer(line)]

        for target in targets:
            if not target or target.startswith("mailto:") or target.startswith("tel:"):
                continue
            if is_external(target):
                continue

            file_part, _, anchor = target.partition("#")

            if not file_part:  # same-file anchor
                if anchor and anchor not in anchors:
                    findings.append(
                        Finding("warning", rel, line_no, f"anchor '#{anchor}' matches no heading")
                    )
                continue

            resolved = (path.parent / file_part).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                findings.append(
                    Finding("error", rel, line_no, f"link '{target}' points outside the repository")
                )
                continue

            if not resolved.exists():
                findings.append(Finding("error", rel, line_no, f"link '{target}' does not exist"))
                continue

            if anchor and resolved.suffix == ".md":
                if anchor not in heading_anchors(read_text(resolved)):
                    findings.append(
                        Finding(
                            "warning",
                            rel,
                            line_no,
                            f"anchor '#{anchor}' matches no heading in {file_part}",
                        )
                    )


def check_referenced_files(
    path: Path, body: str, root: Path, findings: list[Finding]
) -> None:
    rel = path.relative_to(root).as_posix()
    for line_no, line in enumerate(body.splitlines(), start=1):
        for match in BACKTICK_PATTERN.finditer(line):
            token = match.group(1).strip()
            if not looks_like_path(token):
                continue
            if (path.parent / token).exists() or (root / token).exists():
                continue
            findings.append(
                Finding(
                    "error",
                    rel,
                    line_no,
                    f"referenced file '{token}' does not exist",
                )
            )


def validate_skill(
    skill_md: Path, root: Path, findings: list[Finding], today: dt.date
) -> str | None:
    """Validate one skill. Returns its name when the frontmatter yielded one."""
    text = read_text(skill_md)
    rel = skill_md.relative_to(root).as_posix()
    data, body, body_line, error = parse_frontmatter(text)

    if error:
        findings.append(Finding("error", rel, 1, error))
        check_links(skill_md, root, findings)
        return None

    assert data is not None

    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(Finding("error", rel, 1, f"missing required field '{field}'"))

    for field in VERSIONED_FIELDS:
        if field not in data:
            findings.append(Finding("error", rel, 1, f"missing required field '{field}'"))

    name = data.get("name")
    folder = skill_md.parent.name

    if isinstance(name, str) and name.strip():
        if not NAME_PATTERN.match(name):
            findings.append(
                Finding(
                    "error",
                    rel,
                    1,
                    f"name '{name}' must be lowercase kebab-case",
                )
            )
        if name != folder:
            findings.append(
                Finding(
                    "error",
                    rel,
                    1,
                    f"name '{name}' does not match its directory '{folder}'",
                )
            )
        words = len(name.split("-"))
        if words < 2 or words > 4:
            findings.append(
                Finding(
                    "warning",
                    rel,
                    1,
                    f"name '{name}' has {words} words; convention is 2-4",
                )
            )

    description = data.get("description")
    if isinstance(description, str) and description.strip():
        length = len(description.strip())
        if length > DESCRIPTION_MAX:
            findings.append(
                Finding(
                    "error",
                    rel,
                    1,
                    f"description is {length} chars; the limit is {DESCRIPTION_MAX}",
                )
            )
        elif length > DESCRIPTION_WARN:
            findings.append(
                Finding(
                    "warning",
                    rel,
                    1,
                    f"description is {length} chars; keep it under {DESCRIPTION_WARN}",
                )
            )
        if not description.strip().lower().startswith("use when"):
            findings.append(
                Finding(
                    "warning",
                    rel,
                    1,
                    "description should open with 'Use when' so it routes reliably",
                )
            )
    elif isinstance(description, str):
        findings.append(Finding("error", rel, 1, "description is empty"))

    version = data.get("version")
    if version is not None:
        if not isinstance(version, str) or not SEMVER_PATTERN.match(str(version)):
            findings.append(
                Finding("error", rel, 1, f"version '{version}' is not semver (MAJOR.MINOR.PATCH)")
            )

    reviewed = data.get("last-reviewed")
    if reviewed is not None:
        reviewed_str = str(reviewed)
        try:
            reviewed_date = dt.date.fromisoformat(reviewed_str)
        except ValueError:
            findings.append(
                Finding(
                    "error",
                    rel,
                    1,
                    f"last-reviewed '{reviewed_str}' is not an ISO date (YYYY-MM-DD)",
                )
            )
        else:
            if reviewed_date > today:
                findings.append(
                    Finding("error", rel, 1, "last-reviewed is in the future")
                )
            elif (today - reviewed_date).days > STALE_DAYS:
                age = (today - reviewed_date).days
                findings.append(
                    Finding(
                        "warning",
                        rel,
                        1,
                        f"last-reviewed is {age} days old; review it (threshold {STALE_DAYS})",
                    )
                )

    if not body.strip():
        findings.append(Finding("error", rel, body_line, "SKILL.md has no body content"))

    check_links(skill_md, root, findings)
    check_referenced_files(skill_md, body, root, findings)

    return name if isinstance(name, str) and name.strip() else None


def validate(root: Path, today: dt.date) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    skills_dir = root / "skills"

    skill_files = sorted(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []
    # Skip anything vendored into a dependency directory.
    skill_files = [p for p in skill_files if "node_modules" not in p.parts]

    names: dict[str, str] = {}

    for skill_md in skill_files:
        name = validate_skill(skill_md, root, findings, today)
        if name:
            if name in names:
                findings.append(
                    Finding(
                        "error",
                        skill_md.relative_to(root).as_posix(),
                        1,
                        f"name '{name}' is already used by {names[name]}",
                    )
                )
            else:
                names[name] = skill_md.relative_to(root).as_posix()

    # Every skill must be reachable from the routing table.
    index_path = root / "SKILLS.md"
    if skill_files:
        if not index_path.is_file():
            findings.append(Finding("error", "SKILLS.md", 1, "routing index is missing"))
        else:
            index_text = read_text(index_path)
            for skill_md in skill_files:
                rel_link = skill_md.relative_to(root).as_posix()
                if rel_link not in index_text:
                    findings.append(
                        Finding(
                            "error",
                            "SKILLS.md",
                            1,
                            f"{rel_link} is not listed in the skill index",
                        )
                    )

    for doc in ("README.md", "SKILLS.md"):
        doc_path = root / doc
        if doc_path.is_file():
            check_links(doc_path, root, findings)

    return findings, len(skill_files)


def emit(finding: Finding, use_annotations: bool) -> None:
    print(f"{finding.level.upper():7} {finding.path}:{finding.line}  {finding.message}")
    if not use_annotations:
        return
    message = finding.message.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
    print(f"::{finding.level} file={finding.path},line={finding.line}::{message}")


def write_summary(findings: list[Finding], skill_count: int) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]
    lines = [
        "## Skill validation",
        "",
        f"- Skills checked: **{skill_count}**",
        f"- Errors: **{len(errors)}**",
        f"- Warnings: **{len(warnings)}**",
        "",
    ]
    if errors:
        lines += ["| Location | Problem |", "| --- | --- |"]
        lines += [f"| `{f.path}:{f.line}` | {f.message} |" for f in errors[:50]]
        lines.append("")
    if warnings:
        lines += ["<details><summary>Warnings</summary>", ""]
        lines += [f"- `{f.path}:{f.line}` {f.message}" for f in warnings]
        lines += ["", "</details>", ""]
    if not findings:
        lines.append("All checks passed.")
    try:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError:  # pragma: no cover - best effort only
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SKILL.md files.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (default: the parent of this script)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    findings, skill_count = validate(root, dt.date.today())
    annotations = os.environ.get("GITHUB_ACTIONS") == "true"

    print(f"Validating {skill_count} skill(s) under {root}/skills")
    for finding in findings:
        emit(finding, annotations)

    errors = sum(1 for f in findings if f.level == "error")
    warnings = sum(1 for f in findings if f.level == "warning")
    write_summary(findings, skill_count)

    if errors:
        print(f"\n{errors} error(s), {warnings} warning(s).")
        return 1

    print(f"All checks passed ({warnings} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
