/* Update path, USB protocol, boot decision and power cuts during USB uploads.
 * Built twice: with the SD menu (CHBOOT_MENU=1) and without (0). */
#include "testlib.h"
#include "update.h"
#include "proto.h"
#include "appmeta.h"
#include "boot.h"
#include "bootreq.h"
#include "chgame_bootreq.h"
#include "chg_format.h"
#include "hal.h"
#if CHBOOT_MENU
#include "chg.h"
#endif
#include <setjmp.h>

extern jmp_buf host_jmp;
extern int host_jmp_armed;

static uint8_t img[CHGAME_APP_MAX_SIZE], img2[CHGAME_APP_MAX_SIZE];

static void t_update_basic(void)
{
    uint32_t len = 3000, pages = (len + 255) / 256;
    uint8_t page[256];
    make_image(img, len, 1);
    CHECK(upd_begin() == ST_OK, "begin");
    for (uint32_t p = 0; p < pages; p++) {
        memset(page, 0xFF, sizeof page);
        memcpy(page, img + p * 256, len - p * 256 < 256 ? len - p * 256 : 256);
        CHECK(upd_page(CHGAME_APP_START + p * 256, page) == ST_OK, "page %u", p);
    }
    CHECK(upd_end(len, host_crc32(img, len)) == ST_OK, "end");
    CHECK(app_valid_now(), "app valid after update");
    CHECK(appmeta_check() == APP_VALID, "appmeta agrees");
    CHECK(B->erase_count[CHGAME_META_ADDR / 256] == 1, "metadata erased once, then programmed (got %u)", B->erase_count[CHGAME_META_ADDR / 256]);
    CHECK(B->erase_count[CHGAME_APP_START / 256] == 1, "first page erased once");
    /* the same image again: only the metadata page is erased */
    uint32_t ops = B->flash_ops;
    CHECK(upd_begin() == ST_OK, "begin 2");
    for (uint32_t p = 0; p < pages; p++) {
        memset(page, 0xFF, sizeof page);
        memcpy(page, img + p * 256, len - p * 256 < 256 ? len - p * 256 : 256);
        upd_page(CHGAME_APP_START + p * 256, page);
    }
    CHECK(upd_end(len, host_crc32(img, len)) == ST_OK, "end 2");
    CHECK(B->flash_ops - ops == 2, "reinstall costs one erase + one program (got %u ops)", B->flash_ops - ops);
    CHECK(B->erase_count[CHGAME_APP_START / 256] == 1, "identical page not erased again");
    CHECK(B->boot_region_writes == 0, "boot region untouched");
}

/* The system settings block (the metadata page's last bytes, chgame_map.h)
   comes through an update as it was. A blank one costs nothing (the counts in
   t_update_basic); a written one costs the metadata page a second erase. */
static void t_sys_update(void)
{
    uint32_t len = 3000, pages = (len + 255) / 256, i;
    uint8_t page[256];
    make_image(img, len, 9);
    for (uint32_t s = 1; s <= 2; s++) {
        host_init();
        host_install_app(img, len);
        sys_seed(s);
        CHECK(upd_begin() == ST_OK && !app_valid_now() && sys_is(s), "begin: no program, the block kept (pattern %u)", s);
        for (i = CHGAME_META_ADDR; i < CHGAME_SYS_ADDR && B->flash[i] == 0xFF; i++) { }
        CHECK(i == CHGAME_SYS_ADDR, "begin: the header erased (0x%04x)", i);
        for (uint32_t p = 0; p < pages; p++) {
            memset(page, 0xFF, sizeof page);
            memcpy(page, img + p * 256, len - p * 256 < 256 ? len - p * 256 : 256);
            upd_page(CHGAME_APP_START + p * 256, page);
        }
        CHECK(upd_end(len, host_crc32(img, len)) == ST_OK && app_valid_now() && sys_is(s), "end: valid, the block kept (pattern %u)", s);
        CHECK(B->erase_count[CHGAME_META_ADDR / 256] == 2, "metadata page erased twice (got %u)", B->erase_count[CHGAME_META_ADDR / 256]);
    }
}

