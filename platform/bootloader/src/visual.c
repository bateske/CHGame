/*
 * The SD game menu as pictures, and no text at all (docs/visual-menu.md; the
 * card's files: shared/chgame_card.h, spec/card.md; the card's tree: card.c).
 *
 *   power-on -> the cart's cover (GAMES/COVER.PIC) fades in
 *     launch entry in GAMES/MENU.IDX (and START not held) -> its picture,
 *       installed first if it is not the installed one, then it starts
 *     otherwise the installed game, searched for (GAMES/'s games, then its
 *     folders', depth first), fades in once the cover has had its time
 *
 * A folder's rows are its cover, then its entries (games, and folders by
 * their cover) in MENU.IDX's order, then by title. GAMES/ itself lists only
 * its games: its folders are the categories.
 *   UP/DOWN      the row before or after, round the folder
 *   LEFT/RIGHT   the folder beside: at the top, GAMES/ and its folders in a
 *                ring; below the top, the folders of the same parent
 *   A/START      a game: play it (install first if need be); a folder: open
 *                it; a cover: its first row
 *   B            below the top: back up a level; at the top: the about page
 *                (SYSTEM.PIC), which any key closes
 *
 * Each picture is read from the card when it is shown: there is RAM for one.
 * A screen the card cannot give is drawn from a built-in icon (icons.h).
 */
#include "card.h"
#include "hal.h"
#include "icons.h"
#include "sd.h"
#include "fat.h"
#include "install.h"
#include "appmeta.h"
#include "boot.h"
#include "proto.h"
#include "sys.h"
#include "chgame_bootreq.h"
#include "chgame_card.h"

#define SPLASH_MS   1500u       /* the cover at least this long at power-on */
#define HOLD_MS     1000u       /* the launch game's picture before it starts */
#define ICON_S      8u          /* an icon's pixel on the panel */
#define ICON_X      ((LCD_W - ICON_W * ICON_S) / 2)
#define ICON_Y      8u
#define BAR_X       10u         /* the install bar, in a frame of colour 15 */
#define BAR_Y       112u
#define BAR_W       108u
#define BAR_H       6u
#define PIC_SECTORS (CARD_BG_BYTES / 512)

static uint32_t up[DEPTH];      /* the folders above `here`: up[0] is GAMES/ */
static uint32_t row;            /* 0: the folder's cover; k: games[k - 1] */
static file_t found;

/* ---- pictures ---------------------------------------------------------------------- */

/* A picture in MENU.BG's encoding `skip` sectors into the file at clus: its
   palette to lcd_pal, its pixels to lcd_fb. 0 when it is there; otherwise
   the framebuffer may hold part of it and must be drawn over whole. */
static int pic(uint32_t clus, uint32_t size, uint32_t skip)
{
    fat_stream_t s;
    uint32_t k, lba;
    if (!clus) return 1;
    fat_open(&s, clus, size);
    for (k = 0; k < skip + PIC_SECTORS; k++) {
        if (!(lba = fat_next_lba(&s, buf))) return 1;
        if (k < skip) continue;
        if (sd_read(lba, k > skip ? lcd_fb + (k - skip - 1) * 512 : buf)) return 1;
        if (k == skip) {
            if (w32(buf) != CARD_BG_MAGIC) return 1;
            for (uint32_t i = 0; i < 8; i++)
                ((uint32_t *)(void *)lcd_pal)[i] = w32(buf + CARD_BG_OFF_PALETTE + 4 * i);
        }
    }
    return 0;
}

/* Built-in screen n (icons.h), on black. */
static void icon(uint32_t n)
{
    const uint16_t *b = icons[n];
    for (uint32_t i = 0; i < 16; i++) lcd_pal[i] = pal0[i];
    lcd_fill(0, 0, LCD_W, LCD_H, 0);
    for (uint32_t y = ICON_Y; y < ICON_Y + ICON_H * ICON_S; y += ICON_S, b++)
        for (uint32_t x = ICON_X, m = 0x8000; m; x += ICON_S, m >>= 1)
            if (*b & m) lcd_fill(x, y, ICON_S, ICON_S, LCD_RAINBOW);
}

/* SYSTEM.PIC's screen k, else built-in screen n. */
static void screen(uint32_t k, uint32_t n)
{
    if (pic(sys.clus, sys.size, k * PIC_SECTORS)) icon(n);
}

static int find_cover(const uint8_t *d, void *ctx)
{
    (void)ctx;
    if (!same(d, "COVER   PIC") || d[11] & FAT_ATTR_DIR) return 0;
    found.clus = fat_entry_cluster(d);
    found.size = fat_entry_size(d);
    return 1;
}

