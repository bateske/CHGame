"""CHBoardwalk: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_rules": dict(sources=["tools/tests/test_rules.cpp", "src/game/Game.cpp?", "src/game/Board.cpp?",
                                     "src/game/Cpu.cpp?"], includes=["lib"])}
QUICK_ARGS = ["quick"]
SKIP_SCRIPTS = ("device_", "pace")        # pace.txt: frame pacing on the board (the debug build)
