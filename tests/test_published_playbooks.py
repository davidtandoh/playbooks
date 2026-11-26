from __future__ import annotations

import datetime
import json
import pathlib
import re
import sys
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import playbook_index  # noqa: E402
from playbook_index import (  # noqa: E402
    github_anchor,
    heading_anchors,
    read_front_matter,
)

PUBLISHED_PLAYBOOKS = (
    REPOSITORY_ROOT / "building-ai-agents.md",
    REPOSITORY_ROOT / "building-reliable-agents.md",
    REPOSITORY_ROOT / "contextual-retrieval.md",
    REPOSITORY_ROOT / "testing-in-agentic-engineering.md",
    REPOSITORY_ROOT / "ci-for-agentic-engineering.md",
)
TAXONOMY_DRAFTS = {
    REPOSITORY_ROOT / "drafts" / "20261123-persistent-agents.md": (
        "Agent systems",
        ["architecture", "orchestration", "memory", "reliability", "governance", "evals"],
    ),
}
AGENTIC_SRE_DIRECTORY = REPOSITORY_ROOT / "practices" / "agentic-sre"
AGENTIC_SRE_INDEX = AGENTIC_SRE_DIRECTORY / "README.md"
AGENTIC_SRE_PRACTICES = {
    AGENTIC_SRE_DIRECTORY / "autonomy-and-approval.md": (
        "agent-autonomy-levels",
        "agent-toil-budget",
    ),
    AGENTIC_SRE_DIRECTORY / "blast-radius.md": ("tool-blast-radius",),
    AGENTIC_SRE_DIRECTORY / "drift.md": ("drift-and-quality-monitoring",),
    AGENTIC_SRE_DIRECTORY / "incidents.md": ("agent-incident-response",),
    AGENTIC_SRE_DIRECTORY / "launch-review.md": (
        "agentic-product-reliability-review",
    ),
    AGENTIC_SRE_DIRECTORY / "observability.md": ("trace-based-slis",),
    AGENTIC_SRE_DIRECTORY / "postmortems.md": ("agent-postmortems",),
    AGENTIC_SRE_DIRECTORY / "releases.md": ("eval-gated-releases",),
    AGENTIC_SRE_DIRECTORY / "slos-and-error-budgets.md": (
        "agent-slo-design",
        "agent-capacity-and-cost",
    ),
}
RELIABILITY_SKILL = "agent-reliability"
SKILLS_DIRECTORY = REPOSITORY_ROOT / "skills"
PRACTICE_SECTIONS = (
    "Sources",
    "At a glance",
    "Decision guide",
    "Checklist",
    "Rules of thumb",
    "Claim review",
    "Privacy review",
)
# Private names are denied by digest in scripts/private_terms.py.
PRIVATE_TERMS: tuple[str, ...] = ()
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
APPROVED_CATEGORIES = (
    "AI-assisted engineering & software factories",
    "Agent systems",
    "Enterprise AI platform",
)
APPROVED_TOPICS = (
    "architecture",
    "orchestration",
    "tools-and-context",
    "memory",
    "retrieval",
    "evals",
    "observability",
    "reliability",
    "security-and-privacy",
    "cost",
    "delivery-gates",
    "verification",
    "knowledge-capture",
    "governance",
    "model-serving",
    "gateways",
)
REQUIRED_METADATA = {
    "status": "published",
    "claim_review": "complete",
    "privacy_review": "complete",
}


class PublishedPlaybookMetadataTest(unittest.TestCase):
    def test_published_playbooks_pass_publication_gate(self) -> None:
        for path in PUBLISHED_PLAYBOOKS:
            with self.subTest(playbook=path.name):
                metadata = read_front_matter(path)
                for key, expected_value in REQUIRED_METADATA.items():
                    self.assertEqual(metadata.get(key), expected_value)

                published = metadata.get("published")
                self.assertIsInstance(published, str)
                datetime.date.fromisoformat(published)

    def test_drafts_use_controlled_taxonomy(self) -> None:
        for path, (expected_category, expected_topics) in TAXONOMY_DRAFTS.items():
            with self.subTest(draft=path.name):
                metadata = read_front_matter(path)

                self.assertIn(metadata.get("category"), APPROVED_CATEGORIES)
                self.assertEqual(metadata.get("category"), expected_category)
                topics = metadata.get("topics")
                self.assertIsInstance(topics, list)
                self.assertTrue(topics)
                self.assertEqual(len(topics), len(set(topics)))
                self.assertTrue(set(topics).issubset(APPROVED_TOPICS))
                self.assertEqual(topics, expected_topics)


