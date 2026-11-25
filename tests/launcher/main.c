/* SPDX-License-Identifier: MIT */
/*
 * A test ROM. It launches /PIPBOY/HOLO/HELLO.HTP once, with no keys
 * needed, logs what holo_launch returned and exits with status 0 when
 * the tape exited with 0, or 1 otherwise.
 */
#include <pipos/pip.h>

#define TAPE "HELLO.HTP"

int pip_main(const pipos_startup_t *startup)
{
    int32_t rc;

    (void)startup;
    pip_printf("launcher: launching %s\n", TAPE);
    rc = pip_holo_launch(TAPE, "");
    pip_printf("launcher: %s returned %d\n", TAPE, (int)rc);
    return rc == 0 ? 0 : 1;
}
