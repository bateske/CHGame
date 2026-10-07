# SDtoSerial (CHSDWeb) transfer protocol v1

This is a dedicated browser-transfer variant of CHSDtoUSB. The original sketch and separate CHGame checkout remain intact. It reuses the pinned sketch's Sd2Card driver (GPL-3.0-or-later) and CRC/retry behavior, with the CHGame Arduino core's buffered CDC transport. It contains no MSC descriptors, so the OS cannot mount the card while this helper owns it.

FatFs R0.16 is vendored from https://elm-chan.org/fsw/ff/arc/ff16.zip (SHA256 `99f7dc1f7e095356e4a9e3dbe29959090d8b948afe2bbc5441e52fdf4b85449e`). Configuration: FAT16/FAT32 accepted on mount; one 512-byte-sector volume; short filenames; tiny shared sector buffer; no formatting, exFAT, long-name creation, RTC, or dynamic filesystem buffers. FatFs's own notice is in CHSDWeb/FatFs-LICENSE.txt. Driver/application GPL text is in CHSDWeb/LICENSE.

## Frames

Little endian. `43 53` (CS), version `01`, command u8, payload length u16, payload, CRC16 u16. CRC16/CCITT-FALSE covers version through payload, initial FFFF, polynomial 1021. Payload is at most 512 bytes. Request payload starts with a nonzero u32 request ID. Response command is request command OR 80h; payload is request ID, status u8, response bytes.

Stop-and-wait. An exact duplicate of the most recent request replays its cached response without executing it again; reuse of that ID with changed content and older requests return status 32. HELLO establishes a new request sequence after reconnection. A partial frame expires after one second. Noise and bad CRC frames are discarded. The browser retries a timed-out request with the same ID, at most twice. Request IDs belong to the SerialLink connection, not a FileClient; reconnect HELLO and subsequent installer clients share its monotonically increasing sequence.

Paths are NUL-terminated uppercase ASCII 8.3 components, no leading slash, at most 120 characters. `_CHWEB` is reserved for internal recovery. The root is an empty path, accepted by LIST only. The browser rejects carts exceeding this helper's path limit before transferring files. Long paths remain valid cart data for emulator/SD ZIP use.

| Command | Request after ID | Response after status |
|---|---|---|
| 1 HELLO | empty | protocol u8, recovered u8, capacity sectors u32, free sectors u32, max payload u16, max path u16 |
| 2 STAT | path | size u32, reserved u32, directory u8, CHG title 32 bytes (empty for other files) |
| 3 LIST | index u32, directory path | size u32, directory u8, name bytes; empty means end |
| 4 MKDIR | path | empty; existing directory succeeds |
| 5 BEGIN | size u32, whole-file CRC32 u32, path | empty |
| 6 WRITE | offset u32, data | empty; exact sequential offset required |
| 7 COMMIT | empty | empty after full CRC readback, journaled replacement, and synchronization |
| 8 ABORT | empty | closes/removes uncommitted staging; published replacements remain |
| 9 SYNC | empty | empty after the card's writes are complete |
| 10 MENU | empty | sync, acknowledgment, then software reset to hardware menu |
| 11 CHECK | offset u32, running CRC32 u32, path | next offset u32, running CRC32 u32, EOF u8; reads at most 16 KiB |
| 12 READ | offset u32, requested count u16, path | offset u32, data CRC32 u32, EOF u8, up to 480 data bytes |
| 13 CAPS | empty | extension version u8 = 1, feature bits u8 (bit 0: bounded reads, bit 1: stack watermark, bit 2: removal, bit 3: host progress), max read bytes u16 = 480; stack-free watermark u16 and reserved stack bytes u16 |
| 14 REMOVE | path | empty; nonrecursive, restricted to descendants of GAMES, absent files succeed |
| 15 PROGRESS | completed bytes u32, total bytes u32, estimated seconds remaining u32, mode u8 | empty; mode 1 read, 2 write, 0 complete; display-only, no SD access |
| 16 IDENTITY | empty | ASCII `SDtoSerial/1`; available even when SD initialization failed or the last operation was cancelled |

On explicit SD access the browser probes IDENTITY before offering installation. Older helpers can be recognized by HELLO. A recognized helper's card error is surfaced without offering to replace device memory. Idle auto-connect never probes or resets the application. Only a missing helper triggers the warning that installation will erase the current game in device memory. Writes have a separate SD-file review.

CRC32 is reflected IEEE, polynomial EDB88320, initial FFFFFFFF, final XOR FFFFFFFF. CHECK exchanges the unfinalized running state. It keeps large file inspections bounded and responsive. COMMIT may take longer for large files; cancellation waits for the active operation.

The disk adapter writes each sector with CMD24, sends its CRC16, waits for the card to leave its busy state, and checks CMD13 status. It avoids the driver's ACMD23 pre-erase/CMD25 path, which produced intermittent errors on the physical qualification card. Reads use a bounded 512-byte buffer and checked SD transfers.