def level_two_headings(path: pathlib.Path) -> list[str]:
    return [
        line[3:].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    ]


class AgenticSrePracticesTest(unittest.TestCase):
    def test_directory_holds_exactly_the_listed_pages(self) -> None:
        found = set(AGENTIC_SRE_DIRECTORY.glob("*.md"))
        expected = set(AGENTIC_SRE_PRACTICES) | {AGENTIC_SRE_INDEX}
        self.assertEqual(found, expected)

    def test_practices_pass_publication_gate_and_taxonomy(self) -> None:
        for path in AGENTIC_SRE_PRACTICES:
            with self.subTest(practice=path.name):
                metadata = read_front_matter(path)
                for key, expected_value in REQUIRED_METADATA.items():
                    self.assertEqual(metadata.get(key), expected_value)
                published = metadata.get("published")
                self.assertIsInstance(published, str)
                datetime.date.fromisoformat(published)

                self.assertEqual(metadata.get("category"), "Agent systems")
                topics = metadata.get("topics")
                self.assertIsInstance(topics, list)
                self.assertTrue(topics)
                self.assertEqual(len(topics), len(set(topics)))
                self.assertTrue(set(topics).issubset(APPROVED_TOPICS))

    def test_practices_use_the_section_contract(self) -> None:
        for path in AGENTIC_SRE_PRACTICES:
            with self.subTest(practice=path.name):
                self.assertEqual(
                    level_two_headings(path), list(PRACTICE_SECTIONS)
                )
                text = path.read_text(encoding="utf-8")
                self.assertIn("../../building-reliable-agents.md#", text)
                self.assertNotIn("- [ ]", text.split("## Claim review")[1])

    def test_index_lists_every_practice_and_skill_topic(self) -> None:
        index = AGENTIC_SRE_INDEX.read_text(encoding="utf-8")
        for path, topics in AGENTIC_SRE_PRACTICES.items():
            with self.subTest(practice=path.name):
                self.assertIn(f"]({path.name})", index)
                page = path.read_text(encoding="utf-8")
                self.assertEqual(
                    read_front_matter(path).get("skills"),
                    [f"{RELIABILITY_SKILL}/{topic}" for topic in topics],
                )
                self.assertIn(f"Skill: `{RELIABILITY_SKILL}`", page)
                for topic in topics:
                    self.assertIn(f"`{topic}`", page)
                    self.assertIn(
                        f"(../../skills/{RELIABILITY_SKILL}/references/{topic}/guide.md)",
                        index,
                    )

    def test_relative_links_and_anchors_resolve(self) -> None:
        for path in (AGENTIC_SRE_INDEX, *AGENTIC_SRE_PRACTICES):
            text = path.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(text):
                if target.startswith("https://"):
                    continue
                with self.subTest(page=path.name, link=target):
                    file_part, _, anchor = target.partition("#")
                    linked = (
                        (path.parent / file_part).resolve() if file_part else path
                    )
                    self.assertTrue(linked.is_file())
                    if anchor:
                        self.assertIn(anchor, heading_anchors(linked))

    def test_practices_omit_private_product_names(self) -> None:
        for path in (AGENTIC_SRE_INDEX, *AGENTIC_SRE_PRACTICES):
            text = path.read_text(encoding="utf-8").lower()
            for term in PRIVATE_TERMS:
                with self.subTest(page=path.name, term=term):
                    self.assertNotIn(term, text)


