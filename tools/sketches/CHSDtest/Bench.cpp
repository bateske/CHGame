// Bench.cpp - see Bench.h and PROTOCOL.md.
#include <Arduino.h>
#include <CHGame.h>
#include <string.h>
#include "config.h"
#include "Bench.h"
#include "Probe.h"

namespace bench {

Result results[MAX_RESULTS];
int nResults;
bool busy;
bool hold;
uint8_t progress;
char task[24];
bool cardOk;
uint8_t cid[16], csd[16];
bool haveRegs;
uint32_t blocks;

static void (*say)(const char *);
static uint8_t blk[512] __attribute__((aligned(4)));

// ---- lines -------------------------------------------------------------------

static char ln[160];
static char *lp = ln;
static void s(const char *t) { while (*t && lp < ln + sizeof ln - 1) *lp++ = *t++; *lp = 0; }
static void dec(uint32_t v) {
    char t[11];
    int n = 0;
    do { t[n++] = (char)('0' + v % 10); v /= 10; } while (v);
    while (n && lp < ln + sizeof ln - 1) *lp++ = t[--n];
    *lp = 0;
}
static void hex(uint32_t v, int digits) {
    while (digits--) {
        uint8_t d = (v >> (4 * digits)) & 15;
        if (lp < ln + sizeof ln - 1) *lp++ = (char)(d < 10 ? '0' + d : 'A' + d - 10);
    }
    *lp = 0;
}
static void emit() { say(ln); lp = ln; *lp = 0; }
static void sayStr(const char *t) { s(t); emit(); }

static void begin_(const char *what) {
    busy = true;
    progress = 0;
    strncpy(task, what, sizeof task - 1);
    task[sizeof task - 1] = 0;
}

static void note(const char *name, uint8_t v, const char *text) {
    int i = 0;
    while (i < nResults && strcmp(results[i].name, name)) i++;
    if (i == nResults) {
        if (nResults == MAX_RESULTS) return;
        nResults++;
    }
    strncpy(results[i].name, name, sizeof results[i].name - 1);
    results[i].name[sizeof results[i].name - 1] = 0;
    results[i].verdict = v;
    strncpy(results[i].note, text, sizeof results[i].note - 1);
    results[i].note[sizeof results[i].note - 1] = 0;
}

// ---- the card ----------------------------------------------------------------

// Identification with the settings as they are; the card's registers after.
static uint8_t identify(bool regs) {
    uint8_t e = probe::init();
    probe::drain();
    cardOk = !e;
    s("INIT "); s(probe::errName(e)); s(" V"); dec(probe::card.ver); s(probe::card.hc ? " HC" : " SC");
    s(" OCR "); hex(probe::card.ocr, 8); s(" CMD0 "); dec(probe::card.cmd0Tries);
    s(" R1 "); hex(probe::card.lastR1, 2); s(" LOOPS "); dec(probe::card.loops);
    s(" MS "); dec(probe::card.us / 1000); emit();
    if (!e && regs) {
        haveRegs = !probe::reg(10, cid) && !probe::reg(9, csd);
        if (haveRegs) blocks = probe::csdBlocks(csd);
    }
    return e;
}

static void printRegs() {
    if (!haveRegs) { sayStr("REGS NONE"); return; }
    s("CID"); for (int i = 0; i < 16; i++) { s(" "); hex(cid[i], 2); } emit();
    char pnm[6];
    memcpy(pnm, cid + 3, 5);
    pnm[5] = 0;
    for (int i = 0; i < 5; i++) if (pnm[i] < 32 || pnm[i] > 126) pnm[i] = '?';
    char oid[3] = {(char)cid[1], (char)cid[2], 0};
    for (int i = 0; i < 2; i++) if (oid[i] < 32 || oid[i] > 126) oid[i] = '?';
    uint32_t psn = (uint32_t)cid[9] << 24 | (uint32_t)cid[10] << 16 | (uint32_t)cid[11] << 8 | cid[12];
    uint32_t mdt = (uint32_t)(cid[13] & 15) << 8 | cid[14];
    s("  MID "); hex(cid[0], 2); s(" OID "); s(oid); s(" PNM "); s(pnm); s(" PRV ");
    dec(cid[8] >> 4); s("."); dec(cid[8] & 15); s(" PSN "); hex(psn, 8);
    s(" MDT "); dec(2000 + (mdt >> 4)); s("-"); dec(mdt & 15); emit();
    s("CSD"); for (int i = 0; i < 16; i++) { s(" "); hex(csd[i], 2); } emit();
    s("  STRUCT "); dec(csd[0] >> 6); s(" TAAC "); hex(csd[1], 2); s(" NSAC "); dec(csd[2]);
    s(" TRAN_SPEED "); dec(probe::csdHz(csd)); s(" HZ BLOCKS "); dec(blocks);
    s(" MB "); dec(blocks >> 11); emit();
    uint8_t sc[8];
    uint8_t e = probe::scr(sc);
    s("SCR "); if (e) s(probe::errName(e)); else for (int i = 0; i < 8; i++) { s(" "); hex(sc[i], 2); }
    if (!e) { s(" SPEC "); dec(sc[0] & 15); s(" BUS "); hex(sc[1] & 15, 1); }
    emit();
    uint16_t st = probe::status();
    s("STATUS "); hex(st, 4); emit();
}

// ---- reads ---------------------------------------------------------------------

struct Stats {
    uint32_t n, ok, fail, first, sumUs, maxTokUs;
    uint8_t firstErr, firstR1;
    uint32_t errs[probe::E_COUNT];
};

static void account(Stats &st, uint32_t i, uint32_t lba, uint8_t e, const probe::Read &r, bool verbose) {
    st.n++;
    if (!e) {
        st.ok++;
        st.sumUs += r.us;
        if (r.tokenUs > st.maxTokUs) st.maxTokUs = r.tokenUs;
        return;
    }
    if (!st.fail) { st.first = i; st.firstErr = e; st.firstR1 = r.r1; }
    st.fail++;
    st.errs[e]++;
    if (verbose && st.fail <= 6) {
        s("  FAIL #"); dec(i); s(" LBA "); dec(lba); s(" "); s(probe::errName(e)); s(" R1 "); hex(r.r1, 2);
        s(" NCR "); dec(r.ncr); s(" TOKEN "); hex(r.token, 2); emit();
    }
}

static void summary(const char *what, const Stats &st) {
    s(what); s(" "); dec(st.ok); s("/"); dec(st.n); s(" OK");
    if (st.ok) { s(" AVG "); dec(st.sumUs / st.ok); s(" US TOKEN MAX "); dec(st.maxTokUs); s(" US"); }
    if (st.fail) {
        s(" FIRST FAIL #"); dec(st.first); s(" "); s(probe::errName(st.firstErr)); s(" R1 "); hex(st.firstR1, 2);
    }
    emit();
}

static uint32_t spread(uint32_t i, uint32_t n) {
    uint32_t span = blocks ? blocks : 2048;
    return (uint32_t)(((uint64_t)span * i) / (n ? n : 1));
}

static void (*tickFn)();
static void tick(uint32_t i, uint32_t n) {
    progress = (uint8_t)(n ? i * 100 / n : 100);
    if (tickFn) tickFn();
}

// n reads: stride 0 spreads them over the card; mode, words: traffic before each
// (mode 3: a CHGfx flush of the whole screen).
static void reads(Stats &st, uint32_t lba, uint32_t n, uint32_t stride, uint8_t mode, uint32_t words, bool verbose) {
    memset(&st, 0, sizeof st);
    hold = true;                                // the screen waits: only this test's traffic on the bus
    for (uint32_t i = 0; i < n; i++) {
        if (mode == 3) gfx_flush();
        else if (mode) probe::traffic(mode, words);
        uint32_t a = stride ? lba + i * stride : spread(i, n);
        probe::Read r;
        uint8_t e = probe::read(a, blk, r);
        account(st, i, a, e, r, verbose);
    }
    hold = false;
    probe::drain();
    tick(n, n);
}

// The card answers again after a failure? Identification with CHSd's
// settings (the current ones kept).
static bool stillThere() {
    probe::Cfg keep = probe::cfg;
    probe::defaults();
    bool ok = !probe::init();
    probe::cfg = keep;
    if (!ok) sayStr("  CARD GONE: it no longer identifies. Switch off and on before trusting more tests.");
    return ok;
}

// ---- one block, compactly --------------------------------------------------------

static void readOne(uint32_t lba) {
    probe::Read r;
    uint8_t e = probe::read(lba, blk, r);
    probe::drain();
    s("R "); dec(lba); s(" "); s(probe::errName(e)); s(" R1 "); hex(r.r1, 2); s(" NCR "); dec(r.ncr);
    s(" TOK "); hex(r.token, 2); s(" "); dec(r.tokenUs); s(" US");
    if (e == probe::E_OK || e == probe::E_CRC) {
        s(" CRC CARD "); hex(r.crcCard, 4); s(" DATA "); hex(r.crcData, 4);
        uint32_t sum = 0;
        for (int i = 0; i < 512; i++) sum += blk[i];
        s(" SUM "); hex(sum, 5);
    }
    emit();
}

static void (*panelFn)();
void setPanel(void (*fn)()) { panelFn = fn; }

// ---- the profile ---------------------------------------------------------------

static const char *const BR_NAME[8] = {"24M", "12M", "6M", "3M", "1.5M", "750K", "375K", "187K"};

static bool step(const char *name) {
    s("== "); s(name); emit();
    begin_(name);
    return true;
}

void profile() {
    char t[24];
    Stats st;
    nResults = 0;
    probe::defaults();
    sayStr("PROFILE");

    // 1. Identification as CHSd does it; if that fails, each variant.
    step("INIT");
    uint8_t e = identify(true);
    if (e) {
        note("INIT", V_FAIL, probe::errName(e));
        struct V { const char *name; void (*set)(); };
        static const V VARIANTS[] = {
            {"POWER 1000", [] { probe::cfg.powerBytes = 125; probe::cfg.powerMs = 250; }},
            {"CS CYCLE", [] { probe::cfg.csCycle = 1; }},
            {"GAP 4", [] { probe::cfg.gap = 4; probe::cfg.tail = 4; }},
            {"CRC7", [] { probe::cfg.crc = 1; }},
            {"NO CMD59", [] { probe::cfg.cmd59 = 0; }},
            {"NO CMD8", [] { probe::cfg.cmd8 = 0; }},
            {"CMD1", [] { probe::cfg.cmd1 = 1; }},
            {"RECOVER", [] { probe::cfg.recover = 1; probe::cfg.cmd0Tries = 16; }},
            {"BOOTLOADER", [] { probe::bootloader(); }},
        };
        bool any = false;
        for (const V &v : VARIANTS) {
            probe::defaults();
            v.set();
            s("  TRY "); s(v.name); emit();
            if (!identify(true)) { any = true; note("INIT", V_WARN, v.name); break; }
        }
        if (!any) { sayStr("RESULT the card never identifies"); busy = false; return; }
    } else {
        note("INIT", V_PASS, probe::card.hc ? "SDHC" : probe::card.ver == 2 ? "SDSC V2" : "SDSC V1");
    }
    probe::Cfg base = probe::cfg;
    printRegs();
    note("REGS", haveRegs ? V_PASS : V_WARN, haveRegs ? "CID CSD" : "UNREADABLE");

    // 2. Repeated reads with nothing else on the bus.
    step("READ");
    reads(st, 0, 200, 0, 0, 0, true);
    summary("READ 12M", st);
    note("READ", st.fail ? V_FAIL : V_PASS, st.fail ? "FAILS AT 12M" : "200 OK");
    if (st.fail && !stillThere()) { busy = false; return; }

    // 3. Each data clock, slowest first.
    step("SPEED");
    int fastest = -1;
    for (int b = 7; b >= 0; b--) {
        probe::cfg = base;
        probe::cfg.dataBr = (uint8_t)b;
        reads(st, 0, 64, 0, 0, 0, false);
        s("SPEED "); s(BR_NAME[b]); emit();
        summary("  READ", st);
        if (st.fail) { if (!stillThere()) { busy = false; return; } }
        else fastest = b;
    }
    char *q = t;
    q = fmtStr(q, fastest < 0 ? "NONE" : BR_NAME[fastest]);
    fmtStr(q, " FASTEST");
    note("SPEED", fastest == 0 ? V_PASS : fastest < 0 ? V_FAIL : V_WARN, t);
    probe::cfg = base;

    // 4. Reads with the panel's traffic between them.
    step("PANEL");
    static const char *const MODE[4] = {"", "BUS ONLY", "PANEL DATA", "GFX FLUSH"};
    uint8_t worst = V_PASS;
    for (uint8_t m = 1; m <= 3; m++) {
        reads(st, 0, 60, 0, m, 128 * 128, false);
        s("PANEL "); s(MODE[m]); emit();
        summary("  READ", st);
        if (st.fail) {
            worst = V_FAIL;
            note("PANEL", V_FAIL, MODE[m]);
            if (!stillThere()) { busy = false; return; }
        }
    }
    if (worst == V_PASS) note("PANEL", V_PASS, "60 OK EACH");

    // 5. The menu bootloader's sequence: its settings, a picture (17 blocks)
    // at a time, a whole screen of 16-bit pixels after each.
    step("BOOT");
    probe::bootloader();
    e = identify(false);
    if (e) note("BOOT", V_FAIL, probe::errName(e));
    else {
        Stats all;
        memset(&all, 0, sizeof all);
        for (uint32_t pic = 0; pic < 20; pic++) {
            reads(st, 100 + pic * 17, 17, 1, 0, 0, false);
            all.n += st.n; all.ok += st.ok; all.fail += st.fail;
            if (st.fail && all.fail == st.fail) { all.first = pic; all.firstErr = st.firstErr; all.firstR1 = st.firstR1; }
            probe::traffic(2, 128 * 128);
            tick(pic, 20);
        }
        summary("BOOT PICTURES", all);
        if (all.fail) {
            q = fmtStr(t, "PICTURE ");
            q = fmtInt(q, (int32_t)all.first);
            note("BOOT", V_FAIL, t);
            if (!stillThere()) { busy = false; return; }
        } else note("BOOT", V_PASS, "20 PICTURES");
    }
    probe::cfg = base;

    // 6. Without the idle byte before commands, and without the one after.
    step("GAPS");
    worst = V_PASS;
    for (int g = 0; g < 2; g++) {
        probe::cfg = base;
        if (g == 0) probe::cfg.gap = 0; else probe::cfg.tail = 0;
        reads(st, 0, 64, 0, 0, 0, false);
        s(g ? "NO TAIL" : "NO GAP"); emit();
        summary("  READ", st);
        if (st.fail) { worst = V_WARN; if (!stillThere()) { busy = false; return; } }
    }
    note("GAPS", worst, worst == V_PASS ? "NOT NEEDED" : "NEEDED");
    probe::cfg = base;

    // 7. Multi-block reads (CMD18), as CHStlView streams and CHSDtoUSB reads.
    step("MULTI");
    uint32_t fails, us;
    e = probe::readMulti(0, 64, blk, fails, us);
    s("MULTI 64 BLOCKS "); s(probe::errName(e)); s(" FAILS "); dec(fails); s(" US "); dec(us); emit();
    note("MULTI", e ? V_FAIL : V_PASS, e ? probe::errName(e) : "64 OK");
    if (e) stillThere();

    // 8. DO released after a transaction?
    step("IDLE");
    probe::cfg.tail = 0;
    probe::Read r;
    probe::read(0, blk, r);
    uint32_t bad = probe::idle(8);
    probe::cfg = base;
    s("IDLE "); dec(bad); s(" OF 8 BYTES DRIVEN WITH CS HIGH"); emit();
    note("IDLE", bad ? V_WARN : V_PASS, bad ? "DO HELD" : "DO RELEASED");

    busy = false;
    progress = 100;
    sayStr("RESULT");
    for (int i = 0; i < nResults; i++) {
        static const char *const V[4] = {"-", "PASS", "WARN", "FAIL"};
        s("  "); s(results[i].name); s(" "); s(V[results[i].verdict]); s(" "); s(results[i].note); emit();
    }
}

// ---- commands -------------------------------------------------------------------

struct Field { const char *name; uint8_t wide; void *p; };
#define F8(n, f) {n, 0, &probe::cfg.f}
#define F16(n, f) {n, 1, &probe::cfg.f}
static const Field FIELDS[] = {
    F8("IDENTBR", identBr), F8("DATABR", dataBr), F8("POWERBYTES", powerBytes), F8("POWERMS", powerMs),
    F8("GAP", gap), F8("TAIL", tail), F8("NCR", ncr), F8("CRC", crc), F8("CMD59", cmd59), F8("CMD8", cmd8),
    F8("HCS", hcs), F8("CMD1", cmd1), F8("OCRFIRST", ocrFirst), F8("PULLUP", pullup), F8("CSCYCLE", csCycle),
    F8("CMD16", cmd16), F8("CMD0TRIES", cmd0Tries), F8("RECOVER", recover), F16("TOKENMS", tokenMs),
    F16("INITMS", initMs), F8("PATTERN", pattern), F8("TRAFFICBR", trafficBr),
};

static void printCfg() {
    s("CFG");
    for (const Field &f : FIELDS) {
        s(" "); s(f.name); s("=");
        dec(f.wide ? *(uint16_t *)f.p : *(uint8_t *)f.p);
        if (lp > ln + 100) emit();
    }
    if (lp != ln) emit();
}

static char *words[8];
static int nw;
static uint32_t num(int i, uint32_t dflt) {
    if (i >= nw) return dflt;
    const char *t = words[i];
    uint32_t v = 0;
    if (t[0] == '0' && (t[1] == 'X' || t[1] == 'x'))
        for (t += 2; *t; t++) v = v * 16 + (uint32_t)(*t <= '9' ? *t - '0' : (*t | 32) - 'a' + 10);
    else
        for (; *t >= '0' && *t <= '9'; t++) v = v * 10 + (uint32_t)(*t - '0');
    return v;
}
static bool is(const char *w) { return nw && !strcmp(words[0], w); }

void begin(void (*out)(const char *)) {
    say = out;
    probe::out = out;
    probe::defaults();
}

void setTick(void (*fn)()) { tickFn = fn; }

bool run(char *line) {
    nw = 0;
    for (char *c = line; *c && nw < 8;) {
        while (*c == ' ' || *c == '\t') c++;
        if (!*c) break;
        words[nw++] = c;
        while (*c && *c != ' ' && *c != '\t') { if (*c >= 'a' && *c <= 'z') *c -= 32; c++; }
        if (*c) *c++ = 0;
    }
    if (!nw) return false;
    bool ok = true;
    if (is("ID")) sayStr("CHST " CHST_VERSION);
    else if (is("PANEL")) { if (probe::panelUp) sayStr("PANEL ALREADY ON"); else if (panelFn) panelFn(); }
    else if (is("R")) readOne(num(1, 0));
    else if (is("SAME") || is("SCAN")) {
        bool same = is("SAME");
        uint32_t lba = num(1, 0), n = num(2, 100);
        begin_(same ? "SAME" : "SCAN");
        Stats st;
        memset(&st, 0, sizeof st);
        hold = true;
        uint32_t shown = 0;
        for (uint32_t i = 0; i < n; i++) {
            probe::Read r;
            uint32_t a = same ? lba : lba + i;
            uint8_t e = probe::read(a, blk, r);
            account(st, i, a, e, r, false);
            if (e && shown < 12) {
                shown++;
                s("  #"); dec(i); s(" LBA "); dec(a); s(" "); s(probe::errName(e)); s(" TOK "); hex(r.token, 2);
                if (e == probe::E_CRC) { s(" CARD "); hex(r.crcCard, 4); s(" DATA "); hex(r.crcData, 4); }
                emit();
            }
            if (e == probe::E_BUSY) { sayStr("  STOPPED: THE CARD HOLDS DO LOW"); break; }
        }
        hold = false;
        probe::drain();
        summary(same ? "SAME" : "SCAN", st);
    }
    else if (is("CFG")) printCfg();
    else if (is("DEFAULTS")) { probe::defaults(); printCfg(); }
    else if (is("BOOTLOADER")) { probe::bootloader(); printCfg(); }
    else if (is("TRACE")) probe::trace = (uint8_t)num(1, 1);
    else if (is("SET")) {
        for (int i = 1; i + 1 < nw; i += 2) {
            const Field *f = nullptr;
            for (const Field &g : FIELDS) if (!strcmp(g.name, words[i])) f = &g;
            if (!f) { s("ERR NO SETTING "); s(words[i]); emit(); return true; }
            if (f->wide) *(uint16_t *)f->p = (uint16_t)num(i + 1, 0);
            else *(uint8_t *)f->p = (uint8_t)num(i + 1, 0);
        }
        printCfg();
    }
    else if (is("INIT")) { begin_("INIT"); identify(true); }
    else if (is("REGS")) { begin_("REGS"); if (!haveRegs && cardOk) identify(true); printRegs(); }
    else if (is("READ") || is("MIX")) {
        bool mix = is("MIX");
        uint32_t lba = num(1, 0), n = num(2, 1), stride = num(3, 1);
        uint8_t mode = mix ? (uint8_t)num(4, 2) : 0;
        uint32_t w = num(5, 128 * 128);
        begin_(mix ? "MIX" : "READ");
        Stats st;
        reads(st, lba, n, stride, mode, w, true);
        summary(mix ? "MIX" : "READ", st);
    }
    else if (is("DUMP")) {
        probe::Read r;
        uint8_t e = probe::read(num(1, 0), blk, r);
        s("DUMP "); s(probe::errName(e)); s(" R1 "); hex(r.r1, 2); s(" TOKEN "); hex(r.token, 2);
        s(" US "); dec(r.us); emit();
        if (!e || e == probe::E_CRC)
            for (int row = 0; row < 32; row++) {
                hex((uint32_t)row * 16, 3); s(":");
                for (int i = 0; i < 16; i++) { s(" "); hex(blk[row * 16 + i], 2); }
                emit();
            }
    }
    else if (is("MULTI")) {
        uint32_t fails, us;
        uint8_t e = probe::readMulti(num(1, 0), num(2, 16), blk, fails, us);
        s("MULTI "); s(probe::errName(e)); s(" FAILS "); dec(fails); s(" US "); dec(us); emit();
    }
    else if (is("STATUS")) { s("STATUS "); hex(probe::status(), 4); emit(); }
    else if (is("IDLE")) { s("IDLE "); dec(probe::idle(num(1, 8))); emit(); }
    else if (is("TRAFFIC")) {
        uint8_t m = (uint8_t)num(1, 2);
        if (m == 3) gfx_flush(); else probe::traffic(m, num(2, 128 * 128));
    }
    else if (is("RECOVER")) {
        probe::recover();
    }
    else if (is("PARK")) { s("PARK R1 "); hex(probe::park(), 2); emit(); }
    else if (is("PARKMIX")) {
        // n rounds: identify, read, park, traffic (mode 1, cfg.pattern): does
        // a parked card survive what the panel sends?
        uint32_t n = num(1, 20), w = num(2, 128 * 128);
        uint32_t ok = 0, i;
        uint8_t e = 0;
        begin_("PARKMIX");
        hold = true;
        for (i = 0; i < n; i++) {
            if ((e = probe::init()) != 0) break;
            probe::Read r;
            e = probe::read(32, blk, r);
            if (e && e != probe::E_CRC) break;
            e = 0;
            ok++;
            probe::park();
            probe::traffic(1, w);
        }
        hold = false;
        probe::drain();
        s("PARKMIX "); dec(ok); s("/"); dec(n); s(" ROUNDS OK");
        if (i < n) { s(" STOPPED AT "); dec(i); s(" "); s(probe::errName(e)); s(" R1 "); hex(probe::card.lastR1, 2); }
        emit();
    }
    else if (is("PROFILE")) profile();
    else if (is("MENU") || is("RESET")) {
        sayStr("OK");
        delay(50);                              // the line reaches the PC first
        if (is("MENU")) chgame.exitToMenu();
        NVIC_SystemReset();
    }
    else ok = false;
    busy = false;
    probe::drain();
    sayStr(ok ? "OK" : "ERR UNKNOWN");
    return ok;
}

}  // namespace bench
