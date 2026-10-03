/*
 * The menu's files on the SD card: the layout the bootloader's menu reads and
 * the tools write (spec/card.md is the reference; tools/chcart/runtime.py
 * writes it). Everything lives under GAMES/, and every folder in that tree
 * may hold, beside its games (*.CHG, spec/chg.md) and subfolders:
 *
 *   MENU.IDX   the order of the folder's entries, folder titles, the launch
 *              flag: 32-byte records. Record 0 is the header (the magic
 *              "CHX1", the rest 0); record k >= 1 names one entry:
 *                0  char[11]  the entry's 8.3 name as stored in the directory
 *                             ("BLACKJCKCHG", "CARDS      ")
 *               11  u8        flags (CARD_IDX_LAUNCH)
 *               12  char[20]  a folder's title, NUL-padded (0 for a game)
 *              Indexed entries come first, in record order; the rest follow,
 *              sorted by title. Records naming no entry are skipped.
 *   MENU.BG    the background, inherited by subfolders without their own:
 *              a 512-byte header (the magic "CHB1", then at offset 8 the
 *              palette: 16 RGB565 colours, little-endian, the rest 0), then
 *              128 rows of 64 bytes, two pixels a byte, the left one in the
 *              high nibble. Exactly CARD_BG_BYTES, or it is ignored.
 *              Colours 11-14 are the menu's own (CARD_C_*). Colour 15 is
 *              the picture's #FF00FF in the palette: the rainbow bootloader
 *              draws it as one colour turning through the colour wheel
 *              instead, the static one as it is.
 *
 * Integers are little-endian, as everywhere on the card.
 */
#ifndef CHGAME_CARD_H
#define CHGAME_CARD_H

#define CARD_IDX_MAGIC      0x31584843u   /* "CHX1" */
#define CARD_IDX_RECORD     32u
#define CARD_IDX_OFF_FLAGS  11u
#define CARD_IDX_OFF_TITLE  12u
#define CARD_IDX_LAUNCH     0x01u         /* start this entry at power-on (a folder: look inside) */

#define CARD_BG_MAGIC       0x31424843u   /* "CHB1" */
#define CARD_BG_OFF_PALETTE 8u
#define CARD_BG_HEADER      512u
#define CARD_BG_BYTES       (512u + 128u * 64u)

/* The menu's colours in the palette */
#define CARD_C_TEXT         11u           /* titles */
#define CARD_C_DIM          12u           /* a file that is not a game */
#define CARD_C_INK          13u           /* the selected title; the inside of boxes */
#define CARD_C_MARK         14u           /* the installed game's chip */
#define CARD_C_RAINBOW      15u           /* the selection bar, boxes; the rainbow (or as painted) */

#endif
