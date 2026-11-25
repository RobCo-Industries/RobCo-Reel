# The smallest tape that uses Reel: it logs Reel's version and exits
# with status 0. The top-level Makefile builds it with BUILD set.
PIPOS_SDK ?= ../../external/pip-os/sdk
REEL      ?= ../../reel
IMAGE     := HELLO.HTP
KIND      := holotape
SUBTYPE   := utility
NAME      := HELLO
TITLE     := Hello from Reel
VERSION   := 0.1.0
SRCS      := main.c
include $(REEL)/reel.mk
include $(PIPOS_SDK)/pipos-app.mk
