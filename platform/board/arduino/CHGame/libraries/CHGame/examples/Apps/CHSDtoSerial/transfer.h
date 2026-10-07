/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
uint8_t transfer_init(void);
uint8_t transfer_command(uint8_t cmd,const uint8_t *data,uint16_t length,uint8_t *out,uint16_t *size);
uint32_t transfer_crc(uint32_t crc,const uint8_t *data,size_t length);
#ifdef __cplusplus
}
#endif
