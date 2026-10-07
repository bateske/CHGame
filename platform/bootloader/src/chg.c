#include "chg.h"
#include "crc32.h"
#include "chgame_map.h"

_Static_assert(CHG_LAYOUT_ID == (((CHGAME_APP_START >> 8) << 16) | (CHGAME_META_ADDR >> 8)),
               "CHG_LAYOUT_ID must describe chgame_map.h");
#ifdef CHGAME_BOARD_TARGET
_Static_assert(CHGAME_BOARD_TARGET != CHG_TARGET_REV0,
               "a rev0 build leaves CHGAME_BOARD_TARGET undefined (chg_format.h)");
#endif

static uint32_t w(const uint8_t *h, uint32_t off) { return *(const uint32_t *)(const void *)(h + off); }

int chg_check(const uint8_t *h, uint32_t file_size, uint32_t *payload, uint32_t *crc)
{
    uint32_t n = w(h, CHG_OFF_PAYLOAD);
    /* In the bootloader's order; n <= 50,944 once checked, so the sum cannot
       overflow. */
    if (w(h, CHG_OFF_MAGIC) != CHG_MAGIC || crc32_buf(h, CHG_OFF_HCRC) != w(h, CHG_OFF_HCRC) ||
        w(h, CHG_OFF_VERSION) != (CHG_FORMAT_VERSION | CHG_HEADER_BYTES << 16) ||
        w(h, CHG_OFF_TARGET) != CHG_TARGET_ID || w(h, CHG_OFF_LAYOUT) != CHG_LAYOUT_ID ||
        !n || n > CHGAME_APP_MAX_SIZE || (n & 3u) || file_size < CHG_HEADER_BYTES + n)
        return CHG_E_BAD;
    *payload = n;
    *crc = w(h, CHG_OFF_PCRC);
    return CHG_OK;
}
