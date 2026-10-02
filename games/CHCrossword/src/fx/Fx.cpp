#pragma GCC optimize("Os", "no-ipa-sra")   // cold code: size over speed
#include <string.h>
#include <CHGame.h>
#include "Fx.h"
#include "../gfx/Font.h"

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
            default:       p.vy += (p.age & 3) == 0; break;
        }
    }
}

void drawParticles() {
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
        }
    }
}

// ---------------------------------------------------------------------------
// Banner
// ---------------------------------------------------------------------------
static char bannerText[14];                          // the game's longest is 11
static uint8_t bannerLen, bannerStyle, bannerT, bannerFrames;
static int bannerCy;
static bool bannerHeld;

void banner(const char *text, BannerStyle s, int cy, uint8_t frames) {
    bannerLen = (uint8_t)(fmtStr(bannerText, text) - bannerText);
    bannerStyle = s; bannerCy = cy; bannerT = 0; bannerFrames = frames;
    bannerHeld = false;
}

void holdBanner(bool on) { bannerHeld = on; }

bool bannerActive() { return bannerFrames != 0; }

// The letters drop in one after another from DROP px up, bounce as they
// land, then dance on the spot.
static const int DROP = 18, STAGGER = 2, FALL = 12;

static bool dropping() { return bannerT < STAGGER * bannerLen + FALL; }

void drawBanner() {
    if (!bannerFrames) return;
    int t = bannerT;
    uint8_t gap = 1;
    int w = fontWidth(bannerText, gap);
    if (w > 124) w = fontWidth(bannerText, gap = 0);
    int n = bannerLen, off = (dropping() ? DROP : 0) + 2;
    int8_t dy[14];
    for (int k = 0; k < n && k < 14; k++) {
        int tk = t - STAGGER * k, d = 0;
        if (tk < 0) d = -60;                                            // not yet: out of the mask
        else if (tk < FALL) d = -(((256 - ease(OUT_BOUNCE, tk, FALL)) * DROP) >> 8);
        dy[k] = (int8_t)(d + off + ((isin(t * 10 + k * 36) * 2) >> 8));
    }
    int h = FONT_H + off + 2;
    Mask m = maskBegin(w + 1, h);
    maskFont(m, 0, 0, bannerText, dy, gap);
    // Last few frames: blink out.
    if (bannerFrames < 10 && (bannerFrames & 2)) return;
    uint8_t ramp[40];
    for (int r = 0; r < h && r < 40; r++) {
        int g = r - off;                                                // row of the letters
        switch (bannerStyle) {
            case B_RAINBOW: ramp[r] = RAIN[(((r + 8) / 2) + t / 3) % 5]; break;
            default:        ramp[r] = g < 3 ? FX_B : (g < 8 ? GOLD : WOOD); break;   // B_GOLD
        }
    }
    uint8_t outline = bannerStyle == B_RAINBOW ? FX_A : INK;
    maskDraw(m, 64 - w / 2, bannerCy - FONT_H / 2 - off, 0, outline, outline == INK ? -1 : INK, ramp);
}

bool activeRows(int &lo, int &hi) {
    lo = 999; hi = -1;
    if (shaking()) { lo = 0; hi = 127; return true; }
    for (auto &p : parts) if (p.life) { int y = p.y >> 4; if (y - 2 < lo) lo = y - 2; if (y + 3 > hi) hi = y + 3; }
    if (bannerFrames) { if (bannerCy - 30 < lo) lo = bannerCy - 30; if (bannerCy + 12 > hi) hi = bannerCy + 12; }
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
