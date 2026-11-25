# SPDX-License-Identifier: MIT
"""Target test setup: Pip-OS's pipos_testing package.

It comes from the Pip-OS submodule and loads RobCo-Core's harness, which
adds --board and the board fixture. `make test-target` builds the
kernel and the card first, into --build-dir (BUILD in the Makefile).
"""

import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "external", "pip-os", "sdk", "testing"))
pytest_plugins = ["pipos_testing.plugin"]

import pytest  # noqa: E402


def pytest_addoption(parser):
    parser.addoption("--build-dir", default="build",
                     help="build directory, as BUILD in the Makefile")
    parser.addoption("--template-name", default="HOLOC",
                     help="project name of the filled template, as TEMPLATE_NAME in the Makefile")


def _built(request, *parts):
    path = os.path.join(ROOT, request.config.getoption("--build-dir"), *parts)
    if not os.path.exists(path):
        pytest.fail(f"{path} is missing: run make test-target, which builds it")
    return path


@pytest.fixture(scope="session")
def kernel_image(request):
    """The Pip-OS kernel image that make built from the submodule."""
    return _built(request, "pipos", "pipos.img")


@pytest.fixture
def card(request, tmp_path):
    """A copy of the card make sdimage wrote, so a test cannot change it."""
    path = tmp_path / "sd.img"
    shutil.copyfile(_built(request, "pipos", "sd.img"), path)
    return path
