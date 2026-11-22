/*
 * CHGame Rev1 board variant  -  CH32X035G8U6, QFN28. Rev 1.5 uses it too.
 *
 * Rev 1 (the game system) and Rev 1.5 (the same, plus USB-PD sink, battery
 * USB host and a protected power output) have one pinout. The pin roles
 * come from the boards' handoff (designs Rev1C and Rev1B), checked against
 * WCH's datasheet and reference manual; docs/hardware-pinmap.md has the
 * table. It is not Rev0's pinout: a binary built for one board must not run
 * on the other, since each drives pins that the other uses as buttons.
 *
 * WHO OWNS WHAT. These hold for every sketch on this board:
 *
 *   PB5 is bonded to PB1 (DOWN): one pad in this package. Never make PB5 an
 *   output or give it a pull; it reads the DOWN button.
 *
 *   PC10 / PC11 are bonded to PC17 / PC16, USB D+ / D-. They stay floating
 *   inputs.
 *
 *   TIM1 belongs to the backlight (CH1, PB9) and the LED (CH2, PB10), at
 *   TIM1 remap 000. Only CH1 and CH2 may be enabled: remap 000 also puts
 *   CH3 on PB11 (A), CH4 on PC16 (USB D-), ETR on PC17 (USB D+), BKIN on PB5
 *   (DOWN) and CH1N-CH3N on PB6-PB8 (B, SELECT, START). Never enable the
 *   complementary outputs or the break input.
 *
 *   TIM2 belongs to the CHGame library's audio: CH2 on PA1 (the buzzer), at
 *   TIM2 remap 000. TIM2_CH1 (PA0) is never enabled.
 *
 *   PA0 is VBUS sense (VBUS / 101, R28 100k over R11 1k) on Rev 1, and also
 *   HOST_EN on Rev 1.5. Never drive it: analog input only.
 *
 *   PC14 / PC15 are test pads TP14 / TP15 on Rev 1 and CC1 / CC2 (through
 *   the CH211) on Rev 1.5. They stay floating inputs unless a sketch knows
 *   which board it is on.
 *
 *   The backlight (PB9, active high, R20 pulls it down) stays LOW until the
 *   panel shows a defined picture (CHGfx's gfx_begin() does this).
 *
 * The stock CH32X035G8U defaults that would hit this board are overridden
 * below, as on Rev0: Wire on PC18 / PC19 (the stock PC17 / PC16 are USB),
 * Serial1 on PA2 / PA3 (the stock PB10 / PB11 are the LED and A).
 *
 * Serial is USB CDC (see WSerial.h). Serial1 is USART2 on CN3 (PA2 TX,
 * PA3 RX); Wire is I2C1 on CN2 (PC18 SDA, PC19 SCL, 4.7k pull-ups on the
 * board). Both connectors are 3.3 V.
 */
#pragma once

/* platform.txt passes -DARDUINO_{build.board}; without it the core and the
 * libraries would compile Rev0's pins into a Rev1 build. */
#ifndef ARDUINO_CHGAME_REV1
#error "platform.txt must pass -DARDUINO_{build.board} (board package 0.4.0 or later)"
#endif

/* ENABLE Peripherals */
#define                         ADC_MODULE_ENABLED
#define                         UART_MODULE_ENABLED
#define                         SPI_MODULE_ENABLED
#define                         I2C_MODULE_ENABLED
#define                         TIM_MODULE_ENABLED

/* CH32VX035G8 Pins */
#define PA0                     PIN_A0
#define PA1                     PIN_A1
#define PA2                     PIN_A2
#define PA3                     PIN_A3
#define PA4                     PIN_A4
#define PA5                     PIN_A5
#define PA6                     PIN_A6
#define PA7                     PIN_A7
#define PB0                     PIN_A8
#define PB1                     PIN_A9
#define PB3                     10
#define PB4                     11
#define PB6                     12
#define PB7                     13
#define PB8                     14
#define PB9                     15
#define PB10                    16
#define PB11                    17
#define PB12                    18
#define PC0                     PIN_A10
#define PC3                     PIN_A13
#define PC14                    21
#define PC15                    22
#define PC16                    23
#define PC17                    24
#define PC18                    25
#define PC19                    26

