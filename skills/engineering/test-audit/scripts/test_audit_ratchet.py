#!/usr/bin/env python3
"""Tests for audit_ratchet.py: python3 test_audit_ratchet.py"""
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
import audit_ratchet as ar  # noqa: E402


class CountComments(unittest.TestCase):
    def test_counts_plain_and_trailing_comments(self):
        self.assertEqual(ar.count_comments("# one\nx = 1  # two\n"), 2)

    def test_hash_inside_a_string_is_not_a_comment(self):
        self.assertEqual(ar.count_comments('x = "# not a comment"\n'), 0)

    def test_pragmas_are_exempt(self):
        source = ("import os  # noqa: F401\n"
                  "y = f()  # type: ignore[attr-defined]\n"
                  "if z:  # pragma: no cover\n    pass\n"
                  "run()  # nosec B603\n"
                  "# fmt: off\n")
        self.assertEqual(ar.count_comments(source), 0)

    def test_shebang_and_coding_lines_are_exempt_only_at_the_top(self):
        self.assertEqual(ar.count_comments("#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"), 0)
        self.assertEqual(ar.count_comments("x = 1\n\n#!/not/a/shebang\n"), 1)

    def test_one_line_why_is_exempt_but_its_continuation_counts(self):
        self.assertEqual(ar.count_comments("# Why: the API returns 1-based weeks.\n"), 0)
        self.assertEqual(ar.count_comments("# Why: long story\n# and more of it\n"), 1)

    def test_why_needs_the_exact_prefix_and_text(self):
        self.assertEqual(ar.count_comments("# why: lower case\n# Why:\n"), 2)

    def test_script_metadata_and_license_headers_are_exempt(self):
        source = ("# /// script\n# dependencies = ['httpx']\n# ///\n"
                  "# SPDX-License-Identifier: MIT\nx = 1  # counted\n")
        self.assertEqual(ar.count_comments(source), 1)

    def test_a_comment_that_mentions_global_state_still_counts(self):
        self.assertEqual(ar.count_comments("# global state lives here\n"), 1)


try:
    import pygments  # noqa: F401
except ImportError:
    pygments = None


@unittest.skipIf(pygments is None, "Pygments is needed for languages other than Python")
class OtherLanguages(unittest.TestCase):
    def lines(self, path, source):
        return [line for line, _ in ar.comments(path, source)]

    def test_javascript_skips_strings_templates_regexes_and_pragmas(self):
        source = ("const s = '// no'; // one\n/* two\n   three */\n"
                  "const r = /\\/\\//g; // eslint-disable-line no-x\n"
                  "// Why: browsers reorder this.\nconst t = `${x} // no`;\n")
        self.assertEqual(self.lines("a.mjs", source), [1, 2, 3])

    def test_sql_counts_line_and_block_comments_outside_strings(self):
        source = "-- one\nSELECT '-- no' AS x; /* two\nthree */\n/* Why: old rows stay. */\n"
        self.assertEqual(self.lines("m.sql", source), [1, 2, 3])

    def test_templates_count_html_and_jinja_comments_but_not_strings(self):
        source = ("<p>{# one #}</p>\n<!-- two\nthree -->\n<script>// four\n"
                  "let a = '<!-- no -->';</script>\n{# Why: shown twice. #}\n")
        self.assertEqual(self.lines("page.html", source), [1, 2, 3, 4])

    def test_shell_skips_the_shebang_strings_and_shellcheck(self):
        source = "#!/bin/bash\necho '# no' # one\n# shellcheck disable=SC2086\n"
        self.assertEqual(self.lines("run.sh", source), [2])

    def test_an_unknown_suffix_is_an_error(self):
        with self.assertRaises(ar.RatchetError):
            list(ar.comments("a.rb", "# x\n"))


