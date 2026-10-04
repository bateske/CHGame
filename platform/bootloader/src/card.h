#ifndef CHBOOT_CARD_H
#define CHBOOT_CARD_H
#include <stdint.h>
#include "menu.h"
#include "lcd.h"

/* The card as both menus see it (spec/card.md): GAMES/ found, one folder
 * listed at a time (its *.CHG files and folders, in MENU.IDX's order, then by
 * title), the installed game marked; and the keys. menu.c shows the folder as
 * the text list, visual.c as pictures (build.sh --ui=). */

#define TITLE_COLS  19          /* x 8..121; a folder's '>' at 122 */
#define DEPTH       4           /* folders below GAMES/ */

#define G_INSTALLED 0x01        /* (draw_row tests it) */
#define G_BAD       0x02        /* err holds the reason */
#define G_DIR       0x04
#define G_LAUNCH    0x08

typedef struct {
    uint32_t clus, size;
    uint8_t  flags, err, key;           /* key: the MENU.IDX record, 255 = none */
    uint8_t  pic;                       /* visual: the sector its picture starts at in the CHG, 0 = none */
    char     title[TITLE_COLS + 1];     /* space-padded; holds the 11-byte 8.3 name until the scan is done */
} __attribute__((aligned(4))) game_t;

typedef struct { uint32_t clus, size; } file_t;

extern game_t games[MENU_MAX_GAMES];
extern uint32_t ngames, sel, depth, lit;
extern uint32_t here;                   /* the folder shown: its first cluster */
extern uint8_t buf[512];
extern const uint16_t pal0[16];
#if MENU_UI == MENU_UI_LIST
extern uint32_t top;
extern file_t bg;                       /* the MENU.BG in force */
#else
extern file_t sys;                      /* GAMES/SYSTEM.PIC (0: none) */
extern uint32_t stray;                  /* the program in flash is on no card entry: GAMES/ lists it first */
#endif

static inline uint32_t w32(const uint8_t *p) { return *(const uint32_t *)(const void *)p; }

/* An 8.3 directory name (11 bytes, space-padded) against b. */
int same(const uint8_t *a, const char *b);

/* fat_dir() callback: finds GAMES/ in the root and sets here. */
int find_games(const uint8_t *d, void *ctx);

/* Lists the folder `here` and reads the games' headers. Returns the number of
   entries (at the top, with the program in flash first when the list does
   not hold it, or, visual, when the card does not: `stray`). Picks the
   installed game, else the first (sel). */
uint32_t scan(int app);

void flush(uint32_t y0, uint32_t y1);   /* (nothing before the panel is lit) */
void light(void);                       /* the panel on, showing the framebuffer */

uint32_t keys(void);                    /* newly pressed keys, debounced, repeating */
void release(void);                     /* waits for every key to be up */
void wait_key(void);                    /* waits for A, B or START */

#endif