// Alternate pins number
#define PA0_ALT1                (PA0  | ALT1)
#define PA1_ALT1                (PA1  | ALT1)
#define PA2_ALT1                (PA2  | ALT1)
#define PA3_ALT1                (PA3  | ALT1)
#define PA4_ALT1                (PA4  | ALT1)
#define PA5_ALT1                (PA5  | ALT1)
#define PA6_ALT1                (PA6  | ALT1)
#define PA7_ALT1                (PA7  | ALT1)
#define PB0_ALT1                (PB0  | ALT1)
#define PB1_ALT1                (PB1  | ALT1)
#define PC0_ALT1                (PC0  | ALT1)
#define PC3_ALT1                (PC3  | ALT1)



#define NUM_DIGITAL_PINS        27
#define NUM_ANALOG_INPUTS       14
#define ADC_RESOLUTION          12


// On-board LED pin number

/* ---- CHGame Rev1 board pin roles --------------------------------------------
 * QFN28 pin numbers in comments.
 */

/* User LED - PB10 -> R9 (1k) -> LED -> GND, so ACTIVE HIGH. (TIM1_CH2.) */
#define LED_BUILTIN             PB10    /* pin 21 */
#define PIN_LED                 PB10

/* Buzzer - PA1 drives the low-side MOSFET of a magnetic buzzer fed from
 * VSYS: active high, LOW when silent, never left HIGH. (TIM2_CH2.)
 *
 * The core's tone() (Peripherals: Full) stops with the pin LOW on this
 * board (Tone.cpp), and the CHGame library's audio leaves PA1 LOW when
 * silent. Code driving PA1 itself must never leave it HIGH: that is a
 * steady current through the buzzer and R27. */
#define PIN_BUZZER              PA1     /* pin  6 */

/* Display backlight - PB9, ACTIVE HIGH, R20 pulls it down. LOW until the
 * panel shows a defined picture. (TIM1_CH1.) */
#define PIN_LCD_BL              PB9     /* pin 20 */

/* Game buttons. All are switch-to-GND, so they need INPUT_PULLUP and read
 * LOW when pressed. DOWN's pad is also PB5: never drive PB5. */
#define PIN_BTN_UP              PB0     /* pin 13 */
#define PIN_BTN_DOWN            PB1     /* pin 16, bonded to PB5 */
#define PIN_BTN_LEFT            PC3     /* pin  4 */
#define PIN_BTN_RIGHT           PC0     /* pin  3 */
#define PIN_BTN_A               PB11    /* pin 22 */
#define PIN_BTN_B               PB6     /* pin 17 */
#define PIN_BTN_SELECT          PB7     /* pin 18 */
#define PIN_BTN_START           PB8     /* pin 19 */

/* ST7735 128x128 display and microSD share hardware SPI1. The card's DI
 * is gated by SD_CS (an OR gate): deselected, it sees MOSI held high. */
#define PIN_LCD_CS              PA4     /* pin  9  (also SPI1 NSS) */
#define PIN_LCD_DC              PB4     /* pin 15 */
#define PIN_LCD_RST             PB12    /* pin 23 */
#define PIN_SD_CS               PB3     /* pin 14 */

/* VBUS sense: analog input only (analogRead), VBUS / 101 - about 50 mV at
 * 5 V. Never an output: HOST_EN on Rev 1.5. */
#define PIN_VBUS_SENSE          PA0     /* pin  5 */

/* Test pads TP14 / TP15: GPIO on Rev 1, CC1 / CC2 on Rev 1.5 (leave them
 * alone there). Not PWM alongside audio: their timer channels need TIM2
 * remap 6 (which takes audio off PA1) or TIM1 remap 4 (which takes the
 * backlight's and the LED's channels away). */
#define PIN_TP14                PC14    /* pin 28 */
#define PIN_TP15                PC15    /* pin  1 */

#ifndef LED_BUILTIN
  #define LED_BUILTIN           PB10
#endif

/* CHGfx's pins (CHGfx.h keeps Rev0's as its defaults). */
#ifndef CHGFX_CS_PORT
  #define CHGFX_CS_PORT         GPIOA
#endif
#ifndef CHGFX_CS_PIN
  #define CHGFX_CS_PIN          4