/* ABORT, then an upload over USB: the block kept through both. */
static void t_sys_usb(void)
{
    uint8_t cmd, pl[64]; uint16_t n;
    make_image(img2, 6000, 6);
    make_image(img, 20000, 4);
    host_install_app(img2, 6000);
    sys_seed(1);
    bootreq_set(CHGAME_BOOTREQ_USB);
    frame_push(CMD_ABORT, NULL, 0);
    B->limit_us = 500000;
    host_boot();
    CHECK(frame_pop(&cmd, pl, &n) && cmd == (CMD_ABORT | 0x80) && pl[0] == ST_OK, "ABORT answered");
    CHECK(!app_valid_now() && sys_is(1), "ABORT: no program, the block kept");
    bootreq_set(CHGAME_BOOTREQ_USB);
    push_upload(img, 20000, 1);
    B->limit_us = 20000000;
    int end = host_boot();
    int ok = 1;
    while (frame_pop(&cmd, pl, &n)) if (pl[0] != ST_OK) { ok = 0; fprintf(stderr, "cmd %02x st %u\n", cmd, pl[0]); }
    CHECK(end == END_RESET && ok && app_valid_now() && sys_is(1), "upload + RUN: valid, the block kept (end %d)", end);
}

static void t_update_errors(void)
{
    uint8_t page[256];
    memset(page, 0x55, sizeof page);
    CHECK(upd_page(CHGAME_APP_START - 256, page) == ST_ERR_RANGE, "page below app region refused");
    CHECK(upd_page(CHGAME_META_ADDR, page) == ST_ERR_RANGE, "metadata page refused as image page");
    CHECK(upd_page(0, page) == ST_ERR_RANGE, "page 0 refused");
    CHECK(B->boot_region_writes == 0, "boot region untouched");
    make_image(img, 1024, 2);
    host_install_app(img, 1024);
    CHECK(app_valid_now(), "installed");
    upd_begin();
    CHECK(!app_valid_now(), "begin invalidates");
    CHECK(upd_end(1024, 0x12345678u) == ST_ERR_CRC, "wrong CRC refused");
    CHECK(!app_valid_now(), "still invalid after a failed end");
}

static void t_signature(void)
{
    make_image(img, 2048, 3);
    put32(img + CHGAME_BOOT_SIG_OFFSET, CHGAME_BOOT_SIG);
    host_install_app(img, 2048);
    CHECK(appmeta_check() == APP_INVALID_BOOTIMAGE, "a staged bootloader image is never an app");
}

static void t_proto_claim(void)
{
    uint8_t cmd, pl[64]; uint16_t n;
    proto_init();
    frame_push(CMD_HELLO, NULL, 0);
    frame_push(CMD_STATUS, NULL, 0);
    uint8_t rd[6] = {0, 0x30, 0, 0, 16, 0};
    frame_push(CMD_READ, rd, 6);
    for (int i = 0; i < 20; i++) proto_task();
    CHECK(!proto_claimed, "HELLO/STATUS/READ do not claim the bootloader");
    CHECK(frame_pop(&cmd, pl, &n) && cmd == (CMD_HELLO | 0x80) && pl[0] == ST_OK, "HELLO answered");
    CHECK(pl[2] == MODE_BOOTLOADER, "mode bootloader");
    CHECK((pl[4] | pl[5] << 8) == BOOT_VERSION, "boot version");
    CHECK(le32(pl + 18) == hal_uid(0) && le32(pl + 22) == hal_uid(1) && le32(pl + 26) == hal_uid(2),
          "HELLO: the chip's UID at offset 18");
#ifdef CHGAME_BOARD_TARGET
    CHECK(n == 34 && (pl[30] | pl[31] << 8 | pl[32] << 16 | (uint32_t)pl[33] << 24) == CHGAME_BOARD_TARGET,
          "a later board's HELLO ends with its board id (its image's word at 0x14)");
#else
    CHECK(n == 30, "a rev0 HELLO is the 30 bytes it always was: no board field");
#endif
    /* bootloader v2 (BOOT_VERSION 3) dropped the two bench diagnostics */
    CHECK(frame_pop(&cmd, pl, &n) && cmd == (CMD_STATUS | 0x80) && pl[0] == ST_ERR_BADCMD, "STATUS: unknown command");
    CHECK(frame_pop(&cmd, pl, &n) && cmd == (CMD_READ | 0x80) && pl[0] == ST_ERR_BADCMD, "READ: unknown command");
    /* garbage, then a valid frame: resynchronises */
    const char junk[] = "AT+GMM\r\nCGx\x01";
    memcpy(B->rx + B->rx_len, junk, sizeof junk - 1); B->rx_len += sizeof junk - 1;
    frame_push(CMD_ABORT, NULL, 0);
    for (int i = 0; i < 40; i++) proto_task();
    CHECK(proto_claimed, "ABORT claims");
}

