/* SPDX-License-Identifier: MIT */
/*
 * Hello: the smallest tape that links Reel. It logs one line with
 * Reel's version and exits with status 0. The QEMU test waits for the
 * line.
 */
#include <pipos/pip.h>
#include <reel/reel.h>

int pip_main(const pipos_startup_t *startup)
{
    uint32_t v = reel_version();

    (void)startup;
    pip_printf("hello: reel %u.%u.%u\n", (unsigned)(v >> 16), (unsigned)((v >> 8) & 0xffu),
               (unsigned)(v & 0xffu));
    return 0;
}
