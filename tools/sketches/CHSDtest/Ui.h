// The screen: a status bar, three pages (LEFT/RIGHT) and the keys.
//   LOG    the bench's lines as they come, wrapped to the screen
//   CARD   what the card says it is (CID, CSD)
//   TESTS  the profile's verdicts, one row a test
#pragma once
#include <stdint.h>

namespace ui {

void begin();
void log(const char *line);                // a line to the log (and to the PC, by the caller)
void button(uint8_t b);                    // a d-pad press: pages and scrolling
// Draws a frame if one is due (something changed). Returns true if it drew;
// the caller flushes rows [y0, y1).
bool frame(uint32_t now, int &y0, int &y1);
void showTests();                          // the TESTS page, after a profile
void goodbye();

}  // namespace ui