#endif
#ifndef CHGFX_DC_PORT
  #define CHGFX_DC_PORT         GPIOB
#endif
#ifndef CHGFX_DC_PIN
  #define CHGFX_DC_PIN          4
#endif
#ifndef CHGFX_RST_PORT
  #define CHGFX_RST_PORT        GPIOB
#endif
#ifndef CHGFX_RST_PIN
  #define CHGFX_RST_PIN         12
#endif
#ifndef CHGFX_SDCS_PORT
  #define CHGFX_SDCS_PORT       GPIOB
#endif
#ifndef CHGFX_SDCS_PIN
  #define CHGFX_SDCS_PIN        3
#endif
#ifndef CHGFX_BL_PORT
  #define CHGFX_BL_PORT         GPIOB
#endif
#ifndef CHGFX_BL_PIN
  #define CHGFX_BL_PIN          9
#endif



// On-board user button
#ifndef USER_BTN
  #define USER_BTN              PNUM_NOT_DEFINED
#endif

// SPI definitions
#ifndef PIN_SPI_SS
  #define PIN_SPI_SS            PA4
#endif
#ifndef PIN_SPI_MOSI
  #define PIN_SPI_MOSI          PA7
#endif
#ifndef PIN_SPI_MISO
  #define PIN_SPI_MISO          PA6
#endif
#ifndef PIN_SPI_SCK
  #define PIN_SPI_SCK           PA5
#endif

// I2C definitions: I2C1 remap 3, on CN2
/* CHGAME: stock default was PC17 - that is USB D+ on this board. */
#ifndef PIN_WIRE_SDA
  #define PIN_WIRE_SDA          PC18
#endif
/* CHGAME: stock default was PC16 - that is USB D- on this board. */
#ifndef PIN_WIRE_SCL
  #define PIN_WIRE_SCL          PC19
#endif

// Timer Definitions
#ifndef TIMER_TONE
  #define TIMER_TONE            TIM3
#endif
/* CHGAME: the stock TIM2 is the CHGame library's audio on this board, and
 * TIM1 the backlight's and the LED's. Servo and tone() then share TIM3:
 * use one or the other. */
#ifndef TIMER_SERVO
  #define TIMER_SERVO           TIM3
#endif


// UART Definitions
#ifndef SERIAL_UART_INSTANCE
  #define SERIAL_UART_INSTANCE  1
#endif
// Default pin used for generic 'Serial' instance
// Mandatory for Firmata
/* CHGAME: stock default was PB11 - that is the A button here.
 * Serial1 is USART2 on CN3 instead (PA3 RX). */
#ifndef PIN_SERIAL_RX
  #define PIN_SERIAL_RX         PA3
#endif
/* CHGAME: stock default was PB10 - that is the LED here. CN3, PA2 TX. */
#ifndef PIN_SERIAL_TX
  #define PIN_SERIAL_TX         PA2
#endif

/*----------------------------------------------------------------------------
 *        Arduino objects - C++ only
 *----------------------------------------------------------------------------*/

#ifdef __cplusplus
  // These serial port names are intended to allow libraries and architecture-neutral
  // sketches to automatically default to the correct port name for a particular type
  // of use.  For example, a GPS module would normally connect to SERIAL_PORT_HARDWARE_OPEN,
  // the first hardware serial port whose RX/TX pins are not dedicated to another use.
  //
  // SERIAL_PORT_MONITOR        Port which normally prints to the Arduino Serial Monitor
  //
  // SERIAL_PORT_USBVIRTUAL     Port which is USB virtual serial
  //
  // SERIAL_PORT_LINUXBRIDGE    Port which connects to a Linux system via Bridge library
  //
  // SERIAL_PORT_HARDWARE       Hardware serial port, physical RX & TX pins.
  //
  // SERIAL_PORT_HARDWARE_OPEN  Hardware serial ports which are open for use.  Their RX & TX
  //                            pins are NOT connected to anything by default.
  #ifndef SERIAL_PORT_MONITOR
    #define SERIAL_PORT_MONITOR   Serial
  #endif
  #ifndef SERIAL_PORT_HARDWARE
    #define SERIAL_PORT_HARDWARE  Serial
  #endif
#endif
