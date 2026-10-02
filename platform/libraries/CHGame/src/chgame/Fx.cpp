#pragma GCC optimize("Os", "no-ipa-sra")
#include <CHGfx.h>
#include "Fx.h"
#include "RamFunc.h"

namespace fx {

// ---------------------------------------------------------------------------
// Curves: 17-point Q8 tables, linearly interpolated. One table each, so a
// game links only the curves it uses (LINEAR needs none).
// ---------------------------------------------------------------------------
static const int16_t CUBIC[17]  = {0, 45, 84, 119, 148, 173, 194, 210, 224, 235, 242, 248, 252, 254, 256, 256, 256};
static const int16_t BACK[17]   = {0, 69, 126, 173, 209, 237, 257, 271, 278, 281, 281, 277, 272, 267, 261, 258, 256};
static const int16_t INOUT[17]  = {0, 3, 11, 24, 40, 59, 81, 104, 128, 152, 175, 197, 216, 232, 245, 253, 256};
static const int16_t BOUNCE[17] = {0, 8, 30, 68, 121, 189, 248, 215, 196, 193, 204, 231, 249, 240, 246, 253, 256};

static int curve(const int16_t *c, int t, int n) {
    if (n <= 0 || t >= n) return 256;
    if (t <= 0) return 0;
    int p = (t << 8) / n;                    // 0..255
    if (!c) return p;                        // LINEAR
    int i = p >> 4, f = p & 15;
    return c[i] + (((c[i + 1] - c[i]) * f) >> 4);
}

int ease(Ease e, int t, int n) {
    static const int16_t *const CURVES[5] = {nullptr, CUBIC, BACK, INOUT, BOUNCE};
    return curve(CURVES[e], t, n);
}

int bounce(int t, int n) { return curve(BOUNCE, t, n); }

static const uint8_t SIN[65] = {
    0, 6, 13, 19, 25, 31, 38, 44, 50, 56, 62, 68, 74, 80, 86, 92, 98, 104, 109, 115, 121, 126,
    132, 137, 142, 147, 152, 157, 162, 167, 172, 177, 181, 185, 190, 194, 198, 202, 206, 209,
    213, 216, 220, 223, 226, 229, 231, 234, 237, 239, 241, 243, 245, 247, 248, 250, 251, 252,
    253, 254, 255, 255, 255, 255, 255};

int isin(int a) {
    a &= 255;
    int q = a >> 6, i = a & 63;
    int v;
    switch (q) {
        case 0: v = SIN[i]; break;
        case 1: v = SIN[64 - i]; break;
        case 2: v = -SIN[i]; break;
        default: v = -SIN[64 - i]; break;
    }
    return v;
}

static uint32_t seed = 0x1234567u;
uint32_t rnd() { seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5; return seed; }
void reseed() { seed = 0x1234567u; }
int rndRange(int lo, int hi) { return hi > lo ? lo + (int)(rnd() % (uint32_t)(hi - lo)) : lo; }

// ---------------------------------------------------------------------------
// Shake
// ---------------------------------------------------------------------------
static uint8_t shakeT, shakeAmp;

void shake(uint8_t frames, uint8_t amp) { shakeT = frames; shakeAmp = amp; }
bool shaking() { return shakeT != 0; }
void shakeTick() { if (shakeT) shakeT--; }
void shakeStop() { shakeT = 0; }

// Rows y0..y1 moved dy rows and one byte (2 px) sideways, in one pass of
// word copies from SRAM (newlib's memmove is a byte loop in flash: ~10 ms a
// shaken frame). Walks away from the direction of travel so every source row
// is read before it is overwritten; rows the move uncovers shift in place.
CHGAME_RAMFUNC(shake) static void shiftRows(int y0, int y1, int dy, bool right) {
    const int W = GFX_FB_STRIDE / 4;
    for (int k = 0; k <= y1 - y0; k++) {
        int y = dy > 0 ? y1 - k : y0 + k, sy = y - dy;
        if (sy < y0 || sy > y1) sy = y;
        uint32_t *d = (uint32_t *)(gfx_fb + y * GFX_FB_STRIDE);
        const uint32_t *s = (const uint32_t *)(gfx_fb + sy * GFX_FB_STRIDE);
        if (right) {        // d[i] = s[i - 1], the first byte kept
            for (int j = W - 1; j > 0; j--) d[j] = (s[j] << 8) | (s[j - 1] >> 24);
            d[0] = (s[0] << 8) | (s[0] & 0xFF);
        } else {            // d[i] = s[i + 1], the last byte kept
            for (int j = 0; j < W - 1; j++) d[j] = (s[j] >> 8) | (s[j + 1] << 24);
            d[W - 1] = (s[W - 1] >> 8) | (s[W - 1] & 0xFF000000u);
        }
    }
}

void applyShake(int y0, int y1, int fill) {
    if (!shakeT) return;
    int a = (shakeAmp * shakeT + 9) / 10;
    if (a < 1) a = 1;
    int dy = (shakeT & 1) ? a : -a;
    if (fill >= 0) gfx_scroll(y0, y1 - y0 + 1, (shakeT & 2) ? 2 : -2, dy, fill);
    else shiftRows(y0, y1, dy, (shakeT & 2) != 0);               // 2 px sideways
}

}  // namespace fx
