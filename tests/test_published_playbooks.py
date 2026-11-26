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
