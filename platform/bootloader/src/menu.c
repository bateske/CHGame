/*
 * The SD game menu (docs/sd-menu.md; the card's files: shared/chgame_card.h,
 * spec/card.md).
 *
 *   power-on -> card read during the panel's wake-up waits
 *     launch entry in GAMES/MENU.IDX (and START not held) -> that game runs,
 *       installed first if it is not the installed one
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
 * Drawn into lcd.c's framebuffer over the folder's MENU.BG (or a plain
 * screen with the title when there is none), which is read again from the
 * card for every new picture: there is RAM for one copy, not two. The game
 * table lives in RAM. Errors are reported as a number only (docs/sd-menu.md
 * has the list): everything is still checked, but text costs flash.
 */
#include "menu.h"
#include "lcd.h"
#include "sd.h"
#include "fat.h"
#include "chg.h"
#include "install.h"
#include "appmeta.h"
#include "boot.h"
#include "proto.h"
#include "hal.h"
#include "sys.h"
#include "chgame_bootreq.h"
#include "chgame_card.h"

#define TITLE_COLS  19          /* x 8..121; a folder's '>' at 122 */
#define ROWS        10
#define ROW_H       10
#define LIST_Y      20
#define DEPTH       4           /* folders below GAMES/ */

#define G_INSTALLED 0x01        /* (draw_row tests it) */
#define G_BAD       0x02        /* err holds the reason */
#define G_DIR       0x04
#define G_LAUNCH    0x08

typedef struct {
    uint32_t clus, size;
    uint8_t  flags, err, key, pad;      /* key: the MENU.IDX record, 255 = none */
    char     title[TITLE_COLS + 1];     /* space-padded; holds the 11-byte 8.3 name until the scan is done */
} __attribute__((aligned(4))) game_t;
_Static_assert(sizeof(game_t) == 32, "keep game_t at 32 bytes");

typedef struct { uint32_t clus, size; } file_t;

static game_t games[MENU_MAX_GAMES];
static uint32_t ngames, sel, top, depth, lit;
static file_t idx, bg;                  /* the folder's MENU.IDX; the MENU.BG in force */
static struct { uint32_t clus, sel, top; file_t bg; } up[DEPTH];
static uint32_t here;                   /* the folder shown: its first cluster */
static uint8_t buf[512] __attribute__((aligned(4)));

static uint32_t w32(const uint8_t *p) { return *(const uint32_t *)(const void *)p; }

/* The menu's own colours when there is no MENU.BG (the panel black and dark
   grey; the rest by shared/chgame_card.h's roles). */
static const uint16_t pal0[16] = {
    [0] = RGB565(0, 0, 0), [1] = RGB565(64, 64, 64),
    [CARD_C_TEXT] = RGB565(255, 244, 214), [CARD_C_DIM] = RGB565(128, 128, 128),
    [CARD_C_INK] = RGB565(0, 0, 0), [CARD_C_MARK] = RGB565(214, 32, 32),
};

/* ---- the card --------------------------------------------------------------- */

static __attribute__((noinline)) int same(const uint8_t *a, const char *b)
{
    for (uint32_t i = 0; i < 11; i++) if (a[i] != (uint8_t)b[i]) return 0;
    return 1;
}

static int find_games(const uint8_t *d, void *ctx)
{
    (void)ctx;
    if (!same(d, "GAMES      ") || (d[11] & (FAT_ATTR_DIR | FAT_ATTR_LABEL)) != FAT_ATTR_DIR) return 0;
    here = fat_entry_cluster(d);
    return 1;
}

static int add_entry(const uint8_t *d, void *ctx)
{
    game_t *g = &games[ngames];
    file_t *f;
    (void)ctx;
    /* labels, hidden and system files, "." and "..", macOS "._NAME" forks */
    if (d[11] & (FAT_ATTR_LABEL | FAT_ATTR_HIDDEN | FAT_ATTR_SYSTEM) || d[0] == '.' || d[0] == '_') return 0;
    if (!(d[11] & FAT_ATTR_DIR)) {
        f = same(d, "MENU    IDX") ? &idx : same(d, "MENU    BG ") ? &bg : 0;
        if (f) {
            f->clus = fat_entry_cluster(d);
            f->size = fat_entry_size(d);
            return 0;
        }
        if (d[8] != 'C' || d[9] != 'H' || d[10] != 'G') return 0;
    }
    if (ngames == MENU_MAX_GAMES) return 0;     /* (still looking for MENU.*) */
    g->clus = fat_entry_cluster(d);
    g->size = fat_entry_size(d);
    g->flags = d[11] & FAT_ATTR_DIR ? G_DIR : 0;
    g->key = 0xFF;
    for (uint32_t i = 0; i <= TITLE_COLS; i++) g->title[i] = i < 11 ? (char)d[i] : ' ';
    ngames++;
    return 0;
}

