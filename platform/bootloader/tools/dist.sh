#!/usr/bin/env bash
# Build every variant and refresh release/ (the binaries committed for
# flashing without a toolchain) and its SHA256SUMS.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
for m in release locked nomenu app "release --theme=plain" "release --theme=casino"; do
  log="build-${m// /_}.log"; log="${log//--theme=/}"
  ./build.sh $m > "$log" 2>&1 || { cat "$log"; exit 1; }; rm "$log"
done
mkdir -p release
cp build/release/chgame_boot.bin release/chgame_sdboot.bin
cp build/release-plain/chgame_boot.bin  release/chgame_sdboot_plain.bin
cp build/release-casino/chgame_boot.bin release/chgame_sdboot_casino.bin
cp build/locked/chgame_boot.bin  release/chgame_sdboot_locked.bin
cp build/nomenu/chgame_boot.bin  release/chgame_boot_nomenu.bin
cp build/app/chgame_boot.bin     release/chgame_menu_dryrun.bin
# The board package ships the four that Burn Bootloader offers (boards.txt,
# the Bootloader menu): the menu in its three colour themes, and no menu.
PKG=../board/arduino/CHGame/bootloaders/CHGame
cp release/chgame_sdboot.bin release/chgame_sdboot_plain.bin release/chgame_sdboot_casino.bin \
   release/chgame_boot_nomenu.bin "$PKG/"
(cd release && sha256sum chgame_*.bin | sed 's/ \*/  /' > SHA256SUMS && cat SHA256SUMS)
ls -l release
