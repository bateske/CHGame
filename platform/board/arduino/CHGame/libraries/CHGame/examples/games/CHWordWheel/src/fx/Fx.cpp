#pragma GCC optimize("Os", "no-ipa-sra", "no-inline-functions-called-once", "no-jump-tables", "no-guess-branch-probability")   // cold code: size over speed (hot pixel loops live in the CHGame library and CHGfx)
#include "Fx.h"
#include <chgame/Sizzle.inl>
