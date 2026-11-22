# CHBoardTest

One screen that checks a CHGame board: the eight buttons, the LED, the
backlight, the buzzer, the SD card, VBUS sense, CN3, CN2, the test pads and
the core's fault handler. One source builds for Rev0 and Rev1. A Rev 1.5
board is a Rev1 and takes the Rev1 build.

It is for bringing up and repairing boards, so it lives in `tools/sketches`:
the board package does not ship it and it is not on the casino card. It runs
on the board only (there is no simulator run). It saves nothing.

## Build and upload

```bash
chgame --sketch CHBoardTest upload                 # the newest board (Rev1)
chgame --board rev0 --sketch CHBoardTest upload    # a Rev0 board
```

`tools/game.py` builds it with Peripherals "Full" (Serial1, for CN3) and
USB Serial. In the Arduino IDE, pick the board, then Tools > Peripherals >
Full and Tools > USB > Serial. With Peripherals "Game" it still builds, but
the CN3 check then says NEEDS PERIPH FULL.

Upload the build for the board in hand. A Rev0 binary drives some of Rev1's
button pins as outputs, and a Rev1 binary some of Rev0's, so a button press
then shorts an output.

The top right of the screen names the board the binary was built for:
REV0 or REV1, from the board package's `ARDUINO_CHGAME_REV0` /
`ARDUINO_CHGAME_REV1`. A package older than 0.4.0 defines neither and the
screen says UNKNOWN; such a package only builds Rev0's pins.

## Using it

| Button | Does |
|---|---|
| UP / DOWN | pick a check |
| A | run it |
| B | stop the sound |
| SELECT held 2 s, then A | on TP14/15: the pull-up test (Rev 1 only); on FAULT: the deliberate crash |
| START held 3 s | leave (the library's gesture: back to the SD game menu, or a restart under the USB Only bootloader) |

Power off and on, or an upload, also leaves it. Uploads work while it runs.

The bottom line says how to run the picked check, or, for the SD card, what
it found in detail.

## The checks

### Buttons

The eight are drawn at the top. A held button is gold. A button pressed at
least once keeps a cyan edge, and BUTTONS n/8 counts them. Press each one:
expect 8/8, and each lights alone. A quick START press is safe; only a
3-second hold leaves.

| | Rev0 | Rev1 / Rev 1.5 |
|---|---|---|
| UP, DOWN, LEFT, RIGHT | PB4, PC14, PB3, PC15 | PB0, PB1, PC3, PC0 |
| A, B, SELECT, START | PB1, PB6, PB7, PB8 | PB11, PB6, PB7, PB8 |

### SWEEP

A plays one steady tone that rises a semitone every 150 ms, from C2 (65 Hz)
to B8 (7,902 Hz), through the library's `audio::melody()`, then stops. The
line shows the note and its frequency. A holds a note (A again goes on), B
stops. Write down where the buzzer is loud and where it fades out.

Expected: a clean tone at each step through the middle of the range (the
lowest and highest notes may be faint), then DONE, SILENT and silence. On
Rev1 the buzzer is magnetic, fed from VSYS through R27 and switched by Q6
from PA1: after the sweep nothing there is warm. Its design point is about
4 kHz; how loud the rest of the range is has to be measured.

### SOAK

A plays a looping tune of arpeggios from F5 to C7 (698 to 2,093 Hz), driven
about 90% of the time, and counts the time. B stops it; the line keeps the
time it ran. The count turns green at 10:00 and goes on.

For the bench: 10 minutes on USB while charging, measuring the current and
the temperatures of R27, the buzzer and the regulator.

### SD CARD

A initialises the card with CHSd's `sd::init()`, reads sector 0 with
`sd::read()` and mounts the volume with `fat::mount()`.

| The line says | Meaning |
|---|---|
| OK FAT32 7.4GB (green) | the card works and the games can read it |
| OK EXFAT 59.4GB (gold) | the card works, but CHSd reads FAT16 and FAT32 only: reformat it |
| NO CARD | nothing answered (an empty slot fails in about 15 ms) |
| SECTOR 0 FAILED | it initialised, then sent no data |

The size is the volume's, from the first MBR partition (or from the boot
sector of a card without a partition table: a sector 0 that starts with a
jump and holds a FAT BPB, 512 bytes a sector). CHSd reads blocks, not the
card's registers, so the card's type, capacity and CID are not shown. The
bottom line gives the init time, whether sector 0 ends in 55AA and whether
it is an MBR.

Rev1's card CS is PB3 (Rev0: PB11), and its DI is gated by CS through an OR
gate, so a deselected card sees MOSI held high while the panel is drawn.

### VBUS (Rev1 only)

PA0 senses VBUS through R28 (100k) and R11 (1k): PA0 = VBUS / 101. The line
averages 16 ADC reads, about four times a second, and shows
VBUS = code / 4095 x 3.3 V x 101, with the average code.

One code is about 81 mV of VBUS, and the reference is the 3.3 V rail,
uncalibrated, so it is coarse: good for "USB power is there", not for a
measurement.

| Situation | Expected |
|---|---|
| USB (any 5 V source) | about 5.0 V, code about 62, green |
| battery only | close to 0 V, gold |
| Rev 1.5 on a USB-PD charger | about 5.0 V: this firmware negotiates no contract |

PA0 is only ever an analog input here. On Rev 1.5 it is also HOST_EN, and
R11 keeps the host boost off while nothing drives it.

### CN3 UART

