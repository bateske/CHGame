// Probe: the SD card in SPI mode, one command at a time, with every choice a
// driver makes about timing and sequence turned into a setting (Cfg), so a
// test can try them one by one. It never writes to the card: every command
// it sends reads, identifies or resets, so any card is safe to profile.
//
// It is a test bench, not a driver: it reports what the card did (each R1,
// how many bytes it took to come, how long a token took, whether the block's
// CRC16 matched) instead of hiding it, and it does not retry on its own.
// Its defaults are CHSd's (SdSpi.cpp) choices; `bootloader()` sets the menu
// bootloader's (platform/bootloader/src/sd.c).
//
// The bus is SPI1, shared with the panel: every call waits for CHGfx's flush
// and hands SPI1 back as CHGfx left it.
#pragma once
#include <stdint.h>

namespace probe {

// One setting per choice. The comments give CHSd's value first.
struct Cfg {
    uint8_t identBr;     // 7: SPI1 BR during identification, 48 MHz / 2^(BR+1) (7: 187.5 kHz)
    uint8_t dataBr;      // 1: after it (1: 12 MHz, 0: 24 MHz)
    uint8_t powerBytes;  // 10: 0xFF bytes with CS high before CMD0 (8 clocks each)
    uint8_t powerMs;     // 0: a pause before them
    uint8_t gap;         // 1: idle bytes before each command (N_RC)
    uint8_t tail;        // 1: bytes clocked with CS high after a transaction (DO released)
    uint8_t ncr;         // 9: bytes waited for R1
    uint8_t crc;         // 0: CMD0/CMD8's fixed CRCs and 0x95; 1: a real CRC7 on every command
    uint8_t cmd59;       // 1: 0 never sent, 1 CRC checking off, 2 on
    uint8_t cmd8;        // 1: 0 skips SEND_IF_COND (the card taken for v1)
    uint8_t hcs;         // 1: HCS in ACMD41 for a v2 card
    uint8_t cmd1;        // 0: 1 CMD1 when ACMD41 is refused (MMC), 2 CMD1 only
    uint8_t ocrFirst;    // 0: 1 READ_OCR before ACMD41 too
    uint8_t pullup;      // 1: MISO's internal pull-up
    uint8_t csCycle;     // 0: 1 CS high (and a byte) between identification commands
    uint8_t cmd16;       // 1: SET_BLOCKLEN 512 on a byte-addressed card
    uint8_t cmd0Tries;   // 20: CMD0 attempts
    uint8_t recover;     // 0: 1 recover() (CMD12, 520 clocks, stop token) after 6 failed CMD0s
    uint16_t tokenMs;    // 1000: a data token
    uint16_t initMs;     // 1000: ACMD41's loop
    uint8_t pattern;     // (not CHSd's) traffic()'s words: 0 zeros, 1 pseudo-random, 2 all ones
    uint8_t trafficBr;   // (not CHSd's) traffic()'s SPI1 BR: 0 is 24 MHz, the panel's clock
};
extern Cfg cfg;
void defaults();         // CHSd's choices
void bootloader();       // the menu bootloader's: real CRC7, recover(), 2 s ACMD41, 1.5 s token

// What identification found.
struct Card {
    uint8_t err;         // E_* (0: ready)
    uint8_t ver;         // 1 or 2 (CMD8 answered); 3: MMC (CMD1)
    uint8_t hc;          // block addressing
    uint8_t cmd0Tries;   // CMD0s it took
    uint8_t lastR1;      // the R1 that ended it
    uint32_t ocr;
    uint32_t loops;      // ACMD41 (or CMD1) rounds
    uint32_t us;         // identification, start to end
};
extern Card card;

enum : uint8_t {
    E_OK, E_CMD0, E_CMD8, E_ACMD41, E_CMD58, E_CMD16,   // identification
    E_BUSY, E_R1, E_TOKEN, E_DATAERR, E_CRC,           // a read
    E_COUNT
};
const char *errName(uint8_t e);

// A read's account.
struct Read {
    uint8_t err;
    uint8_t r1;          // the command's R1 (0xFF: none)
    uint8_t ncr;         // bytes before R1
    uint8_t token;       // what ended the token wait (BUSY: the byte that was not 0xFF)
    uint16_t crcCard;    // the CRC16 the card sent
    uint16_t crcData;    // the CRC16 of the 512 bytes that came
    uint32_t tokenUs;    // command to token
    uint32_t us;         // the whole transaction
};

// Lines for the PC: every command and its answer when trace is on. They
// wait in RAM while the card is being timed; drain() sends them.
typedef void (*Out)(const char *line);
extern Out out;
extern uint8_t trace;    // 0 off, 1 commands, 2 commands and every byte
void drain();

void hwInit();                                       // SPI1 and its pins, before gfx_begin()
extern bool panelUp;                                 // gfx_begin() has run: wait for CHGfx's flushes
uint8_t init();                                      // identification; card.err
uint8_t park();                                      // CMD0 alone (its R1): idle until identified again
uint8_t read(uint32_t lba, uint8_t *dst, Read &r);   // CMD17; r.err
// CMD18 for n blocks, then CMD12; fails reports the blocks that did not come.
uint8_t readMulti(uint32_t lba, uint32_t n, uint8_t *buf, uint32_t &fails, uint32_t &us);
// CID (CMD10) or CSD (CMD9): 16 bytes with their CRC16 checked.
uint8_t reg(uint8_t cmd, uint8_t *dst);
uint16_t status();                                   // CMD13's R2 (0xFFFF: no answer)
uint8_t scr(uint8_t *dst);                           // ACMD51: 8 bytes
// n bytes clocked with CS high; returns how many were not 0xFF (DO driven
// while deselected).
uint32_t idle(uint32_t n);
void recover();                                      // CMD12, 520 clocks, the stop token
// Traffic for the panel's share of the bus between card commands:
// mode 1 frames of 16 bits at 24 MHz with neither chip selected, 2 the
// same with the panel selected (pixel data), 4 bytes at 24 MHz with neither
// selected; n frames of cfg.pattern.
void traffic(uint8_t mode, uint32_t n);

uint32_t csdBlocks(const uint8_t *csd);              // capacity in 512 B blocks
uint32_t csdHz(const uint8_t *csd);                  // TRAN_SPEED
uint16_t crc16(const uint8_t *p, uint32_t n);

}  // namespace probe
