"""Regression tests for scripts/validate_skills.py.

Each test builds a throwaway repository in a temporary directory and asserts on
the findings the validator returns, so a rule cannot silently stop firing.

Run with:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate_skills.py"

_spec = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
assert _spec and _spec.loader
vs = importlib.util.module_from_spec(_spec)
# dataclasses resolve annotations through sys.modules, so register it first.
sys.modules[_spec.name] = vs
_spec.loader.exec_module(vs)

# A fixed "today" keeps the date rules deterministic.
TODAY = dt.date(2026, 6, 1)
FRESH = "2026-05-01"

DESCRIPTION = "Use when a business term needs a definition. Produces a proposal."
BODY = "## Procedure\n\n1. Do the thing.\n"


def format_findings(findings: list) -> str:
    if not findings:
        return "no findings"
    return "\n".join(
        f"  {f.level} {f.path}:{f.line} {f.message}" for f in findings
    )


class SkillRepo:
    """A minimal repository layout the validator can run against."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
        return path

    def index(self, relative: str) -> None:
        path = self.root / "SKILLS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else "# Skills\n\n"
        path.write_text(existing + f"- `{relative}` — a skill\n", encoding="utf-8")

    def write_skill(self, folder: str, text: str, *, indexed: bool = True) -> Path:
        relative = f"skills/{folder}/SKILL.md"
        path = self.write(relative, text)
        if indexed:
            self.index(relative)
        return path

    def add_skill(
        self,
        *,
        name: str = "define-term",
        folder: str | None = None,
        description: str = DESCRIPTION,
        version: str | None = "0.1.0",
        reviewed: str | None = FRESH,
        body: str = BODY,
        extra: str = "",
        indexed: bool = True,
    ) -> Path:
        lines = [
            "---",
            f"name: {name}",
            f"description: {json.dumps(description)}",
        ]
        if version is not None:
            lines.append(f"version: {version}")
        if reviewed is not None:
            # Unquoted on purpose: YAML parses this into a date object, which is
            # exactly how contributors write it.
            lines.append(f"last-reviewed: {reviewed}")
        if extra:
            lines.append(extra)
        lines += ["---", "", body]
        return self.write_skill(folder or name, "\n".join(lines), indexed=indexed)

    def findings(self) -> list:
        findings, _ = vs.validate(self.root.resolve(), TODAY)
        return findings


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = SkillRepo(Path(self._tmp.name))

    def assertClean(self, findings: list) -> None:
        self.assertEqual(
            findings, [], f"expected no findings, got:\n{format_findings(findings)}"
        )

    def assertFinding(self, findings: list, level: str, fragment: str) -> None:
        matches = [f for f in findings if f.level == level and fragment in f.message]
        self.assertTrue(
            matches,
            f"expected a {level} containing {fragment!r}, got:\n{format_findings(findings)}",
        )

    def assertOnlyFinding(self, findings: list, level: str, fragment: str) -> None:
        self.assertEqual(
            len(findings),
            1,
            f"expected exactly one finding, got:\n{format_findings(findings)}",
        )
        self.assertFinding(findings, level, fragment)

    def assertNoLevel(self, findings: list, level: str) -> None:
        offenders = [f for f in findings if f.level == level]
        self.assertEqual(
            offenders, [], f"expected no {level}s, got:\n{format_findings(offenders)}"
        )


class TestCleanRepository(ValidatorTestCase):
    def test_minimal_skill_is_clean(self) -> None:
        self.repo.add_skill()
        self.assertClean(self.repo.findings())

    def test_quoted_and_unquoted_dates_both_parse(self) -> None:
        self.repo.add_skill(reviewed=FRESH)
        self.assertClean(self.repo.findings())

    def test_repository_itself_has_no_errors(self) -> None:
        findings, count = vs.validate(REPO_ROOT, dt.date.today())
        self.assertGreaterEqual(count, 1)
        errors = [f for f in findings if f.level == "error"]
        self.assertEqual(errors, [], f"repository has errors:\n{format_findings(errors)}")


