# SPDX-License-Identifier: MIT
"""Tests of tools/check_licence.py on small trees in a temporary folder."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "tools", "check_licence.py")
TAG = "SPDX-" + "License-Identifier:"
GOOD_C = f"/* {TAG} MIT */\nint x;\n"


class CheckLicence(unittest.TestCase):
    def run_on(self, files):
        with tempfile.TemporaryDirectory() as root:
            for rel, text in files.items():
                path = os.path.join(root, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(text)
            r = subprocess.run([sys.executable, TOOL, root], capture_output=True, text=True,
                               env={"PATH": os.environ.get("PATH", "")})
            return r.returncode, r.stdout + r.stderr

    def assert_fails(self, files, needle):
        rc, out = self.run_on(files)
        self.assertEqual(rc, 1, out)
        self.assertIn(needle, out)

    def test_clean_tree_passes(self):
        rc, out = self.run_on({"a.c": GOOD_C, "inc/a.h": f"// {TAG} MIT\n",
                               "README.md": "MIT, no other licence.\n",
                               "x.py": f"# {TAG} MIT\n"})
        self.assertEqual(rc, 0, out)

    def test_gpl_notice_fails(self):
        self.assert_fails({"NOTES.txt": "Under the GNU General" + " Public License.\n"},
                          "NOTES.txt: carries a GNU licence notice")

    def test_lgpl_notice_fails_in_any_case(self):
        self.assert_fails({"a.md": "gnu lesser general" + " public license\n"},
                          "a.md: carries a GNU licence notice")

    def test_other_spdx_fails(self):
        self.assert_fails({"a.py": f"# {TAG} Apache-2.0\n"}, "a.py:1: SPDX identifier is 'Apache-2.0'")

    def test_spdx_expression_fails(self):
        self.assert_fails({"a.c": f"/* {TAG} MIT OR GPL-2.0-only */\n"},
                          "SPDX identifier is 'MIT OR GPL-2.0-only'")

    def test_c_without_spdx_fails(self):
        self.assert_fails({"src/a.c": "int x;\n"}, "src/a.c:1: does not start with an MIT SPDX line")

    def test_header_with_spdx_on_line_two_fails(self):
        self.assert_fails({"a.h": "\n" + GOOD_C}, "a.h:1: does not start")

    def test_external_and_build_are_skipped(self):
        bad = "GNU General" + " Public License\n"
        rc, out = self.run_on({"external/x/a.c": bad, "build/a.c": bad, "ok.c": GOOD_C})
        self.assertEqual(rc, 0, out)

    def test_this_repository_passes(self):
        r = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
