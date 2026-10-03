#ifndef CHBOOT_CHG_H
#define CHBOOT_CHG_H
#include <stdint.h>
#include "chg_format.h"

/* The result of checking a CHG file's header (spec/chg.md): magic, header
 * CRC, format version and header size, target and layout, payload size
 * against the file. One code for every failure: the menu shows only that
 * the file is not one it can install. */
#define CHG_OK          0
#define CHG_E_BAD       1

/* h: the first 512 bytes of the file (4-byte aligned). On CHG_OK, *payload
 * and *crc are the payload length and CRC. */
int chg_check(const uint8_t *h, uint32_t file_size, uint32_t *payload, uint32_t *crc);

#endif