Status 0 succeeds; 1–19 are FatFs FRESULT values, including 1 disk I/O, 4 missing file, 5 missing path, 7 denied/full/read-only, 10 write protected, 13 unsupported filesystem. 32 is malformed request/path/offset; 33 busy; 34 CRC mismatch; 35 recovery required; 36 cancelled on the console. Error replies additionally carry the last I/O operation u8 (1 read/2 write), SD driver error u8 and sector u32. These are diagnostics, not authorization to retry destructive operations blindly.

## Replacement and recovery

Only one file is staged at a time in `_CHWEB/NEW.TMP`. BEGIN reserves no published filename and checks available staging space. COMMIT synchronizes and reads back the stage, then writes/synchronizes a CRC-protected `_CHWEB/TXN.DAT` journal. An old destination moves to `OLD.BAK`; the verified stage moves into place and is checked again. Only then are backup and journal removed.

At startup a valid journal rolls forward a verified stage/new destination, or restores a surviving backup when needed. An invalid/torn journal or ambiguous state stops writes and retains recoverable files. An orphan stage with no journal is discarded. No whole-cart or FAT-volume power-loss atomicity is claimed. Back up the card before qualification tests. If automatic recovery refuses: use a card reader to back up the entire card including `_CHWEB`, inspect the journal/old/staged files, and recover deliberately. Never erase `_CHWEB` just to suppress the error.

The installer does not clean/format cards. A single game preserves existing menu files and replaces a same-title CHG under its old name. Multi-game carts publish generated menu files while retaining unrelated files. Indexes are published last, deepest first and root last. Every transferred file is CRC checked again from the browser before final synchronization.

Device-editor changes are staged in browser memory until Update Device. Removal unlists the game and deletes only its CHG, preserving resource files whose ownership is unknown. A folder move copies and verifies every contained file, publishes revised indexes, then removes the old files and empty directories. The browser refuses changed source indexes and insufficient staging space. These multi-file edits are not atomic: interruption can leave duplicate copies or a partly published menu, requiring a rescan. REMOVE never recursively erases directories or accesses files outside GAMES.

The browser reports byte progress and measured-throughput estimates through PROGRESS, at most twice a second except final updates. SDtoSerial shows it as the top gauge (lime writing, mint reading) and as "LEFT m:ss" on the totals line, and COMPLETE once the final update says so. Estimates exclude unknown card stalls and do not promise completion time; folder moves include a read/copy stage and verified writes. Deep scans read bounded game headers/artwork sequentially and never implicitly recover full executable files.

## Build

Install the pinned CHGame board package source and its `riscv-none-embed-gcc` 8.2.0 toolchain in an isolated Arduino data directory. Set `ARDUINO_CLI` and `ARDUINO_CONFIG` if their paths differ from this workspace's defaults.

```sh
node scripts/build-helper.mjs
```

The same build from this folder, with its size and RAM report: `python tools/build.py` (the pinned package found in `../CH32EMU/.tools`). The screen on a PC, old and new side by side: `python harness/run.py` (harness/README.md).

The script compiles `CHGame:ch32v:rev0:usb=serial` and disables only the optional post-build `.chg` packaging hook (the helper is uploaded as raw binary). It rejects a binary over 50,432 bytes and records its size/hash in `web/device/helper.json`. Both save pages remain outside the helper image. The build uses `GFX_CHUNK_ROWS=1` to bound LCD DMA scratch space. Matching source, configuration, source pin, licenses and compiler settings accompany the static package.

## Qualification

`web/device-release.json` is fail-closed. Production requires `qualified`, a hardware evidence record, and a `helperSha256` exactly matching the current helper manifest. The uploader checks this hash again before flashing; rebuilding firmware cannot silently inherit an older qualification. Neither a URL parameter nor a remote message can enable production device access. For local supervised testing only, run `CHGAME_DEVICE_TEST=1 PORT=8082 node scripts/serve.mjs` and visit `/hardware-test.html#device`; this route is generated only by the loopback-bound development server and is not part of the static distribution.

`scripts/hardware-test.mjs COM8 --approved-test-card` and `hardware-stress.mjs` are explicitly invoked test adapters, not production uploaders. They share the browser's framing, uploader and file client. They use pyserial solely to drive the physical device outside a browser. Passing these tests does not substitute for testing the browser's port chooser/re-enumeration, physical game playback, or interruption during replacement.


## Console controls and display

