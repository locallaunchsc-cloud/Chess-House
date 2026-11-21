#!/usr/bin/env python3
"""Chess Houses: SIMPLE / kid mode.

Built for strong pattern-recognition brains (e.g. autistic kids):
  * every visual feature means exactly ONE thing and ALWAYS sits in the SAME spot
  * nothing decorative: no sun/moon/stars, smoke, flowers, mortar lines, text, grid
  * flat shapes, solid fills, high contrast
  * a "lost" feature is drawn as an empty dashed outline in its fixed spot
    (never just vanishes) so two houses can be compared slot by slot.

Fixed layout (top to bottom):
  flag slot -> roof box (+ 2 chimney slots) -> trim band -> 8x8 facade
  -> en-passant strip -> 2 fence slots

Usage:
  python simple.py --moves "1.e4 c5 2.Nf3" -o out.svg [--png]
  python simple.py --fen "<FEN>" -o out.svg [--png]
  python simple.py --legend -o legend.svg --png
"""
import argparse
import os
import sys

import chess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openings import classify, classify_by_resemblance  # noqa: E402

CELL = 56
X0 = 56
W = X0 * 2 + CELL * 8              # 560
FLAG_Y = 8                         # flag slot
ROOF_TOP, ROOF_BOT = 76, 176       # fixed roof box
TRIM_Y, TRIM_H = 176, 16           # trim band
FAC_TOP = TRIM_Y + TRIM_H          # 192
FAC_BOT = FAC_TOP + CELL * 8       # 640
EP_Y = FAC_BOT + 20                # en-passant marker row
FENCE_Y = FAC_BOT + 44             # fence slots
H = FENCE_Y + 52                   # 736

BLACK, WHITE_ = "#000000", "#FFFFFF"
DAY_BG, NIGHT_BG = "#D6ECFF", "#1E1E46"
GROUND = "#3E7B32"
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

# Mid-tone, saturated versions of the family colours so BOTH white and black
# pieces stand out on every wall.
SIMPLE_WALL = {
    "#F6C945": "#E8B400",  # Sicilian  yellow
    "#D9614C": "#D2372A",  # Italian   red
    "#F09A3E": "#F07800",  # Ruy Lopez orange
    "#F2A28F": "#E86F6F",  # Open game salmon
    "#A58BD6": "#8A5CD6",  # French    purple
    "#F3A6C8": "#E05AA0",  # Caro-Kann pink
    "#EFE3C2": "#C9AE6A",  # other e4  sand
    "#6C9BE8": "#2F6FDB",  # QGD       blue
    "#9CCBF0": "#36A3E0",  # QGA       sky
    "#5CC2B0": "#1FA896",  # Slav      teal
    "#6DBF6A": "#3EA63A",  # Indian    green
    "#B9C2CF": "#7D8A9C",  # other d4  slate
    "#B98A62": "#9A6A3E",  # English   brown
    "#E9E4D8": "#A9A9A9",  # start     grey
    "#CFCAC0": "#8E8E8E",  # unknown   dark grey
}


def wall_of(op):
    return SIMPLE_WALL.get(op["wall"], op["wall"])


def shade(hexcol, k):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * k))) for c in (r, g, b))


