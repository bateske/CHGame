// Saving options, lifetime stats, the purse and the game in progress.
//
// The CHGame library keeps the record in flash (chgame/Save.h: two pages
// used in turn, a CRC, this game's own magic "CHYD"); this is what goes in
// it and back out.
//
// A saved game is every card, the dice on the table and the rolls left, so
// CONTINUE picks up exactly where SAVE & QUIT left off, even mid-turn.
#pragma once
#include <chgame/Save.h>

class Yacht;

namespace save {

// (save::available(), false when the image is too big or a write failed,
// is the library's.)
bool load(Yacht &g, bool &hasGame); // options, stats, purse; the game too if hasGame
// Call after gfx_wait(): the page is built in CHGfx's chunk scratch.
bool store(const Yacht &g, bool withGame);

}  // namespace save
