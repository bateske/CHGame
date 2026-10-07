/* SPDX-License-Identifier: GPL-3.0-or-later
 * Sizzle for SDtoSerial: the CHGame library's chgame/Sizzle with this
 * sketch's switches (the library's Sizzle.h lists them all), compiled in
 * Fx.cpp. The same choice as CHSDtoUSB's: no particles and no shake (every
 * millisecond the screen takes is one the card is not serving the website),
 * only the banner over the graph for the moments that need saying.
 */
#pragma once
#include <CHGame.h>

// UI_SIZZLE 1 (the default): the library's banner, scaled 3x5 lettering in
// the house gradient dancing in from a mask (about 1 KB of flash and 400 B
// of RAM, the mask's SRAM inner loops). 0: the screen's own banner, outlined
// 5x7 lettering that pops in and blinks out (Ui.cpp), for a build that needs
// the room.
#ifndef UI_SIZZLE
#define UI_SIZZLE 1
#endif
#if UI_SIZZLE
#define SIZZLE_CONFIGURED 1
#define SIZZLE_NO_PARTICLES 1
#define SIZZLE_KIND_SPARK 0
#define SIZZLE_KIND_STAR 0
#define SIZZLE_KIND_DUST 0
#define SIZZLE_BURST 0
#define SIZZLE_FLOATS 0
#define SIZZLE_HUES_EXPORT 0
#define SIZZLE_HOLD_BANNER 0
#define SIZZLE_SHAKE 0
#define SIZZLE_STYLES (SIZZLE_GREEN | SIZZLE_RED)
#include <chgame/Sizzle.h>
#endif
