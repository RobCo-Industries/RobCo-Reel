# Changelog

All notable changes to RobCo Reel are listed here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Reel follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The layout: `reel/`, `templates/`, `samples/` and `gen/`, each with a README.
- Pip-OS `5f891e7` as the submodule `external/pip-os`, with RobCo-Core `79cbd82` inside it.
- `reel_version()` and `<reel/reel.h>`, with host tests.
- `samples/hello`: a tape that links Reel, logs its version and exits.
- A QEMU test that starts the sample tape from a test launcher ROM on `raspi0`, `raspi1ap`, `raspi2b` and `raspi3b`.
- `tools/check_licence.py`: every file is MIT, every C file starts with an MIT SPDX line.
- `templates/holotape-c`: a holotape in C that draws one screen, logs `tape: ready` and returns 0 on SELECT. It holds its `robco.toml`, icon, scenario and the golden image of its screen.
- `tools/fill_template.py`: fills a template into a new folder and replaces `@NAME@`, as `robco new` will.
- `make template`: fills the template into `build/template/` and builds it through `tests/template/Makefile` and `pipos-app.mk`.
- A QEMU test that boots the template tape on the four boards, compares its screen with the golden image, presses SELECT and reads exit status 0.
- CI through RobCo-Core's `robco-ci.yml`, with the pin and doc link checks.
- `make templates-package`: writes `templates-<version>.zip` with `sdk.json`, `templates.json`, `holotape-c/` and `LICENSES/MIT.txt`, from tracked files only. Two builds give the same bytes.
- The `templates-package` workflow: builds the package twice on every run, and publishes it only for a pushed tag `templates-<version>`.
- `make templates-package-check` passes: Pip-OS's checker reads the archive with its `templates` rules. The main CI and the `templates-package` workflow run it, and a tool test shows it refuses a copy with one byte changed.

### Changed

- Pip-OS pin moved to `a0a523e`, whose package checker knows the `templates` kind, with RobCo-Core `712db81` inside it.
- `make check-workflows` runs Pip-OS's `tools/check_workflow_exprs.py` on this repository's workflows, in place of Reel's own `tools/check_workflows.py`, which missed `${{ github.ref }}` and other forms. A tool test shows a pasted `${{ github.ref }}` fails it.
- The `templates-package` workflow keeps the first build's checksum in `$RUNNER_TEMP`. At the repository root, it made the second build refuse the tree on every run.
- Pip-OS pin moved to `ada823c`, which has the workflow guard `tools/check_workflow_exprs.py`, with RobCo-Core `712db81` inside it. Its new boot text that writes itself is off by default, so Reel needs no change.
