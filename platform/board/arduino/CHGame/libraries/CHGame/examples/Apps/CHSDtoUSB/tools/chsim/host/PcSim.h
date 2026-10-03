// The simulator's PC and card for CHSDtoUSB (pc_host.cpp, card_host.cpp).
// The PC plays a session that tools/chsim/pcsession.py wrote, from the
// folder named by $CHSD_PC (trace.txt, blob.bin, card.bin): no folder, no
// card and no PC.
#pragma once
#include <stdint.h>

void sim_pc_load();                     // reads the session once (the card's first)
void sim_pc_resume();                   // go on past the marker the PC stopped at
char *sim_pc_status(char *p);           // "pc=<line>/<lines> at=<marker> paused=<0|1> done=<0|1>"

// The pretend card.
void card_load(const char *path, uint32_t blocks);
void card_present(bool in);
void card_badBlock(uint32_t lba);       // the next read of this block fails its CRC once
