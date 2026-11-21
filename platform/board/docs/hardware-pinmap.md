# Board pin maps (CH32X035G8U6, QFN28)

Two boards share the chip: **CHGame Rev0** and **CHGame Rev1**. Rev 1.5 is
a Rev1 with USB-PD, a battery USB host and a protected power output added;
its pins are Rev1's except for the roles of PA0, PC14 and PC15, and it uses
the Rev1 board entry. The two pinouts differ, so a program is built for one
board or the other: each drives pins that the other uses as buttons, and a
button press then shorts an output. Sketches use the variants' names
(`variants/CH32X035/CHGame_Rev0/variant_CHGame_Rev0.h`,
`variants/CH32X035/CHGame_Rev1/variant_CHGame_Rev1.h`), not port numbers.

The CH32X035 datasheet's pin table lists seven packages side by side;
**QFN28 is the third numeric column** — a detail worth remembering, because
reading the wrong column makes PC16/PC17 look like pins 7/8 instead of 26/27.

## Side by side

| Role | Rev0 | Rev1 |
|---|---|---|
| UP / DOWN / LEFT / RIGHT | PB4 / PC14 / PB3 / PC15 | PB0 / PB1 / PC3 / PC0 |
| A / B / SELECT / START | PB1 / PB6 / PB7 / PB8 | PB11 / PB6 / PB7 / PB8 |
| LCD CS / DC / RST | PA4 / PB0 / PB12 | PA4 / PB4 / PB12 |
| SD card CS | PB11 | PB3 (it also gates the card's DI) |
| SPI1 SCK / MISO / MOSI | PA5 / PA6 / PA7 | PA5 / PA6 / PA7 |
| Buzzer | PB10, TIM1 CH2: a piezo | PA1, TIM2 CH2: a magnetic buzzer switched by a MOSFET |
| LED | PB9 | PB10 |
| Backlight | always on | PB9, switched |
| PA0 | header H1 | VBUS sense (also HOST_EN on Rev 1.5) |
| PC14 / PC15 | DOWN / RIGHT | test pads TP14 / TP15 (CC1 / CC2 on Rev 1.5) |
| Serial1 (USART2) TX / RX | PA2 / PA3, header H1 | PA2 / PA3, connector CN3 |
| Wire (I2C1) SDA / SCL | PC18 / PC19 | PC18 / PC19, connector CN2 |
| USB D- / D+ | PC16 / PC17 | PC16 / PC17 |

## Rev0

Derived from `Netlist_Schematic1_2026-08-21.tel` and cross-checked against
the datasheet's QFN28 column: every row's pin number was matched to that
column independently. The first derivation left the ports of pins 7-11, 13,
22 and 23 open; they are the variant's, which every program for the board
uses, and they agree with the datasheet. Pins 3-6, the header's GPIOs, are
the variant's too.

| QFN28 pin | Port  | Net          | Function            |
|-----------|-------|--------------|---------------------|
| 1         | PC15  | `BTN_RIGHT`  | D-pad right         |
| 3         | PC0   |              | header H1.8 (`PIN_GPIO1`) |
| 4         | PC3   |              | header H1.7 (`PIN_GPIO2`) |
| 5         | PA0   |              | header H1.6 (`PIN_GPIO3`) |
| 6         | PA1   |              | header H1.5 (`PIN_GPIO4`) |
| 7         | PA2   | `UART_TX`    | header H1.4         |
| 8         | PA3   | `UART_RX`    | header H1.3         |
| 9         | PA4   | `LCD_CS`     | ST7735 chip select  |
| 10        | PA5   | `CLK`        | SPI SCK (LCD + SD)  |
| 11        | PA6   | `MISO`       | SPI (SD)            |
| 12        | PA7   | `MOSI`       | SPI (LCD + SD)      |
| 13        | PB0   | `LCD_DC`     | ST7735 data/command |
| 14        | PB3   | `BTN_LEFT`   | D-pad left          |
| 15        | PB4   | `BTN_UP`     | D-pad up            |
| 16        | PB1   | `BTN_A`      | A button            |
| 17        | PB6   | `BTN_B`      | B button            |
| 18        | PB7   | `BTN_SELECT` | Select              |
| 19        | PB8   | `BTN_START`  | Start               |
| 20        | PB9   | `LED`        | status LED          |
| 21        | PB10  | `BUZZER`     | piezo               |
| 22        | PB11  | `SD_CS`      | microSD chip select |
| 23        | PB12  | `LCD_RST`    | ST7735 reset        |
| 26        | PC16  | `UDM`        | USB D-              |
| 27        | PC17  | `UDP`        | USB D+              |
| 28        | PC14  | `BTN_DOWN`   | D-pad down          |

### Status LED

`PB9 -> R9 -> LED2 -> GND`, so the LED is **active HIGH**. At reset PB9 is a
floating input and the LED is dark, which is useful: anything lighting it means
code is running and has deliberately configured the pin.

## Rev1 (and Rev 1.5)

From the boards' hardware handoff (2026-11-17), which read both designs'
EDA projects (Rev1C, the game system, is Rev 1; Rev1B, with the power
controls, is Rev 1.5), checked against WCH's datasheet and reference
manual. The bring-up checks are `tools/sketches/CHBoardTest` and
[../../bootloader/HARDWARE.md](../../bootloader/HARDWARE.md), "Rev1".

| QFN28 pin | Port | Net | Function | Rev 1.5 |
|---|---|---|---|---|
| 1 | PC15 | `TP15` | test pad | `CC2_MCU`: USB CC2, through the CH211 |
| 3 | PC0 | `BTN_RIGHT` | D-pad right | |
| 4 | PC3 | `BTN_LEFT` | D-pad left | |
| 5 | PA0 | `VBUS_SENSE` | VBUS / 101, analog input only | also `HOST_EN` |
| 6 | PA1 | `AUDIO_PWM` | buzzer, TIM2 CH2 | |
| 7 | PA2 | `UART_TX` | CN3.3, USART2 TX | |
| 8 | PA3 | `UART_RX` | CN3.4, USART2 RX | |
| 9 | PA4 | `LCD_CS` | ST7735 chip select | |
| 10 | PA5 | `CLK` | SPI SCK (LCD + SD) | |
| 11 | PA6 | `MISO` | SPI (SD), 10 kΩ pull-up | |
| 12 | PA7 | `MOSI` | SPI: to the LCD, and to the SD card through the gate; 10 kΩ pull-up | |
| 13 | PB0 | `BTN_UP` | D-pad up | |
| 14 | PB3 | `SD_CS` | microSD chip select, 10 kΩ pull-up | |
| 15 | PB4 | `LCD_DC` | ST7735 data/command | |
| 16 | PB1 (and PB5) | `BTN_DOWN` | D-pad down | |
| 17 | PB6 | `BTN_B` | B button | |
| 18 | PB7 | `BTN_SELECT` | Select | |
| 19 | PB8 | `BTN_START` | Start | |
| 20 | PB9 | `BL_PWM` | backlight, active high, TIM1 CH1 | |
| 21 | PB10 | `USER_LED` | status LED, active high, TIM1 CH2 | |
| 22 | PB11 | `BTN_A` | A button | |
| 23 | PB12 | `LCD_RST` | ST7735 reset, active low | |
| 24 | PC19 | `SCL` | CN2.4, I2C1 SCL (remap 3); also the debug clock DCK | also the CH211's and INA226's bus |
| 25 | PC18 | `SDA` | CN2.3, I2C1 SDA (remap 3); also the debug data DIO | also the CH211's and INA226's bus |
| 26 | PC16 | `UDM` | USB D- | |
| 27 | PC17 | `UDP` | USB D+, and BOOT | |
| 28 | PC14 | `TP14` | test pad | `CC1_MCU`: USB CC1, through the CH211 |

The buttons switch to GND with no external pull-ups: inputs with the
internal pull-up, pressed reads LOW. The D-pad's pins are ADC-capable (UP
A8, DOWN A9, RIGHT A10, LEFT A13), but the fitted switches are digital.

