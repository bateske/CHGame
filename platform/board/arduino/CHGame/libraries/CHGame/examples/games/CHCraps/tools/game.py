"""CHCraps: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

# Each test: its source and the game sources it covers (all graphics-free).
TESTS = {
    "test_craps": dict(sources=["tools/tests/test_craps.cpp", "src/game/Craps.cpp"], opt="-O1", args="filter"),
    "test_dice": dict(sources=["tools/tests/test_dice.cpp", "src/cam/Dice3D.cpp"], opt="-O1", args="filter"),
    "test_zones": dict(sources=["tools/tests/test_zones.cpp", "src/render/Zones.cpp", "src/game/Craps.cpp"],
                       opt="-O1", args="filter"),
}
QUICK_ARGS = []
SIM_TESTS = ["tools/tests/sim_save.py"]
