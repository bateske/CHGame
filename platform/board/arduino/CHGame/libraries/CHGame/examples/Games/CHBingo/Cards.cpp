#pragma GCC optimize("Os")   // cold code: size over speed (hot pixel loops live in the CHGame library and CHGfx)
// The felt: the cards (the one in play and its neighbours on the carousel),
// the power meter and the jackpot either side, the buy-in's row of cards,
// and the bar under them with a little copy of every card.
#include <CHGame.h>
#include "Cards.h"
#include "Layout.h"
#include "Bingo.h"

namespace cards {

using namespace lay;

const uint8_t LETTER_COL[5] = {CYAN, RED, WHITE, FELT_LT, GOLD};
const uint8_t DAUB[DAUBERS] = {RED, BLUE, FELT_LT, CYAN, SKIN};

uint8_t daub(const Bingo &g) { return DAUB[g.opt.dauber < DAUBERS ? g.opt.dauber : 0]; }

// The glove's art has a gold cuff (GOLD, WOOD underneath).
const uint8_t *cuff(uint8_t colour) {
    static uint8_t rm[16];
    for (uint8_t i = 0; i < 16; i++) rm[i] = i;
    rm[GOLD] = colour;
    rm[WOOD] = DARKER[colour & 15];
    return rm;
}

void cellXY(uint8_t cell, int &x, int &y) {
    x = CARD_X + 2 + (cell % 5) * CELL_W + CELL_W / 2;
    y = CARD_Y + 2 + HEAD_H + (cell / 5) * CELL_H + CELL_H / 2;
}

void draw(const Bingo &g, uint8_t k, int x, int y, const Look &look) {
    if (x >= GFX_W || x + CARD_W <= 0) return;
    bool pending = g.hints() && g.pend[k] && look.cursor < 0;
    gfx_fillRect(x + 3, y + 3, CARD_W, CARD_H, FELT_DK);   // its shadow on the felt
    // The frame: rainbow while a called number waits on this card (EASY),
    // cyan while it is picked up; a raised rim otherwise.
    bool flat = pending || look.deny || look.stamp;
    uint8_t edge = flat ? (pending && !look.deny && !look.stamp ? FX_A : RED)
                 : look.cursor >= 0 ? CYAN : look.focused ? GOLD : WOOD;
    gfx_fillRect(x, y, CARD_W, CARD_H, edge);
    if (!flat) {
        gfx_hline(x + 1, y + CARD_H - 1, CARD_W - 1, DARKER[edge]);   // the rim's shaded side
        gfx_vline(x + CARD_W - 1, y + 1, CARD_H - 1, DARKER[edge]);
        gfx_rect(x + 1, y + 1, CARD_W - 2, CARD_H - 2, INK);
    }
    // The header, lit along its top; a card playing for double shows it in
    // wine and gold.
    bool dbl = g.doubleCard == k;
    uint8_t head = dbl ? WINE : NAVY;
    gfx_fillRect(x + 2, y + 2, 5 * CELL_W, HEAD_H, head);
    gfx_hline(x + 2, y + 2, 5 * CELL_W, LIGHTER[head]);
    for (int c = 0; c < 5; c++)
        glyph(x + 2 + c * CELL_W + 5, y + 3, glyph35("BINGO"[c]), 3, dbl ? FX_B : LETTER_COL[c]);
    // The cells: a white and silver checker, sunk a pixel under the header;
    // a raised blot on each daubed one, lit top left, shaded underneath.
    const uint8_t *card = g.cards[k];
    for (int r = 0; r < 5; r++) {
        int cy = y + 2 + HEAD_H + r * CELL_H;
        gfx_fillRect(x + 2, cy, 5 * CELL_W, CELL_H, WHITE);
        for (int c = 0; c < 5; c++) {
            int cx = x + 2 + c * CELL_W, i = r * 5 + c;
            if ((r + c) & 1) gfx_fillRect(cx, cy, CELL_W, CELL_H, SILVER);
            uint8_t ink = INK;
            if ((g.daub[k] >> i) & 1) {
                uint8_t blot = ((look.win >> i) & 1) ? FX_A : ((look.flash >> i) & 1) ? FX_B : i == 12 ? GOLD : daub(g);
                fillRound(cx + 1, cy + 1, CELL_W - 2, CELL_H - 2, 3, DARKER[blot]);
                fillRound(cx + 1, cy + 1, CELL_W - 2, CELL_H - 3, 3, blot);
                gfx_hline(cx + 4, cy + 2, 3, LIGHTER[blot]);
                if (blot == RED || blot == BLUE) ink = WHITE;
            }
            if (i == 12) { text35(cx + 5, cy + 3, "*", ink); continue; }
            char s[4];
            *fmtInt(s, card[i]) = 0;
            text35(cx + (card[i] < 10 ? 5 : 3), cy + 3, s, ink);
        }
    }
    gfx_hline(x + 2, y + 2 + HEAD_H, 5 * CELL_W, SILVER);  // the header's shadow on the cells
    // The cursor of a card picked up, a gold box (shimmering) inside its cell.
    if (look.cursor >= 0) {
        int cx = x + 2 + (look.cursor % 5) * CELL_W, cy = y + 2 + HEAD_H + (look.cursor / 5) * CELL_H;
        gfx_rect(cx, cy, CELL_W, CELL_H, INK);
        gfx_rect(cx + 1, cy + 1, CELL_W - 2, CELL_H - 2, FX_B);
    }
    // HARDCORE: VOID stamped across it, in red on a white label.
    if (look.stamp) {
        int sx = x + CARD_W / 2 - 25, sy = y + 22;
        fillRound(sx + 2, sy + 2, 50, 18, 3, INK);
        fillRound(sx, sy, 50, 18, 3, RED);
        fillRound(sx + 2, sy + 2, 46, 14, 2, WHITE);
        text35x2(sx + 10, sy + 4, "VOID", RED);
    }
}

int buyX(uint8_t i) { return 7 + i * 13; }

static void centred(int y, const char *s, uint8_t c) { text35(64 - text35Width(s) / 2, y, s, c); }

void buyIn(const Bingo &g) {
    uint8_t n = g.buyN, most = g.maxCards();
    // Nine cards in a row: the ones being bought face up, on their shadows;
    // the glove points at the last of them (Presenter).
    for (uint8_t i = 0; i < MAX_CARDS; i++) {
        int x = buyX(i), y = BUY_Y;
        if (i < n) {
            fillRound(x + 1, y - 1, 13, 17, 2, FELT_DK);
            fillRound(x - 1, y - 3, 13, 17, 2, GOLD);
            gfx_hline(x + 1, y - 3, 9, LIGHTER[GOLD]);
            gfx_hline(x + 1, y + 13, 9, WOOD);
            gfx_fillRect(x + 1, y - 1, 9, 13, WHITE);
            gfx_fillRect(x + 1, y - 1, 9, 3, NAVY);
            for (int d = 0; d < 3; d++) gfx_fillRect(x + 2 + ((i + d * 2) % 3) * 3, y + 3 + d * 3, 2, 2, RED);
        } else {
            roundRect(x, y, 11, 14, 2, i < most ? FELT_LT : FELT_DK);
        }
    }
    char buf[32], *p = fmtInt(buf, n);
    *fmtStr(p, n == 1 ? " CARD" : " CARDS") = 0;
    int w = gfx_textWidth(buf);
    const int py = BUY_Y + 20;
    panelLit(64 - w / 2 - 14, py, w + 28, 11, 3, NAVY, FX_B);
    gfx_text(64 - w / 2, py + 2, buf, GOLD);
    text35(64 - w / 2 - 10, py + 3, "<", n > 1 ? WHITE : BLUE);
    text35(64 + w / 2 + 7, py + 3, ">", n < most ? WHITE : BLUE);
    p = fmtMoney(fmtStr(buf, "COST "), (int32_t)g.priceNow() * n);
    *fmtMoney(fmtStr(p, "   POT "), g.potFor(n)) = 0;
    centred(py + 14, buf, GOLD);
    *fmtStr(fmtInt(fmtStr(buf, "THE HALL HOLDS "), RIVALS[g.opt.hall < 3 ? g.opt.hall : 0]), " MORE") = 0;
    centred(py + 21, buf, FELT_LT);
}

// Up to seven cards get cells 3 px wide (a card's proportions); eight or
// nine fit only at 2 px.
int miniCell(const Bingo &g) { return g.nCards <= 7 ? 3 : 2; }
int miniW(const Bingo &g) { return 5 * miniCell(g) + 2; }
int miniX(const Bingo &g, uint8_t k) {
    int pitch = miniW(g) + MINI_GAP;
    return 64 - (g.nCards * pitch - MINI_GAP) / 2 + k * pitch;
}

// A card in little: its frame (rainbow while a number waits on it in EASY,
// gold for the one in play), its header with a dot of each letter's colour,
// and a cell per number: white, daubed, or rainbow while it waits. A card
// thrown out (HARDCORE) leaves an empty slot, crossed out.
static void mini(const Bingo &g, uint8_t k, uint32_t win) {
    bool here = k == g.focus && g.live(k), pending = g.hints() && g.pend[k];
    int cw = miniCell(g), w = miniW(g);
    int x = miniX(g, k), y = here ? MINI_Y - 2 : MINI_Y;
    if (!g.live(k)) {
        fillRound(x, y + 1, w, MINI_H - 1, 2, INK);
        roundRect(x, y + 1, w, MINI_H - 1, 2, WINE);
        gfx_line(x + 3, y + 4, x + w - 4, y + MINI_H - 3, RED);
        gfx_line(x + w - 4, y + 4, x + 3, y + MINI_H - 3, RED);
        return;
    }
    gfx_fillRect(x + 1, y + 1, w, MINI_H, INK);               // its shadow on the bar
    uint8_t edge = pending ? FX_A : here ? GOLD : WOOD;
    gfx_fillRect(x, y, w, MINI_H, edge);
    gfx_fillRect(x + 1, y + 1, w - 2, 2, g.doubleCard == k ? WINE : NAVY);
    gfx_fillRect(x + 1, y + 3, w - 2, 10, WHITE);
    uint32_t wait = g.hints() ? g.pend[k] : 0;
    for (uint8_t i = 0; i < 25; i++) {
        uint8_t r = i / 5, c = i % 5;
        if (!r) gfx_pixel(x + 1 + c * cw + cw / 2, y + 1, LETTER_COL[c]);
        uint8_t col = (((win | wait) >> i) & 1) ? FX_A
                    : ((g.daub[k] >> i) & 1) ? (i == 12 ? GOLD : daub(g)) : WHITE;
        if (col != WHITE) gfx_fillRect(x + 1 + c * cw, y + 3 + r * 2, cw, 2, col);
    }
}

static bool choosing(const Bingo &g) { return g.phase == Phase::Buy || g.phase == Phase::Welcome || g.phase == Phase::Mode; }

void bar(const Bingo &g, uint32_t win, uint8_t winCard) {
    gfx_fillRect(0, BAR_Y, 128, BAR_H, NAVY);
    gfx_hline(0, BAR_Y, 128, INK);
    gfx_hline(0, BAR_Y + 1, 128, BLUE);                   // the bar's lit edge
    if (!choosing(g)) {
        for (uint8_t k = 0; k < g.nCards; k++) mini(g, k, k == winCard ? win : 0);
        return;
    }
    // At the buy-in (and the mode picker): what A does, and the jackpot.
    const char *label = g.phase == Phase::Mode ? "A:PICK" : "A:BUY IN";
    panelLit(30, BAR_Y + 2, 38, 13, 3, INK, FX_B);
    text35(49 - text35Width(label) / 2, BAR_Y + 6, label, FX_B);
    text35(99, BAR_Y + 3, "JACKPOT", SILVER);
    char buf[12];
    *fmtMoney(buf, g.jackpot) = 0;
    text35(126 - text35Width(buf), BAR_Y + 10, buf, FX_B);
}

// A button, raised off the felt: its rim, its face lit along the top, its
// letter. FELT_DK: an empty socket in the felt instead.
static void button(int x, int y, char letter, uint8_t c, uint8_t ink) {
    if (c == FELT_DK) {
        char s[2] = {letter, 0};
        fillRound(x, y + 1, 11, 7, 3, FELT_DK);
        gfx_hline(x + 3, y + 1, 5, INK);                      // its lip's shadow
        text35(x + 4, y + 2, s, ink);
        return;
    }
    fillRound(x + 1, y + 2, 11, 7, 3, INK);                   // its shadow
    fillRound(x, y + 1, 11, 7, 3, DARKER[c]);
    fillRound(x, y, 11, 6, 3, c);
    gfx_hline(x + 3, y + 1, 5, LIGHTER[c]);
    char s[2] = {letter, 0};
    text35(x + 4, y + 1, s, ink);
}

// EASY: the power meter, a glass tube in brass fittings standing on the
// felt. Twelve segments, blue to cyan to white as it fills, each rounded by
// a lit left edge and a shaded right one; gold all the way up when a
// power-up is held (FX_B shimmers), cyan while FREEZE holds the caller.
static void powerTube(const Bingo &g, bool frozen) {
    static const char *const POWER[4] = {"POWER", "WILD", "FREEZE", "2X POT"};
    uint8_t p = g.power <= POWER_KINDS ? g.power : 0;
    const char *label = frozen ? "FROZEN" : POWER[p];
    text35(SIDE_LX - text35Width(label) / 2, SIDE_Y, label, frozen ? CYAN : p ? FX_B : SILVER);
    const int x = TUBE_X, y = TUBE_Y, w = TUBE_W, h = TUBE_H;
    gfx_fillRect(x + w + 1, y - 1, 1, h + 4, FELT_DK);         // its shadow on the felt
    gfx_fillRect(x, y + h + 3, w + 2, 1, FELT_DK);
    // The glass: dark inside, a streak of reflection down its left side.
    gfx_fillRect(x, y, w, h, INK);
    gfx_vline(x + 1, y + 1, h - 2, NAVY);
    for (uint8_t i = 0; i < POWER_FULL; i++) {
        int sy = y + h - 3 - i * 3;
        uint8_t c = p ? FX_B : frozen ? CYAN : i >= g.meter ? NAVY : i < 4 ? BLUE : i < 8 ? CYAN : WHITE;
        gfx_hline(x + 2, sy, w - 4, c);
        gfx_hline(x + 2, sy + 1, w - 4, c == NAVY ? INK : DARKER[c]);   // each segment's underside
        gfx_pixel(x + 2, sy, c == NAVY ? NAVY : LIGHTER[c]);
        gfx_pixel(x + w - 3, sy, c == NAVY ? INK : DARKER[c]);
    }
    gfx_vline(x + 1, y + 3, 7, SILVER);                       // the glint on the glass
    gfx_pixel(x + 1, y + 11, BLUE);
    // The scale beside it, a notch every quarter.
    for (uint8_t i = 2; i < POWER_FULL; i += 3) gfx_hline(x + w + 1, y + h - 3 - i * 3, 2, FELT_LT);
    // The brass caps, top and bottom, lit from above.
    for (int cy = y - 3; cy <= y + h; cy += h + 3) {
        fillRound(x - 1, cy, w + 2, 3, 1, WOOD);
        gfx_hline(x, cy, w, GOLD);
        gfx_pixel(x + 1, cy, WHITE);
        gfx_hline(x, cy + 2, w, WINE);
    }
    button(SIDE_LX - 6, y + h + 4, 'B', p ? RED : FELT_DK, p ? WHITE : FELT);
}

// HARD: no power-ups. In their place the mode, what it pays, and what the
// buttons do now.
static void modeBadge(const Bingo &g) {
    bool core = g.mode == M_HARDCORE;
    text35(SIDE_LX - 7, SIDE_Y, "HARD", core ? RED : WHITE);
    if (core) text35(SIDE_LX - 7, SIDE_Y + 6, "CORE", RED);
    // A gold medal: what the pot is multiplied by.
    const int cx = SIDE_LX, cy = 79 + core * 2;
    gfx_fillCircle(cx + 1, cy + 1, 10, INK);
    gfx_fillCircle(cx, cy, 10, WOOD);
    gfx_fillCircle(cx, cy, 9, GOLD);
    gfx_fillCircle(cx + 1, cy + 1, 7, WOOD);
    gfx_fillCircle(cx, cy, 7, core ? WINE : NAVY);
    gfx_hline(cx - 4, cy - 8, 6, WHITE);                      // its glint
    char s[3] = {'X', (char)('0' + PAYS[g.mode < MODES ? g.mode : 0]), 0};
    text35x2(cx - 7, cy - 4, s, FX_B);
    const char *hint = g.picking ? "B:BACK" : "A:PICK";
    text35(SIDE_LX - text35Width(hint) / 2, 95, hint, g.picking ? CYAN : SILVER);
    button(SIDE_LX - 6, 101, g.picking ? 'B' : 'A', g.picking ? RED : GOLD, g.picking ? WHITE : INK);
}

// A pile of coins seen from above at an angle. A stack shows its top face
// (9x4, lit, its stamped rim, a glint that shimmers) and the edge of every
// coin under it: a gold row with a sheen down its lit left side, shaded
// right, and a dark line between one coin and the next. A coin now and then
// sits a pixel off true, so it reads as a pile, not a pillar.
static int coinOff(int j) { return j % 5 == 3 ? 1 : j % 7 == 5 ? -1 : 0; }

static void coinStack(int x, int base, int n) {
    if (n <= 0) return;
    gfx_hline(x + 1, base + 1, 9, FELT_DK);                   // its shadow on the felt
    gfx_hline(x + 3, base + 2, 6, FELT_DK);
    for (int j = 0; j < n; j++) {
        int cx = x + coinOff(j), ey = base - 1 - 2 * j;
        gfx_hline(cx, ey, 9, GOLD);
        gfx_pixel(cx + 1, ey, WHITE);
        gfx_hline(cx + 6, ey, 2, WOOD);
        gfx_pixel(cx + 8, ey, WINE);
        gfx_hline(cx + 1, ey + 1, 7, WOOD);
        gfx_pixel(cx + 7, ey + 1, WINE);
    }
    int fx = x + coinOff(n - 1), fy = base - 2 * n - 3;
    gfx_hline(fx + 1, fy, 7, GOLD);
    gfx_hline(fx + 2, fy, 3, WHITE);
    gfx_hline(fx, fy + 1, 9, GOLD);
    gfx_hline(fx, fy + 2, 9, GOLD);
    gfx_hline(fx + 2, fy + 1, 5, WOOD);                        // the stamped rim
    gfx_hline(fx + 3, fy + 1, 3, FX_B);                        // inside it, the light
    gfx_pixel(fx + 2, fy + 2, WOOD);
    gfx_pixel(fx + 6, fy + 2, WOOD);
    gfx_hline(fx + 1, fy + 3, 7, WOOD);
}

// The jackpot: its sign, and the gold under it, more of it as it grows:
// nine coins at the seed and one more for every $5, up to thirty: two
// stacks at the back, a short one in front, one coin lying loose.
static void jackpotPile(const Bingo &g) {
    panelLit(SIDE_RX - 11, SIDE_Y - 3, 23, 15, 3, WINE, GOLD);
    text35(SIDE_RX - text35Width("JACK") / 2, SIDE_Y, "JACK", FX_B);
    text35(SIDE_RX - text35Width("POT") / 2, SIDE_Y + 6, "POT", FX_B);
    int32_t n32 = 9 + (g.jackpot - JACKPOT_SEED) / 5;
    int n = (n32 < 9 ? 9 : n32 > 30 ? 30 : (int)n32) - 1;
    int front = n / 4 < 6 ? n / 4 : 6, rest = n - front;
    int left = (rest + 1) / 2 < 12 ? (rest + 1) / 2 : 12, right = rest - left < 12 ? rest - left : 12;
    coinStack(SIDE_RX - 11, 92, left);
    coinStack(SIDE_RX + 1, 90, right);
    coinStack(SIDE_RX - 6, 98, front);
    coinStack(SIDE_RX + 3, 100, 1);
    char buf[12];
    *fmtShort(buf, g.jackpot) = 0;
    text35(SIDE_RX - text35Width(buf) / 2, 104, buf, FX_B);
}

void sides(const Bingo &g, bool frozen) {
    if (g.hints()) powerTube(g, frozen);
    else modeBadge(g);
    jackpotPile(g);
}

// The start of a game: EASY, HARD or HARDCORE, what each pays and what it
// asks of you.
void modes(const Bingo &g) {
    static const char *const NAME[MODES] = {"EASY", "HARD", "HARDCORE"};
    static const uint8_t COL[MODES] = {CYAN, GOLD, RED};
    static const char *const WHAT[MODES] = {"A PICKS, THE GLOVE FINDS IT", "FIND THEM, DAUB EACH ONE",
                                            "A WRONG DAUB LOSES THE CARD"};
    for (uint8_t m = 0; m < MODES; m++) {
        int y = MODE_Y + m * MODE_PITCH;
        bool sel = m == g.mode;
        panelLit(MODE_X, y, MODE_W, 14, 3, sel ? NAVY : INK, sel ? FX_B : WOOD);
        gfx_text(MODE_X + 6, y + 4, NAME[m], sel ? COL[m] : SILVER);
        char s[8];
        *fmtInt(fmtStr(s, "POT X"), PAYS[m]) = 0;
        text35(MODE_X + MODE_W - 5 - text35Width(s), y + 5, s, sel ? GOLD : FELT_LT);
    }
    const char *what = WHAT[g.mode < MODES ? g.mode : 0];
    text35(64 - text35Width(what) / 2, MODE_Y + MODES * MODE_PITCH + 2, what, WHITE);
}

}  // namespace cards
