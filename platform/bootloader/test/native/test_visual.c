/* Whole-boot scenarios with the visual menu (src/visual.c): each boot is a
 * fresh process (host.h). argv[1]: the manifest written by boot_cases.py
 * (card images, packages); argv[2]: the folder for frame dumps.
 *
 * img_vcart (boot_cases.py: visual_cards), as the menu orders it:
 *   GAMES/            cover; rows: ZULU (BRAVO's payload), MIKE, AAA EXTRA
 *                     (copied by hand: no picture, not in the index); its
 *                     folders FOLDER ONE, TWO and EMPTY (by hand, no cover)
 *                     are the categories, in a ring with GAMES/ itself
 *     FOLDER ONE/     cover; rows: ALPHA GAME, INNER (by its cover), OTHER
 *                     (no cover)
 *       INNER/        cover; BRAVO
 *       OTHER/        OSCAR
 *     TWO/            (no cover) ROMEO
 *   SYSTEM.PIC        nine test pictures, one per screen
 * Every game but EXTRA has a picture. img_vcartlaunch is the same cart
 * launching ALPHA GAME; img_vcartbad breaks pictures (vcartbad below).
 * Power-on stays on the cover (A there: the installed game's picture); a
 * launch game runs at once if it is installed, else waits on its picture. */
#include "testlib.h"
#include "hal.h"
#include "lcd.h"                  /* (LCD_SLIDE_STEPS) */
#include "proto.h"
#include "bootreq.h"
#include "chgame_bootreq.h"
#include "chg_format.h"

#define MAXP 40
static struct { char name[16]; int code; uint32_t len, crc; char path[512]; } pk[MAXP];
static int npk;
static char img_fat32[512], img_fat32sys[512], img_vcart[512], img_vcartlaunch[512], img_vcartbad[512], img_cartbig[512];
static const char *frames, *frame_prefix = "";
static uint8_t payload[CHGAME_APP_MAX_SIZE];

#define READY 3200u                          /* ms: the menu takes keys (splash, search, fades done) */
#define STEP  700u                           /* ms between presses: a move reads a picture and slides it in */

static int pkg(const char *name)
{
    for (int i = 0; i < npk; i++) if (!strcmp(pk[i].name, name)) return i;
    fprintf(stderr, "no package %s\n", name); exit(2);
}

static void preinstall(const char *name)
{
    int i = pkg(name);
    FILE *f = fopen(pk[i].path, "rb");
    fseek(f, CHG_HEADER_BYTES, SEEK_SET);
    size_t n = fread(payload, 1, pk[i].len, f);
    fclose(f);
    host_install_app(payload, (uint32_t)n);
}

static int installed_is(const char *name)
{
    int i = pkg(name);
    return app_valid_now() && le32(B->flash + CHGAME_META_ADDR + 8) == pk[i].len &&
           le32(B->flash + CHGAME_META_ADDR + 12) == pk[i].crc;
}

static void snap(const char *tag)
{
    char p[1024];
    snprintf(p, sizeof p, "%s/%sv_%s.ppm", frames, frame_prefix, tag);
    lcd_model_dump_ppm(&B->lcd, p);
}

static void card(const char *path) { sd_model_insert(&B->sd, path ? SD_SDHC : SD_NONE, path); }

static void press(uint32_t at_ms, uint32_t mask)
{
    host_keys(at_ms, mask);
    host_keys(at_ms + 100, 0);
}

/* n presses from READY, STEP apart; the boot ends a second after the last */
static void keys(const uint32_t *k, int n)
{
    for (int i = 0; i < n; i++) press(READY + STEP * (uint32_t)i, k[i]);
    B->limit_us = (uint64_t)(READY + STEP * (uint32_t)n + 1000) * 1000;
}

static void lcd_sane(const char *what)
{
    CHECK(B->lcd.timing_violations == 0, "%s: panel timing violations %u", what, B->lcd.timing_violations);
    CHECK(B->lcd.garbage_shown == 0, "%s: display switched on over unwritten pixels", what);
    CHECK(B->bus_conflicts == 0, "%s: both chip selects low", what);
    CHECK(B->spi_off_xfers == 0, "%s: %u SPI transfers with SPI1 off (would hang the chip)", what, B->spi_off_xfers);
    CHECK(B->wrong_frames == 0, "%s: %u transfers in the wrong frame size", what, B->wrong_frames);
    CHECK(B->sd.init_fast == 0, "%s: card identified above 400 kHz", what);
}

