#include "Sounds.h"

static const audio::Step CURSOR[]    = { AUDIO_STEP(2100, 0, 10) };
static const audio::Step SELECT[]    = { AUDIO_STEP(1700, 0, 18), AUDIO_STEP(2600, 0, 30) };
static const audio::Step DENY[]      = { AUDIO_STEP(900, 650, 70) };
static const audio::Step CHIP[]      = { AUDIO_STEP(3100, 0, 12), AUDIO_REST(9), AUDIO_STEP(3700, 0, 26) };
static const audio::Step COIN[]      = { AUDIO_STEP(2800, 0, 10), AUDIO_STEP(3700, 0, 28) };
static const audio::Step WHOOSH[]    = { AUDIO_STEP(1200, 3800, 90) };
static const audio::Step WIN[]       = { AUDIO_STEP(2093, 0, 60), AUDIO_STEP(2637, 0, 60), AUDIO_STEP(3136, 0, 60), AUDIO_STEP(4186, 0, 170) };
static const audio::Step BIGWIN[]    = {
    AUDIO_STEP(1568, 0, 50), AUDIO_STEP(2093, 0, 50), AUDIO_STEP(2637, 0, 50), AUDIO_STEP(3136, 0, 90),
    AUDIO_STEP(2093, 0, 40), AUDIO_STEP(2637, 0, 40), AUDIO_STEP(2093, 0, 40), AUDIO_STEP(2637, 0, 40),
    AUDIO_STEP(3136, 0, 40), AUDIO_STEP(4186, 0, 40), AUDIO_STEP(3136, 0, 40), AUDIO_STEP(4186, 0, 40),
    AUDIO_STEP(2000, 4200, 220) };
static const audio::Step LOSE[]      = { AUDIO_STEP(1300, 950, 140), AUDIO_STEP(950, 700, 220) };
static const audio::Step BROKE[]     = { AUDIO_STEP(1568, 1480, 300), AUDIO_STEP(1480, 1397, 300), AUDIO_STEP(1397, 1319, 300), AUDIO_STEP(1319, 1249, 400), AUDIO_STEP(1249, 1180, 400) };
static const audio::Step PLACE[]     = { AUDIO_STEP(1300, 700, 26), AUDIO_REST(18), AUDIO_STEP(2800, 0, 6) };   // a mark lands
static const audio::Step POOF[]      = { AUDIO_STEP(2600, 1100, 70) };                  // a mark vanishes
static const audio::Step TIC[]       = { AUDIO_STEP(1568, 0, 45) };                     // one, two, three in a line
static const audio::Step TAC[]       = { AUDIO_STEP(2093, 0, 45) };
static const audio::Step MEOW[]      = { AUDIO_STEP(1500, 2300, 110), AUDIO_STEP(2300, 1250, 260) };   // a cat's game
static const audio::Step TITLE[]     = {                                       // the title's sting
    AUDIO_STEP(1047, 0, 90), AUDIO_STEP(1319, 0, 90), AUDIO_STEP(1568, 0, 90), AUDIO_STEP(2093, 0, 150), AUDIO_REST(60),
    AUDIO_STEP(1568, 0, 80), AUDIO_STEP(2093, 0, 260) };
static const audio::Step BOOM[]      = { AUDIO_STEP(1400, 500, 60), AUDIO_STEP(900, 400, 50), AUDIO_STEP(700, 350, 160) };   // a mine
static const audio::Step TICK[]      = { AUDIO_STEP(1100, 0, 3) };
static const audio::Step TOCK[]      = { AUDIO_STEP(850, 0, 3) };

const audio::Effect SOUNDS[(int)Sfx::COUNT] = {
    AUDIO_EFFECT(CURSOR, 0), AUDIO_EFFECT(SELECT, 1), AUDIO_EFFECT(DENY, 1), AUDIO_EFFECT(CHIP, 1),
    AUDIO_EFFECT(COIN, 1), AUDIO_EFFECT(WHOOSH, 1), AUDIO_EFFECT(WIN, 3), AUDIO_EFFECT(BIGWIN, 4),
    AUDIO_EFFECT(LOSE, 3), AUDIO_EFFECT(BROKE, 4), AUDIO_EFFECT(PLACE, 1), AUDIO_EFFECT(POOF, 2),
    AUDIO_EFFECT(TIC, 2), AUDIO_EFFECT(TAC, 2), AUDIO_EFFECT(MEOW, 3), AUDIO_EFFECT(TITLE, 2),
    AUDIO_EFFECT(BOOM, 3), AUDIO_EFFECT(TICK, audio::SOFT), AUDIO_EFFECT(TOCK, audio::SOFT),
};