/* The row's picture into the framebuffer (nothing is sent). */
static void show(void)
{
    game_t *g = &games[row ? row - 1 : 0];
    if (!row || g->flags & G_DIR) {         /* a cover: this folder's, or the entry's */
        found.clus = 0;
        fat_dir(row ? g->clus : here, buf, find_cover, 0);
        if (pic(found.clus, found.size, 0)) screen(CARD_SYS_FOLDER, ICON_FOLDER);
        return;
    }
    if (!g->clus) screen(CARD_SYS_INSTALLED, ICON_GAME);       /* the program in flash */
    else if (g->flags & G_BAD) screen(CARD_SYS_ERROR + g->err - 1, ICON_ERROR);
    else if (!g->pic || pic(g->clus, g->size, g->pic)) screen(CARD_SYS_GAME, ICON_GAME);
    if (g->flags & G_INSTALLED) lcd_fill(2, 2, 4, 4, CARD_C_MARK);   /* the chip */
}

/* Whole frames toward lcd_dark == to: 0 the picture, LCD_DARK black. */
static void fade(uint32_t to)
{
    while (lcd_dark != to) {
        lcd_dark += lcd_dark < to ? 1 : (uint32_t)-1;
        lcd_flush(0, LCD_H);
    }
}

/* Through black to the row's picture. */
static void crossfade(void)
{
    fade(LCD_DARK);
    show();
    fade(0);
}

/* The rainbow's next step every 40 ms (a turn of the wheel in ~3.8 s). */
static void tick(void)
{
#if LCD_TURNS
    static uint32_t t_hue;
    if (sys_ticks() - t_hue >= 40u * SYS_TICKS_PER_MS) {
        t_hue = sys_ticks();
        lcd_step();
    }
#endif
}

static __attribute__((noinline)) void wait_ms(uint32_t t0, uint32_t ms)
{
    while (sys_ticks() - t0 < ms * SYS_TICKS_PER_MS) tick();
}

void menu_progress(uint32_t done, uint32_t total)
{
    lcd_fill(BAR_X, BAR_Y, (BAR_W * (done + 1)) / total, BAR_H, LCD_RAINBOW);
    lcd_flush(BAR_Y, BAR_Y + BAR_H);
}

/* ---- the tree ---------------------------------------------------------------------- */

static uint32_t find(uint32_t clus)     /* the entry starting at clus (ngames: none) */
{
    uint32_t i = 0;
    while (i < ngames && games[i].clus != clus) i++;
    return i;
}

static void enter(uint32_t i, int app)  /* into the folder of entry i */
{
    up[depth++] = here;
    here = games[i].clus;
    scan(app);
}

static uint32_t leave(int app)          /* a level up; the entry of the folder left */
{
    uint32_t c = here;
    here = up[--depth];
    scan(app);
    return find(c);
}

/* LEFT (-1) or RIGHT (1): the folder beside this one, on its cover. At the
   top the ring is GAMES/ itself and its folders; below, the folders of the
   same parent. */
static void flip(uint32_t d, int app)
{
    uint32_t i, n, k;
    n = depth <= 1;                         /* (GAMES/ itself, at the top: entry ngames) */
    i = depth ? leave(app) : ngames;
    n += ngames;
    for (k = 0; k < n; k++) {
        i = (i + n + d) % n;
        if (i == ngames) break;
        if (games[i].flags & G_DIR) {
            enter(i, app);
            break;
        }
    }
    row = 0;
}

/* Depth first from GAMES/ to the first game flagged `want`: G_INSTALLED
   looks in every folder, G_LAUNCH only in folders flagged too. The menu is
   left on it (row) and 1 returned; else back at GAMES/'s cover, 0. */
static int seek(uint32_t want, int app)
{
    uint32_t i = 0, j, go = G_DIR | (want & G_LAUNCH);
    for (;;) {
        for (j = 0; j < ngames; j++)
            if ((games[j].flags & (G_DIR | want)) == want) {
                row = j + 1;
                return 1;
            }
        while (i < ngames && (games[i].flags & go) != go) i++;
        if (i < ngames && depth < DEPTH) {
            enter(i, app);
            i = 0;
        } else if (depth) {
            i = leave(app) + 1;
        } else {
            row = 0;
            return 0;
        }
    }
}

/* A or START on entry i: a folder opens on its first row (the installed game
   if it is there), a game runs (installed first if need be). Returns only for
   a folder (0) or an error (INST_E_*). */
static int start(uint32_t i, int app)
{
    game_t *g = &games[i];
    int rc;
    if (g->flags & G_DIR) {
        if (depth < DEPTH) {
            enter(i, app);
            row = ngames ? sel + 1 : 0;
        }
        return INST_OK;
    }
    if (g->flags & G_BAD) return g->err;
    if (!(g->flags & G_INSTALLED) || CHBOOT_APP) {
        lcd_fill(BAR_X - 2, BAR_Y - 2, BAR_W + 4, BAR_H + 4, LCD_RAINBOW);     /* the bar, over the picture */
        lcd_fill(BAR_X - 1, BAR_Y - 1, BAR_W + 2, BAR_H + 2, CARD_C_INK);
        lcd_flush(0, LCD_H);
        rc = install(g->clus, g->size, buf);
        if (rc) return rc;
    }
#if CHBOOT_APP
    /* Dry run (build.sh app): the package checked, nothing written. */
    icon(ICON_OK);
    lcd_flush(0, LCD_H);
    wait_key();
    show();
    lcd_flush(0, LCD_H);
    return INST_OK;
#endif
    fade(LCD_DARK);
    release();
    boot_reset(CHGAME_BOOTREQ_RUN);
}

