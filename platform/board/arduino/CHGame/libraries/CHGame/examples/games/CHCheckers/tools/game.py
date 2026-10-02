"""CHCheckers: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_checkers": dict(sources=["tools/tests/test_checkers.cpp", "src/game/Match.cpp?"], args="none")}
QUICK_ARGS = []
ECHO = ("THINK", "RPROF")
