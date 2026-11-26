# SPDX-License-Identifier: MIT
"""Tests of tools/check_workflows.py."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "tools", "check_workflows.py")
E = "${{"


class CheckWorkflows(unittest.TestCase):
    def run_on(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "w.yml")
            with open(path, "w") as f:
                f.write(text)
            r = subprocess.run([sys.executable, TOOL, path], capture_output=True, text=True,
                               env={"PATH": os.environ.get("PATH", "")})
            return r.returncode, r.stdout + r.stderr

    def test_refuses_the_old_tag_line(self):
        code, log = self.run_on(
            "jobs:\n  a:\n    steps:\n"
            "      - name: The tag names the package\n"
            "        if: startsWith(github.ref, 'refs/tags/templates-')\n"
            f'        run: test -f "build/{E} github.ref_name }}}}.zip"\n')
        self.assertEqual(code, 1, log)
        self.assertIn("w.yml:6:", log)

    def test_refuses_a_block_with_head_ref_and_event(self):
        for expr in ("github.head_ref", "github.event.pull_request.title"):
            code, log = self.run_on(
                "steps:\n  - run: |\n      echo start\n"
                f"      echo {E} {expr} }}}}\n  - uses: x/y@v1\n")
            self.assertEqual(code, 1, log)
            self.assertIn("w.yml:4:", log)

    def test_passes_env_and_safe_values(self):
        code, log = self.run_on(
            "steps:\n  - name: ok\n    env:\n"
            f"      TAG: {E} github.ref_name }}}}\n"
            "    run: |\n      test -n \"$TAG\"\n"
            f"      echo {E} matrix.board }}}}\n"
            f"  - name: later\n    with:\n      title: {E} github.event.pull_request.title }}}}\n")
        self.assertEqual(code, 0, log)

    def test_repository_workflows_pass(self):
        r = subprocess.run([sys.executable, TOOL], cwd=ROOT, capture_output=True, text=True,
                           env={"PATH": os.environ.get("PATH", "")})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
