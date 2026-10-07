/* SPDX-License-Identifier: GPL-3.0-or-later
 * What the website is doing to the card, worked out from the commands going
 * past (CHSDtoUSB's Monitor does the same from SD blocks).
 *
 * Display.cpp reports every command before and after it runs. From that this
 * keeps what the screen shows: a history of 125 ms slices for the graph, an
 * event log by file name, and the session's totals. It only watches: it never
 * touches the card, the serial port or the protocol's state.
 */
#pragma once
#include <stdint.h>

namespace mon {

// ---- The card, as HELLO last reported it ------------------------------------
struct Card {
    uint32_t sectors, freeSectors;     // 512 B each; freeSectors falls as files are committed
    uint8_t error;                     // transfer_init()'s result: 0 ready
    bool known;                        // HELLO has answered
    bool recovered;                    // ... and a journaled replacement was finished at start
};
extern Card card;
uint32_t usedPermille();               // 0..1000; 0 while not known

// ---- The session --------------------------------------------------------------
extern bool mounted;                   // transfer_init() has returned
extern bool linked;                    // HELLO has answered
extern bool stopped;                   // cancelled on the console: commands are refused until HELLO
extern bool transferActive;            // BEGIN, CHECK or READ since the last ABORT or SYNC
extern bool verifying;                 // inside COMMIT: the staged file is read back
extern bool failed;                    // the last command answered an error
extern bool done;                      // the job is finished: SYNC after work, and nothing since
extern uint8_t lastFail, lastFailCmd;  // ... the newest one's status and command (0: none yet)

// The whole job as the website measures it (PROGRESS): bytes done and to do,
// its estimate of the seconds left, and what it is at. Forgotten at HELLO.
struct Progress { uint32_t done, total, seconds; uint8_t mode; bool known; };
enum : uint8_t { P_COMPLETE, P_READ, P_WRITE };
extern Progress progress;

// ---- History: one column per 125 ms of traffic --------------------------------
enum : uint8_t { K_PUT = 1, K_GET = 2, K_CHECK = 4, K_META = 8, C_VERIFY = 0x10, C_FAIL = 0x20, C_RETRY = 0x40 };
struct __attribute__((packed)) Column {   // three bytes: 128 of them are 384
    uint16_t kbs : 12;                 // file data over the link in the slice, KB/s (C_VERIFY: the card reading itself)
    uint16_t mark : 4;                 // the event that happened in it (EvType), 0 none
    uint8_t flags;                     // what the slice carried (K_*), C_VERIFY, C_FAIL, C_RETRY
};
const int HISTORY = 128;
const uint32_t SLICE_MS = 125;
extern Column hist[HISTORY];
extern uint32_t columns;               // slices so far; the newest is hist[(columns - 1) % HISTORY]

struct Stats {
    uint32_t cmds;                     // commands run
    uint32_t bytesIn, bytesOut;        // file data written to the card, read back to the PC
    uint32_t bytesChk;                 // ... and checked on the card (CHECK, COMMIT's read-back)
    uint32_t busyUs;                   // time inside commands, total
    uint32_t lastMs;                   // millis() of the last traffic
    uint16_t filesIn, filesOut, dirs;
    uint16_t dups, drops, fails;       // duplicates replayed, frames dropped (CRC), error answers
    uint16_t peakIn, peakOut;          // KB/s, the best slice
    uint16_t removed;                  // files removed
    uint8_t lastKind;                  // K_* of the last command
    uint32_t jobT0;                    // millis() of the HELLO that began the job
    uint32_t jobBytes;                 // ... and what it has moved since: files in or out, removed
    uint16_t jobFiles, jobRemoved;
};
extern Stats st;

// ---- Events -------------------------------------------------------------------
enum EvType : uint8_t {
    EV_NONE, EV_PUT, EV_GET, EV_CHK, EV_DIR, EV_LIST, EV_LINK, EV_CARD,
    EV_RECOVER, EV_ABORT, EV_STOP, EV_SYNC, EV_MENU, EV_FAIL, EV_DEL,
    EV_DONE = 0x80, EV_GOT,            // said only: a file committed, a file read to its end
};
struct Event {
    uint32_t value;                    // bytes, entries or a status, by type
    uint32_t done;                     // EV_PUT, EV_GET, EV_CHK: bytes so far
    uint32_t t;                        // millis() when it happened or finished
    uint8_t type;
    uint8_t live;                      // 1: still going, 2: EV_PUT being verified
    char name[14];                     // an 8.3 name, or what happened
};
const int EVENTS = 8;
extern Event ev[EVENTS];
extern uint32_t events;                // so far; the newest is ev[(events - 1) % EVENTS]
const Event *newest(int back);         // 0 = newest; nullptr past the end
const Event *liveFile();               // the file being received, or nullptr

// What the screen has still to announce (a beep, a banner): EvTypes, oldest first.
extern uint8_t said[8], saidCount;

// ---- Hooks, from Display.cpp --------------------------------------------------
void cardState(uint32_t now, uint8_t error);
void command(uint8_t cmd, uint16_t length);          // about to run
void result(uint32_t now, uint8_t cmd, const uint8_t *data, uint16_t length, uint8_t status,
            const uint8_t *out, uint16_t size);
void polled(uint32_t now);                           // a block was read inside a long command
void link(uint32_t now, uint8_t what, uint8_t cmd);  // 1 duplicate replayed, 2 refused, 3 frame dropped
void cancelled(uint32_t now, uint8_t action, uint8_t error);   // B or START: abort and sync have run
void tick(uint32_t now);                             // from the loop: closes a slice that has run its time

}  // namespace mon