Serial1's pins (USART2: PA2 TX, PA3 RX) at 115200 send 16 bytes, one at a
time, and wait up to 1 ms for each to come back. Jumper CN3 pin 3 (TX) to
pin 4 (RX), then press A.

`Serial1.begin()` sets up the pins, the baud rate and the USART. The bytes
are then sent and read on the USART's registers, polled. Before board
package 0.4.0 the core's `Serial1` did not receive on these pins: it is
built for USART1, and its `begin()` enabled the receive interrupt for
USART1 only, while PA2 and PA3 are USART2, so `Serial1.read()` never
returned a byte. 0.4.0 fixes that. The check works with either core: it
finds the USART from the pin map, as the core does, and turns its receive
interrupt off while it runs.

| The line says | Meaning |
|---|---|
| PASS 16/16 AT 115200 | the 16 bytes came back |
| NO LOOP | nothing came back: no jumper, or a broken line |
| BAD n/16 RIGHT | bytes came back wrong |

Serial1 starts at the first A and then stays on (TX idles high) until a
reset. On Rev0 the same pins are on header H1.

### CN2 I2C

Reads SDA (PC18) and SCL (PC19) every frame, as they are. Nothing is sent:
no start condition and no address. On Rev 1.5, 0x34 and 0x35 (the CH211)
and 0x40 (the INA226) are the power devices, and only the power library
talks to them.

Expected on Rev1 and Rev 1.5: SDA H SCL H IDLE HIGH, from the 4.7k
pull-ups to 3.3 V on both lines. A line held low means something on the
bus pulls it: an accessory, a short, or, on Rev 1.5 after a power app has
run, the CH211 pulling SCL for an interrupt. A high reading does not prove
the pull-ups are fitted: a floating line can read high too, and these are
also the debug interface's pins (DIO, DCK). Measure the resistors if in
doubt.

Rev0 has no pull-ups on PC18 and PC19, and its pin map does not put them on
a header, so the line shows the two levels in grey, with no verdict. What
they read depends on what is fitted and connected; a high reading may come
only from the debug interface, which has both pins after reset.

### TP14/15 (Rev1 only)

On this line, hold SELECT for 2 s (the line says ARMED: A TESTS), keep
holding it and press A. The check pulls each test pad up (the MCU's
pull-up, never an output), reads it and leaves it floating again. FREE
means the pad followed the pull: nothing holds it. LOW means it is tied to
something, such as a CC line's 5.1k Rd. These pins have no pull-down on the
CH32X035, so a pad held high also reads FREE.

Expected on Rev 1: TP14 FREE TP15 FREE, unplugged and with the USB-C cable
in either way round: the pads are not connected to CC.

Run it on a Rev 1 only. On a Rev 1.5 PC14 and PC15 are CC1 and CC2 through
the CH211, and belong to the PD policy. The Rev1 build runs on both boards
and cannot tell them apart, so it leaves the two pins untouched until the
check is armed.

### LED

A steps through OFF, ON and BLINKING. Rev0's LED is PB9, Rev1's is PB10;
both are active high.

### BACKLIGHT

Rev1: PB9, active high, held off by R20. CHGfx's `gfx_begin()` keeps it
dark, puts a black frame on the panel and only then lights it, so the
screen never shows the panel's power-up noise. A darkens it for 1 s.

Expected: at power-on and after each upload the screen comes on black,
then draws; A darkens it for a second.

Rev0 has no backlight pin: it is on whenever the board is.

### FAULT

On this line, hold SELECT for 2 s (the line says ARMED: A CRASHES), keep
holding it and press A. The sketch turns the LED off, so a lit LED
afterwards can only come from the fault handler. The screen shows what to
expect, a 2 kHz tone starts, and 250 ms later the sketch runs an illegal
instruction. The core's fault handler then turns interrupts off, drives the
buzzer pin low and lights the LED.

| | Rev0 | Rev1 / Rev 1.5 |
|---|---|---|
| buzzer pin, low | PB10 | PA1 (0 V on a meter) |
| LED, lit | PB9 | PB10 |
| backlight | always on | PB9 untouched: stays on |

Expected: the tone stops at once, the LED is lit, the screen stays as it
is, and USB goes away. Power off and on to go on. If the line ever says NOT
TRAPPED, the instruction did not trap.

In a debug build the handler sets the buzzer and LED pins the same way,
then hands the board to the library's debug protocol, which keeps
answering until the board is powered off or reset: `!` reports the crash
and `B` goes to the bootloader. USB stays up, and A does not restart the
sketch.

## The USB serial port

In a release build, with the port open (any terminal), each result is also
a line:

```
CHBT BOARD: REV1, CHBOARDTEST 1.0
CHBT BUTTON: A
CHBT SD: OK FAT32 7.4GB
CHBT SD: INIT 120 MS, 55AA OK, MBR
CHBT CN3: PASS 16/16 AT 115200
CHBT VBUS: 5.0V CODE 62 COARSE
CHBT SOAK: 3:00
```

The board line comes when the port opens, a button line the first time
each button is pressed, VBUS every 5 s (Rev1), the soak's time every
minute, and a line for each check run. A debug build sends none of these:
there the port is the debug protocol's, for `chgame shot`.

## Files

| File | |
|---|---|
| `CHBoardTest.ino` | the screen, the buttons, the LED, the backlight and the sound |
| `Checks.h`, `Checks.cpp` | SD, VBUS, CN3, CN2, the test pads and the fault |
| `config.h` | the version (prefix and debug hello `CHBT`) and the board |
| `tools/game.py` | the board options for the shared tools |
