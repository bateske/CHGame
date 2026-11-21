/*
 * The few hardware operations the portable parts of the bootloader need: the
 * pins, SPI1, the buttons and the LED. On the board these are static inline
 * register accesses, so the layer costs nothing; the host test harness
 * (test/native) provides the same names as functions over its models of the
 * card, the panel and the flash.
 *
 * Two boards, one source (docs/hardware-revisions.md): rev0 when the build
 * names no board (CHGAME_BOARD_TARGET undefined: the binaries rev0 has always
 * had), rev1 when it names rev1's id (build.sh --board=rev1). Rev 1.5 is a
 * rev1. Any other id stops the build: wrong pins short a pressed key.
 *
 * Rev0 pins (platform/board/docs/hardware-pinmap.md, variant_CHGame_Rev0.h):
 *   SPI1   SCK PA5, MISO PA6, MOSI PA7 - shared by the panel and the card
 *   panel  CS PA4, DC PB0, RST PB12
 *   card   CS PB11
 *   LED    PB9 (active high), buzzer PB10 (held low)
 *   keys   A PB1, LEFT PB3, UP PB4, B PB6, SELECT PB7, START PB8,
 *          DOWN PC14, RIGHT PC15 - all to GND, internal pull-ups
 *
 * Rev1 pins (variant_CHGame_Rev1.h):
 *   SPI1   SCK PA5, MISO PA6, MOSI PA7, as rev0
 *   panel  CS PA4, DC PB4, RST PB12; backlight PB9 (active high, pulled
 *          down on the board): dark until the panel shows a written frame
 *   card   CS PB3
 *   LED    PB10 (active high); the buzzer (PA1) is left floating, its
 *          MOSFET's gate pulled down
 *   keys   UP PB0, DOWN PB1, A PB11, B PB6, SELECT PB7, START PB8,
 *          LEFT PC3, RIGHT PC0 - all to GND, internal pull-ups. PB5 is
 *          bonded to PB1's pad: never an output
 *   never  PA0 (VBUS sense), PC14/PC15 (test pads; CC1/CC2 on Rev 1.5):
 *          floating inputs, as reset leaves them
 *
 * None of MISO, the two chip selects or LCD_RST has a pull-up on the board,
 * so hal_pins_init() drives every one of them before anything else runs.
 */
#ifndef CHBOOT_HAL_H
#define CHBOOT_HAL_H
#include <stdint.h>
/* The board ids first: every board test below compares CHGAME_BOARD_TARGET
 * with CHG_TARGET_REV1, and an undefined name in #if is 0. */
#include "chg_format.h"

#if defined(CHGAME_BOARD_TARGET) && CHGAME_BOARD_TARGET != CHG_TARGET_REV1
#error "no pins for this board: rev0 leaves CHGAME_BOARD_TARGET undefined, rev1 is CHG_TARGET_REV1 (chg_format.h)"
#endif

/* CHBOOT_APP 1: the dry-run build that runs as a program (build.sh app). */
#ifndef CHBOOT_APP
#define CHBOOT_APP 0
#endif

#if defined(CHGAME_BOARD_TARGET)            /* rev1 */
/* Logical key bits, all within bits 0-8, so every mask of them is an
 * immediate (andi): GPIOB's UP, DOWN, B, SELECT and START where they are
 * (PB0, PB1, PB6-8); A (PB11) shifted down by 7 into bit 4; RIGHT and LEFT
 * (PC0, PC3) shifted up by 2 together into bits 2 and 5. */
#define BTN_UP      (1u << 0)
#define BTN_DOWN    (1u << 1)
#define BTN_RIGHT   (1u << 2)
#define BTN_A       (1u << 4)
#define BTN_LEFT    (1u << 5)
#define BTN_B       (1u << 6)
#define BTN_SELECT  (1u << 7)
#define BTN_START   (1u << 8)
#define BTN_ALL     (BTN_UP | BTN_DOWN | BTN_RIGHT | BTN_A | BTN_LEFT | BTN_B | BTN_SELECT | BTN_START)
/* The keys' pins on each port (their pull-ups): PB0/1/6/7/8/11, PC0/3. */
#define BTN_PORTB   ((1u << 0) | (1u << 1) | (1u << 6) | (1u << 7) | (1u << 8) | (1u << 11))
#define BTN_PORTC   ((1u << 0) | (1u << 3))
/* The pressed keys from the two ports' input words (pressed reads low):
 * masked first, inverted once at the end. */
