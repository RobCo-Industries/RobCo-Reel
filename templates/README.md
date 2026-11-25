# templates

Project skeletons that `robco new` writes into a new project folder. Studio ships them as the `templates` package.

## What lives here

- `holotape-c`: a holotape in C. It draws one screen, logs `tape: ready` and returns 0 when SELECT is pressed.

Each template folder holds exactly the files a new project gets, laid out as they go into it, with no README and no Makefile. `robco.toml` holds the token `@NAME@`, which `robco new` replaces with the project name. The other files are copied byte for byte. `tools/fill_template.py` does the same for Reel's own tests.

`robco.toml` and `tests/start.toml` must match the spec byte for byte, so they carry no SPDX line. They are MIT like every file here, by the repository's `LICENSE`.

The tests build each template through `make template` and boot it in QEMU, see [docs/TESTING.md](../docs/TESTING.md#the-template-test).

## What must never live here

- Any file under a licence other than MIT. A template is copied into a user's project and becomes part of their tape.
- A template that does not build and pass its own test in CI.
- Art, text or sound copied from the Fallout games.
