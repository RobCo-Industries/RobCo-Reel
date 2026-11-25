# reel

The Reel runtime: a small C library that a holotape links. It runs on Pip-OS in user mode and reaches the hardware only through the `pip_*` calls of the Pip-OS SDK.

## What lives here

- `include/reel/`: the public headers. A tape includes `<reel/reel.h>`.
- `src/`: the library sources. Each file starts with an MIT SPDX line.
- `reel.mk`: the make fragment a tape includes before the SDK's `pipos-app.mk`. It adds the sources and the include path.

Today the library holds one function, `reel_version()`. The kit of plan milestone S6 comes later: the loop, sprites and tiles, text, menus, input, timers, sound cues, saves and the log.

## What must never live here

- Code that touches hardware, registers or kernel internals.
- Any file under a licence other than MIT.
- Code from RobCo Studio, or anything Studio's repository owns.
- A C library beyond what `libpip` offers. Reel builds freestanding, with soft float.
