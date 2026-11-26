"""Build the "applies when" index of published playbooks and practice pages.

Usage:
    python3 scripts/playbook_index.py          # rewrite generated files
    python3 scripts/playbook_index.py --check  # exit 1 if any is stale

Only pages whose front matter says `status: published` enter the index.

See README.md#conventions for skills front matter, the public allowlist,
and generated page sections.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import posixpath
import re
import sys


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_PATH = REPOSITORY_ROOT / "index.json"
README_PATH = REPOSITORY_ROOT / "README.md"
README_BEGIN = "<!-- playbook-index:v1:begin -->"
README_END = "<!-- playbook-index:v1:end -->"
SKILLS_FILE = "skills-public.json"
PAGE_SKILLS_BEGIN = "<!-- playbook-skills:v1:begin -->"
PAGE_SKILLS_END = "<!-- playbook-skills:v1:end -->"
PAGE_SKILLS_HEADING = "## Skills that put this into practice"
NO_SKILLS = "none"
SKILL_REFERENCE = re.compile(r"([a-z0-9]+(?:-[a-z0-9]+)*)(?:/([a-z0-9]+(?:-[a-z0-9]+)*))?")
SKILL_ENTRY_KEYS = {"description", "public_url", "topics"}
SKILL_DESCRIPTION_LIMIT = 240
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
            if current_list == "path_globs" and not value.startswith('"'):
                if value.startswith(YAML_INDICATORS) or ": " in value or " #" in value:
                    raise ValueError(f"{path.name} path_globs requires double-quoted patterns")
            if current_list == "path_globs" and value.startswith('"'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path.name} has malformed path_globs quoting") from error
                if not isinstance(value, str):
                    raise ValueError(f"{path.name} path_globs items must be strings")
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
    if "path_globs" in metadata:
        patterns = metadata["path_globs"]
        if not isinstance(patterns, list) or not patterns:
            errors.append("path_globs must be a non-empty list when present")
        else:
            if len(patterns) != len(set(patterns)):
                errors.append("path_globs repeats an item")
            for pattern in patterns:
                if (
                    not pattern
                    or pattern.startswith(("/", "~", "!", "'"))
                    or "\\" in pattern
                    or ":" in pattern
                    or any(part in ("", ".", "..") for part in pattern.split("/"))
                    or any(character.isspace() for character in pattern)
                    or not re.search(r"[a-zA-Z0-9_-]", pattern)
                ):
                    errors.append(f"path_globs item must be a specific relative POSIX glob: {pattern!r}")
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


def load_public_skills() -> dict[str, dict[str, object]]:
    """Return the skills allowlist, keyed by skill id.

    A repository without an allowlist has no public skills, so any page that
    names a skill fails validation.
    """
    path = REPOSITORY_ROOT / SKILLS_FILE
    if not path.is_file():
        return {}
    allowlist = json.loads(path.read_text(encoding="utf-8"))
    if allowlist.get("version") != 1 or not isinstance(allowlist.get("skills"), dict):
        raise ValueError("skills-public.json must be version 1 with a skills object")
    return allowlist["skills"]


def public_skills_errors(skills: dict[str, dict[str, object]]) -> list[str]:
    """Return every problem with the skills allowlist itself."""
    errors = []
    for skill_id, entry in skills.items():
        prefix = f"skills-public.json {skill_id!r}"
        reference = SKILL_REFERENCE.fullmatch(skill_id)
        if reference is None or reference[2]:
            errors.append(f"{prefix}: id must be lowercase words joined by hyphens")
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue
        unknown = set(entry) - SKILL_ENTRY_KEYS
        if unknown:
            errors.append(f"{prefix}: unknown keys {sorted(unknown)}")
        description = entry.get("description")
        if (
            not isinstance(description, str)
            or not description.endswith(".")
            or ". " in description
            or "\n" in description
            or len(description) > SKILL_DESCRIPTION_LIMIT
        ):
            errors.append(
                f"{prefix}: description must be one sentence of at most "
                f"{SKILL_DESCRIPTION_LIMIT} characters"
            )
        url = entry.get("public_url")
        if url is not None:
            if not isinstance(url, str) or not url:
                errors.append(f"{prefix}: public_url must be a non-empty string")
            elif not url.startswith("https://"):
                target = (REPOSITORY_ROOT / url).resolve()
                if url.startswith("/") or not target.is_file():
                    errors.append(
                        f"{prefix}: public_url must be https:// or a file in this repository"
                    )
        topics = entry.get("topics", [])
        if (
            not isinstance(topics, list)
            or len(topics) != len(set(topics))
            or not all(
                isinstance(topic, str) and SKILL_REFERENCE.fullmatch(topic)
                for topic in topics
            )
        ):
            errors.append(f"{prefix}: topics must be a list of unique topic ids")
    return errors


def skills_metadata_errors(
    metadata: dict[str, object], skills: dict[str, dict[str, object]]
) -> list[str]:
    """Return every problem with a page's optional skills front matter."""
    items = metadata.get("skills")
    if items is None or items == NO_SKILLS:
        return []
    if not isinstance(items, list) or not items:
        return [f"skills must be a non-empty list or {NO_SKILLS!r}"]
    errors = []
    if len(items) != len(set(items)):
        errors.append("skills repeats an item")
    for item in items:
        reference = SKILL_REFERENCE.fullmatch(item)
        if reference is None:
            errors.append(f"skills item is not <id> or <id>/<topic>: {item!r}")
        elif reference[1] not in skills:
            errors.append(f"skills item names a skill outside skills-public.json: {item!r}")
        elif reference[2] and reference[2] not in skills[reference[1]].get("topics", []):
            errors.append(f"skills item names an unknown topic: {item!r}")
    return errors