#define HAL_KEYS(b, c) ((((b) & (BTN_UP | BTN_DOWN | BTN_B | BTN_SELECT | BTN_START)) \
                         | ((b) >> 7 & BTN_A) | ((c) & (BTN_RIGHT | BTN_LEFT) >> 2) << 2) ^ BTN_ALL)
_Static_assert(HAL_KEYS(0xFFFFFFFFu, 0xFFFFFFFFu) == 0 && HAL_KEYS(~(1u << 11), 0xFFFFFFFFu) == BTN_A
               && HAL_KEYS(0xFFFFFFFFu, ~1u) == BTN_RIGHT && HAL_KEYS(0xFFFFFFFFu, ~(1u << 3)) == BTN_LEFT
               && BTN_ALL == 0x1F7u, "rev1 key bits (hal.h)");
#else                                       /* rev0 */
/* Button bits are the port bits themselves: GPIOB 1/3/4/6/7/8 and GPIOC 14/15
 * do not overlap, so one 16-bit mask holds them all. */
#define BTN_A       (1u << 1)
#define BTN_LEFT    (1u << 3)
#define BTN_UP      (1u << 4)
#define BTN_B       (1u << 6)
#define BTN_SELECT  (1u << 7)
#define BTN_START   (1u << 8)
#define BTN_DOWN    (1u << 14)
#define BTN_RIGHT   (1u << 15)
#define BTN_PORTB   (BTN_A | BTN_LEFT | BTN_UP | BTN_B | BTN_SELECT | BTN_START)
#define BTN_PORTC   (BTN_DOWN | BTN_RIGHT)
#define BTN_ALL     (BTN_PORTB | BTN_PORTC)
/* The pressed keys from the two ports' input words (pressed reads low), as
 * hal_buttons() reads them. */
#define HAL_KEYS(b, c) ((~(b) & BTN_PORTB) | (~(c) & BTN_PORTC))
#endif

/* SPI1 baud-rate field (CTLR1.BR): SCK = 48 MHz / 2^(BR+1). */
#define SPI_BR_187K5  7u
#define SPI_BR_6M     2u
#define SPI_BR_12M    1u
#define SPI_BR_24M    0u
#define HAL_SPI_16BIT (1u << 11)   /* CTLR1.DFF: 16-bit frames */

#ifdef CHBOOT_HOST

void     hal_pins_init(void);
void     hal_spi_speed(uint32_t br);
uint8_t  hal_spi_xfer(uint8_t b);
void     hal_spi_frames(uint32_t ctl);
void     hal_spi_put16(uint32_t v);
void     hal_sd_select(int on);
void     hal_lcd_select(int on);
void     hal_lcd_dc(int data);
void     hal_lcd_rst(int high);
uint32_t hal_buttons(void);
void     hal_led(int on);
void     hal_backlight_on(void);    /* (both boards: the model checks when it is called) */
uint32_t hal_uid(uint32_t word);
int      hal_soft_reset(void);
const uint8_t *hal_flash(uint32_t addr);
void     hal_reset(void) __attribute__((noreturn));
#define FLASH_AT(a)   hal_flash(a)

#else

#include "ch32x035.h"

/* Composed pin configuration, one nibble per pin (CNF:MODE).
 *   0x3 push-pull output, 0xB alternate-function push-pull,
 *   0x8 input with pull-up/down (OUTDR selects up), 0x4 floating input.
 * GPIOB/GPIOC CFGHR are WRITE-ONLY on this part (reading returns garbage), so
 * they are only ever written whole, from these constants.
 * PB5 shares pin 16 with rev0's BTN_A (rev1's DOWN): it stays a floating
 * input, never an output.
 *
 * Every pin the bootloader does not use is left as reset leaves it, a
 * floating input (high-Z). Rev0: the buzzer (PB10), PB2, PB5, PB13-15, PC0-13,
 * PA0-3 and PA8-15. A board that puts any of them to another use sees
 * nothing from the bootloader. The USB pins (PC16, PC17) are the USB
 * stack's own (USB_init). The USB-only bootloader (CHBOOT_MENU 0, build.sh
 * nomenu) drives the LED and nothing else: the card's, the panel's and the
 * keys' pins stay high-Z too, for a board without those parts.
 *
 * Rev1 leaves high-Z: the buzzer (PA1), PA0 (VBUS sense), PA2/PA3 (USART2),
 * PB2, PB5 (PB1's pad), PB13-15, PC1/PC2, PC4-15 (PC14/PC15 the test pads)
 * and PC18/PC19 (I2C). It writes GPIOC's CFGLR (PC0, PC3) and never its
 * CFGHR. The backlight (PB9) is driven low until lcd_on() has shown a frame;
 * the USB-only build leaves it high-Z (dark: the board pulls it down). */
