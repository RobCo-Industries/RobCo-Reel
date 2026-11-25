# SPDX-License-Identifier: MIT
"""The holotape-c template in QEMU.

`make template` fills templates/holotape-c into build/template/ with
tools/fill_template.py and builds it through tests/template/Makefile.
This test writes a card with the PIPOS.CFG of the spec's simulator card
(STUDIO_CLI.md, "The simulator card"), the template launcher ROM and the
tape. It waits for the tape's line, compares the screen with the
template's golden image, presses SELECT and reads the exit status that
the launcher logs.

Set REEL_UPDATE_GOLDEN=1 to write the golden image from the capture, then
look at it before committing it.
"""

import os
import re

import pytest
from conftest import ROOT, _built
from pipos_testing import TIMEOUT, booted, check_golden, make_card, no_exception, press, screenshot

GOLDEN = os.path.join(ROOT, "templates", "holotape-c", "tests", "golden", "start", "ready.png")
READY_LINE = re.compile(r"^tape: ready\r?\n", re.M)

# The simulator card's /PIPBOY/PIPOS.CFG, byte for byte: 11 lines, 113 bytes.
SIM_CFG = (b"[display]\nscheme = green\nline_delay_ms = 0\nbackend = hdmi\n\n"
           b"[audio]\nvolume = 100\nbeep = no\n\n[holotape]\nslot = off\n")


@pytest.fixture
def template_card(request, tmp_path):
    name = request.config.getoption("--template-name")
    tape = _built(request, "template", "holotape-c", "build", f"{name}.HTP")
    rom = _built(request, "launcher-template", "ROM1.ROM")
    files = {"PIPBOY/PIPOS.CFG": SIM_CFG}
    for card_path, src in (("PIPBOY/ROM1.ROM", rom), (f"PIPBOY/HOLO/{name}.HTP", tape)):
        with open(src, "rb") as f:
            files[card_path] = f.read()
    return name, make_card(tmp_path / "sd.img", files)


def test_sim_cfg_is_the_spec_text():
    assert len(SIM_CFG) == 113 and SIM_CFG.count(b"\n") == 11


def test_template_screen_and_exit(kernel_image, template_card, board, tmp_path):
    name, card = template_card
    returned = re.compile(rf"^launcher: {name}\.HTP returned (-?\d+)\r?\n", re.M)
    # The tape waits for SELECT, so the kernel prints ev=ready only after it.
    with booted(kernel_image, board, sd=card, wait="jump") as vm:
        vm.wait_for(READY_LINE, timeout=TIMEOUT)
        check_golden(screenshot(vm, tmp_path), GOLDEN, update_var="REEL_UPDATE_GOLDEN")
        assert not returned.findall(vm.serial), vm.serial
        press(vm, "select")
        vm.wait_for(re.compile(r"@RC stage=pipos ev=ready rom=\d\n"), timeout=TIMEOUT)
        assert len(READY_LINE.findall(vm.serial)) == 1, vm.serial
        assert returned.findall(vm.serial) == ["0"], vm.serial
        exits = [m for m in vm.markers() if m.get("ev") == "rom_exit"]
        assert [m.get("status") for m in exits] == ["0"], vm.serial
        no_exception(vm)
