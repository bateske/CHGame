// Sparkle: a particle pool and pop-up banners, on top of the CHGame
// library's fx:: (easing, integer sine, randomness and the screen shake).
#pragma once
#include <CHGame.h>

namespace fx {

enum Kind : uint8_t { SPARK, CONFETTI, STAR, DUST };
void spawn(Kind k, int x, int y, int vx16, int vy16, uint8_t life, uint8_t colour);
void burst(Kind k, int x, int y, uint8_t n, int speed16, uint8_t colour);  // radial
void fountain(int x, int y, uint8_t n);                                    // confetti up

// Big centred lettering with an outline; pops in, holds, fades.
enum BannerStyle : uint8_t { B_RAINBOW, B_GOLD, B_RED, B_CYAN, B_WHITE };
void banner(const char *text, BannerStyle s, int cy, uint8_t frames = 70);
void holdBanner(bool on);            // keep the banner up (before it blinks out) until false
bool bannerActive();

// Vertical extent of everything transient on screen (particles, banner,
// shake). Returns false if nothing is moving.
bool activeRows(int &lo, int &hi);

void clear();
void update();                      // once per frame
// dust: the size of a DUST puff (2 at the board's usual size, more zoomed in).
void drawParticles(uint8_t dust);
bool particles();                    // any still flying (screen space: the stage keeps the camera still meanwhile)
extern const uint8_t RAIN[5];        // the casino rainbow: red, gold, green, cyan, blue
void drawBanner();

}  // namespace fx
