"""CHStlView: what the shared tools need to know (the schema is in
the repository's tools/gamecfg.py; `chgame test`, `chgame check`,
`chgame redraw` read this)."""
import subprocess
import sys

# The renderer's fixed-point pipeline against double precision: every
# sample, and the edge cases (tiny, huge, far out, NaN, flat), over 7 views.
TESTS = {"accuracy": dict(sources=["tools/tests/accuracy.cpp", "StlRender.cpp"],
                          defines=["CHTEST", "STL_TEST_HOOK"], includes=["lib"], run=False)}
# Every script gets the sample card (tools/chsim/chdrive.py makes it too).
CARD = dict(scripts="", file="out/card.img", build=["tools/make_card.py"])
ECHO = ("STATE",)


def after_tests(ctx, exes):
    exe = exes.get("accuracy")
    if not exe:
        return False
    edge = ctx.out / "edge"
    subprocess.run([sys.executable, str(ctx.game / "tools" / "tests" / "make_edge_cases.py"), str(edge)],
                   check=True)
    models = sorted((ctx.game / "sdcard" / "MODELS").glob("*.STL")) + sorted(edge.glob("*.STL"))
    bad = [m.name for m in models if subprocess.run([str(exe), str(m)]).returncode]
    if bad:
        print("accuracy: failed on " + " ".join(bad))
    return not bad
