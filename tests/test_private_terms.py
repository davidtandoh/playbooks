from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "private_terms.py"
sys.path.insert(0, str(SCRIPT.parent))

import private_terms  # noqa: E402


EXAMPLE_DENIED = frozenset(
    {private_terms.digest("examplecorp"), private_terms.digest("acme rocket")}
)


class PrivateTermsScanTest(unittest.TestCase):
    def test_repository_markdown_omits_denied_terms(self) -> None:
        paths = private_terms.markdown_files()
        self.assertIn(
            REPOSITORY_ROOT / "drafts" / "20261011-local-first-ci.md", paths
        )
        self.assertEqual(private_terms.scan(), [])

    def test_denylist_holds_only_digests(self) -> None:
        self.assertTrue(private_terms.DENIED_DIGESTS)
        for value in private_terms.DENIED_DIGESTS:
            with self.subTest(value=value):
                self.assertRegex(value, re.compile(r"^[0-9a-f]{64}$"))

    def test_matches_single_word_case_insensitively(self) -> None:
        text = "intro\nThe ExampleCorp estate\nend"
        self.assertEqual(private_terms.matching_lines(text, EXAMPLE_DENIED), [2])

    def test_matches_phrase_across_punctuation_and_lines(self) -> None:
        self.assertEqual(
            private_terms.matching_lines("an Acme-Rocket run", EXAMPLE_DENIED), [1]
        )
        self.assertEqual(
            private_terms.matching_lines("an acme\nrocket run", EXAMPLE_DENIED), [1]
        )

    def test_ignores_partial_words_and_single_words_of_a_phrase(self) -> None:
        for text in ("examplecorporation", "acme tools", "rocket science", ""):
            with self.subTest(text=text):
                self.assertEqual(
                    private_terms.matching_lines(text, EXAMPLE_DENIED), []
                )

    def test_digest_normalizes_case_and_separators(self) -> None:
        self.assertEqual(
            private_terms.digest("Acme-Rocket"), private_terms.digest("acme  rocket")
        )
        with self.assertRaises(ValueError):
            private_terms.digest("--")

    def test_scan_reports_location_without_the_term(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "drafts").mkdir()
            (root / "drafts" / "page.md").write_text(
                "clean\nnamed examplecorp here\n", encoding="utf-8"
            )
            (root / "notes.txt").write_text("examplecorp", encoding="utf-8")
            findings = private_terms.scan(root, EXAMPLE_DENIED)
        self.assertEqual(findings, ["drafts/page.md:2"])

    def test_cli_add_prints_digest_and_scan_passes(self) -> None:
        added = subprocess.run(
            [sys.executable, str(SCRIPT), "add", "Acme Rocket"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(added.stdout.strip(), private_terms.digest("acme rocket"))
        scanned = subprocess.run(
            [sys.executable, str(SCRIPT), "scan"], capture_output=True, text=True
        )
        self.assertEqual(scanned.returncode, 0, scanned.stderr)


if __name__ == "__main__":
    unittest.main()
