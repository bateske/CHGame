#pragma GCC optimize("Os", "no-ipa-sra", "no-inline-functions-called-once", "no-jump-tables", "no-guess-branch-probability")   // cold code: size over speed (hot pixel loops live in the CHGame library and CHGfx)
// The library's chgame/Sizzle (particles, banners, floats), compiled here
// under this file's size pragma and Fx.h's switches.
#include "Fx.h"
#include <chgame/Sizzle.inl>
