/* SPDX-License-Identifier: GPL-3.0-or-later
 * The watch's beeps, CHSDtoUSB's voices: soft ticks for files, clear chirps
 * for the card and the website.
 */
#pragma once
#include <CHGame.h>

enum class Sfx : uint8_t {
    FileNew, FileDone, FileTouch, FileGone, CardIn, Connect, Stop, Sync, Big, Fail, Menu, Page, Done, Jam, COUNT
};

void soundsBegin();
