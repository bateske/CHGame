"""CHSDtest: what the shared tools need to know (the schema is in the
repository's tools/gamecfg.py; `chgame build`, `check`, `export` and `card`
read this).

The bench talks to a real card over SPI1's registers, so it runs on the
board only; its serial port is the bench's command line (PROTOCOL.md), so
there is no device debug build either."""
# The USB CDC port is the command line: USB Serial, not the release
# default's "Upload only". Smallest + LTO, as the other apps. The tools swap
# the board field (rev0 here) for the board a build is for (--board;
# tools/device.py fqbn()), keeping the options.
FQBN = "CHGame:ch32v:rev0:opt=oslto,rtlib=nano,periph=game,usb=serial"
