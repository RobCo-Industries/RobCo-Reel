# Contributing

## Build and test

```sh
git submodule update --init --recursive
make CI=1 all test-host
make test
```

[docs/BUILD.md](docs/BUILD.md) lists the tools and targets. [docs/TESTING.md](docs/TESTING.md) explains the tests.

## Licence

Every file in this repository is MIT, and every C and header file starts with this line:

```c
/* SPDX-License-Identifier: MIT */
```

These files end up inside tapes other people write. Studio copies templates into a user's project and compiles Reel into the user's tape. A tape made that way belongs to its author, under any licence the author picks. One file under the GPL or another copyleft licence would reach into every tape that uses it. So nothing here may carry one.

`make check-licence` holds the line, and `make test-host` and CI run it. It fails on a GNU licence notice, on an SPDX identifier other than `MIT`, and on a C or header file whose first line is not the MIT SPDX line. Do not copy code into this repository unless you wrote it or it is MIT. Contributions come in under the MIT licence.

## Code rules

- Reel calls Pip-OS only through the `pip_*` functions of the SDK. No registers, no kernel internals.
- Reel builds freestanding with the SDK flags: ARMv6, soft float, no C library beyond `libpip`.
- Pure logic gets a host test in `tests/host/`.
- Every change that alters behaviour comes with a test that fails without it.
- Do not edit `external/pip-os`. Move the submodule pin in its own commit, update the workflow's RobCo-Core pin to the one inside Pip-OS, then run `make check-pins`.

## Commits

- Small commits that each build and pass `make CI=1 all test-host`.
- A plain subject in the imperative: "Add the timer module", not "Added" or "Adds".
- Stage files by name.

## Prose

Docs, comments and commit messages use short, plain sentences in the active voice. Every claim must match the code. Headings use sentence case. Diagrams are Mermaid.

## Content

All artwork, fonts, sounds and text must be original. Do not copy anything from the Fallout games: no quotes, logos or art.
