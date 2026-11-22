// Every coordinate of the 128x128 play screen in one place.
//
// The wall and the rail are CHBlackjack's; the felt below them holds the
// card in play in the middle, as a carousel (the others slide past on a
// swipe), with the power meter on its left and the jackpot on its right:
//
//   0..41   back wall: the caller, the PURSE/POT plaque (his speech bubble
//           covers it while he talks), the board of the last balls
//  42..45   wooden rail with the chip rack
//  46..111  the felt: power | the card in play | jackpot (or the buy-in)
// 112..127  the bar: a little copy of every card, centred
#pragma once
#include <stdint.h>

namespace lay {

constexpr int WALL_H = 42;
constexpr int DEALER_X = 2, DEALER_Y = 0;          // even x: fast blits
constexpr int FACE_X = DEALER_X + 12, FACE_Y = DEALER_Y + 14;   // expression patch

constexpr int PLAQUE_X = 52, PLAQUE_Y = 3, PLAQUE_W = 48, PLAQUE_H = 34;
constexpr int BUBBLE_X = 50, BUBBLE_Y = 2, BUBBLE_W = 51, BUBBLE_H = 35;   // over the plaque
constexpr int TOTE_X = 103, TOTE_Y = 3, TOTE_W = 23, TOTE_H = 37;

constexpr int RAIL_Y = 42, RAIL_H = 4;
constexpr int TRAY_X = 54, TRAY_W = 44;                        // the chip rack

constexpr int TABLE_Y = 46;

// A card: a 2 px frame, the B-I-N-G-O header, five rows of five cells.
constexpr int CELL_W = 14, CELL_H = 10, HEAD_H = 8;
constexpr int CARD_W = 5 * CELL_W + 4, CARD_H = HEAD_H + 5 * CELL_H + 4;   // 74 x 62
constexpr int CARD_X = 26, CARD_Y = 48;                        // the card in play
constexpr int CARD_PITCH = 104;                                // its neighbours wait off the screen

// Either side of it: the power meter (left) and the jackpot (right).
constexpr int SIDE_LX = CARD_X / 2;                            // their centres
constexpr int SIDE_RX = (CARD_X + CARD_W + 3 + 128) / 2;
constexpr int SIDE_Y = 51;                                     // their labels
constexpr int TUBE_X = SIDE_LX - 5, TUBE_Y = 61, TUBE_W = 10, TUBE_H = 37;   // the power meter: 12 segments, in caps

constexpr int BUY_Y = TABLE_Y + 20;                           // the buy-in's row of cards
constexpr int MODE_X = 18, MODE_Y = 49, MODE_W = 92, MODE_PITCH = 16;   // the mode picker's rows

constexpr int BAR_Y = 112, BAR_H = 16;
// The bar's little cards: a 1 px frame, a 2 px header, 5x5 cells of 3x2
// (2x2 for eight or nine cards); the one in play stands 2 px higher, and
// the glove rests over it.
constexpr int MINI_H = 14, MINI_GAP = 1, MINI_Y = BAR_Y + 2;
constexpr int BANNER_Y = 78;
constexpr int STRIP_Y = BANNER_Y - 18, STRIP_H = 35;            // the black band a banner stands on

}  // namespace lay
