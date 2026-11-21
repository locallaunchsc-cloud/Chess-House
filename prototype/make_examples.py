#!/usr/bin/env python3
"""Regenerate everything in ../examples/ (SVG + PNG)."""
import os
import re

import cairosvg

from house import W, H, parse_moves, render, svg_doc
from openings import classify

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "examples")

GAMES = {
    "sicilian_najdorf": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6",
    "italian_game": "1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5",
    "queens_gambit_declined": "1.d4 d5 2.c4 e6 3.Nc3 Nf6",
}


def save(svg, name):
    path = os.path.join(OUT, name)
    with open(path + ".svg", "w") as fh:
        fh.write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path + ".png")


def contact_sheet(boards, sans, cols=4, scale=0.42):
    cw, ch = W * scale, (H + 40) * scale
    rows = (len(boards) + cols - 1) // cols
    parts = []
    for i, _ in enumerate(boards):
        x, y = (i % cols) * cw, (i // cols) * ch
        inner = render(boards[i], classify(boards[: i + 1]), label=True)
        if i == 0:
            cap = "start"
        else:
            n = (i + 1) // 2
            cap = f"{n}. {sans[i-1]}" if i % 2 == 1 else f"{n}... {sans[i-1]}"
        parts.append(f'<svg x="{x}" y="{y}" width="{W*scale}" height="{H*scale}" viewBox="0 0 {W} {H}">{inner}</svg>')
        parts.append(f'<text x="{x + cw/2}" y="{y + H*scale + 14}" font-size="14" font-weight="bold" '
                     f'text-anchor="middle" font-family="sans-serif">{cap}</text>')
    return svg_doc('<rect width="100%" height="100%" fill="#FFFFFF"/>' + "".join(parts), cols * cw, rows * ch)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, moves in GAMES.items():
        boards, sans = parse_moves(moves)
        save(svg_doc(render(boards[-1], classify(boards))), name)
        save(svg_doc(render(boards[-1], classify(boards), label=False)), name + "_quiz")
    # move-by-move Sicilian
    boards, sans = parse_moves(GAMES["sicilian_najdorf"])
    seq = os.path.join(OUT, "sicilian_sequence")
    os.makedirs(seq, exist_ok=True)
    for i in range(len(boards)):
        save(svg_doc(render(boards[i], classify(boards[: i + 1]))), os.path.join("sicilian_sequence", f"ply{i:02d}"))
    save(contact_sheet(boards, sans), "sicilian_sequence_sheet")
    print("examples written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
