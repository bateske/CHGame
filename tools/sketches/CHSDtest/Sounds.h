// The bench's beeps: a chirp when a test starts, a rising one when every
// test passed, a low one when any failed.
#pragma once
#include <CHGame.h>

enum class Sfx : uint8_t { Start, Pass, Fail, COUNT };

void soundsBegin();
