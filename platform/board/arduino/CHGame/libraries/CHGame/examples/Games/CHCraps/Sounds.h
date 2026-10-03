// The game's sound effects and the status LED, for the CHGame library's
// piezo sequencer (chgame/Audio.h): every action has a voice, a short step
// list kept inside the piezo's 1-4 kHz sweet spot; the dice rattle and the
// dealer's typewriter are blips. No music: it goes in only if flash is left
// once the game is complete.
#pragma once
#include <chgame/Audio.h>         // the CHGame library's sound engine

enum class Sfx : uint8_t {
    Cursor, Select, Deny, Chip, ChipTake, Throw, Bounce, Wall, Clack, Point, Win, BigWin,
    SevenOut, Craps, Coin, Sweep, Hot, Whoosh, Lose, Broke, COUNT
};

// The effects, in Sfx order: audio::begin(SOUNDS, (uint8_t)Sfx::COUNT).
extern const audio::Effect SOUNDS[(int)Sfx::COUNT];