/* The menu's order on img_fat32 (no index: by title), as boot_cases.py wrote it */
static int menu_index(const char *name) { return pkg(name); }

static uint16_t ref[LCD_W * LCD_H];
static void remember(void) { memcpy(ref, B->lcd.fb, sizeof ref); }
static int same_as_remembered(void) { return !memcmp(ref, B->lcd.fb, sizeof ref); }
/* The same inside the installed game's border (it turns with the rainbow). */
static int same_inside_border(void)
{
    for (int y = 1; y < 127; y++)
        if (memcmp(ref + y * 128 + 1, B->lcd.fb + y * 128 + 1, 126 * sizeof ref[0])) return 0;
    return 1;
}
static uint16_t about_ref[LCD_W * LCD_H];
static void remember_about(void) { memcpy(about_ref, B->lcd.fb, sizeof about_ref); }
static int same_as_about(void) { return !memcmp(about_ref, B->lcd.fb, sizeof about_ref); }

/* ---- power-on --------------------------------------------------------------------- */

static void t_no_card_runs_app(void)
{
    preinstall("BRAVO.CHG");
    card(NULL);
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "no card: RUN reset");
    CHECK(host_boot() == END_JUMP, "then the app starts");
    CHECK(B->flash_ops == 0, "no flash writes");
}

static void t_no_card_no_app(void)
{
    card(NULL);
    B->limit_us = 1500000;
    CHECK(host_boot() == END_HANG, "no card, no app: waits");
    CHECK(B->usb_up && B->lcd.on, "in USB mode, saying so");
    lcd_sane("no games");
    snap("no_games");
}

static void t_splash(void)
{
    card(img_vcart);
    B->limit_us = 4000000;
    CHECK(host_boot() == END_HANG, "the menu waits");
    CHECK(B->usb_up, "USB alive");
    CHECK(B->flash_ops == 0, "showing the menu writes nothing");
    lcd_sane("splash");
    snap("splash");                          /* no program: the cover stays */
}

static uint16_t cover_ref[LCD_W * LCD_H];

/* A boot with ALPHA installed (it is in FOLDER ONE) and these keys */
static int alpha_keys(const uint32_t *k, int n)
{
    host_init();
    preinstall("ALPHA.CHG");
    card(img_vcart);
    keys(k, n);
    return host_boot();
}

#if !LCD_TURNS                               /* (the cover turns in the rainbow: compared in the static style) */
#define ON_COVER(what) CHECK(!memcmp(cover_ref, B->lcd.fb, sizeof cover_ref), what)
#else
#define ON_COVER(what) (void)0
#endif

/* Power-on stays on the cart's cover, installed game or not; A on the cover
   shows the installed game's picture, where A runs it and B goes back. */