The LCD is CHSDtoUSB's instrument panel in the CHGame library's "secret agent" style (its Agent.h, carried here unchanged), in the website's palette: its dark glass, lime, grey-greens and coral, widened to sixteen colours. Across the top a status bar names what the helper is doing (STANDBY, SCANNING, WRITING, READING, VERIFY, COMPLETE, READY, STOPPING, STOPPED, ERROR, or the card's trouble: NO CARD, NOT FAT, RECOVERY) beside a seven-segment readout of the link's file-data rate in KB/s (gold: the card reading itself back). Under it a two-pixel gauge: the website's whole-job progress (PROGRESS), else the file being received, else how full the card is. The graph holds one column per 125 ms of traffic, auto-ranged from 16 KB/s to 1 MB/s: lime for data to the card, mint for data to the website, solid gold where the card reads itself back (verifying), a tick for commands that move no file data, coral where an answer was an error or a frame was replayed, with a mark for each event; the strip under it colours what every slice carried; the totals line gives bytes in and out and the busy percentage, or the website's "LEFT m:ss" estimate while PROGRESS runs. While no website has called, or a website has said nothing for a minute, the graph's place is taken by the scope: a sweep going round, contacts drifting through and lighting as it passes, a scanner running along the gauge row, the time waited, "SEARCHING FOR HOST..." (or "WAITING FOR HOST..."), and under it, in place of the pages, a large PRESS A in the banner's lettering, FOR QR CODE, PLAY.CHGAME.WEBSITE. A then fills the screen with the website's QR code (`https://play.chgame.website`, version 2, from `CHSDWeb/Qr.h`, made by `tools/qr.py`) for a phone; A or B again, or any d-pad key, puts it away, and so does the website's HELLO. The QR code is also one key away while stopped or while the card has trouble. A contact comes by every two or three seconds, now and then two: plain pings, and between a handful of those one of something sillier, in turn (an airplane, a boat, a rocket, a rabbit, a banana: `CHSDWeb/Shapes.h`, from `tools/shapes.py`). The Konami code on the scope (up up down down left right left right A B) jams it: grape jelly oozes down over the whole screen under WE'VE BEEN JAMMED!, and once it is covered it waits for a key, then the show starts over with the opening sweep. The readouts stop at 99:59, 99999 sweeps and 9,999,999 seconds, each turning rainbow at its limit (`UI_LONG_WAIT 0` leaves that out). Any command from the website ends all of that at once. The panel below has three pages, LEFT/RIGHT: EVENTS (the last eight events by file name, with live progress; UP/DOWN scrolls), STATS (bytes, files, peaks, commands, duplicates replayed, frames dropped, failures, the stack's low-water mark) and CARD (size, free space, journal state, staging, limits, the last error). The bottom row names the keys. Banners (the CHGame library's Sizzle lettering in the house gradient, dancing in over the graph; `UI_SIZZLE=0` builds the screen's own outlined banner instead and saves about 1 KB of flash and 400 B of RAM) announce LINKED, RECOVERED, CRC ERROR and FAILED; short beeps mark files, the card, the website, a cancel, the job's end and the exit.

The job's end is marked: the status word reads COMPLETE once the website has said SYNC after installing, removing or reading files (or sent a PROGRESS of mode 0), IDLE after ten quiet seconds otherwise. If the website then stays quiet for a second, a COMPLETE card takes the graph's place for five seconds (files, bytes, time, the average rate, VERIFIED CRC OK) with a four-note jingle and a blink of the LED; if MENU comes instead, the goodbye screen carries the same stamp and the sketch waits 1.4 s instead of its usual 100 ms before resetting, so it can be read (the MENU answer itself is not delayed).

Updates are synchronous and throttled: at most five frames a second while commands stream (and between the blocks of a long COMMIT or CHECK, after the SD read has released SPI), 25 while a banner, the opening sweep or the exit countdown animates, none while nothing changes; every flush blocks, so the card always finds SPI1 idle; a frame holds the link up by its drawing and a flush of about 5 ms (the top part alone) to 8.4 ms. Nothing on the screen changes an answer: the display hooks only watch (Display.h), and `harness/run.py`'s compatibility session sends the original firmware and this one the same bytes and demands identical answers and card images.

B requests cancellation: the current command finishes, staging is aborted, and the card is synchronized before subsequent transfer commands receive status 36 (STOPPING, then STOPPED on the screen; before any website has called there is nothing to stop and the search simply goes on). HELLO begins a new interaction. START held for three seconds requests a safe return to the bootloader. During the hold an EXIT? box with a countdown replaces the graph (coral, with TRANSFER ACTIVE!, while files are open); the LED blinks and short tones sound. Releasing START before the threshold keeps the helper running. Neither control interrupts a journaled COMMIT. Long readback loops poll controls only after their SD read releases SPI; the pending action is performed at the command boundary. B leaves errors visible for recovery. An explicit three-second START hold may still return to the menu after a failed abort/sync or absent card; journal/stage files remain intact for recovery on the next helper start. The reset occurs only after the current operation has returned, with a MENU screen and a jingle first.

READ rejects writes-in-progress, out-of-range offsets and counts over the negotiated bound. Exact duplicates replay cached bytes. The browser verifies frame CRC, offset, length, per-chunk CRC32, final size and EOF; cancellation happens between chunks. Card recovery is reconstruction from available CHG/menu/picture files, not retrieval of an original .chgame archive. Missing descriptions/licences are not invented, and additional SD asset ownership requires user selection.
