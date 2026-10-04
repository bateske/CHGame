#ifndef CHBOOT_SD_H
#define CHBOOT_SD_H
#include <stdint.h>

/* SPI-mode SD card, polled single-block reads (CMD17). The card shares SPI1
 * with the panel; every call selects the card itself and leaves it
 * deselected, with the panel's chip select untouched (high). */

int sd_init(void);                          /* 0 = card ready, then SPI at the run clock */
int sd_read(uint32_t lba, uint8_t *dst);    /* 0 = 512 bytes read */
#if MENU_UI == MENU_UI_VISUAL
/* SPI1's frames and clock (hal_spi_frames), out of line: the panel's
   pixels and the card's data go as 16-bit frames at 24 MHz. */
void sd_frames(uint32_t ctl);
#define sd_speed(br) sd_frames((br) << 3)   /* (hal_spi_speed's work, and more, out of line) */
uint8_t sd_x(uint8_t b);                    /* a byte out, its echo back: the panel's too */
#else
#define sd_speed(br) hal_spi_speed(br)
#endif

#ifndef SD_SPI_BR
#define SD_SPI_BR SPI_BR_12M                /* data clock; HW1 confirms the choice */
#endif

#endif