/* The keys from the two ports' input words (hal.h HAL_KEYS, which the board's
   hal_buttons() applies to GPIOB/GPIOC INDR; pressed reads low): each key's
   pin low alone gives its bit and only that, every other pin gives nothing,
   and the eight bits are BTN_ALL. */
static void t_keys(void)
{
    static const struct { const char *name; uint8_t port, pin; uint32_t bit; } key[8] = {
#ifdef CHGAME_BOARD_TARGET                   /* rev1 */
        { "UP", 'B', 0, BTN_UP }, { "DOWN", 'B', 1, BTN_DOWN }, { "LEFT", 'C', 3, BTN_LEFT },
        { "RIGHT", 'C', 0, BTN_RIGHT }, { "A", 'B', 11, BTN_A }, { "B", 'B', 6, BTN_B },
        { "SELECT", 'B', 7, BTN_SELECT }, { "START", 'B', 8, BTN_START },
    };
    /* PB5 is PB1's pad on the package: only ever read together with DOWN */
    static const struct { uint8_t port, pin; } other[] = {
        { 'B', 2 }, { 'B', 3 }, { 'B', 4 }, { 'B', 5 }, { 'B', 9 }, { 'B', 10 }, { 'B', 12 },
        { 'C', 1 }, { 'C', 2 }, { 'C', 14 }, { 'C', 15 },
#else                                        /* rev0 */
        { "UP", 'B', 4, BTN_UP }, { "DOWN", 'C', 14, BTN_DOWN }, { "LEFT", 'B', 3, BTN_LEFT },
        { "RIGHT", 'C', 15, BTN_RIGHT }, { "A", 'B', 1, BTN_A }, { "B", 'B', 6, BTN_B },
        { "SELECT", 'B', 7, BTN_SELECT }, { "START", 'B', 8, BTN_START },
    };
    static const struct { uint8_t port, pin; } other[] = {
        { 'B', 0 }, { 'B', 2 }, { 'B', 5 }, { 'B', 9 }, { 'B', 10 }, { 'B', 11 }, { 'B', 12 },
        { 'C', 0 }, { 'C', 3 }, { 'C', 13 },
#endif
    };
    /* INDR as read: every implemented pin high (24 bits), or every bit */
    static const uint32_t high[2] = { 0x00FFFFFFu, 0xFFFFFFFFu };
    for (int h = 0; h < 2; h++) {
        uint32_t all = 0, b_all = high[h], c_all = high[h];
        CHECK(HAL_KEYS(high[h], high[h]) == 0, "every pin high (%08X): no key", high[h]);
        for (int i = 0; i < 8; i++) {
            uint32_t b = high[h], c = high[h], k;
            if (key[i].port == 'B') b &= ~(1u << key[i].pin), b_all &= ~(1u << key[i].pin);
            else c &= ~(1u << key[i].pin), c_all &= ~(1u << key[i].pin);
            k = HAL_KEYS(b, c);
            CHECK(k == key[i].bit, "%s (P%c%u low): %03X, not BTN_%s %03X", key[i].name, key[i].port, key[i].pin,
                  k, key[i].name, key[i].bit);
            CHECK(!(all & key[i].bit), "BTN_%s shares a bit", key[i].name);
            all |= key[i].bit;
        }
        CHECK(all == BTN_ALL, "BTN_ALL %X is the eight keys' bits %X", BTN_ALL, all);
        CHECK(HAL_KEYS(b_all, c_all) == BTN_ALL, "all eight pressed: BTN_ALL (%X)", HAL_KEYS(b_all, c_all));
        for (unsigned i = 0; i < sizeof other / sizeof other[0]; i++) {
            uint32_t b = high[h], c = high[h];
            if (other[i].port == 'B') b &= ~(1u << other[i].pin);
            else c &= ~(1u << other[i].pin);
            CHECK(HAL_KEYS(b, c) == 0, "P%c%u low: no key (%X)", other[i].port, other[i].pin, HAL_KEYS(b, c));
        }
    }
#ifdef CHGAME_BOARD_TARGET
    CHECK(BTN_ALL <= 0x1FFu, "rev1: every key mask fits an immediate (BTN_ALL %X)", BTN_ALL);
#endif
}

