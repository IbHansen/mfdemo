"""Regenerate the diagrams from their .dot sources.

Needs graphviz on PATH (it ships with the book314 environment).
Writes a PNG at 200 dpi for LaTeX/PDF and an SVG for anything that wants it.

    python diagrams/build.py
"""
import subprocess, sys, pathlib

here = pathlib.Path(__file__).parent
dots = sorted(here.glob("*.dot"))
if not dots:
    sys.exit("no .dot files found in " + str(here))

for d in dots:
    for fmt, extra in (("png", ["-Gdpi=200"]), ("svg", [])):
        out = d.with_suffix("." + fmt)
        subprocess.run(["dot", "-T" + fmt, *extra, "-o", str(out), str(d)], check=True)
    print("built", d.stem)
print(f"\n{len(dots)} diagram(s) rebuilt.")
