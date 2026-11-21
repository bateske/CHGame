// The screen, in the secret agent style the SD apps share (Agent.h): a test
// instrument's amber on brown-black, every element a reading. See Ui.h.
//
// It is drawn only between the bench's steps, never inside one: the panel
// shares SPI1 with the card, and a test that measures the card on a quiet
// bus must have one (Bench.h: hold).
#include <CHGame.h>
#include <string.h>
#include "Ui.h"
#include "Agent.h"
#include "Bench.h"
#include "Probe.h"

namespace ui {

using agent::tiny;
using agent::tinyR;
using agent::centred;
enum : uint8_t {
    BG = agent::BG, PALE = agent::PALE, GRID = agent::GRID, MID = agent::MID, LIVE = agent::LIVE,
    DIM = agent::DIM, RED = agent::ALERT, PANEL = agent::PANEL,
    GREEN, GOLD,
};
// The agent's roles in a bench instrument's amber (RGB444), then pass green
// and warning gold.
static const uint16_t PALETTE[16] = {
    0x100,
    0xFEB,      // PALE
    0x420,      // GRID
    0x850,      // MID
    0xFB3,      // LIVE
    0xA86,      // DIM
    0xF32,      // ALERT
    0x310,      // PANEL
    0x5E5,      // GREEN: pass
    0xFD2,      // GOLD: warn
};

// ---- Layout ----------------------------------------------------------------------
const int TAB_Y = 14;
const int BODY_Y = 22;
const int LINES = 15, LINE_H = 6;               // the log, in the 3x5 font
const int COLS = 31;                            // 3x5 characters across (4 px each, from x = 2)
const int TASK_Y = 113;
const int KEYS_Y = 121;

enum Page : uint8_t { P_LOG, P_CARD, P_TESTS, PAGES };
static uint8_t page = P_LOG;
static bool dirty = true;

// ---- the log ---------------------------------------------------------------------
static const int ROWS = 30;
static char rows[ROWS][COLS + 1];
static uint32_t nRows;                          // rows ever written
static uint32_t scroll;                         // rows back from the newest

static void push(const char *s, int n) {
    char *r = rows[nRows % ROWS];
    memcpy(r, s, (size_t)n);
    r[n] = 0;
    nRows++;
}

void log(const char *line) {
    int n = (int)strlen(line);
    const char *s = line;
    bool first = true;
    while (n > 0 || first) {
        int w = first ? COLS : COLS - 2;
        int k = n < w ? n : w;
        if (k < n)                              // break at a space if there is one
            for (int j = k; j > w / 2; j--) if (s[j] == ' ') { k = j; break; }
        if (first) push(s, k);
        else {
            char t[COLS + 1] = "  ";
            memcpy(t + 2, s, (size_t)k);
            push(t, k + 2);
        }
        s += k;
        n -= k;
        while (n > 0 && *s == ' ') { s++; n--; }
        first = false;
    }
    scroll = 0;
    dirty = true;
}

// ---- text helpers ----------------------------------------------------------------
static char *num(char *p, uint32_t v) {
    char t[10];
    int n = 0;
    do { t[n++] = (char)('0' + v % 10); v /= 10; } while (v);
    while (n) *p++ = t[--n];
    *p = 0;
    return p;
}
static char *hex(char *p, uint32_t v, int digits) {
    for (int i = digits - 1; i >= 0; i--) *p++ = "0123456789ABCDEF"[(v >> (4 * i)) & 15];
    *p = 0;
    return p;
}
static char *printable(char *p, const uint8_t *s, int n) {
    for (int i = 0; i < n; i++) *p++ = (s[i] >= 32 && s[i] < 127) ? (char)s[i] : '?';
    *p = 0;
    return p;
}

// ---- pages -----------------------------------------------------------------------
static void drawLog() {
    uint32_t shown = nRows < ROWS ? nRows : ROWS;
    uint32_t n = shown < LINES ? shown : LINES;
    for (uint32_t i = 0; i < n; i++) {
        uint32_t back = scroll + n - 1 - i;     // rows back from the newest
        if (back >= shown) continue;
        const char *r = rows[(nRows - 1 - back) % ROWS];
        uint8_t c = !strncmp(r, "==", 2) ? PALE : strstr(r, "FAIL") || strstr(r, "ERR") || strstr(r, "GONE") ? RED
                  : !strncmp(r, "OK", 2) ? DIM : LIVE;
        tiny(2, BODY_Y + (int)i * LINE_H, r, c);
    }
    if (!nRows) centred(60, "PRESS A", DIM);
}

static void field(int y, const char *label, const char *value, uint8_t c = LIVE) {
    tiny(4, y, label, DIM);
    gfx_text(44, y - 1, value, c);
}

static void drawCard() {
    char t[24], *p;
    if (!bench::cardOk && !bench::haveRegs) {
        centred(52, "NO CARD", RED, 2);
        centred(74, "A: PROFILE", DIM);
        return;
    }
    const probe::Card &c = probe::card;
    int y = BODY_Y + 2;
    field(y, "TYPE", c.ver == 3 ? "MMC" : c.hc ? "SDHC/XC" : c.ver == 2 ? "SDSC V2" : "SDSC V1"); y += 10;
    if (bench::haveRegs) {
        const uint8_t *cid = bench::cid;
        p = num(t, bench::blocks >> 11); fmtStr(p, " MB");
        field(y, "SIZE", t); y += 10;
        p = hex(t, cid[0], 2); p = fmtStr(p, " "); printable(p, cid + 1, 2);
        field(y, "MAKER", t); y += 10;
        printable(t, cid + 3, 5);
        field(y, "NAME", t); y += 10;
        p = num(t, cid[8] >> 4); *p++ = '.'; num(p, cid[8] & 15);
        field(y, "REV", t); y += 10;
        uint32_t mdt = (uint32_t)(cid[13] & 15) << 8 | cid[14];
        p = num(t, 2000 + (mdt >> 4)); *p++ = '-'; num(p, mdt & 15);
        field(y, "MADE", t); y += 10;
        p = num(t, probe::csdHz(bench::csd) / 1000000); fmtStr(p, " MHZ");
        field(y, "SPEED", t); y += 10;
    }
    p = hex(t, c.ocr, 8);
    field(y, "OCR", t, DIM);
}

static void drawTests() {
    using namespace bench;
    if (!nResults) { centred(52, "NO RESULTS", DIM, 1); centred(66, "A: PROFILE", DIM); return; }
    static const char *const V[4] = {"--", "PASS", "WARN", "FAIL"};
    static const uint8_t C[4] = {GRID, GREEN, GOLD, RED};
    for (int i = 0; i < nResults && i < 11; i++) {
        int y = BODY_Y + 1 + i * 8;
        tiny(2, y, results[i].name, PALE);
        agent::chip(32, y - 1, 19, V[results[i].verdict], C[results[i].verdict]);
        tiny(55, y, results[i].note, results[i].verdict == V_FAIL ? RED : LIVE);
    }
}

// ---- the frame -------------------------------------------------------------------
bool frame(uint32_t now, int &y0, int &y1) {
    (void)now;
    if (!dirty) return false;
    dirty = false;
    gfx_clear(BG);
    agent::statusBar("SD TEST", PALE);
    if (bench::busy) agent::readout(bench::progress, LIVE, "PCT", "");
    else agent::readout(bench::haveRegs ? bench::blocks >> 11 : 0, LIVE, "MB", "");
    static const char *const NAMES[PAGES] = {"LOG", "CARD", "TESTS"};
    agent::tabs(TAB_Y, NAMES, PAGES, page);
    if (page == P_LOG) drawLog();
    else if (page == P_CARD) drawCard();
    else drawTests();
    if (bench::busy) {
        tiny(2, TASK_Y, bench::task, PALE);
        agent::gauge(60, TASK_Y + 1, 66, 3, bench::progress, 100, LIVE);
    }
    agent::keys(KEYS_Y, "A:PROFILE B:INIT");
    y0 = 0;
    y1 = GFX_H;
    return true;
}

void button(uint8_t b) {
    uint32_t shown = nRows < ROWS ? nRows : ROWS;
    if (b == RIGHT_BUTTON) page = (uint8_t)((page + 1) % PAGES);
    else if (b == LEFT_BUTTON) page = (uint8_t)((page + PAGES - 1) % PAGES);
    else if (b == UP_BUTTON && page == P_LOG && scroll + LINES < shown) scroll++;
    else if (b == DOWN_BUTTON && scroll) scroll--;
    dirty = true;
}

void showTests() { page = P_TESTS; dirty = true; }

void begin() {
    pal::init(PALETTE);
    pal::setCycling(false);
}

void goodbye() {
    gfx_wait();
    gfx_clear(BG);
    centred(56, "MENU", LIVE, 2);
}

}  // namespace ui
