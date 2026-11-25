#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fills a template into a new project folder, as `robco new` does.

    tools/fill_template.py <template> <dest> <name>

It copies every file of <template> into <dest>, which must not exist yet
and must not lie inside <template>. In the files of SUBSTITUTE it
replaces every @NAME@ with <name> and changes no other byte. Any other
token in such a file is an error. Every other file is copied byte for
byte. It checks everything before it writes the first file. The rules
are those of the spec, SDK_PACKAGE.md, "Tokens".

<name> follows the project name rules: 1 to 8 characters from A to Z,
0 to 9, _ and -. Exits 0 on success, 1 on an error, 2 on bad usage.
"""

import os
import re
import sys

# The files of each template whose tokens are replaced, by template id.
# templates.json states the same set as "substitute": true.
SUBSTITUTE = {
    "holotape-c": {"robco.toml"},
}

TOKEN_RE = re.compile(rb"@[A-Z_]+@")
NAME_RE = re.compile(r"[A-Z0-9_-]{1,8}")


class FillError(Exception):
    pass


def template_files(template):
    """Every file of the template, as sorted paths with forward slashes."""
    out = []
    for d, dirs, files in os.walk(template):
        dirs.sort()
        for name in dirs:
            path = os.path.join(d, name)
            if os.path.islink(path):
                raise FillError(f"{path}: not a regular folder")
        for name in files:
            path = os.path.join(d, name)
            if os.path.islink(path) or not os.path.isfile(path):
                raise FillError(f"{path}: not a regular file")
            out.append(os.path.relpath(path, template).replace(os.sep, "/"))
    return sorted(out)


def substitute(data, name, rel):
    for token in sorted(set(TOKEN_RE.findall(data))):
        if token != b"@NAME@":
            raise FillError(f"templates: token: {rel}: {token.decode()}")
    return data.replace(b"@NAME@", name.encode())


def fill(template, dest, name, subst):
    if not NAME_RE.fullmatch(name):
        raise FillError(f"bad name {name!r}: 1 to 8 of A-Z, 0-9, _ and -")
    t = os.path.realpath(template)
    d = os.path.realpath(dest)
    if d == t or d.startswith(t + os.sep):
        raise FillError(f"{dest}: inside the template folder")
    if os.path.lexists(dest):
        raise FillError(f"{dest}: already exists")
    files = template_files(template)
    missing = sorted(subst - set(files))
    if missing:
        raise FillError(f"substituted file missing from the template: {', '.join(missing)}")
    out = {}
    for rel in files:
        with open(os.path.join(template, rel), "rb") as f:
            data = f.read()
        out[rel] = substitute(data, name, rel) if rel in subst else data
    for rel, data in out.items():
        path = os.path.join(dest, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    return files


def main(argv):
    if len(argv) != 4:
        print("usage: fill_template.py <template> <dest> <name>", file=sys.stderr)
        return 2
    template, dest, name = argv[1:]
    tid = os.path.basename(os.path.normpath(template))
    if not os.path.isdir(template) or tid not in SUBSTITUTE:
        print(f"fill-template: {template} is not a known template", file=sys.stderr)
        return 2
    try:
        fill(template, dest, name, SUBSTITUTE[tid])
    except FillError as e:
        print(f"fill-template: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
