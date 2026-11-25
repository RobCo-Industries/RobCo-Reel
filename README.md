# RobCo Reel

Reel is a small C runtime for holotapes on [Pip-OS](https://github.com/RobCo-Industries/Pip-OS), with project templates and samples. [RobCo Studio](https://github.com/RobCo-Industries/RobCo-Studio) copies or links these files into what a user builds.

## Status

This is a skeleton. No runtime feature works yet.

What exists:

- `reel/`: the library, with one function, `reel_version()`, and its header.
- `samples/hello/`: a tape that links Reel, logs one line and exits. It builds with the Pip-OS SDK into a sealed `ROBCO78` image of 3716 bytes.
- Host tests for the library, and one QEMU test that boots Pip-OS, starts the tape from a test ROM and waits for its line, on four boards.
- A check that every file is MIT.
- CI through the suite's shared workflow.

What does not exist yet:

- The kit: the loop, sprites and tiles, text, menus, input, timers, sound cues, saves.
- `templates/` and `gen/` hold only a README each.
- A `libreel.a` and the `reel` and `templates` packages for Studio.
- Any run on real hardware.

## Layout

| Folder | Holds |
|---|---|
| [`reel/`](reel/) | The runtime that tapes link |
| [`templates/`](templates/) | Project skeletons for `robco new` |
| [`samples/`](samples/) | Small tapes that use Reel |
| [`gen/`](gen/) | Skeleton files Studio's asset packer fills |
| `tests/` | Host tests, the QEMU tests and their launcher ROM |
| `tools/` | The licence check |
| `external/pip-os` | Pip-OS at a pinned commit, with RobCo-Core inside it |

## Build and test

```sh
git submodule update --init --recursive
make
make test-host
make test BOARD=raspi2b
```

See [docs/BUILD.md](docs/BUILD.md) and [docs/TESTING.md](docs/TESTING.md). The Pip-OS SDK is described in Pip-OS's [ROM_DEVELOPMENT.md](https://github.com/RobCo-Industries/Pip-OS/blob/5f891e75ac0894beec1d4e9d8cb37c00ec0fbf3e/docs/ROM_DEVELOPMENT.md).

## Licence

MIT. See [LICENSE](LICENSE).

Everything here ends up inside a tape that someone else wrote. It is MIT so that their tape stays theirs, under any licence they pick.

## Names

The names come from the Fallout games. All code, art, sound and text in this repository are original. This project is not affiliated with the owners of Fallout.
