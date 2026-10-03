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

/* Entries a folder can list (games and folders): each is 32 B of RAM, and
 * 240 fill what the framebuffer, the buffers and the 2 KB stack leave of the
 * 20 KB (SIZES.md). More games go in folders, which have no limit. The tools
 * refuse a cart with a fuller folder (spec/card.md). */
#ifndef MENU_MAX_GAMES
#define MENU_MAX_GAMES 240
#endif

#endif
