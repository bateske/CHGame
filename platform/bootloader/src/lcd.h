#ifndef CHBOOT_LCD_H
#define CHBOOT_LCD_H
#include <stdint.h>

/* The ST7735S panel and the menu's framebuffer: 128x128 pixels of 4 bits,
 * two to a byte (the left one in the high nibble), turned into RGB565 through
 * lcd_pal as they are sent. Colour 15 depends on the style the bootloader is
 * built in (build.sh --style=):
 *   rainbow (the default)  one colour turning through the colour wheel
 *                          (lcd_step), whatever the palette says
 *   static                 the palette's, like the others: the cards the
 *                          tools make give it the picture's #FF00FF
 * Bring-up is split so the card can be read during the panel's two 120 ms
 * waits:
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

#define MENU_STYLE_RAINBOW 0
#define MENU_STYLE_STATIC  1
#ifndef MENU_STYLE
#define MENU_STYLE MENU_STYLE_RAINBOW
#endif
#define LCD_TURNS (MENU_STYLE == MENU_STYLE_RAINBOW)

/* The menu's face (build.sh --ui=): the text list over MENU.BG (menu.c), or
   one picture at a time and no text at all (visual.c). */
#define MENU_UI_LIST   0
#define MENU_UI_VISUAL 1
#ifndef MENU_UI
#define MENU_UI MENU_UI_LIST
#endif

/* RGB565 */
#define RGB565(r, g, b) ((uint16_t)((((r) & 0xF8) << 8) | (((g) & 0xFC) << 3) | ((b) >> 3)))

extern uint8_t  lcd_fb[LCD_W * LCD_H / 2];
extern uint16_t lcd_pal[16];

void lcd_reset(void);
void lcd_wake(void);
void lcd_on(void);
/* Sends rows y0..y1-1 to the panel. */
void lcd_flush(uint32_t y0, uint32_t y1);
#if LCD_TURNS
/* Turns colour 15 a step round the wheel and sends the rows that show it
   (the visual menu: the whole picture, which its 16-bit send does in ~19 ms). */
void lcd_step(void);
#endif
/* Drawing into the framebuffer (nothing is sent). Text is the 5x7 font in
   6-pixel cells, glyph pixels only; the visual menu has none. */
void lcd_fill(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t c);
#if MENU_UI == MENU_UI_LIST
void lcd_text(uint32_t x, uint32_t y, const char *s, uint32_t n, uint32_t c);
#else
/* How dark the panel shows the framebuffer: every colour halved this many
   times (fades; LCD_DARK: black). */
#define LCD_DARK 6
extern uint32_t lcd_dark;
/* The framebuffer slides in over the panel's picture from one side, in
   eight steps. */
#define LCD_FROM_BOTTOM 0
#define LCD_FROM_TOP    1
#define LCD_FROM_RIGHT  2
#define LCD_FROM_LEFT   3
void lcd_slide(uint32_t d);
#endif

#endif
