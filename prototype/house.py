#!/usr/bin/env python3
"""Chess Houses prototype: turn a chess position into an SVG house.

Usage:
  python house.py --moves "1.e4 c5 2.Nf3 d6" -o out.svg [--png]
  python house.py --fen "<FEN>" -o out.svg [--png]
  python house.py --moves "..." --sequence -o outdir/   # one house per ply

Encoding (see ../DESIGN.md):
  * Wall colour / trim / roof shape  = opening family (Layer 1, gestalt)
  * 8 columns x 8 floors of the facade = files a-h x ranks 1-8 (Layer 2, exact)
      pawn   -> brick block        knight -> horseshoe-arch window
      bishop -> pointed-arch window rook  -> square tower window with battlement
      queen  -> round window + balcony    king -> door with a crown
      White pieces glow warm yellow (lights on); Black pieces are dark glass.
  * Garden fence gates (bottom)  = White castling rights (left gate O-O-O, right gate O-O)
  * Chimneys (roof)              = Black castling rights (left q, right k)
  * Puddle under a column        = en-passant square file
  * Day sky / night sky          = White / Black to move
  * Flag on the roof             = material balance (colour = side ahead, stripes = pawns ahead)
  * House number                 = full-move number
"""
import argparse
import math
import os
import re
import sys

import chess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openings import classify, classify_by_resemblance  # noqa: E402

CELL = 56
COLS = 8
X0 = 96                      # left edge of facade
GROUND = 640                 # y of ground line
TOP = GROUND - CELL * 8      # top of facade
W, H = X0 * 2 + CELL * COLS, 760

LIT = "#FFFCEB"; LIT_FRAME = "#5A4500"
DARK = "#262A3B"; DARK_FRAME = "#F5F5F5"
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}


def cell_xy(sq):
    f, r = chess.square_file(sq), chess.square_rank(sq)
    return X0 + f * CELL, GROUND - (r + 1) * CELL


def shade(hexcol, k):
    hexcol = hexcol.lstrip("#")
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
    f = lambda c: max(0, min(255, int(c * k)))
    return "#%02X%02X%02X" % (f(r), f(g), f(b))


