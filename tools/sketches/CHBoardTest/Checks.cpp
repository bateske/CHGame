// The board's checks (Checks.h). Every pin comes from the board's variant
// (PIN_VBUS_SENSE, PIN_WIRE_SDA, PIN_TP14 ...), so one source serves both
// boards; the only Rev1-only checks are VBUS and the test pads.
#include <CHGame.h>
#include <SdSpi.h>
#include <Fat.h>
#include "Checks.h"

namespace checks {

Text &Text::n(int32_t v) {
    char b[12];
    fmtInt(b, v);
    return s(b);
}

// ---------------------------------------------------------------------------
// SD
// ---------------------------------------------------------------------------
static uint32_t le32(const uint8_t *b) {
    return b[0] | (uint32_t)b[1] << 8 | (uint32_t)b[2] << 16 | (uint32_t)b[3] << 24;
}

static void size(Text &t, uint32_t sectors) {
    uint32_t mb = sectors >> 11;
    if (mb < 1024) {
        t.n(mb).s("MB");
        return;
    }
    uint32_t g10 = mb * 10 / 1024;
    t.n(g10 / 10).s(".").n(g10 % 10).s("GB");
}

void sd(Result &r, Result &detail) {
    static uint8_t buf[512] __attribute__((aligned(4)));
    uint32_t t0 = millis();
    bool ok = sd::init();
    uint32_t ms = millis() - t0;
    if (!ok) {
        Text(r, RED).s("NO CARD");
        Text(detail, SILVER).s("NO ANSWER AFTER ").n(ms).s(" MS");
        return;
    }
    if (!sd::read(0, buf)) {
        Text(r, RED).s("SECTOR 0 FAILED");
        Text(detail, SILVER).s("INIT OK (").n(ms).s(" MS), NO DATA");
        return;
    }
    bool sig = buf[510] == 0x55 && buf[511] == 0xAA;
    // CHSd reads blocks, not the card's registers (CSD, CID), so the size
    // shown is the volume's: the first MBR partition's, or a volume that
    // starts at sector 0 (no partition table) from its boot sector. A jump
    // alone does not make a boot sector (GRUB's and syslinux's MBRs start
    // EB 63 and EB 5E): it also needs a BPB, 512 bytes a sector and a power
    // of two sectors a cluster.
    uint8_t spc = buf[0x0D];
    bool vbr = (buf[0] == 0xEB || buf[0] == 0xE9) && buf[0x0B] == 0x00 && buf[0x0C] == 0x02
               && spc && !(spc & (spc - 1));
    uint8_t type = 0;
    uint32_t sectors;
    if (vbr) {
        sectors = buf[0x13] | (uint32_t)buf[0x14] << 8;
        if (!sectors) sectors = le32(buf + 0x20);
    } else {
        type = buf[0x1C2];
        sectors = le32(buf + 0x1CA);
    }
    int8_t fs = fat::mount(buf);            // clobbers buf
    const char *name = fs == fat::E_EXFAT ? "EXFAT"
                     : fs == fat::E_NOFS ? "NO FAT"
                     : fs != fat::OK ? "READ ERR"
                     : type == 0x0B || type == 0x0C ? "FAT32"
                     : type == 0x04 || type == 0x06 || type == 0x0E ? "FAT16"
                     : "FAT";
    // Green when the games could read it; gold when the card works but its
    // volume is not one CHSd mounts.
    Text t(r, fs == fat::OK ? FELT_LT : GOLD);
    t.s("OK ").s(name);
    if (sectors) {
        t.s(" ");
        size(t, sectors);
    }
    Text(detail, SILVER).s("INIT ").n(ms).s(" MS, ").s(sig ? "55AA OK" : "NO 55AA")
        .s(vbr ? ", NO MBR" : ", MBR");
}

// ---------------------------------------------------------------------------
// CN3: the UART loopback
// ---------------------------------------------------------------------------
// Serial1.begin() sets up the pins, the baud rate and the USART, but the
// core's Serial1 cannot receive on these pins: it is built for USART1,
// uart_init() takes the USART from the pins (PA2/PA3: USART2), and begin()
// then enables the receive interrupt for USART1 only, so Serial1.read()
// never returns a byte. So the check runs on the USART's registers, polled,
// one byte at a time: each comes back about 87 us after it is sent. The
// USART is the one uart_init() chose, found the same way, from the pin map.
void uartLoop(Result &r) {
#if defined(HAVE_HWSERIAL1)
    static bool begun = false;
    if (!begun) {                           // started once, then left on: TX idles high
        Serial1.begin(115200);
        begun = true;
        delay(2);
    }
    USART_TypeDef *u = (USART_TypeDef *)pinmap_peripheral(digitalPinToPinName(PIN_SERIAL_TX),
                                                           PinMap_UART_TX);
    if (u == NP) {
        Text(r, RED).s("NO USART ON TX PIN");
        return;
    }
    // A core that serves this USART by interrupt would take the bytes first:
    // its receive interrupt is off for the test, then put back.
    uint16_t ctlr1 = u->CTLR1;
    u->CTLR1 = (uint16_t)(ctlr1 & ~USART_CTLR1_RXNEIE);
    (void)u->STATR;                         // a stale byte or an overrun: drop it
    (void)u->DATAR;
    static const uint8_t PAT[16] = {'C', 'H', 'B', 'T', ' ', 'C', 'N', '3',
                                    0x55, 0xAA, 0x00, 0xFF, 0x0F, 0xF0, 0x81, 0x7E};
    uint8_t got = 0, good = 0;
    for (uint8_t i = 0; i < sizeof PAT; i++) {
        while (!(u->STATR & USART_FLAG_TXE)) {}
        u->DATAR = PAT[i];
        uint32_t t0 = micros();
        while (!(u->STATR & USART_FLAG_RXNE) && micros() - t0 < 1000) {}
        if (!(u->STATR & USART_FLAG_RXNE)) continue;
        got++;
        if ((uint8_t)u->DATAR == PAT[i]) good++;
    }
    u->CTLR1 = ctlr1;
    if (!got) Text(r, RED).s("NO LOOP");
    else if (good == sizeof PAT) Text(r, FELT_LT).s("PASS 16/16 AT 115200");
    else Text(r, RED).s("BAD ").n(good).s("/16 RIGHT");
#else
    // Built with Peripherals "Game", which compiles Serial1 out.
    Text(r, GOLD).s("NEEDS PERIPH FULL");
#endif
}

// ---------------------------------------------------------------------------
// CN2: the I2C lines' levels
// ---------------------------------------------------------------------------
// The pins are left exactly as they are (after reset: floating inputs, and
// the two-wire debug interface's DIO and DCK): reading INDR sends nothing.
// Nothing here addresses a device: on Rev 1.5, 0x34/0x35 (CH211) and 0x40
// (INA226) are the power devices, and only the power library talks to them.
// Port C's clock is on already: chgame.boot() set up buttons on port C (Rev0
// DOWN and RIGHT, Rev1 LEFT and RIGHT).
// Rev1 and Rev 1.5 pull both lines up (4.7k), so low is a fault there. Rev0
// has no pull-ups on them: its levels are shown with no verdict.
uint8_t i2cLines(Result &r) {
    bool sda = digitalRead(PIN_WIRE_SDA), scl = digitalRead(PIN_WIRE_SCL);
#if CHBT_REV1
    Text t(r, sda && scl ? FELT_LT : RED);
#else
    Text t(r, SILVER);
#endif
    t.s("SDA ").s(sda ? "H" : "L").s(" SCL ").s(scl ? "H" : "L");
#if CHBT_REV1
    t.s(sda && scl ? " IDLE HIGH" : " HELD LOW");
#endif
    return (uint8_t)(sda | scl << 1);
}

#if CHBT_REV1
// ---------------------------------------------------------------------------
// PA0: VBUS sense (Rev1)
// ---------------------------------------------------------------------------
// VBUS / 101 (R28 100k over R11 1k). analogRead() puts PA0 in analog input
// mode, which never drives it: on Rev 1.5 it is also HOST_EN, and R11 keeps
// the host boost off while nothing drives it. 12-bit codes against the 3.3 V
// rail, so one code is about 81 mV of VBUS: coarse, and uncalibrated.
void vbus(Result &r) {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < 16; i++) sum += analogRead(PIN_VBUS_SENSE);
    uint32_t mv = sum * 20831u / 4095u;     // (sum / 16) / 4095 x 3300 mV x 101
    uint32_t d = (mv + 50) / 100;           // tenths of a volt
    Text(r, mv >= 4000 ? FELT_LT : GOLD).n(d / 10).s(".").n(d % 10).s("V CODE ").n((sum + 8) / 16)
        .s(" COARSE");
}

