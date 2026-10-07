// Cards, chips, seat avatars and the dealer button (CardArt.h).
#pragma GCC optimize("Os")   // cold code: size over speed (hot pixel loops live in the CHGame library)
// The big card derived from Press-Play-On-Tape/Blackjack (Apache-2.0),
// PlayGameState_Render.cpp drawCard(), via CHBlackjack.
#include <CHGame.h>
#include "CardArt.h"
#include "Cards.h"
#include "src/assets/Assets.h"

namespace art {

bool fourColour = false;

const uint8_t SEAT_COLOUR[6] = {RED, BLUE, GOLD, CYAN, SILVER, SKIN};
const char *const SEAT_NAME[6] = {"RED", "BLUE", "GOLD", "CYAN", "SILVER", "PEACH"};

uint8_t suitColour(uint8_t c) {
    static const uint8_t TWO[4] = {INK, RED, RED, INK}, FOUR[4] = {FELT_DK, BLUE, RED, INK};
    return (fourColour ? FOUR : TWO)[suitOf(c)];
}

static void span1(int x, int y, const uint8_t *d, uint8_t c) {
    uint8_t h = d[1];
    d += 2;
    for (int j = 0; j < h; j++) {
        uint8_t n = *d++;
        while (n--) { gfx_hline(x + d[0], y + j, d[1], c); d += 2; }
    }
}

static void back(int x, int y, int w, int h, uint8_t edge) {
    fillRound(x, y, w, h, 2, WINE);
    if (w > 6) {
        dither(x + 2, y + 2, w - 4, h - 4, RED, 0);
        if (h > 20) gfx_rect(x + 2, y + 2, w - 4, h - 4, WHITE);
    }
    if (w >= 12) {
        // A small gold diamond in the middle.
        int cx = x + w / 2, cy = y + h / 2;
        for (int i = 0; i < 4; i++) gfx_hline(cx - i, cy - 3 + i, 2 * i + 1, GOLD);
        for (int i = 0; i < 3; i++) gfx_hline(cx - 2 + i, cy + 1 + i, 5 - 2 * i, GOLD);
    }
    roundRect(x, y, w, h, 2, edge);
}

// Drop shadow on the felt, 1 px right of and below a w x h card, following
// its rounded corner.
static void shadow(int x, int y, int w, int h) {
    gfx_vline(x + w, y + 2, h - 4, FELT_DK);
    gfx_hline(x + 2, y + h, w - 4, FELT_DK);
    if (w < 5) return;
    gfx_pixel(x + w - 1, y + h - 2, FELT_DK);
    gfx_pixel(x + w - 2, y + h - 1, FELT_DK);
}

void card(int x, int y, uint8_t c, bool faceUp, int w, bool full, uint8_t edge) {
    const int H = CARD_H;
    if (w < CARD_W) x += (CARD_W - w) / 2;
    if (w <= 0) return;
    shadow(x, y, w, H);
    if (!faceUp) { back(x, y, w, H, edge); return; }
    panel(x, y, w, H, 2, WHITE, edge);
    if (w < 10) return;
    uint8_t col = suitColour(c), r = rankOf(c), s = suitOf(c);
    int ix = x + 2 - (CARD_W - w) / 4;                   // corner index slides in as it squashes
    if (w >= 16) {
        glyph(ix, y + 3, RANK_GLYPH + r * 7, RANK_WIDTH[r], col);
        glyph(ix, y + 12, SUIT_SMALL + s * 5, 5, col);
    }
    if (!full || w < 20) return;
    if (r == RA) {
        span1(x + 7, y + 9, PIP13 + PIP13_AT[s], col);
    } else if (r >= RJ) {
        static const uint8_t *const COURT[3] = {COURT_JACK, COURT_QUEEN, COURT_KING};
        uint8_t remap[16];
        for (uint8_t i = 0; i < 16; i++) remap[i] = i;
        remap[RED] = col == INK || col == FELT_DK ? BLUE : col;   // robe in the suit colour
        sprite4(COURT[r - RJ], x + 7, y + 5, remap);
        glyph(x + 16, y + 20, SUIT_SMALL + s * 5, 5, col);
    } else {
        span1(x + 9, y + 11, PIP9 + PIP9_AT[s], col);
    }
}

// The mini card: a 3x5 rank over the suit, 10x15. Its 7 px left strip
// holds both, so a stud row can overlap them 7 px apart.
void mini(int x, int y, uint8_t c, bool faceUp, int w, uint8_t edge) {
    if (w < MINI_W) x += (MINI_W - w) / 2;
    if (w <= 0) return;
    gfx_vline(x + w, y + 2, MINI_H - 3, FELT_DK);
    if (!faceUp) {
        fillRound(x, y, w, MINI_H, 1, WINE);
        if (w > 4) dither(x + 1, y + 1, w - 2, MINI_H - 2, RED, 0);
        roundRect(x, y, w, MINI_H, 1, edge);
        return;
    }
    panel(x, y, w, MINI_H, 1, WHITE, edge);
    if (w < 7) return;
    uint8_t col = suitColour(c), r = rankOf(c);
    int ix = x + 1 + (w - MINI_W) / 2;
    if (r == RT) {                                       // "10" in five columns
        static const uint8_t TEN[5] = {0x1F, 0x00, 0x1F, 0x11, 0x1F};
        glyph(ix, y + 2, TEN, 5, col);
    } else {
        char ch = r <= R9 ? (char)('2' + r) : "JQKA"[r - RJ];
        glyph(ix + 1, y + 2, glyph35(ch), 3, col);
    }
    glyph(ix, y + 8, SUIT_SMALL + suitOf(c) * 5, 5, col);
}

void dim(int x, int y, int w, int h) {
    static const uint8_t DIM[16] = {INK, SILVER, INK, FELT_DK, FELT, SILVER, WINE, WINE,
                                    WOOD, WOOD, NAVY, INK, WOOD, SILVER, FX_A, FX_B};
    remapRect(x, y, w, h, DIM);
}

// ---------------------------------------------------------------------------
// Chips: $1 white, $5 red, $10 blue, $25 green, $100 black, $500 wine, $1000 gold.
// ---------------------------------------------------------------------------
static const uint8_t CHIP_BODY[7] = {WHITE, RED, BLUE, FELT_LT, INK, WINE, GOLD};
static const uint8_t CHIP_EDGE[7] = {BLUE, WHITE, WHITE, WHITE, GOLD, GOLD, INK};
static const uint8_t CHIP_SHADE[7] = {SILVER, WINE, NAVY, FELT_DK, INK, INK, WOOD};
static const uint8_t CHIP_LABEL[7] = {WHITE, SKIN, CYAN, WHITE, NAVY, RED, WHITE};
static const int32_t CHIP_VALUE[7] = {1, 5, 10, 25, 100, 500, 1000};

int chipDenom(int32_t amount) {
    for (int i = 6; i >= 0; i--) if (amount >= CHIP_VALUE[i]) return i;
    return 0;
}

// A 9 px chip in perspective (the casino chip family: tools/art/chip9_*.txt):
// sprites in placeholder colours - WHITE body, BLUE edge inserts, SILVER
// shade, CYAN lit label - that the denomination's remap replaces. Stacked
// 2 px apart, each face covers the rim of the one below; the lower chips
// alternate two cuts, so their inserts make a countable pattern.
void chip(int cx, int y, uint8_t d, bool top) {
    uint8_t rm[16];
    for (uint8_t i = 0; i < 16; i++) rm[i] = i;
    rm[WHITE] = CHIP_BODY[d]; rm[BLUE] = CHIP_EDGE[d]; rm[SILVER] = CHIP_SHADE[d]; rm[CYAN] = CHIP_LABEL[d];
    if (top) sprite4(CHIP9_TOP, cx - 4, y, rm);
    else sprite4((y >> 1) & 1 ? CHIP9_SIDE_ALT : CHIP9_SIDE, cx - 4, y + 2, rm);
}

void chipStack(int cx, int baseY, int32_t amount, uint8_t maxChips) {
    uint8_t chips[16], n = 0;
    for (int d = 6; d >= 0 && n < 16; d--)
        while (amount >= CHIP_VALUE[d] && n < 16) { chips[n++] = (uint8_t)d; amount -= CHIP_VALUE[d]; }
    if (!n) return;
    uint8_t first = n > maxChips ? (uint8_t)(n - maxChips) : 0;   // the top of tall stacks
    for (uint8_t i = first; i < n; i++)
        chip(cx, baseY - 2 * (i - first), chips[i], i == n - 1);
}

// A seat's chip, 9x9, in the casino chips' look (a lit label, insert dashes,
// the rim's shade at the lower right): two pixels a byte, low nibble first;
// 0 clear, 1 ink, 2 the seat's colour, 3 its shade, 4 its lit label, 5 its inserts.
//   ..kkkkk..
//   .kbeeebk.
//   kbbbbbbbk
//   kebhhhbek
//   kebhhhbek
//   kebhhhbek
//   kbbbbbbsk
//   .kbeeesk.
//   ..kkkkk..
static const uint8_t AVATAR[41] = {0x00, 0x11, 0x11, 0x01, 0x00, 0x21, 0x55, 0x25, 0x01, 0x21, 0x22, 0x22, 0x22, 0x11, 0x25, 0x44, 0x24, 0x15, 0x51, 0x42, 0x44, 0x52, 0x11, 0x25, 0x44, 0x24, 0x15, 0x21, 0x22, 0x22, 0x32, 0x01, 0x21, 0x55, 0x35, 0x01, 0x00, 0x11, 0x11, 0x01, 0x00};
// Per seat (SEAT_COLOUR's order): shade, label, inserts.
static const uint8_t SEAT_ROLE[6][3] = {{WINE, SKIN, WHITE}, {NAVY, CYAN, WHITE}, {WOOD, WHITE, INK},
                                        {BLUE, WHITE, NAVY}, {NAVY, WHITE, NAVY}, {WOOD, WHITE, WOOD}};

void avatar(int cx, int cy, uint8_t colour) {
    uint8_t s = colour % 6;
    const uint8_t col[6] = {0, INK, SEAT_COLOUR[s], SEAT_ROLE[s][0], SEAT_ROLE[s][1], SEAT_ROLE[s][2]};
    for (int j = 0, n = 0; j < 9; j++)
        for (int i = 0; i < 9; i++, n++) {
            uint8_t v = (AVATAR[n >> 1] >> ((n & 1) << 2)) & 15;
            if (v) gfx_pixel(cx - 4 + i, cy - 4 + j, col[v]);
        }
}

// The dealer button, round from the rounded-rect corner table: at r = w / 2
// it draws a pixel-art circle, so CHGfx's circle code needn't be linked.
void button(int cx, int cy) {
    panel(cx - 3, cy - 3, 7, 7, 3, WHITE, INK);
    // A tiny D.
    gfx_vline(cx - 1, cy - 1, 3, INK);
    gfx_pixel(cx, cy - 1, INK); gfx_pixel(cx, cy + 1, INK); gfx_pixel(cx + 1, cy, INK);
}

}  // namespace art
