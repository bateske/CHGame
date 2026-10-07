/*
 * The SD game menu as a text list (docs/sd-menu.md; the card's files:
 * shared/chgame_card.h, spec/card.md; the card's tree: card.c).
 *
 *   power-on -> card read during the panel's wake-up waits
 *     launch entry in GAMES/MENU.IDX (and START not held) -> if it is the
 *       installed game it runs at once, the panel never lit; otherwise the
 *       list opens on it (A installs it: a power-on never writes flash)
 *     otherwise the list of GAMES/: folders and *.CHG titles, in MENU.IDX's
 *     order, then by title, the installed game preselected
 *       A/START on a folder           -> its list (B goes back)
 *       A/START on the installed game -> RUN reset (no flash write)
 *       A/START on another game       -> install (install.c) -> RUN reset
 *       UP/DOWN, LEFT/RIGHT           -> move, page
 *
 * No card, no FAT volume or no entries: the installed program just runs, as
 * before there was a menu. USB stays alive while the menu is up, so an upload
 * can start at any time: HELLO/STATUS/READ leave the menu alone, any other
 * command hands over to the upload screen.
 *
 * Drawn into lcd.c's framebuffer over the folder's MENU.BG (or plain black
 * when there is none), which is read again from the card for every new
 * picture: there is RAM for one copy, not two. Errors are reported as a
 * number only (docs/sd-menu.md has the list): everything is still checked,
 * but text costs flash.
 */
#include "card.h"
#include "sd.h"
#include "fat.h"
#include "install.h"
#include "appmeta.h"
#include "boot.h"
#include "proto.h"
#include "hal.h"
#include "sys.h"
#include "chgame_bootreq.h"
#include "chgame_card.h"

#define ROWS        10
#define ROW_H       10
#define LIST_Y      20

static struct { uint32_t clus, sel, top; file_t bg; } up[DEPTH];

/* ---- drawing ------------------------------------------------------------------- */

/* The background: MENU.BG, with the logo and anything else in it (the
   menu draws nothing over its top 20 rows and bottom 8), or plain black when
   there is none (or it is not one). */
static void background(void)
{
    uint32_t k = 0;
    if (bg.clus && bg.size == CARD_BG_BYTES) {
        fat_stream_t s;
        uint32_t lba;
        fat_open(&s, bg.clus, bg.size);
        for (; k < CARD_BG_BYTES / 512; k++) {
            if (!(lba = fat_next_lba(&s, buf)) || sd_read(lba, k ? lcd_fb + (k - 1) * 512 : buf)) break;
            if (!k) {
                if (w32(buf) != CARD_BG_MAGIC) break;
                for (uint32_t i = 0; i < 8; i++)
                    ((uint32_t *)(void *)lcd_pal)[i] = w32(buf + CARD_BG_OFF_PALETTE + 4 * i);
            }
        }
        if (k != CARD_BG_BYTES / 512) bg.clus = 0;      /* broken: not again */
    }
    if (k != CARD_BG_BYTES / 512) {
        for (uint32_t i = 0; i < 16; i++) lcd_pal[i] = pal0[i];
        lcd_fill(0, 0, LCD_W, LCD_H, 0);
    }
#if !LCD_TURNS
    /* The static style: colour 15 (the bar, the boxes, the picture's #FF00FF)
       in the menu's text colour, not the hot pink the palette holds. */
    lcd_pal[LCD_RAINBOW] = lcd_pal[CARD_C_TEXT];
#endif
}

static void draw_list(void)
{
    if (sel < top) top = sel;
    if (sel >= top + ROWS) top = sel - ROWS + 1;
    background();
    for (uint32_t i = top; i < top + ROWS && i < ngames; i++) {
        uint32_t y = LIST_Y + (i - top) * ROW_H, c = CARD_C_TEXT;
        game_t *g = &games[i];
        if (i == sel) {
            lcd_fill(0, y, LCD_W, ROW_H, LCD_RAINBOW);
            c = CARD_C_INK;
        } else if (g->flags & G_BAD) c = CARD_C_DIM;
        if (g->flags & G_INSTALLED) lcd_fill(2, y + 2, 3, 6, CARD_C_MARK);     /* the chip */
        lcd_text(8, y + 1, g->title, TITLE_COLS, c);
        if (g->flags & G_DIR) lcd_text(LCD_W - 6, y + 1, ">", 1, c);
    }
    flush(0, LCD_H);
}

/* Centred; at most TITLE_COLS characters. */
static void text_c(uint32_t y, const char *s, uint32_t c)
{
    uint32_t n = 0;
    while (s[n] && n < TITLE_COLS) n++;
    lcd_text((LCD_W - n * 6) / 2, y, s, n, c);
}

/* A game's title is padded to TITLE_COLS, so text_c() always draws it 114
   pixels wide, from x 7. The box leaves 3 pixels each side of that inside
   its 2-pixel border, and the progress bar runs under the title, edge to
   edge. */