# ------------------------------------------------------------------ pieces
def piece_shape(pt, white, cx, cy):
    """Flat silhouette centred on (cx, cy). Same centre for every piece."""
    fill, stroke = (WHITE_, BLACK) if white else (BLACK, WHITE_)
    a = f'fill="{fill}" stroke="{stroke}" stroke-width="3" stroke-linejoin="round"'
    if pt == chess.PAWN:            # small square = brick
        return f'<rect x="{cx-12}" y="{cy-12}" width="24" height="24" {a}/>'
    if pt == chess.ROOK:            # square with 3 battlements
        return (f'<path d="M{cx-16},{cy+18} L{cx-16},{cy-18} L{cx-9},{cy-18} L{cx-9},{cy-10} '
                f'L{cx-3},{cy-10} L{cx-3},{cy-18} L{cx+3},{cy-18} L{cx+3},{cy-10} L{cx+9},{cy-10} '
                f'L{cx+9},{cy-18} L{cx+16},{cy-18} L{cx+16},{cy+18} Z" {a}/>')
    if pt == chess.KNIGHT:          # round-top arch (horseshoe)
        return (f'<path d="M{cx-15},{cy+20} L{cx-15},{cy-5} A15,15 0 0 1 {cx+15},{cy-5} '
                f'L{cx+15},{cy+20} Z" {a}/>')
    if pt == chess.BISHOP:          # pointed arch
        return (f'<path d="M{cx-14},{cy+20} L{cx-14},{cy-4} L{cx},{cy-22} L{cx+14},{cy-4} '
                f'L{cx+14},{cy+20} Z" {a}/>')
    if pt == chess.QUEEN:           # circle
        return f'<circle cx="{cx}" cy="{cy}" r="18" {a}/>'
    if pt == chess.KING:            # tall door with a 3-point crown top
        return (f'<path d="M{cx-13},{cy+22} L{cx-13},{cy-12} L{cx-13},{cy-22} L{cx-6},{cy-14} '
                f'L{cx},{cy-24} L{cx+6},{cy-14} L{cx+13},{cy-22} L{cx+13},{cy+22} Z" {a}/>')
    return ""


def slot_center(sq):
    f, r = chess.square_file(sq), chess.square_rank(sq)
    return X0 + f * CELL + CELL / 2, FAC_BOT - r * CELL - CELL / 2


# ------------------------------------------------------------------ slots
def on_off(present, x, y, w, h, fill, stroke):
    if present:
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{stroke}" '
            f'stroke-width="2" stroke-dasharray="5,4" opacity="0.8"/>')


def roof(style, color, outline):
    L, R, mid = X0 - 12, X0 + CELL * 8 + 12, W / 2
    a = f'fill="{color}" stroke="{outline}" stroke-width="3" stroke-linejoin="round"'
    if style == "gable":       # 1.e4: triangle
        return f'<path d="M{L},{ROOF_BOT} L{mid},{ROOF_TOP} L{R},{ROOF_BOT} Z" {a}/>'
    if style == "castle":      # 1.d4: battlements
        n, d = 7, []
        w = (R - L) / (2 * n - 1)
        d.append(f"M{L},{ROOF_BOT}")
        for i in range(n):
            x1 = L + 2 * i * w
            d.append(f"L{x1},{ROOF_TOP} L{x1+w},{ROOF_TOP} L{x1+w},{ROOF_TOP+40}"
                     + (f" L{x1+2*w},{ROOF_TOP+40}" if i < n - 1 else ""))
        d.append(f"L{R},{ROOF_BOT} Z")
        return f'<path d="{" ".join(d)}" {a}/>'
    if style == "mansard":     # 1.c4: trapezoid
        return f'<path d="M{L},{ROOF_BOT} L{L+70},{ROOF_TOP} L{R-70},{ROOF_TOP} L{R},{ROOF_BOT} Z" {a}/>'
    if style == "dome":        # 1.Nf3: half-ellipse
        return f'<path d="M{L},{ROOF_BOT} A{(R-L)/2},{ROOF_BOT-ROOF_TOP} 0 0 1 {R},{ROOF_BOT} Z" {a}/>'
    # start / other: flat box (fills the same roof box)
    return f'<rect x="{L}" y="{ROOF_BOT-40}" width="{R-L}" height="40" {a}/>'


CHIM_X = {"q": X0 + CELL * 1, "k": X0 + CELL * 7 - 30}   # fixed chimney slots
CHIM_Y, CHIM_W, CHIM_H = ROOF_TOP + 4, 30, 56
FENCE_X = {"Q": X0, "K": X0 + CELL * 5}                  # fixed fence slots
FENCE_W, FENCE_H = CELL * 3, 26
FLAG_X, FLAG_W, FLAG_H = W / 2 + 4, 92, 40


def material_diff(board):
    m = lambda c: sum(len(board.pieces(pt, c)) * v for pt, v in VALUES.items())
    return m(chess.WHITE) - m(chess.BLACK)


