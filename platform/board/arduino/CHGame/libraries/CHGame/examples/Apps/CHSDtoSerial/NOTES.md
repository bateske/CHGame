# CHSDtoSerial: notes

For anyone changing the helper. The README says what it is; PROTOCOL.md is
the contract with the website.

## Where it came from

The `SDtoSerial` project (`D:\LocalProjects\SDtoSerial`), a CDC-only variant
of CHSDtoUSB written for the CHGame website. There the sketch lived in
`CHSDWeb/` with a PC harness (`harness/`) that built two copies of it and
drove them over the serial protocol: the frozen original firmware and the
rewritten screen, byte for byte, to prove the screen rewrite changed no
answer. It was brought into the board package on 2026-10-06 as
`examples/Apps/CHSDtoSerial`:

| Then (`SDtoSerial/CHSDWeb`) | Now |
|---|---|
| `CHSDWeb.ino` | `CHSDtoSerial.ino`, using `Serial` directly as before; the save magic / debug id rules got it `config.h`'s `CHSS_VERSION` and the `CHSS` debug id (it saves nothing and has no board debug build) |
| its own `tools/build.py` (the website's build-helper flags) | the repository's `chgame build`; `tools/game.py` pins `usb=serial` and `GFX_CHUNK_ROWS=1` |
| `tools/qr.py`, `tools/shapes.py` wrote `CHSDWeb/Qr.h`, `Shapes.h` | the same, writing beside the sketch |
| `Agent.h/.cpp`, `Sd2Card*`, `Sd2PinMap.h`, `SdInfo.h`, `LICENSE` | identical to CHSDtoUSB's (the shared secret-agent chrome and SD driver); `Sd2Card.cpp` keeps its one CHSDWeb change (CMD24 with the card's CRC for single FAT sectors) |

`Agent.h/.cpp` is the same file in CHSDtoUSB and CHStlView: change all three.

## Not in the repository's simulator

The sketch was developed and driven on a PC in the `SDtoSerial` project's own
harness (it plays a pretend website against a card image in RAM) and has run
on the board as the website's live helper. It is **not** wired into this
repository's simulator (`tools/chsim`), so `chgame check` for it builds the
board image and no more: there are no scripts in `tools/scripts`, and the
simulator host shims that would let the pretend website drive it here were
not ported. Wiring it in would mean a `tools/chsim/host/` with the serial
link and the RAM card (the harness's `disk_host.c` is a starting point) and a
session writer like the harness's `run.py`. The website's own browser tests
are the live check on hardware.

Because the USB serial port is the protocol, there is no `CHGAME_DEBUG` build
for the board (it would want the same port); the sketch `#error`s on one, the
same guard CHSDtoUSB carries.

## Sizes (release FQBN with `GFX_CHUNK_ROWS=1`, 2026-10-06)

| | Flash | Static RAM |
|---|---|---|
| CHSDtoSerial | 46,700 B of 50,944 | 17,368 B of 18,416 |

Both save pages (≤ 50,432 B) stay free, so a game's save survives a trip
through the helper, as it does through CHSDtoUSB. `docs/upstream-chgame.md` in
the `SDtoSerial` project lists what the CHGame library could change so this
app (and any other) would spend less SRAM on copies of library inner loops it
does not need to be fast.

## The protocol is a contract

`CHSDtoSerial.ino` and `transfer.c` are byte for byte what the website
qualified against. The upload protocol is separate and unchanged (the web
project's browser uploader is its fourth implementation:
[protocol.md](../../../../../../../../../platform/board/docs/protocol.md),
"Host conventions"). Change either only with its spec and the browser side.
