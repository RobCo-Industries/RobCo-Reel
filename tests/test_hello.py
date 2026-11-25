# SPDX-License-Identifier: MIT
"""The hello sample tape in QEMU.

The card holds the launcher ROM of tests/launcher as PIPBOY/ROM1.ROM and
the sample as PIPBOY/HOLO/HELLO.HTP. The launcher runs the tape once with
no key, logs what holo_launch returned and exits, so the kernel prints
ev=ready.
"""

import os
import re

from conftest import ROOT
from pipos_testing import booted, no_exception

HELLO = re.compile(r"^hello: reel (\d+)\.(\d+)\.(\d+)\r?\n", re.M)
RETURNED = re.compile(r"^launcher: HELLO\.HTP returned (-?\d+)\r?\n", re.M)
VERSION_H = "reel/include/reel/reel.h"


def header_version():
    with open(os.path.join(ROOT, VERSION_H)) as f:
        src = f.read()
    return tuple(re.search(rf"#define REEL_VERSION_{part}\s+(\d+)", src)[1]
                 for part in ("MAJOR", "MINOR", "PATCH"))


def test_hello_logs_reel_version(kernel_image, card, board):
    # booted() waits for ev=ready, which the kernel prints after the ROM exits.
    with booted(kernel_image, board, sd=card) as vm:
        assert HELLO.findall(vm.serial) == [header_version()], vm.serial
        assert RETURNED.findall(vm.serial) == ["0"], vm.serial
        exits = [m for m in vm.markers() if m.get("ev") == "rom_exit"]
        assert [m.get("status") for m in exits] == ["0"], vm.serial
        no_exception(vm)
