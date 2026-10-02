#pragma GCC optimize("Os")   // cold code: size over speed
#include <CHGame.h>
#include <string.h>
#include "Fx.h"

namespace fx {

// ---------------------------------------------------------------------------
// Particles
// ---------------------------------------------------------------------------
struct Particle { int16_t x, y; int8_t vx, vy; uint8_t life, colour, kind, age; };
static Particle parts[48];
const uint8_t RAIN[5] = {RED, GOLD, FELT_LT, CYAN, BLUE};

bool particles() {
    for (auto &p : parts) if (p.life) return true;
    return false;
}

void spawn(Kind k, int x, int y, int vx, int vy, uint8_t life, uint8_t colour) {
    Particle *slot = nullptr;
    for (auto &p : parts) if (!p.life) { slot = &p; break; }
    if (!slot) slot = &parts[rnd() % 48];                 // steal one
    slot->x = (int16_t)(x << 4); slot->y = (int16_t)(y << 4);
    slot->vx = (int8_t)(vx < -127 ? -127 : vx > 127 ? 127 : vx);
    slot->vy = (int8_t)(vy < -127 ? -127 : vy > 127 ? 127 : vy);
    slot->life = life; slot->colour = colour; slot->kind = k; slot->age = 0;
}

void burst(Kind k, int x, int y, uint8_t n, int speed, uint8_t colour) {
    for (uint8_t i = 0; i < n; i++) {
        int a = (int)(i * 256 / n) + rndRange(0, 12);
        int sp = speed / 2 + rndRange(0, speed / 2 + 1);
        int vy = (isin(a) * sp) >> 8;
        if (k == DUST) vy /= 2;                           // puffs spread along the floor
        spawn(k, x, y, (isin(a + 64) * sp) >> 8, vy, (uint8_t)rndRange(20, 40), colour);
    }
}

void fountain(int x, int y, uint8_t n) {
    static const uint8_t CONF[6] = {RED, GOLD, FELT_LT, CYAN, BLUE, WHITE};
    for (uint8_t i = 0; i < n; i++)
        spawn(CONFETTI, x + rndRange(-4, 5), y, rndRange(-28, 29), rndRange(-60, -30), (uint8_t)rndRange(40, 70),
              CONF[rnd() % 6]);
}

static void updateParticles() {
    for (auto &p : parts) {
        if (!p.life) continue;
        p.life--; p.age++;
        p.x += p.vx; p.y += p.vy;
        switch (p.kind) {
            case CONFETTI: if (p.age & 1) p.vy += 2; if (p.vy > 24) p.vy = 24;
                           p.vx = (int8_t)(p.vx * 15 / 16); break;
            case DUST:     p.vx = (int8_t)(p.vx * 7 / 8); p.vy = (int8_t)(p.vy * 7 / 8); break;
            default:       p.vy += (p.age & 3) == 0; break;
        }
    }
}

void drawParticles(uint8_t dust) {
    for (auto &p : parts) {
        if (!p.life) continue;
        int x = p.x >> 4, y = p.y >> 4;
        uint8_t c = p.colour;
        switch (p.kind) {
            case SPARK:
                gfx_pixel(x, y, c);
                if (p.age < 8) { gfx_pixel(x - 1, y, c); gfx_pixel(x + 1, y, c);
                                 gfx_pixel(x, y - 1, c); gfx_pixel(x, y + 1, c); }
                break;
            case CONFETTI:
                if ((p.age >> 2) & 1) gfx_hline(x, y, 2, c);
                else gfx_vline(x, y, 2, c);
                break;
            case STAR:
                gfx_hline(x - 1, y, 3, c); gfx_vline(x, y - 1, 3, c);
                break;
            case DUST: {                                  // a puff, down to a speck, centred
                int s = p.life > 10 ? dust : (p.life > 4 || (p.life & 1)) ? (dust + 1) / 2 : 0;
                gfx_fillRect(x - s / 2, y - s / 2, s, s, c);
                break;
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Banner
// ---------------------------------------------------------------------------
static char bannerText[14];
static uint8_t bannerStyle, bannerT, bannerFrames;
static int bannerCy;
static bool bannerHeld;

void banner(const char *text, BannerStyle s, int cy, uint8_t frames) {
    strncpy(bannerText, text, sizeof bannerText - 1);
    bannerText[sizeof bannerText - 1] = 0;
    bannerStyle = s; bannerCy = cy; bannerT = 0; bannerFrames = frames;
    bannerHeld = false;
}

void holdBanner(bool on) { bannerHeld = on; }

bool bannerActive() { return bannerFrames != 0; }

void drawBanner() {
    if (!bannerFrames) return;
    int t = bannerT;
    uint8_t scale = t < 3 ? 2 : (t < 7 ? 4 : 3);
    int w = text35WidthScaled(bannerText, scale);
    while (w > 124 && scale > 2) w = text35WidthScaled(bannerText, --scale);
    int h = 6 * scale;
    int8_t dy[14];
    int n = (int)strlen(bannerText);
    for (int k = 0; k < n && k < 14; k++) dy[k] = (int8_t)((isin(t * 10 + k * 36) * 2) >> 8) + 2;
    Mask m = maskBegin(w + 1, h + 5);
    maskText35(m, 0, 0, bannerText, scale, dy);
    // Last few frames: blink out.
    if (bannerFrames < 10 && (bannerFrames & 2)) return;
    uint8_t ramp[32];
    for (int r = 0; r < h + 5 && r < 32; r++) {
        switch (bannerStyle) {
            case B_RAINBOW: ramp[r] = RAIN[((r / 2) + t / 3) % 5]; break;
            case B_GOLD:    ramp[r] = r < 3 ? FX_B : (r < h / 2 + 6 ? GOLD : WOOD); break;
            case B_RED:     ramp[r] = r < 3 ? WHITE : RED; break;
            case B_CYAN:    ramp[r] = r < 3 ? WHITE : CYAN; break;
            default:        ramp[r] = WHITE; break;
        }
    }
    uint8_t outline = bannerStyle == B_RAINBOW ? FX_A : INK;
    maskDraw(m, 64 - w / 2, bannerCy - h / 2 - 2, 0, outline, bannerStyle == B_RAINBOW ? INK : WINE, ramp);
}

bool activeRows(int &lo, int &hi) {
    lo = 999; hi = -1;
    if (shaking()) { lo = 0; hi = 127; return true; }
    for (auto &p : parts) if (p.life) { int y = p.y >> 4; if (y - 2 < lo) lo = y - 2; if (y + 3 > hi) hi = y + 3; }
    if (bannerFrames) { if (bannerCy - 18 < lo) lo = bannerCy - 18; if (bannerCy + 18 > hi) hi = bannerCy + 18; }
    return hi >= lo;
}

void clear() {
    memset(parts, 0, sizeof parts);
    bannerFrames = 0;
    bannerHeld = false;
    shakeStop();
}

void update() {
    updateParticles();
    if (bannerFrames) {
        if (!bannerHeld || bannerFrames > 10) bannerFrames--;    // held: up, until let go to blink out
        if (!++bannerT) bannerT = 128;                           // (the same phase of the dance)
    }
    shakeTick();
}

}  // namespace fx