def flag(board, outline):
    s = [f'<line x1="{W/2}" y1="{FLAG_Y}" x2="{W/2}" y2="{ROOF_TOP}" stroke="{outline}" stroke-width="4"/>']
    diff = material_diff(board)
    if diff == 0:
        s.append(on_off(False, FLAG_X, FLAG_Y, FLAG_W, FLAG_H, None, outline))
        return "".join(s)
    fill, bar = (WHITE_, BLACK) if diff > 0 else (BLACK, WHITE_)
    s.append(f'<rect x="{FLAG_X}" y="{FLAG_Y}" width="{FLAG_W}" height="{FLAG_H}" fill="{fill}" stroke="{outline}" stroke-width="3"/>')
    for i in range(min(abs(diff), 9)):     # one bar per pawn of advantage
        s.append(f'<rect x="{FLAG_X + 6 + i*9.4}" y="{FLAG_Y+7}" width="5" height="{FLAG_H-14}" fill="{bar}"/>')
    return "".join(s)


def render_simple(board, op):
    night = board.turn == chess.BLACK
    bg = NIGHT_BG if night else DAY_BG
    outline = WHITE_ if night else BLACK      # outlines for slots that sit on the sky
    wall = wall_of(op)
    s = [f'<rect width="{W}" height="{H}" fill="{bg}"/>',
         f'<rect x="0" y="{FAC_BOT}" width="{W}" height="{H-FAC_BOT}" fill="{GROUND}"/>']
    s.append(flag(board, outline))
    s.append(roof(op["roof"], shade(wall, 0.6), BLACK))
    # chimneys: Black castling rights (black = Black's)
    s.append(on_off(board.has_queenside_castling_rights(chess.BLACK), CHIM_X["q"], CHIM_Y, CHIM_W, CHIM_H, BLACK, outline))
    s.append(on_off(board.has_kingside_castling_rights(chess.BLACK), CHIM_X["k"], CHIM_Y, CHIM_W, CHIM_H, BLACK, outline))
    # trim band: variation
    s.append(f'<rect x="{X0-12}" y="{TRIM_Y}" width="{CELL*8+24}" height="{TRIM_H}" fill="{op["trim"]}" stroke="{BLACK}" stroke-width="3"/>')
    # facade
    s.append(f'<rect x="{X0}" y="{FAC_TOP}" width="{CELL*8}" height="{CELL*8}" fill="{wall}" stroke="{BLACK}" stroke-width="3"/>')
    for sq, pc in sorted(board.piece_map().items()):
        cx, cy = slot_center(sq)
        s.append(piece_shape(pc.piece_type, pc.color == chess.WHITE, cx, cy))
    # en-passant marker under its column
    if board.ep_square is not None and board.has_legal_en_passant():
        cx = X0 + chess.square_file(board.ep_square) * CELL + CELL / 2
        s.append(f'<circle cx="{cx}" cy="{EP_Y}" r="9" fill="#FFD400" stroke="{BLACK}" stroke-width="3"/>')
    # fences: White castling rights (white = White's)
    s.append(on_off(board.has_queenside_castling_rights(chess.WHITE), FENCE_X["Q"], FENCE_Y, FENCE_W, FENCE_H, WHITE_, BLACK))
    s.append(on_off(board.has_kingside_castling_rights(chess.WHITE), FENCE_X["K"], FENCE_Y, FENCE_W, FENCE_H, WHITE_, BLACK))
    return "\n".join(s)


def svg_doc(inner, w=W, h=H):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{inner}\n</svg>\n'


