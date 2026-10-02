#!/usr/bin/env bash
# Build every variant and refresh release/ (the binaries committed for
# flashing without a toolchain) and its SHA256SUMS.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
for m in release locked nomenu app; do ./build.sh "$m" > "build-$m.log" 2>&1 || { cat "build-$m.log"; exit 1; }; rm "build-$m.log"; done
mkdir -p release
cp build/release/chgame_boot.bin release/chgame_sdboot.bin
cp build/locked/chgame_boot.bin  release/chgame_sdboot_locked.bin
cp build/nomenu/chgame_boot.bin  release/chgame_boot_nomenu.bin
cp build/app/chgame_boot.bin     release/chgame_menu_dryrun.bin
# The board package ships the two that Burn Bootloader offers (boards.txt,
# the Bootloader menu), beside the 0.2.4 bootloader that is kept as it was.
PKG=../board/arduino/CHGame/bootloaders/CHGame
cp release/chgame_sdboot.bin release/chgame_boot_nomenu.bin "$PKG/"
(cd release && sha256sum chgame_*.bin > SHA256SUMS && cat SHA256SUMS)
ls -l release
