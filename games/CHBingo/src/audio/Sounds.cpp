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
static const audio::Step BALL[]      = { AUDIO_STEP(2637, 0, 45), AUDIO_STEP(3520, 0, 90) };                 // a ball is called
static const audio::Step POWER[]     = { AUDIO_STEP(1568, 0, 35), AUDIO_STEP(2093, 0, 35), AUDIO_STEP(2637, 0, 35), AUDIO_STEP(3136, 3900, 110) };
static const audio::Step TICK[]      = { AUDIO_STEP(1100, 0, 3) };
static const audio::Step TOCK[]      = { AUDIO_STEP(850, 0, 3) };

const audio::Effect SOUNDS[(int)Sfx::COUNT] = {
    AUDIO_EFFECT(CURSOR, 0), AUDIO_EFFECT(SELECT, 1), AUDIO_EFFECT(DENY, 1), AUDIO_EFFECT(CHIP, 1),
    AUDIO_EFFECT(COIN, 1), AUDIO_EFFECT(WHOOSH, 1), AUDIO_EFFECT(WIN, 3), AUDIO_EFFECT(BIGWIN, 4),
    AUDIO_EFFECT(LOSE, 3), AUDIO_EFFECT(BROKE, 4), AUDIO_EFFECT(BALL, 1), AUDIO_EFFECT(POWER, 2),
    AUDIO_EFFECT(TICK, audio::SOFT), AUDIO_EFFECT(TOCK, audio::SOFT),
};