#if CHBOOT_MENU
static void t_chg_board(void)
{
    /* A package installs only on the board it was built for: this build's
       target id (rev0's, CX35, when the build names none), never another's. */
    static uint32_t h32[CHG_HEADER_BYTES / 4];
    uint8_t *h = (uint8_t *)h32;
    uint32_t n = 0, crc;
    const uint32_t other = CHG_TARGET_ID == CHG_TARGET_REV0 ? CHG_TARGET_REV1 : CHG_TARGET_REV0;
    for (int k = 0; k < 2; k++) {
        memset(h, 0, CHG_HEADER_BYTES);
        put32(h + CHG_OFF_MAGIC, CHG_MAGIC);
        put32(h + CHG_OFF_VERSION, CHG_FORMAT_VERSION | CHG_HEADER_BYTES << 16);
        put32(h + CHG_OFF_TARGET, k ? other : CHG_TARGET_ID);
        put32(h + CHG_OFF_LAYOUT, CHG_LAYOUT_ID);
        put32(h + CHG_OFF_PAYLOAD, 1024);
        put32(h + CHG_OFF_HCRC, host_crc32(h, CHG_OFF_HCRC));
        int r = chg_check(h, CHG_HEADER_BYTES + 1024, &n, &crc);
        if (k)
            CHECK(r == CHG_E_BAD, "another board's package is refused");
        else
            CHECK(r == CHG_OK && n == 1024, "this board's package is accepted");
    }
}
#endif

static void t_usb_upload_run(void)
{
    uint8_t cmd, pl[64]; uint16_t n;
    uint32_t len = 20000;
    make_image(img, len, 4);
    bootreq_set(CHGAME_BOOTREQ_USB);
    push_upload(img, len, 1);
    int end = host_boot();
    CHECK(end == END_RESET, "upload + RUN ends in a reset (got %d)", end);
    CHECK(B->retained[0] == CHGAME_BOOTREQ_RUN && B->retained[1] == ~CHGAME_BOOTREQ_RUN, "RUN request left for the next boot");
    int all_ok = 1, count = 0;
    while (frame_pop(&cmd, pl, &n)) { count++; if (pl[0] != ST_OK) { all_ok = 0; fprintf(stderr, "cmd %02x st %u\n", cmd, pl[0]); } }
    CHECK(all_ok && count == 2 + (int)((len + 255) / 256) + 1, "every response OK (%d responses)", count);
    CHECK(app_valid_now(), "uploaded app valid");
    for (uint32_t p = CHGAME_APP_START / 256; p < (CHGAME_APP_START + len + 255) / 256; p++)
        if (B->erase_count[p] != 1) { CHECK(0, "page %u erased %u times", p, B->erase_count[p]); break; }
    end = host_boot();
    CHECK(end == END_JUMP, "RUN request starts the app (got %d)", end);
    CHECK(B->retained[0] == 0 && B->retained[1] == 0, "request consumed");
    CHECK(B->boot_region_writes == 0, "boot region untouched");
}

/* sys: the system settings block's pattern (sys_seed), 0 for a blank one. */
static void powercut_sweep(uint32_t sys)
{
    uint32_t len = 3000;          /* 12 pages: a complete sweep stays quick */
    make_image(img, len, 5);
    make_image(img2, 6000, 6);
    /* reference run: how many flash operations does the upload take? */
    host_install_app(img2, 6000);
    sys_seed(sys);
    bootreq_set(CHGAME_BOOTREQ_USB);
    push_upload(img, len, 0);
    B->limit_us = 3000000;
    host_boot();
    uint32_t total = B->flash_ops;
    CHECK(app_valid_now(), "reference upload valid");
    int bad = 0;
    for (uint32_t k = 1; k <= total; k++) {
        host_init();
        B->limit_us = 3000000;
        host_install_app(img2, 6000);
        sys_seed(sys);
        bootreq_set(CHGAME_BOOTREQ_USB);
        push_upload(img, len, 0);
        B->cut_at_op = k;
        int end = host_boot();
        if (end != END_POWERCUT) { bad++; fprintf(stderr, "cut %u: no cut (%d)\n", k, end); continue; }
        B->cut_at_op = 0;
        B->rx_len = B->rx_pos = 0;
        int valid = app_valid_now();
        /* Nothing partial may ever be launchable. The metadata is written
           last, so the only launchable state after a cut is the complete new
           image (a cut during the metadata program itself can leave the whole
           record written). The old app can never come back: BEGIN erases its
           metadata first. */
        int complete = le32(B->flash + CHGAME_META_ADDR + 8) == len && !memcmp(B->flash + CHGAME_APP_START, img, len);
        if (valid && !complete) { bad++; fprintf(stderr, "cut at op %u/%u left a launchable partial image\n", k, total); }
        if (!valid && k == total - 1) { /* fine either way */ }
        end = host_run(3);
        if (end == END_JUMP && !complete) { bad++; fprintf(stderr, "cut %u: jumped into a partial image\n", k); }
        if (B->boot_region_writes) { bad++; fprintf(stderr, "cut %u: boot region written\n", k); }
        /* The block can only be lost by a cut while the metadata page itself
           is rewritten, and a blank one by none. */
        if (!sys_is(sys) && (!sys || B->cut_addr != CHGAME_META_ADDR)) {
            bad++; fprintf(stderr, "cut %u (page 0x%04x): the system settings block changed\n", k, B->cut_addr);
        }
    }
    CHECK(bad == 0, "power cut at each of %u flash operations of an upload (block pattern %u)", total, sys);
}