#if defined(CHGAME_BOARD_TARGET)            /* rev1 */
#define HAL_GPIOA_CFGLR  0xB8B34444u   /* PA7 MOSI, PA6 MISO pu, PA5 SCK, PA4 LCD_CS */
#define HAL_GPIOB_CFGLR  0x88433488u   /* PB7 SEL, PB6 B, PB5 -, PB4 DC, PB3 SD_CS, PB2 -, PB1 DOWN, PB0 UP */
#define HAL_GPIOB_CFGHR  0x44438338u   /* PB12 LCD_RST, PB11 A, PB10 LED, PB9 backlight, PB8 START */
#define HAL_GPIOC_CFGLR  0x44448448u   /* PC3 LEFT, PC0 RIGHT */
#define HAL_GPIOB_CFGHR_LED 0x44444344u /* (USB only) PB10 LED; every other pin as reset left it */
/* A GPIO register by its address (rev1's accesses): written so, rather than
 * as GPIOB->BSHR, GCC shares one base register among the three ports'
 * registers, and the menu builds are 16-20 B smaller (SIZES.md). */
#define HAL_GPIO(base, reg) (*(volatile uint32_t *)((base) + __builtin_offsetof(GPIO_TypeDef, reg)))
#else                                       /* rev0 */
#define HAL_GPIOA_CFGLR  0xB8B34444u   /* PA7 MOSI, PA6 MISO pu, PA5 SCK, PA4 LCD_CS */
#define HAL_GPIOB_CFGLR  0x88488483u   /* PB7 SEL, PB6 B, PB5 -, PB4 UP, PB3 LEFT, PB2 -, PB1 A, PB0 DC */
#define HAL_GPIOB_CFGHR  0x44433438u   /* PB12 LCD_RST, PB11 SD_CS, PB10 -, PB9 LED, PB8 START */
#define HAL_GPIOC_CFGHR  0x88444444u   /* PC15 RIGHT, PC14 DOWN */
#define HAL_GPIOB_CFGHR_LED 0x44444434u /* (USB only) PB9 LED; every other pin as reset left it */
#endif

#ifndef CHBOOT_MENU
#define CHBOOT_MENU 1
#endif

