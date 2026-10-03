// CHWords - a casino crossword tile game for the CHGame handheld (CH32X035,
// 128x128 ST7735, piezo, microSD), in the look of CHBlackjack and its tables.
//
// The rules are in src/rules, the dictionary (a compressed list in flash,
// and the full one on the SD card) in src/dict and src/sd, the CPU in
// src/ai, the game's flow in src/game, and everything you see and hear in
// src/stage and src/states.
#include <CHGame.h>
#include "config.h"

// Built for Tools > USB > Upload only: with USB Serial compiled in, the game
// is about 100 B over the flash. A debug build keeps Serial for the debug
// protocol and makes room with CHWD_LEAN instead.
#if defined(USE_CHGAME_USB_CDC) && !CHGAME_DEBUG
#error "CHWords needs Tools > USB > Upload only to fit in the flash (and Tools > Optimize > Smallest + LTO, the default)"
#endif
#include "src/Frame.h"

void setup() {
    arduboy.boot();
    gfx_begin(GFX_DIV2, GFX_12BPP);
    frame::begin();
    arduboy.setFrameRate(CHWD_FPS);
}

void loop() {
    frame::run();
}
