"""CHSDtoSerial: what the shared tools need to know (the schema is in the
repository's tools/gamecfg.py; `chgame build`, `check`, `export` and `card`
read this).

The simulator plays the website (tools/chsim/host/web_host.cpp): a session
tools/chsim/websession.py writes, chosen by the script's name, against a
card image held in RAM (host/disk_host.c), so the scripts show every
screen and every answer is checked against what the website expects. On
the board the sketch's USB serial port is the protocol itself, so there is
no device debug build (`chgame run --device` has no port to use); the
website's own hardware tests drive it there."""
ECHO = ("STATE",)
# The USB CDC port is the protocol: USB Serial, not the release default's
# "Upload only". Smallest + LTO, as the website's build-helper builds it.
FQBN = "CHGame:ch32v:rev0:opt=oslto,rtlib=nano,periph=game,usb=serial"
# One row of LCD DMA scratch instead of two: 512 B of RAM kept for the card's
# buffers. The website's build-helper builds with the same; so does the
# simulator, so the banner's mask fits the same scratch there.
DEFINES = ["GFX_CHUNK_ROWS=1"]
