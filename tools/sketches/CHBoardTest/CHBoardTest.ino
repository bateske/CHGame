// CHBoardTest - one screen that checks a CHGame board, for bring-up.
//
// One source builds for Rev0 and Rev1 (a Rev 1.5 board is a Rev1); the
// board it was built for is at the top right. Below it are the eight
// buttons, drawn live, then the checks, one a line, each with what it
// found. The bottom line says how to run the one picked. README.md says
// what each should read.
//
//   UP / DOWN       pick a check
//   A               run it (SWEEP: hold the note, then go on)
//   B               stop the sound
//   SELECT 2 s + A  on TP14/15: the pull-up test (Rev 1 only, not 1.5);
//                   on FAULT: the deliberate crash
//   START (3 s)     leave: the library's gesture, back to the SD game menu
//
// It runs at 60 frames a second, the rate the library's START hold counts
// in (180 frames).
//
// With the USB serial port open, each result is also a line on it
// ("CHBT SD: OK FAT32 7.4GB"), except in a debug build, where the port is
// the debug protocol's.
//
// The files:
//   CHBoardTest.ino   the screen, the buttons, the LED, the backlight, the sound
//   Checks.*          SD, VBUS, CN3, CN2, the test pads and the fault
//   config.h          the version and the board
//
// It lives in tools/sketches, not among the CHGame library's examples: the
// board package does not ship it. It runs on the board only.
#include <CHGame.h>
#include "config.h"
#include "Checks.h"

using checks::Result;
using checks::Text;

// Results go to USB Serial in a release build with USB Serial on.
#if defined(USE_CHGAME_USB_CDC) && !CHGAME_DEBUG
#define CHBT_SERIAL 1
#else
#define CHBT_SERIAL 0
#endif

static const uint8_t FPS = 60;

static void report(const char *what, const char *text) {
#if CHBT_SERIAL
    if (!Serial) return;
    Serial.write("CHBT ");
    Serial.write(what);
    Serial.write(": ");
    Serial.write(text);
    Serial.write("\r\n");
#else
    (void)what;
    (void)text;
#endif
}

// ---------------------------------------------------------------------------
// The checks, top to bottom
// ---------------------------------------------------------------------------
enum Item : uint8_t { I_SWEEP, I_SOAK, I_SD, I_VBUS, I_UART, I_LINES, I_PADS, I_LED, I_LIGHT, I_FAULT };
static const char *const NAMES[] = {"SWEEP", "SOAK", "SD CARD", "VBUS", "CN3 UART",
                                    "CN2 I2C", "TP14/15", "LED", "BACKLIGHT", "FAULT"};
static const uint8_t ITEMS[] = {
    I_SWEEP, I_SOAK, I_SD,
#if CHBT_REV1
    I_VBUS,
#endif
    I_UART, I_LINES,
#if CHBT_REV1
    I_PADS,
#endif
    I_LED, I_LIGHT, I_FAULT,
};
static const uint8_t N_ITEMS = sizeof ITEMS;
static uint8_t cur;                         // the picked line

// What the checks found.
static Result sdRes, sdDetail, uartRes, linesRes, vbusRes, faultRes;
#if CHBT_REV1
static Result padsRes;
#endif
static uint8_t sdPending;                   // 1: A pressed; 2: "READING" drawn; then it runs
static uint8_t seen;                        // the buttons pressed at least once
static uint16_t selectHeld;                 // frames SELECT has been held
static const char *const BUTTONS[8] = {"A", "B", "UP", "DOWN", "LEFT", "RIGHT", "START", "SELECT"};

// ---------------------------------------------------------------------------
// Sound
// ---------------------------------------------------------------------------
// A chirp when a check passes.
AUDIO_STEPS(CHIRP) = {AUDIO_STEP(2100, 0, 30), AUDIO_REST(20), AUDIO_STEP(3100, 0, 60)};
const audio::Effect SOUNDS[] = {AUDIO_EFFECT(CHIRP, 2)};

// The sweep: a one-note melody that loops with no gap, so it is one steady
// tone, and its note goes up a semitone every SWEEP_MS. C2 (65 Hz) to B8
// (7,902 Hz), the library's top note. A holds a note, to write down where
// the buzzer is loud and where it fades.
static const uint8_t SWEEP_LO = 36, SWEEP_HI = 119;
static const uint16_t SWEEP_MS = 150;
static uint8_t sweepTune[2] = {SWEEP_LO, 1};
static const audio::Melody SWEEP_MEL = {sweepTune, 1, 100, 0};