class CountToDelete(unittest.TestCase):
    def test_counts_decorators_and_param_marks(self):
        source = (
            "import pytest\n"
            "@pytest.mark.to_delete(issue=12)\n"
            "def test_a(): pass\n"
            "@pytest.mark.parametrize('x', [pytest.param(1, marks=pytest.mark.to_delete(issue=13))])\n"
            "def test_b(x): pass\n")
        self.assertEqual(ar.count_to_delete(source, "t.py"), 2)

    def test_marker_without_an_issue_number_is_an_error(self):
        for bad in ("@pytest.mark.to_delete\n", "@pytest.mark.to_delete()\n",
                    "@pytest.mark.to_delete(issue='12')\n", "@pytest.mark.to_delete(issue=0)\n",
                    "@pytest.mark.to_delete(issue=True)\n"):
            with self.subTest(bad=bad), self.assertRaises(ar.RatchetError):
                ar.count_to_delete("import pytest\n" + bad + "def test_a(): pass\n", "t.py")

    def test_other_markers_do_not_count(self):
        source = "import pytest\n@pytest.mark.slow\ndef test_a(): pass\n"
        self.assertEqual(ar.count_to_delete(source, "t.py"), 0)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cwd = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.cwd)
        subprocess.run(["git", "init", "-q"], check=True)
        (self.root / "src").mkdir()
        (self.root / "other").mkdir()
        self.write("src/a.py", "# one\n# two\nx = 1\n")
        self.write("other/skip.py", "# outside the roots\n")

    def write(self, path, text):
        (self.root / path).write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", path], check=True)

    def run_cli(self, *args):
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = ar.main(list(args))
        return code, err.getvalue()

    def test_full_ratchet_cycle(self):
        self.assertEqual(self.run_cli("init", "--roots", "src")[0], 0)
        self.assertEqual(self.run_cli("check")[0], 0)
        self.assertEqual(self.run_cli("init", "--roots", "src")[0], 2)

        self.write("src/a.py", "# one\n# two\n# three\nx = 1\n")
        code, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("src/a.py has 3, baseline 2", err)
        self.assertEqual(self.run_cli("update")[0], 1)

        self.write("src/b.py", "# new file\n")
        self.write("src/a.py", "# Why: kept as a one-liner.\nx = 1\n")
        code, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("src/b.py has 1, baseline 0", err)

        self.write("src/b.py", "y = 2\n")
        code, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("fell below the baseline", err)
        self.assertEqual(self.run_cli("update")[0], 0)
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_a_version_1_baseline_still_checks_python(self):
        self.assertEqual(self.run_cli("init", "--roots", "src")[0], 0)
        data = json.loads(Path(".agents/audit-baseline.json").read_text())
        data["version"] = 1
        del data["languages"]
        Path(".agents/audit-baseline.json").write_text(json.dumps(data))
        self.assertEqual(self.run_cli("check")[0], 0)

    @unittest.skipIf(pygments is None, "Pygments is needed for languages other than Python")
    def test_extend_adds_a_language_without_raising_the_others(self):
        self.write("src/q.sql", "-- one\n-- two\nSELECT 1;\n")
        self.assertEqual(self.run_cli("init", "--roots", "src")[0], 0)
        self.write("src/a.py", "# one\n# two\n# three\nx = 1\n")
        self.assertEqual(self.run_cli("extend", "--languages", "sql")[0], 0)
        code, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("src/a.py has 3, baseline 2", err)
        data = json.loads(Path(".agents/audit-baseline.json").read_text())
        self.assertEqual((data["languages"], data["comments"]["src/q.sql"]), (["py", "sql"], 2))

    def test_explain_lists_each_counted_line(self):
        self.assertEqual(self.run_cli("init", "--roots", "src")[0], 0)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(ar.main(["report", "--explain", "src/a.py"]), 0)
        self.assertEqual(out.getvalue().splitlines(), ["src/a.py:1: # one", "src/a.py:2: # two"])

    def test_check_without_a_baseline_fails_clearly(self):
        code, err = self.run_cli("check")
        self.assertEqual(code, 2)
        self.assertIn("run init first", err)


if __name__ == "__main__":
    unittest.main()
