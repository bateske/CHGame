"""CHBoardTest: what the shared tools need to know (the schema is in the
repository's tools/gamecfg.py; `chgame build` and `upload` read this).

A board check for bring-up. It reads the board's pins and talks to the SD
card, so it runs on the board only: no simulator scripts, no tests. It is
not on the casino card."""
# Peripherals "Full" for Serial1 (CN3's loopback); USB Serial carries the
# results as text lines. The board field is the tools' to swap (--board).
FQBN = "CHGame:ch32v:rev0:opt=oslto,rtlib=nano,periph=full,usb=serial"
# It saves nothing, so the image may use the save pages too.
SAVE_PAGES = 0
