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

    def test_index_lists_every_practice_and_skill(self) -> None:
        index = AGENTIC_SRE_INDEX.read_text(encoding="utf-8")
        for path, skill_ids in AGENTIC_SRE_PRACTICES.items():
            with self.subTest(practice=path.name):
                self.assertIn(f"]({path.name})", index)
                page = path.read_text(encoding="utf-8")
                for skill_id in skill_ids:
                    self.assertIn(f"`skills/{skill_id}/`", index)
                    self.assertIn(f"`{skill_id}`", page)

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


class EngineeringStandardsPracticesTest(unittest.TestCase):
    def test_directory_holds_exactly_the_listed_pages(self) -> None:
        found = set(ENGINEERING_STANDARDS_DIRECTORY.glob("*.md"))
        self.assertEqual(found, {ENGINEERING_STANDARDS_INDEX, API_DESIGN_PAGE})
        index = ENGINEERING_STANDARDS_INDEX.read_text(encoding="utf-8")
        self.assertIn(f"]({API_DESIGN_PAGE.name})", index)

    def test_api_design_passes_publication_gate_and_taxonomy(self) -> None:
        metadata = read_front_matter(API_DESIGN_PAGE)
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

    def test_api_design_uses_the_section_contract(self) -> None:
        self.assertEqual(
            level_two_headings(API_DESIGN_PAGE), list(PRACTICE_SECTIONS)
        )

    def test_relative_links_and_anchors_resolve(self) -> None:
        for path in (ENGINEERING_STANDARDS_INDEX, API_DESIGN_PAGE):
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
        for path in (ENGINEERING_STANDARDS_INDEX, API_DESIGN_PAGE):
            text = path.read_text(encoding="utf-8").lower()
            for term in PRIVATE_TERMS:
                with self.subTest(page=path.name, term=term):
                    self.assertNotIn(term, text)


class PlaybookIndexTest(unittest.TestCase):
    def test_every_published_page_has_matching_metadata(self) -> None:
        pages = playbook_index.published_pages()
        self.assertEqual(
            set(pages),
            set(PUBLISHED_PLAYBOOKS) | set(AGENTIC_SRE_PRACTICES) | {API_DESIGN_PAGE},
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


class LicenseTest(unittest.TestCase):
    def test_repository_is_mit_licensed_to_david_tandoh(self) -> None:
        text = (REPOSITORY_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("MIT License\n"))
        self.assertIn("Copyright (c) 2026 David Tandoh", text)


if __name__ == "__main__":
    unittest.main()