static void t_found(void)
{
    static const uint32_t a[] = { BTN_A }, b[] = { BTN_B }, sel[] = { BTN_SELECT }, ba[] = { BTN_B, BTN_A };
    static const uint32_t astart[] = { BTN_A, BTN_START }, aa[] = { BTN_A, BTN_A }, ab[] = { BTN_A, BTN_B };
    static const uint32_t adown[] = { BTN_A, BTN_DOWN, BTN_LEFT, BTN_SELECT };
    static const uint32_t inb[] = { BTN_RIGHT, BTN_DOWN, BTN_B }, insel[] = { BTN_RIGHT, BTN_DOWN, BTN_SELECT };
    card(img_vcart);                         /* the cart's cover, nothing installed, for comparing */
    B->limit_us = READY * 1000;
    CHECK(host_boot() == END_HANG, "the cover");
    memcpy(cover_ref, B->lcd.fb, sizeof cover_ref);
    host_init();
    preinstall("ALPHA.CHG");
    card(img_vcart);
    B->limit_us = READY * 1000;
    CHECK(host_boot() == END_HANG, "menu");
    lcd_sane("found");
    ON_COVER("power-on with a game installed: the cover stays");
    CHECK(alpha_keys(a, 1) == END_HANG, "A on the cover: the installed game's picture");
    lcd_sane("found");
    snap("found");                           /* ALPHA GAME, in FOLDER ONE, with the border */
    {                                        /* the installed game's border: the outermost pixels, one colour */
        uint32_t odd = 0;
        for (int i = 0; i < 128; i++)
            odd += (B->lcd.fb[i] != B->lcd.fb[0]) + (B->lcd.fb[127 * 128 + i] != B->lcd.fb[0])
                 + (B->lcd.fb[i * 128] != B->lcd.fb[0]) + (B->lcd.fb[i * 128 + 127] != B->lcd.fb[0]);
        CHECK(odd == 0, "the border: rows 0 and 127, columns 0 and 127, in one colour (%u pixels differ)", odd);
        CHECK(B->lcd.fb[129] != B->lcd.fb[0] || B->lcd.fb[2 * 128 + 2] != B->lcd.fb[0], "one pixel wide");
#if !LCD_TURNS
        CHECK(B->lcd.fb[0] == 0xFFBA, "static: the border is the menu's near-white #FFF4D6 (%04X)", B->lcd.fb[0]);
#endif
    }
    remember();
    CHECK(alpha_keys(astart, 2) == END_HANG && same_inside_border(), "START does nothing");
    CHECK(alpha_keys(inb, 3) == END_HANG, "B in a folder of the root");
    ON_COVER("B in a folder of the root: the cart's cover");
    CHECK(alpha_keys(insel, 3) == END_HANG, "SELECT");
    ON_COVER("SELECT: the cart's cover");
    CHECK(alpha_keys(b, 1) == END_HANG, "B on the cart's cover: the about page");
    snap("about");
    remember_about();
    CHECK(alpha_keys(sel, 1) == END_HANG && same_as_about(), "SELECT at the root: the about page");
    CHECK(alpha_keys(ba, 2) == END_HANG, "any key closes it");
    ON_COVER("any key closes it: the cover again");
    CHECK(alpha_keys(adown, 4) == END_HANG && same_inside_border(), "the installed game's picture: only A and B count");
    CHECK(alpha_keys(ab, 2) == END_HANG, "...B there");
    ON_COVER("...B there: the cover again");
    CHECK(alpha_keys(aa, 2) == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "...A there: RUN");
    CHECK(B->flash_ops == 0, "nothing written");
}

static void t_found_first_copy(void)
{
    preinstall("BRAVO.CHG");                 /* ZULU at the top holds the same payload */
    card(img_vcart);
    press(READY, BTN_A);
    B->limit_us = (READY + 1000) * 1000;
    CHECK(host_boot() == END_HANG, "menu");
    snap("found_home");                      /* A on the cover: ZULU, the first copy in the search's order */
}

static void t_stray(void)
{
    static const uint32_t a[] = { BTN_A }, aa[] = { BTN_A, BTN_A }, down[] = { BTN_DOWN };
    preinstall("STRAY.CHG");                 /* on no card entry */
    card(img_vcart);
    keys(a, 1);
    CHECK(host_boot() == END_HANG, "menu");
    snap("stray");                           /* A on the cover: the program in flash, SYSTEM.PIC's picture of it */
    remember();
    host_init();
    preinstall("STRAY.CHG");
    card(img_vcart);
    keys(down, 1);
    CHECK(host_boot() == END_HANG && same_inside_border(), "DOWN from the cover: GAMES/ lists it first");
    host_init();
    preinstall("STRAY.CHG");
    card(img_vcart);
    keys(aa, 2);
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "A on it: RUN");
    CHECK(B->flash_ops == 0, "with no flash write");
}

/* ---- moving ----------------------------------------------------------------------- */

static void t_rows(void)
{
    static const uint32_t k[] = { BTN_DOWN, BTN_DOWN, BTN_DOWN, BTN_DOWN, BTN_UP };
    static const char *tag[] = { "row_zulu", "row_mike", "row_extra", "row_wrap", "row_up" };
    for (int n = 1; n <= 5; n++) {
        host_init();
        card(img_vcart);
        keys(k, n);
        CHECK(host_boot() == END_HANG, "%d moves", n);
        CHECK(B->lcd.col_writes == 0 && B->lcd.row_writes >= (LCD_SLIDE_STEPS - 1u) * n, "%d moves: slides up or down (%u part steps)", n, B->lcd.row_writes);   /* (a slide's 8th step is the whole picture) */
        lcd_sane(tag[n - 1]);
        snap(tag[n - 1]);
    }
}