class TestFrontmatter(ValidatorTestCase):
    def test_missing_frontmatter_block(self) -> None:
        self.repo.write_skill("define-term", "Just prose, no frontmatter.\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "must start with a '---' frontmatter block"
        )

    def test_unclosed_frontmatter_block(self) -> None:
        self.repo.write_skill("define-term", "---\nname: define-term\nbody\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "frontmatter block is never closed"
        )

    def test_invalid_yaml(self) -> None:
        self.repo.write_skill(
            "define-term", "---\nname: 'unclosed\n---\n\nSome body.\n"
        )
        self.assertOnlyFinding(self.repo.findings(), "error", "not valid YAML")

    def test_frontmatter_must_be_a_mapping(self) -> None:
        self.repo.write_skill("define-term", "---\n- one\n- two\n---\n\nSome body.\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "must be a mapping of fields"
        )

    def test_missing_name(self) -> None:
        self.repo.write_skill(
            "define-term",
            "---\ndescription: Use when defining a term.\nversion: 0.1.0\n"
            f"last-reviewed: {FRESH}\n---\n\n{BODY}",
        )
        self.assertOnlyFinding(
            self.repo.findings(), "error", "missing required field 'name'"
        )

    def test_missing_description(self) -> None:
        self.repo.write_skill(
            "define-term",
            "---\nname: define-term\nversion: 0.1.0\n"
            f"last-reviewed: {FRESH}\n---\n\n{BODY}",
        )
        self.assertOnlyFinding(
            self.repo.findings(), "error", "missing required field 'description'"
        )

    def test_missing_version(self) -> None:
        self.repo.add_skill(version=None)
        self.assertOnlyFinding(
            self.repo.findings(), "error", "missing required field 'version'"
        )

    def test_missing_last_reviewed(self) -> None:
        self.repo.add_skill(reviewed=None)
        self.assertOnlyFinding(
            self.repo.findings(), "error", "missing required field 'last-reviewed'"
        )


class TestNaming(ValidatorTestCase):
    def test_name_must_be_kebab_case(self) -> None:
        self.repo.add_skill(name="Define_Term")
        findings = self.repo.findings()
        self.assertFinding(findings, "error", "must be lowercase kebab-case")

    def test_name_must_match_directory(self) -> None:
        self.repo.add_skill(name="define-business-term", folder="define-term")
        self.assertOnlyFinding(
            self.repo.findings(),
            "error",
            "does not match its directory 'define-term'",
        )

    def test_single_word_name_warns(self) -> None:
        self.repo.add_skill(name="glossary")
        findings = self.repo.findings()
        self.assertOnlyFinding(findings, "warning", "convention is 2-4")

    def test_five_word_name_warns(self) -> None:
        self.repo.add_skill(name="a-b-c-d-e")
        self.assertOnlyFinding(self.repo.findings(), "warning", "convention is 2-4")

    def test_duplicate_names_are_rejected(self) -> None:
        # Nested folders let two skills share a name while matching their folder.
        self.repo.add_skill(folder="group-one/define-term")
        self.repo.add_skill(folder="group-two/define-term")
        self.assertOnlyFinding(self.repo.findings(), "error", "is already used by")


class TestDescription(ValidatorTestCase):
    def test_description_over_the_hard_limit(self) -> None:
        self.repo.add_skill(description="Use when " + "x" * (vs.DESCRIPTION_MAX + 10))
        findings = self.repo.findings()
        self.assertOnlyFinding(findings, "error", "the limit is 1024")

    def test_description_in_the_warning_band(self) -> None:
        description = "Use when " + "y" * (vs.DESCRIPTION_WARN + 20)
        self.repo.add_skill(description=description)
        findings = self.repo.findings()
        self.assertOnlyFinding(findings, "warning", "keep it under 700")
        self.assertNoLevel(findings, "error")

    def test_description_must_open_with_use_when(self) -> None:
        self.repo.add_skill(description="Helps define a business term.")
        self.assertOnlyFinding(
            self.repo.findings(), "warning", "should open with 'Use when'"
        )

    def test_lowercase_use_when_is_accepted(self) -> None:
        self.repo.add_skill(description="use when defining a term. Produces a proposal.")
        self.assertClean(self.repo.findings())

    def test_empty_description(self) -> None:
        self.repo.add_skill(description="   ")
        self.assertFinding(self.repo.findings(), "error", "description is empty")


