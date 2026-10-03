"""CHRoulette: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_rules": dict(sources=["tools/tests/test_rules.cpp", "src/game/*.cpp", "lib/chgame/Ease.cpp",
                                     "src/assets/WheelMap.cpp"], includes=["lib"], args="none",
                            reference=dict(module="ref_roulette", func="lines"))}
QUICK_ARGS = []
EXTRA_TEST_SCRIPTS = ["tools/tests/run_ball_tests.py"]     # the ball's physics (src/wheel/Ball.cpp)