ENGINEERING_STANDARDS_DIRECTORY = (
    REPOSITORY_ROOT / "practices" / "engineering-standards"
)
ENGINEERING_STANDARDS_INDEX = ENGINEERING_STANDARDS_DIRECTORY / "README.md"
API_DESIGN_PAGE = ENGINEERING_STANDARDS_DIRECTORY / "api-design.md"
OBSERVABILITY_PAGE = ENGINEERING_STANDARDS_DIRECTORY / "observability.md"
PERFORMANCE_PAGE = ENGINEERING_STANDARDS_DIRECTORY / "performance-and-memory.md"
ENGINEERING_PAGES = (API_DESIGN_PAGE, OBSERVABILITY_PAGE, PERFORMANCE_PAGE)


class EngineeringStandardsPracticesTest(unittest.TestCase):
    def test_directory_holds_exactly_the_listed_pages(self) -> None:
        found = set(ENGINEERING_STANDARDS_DIRECTORY.glob("*.md"))
        self.assertEqual(found, {ENGINEERING_STANDARDS_INDEX, *ENGINEERING_PAGES})
        index = ENGINEERING_STANDARDS_INDEX.read_text(encoding="utf-8")
        self.assertIn(f"]({API_DESIGN_PAGE.name})", index)
        self.assertIn(f"]({OBSERVABILITY_PAGE.name})", index)
        self.assertIn(f"]({PERFORMANCE_PAGE.name})", index)

    def test_practices_pass_publication_gate_and_taxonomy(self) -> None:
        for page in ENGINEERING_PAGES:
            with self.subTest(page=page.name):
                metadata = read_front_matter(page)
                for key, expected_value in REQUIRED_METADATA.items():
                    self.assertEqual(metadata.get(key), expected_value)
                published = metadata.get("published")
                self.assertIsInstance(published, str)
                datetime.date.fromisoformat(published)
                self.assertIn(metadata.get("category"), APPROVED_CATEGORIES)
                topics = metadata.get("topics")
                self.assertIsInstance(topics, list)
                self.assertTrue(topics)
                self.assertEqual(len(topics), len(set(topics)))
                self.assertTrue(set(topics).issubset(APPROVED_TOPICS))

    def test_practices_use_the_section_contract(self) -> None:
        for page in ENGINEERING_PAGES:
            with self.subTest(page=page.name):
                self.assertEqual(level_two_headings(page), list(PRACTICE_SECTIONS))

    def test_relative_links_and_anchors_resolve(self) -> None:
        for path in (ENGINEERING_STANDARDS_INDEX, *ENGINEERING_PAGES):
            text = path.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(text):
                if target.startswith("https://"):
                    continue
                with self.subTest(page=path.name, link=target):
                    file_part, _, anchor = target.partition("#")
                    linked = (
                        (path.parent / file_part).resolve() if file_part else path
                    )
                    self.assertTrue(linked.is_file())
                    if anchor:
                        self.assertIn(anchor, heading_anchors(linked))

    def test_practices_omit_private_product_names(self) -> None:
        for path in (ENGINEERING_STANDARDS_INDEX, *ENGINEERING_PAGES):
            text = path.read_text(encoding="utf-8").lower()
            for term in PRIVATE_TERMS:
                with self.subTest(page=path.name, term=term):
                    self.assertNotIn(term, text)


