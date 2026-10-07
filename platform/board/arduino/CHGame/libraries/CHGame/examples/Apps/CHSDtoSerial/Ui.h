/* SPDX-License-Identifier: GPL-3.0-or-later
 * The screen, CHSDtoUSB's instrument panel for the serial link: a status
 * bar with the speed, a gauge, one graph column per 125 ms of traffic, and a
 * panel with the event log, the session's numbers or the card's details
 * (LEFT/RIGHT). It reads Monitor.h; Display.cpp calls it between commands.
 */
#pragma once
#include <stdint.h>

namespace ui {

enum Mode : uint8_t { M_BOOT, M_CARD, M_STANDBY, M_READY, M_STOPPED };

struct Status {
    uint8_t mode;
    bool stopping;                          // B was pressed: the cancel waits for the command in progress
    uint16_t exitMs;                        // START held this long (0: not held); 3000 leaves
};

void begin();
void splash();                              // the title, while the card mounts
void button(uint8_t b);                     // a d-pad press (LEFT_BUTTON ...): pages and scrolling
// Draws a frame if one is due (something changed, or an animation runs; `force`:
// now). Returns true if it drew; the caller flushes rows [y0, y1).
bool frame(uint32_t now, const Status &s, bool force, int &y0, int &y1);
void goodbye();                             // "MENU", before the reset back to the SD menu
void tick();                                // once per 40 ms: the banner's clock
#ifdef CHSIM
struct Perf { uint32_t frames, totalUs, maxUs, rows; };   // drawing time, rows flushed (the harness reads it)
extern Perf perf;
#endif

}  // namespace ui
