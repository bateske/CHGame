// Sparkle: a particle pool, pop-up banners and floating "+$15" texts. The
// easing, sine, randomness and screen shake are the CHGame library's
// (fx:: in chgame/Fx.h).
#pragma once
#include <stdint.h>
#include <CHGame.h>

namespace fx {

enum Kind : uint8_t { SPARK, CONFETTI, COIN, RAIN, STAR, DUST };
void spawn(Kind k, int x, int y, int vx16, int vy16, uint8_t life, uint8_t colour);
void burst(Kind k, int x, int y, uint8_t n, int speed16, uint8_t colour);  // radial
void fountain(Kind k, int x, int y, uint8_t n);                            // confetti/coins up
void explode(int x, int y, uint8_t n);                                     // coins, every way at once
bool particlesAlive();

// Big centred lettering with an outline; pops in, holds, fades.
enum BannerStyle : uint8_t { B_RAINBOW, B_GOLD, B_RED, B_CYAN, B_WHITE };
void banner(const char *text, BannerStyle s, int cy, uint8_t frames = 70);
bool bannerActive();

void floatText(const char *text, int x, int y, uint8_t colour);

// Vertical extent of everything transient on screen (particles, floats,
// banner, shake). Returns false if nothing is moving.
bool activeRows(int &lo, int &hi);

void clear();
void update();                      // once per frame
void drawParticles();
void drawBanner();
void drawFloats();

}  // namespace fx
