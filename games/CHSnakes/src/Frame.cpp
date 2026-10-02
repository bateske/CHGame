#pragma GCC optimize("Os")
#include <Arduino.h>
#include <CHGame.h>
#include "../config.h"
#include "Frame.h"
#include "states/Screens.h"
#include "debug/Debug.h"
#include "audio/Sounds.h"

namespace frame {

void begin() {
    dbg::paintStack();
    audio::begin(SOUNDS, (uint8_t)Sfx::COUNT, false);   // on once the options are read
    pal::init();
    screens::begin();
}

void run() {
    dbg::poll();
    if (!arduboy.nextFrame()) return;
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
}

}  // namespace frame
