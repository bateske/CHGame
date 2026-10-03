"""CHChess: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_chess": dict(sources=["tools/tests/test_chess.cpp", "Match.cpp?"], args="none")}
QUICK_ARGS = []
SKIP_SCRIPTS = ("device_", "pace")        # pace.txt: frame pacing on the board (the debug build)
