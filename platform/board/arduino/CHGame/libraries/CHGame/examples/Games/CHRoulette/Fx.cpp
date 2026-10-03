#pragma GCC optimize("Os")   // cold code: size over speed (hot pixel loops live in the CHGame library and CHGfx)
// The library's chgame/Sizzle, compiled here under this game's switches
// (Fx.h) and size pragma.
#include "Fx.h"
#include <chgame/Sizzle.inl>
