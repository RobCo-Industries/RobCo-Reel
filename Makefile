# RobCo Reel: the Reel runtime, its samples and templates, built with the
# Pip-OS SDK in external/pip-os.
#
#   make                      the sample tapes, into build/samples/
#   make test-host            host unit tests and the licence check
#   make test                 test-host, then the QEMU tests on every board
#   make test BOARD=raspi0    the same, the QEMU tests on one board
#   make test-target          the QEMU tests only (BOARD=<name> or all)
#   make check-licence        every file is MIT, every C file says so
#   make clean

PIP_OS     := external/pip-os
ROBCO_CORE := $(PIP_OS)/external/robco-core
BUILD      ?= build
BOARD      ?= all
PYTHON     ?= python3

ifeq ($(wildcard $(PIP_OS)/sdk/pipos-app.mk $(ROBCO_CORE)/mk/host.mk),)
$(error $(PIP_OS) is empty: run git submodule update --init --recursive)
endif

.DEFAULT_GOAL := all

# QEMU runs and builds below share build/; keep top-level goals serial.
.NOTPARALLEL:

# ---- Sample tapes, each through the Pip-OS SDK -------------------------------

# Each sample has its own Makefile with reel/reel.mk and the SDK's
# pipos-app.mk. It builds into build/samples/<name>/.
SAMPLES_BUILD := $(abspath $(BUILD))/samples
HELLO_TAPE    := $(SAMPLES_BUILD)/hello/HELLO.HTP
SUB_MAKE      := $(MAKE) --no-print-directory CI=$(CI) PYTHON=$(PYTHON)

.PHONY: all samples
all: samples

samples:
	$(SUB_MAKE) -C samples/hello BUILD=$(SAMPLES_BUILD)/hello

# ---- Host unit tests, with RobCo-Core's host.mk ------------------------------

HOST_TEST_DIR := tests/host
HOST_SRCS     := $(sort $(wildcard reel/src/*.c))
HOST_INCLUDES := reel/include
include $(ROBCO_CORE)/mk/host.mk

# host.mk only sees the headers at the top of each include folder.
$(HOST_TESTS): $(wildcard reel/include/reel/*.h)

# ---- Checks ------------------------------------------------------------------

.PHONY: check-licence tools-test

check-licence:
	$(PYTHON) tools/check_licence.py

# The tests of the Python tools: unittest, so no pytest is needed.
tools-test:
	$(PYTHON) -m unittest discover -s tests/tools -p 'test_*.py'

# The C host tests come from host.mk's test-host; these run first.
test-host: check-licence tools-test

# ---- QEMU tests --------------------------------------------------------------

# The launcher ROM starts the sample tape. Pip-OS's own Makefile builds
# the kernel and the card, through the interface of its
# ROM_DEVELOPMENT.md, "Using Pip-OS from another repository".
LAUNCHER    := $(abspath $(BUILD))/launcher/ROM1.ROM
PIPOS_BUILD := $(abspath $(BUILD))/pipos
PIPOS_MAKE  := $(MAKE) --no-print-directory -C $(PIP_OS) BUILD=$(PIPOS_BUILD) PYTHON=$(PYTHON)

.PHONY: launcher kernel sdimage test test-target venv
launcher:
	$(SUB_MAKE) -C tests/launcher BUILD=$(abspath $(BUILD))/launcher

kernel:
	$(PIPOS_MAKE) kernel

sdimage: all launcher
	$(PIPOS_MAKE) sdimage ROM=$(LAUNCHER) TAPE=$(HELLO_TAPE)

VENV := .venv
venv: $(VENV)/.installed
$(VENV)/.installed: $(ROBCO_CORE)/tests/requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q -r $<
	touch $@

test: test-host
	$(MAKE) --no-print-directory test-target

test-target: sdimage kernel venv
	$(VENV)/bin/pytest $(wildcard tests/test_*.py) -v --board $(BOARD) --build-dir $(BUILD)

clean:
	rm -rf $(BUILD)
