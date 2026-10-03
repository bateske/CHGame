// Sparkle: a particle pool, pop-up banners and floating "+$15" texts, the
// CHGame library's chgame/Sizzle configured here (the switches that differ
// from its defaults; the library's Sizzle.h lists every one) and compiled
// in Fx.cpp. Easing, sine, randomness and the screen shake are the
// library's (fx:: in chgame/Fx.h).
#pragma once
#include <CHGame.h>

#define SIZZLE_CONFIGURED 1
#define SIZZLE_KIND_COIN 1
#define SIZZLE_KIND_RAIN 1
#define SIZZLE_RAIN_KIND_NAME RAIN
#define SIZZLE_DUST 1
#define SIZZLE_HUES_EXPORT 0
#define SIZZLE_HOLD_BANNER 0
#define SIZZLE_BANNER_WRAP 0
#define SIZZLE_BANNER_FILL WHITE
#define SIZZLE_COLOUR_INLINE 1
#include <chgame/Sizzle.h>