static void t_flip(void)
{
    static const uint32_t k[] = { BTN_RIGHT, BTN_RIGHT, BTN_RIGHT, BTN_RIGHT, BTN_LEFT };
    static const char *tag[] = { "flip_one", "flip_two", "flip_empty", "flip_home", "flip_left" };
    for (int n = 1; n <= 5; n++) {
        host_init();
        card(img_vcart);
        keys(k, n);
        CHECK(host_boot() == END_HANG, "%d flips", n);
        CHECK(B->lcd.col_writes == (LCD_SLIDE_STEPS - 1u) * n, "%d flips: each slides in sideways (%u part steps, then the whole)", n, B->lcd.col_writes);
        CHECK(B->lcd.first_col_xs == 2 + 128 - 128 / LCD_SLIDE_STEPS, "RIGHT: the first step at the right edge (x %u)", B->lcd.first_col_xs - 2u);
        lcd_sane(tag[n - 1]);
        snap(tag[n - 1]);
    }
    static const uint32_t left[] = { BTN_LEFT };
    host_init();
    card(img_vcart);
    keys(left, 1);
    CHECK(host_boot() == END_HANG, "LEFT from the cover");
    CHECK(B->lcd.col_writes == LCD_SLIDE_STEPS - 1 && B->lcd.first_col_xs == 2, "LEFT: from the left edge (x %u)", B->lcd.first_col_xs - 2u);
}

/* The zoo card has no folders: at the top LEFT and RIGHT have nowhere to go,
   and do nothing. */
static void t_flip_no_folders(void)
{
    static const uint32_t down[] = { BTN_DOWN }, lr[] = { BTN_DOWN, BTN_LEFT, BTN_RIGHT };
    card(img_fat32sys);
    keys(down, 1);
    CHECK(host_boot() == END_HANG, "the first game");
    remember();
    host_init();
    card(img_fat32sys);
    keys(lr, 3);
    CHECK(host_boot() == END_HANG && same_as_remembered(), "LEFT and RIGHT with no folders: the same picture stays");
    CHECK(B->lcd.col_writes == 0, "no sideways slide (%u part steps)", B->lcd.col_writes);
}

static void t_folders(void)
{
    static const uint32_t entry[] = { BTN_RIGHT, BTN_DOWN, BTN_DOWN };
    static const uint32_t in[] = { BTN_RIGHT, BTN_DOWN, BTN_DOWN, BTN_A };
    static const uint32_t out[] = { BTN_RIGHT, BTN_DOWN, BTN_DOWN, BTN_A, BTN_B };
    static const uint32_t side[] = { BTN_RIGHT, BTN_DOWN, BTN_DOWN, BTN_A, BTN_RIGHT };
    static const uint32_t round[] = { BTN_RIGHT, BTN_DOWN, BTN_DOWN, BTN_A, BTN_RIGHT, BTN_RIGHT, BTN_DOWN, BTN_A };
    card(img_vcart);
    keys(entry, 3);
    CHECK(host_boot() == END_HANG, "FOLDER ONE's third row: INNER, by its cover");
    snap("inner_entry");
    remember();
    host_init();
    card(img_vcart);
    keys(in, 4);
    CHECK(host_boot() == END_HANG, "A on it: INNER, on its first game");
    snap("inner_bravo");
    host_init();
    card(img_vcart);
    keys(out, 5);
    CHECK(host_boot() == END_HANG, "B: back on INNER's row");
    CHECK(same_as_remembered(), "the same picture as before A");
    host_init();
    card(img_vcart);
    keys(side, 5);
    CHECK(host_boot() == END_HANG, "RIGHT in INNER: OTHER, the folder beside it");
    snap("other");
    host_init();
    card(img_vcart);
    keys(round, 8);
    CHECK(host_boot() == END_RESET && installed_is("BRAVO.CHG"), "RIGHT twice comes round to INNER: A installs BRAVO");
    lcd_sane("folders");
}

/* ---- installing ------------------------------------------------------------------- */

