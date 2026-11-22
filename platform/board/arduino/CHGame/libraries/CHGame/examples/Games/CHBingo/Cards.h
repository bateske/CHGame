// The felt: bingo cards, the buy-in and the bar under them.
#pragma once
#include <stdint.h>

class Bingo;

namespace cards {

extern const uint8_t LETTER_COL[5];     // B I N G O
constexpr uint8_t DAUBERS = 5;
extern const uint8_t DAUB[DAUBERS];     // the dauber colours: red, blue, green, cyan, peach
uint8_t daub(const Bingo &g);           // the player's
// The glove with its cuff in the dauber's colour.
const uint8_t *cuff(uint8_t colour);

// How a card is lit this frame.
struct Look {
    uint32_t flash;         // cells just daubed (drawn bright)
    uint32_t win;           // the winning line (rainbow)
    int8_t   cursor;        // HARD: the cursor's cell, -1 = not picked up
    bool     focused, deny; // deny: A found nothing to daub
    bool     stamp;         // HARDCORE: VOID across it
};

// Card k with its top left at x, y (it may hang off any side of the felt).
void draw(const Bingo &g, uint8_t k, int x, int y, const Look &look);
// The centre of a cell of the card in play.
void cellXY(uint8_t cell, int &x, int &y);

void buyIn(const Bingo &g);
int  buyX(uint8_t i);                // the left edge of the buy-in's card i
// The bar: every card in little (win: the winning line on card winCard),
// or at the buy-in what A does and the jackpot.
void bar(const Bingo &g, uint32_t win, uint8_t winCard);
int  miniX(const Bingo &g, uint8_t k);   // the left edge of card k's little copy
int  miniW(const Bingo &g);              // its width: 17 px up to seven cards, 12 for more
// Either side of the card in play: the power meter (EASY) or the mode
// (HARD), and the jackpot. frozen: the caller is held (FREEZE).
void sides(const Bingo &g, bool frozen);
// The mode picker at the start of a game.
void modes(const Bingo &g);

}  // namespace cards
