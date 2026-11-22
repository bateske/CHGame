// The board's checks. Each leaves a Result: the text the screen shows
// beside the check's name, and the line the USB serial port reports.
#pragma once
#include <stdint.h>
#include "config.h"

namespace checks {

struct Result {
    char text[33];      // the help line's 32 characters at most; a value is 21
    uint8_t colour;     // a house colour: FELT_LT pass, RED fail, GOLD note
};

// A Result's text, built a piece at a time and cut at the buffer's end:
// Text(r, RED).s("BAD ").n(3).s("/16").
class Text {
public:
    Text(Result &r, uint8_t colour) : p(r.text), end(r.text + sizeof r.text - 1) {
        r.colour = colour;
        *p = 0;
    }
    Text &s(const char *t) {
        while (*t && p < end) *p++ = *t++;
        *p = 0;
        return *this;
    }
    Text &n(int32_t v);
private:
    char *p, *end;
};

// SD: CHSd's sd::init(), sector 0, then fat::mount(). SPI1 is the panel's
// too, so only between gfx_wait() and the next flush. `detail` gets the
// init time, the 55AA signature and whether sector 0 is an MBR.
void sd(Result &r, Result &detail);

// CN3: Serial1's pins (USART2, PA2 TX, PA3 RX) at 115200. 16 bytes, one at
// a time, each waited for up to 1 ms: TX jumpered to RX sends them back.
void uartLoop(Result &r);

// CN2: SDA (PC18) and SCL (PC19) read as they are. No I2C at all. Returns
// the levels (bit 0 SDA, bit 1 SCL), to report a change.
uint8_t i2cLines(Result &r);

#if CHBT_REV1
// PA0: VBUS / 101, read with the ADC (16 samples averaged).
void vbus(Result &r);
// TP14 / TP15: each pulled up, read, then left floating again. Rev 1 only:
// on a Rev 1.5 they are CC1/CC2.
void testPads(Result &r);
#endif

// A tone, then an illegal instruction: the core's fault handler takes over
// and never returns. This returns only if the instruction did not trap.
void fault();

}  // namespace checks