### Bonded pads

**PB1 and PB5 are one pad** in this package. PB5 is never made an output or
given a pull: it is the DOWN button. **PC10 and PC11** share the pads of
PC17 and PC16, USB D+ and D-, and stay floating inputs.

### Timers

| Timer | Channel | Pin | Owner |
|---|---|---|---|
| TIM1, remap 000 | CH1 | PB9 | the backlight |
| | CH2 | PB10 | the LED |
| TIM2, remap 000 | CH2 | PA1 | the buzzer (the CHGame library's audio) |
| TIM3 | | | `tone()` and `Servo`, one at a time |

At remap 000 TIM1 also puts CH3 on PB11 (A), CH4 on PC16 (USB D-), ETR on
PC17 (USB D+), **BKIN on PB5** (DOWN) and **CH1N-CH3N on PB6-PB8** (B,
SELECT, START). Only CH1 and CH2 are ever enabled: never the complementary
outputs or the break input, or a button would short a driven pin.
**TIM2_CH1 is never enabled:** at remap 000 it is PA0. PA2 and PA3 can be
TIM2 CH3 and CH4, which share audio's period. TP14 and TP15 cannot be PWM
pins while the board's own features run: their channels need TIM1 remap 4
(which takes the backlight's and the LED's channels) or TIM2 remap 6 (which
takes audio off PA1). The variant's `PinMap_TIM` lists only PB9 and PB10 (TIM1
remap 000) and PA1, so `analogWrite()` reaches nothing else.