static void t_usb_powercut_sweep(void) { powercut_sweep(0); }
static void t_sys_powercut_sweep(void) { powercut_sweep(1); }

#if CHGAME_ALLOW_SELFUPDATE
/* sys: the system settings block's pattern (sys_seed), 0 for a blank one. */
static void selfupdate(uint32_t sys)
{
    uint8_t cmd, pl[64], key[4], wb[8]; uint16_t n;
    uint32_t len = 9000;
    make_image(img, len, 8);
    put32(img + CHGAME_BOOT_SIG_OFFSET, CHGAME_BOOT_SIG);     /* a bootloader image */
    sys_seed(sys);
    bootreq_set(CHGAME_BOOTREQ_USB);
    put32(key, CHGAME_DEV_KEY);
    frame_push(CMD_DEV_UNLOCK, key, 4);                       /* unlock first (host fix) */
    push_upload(img, len, 0);
    put32(wb, len); put32(wb + 4, host_crc32(img, len));
    frame_push(CMD_DEV_WRITE_BOOT, wb, 8);
    int end = host_boot();
    CHECK(end == END_RESET && B->selfupdate_calls == 1, "self-update ran (end %d)", end);
    int ok = 1;
    while (frame_pop(&cmd, pl, &n)) if (pl[0] != ST_OK) { ok = 0; fprintf(stderr, "cmd %02x -> %u\n", cmd, pl[0]); }
    CHECK(ok, "staging a bootloader image is accepted (END ok), and so is DEV_WRITE_BOOT");
    CHECK(!memcmp(B->flash, img, len), "boot region holds the new image");
    CHECK(!app_valid_now(), "the staged copy is not an app (metadata erased, signature)");
    CHECK(sys_is(sys), "the system settings block kept through staging and DEV_WRITE_BOOT (pattern %u)", sys);
}

static void t_selfupdate(void) { selfupdate(0); }
static void t_sys_selfupdate(void) { selfupdate(1); }
#endif

#if !CHBOOT_MENU
static void t_boot_nomenu(void)
{
    make_image(img, 4096, 7);
    host_install_app(img, 4096);
    CHECK(host_boot() == END_JUMP, "valid app, no request: runs");
    bootreq_set(CHGAME_BOOTREQ_USB);
    B->limit_us = 500000;
    CHECK(host_boot() == END_HANG && B->usb_up, "USB request: USB mode");
    CHECK(host_boot() == END_JUMP, "request was consumed");
    upd_begin();
    CHECK(host_boot() == END_HANG && B->usb_up, "invalid app: USB mode");
}
#endif

int main(void)
{
    TEST(t_update_basic);
    TEST(t_sys_update);
    TEST(t_update_errors);
    TEST(t_signature);
    TEST(t_proto_claim);
    TEST(t_keys);
#if CHBOOT_MENU
    TEST(t_chg_board);
#endif
    TEST(t_usb_upload_run);
    TEST(t_usb_powercut_sweep);
    TEST(t_sys_usb);
    TEST(t_sys_powercut_sweep);
#if CHGAME_ALLOW_SELFUPDATE
    TEST(t_selfupdate);
    TEST(t_sys_selfupdate);
#endif
#if !CHBOOT_MENU
    TEST(t_boot_nomenu);
#endif
    return test_summary();
}