def page_skills(
    metadata: dict[str, object], skills: dict[str, dict[str, object]]
) -> list[dict[str, object]] | None:
    """Group a page's skills front matter by skill id, in first-mention order.

    Returns None when the page does not declare skills.
    """
    items = metadata.get("skills")
    if items is None:
        return None
    if items == NO_SKILLS:
        return []
    grouped: dict[str, dict[str, object]] = {}
    for item in items:
        skill_id, _, topic = item.partition("/")
        entry = grouped.setdefault(
            skill_id,
            {
                "id": skill_id,
                "description": skills[skill_id]["description"],
                "topics": [],
            },
        )
        if "public_url" in skills[skill_id]:
            entry["public_url"] = skills[skill_id]["public_url"]
        if topic:
            entry["topics"].append(topic)
    return list(grouped.values())


def is_root_playbook(relative: str) -> bool:
    return "/" not in relative


def build_entries() -> list[dict[str, object]]:
    skills = load_public_skills()
    allowlist_errors = public_skills_errors(skills)
    if allowlist_errors:
        raise ValueError("; ".join(allowlist_errors))
    entries = []
    for path in published_pages():
        metadata = read_front_matter(path)
        errors = matching_metadata_errors(path) + skills_metadata_errors(
            metadata, skills
        )
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        if errors:
            raise ValueError(f"{relative}: " + "; ".join(errors))
        rules = []
        for rule in metadata["key_rules"]:
            citation = KEY_RULE_CITATION.fullmatch(rule)
            rules.append({"rule": citation[1], "source": f"{relative}#{citation[2]}"})
        entry = {
            "path": relative,
            "title": page_title(path),
            **{key: metadata[key] for key in MATCHING_KEYS},
            "key_rules": rules,
        }
        if "path_globs" in metadata:
            entry["path_globs"] = metadata["path_globs"]
        declared = page_skills(metadata, skills)
        if declared is not None:
            entry["skills"] = declared
        entries.append(entry)
    return entries


def skill_link(skill: dict[str, object], page: str) -> str:
    """Return the skill id as Markdown, linked when the skill is published."""
    label = f"`{skill['id']}`"
    url = skill.get("public_url")
    if not url:
        return label
    if not url.startswith("https://"):
        url = posixpath.relpath(url, posixpath.dirname(page) or ".")
    return f"[{label}]({url})"


def skill_summary(skill: dict[str, object], page: str) -> str:
    """Return the skill link followed by its topics, if any."""
    text = skill_link(skill, page)
    if skill["topics"]:
        text += " (" + ", ".join(f"`{topic}`" for topic in skill["topics"]) + ")"
    return text


def render_page_skills(entry: dict[str, object]) -> str:
    lines = [
        PAGE_SKILLS_BEGIN,
        "<!-- Generated by scripts/playbook_index.py from the skills front matter."
        " Do not edit by hand. -->",
        PAGE_SKILLS_HEADING,
        "",
    ]
    skills = entry["skills"]
    if not skills:
        lines.append("No agent skill puts this playbook into practice yet.")
    else:
        lines.append(
            "These agent skills turn the rules above into steps an agent follows."
        )
        if any(not skill.get("public_url") for skill in skills):
            lines.append(
                "A skill without a link is not published; only its id and"
                " summary are public."
            )
        lines.append("")
        lines += [
            f"- {skill_summary(skill, entry['path'])}: {skill['description']}"
            for skill in skills
        ]
    lines.append(PAGE_SKILLS_END)
    return "\n".join(lines)


def render_page(text: str, entry: dict[str, object]) -> str:
    """Return a page with its generated skills section brought up to date."""
    path = entry["path"]
    has_markers = PAGE_SKILLS_BEGIN in text or PAGE_SKILLS_END in text
    if "skills" not in entry or not is_root_playbook(path):
        if has_markers:
            raise ValueError(
                f"{path} has playbook-skills markers but no rendered skills section;"
                " only root playbooks with skills front matter render one"
            )
        return text
    before, begin, rest = text.partition(PAGE_SKILLS_BEGIN)
    _, end, after = rest.partition(PAGE_SKILLS_END)
    if not begin or not end:
        raise ValueError(f"{path} declares skills but lacks the {PAGE_SKILLS_BEGIN} markers")
    return before + render_page_skills(entry) + after


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
        ]
        if "path_globs" in entry:
            lines.append(
                "- Path globs (PR gate): "
                + ", ".join(f"`{pattern}`" for pattern in entry["path_globs"])
                + "."
            )
        if "skills" in entry:
            lines.append(
                "- Skills: "
                + (
                    ", ".join(
                        skill_summary(skill, README_PATH.name)
                        for skill in entry["skills"]
                    )
                    or "none yet"
                )
                + "."
            )
        lines += [
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
        help="write nothing; exit 1 if index.json, the README index, or a"
        " page's skills section is stale",
    )
    arguments = parser.parse_args(argv)
    entries = build_entries()
    expected = {
        INDEX_PATH: render_index(entries),
        README_PATH: render_readme(README_PATH.read_text(encoding="utf-8"), entries),
    }
    for entry in entries:
        page = REPOSITORY_ROOT / entry["path"]
        text = page.read_text(encoding="utf-8")
        rendered = render_page(text, entry)
        if rendered != text:
            expected[page] = rendered
    if arguments.check:
        stale = [
            path.relative_to(REPOSITORY_ROOT).as_posix()
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
