#!/usr/bin/env python3
"""Regenerate ../examples/simple/ (kid mode): 3 openings, Sicilian sequence,
a spot-the-difference pair and the legend."""
import os

import cairosvg

from house import parse_moves
from make_examples import GAMES
from openings import classify
from simple import W, H, legend_svg, render_simple, svg_doc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "simple")


def save(svg, name):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p + ".svg", "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=p + ".png")


def sheet(boards, idx, cols, scale=0.42, gap=16):
    cw, ch = W * scale + gap, H * scale + gap
    rows = (len(idx) + cols - 1) // cols
    parts = ['<rect width="100%" height="100%" fill="#FFFFFF"/>']
    for k, i in enumerate(idx):
        x, y = (k % cols) * cw + gap / 2, (k // cols) * ch + gap / 2
        parts.append(f'<svg x="{x}" y="{y}" width="{W*scale}" height="{H*scale}" viewBox="0 0 {W} {H}">'
                     f'{render_simple(boards[i], classify(boards[:i+1]))}</svg>')
    return svg_doc("".join(parts), cols * cw, rows * ch)


def main():
    for name, moves in GAMES.items():
        boards, _ = parse_moves(moves)
        save(svg_doc(render_simple(boards[-1], classify(boards))), name)
    boards, _ = parse_moves(GAMES["sicilian_najdorf"])
    for i in range(len(boards)):
        save(svg_doc(render_simple(boards[i], classify(boards[:i+1]))), f"sicilian_sequence/ply{i:02d}")
    save(sheet(boards, list(range(len(boards))), cols=6, scale=0.36), "sicilian_sequence_sheet")
    # spot the difference: before / after 5...a6
    save(sheet(boards, [9, 10], cols=2, scale=0.6), "spot_the_difference")
    save(legend_svg(), "legend")
    print("written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
