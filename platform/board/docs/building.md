# Building and releasing

Everything here runs from the repository root, in Python, on Windows, Linux
or macOS. The only shell script left is the bootloader's own build.

## Prerequisites

| Tool | Needed for | Notes |
|---|---|---|
| Python 3.10+ | every tool: `pip install -e .[sim]` (the `chgame` command, Pillow, pyserial, zig for the simulator) | `tools/requirements.txt` lists the same packages for a plain install |
| Go 1.25+ | rebuilding `chgame-upload`, the Go uploader the board package installs | not needed to use the board, nor for the Python uploader |
| RISC-V GCC (`riscv-none-embed-gcc` 8.2.0) | the bootloader | the board package installs one (`Arduino15/packages/CHGame/tools/riscv-none-embed-gcc/8.2.0`) |
| `arduino-cli` | compiling sketches, verifying a release | |
| `gh` | publishing a release | `gh auth login` once |
| `wchisp` | first flash and recovery through the factory ISP | installed by the board package |
| Git Bash (Windows) | `platform/bootloader/build.sh` only | the release script does not call it |

## The bootloader

```bash
platform/bootloader/build.sh [release|locked|nomenu|app]    # -> platform/bootloader/build/
python3 platform/bootloader/test/native/run_tests.py         # the PC suite (flash/SD/panel models, power cuts, menu frames)
platform/bootloader/tools/dist.sh                            # refresh release/ (+ SHA256SUMS) and bootloaders/CHGame/
```

`dist.sh` copies the binaries into
`platform/board/arduino/CHGame/bootloaders/CHGame/`, where the board
package carries them (*Tools > Bootloader*). The release script does not
build the bootloader: it checks that the committed binaries match
`platform/bootloader/release/SHA256SUMS` and refuses otherwise.

The layout has one source of truth, `platform/bootloader/src/chgame_map.h`.
`host/py/chgame_upload/layout.py` mirrors it for the uploader, which ships
without the header; `test/protocol/test_layout.py` holds the two together.

## The uploader

There are two implementations of the host side of the bootloader protocol
([protocol.md](protocol.md)), with the same verbs and flags:

- **Go, `chgame-upload`** (`platform/bootloader/host/go`): the executable
  the board package installs as an Arduino tool, because Arduino provides no
  interpreter. Built for the five hosts Arduino supports:

  ```bash
  python tools/release/build_uploader.py                    # -> out/chgame-upload/<host>/chgame-upload[.exe]
  python tools/release/build_uploader.py --host x86_64-mingw32
  ```

  | Arduino host | System |
  |---|---|
  | `x86_64-mingw32` | Windows |
  | `x86_64-pc-linux-gnu` | Linux, Intel/AMD |
  | `aarch64-linux-gnu` | Linux, ARM 64-bit |
  | `x86_64-apple-darwin` | macOS, Intel |
  | `arm64-apple-darwin` | macOS, Apple silicon |

  Go comes from `$CHGAME_GO`, a toolchain unpacked in `.toolchains/go` at
  the repository root (gitignored), or the PATH. Cross-compiled from one
  machine with cgo off.

- **Python, `chgame_upload`** (`platform/bootloader/host/py`): what every
  tool in this repository calls (`chgame upload`, `chgame uploader ...`) and
  what the bootloader's hardware tests drive. `python -m chgame_upload probe`
  from that folder; `pip install -e platform/bootloader/host/py` adds a
  `chgame-upload` command of its own. It accepts the Go spellings of the
  flags (`-port`, `-run`), so `platform.txt`'s recipes run unchanged
  against either.

**Parity.** `platform/bootloader/test/protocol/vectors.json` holds the
frames, checksums, HELLO parse, chunking, image rules and layout that both
must compute, written by the Python package:

```bash
python -m unittest discover -s platform/bootloader/test/protocol        # Python: the vectors, the layout, the CLI, uploads against a fake bootloader
cd platform/bootloader/host/go && go test ./...                          # Go: the same vectors
python -m chgame_upload.vectors --write platform/bootloader/test/protocol/vectors.json   # after a protocol change (and update protocol.md)
python platform/bootloader/test/hil/test_parity.py [--image x.bin]      # both tools against a board
```

The release script runs the first two. The version is `version` in
`host/go/main.go` and `__version__` in `host/py/chgame_upload/__init__.py`;
the tests refuse a mismatch.

## The Python tools

`pip install -e .[sim]` in the repository root installs the `chgame`
command and the packages the tools need, in one environment. `tools/README.md`
describes every tool; `CLAUDE.md` has the commands.

## Releasing