/* ---- the menu ------------------------------------------------------------------------ */

void menu_main(int app, int launch)
{
    uint32_t k, n = 0, t0, old, was, modal = 0;
    int rc = INST_OK;

    (void)launch;
    lcd_reset();
    if (!sd_init() && !fat_mount(buf) && fat_dir(0, buf, find_games, 0) == 1)
        n = scan(app);                      /* the card is read during the panel's waits */
#if !CHBOOT_APP
    if (!n && app == APP_VALID)
        boot_reset(CHGAME_BOOTREQ_RUN);     /* nothing on the card: run what is installed */
#endif
    if (!n) {                               /* nothing to show: USB mode, saying so (B there looks again) */
        icon(ICON_FOLDER);
        light();
        return;
    }
    show();                                 /* the cart's cover */
    lcd_dark = LCD_DARK;
    light();
    fade(0);
    t0 = sys_ticks();
#if !CHBOOT_APP
    /* The launch entry, followed down through flagged folders: after the
       cover, its picture, then it starts (an error: the menu, there). Else
       the installed game, wherever it is on the card. */
    if (launch && seek(G_LAUNCH, app)) n = 0;     /* (n: GAMES/'s entries until here, so 0 means launch) */
    else if (app == APP_VALID && !seek(G_INSTALLED, app)) {
        stray = 1;                          /* the program in flash is on no card entry: first in GAMES/ */
        scan(app);
        row = 1;
    }
    proto_init();
#endif
    if (row) {                              /* from the cover, once it has had its time */
        wait_ms(t0, SPLASH_MS);
        crossfade();
    }
#if !CHBOOT_APP
    if (!n) {
        if (games[row - 1].flags & G_INSTALLED) wait_ms(sys_ticks(), HOLD_MS);
        rc = start(row - 1, app);
    }
#endif

    for (;;) {
        old = row;
        was = here;
        tick();
#if !CHBOOT_APP
        proto_task();
        if (proto_claimed) {
            icon(ICON_USB);
            lcd_flush(0, LCD_H);
            return;
        }
#endif
        if (rc) {                           /* until a key: the error's screen */
            if (rc == INST_E_LOST)          /* the old program is gone (and its metadata, so no scan marks it again) */
                for (n = 0; n < ngames; n++) games[n].flags &= (uint8_t)~G_INSTALLED;
            screen(CARD_SYS_ERROR + (uint32_t)rc - 1, ICON_ERROR);
            lcd_flush(0, LCD_H);
            rc = INST_OK;
            modal = 1;
            continue;
        }
        k = keys();
        if (modal) {                        /* an error or the about page: any key closes it */
            if (k) {
                modal = 0;
                show();
                lcd_flush(0, LCD_H);
            }
            continue;
        }
#if CHBOOT_APP
        if (k & BTN_SELECT) boot_reset(CHGAME_BOOTREQ_USB);
#endif
        if (!row && k & (BTN_A | BTN_START)) k = BTN_DOWN;   /* A on a cover: its first row */
        if (k & (BTN_UP | BTN_DOWN)) {
            n = ngames + 1;
            do row = (row + n + (k & BTN_UP ? (uint32_t)-1 : 1u)) % n;
            while (row && !depth && games[row - 1].flags & G_DIR);
        }
        if (k & (BTN_LEFT | BTN_RIGHT)) {  /* the folder beside: it slides in sideways */
            flip(k & BTN_LEFT ? (uint32_t)-1 : 1u, app);
            show();
            lcd_slide(k & BTN_LEFT ? LCD_FROM_LEFT : LCD_FROM_RIGHT);
            continue;
        }
        if (k & BTN_B) {
            if (depth > 1) row = leave(app) + 1;
            else if (!pic(sys.clus, sys.size, CARD_SYS_ABOUT * PIC_SECTORS)) {
                lcd_flush(0, LCD_H);
                modal = 1;
                continue;
            } else show();                  /* (no about page: the row's picture back, as on the panel) */
        }
        if (row && k & (BTN_A | BTN_START)) rc = start(row - 1, app);
        if (here != was) crossfade();       /* in or out of a folder: through black */
        else if (row != old) {              /* the same folder: it slides in */
            show();
            lcd_slide(k & BTN_UP ? LCD_FROM_TOP : LCD_FROM_BOTTOM);
        }
    }
}

void menu_usb_notice(void)
{
#if !CHBOOT_APP
    proto_init();                           /* enumerate first; the panel can wait */
#endif
    lcd_reset();
    icon(ICON_USB);
    light();
}