static void t_install(void)
{
    static const uint32_t mike[] = { BTN_DOWN, BTN_DOWN, BTN_A };
    card(img_vcart);
    keys(mike, 3);
    B->limit_us = 12000000;
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "MIKE: install, RUN");
    CHECK(installed_is("MIKE.CHG"), "MIKE installed");
    CHECK(B->boot_region_writes == 0, "boot region untouched");
    lcd_sane("install");
    uint32_t total = B->flash_ops;
    CHECK(host_boot() == END_JUMP, "MIKE starts");
    /* the panel when half the writing is done: boots stopped 5 ms later each time */
    for (uint64_t at = (uint64_t)(READY + 2 * STEP) * 1000; at < 12000000; at += 5000) {
        host_init();
        card(img_vcart);
        keys(mike, 3);
        B->limit_us = at;
        if (host_boot() == END_HANG && B->flash_ops >= total / 2) break;
    }
    CHECK(B->flash_ops >= total / 2 && B->flash_ops < total, "partway through writing (%u of %u ops)", B->flash_ops, total);
    snap("installing");                      /* the bar over MIKE's picture */
    /* installed: A on the cover shows it, A again runs it, nothing written */
    host_init();
    preinstall("MIKE.CHG");
    card(img_vcart);
    press(READY, BTN_A);
    B->limit_us = (READY + 1000) * 1000;
    host_boot();
    snap("mike_installed");
    host_init();
    preinstall("MIKE.CHG");
    card(img_vcart);
    press(READY, BTN_A);
    press(READY + STEP, BTN_A);
    B->limit_us = 8000000;
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN && B->flash_ops == 0,
          "A on the installed game: RUN, no write (%u ops)", B->flash_ops);
}

static void t_errors(void)
{
    /* img_fat32 (the zoo, by title, no folders) with SYSTEM.PIC added; BRAVO
       installed (nothing may be written over it). The menu starts on the
       cover: each row is that many presses of DOWN from it. */
    static const struct { const char *name; const char *tag; } bad[] = {
        { "BADPCRC.CHG", "error_2" }, { "BOOTIMG.CHG", "error_3" }, { "WRONGTGT.CHG", "error_5" },
    };
    for (unsigned i = 0; i < sizeof bad / sizeof bad[0]; i++) {
        uint32_t k[64];
        int to = menu_index(bad[i].name), n = 0;
        host_init();
        preinstall("BRAVO.CHG");
        card(img_fat32sys);
        for (int j = -1; j < to; j++) k[n++] = BTN_DOWN;
        if (i == 2) {                        /* (a header the menu refuses shows its error as its picture) */
            keys(k, n);
            CHECK(host_boot() == END_HANG, "%s's row", bad[i].name);
            snap("bad_row");
        }
        host_init();
        preinstall("BRAVO.CHG");
        card(img_fat32sys);
        k[n++] = BTN_A;
        keys(k, n);
        CHECK(host_boot() == END_HANG, "%s: the error, until a key", bad[i].name);
        CHECK(B->flash_ops == 0 && installed_is("BRAVO.CHG"), "%s: nothing written", bad[i].name);
        snap(bad[i].tag);
        host_init();
        preinstall("BRAVO.CHG");
        card(img_fat32);                     /* no SYSTEM.PIC: the built-in screen */
        keys(k, n);
        CHECK(host_boot() == END_HANG, "%s without SYSTEM.PIC", bad[i].name);
        if (!i) snap("error_icon");
    }
}

static void t_card_dies_mid_install(void)
{
    static const uint32_t mike[] = { BTN_DOWN, BTN_DOWN, BTN_A };
    preinstall("BRAVO.CHG");                 /* ZULU's payload (the menu starts on the cover all the same) */
    card(img_vcart);
    keys(mike, 3);
    B->card_dies_on_flash = 1;
    B->limit_us = 12000000;
    CHECK(host_boot() == END_HANG, "card dies in pass 2: the error");
    CHECK(!app_valid_now(), "no program left (never a partial one)");
    snap("install_failed");
    host_power_cycle();
    host_keys_clear();
    B->card_dies_on_flash = 0;
    keys(mike, 3);
    B->limit_us = 12000000;
    CHECK(host_boot() == END_RESET && installed_is("MIKE.CHG"), "next power-on: MIKE installs");
}

