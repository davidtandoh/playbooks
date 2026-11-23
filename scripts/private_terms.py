"""Block private names from tracked text files without publishing those names.

The denylist holds only SHA-256 digests of normalized terms. A term is
normalized by lowercasing it and joining its alphanumeric tokens with single
spaces, so "Foo-Bar" and "foo bar" share one digest. The scanner hashes every
one-, two- and three-token phrase in each tracked text file and reports the
file and line of a match, never the matched text.

Usage:
    python3 scripts/private_terms.py add <term>   # print the digest to paste
    python3 scripts/private_terms.py scan         # exit 1 on any match
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys
from collections.abc import Iterable, Iterator
from typing import Optional


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
    tokens = TOKEN_PATTERN.findall(term.lower())
    if len(tokens) > MAX_PHRASE_TOKENS:
        raise ValueError(f"term exceeds {MAX_PHRASE_TOKENS} tokens")
    normalized = " ".join(tokens)
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


def tracked_files(root: pathlib.Path = REPOSITORY_ROOT) -> list[pathlib.Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return sorted(
        root / pathlib.Path(name.decode("utf-8", errors="surrogateescape"))
        for name in set(result.stdout.split(b"\0"))
        if name and name != b"scripts/private_terms.py"
    )


def read_tracked_text(path: pathlib.Path) -> Optional[str]:
    if path.is_symlink():
        raise ValueError("tracked symlink cannot be scanned")
    with path.open("rb") as source:
        content = source.read(16 * 1024 * 1024 + 1)
    if len(content) > 16 * 1024 * 1024:
        raise ValueError("tracked file exceeds scan byte limit")
    if b"\0" in content:
        return None
    return content.decode("utf-8", errors="surrogateescape")


def scan(
    root: pathlib.Path = REPOSITORY_ROOT, denied: Iterable[str] = DENIED_DIGESTS
) -> list[str]:
    """Return "path:line" findings for every tracked text file under root."""
    findings = []
    for path in tracked_files(root):
        relative = path.relative_to(root)
        text = read_tracked_text(path)
        if text is None:
            continue
        for line_number in matching_lines(text, denied):
            findings.append(f"{relative}:{line_number}")
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("term")
    commands.add_parser("scan")
    args = parser.parse_args(argv)
    if args.command == "add":
        try:
            value = digest(args.term)
        except ValueError as error:
            parser.error(str(error))
        print(value)
        return 0
    findings = scan()
    for finding in findings:
        print(f"{finding}: denied private term", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
