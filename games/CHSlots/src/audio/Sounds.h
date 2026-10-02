// The game's sound effects, its three tunes and the status LED, for the
// CHGame library's piezo sequencer (chgame/Audio.h): every action has a
// voice, a short step list kept inside the piezo's 1-4 kHz sweet spot; the
// reel ticks and the win counting up are blips. Music is one line of notes
// (an audio::Melody) that loops underneath; an effect takes the piezo while
// it plays and the tune carries on in time behind it.
#pragma once
#include <chgame/Audio.h>         // the CHGame library's sound engine

enum class Sfx : uint8_t {
    Cursor, Select, Deny, Chip, Lever, Thunk, Antic, Lock, Coin, Win, BigWin, Jackpot,
    Gong, Roar, Broke, COUNT
};
enum class Song : uint8_t { None, Title, Free, Wheel, COUNT };

// The effects, in Sfx order: audio::begin(SOUNDS, (uint8_t)Sfx::COUNT).
extern const audio::Effect SOUNDS[(int)Sfx::COUNT];

// Plays until another song (or None) is asked for; asking for the song
// already playing does not start it over.
void playSong(Song s, bool loop = true);
// The Options MUSIC toggle: back on, the song starts over.
void setMusicOn(bool on);
