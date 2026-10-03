// The game's sound effects, for the CHGame library's piezo sequencer
// (chgame/Audio.h): short step lists kept inside the piezo's 1-4 kHz sweet
// spot. There is no music: the fanfares are effects too (flash goes to the
// games). Rolling chip counts are blips made up on the spot (audio::blip).
// Every sweep glides (audio::GLIDE), as the game's own sequencer played them.
#pragma once
#include <chgame/Audio.h>         // the CHGame library's sound engine

enum class Sfx : uint8_t {
    Cursor, Select, Deny, Deal, Flip, Chip, Slide, Knock, Fold, Raise, AllIn,
    Win, BigWin, Lose, Shuffle, Coin, Turn, Bust, Title, Whoosh,
    Tick, Tock,                      // soft: quieter than the rest
    COUNT
};

// The effects, in Sfx order: audio::begin(SOUNDS, (uint8_t)Sfx::COUNT).
extern const audio::Effect SOUNDS[(int)Sfx::COUNT];
