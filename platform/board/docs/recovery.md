# Recovery — getting back to the WCH factory ISP

The CH32X035's factory USB ISP bootloader lives in a separate, non-erasable boot
area. Nothing this project writes can damage it, so this path always works no
matter how badly the custom bootloader or application is broken. **Never remove
or obstruct it.**

## The hardware condition

From the board netlist: `SW9` (the DOWNLOAD/BOOT button) bridges the `UDP` net
(USB D+, `PC17`, MCU pin 27) to `3v3` through `R10` (4.7 kΩ). The CH32X035
samples USB D+ at reset; finding it pulled high through a resistor is what
selects the factory ISP instead of user flash. Rev1 (and Rev 1.5) have the
same button on the same pin.

The consequence: **BOOT must be held across a reset**, not merely pressed.

## Procedure

1. Hold the BOOT button down.
2. Cycle power with the slide switch (off, then on) while still holding BOOT.
3. Release BOOT.
4. The device enumerates as `1A86:55E0` instead of the usual CDC COM port.

Then write the bootloader of the board in your hand, naming that board
with `-device`:

```bash
chgame-upload provision -device rev1 -bootloader <package>/bootloaders/CHGame/rev1/chgame_sdboot.bin
chgame-upload provision -device rev0 -bootloader <package>/bootloaders/CHGame/chgame_sdboot.bin
```

`chgame-upload` is the uploader the board package installs
(`Arduino15/packages/CHGame/tools/chgame-upload/<version>/`), and
`<package>` the installed package
(`Arduino15/packages/CHGame/hardware/ch32v/<version>`); Rev1's images need
0.4.0 or later. In a clone of this repository, `chgame uploader provision
...` is the Python uploader with the same verbs and flags (one dash or two),
and the images are also in `platform/bootloader/release/`:

| Board | `-device` | In the package | In the repository |
|---|---|---|---|
| CHGame Rev0 | `rev0` | `bootloaders/CHGame/` | `platform/bootloader/release/` |
| CHGame Rev1, Rev 1.5 | `rev1` | `bootloaders/CHGame/rev1/` | `platform/bootloader/release/rev1/` |

Each folder has the same five: `chgame_sdboot.bin` and
`chgame_sdboot_static.bin` (the SD Text Menu, Rainbow and Static),
`chgame_sdvisual.bin` and `chgame_sdvisual_static.bin` (the SD Graphic
Menu), and `chgame_boot_nomenu.bin` (USB Only).

**Never put one board's bootloader on the other.** Rev0's menu bootloaders
drive PB0 and PB11, which are Rev1's UP and A, and Rev1's drive PB3 and
PB4, which are Rev0's LEFT and UP: a press of that button then shorts a
driven output.

What `provision` does (chgame-upload 0.3.0):
- It reads the image's board word (offset `0x14`: 0 is rev0, `CGR1` rev1)
  and refuses an image built for another board than `-device`, before
  anything is touched. The ROM cannot tell which board it is on, so this
  checks the image against the board you name, not against the board on
  the cable.
- It refuses while wchisp sees more than one device in ISP mode: leave only
  the board to provision in ISP mode.
- It prints the chip, its UID and the image's board, and asks before
  erasing. `-yes` writes without asking.
- It erases the whole code flash, then writes and verifies the image. (An
  erase of only the bootloader's pages would leave the old sketch and its
  metadata, and the new bootloader would start that sketch.)

Then switch off and on without BOOT: the reset that ends provisioning is a
soft one. With a menu bootloader the board shows the menu; with USB Only,
or with no program installed, it waits in USB mode with the LED blinking.

**In the Arduino IDE:** pick the board (*Tools > Board*), *Tools >
Bootloader*, *Tools > Programmer > WCH factory ISP*, then *Burn
Bootloader*. It runs `chgame-upload burn -method isp -device <the board's>`,
which checks the image as `provision` does and never asks.

## Requirements on the host

`wchisp` talks to the ISP device over WinUSB, so on Windows the `1A86:55E0`
device needs the WinUSB driver bound to it (Zadig, or the WCH driver package).
**This requirement applies only to recovery and factory provisioning.** Normal
end-user flashing goes over the CHGame bootloader's own USB CDC interface, which
every OS drives with an inbox class driver and no installation at all.

The board package installs `wchisp`
(`Arduino15/packages/CHGame/tools/wchisp/<version>/`). The uploaders take
it from `-wchisp` (the IDE's recipes pass it), then `CHGAME_WCHISP`, then
the PATH.

## Verifying without flashing

```bash
wchisp probe
wchisp info
```

At a new board's bring-up, record what `wchisp info` reports (the chip, its
UID, BTVER, RDPR, WRP and RST_MOD). Nothing in this project changes an
option byte.

## Confirmed on hardware

Milestone 0 gate passed 2026-08-21 on the development board (Rev0):

```
$ wchisp probe
Found 1 devices
Device #0: CH32X035G8U6[0x5623]

$ wchisp info
Chip: CH32X035G8U6[0x5623]
Chip UID: CD-AB-88-D8-60-BE-B5-42
BTVER(bootloader ver): 02.60
RDPR 0xA5 -> Unprotected      WRP 0xFFFFFFFF -> Unprotected
RST_MOD 0b11 -> RST alternate function disabled, PA21/PC3/PB7 are GPIO
```

Note `RST_MOD`: `0b11` (the reset function off) is the reference manual's
default, and it does not matter on this package: no bonded pin of the
CH32X035G8U6 has a reset function (PA21 is not bonded, and the datasheet
gives PC3's RST to the QSOP28 and TSSOP20 packages only and PB7's to the
CH32X033), so PB7 is `BTN_SELECT` whatever it says
([hardware-pinmap.md](hardware-pinmap.md)). It is recorded, never changed.
The only ways to reset the part are the power switch and
`NVIC_SystemReset()` — which is precisely why the software boot-request path
has to be reliable.

The chip UID also explains the USB serial number seen in app mode
(`JJFFFFFFFF42B5BE60D888ABCD`): the CDC library builds it from the 96-bit UID.

## Why this path cannot be destroyed

The CH32X035 datasheet (section on memory organisation) splits flash in two:

- **62 KB Code FLASH** — the user area, everything this project writes.
- **3328 B System FLASH** — the BOOT area holding the factory ISP program.

User-area erase and program operations cannot reach the System FLASH, so no
bootloader bug, interrupted update, or corrupt image can remove the recovery
path. `wchisp erase`/`flash` likewise only touch the 62 KB user area — the run
above erased 63 sectors and left the ISP intact.

Note that `wchisp` reports "Code Flash: 64KiB" from its chip ID table. That is
the nominal part-family size; the datasheet is explicit that the G8U6 user area
is 62 KB, which is what `bootloader/src/chgame_map.h` and the stock Arduino core
linker script both assume.
