// CHCrossword - a crossword for the CHGame handheld (CH32X035, 128x128
// ST7735, piezo), in the look of CHBlackjack and the casino games after it.
//
// The puzzles are packed in src/game/PuzzleData.cpp (from tools/puzzles),
// with more in packs on the SD card (src/pack, src/sd); the rules and the
// score are in src/game, and everything you see and hear in src/stage and
// src/states.
#include <CHGame.h>
#include "config.h"

// Built for Tools > USB > Upload only: with USB Serial compiled in, the game
// is about 100 B over the flash. A debug build keeps Serial for the debug
// protocol and makes room with CHCW_LEAN instead.
#if defined(USE_CHGAME_USB_CDC) && !CHGAME_DEBUG
#error "CHCrossword needs Tools > USB > Upload only to fit in the flash (and Tools > Optimize > Smallest + LTO, the default)"
#endif
#include "src/Frame.h"

void setup() {
    arduboy.boot();
    gfx_begin(GFX_DIV2, GFX_12BPP);
    frame::begin();
    arduboy.setFrameRate(CHCW_FPS);
}

void loop() {
    frame::run();
}