#if defined(CHGAME_BOARD_TARGET)            /* rev1 */
static inline void hal_pins_init(void)
{
#if CHBOOT_MENU
    RCC->APB2PCENR |= RCC_APB2Periph_AFIO | RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB
                    | RCC_APB2Periph_GPIOC | RCC_APB2Periph_SPI1;
    /* Levels first, so no pin glitches when it becomes an output: both chip
     * selects, LCD_RST and DC high, MISO and the key pull-ups up, the
     * backlight and the LED low. */
    HAL_GPIO(GPIOA_BASE, BSHR) = (1u << 4) | (1u << 6);
    HAL_GPIO(GPIOB_BASE, BSHR) = (1u << 3) | (1u << 4) | (1u << 12) | BTN_PORTB;
    HAL_GPIO(GPIOB_BASE, BCR)  = (1u << 9) | (1u << 10);
    HAL_GPIO(GPIOC_BASE, BSHR) = BTN_PORTC;
    HAL_GPIO(GPIOA_BASE, CFGLR) = HAL_GPIOA_CFGLR;
    HAL_GPIO(GPIOB_BASE, CFGLR) = HAL_GPIOB_CFGLR;
    HAL_GPIO(GPIOB_BASE, CFGHR) = HAL_GPIOB_CFGHR;
    HAL_GPIO(GPIOC_BASE, CFGLR) = HAL_GPIOC_CFGLR;
#else
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOB;
    HAL_GPIO(GPIOB_BASE, BCR)   = 1u << 10;
    HAL_GPIO(GPIOB_BASE, CFGHR) = HAL_GPIOB_CFGHR_LED;
#endif
}
#else                                       /* rev0 */
static inline void hal_pins_init(void)
{
#if CHBOOT_MENU
    RCC->APB2PCENR |= RCC_APB2Periph_AFIO | RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB
                    | RCC_APB2Periph_GPIOC | RCC_APB2Periph_SPI1;
    /* Levels first, so no pin glitches when it becomes an output: both chip
     * selects, LCD_RST and DC high, MISO and the key pull-ups up, LED low. */
    GPIOA->BSHR = (1u << 4) | (1u << 6);
    GPIOB->BSHR = (1u << 0) | (1u << 11) | (1u << 12) | BTN_PORTB;
    GPIOB->BCR  = 1u << 9;
    GPIOC->BSHR = BTN_PORTC;
    GPIOA->CFGLR = HAL_GPIOA_CFGLR;
    GPIOB->CFGLR = HAL_GPIOB_CFGLR;
    GPIOB->CFGHR = HAL_GPIOB_CFGHR;
    GPIOC->CFGHR = HAL_GPIOC_CFGHR;
#else
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOB;
    GPIOB->BCR   = 1u << 9;
    GPIOB->CFGHR = HAL_GPIOB_CFGHR_LED;
#endif
}
#endif

/* Mode 0, 8-bit, MSB first, master with software NSS. BR changes only with
 * SPE clear. */
static inline void hal_spi_speed(uint32_t br)
{
    while (SPI1->STATR & SPI_STATR_BSY) { }
    SPI1->CTLR1 = (uint16_t)(SPI_CTLR1_MSTR | SPI_CTLR1_SSI | SPI_CTLR1_SSM | (br << 3));
    SPI1->CTLR1 = (uint16_t)(SPI_CTLR1_MSTR | SPI_CTLR1_SSI | SPI_CTLR1_SSM | (br << 3) | SPI_CTLR1_SPE);
}

/* Every byte out is a byte in: always reading DATAR keeps RXNE and OVR from
 * leaving stale bytes for the card reads. */
static inline uint8_t hal_spi_xfer(uint8_t b)
{
    SPI1->DATAR = b;
    while (!(SPI1->STATR & SPI_STATR_RXNE)) { }
    return (uint8_t)SPI1->DATAR;
}

/* SPI1's frames and speed, ctl = (BR << 3) | HAL_SPI_16BIT or not: first the
 * wire runs dry and the unread echo and the overrun are cleared (bytes sent
 * with hal_spi_put16() are never read), so no stale byte reaches a card read.
 * The panel's pixels go as 16-bit frames at 24 MHz, as CHGfx sends them; the
 * card needs 8-bit frames back. */
static inline void hal_spi_frames(uint32_t ctl)
{
    while (!(SPI1->STATR & SPI_STATR_TXE)) { }
    while (SPI1->STATR & SPI_STATR_BSY) { }
    (void)SPI1->DATAR;
    (void)SPI1->STATR;
    SPI1->CTLR1 = (uint16_t)(SPI_CTLR1_MSTR | SPI_CTLR1_SSI | SPI_CTLR1_SSM | ctl);
    SPI1->CTLR1 = (uint16_t)(SPI_CTLR1_MSTR | SPI_CTLR1_SSI | SPI_CTLR1_SSM | ctl | SPI_CTLR1_SPE);
}

/* One 16-bit frame, queued: the next waits in the SPI while this one shifts,
 * so the wire, not the CPU, sets the pace. Its echo is never read. */
static inline void hal_spi_put16(uint32_t v)
{
    while (!(SPI1->STATR & SPI_STATR_TXE)) { }
    SPI1->DATAR = (uint16_t)v;
}