static void t_powercut_sweep(void)
{
    static const uint32_t mike[] = { BTN_DOWN, BTN_DOWN, BTN_A };
    card(img_vcart);                         /* (no program: the menu starts on the cover) */
    keys(mike, 3);
    B->limit_us = 12000000;
    host_boot();
    uint32_t total = B->flash_ops;
    CHECK(installed_is("MIKE.CHG") && total > 4, "reference install (%u ops)", total);
    int bad = 0;
    for (uint32_t k = 1; k <= total; k += (total > 40 ? 3 : 1)) {
        host_init();
        card(img_vcart);
        keys(mike, 3);
        B->limit_us = 12000000;
        B->cut_at_op = k;
        if (host_boot() != END_POWERCUT) { bad++; continue; }
        B->cut_at_op = 0;
        host_keys_clear();
        int complete = installed_is("MIKE.CHG");
        if (app_valid_now() && !complete) { bad++; fprintf(stderr, "cut %u: a partial image is launchable\n", k); }
        keys(mike, 3);
        B->limit_us = 12000000;
        int end = host_boot();
        if (end == END_JUMP) { bad++; fprintf(stderr, "cut %u: jumped without a RUN request\n", k); }
        if (!installed_is("MIKE.CHG")) { bad++; fprintf(stderr, "cut %u: reinstall failed (end %d)\n", k, end); }
        if (B->boot_region_writes) { bad++; fprintf(stderr, "cut %u: boot region written\n", k); }
    }
    CHECK(bad == 0, "power cut across the %u flash operations of an install", total);
}

/* ---- launch ----------------------------------------------------------------------- */

/* The launch game, not installed: the cover, then its picture, and the menu
   waits there (A installs it). A power-on never writes flash by itself. */
static void t_launch(void)
{
    static const uint32_t alpha[] = { BTN_RIGHT, BTN_DOWN };
    card(img_vcart);                         /* ALPHA GAME's picture, reached by hand, for comparing */
    keys(alpha, 2);
    CHECK(host_boot() == END_HANG, "ALPHA GAME by hand");
    remember();
    host_init();
    card(img_vcartlaunch);
    B->limit_us = 1000000;
    CHECK(host_boot() == END_HANG, "the cover first");
    snap("launch_cover");
    host_init();
    card(img_vcartlaunch);
    B->limit_us = READY * 1000;
    CHECK(host_boot() == END_HANG, "then the launch game's picture, waiting");
    CHECK(same_as_remembered(), "ALPHA GAME, inside FOLDER ONE, no border");
    CHECK(B->flash_ops == 0, "nothing written by the power-on (%u ops)", B->flash_ops);
    lcd_sane("launch");
    snap("launch_game");
    host_init();
    card(img_vcartlaunch);
    press(READY, BTN_A);
    B->limit_us = 12000000;
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "A: it installs, RUN");
    CHECK(installed_is("ALPHA.CHG"), "ALPHA GAME installed");
    CHECK(host_boot() == END_JUMP, "and it starts");
}

static void t_launch_installed(void)
{
    preinstall("ALPHA.CHG");
    card(img_vcartlaunch);
    B->limit_us = 4000000;
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "launch game installed: RUN at once");
    CHECK(B->flash_ops == 0, "nothing written (%u ops)", B->flash_ops);
    CHECK(!B->lcd.on && B->lcd.pixels == 0, "the panel never switched on");
    CHECK(B->now_us < 1000000, "power-on to RUN in %llu ms", (unsigned long long)(B->now_us / 1000));
    lcd_sane("launch installed");
}

static void t_launch_start_held(void)
{
    preinstall("ALPHA.CHG");
    card(img_vcartlaunch);
    host_keys(0, BTN_START);                 /* held from power-on... */
    host_keys(1500, 0);
    B->limit_us = READY * 1000;
    CHECK(host_boot() == END_HANG, "START held at power-on: the menu, not the launch game");
    CHECK(B->flash_ops == 0, "nothing written");
    snap("launch_start");
}

/* ---- USB -------------------------------------------------------------------------- */

