// Sparkle: a particle pool, pop-up banners and floating "+$15" texts, on
// top of the CHGame library's fx:: (the bounce curve, integer sine,
// randomness and the screen shake).
// The particle pool, the banner and the floats are the CHGame library's
// chgame/Sizzle, configured here (the switches that differ from its defaults)
// and compiled in Fx.cpp; the library's Sizzle.h lists every switch.
#pragma once
#include <CHGame.h>
#include "config.h"

#define SIZZLE_CONFIGURED 1
#define SIZZLE_NO_PARTICLES CHTT_LEAN    // a device debug build has no particles, to fit
#define SIZZLE_KIND_COIN 1
#define SIZZLE_KIND_RAIN 1
#define SIZZLE_BANNER_FILL WHITE
#define SIZZLE_COLOUR_INLINE 1
#define SIZZLE_STYLES (SIZZLE_RAINBOW | SIZZLE_RED | SIZZLE_CYAN)
#include <chgame/Sizzle.h>
