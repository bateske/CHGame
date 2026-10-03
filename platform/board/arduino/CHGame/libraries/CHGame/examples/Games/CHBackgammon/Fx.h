// Sparkle: a particle pool and pop-up banners, on top of the CHGame
// library's fx:: (easing, integer sine, randomness and the screen shake).
// The particle pool, the banner and the floats are the CHGame library's
// chgame/Sizzle, configured here (the switches that differ from its defaults)
// and compiled in Fx.cpp; the library's Sizzle.h lists every switch.
#pragma once
#include <CHGame.h>

#define SIZZLE_CONFIGURED 1
#define SIZZLE_BANNER_DROP 1
#define SIZZLE_FLOATS 0
#include <chgame/Sizzle.h>
