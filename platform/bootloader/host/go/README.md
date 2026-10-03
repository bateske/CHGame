# chgame-upload

The uploader the board package installs: one program with nothing to install
beside it, built for every computer Arduino runs on. The Arduino IDE and
`arduino-cli` run it for *Upload*, *Burn Bootloader* and *Upload Using
Programmer* (`platform/board/arduino/CHGame/platform.txt`); it can also be
run by hand.

```
chgame-upload probe                      list the boards and what each is running
chgame-upload info                       the bootloader's version and memory map
chgame-upload flash game.bin -run        upload a sketch (what Upload does)
chgame-upload selfupdate boot.bin        replace the bootloader over USB
chgame-upload provision -bootloader boot.bin [-app game.bin]
                                         write through the factory ISP (hold BOOT, power cycle)
chgame-upload burn -method usb|isp -bootloader boot.bin [-app game.bin]
                                         what Burn Bootloader runs: selfupdate or provision
```

`-port <PORT>` picks a board; without it the tool looks for USB `16C0:27DD`.

## Replacing the bootloader over USB

`selfupdate` (and `burn -method usb`) goes through the bootloader that is
already on the board, so it needs no driver and no button:

1. It refuses an image that is not a bootloader for this board (too large,
   or linked for the sketch's address).
2. It restarts the board into its bootloader, unlocks the update commands
   and stages the new image in the sketch's flash, checked like any upload.
3. The board checks the staged copy again, copies it over the boot region
   and resets. The tool waits for it and reports the version now running.

The installed sketch is erased (its flash is the staging area); with
`-app`, the sketch is uploaded afterwards. If the power goes during the
copy in step 3, about a second, the board needs the factory ISP
([recovery](../../../board/docs/recovery.md)). A `locked` bootloader build
refuses the update, and then the factory ISP is the only way.

Tried on a board on 2026-10-02 through `arduino-cli burn-bootloader`: SD
menu to classic 0.2.4, classic to no-menu, no-menu to classic, classic to SD
menu, then *Upload Using Programmer* and a normal upload.

## Building

```bash
python tools/release/build_uploader.py     # needs Go 1.25 or later; writes out/chgame-upload/<host>/ at the repository root
go test ./...                              # against test/protocol/vectors.json, shared with the Python uploader
```

It cross-compiles all five hosts from one machine, with cgo off:

| Arduino host | System |
|---|---|
| `x86_64-mingw32` | Windows |
| `x86_64-pc-linux-gnu` | Linux, Intel/AMD |
| `aarch64-linux-gnu` | Linux, ARM 64-bit |
| `x86_64-apple-darwin` | macOS, Intel |
| `arm64-apple-darwin` | macOS, Apple silicon |

On Linux the user must be allowed to open the serial port (usually the
`dialout` group). On macOS, finding the board without `-port` goes by the
device name (`/dev/cu.usbmodem*`), since the USB lookup would need cgo;
Arduino always passes the port.

## Files

| | |
|---|---|
| `main.go` | the commands |
| `client.go` | the serial port, the 1200-baud touch, waiting for the board |
| `protocol.go` | the frame format and HELLO (`platform/board/docs/protocol.md`) |
| `upload.go` | upload, the bootloader update, the factory ISP image and `wchisp` |
| `ports_usb.go`, `ports_darwin.go` | finding the board |

`../py` (the package `chgame_upload`) is the same tool in Python, with the
same verbs and flags: what the repository's tools and the bootloader's
hardware tests use. `protocol_test.go` and `upload_test.go` check this tool
against `../../test/protocol/vectors.json`, which the Python package
writes, so the two cannot drift apart. The version is `version` in
`main.go` (and `__version__` in the Python package; the tests refuse a
mismatch); the board package's index names the version it installs.

It came from CH32SerialBoot v0.2.4 (`host/go`, tool version 0.1.0). Changed
here: `selfupdate` and `burn` (0.2.0). MIT licence, as the bootloader
([../../LICENSE](../../LICENSE)); `go.bug.st/serial` is BSD-3-Clause
([../../THIRD-PARTY.md](../../THIRD-PARTY.md)).
