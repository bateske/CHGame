// Bench: the tests, as commands. A line from the PC (USB serial) or a
// button runs one; what it finds goes out as lines (to the PC and to the
// screen's log), and the last line of every command is "OK" or "ERR ...".
// PROTOCOL.md lists the commands; PROFILE is the whole test, the one the A
// button runs.
#pragma once
#include <stdint.h>

namespace bench {

void begin(void (*out)(const char *line));
// Called between the steps of a long command, so the screen can keep up.
void setTick(void (*fn)());
// The PANEL command starts the screen through this (the sketch's): with a PC
// attached, the panel stays off until it is asked for, so a test can see the
// card before the panel has ever been on the bus.
void setPanel(void (*fn)());
// One command line ("READ 0 100"); false if it was not a command.
bool run(char *line);
void profile();

// What the screen shows.
enum Verdict : uint8_t { V_NONE, V_PASS, V_WARN, V_FAIL };
struct Result {
    char name[8];
    uint8_t verdict;
    char note[24];
};
static const int MAX_RESULTS = 16;
extern Result results[MAX_RESULTS];
extern int nResults;
extern bool busy;                  // a command is running (the screen shows progress)
extern bool hold;                  // a measurement needs a quiet bus: the screen waits
extern uint8_t progress;           // 0-100 within it
extern char task[24];              // what it is doing
// The card as identified last (none: cardOk false).
extern bool cardOk;
extern uint8_t cid[16], csd[16];
extern bool haveRegs;
extern uint32_t blocks;

}  // namespace bench
