// CHGame: the one include for a CHGame sketch.
//
//     #include <CHGame.h>
//
// brings, on top of CHGfx (the framebuffer, the panel and its DMA):
//
//   chgame/Input.h    CHGame `arduboy`: buttons, frame pacing, START held
//                     3 s goes back to the SD game menu
//   chgame/Palette.h  the house colours (INK, WHITE, FELT ... FX_A, FX_B) and
//                     pal:: (themes, fades, flashes, colour cycling)
//   chgame/Draw.h     rounded panels, span sprites, dithering, the 3x5 font
//   chgame/Mask.h     outlined, shadowed and gradient lettering and logos
//   chgame/Fx.h       fx:: easing, integer sine, randomness, screen shake
//   chgame/Fmt.h      number formatting without printf
//   chgame/RamFunc.h  CHGAME_RAMFUNC: code that runs from SRAM
//
// The casino games in this library's examples are built from these.
#pragma once
#include <CHGfx.h>
#include "chgame/Input.h"
#include "chgame/RamFunc.h"
#include "chgame/Palette.h"
#include "chgame/Draw.h"
#include "chgame/Mask.h"
#include "chgame/Fx.h"
#include "chgame/Fmt.h"
