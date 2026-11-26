# SPDX-License-Identifier: MIT
"""make check-workflows runs Pip-OS's guard: a pasted expression fails it."""

import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CheckWorkflowsWiring(unittest.TestCase):
    def run_make(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "scratch.yml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return subprocess.run(
                ["make", "-s", "-C", ROOT, "check-workflows", "WORKFLOWS=" + path],
                capture_output=True, text=True)

    def test_pasted_ref_fails(self):
        r = self.run_make('jobs:\n  a:\n    steps:\n      - run: echo "${{ github.ref }}"\n')
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("scratch.yml", r.stdout + r.stderr)

    def test_env_shape_passes(self):
        r = self.run_make('jobs:\n  a:\n    steps:\n      - env:\n          REF: ${{ github.ref }}\n        run: echo "$REF"\n')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
