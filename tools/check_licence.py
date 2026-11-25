#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Holds the licence line of this repository.

Every file here may end up inside a tape someone else writes, so all of
it is MIT. The check fails when:

- a file carries a GNU licence notice: GPL, LGPL or AGPL;
- a file carries an SPDX licence identifier other than MIT;
- a .c or .h file does not start with an SPDX line that says MIT.

    tools/check_licence.py [root]

root defaults to the repository root. It skips .git, external/ (the
Pip-OS submodule, which has its own licence), build output, Python caches
and the local files of coding assistants. It does not call git, so it
runs in the CI container. Exits 0 when clean, 1 on a finding.
"""

import os
import re
import sys

# Split so that this file does not match itself.
SPDX_TAG = "SPDX-" + "License-Identifier:"
GNU_NOTICES = (
    "GNU General" + " Public License",
    "GNU Lesser General" + " Public License",
    "GNU Library General" + " Public License",
    "GNU Affero General" + " Public License",
)
SPDX_RE = re.compile(re.escape(SPDX_TAG) + r"[ \t]*([^\r\n]*)")
FIRST_LINE_RE = re.compile(
    r"^(?:/\*[ \t]*" + re.escape(SPDX_TAG) + r"[ \t]*MIT[ \t]*\*/|//[ \t]*"
    + re.escape(SPDX_TAG) + r"[ \t]*MIT)[ \t]*\r?$")

SKIP_DIRS = {".git", "external", "build", ".venv", "__pycache__", ".pytest_cache", ".claude"}
SKIP_FILES = {"CLAUDE.md", "AGENTS.md"}
C_EXT = (".c", ".h")


def spdx_value(raw):
    """The identifier with a closing comment marker removed."""
    value = raw.strip()
    for end in ("*/", "-->"):
        if value.endswith(end):
            value = value[: -len(end)].strip()
    return value


def check_file(path, rel):
    with open(path, "rb") as f:
        text = f.read().decode("utf-8", errors="replace")
    problems = []
    for notice in GNU_NOTICES:
        if notice.lower() in text.lower():
            problems.append(f"{rel}: carries a GNU licence notice: {notice}")
    for n, line in enumerate(text.splitlines(), 1):
        m = SPDX_RE.search(line)
        if m and spdx_value(m.group(1)) != "MIT":
            problems.append(f"{rel}:{n}: SPDX identifier is "
                            f"'{spdx_value(m.group(1))}', not MIT")
    if rel.endswith(C_EXT):
        first = text.split("\n", 1)[0]
        if not FIRST_LINE_RE.match(first):
            problems.append(f"{rel}:1: does not start with an MIT SPDX line, "
                            f"such as /* {SPDX_TAG} MIT */")
    return problems


def main(argv):
    if len(argv) > 2 or (len(argv) == 2 and argv[1].startswith("-")):
        print("usage: check_licence.py [root]", file=sys.stderr)
        return 2
    root = argv[1] if len(argv) == 2 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(root):
        print(f"check-licence: {root} is not a folder", file=sys.stderr)
        return 2
    problems = []
    count = 0
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for name in sorted(files):
            if name in SKIP_FILES:
                continue
            path = os.path.join(d, name)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            count += 1
            problems += check_file(path, os.path.relpath(path, root).replace(os.sep, "/"))
    for p in problems:
        print(f"check-licence: {p}", file=sys.stderr)
    if problems:
        return 1
    print(f"check-licence: {count} files, all MIT")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
