"""Build the "applies when" index of published playbooks and practice pages.

Usage:
    python3 scripts/playbook_index.py          # rewrite index.json and README
    python3 scripts/playbook_index.py --check  # exit 1 if either is stale

Only pages whose front matter says `status: published` enter the index.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_PATH = REPOSITORY_ROOT / "index.json"
README_PATH = REPOSITORY_ROOT / "README.md"
README_BEGIN = "<!-- playbook-index:v1:begin -->"
README_END = "<!-- playbook-index:v1:end -->"
MATCHING_KEYS = ("applies_when", "signals", "key_rules")
KEY_RULES_RANGE = (3, 7)
KEY_RULE_CITATION = re.compile(r"(.+) \(#([^\s()]+)\)")
# A list item must also read as a plain YAML scalar, so that GitHub renders
# the front matter. These characters cannot start a plain scalar.
YAML_INDICATORS = tuple("-?:,[]{}#&*!|>'\"%@`")


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


def front_matter_status(path: pathlib.Path) -> str | None:
    """Return the top-level `status` value without parsing the whole block.

    Drafts may use richer YAML than read_front_matter accepts, so only the
    status line decides whether a page needs the full parse.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return None
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("status:"):
            return line.partition(":")[2].strip()
    return None


def published_pages() -> list[pathlib.Path]:
    """Return every Markdown page whose front matter says it is published."""
    pages = []
    for path in sorted(REPOSITORY_ROOT.rglob("*.md")):
        relative = path.relative_to(REPOSITORY_ROOT)
        if relative.parts[0].startswith("."):
            continue
        if front_matter_status(path) == "published":
            pages.append(path)
    return pages


def page_title(path: pathlib.Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip().removeprefix("Playbook: ")
    raise ValueError(f"{path.name} has no level-one heading")


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


def matching_metadata_errors(path: pathlib.Path) -> list[str]:
    """Return every problem with a published page's matching metadata."""
    metadata = read_front_matter(path)
    errors = []
    for key in MATCHING_KEYS:
        items = metadata.get(key)
        if not isinstance(items, list) or not items:
            errors.append(f"{key} must be a non-empty list")
            continue
        if len(items) != len(set(items)):
            errors.append(f"{key} repeats an item")
        for item in items:
            if item.startswith(YAML_INDICATORS) or ": " in item or " #" in item:
                errors.append(f"{key} item is not a plain YAML scalar: {item!r}")
    rules = metadata.get("key_rules")
    low, high = KEY_RULES_RANGE
    if isinstance(rules, list) and not low <= len(rules) <= high:
        errors.append(f"key_rules must have {low} to {high} items")
    if isinstance(rules, list):
        anchors = heading_anchors(path)
        for rule in rules:
            citation = KEY_RULE_CITATION.fullmatch(rule)
            if citation is None:
                errors.append(f"key_rules item lacks a trailing (#anchor): {rule!r}")
            elif citation[2] not in anchors:
                errors.append(f"key_rules item cites a missing heading: {rule!r}")
    return errors


def build_entries() -> list[dict[str, object]]:
    entries = []
    for path in published_pages():
        errors = matching_metadata_errors(path)
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        if errors:
            raise ValueError(f"{relative}: " + "; ".join(errors))
        metadata = read_front_matter(path)
        rules = []
        for rule in metadata["key_rules"]:
            citation = KEY_RULE_CITATION.fullmatch(rule)
            rules.append({"rule": citation[1], "source": f"{relative}#{citation[2]}"})
        entries.append(
            {
                "path": relative,
                "title": page_title(path),
                **{key: metadata[key] for key in MATCHING_KEYS},
                "key_rules": rules,
            }
        )
    return entries


def render_index(entries: list[dict[str, object]]) -> str:
    return json.dumps({"version": 1, "playbooks": entries}, indent=2, sort_keys=True) + "\n"


def render_readme_section(entries: list[dict[str, object]]) -> str:
    lines = [
        README_BEGIN,
        "<!-- Generated by scripts/playbook_index.py. Do not edit by hand. -->",
    ]
    for entry in entries:
        lines += [
            "",
            f"**[{entry['title']}]({entry['path']})**",
            "",
            "- Applies when: " + "; ".join(entry["applies_when"]) + ".",
            "- Signals: " + ", ".join(f"`{s}`" for s in entry["signals"]) + ".",
            "- Key rules:",
        ]
        lines += [
            f"  {number}. {rule['rule']} ([source]({rule['source']}))"
            for number, rule in enumerate(entry["key_rules"], start=1)
        ]
    lines.append(README_END)
    return "\n".join(lines)


def render_readme(readme: str, entries: list[dict[str, object]]) -> str:
    before, begin, rest = readme.partition(README_BEGIN)
    _, end, after = rest.partition(README_END)
    if not begin or not end:
        raise ValueError(f"README.md lacks the {README_BEGIN} markers")
    return before + render_readme_section(entries) + after


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if index.json or the README index is stale",
    )
    arguments = parser.parse_args(argv)
    entries = build_entries()
    expected = {
        INDEX_PATH: render_index(entries),
        README_PATH: render_readme(README_PATH.read_text(encoding="utf-8"), entries),
    }
    if arguments.check:
        stale = [
            path.name
            for path, text in expected.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            print(
                "Stale: " + ", ".join(stale)
                + ". Run python3 scripts/playbook_index.py",
                file=sys.stderr,
            )
            return 1
        return 0
    for path, text in expected.items():
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
