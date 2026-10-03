"""CHPoker: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""

TESTS = {"test_poker": dict(sources=["tools/tests/test_*.cpp", "Ai.cpp", "Hand.cpp", "Table.cpp", "Variants.cpp"], includes=["lib"])}
QUICK_ARGS = []                 # (`chgame test --long` adds the exhaustive seven-card enumeration)
