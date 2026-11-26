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

### Changed

- Pip-OS pin moved to `93a07d2`, the commit that builds the `pipos` SDK package, with RobCo-Core `712db81` inside it.
