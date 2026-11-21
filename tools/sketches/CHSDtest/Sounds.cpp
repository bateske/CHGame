// The effects (chgame/Audio.h: start Hz, end Hz (0: hold), ms).
#include "Sounds.h"

AUDIO_STEPS(S_START) = { AUDIO_STEP(2400, 0, 20) };
AUDIO_STEPS(S_PASS)  = { AUDIO_STEP(2000, 0, 30), AUDIO_REST(10), AUDIO_STEP(2500, 0, 30), AUDIO_REST(10),
                         AUDIO_STEP(3000, 0, 60) };
AUDIO_STEPS(S_FAIL)  = { AUDIO_STEP(320, 0, 110), AUDIO_REST(40), AUDIO_STEP(240, 0, 180) };

static const audio::Effect SOUNDS[] = {
    AUDIO_EFFECT(S_START, 2), AUDIO_EFFECT(S_PASS, 4), AUDIO_EFFECT(S_FAIL, 5),
};

void soundsBegin() { audio::begin(SOUNDS, (uint8_t)Sfx::COUNT); }