// ---------------------------------------------------------------------------
// TP14 / TP15 (Rev1)
// ---------------------------------------------------------------------------
// A pad nothing else holds follows the MCU's pull-up: FREE. One that reads
// LOW is tied to something, such as a CC line's 5.1k Rd. A pull-up only,
// never an output, and the pad goes back to a floating input. (There is no
// pull-down to try: the CH32X035 has them on PA0-PA15 and PC16-PC17 only,
// so a pad held HIGH looks free.) This firmware cannot tell a Rev 1 from a
// Rev 1.5, where PC14/PC15 are CC1/CC2 through the CH211, so the sketch runs
// this only when the operator arms it (SELECT held 2 s, then A).
static bool pulledHigh(uint32_t pin) {
    pinMode(pin, INPUT_PULLUP);
    delayMicroseconds(200);
    bool up = digitalRead(pin);
    pinMode(pin, INPUT);
    return up;
}

void testPads(Result &r) {
    bool a = pulledHigh(PIN_TP14), b = pulledHigh(PIN_TP15);
    Text(r, a && b ? FELT_LT : RED).s("TP14 ").s(a ? "FREE" : "LOW").s(" TP15 ").s(b ? "FREE" : "LOW");
}
#endif

// ---------------------------------------------------------------------------
// The deliberate fault
// ---------------------------------------------------------------------------
void fault() {
    audio::note(2000, 500, 15);             // the tone the handler must silence
    uint32_t t0 = millis();
    while (millis() - t0 < 250) {}
    // c.unimp: the all-zero 16-bit instruction, which RISC-V reserves as
    // illegal. (A call through a null pointer would not fault here: address
    // 0 is flash, the bootloader's own start, so it would simply restart.)
    __asm volatile (".2byte 0x0000" ::: "memory");
}

}  // namespace checks
