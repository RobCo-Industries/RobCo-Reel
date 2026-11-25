/* SPDX-License-Identifier: MIT */
/*
 * Reel, a small runtime for Pip-OS holotapes. Include this header only.
 *
 * Today it holds the version. The kit comes in later milestones.
 */
#ifndef REEL_REEL_H
#define REEL_REEL_H

#include <stdint.h>

#define REEL_VERSION_MAJOR 0
#define REEL_VERSION_MINOR 1
#define REEL_VERSION_PATCH 0

_Static_assert(REEL_VERSION_MINOR <= 255 && REEL_VERSION_PATCH <= 255,
               "the minor and patch numbers each fit one byte of REEL_VERSION");

/* (major << 16) | (minor << 8) | patch, as Pip-OS encodes its own version. */
#define REEL_VERSION \
    (((uint32_t)REEL_VERSION_MAJOR << 16) | ((uint32_t)REEL_VERSION_MINOR << 8) | \
     (uint32_t)REEL_VERSION_PATCH)

/*
 * The version of the Reel library the tape was linked with, encoded as
 * REEL_VERSION. It can differ from REEL_VERSION when the header and the
 * library come from two releases.
 */
uint32_t reel_version(void);

#endif
