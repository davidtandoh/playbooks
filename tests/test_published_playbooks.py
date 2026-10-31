from __future__ import annotations

import datetime
import pathlib
import re
import unittest


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLISHED_PLAYBOOKS = (
    REPOSITORY_ROOT / "building-ai-agents.md",
    REPOSITORY_ROOT / "building-reliable-agents.md",
)
TAXONOMY_DRAFTS = {
    REPOSITORY_ROOT / "drafts" / "20261003-contextual-retrieval.md": (
        "Enterprise AI platform",
        ["retrieval", "evals", "cost"],
    ),
    REPOSITORY_ROOT / "drafts" / "20261011-local-first-ci.md": (
        "AI-assisted engineering & software factories",
        ["delivery-gates", "verification", "security-and-privacy", "cost"],
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
PRIVATE_TERMS = ("omnigent", "firstmate", "mlflow")
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


def read_front_matter(path: pathlib.Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path.name} has no front matter")

    try:
        closing_delimiter = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"{path.name} has unterminated front matter") from error

    metadata: dict[str, object] = {}
    current_list = None
    for line in lines[1:closing_delimiter]:
        if line.startswith("  - "):
            if current_list is None:
                raise ValueError(
                    f"{path.name} has a list item without a front matter key"
                )
            value = line[4:].strip()
            if not value:
                raise ValueError(f"{path.name} has an empty list item")
            items = metadata[current_list]
            if not isinstance(items, list):
                raise ValueError(f"{path.name} has malformed list metadata")
            items.append(value)
            continue

        current_list = None
        key, separator, value = line.partition(":")
        if not separator or not key:
            raise ValueError(f"{path.name} has malformed front matter: {line!r}")
        if key in metadata:
            raise ValueError(f"{path.name} repeats front matter key {key!r}")
        if value.strip():
            metadata[key] = value.strip()
        else:
            metadata[key] = []
            current_list = key
    return metadata


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


def github_anchor(heading: str) -> str:
    """Return the anchor GitHub generates for a Markdown heading."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_anchors(path: pathlib.Path) -> set[str]:
    anchors = set()
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("#"):
            anchors.add(github_anchor(line.lstrip("#")))
    return anchors


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


class LicenseTest(unittest.TestCase):
    def test_repository_is_mit_licensed_to_david_tandoh(self) -> None:
        text = (REPOSITORY_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("MIT License\n"))
        self.assertIn("Copyright (c) 2026 David Tandoh", text)


if __name__ == "__main__":
    unittest.main()