/* Up to TITLE_COLS characters of s into a title: a NUL ends it, lower case is
   folded (the font has capitals only), anything else unprintable is '?'. */
static void set_title(game_t *g, const uint8_t *s)
{
    for (uint32_t k = 0, end = 0; k < TITLE_COLS; k++) {
        char ch = (char)s[k];
        if (!ch) end = 1;
        if (ch >= 'a' && ch <= 'z') ch -= 32;
        g->title[k] = end ? ' ' : (ch < 32 || ch > '_' ? '?' : ch);
    }
}

static void read_index(void)
{
    fat_stream_t s;
    uint32_t lba, k = 0;
    fat_open(&s, idx.clus, idx.size);
    while ((lba = fat_next_lba(&s, buf)) && !sd_read(lba, buf))
        for (const uint8_t *e = buf; e < buf + sizeof buf; e += CARD_IDX_RECORD, k++) {
            if (!k) {
                if (w32(e) != CARD_IDX_MAGIC) return;
                continue;
            }
            for (uint32_t i = 0; i < ngames; i++) {
                game_t *g = &games[i];
                if (g->key != 0xFF || !same(e, g->title)) continue;
                g->key = (uint8_t)(k < 0xFF ? k : 0xFE);
                if (e[CARD_IDX_OFF_FLAGS] & CARD_IDX_LAUNCH) g->flags |= G_LAUNCH;
                if (g->flags & G_DIR && e[CARD_IDX_OFF_TITLE]) set_title(g, e + CARD_IDX_OFF_TITLE);
            }
        }
}

/* Struct assignment would call newlib's memcpy (a byte loop in flash, and
   178 B of it): entries are 8 words, copied as words. */
static void copy(game_t *d, const game_t *s)
{
    for (uint32_t i = 0; i < sizeof(game_t) / 4; i++)
        ((uint32_t *)(void *)d)[i] = ((const uint32_t *)(const void *)s)[i];
}

static int less(const game_t *a, const game_t *b)
{
    if (a->key != b->key) return a->key < b->key;
    for (uint32_t i = 0; i < TITLE_COLS; i++)
        if (a->title[i] != b->title[i]) return a->title[i] < b->title[i];
    return 0;
}

/* Lists the folder `here` and reads the games' headers. Returns the number of
   entries (at the top, with "INSTALLED PROGRAM" when the program in flash is
   not among them). Picks the installed game, else the first. */
static uint32_t scan(int app)
{
    const chgame_meta_t *m = appmeta();
    uint32_t i, installed = 0;

    ngames = idx.clus = 0;
    fat_dir(here, buf, add_entry, 0);
    if (idx.clus) read_index();
    for (i = 0; i < ngames; i++) {
        game_t *g = &games[i];
        fat_stream_t s;
        uint32_t lba, n, crc;
        int rc;
        if (g->flags & G_DIR) continue;
        fat_open(&s, g->clus, g->size);
        lba = fat_next_lba(&s, buf);
        rc = lba && !sd_read(lba, buf) ? chg_check(buf, g->size, &n, &crc) : -1;
        if (rc) {
            g->flags |= G_BAD;
            g->err = (uint8_t)(rc < 0 ? INST_E_READ : INST_E_PKG);
            continue;                       /* (its 8.3 name stands in: "BADFILE CHG") */
        }
        set_title(g, buf + CHG_OFF_TITLE);
        if (app == APP_VALID && m->length == n && m->crc32 == crc) {
            g->flags |= G_INSTALLED;
            installed = 1;
        }
    }
    /* insertion sort: MENU.IDX's order, then by title */
    for (i = 1; i < ngames; i++) {
        game_t t;
        uint32_t j = i;
        copy(&t, &games[i]);
        for (; j && less(&t, &games[j - 1]); j--) copy(&games[j], &games[j - 1]);
        copy(&games[j], &t);
    }
    if (ngames && !depth && app == APP_VALID && !installed && ngames < MENU_MAX_GAMES) {
        for (i = ngames; i; i--) copy(&games[i], &games[i - 1]);
        games[0].flags = G_INSTALLED;      /* (its clus is never used) */
        set_title(&games[0], (const uint8_t *)"INSTALLED PROGRAM");
        ngames++;
    }
    for (sel = 0; sel < ngames && !(games[sel].flags & G_INSTALLED); sel++) { }
    if (sel == ngames) sel = 0;
    top = 0;                                /* (draw_list scrolls to sel) */
    return ngames;
}

