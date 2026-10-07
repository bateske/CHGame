/* SPDX-License-Identifier: GPL-3.0-or-later
 * The screen. CHSDtoUSB's instrument panel, in the "secret agent" style its
 * Agent.h carries (a spy's wristwatch: every element is a reading, nothing is
 * decoration), fed by the serial protocol instead of SD blocks. See Ui.h.
 *
 * A frame is drawn only when something changed or a short animation runs,
 * and only between commands or between two blocks of a long one (the panel
 * shares SPI1 with the card). The top part (status, gauge, graph, totals) is
 * redrawn whole; the panel below only when what it shows changed, and only
 * then flushed. The graph is written straight into the framebuffer, two
 * columns a byte; text is CHGfx's 5x7 and the library's 3x5, the speed
 * seven-segment digits.
 *
 * No particles: an event gets a beep (soft for files, louder for the card
 * and the website), and a big one (linked, synced, a failure) a Sizzle
 * banner over the graph.
 */
#include <CHGame.h>
#include <string.h>
#include "Ui.h"
#include "Agent.h"
#include "Fx.h"
#include "Sounds.h"
#include "Monitor.h"
#include "Qr.h"
#include "Shapes.h"

extern "C" uint16_t transfer_stack_free(void);          // the stack's low-water mark (Memory.cpp)
const uint8_t *gfx__builtinGlyph(char ch);               // CHGfx's 5x7 glyphs (its CHGfx_internal.h)

