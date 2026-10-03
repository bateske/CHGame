// The simulator's PC: the sketch's UsbMsc API (UsbMsc.cpp is compiled out
// under CHSIM), driven by a pretend Windows PC instead of the USBFS
// peripheral. It plays a session tools/chsim/pcsession.py wrote ($CHSD_PC:
// trace.txt, blob.bin, card.bin) in virtual time:
//
//   card BLOCKS        the card in the slot (the first line)
//   usb                the PC enumerates the reader
//   R LBA N / W LBA N @OFF / W LBA N ~
//                      READ (10) / WRITE (10) with data from blob.bin / file data
//   wait MS            the PC does nothing for a while
//   eject              the PC ejects the medium
//   pull / insert      the card comes out / goes back in
//   fault LBA          the next read of LBA fails its CRC once
//   press BUTTON MS    a button held (the debug protocol's injected buttons)
//   snap NAME          a marker: the PC stops here until G (the scripts'
//                      `pcto NAME` runs frames to it, then snaps)
//   rec / stop / note  ignored (the scripts record)
//
// Time: on the board the loop spins on USB between frames, so a frame
// lasts its whole period (40 ms at 25 fps) and the PC works through it.
// poll() plays the PC for one frame period each time a new frame begins.
// A block read takes ~1.0 ms (full-speed USB), a block written ~1.25 ms
// plus ~0.9 ms for the card to start programming, with a little jitter; a
// command waits for a panel flush in flight (card_host.cpp), so the screen
// shows up in the throughput as it would on the board.
#include <Arduino.h>
#include <CHGame.h>
#include <string>
#include <vector>
#include "sim.h"
#include "PcSim.h"
#include "UsbMsc.h"

static std::vector<std::string> s_lines;
static std::vector<uint8_t> s_blob;
static size_t s_pos = 0;
static bool s_loaded = false, s_paused = false, s_inPlay = false;
static std::string s_marker = "-";
static uint32_t s_due = 0, s_frame = 0xFFFFFFFFu, s_frameEnd = 0;
static uint8_t s_btn = 0;
static uint32_t s_btnUntil = 0;
static const uint32_t FRAME_US = 40000;

static uint32_t s_rng = 1;
static uint32_t rng() { s_rng ^= s_rng << 13; s_rng ^= s_rng >> 17; s_rng ^= s_rng << 5; return s_rng; }
static uint32_t jitter(uint32_t us) { return us - us / 20 + rng() % (us / 10 + 1); }

void sim_pc_load() {
    if (s_loaded) return;
    s_loaded = true;
    const char *dir = getenv("CHSD_PC");
    if (!dir || !*dir) return;
    std::string d = dir;
    if (FILE *f = fopen((d + "/blob.bin").c_str(), "rb")) {
        fseek(f, 0, SEEK_END);
        s_blob.resize((size_t)ftell(f));
        fseek(f, 0, SEEK_SET);
        if (fread(s_blob.data(), 1, s_blob.size(), f) != s_blob.size()) s_blob.clear();
        fclose(f);
    }
    FILE *t = fopen((d + "/trace.txt").c_str(), "r");
    if (!t) { fprintf(stderr, "chsim: no trace in %s\n", dir); return; }
    char line[256];
    while (fgets(line, sizeof line, t)) s_lines.push_back(line);
    fclose(t);
    unsigned blocks = 0;
    if (!s_lines.empty() && sscanf(s_lines[0].c_str(), "card %u", &blocks) == 1) {
        card_load((d + "/card.bin").c_str(), blocks);
        s_pos = 1;
    }
}

void sim_pc_resume() { s_paused = false; }

char *sim_pc_status(char *p) {
    p = fmtInt(fmtStr(p, "pc="), (int32_t)s_pos);
    p = fmtInt(fmtStr(p, "/"), (int32_t)s_lines.size());
    p = fmtStr(fmtStr(p, " at="), s_marker.c_str());
    p = fmtInt(fmtStr(p, " paused="), s_paused);
    return fmtInt(fmtStr(p, " done="), s_pos >= s_lines.size());
}

