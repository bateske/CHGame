#ifndef CHBOOT_MENU_H
#define CHBOOT_MENU_H
#include <stdint.h>

/* The SD game menu. Returns only to hand over to USB upload mode (a host
 * started an upload, or there is nothing to run); starting a program is a
 * RUN reset. app: appmeta_check() of the installed program. launch: start
 * the card's launch entry, if it names one, instead of showing the list (a
 * power-on without START held). */
void menu_main(int app, int launch);

/* Entered by a USB request (1200-baud touch): USB first, then the panel
 * saying so. */
void menu_usb_notice(void);

/* Install progress (install.c). */
void menu_progress(uint32_t done, uint32_t total);

#ifndef MENU_MAX_GAMES
#define MENU_MAX_GAMES 128
#endif

#endif
