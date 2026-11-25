# Reel for a tape built with the Pip-OS SDK. Include it before the SDK's
# pipos-app.mk, after SRCS and CFLAGS_EXTRA are set:
#
#   REEL := ../../reel
#   include $(REEL)/reel.mk
#   include $(PIPOS_SDK)/pipos-app.mk
#
# It adds Reel's sources to SRCS and its headers to CFLAGS_EXTRA. The
# SDK compiles them with the tape's own flags, and --gc-sections drops
# what the tape does not call.

ifeq ($(strip $(REEL)),)
$(error REEL is not set)
endif

REEL_DIR     := $(patsubst %/,%,$(strip $(REEL)))
REEL_SRCS    := $(sort $(wildcard $(REEL_DIR)/src/*.c))
SRCS         += $(REEL_SRCS)
CFLAGS_EXTRA += -I$(REEL_DIR)/include
