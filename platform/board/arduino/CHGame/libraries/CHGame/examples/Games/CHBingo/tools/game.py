"""CHBingo: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_bingo": dict(sources=["tools/tests/test_bingo.cpp", "src/game/*.cpp"], args="none",
                            reference=dict(module="ref_bingo", func="dump_lines"))}
QUICK_ARGS = []
SIM_TESTS = ["tools/tests/sim_save.py"]
