# CHGame bootloader protocol

Normative description of the wire format spoken over USB CDC between a host and
the CHGame bootloader. Three implementations must agree:

| Implementation | Location |
|---|---|
| Device (C) | `bootloader/src/proto.{h,c}` |
| Host (Go) — the board package's tool | `platform/bootloader/host/go/protocol.go` |
| Host (Python) — the repository's tools and the tests | `platform/bootloader/host/py/chgame_upload/protocol.py` |
| Host (browser, Web Serial) — the web emulator project's uploader | its own repository; it follows this document and the conventions below, and changes nothing in the bootloader |

`platform/bootloader/test/protocol/vectors.json` (written by `python -m
chgame_upload.vectors --write`) holds frames, checksums and image rules that
the Go and Python hosts are both tested against.

The browser uploader is the fourth, as this document always meant it to be.
The whole point of a small binary protocol over plain CDC is that all four
can be the same protocol: CDC is driven by an inbox class driver on every OS,
so nothing here requires a driver install, WinUSB, WebUSB or a helper
application. This document, together with `shared/chgame_usb_identity.h`
and the 1200-baud touch described under "Host conventions", is therefore a
contract with that project, like [spec/](../../../spec/README.md): a change to
any of them is made here first and told to the other side.

## Frame

```
+------+------+-----+-----+----------+---------------+--------+
| 0x43 | 0x47 | ver | cmd | len (LE) | payload[len]  | crc16  |
| 'C'  | 'G'  |  1  |     |  u16     |               |  u16   |
+------+------+-----+-----+----------+---------------+--------+
                \_______________ CRC-16/CCITT-FALSE _______/
```

- **CRC-16/CCITT-FALSE**: poly `0x1021`, init `0xFFFF`, no reflection, no final
  XOR. Computed over `ver`, `cmd`, `len` and `payload` — not over the start
  marker. Check value for `"123456789"` is `0x29B1`.
- **Maximum payload**: 512 bytes. A `WRITE` therefore carries a whole 256-byte
  flash page plus its 4-byte offset, so the device commits exactly one page per
  frame.
- Frames span several 64-byte USB packets. That is ordinary USB and works; see
  gotcha 3 in `ch32x035-gotchas.md` for why this sentence is here.

Responses echo the command with **bit 7 set** and carry a status code as
`payload[0]`.

### Framing errors

A frame that fails CRC is answered with `ERR_FRAME`. The receiver then resynchronises
by scanning for the next `'C' 'G'`.

A frame that stops arriving part-way through is abandoned after
**250 ms** (`PROTO_RX_TIMEOUT_MS`) and the parser returns to hunting for a start
marker. Without that timeout a truncated frame silently consumes the first bytes
of the next one — its length field absorbs the `'C'` — so a host that died
mid-frame poisons the first command of the next session.

## Commands

| Code | Name | Payload | Response payload |
|---|---|---|---|
| `0x01` | `HELLO` | — | status, identification (below) |
| `0x02` | `BEGIN` | `size u32`, `crc32 u32` | status |
| `0x03` | `WRITE` | `offset u32`, `data[]` | status |
| `0x04` | `END` | — | status |
| `0x05` | `RUN` | — | status, then the device launches the app |
| `0x06` | `STATUS` | — | status, progress, diagnostics (bootloader versions 1 and 2 only: `ERR_BADCMD` from version 3) |
| `0x07` | `ABORT` | — | status |
| `0x08` | `READ` | `addr u32`, `len u16` | status, `data[len]` (versions 1 and 2 only: `ERR_BADCMD` from version 3) |
| `0x40` | `DEV_UNLOCK` | `key u32` | status |
| `0x41` | `DEV_WRITE_BOOT` | `size u32`, `crc32 u32` | status, then resets |

### Bootloader versions

The `bootloader version` field of `HELLO` (`BOOT_VERSION` in `proto.h`):

| Version | Bootloader | What changed for a host |
|---|---|---|
| 1 | board package 0.2.4 (`release/0.2.4/`) | the protocol as above, `RUN` jumps to the program |
| 2 | the first SD game menu (board package 0.3.0 as staged) | `RUN` resets into the program instead of jumping; images carrying the bootloader signature (`CHBL` at offset 8) are never launched |
| 3 | menu v2 and the visual menu (2026-10-03, current) | `STATUS` and `READ` removed: `END`'s CRC check of the flash is the verification; `-verify`'s readback is "not available" |

The upload sequence (`HELLO`, `BEGIN`, `WRITE`, `END`, `RUN`, `ABORT`) is the
same in all three. A host may insist on a minimum version for reasons of its
own (the web uploader asks for 3, the version whose menu reads the card
layout its tools write); the right answer to an older one is the upgrade
procedure below, not a different protocol.