The version is the `version=` line in
`platform/board/arduino/CHGame/platform.txt`. That is the number Boards
Manager compares with what a user has installed to decide whether to offer
an update, so every release bumps it, and the release script refuses a
version that does not match it. The platform and the uploader are versioned
apart: `chgame-upload`'s version only moves when `host/go` changes behaviour.
The next release is platform **0.3.0** with `chgame-upload` **0.2.0** (the
0.1.0 tool that 0.2.4 installs has no `burn` command).

1. Bump `version=` in `platform.txt`.
2. Retitle the `## Unreleased` (or `## <version> (not yet released)`)
   section of `platform/board/CHANGELOG.md` to `## <version> (<date>)`. The
   script uses it as the GitHub release notes, refuses to run without it,
   and refuses to publish while it says "not yet released".
3. If the bootloader changed: `build.sh` and `tools/dist.sh`, commit.
4. Commit and push. The release tag is created on GitHub at the pushed
   `main`, so the script also refuses a dirty tree or an unpushed `HEAD`.
5. `python tools/release/release.py --dry-run`: builds everything into
   `out/dist/` and publishes nothing. Look at the asset table and the ten
   largest files of the archive. It also runs the new-user test against
   what it built (below, *Staging and the new-user test*) and makes the
   casino cart and the SD card from it; `--no-accept` skips that, for a dry
   run only.
6. `python tools/release/release.py` (`--repo bateske/CHGame` is the
   default).
7. Commit `tools/release/chgame_upload_tool.json`, which now points at the
   new tag, and `git fetch --tags`.

The steps the script runs, for doing them by hand:

```bash
python -m unittest discover -s platform/bootloader/test/protocol
(cd platform/bootloader/host/go && go test ./...)
python tools/release/build_uploader.py
python tools/release/make_tool_archives.py --base-url https://github.com/bateske/CHGame/releases/download/v<version>
python tools/release/make_package.py --base-url https://github.com/bateske/CHGame/releases/download/v<version>
```

They produce, in `out/dist/`:

- `CHGame-ch32v-<version>.tar.bz2`, the platform archive;
- `chgame-upload-<toolversion>-<host>.tar.bz2`, one per host;
- `package_chgame_index.json`, the Boards Manager index;
- `CHGame-Casino-<version>.chgame`, every game and app as one cart (the
  format games are shared in: spec/chgame.md), built by the new-user test
  from the installed package's own examples (tools/sdcard/casino.json);
- `CHGame-sdcard-<version>.zip`, that cart's SD card (spec/card.md: the
  `GAMES` folder with the CHG files, the menu's order and background, and
  the games' data files);
- `release-notes-<version>.md`.

All of them go to a GitHub release tagged `v<version>` (the script uploads
them). The index references the archives by URL with pinned SHA-256
checksums, so they must land exactly where `--base-url` says: GitHub release
assets are flat, so the URL is the base plus the file name. The archives
are reproducible (sorted members, no owner, the HEAD commit's time as the
one timestamp), so rebuilding from the same tree gives the same checksums.

Publish it as a normal release, never a pre-release: the README points
users at `/releases/latest/download/package_chgame_index.json`, and that
alias skips pre-releases. Once the release is up, the Arduino IDE offers
the new version in Boards Manager the next time it refreshes its indexes.
The script also re-uploads the new index to every earlier `v*` release, so
someone who added an explicit version URL instead of `latest` is offered
the update as well.

### What the index contains

One packager, `CHGame`, carrying three tools, so that a single Boards
Manager URL installs everything:

| Tool | Where its definition comes from |
|---|---|
| `riscv-none-embed-gcc` 8.2.0 | `tools/release/tool_defs/riscv-none-embed-gcc.json`: the upstream CH32 index's entry, verbatim (same binaries, already proven) |
| `wchisp` 0.3.0 | `tools/release/tool_defs/wchisp.json`: the upstream GitHub release assets, checksums pinned |
| `chgame-upload` | `tools/release/chgame_upload_tool.json`, written by `make_tool_archives.py` |

The two vendored definitions were taken once from an installed index
(`make_package.py --import-tool-defs`); a release needs no installed core.
Two hosting caveats: the wchisp and toolchain entries reference somebody
else's release assets, so availability is not guaranteed. Mirroring them
into this repository's releases would make installs reproducible; wchisp is
GPL-2.0, so mirroring it means shipping its licence and a source offer
(`platform/board/THIRD-PARTY.md`).

### What the platform archive contains

