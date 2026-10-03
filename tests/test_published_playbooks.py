from __future__ import annotations

import datetime
import pathlib
import unittest


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLISHED_PLAYBOOKS = (
    REPOSITORY_ROOT / "building-ai-agents.md",
    REPOSITORY_ROOT / "building-reliable-agents.md",
)
CONTEXTUAL_RETRIEVAL_DRAFT = (
    REPOSITORY_ROOT / "drafts" / "20261003-contextual-retrieval.md"
)
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

    def test_contextual_retrieval_uses_controlled_taxonomy(self) -> None:
        metadata = read_front_matter(CONTEXTUAL_RETRIEVAL_DRAFT)

        self.assertIn(metadata.get("category"), APPROVED_CATEGORIES)
        topics = metadata.get("topics")
        self.assertIsInstance(topics, list)
        self.assertTrue(topics)
        self.assertEqual(len(topics), len(set(topics)))
        self.assertTrue(set(topics).issubset(APPROVED_TOPICS))
        self.assertEqual(topics, ["retrieval", "evals", "cost"])


if __name__ == "__main__":
    unittest.main()