// The soak: game music's load, arpeggios from F5 to C7 (698 to 2,093 Hz)
// with short gaps, so the buzzer is driven about 90% of the time.
static const uint8_t SOAK_TUNE[] = {
    84, 1, 88, 1, 91, 1, 96, 1,   81, 1, 84, 1, 88, 1, 93, 1,
    77, 1, 81, 1, 84, 1, 89, 1,   79, 1, 83, 1, 86, 1, 91, 1,
};
static const audio::Melody SOAK_MEL = {SOAK_TUNE, sizeof SOAK_TUNE / 2, 125, 12};

enum : uint8_t { S_IDLE, S_SWEEP, S_HOLD, S_SOAK };
static uint8_t sound = S_IDLE;
static uint32_t soundAt;                    // the sweep's note, or the soak, started then
static bool sweepDone;
static uint16_t soakSecs;                   // the soak's time, kept when it stops
static uint16_t soakMinutes;                // minutes already reported

// MIDI note to Hz, as the library plays it: the top octave, shifted down.
static uint16_t noteHz(uint8_t n) {
    static const uint16_t TOP[12] = {4186, 4435, 4699, 4978, 5274, 5588, 5920, 6272, 6645, 7040, 7459, 7902};
    return TOP[n % 12] >> (9 - n / 12);
}

static void noteText(Text &t, uint8_t n) {
    static const char LETTER[] = "CCDDEFFGGAAB";
    char name[3] = {LETTER[n % 12], (char)((0x54A >> (n % 12)) & 1 ? '#' : 0), 0};
    t.s(name).n(n / 12 - 1).s(" ").n(noteHz(n)).s("HZ");
}

static void startSweep() {
    sweepTune[0] = SWEEP_LO;
    audio::melody(SWEEP_MEL);
    sound = S_SWEEP;
    sweepDone = false;
    soundAt = millis();
    report("SWEEP", "STARTED AT C2 65HZ");
}

static void startSoak() {
    audio::melody(SOAK_MEL);
    sound = S_SOAK;
    soakSecs = soakMinutes = 0;
    soundAt = millis();
    report("SOAK", "STARTED");
}

static void stopSound() {
    if (sound == S_IDLE) return;
    audio::stopMusic();
    if (sound == S_SOAK) {
        char b[8];
        fmtTime(b, soakSecs);
        report("SOAK STOPPED", b);
    } else {
        report("SWEEP", "STOPPED");
    }
    sound = S_IDLE;
}

static void tickSound() {
    uint32_t now = millis();
    if (sound == S_SWEEP && now - soundAt >= SWEEP_MS) {
        soundAt += SWEEP_MS;
        if (sweepTune[0] < SWEEP_HI) {
            sweepTune[0]++;                 // the melody reads it every ms
        } else {
            audio::stopMusic();
            sound = S_IDLE;
            sweepDone = true;
            report("SWEEP", "DONE, SILENT");
        }
    } else if (sound == S_SOAK) {
        soakSecs = (uint16_t)((now - soundAt) / 1000);
        if (soakSecs / 60 > soakMinutes) {
            soakMinutes = soakSecs / 60;
            char b[8];
            fmtTime(b, soakSecs);
            report("SOAK", b);
        }
    }
}

static void chirpIf(const Result &r) {
    if (r.colour == FELT_LT) audio::sfx(0);
}

// ---------------------------------------------------------------------------
// LED and backlight
// ---------------------------------------------------------------------------
enum : uint8_t { L_OFF, L_ON, L_BLINK };
static const char *const LED_NAMES[] = {"OFF", "ON", "BLINKING"};
static uint8_t ledMode = L_OFF;

static void tickLed() {
    bool lit = ledMode == L_ON || (ledMode == L_BLINK && ((millis() >> 8) & 1));
    digitalWrite(PIN_LED, lit ? HIGH : LOW);
}

// Rev1's backlight is a pin (PB9, active high). CHGfx's gfx_begin() keeps it
// low, blanks the panel, and only then lights it; A here darkens it for 1 s.
// Rev0's backlight has no pin: it is on whenever the board is.
#ifdef PIN_LCD_BL
static bool dark;
static uint32_t darkAt;

