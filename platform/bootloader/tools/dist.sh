#!/usr/bin/env bash
# Build every variant and refresh release/ (the binaries committed for
# flashing without a toolchain) and its SHA256SUMS.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
for m in release locked nomenu app "release --style=static" "release --ui=visual"          "release --ui=visual --style=static" "app --ui=visual"; do
  log="build-${m// /_}.log"; log="${log//--style=/}"; log="${log//--ui=/}"
  ./build.sh $m > "$log" 2>&1 || { cat "$log"; exit 1; }; rm "$log"
done
mkdir -p release
cp build/release/chgame_boot.bin release/chgame_sdboot.bin
cp build/release-static/chgame_boot.bin release/chgame_sdboot_static.bin
cp build/locked/chgame_boot.bin  release/chgame_sdboot_locked.bin
cp build/nomenu/chgame_boot.bin  release/chgame_boot_nomenu.bin
cp build/app/chgame_boot.bin     release/chgame_menu_dryrun.bin
cp build/release-visual/chgame_boot.bin        release/chgame_sdvisual.bin
cp build/release-visual-static/chgame_boot.bin release/chgame_sdvisual_static.bin
cp build/app-visual/chgame_boot.bin            release/chgame_visual_dryrun.bin
# The board package ships the five that Burn Bootloader offers (boards.txt,
# the Bootloader menu): the list menu and the visual menu, each in its two
# styles, and no menu.
PKG=../board/arduino/CHGame/bootloaders/CHGame
cp release/chgame_sdboot.bin release/chgame_sdboot_static.bin release/chgame_sdvisual.bin    release/chgame_sdvisual_static.bin release/chgame_boot_nomenu.bin "$PKG/"
(cd release && sha256sum chgame_*.bin | sed 's/ \*/  /' > SHA256SUMS && cat SHA256SUMS)
ls -l release