### Status codes

| Code | Name | Meaning |
|---|---|---|
| `0x00` | `OK` | |
| `0x01` | `ERR_BADCMD` | unknown command |
| `0x02` | `ERR_STATE` | not valid in the current state (e.g. `WRITE` before `BEGIN`, or a non-sequential offset) |
| `0x03` | `ERR_RANGE` | address or length outside the permitted region |
| `0x04` | `ERR_SIZE` | size rejected (zero, unaligned, too large, or a malformed payload) |
| `0x05` | `ERR_CRC` | image CRC mismatch |
| `0x06` | `ERR_FLASH` | erase or program failed, including a failed read-back |
| `0x07` | `ERR_LOCKED` | developer command without a valid unlock |
| `0x08` | `ERR_FRAME` | frame CRC mismatch |
| `0x09` | `ERR_NOTIMPL` | command recognised but not implemented |

### HELLO response

After the status byte:

| Offset | Type | Field |
|---|---|---|
| 1 | u8 | protocol version |
| 2 | u8 | mode: 1 = bootloader, 2 = application |
| 3 | u8 | application state: 0 valid, 1 no metadata, 2 bad length, 3 bad CRC |
| 4 | u16 | bootloader version |
| 6 | u32 | `APP_START` |
| 10 | u32 | `APP_MAX_SIZE` |
| 14 | u16 | flash page size |
| 16 | u16 | maximum payload |
| 18 | 12 B | chip unique ID |

A host must take the region and page size from `HELLO` rather than assuming
them. That is what lets the bootloader reservation change without every tool
needing an update.

**Mode 2 is never sent.** Applications deliberately do not implement this
protocol: a sketch owns its `Serial` stream, so a responder living in the core
would eat bytes the sketch was meant to receive and inject frames into its
output. An application is identified by being **present but silent** — a CHGame
port that does not answer `HELLO`.

## Upload sequence

```
HOST                                    BOOTLOADER

HELLO ------------------------------->
      <------------------------------- OK, region, page size, max payload

BEGIN size,crc32 -------------------->  erase metadata page FIRST,
                                        then erase the application pages
      <------------------------------- OK

WRITE offset,data -------------------->  stage, commit whole pages,
      <------------------------------- OK   read back and verify each page
   ... repeated, offsets strictly sequential ...

END ---------------------------------->  recompute CRC-32 FROM FLASH,
      <------------------------------- OK   then write the metadata page

RUN ---------------------------------->  ack, detach USB, jump to the app
```

Three properties are worth calling out because they are what make an interrupted
update safe:

1. **`BEGIN` erases the metadata page before anything else.** From that instant
   the application is marked invalid, so a power loss anywhere in the rest of the
   update leaves the bootloader in charge rather than a half-written image that
   still looks launchable.
2. **`END` computes the CRC from flash**, not from anything the device buffered.
   The only claim worth making is about what is actually stored.
3. **Validity comes from the metadata record and nothing else.** A 95%-complete
   image is refused exactly as firmly as an empty one. Verified by real power
   cuts — see the appendix in `ch32x035-gotchas.md`.

`WRITE` offsets must be strictly sequential. That is not a limitation worth
relaxing: it removes any need to track which parts of the region have been
written, makes "bytes accepted" an exact resume point, and catches a host bug
that skips or repeats a chunk immediately rather than producing an image that
fails CRC for no visible reason.

## Host conventions

What every uploader does around the frames, so that the four behave the same
on the same board. The browser uploader of the web emulator project was
checked against this list on 2026-10-06 and follows it.

