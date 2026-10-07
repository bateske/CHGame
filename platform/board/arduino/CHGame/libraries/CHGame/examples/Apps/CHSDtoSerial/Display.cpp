/* SPDX-License-Identifier: GPL-3.0-or-later
 * The console: buttons, LED, beeps and the screen (Ui.cpp) between the
 * sketch's serial work. Synchronous, bounded LCD updates between filesystem
 * operations only: every flush here blocks, so the card always finds SPI1
 * idle, and nothing runs during SD activity except between the blocks of a
 * long command (transfer_ui_poll), after the SD read has released SPI.
 *
 * B and START keep the first screen's exact rules, since they feed the
 * protocol's cancel: B asks for a cancel at once, START held three seconds
 * asks to leave; the sketch acts at its next command boundary. A and the
 * d-pad are the screen's alone: pages, and the website's QR code while no
 * website is talking.
 */
#include <CHGame.h>
#include "Display.h"
#include "Monitor.h"
#include "Ui.h"
#include "Sounds.h"

static uint8_t requested, padPrev;
static bool priorB;
static uint32_t startHeld, lastBeep, lastTick;

static ui::Status status(uint32_t now) {
    ui::Status s;
    s.mode = !mon::mounted ? ui::M_BOOT : mon::card.error ? ui::M_CARD : mon::stopped ? ui::M_STOPPED
           : !mon::linked ? ui::M_STANDBY : ui::M_READY;
    s.stopping = (requested & 1) != 0;
    uint32_t held = startHeld ? now - startHeld : 0;
    s.exitMs = (uint16_t)(startHeld ? (held < 1 ? 1 : held > 3000 ? 3000 : held) : 0);
    return s;
}

// A frame when one is due. Called from every control poll: between frames
// of serial input, and between the blocks of a long command.
static void pump(uint32_t now, bool force) {
    if (now - lastTick >= 40) {                          // the 25 Hz logic tick: banners, the LED, the d-pad
        lastTick = now;
        ui::tick();
        audio::update();
        pal::tick();                                     // (the rainbow, when a readout has hit its limit)
        uint8_t pad = chgame_readButtons() & (A_BUTTON | UP_BUTTON | DOWN_BUTTON | LEFT_BUTTON | RIGHT_BUTTON);
        uint8_t hit = (uint8_t)(pad & ~padPrev);
        padPrev = pad;
        for (uint8_t b = A_BUTTON; b <= RIGHT_BUTTON; b = (uint8_t)(b << 1))
            if (hit & b) ui::button(b);
    }
    mon::tick(now);
    int y0, y1;
    if (ui::frame(now, status(now), force, y0, y1)) {
        pal::commit();                                   // (a palette change lands with this flush)
        gfx_flushRect(0, y0, GFX_W, y1 - y0);            // blocking: DMA is finished before the card can claim SPI1
    }
}

void display_begin() {
    chgame.boot();                                       // the buttons' pull-ups
    chgame.startExits = false;                           // START is handled here, at a command boundary
    pinMode(PIN_LED, OUTPUT);
    gfx_begin(GFX_DIV2, GFX_12BPP);
    ui::begin();
    soundsBegin();
    ui::splash();
    gfx_flush();
}

void display_card(uint8_t error) {
    mon::cardState(millis(), error);
    pump(millis(), true);
}

void display_command(uint8_t cmd, const uint8_t *, uint16_t length) {
    digitalWrite(PIN_LED, HIGH);
    mon::command(cmd, length);
    if (cmd == 7 && !length) pump(millis(), true);       // COMMIT takes a while: the screen says so first
}

void display_result(uint8_t cmd, const uint8_t *data, uint16_t length, uint8_t error, const uint8_t *out,
                    uint16_t size) {
    uint32_t now = millis();
    mon::result(now, cmd, data, length, error, out, size);
    if (!startHeld) digitalWrite(PIN_LED, LOW);
    if (cmd == 10 && !error) {                           // MENU: the answer goes out, then the sketch resets
        audio::sfx(mon::done ? Sfx::Done : Sfx::Menu);
        ui::goodbye();
        gfx_flush();
        return;
    }
    pump(now, false);
}

void display_link(uint8_t what, uint8_t cmd) { mon::link(millis(), what, cmd); }

// The 100 ms the sketch always waited before resetting for the menu; after
// a finished job, long enough to read "COMPLETE" and hear its jingle.
void display_leaving() { delay(mon::done ? 1400 : 100); }

void display_cancelled(uint8_t action, uint8_t error) {
    uint32_t now = millis();
    mon::cancelled(now, action, error);
    if (action & 2) {                                    // leaving: the sketch resets once this returns
        audio::sfx(Sfx::Menu);
        ui::goodbye();
        gfx_flush();
        delay(120);                                      // the jingle
        return;
    }
    pump(now, true);
}

uint8_t display_controls() {
    uint32_t now = millis();
    uint8_t held = chgame_readButtons();
    bool b = (held & B_BUTTON) != 0, start = (held & START_BUTTON) != 0;
    if (b && !priorB) { requested |= 1; ui::button(B_BUTTON); }   // (the screen may also show the QR code)
    priorB = b;
    if (start) {
        if (!startHeld) { startHeld = now ? now : 1; lastBeep = now - 500; }
        digitalWrite(PIN_LED, ((now - startHeld) / 150) & 1);
        if (now - lastBeep >= 700) { lastBeep = now; audio::note(mon::transferActive ? 1800 : 900, 45, 7); }
        if (now - startHeld >= 3000) requested |= 2;
    } else if (startHeld) {
        startHeld = 0;
        digitalWrite(PIN_LED, LOW);
    }
    pump(now, false);
    return requested;
}
void display_controls_done() { requested = 0; }
extern "C" void transfer_ui_poll(void) { mon::polled(millis()); display_controls(); }
