# SPDX-License-Identifier: MIT
"""Tests of tools/templates_package.py and of make templates-package's git calls."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, "tools", "templates_package.py")
HEADER = os.path.join(ROOT, "reel", "include", "reel", "reel.h")
CHECKER = os.path.join(ROOT, "external", "pip-os", "tools", "sdk_package.py")
COMMIT = "0123456789abcdef0123456789abcdef01234567"


def zip_name(header=HEADER):
    """The archive's name, from the version the tool reads in the header."""
    r = subprocess.run([sys.executable, TOOL, "--print-version", "--version-header", header],
                       capture_output=True, text=True, check=True, env={"PATH": os.environ["PATH"]})
    return f"templates-{r.stdout.strip()}.zip"

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

    def run_tool(self, tracked=TRACKED, root=ROOT, extra=(), header=HEADER):
        lst = os.path.join(self.tmp, "list")
        with open(lst, "wb") as f:
            f.write(b"".join(t.encode() + b"\0" for t in tracked))
        r = subprocess.run([sys.executable, TOOL, "--out", self.out, "--version-header", header,
                            "--built-from", f"RobCo-Reel={COMMIT}", "--tracked", lst,
                            "--root", root, *extra],
                           capture_output=True, text=True, env={"PATH": os.environ["PATH"]})
        return r.returncode, r.stdout + r.stderr

    def check(self, zpath):
        r = subprocess.run([sys.executable, CHECKER, "check", zpath, "--skip-short", "--forbid", ROOT],
                           capture_output=True, text=True, env={"PATH": os.environ["PATH"]})
        return r.returncode, r.stdout + r.stderr

    def test_checker_passes_the_package_and_refuses_a_spoiled_copy(self):
        code, log = self.run_tool()
        self.assertEqual(code, 0, log)
        zpath = os.path.join(self.out, zip_name())
        code, log = self.check(zpath)
        self.assertEqual(code, 0, log)
        spoiled = os.path.join(self.tmp, "spoiled", zip_name())
        os.makedirs(os.path.dirname(spoiled))
        shutil.copyfile(zpath, spoiled)
        with zipfile.ZipFile(spoiled) as z:
            info = z.getinfo("holotape-c/src/main.c")
        with open(spoiled, "r+b") as f:
            f.seek(info.header_offset + 26)
            name_len, extra_len = int.from_bytes(f.read(2), "little"), int.from_bytes(f.read(2), "little")
            at = info.header_offset + 30 + name_len + extra_len
            f.seek(at)
            byte = f.read(1)
            f.seek(at)
            f.write(bytes([byte[0] ^ 0x01]))
        code, log = self.check(spoiled)
        self.assertEqual(code, 1, log)
        self.assertIn("holotape-c/src/main.c", log)

    def test_layout_and_manifest(self):
        code, log = self.run_tool()
        self.assertEqual(code, 0, log)
        zpath = os.path.join(self.out, zip_name())
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
            with open(os.path.join(self.out, zip_name()), "rb") as f:
                sums.append(hashlib.sha256(f.read()).hexdigest())
        self.assertEqual(sums[0], sums[1])

    def test_archive_follows_the_version_header(self):
        header = os.path.join(self.tmp, "reel.h")
        with open(HEADER) as f:
            text = f.read()
        for p, n in (("MAJOR", 7), ("MINOR", 8), ("PATCH", 9)):
            text = re.sub(rf"^(#define\s+REEL_VERSION_{p}\s+)\d+", rf"\g<1>{n}", text, flags=re.M)
        with open(header, "w") as f:
            f.write(text)
        self.assertEqual(zip_name(header), "templates-7.8.9.zip")
        code, log = self.run_tool(header=header)
        self.assertEqual(code, 0, log)
        self.assertEqual(log.strip(), os.path.join(self.out, "templates-7.8.9.zip"))
        with zipfile.ZipFile(os.path.join(self.out, zip_name(header))) as z:
            self.assertEqual(json.loads(z.read("sdk.json"))["version"], "7.8.9")

    def test_untracked_file_stays_out(self):
        code, log = self.run_tool(tracked=[t for t in TRACKED if not t.endswith("icon.pbm")])
        self.assertEqual(code, 0, log)
        with zipfile.ZipFile(os.path.join(self.out, zip_name())) as z:
            self.assertNotIn("holotape-c/icon.pbm", z.namelist())

    def test_refuses_a_forbidden_text(self):
        code, log = self.run_tool(extra=("--forbid", "draws one screen"))
        self.assertEqual(code, 1)
        self.assertIn("templates.json: holds 'draws one screen'", log)
        self.assertFalse(os.path.exists(os.path.join(self.out, zip_name())))

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
            self.assertFalse(os.path.exists(os.path.join(tmp, "build", zip_name())))


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          check=True, capture_output=True, env={"PATH": os.environ["PATH"]}).stdout


class MakeBuildFolder(unittest.TestCase):
    """The clean check leaves out a BUILD inside the checkout, in a scratch clone."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.repo = os.path.join(tmp.name, "reel")
        # Local files only: the clone takes HEAD, the work tree's Makefile, and
        # the submodules as plain files from git archive.
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", ROOT, cls.repo], check=True,
                       env={"PATH": os.environ["PATH"]})
        shutil.copy(os.path.join(ROOT, "Makefile"), os.path.join(cls.repo, "Makefile"))
        git(cls.repo, "rm", "-q", "--cached", "external/pip-os")
        for sub in ("external/pip-os", "external/pip-os/external/robco-core"):
            dest = os.path.join(cls.repo, sub)
            os.makedirs(dest, exist_ok=True)
            data = git(os.path.join(ROOT, sub), "archive", "HEAD")
            subprocess.run(["tar", "-x", "-C", dest], input=data, check=True)
        git(cls.repo, "add", "-A")
        git(cls.repo, "commit", "-q", "-m", "scratch")

    def make(self, build):
        return subprocess.run(["make", "--no-print-directory", "-C", self.repo, "templates-package",
                               f"BUILD={build}"], capture_output=True, text=True,
                              env={"PATH": os.environ["PATH"], "HOME": os.path.join(self.repo, "nohome")})

    def tearDown(self):
        git(self.repo, "clean", "-qfdx")

    def digest(self, build):
        path = os.path.join(self.repo, build, zip_name())
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def test_out_builds_on_a_clean_tree_with_the_default_bytes(self):
        r = self.make("out")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = self.digest("out")
        git(self.repo, "clean", "-qfdx")
        r = self.make("build")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out, self.digest("build"))

    def test_untracked_file_inside_out_passes(self):
        os.makedirs(os.path.join(self.repo, "out"))
        open(os.path.join(self.repo, "out", "stray"), "w").close()
        r = self.make("out")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_untracked_file_outside_out_fails(self):
        open(os.path.join(self.repo, "stray"), "w").close()
        r = self.make("out")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("?? stray", r.stderr)

    def test_dash_name_is_a_literal_path(self):
        open(os.path.join(self.repo, "stray"), "w").close()
        r = self.make("-x*")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("?? stray", r.stderr)

    def test_checkout_itself_is_refused(self):
        r = self.make(".")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("is the checkout itself", r.stderr)

    def test_folder_with_tracked_files_is_refused(self):
        r = self.make("templates")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("holds tracked files", r.stderr)


if __name__ == "__main__":
    unittest.main()