### PA0: VBUS sense

R28 (100 kΩ) from VBUS and R11 (1 kΩ) to GND: PA0 = VBUS / 101, about
50 mV at 5 V. It is an **analog input, never driven and never pulled.** On
Rev 1.5 the same node is `HOST_EN`: high starts the battery boost (USB host
power) and turns off the input buck; the 1 kΩ keeps it off while PA0 floats.
A driven PA0 measures its own level, not VBUS. With the 3.3 V rail as the
ADC's reference one code is about 81 mV of VBUS: enough to see whether USB
power is there, not to measure it. PA0 does not measure the battery.

### Buzzer, backlight, LED

- **Buzzer:** PA1 switches the low-side MOSFET (Q6, through R25) of a
  magnetic buzzer fed from `VSYS_SW` through R27, with flyback protection.
  Active high and **LOW when silent: never left HIGH**, which is a steady
  current through the buzzer and R27. Its design point is about 4 kHz at
  up to 50% duty; the loudness across the range is to be measured.
- **Backlight:** PB9 drives Q5, active high, and R20 holds it off through
  reset. It stays LOW until the panel shows a defined picture (CHGfx's
  `gfx_begin()`, and the rev1 bootloaders after the panel's first frame).
- **LED:** `PB10 -> R9 (1 kΩ) -> LED -> GND`, active high. The charge LED
  is the charger's, not a GPIO.

### The SD card's DI gate

U12, an SN74LVC1G32 OR gate: the card's DI is MOSI OR SD_CS. With SD_CS low
the card sees MOSI; with it high its DI is held high, whatever the panel is
sent. SCK stays shared and ungated, so the card still gets its start-up
clocks with CS high. There is no card-detect pin and no switch on the
card's power ([../../../docs/hardware-revisions.md](../../../docs/hardware-revisions.md),
"For rev1: the SD card's DI gate").

### CN2 and CN3

| Connector | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| CN2, I2C | GND | 3.3 V | PC18 SDA | PC19 SCL |
| CN3, UART | GND | 3.3 V | PA2, the MCU's TX | PA3, the MCU's RX |

Both are 3.3 V, powered with the game rail (no software switch), and the
shell pads are GND. CN2 is `Wire` (I2C1 at remap 3, 4.7 kΩ pull-ups on the
board) or the WCH two-wire debug interface (DIO, DCK). On Rev 1.5 the bus
also carries the CH211 (0x35; 0x34 is its fast-read address) and the INA226
(0x40). CN3 is `Serial1` (USART2), not an I2C port: cross TX and RX to the
accessory.

### Test pads TP14 / TP15

PC14 and PC15 on Rev 1, not connected to USB's CC lines: floating inputs
unless a sketch uses them (`PIN_TP14`, `PIN_TP15`); they are not ADC
channels. On Rev 1.5 they are CC1 and CC2, through the CH211.

## Both boards

### BOOT button

`SW9` bridges `UDP` (PC17, pin 27) to 3V3 through `R10` (4.7 kΩ). The part
samples USB D+ at reset; finding it pulled high selects the factory ISP. So BOOT
must be **held across a reset**, not merely pressed. See `recovery.md`.

### No external reset pin

No bonded pin of the CH32X035G8U6 has a reset function. The datasheet puts
RST on PA21, which this package does not have; on PC3 only in the QSOP28
and TSSOP20 packages; and on PB7 only in the CH32X033's TSSOP20. So PB7
(SELECT on both boards) and PC3 (LEFT on Rev1) are GPIOs whatever the option
byte `RST_MOD` says. The chips read `RST_MOD = 0b11` (the reset function
off, the reference manual's default; `recovery.md`). It is recorded at
bring-up and never changed. The only ways to reset this part are the power
switch and `NVIC_SystemReset()` — which is why the software boot-request
path has to be reliable.
