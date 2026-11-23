"""Block private names from Markdown without publishing those names.

The denylist holds only SHA-256 digests of normalized terms. A term is
normalized by lowercasing it and joining its alphanumeric tokens with single
spaces, so "Foo-Bar" and "foo bar" share one digest. The scanner hashes every
one-, two- and three-token phrase in each Markdown file and reports the
file and line of a match, never the matched text.

Usage:
    python3 scripts/private_terms.py add <term>   # print the digest to paste
    python3 scripts/private_terms.py scan         # exit 1 on any match
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys
from collections.abc import Iterable, Iterator


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_PHRASE_TOKENS = 3
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
DENIED_DIGESTS = frozenset(
    {
        "5f876991652e4e04751fd86108131660847ba56f1784874638f683cc15876de4",
        "53abb6615338bae6eba4c06bc4d27740578732d33a963db7660231bddb16e89e",
        "6accd937d574615b71052b44f5df52a368034ab02198eff32d7212c64597608d",
        "ab9a1a62bcd9e6c1f8bda47b402f61c52cd2f7a9310172e7b6f1dc584ffb3a0e",
        "b1a8f0a4d2aae9e01582f244dadd434276725eb1db0cea11ca8bcfcbef640eb6",
        "c1cbb8108bc8f123dd633dfa518481cb84dc00d12807b6be4915a80aab091636",
        "4fd66075551066c02f7c260c73df47c9fe550e734e8ea4b9c0e07e4341df0dc7",
        "1729aebb6a6da8d3bdcb6a2f0901a6136f479a90b97543db5bbefa415ff649e6",
        "09527e431dd1fe6d422df0de0c5b4ea0c6d8494ab56f1c48c3281d579bc1f688",
        "4a1c9b727d9b9498b09e57331881beae8242530b32e64bbfc0fbdca3275957e2",
    }
)


def digest(term: str) -> str:
    """Return the denylist digest for a term or phrase."""
    normalized = " ".join(TOKEN_PATTERN.findall(term.lower()))
    if not normalized:
        raise ValueError("term has no letters or digits")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _tokens(text: str) -> Iterator[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for token in TOKEN_PATTERN.findall(line.lower()):
            yield line_number, token


def matching_lines(text: str, denied: Iterable[str] = DENIED_DIGESTS) -> list[int]:
    """Return the sorted line numbers where a denied phrase starts."""
    denied = frozenset(denied)
    tokens = list(_tokens(text))
    lines = set()
    for start, (line_number, _) in enumerate(tokens):
        for length in range(1, MAX_PHRASE_TOKENS + 1):
            phrase = tokens[start : start + length]
            if len(phrase) < length:
                break
            words = " ".join(token for _, token in phrase)
            if hashlib.sha256(words.encode("utf-8")).hexdigest() in denied:
                lines.add(line_number)
    return sorted(lines)


def markdown_files(root: pathlib.Path = REPOSITORY_ROOT) -> list[pathlib.Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if ".git" not in path.relative_to(root).parts
    )


def scan(
    root: pathlib.Path = REPOSITORY_ROOT, denied: Iterable[str] = DENIED_DIGESTS
) -> list[str]:
    """Return "path:line" findings for every Markdown file under root."""
    findings = []
    for path in markdown_files(root):
        relative = path.relative_to(root)
        for line_number in matching_lines(
            path.read_text(encoding="utf-8"), denied
        ):
            findings.append(f"{relative}:{line_number}")
    return findings


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "add":
        print(digest(argv[1]))
        return 0
    if argv == ["scan"]:
        findings = scan()
        for finding in findings:
            print(f"{finding}: denied private term", file=sys.stderr)
        return 1 if findings else 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
