"""CHSolitaire: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_klondike": dict(sources=["tools/tests/test_*.cpp", "src/game/*.cpp"])}
QUICK_ARGS = []
ONCE_SCRIPTS = {"perf"}         # its host timings vary from run to run