static void box(const char *l1, const char *l2)
{
    lcd_fill(2, 36, LCD_W - 4, 52, LCD_RAINBOW);
    lcd_fill(4, 38, LCD_W - 8, 48, CARD_C_INK);
    text_c(46, l1, LCD_RAINBOW);
    if (l2) text_c(60, l2, CARD_C_TEXT);
    flush(36, 88);
}

void menu_progress(uint32_t done, uint32_t total)
{
    lcd_fill(7, 72, ((LCD_W - 14) * (done + 1)) / total, 6, LCD_RAINBOW);
    flush(72, 78);
}

/* ---- the menu ------------------------------------------------------------------------ */

/* A or START on entry i: a folder opens, a game runs (installed first if need
   be). Returns only for a folder (0) or an error (INST_E_*). */
static int start(uint32_t i, int app)
{
    game_t *g = &games[i];
    int rc = INST_OK;
    if (g->flags & G_DIR) {
        if (depth < DEPTH) {
            up[depth].clus = here; up[depth].sel = sel; up[depth].top = top; up[depth].bg = bg;
            depth++;
            here = g->clus;
            scan(app);
        }
        return INST_OK;
    }
    if (g->flags & G_BAD) return g->err;
    if (!(g->flags & G_INSTALLED) || CHBOOT_APP) {
        if (!lit) draw_list();
        box("INSTALLING", g->title);
        light();
        rc = install(g->clus, g->size, buf);
        if (rc) return rc;
    }
#if CHBOOT_APP
    /* Dry run (build.sh app): the package checked, nothing written. */
    box("DRY RUN OK", 0);
    wait_key();
    return INST_OK;
#endif
    release();
    boot_reset(CHGAME_BOOTREQ_RUN);
}

void menu_main(int app, int launch)
{
    uint32_t k, n = 0;
    int rc = INST_OK;

    (void)launch;
    lcd_reset();
    if (!sd_init() && !fat_mount(buf) && fat_dir(0, buf, find_games, 0) == 1)
        n = scan(app);                      /* the card is read during the panel's waits */
#if !CHBOOT_APP
    if (!n && app == APP_VALID)
        boot_reset(CHGAME_BOOTREQ_RUN);     /* nothing on the card: run what is installed */
    /* The launch entry, followed down through flagged folders: the installed
       game starts at once (the panel never lit); any other is only selected,
       so a power-on never writes over the game that was in flash. */
    for (k = 0; launch && k <= DEPTH; k++) {
        for (n = 0; n < ngames && !(games[n].flags & G_LAUNCH); n++) { }
        if (n == ngames) break;
        sel = n;
        if (!(games[n].flags & (G_DIR | G_INSTALLED))) break;      /* not installed: the list, on it */
        start(n, app);                      /* a folder: into it; the installed game: RUN (no return) */
    }
#endif
    if (!ngames && !depth) {                /* nothing to list: USB mode, saying so (B there looks again) */
        background();
        box("NO GAMES", 0);
        light();
        return;
    }
#if !CHBOOT_APP
    proto_init();
#endif
    draw_list();
    light();

    for (;;) {
        uint32_t old = sel, old_depth = depth;
#if !CHBOOT_APP
#if LCD_TURNS
        static uint32_t t_hue;
        if (sys_ticks() - t_hue >= 40u * SYS_TICKS_PER_MS) {   /* a turn of the wheel in ~3.8 s */
            t_hue = sys_ticks();
            lcd_step();
        }
#endif
        proto_task();
        if (proto_claimed) {
            box("USB UPLOAD", "B: MENU");
            return;
        }
#endif
        if (rc) {
            static char err[] = "ERROR 0";
            err[6] = (char)('0' + rc);
            if (rc == INST_E_LOST)
                for (n = 0; n < ngames; n++) games[n].flags &= (uint8_t)~G_INSTALLED;
            box(err, 0);
            wait_key();
            rc = INST_OK;
            draw_list();
            continue;
        }
        k = keys();
        if (!ngames) k &= BTN_B;            /* an empty folder: B leaves it, nothing else */
        if (k & BTN_UP)    sel = sel ? sel - 1 : ngames - 1;
        if (k & BTN_DOWN)  sel = sel + 1 < ngames ? sel + 1 : 0;
        if (k & BTN_LEFT)  sel = sel >= ROWS ? sel - ROWS : 0;
        if (k & BTN_RIGHT) sel = sel + ROWS < ngames ? sel + ROWS : ngames - 1;
#if CHBOOT_APP
        if (k & BTN_SELECT) boot_reset(CHGAME_BOOTREQ_USB);
#endif
        if (k & BTN_B && depth) {
            depth--;
            here = up[depth].clus;
            bg = up[depth].bg;
            scan(app);
            sel = up[depth].sel;
            top = up[depth].top;
        }
        if (k & (BTN_A | BTN_START))
            rc = start(sel, app);
        if (sel != old || depth != old_depth || (k & (BTN_A | BTN_START) && !rc))
            draw_list();
    }
}

void menu_usb_notice(void)
{
#if !CHBOOT_APP
    proto_init();                           /* enumerate first; the panel can wait */
#endif
    lcd_reset();
    background();
    box("USB UPLOAD", "B: MENU");
    lcd_wake();
    lcd_on();
}
