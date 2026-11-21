#include "update.h"
#include "proto.h"
#include "flash.h"
#include "appmeta.h"
#include "crc32.h"
#include "hal.h"
#include "chgame_map.h"

/* Rewrites the metadata page: the header for an image of len bytes (len 0:
   none, so the installed program is invalid), 0xFF after it, and the system
   settings block (its last CHGAME_SYS_SIZE bytes, chgame_map.h) kept as it
   is. An erased page is not erased again before it is programmed, and one
   with nothing to write is only erased: while the block is blank, an update
   costs this page one erase and one program, as it did before the block. */
static uint8_t meta_put(uint32_t len, uint32_t crc)
{
    uint32_t page[CHGAME_PAGE_SIZE / 4u];
    chgame_meta_t *m = (chgame_meta_t *)page;
    uint32_t i, w, used = 0, put = len;   /* any word programmed / anything to write */

    for (i = 0; i < CHGAME_PAGE_SIZE / 4u; i++) {
        w = FLASH_W(CHGAME_META_ADDR + i * 4u);
        used |= ~w;
        if (i < (CHGAME_SYS_ADDR - CHGAME_META_ADDR) / 4u)
            w = 0xFFFFFFFFu;
        put |= ~w;
        page[i] = w;
    }
    if (len) {
        m->magic        = CHGAME_META_MAGIC;
        m->meta_version = CHGAME_META_VERSION;
        m->length       = len;
        m->crc32        = crc;
        m->app_version  = 0u;
    }

    return (put ? flash_write_page(CHGAME_META_ADDR, (const uint8_t *)page, FLASH_REGION_APP, used)
                : flash_erase_page(CHGAME_META_ADDR, FLASH_REGION_APP)) == FLASH_OK ? ST_OK : ST_ERR_FLASH;
}

uint8_t upd_begin(void)
{
    return meta_put(0u, 0u);
}

uint8_t upd_page(uint32_t addr, const uint8_t *buf)
{
    const uint8_t *f = FLASH_AT(addr);
    uint32_t i;
    int rc;

    if (addr < CHGAME_APP_START || addr >= CHGAME_META_ADDR)
        return ST_ERR_RANGE;
    for (i = 0; i < CHGAME_PAGE_SIZE && f[i] == buf[i]; i++) { }
    if (i == CHGAME_PAGE_SIZE)
        return ST_OK;
    rc = flash_write_page(addr, buf, FLASH_REGION_APP, 1);
    if (rc == FLASH_OK)        return ST_OK;
    if (rc == FLASH_ERR_RANGE) return ST_ERR_RANGE;
    return ST_ERR_FLASH;
}

uint8_t upd_end(uint32_t len, uint32_t crc)
{
    int rc;

    /* Verify from FLASH, not from anything buffered: the only claim worth
       making is about what is actually stored. */
    if (crc32_buf(FLASH_AT(CHGAME_APP_START), len) != crc)
        return ST_ERR_CRC;

    /* upd_begin() left this page erased, or holding the system settings
       block alone. Erased, it is only programmed: the metadata page is the
       one erased on every update, and that halves its wear. */
    if (meta_put(len, crc) != ST_OK)
        return ST_ERR_FLASH;

    /* Re-read through the same path the boot decision uses, so success means
       exactly "the next boot will launch this" - or, for a bootloader image
       staged for DEV_WRITE_BOOT, "stored intact" (it is never launched). */
    rc = appmeta_check();
    return rc == APP_VALID || rc == APP_INVALID_BOOTIMAGE ? ST_OK : ST_ERR_CRC;
}