#if defined(CHGAME_BOARD_TARGET)            /* rev1 */
static inline void hal_sd_select(int on)  { if (on) HAL_GPIO(GPIOB_BASE, BCR) = 1u << 3; else HAL_GPIO(GPIOB_BASE, BSHR) = 1u << 3; }
static inline void hal_lcd_select(int on) { if (on) HAL_GPIO(GPIOA_BASE, BCR) = 1u << 4; else HAL_GPIO(GPIOA_BASE, BSHR) = 1u << 4; }
static inline void hal_lcd_dc(int data)   { if (data) HAL_GPIO(GPIOB_BASE, BSHR) = 1u << 4; else HAL_GPIO(GPIOB_BASE, BCR) = 1u << 4; }
static inline void hal_lcd_rst(int high)  { if (high) HAL_GPIO(GPIOB_BASE, BSHR) = 1u << 12; else HAL_GPIO(GPIOB_BASE, BCR) = 1u << 12; }
static inline void hal_led(int on)        { if (on) HAL_GPIO(GPIOB_BASE, BSHR) = 1u << 10; else HAL_GPIO(GPIOB_BASE, BCR) = 1u << 10; }
/* Once, by lcd_on(), when the panel shows the frame it was sent. */
static inline void hal_backlight_on(void) { HAL_GPIO(GPIOB_BASE, BSHR) = 1u << 9; }

/* Pressed keys read low (HAL_KEYS: the logical bits). */
static inline uint32_t hal_buttons(void)
{
    uint32_t b = HAL_GPIO(GPIOB_BASE, INDR), c = HAL_GPIO(GPIOC_BASE, INDR);
    return HAL_KEYS(b, c);
}
#else                                       /* rev0 */
static inline void hal_sd_select(int on)  { if (on) GPIOB->BCR = 1u << 11; else GPIOB->BSHR = 1u << 11; }
static inline void hal_lcd_select(int on) { if (on) GPIOA->BCR = 1u << 4;  else GPIOA->BSHR = 1u << 4; }
static inline void hal_lcd_dc(int data)   { if (data) GPIOB->BSHR = 1u << 0; else GPIOB->BCR = 1u << 0; }
static inline void hal_lcd_rst(int high)  { if (high) GPIOB->BSHR = 1u << 12; else GPIOB->BCR = 1u << 12; }
static inline void hal_led(int on)        { if (on) GPIOB->BSHR = 1u << 9; else GPIOB->BCR = 1u << 9; }
#define hal_backlight_on() ((void)0)        /* (no backlight pin: always lit) */

/* Pressed keys read low. */
static inline uint32_t hal_buttons(void)
{
    return (~GPIOB->INDR & BTN_PORTB) | (~GPIOC->INDR & BTN_PORTC);
}
#endif

#ifndef CH32X035_ESIG_UNIID1
#define CH32X035_ESIG_UNIID1  0x1FFFF7E8u   /* 96-bit unique ID */
#endif
static inline uint32_t hal_uid(uint32_t word)
{
    return ((const volatile uint32_t *)CH32X035_ESIG_UNIID1)[word];
}

/* 1 if this boot follows a reset without loss of power (NVIC_SystemReset: a
   program going back to the menu, an upload request), 0 after power-on.
   Clears the reset flags, so the next boot sees only its own cause. The
   software-reset flag cannot tell the two apart: on the board it is set
   after a power-on as well (test/hil/RESULTS-2026-10-01.md; the factory boot
   code runs first and enters the user flash with a software reset). The
   power-on flag can. */
static inline int hal_soft_reset(void)
{
    uint32_t f = RCC->RSTSCKR;
    RCC->RSTSCKR |= RCC_RMVF;
    return (f & RCC_PORRSTF) == 0;
}

/* A full system reset (PFIC CFGR SYSRESET); SRAM survives it. */
static inline __attribute__((noreturn)) void hal_reset(void)
{
    NVIC->CFGR = NVIC_KEY3 | (1u << 7);
    for (;;) { }
}

#define FLASH_AT(a)   ((const uint8_t *)(uintptr_t)(a))

#endif /* CHBOOT_HOST */

/* An aligned word of flash. */
#define FLASH_W(a)    (*(const uint32_t *)(const void *)FLASH_AT(a))

/* The board word of the bootloader's own image (offset 0x14, the vector
 * table's reserved slot: startup_chgame_boot.S, chg_format.h): CHG_TARGET_ID
 * on a board after rev0, 0 on rev0. (Only a bootloader build reads it: the
 * dry run, at 0x3000, has no HELLO.) */
#define HAL_BOARD_WORD FLASH_W(0x14u)

#endif
