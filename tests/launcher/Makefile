# A test ROM that launches one tape once and exits. The top-level
# Makefile builds it with BUILD set, for the QEMU tests only, once per
# tape: TAPE is the file name in /PIPBOY/HOLO/.
PIPOS_SDK    ?= ../../external/pip-os/sdk
TAPE         ?= HELLO.HTP
IMAGE        := ROM1.ROM
KIND         := rom
NAME         := LAUNCHER
TITLE        := Reel test launcher
VERSION      := 0.1.0
SRCS         := main.c
CFLAGS_EXTRA := '-DTAPE="$(TAPE)"'
include $(PIPOS_SDK)/pipos-app.mk
