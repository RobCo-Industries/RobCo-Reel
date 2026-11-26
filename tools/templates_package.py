#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Writes the templates package, templates-<version>.zip.

    templates_package.py --print-version --version-header H
    templates_package.py --out DIR --version-header H --built-from REPO=COMMIT
        --tracked LIST [--root DIR] [--forbid TEXT]... [--user NAME]...

The layout is RobCo-Core's docs/spec/SDK_PACKAGE.md, "The templates
package": sdk.json, templates.json, one folder per template and
LICENSES/MIT.txt, which is this repository's LICENSE.

LIST holds the files git tracks, NUL-separated, as `git ls-files -z`
writes them. Only those files go in, so an untracked file never does.
The version is REEL_VERSION_MAJOR, MINOR and PATCH of H.

The archive bytes depend only on the files and the arguments. The zip
writer is the one of Pip-OS's tools/sdk_package.py: sdk.json first, then
the entries in byte order of their names, stored, dated 1980-01-01 00:00,
mode 0644, no extra field.

Before it writes, it searches every file, sdk.json included, for each
--forbid text and each --user name in the forms /home/NAME, /Users/NAME,
\\Users\\NAME and NAME@, and refuses the package on a hit. A text under 4
characters is not searched, and a note says so.

Exits 0 with the archive path on stdout, 1 on a refusal. Stdlib only.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "external", "pip-os", "tools"))
import fill_template  # noqa: E402
import sdk_package  # noqa: E402

NAME = "templates"
REPO = "RobCo-Reel"
MANIFEST = "sdk.json"
INDEX = "templates.json"
LICENCE_SRC = "LICENSE"
LICENCE_PATH = "LICENSES/MIT.txt"
# SDK_PACKAGE.md, "The templates package": these three formats, each 1.
FORMATS = {"project": 1, "scenario": 1, "templates": 1}
# SDK_PACKAGE.md, "Licences": MIT for every template file.
LICENCES = [{"paths": [""], "spdx": "MIT"}]
# Every template, by id. SDK_PACKAGE.md, "The holotape-c template".
# Which files are substituted comes from tools/fill_template.py, so the
# package and Reel's own tests fill a template the same way.
TEMPLATES = {
    "holotape-c": {
        "title": "Holotape in C",
        "description": "A holotape in C that draws one screen and waits for SELECT.",
        "kind": "holotape",
    },
}
FORBID_MIN = 4
USER_FORMS = ("/home/{}", "/Users/{}", "\\Users\\{}", "{}@")


class Error(Exception):
    """A refusal, with its message."""


def version_of(header):
    with open(header, encoding="utf-8") as f:
        text = f.read()
    parts = []
    for p in ("MAJOR", "MINOR", "PATCH"):
        m = re.findall(rf"^#define\s+REEL_VERSION_{p}\s+(0|[1-9][0-9]{{0,4}})\s*$", text, re.M)
        if len(m) != 1 or int(m[0]) > 65535:
            raise Error(f"{header}: want one #define REEL_VERSION_{p} from 0 to 65535")
        parts.append(m[0])
    return ".".join(parts)


def read_tracked(path):
    with open(path, "rb") as f:
        raw = f.read()
    names = [n.decode("utf-8") for n in raw.split(b"\0") if n]
    if not names:
        raise Error(f"{path}: git listed no file")
    return set(names)


def layout(tracked):
    """(templates.json document, {archive path: source path})."""
    sources = {}
    if LICENCE_SRC not in tracked:
        raise Error(f"{LICENCE_SRC} is not tracked")
    sources[LICENCE_PATH] = LICENCE_SRC
    known = set(TEMPLATES) | {"README.md"}
    for t in sorted(tracked):
        if t.startswith("templates/") and t.split("/")[1] not in known:
            raise Error(f"{t}: no template {t.split('/')[1]!r} in TEMPLATES")
    doc = {"format": 1, "templates": []}
    for tid in sorted(TEMPLATES, key=lambda s: s.encode("utf-8")):
        prefix = f"templates/{tid}/"
        paths = sorted((t[len(prefix):] for t in tracked if t.startswith(prefix)),
                       key=lambda s: s.encode("utf-8"))
        if not paths:
            raise Error(f"{prefix}: git tracks no file")
        subst = fill_template.SUBSTITUTE.get(tid)
        if subst is None or not subst <= set(paths):
            raise Error(f"{tid}: its substituted files are not all tracked")
        files = []
        for p in paths:
            why = sdk_package.name_problem(p)
            if why:
                raise Error(f"{prefix}{p}: the path {why}")
            files.append({"path": p, "substitute": p in subst})
            sources[f"{tid}/{p}"] = prefix + p
        doc["templates"].append({"id": tid, **TEMPLATES[tid], "files": files})
    return doc, sources


def json_bytes(doc):
    return (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def forbidden(forbid, users):
    texts, notes = [], []
    for t in list(forbid) + [f.format(u) for u in users for f in USER_FORMS]:
        if len(t) < FORBID_MIN:
            notes.append(f"note: {t!r} is under {FORBID_MIN} characters, not searched")
        elif t not in texts:
            texts.append(t)
    return texts, notes


def build(args):
    version = version_of(args.version_header)
    repo, _, commit = args.built_from.partition("=")
    if repo != REPO or not sdk_package.HEX40.fullmatch(commit):
        raise Error(f"--built-from {args.built_from}: want {REPO}=<40 lower case hex digits>")
    doc, sources = layout(read_tracked(args.tracked))
    data = {INDEX: json_bytes(doc)}
    for path, src in sources.items():
        full = os.path.join(args.root, src)
        if os.path.islink(full) or not os.path.isfile(full):
            raise Error(f"{src}: not a regular file")
        with open(full, "rb") as f:
            data[path] = f.read()
    order = sorted(data, key=lambda p: p.encode("utf-8"))
    files = [{"path": p, "size": len(data[p]), "sha256": sdk_package.sha256(data[p])}
             for p in order]
    manifest = json_bytes({
        "format": 1,
        "name": NAME,
        "version": version,
        "built_from": [{"repo": REPO, "commit": commit}],
        "formats": FORMATS,
        "requires": [],
        "licences": LICENCES,
        "files": files,
    })
    texts, notes = forbidden(args.forbid, args.user)
    for n in notes:
        print(n, file=sys.stderr)
    hits = [f"{p}: holds {t!r}" for p, b in [(MANIFEST, manifest)] + [(p, data[p]) for p in order]
            for t in texts if t.encode("utf-8") in b]
    if hits:
        raise Error("a machine text is in the package: " + "; ".join(hits))
    os.makedirs(args.out, exist_ok=True)
    out = os.path.join(args.out, f"{NAME}-{version}.zip")
    sdk_package.write_zip(out, [(MANIFEST, manifest)] + [(p, data[p]) for p in order])
    print(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--print-version", action="store_true",
                    help="print the version of --version-header and stop")
    ap.add_argument("--version-header", required=True)
    ap.add_argument("--out")
    ap.add_argument("--built-from")
    ap.add_argument("--tracked")
    ap.add_argument("--root", default=".")
    ap.add_argument("--forbid", action="append", default=[])
    ap.add_argument("--user", action="append", default=[])
    args = ap.parse_args(argv)
    if not args.print_version and not (args.out and args.built_from and args.tracked):
        ap.error("--out, --built-from and --tracked are required to build")
    try:
        if args.print_version:
            print(version_of(args.version_header))
        else:
            build(args)
    except (Error, OSError, UnicodeDecodeError) as e:
        print(f"templates-package: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
