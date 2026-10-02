// Sparkle: a particle pool, pop-up banners and floating "+$15" texts, on
// top of the CHGame library's fx:: (easing, integer sine, randomness and the
// screen shake).
#pragma once
#include <CHGame.h>

namespace fx {

enum Kind : uint8_t { SPARK, CONFETTI, COIN, RAIN, STAR, DUST };
void spawn(Kind k, int x, int y, int vx16, int vy16, uint8_t life, uint8_t colour);
void burst(Kind k, int x, int y, uint8_t n, int speed16, uint8_t colour);  // radial
void fountain(Kind k, int x, int y, uint8_t n);                            // confetti/coins up

// Big centred lettering with an outline; pops in, holds, fades.
enum BannerStyle : uint8_t { B_RAINBOW, B_GOLD, B_RED, B_CYAN, B_WHITE };
void banner(const char *text, BannerStyle s, int cy, uint8_t frames = 70);   // <= 15 chars
void holdBanner(bool on);            // keep the banner up (before it blinks out) until false
bool bannerActive();

void floatText(const char *text, int x, int y, uint8_t colour);    // "+$15", rising (<= 9 chars)

// Vertical extent of everything transient on screen (particles, floats,
// banner, shake). Returns false if nothing is moving.
bool activeRows(int &lo, int &hi);

void clear();
void update();                      // once per frame
void drawParticles();
bool particles();                    // any still flying
extern const uint8_t HUES[5];        // the casino rainbow: red, gold, green, cyan, blue
void drawBanner();
void drawFloats();

}  // namespace fx