# ---------------------------------------------------------------- pieces
def piece_svg(piece, x, y):
    c = CELL
    white = piece.color == chess.WHITE
    glass, frame = (LIT, LIT_FRAME) if white else (DARK, DARK_FRAME)
    pt = piece.piece_type
    cx = x + c / 2
    s = []
    if pt == chess.PAWN:
        # brick block: 3 rows of bricks
        base = "#F3E9D2" if white else "#5B3A29"
        mortar = "#9C8B6E" if white else "#2A1A12"
        bx, by, bw, bh = x + 6, y + 14, c - 12, c - 20
        s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{base}" stroke="{mortar}" stroke-width="2" rx="2"/>')
        for i in (1, 2):
            yy = by + bh * i / 3
            s.append(f'<line x1="{bx}" y1="{yy}" x2="{bx+bw}" y2="{yy}" stroke="{mortar}" stroke-width="1.5"/>')
        for row in range(3):
            y1, y2 = by + bh * row / 3, by + bh * (row + 1) / 3
            offs = [0.5] if row % 2 == 0 else [0.25, 0.75]
            for o in offs:
                xx = bx + bw * o
                s.append(f'<line x1="{xx}" y1="{y1}" x2="{xx}" y2="{y2}" stroke="{mortar}" stroke-width="1.5"/>')
    elif pt == chess.KNIGHT:
        # horseshoe arch: wide round top, pinched bottom
        r = 16
        top = y + 10
        p = (f"M{cx-10},{y+c-8} L{cx-13},{top+r+6} A{r},{r} 0 1 1 {cx+13},{top+r+6} "
             f"L{cx+10},{y+c-8} Z")
        s.append(f'<path d="{p}" fill="{glass}" stroke="{frame}" stroke-width="3"/>')
        s.append(f'<line x1="{cx}" y1="{top+4}" x2="{cx}" y2="{y+c-8}" stroke="{frame}" stroke-width="1.5"/>')
    elif pt == chess.BISHOP:
        # pointed gothic arch (mitre)
        p = f"M{cx-12},{y+c-8} L{cx-12},{y+24} Q{cx-12},{y+10} {cx},{y+4} Q{cx+12},{y+10} {cx+12},{y+24} L{cx+12},{y+c-8} Z"
        s.append(f'<path d="{p}" fill="{glass}" stroke="{frame}" stroke-width="3"/>')
        s.append(f'<line x1="{cx-7}" y1="{y+22}" x2="{cx+7}" y2="{y+34}" stroke="{frame}" stroke-width="2"/>')
    elif pt == chess.ROOK:
        # square window with battlements on top
        bx, by, bw = x + 10, y + 16, c - 20
        s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{c-24}" fill="{glass}" stroke="{frame}" stroke-width="3"/>')
        for i in range(3):
            s.append(f'<rect x="{bx + i*(bw-8)/2}" y="{by-9}" width="8" height="9" fill="{frame}"/>')
        s.append(f'<line x1="{cx}" y1="{by}" x2="{cx}" y2="{y+c-8}" stroke="{frame}" stroke-width="1.5"/>')
        s.append(f'<line x1="{bx}" y1="{by+(c-24)/2}" x2="{bx+bw}" y2="{by+(c-24)/2}" stroke="{frame}" stroke-width="1.5"/>')
    elif pt == chess.QUEEN:
        # rose window with a balcony + flower pots
        cy = y + 22
        s.append(f'<circle cx="{cx}" cy="{cy}" r="15" fill="{glass}" stroke="{frame}" stroke-width="3"/>')
        for a in range(0, 180, 45):
            dx, dy = 15 * math.cos(math.radians(a)), 15 * math.sin(math.radians(a))
            s.append(f'<line x1="{cx-dx}" y1="{cy-dy}" x2="{cx+dx}" y2="{cy+dy}" stroke="{frame}" stroke-width="1.2"/>')
        rail = "#FFFFFF" if not white else "#5A4500"
        s.append(f'<rect x="{x+4}" y="{y+c-12}" width="{c-8}" height="5" fill="{rail}"/>')
        for i in range(6):
            xx = x + 7 + i * (c - 14) / 5
            s.append(f'<line x1="{xx}" y1="{y+c-12}" x2="{xx}" y2="{y+c-3}" stroke="{rail}" stroke-width="2"/>')
        s.append(f'<circle cx="{x+9}" cy="{y+c-15}" r="4" fill="#E53950"/><circle cx="{x+c-9}" cy="{y+c-15}" r="4" fill="#E53950"/>')
    elif pt == chess.KING:
        # door with a crown above
        dx, dy, dw = x + 14, y + 18, c - 28
        s.append(f'<rect x="{dx}" y="{dy}" width="{dw}" height="{c-18}" rx="3" fill="{glass}" stroke="{frame}" stroke-width="3"/>')
        s.append(f'<circle cx="{dx+dw-6}" cy="{dy+(c-18)/2+3}" r="2.5" fill="{frame}"/>')
        crown = (f"M{cx-11},{y+15} L{cx-11},{y+5} L{cx-5},{y+10} L{cx},{y+2} "
                 f"L{cx+5},{y+10} L{cx+11},{y+5} L{cx+11},{y+15} Z")
        s.append(f'<path d="{crown}" fill="#F2B705" stroke="#7A5600" stroke-width="1.5"/>')
    return "\n".join(s)


# ---------------------------------------------------------------- house parts
def roof_svg(style, wall, trim, board):
    L, R = X0 - 14, X0 + CELL * COLS + 14
    mid = (L + R) / 2
    roofc = shade(wall, 0.62)
    s = []
    # chimneys = Black castling rights (drawn first so roof overlaps base)
    chim = []
    if board.has_queenside_castling_rights(chess.BLACK):
        chim.append(X0 + CELL * 1.5)
    if board.has_kingside_castling_rights(chess.BLACK):
        chim.append(X0 + CELL * 6.5)
    for cxm in chim:
        s.append(f'<rect x="{cxm-14}" y="{TOP-92}" width="28" height="92" fill="#8D4B3B" stroke="#3A1E16" stroke-width="2"/>')
        s.append(f'<rect x="{cxm-18}" y="{TOP-100}" width="36" height="10" fill="#6E3A2D"/>')
        for k, (ox, oy, r) in enumerate([(4, -112, 8), (12, -128, 10), (6, -148, 12)]):
            s.append(f'<circle cx="{cxm+ox}" cy="{TOP+oy}" r="{r}" fill="#E6E6E6" opacity="{0.85-0.2*k}"/>')
    if style == "gable":
        s.append(f'<path d="M{L},{TOP} L{mid},{TOP-120} L{R},{TOP} Z" fill="{roofc}" stroke="{trim}" stroke-width="6" stroke-linejoin="round"/>')
        apex = (mid, TOP - 120)
    elif style == "castle":
        s.append(f'<rect x="{L}" y="{TOP-40}" width="{R-L}" height="40" fill="{roofc}" stroke="{trim}" stroke-width="5"/>')
        n = 9
        w = (R - L) / (2 * n - 1)
        for i in range(n):
            s.append(f'<rect x="{L + 2*i*w}" y="{TOP-64}" width="{w}" height="24" fill="{roofc}" stroke="{trim}" stroke-width="4"/>')
        apex = (mid, TOP - 64)
    elif style == "mansard":
        s.append(f'<path d="M{L},{TOP} L{L+40},{TOP-70} L{R-40},{TOP-70} L{R},{TOP} Z" fill="{roofc}" stroke="{trim}" stroke-width="5"/>')
        apex = (mid, TOP - 70)
    elif style == "dome":
        s.append(f'<path d="M{L},{TOP} A{(R-L)/2},110 0 0 1 {R},{TOP} Z" fill="{roofc}" stroke="{trim}" stroke-width="5"/>')
        apex = (mid, TOP - 110)
    else:
        s.append(f'<rect x="{L}" y="{TOP-22}" width="{R-L}" height="22" fill="{roofc}" stroke="{trim}" stroke-width="5"/>')
        apex = (mid, TOP - 22)
    return "\n".join(s), apex