class PlaybookIndexTest(unittest.TestCase):
    def test_every_published_page_has_matching_metadata(self) -> None:
        pages = playbook_index.published_pages()
        self.assertEqual(
            set(pages),
            set(PUBLISHED_PLAYBOOKS) | set(AGENTIC_SRE_PRACTICES) | set(ENGINEERING_PAGES),
        )
        for path in pages:
            with self.subTest(page=path.name):
                self.assertEqual(playbook_index.matching_metadata_errors(path), [])

    def test_index_and_readme_are_current(self) -> None:
        self.assertEqual(playbook_index.main(["--check"]), 0)

    def test_drafts_stay_out_of_the_index(self) -> None:
        indexed = {
            entry["path"]
            for entry in json.loads(
                playbook_index.INDEX_PATH.read_text(encoding="utf-8")
            )["playbooks"]
        }
        for path in TAXONOMY_DRAFTS:
            with self.subTest(draft=path.name):
                relative = path.relative_to(REPOSITORY_ROOT).as_posix()
                self.assertNotIn(relative, indexed)

    def test_missing_metadata_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            page = pathlib.Path(directory) / "page.md"
            page.write_text(
                "---\nstatus: published\nsignals:\n  - *.proto\n"
                "key_rules:\n  - One.\n  - Two. (#missing)\n---\n# Page\n",
                encoding="utf-8",
            )
            errors = playbook_index.matching_metadata_errors(page)
        self.assertIn("applies_when must be a non-empty list", errors)
        self.assertIn("key_rules must have 3 to 7 items", errors)
        self.assertIn(
            "signals item is not a plain YAML scalar: '*.proto'", errors
        )
        self.assertIn(
            "key_rules item lacks a trailing (#anchor): 'One.'", errors
        )
        self.assertIn(
            "key_rules item cites a missing heading: 'Two. (#missing)'", errors
        )

    def test_key_rules_emit_text_and_section_sources(self) -> None:
        self.assertEqual(
            github_anchor("1. Gate: build an agent?"), "1-gate-build-an-agent"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            page = root / "page.md"
            page.write_text(
                "---\nstatus: published\napplies_when:\n  - building agents\n"
                "signals:\n  - agent\nkey_rules:\n"
                "  - Check the gate. (#1-gate-build-an-agent)\n"
                "  - Keep scope narrow. (#rules-of-thumb)\n"
                "  - Check outputs. (#rules-of-thumb)\n---\n# Page\n"
                "## 1. Gate: build an agent?\n## Rules of thumb\n",
                encoding="utf-8",
            )
            with mock.patch.object(playbook_index, "REPOSITORY_ROOT", root):
                entries = playbook_index.build_entries()
        expected_rules = [
            {"rule": "Check the gate.", "source": "page.md#1-gate-build-an-agent"},
            {"rule": "Keep scope narrow.", "source": "page.md#rules-of-thumb"},
            {"rule": "Check outputs.", "source": "page.md#rules-of-thumb"},
        ]
        index = json.loads(playbook_index.render_index(entries))
        self.assertEqual(index["playbooks"][0]["key_rules"], expected_rules)
        readme = playbook_index.render_readme_section(entries)
        for number, rule in enumerate(expected_rules, start=1):
            self.assertIn(
                f"  {number}. {rule['rule']} ([source]({rule['source']}))", readme
            )


# Arrows and box corners that mark a hand-drawn ASCII diagram.
ASCII_DIAGRAM_MARKS = ("->", "<-", "+-", "-+", "\u2192")


def fenced_blocks(text: str) -> list[tuple[int, str, str]]:
    """Return (opening line number, info string, body) for each code fence."""
    blocks = []
    opening = None
    body: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if opening is None:
            if stripped.startswith("```"):
                opening = (number, stripped[3:].strip())
                body = []
        elif stripped == "```":
            blocks.append((opening[0], opening[1], "\n".join(body)))
            opening = None
        else:
            body.append(line)
    return blocks


def ascii_diagram_errors(text: str) -> list[str]:
    """Report text fences that hold an ASCII diagram."""
    errors = []
    for number, info, body in fenced_blocks(text):
        if info == "text" and any(mark in body for mark in ASCII_DIAGRAM_MARKS):
            errors.append(f"line {number}: ASCII diagram; use a mermaid fence")
    return errors


class DiagramTest(unittest.TestCase):
    def test_markdown_diagrams_use_mermaid(self) -> None:
        for path in sorted(REPOSITORY_ROOT.glob("**/*.md")):
            with self.subTest(page=path.relative_to(REPOSITORY_ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(ascii_diagram_errors(text), [])

    def test_only_text_fence_ascii_diagrams_are_reported(self) -> None:
        text = (
            "```text\nplain output\n```\n"
            "```text\nA -> B\n```\n"
            "```\nA\n```\n"
            "```mermaid\nflowchart LR\n    A --> B\n```\n"
        )
        self.assertEqual(
            ascii_diagram_errors(text),
            [
                "line 4: ASCII diagram; use a mermaid fence",
            ],
        )


def write_page(root: pathlib.Path, name: str, skills: str, body: str = "") -> None:
    page = root / name
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        "---\nstatus: published\napplies_when:\n  - building agents\n"
        "signals:\n  - agent\nkey_rules:\n  - One. (#page)\n  - Two. (#page)\n"
        f"  - Three. (#page)\n{skills}---\n# Page\n{body}",
        encoding="utf-8",
    )


def write_allowlist(root: pathlib.Path) -> None:
    (root / "skills-public.json").write_text(
        json.dumps(
            {
                "version": 1,
                "skills": {
                    "linked-skill": {
                        "description": "Does one thing.",
                        "public_url": "https://example.com/linked-skill",
                        "topics": ["first-topic"],
                    },
                    "private-skill": {"description": "Does another thing."},
                },
            }
        ),
        encoding="utf-8",
    )


SKILL_MARKERS = (
    f"{playbook_index.PAGE_SKILLS_BEGIN}\n{playbook_index.PAGE_SKILLS_END}\n"
)


class PlaybookSkillsTest(unittest.TestCase):
    def test_allowlist_is_valid(self) -> None:
        skills = playbook_index.load_public_skills()
        self.assertTrue(skills)
        self.assertEqual(playbook_index.public_skills_errors(skills), [])

    def test_every_published_page_declares_skills(self) -> None:
        for entry in playbook_index.build_entries():
            with self.subTest(page=entry["path"]):
                self.assertIn("skills", entry)

    def test_root_playbooks_render_the_skills_section(self) -> None:
        for path in PUBLISHED_PLAYBOOKS:
            with self.subTest(playbook=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count(playbook_index.PAGE_SKILLS_HEADING), 1)
                self.assertIn(playbook_index.PAGE_SKILLS_BEGIN, text)

    def test_skills_directory_holds_only_allowlisted_exports(self) -> None:
        skills = playbook_index.load_public_skills()
        exported = {path.name for path in SKILLS_DIRECTORY.iterdir() if path.is_dir()}
        self.assertEqual(exported, {RELIABILITY_SKILL})
        for name in exported:
            with self.subTest(skill=name):
                self.assertEqual(
                    skills[name].get("public_url"), f"skills/{name}/SKILL.md"
                )
                entrypoint = (SKILLS_DIRECTORY / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                lines = entrypoint.splitlines()
                self.assertEqual(lines[0], "---")
                self.assertIn("---", lines[1:])
                metadata = {
                    key.strip(): value.strip()
                    for line in lines[1:lines.index("---", 1)]
                    if line.strip()
                    for key, value in [line.split(":", 1)]
                }
                self.assertEqual(metadata["name"], name)
                self.assertTrue(metadata["description"].strip("\"'"))
                self.assertIn(f"`{name}`", (SKILLS_DIRECTORY / "README.md").read_text(
                    encoding="utf-8"
                ))

    def test_reliability_topics_match_the_exported_guides(self) -> None:
        topics = playbook_index.load_public_skills()[RELIABILITY_SKILL]["topics"]
        references = SKILLS_DIRECTORY / RELIABILITY_SKILL / "references"
        self.assertEqual(
            sorted(path.name for path in references.iterdir() if path.is_dir()),
            sorted(topics),
        )
        entrypoint = (SKILLS_DIRECTORY / RELIABILITY_SKILL / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for topic in topics:
            with self.subTest(topic=topic):
                self.assertTrue((references / topic / "guide.md").is_file())
                self.assertTrue((references / topic / "PROVENANCE.md").is_file())
                self.assertIn(f"(references/{topic}/guide.md)", entrypoint)
        covered = {
            topic for practice in AGENTIC_SRE_PRACTICES.values() for topic in practice
        }
        self.assertEqual(covered, set(topics))

    def test_skill_links_resolve(self) -> None:
        for path in sorted(SKILLS_DIRECTORY.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(text):
                if target.startswith("https://"):
                    continue
                with self.subTest(page=path.relative_to(REPOSITORY_ROOT), link=target):
                    file_part, _, anchor = target.partition("#")
                    linked = (path.parent / file_part).resolve() if file_part else path
                    self.assertTrue(linked.is_file())
                    if anchor:
                        self.assertIn(anchor, heading_anchors(linked))

    def test_allowlist_errors_are_reported(self) -> None:
        errors = playbook_index.public_skills_errors(
            {
                "Bad_Id": {"description": "Fine."},
                "two-sentences": {"description": "One. Two."},
                "bad-url": {"description": "Fine.", "public_url": "missing.md"},
                "extra": {"description": "Fine.", "owner": "someone"},
            }
        )
        self.assertEqual(len(errors), 4)

    def test_page_skills_are_grouped_and_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            write_allowlist(root)
            write_page(
                root,
                "page.md",
                "skills:\n  - linked-skill/first-topic\n  - private-skill\n",
                "## Page\n" + SKILL_MARKERS,
            )
            write_page(root, "none.md", "skills: none\n", "## Page\n" + SKILL_MARKERS)
            with mock.patch.object(playbook_index, "REPOSITORY_ROOT", root):
                entries = playbook_index.build_entries()
                rendered = {
                    entry["path"]: playbook_index.render_page(
                        (root / entry["path"]).read_text(encoding="utf-8"), entry
                    )
                    for entry in entries
                }
        by_path = {entry["path"]: entry for entry in entries}
        self.assertEqual(
            by_path["page.md"]["skills"],
            [
                {
                    "id": "linked-skill",
                    "description": "Does one thing.",
                    "topics": ["first-topic"],
                    "public_url": "https://example.com/linked-skill",
                },
                {"id": "private-skill", "description": "Does another thing.", "topics": []},
            ],
        )
        self.assertEqual(by_path["none.md"]["skills"], [])
        self.assertIn(
            "- [`linked-skill`](https://example.com/linked-skill) (`first-topic`):"
            " Does one thing.",
            rendered["page.md"],
        )
        self.assertIn("- `private-skill`: Does another thing.", rendered["page.md"])
        self.assertIn("A skill without a link is not published", rendered["page.md"])
        self.assertIn("No agent skill puts this playbook", rendered["none.md"])

    def test_skills_outside_the_allowlist_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            write_allowlist(root)
            write_page(
                root,
                "page.md",
                "skills:\n  - unlisted-skill\n  - linked-skill/other-topic\n"
                "  - Not An Id\n",
            )
            with mock.patch.object(playbook_index, "REPOSITORY_ROOT", root):
                with self.assertRaises(ValueError) as raised:
                    playbook_index.build_entries()
        message = str(raised.exception)
        self.assertIn("outside skills-public.json: 'unlisted-skill'", message)
        self.assertIn("unknown topic: 'linked-skill/other-topic'", message)
        self.assertIn("not <id> or <id>/<topic>: 'Not An Id'", message)

    def test_markers_must_match_the_declaration(self) -> None:
        entry = {"path": "page.md", "skills": []}
        with self.assertRaisesRegex(ValueError, "lacks the"):
            playbook_index.render_page("# Page\n", entry)
        practice = {"path": "practices/set/page.md", "skills": []}
        with self.assertRaisesRegex(ValueError, "only root playbooks"):
            playbook_index.render_page(SKILL_MARKERS, practice)
        undeclared = {"path": "page.md"}
        with self.assertRaisesRegex(ValueError, "only root playbooks"):
            playbook_index.render_page(SKILL_MARKERS, undeclared)


class LicenseTest(unittest.TestCase):
    def test_repository_is_mit_licensed_to_david_tandoh(self) -> None:
        text = (REPOSITORY_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("MIT License\n"))
        self.assertIn("Copyright (c) 2026 David Tandoh", text)


if __name__ == "__main__":
    unittest.main()
