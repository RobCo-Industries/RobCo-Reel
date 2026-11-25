/* SPDX-License-Identifier: MIT */
/* Host tests for reel_version() and the version macros. */
#include "rc_test.h"

#include <reel/reel.h>

TEST(version_matches_header)
{
    CHECK_EQ(reel_version(), REEL_VERSION);
}

TEST(version_fields)
{
    uint32_t v = reel_version();

    CHECK_EQ(v >> 16, (uint32_t)REEL_VERSION_MAJOR);
    CHECK_EQ((v >> 8) & 0xffu, (uint32_t)REEL_VERSION_MINOR);
    CHECK_EQ(v & 0xffu, (uint32_t)REEL_VERSION_PATCH);
}