static void tickLight() {
    if (dark && millis() - darkAt >= 1000) {
        digitalWrite(PIN_LCD_BL, HIGH);
        dark = false;
    }
}
#endif

// ---------------------------------------------------------------------------
// The deliberate fault
// ---------------------------------------------------------------------------
// The LED goes off first, so a lit LED afterwards is the handler's doing.
static void crash() {
    report("FAULT", "LED OFF, A TONE, THEN AN ILLEGAL INSTRUCTION");
    ledMode = L_OFF;
    digitalWrite(PIN_LED, LOW);
    stopSound();
    gfx_wait();
    gfx_clear(INK);
    gfx_fillRect(0, 0, GFX_W, 9, WINE);
    text35(2, 2, "DELIBERATE FAULT", WHITE);
    text35(2, 14,
           "THE LED WAS TURNED OFF. A TONE\n"
           "SOUNDS, THEN AN ILLEGAL\n"
           "INSTRUCTION RUNS. THE CORE'S\n"
           "FAULT HANDLER SHOULD NOW HAVE:\n"
           "\n"
           "- SILENCED THE BUZZER\n"
           "- LIT THE LED\n"
           "- LEFT THIS SCREEN AS IT IS\n"
           "\n"
           "POWER OFF AND ON TO GO ON.",
           WHITE);
    pal::commit();
    gfx_flush();                            // on the panel before the crash
    checks::fault();
    // Still here: the instruction did not trap.
    Text(faultRes, RED).s("NOT TRAPPED");
    report("FAULT", "NOT TRAPPED: STILL RUNNING");
}

// ---------------------------------------------------------------------------
// The buttons
// ---------------------------------------------------------------------------
// Two checks run only when armed, SELECT held 2 s, then A: FAULT, which
// stops the board, and TP14/15, which must not run on a Rev 1.5 (its pads
// are CC1/CC2 there, and this firmware cannot tell a 1.5 from a Rev 1).
static bool armed() { return selectHeld >= 2 * FPS; }

static void act(uint8_t item) {
    switch (item) {
    case I_SWEEP:
        if (sound == S_SWEEP) {
            sound = S_HOLD;
        } else if (sound == S_HOLD) {
            sound = S_SWEEP;
            soundAt = millis();
        } else {
            startSweep();
        }
        break;
    case I_SOAK:
        if (sound != S_SOAK) startSoak();
        break;
    case I_SD:
        sdPending = 1;                      // run after gfx_wait(): SPI1 is the panel's too
        break;
    case I_UART:
        checks::uartLoop(uartRes);
        chirpIf(uartRes);
        report("CN3", uartRes.text);
        break;
#if CHBT_REV1
    case I_PADS:
        if (!armed()) break;
        checks::testPads(padsRes);
        report("TP14/15", padsRes.text);
        break;
#endif
    case I_LED:
        ledMode = (uint8_t)((ledMode + 1) % 3);
        report("LED", LED_NAMES[ledMode]);
        break;
    case I_LIGHT:
#ifdef PIN_LCD_BL
        digitalWrite(PIN_LCD_BL, LOW);
        dark = true;
        darkAt = millis();
        report("BACKLIGHT", "DARK FOR 1 S");
#endif
        break;
    case I_FAULT:
        if (armed()) crash();
        break;
    }
}

static void tickReport() {
#if CHBT_SERIAL
    static bool open = false;
    bool now = (bool)Serial;
    if (now && !open) report("BOARD", CHBT_BOARD ", CHBOARDTEST " CHBT_VERSION);
    open = now;
#if CHBT_REV1
    static uint32_t vbusAt;
    if (open && millis() - vbusAt >= 5000) {
        vbusAt = millis();
        report("VBUS", vbusRes.text);
    }
#endif
#endif
}

