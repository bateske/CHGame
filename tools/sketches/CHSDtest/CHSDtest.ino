// CHSDtest - an SD card test bench.
//
// Put a card in and press A: the CHGame tries the card every way a driver
// could talk to it (identification variants, each SPI clock from 187.5 kHz
// to 24 MHz, the panel's traffic between reads, the menu bootloader's own
// sequence, multi-block reads, the gaps the SD specification asks for) and
// says which work. It only reads: nothing on the card changes.
//
// The same tests run from a PC over the USB serial port, one command a line
// (PROTOCOL.md): every setting can be changed and every command traced byte
// by byte, so a card that misbehaves can be taken apart. That is what it is
// for: finding out why a card fails, and what a driver (CHSd, the menu
// bootloader) has to do to make it work.
//
//   A              run the profile
//   B              identify the card again (INIT and its registers)
//   LEFT / RIGHT   the page: LOG, CARD, TESTS
//   UP / DOWN      scroll the log
//   START (3 s)    back to the SD game menu
//
// The files:
//   CHSDtest.ino   the serial port and the buttons
//   Bench.*        the tests, as commands
//   Probe.*        the card, one SPI command at a time, every choice a setting
//   Ui.*           the screen
//   Agent.*        the secret agent chrome (a copy of CHSDtoUSB's)
//
// It lives in tools/sketches, not among the CHGame library's examples: the
// board package does not ship it.
//   Fx.*, Sounds.* the beeps
#include <CHGame.h>
#include <string.h>
#include "config.h"
#include "Bench.h"
#include "Probe.h"
#include "Ui.h"
#include "Sounds.h"

static char rx[120];
static uint8_t rxN;
static uint32_t lastDraw;

static bool pcSeen;                     // a command came over USB
static const uint32_t PC_WINDOW_MS = 6000;   // how long the panel waits for one at start

static void draw(bool force) {
    if (bench::hold || !probe::panelUp) return;
    uint32_t now = millis();
    if (!force && now - lastDraw < 120) return;
    int y0, y1;
    if (ui::frame(now, y0, y1)) {
        pal::commit();
        gfx_flushRect(0, y0, GFX_W, y1 - y0);
    }
    lastDraw = now;
}

static void out(const char *line) {
    if (Serial) {
        Serial.write(line, strlen(line));
        Serial.write("\r\n", 2);
    }
    ui::log(line);
    draw(false);
}

static void tick() { draw(false); }

// The panel's start: CHGfx's initialisation and the first frame. Until
// then nothing but the card is on SPI1.
static void startPanel() {
    gfx_begin(GFX_DIV2, GFX_12BPP);
    probe::panelUp = true;
    ui::begin();
    out("PANEL ON");
    draw(true);
}

static void command(const char *text) {
    char line[sizeof rx];
    strncpy(line, text, sizeof line - 1);
    line[sizeof line - 1] = 0;
    bool profile = !strcmp(line, "PROFILE");
    audio::sfx(Sfx::Start);
    bench::run(line);
    if (profile) {
        bool fail = false;
        for (int i = 0; i < bench::nResults; i++) fail |= bench::results[i].verdict == bench::V_FAIL;
        audio::sfx(fail ? Sfx::Fail : Sfx::Pass);
        ui::showTests();
    }
    draw(true);
}

void setup() {
    chgame.boot();
    pinMode(LED_BUILTIN, OUTPUT);
    probe::hwInit();                    // the bus is the card's alone until the panel starts
    soundsBegin();
    chgame.setFrameRate(25);
    Serial.begin(115200);
    bench::begin(out);
    bench::setTick(tick);
    bench::setPanel(startPanel);
    out("CHST " CHST_VERSION " READY, PANEL OFF");
}

void loop() {
    while (Serial.available()) {
        int c = Serial.read();
        if (c == '\r' || c == '\n') {
            if (rxN) {
                rx[rxN] = 0;
                rxN = 0;
                pcSeen = true;
                digitalWrite(LED_BUILTIN, HIGH);
                command(rx);
                digitalWrite(LED_BUILTIN, LOW);
            }
        } else if (rxN < sizeof rx - 1) rx[rxN++] = (char)c;
    }
    // On its own (no PC within the window), the screen starts and the buttons run it.
    if (!probe::panelUp && !pcSeen && millis() > PC_WINDOW_MS) startPanel();
    if (!chgame.nextFrame()) return;
    chgame.pollButtons();
    if (probe::panelUp) {
        if (chgame.justPressed(A_BUTTON)) command("PROFILE");
        else if (chgame.justPressed(B_BUTTON)) command("INIT");
        for (uint8_t b = UP_BUTTON; b <= RIGHT_BUTTON; b <<= 1)
            if (chgame.justPressed(b)) ui::button(b);
    }
    pal::tick();
    audio::update();
    draw(false);
}
