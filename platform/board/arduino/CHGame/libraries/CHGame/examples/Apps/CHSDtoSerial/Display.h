/* SPDX-License-Identifier: GPL-3.0-or-later
 * The console's side of the sketch: buttons, LED, beeps and the screen.
 * Every call only watches; none changes what the serial port answers.
 */
#pragma once
#include <stdint.h>
#ifdef CHWEB_HOST
inline uint8_t host_controls; inline uint8_t display_controls(){return host_controls;} inline void display_controls_done(){host_controls=0;} inline void display_begin(){} inline void display_card(uint8_t){} inline void display_command(uint8_t,const uint8_t*,uint16_t){} inline void display_result(uint8_t,const uint8_t*,uint16_t,uint8_t,const uint8_t*,uint16_t){} inline void display_link(uint8_t,uint8_t){} inline void display_cancelled(uint8_t,uint8_t){} inline void display_leaving(){delay(100);}
#else
uint8_t display_controls();            // bit 0: B asked for a cancel; bit 1: START held three seconds
void display_controls_done();
void display_begin();                  // the title screen, before the card mounts
void display_card(uint8_t error);      // transfer_init()'s result
void display_command(uint8_t command,const uint8_t *data,uint16_t length);                 // about to run
void display_result(uint8_t command,const uint8_t *data,uint16_t length,uint8_t error,const uint8_t *out,uint16_t size);
void display_link(uint8_t what,uint8_t command);   // 1 duplicate replayed, 2 refused, 3 frame dropped, 4 identity probe
void display_cancelled(uint8_t action,uint8_t error);   // B (1) or START (2) handled: abort and sync have run
void display_leaving();                // MENU answered: the moment before the reset (at least the 100 ms it always took)
#endif
