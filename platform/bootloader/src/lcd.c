/* ST7735S panel driver and framebuffer for the menu. The configuration bytes
 * are CHGfx 1.3.0's panel set-up (frame rate, power, gamma), in a table. */
#include "lcd.h"
#include "font5x7.h"
#include "hal.h"
#include "sys.h"

static uint32_t t_wait;          /* tick stamp the next 120 ms wait runs from */

static void wait120(void)
{
    while (sys_ticks() - t_wait < 120u * SYS_TICKS_PER_MS) { }
}

/* One out-of-line copy of the SPI byte: inlined, every call site is a loop. */
static __attribute__((noinline)) void out(uint32_t b)
{
    hal_spi_xfer((uint8_t)b);
}

static void cmd(uint8_t c)
{
    hal_lcd_dc(0);
    out(c);
    hal_lcd_dc(1);
}

void lcd_reset(void)
{
    /* SPI1 may not be running yet (the USB-notice path never reads the card),
       and a transfer on a disabled SPI would wait forever. */
    hal_spi_speed(SPI_BR_12M);
    hal_lcd_select(0);
    hal_lcd_rst(0);
    sys_delay_ms(1);                 /* >= 10 us low */
    hal_lcd_rst(1);
    t_wait = sys_ticks();
}

void lcd_wake(void)
{
    wait120();
    hal_lcd_select(1);
    cmd(0x11);                       /* SLPOUT */
    hal_lcd_select(0);
    t_wait = sys_ticks();
}

/* {command, number of data bytes, data...}, ended by a 0 command. */
static const uint8_t init_seq[] = {
    0xB1, 3, 0x05, 0x3A, 0x3A,                       /* FRMCTR1: CHGfx's faster frame rate */
    0xB2, 3, 0x05, 0x3A, 0x3A,                       /* FRMCTR2 */
    0xB3, 6, 0x05, 0x3A, 0x3A, 0x05, 0x3A, 0x3A,     /* FRMCTR3 */
    0xB4, 1, 0x07,                                   /* INVCTR */
    0xC0, 3, 0xA2, 0x02, 0x84,                       /* PWCTR1..5, VMCTR1 */
    0xC1, 1, 0xC5,
    0xC2, 2, 0x0A, 0x00,
    0xC3, 2, 0x8A, 0x2A,
    0xC4, 2, 0x8A, 0xEE,
    0xC5, 1, 0x0E,
    0x20, 0,                                         /* INVOFF */
    0x36, 1, 0xC8,                                   /* MADCTL: the 1.44" green-tab orientation */
    0x2A, 4, 0, 2, 0, LCD_W + 1,                     /* CASET: always the whole width, from column 2 */
    0x3A, 1, 0x05,                                   /* COLMOD: RGB565 */
    0xE0, 16, 0x02, 0x1c, 0x07, 0x12, 0x37, 0x32, 0x29, 0x2d,   /* gamma + */
              0x29, 0x25, 0x2B, 0x39, 0x00, 0x01, 0x03, 0x10,
    0xE1, 16, 0x03, 0x1d, 0x07, 0x06, 0x2E, 0x2C, 0x29, 0x2D,   /* gamma - */
              0x2E, 0x2E, 0x37, 0x3F, 0x00, 0x00, 0x02, 0x10,
    0x13, 0,                                         /* NORON */
    0
};

uint8_t  lcd_fb[LCD_W * LCD_H / 2] __attribute__((aligned(4)));
uint16_t lcd_pal[16];

#if LCD_TURNS
static uint8_t  shows[LCD_H];               /* 1: the row holds colour 15 */
static uint32_t phase, now15;               /* colour 15 at the moment */

/* The colour wheel, 192 steps: each channel ramps up, stays full, ramps down
   and stays off, a third of a turn apart, lifted onto a floor (10 of 31) so
   the darkest hue is still light enough for black text. Five bits per
   channel, green's sixth bit left at 0. */
static uint32_t hue(uint32_t p)
{
    uint32_t c = 0;
    p += 64;                                /* red, then green, then blue */
    for (uint32_t k = 0; k < 3; k++, p += 128) {
        uint32_t q = p % 192, v = q < 32 ? q : q < 96 ? 31 : q < 128 ? 127 - q : 0;
        c = c << 5 | (10 + ((v * 11) >> 4));
    }
    return (c & 0x7FE0) << 1 | (c & 0x1F);
}

void lcd_step(void)
{
    now15 = hue(phase += 2);         /* (hue() takes it modulo a turn) */
    for (uint32_t y = 0; y < LCD_H; y++)
        if (shows[y]) lcd_flush(y, y + 1);
}
#endif

void lcd_on(void)
{
    const uint8_t *p = init_seq;
    wait120();
    hal_lcd_select(1);
    while (*p) {
        uint32_t n = p[1];
        cmd(p[0]);
        p += 2;
        while (n--) out(*p++);
    }
    hal_lcd_select(0);
#if LCD_TURNS
    now15 = hue(phase);
#endif
    lcd_flush(0, LCD_H);             /* never show the RAM's power-up noise */
    hal_lcd_select(1);
    cmd(0x29);                       /* DISPON */
    hal_lcd_select(0);
}

static __attribute__((noinline)) void px(uint32_t c)
{
    out(c >> 8);
    out(c);
}

void lcd_flush(uint32_t y0, uint32_t y1)
{
    const uint8_t *p = lcd_fb + y0 * (LCD_W / 2);
    hal_lcd_select(1);
    cmd(0x2B);                       /* RASET (rows start at the panel's row 3; CASET is set once) */
    px(y0 + 3);
    px(y1 + 2);
    cmd(0x2C);                       /* RAMWR */
    for (uint32_t y = y0; y < y1; y++) {
#if LCD_TURNS
        uint32_t f = 0;
        for (uint32_t x = 0; x < LCD_W; x++) {
            uint32_t i = x & 1 ? *p++ & 15 : *p >> 4;
            if (i == LCD_RAINBOW) { f = 1; px(now15); }
            else px(lcd_pal[i]);
        }
        shows[y] = (uint8_t)f;
#else
        for (uint32_t x = 0; x < LCD_W; x++)
            px(lcd_pal[x & 1 ? *p++ & 15 : *p >> 4]);
#endif
    }
    hal_lcd_select(0);
}

void lcd_fill(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t c)
{
    for (uint32_t j = y; j < y + h; j++)
        for (uint32_t i = x; i < x + w; i++) {
            uint8_t *p = lcd_fb + j * (LCD_W / 2) + (i >> 1);
            *p = (uint8_t)(i & 1 ? (*p & 0xF0) | c : (*p & 0x0F) | c << 4);
        }
}

void lcd_text(uint32_t x, uint32_t y, const char *s, uint32_t n, uint32_t c)
{
    for (; n && *s; n--, s++, x += 6) {
        uint32_t ch = (uint8_t)*s;          /* ('~' and the like: a folder's 8.3 name, CARDGA~1;
                                               8.3 names have no control characters) */
        const uint8_t *g = font5x7 + ((ch > FONT5X7_LAST ? '?' : ch) - 32) * 5;
        for (uint32_t gc = 0; gc < 5; gc++)
            for (uint32_t gr = 0; gr < 7; gr++)
                if (g[gc] >> gr & 1) lcd_fill(x + gc, y + gr, 1, 1, c);
    }
}