# ------------------------------------------------------------------ legend
def legend_svg():
    LW, LH = 1200, 1720
    F = 'font-family="DejaVu Sans, sans-serif"'
    s = [f'<rect width="{LW}" height="{LH}" fill="#FFFFFF"/>',
         f'<text x="40" y="58" font-size="38" font-weight="bold" {F}>Chess Houses: Legend</text>',
         f'<text x="40" y="94" font-size="20" {F} fill="#333">Every feature means one thing and is always in the same place. '
         f'An empty dashed box = that thing is gone.</text>']
    # left: a reference house (start position) with numbered call-outs
    b = chess.Board()
    op = classify([b])
    s.append(f'<g transform="translate(30,130) scale(0.78)">{render_simple(b, op)}</g>')
    sc, ox, oy = 0.78, 30, 130
    P = lambda x, y: (ox + x * sc, oy + y * sc)
    callouts = [
        ("1", P(W / 2 + 4 + FLAG_W / 2, FLAG_Y + FLAG_H / 2)),
        ("2", P(W / 2 - 90, ROOF_BOT - 20)),
        ("3", P(CHIM_X["q"] + 15, CHIM_Y + 28)),
        ("4", P(W / 2, TRIM_Y + 8)),
        ("5", P(X0 + CELL * 4, FAC_TOP + CELL * 4)),
        ("6", P(X0 + CELL * 4, EP_Y)),
        ("7", P(FENCE_X["Q"] + FENCE_W / 2, FENCE_Y + 13)),
        ("8", P(W - 10, 40)),
    ]
    for n, (x, y) in callouts:
        s.append(f'<circle cx="{x}" cy="{y}" r="15" fill="#E4002B" stroke="#FFF" stroke-width="2"/>'
                 f'<text x="{x}" y="{y+6}" font-size="17" font-weight="bold" text-anchor="middle" fill="#FFF" {F}>{n}</text>')
    # right column: explanations
    x0, y = 500, 150
    rows = [
        ("1", "FLAG (top, right of the pole) = who has more pieces",
              "Empty dashed box = equal. White flag = White is ahead. Black flag = Black is ahead. Number of bars = how many pawns ahead (pawn 1, knight 3, bishop 3, rook 5, queen 9)."),
        ("2", "ROOF SHAPE = White's first move",
              "Triangle = 1.e4   Battlements = 1.d4   Trapezoid = 1.c4   Dome = 1.Nf3   Flat = no move yet / other."),
        ("3", "CHIMNEYS = can Black still castle?",
              "Left chimney = long castle (O-O-O), right chimney = short castle (O-O). Filled black = yes. Dashed = no."),
        ("4", "TRIM BAND = which variation",
              "Same wall colour + different band = sister openings, e.g. yellow + blue band = Najdorf."),
        ("5", "WALL COLOUR = opening family",
              "The 8x8 wall IS the board: left to right = a to h, bottom to top = 1 to 8. White lives at the bottom, Black at the top."),
        ("6", "YELLOW DOT under a column = en passant",
              "A pawn on that column can be captured en passant right now."),
        ("7", "FENCES = can White still castle?",
              "Left fence = long castle (O-O-O), right fence = short castle (O-O). Filled white = yes. Dashed = no."),
        ("8", "SKY = whose turn",
              "Light sky = White to move. Dark sky = Black to move."),
    ]
    for n, title, body in rows:
        s.append(f'<circle cx="{x0}" cy="{y-7}" r="15" fill="#E4002B"/>'
                 f'<text x="{x0}" y="{y-1}" font-size="17" font-weight="bold" text-anchor="middle" fill="#FFF" {F}>{n}</text>')
        s.append(f'<text x="{x0+26}" y="{y}" font-size="20" font-weight="bold" {F}>{title}</text>')
        words, line, ly = body.split(), "", y + 26
        for w_ in words:
            if len(line) + len(w_) > 60:
                s.append(f'<text x="{x0+26}" y="{ly}" font-size="17" fill="#333" {F}>{line}</text>')
                line, ly = "", ly + 22
            line += w_ + " "
        s.append(f'<text x="{x0+26}" y="{ly}" font-size="17" fill="#333" {F}>{line}</text>')
        y = ly + 44
    # pieces table
    ty = 900
    s.append(f'<text x="40" y="{ty}" font-size="26" font-weight="bold" {F}>Pieces = shapes on the wall</text>')
    s.append(f'<text x="40" y="{ty+30}" font-size="18" fill="#333" {F}>White piece = white shape with black edge. Black piece = black shape with white edge.</text>')
    names = [(chess.PAWN, "Pawn", "small square"), (chess.KNIGHT, "Knight", "round arch"),
             (chess.BISHOP, "Bishop", "pointed arch"), (chess.ROOK, "Rook", "tower top"),
             (chess.QUEEN, "Queen", "circle"), (chess.KING, "King", "crown door")]
    for i, (pt, nm, desc) in enumerate(names):
        cx = 110 + i * 190
        s.append(f'<rect x="{cx-75}" y="{ty+55}" width="150" height="90" fill="#E8B400" stroke="#000" stroke-width="2"/>')
        s.append(piece_shape(pt, True, cx - 32, ty + 100))
        s.append(piece_shape(pt, False, cx + 32, ty + 100))
        s.append(f'<text x="{cx}" y="{ty+175}" font-size="21" font-weight="bold" text-anchor="middle" {F}>{nm}</text>')
        s.append(f'<text x="{cx}" y="{ty+199}" font-size="17" text-anchor="middle" fill="#333" {F}>{desc}</text>')
    # roof shapes + sky
    ty = 1160
    s.append(f'<text x="40" y="{ty}" font-size="26" font-weight="bold" {F}>Roof shape = first move</text>'
             f'<text x="800" y="{ty}" font-size="26" font-weight="bold" {F}>Sky = whose turn</text>')
    roofs = [("gable", "1.e4"), ("castle", "1.d4"), ("mansard", "1.c4"), ("dome", "1.Nf3"), ("flat", "none / other")]
    for i, (st, nm) in enumerate(roofs):
        x = 40 + i * 140
        s.append(f'<g transform="translate({x},{ty+20}) scale(0.22,0.6) translate(0,{-ROOF_TOP})">{roof(st, "#666666", "#000")}</g>')
        s.append(f'<text x="{x+62}" y="{ty+110}" font-size="18" text-anchor="middle" {F}>{nm}</text>')
    for i, (bgc, nm) in enumerate([(DAY_BG, "White to move"), (NIGHT_BG, "Black to move")]):
        x = 800 + i * 190
        s.append(f'<rect x="{x}" y="{ty+30}" width="150" height="56" fill="{bgc}" stroke="#000" stroke-width="2"/>'
                 f'<text x="{x+75}" y="{ty+110}" font-size="18" text-anchor="middle" {F}>{nm}</text>')
    # wall colours
    ty = 1330
    s.append(f'<text x="40" y="{ty}" font-size="26" font-weight="bold" {F}>Wall colour = opening family</text>')
    fams = [("#F6C945", "Sicilian"), ("#D9614C", "Italian"), ("#F09A3E", "Ruy Lopez"), ("#F2A28F", "Open Game (1.e4 e5)"),
            ("#A58BD6", "French"), ("#F3A6C8", "Caro-Kann"), ("#EFE3C2", "Other 1.e4"), ("#6C9BE8", "Queen's Gambit Declined"),
            ("#9CCBF0", "Queen's Gambit Accepted"), ("#5CC2B0", "Slav"), ("#6DBF6A", "Indian Defences"), ("#B9C2CF", "Other 1.d4"),
            ("#B98A62", "English / Reti"), ("#E9E4D8", "Starting position"), ("#CFCAC0", "Unknown")]
    for i, (k, nm) in enumerate(fams):
        col, row = i % 3, i // 3
        x, yy = 40 + col * 380, ty + 30 + row * 56
        s.append(f'<rect x="{x}" y="{yy}" width="60" height="40" fill="{SIMPLE_WALL[k]}" stroke="#000" stroke-width="2"/>'
                 f'<text x="{x+74}" y="{yy+27}" font-size="19" {F}>{nm}</text>')
    return svg_doc("\n".join(s), LW, LH)


def main():
    from house import parse_moves
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fen"); g.add_argument("--moves"); g.add_argument("--legend", action="store_true")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--png", action="store_true")
    a = ap.parse_args()
    if a.legend:
        svg = legend_svg()
    elif a.fen:
        b = chess.Board(a.fen)
        svg = svg_doc(render_simple(b, classify_by_resemblance(b)))
    else:
        boards, _ = parse_moves(a.moves)
        svg = svg_doc(render_simple(boards[-1], classify(boards)))
    with open(a.out, "w") as fh:
        fh.write(svg)
    if a.png:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=a.out[:-4] + ".png")


if __name__ == "__main__":
    main()
