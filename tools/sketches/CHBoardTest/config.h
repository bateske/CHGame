// CHBoardTest's version and the board it is built for. CHBT is this
// sketch's prefix, and "CHBT" its debug hello (every sketch has its own:
// the repository's CLAUDE.md, rule 7). It saves nothing.
#pragma once
#define CHBT_VERSION "1.0"

// The board package passes -DARDUINO_<board> (0.4.0 and later): CHGAME_REV0
// or CHGAME_REV1. A Rev 1.5 board is a Rev1. An older package passes
// neither: it only knows Rev0, so the pins are Rev0's, but the screen says
// UNKNOWN rather than guess.
#if defined(ARDUINO_CHGAME_REV1)
#define CHBT_BOARD "REV1"
#define CHBT_REV1 1
#elif defined(ARDUINO_CHGAME_REV0)
#define CHBT_BOARD "REV0"
#define CHBT_REV1 0
#else
#define CHBT_BOARD "UNKNOWN"
#define CHBT_REV1 0
#endif
