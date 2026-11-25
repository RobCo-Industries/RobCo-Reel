/* SPDX-License-Identifier: MIT */
/*
 * A holotape in C. It draws one screen, logs "tape: ready" once the
 * screen is up, then waits. SELECT ends the tape with status 0.
 *
 * The screen depends only on this code and on the scheme colour that
 * pip_gfx_info gives, so it looks the same on every board.
 */
#include <pipos/pip.h>

#define SCREEN_W 320
#define SCREEN_H 240

/* Draws text centred on the screen's width, top at y. */
static void draw_centred(int32_t y, const char *text, uint32_t scale)
{
    int32_t w = (int32_t)PIP_TM_WIDTH(pip_text_metrics(text, scale));

    pip_draw_text((SCREEN_W - w) / 2, y, text, scale);
}

static void draw_screen(void)
{
    pip_gfx_info_t gi;
    uint32_t fg = 0x33e066;
    uint32_t dim;

    if (pip_gfx_info(&gi) == 0) {
        fg = gi.fg_default;
    }
    dim = (fg >> 1) & 0x7f7f7fu;

    pip_clear(0);
    pip_set_color(fg, PIP_COLOR_NONE);
    pip_rect_xywh(0, 0, SCREEN_W, SCREEN_H, PIP_RECT_OUTLINE);
    pip_rect_xywh(4, 4, SCREEN_W - 8, SCREEN_H - 8, PIP_RECT_OUTLINE);
    draw_centred(44, "HOLOTAPE", 4);
    pip_draw_line(60, 120, SCREEN_W - 60, 120);
    draw_centred(136, "Ready.", 2);
    pip_set_color(dim, PIP_COLOR_NONE);
    draw_centred(200, "Press SELECT to exit", 1);
    pip_present();
}

int pip_main(const pipos_startup_t *startup)
{
    pip_event_t ev;

    (void)startup;
    draw_screen();
    pip_printf("tape: ready\n");

    for (;;) {
        if (pip_wait_event(&ev, PIP_WAIT_FOREVER) == 1 && ev.type == PIP_EV_BUTTON &&
            ev.value == PIP_EV_PRESS && ev.code == PIP_BTN_SELECT) {
            return 0;
        }
    }
}
