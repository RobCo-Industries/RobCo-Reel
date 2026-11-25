# RobCo Reel: the Reel runtime, tested on the host with RobCo-Core's
# host.mk from the Pip-OS submodule in external/pip-os.
#
#   make                      the host test binaries
#   make test-host            host unit tests and the licence check
#   make check-licence        every file is MIT, every C file says so
#   make clean

PIP_OS     := external/pip-os
ROBCO_CORE := $(PIP_OS)/external/robco-core
BUILD      ?= build
PYTHON     ?= python3

ifeq ($(wildcard $(PIP_OS)/sdk/pipos-app.mk $(ROBCO_CORE)/mk/host.mk),)
$(error $(PIP_OS) is empty: run git submodule update --init --recursive)
endif

.DEFAULT_GOAL := all

# ---- Host unit tests, with RobCo-Core's host.mk ------------------------------

HOST_TEST_DIR := tests/host
HOST_SRCS     := $(sort $(wildcard reel/src/*.c))
HOST_INCLUDES := reel/include
include $(ROBCO_CORE)/mk/host.mk

.PHONY: all
all: host-tests

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

test: test-host

clean:
	rm -rf $(BUILD)
