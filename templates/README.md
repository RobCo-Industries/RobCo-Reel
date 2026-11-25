# templates

Project skeletons that `robco new` writes into a new project folder. Studio ships them as the `templates` package.

## What lives here

Nothing yet. The first template, a holotape in C, comes with plan milestone S1. The holotape game template comes with S6.

Each template is a folder with a `robco.toml`, its sources and a short README. It builds into a sealed tape.

## What must never live here

- Any file under a licence other than MIT. A template is copied into a user's project and becomes part of their tape.
- A template that does not build and pass its own test in CI.
- Art, text or sound copied from the Fallout games.