class TestVersionAndDates(ValidatorTestCase):
    def test_version_must_be_semver(self) -> None:
        self.repo.add_skill(version="0.1")
        self.assertOnlyFinding(self.repo.findings(), "error", "is not semver")

    def test_last_reviewed_must_be_an_iso_date(self) -> None:
        self.repo.add_skill(reviewed="May 2026")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "is not an ISO date"
        )

    def test_last_reviewed_cannot_be_in_the_future(self) -> None:
        self.repo.add_skill(reviewed=(TODAY + dt.timedelta(days=1)).isoformat())
        self.assertOnlyFinding(self.repo.findings(), "error", "is in the future")

    def test_stale_review_warns(self) -> None:
        stale = TODAY - dt.timedelta(days=vs.STALE_DAYS + 1)
        self.repo.add_skill(reviewed=stale.isoformat())
        self.assertOnlyFinding(self.repo.findings(), "warning", "days old")

    def test_review_exactly_at_the_threshold_is_fine(self) -> None:
        boundary = TODAY - dt.timedelta(days=vs.STALE_DAYS)
        self.repo.add_skill(reviewed=boundary.isoformat())
        self.assertClean(self.repo.findings())


class TestBody(ValidatorTestCase):
    def test_empty_body(self) -> None:
        self.repo.add_skill(body="")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "has no body content"
        )


class TestLinks(ValidatorTestCase):
    def test_broken_relative_link(self) -> None:
        self.repo.add_skill(body="See [the rubric](references/rubric.md).\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "link 'references/rubric.md' does not exist"
        )

    def test_valid_relative_link_with_anchor(self) -> None:
        self.repo.write("skills/define-term/references/rubric.md", "## Criteria\n\nText.\n")
        self.repo.add_skill(body="See [the rubric](references/rubric.md#criteria).\n")
        self.assertClean(self.repo.findings())

    def test_missing_anchor_in_same_file(self) -> None:
        self.repo.add_skill(body="## Procedure\n\nSee [step](#no-such-heading).\n")
        self.assertOnlyFinding(
            self.repo.findings(), "warning", "anchor '#no-such-heading' matches no heading"
        )

    def test_missing_anchor_in_another_file(self) -> None:
        self.repo.write("skills/define-term/references/rubric.md", "## Criteria\n\nText.\n")
        self.repo.add_skill(body="See [the rubric](references/rubric.md#other).\n")
        self.assertOnlyFinding(
            self.repo.findings(),
            "warning",
            "matches no heading in references/rubric.md",
        )

    def test_link_escaping_the_repository(self) -> None:
        self.repo.add_skill(body="See [outside](../../../outside.md).\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "points outside the repository"
        )

    def test_external_links_are_ignored(self) -> None:
        self.repo.add_skill(body="See [docs](https://example.com/page.md).\n")
        self.assertClean(self.repo.findings())

    def test_links_in_code_fences_are_ignored(self) -> None:
        self.repo.add_skill(
            body="## Procedure\n\n```markdown\n[missing](references/missing.md)\n```\n"
        )
        self.assertClean(self.repo.findings())

    def test_href_attributes_are_checked(self) -> None:
        self.repo.add_skill(body='<a href="assets/missing.pdf">template</a>\n')
        self.assertOnlyFinding(
            self.repo.findings(), "error", "link 'assets/missing.pdf' does not exist"
        )

    def test_readme_links_are_checked(self) -> None:
        self.repo.add_skill()
        self.repo.write("README.md", "# Readme\n\n[gone](docs/missing.md)\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "link 'docs/missing.md' does not exist"
        )

    def test_skills_index_links_are_checked(self) -> None:
        self.repo.add_skill()
        # Keep the entry the validator requires, and add one dead link.
        self.repo.write(
            "SKILLS.md",
            "# Skills\n\n- `skills/define-term/SKILL.md` — a skill\n\n"
            "[gone](docs/missing.md)\n",
        )
        self.assertOnlyFinding(
            self.repo.findings(), "error", "link 'docs/missing.md' does not exist"
        )


class TestReferencedFiles(ValidatorTestCase):
    def test_missing_backticked_reference(self) -> None:
        self.repo.add_skill(body="Read `references/rubric.md` before drafting.\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "referenced file 'references/rubric.md'"
        )

    def test_existing_backticked_reference(self) -> None:
        self.repo.write("skills/define-term/references/rubric.md", "## Criteria\n")
        self.repo.add_skill(body="Read `references/rubric.md` before drafting.\n")
        self.assertClean(self.repo.findings())

    def test_backticked_reference_resolves_from_the_repository_root(self) -> None:
        self.repo.write("scripts/tool.py", "print('hi')\n")
        self.repo.add_skill(body="Run `scripts/tool.py` to check.\n")
        self.assertClean(self.repo.findings())


