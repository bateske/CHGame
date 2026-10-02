#pragma GCC optimize("Os")
#include <Arduino.h>
#include <CHGame.h>
#include "../config.h"
#include "Frame.h"
#include "states/Screens.h"
#include "debug/Debug.h"
#include "audio/Audio.h"

namespace frame {

// The table's colours: FELT_DK and FELT only. FELT_LT stays green whatever
// the table - it is the bamboo suit's ink.
static const uint16_t FELTS[pal::THEME_COUNT][3] = {
    {0x042, 0x173, 0x4B5},   // classic green
    {0x024, 0x149, 0x4B5},   // blue
    {0x401, 0x812, 0x4B5},   // red
    {0x203, 0x517, 0x4B5},   // purple
};

void begin() {
    dbg::paintStack();
    pal::setThemes(FELTS, pal::THEME_COUNT);
    pal::init();
    screens::begin();
}

bool run() {
    dbg::poll();
    if (!arduboy.nextFrame()) return false;
    dbg::markUpdateStart();
    // Logic runs at a fixed 60 Hz. If a heavy frame made drawing fall
    // behind, catch up (up to three ticks) before drawing again.
    uint8_t ticks = 0;
    do {
        arduboy.pollButtons();
        pal::tick();
        audio::update();
        screens::update();
    } while (++ticks < 3 && arduboy.nextFrame());
    gfx_wait();
    pal::commit();
    dbg::markRenderStart();
    screens::render(arduboy.frameCount);
    dbg::markRenderEnd();
    gfx_flushAsync();
    return true;
}

}  // namespace frame