static void t_usb_notice(void)
{
    preinstall("ALPHA.CHG");
    card(img_vcart);
    bootreq_set(CHGAME_BOOTREQ_USB);
    B->limit_us = 1500000;
    CHECK(host_boot() == END_HANG && B->usb_up, "USB request: upload mode");
    CHECK(B->sd.cmds == 0, "card not touched");
    lcd_sane("usb notice");
    snap("usb_notice");
    bootreq_set(CHGAME_BOOTREQ_USB);
    press(600, BTN_B);
    CHECK(host_boot() == END_RESET && B->retained[0] == 0, "B leaves USB mode for the menu");
}

static void t_upload_at_menu(void)
{
    uint8_t img[8192];
    preinstall("ALPHA.CHG");
    card(img_vcart);
    make_image(img, sizeof img, 77);
    push_upload(img, sizeof img, 1);
    CHECK(host_boot() == END_RESET && B->retained[0] == CHGAME_BOOTREQ_RUN, "upload at the menu, then RUN");
    CHECK(app_valid_now() && le32(B->flash + CHGAME_META_ADDR + 8) == sizeof img, "uploaded sketch installed");
    host_power_cycle();
    press(READY, BTN_A);
    B->limit_us = (READY + 1000) * 1000;
    CHECK(host_boot() == END_HANG, "next power-on: the cover; A: the program in flash");
    snap("usb_sketch");
}

/* ---- pictures the card cannot give ------------------------------------------------- */

static void t_bad_pictures(void)
{
    /* img_vcartbad: MIKE's picture field points past its file, ZULU's file
       is cut halfway through its picture, FOLDER ONE's COVER.PIC is short,
       and there is no SYSTEM.PIC: every one of them is the built-in screen */
    static const uint32_t zulu[] = { BTN_DOWN };
    static const uint32_t mike[] = { BTN_DOWN, BTN_DOWN };
    static const uint32_t one[] = { BTN_RIGHT };
    static const uint32_t extra[] = { BTN_DOWN, BTN_DOWN, BTN_DOWN };
    card(img_vcartbad);
    keys(extra, 3);
    CHECK(host_boot() == END_HANG, "EXTRA: no picture");
    lcd_sane("bad pictures");
    snap("bad_extra");
    remember();
    host_init();
    card(img_vcartbad);
    keys(zulu, 1);
    CHECK(host_boot() == END_HANG, "ZULU, cut short");
#if !LCD_TURNS                               /* (the static style: in the rainbow, colour 15 is never twice the same) */
    CHECK(same_as_remembered(), "ZULU's broken picture: the no-picture screen");
#endif
    host_init();
    card(img_vcartbad);
    keys(mike, 2);
    CHECK(host_boot() == END_HANG, "MIKE, offset past its end");
#if !LCD_TURNS
    CHECK(same_as_remembered(), "MIKE's missing picture: the no-picture screen");
#endif
    host_init();
    card(img_vcartbad);
    keys(one, 1);
    CHECK(host_boot() == END_HANG, "FOLDER ONE, COVER.PIC short");
    snap("bad_cover");
}

/* 250 games in one folder: 240 listed, UP from the cover wraps to the last */
static void t_full_folder(void)
{
    card(img_cartbig);
    press(READY, BTN_UP);
    press(READY + STEP, BTN_A);
    B->limit_us = 12000000;
    CHECK(host_boot() == END_RESET && installed_is("G239.CHG"), "UP from the cover: GAME 239, and it installs");
}

/* The real card (`chgame card`): the splash, each folder's cover, each game's
   picture (frames for the docs, tools/screens.py), and every program
   installed from a fresh board through its folder (code: folder row << 8 |
   row; all the casino's games are in folders). */
