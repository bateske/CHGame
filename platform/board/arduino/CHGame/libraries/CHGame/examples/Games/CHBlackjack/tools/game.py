"""CHBlackjack: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_rules": dict(sources=["tools/tests/test_rules.cpp", "src/game/Round.cpp"], opt="-O1", defines=[],
                            includes=["lib"], args="none")}
QUICK_ARGS = []
SKIP_SCRIPTS = ("device_", "prof", "perf_free")    # prof*.txt, perf_free.txt: a CHGAME_PROFILE build on the board
