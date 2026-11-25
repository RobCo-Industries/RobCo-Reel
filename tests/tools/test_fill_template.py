# SPDX-License-Identifier: MIT
"""Tests of tools/fill_template.py, on the real template and on small trees."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "tools", "fill_template.py")
TEMPLATE = os.path.join(ROOT, "templates", "holotape-c")

sys.path.insert(0, os.path.join(ROOT, "tools"))
import fill_template  # noqa: E402

# The five files the spec gives holotape-c, SDK_PACKAGE.md, "The holotape-c template".
FILES = ["icon.pbm", "robco.toml", "src/main.c", "tests/golden/start/ready.png",
         "tests/start.toml"]


def snapshot(root):
    out = {}
    for d, _, files in os.walk(root):
        for name in files:
            path = os.path.join(d, name)
            with open(path, "rb") as f:
                out[os.path.relpath(path, root)] = f.read()
    return out


class FillTemplate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_tool(self, *args):
        r = subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True,
                           env={"PATH": os.environ.get("PATH", "")})
        return r.returncode, r.stdout + r.stderr

    def write(self, root, files):
        for rel, data in files.items():
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)

    def test_template_holds_the_spec_files(self):
        self.assertEqual(fill_template.template_files(TEMPLATE), FILES)

    def test_fills_name_and_copies_the_rest(self):
        before = snapshot(TEMPLATE)
        dest = os.path.join(self.tmp.name, "p")
        rc, out = self.run_tool(TEMPLATE, dest, "MYTAPE")
        self.assertEqual(rc, 0, out)
        self.assertEqual(snapshot(TEMPLATE), before)
        got = snapshot(dest)
        self.assertEqual(sorted(k.replace(os.sep, "/") for k in got), FILES)
        toml = before["robco.toml"]
        self.assertIn(b'name = "@NAME@"', toml)
        self.assertEqual(got["robco.toml"], toml.replace(b"@NAME@", b"MYTAPE"))
        for rel in FILES[2:] + FILES[:1]:
            key = rel.replace("/", os.sep)
            self.assertEqual(got[key], before[key], rel)

    def test_unsubstituted_file_keeps_its_tokens(self):
        src = os.path.join(self.tmp.name, "t")
        self.write(src, {"a.toml": b"x = \"@NAME@\"\r\n", "b.txt": b"@NAME@ @OTHER@\n"})
        dest = os.path.join(self.tmp.name, "p")
        fill_template.fill(src, dest, "AB", {"a.toml"})
        got = snapshot(dest)
        self.assertEqual(got["a.toml"], b"x = \"AB\"\r\n")
        self.assertEqual(got["b.txt"], b"@NAME@ @OTHER@\n")

    def test_unknown_token_fails_and_writes_nothing(self):
        src = os.path.join(self.tmp.name, "t")
        self.write(src, {"a.toml": b"@NAME@ @TITLE@\n"})
        dest = os.path.join(self.tmp.name, "p")
        with self.assertRaisesRegex(fill_template.FillError, "templates: token: a.toml: @TITLE@"):
            fill_template.fill(src, dest, "AB", {"a.toml"})
        self.assertFalse(os.path.exists(dest))

    def symlink_or_skip(self, target, link, is_dir):
        try:
            os.symlink(target, link, target_is_directory=is_dir)
        except (OSError, NotImplementedError) as e:
            self.skipTest(f"cannot make links here: {e}")

    def test_linked_file_fails(self):
        src = os.path.join(self.tmp.name, "t")
        self.write(src, {"a.toml": b"x\n", "real/b.txt": b"b\n"})
        self.symlink_or_skip(os.path.join(src, "real", "b.txt"), os.path.join(src, "b.txt"), False)
        dest = os.path.join(self.tmp.name, "p")
        with self.assertRaisesRegex(fill_template.FillError, "not a regular file"):
            fill_template.fill(src, dest, "AB", {"a.toml"})
        self.assertFalse(os.path.exists(dest))

    def test_linked_folder_fails(self):
        src = os.path.join(self.tmp.name, "t")
        self.write(src, {"a.toml": b"x\n"})
        other = os.path.join(self.tmp.name, "other")
        self.write(other, {"c.txt": b"c\n"})
        self.symlink_or_skip(other, os.path.join(src, "sub"), True)
        dest = os.path.join(self.tmp.name, "p")
        with self.assertRaisesRegex(fill_template.FillError, "not a regular folder"):
            fill_template.fill(src, dest, "AB", {"a.toml"})
        self.assertFalse(os.path.exists(dest))

    def test_bad_names_fail(self):
        for name in ("", "lower", "NINECHARS", "A~1", "A B"):
            dest = os.path.join(self.tmp.name, "p")
            rc, out = self.run_tool(TEMPLATE, dest, name)
            self.assertEqual(rc, 1, name)
            self.assertIn("bad name", out)
            self.assertFalse(os.path.exists(dest))

    def test_dest_inside_template_fails(self):
        before = snapshot(TEMPLATE)
        rc, out = self.run_tool(TEMPLATE, os.path.join(TEMPLATE, "build"), "AB")
        self.assertEqual(rc, 1, out)
        self.assertIn("inside the template folder", out)
        self.assertEqual(snapshot(TEMPLATE), before)

    def test_existing_dest_fails(self):
        rc, out = self.run_tool(TEMPLATE, self.tmp.name, "AB")
        self.assertEqual(rc, 1, out)
        self.assertIn("already exists", out)


if __name__ == "__main__":
    unittest.main()
