// SdSpi - a read-only SPI-mode microSD block driver (CHSd, MIT: see NOTICE).
//
// HypeRunner's clean-room driver cut down to what reading a game's data
// file needs: identify the card, read one 512-byte block. No writing, no
// CRC (the games' files check their own blocks or records), and DMA only in
// stream(), for a sketch that reads whole files every frame.
//
// BUS RULE: SPI1 is shared with the LCD. Call these only after gfx_wait(),
// before the next flush. SPI1 is handed back exactly as CHGfx left it.
//
// After a read fails, call init() before reading again: a block whose token
// came late may still be on its way, and init()'s CMD0 is what clears it.
#pragma once
#include <stdint.h>

namespace sd {

bool init();                                // false: no card, or not one this can read
bool read(uint32_t lba, uint8_t *dst);      // one block; false: the card did not deliver

// Streaming, for a sketch that reads a file over and over (CHStlView reads
// a whole model every frame): n blocks from lba in one multi-block read
// (CMD18) at 24 MHz, each block landing by DMA in buf0 / buf1 in turn while
// fn(block, ctx) works on the one before. fn must keep off SPI1 and the two
// buffers' other half; it gets each block once, in order. Costs about 0.6 ms
// of card latency per call plus 0.17 ms per block, against ~1.5 ms per block
// for read(). No CRC is checked (a block garbled on the wire reaches fn as
// it came). DMA1 channels 2 and 3 are borrowed and left off: CHGfx sets
// channel 3 up afresh for every flush. False: the card stopped delivering
// (init() before the next read, as above). The games never call it, so it
// is not in their images.
typedef void (*BlockFn)(const uint8_t *block, void *ctx);
bool stream(uint32_t lba, uint32_t n, uint8_t *buf0, uint8_t *buf1, BlockFn fn, void *ctx);

}  // namespace sd