/* ---- drawing ------------------------------------------------------------------- */

static void flush(uint32_t y0, uint32_t y1)
{
    if (lit) lcd_flush(y0, y1);             /* before lcd_on(), the picture waits for it */
}

/* The background: MENU.BG, or the menu's own when there is none (or it is
   not one): black, a grey band and the title. */
static void background(void)
{
    if (bg.clus && bg.size == CARD_BG_BYTES) {
        fat_stream_t s;
        uint32_t k, lba;
        fat_open(&s, bg.clus, bg.size);
        for (k = 0; k < CARD_BG_BYTES / 512; k++) {
            if (!(lba = fat_next_lba(&s, buf)) || sd_read(lba, k ? lcd_fb + (k - 1) * 512 : buf)) break;
            if (!k) {
                if (w32(buf) != CARD_BG_MAGIC) break;
                for (uint32_t i = 0; i < 8; i++)
                    ((uint32_t *)(void *)lcd_pal)[i] = w32(buf + CARD_BG_OFF_PALETTE + 4 * i);
            }
        }
        if (k == CARD_BG_BYTES / 512) return;
        bg.clus = 0;                        /* broken: not again */
    }
    for (uint32_t i = 0; i < 16; i++) lcd_pal[i] = pal0[i];
    lcd_fill(0, 0, LCD_W, LCD_H, 0);
    lcd_fill(0, 0, LCD_W, LIST_Y - 2, 1);
    lcd_text((LCD_W - 6 * 12) / 2, 2, "CHGAME", 6, LCD_RAINBOW, 2);
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
        lcd_text(8, y + 1, g->title, TITLE_COLS, c, 1);
        if (g->flags & G_DIR) lcd_text(LCD_W - 6, y + 1, ">", 1, c, 1);
    }
    flush(0, LCD_H);
}

/* Centred; at most TITLE_COLS characters. */
static void text_c(uint32_t y, const char *s, uint32_t c)
{
    uint32_t n = 0;
    while (s[n] && n < TITLE_COLS) n++;
    lcd_text((LCD_W - n * 6) / 2, y, s, n, c, 1);
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

/* The panel on, showing the framebuffer, if it is not on yet. */
static void light(void)
{
    if (lit) return;
    lcd_wake();
    lcd_on();
    lit = 1;
}

/* ---- keys ------------------------------------------------------------------------- */

static uint32_t k_prev = BTN_ALL, k_last, k_rep;

/* Newly pressed keys, sampled every 15 ms (debounce), with UP/DOWN repeating
   after 400 ms every 80 ms. Keys held when the menu starts (START at
   power-on) count only after a release: k_prev starts with every key down. */
static uint32_t keys(void)
{
    uint32_t t = sys_ticks(), now, out;
    if (t - k_last < 15u * SYS_TICKS_PER_MS) return 0;
    k_last = t;
    now = hal_buttons();
    out = now & ~k_prev;
    if (out) k_rep = t + 400u * SYS_TICKS_PER_MS;
    else if ((now & (BTN_UP | BTN_DOWN)) && (int32_t)(t - k_rep) >= 0) {
        out = now & (BTN_UP | BTN_DOWN);
        k_rep = t + 80u * SYS_TICKS_PER_MS;
    }
    k_prev = now;
    return out;
}

/* Waits for every key to be up (so a game never starts with A still held). */
static void release(void)
{
    uint32_t t = sys_ticks();
    while (sys_ticks() - t < 30u * SYS_TICKS_PER_MS)
        if (hal_buttons()) t = sys_ticks();
}

static void wait_key(void)
{
    while (!(keys() & (BTN_A | BTN_B | BTN_START))) { }
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
    /* The launch entry, followed down through folders; on any error the menu
       comes up there, saying so. */
    for (k = 0; launch && !rc && k <= DEPTH; k++) {
        for (n = 0; n < ngames && !(games[n].flags & G_LAUNCH); n++) { }
        if (n == ngames) break;
        rc = start(n, app);
    }
    proto_init();
#endif
    if (ngames) draw_list();
    else {
        background();
        box("NO GAMES", 0);
    }
    light();

    for (;;) {
        uint32_t old = sel, old_depth = depth;
#if !CHBOOT_APP
        static uint32_t t_hue;
        if (sys_ticks() - t_hue >= 40u * SYS_TICKS_PER_MS) {   /* a turn of the wheel in ~3.8 s */
            t_hue = sys_ticks();
            lcd_step();
        }
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
        if (!ngames) continue;
        k = keys();
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
