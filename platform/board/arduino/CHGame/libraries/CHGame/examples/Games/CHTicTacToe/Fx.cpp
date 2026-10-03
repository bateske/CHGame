// Builds the CHGame library's chgame/Sizzle (particles, banners, floating
// texts) under this file's size pragma, with the switches in Fx.h.
#pragma GCC optimize("Os")   // cold code: size over speed (hot pixel loops live in the CHGame library and CHGfx)
#include "Fx.h"
#include <chgame/Sizzle.inl>
