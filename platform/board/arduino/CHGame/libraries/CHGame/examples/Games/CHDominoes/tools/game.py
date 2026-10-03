"""CHDominoes: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_dominoes": dict(sources=["tools/tests/test_dominoes.cpp", "Dominoes.cpp", "Ai.cpp",
                                        "Match.cpp", "Layout.cpp"], includes=["lib"])}
