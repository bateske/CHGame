// The game's sound effects, for the CHGame library's piezo sequencer
// (chgame/Audio.h): short step lists kept inside the piezo's 1-4 kHz sweet
// spot. There is no music - the fanfares are effects too. Tick and Tock,
// the auction's clock, are played soft; bids climbing and counters rolling
// are audio::blip() notes made up on the spot.
#pragma once
#include <chgame/Audio.h>         // the CHGame library's sound engine

enum class Sfx : uint8_t {
    Cursor, Select, Deny, Dice, Land, Hop, Coin, Pay, Buy, Gavel, Flip, Jail, Build, Doubles,
    Whoosh, Win, Lose, Turn, Title,
    Tick, Tock,                      // soft: quieter than the rest
    COUNT
};

// The effects, in Sfx order: audio::begin(SOUNDS, (uint8_t)Sfx::COUNT).
extern const audio::Effect SOUNDS[(int)Sfx::COUNT];
