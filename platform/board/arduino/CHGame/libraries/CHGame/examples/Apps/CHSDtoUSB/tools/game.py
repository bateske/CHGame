"""CHSDtoUSB: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame check` reads this).

The simulator plays a pretend Windows PC and a 16 GB FAT32 card
(tools/chsim/host/pc_host.cpp, card_host.cpp; the sessions are
tools/chsim/pcsession.py's, chosen by the script's name), so the scripts
show every screen; the drive itself is tested on the board by
tools/chsd_test.py."""
ECHO = ("STATE",)
# USB Serial and the mass-storage drive need the full USB stack (no
# usb=uploadonly), and it is tested on the board with -Os, not yet with LTO.
FQBN = "CHGame:ch32v:rev0:opt=osstd"