Every file git tracks under `platform/board/arduino/CHGame`: the core, the
variant, the bootloaders, `boards.txt`/`platform.txt`, and the `libraries/`
folder with CHGfx, CHSd and CHGame, whose examples are the twenty games
whole (their `tools/`, art, `sdcard/` data and README GIFs included: the
IDE's *File > Examples* copies a sketch's whole folder). The excludes are
the visible constants in `tools/release/_common.py`
(`PACKAGE_EXCLUDE_NAMES`, `_DIRS`, `_SUFFIXES`: `.gitignore`,
`platform.local.txt`, `build/`, `out/`, `probes/`, `__pycache__`, `.pyc`);
the packager refuses any path that still has a build folder in it, and any
sketch inside another example's folder (*File > Examples* would show it
nested in that example: that is why CHBlackjack's `tools/probes/FlashProbe`
is left out), and prints the file count and the ten largest files, so a
regression shows in the dry run. The GIFs are the bulk of it (about 17 MB of ~25); dropping them is one
name in `PACKAGE_EXCLUDE_NAMES`, at the price of the READMEs' pictures
inside the IDE's copy.

### Staging and the new-user test

```bash
python tools/release/stage.py [--quick] [--serve]     # build 0.3.0-local into out/stage/, test it as a new user
python tools/release/serve.py [--dist out/stage]     # serve it to the Arduino IDE on localhost:8765
python tools/release/acceptance.py [--dist out/dist] [--all] [--card x.zip]   # the test on its own
```

`stage.py` builds what `release.py` builds, versioned `<version>-local`
(the uploader `<tool version>-local`), with every URL on
`http://localhost:8765`, and runs `acceptance.py` on it. The pre-release
version sorts before the release, so a staged install is offered the
release as an update, and the uploader is downloaded again then.

`acceptance.py` serves the folder (`serve.py` points the index's own URLs
at itself, so an `out/dist/` built for GitHub serves the same, with the
same checksums) and installs it with a fresh `arduino-cli` whose data
folder, sketchbook and config are in `out/newuser/`. It checks the three
tools, the platform libraries, the examples under *File > Examples*, the
*Bootloader* and *Programmer* menus and the bootloader files, then copies
examples into the sketchbook and compiles them with plain `arduino-cli
compile`: Hello and CHChess with the IDE's default options, CHFour and
CHWords with the release options, CHWords with the defaults (it must stop
with its "needs Tools > USB > Upload only" message), and *Export Compiled
Binary* must leave a `.bin` and a valid `.chg`. `--all` compiles every
game and app from the installed package, and `--card` makes the casino
cart from those builds and packs its SD card. It touches no board.
[trying-a-release.md](trying-a-release.md) is the same by hand, in the IDE,
with a board.

The toolchain archive is kept in `out/arduino-downloads/` between runs;
the package's own archives there are deleted before each install, since
they change between builds of the same version.

### Traps when publishing

- **`/releases/latest/` skips pre-releases.** A release marked pre-release
  is not reachable through the `latest` alias at all: the URL 404s.
- **arduino-cli caches the index.** If a previous index was fetched from a
  different URL, `core update-index` can quietly keep serving the cached
  copy. Delete `Arduino15/package_chgame_index.json` before testing a new
  one (`%LOCALAPPDATA%\Arduino15` on Windows, `~/.arduino15` on Linux,
  `~/Library/Arduino15` on macOS).
- **A tool at the same version is not re-downloaded.** Bump the tool's
  version, or delete `Arduino15/packages/CHGame/tools/chgame-upload/<version>`.
- **`platform.local.txt`** in an installed package overrides the released
  `platform.txt`; it is never packaged, but it is easy to forget it is there.

### Verifying a release

```bash
arduino-cli core uninstall CHGame:ch32v
rm -rf "$ARDUINO15/packages/CHGame"
arduino-cli core update-index --additional-urls https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json
arduino-cli core install CHGame:ch32v --additional-urls https://github.com/bateske/CHGame/releases/latest/download/package_chgame_index.json
arduino-cli compile -b CHGame:ch32v:rev0 -u -p <port> platform/board/arduino/CHGame/libraries/CHGame/examples/Hello
arduino-cli burn-bootloader -b CHGame:ch32v:rev0 -P chgameusb -p <port>
```

The compile line has no `--library`: the package must deliver the
libraries itself (the roadmap's acceptance test). Removing the package
directory matters: `arduino-cli` will not re-download a tool it already has
at the same version, so an in-place upgrade can silently test a stale
binary.

## Hardware tests

```bash
python platform/bootloader/test/hil/test_protocol.py           # 27 protocol and flash-safety checks
python platform/bootloader/test/hil/test_soak.py --cycles 100  # unattended, ~5 minutes
python platform/bootloader/test/hil/test_powercut.py arm --hold-at 95
python platform/bootloader/test/hil/test_powercut.py verify    # after restoring power
python platform/bootloader/test/hil/test_parity.py             # the Go and Python uploaders agree
```

The soak alternates between two different images deliberately: uploading
the same bytes repeatedly would pass even if the device quietly ignored the
write and kept running the previous sketch. The power-cut test is the one
thing that cannot be automated here: only physically removing power can
interrupt a flash page mid-program.