class TestIndex(ValidatorTestCase):
    def test_missing_index_file(self) -> None:
        self.repo.add_skill(indexed=False)
        self.assertOnlyFinding(
            self.repo.findings(), "error", "routing index is missing"
        )

    def test_skill_missing_from_the_index(self) -> None:
        self.repo.add_skill(indexed=False)
        self.repo.write("SKILLS.md", "# Skills\n\nNothing here yet.\n")
        self.assertOnlyFinding(
            self.repo.findings(), "error", "is not listed in the skill index"
        )


class TestReporting(ValidatorTestCase):
    def test_annotations_escape_percent(self) -> None:
        finding = vs.Finding("error", "skills/x/SKILL.md", 7, "50% broken")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            vs.emit(finding, use_annotations=True)
        output = buffer.getvalue()
        self.assertIn("::error file=skills/x/SKILL.md,line=7::", output)
        self.assertIn("50%25 broken", output)

    def test_plain_output_has_no_annotations(self) -> None:
        finding = vs.Finding("warning", "skills/x/SKILL.md", 7, "a note")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            vs.emit(finding, use_annotations=False)
        output = buffer.getvalue()
        self.assertIn("WARNING skills/x/SKILL.md:7  a note", output)
        self.assertNotIn("::warning", output)

    def test_job_summary_is_written(self) -> None:
        findings = [
            vs.Finding("error", "SKILLS.md", 1, "bad thing"),
            vs.Finding("warning", "SKILLS.md", 2, "minor thing"),
        ]
        summary = Path(self._tmp.name) / "summary.md"
        with unittest.mock.patch.dict(
            os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}
        ):
            vs.write_summary(findings, 1)
        text = summary.read_text(encoding="utf-8")
        self.assertIn("Skills checked: **1**", text)
        self.assertIn("Errors: **1**", text)
        self.assertIn("Warnings: **1**", text)
        self.assertIn("`SKILLS.md:1`", text)

    def test_job_summary_is_skipped_without_the_variable(self) -> None:
        with unittest.mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GITHUB_STEP_SUMMARY", None)
            vs.write_summary([], 0)  # must not raise


class TestPolicyConstants(unittest.TestCase):
    """Pinned so a threshold change is a deliberate edit here and in the README."""

    def test_documented_thresholds(self) -> None:
        self.assertEqual(vs.DESCRIPTION_WARN, 700)
        self.assertEqual(vs.DESCRIPTION_MAX, 1024)
        self.assertEqual(vs.STALE_DAYS, 180)


class TestCommandLine(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = SkillRepo(Path(self._tmp.name))

    def run_cli(self, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
        base = {k: v for k, v in os.environ.items() if k != "GITHUB_STEP_SUMMARY"}
        base.pop("GITHUB_ACTIONS", None)
        if env:
            base.update(env)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=base,
            timeout=60,
        )

    def test_clean_repository_exits_zero(self) -> None:
        self.repo.add_skill()
        result = self.run_cli("--root", self._tmp.name)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All checks passed", result.stdout)

    def test_errors_exit_one(self) -> None:
        self.repo.add_skill(body="[gone](references/missing.md)\n")
        result = self.run_cli("--root", self._tmp.name)
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not exist", result.stdout)
        self.assertIn("error(s)", result.stdout)

    def test_warnings_do_not_fail_the_build(self) -> None:
        self.repo.add_skill(description="Helps define a business term.")
        result = self.run_cli("--root", self._tmp.name)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("warning(s)", result.stdout)

    def test_missing_root_exits_two(self) -> None:
        result = self.run_cli("--root", str(Path(self._tmp.name) / "nope"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("is not a directory", result.stderr)

    def test_annotations_are_emitted_on_github_actions(self) -> None:
        self.repo.add_skill(body="[gone](references/missing.md)\n")
        result = self.run_cli(
            "--root", self._tmp.name, env={"GITHUB_ACTIONS": "true"}
        )
        self.assertIn(
            "::error file=skills/define-term/SKILL.md,", result.stdout
        )


if __name__ == "__main__":
    unittest.main()
