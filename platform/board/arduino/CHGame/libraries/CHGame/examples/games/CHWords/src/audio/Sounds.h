// The game's sound effects, for the CHGame library's piezo sequencer
// (chgame/Audio.h): short step lists kept inside the piezo's 1-4 kHz sweet
// spot. There is no music - the fanfares are effects too. A word lighting
// up plays its notes with audio::note() (src/stage/Stage.cpp).
#pragma once
#include <chgame/Audio.h>         // the CHGame library's sound engine

enum class Sfx : uint8_t {
    Cursor, Select, Deny, Land, Lift, Coin, Rattle, Doubles, Pickup,
    Whoosh, NoMove, Win, Lose, Turn, Title,
    Tick,                            // soft (quieter than the rest)
    COUNT
};

// The effects, in Sfx order: audio::begin(SOUNDS, (uint8_t)Sfx::COUNT).
extern const audio::Effect SOUNDS[(int)Sfx::COUNT];