static void logic() {
    uint8_t held = chgame.buttons();
    uint8_t fresh = (uint8_t)(held & ~seen);
    for (uint8_t i = 0; i < 8; i++)
        if ((fresh >> i) & 1) report("BUTTON", BUTTONS[i]);
    seen |= held;
    if (!(held & SELECT_BUTTON)) selectHeld = 0;
    else if (selectHeld < 0xFFFF) selectHeld++;

    if (chgame.repeat(UP_BUTTON)) cur = cur ? cur - 1 : N_ITEMS - 1;
    if (chgame.repeat(DOWN_BUTTON)) cur = cur + 1 < N_ITEMS ? cur + 1 : 0;
    if (chgame.justPressed(A_BUTTON)) act(ITEMS[cur]);
    if (chgame.justPressed(B_BUTTON)) stopSound();

    tickSound();
    tickLed();
#ifdef PIN_LCD_BL
    tickLight();
#endif
#if CHBT_REV1
    if (chgame.everyXFrames(16)) checks::vbus(vbusRes);
#endif
    static uint8_t lines = 0xFF;            // the CN2 levels last reported
    uint8_t now = checks::i2cLines(linesRes);
    if (now != lines) {
        lines = now;
        report("CN2", linesRes.text);
    }
    tickReport();
}

// ---------------------------------------------------------------------------
// The screen
// ---------------------------------------------------------------------------
static const int ROW_Y = 40, ROW_H = 8, VALUE_X = 44, HELP_Y = 122;

// An armed check's line while SELECT is held on it; false otherwise.
static bool arming(uint8_t item, Result &v, const char *armedText) {
    if (ITEMS[cur] != item || !selectHeld) return false;
    if (armed()) Text(v, RED).s(armedText);
    else Text(v, GOLD).s("HOLD SELECT...");
    return true;
}

static void value(uint8_t item, Result &v) {
    char b[8];
    switch (item) {
    case I_SWEEP:
        if (sound == S_SWEEP || sound == S_HOLD) {
            Text t(v, GOLD);
            noteText(t, sweepTune[0]);
            if (sound == S_HOLD) t.s(" HELD");
        } else if (sweepDone) {
            Text(v, FELT_LT).s("DONE, SILENT");
        } else {
            Text(v, SILVER).s("PRESS A");
        }
        break;
    case I_SOAK:
        fmtTime(b, soakSecs);
        if (sound == S_SOAK) Text(v, soakSecs >= 600 ? FELT_LT : GOLD).s("PLAYING ").s(b);
        else if (soakSecs) Text(v, SILVER).s("STOPPED AT ").s(b);
        else Text(v, SILVER).s("PRESS A");
        break;
    case I_SD:
        if (sdPending) Text(v, GOLD).s("READING...");
        else v = sdRes;
        break;
    case I_VBUS:  v = vbusRes; break;
    case I_UART:  v = uartRes; break;
    case I_LINES: v = linesRes; break;
#if CHBT_REV1
    case I_PADS:
        if (arming(I_PADS, v, "ARMED: A TESTS")) break;
        if (padsRes.text[0]) v = padsRes;
        else Text(v, SILVER).s("SELECT 2 S, THEN A");
        break;
#endif
    case I_LED:
        Text(v, ledMode ? GOLD : SILVER).s(LED_NAMES[ledMode]);
        break;
    case I_LIGHT:
#ifdef PIN_LCD_BL
        if (dark) Text(v, GOLD).s("DARK FOR 1 S");
        else Text(v, WHITE).s("LIT AFTER BLANKING");
#else
        Text(v, SILVER).s("ALWAYS ON");
#endif
        break;
    case I_FAULT:
        if (arming(I_FAULT, v, "ARMED: A CRASHES")) break;
        if (faultRes.text[0]) v = faultRes;
        else Text(v, SILVER).s("SELECT 2 S, THEN A");
        break;
    }
}

// The bottom line: how to run the picked check, or what it found in detail.
static void help(uint8_t item, Result &h) {
    const char *s = "";
    switch (item) {
    case I_SWEEP: s = "C2 TO B8: A HOLDS, B STOPS"; break;
    case I_SOAK:  s = "A STARTS, B STOPS. RUN 10 MIN"; break;
    case I_SD:
        if (sdDetail.text[0]) {
            h = sdDetail;
            return;
        }
        s = "A: INIT, READ SECTOR 0, MOUNT";
        break;
    case I_VBUS:  s = "PA0 = VBUS/101, 81 MV A CODE"; break;
    case I_UART:  s = "JUMPER CN3 TX TO RX, THEN A"; break;
#if CHBT_REV1
    case I_LINES: s = "LEVELS ONLY: NO I2C IS SENT"; break;
#else
    case I_LINES: s = "LEVELS ONLY; REV0: NO PULL-UPS"; break;
#endif
#if CHBT_REV1
    case I_PADS:  s = "REV 1 ONLY: ON 1.5 THEY ARE CC"; break;
#endif
    case I_LED:   s = "A: OFF, ON, BLINKING"; break;
#ifdef PIN_LCD_BL
    case I_LIGHT: s = "A: DARK FOR 1 S"; break;
#else
    case I_LIGHT: s = "THIS BOARD HAS NO BACKLIGHT PIN"; break;
#endif
    case I_FAULT: s = "STOPS THE BOARD: POWER CYCLE"; break;
    }
    Text(h, SILVER).s(s);
}

