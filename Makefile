# RobCo Reel: the Reel runtime, its samples and templates, built with the
# Pip-OS SDK in external/pip-os.
#
#   make                      the sample tapes, into build/samples/
#   make template             the holotape-c template, filled and built
#                             into build/template/
#   make test-host            host unit tests, the licence check and the
#                             pin checks
#   make test                 test-host, then the QEMU tests on every board
#   make test BOARD=raspi0    the same, the QEMU tests on one board
#   make test-target          the QEMU tests only (BOARD=<name> or all)
#   make check-licence        every file is MIT, every C file says so
#   make check-pins           CI pins and doc links match the submodules
#   make templates-package    build/templates-<version>.zip, the templates
#                             package: see docs/TEMPLATES_PACKAGE.md
#   make templates-package-check  Pip-OS's package checker on that archive
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
all: samples template

samples:
	$(SUB_MAKE) -C samples/hello BUILD=$(SAMPLES_BUILD)/hello

# ---- The holotape-c template, through its Makefile path ----------------------

# tools/fill_template.py fills the template into a fresh folder, as
# `robco new` would, and tests/template/Makefile builds it there with
# pipos-app.mk. Nothing is written into templates/.
TEMPLATE      := templates/holotape-c
TEMPLATE_NAME := HOLOC
TEMPLATE_DIR  := $(abspath $(BUILD))/template/holotape-c
TEMPLATE_TAPE := $(TEMPLATE_DIR)/build/$(TEMPLATE_NAME).HTP

.PHONY: template
template:
	rm -rf $(TEMPLATE_DIR)
	$(PYTHON) tools/fill_template.py $(TEMPLATE) $(TEMPLATE_DIR) $(TEMPLATE_NAME)
	$(SUB_MAKE) -C $(TEMPLATE_DIR) -f $(abspath tests/template/Makefile) NAME=$(TEMPLATE_NAME)

# ---- The templates package --------------------------------------------------

# tools/templates_package.py writes the archive from the files git tracks,
# so the work tree must be clean and built_from names its commit. Each git
# call stops the build with git's own message when it fails. The checker
# is Pip-OS's tools/sdk_package.py, used as it stands.
PKG_LIST    := $(abspath $(BUILD))/templates-package.files
PKG_HEADER  := reel/include/reel/reel.h
PKG_CHECK   := $(PIP_OS)/tools/sdk_package.py
PKG_FORBID   = --forbid "$(CURDIR)" --forbid "$(abspath $(BUILD))" \
               --forbid "$$HOME" --forbid "$$(hostname)" --user "$$(id -un)"

.PHONY: templates-package templates-package-check
templates-package:
	@t=$$(git status --porcelain --untracked-files=all) || { \
	    echo "templates-package: git status failed in $(CURDIR), see git's message above" >&2; exit 1; }; \
	if [ -n "$$t" ]; then \
	    echo "templates-package: the work tree has changes, so built_from would not name its sources:" >&2; \
	    echo "$$t" >&2; exit 1; fi
	@mkdir -p $(abspath $(BUILD))
	@git ls-files -z -- LICENSE templates > $(PKG_LIST) || { \
	    echo "templates-package: git ls-files failed, see git's message above" >&2; exit 1; }; \
	test -s $(PKG_LIST) || { echo "templates-package: git ls-files listed no file" >&2; exit 1; }
	@c=$$(git rev-parse --verify HEAD) && [ -n "$$c" ] || { \
	    echo "templates-package: git cannot name the commit of $(CURDIR), see git's message above" >&2; exit 1; }; \
	$(PYTHON) tools/templates_package.py --out $(abspath $(BUILD)) \
	    --version-header $(PKG_HEADER) --built-from RobCo-Reel=$$c \
	    --tracked $(PKG_LIST) $(PKG_FORBID)

templates-package-check:
	@v=$$($(PYTHON) tools/templates_package.py --print-version --version-header $(PKG_HEADER)) || exit 1; \
	$(PYTHON) $(PKG_CHECK) check $(abspath $(BUILD))/templates-$$v.zip --skip-short $(PKG_FORBID)

# ---- Host unit tests, with RobCo-Core's host.mk ------------------------------

HOST_TEST_DIR := tests/host
HOST_SRCS     := $(sort $(wildcard reel/src/*.c))
HOST_INCLUDES := reel/include
include $(ROBCO_CORE)/mk/host.mk

# host.mk only sees the headers at the top of each include folder.
$(HOST_TESTS): $(wildcard reel/include/reel/*.h)

# ---- Checks ------------------------------------------------------------------

.PHONY: check-licence check-workflows check-pins check-pins-test tools-test

check-licence:
	$(PYTHON) tools/check_licence.py

# No tag, branch or event text pasted into a workflow's run: script.
check-workflows:
	$(PYTHON) tools/check_workflows.py

# RobCo-Core's scripts: the CI pins, then the doc links once per pinned
# repository, Pip-OS and the RobCo-Core inside it.
check-pins:
	$(ROBCO_CORE)/tools/check_pins.sh .github/workflows/ci.yml
	$(ROBCO_CORE)/tools/check_doc_links.sh --repo RobCo-Industries/Pip-OS . $(PIP_OS)
	$(ROBCO_CORE)/tools/check_doc_links.sh . $(ROBCO_CORE)

check-pins-test:
	tests/host/check_pins_test.sh

# The tests of the Python tools: unittest, so no pytest is needed.
tools-test:
	$(PYTHON) -m unittest discover -s tests/tools -p 'test_*.py'

# The C host tests come from host.mk's test-host; these run first.
test-host: check-licence check-workflows tools-test check-pins check-pins-test

# ---- QEMU tests --------------------------------------------------------------

# The launcher ROM starts one tape: one build for the hello sample, one
# for the template. tests/test_template.py writes the template's card. Pip-OS's own Makefile builds
# the kernel and the card, through the interface of its
# ROM_DEVELOPMENT.md, "Using Pip-OS from another repository".
LAUNCHER    := $(abspath $(BUILD))/launcher/ROM1.ROM
TEMPLATE_LAUNCHER_BUILD := $(abspath $(BUILD))/launcher-template
PIPOS_BUILD := $(abspath $(BUILD))/pipos
PIPOS_MAKE  := $(MAKE) --no-print-directory -C $(PIP_OS) BUILD=$(PIPOS_BUILD) PYTHON=$(PYTHON)

.PHONY: launcher kernel sdimage test test-target venv
launcher:
	$(SUB_MAKE) -C tests/launcher BUILD=$(abspath $(BUILD))/launcher TAPE=HELLO.HTP
	$(SUB_MAKE) -C tests/launcher BUILD=$(TEMPLATE_LAUNCHER_BUILD) TAPE=$(TEMPLATE_NAME).HTP

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

test-target: sdimage template kernel venv
	$(VENV)/bin/pytest $(wildcard tests/test_*.py) -v --board $(BOARD) --build-dir $(BUILD) \
	    --template-name $(TEMPLATE_NAME)

clean:
	rm -rf $(BUILD)
