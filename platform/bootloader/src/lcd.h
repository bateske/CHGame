#ifndef CHBOOT_LCD_H
#define CHBOOT_LCD_H
#include <stdint.h>

/* The ST7735S panel and the menu's framebuffer: 128x128 pixels of 4 bits,
 * two to a byte (the left one in the high nibble), turned into RGB565 through
 * lcd_pal as they are sent. Colour 15 is not in the palette: it is the colour
 * wheel, its hue moving with x + y and with time (lcd_step), so whatever is
 * drawn in it is a moving rainbow. Bring-up is split so the card can be read
 * during the panel's two 120 ms waits:
 *
 *   lcd_reset()   reset pulse; starts the 120 ms reset wait
 *   ...           (read the card, draw the first picture)
 *   lcd_wake()    finish the wait, Sleep Out; starts the next 120 ms
 *   ...
 *   lcd_on()      finish the wait, configure, send the picture, display on
 *
 * 128x128 visible; MADCTL 0xC8 and the 1.44" panel's column/row offsets
 * (2, 3), as CHGfx uses. */

#define LCD_W 128
#define LCD_H 128
#define LCD_RAINBOW 15u

/* RGB565 */
#define RGB565(r, g, b) ((uint16_t)((((r) & 0xF8) << 8) | (((g) & 0xFC) << 3) | ((b) >> 3)))

extern uint8_t  lcd_fb[LCD_W * LCD_H / 2];
extern uint16_t lcd_pal[16];

void lcd_reset(void);
void lcd_wake(void);
void lcd_on(void);
/* Sends rows y0..y1-1 to the panel. */
void lcd_flush(uint32_t y0, uint32_t y1);
/* Turns the colour wheel a step and sends the rows that show it. */
void lcd_step(void);
/* Drawing into the framebuffer (nothing is sent). Text is the 5x7 font in
   6-pixel cells, scale 1 or 2, glyph pixels only. */
void lcd_fill(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t c);
void lcd_text(uint32_t x, uint32_t y, const char *s, uint32_t n, uint32_t c, uint32_t scale);

#endif