static void drawButton(int x, int y, int w, const char *label, uint8_t b) {
    bool down = chgame.pressed(b);
    gfx_fillRect(x, y, w, 9, down ? GOLD : INK);
    gfx_rect(x, y, w, 9, down ? WHITE : (seen & b) ? CYAN : SILVER);
    text35(x + (w - text35Width(label)) / 2, y + 2, label, down ? INK : WHITE);
}

static void draw() {
    gfx_clear(INK);
    gfx_fillRect(0, 0, GFX_W, 9, NAVY);
    text35(2, 2, "CHGAME BOARD TEST " CHBT_VERSION, WHITE);
    text35(126 - text35Width(CHBT_BOARD), 2, CHBT_BOARD, GOLD);

    // The buttons: held is gold, pressed at least once has a cyan edge.
    drawButton(13, 11, 9, "U", UP_BUTTON);
    drawButton(3, 20, 9, "L", LEFT_BUTTON);
    drawButton(23, 20, 9, "R", RIGHT_BUTTON);
    drawButton(13, 29, 9, "D", DOWN_BUTTON);
    drawButton(36, 26, 27, "SELECT", SELECT_BUTTON);
    drawButton(66, 26, 23, "START", START_BUTTON);
    drawButton(92, 26, 11, "B", B_BUTTON);
    drawButton(107, 18, 11, "A", A_BUTTON);
    uint8_t n = 0;
    for (uint8_t m = seen; m; m &= (uint8_t)(m - 1)) n++;
    char b[16], *p = fmtStr(b, "BUTTONS ");
    p = fmtInt(p, n);
    fmtStr(p, "/8");
    text35(36, 13, b, n == 8 ? FELT_LT : SILVER);

    for (uint8_t i = 0; i < N_ITEMS; i++) {
        int y = ROW_Y + i * ROW_H;
        bool picked = i == cur;
        if (picked) gfx_fillRect(0, y, GFX_W, ROW_H, NAVY);
        text35(3, y + 2, NAMES[ITEMS[i]], picked ? GOLD : SILVER);
        Result v;
        value(ITEMS[i], v);
        text35(VALUE_X, y + 2, v.text, v.colour);
    }
    Result h;
    help(ITEMS[cur], h);
    gfx_hline(0, HELP_Y - 2, GFX_W, NAVY);
    text35(2, HELP_Y, h.text, h.colour);
}

// ---------------------------------------------------------------------------
void setup() {
    chgame.boot();                          // START held 3 s still leaves for the menu
    dbg::begin("CHBT " CHBT_VERSION);
#if CHBT_SERIAL
    Serial.begin();
#endif
    audio::begin(SOUNDS, 1);
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);
    gfx_begin(GFX_DIV2, GFX_12BPP);         // Rev1: lights the backlight once the panel is black
    pal::init();
    chgame.setFrameRate(FPS);
    Text(sdRes, SILVER).s("PRESS A");
    Text(uartRes, SILVER).s("PRESS A");
#if CHBT_REV1
    analogReadResolution(12);
    checks::vbus(vbusRes);
#endif
}

void loop() {
    dbg::poll();
    if (!chgame.nextFrame()) return;
    chgame.pollButtons();
    logic();
    pal::tick();
    audio::update();

    gfx_wait();
    if (sdPending && ++sdPending > 2) {     // "READING" went out last frame
        checks::sd(sdRes, sdDetail);
        sdPending = 0;
        chirpIf(sdRes);
        report("SD", sdRes.text);
        report("SD", sdDetail.text);
    }
    pal::commit();
    draw();
    gfx_flushAsync();
}
