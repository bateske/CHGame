// The game's sounds, for the CHGame library's piezo sequencer
// (chgame/Audio.h): effects are short step lists kept inside the piezo's
// 1-4 kHz sweet spot (CHBlackjack's, plus the croupier, the ball and the
// rake), and music is Playtune scores (tools/make_music.py writes Music.cpp).
// The soft effects and blips (the ball rolling round the track) play on a
// narrow pulse, so they sit under everything else.
#pragma once
#include <chgame/Audio.h>         // the CHGame library's sound engine

enum class Sfx : uint8_t {
    Cursor, Select, Deny, Chip, Coin, Whoosh, Win, BigWin, Lose, Broke,
    Flick, Clack, Thunk, Rake,
    Tick, Tock,                      // soft (quieter than the rest): keep them last
    COUNT
};
enum class Song : uint8_t { Title, Victory, Broke };

// The effects, in Sfx order: audio::begin(SOUNDS, (uint8_t)Sfx::COUNT).
extern const audio::Effect SOUNDS[(int)Sfx::COUNT];

// Song s (its score from Music.cpp) as the music: loop = repeat it at its end.
void playSong(Song s, bool loop);