namespace usbmsc {

volatile uint32_t blocksRead = 0, blocksWritten = 0;
static BlockDevice dev;
static State st = OFF;
static bool busyNow = false, ejected = false, ro = false;
alignas(4) static uint8_t sector[512];

static void command(bool write, uint32_t lba, uint32_t n, const uint8_t *data) {
    alignas(4) static uint8_t buf[512];
    busyNow = true;
    st = write ? WRITING : READING;
    sim_advance(150);                                   // CBW in, decoded
    bool ok;
    if (write) {
        ok = dev.writeStart(lba, n);
        sim_advance(jitter(900));                       // the card starts programming
        for (uint32_t i = 0; ok && i < n; i++) {
            if (data) memcpy(buf, data + 512 * i, 512);
            else {                                      // file data: anything but a directory
                uint32_t x = (lba + i) * 2654435761u + 1;
                for (int k = 0; k < 512; k++) { x ^= x << 13; x ^= x >> 17; x ^= x << 5; buf[k] = (uint8_t)x; }
            }
            sim_advance(jitter(1240));
            if (!dev.writeBlock(buf)) ok = false;
            else blocksWritten++;
        }
        dev.writeStop();
    } else {
        ok = dev.readStart(lba);
        sim_advance(jitter(350));                       // access latency
        for (uint32_t i = 0; ok && i < n; i++) {
            if (!dev.readBlock(buf)) ok = false;
            else blocksRead++;
            sim_advance(jitter(1000));
        }
        dev.readStop();
    }
    sim_advance(100);                                   // CSW out
    busyNow = false;
    st = CONFIGURED;
}

static uint8_t buttonOf(const char *b) {
    static const struct { const char *n; uint8_t m; } B[] = {
        {"UP", UP_BUTTON}, {"DOWN", DOWN_BUTTON}, {"LEFT", LEFT_BUTTON}, {"RIGHT", RIGHT_BUTTON},
        {"A", A_BUTTON}, {"B", B_BUTTON}, {"SELECT", SELECT_BUTTON}, {"START", START_BUTTON}};
    for (auto &x : B)
        if (!strcmp(b, x.n)) return x.m;
    return 0;
}

// One line of the session, at its time.
static void step(const char *line) {
    char op[16] = "", arg[200] = "";
    unsigned a = 0, b = 0;
    sscanf(line, "%15s", op);
    uint32_t now = sim_now();
    s_due = now;
    if (!strcmp(op, "usb")) {
        st = CONFIGURED;
        s_due = now + 1000;
    } else if ((op[0] == 'R' || op[0] == 'W') && !op[1]) {
        char at[32] = "";
        sscanf(line, "%*s %u %u %31s", &a, &b, at);
        const uint8_t *data = nullptr;
        if (op[0] == 'W' && at[0] == '@') data = s_blob.data() + strtoul(at + 1, nullptr, 10);
        command(op[0] == 'W', a, b, data);
        s_due = sim_now() + 200;                        // the PC's turnaround
    } else if (!strcmp(op, "wait")) {
        sscanf(line, "%*s %u", &a);
        s_due = now + a * 1000;
    } else if (!strcmp(op, "eject")) {
        ejected = true;
        s_due = now + 1000;
    } else if (!strcmp(op, "pull") || !strcmp(op, "insert")) {
        card_present(op[0] == 'i');
        s_due = now + 1000;
    } else if (!strcmp(op, "fault")) {
        sscanf(line, "%*s %u", &a);
        card_badBlock(a);
    } else if (!strcmp(op, "press")) {
        sscanf(line, "%*s %199s %u", arg, &a);
        s_btn = buttonOf(arg);
        chgame.injected |= s_btn;
        s_btnUntil = now + a * 1000;
        s_due = now + a * 1000 + 100000;
    } else if (!strcmp(op, "snap")) {
        sscanf(line, "%*s %199s", arg);
        s_marker = arg;
        s_paused = true;
        s_due = now + 1000;
    }
}

// The PC's share of a frame: lines due before the frame's period is up.
static void play() {
    if (s_inPlay) return;                               // (a command's own calls into the sketch)
    s_inPlay = true;
    if (chgame.frameCount != s_frame) {
        s_frame = chgame.frameCount;
        s_frameEnd = sim_now() + FRAME_US;
        while (true) {
            uint32_t now = sim_now();
            if (s_btn && (int32_t)(now - s_btnUntil) >= 0) { chgame.injected &= (uint8_t)~s_btn; s_btn = 0; }
            if ((int32_t)(now - s_frameEnd) >= 0) break;
            bool idle = s_paused || s_pos >= s_lines.size();
            uint32_t next = idle ? s_frameEnd : s_due;
            if ((int32_t)(next - s_frameEnd) > 0) next = s_frameEnd;
            if ((int32_t)(next - now) > 0) { sim_advance(next - now); continue; }
            step(s_lines[s_pos++].c_str());
        }
    }
    s_inPlay = false;
}

void begin(const BlockDevice &d) { dev = d; st = WAITING; }
void poll() { play(); }
State state() { return st == CONFIGURED && ejected ? EJECTED : st; }
bool busy() { return busyNow; }
void setReadOnly(bool r) { ro = r; }
bool readOnly() { return ro; }
void mediaChanged() { ejected = false; }
void detach() { st = OFF; }
int cdcRead() { return -1; }
bool cdcWrite(const char *, uint8_t) { return true; }
uint8_t *buffer() { return sector; }

}  // namespace usbmsc
