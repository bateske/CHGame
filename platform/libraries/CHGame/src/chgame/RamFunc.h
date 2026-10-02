// CHGAME_RAMFUNC(name): run a function from SRAM. Flash has 3 wait states
// and no cache: from flash a per-pixel loop costs ~3 us a pixel on this
// part; from SRAM about a third of that. Every RAMFUNC costs its size in RAM.
//
// The section name is CHGfx 1.3's trick: the core's link script puts
// *(.gnu.linkonce.r.*) first in .data (copied to SRAM at boot), ahead of
// .sdata/.sbss. linkonce merges sections of the same name, so every
// function needs a name of its own (which also lets the linker drop unused
// ones one at a time). The library's are "chg.<name>"; CHGfx's are
// "chgfx.<name>". A sketch's own CHGAME_APP_RAMFUNC(name) uses
// "app.<name>", so a game's `save` can never merge with the library's.
#pragma once

#if defined(__riscv) && !defined(CHSIM)
#define CHGAME_RAMFUNC(name) __attribute__((section(".gnu.linkonce.r.chg." #name), noinline))
#define CHGAME_APP_RAMFUNC(name) __attribute__((section(".gnu.linkonce.r.app." #name), noinline))
#else
#define CHGAME_RAMFUNC(name) __attribute__((noinline))     // the simulator, host tests and tools
#define CHGAME_APP_RAMFUNC(name) __attribute__((noinline))
#endif