def flag_svg(board, apex):
    def mat(color):
        return sum(len(board.pieces(pt, color)) * v for pt, v in VALUES.items())
    diff = mat(chess.WHITE) - mat(chess.BLACK)
    ax, ay = apex
    s = [f'<line x1="{ax}" y1="{ay}" x2="{ax}" y2="{ay-60}" stroke="#333" stroke-width="3"/>']
    if diff == 0:
        s.append(f'<circle cx="{ax}" cy="{ay-62}" r="5" fill="#333"/>')  # bare pole = equal
        return "\n".join(s)
    col, stripe = ("#FFFFFF", "#D32F2F") if diff > 0 else ("#222222", "#FFD54F")
    s.append(f'<rect x="{ax}" y="{ay-60}" width="54" height="34" fill="{col}" stroke="#333" stroke-width="2"/>')
    n = min(abs(diff), 9)
    for i in range(n):
        xx = ax + 5 + i * 5.2
        s.append(f'<line x1="{xx}" y1="{ay-56}" x2="{xx}" y2="{ay-30}" stroke="{stripe}" stroke-width="3"/>')
    return "\n".join(s)


def sky_svg(board):
    if board.turn == chess.WHITE:
        return (f'<rect width="{W}" height="{H}" fill="#BFE6FF"/>'
                f'<circle cx="{W-70}" cy="70" r="36" fill="#FFD93B"/>')
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="2" fill="#FFF"/>'
                    for x, y in [(40, 40), (120, 90), (200, 30), (300, 60), (420, 25), (500, 100), (90, 180), (560, 170)])
    return (f'<rect width="{W}" height="{H}" fill="#1B2347"/>{stars}'
            f'<circle cx="{W-70}" cy="70" r="30" fill="#F4F1C9"/><circle cx="{W-56}" cy="62" r="26" fill="#1B2347"/>')


def garden_svg(board):
    s = [f'<rect x="0" y="{GROUND}" width="{W}" height="{H-GROUND}" fill="#7CC36B"/>']
    fy = GROUND + 40
    # White castling rights = fence + gate on that side
    def fence(x1, x2):
        out = [f'<rect x="{x1}" y="{fy+8}" width="{x2-x1}" height="5" fill="#FFFFFF" stroke="#777"/>']
        x = x1
        while x <= x2:
            out.append(f'<path d="M{x},{fy+30} L{x},{fy} L{x+5},{fy-7} L{x+10},{fy} L{x+10},{fy+30} Z" fill="#FFFFFF" stroke="#777"/>')
            x += 16
        return "".join(out)
    if board.has_queenside_castling_rights(chess.WHITE):
        s.append(fence(X0, X0 + CELL * 3))
    if board.has_kingside_castling_rights(chess.WHITE):
        s.append(fence(X0 + CELL * 5, X0 + CELL * 8 - 10))
    # path to the house
    return "\n".join(s)


def ep_svg(board):
    if board.ep_square is None or not board.has_legal_en_passant():
        return ""
    x = X0 + chess.square_file(board.ep_square) * CELL + CELL / 2
    return f'<ellipse cx="{x}" cy="{GROUND+18}" rx="24" ry="8" fill="#4FA3E0" stroke="#1E6FA8" stroke-width="2"/>'


