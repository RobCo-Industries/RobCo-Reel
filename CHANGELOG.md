# Changelog

All notable changes to RobCo Reel are listed here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Reel follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The layout: `reel/`, `templates/`, `samples/` and `gen/`, each with a README.
- Pip-OS `5f891e7` as the submodule `external/pip-os`, with RobCo-Core `79cbd82` inside it.
- `reel_version()` and `<reel/reel.h>`, with host tests.
- `samples/hello`: a tape that links Reel, logs its version and exits.
- A QEMU test that starts the tape from a test launcher ROM on `raspi0`, `raspi1ap`, `raspi2b` and `raspi3b`.
- `tools/check_licence.py`: every file is MIT, every C file starts with an MIT SPDX line.
- CI through RobCo-Core's `robco-ci.yml`, with the pin and doc link checks.
