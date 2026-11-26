#!/usr/bin/env python3
"""Tests for audit_inventory.py: python3 test_audit_inventory.py"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_inventory as ai  # noqa: E402


class Inventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cwd = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.cwd)
        subprocess.run(["git", "init", "-q"], check=True)
        self.write("src/pkg/limits.py",
                   "def clamp(x):\n    # Why: callers pass seconds.\n    return max(0, x)\n\n\n"
                   "# Kept for the old API.\n# Remove later.\nOLD = 1\n")
        self.write("tests/test_limits.py",
                   "import pytest\nfrom pkg.limits import clamp\n\n\n"
                   "@pytest.mark.parametrize('x', [1])\ndef test_clamp(x):\n    assert clamp(x) == 1  # noqa: S101\n\n\n"
                   "class TestOld:\n    def test_old(self):\n        assert True\n")

    def write(self, path, text):
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", path], check=True)

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ai.main(list(args)), 0)

    def read(self, path):
        return [json.loads(line) for line in Path(path).read_text().splitlines()]

    def test_tests_carry_decorators_class_names_and_the_imported_helper(self):
        self.run_main("tests", "--roots", "tests", "--out", "inv", "--batch", "1")
        first, second = self.read("inv/tests-001.jsonl")[0], self.read("inv/tests-002.jsonl")[0]
        self.assertEqual((first["id"], second["id"]),
                         ("tests/test_limits.py::test_clamp", "tests/test_limits.py::TestOld::test_old"))
        self.assertTrue(first["source"].startswith("@pytest.mark.parametrize"))
        self.assertIn("def clamp(x):", first["helpers"])
        self.assertEqual(second["helpers"], "")

    def test_comment_blocks_skip_what_the_ratchet_exempts(self):
        self.run_main("comments", "--roots", "src", "tests", "--out", "inv")
        items = self.read("inv/comments-001.jsonl")
        self.assertEqual([i["id"] for i in items], ["src/pkg/limits.py:6"])
        self.assertIn("    6> # Kept for the old API.", items[0]["context"])
        self.assertIn("    7> # Remove later.", items[0]["context"])


if __name__ == "__main__":
    unittest.main()
