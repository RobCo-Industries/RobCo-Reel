# SPDX-License-Identifier: MIT
"""Refuse a GitHub Actions run: block that pastes outside text into its script.

Usage: check_workflows.py [FILE...]   default: .github/workflows/*.yml and *.yaml

Actions expands ${{ ... }} into a run: script before the shell reads it, so a
tag or branch name such as templates-$(id) runs as a command. This check fails
when a run: block holds ${{ with github.ref_name, github.head_ref or anything
under github.event. Pass such a value through env: and expand it as "$NAME".

It reads the files as text, line by line, not as YAML. It cannot see:
a run: in a flow mapping such as {run: ...}, YAML anchors and aliases,
scripts in other keys such as actions/github-script's script:, composite
actions or reusable workflows in other repositories, and other outside text
such as inputs.* or step outputs that carry it.
"""

import glob
import os
import re
import sys

RUN = re.compile(r"^(\s*)(?:-\s+)?run:\s*(.*)$")
BAD = re.compile(r"\$\{\{[^}]*\b(github\.ref_name|github\.head_ref|github\.event\.)")


def run_blocks(lines):
    """Yield (line number, text) for each line that belongs to a run: value."""
    i = 0
    while i < len(lines):
        m = RUN.match(lines[i])
        i += 1
        if not m:
            continue
        key_col = len(m.group(1)) + (lines[i - 1][len(m.group(1)):].find("run:"))
        yield i, m.group(2)
        while i < len(lines):
            line = lines[i]
            if line.strip() and len(line) - len(line.lstrip()) <= key_col:
                break
            yield i + 1, line
            i += 1


def check(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{path}:{n}: run: block pastes {m.group(1)} into the script; pass it through env:"
            for n, text in run_blocks(lines) for m in [BAD.search(text)] if m]


def main(argv):
    files = argv or sorted(glob.glob(".github/workflows/*.yml") + glob.glob(".github/workflows/*.yaml"))
    if not files:
        print("check_workflows: no workflow file", file=sys.stderr)
        return 1
    errors = [e for p in files for e in check(p)]
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        return 1
    print(f"check_workflows: {len(files)} files, no outside text in a run: block")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
