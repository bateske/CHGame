#!/usr/bin/env bash
# Build every variant for every board and refresh release/ (the binaries
# committed for flashing without a toolchain: rev0's in release/, rev1's in
# release/rev1/) and its SHA256SUMS (rev0's lines first, as they always were,
# then rev1/...), and the board package's bootloaders (rev0's in
# bootloaders/CHGame/, rev1's in bootloaders/CHGame/rev1/).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
PKG=../board/arduino/CHGame/bootloaders/CHGame
for board in rev0 rev1; do
  if [ "$board" = rev0 ]; then sfx=; dst=release; pkg="$PKG"
  else sfx="-$board"; dst="release/$board"; pkg="$PKG/$board"; fi
  for m in release locked nomenu app "release --style=static" "release --ui=visual" \
           "release --ui=visual --style=static" "app --ui=visual"; do
    log="build-$board-${m// /_}.log"; log="${log//--style=/}"; log="${log//--ui=/}"
    ./build.sh --board=$board $m > "$log" 2>&1 || { cat "$log"; exit 1; }; rm "$log"
  done
  mkdir -p "$dst" "$pkg"
  cp build/release$sfx/chgame_boot.bin "$dst/chgame_sdboot.bin"
  cp build/release-static$sfx/chgame_boot.bin "$dst/chgame_sdboot_static.bin"
  cp build/locked$sfx/chgame_boot.bin  "$dst/chgame_sdboot_locked.bin"
  cp build/nomenu$sfx/chgame_boot.bin  "$dst/chgame_boot_nomenu.bin"
  cp build/app$sfx/chgame_boot.bin     "$dst/chgame_menu_dryrun.bin"
  cp build/release-visual$sfx/chgame_boot.bin        "$dst/chgame_sdvisual.bin"
  cp build/release-visual-static$sfx/chgame_boot.bin "$dst/chgame_sdvisual_static.bin"
  cp build/app-visual$sfx/chgame_boot.bin            "$dst/chgame_visual_dryrun.bin"
  # The board package ships the five that Burn Bootloader offers (boards.txt,
  # the Bootloader menu): the list menu and the visual menu, each in its two
  # styles, and no menu.
  cp "$dst/chgame_sdboot.bin" "$dst/chgame_sdboot_static.bin" "$dst/chgame_sdvisual.bin" \
     "$dst/chgame_sdvisual_static.bin" "$dst/chgame_boot_nomenu.bin" "$pkg/"
done
(cd release && { sha256sum chgame_*.bin; sha256sum rev1/chgame_*.bin; } | sed 's/ \*/  /' > SHA256SUMS && cat SHA256SUMS)
ls -l release release/rev1
