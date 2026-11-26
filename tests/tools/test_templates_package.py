# SPDX-License-Identifier: MIT
"""Tests of tools/templates_package.py and of make templates-package's git calls."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "tools", "templates_package.py")
HEADER = os.path.join(ROOT, "reel", "include", "reel", "reel.h")
COMMIT = "0123456789abcdef0123456789abcdef01234567"

# SDK_PACKAGE.md, "The holotape-c template": the templates.json it gives.
SPEC_INDEX = {
    "format": 1,
    "templates": [{
        "id": "holotape-c",
        "title": "Holotape in C",
        "description": "A holotape in C that draws one screen and waits for SELECT.",
        "kind": "holotape",
        "files": [
            {"path": "icon.pbm", "substitute": False},
            {"path": "robco.toml", "substitute": True},
            {"path": "src/main.c", "substitute": False},
            {"path": "tests/golden/start/ready.png", "substitute": False},
            {"path": "tests/start.toml", "substitute": False},
        ],
    }],
}
TRACKED = ["LICENSE", "templates/README.md", "templates/holotape-c/icon.pbm",
           "templates/holotape-c/robco.toml", "templates/holotape-c/src/main.c",
           "templates/holotape-c/tests/golden/start/ready.png",
           "templates/holotape-c/tests/start.toml"]


class TemplatesPackage(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.out = os.path.join(self.tmp, "out")

    def run_tool(self, tracked=TRACKED, root=ROOT, extra=()):
        lst = os.path.join(self.tmp, "list")
        with open(lst, "wb") as f:
            f.write(b"".join(t.encode() + b"\0" for t in tracked))
        r = subprocess.run([sys.executable, TOOL, "--out", self.out, "--version-header", HEADER,
                            "--built-from", f"RobCo-Reel={COMMIT}", "--tracked", lst,
                            "--root", root, *extra],
                           capture_output=True, text=True, env={"PATH": os.environ["PATH"]})
        return r.returncode, r.stdout + r.stderr

    def test_layout_and_manifest(self):
        code, log = self.run_tool()
        self.assertEqual(code, 0, log)
        zpath = os.path.join(self.out, "templates-0.1.0.zip")
        with zipfile.ZipFile(zpath) as z:
            names = z.namelist()
            doc = json.loads(z.read("sdk.json"))
            self.assertEqual(json.loads(z.read("templates.json")), SPEC_INDEX)
            for e in doc["files"]:
                self.assertEqual(hashlib.sha256(z.read(e["path"])).hexdigest(), e["sha256"])
            with open(os.path.join(ROOT, "LICENSE"), "rb") as f:
                self.assertEqual(z.read("LICENSES/MIT.txt"), f.read())
            self.assertTrue(all(i.compress_type == zipfile.ZIP_STORED for i in z.infolist()))
        self.assertEqual(names[0], "sdk.json")
        paths = [e["path"] for e in doc["files"]]
        self.assertEqual(paths, sorted(paths, key=str.encode))
        self.assertEqual(set(names), set(paths) | {"sdk.json"})
        self.assertNotIn("templates/README.md", names)
        self.assertEqual(doc["name"], "templates")
        self.assertEqual(doc["formats"], {"project": 1, "scenario": 1, "templates": 1})
        self.assertEqual(doc["requires"], [])
        self.assertEqual(doc["built_from"], [{"repo": "RobCo-Reel", "commit": COMMIT}])
        self.assertEqual(doc["licences"], [{"paths": [""], "spdx": "MIT"}])
        for absent in ("abi", "tools", "firmware"):
            self.assertNotIn(absent, doc)

    def test_same_bytes_twice(self):
        sums = []
        for _ in range(2):
            self.assertEqual(self.run_tool()[0], 0)
            with open(os.path.join(self.out, "templates-0.1.0.zip"), "rb") as f:
                sums.append(hashlib.sha256(f.read()).hexdigest())
        self.assertEqual(sums[0], sums[1])

    def test_untracked_file_stays_out(self):
        code, log = self.run_tool(tracked=[t for t in TRACKED if not t.endswith("icon.pbm")])
        self.assertEqual(code, 0, log)
        with zipfile.ZipFile(os.path.join(self.out, "templates-0.1.0.zip")) as z:
            self.assertNotIn("holotape-c/icon.pbm", z.namelist())

    def test_refuses_a_forbidden_text(self):
        code, log = self.run_tool(extra=("--forbid", "draws one screen"))
        self.assertEqual(code, 1)
        self.assertIn("templates.json: holds 'draws one screen'", log)
        self.assertFalse(os.path.exists(os.path.join(self.out, "templates-0.1.0.zip")))

    def test_refuses_a_user_home(self):
        root = os.path.join(self.tmp, "root")
        shutil.copytree(os.path.join(ROOT, "templates"), os.path.join(root, "templates"))
        shutil.copy(os.path.join(ROOT, "LICENSE"), root)
        with open(os.path.join(root, "templates/holotape-c/src/main.c"), "ab") as f:
            f.write(b"/* /home/someone/x */\n")
        code, log = self.run_tool(root=root, extra=("--user", "someone"))
        self.assertEqual(code, 1)
        self.assertIn("holotape-c/src/main.c: holds '/home/someone'", log)

    def test_refuses_an_unknown_template(self):
        code, log = self.run_tool(tracked=TRACKED + ["templates/other/a.c"])
        self.assertEqual(code, 1)
        self.assertIn("no template 'other'", log)

    def test_refuses_without_licence(self):
        code, log = self.run_tool(tracked=TRACKED[1:])
        self.assertEqual(code, 1)
        self.assertIn("LICENSE is not tracked", log)

    def test_refuses_an_empty_list(self):
        code, log = self.run_tool(tracked=[])
        self.assertEqual(code, 1)
        self.assertIn("git listed no file", log)


class MakeGitCalls(unittest.TestCase):
    """make templates-package stops with git's own message when git fails."""

    def test_git_failure_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = os.path.join(tmp, "git")
            with open(fake, "w") as f:
                f.write("#!/bin/sh\necho 'fatal: detected dubious ownership' >&2\nexit 128\n")
            os.chmod(fake, 0o755)
            r = subprocess.run(["make", "--no-print-directory", "-C", ROOT, "templates-package",
                                f"BUILD={tmp}/build"],
                               capture_output=True, text=True,
                               env={"PATH": tmp + os.pathsep + os.environ["PATH"]})
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("fatal: detected dubious ownership", r.stderr)
            self.assertIn("templates-package: git status failed", r.stderr)
            self.assertFalse(os.path.exists(os.path.join(tmp, "build", "templates-0.1.0.zip")))


if __name__ == "__main__":
    unittest.main()
