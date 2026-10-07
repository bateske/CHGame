/* SPDX-License-Identifier: GPL-3.0-or-later
 * See Monitor.h. Requests are read here only after transfer_command() has
 * accepted them (status 0), so every path is a checked, NUL-terminated 8.3
 * path inside the frame.
 */
#include <Arduino.h>
#include <string.h>
#include "Monitor.h"

namespace mon {

Card card;
bool mounted, linked, stopped, transferActive, verifying, failed, done;
uint8_t lastFail, lastFailCmd;
Progress progress;
Column hist[HISTORY];
uint32_t columns;
Stats st;
Event ev[EVENTS];
uint32_t events;
uint8_t said[8], saidCount;

static const uint32_t GAP_MS = 600;            // a pause this long shows as a gap in the graph
static uint32_t sliceStart, sliceBytes, sliceChk, cmdT0;   // the slice: when it opened, its link bytes, its card-check bytes
static uint8_t sliceFlags, sliceMark;
static bool sliceOpen, toldRecovered;
static uint32_t livePut, liveGet, liveChk, liveList;   // the events still growing (`events` after their push)
static uint16_t putsSinceSync;

// A failure's line names what failed: a command, or (0) the card itself at the start.
static const char *const OPS[] = {"CARD", "HELLO", "STAT", "LIST", "MKDIR", "BEGIN", "WRITE", "COMMIT",
                                  "ABORT", "SYNC", "MENU", "CHECK", "READ", "CAPS", "REMOVE", "PROGRESS"};

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static const char *base(const uint8_t *path) {
    const char *s = strrchr((const char *)path, '/');
    return s ? s + 1 : (const char *)path;
}

uint32_t usedPermille() {
    uint32_t all = card.sectors, used = all - card.freeSectors;
    if (!card.known || !all || card.freeSectors > all) return 0;
    while (used > 0xFFFFFFFFu / 1000) { used >>= 1; all >>= 1; }
    return used * 1000 / all;
}

// ---- The graph's slices ---------------------------------------------------------
static void column(uint16_t kbs, uint8_t flags, uint8_t mark) {
    Column &c = hist[columns++ % HISTORY];
    c.kbs = kbs;
    c.mark = mark;
    c.flags = flags;
}

// A slice that has run its time becomes a column (several, after one long command).
static void roll(uint32_t now) {
    if (!sliceOpen) return;
    uint32_t ms = now - sliceStart;
    if (ms < SLICE_MS) return;
    uint32_t bytes = sliceBytes, flags = sliceFlags;
    if (!bytes && sliceChk) { bytes = sliceChk; flags |= C_VERIFY; }   // nothing on the link: the card reading itself
    uint32_t kbs = (bytes * 1000 / ms) >> 10;
    if (bytes && !kbs) kbs = 1;
    if (kbs > 4095) kbs = 4095;
    if (!(flags & C_VERIFY)) {
        if ((flags & K_PUT) && kbs > st.peakIn) st.peakIn = (uint16_t)kbs;
        else if ((flags & K_GET) && kbs > st.peakOut) st.peakOut = (uint16_t)kbs;
    }
    uint32_t n = ms / SLICE_MS;
    if (n > 8) n = 8;
    for (uint32_t i = 0; i < n; i++) column((uint16_t)kbs, (uint8_t)flags, i ? 0 : sliceMark);
    sliceOpen = false;
}

static void touch(uint32_t now, uint8_t flags, uint32_t bytes, uint32_t chk = 0) {
    roll(now);
    if (!sliceOpen) {
        if (columns && now - st.lastMs > GAP_MS) column(0, 0, 0);
        sliceOpen = true;
        sliceStart = now;
        sliceBytes = sliceChk = 0;
        sliceFlags = sliceMark = 0;
    }
    sliceBytes += bytes;
    sliceChk += chk;
    sliceFlags |= flags;
    st.lastMs = now;
    if (flags & (K_PUT | K_GET | K_CHECK | K_META)) st.lastKind = flags & (K_PUT | K_GET | K_CHECK | K_META);
}

void tick(uint32_t now) { roll(now); }

// ---- Events -----------------------------------------------------------------------
static void say(uint8_t what) {
    if (saidCount < sizeof said) said[saidCount++] = what;
}

// (After touch(): the slice the event marks is open.)
static Event *push(uint32_t now, uint8_t type, const char *name, uint32_t value) {
    Event *e = &ev[events++ % EVENTS];
    e->type = type;
    e->live = 0;
    e->value = value;
    e->done = 0;
    e->t = now;
    strncpy(e->name, name, sizeof e->name - 1);
    e->name[sizeof e->name - 1] = 0;
    if (!sliceMark || type == EV_FAIL || type == EV_STOP) sliceMark = type;
    say(type);
    return e;
}

static Event *live(uint32_t seq) {
    Event *e = seq && events - seq < (uint32_t)EVENTS ? &ev[(seq - 1) % EVENTS] : nullptr;
    return e && e->live ? e : nullptr;
}

const Event *newest(int back) {
    uint32_t shown = events < (uint32_t)EVENTS ? events : EVENTS;
    return (uint32_t)back < shown ? &ev[(events - 1 - back) % EVENTS] : nullptr;
}

const Event *liveFile() { return live(livePut); }

static void fail(uint32_t now, uint8_t cmd, uint8_t status, Event *e) {
    failed = true;
    st.fails++;
    lastFail = status;
    lastFailCmd = cmd;
    if (e) {                                             // the file's own line says so
        e->type = EV_FAIL;
        e->live = 0;
        e->value = status;
        e->t = now;
        sliceMark = EV_FAIL;
        say(EV_FAIL);
    } else {
        push(now, EV_FAIL, cmd < sizeof OPS / sizeof OPS[0] ? OPS[cmd] : "REQUEST", status);
    }
    touch(now, C_FAIL, 0);
}

// ---- Hooks ------------------------------------------------------------------------
void cardState(uint32_t now, uint8_t error) {
    mounted = true;
    card.error = error;
    touch(now, K_META, 0);
    if (error) fail(now, 0, error, nullptr);
    else push(now, EV_CARD, "CARD READY", 0);
}

void command(uint8_t cmd, uint16_t length) {
    cmdT0 = micros();
    if (cmd == 7 && !length) {                           // COMMIT: read back, journal, publish
        verifying = true;
        if (Event *e = live(livePut)) e->live = 2;
    }
}

void polled(uint32_t now) {
    uint32_t chk = verifying || !mounted ? 512 : 0;      // (CHECK counts its own, from its answer)
    st.bytesChk += chk;
    touch(now, K_CHECK, 0, chk);
}

void link(uint32_t now, uint8_t what, uint8_t cmd) {
    if (what == 3) { st.drops++; return; }
    if (what == 4) { touch(now, K_META, 0); return; }     // IDENTITY: the website looking before it leaps
    if (what == 1) {
        st.dups++;
        if (cmd == 1) stopped = false;                   // a replayed HELLO lifts the cancel too
    }
    touch(now, C_RETRY, 0);
}

// B before any website has called stops nothing worth telling: the search
// goes on (the sketch's cancel state is lifted by the HELLO that comes).
void cancelled(uint32_t now, uint8_t action, uint8_t error) {
    touch(now, K_META, 0);
    bool fresh = linked && !stopped;                     // a session to stop
    verifying = false;
    if (Event *e = live(livePut)) { e->type = EV_ABORT; e->live = 0; e->t = now; }
    livePut = 0;
    if (linked) stopped = true;
    if (error) { fail(now, 8, error, nullptr); return; }
    transferActive = false;
    if (action & 2) push(now, EV_STOP, "EXIT TO MENU", 0);
    else if (fresh) push(now, EV_STOP, "STOPPED: B", 0);
}

void result(uint32_t now, uint8_t cmd, const uint8_t *d, uint16_t length, uint8_t status,
            const uint8_t *out, uint16_t size) {
    st.busyUs += micros() - cmdT0;
    st.cmds++;
    verifying = false;
    if (cmd != 9 && cmd != 10 && cmd != 13 && cmd != 15) done = false;   // (more work, or a new job)
    touch(now, 0, 0);
    if (status) {
        if (card.error) return;                          // no card: every answer says so, and so does the screen
        // "Not on the card" answers the website's question: it is not a failure.
        if ((cmd == 2 || cmd == 11) && (status == 4 || status == 5)) { touch(now, K_META, 0); return; }
        Event *e = cmd == 7 ? live(livePut) : nullptr;
        if (e) livePut = 0;
        fail(now, cmd, status, e);
        return;
    }
    failed = false;
    uint8_t kind = K_META;
    uint32_t bytes = 0;
    Event *e;
    switch (cmd) {
        case 1:                                          // HELLO: protocol, recovered, capacity, free, limits
            card.known = true;
            if (!st.filesIn) card.recovered = out[1] != 0;   // (after a COMMIT the flag only says the journal ran)
            card.sectors = get32(out + 2);
            card.freeSectors = get32(out + 6);
            progress = {0, 0, 0, P_COMPLETE, false};     // a new job; the website will measure it afresh
            st.jobT0 = now;
            st.jobBytes = 0;
            st.jobFiles = st.jobRemoved = 0;
            if (!linked || stopped) {
                linked = true;
                stopped = false;
                push(now, EV_LINK, "WEBSITE", out[0]);
                if (out[1] && !toldRecovered && !st.filesIn) {
                    toldRecovered = true;
                    push(now, EV_RECOVER, "RECOVERED", 0);
                }
            }
            break;
        case 3: {                                        // LIST: index, directory; an empty answer ends it
            uint32_t index = get32(d);
            if (!index) {
                push(now, EV_LIST, length > 5 ? base(d + 4) : "CARD ROOT", 0)->live = 1;
                liveList = events;
            }
            if ((e = live(liveList))) {
                if (size) e->value = index + 1;
                else { e->live = 0; e->t = now; }
            }
            break;
        }
        case 4:
            st.dirs++;
            push(now, EV_DIR, base(d), 0);
            break;
        case 5:                                          // BEGIN: size, CRC, path
            transferActive = true;
            kind = K_PUT;
            push(now, EV_PUT, base(d + 8), get32(d))->live = 1;
            livePut = events;
            break;
        case 6:                                          // WRITE: offset, data
            kind = K_PUT;
            bytes = (uint32_t)length - 4;
            st.bytesIn += bytes;
            if ((e = live(livePut))) e->done += bytes;
            break;
        case 7:                                          // COMMIT
            kind = K_CHECK;
            st.filesIn++;
            st.jobFiles++;
            putsSinceSync++;
            if ((e = live(livePut))) {
                uint32_t s = (e->value + 511) >> 9;
                card.freeSectors = card.freeSectors > s ? card.freeSectors - s : 0;
                st.jobBytes += e->value;
                e->live = 0;
                e->done = e->value;
                e->t = now;
            }
            livePut = 0;
            say(EV_DONE);
            break;
        case 8:                                          // ABORT: the staged file is dropped
            transferActive = false;
            if ((e = live(livePut))) { e->type = EV_ABORT; e->live = 0; e->t = now; say(EV_ABORT); }
            livePut = 0;
            break;
        case 9:                                          // SYNC: the website's last word on a job
            transferActive = false;
            push(now, EV_SYNC, "CARD SYNCED", putsSinceSync);
            putsSinceSync = 0;
            done = st.jobFiles || st.jobRemoved;
            break;
        case 10:
            push(now, EV_MENU, "TO THE MENU", 0);
            break;
        case 14:                                         // REMOVE: a game's file, under GAMES
            st.removed++;
            st.jobRemoved++;
            push(now, EV_DEL, base(d), 0);
            break;
        case 15:                                         // PROGRESS: the website's own measure of the job
            progress = {get32(d), get32(d + 4), get32(d + 8), d[12], true};
            transferActive = progress.done < progress.total;
            kind = 0;                                    // (display only: neither traffic nor a command to tick)
            break;
        case 11: {                                       // CHECK: offset, CRC, path -> next offset, CRC, EOF
            transferActive = true;
            kind = K_CHECK;
            uint32_t next = get32(out);
            const char *name = base(d + 8);
            st.bytesChk += next - get32(d);
            touch(now, K_CHECK, 0, next - get32(d));
            e = live(liveChk);
            if (!e || strcmp(e->name, name)) {
                e = push(now, EV_CHK, name, 0);
                e->live = 1;
                liveChk = events;
            }
            e->done = next;
            if (out[8]) { e->live = 0; e->value = next; e->t = now; }
            break;
        }
        case 12: {                                       // READ: offset, count, path -> offset, CRC, EOF, data
            transferActive = true;
            kind = K_GET;
            bytes = (uint32_t)size - 9;
            st.bytesOut += bytes;
            const char *name = base(d + 6);
            e = live(liveGet);
            if (!e || strcmp(e->name, name)) {
                e = push(now, EV_GET, name, 0);
                e->live = 1;
                liveGet = events;
            }
            e->done = get32(d) + bytes;
            if (out[8]) {
                e->live = 0;
                e->value = e->done;
                e->t = now;
                st.filesOut++;
                st.jobFiles++;
                st.jobBytes += e->done;
                say(EV_GOT);
            }
            break;
        }
    }
    touch(now, kind, bytes);
}

}  // namespace mon