namespace ui {

// ---- Palette ------------------------------------------------------------------
// The secret agent chrome in its house slots (Agent.h), then the panel's own
// colours. The website's dark glass, lime, grey-greens and coral (the first
// screen's five colours), widened to sixteen: RGB444.
using agent::tiny;
using agent::tinyR;
using agent::tinyW;
using agent::wipe;
using agent::centred;
enum : uint8_t {
    BG = agent::BG, PALE = agent::PALE, GRID = agent::GRID, MID = agent::MID, LIME = agent::LIVE,
    DIM = agent::DIM, CORAL = agent::ALERT, PANEL = agent::PANEL,
    GOLD, MINT, WFILL, RMID, RFILL, AQUA, WMID, GFILL,
};
static const uint16_t PALETTE[16] = {
    0x111,      // BG: the website's glass
    0xEFD,      // PALE
    0x343,      // GRID: its dark grey-green
    0x6A4,      // MID
    0xCE8,      // LIME: its accent; what goes to the card
    0x9A9,      // DIM: its grey-green
    0xE86,      // CORAL: its warning
    0x232,      // PANEL
    0xEE5,      // GOLD: the card checking itself
    0x5DA,      // MINT: what comes back from the card
    0x463,      // WFILL: under the lime line
    0x3A7,      // RMID
    0x254,      // RFILL: under the mint line
    0x6CC,      // AQUA: the link and the directories
    0x8B5,      // WMID
    0x762,      // GFILL: under the gold line
};

// ---- Layout -------------------------------------------------------------------
const int GAUGE_Y = 12;                        // the file's progress or the card's fill, 2 px
const int GY = 16, GH = 46;                    // graph rows GY .. GY + GH - 1
const int GB = GY + GH - 1;                    // its bottom row
const int STRIP_Y = GB + 2;                    // what each slice carried, 2 px
const int SUM_Y = STRIP_Y + 4;                 // totals line (Tiny)
const int TAB_Y = SUM_Y + 8;                   // page tabs (Tiny)
const int PAGE_Y = TAB_Y + 8;                  // page body
const int HOST_Y = 72;                         // "SEARCHING FOR HOST..." on the scope (its dots walk)
const int SCOPE_BOTTOM = HOST_Y + 7;           // the scope's top region reaches past that line, so its
                                               // animated dots are flushed every frame (above PRESS A at 80)
const int LINES = 4, LINE_H = 9;
const int KEY_Y = 121;                         // what B and START do
const int INTRO = 15;                          // frames of the opening sweep

enum Page : uint8_t { P_LOG, P_STATS, P_CARD, PAGES };
static uint8_t page = P_LOG, scroll = 0;

// ---- Text -----------------------------------------------------------------------
static inline char *put(char *p, const char *s) { return fmtStr(p, s); }
static char *num(char *p, uint32_t v) {
    char t[10];
    int n = 0;
    do { t[n++] = (char)('0' + v % 10); v /= 10; } while (v);
    while (n) *p++ = t[--n];
    *p = 0;
    return p;
}
// A size as 3 significant digits: 512B 12.3K 357M 1.23G. v counts 1024^u bytes.
static char *size(char *p, uint32_t v, int u = 0) {
    static const char UNIT[] = "BKMGT";
    uint32_t frac = 0;                                   // what is below one unit, in 1/1024
    while (v >= 1000 && u < 4) { frac = v & 1023; v >>= 10; u++; }
    p = num(p, v);
    if (u && v < 100) {
        uint32_t h = frac * 100 >> 10;
        *p++ = '.';
        *p++ = (char)('0' + h / 10);
        if (v < 10) *p++ = (char)('0' + h % 10);
    }
    *p++ = UNIT[u];
    *p = 0;
    return p;
}
// A count in at most 4 characters: 9999, 123K, 45M.
static char *count(char *p, uint32_t v) {
    if (v < 10000) return num(p, v);
    if (v < 1000000) return put(num(p, v / 1000), "K");
    return put(num(p, v / 1000000), "M");
}
// a * scale / b without 64-bit division: both are halved until it fits.
static uint32_t ratio(uint32_t a, uint32_t b, uint32_t scale) {
    while (a > 0xFFFFFFFFu / scale) { a >>= 1; b >>= 1; }
    return b ? a * scale / b : 0;
}

static void small(int x, int y, const char *s, uint8_t c) { gfx_text(x, y, s, c); }   // 5x7, y = top
// The same font with its eighth row (gfx_text stops at seven and clips the
// tails of g, j, p, q and y): for sentences. glyph() is the library's.
static void prose(int x, int y, const char *s, uint8_t c) {
    for (; *s; s++, x += 6) glyph(x, y, gfx__builtinGlyph(*s), 5, c);
}
static void proseC(int y, const char *s, uint8_t c) { prose(64 - ((int)strlen(s) * 6 - 1) / 2, y, s, c); }
// The alert box with its title, the lines drawn after it in prose (so their
// descenders survive): agent::alert's with empty lines, at its two-line height.
static void alertBox(int top, const char *title, bool two, uint8_t c) {
    agent::alert(top, title, "", two ? "" : nullptr, c);
}

// ---- Direct framebuffer spans (the graph's inner loop) -------------------------
static inline void vspan(int x, int y0, int y1, uint8_t c) {   // rows y0..y1, y0 <= y1
    uint8_t *p = gfx_fb + y0 * GFX_FB_STRIDE + (x >> 1);
    if (x & 1) {
        uint8_t v = (uint8_t)(c << 4);
        for (int y = y0; y <= y1; y++, p += GFX_FB_STRIDE) *p = (uint8_t)((*p & 0x0F) | v);
    } else {
        for (int y = y0; y <= y1; y++, p += GFX_FB_STRIDE) *p = (uint8_t)((*p & 0xF0) | c);
    }
}
static inline void dot(int x, int y, uint8_t c) {
    uint8_t *p = gfx_fb + y * GFX_FB_STRIDE + (x >> 1);
    *p = x & 1 ? (uint8_t)((*p & 0x0F) | (c << 4)) : (uint8_t)((*p & 0xF0) | c);
}

// ---- Events, as the log and the graph show them ---------------------------------------
struct EvLook { const char tag[5]; uint8_t c; };
static const EvLook LOOK[] = {
    {"", DIM},      {"PUT", LIME},  {"GET", MINT},  {"CHK", GOLD},   {"DIR", LIME},   {"LIST", AQUA},
    {"LINK", AQUA}, {"CARD", PALE}, {"RCVR", GOLD}, {"ABRT", CORAL}, {"STOP", CORAL}, {"SYNC", GOLD},
    {"MENU", GOLD}, {"FAIL", CORAL}, {"DEL", CORAL},
};

// The text of an event line: name (5x7) and value (Tiny, right).
static void evText(const mon::Event &e, char *name, char *val) {
    put(name, e.name);
    *val = 0;
    switch (e.type) {
        case mon::EV_PUT:
            if (e.live == 2) put(val, "CHECK");
            else if (e.live && e.value) {
                uint32_t pc = ratio(e.done, e.value, 100);
                put(num(val, pc > 99 ? 99 : pc), "%");
            } else size(val, e.value);
            return;
        case mon::EV_GET: case mon::EV_CHK: size(val, e.live ? e.done : e.value); return;
        case mon::EV_ABORT: size(val, e.done); return;
        case mon::EV_LIST: num(val, e.value); return;
        case mon::EV_LINK: num(put(val, "V"), e.value); return;
        case mon::EV_SYNC: if (e.value) put(num(val, e.value), e.value == 1 ? " FILE" : " FILES"); return;
        case mon::EV_FAIL: num(put(val, "E"), e.value); return;
    }
}

// ---- Rates over the last second, from two 500 ms samples ------------------------------
struct Sample { uint32_t t, in, out, chk, busy; };
static Sample smp[3];
static uint32_t nextSample = 0;
static uint32_t rateIn, rateOut, rateChk, activePc;   // KB/s, KB/s, KB/s, %

static void sampleRates(uint32_t now) {
    if ((int32_t)(now - nextSample) < 0) return;
    nextSample = now + 500;
    smp[0] = smp[1];
    smp[1] = smp[2];
    smp[2] = {now, mon::st.bytesIn, mon::st.bytesOut, mon::st.bytesChk, mon::st.busyUs};
    // The samples land between commands, so the window is a second or a little more.
    uint32_t ms = smp[2].t - smp[0].t;
    if (!ms) return;
    rateIn = ratio(smp[2].in - smp[0].in, ms, 1000) >> 10;
    rateOut = ratio(smp[2].out - smp[0].out, ms, 1000) >> 10;
    rateChk = ratio(smp[2].chk - smp[0].chk, ms, 1000) >> 10;
    uint32_t b = (smp[2].busy - smp[0].busy) / (ms * 10);
    activePc = b > 100 ? 100 : b;
}

// ---- Status bar -----------------------------------------------------------------------
static void sdIcon(int x, int y, uint8_t body, uint8_t label) {
    gfx_hline(x + 2, y, 5, body);
    gfx_hline(x + 1, y + 1, 6, body);
    gfx_fillRect(x, y + 2, 7, 7, body);
    dot(x + 3, y + 1, GOLD);
    dot(x + 5, y + 1, GOLD);
    gfx_fillRect(x + 1, y + 4, 5, 4, label);
}

// ---- The scope: what the screen does while no website is talking -----------------------------
// Instead of an empty graph (no website yet, or a website that has gone
// quiet for a minute): a sweep going round, contacts drifting through that
// light up as it passes, a scanner running along the gauge row, the time
// waited, and the one thing to do about it (A: the website's QR code).
//
// A contact comes by every few seconds, now and then two: mostly plain
// pings, and between a handful of those one of something sillier, in turn:
// an airplane, a boat, a rocket, a rabbit, a banana (Shapes.h). As on a
// real scope, a contact is painted where the sweep found it and sits there
// fading until the sweep comes round and paints it where it is now. The
// Konami code on the scope (up up down down left right left right A B) jams
// it: grape jelly oozes down over everything, and once the screen is covered
// the show starts over, with the opening sweep.
static uint32_t scopeT0;                                 // millis() when the scope came up (the WAIT readout)
static uint8_t beam;                                     // the sweep's angle, in 1/256 turns
static uint32_t sweeps;                                  // turns so far (shown up to 99999)
static uint32_t waited, waitTick;                        // seconds since the scope came up (counted past millis()'s wrap), and the last whole one
static bool maxed;                                       // a readout at its limit: the rainbow cycles for it

// ---- The long wait ----------------------------------------------------------------------
// Hello, reader. If you are here because a CHGame sat on this screen long
// enough to find out, or because you read everything: the WAIT readout tops
// out at 99:59 (an hour and forty minutes), SWEEP at 99999 turns (just under
// four days), and the seconds in the status bar at 9,999,999 (115 days,
// counted past the clock's own wrap at 49.7 days). Each limit, once reached,
// is drawn in the library's cycling rainbow, and with the last one the whole
// scope turns rainbow too, and the search line says hello. Nobody will see
// it; it is here for you. UI_LONG_WAIT 0 compiles the rainbow out (the
// readouts then just stop at their limits) should a future feature need the
// hundred-odd bytes.
#ifndef UI_LONG_WAIT
#define UI_LONG_WAIT 1
#endif
static const uint32_t WAIT_MAX = 5999, SWEEP_MAX = 99999, SECS_MAX = 9999999;
static bool scopeWas, jammed, jamCovered;               // jamCovered: the jelly is over everything, waiting for a key
struct Contact {
    int16_t x, y, vx, vy;                                // where it is, from the centre, in 1/16 px
    int8_t sx, sy;                                       // where the sweep last painted it, in px
    uint8_t glow, kind;                                  // how long ago that was; what it is (0: a ping)
    bool live;
};
static Contact contacts[3];
static const uint8_t ECHO = 28;                          // frames an echo lasts: a third of the sweep's turn
static uint32_t nextSpawn;                               // millis() of the next contact
static uint8_t pingsLeft, nextShape = 1;                 // plain pings before the next shape; which shape
static uint8_t konami;                                   // how much of the code has been keyed
static uint8_t ooze[64];                                 // the jelly's lower edge, per two columns
static uint8_t jamT;                                     // frames of the jam so far: the lettering's dance
static bool qrShown, qrDrawn;                            // the website's QR code fills the screen
static uint32_t payoffT0;                                // the "done" card: when it came up (0: not showing)
static bool payoffShown;                                 // ... for this job
static uint8_t introT;                                   // frames of the opening sweep drawn so far

static const int SCOPE_R = 25;

// A contact enters at the rim just ahead of the sweep, so it is painted
// within the second, and crosses in six to twelve seconds: three or four
// paintings on its way.
static void spawn(Contact &c, uint8_t kind) {
    int a = beam + 24 + (int)(fx::rnd() % 16);
    c.x = (int16_t)(fx::icos(a) * (SCOPE_R - 6) / 16);  // (256ths of a pixel * 16 / 256)
    c.y = (int16_t)(fx::isin(a) * (SCOPE_R - 6) / 16);
    int b = a + 128 + (int)(fx::rnd() % 64) - 32;
    int sp = 2 + (int)(fx::rnd() % 3);
    c.vx = (int16_t)(fx::icos(b) * sp / 256);
    c.vy = (int16_t)(fx::isin(b) * sp / 256);
    c.glow = 0;
    c.kind = kind;
    c.live = true;
}

static void jamPalette(bool on);
static void jamStart() {
    jammed = true;
    jamCovered = false;
    jamT = 0;
    memset(ooze, 0, sizeof ooze);
    jamPalette(true);
    audio::sfx(Sfx::Jam);
}

static void jamPalette(bool on) {                        // three graph fills, unused here, turn grape
    pal::setFx(WFILL, on ? 0x63A : PALETTE[WFILL]);      // the jelly
    pal::setFx(GFILL, on ? 0xA6D : PALETTE[GFILL]);      // its glistening tips, the lettering's middle
    pal::setFx(RMID, on ? 0xD9F : PALETTE[RMID]);        // the lettering's light
}

static void startShow(uint32_t now) {
    sweeps = 0;
    waited = 0;
    waitTick = now;
    konami = 0;
    nextSpawn = now + 1500;
    pingsLeft = 2 + (uint8_t)(fx::rnd() % 3);
    if (jammed) { jammed = jamCovered = false; jamPalette(false); }
    if (maxed) { maxed = false; pal::setCycling(false); pal::setFx(WMID, PALETTE[WMID]); pal::setFx(GFILL, PALETTE[GFILL]); }
    for (auto &c : contacts) c.live = false;
}

// Is the contact in the wedge the beam swept this frame?
static bool swept(const Contact &c, uint8_t b) {
    int px = c.x / 16, py = c.y / 16;
    int ax = fx::icos(b - 3), ay = fx::isin(b - 3), bx = fx::icos(b), by = fx::isin(b);
    return ax * py - ay * px >= 0 && px * by - py * bx >= 0 && px * bx + py * by > 0;
}

static const char *cardWord(uint8_t error) {
    return error == 3 ? "NO CARD" : error == 13 ? "NOT FAT" : error == 35 ? "RECOVERY" : "CARD ERROR";
}

static void statusBar(uint32_t now, const Status &s, bool active) {
    wipe(0, 11, PANEL);
    const char *word;
    uint8_t c, body, label = BG;
    bool blink = (now / 120) & 1;
    switch (s.mode) {
        case M_CARD: word = cardWord(mon::card.error); c = CORAL; body = CORAL; break;
        case M_STANDBY:
            if (jammed) { word = "JAMMED"; c = CORAL; body = CORAL; }
            else { word = "SEARCHING"; c = AQUA; body = DIM; label = blink ? AQUA : BG; }
            break;
        case M_STOPPED: word = "STOPPED"; c = GOLD; body = GOLD; break;
        default:
            if (s.stopping) { word = "STOPPING"; c = GOLD; body = GOLD; }
            else if (mon::failed) { word = "ERROR"; c = CORAL; body = CORAL; }
            else if (jammed) { word = "JAMMED"; c = CORAL; body = CORAL; }
            else if (!active && (mon::done || (mon::progress.known && mon::progress.mode == mon::P_COMPLETE))) { word = "COMPLETE"; c = LIME; body = LIME; }
            else if (!active && now - mon::st.lastMs >= 10000) { word = "IDLE"; c = DIM; body = DIM; }
            else if (!active) { word = "READY"; c = MID; body = MID; }
            else if (mon::st.lastKind & mon::K_PUT) { word = "WRITING"; c = LIME; body = LIME; label = blink ? PALE : WFILL; }
            else if (mon::st.lastKind & mon::K_GET) { word = "READING"; c = MINT; body = MINT; label = blink ? PALE : RFILL; }
            else if (mon::st.lastKind & mon::K_CHECK) { word = "VERIFY"; c = GOLD; body = GOLD; label = blink ? PALE : BG; }
            else { word = "SCANNING"; c = AQUA; body = AQUA; label = blink ? PALE : BG; }
    }
    sdIcon(2, 1, body, label);
    small(13, 2, word, c);
    // The speed now, as a watch would show it: dark segments behind lit ones.
    // File data over the link; with none moving, the card checking itself.
    // While searching for the host: how long the search has run, in seconds.
    uint32_t v = rateIn + rateOut;
    bool out = rateOut > rateIn;
    uint8_t on = out ? MINT : LIME;
    const char *unit1 = "KB", *unit2 = "/S";
    int digits = 3;
    if (scopeWas) {                                      // how long without a host: up to seven digits
        v = waited; on = AQUA; unit1 = ""; unit2 = "SEC";
        for (uint32_t q = v; q >= 1000 && digits < 7; q /= 10) digits++;
#if UI_LONG_WAIT
        if (waited == SECS_MAX) on = WMID;               // (the rainbow's slot)
#endif
    }
    else if (!v) { v = rateChk; on = v ? GOLD : DIM; }
    else {                                               // which way the data goes: up to the PC, down to the card
        int ax = 88;
        for (int k = 0; k < 3; k++) gfx_hline(ax + 2 - k, out ? 2 + k : 8 - k, 1 + 2 * k, on);
        gfx_vline(ax + 2, out ? 5 : 2, 4, on);
    }
    if (digits == 3 && v > 999) v = 999;
    agent::seg7Num(113 - 6 * digits, 1, v, digits, on, GRID);
    tiny(115, 0, unit1, DIM);
    tiny(115, 6, unit2, DIM);
}

// The whole job as the website measures it; else the file being received, as
// far as it has come; otherwise how full the card is.
static void gauge() {
    gfx_fillRect(0, GAUGE_Y, 128, 2, GRID);
    const mon::Progress &p = mon::progress;
    if (p.known && p.total && p.done < p.total) {
        int w = (int)ratio(p.done, p.total, 128);
        gfx_fillRect(0, GAUGE_Y, w, 2, p.mode == mon::P_READ ? MINT : LIME);
        if (w) gfx_vline(w - 1, GAUGE_Y, 2, PALE);
        return;
    }
    const mon::Event *f = mon::liveFile();
    if (f && f->value) {
        int w = (int)ratio(f->done > f->value ? f->value : f->done, f->value, 128);
        gfx_fillRect(0, GAUGE_Y, w, 2, f->live == 2 ? GOLD : LIME);
        if (w) gfx_vline(w - 1, GAUGE_Y, 2, PALE);
        return;
    }
    if (!mon::card.known) return;
    uint32_t pm = mon::usedPermille();
    int used = (int)(pm * 128 / 1000);
    if (!used && mon::card.freeSectors < mon::card.sectors) used = 1;
    uint8_t c = pm >= 970 ? CORAL : pm >= 900 ? GOLD : MID;
    gfx_fillRect(0, GAUGE_Y, used, 2, c);
    if (used) gfx_vline(used - 1, GAUGE_Y, 2, pm >= 900 ? c : LIME);
}

// ---- The graph: one column per slice of traffic, newest on the right -----------------
// Its top is 16 KB/s << fullShift: the smallest of 16K ... 1M that holds
// the link's data in view with a little room (the card checking itself, in
// gold, is faster and simply reaches the top).
static uint8_t fullShift;

static inline int colHeight(uint32_t kbs) {
    if (!kbs) return 0;
    uint32_t h = (kbs * GH) >> (4 + fullShift);
    return h < 1 ? 1 : (h > GH ? GH : (int)h);
}

static uint8_t stripColour(uint8_t f, bool low) {
    if (f & mon::C_FAIL) return CORAL;
    if (low && (f & mon::K_CHECK)) return GOLD;
    if (f & mon::K_PUT) return LIME;
    if (f & mon::K_GET) return MINT;
    if (f & mon::K_CHECK) return GOLD;
    return f & mon::K_META ? AQUA : PANEL;
}

static void markGlyph(int x, uint8_t type, uint8_t c) {
    int y = GY + 1;
    switch (type) {
        case mon::EV_PUT: case mon::EV_DIR:              // +
            dot(x - 1, y + 1, c); dot(x, y + 1, c); dot(x + 1, y + 1, c); dot(x, y, c); dot(x, y + 2, c); break;
        case mon::EV_FAIL: case mon::EV_STOP: case mon::EV_ABORT:   // x
            dot(x - 1, y, c); dot(x + 1, y, c); dot(x, y + 1, c); dot(x - 1, y + 2, c); dot(x + 1, y + 2, c); break;
        default:                                         // a diamond
            dot(x, y, c); dot(x - 1, y + 1, c); dot(x + 1, y + 1, c); dot(x, y + 2, c); break;
    }
}

// The area is already clear. The fills go in column pairs (two columns share a
// framebuffer byte): the rows where both are filled are plain byte stores.
static void graph(uint32_t now) {
    static const char *const SCALE[7] = {"16K", "32K", "64K", "128K", "256K", "512K", "1M"};
    static const mon::Column NONE = {0, 0, 0};
    uint32_t n = mon::columns;
    int first = n >= 128 ? 0 : 128 - (int)n;
#define COL(x) ((x) >= first ? mon::hist[(n + (uint32_t)(x)) & 127] : NONE)

    uint32_t peak = 0;                                   // of the link's data; the card checks itself faster
    for (int x = first; x < 128; x++)
        if (!(COL(x).flags & mon::C_VERIFY) && COL(x).kbs > peak) peak = COL(x).kbs;
    for (fullShift = 0; fullShift < 6 && (14u << fullShift) < peak; fullShift++) { }

    // Grid: dotted rules at each quarter of the scale; verticals every two
    // seconds of traffic that move with the data, as Task Manager's do with time.
    for (int k = 1; k < 4; k++) {
        uint8_t *p = gfx_fb + (GB - GH * k / 4) * GFX_FB_STRIDE;
        uint8_t v = n & 1 ? (uint8_t)(GRID << 4) : GRID;
        for (int i = 0; i < GFX_FB_STRIDE; i++) p[i] = v;
    }
    for (int x = 127 - (int)(n % 16); x >= 0; x -= 16)
        for (int y = GY + (x & 1); y <= GB; y += 2) dot(x, y, GRID);
    tiny(1, GY + 1, SCALE[fullShift], DIM);

    gfx_fillRect(0, STRIP_Y, 128, 2, PANEL);
    uint8_t *strip = gfx_fb + STRIP_Y * GFX_FB_STRIDE;
    for (int x = first & ~1; x < 128; x += 2) {
        const mon::Column &a = COL(x), &b = COL(x + 1);
        // Fills start two rows under the line, which get a brighter shade.
        int ta = GB + 4 - colHeight(a.kbs), tb = GB + 4 - colHeight(b.kbs);
        uint8_t ca = a.flags & mon::C_VERIFY ? GFILL : a.flags & mon::K_PUT ? WFILL : RFILL;
        uint8_t cb = b.flags & mon::C_VERIFY ? GFILL : b.flags & mon::K_PUT ? WFILL : RFILL;
        int both = ta > tb ? ta : tb;
        uint8_t *p = gfx_fb + both * GFX_FB_STRIDE + (x >> 1);
        uint8_t v = (uint8_t)(ca | (cb << 4));
        for (int y = both; y <= GB; y++, p += GFX_FB_STRIDE) *p = v;
        if (ta < both && ta <= GB) vspan(x, ta, (both <= GB ? both : GB + 1) - 1, ca);
        if (tb < both && tb <= GB) vspan(x + 1, tb, (both <= GB ? both : GB + 1) - 1, cb);
        strip[x >> 1] = (uint8_t)(stripColour(a.flags, false) | (stripColour(b.flags, false) << 4));
        strip[(x >> 1) + GFX_FB_STRIDE] = (uint8_t)(stripColour(a.flags, true) | (stripColour(b.flags, true) << 4));
    }
    int prev = GB + 1, t = GB + 1;
    for (int x = first; x < 128; x++) {
        const mon::Column &c = COL(x);
        uint8_t f = c.flags;
        bool put = f & mon::K_PUT, verify = f & mon::C_VERIFY;   // verify: the card reading itself back, in gold
        t = GB + 1 - colHeight(c.kbs);
        if (t <= GB) {
            uint8_t mid = verify ? GOLD : put ? WMID : RMID;
            if (t + 1 <= GB) dot(x, t + 1, mid);
            if (t + 2 <= GB) dot(x, t + 2, mid);
            // The line: from this column's top to the last one's, so it reads as a line.
            uint8_t line = f & (mon::C_FAIL | mon::C_RETRY) ? CORAL : verify ? GOLD : (put ? LIME : MINT);
            if (prev > GB || prev == t) dot(x, t, line);
            else vspan(x, t < prev ? t : prev, t < prev ? prev : t, line);
        } else if (f & mon::K_META) {
            dot(x, GB, AQUA);                            // commands without file data: a tick
        }
        prev = t;
        if (f & mon::C_FAIL) vspan(x, GY, GB, CORAL);
        if (c.mark) markGlyph(x < 1 ? 1 : (x > 126 ? 126 : x), c.mark, LOOK[c.mark].c);
    }
    // The newest slice glows while commands keep coming.
    if (n && now - mon::st.lastMs < 250 && t <= GB) dot(127, t, PALE);
#undef COL
}

// ---- Totals line and pages ----------------------------------------------------------------
static void totals() {
    char b[16];
    int x = tiny(0, SUM_Y, "PUT", DIM) + 2;
    size(b, mon::st.bytesIn);
    x = tiny(x, SUM_Y, b, LIME) + 6;
    x = tiny(x, SUM_Y, "GET", DIM) + 2;
    size(b, mon::st.bytesOut);
    tiny(x, SUM_Y, b, MINT);
    const mon::Progress &p = mon::progress;
    if (p.known && p.done < p.total) {                   // the website's estimate of what is left
        fmtTime(b, (uint16_t)(p.seconds > 5999 ? 5999 : p.seconds));   // m:ss
        tinyR(127, SUM_Y, b, PALE);
        tinyR(127 - tinyW(b) - 4, SUM_Y, "LEFT", DIM);
        return;
    }
    put(num(b, activePc), "%");
    tinyR(127, SUM_Y, b, activePc ? PALE : DIM);
    tinyR(127 - tinyW(b) - 4, SUM_Y, "BUSY", DIM);
}

static void tabs(uint32_t now) {
    static const char *const NAME[PAGES] = {"EVENTS", "STATS", "CARD"};
    agent::tabs(TAB_Y, NAME, PAGES, page);
    char b[12];
    if (page == P_STATS) {                              // how long the helper has been running
        uint32_t t = now / 1000;
        char *p = num(put(b, "UP "), t / 3600);
        *p++ = ':';
        *p++ = (char)('0' + t / 600 % 6); *p++ = (char)('0' + t / 60 % 10);
        *p++ = ':';
        *p++ = (char)('0' + t / 10 % 6); *p++ = (char)('0' + t % 10);
        *p = 0;
    }
    if (page == P_STATS || (page == P_LOG && mon::events)) {
        if (page == P_LOG) {
            uint32_t shown = mon::events < (uint32_t)mon::EVENTS ? mon::events : mon::EVENTS;
            char *p = num(b, scroll + 1);
            *p++ = '/';
            num(p, shown);
        }
        int bw = tinyW(b);
        gfx_fillRect(127 - bw - 2, TAB_Y - 1, bw + 3, 7, BG);
        tinyR(127, TAB_Y, b, DIM);
    }
}

static void logPage(uint32_t now) {
    if (!mon::events) {
        prose(4, PAGE_Y + 6, "No activity yet", DIM);
        tiny(4, PAGE_Y + 18, "FILES THE WEBSITE SENDS OR", DIM);
        tiny(4, PAGE_Y + 25, "READS SHOW UP HERE BY NAME", DIM);
        return;
    }
    for (int i = 0; i < LINES; i++) {
        const mon::Event *e = mon::newest(scroll + i);
        if (!e) break;
        int y = PAGE_Y + i * LINE_H;
        const EvLook &l = LOOK[e->type];
        uint32_t age = now - e->t;
        bool fresh = scroll + i == 0 && age < 300;
        gfx_fillRect(0, y, 17, 7, fresh && ((age / 75) & 1) ? PALE : l.c);
        tiny(9 - tinyW(l.tag) / 2, y + 1, l.tag, BG);
        char name[16], val[12];
        evText(*e, name, val);
        uint8_t tc = scroll + i == 0 ? (fresh ? PALE : LIME) : (i < 2 ? PALE : DIM);
        small(20, y, name, tc);
        if (val[0]) tinyR(127, y + 1, val, e->live ? l.c : (i + scroll == 0 ? PALE : DIM));
        if (e->live) {                                   // still going: how far along
            const int w = 107;
            uint8_t c = e->live == 2 ? GOLD : l.c;
            gfx_hline(20, y + 8, w, GRID);
            if (e->live == 1 && e->type == mon::EV_PUT && e->value) {
                gfx_hline(20, y + 8, (int)ratio(e->done > e->value ? e->value : e->done, e->value, (uint32_t)w), c);
            } else {                                     // no size to measure against: a sweep
                int at = (int)((now / 40) % w);
                gfx_hline(20 + at, y + 8, 8 < w - at ? 8 : w - at, c);
            }
        }
    }
}

// A line of the card page: label (dim) value (bright) pairs.
struct Pen {
    int x, y;
    Pen &l(const char *s) { x = tiny(x, y, s, DIM) + 3; return *this; }
    Pen &v(const char *s, uint8_t c = PALE) { x = tiny(x, y, s, c) + 5; return *this; }
};

// Three columns of label and value.
static void row(int y, const char *l1, const char *v1, uint8_t c1, const char *l2, const char *v2, uint8_t c2,
                const char *l3, const char *v3, uint8_t c3) {
    tiny(0, y, l1, DIM);  tiny(22, y, v1, c1);
    tiny(54, y, l2, DIM); tiny(73, y, v2, c2);
    tiny(89, y, l3, DIM); tiny(107, y, v3, c3);
}

static void statsPage() {
    char a[16], b[16], c[16];
    const mon::Stats &s = mon::st;
    int y = PAGE_Y;
    size(a, s.bytesIn);
    count(b, s.filesIn);
    put(num(c, s.peakIn), "K");
    row(y, "PUT", a, LIME, "FILE", b, PALE, "PEAK", c, LIME);
    size(a, s.bytesOut);
    count(b, s.filesOut);
    put(num(c, s.peakOut), "K");
    row(y + 7, "GET", a, MINT, "FILE", b, PALE, "PEAK", c, MINT);
    size(a, s.bytesChk);
    count(b, s.cmds);
    put(num(c, activePc), "%");
    row(y + 14, "CHECK", a, GOLD, "CMDS", b, PALE, "BUSY", c, PALE);
    count(a, s.dirs);
    count(b, s.dups);
    count(c, s.drops);
    row(y + 21, "DIRS", a, PALE, "DUP", b, s.dups ? GOLD : PALE, "DROP", c, s.drops ? GOLD : PALE);
    count(a, s.fails);
    count(b, transfer_stack_free());
    num(put(c, "V"), 1);
    row(y + 28, "FAIL", a, s.fails ? CORAL : PALE, "STK", b, PALE, "LINK", c, AQUA);
}

static void cardPage() {
    char a[16], b[16], c[16];
    int y = PAGE_Y;
    const mon::Card &k = mon::card;
    if (k.error || !k.known) {
        prose(4, y + 6, k.error ? "No card to read" : "Card mounted", DIM);
        tiny(4, y + 18, k.error ? "PUT IN A FAT16 OR FAT32 CARD" : "ITS SIZE AND FREE SPACE COME", DIM);
        tiny(4, y + 25, k.error ? "AND START THE HELPER AGAIN" : "WITH THE WEBSITE'S HELLO", DIM);
        return;
    }
    size(a, k.sectors / 2, 1);
    size(b, k.freeSectors / 2, 1);
    put(num(c, (mon::usedPermille() + 5) / 10), "%");
    Pen{0, y}.l("SIZE").v(a).l("FREE").v(b, LIME).l("USED").v(c);
    Pen{0, y + 7}.l("VOLUME").v("FAT", AQUA).l("JOURNAL").v(k.recovered ? "REPLAYED" : "CLEAN", k.recovered ? GOLD : PALE);
    const mon::Event *f = mon::liveFile();
    Pen{0, y + 14}.l("STAGING").v(f ? (f->live == 2 ? "VERIFYING" : "RECEIVING") : "EMPTY", f ? LIME : PALE);
    Pen{0, y + 21}.l("FRAME").v("512").l("PATH").v("120").l("READ").v("480");
    if (mon::lastFail) {
        num(put(a, "E"), mon::lastFail);
        num(put(b, "CMD "), mon::lastFailCmd);
        Pen{0, y + 28}.l("LAST ERROR").v(a, CORAL).v(b, DIM);
    } else {
        Pen{0, y + 28}.l("LAST ERROR").v("NONE");
    }
}

static void scope(uint32_t now, bool searching) {
    const int cx = 64, cy = 42, R = SCOPE_R;
    while (now - waitTick >= 1000 && waited < SECS_MAX) { waitTick += 1000; waited++; }
#if UI_LONG_WAIT
    const uint8_t ring = waited == SECS_MAX ? WMID : GRID, live = waited == SECS_MAX ? WMID : LIME;
#else
    const uint8_t ring = GRID, live = LIME;
#endif
    // The scanner along the gauge row: a head running left and right, with a tail.
    gfx_fillRect(0, GAUGE_Y, 128, 2, PANEL);
    uint32_t t = now % 1500;
    bool back = t >= 750;
    int head = (int)((back ? 1500 - t : t) * 120 / 750);
    gfx_fillRect(back ? head + 8 : head - 6, GAUGE_Y, 6, 2, RFILL);
    gfx_fillRect(head, GAUGE_Y, 8, 2, AQUA);
    // The scope: rings, a dotted cross, the sweep with its fading tail.
    gfx_circle(cx, cy, R, ring);
    gfx_circle(cx, cy, 17, ring);
    gfx_circle(cx, cy, 9, ring);
    for (int d = -R; d <= R; d += 2) { dot(cx + d, cy, ring); dot(cx, cy + d, ring); }
    beam = (uint8_t)(beam + 3);
    if (beam < 3 && sweeps < SWEEP_MAX) sweeps++;
    for (int k = 6; k >= 0; k--) {
        int a = beam - 2 * k;
        uint8_t c = k == 0 ? live : k == 1 && !maxed ? WMID : k < 4 ? MID : ring;   // (WMID is the rainbow's slot)
        gfx_line(cx, cy, cx + (fx::icos(a) * R) / 256, cy + (fx::isin(a) * R) / 256, c);
    }
    // The contacts: one comes by every three or four seconds, now and then a pair.
    if ((int32_t)(now - nextSpawn) >= 0) {
        nextSpawn = now + 3000 + fx::rnd() % 1500;
        Contact *a = nullptr, *b = nullptr;
        for (auto &c : contacts) if (!c.live) { if (!a) a = &c; else if (!b) b = &c; }
        if (a) {
            uint8_t kind = 0;
            if (pingsLeft) pingsLeft--;
            else { kind = nextShape; nextShape = (uint8_t)(nextShape % SHAPE_COUNT + 1); pingsLeft = 3 + (uint8_t)(fx::rnd() % 4); }
            spawn(*a, kind);
            if (!kind && b && fx::rnd() % 5 == 0) spawn(*b, 0);
        }
    }
    // Each drifts on unseen. The sweep paints it where it is (three frames
    // after passing its middle, so the whole of a shape lies behind the
    // beam); the echo stays put and fades until the sweep comes round again.
    // One that has drifted out is gone once its last echo has faded.
    for (auto &c : contacts) {
        if (!c.live) continue;
        int nx = (c.x + c.vx) / 16, ny = (c.y + c.vy) / 16;
        bool inside = nx * nx + ny * ny <= (R - 6) * (R - 6);
        if (inside) { c.x = (int16_t)(c.x + c.vx); c.y = (int16_t)(c.y + c.vy); }
        if (inside && swept(c, beam)) { c.glow = ECHO + 3; c.sx = (int8_t)(c.x / 16); c.sy = (int8_t)(c.y / 16); }
        else if (c.glow) c.glow--;
        if (!c.glow) { if (!inside) c.live = false; continue; }
        if (c.glow > ECHO) continue;
        uint8_t col = c.glow > ECHO * 2 / 3 ? PALE : c.glow > ECHO / 3 ? live : MID;
        if (!c.kind) dot(cx + c.sx, cy + c.sy, col);      // a ping: one pixel
        else {
            const Shape &sh = SHAPES[c.kind - 1];
            glyph16(cx + c.sx - sh.w / 2, cy + c.sy - sh.h / 2, sh.rows, sh.h, col);
        }
    }
    dot(cx, cy, PALE);
    // The readings beside it.
    char b[24];
    tiny(2, 22, "LINK", DIM); tiny(2, 29, "USB CDC", AQUA);
    uint32_t shown = waited > WAIT_MAX ? WAIT_MAX : waited;
#if UI_LONG_WAIT
    bool wasMaxed = maxed;
    maxed = waited >= WAIT_MAX || sweeps >= SWEEP_MAX;
    if (maxed != wasMaxed) pal::setCycling(maxed);       // (startShow() puts the slots back)
#endif
    tiny(2, 37, "WAIT", DIM); fmtTime(b, (uint16_t)shown); tiny(2, 44, b, shown == WAIT_MAX && UI_LONG_WAIT ? WMID : PALE);
    tiny(2, 52, "CARD", DIM); tiny(2, 59, "FAT OK", LIME);
    tinyR(126, 22, "HOST", DIM);
    if (searching) tinyR(126, 29, "NONE", ((now / 400) & 1) ? DIM : GRID);
    else tinyR(126, 29, "QUIET", AQUA);
    tinyR(126, 37, "SWEEP", DIM); num(b, sweeps); tinyR(126, 44, b, sweeps == SWEEP_MAX && UI_LONG_WAIT ? WMID : PALE);
    tinyR(126, 52, "PROTO", DIM); tinyR(126, 59, "CS V1", PALE);
    // What it is doing, with its dots walking.
    char *p = put(b, waited == SECS_MAX && UI_LONG_WAIT ? "HELLO, PATIENT ONE" : searching ? "SEARCHING FOR HOST" : "WAITING FOR HOST");
    for (uint32_t i = 0; i < (now / 400) % 4; i++) *p++ = '.';
    *p = 0;
    tiny(64 - tinyW(searching ? "SEARCHING FOR HOST..." : "WAITING FOR HOST...") / 2, HOST_Y, b, PALE);
}

// A line of the jam's lettering: the 3x5 font at scale 2 in a mask, each
// letter bobbing on its own phase (Sizzle's dance), painted through a purple
// ramp with a dark ring, so it reads on the glass and on the jelly alike.
static void jamLine(const char *text, int cy) {
    const uint8_t scale = 2;
    int w = text35WidthScaled(text, scale), h = 6 * scale;
    int8_t dy[12];
    int n = (int)strlen(text);
    for (int k = 0; k < n && k < 12; k++) dy[k] = (int8_t)(((fx::isin(jamT * 10 + k * 36) * 2) >> 8) + 2);
    Mask m = maskBegin(w + 1, h + 5);
    maskText35(m, 0, 0, text, scale, dy);
    uint8_t ramp[20];
    for (int r = 0; r < h + 5 && r < 20; r++) ramp[r] = r < 3 ? PALE : r < 9 ? RMID : GFILL;
    maskDraw(m, 64 - w / 2, cy - h / 2 - 2, 0, BG, PANEL, ramp);
}

// Grape jelly, from the top, in 64 drips of two columns: each runs down at
// its own pace, pulled along by its neighbours, with a glistening tip, and
// the news in waving letters. Drawn over everything; once every drip has
// reached the bottom it stays, letters dancing, until a key is pressed (or
// the website calls: any command ends the scope and the jam with it).
static void jam(uint32_t) {
    bool covered = true;
    jamT++;
    if (jamCovered) {
        gfx_clear(WFILL);
        jamLine("WE'VE BEEN", 46);
        jamLine("JAMMED!", 70);
        if ((jamT / 12) & 1) tiny(64 - tinyW("PRESS ANY KEY") / 2, 112, "PRESS ANY KEY", PALE);
        return;
    }
    for (int i = 0; i < 64; i++) {
        int h = ooze[i] + 1 + (int)(fx::rnd() % 3);
        if (i && ooze[i - 1] > h + 5) h = ooze[i - 1] - 5;
        if (i < 63 && ooze[i + 1] > h + 5) h = ooze[i + 1] - 5;
        if (fx::rnd() % 30 == 0) h += 6;                 // a drip lets go
        if (h > GFX_H) h = GFX_H;
        ooze[i] = (uint8_t)h;
        if (h < GFX_H) covered = false;
        if (h) gfx_fillRect(2 * i, 0, 2, h, WFILL);      // (grape, for the while)
        if (h >= 3) gfx_fillRect(2 * i, h - 3, 2, h < GFX_H ? 3 : 1, GFILL);
    }
    jamLine("WE'VE BEEN", 46);
    jamLine("JAMMED!", 70);
    if (covered) jamCovered = true;
}

// The job is done and the website has nothing more to say: a card over the
// graph, for five seconds, with what was done.
static void payoff(uint32_t now) {
    const mon::Stats &s = mon::st;
    char a[16], b[16], c[16];
    uint32_t secs = (s.lastMs - s.jobT0) / 1000;
    alertBox(GY + 1, "COMPLETE", true, LIME);
    int x = 14;
    count(a, s.jobFiles);
    x = tiny(x, GY + 20, a, PALE) + 2;
    x = tiny(x, GY + 20, s.jobFiles == 1 ? "FILE" : "FILES", DIM) + 5;
    count(a, s.jobRemoved);
    if (s.jobRemoved) { x = tiny(x, GY + 20, a, PALE) + 2; x = tiny(x, GY + 20, "GONE", DIM) + 5; }
    size(b, s.jobBytes);
    x = tiny(x, GY + 20, b, LIME) + 5;
    fmtTime(c, (uint16_t)(secs > 5999 ? 5999 : secs));
    tiny(x, GY + 20, c, PALE);
    x = tiny(14, GY + 28, "VERIFIED", DIM) + 5;
    x = tiny(x, GY + 28, "CRC OK", LIME) + 6;
    put(num(a, secs ? s.jobBytes / 1024 / secs : s.jobBytes / 1024), "K/S AVG");
    tiny(x, GY + 28, a, PALE);
    (void)now;
}

// Under the scope, instead of the pages: what to do about it, large: the
// banner's lettering (the 3x5 font at scale 3 through the house gradient,
// as Sizzle paints it), standing still.
static void prompt(uint32_t) {
    const char *text = "PRESS A";
    const uint8_t scale = 3;
    int w = text35WidthScaled(text, scale), h = 6 * scale;
    Mask m = maskBegin(w + 1, h + 5);
    maskText35(m, 0, 0, text, scale);
    uint8_t ramp[24];
    for (int r = 0; r < h + 5 && r < 24; r++) ramp[r] = r < 3 ? PALE : r < h / 2 + 6 ? LIME : MID;
    maskDraw(m, 64 - w / 2, 80, 0, BG, PANEL, ramp);   // lettering rows 81-98, its shadow 99
    tiny(64 - tinyW("FOR QR CODE") / 2, 102, "FOR QR CODE", DIM);
    small(64 - ((int)sizeof QR_TITLE * 6 - 7) / 2, 111, QR_TITLE, AQUA);
}

// The website's address, for a phone: dark modules on a light screen.
static void qrScreen() {
    const int sc = 4, x0 = (GFX_W - QR_SIZE * sc) / 2, y0 = 6;
    gfx_clear(PALE);
    for (int y = 0; y < QR_SIZE; y++)
        for (int x = 0; x < QR_SIZE; x++) {
            int i = y * QR_SIZE + x;
            if (QR_BITS[i >> 3] & (0x80 >> (i & 7))) gfx_fillRect(x0 + x * sc, y0 + y * sc, sc, sc, BG);
        }
    tiny(64 - tinyW(QR_TITLE) / 2, 112, QR_TITLE, BG);
    tiny(64 - tinyW("A/B: BACK") / 2, 121, "A/B: BACK", MID);
}

// ---- Overlays for the states with nothing to graph -------------------------------------
// The graph stays visible behind, dimmed: each colour to a darker one.
// (gfx_remapRect would do it, but lives in SRAM; this runs only when idle.)
static void dimRows(int y0, int y1) {
    static const uint8_t DIMMED[16] = {BG, DIM, PANEL, GRID, WFILL, GRID, GRID, BG,
                                       WFILL, RFILL, PANEL, RFILL, PANEL, RFILL, WFILL, PANEL};
    for (uint8_t *p = gfx_fb + y0 * GFX_FB_STRIDE, *e = gfx_fb + y1 * GFX_FB_STRIDE; p < e; p++)
        *p = (uint8_t)(DIMMED[*p & 15] | (DIMMED[*p >> 4] << 4));
}

static void overlay(const Status &s) {
    const char *title, *l1 = nullptr, *l2 = nullptr;
    uint8_t c;
    if (s.exitMs) {                                      // START is down: three seconds leave
        title = "EXIT?";
        c = mon::transferActive ? CORAL : GOLD;
        l1 = mon::transferActive ? "TRANSFER ACTIVE!" : "Hold START: menu";
        l2 = "Release to remain";
    } else switch (s.mode) {
        case M_CARD:
            title = mon::card.error == 3 || mon::card.error == 13 || mon::card.error == 35
                        ? cardWord(mon::card.error) : "CARD ERR";
            c = CORAL;
            if (mon::card.error == 3) { l1 = "Insert a card"; l2 = "and start again"; }
            else if (mon::card.error == 13) { l1 = "Card needs FAT16"; l2 = "or FAT32 format"; }
            else if (mon::card.error == 35) { l1 = "Back the card up"; l2 = "See the website"; }
            else { l1 = "Check the card"; l2 = "and start again"; }
            break;
        case M_STOPPED: title = "STOPPED"; c = GOLD; l1 = "The card is safe"; l2 = "Reconnect website"; break;
        default: return;
    }
    dimRows(GY, STRIP_Y + 2);
    int top = GY + (l2 ? 5 : 9);
    alertBox(top, title, l2 != nullptr, c);
    if (l1) proseC(top + 19, l1, PALE);
    if (l2) proseC(top + 27, l2, PALE);
    if (s.exitMs) {                                      // the hold, filling the box's lower rim
        int w = (int)(s.exitMs > 3000 ? 3000 : s.exitMs) * 106 / 3000;
        gfx_fillRect(11, top + 34, w, 2, c);
    }
}

// ---- The banner -------------------------------------------------------------------------------
// Big lettering over the graph for the moments that need saying: LINKED,
// RECOVERED, CRC ERROR, FAILED. With UI_SIZZLE the library's wave (Fx.h);
// otherwise outlined 5x7 that pops in (small, large, then settles) and
// blinks out, which is what the agent style says anyway.
static const int BANNER_Y = GY + GH / 2;
#if UI_SIZZLE
static void bannerShow(const char *text, bool red, uint8_t frames) { fx::banner(text, red ? fx::B_RED : fx::B_GREEN, BANNER_Y, frames); }
static bool bannerUp() { return fx::bannerActive(); }
static void bannerClear() { fx::clear(); }
static void bannerDraw() { fx::drawBanner(); }
void tick() { fx::update(); }
#else
static char bannerText[14];
static uint8_t bannerT, bannerFrames;
static bool bannerRed;
static void bannerShow(const char *text, bool red, uint8_t frames) {
    strncpy(bannerText, text, sizeof bannerText - 1);
    bannerText[sizeof bannerText - 1] = 0;
    bannerRed = red;
    bannerT = 0;
    bannerFrames = frames;
}
static bool bannerUp() { return bannerFrames != 0; }
static void bannerClear() { bannerFrames = 0; }
static void bannerDraw() {
    if (!bannerFrames || (bannerFrames < 10 && (bannerFrames & 2))) return;   // (the last frames blink)
    uint8_t c = bannerRed ? CORAL : LIME;
    if (bannerT < 2) centred(BANNER_Y - 3, bannerText, c);                   // pops: small, then outlined
    else agent::outlined(BANNER_Y - 7, bannerText, c, BG);
}
void tick() { if (bannerFrames) { bannerFrames--; bannerT++; } }
#endif

// ---- Frames ---------------------------------------------------------------------------------
static uint32_t lastFrame = 0xFFFF0000u, lastSig = 0, seenEvents = 0;
static uint32_t panelSig = 0, panelMs = 0, panelEvents = 0;
static bool panelValid = false;
static uint8_t lastMode = 0xFF;

void begin() {
    pal::init(PALETTE);
    pal::setCycling(false);             // no LUT rebuilds behind the card's back
}

// A, while no website is talking (searching, stopped, the card's trouble):
// the website's QR code; A or B again, or the d-pad: back. Otherwise the
// d-pad turns the pages. B is the sketch's (the cancel); here it only ends
// the Konami code, which jams the scope.
void button(uint8_t b) {
    uint32_t shown = mon::events < (uint32_t)mon::EVENTS ? mon::events : mon::EVENTS;
    static const uint8_t CODE[10] = {UP_BUTTON, UP_BUTTON, DOWN_BUTTON, DOWN_BUTTON, LEFT_BUTTON, RIGHT_BUTTON,
                                     LEFT_BUTTON, RIGHT_BUTTON, A_BUTTON, B_BUTTON};
    if (jammed && jamCovered) {                          // any key clears the jam; the opening sweep uncovers the scope
        startShow(millis());
        introT = 0;
        lastSig = 0;
        panelValid = false;
        return;
    }
    if (scopeWas && !qrShown) {
        konami = b == CODE[konami] ? (uint8_t)(konami + 1) : (b == CODE[0] ? 1 : 0);
        if (konami == 9) return;                         // the A of the code is not the QR's
        if (konami == 10) { konami = 0; if (!jammed) jamStart(); return; }
        if (!(b & (A_BUTTON | B_BUTTON))) return;        // the d-pad has no page to turn here
    }
    if (qrShown && (b & B_BUTTON)) { qrShown = false; lastSig = 0; panelValid = false; return; }   // B backs out too
    if (b & B_BUTTON) return;
    if (b & A_BUTTON) {
        if (lastMode == M_READY || lastMode == M_BOOT) return;
        qrShown = !qrShown;
    }
    else if (qrShown) qrShown = false;
    else if (b == RIGHT_BUTTON) { page = (uint8_t)((page + 1) % PAGES); }
    else if (b == LEFT_BUTTON) { page = (uint8_t)((page + PAGES - 1) % PAGES); }
    else if (b == DOWN_BUTTON && page == P_LOG && scroll + LINES < shown) scroll++;
    else if (b == UP_BUTTON && page == P_LOG && scroll) scroll--;
    else return;
    audio::sfx(Sfx::Page);
    lastSig = 0;
    panelValid = false;
}

// What the monitor has to say: a beep, and for the big moments a banner over
// the graph. (The log's chip flashes by itself, logPage().)
static void announce() {
    for (uint8_t i = 0; i < mon::saidCount; i++) {
        switch (mon::said[i]) {
            case mon::EV_PUT: case mon::EV_DIR: audio::sfx(Sfx::FileNew); break;
            case mon::EV_GET: case mon::EV_CHK: case mon::EV_LIST: audio::sfx(Sfx::FileTouch); break;
            case mon::EV_DEL: audio::sfx(Sfx::FileGone); break;
            case mon::EV_DONE: case mon::EV_GOT: audio::sfx(Sfx::FileDone); break;
            case mon::EV_CARD: audio::sfx(Sfx::CardIn); break;
            case mon::EV_LINK: bannerShow("LINKED", false, 50); audio::sfx(Sfx::Connect); break;
            case mon::EV_RECOVER: bannerShow("RECOVERED", false, 60); audio::sfx(Sfx::Big); break;
            case mon::EV_ABORT: case mon::EV_STOP: audio::sfx(Sfx::Stop); break;
            case mon::EV_SYNC: audio::sfx(Sfx::Sync); break;   // (the job's end has its own card)
            case mon::EV_FAIL:
                if (!mon::card.error) bannerShow(mon::lastFail == 34 ? "CRC ERROR" : "FAILED", true, 60);
                audio::sfx(Sfx::Fail);
                break;
        }
    }
    mon::saidCount = 0;
    for (; seenEvents < mon::events; seenEvents++)
        if (scroll) scroll++;                            // keep the lines being read in place
    uint32_t shown = mon::events < (uint32_t)mon::EVENTS ? mon::events : mon::EVENTS;
    if (scroll + LINES > shown) scroll = shown > LINES ? (uint8_t)(shown - LINES) : 0;
}

// The bottom panel (tabs, page and keys) is redrawn only when what it shows
// changed, and at most twice a second unless an event just came in: its text
// is most of a frame's drawing. Rows it leaves alone are not flushed either.
static uint32_t panelSigOf(uint32_t now, const Status &s) {
    uint32_t h = 2166136261u;
    auto mix = [&h](uint32_t v) { h = (h ^ v) * 16777619u; };
    mix(page); mix(scroll); mix(mon::events); mix(s.mode); mix(scopeWas);
    if (scopeWas) return h;                              // the prompt stands still
    if (page == P_LOG) {
        for (int i = 0; i < LINES; i++) {
            const mon::Event *e = mon::newest(scroll + i);
            if (!e) break;
            mix(e->t); mix(e->done); mix(e->value); mix(e->type); mix(e->live);
            if (e->live && !(e->live == 1 && e->type == mon::EV_PUT && e->value)) mix(now / 40);   // the sweep
            if (!i && !scroll && now - e->t < 300) mix(now / 75);   // a new event's chip flashes
        }
    } else if (page == P_STATS) {
        const mon::Stats &s = mon::st;
        mix(s.bytesIn >> 10); mix(s.bytesOut >> 10); mix(s.bytesChk >> 12); mix(s.cmds >> 3); mix(s.filesIn);
        mix(s.filesOut); mix(s.peakIn); mix(s.peakOut); mix(activePc); mix(s.dirs); mix(s.dups); mix(s.drops);
        mix(s.fails); mix(now / 1000);
    } else {
        const mon::Event *f = mon::liveFile();
        mix(mon::card.freeSectors); mix(mon::card.sectors); mix(mon::card.known); mix(mon::card.error);
        mix(mon::lastFail); mix(f ? f->live : 0);
    }
    return h;
}

#ifdef CHSIM
Perf perf;
#endif

bool frame(uint32_t now, const Status &s, bool force, int &y0, int &y1) {
    sampleRates(now);
    if (s.mode == M_BOOT) return false;                  // the splash stays until the card has answered
    if (s.mode != lastMode) {
        lastMode = s.mode;
        lastSig = 0;
        bannerClear();                                   // (a box, not a banner)
        if (s.mode == M_READY) qrShown = false;          // the website has called: back to work
    }
    bool qr = qrShown && !s.exitMs;
    if (qr) {                                            // a still: drawn once, until a key or the website
        if (qrDrawn && !force) return false;
        gfx_wait();
        qrScreen();
        qrDrawn = true;
        panelValid = false;
#ifdef CHSIM
        perf.frames++;
#endif
        y0 = 0;
        y1 = GFX_H;
        return true;
    }
    qrDrawn = false;
    uint32_t quiet = now - mon::st.lastMs;
    bool active = quiet < 400 && mon::columns;
    // The job's end: once the website has said SYNC and then nothing for a
    // second, the card comes up for five seconds, with its jingle.
    if (!mon::done) payoffShown = false;
    if (mon::done && !payoffShown && !active && quiet >= 1200) {
        payoffShown = true;
        payoffT0 = now;
        bannerClear();                                   // (any banner still up yields to the card)
        audio::sfx(Sfx::Done);
        audio::led(audio::LED_TRIPLE);
    }
    bool card = payoffT0 && now - payoffT0 < 5000 && mon::done && !active;
    if (!card) payoffT0 = 0;
    // The scope: with no website yet, or with one that has said nothing for a minute.
    // (B ends the Konami code and is also the sketch's cancel: a jam already under way plays out.)
    bool standby = s.mode == M_STANDBY || (s.mode == M_READY && quiet >= 60000 && !card) || (jammed && s.mode == M_STOPPED);
    if (standby && !scopeWas) { scopeT0 = now; startShow(now); }
    if (!standby && scopeWas && jammed) { jammed = false; jamPalette(false); }
    scopeWas = standby;
    const mon::Event *e0 = mon::newest(0);
    const mon::Event *f = mon::liveFile();
    bool intro = introT < INTRO;
    bool anim = intro || standby || s.exitMs || bannerUp() || mon::saidCount || (e0 && now - e0->t < 320) || active;
    uint32_t sig = mon::columns * 2654435761u ^ mon::events * 40503u ^ (e0 ? e0->t + e0->done + e0->live : 0) ^
                   (rateIn << 7) ^ (rateOut << 17) ^ (rateChk << 12) ^ activePc ^ ((uint32_t)s.mode << 28) ^
                   ((uint32_t)s.stopping << 31) ^ ((uint32_t)page << 24) ^ ((uint32_t)scroll << 20) ^
                   mon::card.freeSectors ^ mon::card.sectors ^ (uint32_t)active << 27 ^ (uint32_t)mon::failed << 26 ^
                   (f ? f->done * 31u : 0) ^ (mon::progress.done >> 6) * 2246822519u ^ mon::progress.seconds * 3266489917u ^
                   (uint32_t)card << 25 ^ (uint32_t)mon::done << 23 ^ (quiet >= 10000 ? 0x5A5Au : 0) ^
                   (page == P_STATS ? now / 1000 * 7919u : 0);                               // (its clock)
    // 5 frames a second while commands stream (a frame holds up the next
    // command by its drawing and flush, ~10 ms), 25 for a short animation
    // otherwise, none while nothing changes.
    if (!force) {
        uint32_t every = intro || standby || s.exitMs ? 40 : active ? 200 : (anim ? 40 : 100);
        if (now - lastFrame < every) return false;
        if (!anim && sig == lastSig && panelValid) return false;
    }
    lastFrame = now;
    lastSig = sig;
    announce();

    uint32_t ps = panelSigOf(now, s);
    bool panel = !panelValid || intro || jammed ||
                 (ps != panelSig && (mon::events != panelEvents || now - panelMs >= 500 || (e0 && now - e0->t < 300)));

    // The top region redrawn and flushed every frame when the panel below is
    // not. On the scope it reaches past the walking "SEARCHING FOR HOST..."
    // dots, so they animate on the panel, not just in the framebuffer.
    const int topEnd = standby ? SCOPE_BOTTOM : TAB_Y - 1;
    gfx_wait();                                          // (flushes here are blocking: nothing is in flight)
    wipe(0, panel ? GFX_H : topEnd, BG);
    statusBar(now, s, active);
    if (standby) scope(now, s.mode == M_STANDBY);
    else if (card) { gauge(); payoff(now); totals(); }
    else { gauge(); graph(now); totals(); }
    if (panel) {
        if (standby) prompt(now);
        else {
            tabs(now);
            if (page == P_LOG) logPage(now);
            else if (page == P_STATS) statsPage();
            else cardPage();
        }
        if (!standby) agent::keys(KEY_Y, s.mode == M_READY ? "B:CANCEL START:EXIT~(HOLD)" : "A:QR B:CANCEL START:EXIT~(HOLD)");
        panelSig = ps;
        panelMs = now;
        panelEvents = mon::events;
        panelValid = true;
    }
    overlay(s);
    if (!s.exitMs) bannerDraw();
    if (jammed) jam(now);
    if (intro) {                                         // the opening: a sweep uncovers the panel
        int y = introT++ * 9;
        wipe(y, GFX_H, BG);
        agent::sweep(y);
        if (introT == INTRO) panelValid = false;         // its tail is still on the bottom rows: one more full frame
    }
    y0 = 0;
    y1 = panel ? GFX_H : topEnd;
#ifdef CHSIM
    perf.frames++;
    perf.rows += (uint32_t)(y1 - y0);
#endif
    return true;
}

void splash() {
    gfx_clear(BG);
    agent::brackets(2, 34, 124, 54, 6, MID);
    agent::outlined(44, "SDtoSerial", LIME, PANEL);
    tiny(64 - tinyW("CHGAME WEB CARD LINK") / 2, 64, "CHGAME WEB CARD LINK", DIM);
    tiny(64 - tinyW("MOUNTING THE CARD") / 2, 76, "MOUNTING THE CARD", AQUA);
}

void goodbye() {
    gfx_wait();
    gfx_clear(BG);
    if (jammed) { jammed = false; jamPalette(false); }
    if (mon::done) {                                     // the job is done: say so on the way out
        agent::brackets(4, 26, 120, 76, 6, MID);
        agent::outlined(34, "COMPLETE", LIME, PANEL);
        char b[16];
        count(b, mon::st.jobFiles);
        int x = 64 - (tinyW(b) + tinyW(mon::st.jobFiles == 1 ? " FILE  ON THE CARD" : " FILES ON THE CARD")) / 2;
        x = tiny(x, 56, b, PALE) + 2;
        tiny(x, 56, mon::st.jobFiles == 1 ? "FILE  ON THE CARD" : "FILES ON THE CARD", DIM);
        centred(72, "MENU", PALE, 2);
        return;
    }
    agent::brackets(30, 44, 68, 38, 6, MID);
    centred(56, "MENU", LIME, 2);
}

}  // namespace ui