def render(board, opening, label=True):
    wall, trim = opening["wall"], opening["trim"]
    out = [sky_svg(board), garden_svg(board), ep_svg(board)]
    roof, apex = roof_svg(opening["roof"], wall, trim, board)
    out.append(flag_svg(board, apex))
    out.append(roof)
    # facade
    out.append(f'<rect x="{X0}" y="{TOP}" width="{CELL*COLS}" height="{CELL*8}" fill="{wall}" stroke="{trim}" stroke-width="6"/>')
    # faint floor lines + column guides so kids can count floors/columns
    for i in range(1, 8):
        out.append(f'<line x1="{X0}" y1="{TOP+i*CELL}" x2="{X0+CELL*8}" y2="{TOP+i*CELL}" stroke="{shade(wall,0.85)}" stroke-width="1"/>')
        out.append(f'<line x1="{X0+i*CELL}" y1="{TOP}" x2="{X0+i*CELL}" y2="{GROUND}" stroke="{shade(wall,0.9)}" stroke-width="1" stroke-dasharray="3,5"/>')
    for sq, pc in board.piece_map().items():
        x, y = cell_xy(sq)
        out.append(piece_svg(pc, x, y))
    # column letters / floor numbers (the house's "street address")
    txt = "#FFFFFF" if board.turn == chess.BLACK else "#334"
    for f in range(8):
        out.append(f'<text x="{X0+f*CELL+CELL/2}" y="{GROUND+16}" font-size="14" font-weight="bold" text-anchor="middle" fill="#2E5E24" font-family="sans-serif">{"abcdefgh"[f]}</text>')
    for r in range(8):
        out.append(f'<text x="{X0-26}" y="{GROUND-r*CELL-CELL/2+5}" font-size="14" text-anchor="middle" fill="{txt}" font-family="sans-serif">{r+1}</text>')
    # house number = move number
    out.append(f'<rect x="{X0+CELL*8+20}" y="{GROUND-60}" width="44" height="30" rx="4" fill="#FFFFFF" stroke="#333" stroke-width="2"/>'
               f'<text x="{X0+CELL*8+42}" y="{GROUND-39}" font-size="16" font-weight="bold" text-anchor="middle" font-family="sans-serif">{board.fullmove_number}</text>')
    if label:
        name = f'{opening["name"]} ({opening["eco"]})'
        out.append(f'<rect x="8" y="{H-26}" width="{W-16}" height="22" rx="6" fill="#FFFFFFCC"/>'
                   f'<text x="{W/2}" y="{H-10}" font-size="14" text-anchor="middle" font-family="sans-serif" fill="#222">{name}</text>')
    return "\n".join(out)


def svg_doc(inner, w=W, h=H):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{inner}\n</svg>\n'


# ---------------------------------------------------------------- inputs
def parse_moves(text):
    text = re.sub(r"\{[^}]*\}", " ", text)
    toks = [t for t in text.replace(".", ". ").split()
            if not re.fullmatch(r"\d+\.+|1-0|0-1|1/2-1/2|\*", t)]
    b = chess.Board()
    boards = [b.copy()]
    sans = []
    for t in toks:
        sans.append(b.san(b.parse_san(t)))
        b.push_san(t)
        boards.append(b.copy())
    return boards, sans


def house_for_boards(boards, label=True):
    return svg_doc(render(boards[-1], classify(boards), label))


def write(svg_text, path, png=False):
    with open(path, "w") as fh:
        fh.write(svg_text)
    if png:
        import cairosvg
        cairosvg.svg2png(bytestring=svg_text.encode(), write_to=path[:-4] + ".png")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fen")
    g.add_argument("--moves")
    ap.add_argument("-o", "--out", required=True, help="SVG file, or directory with --sequence")
    ap.add_argument("--png", action="store_true", help="also write PNG (needs cairosvg)")
    ap.add_argument("--sequence", action="store_true", help="one house per ply")
    ap.add_argument("--no-label", action="store_true", help="hide the opening-name signboard (quiz mode)")
    a = ap.parse_args()
    label = not a.no_label
    if a.fen:
        board = chess.Board(a.fen)
        write(svg_doc(render(board, classify_by_resemblance(board), label)), a.out, a.png)
        return
    boards, sans = parse_moves(a.moves)
    if not a.sequence:
        write(house_for_boards(boards, label), a.out, a.png)
        return
    os.makedirs(a.out, exist_ok=True)
    for i in range(len(boards)):
        write(house_for_boards(boards[:i + 1], label), os.path.join(a.out, f"ply{i:02d}.svg"), a.png)


if __name__ == "__main__":
    main()