**Finding the board.** VID:PID `16C0:27DD`
(`shared/chgame_usb_identity.h`). The bootloader and a sketch present the
same descriptors and the same serial number (`CG` + the chip's unique id),
so the board keeps one port across the sketch -> bootloader -> sketch
transition, and a Web Serial permission granted once stays granted. The
mode is therefore found by asking: a bootloader answers `HELLO` with mode 1;
a sketch never answers (applications do not implement this protocol).

**Entering the bootloader: the 1200-baud touch.** Open the port at 1200 baud
and drop DTR (closing the port does it). The core detects the pair in the
USB control path, so it works for any sketch, one that never touches
`Serial` or one stuck in a loop, and with both *Tools > USB* options. About
10 ms later the sketch drops the D+ pull-up and resets with the `CHGB`
request; the bootloader enumerates again under the same identity (the menu
bootloaders show their USB screen) and answers `HELLO`. The uploaders wait
up to 10 s for that. A board already in the bootloader (power-on with B
held, no valid program, the menu) needs no touch: `HELLO` first, touch only
if there is no answer.

**Ordinary connections** open at any rate but 1200, which is reserved;
115200 is the convention (the Python uploader, `tools/serialcap.py`, the
browser). The rate is ignored by the device. Assert DTR as a terminal does:
a sketch may wait for it (`Serial`'s `waitForPC()`).

**`HELLO` first.** Check mode 1, protocol version 1, a bootloader version
you accept, and take `APP_START`, `APP_MAX_SIZE`, the page size and the
maximum payload from the answer. `APP_START` must equal the load address
the image was linked for (`0x3000` for `rev0`, spec/chgame.md's device
table); refuse to upload otherwise.

**The image.** The raw `.bin` (a `.hex` or `.elf` converted on the host, as
`tools/chcart` does), padded with `0xFF` to a multiple of 4. `BEGIN` carries
the padded length and the CRC-32 (IEEE, as zlib) of the padded bytes; `END`
checks that CRC against what is in flash. The length may not exceed
`APP_MAX_SIZE` (50,944 B on `rev0`). Refuse an image carrying the
bootloader signature `0x4C424843` (`CHBL`) at offset 8 before uploading it:
the bootloader stores it but never launches it, so `RUN` would answer
`ERR_CRC`.

**The save pages.** Only the pages an upload writes are erased (no
pre-erase since version 2; version 1 erased the image's own pages twice),
and the metadata page is separate. So an image of at most 50,432 B leaves
the two shared save pages at `0xF500` and `0xF600` untouched, and a game's
save survives a detour through a utility sketch, as it does through
`CHSDtoUSB` here (43,532 B) and the website's SD-over-serial helper
(`examples/Apps/CHSDtoSerial`, 46,700 B), which it keeps under 50,432 B for
that reason. Up to 50,688 B keeps one page;
above that saving is off (spec/chgame.md `save-pages`).

**`WRITE`** in strictly sequential offsets, whole flash pages at a time
(256 B; at most `max payload - 4` bytes a frame): the device commits one
page per frame. **`END`**, then **`RUN`**: the device acknowledges, waits
60 ms, detaches and resets into the program, which enumerates again under
the same identity (the uploaders wait up to 6 s for it). On any failure
send **`ABORT`**: it erases the metadata page, so the board is left with no
valid program (it stays in the bootloader, or shows the menu, at the next
power-on) rather than a half-written one that looks launchable. A host that
dies without sending it leaves the board in the same state, since `BEGIN`
erased the metadata first.

**Bootloaders are not flashed by the web.** `DEV_UNLOCK` and
`DEV_WRITE_BOOT` are the board package's and `chgame uploader`'s business.
A bootloader a host does not support is replaced by the documented upgrade:
*Tools > Bootloader*, *Tools > Programmer* **CHGame USB**, *Tools > Burn
Bootloader* in the IDE with the 0.3.0 package, or `chgame uploader
selfupdate <bin> --yes` (README.md, "The menu bootloader"; the `locked`
build has no self-update and needs the factory ISP, `recovery.md`).

**What `HELLO` does not say.** Which face the bootloader has (the text
menu, the graphic menu, or *USB Only*, which has no card at all) and its
style: the three answer `HELLO` alike. A host that needs the card can only
find out by trying it (the web project's SD-over-serial sketch), or by
asking the user.

## Bounds checking

Every address computation is validated as `offset + len <= size` **and**
`APP_START + offset + len <= APP_END`, in unsigned arithmetic with an explicit
wrap check, before any flash is touched.

The checks are duplicated at two levels on purpose. The protocol layer checks,
and `flash.c` checks again at the point of no return — a caller bug must not be
able to erase the bootloader. `test/hil/test_protocol.py` asserts the boot region
is byte-identical after every malformed frame, bad CRC, overrun attempt, aborted
transaction and locked developer command it can throw at the device.

## Developer commands

`DEV_UNLOCK` and `DEV_WRITE_BOOT` let the bootloader replace itself over USB,
which turns a bootloader iteration from a physical BOOT-button-plus-power-cycle
into a single command. The new image is first staged through the **ordinary**
upload path into the application region — so it gets the same bounds checking,
per-page verification and CRC as any firmware — and only then promoted.

The unlock key is an interlock against **accidents**, not a security control.
It is plainly visible in the binary to anyone who cares to look, and that is
fine: the threat being managed is "an upload tool bug bricks the bootloader",
not "an attacker with physical USB access". Do not describe it as protection.

The whole facility compiles out when `CHGAME_ALLOW_SELFUPDATE` is 0, which is
what a shipping build should do.

There is an unavoidable window, roughly the erase-and-program time of the boot
region, in which a power loss leaves the device with no usable bootloader. That
is recoverable exactly one way: the BOOT button and the factory ISP. It is why
that path must never be compromised.
