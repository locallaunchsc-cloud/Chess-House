#!/usr/bin/env python3
"""Regenerate ../examples/real/ (real-house mode, the main style)."""
import os

import cairosvg

from house import parse_moves
from make_examples import GAMES
from openings import classify
from real_house import CROP, W, render_real, svg_doc
from real_house import H as FULL_H
H = FULL_H - CROP
from real_legend import legend_svg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "real")
FONT = 'font-family="DejaVu Sans, sans-serif"'


def save(svg, name):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".svg", "w") as fh:
        fh.write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=p + ".png")


def caption(i, sans):
    if i == 0:
        return "start: every shutter closed"
    n = (i + 1) // 2
    return f"{n}. {sans[i-1]}" if i % 2 == 1 else f"{n}... {sans[i-1]}"


def sheet(boards, sans, cols=4, scale=0.36, label=True):
    cw, ch = W * scale + 14, H * scale + 34
    rows = (len(boards) + cols - 1) // cols
    parts = ['<rect width="100%" height="100%" fill="#FFFFFF"/>']
    for i in range(len(boards)):
        x, y = (i % cols) * cw + 7, (i // cols) * ch + 4
        parts.append(f'<svg x="{x}" y="{y}" width="{W*scale}" height="{H*scale}" viewBox="0 {CROP} {W} {H}">'
                     f'{render_real(boards[i], classify(boards[:i+1]), label)}</svg>')
        parts.append(f'<text x="{x + W*scale/2}" y="{y + H*scale + 22}" font-size="17" font-weight="bold" '
                     f'text-anchor="middle" {FONT}>{caption(i, sans)}</text>')
    return svg_doc("".join(parts), cols * cw, rows * ch)


def main():
    for name, moves in GAMES.items():
        boards, _ = parse_moves(moves)
        save(svg_doc(render_real(boards[-1], classify(boards))), name)
        save(svg_doc(render_real(boards[-1], classify(boards), label=False)), name + "_quiz")
    boards, sans = parse_moves(GAMES["sicilian_najdorf"])
    for i in range(len(boards)):
        save(svg_doc(render_real(boards[i], classify(boards[:i+1]))), f"sicilian_sequence/ply{i:02d}")
    save(sheet(boards, sans), "sicilian_sequence_sheet")
    # the three openings side by side (no signs) to show they look different
    trio = []
    for name, moves in GAMES.items():
        b, _ = parse_moves(moves)
        trio.append(render_real(b[-1], classify(b), label=False))
    sc = 0.5
    parts = ['<rect width="100%" height="100%" fill="#FFFFFF"/>']
    for i, inner in enumerate(trio):
        parts.append(f'<svg x="{i*(W*sc+10)}" y="0" width="{W*sc}" height="{H*sc}" viewBox="0 {CROP} {W} {H}">{inner}</svg>')
    save(svg_doc("".join(parts), 3 * (W * sc + 10), H * sc), "three_openings")
    save(legend_svg(), "legend")
    print("written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
