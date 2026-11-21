// Probe.cpp - see Probe.h. Written from the SD Physical Layer Simplified
// Specification (SPI mode, chapter 7) and the CH32X035 reference manual, as
// CHSd's SdSpi.cpp was; the register handling is CHSd's.
#include <Arduino.h>
#include <CHGame.h>
#include <string.h>
#include "Probe.h"

namespace probe {

Cfg cfg;
Card card;
Out out;
uint8_t trace;
bool panelUp;

// SPI1: master, software NSS held high, mode 0, MSB first.
static const uint32_t SPI_MASTER = (1u << 2) | (1u << 8) | (1u << 9);   // MSTR | SSI | SSM
static const uint32_t SPE = 1u << 6, DFF = 1u << 11;
static const uint32_t RXNE = 1u << 0, TXE = 1u << 1, BSY = 1u << 7;

void defaults() {
    cfg.identBr = 7;
    cfg.dataBr = 1;
    cfg.powerBytes = 10;
    cfg.powerMs = 0;
    cfg.gap = 1;
    cfg.tail = 1;
    cfg.ncr = 9;
    cfg.crc = 0;
    cfg.cmd59 = 1;
    cfg.cmd8 = 1;
    cfg.hcs = 1;
    cfg.cmd1 = 0;
    cfg.ocrFirst = 0;
    cfg.pullup = 1;
    cfg.csCycle = 0;
    cfg.cmd16 = 1;
    cfg.cmd0Tries = 20;
    cfg.recover = 0;
    cfg.tokenMs = 1000;
    cfg.initMs = 1000;
    cfg.pattern = 1;
    cfg.trafficBr = 0;
}

void bootloader() {
    defaults();
    cfg.crc = 1;
    cfg.ncr = 10;
    cfg.cmd0Tries = 16;
    cfg.recover = 1;
    cfg.tokenMs = 1500;
    cfg.initMs = 2000;
}

const char *errName(uint8_t e) {
    static const char *const N[E_COUNT] = {
        "OK", "NO CMD0", "CMD8", "ACMD41", "CMD58", "CMD16", "BUSY", "R1", "NO TOKEN", "DATA ERR", "CRC",
    };
    return e < E_COUNT ? N[e] : "?";
}

// ---- the trace ---------------------------------------------------------------

static char line[200];
static char *lp = line;
static uint8_t rx[24];                          // the bytes of the last R1 wait (trace 2)
static uint32_t nrx;

static void s(const char *t) { while (*t && lp < line + sizeof line - 1) *lp++ = *t++; *lp = 0; }
static void hex(uint32_t v, int digits) {
    while (digits--) {
        uint8_t d = (v >> (4 * digits)) & 15;
        if (lp < line + sizeof line - 1) *lp++ = (char)(d < 10 ? '0' + d : 'A' + d - 10);
    }
    *lp = 0;
}
static void dec(uint32_t v) {
    char t[11];
    int n = 0;
    do { t[n++] = (char)('0' + v % 10); v /= 10; } while (v);
    while (n && lp < line + sizeof line - 1) *lp++ = t[--n];
    *lp = 0;
}
// Trace lines wait in RAM until drain(): printing to the PC while a command
// runs would put USB's time inside the card's timings.
static char held[1024];
static uint32_t heldN, dropped;

static void emit() {
    uint32_t n = (uint32_t)(lp - line) + 1;
    if (heldN + n <= sizeof held) {
        memcpy(held + heldN, line, n);
        heldN += n;
    } else dropped++;
    lp = line;
    *lp = 0;
}

void drain() {
    for (uint32_t i = 0; i < heldN; i += (uint32_t)strlen(held + i) + 1)
        if (out) out(held + i);
    heldN = 0;
    if (dropped) {
        s("  ("); dec(dropped); s(" TRACE LINES DROPPED)");
        dropped = 0;
        if (out) out(line);
        lp = line;
        *lp = 0;
    }
}

// ---- the bus -----------------------------------------------------------------

static uint8_t br;
static uint16_t saved;                          // CHGfx's SPI1 setup, put back afterwards

static uint8_t x(uint8_t b) {
    SPI1->DATAR = b;
    while (!(SPI1->STATR & RXNE)) {}
    return (uint8_t)SPI1->DATAR;
}

// BR and the frame size may change only while SPE is clear.
static void spiSet(uint32_t ctlr1) {
    while (SPI1->STATR & BSY) {}
    SPI1->CTLR1 = (uint16_t)(ctlr1 & ~SPE);
    SPI1->CTLR1 = (uint16_t)ctlr1;
}

// The card's chip select: PB11 on CHGame Rev0, PB3 on Rev1 (where PB11 is
// the A button). The panel's, PA4, is the same on both.
#if defined(ARDUINO_CHGAME_REV1)
static void select(bool on) {
    if (on) GPIOB->BCR = 1u << 3;
    else GPIOB->BSHR = 1u << 3;
}
#else
static void select(bool on) {
    if (on) GPIOB->BCR = 1u << 11;
    else GPIOB->BSHR = 1u << 11;
}
#endif

// (CHGfx's flush state reads "busy" until gfx_begin(): no wait before it.)
static void claim() {
    if (panelUp) gfx_wait();
    GPIOA->BSHR = 1u << 4;                      // the panel deselected
    saved = (uint16_t)SPI1->CTLR1;
    spiSet(SPI_MASTER | SPE | ((uint32_t)br << 3));
    (void)SPI1->DATAR;                          // the panel never reads: RXNE and OVR are set
    (void)SPI1->STATR;
}

static void release() {
    select(false);
    for (uint32_t k = cfg.tail; k; k--) x(0xFF);
    spiSet(saved);
}

// SPI1 and its pins as CHGfx would leave them, for a test before
// gfx_begin(): SCK and MOSI alternate function, MISO input with pull-up, both
// chip selects high outputs. The panel's other pins are left alone. GPIOB's
// CFGHR does not read back (platform/board/docs/ch32x035-gotchas.md): it is
// written from the core's shadow, as the library and CHGfx write it, or the
// next of them to write it puts PB11 back to an input.
#if defined(ARDUINO_CHGAME_REV1)
// Rev1: SD_CS is PB3, in GPIOB's CFGLR, which reads back: a masked write.
void hwInit() {
    RCC->APB2PCENR |= RCC_APB2Periph_AFIO | RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB | RCC_APB2Periph_SPI1;
    GPIOA->BSHR = (1u << 4) | (1u << 6);
    GPIOB->BSHR = 1u << 3;
    GPIOA->CFGLR = (GPIOA->CFGLR & 0x0000FFFFu) | 0xB8B30000u;   // PA7 MOSI, PA6 MISO pu, PA5 SCK, PA4 LCD_CS
    GPIOB->CFGLR = (GPIOB->CFGLR & ~(0xFu << 12)) | (0x3u << 12); // PB3 SD_CS: push-pull output
    spiSet(SPI_MASTER | SPE | (7u << 3));
}
#else
extern "C" volatile uint32_t CFGHR_tmpB;
void hwInit() {
    RCC->APB2PCENR |= RCC_APB2Periph_AFIO | RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB | RCC_APB2Periph_SPI1;
    GPIOA->BSHR = (1u << 4) | (1u << 6);
    GPIOB->BSHR = 1u << 11;
    GPIOA->CFGLR = (GPIOA->CFGLR & 0x0000FFFFu) | 0xB8B30000u;   // PA7 MOSI, PA6 MISO pu, PA5 SCK, PA4 LCD_CS
    CFGHR_tmpB = (CFGHR_tmpB & ~(0xFu << 12)) | (0x3u << 12);   // PB11 SD_CS: push-pull output
    GPIOB->CFGHR = CFGHR_tmpB;
    spiSet(SPI_MASTER | SPE | (7u << 3));
}
#endif

static void pins() {
    // PA6 (MISO): input with pull-up (CFG 0x8, ODR 1), or floating (0x4).
    GPIOA->CFGLR = (GPIOA->CFGLR & ~(0xFul << 24)) | ((cfg.pullup ? 0x8ul : 0x4ul) << 24);
    if (cfg.pullup) GPIOA->BSHR = 1u << 6;
}

// Clocks 0xFF until a token arrives (tok: anything but 0xFF) or busy ends
// (!tok: 0xFF), or ms runs out. Returns the last byte.
static uint8_t wait(bool tok, uint32_t ms) {
    uint32_t t0 = micros();
    uint8_t b;
    do b = x(0xFF); while ((b == 0xFF) == tok && micros() - t0 <= ms * 1000u);
    return b;
}

// ---- commands ----------------------------------------------------------------

static uint8_t crc7(const uint8_t *f, uint32_t n) {
    uint8_t c = 0;
    for (uint32_t i = 0; i < n; i++)
        for (uint8_t d = f[i], b = 8; b; b--, d <<= 1) {
            c <<= 1;
            if ((d ^ c) & 0x80) c ^= 0x09;
        }
    return (uint8_t)(c & 0x7F);
}

uint16_t crc16(const uint8_t *p, uint32_t n) {
    uint16_t c = 0;
    while (n--) {
        c ^= (uint16_t)*p++ << 8;
        for (int i = 0; i < 8; i++) c = (uint16_t)((c << 1) ^ ((c & 0x8000) ? 0x1021 : 0));
    }
    return c;
}

static uint8_t lastNcr;
static bool quiet;                              // ACMD41's middle rounds go untraced

static uint8_t cmd(uint8_t c, uint32_t arg) {
    for (uint32_t k = cfg.gap; k; k--) x(0xFF);
    uint8_t f[6] = {(uint8_t)(0x40 | c), (uint8_t)(arg >> 24), (uint8_t)(arg >> 16), (uint8_t)(arg >> 8),
                    (uint8_t)arg, 0};
    if (cfg.crc || c == 59) f[5] = (uint8_t)(crc7(f, 5) << 1 | 1);
    else f[5] = c == 8 ? 0x87 : 0x95;           // CHSd: CMD0's and CMD8's, the rest unchecked
    for (int i = 0; i < 6; i++) x(f[i]);
    uint8_t r;
    nrx = 0;
    uint32_t k = 0;
    do {
        r = x(0xFF);
        if (nrx < sizeof rx) rx[nrx++] = r;
    } while ((r & 0x80) && ++k < cfg.ncr);
    lastNcr = (uint8_t)k;
    if (trace && !quiet) {
        s("  CMD"); dec(c); s(" "); hex(arg, 8); s(" R1 "); hex(r, 2); s(" NCR "); dec(k);
        if (trace > 1) {
            s(" RX");
            for (uint32_t i = 0; i < nrx; i++) { s(" "); hex(rx[i], 2); }
        }
        emit();
    }
    return r;
}

static uint32_t rd32() {
    uint32_t r = 0;
    for (uint32_t i = 4; i; i--) r = (r << 8) | x(0xFF);
    if (trace && !quiet) { s("    +"); hex(r, 8); emit(); }
    return r;
}

static void cycle() {
    if (!cfg.csCycle) return;
    select(false);
    x(0xFF);
    select(true);
}

static void recoverSelected() {
    cmd(12, 0);                                 // stops a CMD18 stream
    wait(false, 500);
    for (uint32_t k = 520; k; k--) x(0xFF);     // completes a CMD25 block cut short
    wait(false, 500);
    x(0xFD);                                    // stop token: ends a CMD25 between blocks
    wait(false, 500);
}

void recover() {
    br = cfg.identBr;
    claim();
    select(true);
    recoverSelected();
    release();
}

static uint8_t ident() {
    uint8_t r = 0xFF;
    uint32_t k;
    wait(false, 500);
    for (k = 0; k < cfg.cmd0Tries; k++) {
        if (cfg.recover && k == 6) recoverSelected();
        if ((r = cmd(0, 0)) == 0x01) break;
        cycle();
    }
    card.cmd0Tries = (uint8_t)(k + 1);
    card.lastR1 = r;
    if (r != 0x01) return E_CMD0;
    cycle();
    if (cfg.cmd59) cmd(59, cfg.cmd59 == 2 ? 1 : (cfg.crc ? 0 : 0x9A));
    cycle();
    card.ver = 1;
    if (cfg.cmd8) {
        r = cmd(8, 0x1AA);                      // SEND_IF_COND 2.7-3.6 V, check pattern 0xAA
        card.lastR1 = r;
        if (!(r & 0x04)) {                      // not an illegal command: v2.00 or later
            if (r != 0x01 || (rd32() & 0xFFF) != 0x1AA) return E_CMD8;
            card.ver = 2;
        }
        cycle();
    }
    if (cfg.ocrFirst) {
        if (cmd(58, 0) <= 1) card.ocr = rd32();
        cycle();
    }
    bool mmc = cfg.cmd1 == 2;
    uint32_t t0 = micros();
    card.loops = 0;
    do {
        quiet = card.loops > 1;
        if (mmc) r = cmd(1, 0);
        else {
            r = cmd(55, 0);
            if (r <= 1) r = cmd(41, card.ver == 2 && cfg.hcs ? 1ul << 30 : 0);
            if ((r & 0x04) && cfg.cmd1 == 1) { mmc = true; r = 1; }
        }
        card.loops++;
        card.lastR1 = r;
        if (r > 1 || micros() - t0 > cfg.initMs * 1000u) { quiet = false; return E_ACMD41; }
        cycle();
    } while (r);
    quiet = false;
    if (trace) { s("  ready after "); dec(card.loops); s(mmc ? " CMD1" : " ACMD41"); s(" rounds, "); dec((micros() - t0) / 1000); s(" ms"); emit(); }
    if (mmc) card.ver = 3;
    card.hc = 0;
    r = cmd(58, 0);                             // READ_OCR: powered up, CCS = block addressing
    card.lastR1 = r;
    if (r <= 1) card.ocr = rd32();
    else if (card.ver == 2) return E_CMD58;
    if (card.ver == 2) card.hc = (uint8_t)((card.ocr >> 30) & 1);
    cycle();
    if (!card.hc && cfg.cmd16 && (r = cmd(16, 512)) != 0) { card.lastR1 = r; return E_CMD16; }
    return E_OK;
}

// CMD0 alone: the card back to its idle state, where it takes no reads or
// writes until it is identified again.
uint8_t park() {
    br = cfg.identBr;
    claim();
    select(true);
    uint8_t r = cmd(0, 0);
    release();
    return r;
}

uint8_t init() {
    uint32_t t0 = micros();
    card = Card();
    pins();
    br = cfg.identBr;
    claim();
    select(false);
    if (cfg.powerMs) delay(cfg.powerMs);
    for (uint32_t k = cfg.powerBytes; k; k--) x(0xFF);   // >= 74 clocks with CS high
    select(true);
    card.err = ident();
    release();
    br = cfg.dataBr;
    card.us = micros() - t0;
    return card.err;
}

// A data block of n bytes after its token, CRC16 checked.
static uint16_t lastCard, lastData;
static uint8_t data(uint8_t *dst, uint32_t n, uint32_t ms, uint8_t &token) {
    token = wait(true, ms);
    if (token != 0xFE) return token == 0xFF ? E_TOKEN : E_DATAERR;
    for (uint32_t i = 0; i < n; i++) dst[i] = x(0xFF);
    lastCard = (uint16_t)(x(0xFF) << 8);
    lastCard |= x(0xFF);
    lastData = crc16(dst, n);
    return lastCard == lastData ? E_OK : E_CRC;
}

uint8_t read(uint32_t lba, uint8_t *dst, Read &r) {
    br = cfg.dataBr;
    claim();
    select(true);
    uint32_t t0 = micros();
    r.r1 = 0xFF;
    r.ncr = 0;
    r.token = 0xFF;
    r.tokenUs = 0;
    uint8_t b = wait(false, 500);
    if (b != 0xFF) { r.err = E_BUSY; r.token = b; }
    else if ((r.r1 = cmd(17, card.hc ? lba : lba << 9)) != 0) { r.ncr = lastNcr; r.err = E_R1; }
    else {
        r.ncr = lastNcr;
        uint32_t t1 = micros();
        r.err = data(dst, 512, cfg.tokenMs, r.token);
        r.tokenUs = micros() - t1;
        r.crcCard = lastCard;
        r.crcData = lastData;
    }
    r.us = micros() - t0;
    release();
    return r.err;
}

uint8_t readMulti(uint32_t lba, uint32_t n, uint8_t *buf, uint32_t &fails, uint32_t &us) {
    br = cfg.dataBr;
    claim();
    select(true);
    uint32_t t0 = micros();
    fails = 0;
    uint8_t e = E_OK, token;
    if (wait(false, 500) != 0xFF) e = E_BUSY;
    else if (cmd(18, card.hc ? lba : lba << 9) != 0) e = E_R1;
    else
        for (uint32_t k = 0; k < n; k++) {
            uint8_t b = data(buf, 512, cfg.tokenMs, token);
            if (b) { fails++; if (!e) e = b; if (b == E_TOKEN) { fails += n - k - 1; break; } }
        }
    // CMD12: a stuff byte comes before its R1, then busy.
    x(0x4C); x(0); x(0); x(0); x(0); x(0x61);
    x(0xFF);
    uint8_t r;
    uint32_t k = 9;
    do r = x(0xFF); while ((r & 0x80) && --k);
    wait(false, 500);
    us = micros() - t0;
    release();
    return e;
}

uint8_t reg(uint8_t c, uint8_t *dst) {
    br = cfg.dataBr;
    claim();
    select(true);
    uint8_t token, e = E_OK;
    if (wait(false, 500) != 0xFF) e = E_BUSY;
    else if (cmd(c, 0) != 0) e = E_R1;
    else e = data(dst, 16, 100, token);
    release();
    return e;
}

uint8_t scr(uint8_t *dst) {
    br = cfg.dataBr;
    claim();
    select(true);
    uint8_t token, e = E_OK;
    if (wait(false, 500) != 0xFF) e = E_BUSY;
    else if (cmd(55, 0) > 1 || cmd(51, 0) != 0) e = E_R1;
    else e = data(dst, 8, 100, token);
    release();
    return e;
}

uint16_t status() {
    br = cfg.dataBr;
    claim();
    select(true);
    uint8_t r = cmd(13, 0);
    uint16_t v = r & 0x80 ? 0xFFFF : (uint16_t)(r << 8 | x(0xFF));
    release();
    return v;
}

uint32_t idle(uint32_t n) {
    claim();
    select(false);
    uint32_t bad = 0;
    for (; n; n--) if (x(0xFF) != 0xFF) bad++;
    spiSet(saved);
    return bad;
}

void traffic(uint8_t mode, uint32_t n) {
    if (panelUp) gfx_wait();
    saved = (uint16_t)SPI1->CTLR1;
    select(false);
    if (mode == 2) GPIOA->BCR = 1u << 4;        // the panel selected: these are pixels
    // 16-bit frames at 24 MHz, as the bootloader sends pixels; mode 4: bytes at 24 MHz, as CHGfx sends them
    spiSet(SPI_MASTER | SPE | (mode == 4 ? 0 : DFF) | ((uint32_t)cfg.trafficBr << 3));
    static uint32_t lfsr = 0x1234567u;
    for (; n; n--) {
        uint16_t w = 0;
        if (cfg.pattern == 1) { lfsr ^= lfsr << 13; lfsr ^= lfsr >> 17; lfsr ^= lfsr << 5; w = (uint16_t)lfsr; }
        else if (cfg.pattern == 2) w = 0xFFFF;
        while (!(SPI1->STATR & TXE)) {}
        SPI1->DATAR = w;
    }
    while (!(SPI1->STATR & TXE)) {}
    while (SPI1->STATR & BSY) {}
    GPIOA->BSHR = 1u << 4;
    (void)SPI1->DATAR;                          // the echo and the overrun, as the bootloader clears them
    (void)SPI1->STATR;
    spiSet(saved);
}

// ---- registers ----------------------------------------------------------------

// Bits hi..lo of a 128-bit register sent MSB first (r[0] holds bits 127..120).
static uint32_t bits(const uint8_t *r, int hi, int lo) {
    uint32_t v = 0;
    for (int b = hi; b >= lo; b--) v = (v << 1) | ((r[15 - b / 8] >> (b % 8)) & 1);
    return v;
}

uint32_t csdBlocks(const uint8_t *csd) {
    if ((csd[0] >> 6) == 1) return (bits(csd, 69, 48) + 1) << 10;           // CSD 2.0: (C_SIZE + 1) * 512 KB
    uint32_t n = (bits(csd, 73, 62) + 1) << (bits(csd, 49, 47) + 2);        // CSD 1.0 (and MMC)
    uint32_t len = bits(csd, 83, 80);
    return len >= 9 ? n << (len - 9) : n >> (9 - len);
}

uint32_t csdHz(const uint8_t *csd) {
    static const uint8_t TEN[16] = {0, 10, 12, 13, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80};
    static const uint32_t UNIT[4] = {10000, 100000, 1000000, 10000000};      // unit / 10
    uint8_t t = csd[3];
    return (t & 7) < 4 ? TEN[(t >> 3) & 15] * UNIT[t & 7] : 0;
}

}  // namespace probe
