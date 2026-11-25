#!/bin/sh
# SPDX-License-Identifier: MIT
# Checks the wiring of make check-pins in a temporary copy of the repo:
# the copy passes, then a stale Pip-OS link and a stale RobCo-Core link
# each fail with the file, the line and the repository. The copy holds
# the Makefile, the CI workflow and every Markdown file at the root and
# in docs/; the folders the
# Makefile reads are links to the real ones. A fake git that always
# fails comes first on PATH: the checks must not call git, as in CI.
set -eu
root=$(cd "$(dirname "$0")/../.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
old=2222222222222222222222222222222222222222

fail() {
    echo "check_pins_test: $*" >&2
    exit 1
}

mkdir -p "$tmp/bin" "$tmp/r/.github/workflows" "$tmp/r/docs"
printf '#!/bin/sh\necho "fake git: called" >&2\nexit 1\n' > "$tmp/bin/git"
chmod +x "$tmp/bin/git"
PATH=$tmp/bin:$PATH
export PATH

cp "$root/Makefile" "$tmp/r/"
cp "$root/.github/workflows/ci.yml" "$tmp/r/.github/workflows/"
for f in "$root"/*.md "$root"/docs/*.md; do
    if [ -f "$f" ]; then
        cp "$f" "$tmp/r/${f#"$root"/}"
    fi
done
for d in external reel samples tests tools; do
    ln -s "$root/$d" "$tmp/r/$d"
done

check() {
    make --no-print-directory -C "$tmp/r" BUILD="$tmp/build" check-pins >"$tmp/out" 2>&1
}

check || fail "a clean copy failed: $(cat "$tmp/out")"
if grep -q 'fake git' "$tmp/out"; then
    fail "check-pins called git"
fi

# $1: owner/name of the repository, $2: the message part that names it.
stale() {
    printf '# Stale\n\n[x](https://github.com/%s/blob/%s/README.md)\n' "$1" "$old" \
        > "$tmp/r/docs/STALE.md"
    if check; then
        fail "a stale $1 link passed"
    fi
    rm -f "$tmp/r/docs/STALE.md"
    grep -q "docs/STALE.md:3" "$tmp/out" || fail "no file and line for $1 in: $(cat "$tmp/out")"
    grep -q "$old" "$tmp/out" || fail "no stale hash for $1 in: $(cat "$tmp/out")"
    grep -q "$2" "$tmp/out" || fail "no '$2' for $1 in: $(cat "$tmp/out")"
}

stale RobCo-Industries/Pip-OS "links Pip-OS at"
stale RobCo-Industries/RobCo-Core "links RobCo-Core at"

# A stale commit in the workflow fails too.
sed "s/robco-ci.yml@[0-9a-f]*/robco-ci.yml@$old/" "$root/.github/workflows/ci.yml" \
    > "$tmp/r/.github/workflows/ci.yml"
if check; then
    fail "a stale workflow pin passed"
fi
cp "$root/.github/workflows/ci.yml" "$tmp/r/.github/workflows/ci.yml"
check || fail "the restored copy failed: $(cat "$tmp/out")"
echo "check_pins_test: passed"
