# The Makefile path of the holotape-c template, for Reel's own tests. It
# lives outside the template, which a new project copies as it is. The
# top-level Makefile fills the template into a folder of its own, then
# runs this file there with NAME set to the filled project name:
#
#   make -C <filled project> -f <this file> NAME=<name>
#
# The values match the template's robco.toml, as the spec's
# STUDIO_PROJECT.md, "A project that also builds with a Makefile", says.
# The tape is build/$(NAME).HTP in the filled folder.
HERE      := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PIPOS_SDK ?= $(HERE)/../../external/pip-os/sdk
ifeq ($(strip $(NAME)),)
$(error NAME is not set: give the project name of the filled template)
endif
IMAGE     := $(NAME).HTP
KIND      := holotape
TITLE     := $(NAME)
VERSION   := 0.1.0
SUBTYPE   := utility
ICON      := icon.pbm
ABI       := 1.4
SRCS      := src/main.c
include $(PIPOS_SDK)/pipos-app.mk