static void t_real_card(void)
{
    char tag[32];
    uint32_t k[64];
    int last = -1;
    static const uint32_t b[] = { BTN_B };
    card(img_fat32);
    B->limit_us = READY * 1000;
    CHECK(host_boot() == END_HANG, "real card: the splash");
    lcd_sane("real splash");
    snap("real_splash");
    host_init();
    card(img_fat32);
    keys(b, 1);
    CHECK(host_boot() == END_HANG, "B at the top: the about page");
    snap("real_about");
    for (int i = 0; i < npk; i++) {
        int folder = pk[i].code >> 8, row = pk[i].code & 255, n = 0;
        CHECK(folder != 255, "%s: in a folder", pk[i].name);
        for (int f = 0; f <= folder; f++) k[n++] = BTN_RIGHT;
        if (folder != last) {                /* its folder's cover */
            host_init();
            card(img_fat32);
            keys(k, n);
            host_boot();
            snprintf(tag, sizeof tag, "real_cover_%d", folder);
            snap(tag);
            last = folder;
        }
        for (int r = 0; r <= row; r++) k[n++] = BTN_DOWN;
        host_init();
        card(img_fat32);
        keys(k, n);
        host_boot();
        snprintf(tag, sizeof tag, "real_game_%02d", i);
        snap(tag);
        host_init();
        card(img_fat32);
        k[n++] = BTN_A;
        keys(k, n);
        B->limit_us += 8000000;
        int end = host_boot();
        CHECK(end == END_RESET && installed_is(pk[i].name), "%s installs (end %d)", pk[i].name, end);
        uint32_t total = B->flash_ops;
        CHECK(host_boot() == END_JUMP, "%s starts", pk[i].name);
        if (!i) {                            /* the first one again, half written: the bar over its picture */
            for (uint64_t at = (uint64_t)(READY + STEP * (uint32_t)(n - 1)) * 1000; at < 20000000; at += 5000) {
                host_init();
                card(img_fat32);
                keys(k, n);
                B->limit_us = at;
                if (host_boot() == END_HANG && B->flash_ops >= total / 2) break;
            }
            snap("real_installing");
        }
    }
}

int main(int argc, char **argv)
{
    char line[1024];
    FILE *f = fopen(argv[1], "r");
    frames = argv[2];
    if (!f) { perror(argv[1]); return 2; }
    while (fgets(line, sizeof line, f)) {
        char a[32], b[512], c[512];
        if (sscanf(line, "%31s", a) != 1) continue;
        if (!strcmp(a, "img")) {
            sscanf(line, "%*s %511s %511s", b, c);
            if (!strcmp(b, "fat32")) snprintf(img_fat32, sizeof img_fat32, "%s", c);
            if (!strcmp(b, "fat32sys")) snprintf(img_fat32sys, sizeof img_fat32sys, "%s", c);
            if (!strcmp(b, "vcart")) snprintf(img_vcart, sizeof img_vcart, "%s", c);
            if (!strcmp(b, "vcartlaunch")) snprintf(img_vcartlaunch, sizeof img_vcartlaunch, "%s", c);
            if (!strcmp(b, "vcartbad")) snprintf(img_vcartbad, sizeof img_vcartbad, "%s", c);
            if (!strcmp(b, "cartbig")) snprintf(img_cartbig, sizeof img_cartbig, "%s", c);
        } else if (!strcmp(a, "pkg") && npk < MAXP) {
            sscanf(line, "%*s %15s %d %u %x %511s", pk[npk].name, &pk[npk].code, &pk[npk].len, &pk[npk].crc, pk[npk].path);
            npk++;
        }
    }
    fclose(f);
    if (argc > 3 && !strcmp(argv[3], "real")) {
        TEST(t_real_card);
        return test_summary();
    }
    if (argc > 4 && !strcmp(argv[3], "style")) {    /* the static style: the same menu, its screens */
        frame_prefix = argv[4];
        TEST(t_no_card_no_app);
        TEST(t_splash);
        TEST(t_found);
        TEST(t_install);
        TEST(t_errors);
        TEST(t_usb_notice);
        TEST(t_flip);
        TEST(t_bad_pictures);
        return test_summary();
    }
    TEST(t_no_card_runs_app);
    TEST(t_no_card_no_app);
    TEST(t_splash);
    TEST(t_found);
    TEST(t_found_first_copy);
    TEST(t_stray);
    TEST(t_rows);
    TEST(t_flip);
    TEST(t_flip_no_folders);
    TEST(t_folders);
    TEST(t_install);
    TEST(t_errors);
    TEST(t_card_dies_mid_install);
    TEST(t_powercut_sweep);
    TEST(t_launch);
    TEST(t_launch_installed);
    TEST(t_launch_start_held);
    TEST(t_usb_notice);
    TEST(t_upload_at_menu);
    TEST(t_bad_pictures);
    TEST(t_full_folder);
    return test_summary();
}
