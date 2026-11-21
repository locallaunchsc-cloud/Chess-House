#!/usr/bin/env python3
"""Chess Houses: REAL HOUSE mode (main style).

The position is NOT drawn as a grid. Instead the chess-meaningful features of the
position become ordinary house features. Every feature has one meaning and always
lives in the same place on the house.

  WHOLE HOUSE
    wall colour + siding ..... opening family   (Sicilian = yellow clapboard, ...)
    roof shape ............... White's first move (e4 gable, d4 hip, c4 barn, Nf3 flat)
    trim colour .............. variation (window frames, door, gutters)
    day / night .............. White / Black to move (windows glow at night)
  GROUND FLOOR = WHITE, UPSTAIRS = BLACK. Each floor has 6 spots, left to right,
  in the same order the pieces start on the board:  b-knight, c-bishop, queen,
  king, f-bishop, g-knight
    closed shutters .......... that piece is still at home
    round window ............. a knight came out
    square window ............ a bishop came out
    bay window (sticks out) .. the queen came out
    bare wall ................ that piece was captured
    king spot ................ downstairs = front door, upstairs = tall window:
                               double = can still castle both ways, single = one way
                               (or already castled), boarded up = can't castle any more
  EXTRAS
    garage (right / left) .... White castled short / long
    chimney (right / left) ... Black castled short / long
    front porch + columns .... White's rooks are connected
    upstairs balcony railing . Black's rooks are connected
    front steps (0-2) ........ White's centre pawns (d/e) that moved forward
    flower boxes (0-2) ....... Black's centre pawns (d/e) that moved forward
    garden path .............. a pawn has been captured (the game has opened up)
    flag in the yard ......... someone is ahead in material: white flag = White,
                               dark flag = Black, dots = how many pawns' worth
    name sign ................ optional (hide for quizzes)

Usage:
  python real_house.py --moves "1.e4 c5 2.Nf3" -o out.svg [--png] [--no-label]
  python real_house.py --fen "<FEN>" -o out.svg [--png]
  python real_house.py --legend -o legend.svg --png
"""
import argparse
import os
import sys

import chess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openings as OP  # noqa: E402
from openings import classify, classify_by_resemblance  # noqa: E402

W, H = 1000, 640
CROP = 96                    # top of the picture that is actually shown
GROUND = 500                 # ground line
HX0, HX1 = 240, 660          # house body x-range
BODY_TOP = 290
MID_FLOOR = 395              # boundary between floors
GF_Y, UF_Y = 446, 340        # window centre lines (ground / upper)
SLOT_X = [HX0 + 35 + 70 * i for i in range(6)]   # Nb, Bc, Q, K, Bf, Ng
SLOTS = ["Nb", "Bc", "Q", "K", "Bf", "Ng"]
FONT = 'font-family="DejaVu Sans, sans-serif"'
INK = "#2B2B2B"
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}

SIDING = {  # family wall colour -> siding texture
    OP.YELLOW: "clapboard", OP.RED: "brick", OP.ORANGE: "stucco", OP.SALMON: "batten",
    OP.PURPLE: "shingle", OP.PINK: "stucco", OP.CREAM: "clapboard", OP.BLUE: "stone",
    OP.SKY: "clapboard", OP.TEAL: "batten", OP.GREEN: "shingle", OP.GREY: "stone",
    OP.BROWN: "batten", OP.WHITE: "clapboard", OP.UNKNOWN_WALL: "stucco",
}
ROOF_COLOR = {"gable": "#8A3B2B", "castle": "#4C5866", "mansard": "#5E4433",
              "dome": "#3F6E5A", "flat": "#7A7A7A"}


def shade(hexcol, k):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * k))) for c in (r, g, b))


# ====================================================================== features
def piece_slots(board, color):
    """Return dict slot -> 'home' | 'out' | 'gone' for N, B, Q of one colour."""
    r = 0 if color == chess.WHITE else 7
    sq = lambda f: chess.square(f, r)
    res = {}
    for kind, pt, files in (("N", chess.KNIGHT, (1, 6)), ("B", chess.BISHOP, (2, 5))):
        names = [kind + "bcdefgh"[f - 1] for f in files]
        home = [board.piece_at(sq(f)) == chess.Piece(pt, color) for f in files]
        total = len(board.pieces(pt, color))
        out = max(0, total - sum(home))
        for name, h in zip(names, home):
            if h:
                res[name] = "home"
            elif out > 0:
                res[name] = "out"; out -= 1
            else:
                res[name] = "gone"
    q = board.pieces(chess.QUEEN, color)
    res["Q"] = "home" if sq(3) in q else ("out" if q else "gone")
    return res


def castled_side(board, color):
    """'K' / 'Q' if this side has castled, else None.
    Uses the move history when there is one; for a bare FEN it guesses from the
    position (no castling rights left and the king sits on a castled square)."""
    if board.move_stack:
        b = board.root()
        for mv in board.move_stack:
            if b.turn == color and b.is_castling(mv):
                return "K" if b.is_kingside_castling(mv) else "Q"
            b.push(mv)
        return None
    if board.has_castling_rights(color):
        return None
    f = chess.square_file(board.king(color))
    r = chess.square_rank(board.king(color))
    if r != (0 if color == chess.WHITE else 7):
        return None
    return "K" if f >= 6 else ("Q" if f <= 2 else None)


def king_spot(board, color):
    n = int(board.has_kingside_castling_rights(color)) + int(board.has_queenside_castling_rights(color))
    if n == 2:
        return "double"
    if n == 1 or castled_side(board, color):
        return "single"
    return "boarded"


def rooks_connected(board, color):
    r = 0 if color == chess.WHITE else 7
    rooks = [s for s in board.pieces(chess.ROOK, color) if chess.square_rank(s) == r]
    if len(rooks) != 2:
        return False
    a, b = sorted(chess.square_file(s) for s in rooks)
    return all(board.piece_at(chess.square(f, r)) is None for f in range(a + 1, b))


def centre_pawns_advanced(board, color):
    start = 1 if color == chess.WHITE else 6
    return sum(1 for s in board.pieces(chess.PAWN, color)
               if chess.square_file(s) in (3, 4) and chess.square_rank(s) != start)


def pawns_traded(board):
    """True once any pawn has left the board (the position has started to open)."""
    return len(board.pieces(chess.PAWN, chess.WHITE)) + len(board.pieces(chess.PAWN, chess.BLACK)) < 16


def material_diff(board):
    m = lambda c: sum(len(board.pieces(pt, c)) * v for pt, v in VALUES.items())
    return m(chess.WHITE) - m(chess.BLACK)


def features(board, op):
    return dict(
        night=board.turn == chess.BLACK,
        white=piece_slots(board, chess.WHITE), black=piece_slots(board, chess.BLACK),
        wking=king_spot(board, chess.WHITE), bking=king_spot(board, chess.BLACK),
        garage=castled_side(board, chess.WHITE), chimney=castled_side(board, chess.BLACK),
        porch=rooks_connected(board, chess.WHITE), railing=rooks_connected(board, chess.BLACK),
        steps=min(2, centre_pawns_advanced(board, chess.WHITE)),
        boxes=min(2, centre_pawns_advanced(board, chess.BLACK)),
        path=pawns_traded(board), diff=material_diff(board),
        wall=op["wall"], trim=op["trim"], roof=op["roof"],
        siding=SIDING.get(op["wall"], "clapboard"), name=op["name"],
    )


# ====================================================================== drawing
class Pen:
    def __init__(self, f):
        self.f = f
        self.s = []
        self.glass = "#FFD45E" if f["night"] else "#CFE9F7"
        self.frame = f["trim"]

    def add(self, x):
        self.s.append(x)


def sky(p):
    f = p.f
    if f["night"]:
        p.add(f'<rect width="{W}" height="{H}" fill="#1E2752"/>')
        p.add(f'<circle cx="{W-110}" cy="150" r="34" fill="#F4F0C8"/><circle cx="{W-94}" cy="140" r="30" fill="#1E2752"/>')
    else:
        p.add(f'<rect width="{W}" height="{H}" fill="#BFE4FA"/>')
        p.add(f'<circle cx="{W-110}" cy="150" r="36" fill="#FFD23F"/>')
    p.add(f'<rect x="0" y="{GROUND}" width="{W}" height="{H-GROUND}" fill="{"#3F7A3A" if f["night"] else "#7BC46A"}"/>')


def roof_poly(style):
    L, R, T = HX0 - 26, HX1 + 26, BODY_TOP
    if style == "gable":
        return f"M{L},{T} L{(L+R)/2},{T-150} L{R},{T} Z", ((L + R) / 2, T - 150)
    if style == "castle":      # hip roof (1.d4)
        return f"M{L},{T} L{L+110},{T-110} L{R-110},{T-110} L{R},{T} Z", ((L + R) / 2, T - 110)
    if style == "mansard":     # gambrel / barn roof (1.c4)
        return (f"M{L},{T} L{L+40},{T-70} L{(L+R)/2},{T-130} L{R-40},{T-70} L{R},{T} Z", ((L + R) / 2, T - 130))
    if style == "dome":        # flat modern roof with parapet (1.Nf3)
        return f"M{L},{T} L{L},{T-34} L{R},{T-34} L{R},{T} Z", ((L + R) / 2, T - 34)
    # start position / other: low shed roof
    return f"M{L},{T} L{L},{T-50} L{R},{T-20} L{R},{T} Z", ((L + R) / 2, T - 50)


def roof_and_chimney(p):
    f = p.f
    d, _ = roof_poly(f["roof"])
    # chimney (behind roof): Black castled
    if f["chimney"]:
        cx = HX1 - 70 if f["chimney"] == "K" else HX0 + 50
        p.add(f'<rect x="{cx}" y="{BODY_TOP-170}" width="34" height="150" fill="#9C4A3A" stroke="{INK}" stroke-width="3"/>'
              f'<rect x="{cx-5}" y="{BODY_TOP-180}" width="44" height="12" fill="#7E3A2D" stroke="{INK}" stroke-width="3"/>')
    col = ROOF_COLOR.get(f["roof"], "#7A7A7A")
    p.add(f'<path d="{d}" fill="{col}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    # roof shingle lines
    for y in range(BODY_TOP - 140, BODY_TOP, 18):
        p.add(f'<line x1="{HX0-30}" y1="{y}" x2="{HX1+30}" y2="{y}" stroke="{shade(col,0.8)}" stroke-width="2" '
              f'clip-path="url(#roofclip)"/>')
    p.add(f'<defs><clipPath id="roofclip"><path d="{d}"/></clipPath></defs>')
    # gutter in trim colour
    p.add(f'<rect x="{HX0-30}" y="{BODY_TOP-6}" width="{HX1-HX0+60}" height="10" rx="3" fill="{f["trim"]}" stroke="{INK}" stroke-width="2"/>')


def siding(p):
    f = p.f
    wall = f["wall"]
    line = shade(wall, 0.82)
    x0, x1, y0, y1 = HX0, HX1, BODY_TOP + 4, GROUND - 12
    p.add(f'<rect x="{HX0}" y="{BODY_TOP}" width="{HX1-HX0}" height="{GROUND-BODY_TOP}" fill="{wall}" stroke="{INK}" stroke-width="3"/>')
    t = f["siding"]
    if t == "clapboard":
        for y in range(y0 + 10, y1, 14):
            p.add(f'<line x1="{x0+2}" y1="{y}" x2="{x1-2}" y2="{y}" stroke="{line}" stroke-width="2"/>')
    elif t == "batten":
        for x in range(x0 + 16, x1, 20):
            p.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{line}" stroke-width="3"/>')
    elif t in ("brick", "stone"):
        bh, bw = (12, 30) if t == "brick" else (22, 40)
        row = 0
        for y in range(y0, y1 - bh + 1, bh):
            off = (bw / 2) * (row % 2)
            x = x0 - off
            while x < x1:
                xa, xb = max(x, x0 + 2), min(x + bw - 3, x1 - 2)
                if xb - xa > 4:
                    rx = 2 if t == "brick" else 6
                    p.add(f'<rect x="{xa}" y="{y+1.5}" width="{xb-xa}" height="{bh-3}" rx="{rx}" fill="{shade(wall, 1.06 if (row+int(x))%3 else 0.94)}" stroke="{line}" stroke-width="1"/>')
                x += bw
            row += 1
    elif t == "shingle":
        row = 0
        for y in range(y0 + 10, y1, 14):
            p.add(f'<line x1="{x0+2}" y1="{y}" x2="{x1-2}" y2="{y}" stroke="{line}" stroke-width="1.5"/>')
            for x in range(x0 + 6 + (8 if row % 2 else 0), x1 - 4, 16):
                p.add(f'<line x1="{x}" y1="{y-14}" x2="{x}" y2="{y}" stroke="{line}" stroke-width="1"/>')
            row += 1
    elif t == "stucco":
        import random
        rnd = random.Random(7)  # fixed seed: same texture every time
        for _ in range(90):
            p.add(f'<circle cx="{rnd.uniform(x0+4,x1-4):.0f}" cy="{rnd.uniform(y0,y1):.0f}" r="1.6" fill="{line}"/>')
    # foundation
    p.add(f'<rect x="{HX0-6}" y="{GROUND-12}" width="{HX1-HX0+12}" height="14" fill="#9A9A9A" stroke="{INK}" stroke-width="3"/>')
    # floor band
    p.add(f'<rect x="{HX0}" y="{MID_FLOOR-4}" width="{HX1-HX0}" height="8" fill="{f["trim"]}" stroke="{INK}" stroke-width="2"/>')


def shutters(p, cx, cy):
    col = shade(p.frame, 0.9)
    s = []
    for dx in (-23, 1):
        s.append(f'<rect x="{cx+dx}" y="{cy-25}" width="22" height="50" fill="{col}" stroke="{INK}" stroke-width="2.5"/>')
        for k in range(1, 6):
            s.append(f'<line x1="{cx+dx+3}" y1="{cy-25+k*8.3}" x2="{cx+dx+19}" y2="{cy-25+k*8.3}" stroke="{INK}" stroke-width="1" opacity="0.6"/>')
    p.add("".join(s))


def square_window(p, cx, cy, w=46, h=50):
    p.add(f'<rect x="{cx-w/2-4}" y="{cy-h/2-4}" width="{w+8}" height="{h+8}" fill="{p.frame}" stroke="{INK}" stroke-width="2.5"/>'
          f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" fill="{p.glass}" stroke="{INK}" stroke-width="1.5"/>'
          f'<line x1="{cx}" y1="{cy-h/2}" x2="{cx}" y2="{cy+h/2}" stroke="{p.frame}" stroke-width="4"/>'
          f'<line x1="{cx-w/2}" y1="{cy}" x2="{cx+w/2}" y2="{cy}" stroke="{p.frame}" stroke-width="4"/>'
          f'<rect x="{cx-w/2-8}" y="{cy+h/2+3}" width="{w+16}" height="6" fill="{p.frame}" stroke="{INK}" stroke-width="2"/>')


def round_window(p, cx, cy, r=25):
    p.add(f'<circle cx="{cx}" cy="{cy}" r="{r+5}" fill="{p.frame}" stroke="{INK}" stroke-width="2.5"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{p.glass}" stroke="{INK}" stroke-width="1.5"/>'
          f'<line x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}" stroke="{p.frame}" stroke-width="4"/>'
          f'<line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" stroke="{p.frame}" stroke-width="4"/>')


def bay_window(p, cx, cy):
    w, h = 60, 58
    roofc = ROOF_COLOR.get(p.f["roof"], "#777")
    p.add(f'<path d="M{cx-w/2-6},{cy-h/2} L{cx-w/2+4},{cy-h/2-14} L{cx+w/2-4},{cy-h/2-14} L{cx+w/2+6},{cy-h/2} Z" fill="{roofc}" stroke="{INK}" stroke-width="2.5"/>'
          f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" fill="{p.frame}" stroke="{INK}" stroke-width="2.5"/>')
    for i, (a, b) in enumerate(((-w/2+4, -w/2+16), (-w/2+19, w/2-19), (w/2-16, w/2-4))):
        g = p.glass if i == 1 else shade(p.glass, 0.85)
        p.add(f'<rect x="{cx+a}" y="{cy-h/2+4}" width="{b-a}" height="{h-14}" fill="{g}" stroke="{INK}" stroke-width="1.2"/>')
    p.add(f'<rect x="{cx-w/2-4}" y="{cy+h/2-6}" width="{w+8}" height="10" fill="{shade(p.frame,0.85)}" stroke="{INK}" stroke-width="2"/>')


def front_door(p, cx, kind):
    top, bot = GROUND - 92, GROUND - 12
    door = shade(p.frame, 0.95)
    if kind == "double":
        w = 60
        p.add(f'<rect x="{cx-w/2-5}" y="{top-5}" width="{w+10}" height="{bot-top+5}" fill="{INK}"/>')
        for dx in (-w/2, 0):
            p.add(f'<rect x="{cx+dx}" y="{top}" width="{w/2}" height="{bot-top}" fill="{door}" stroke="{INK}" stroke-width="2"/>'
                  f'<rect x="{cx+dx+6}" y="{top+8}" width="{w/2-12}" height="26" fill="{p.glass}" stroke="{INK}" stroke-width="1.2"/>'
                  f'<rect x="{cx+dx+6}" y="{top+42}" width="{w/2-12}" height="28" fill="none" stroke="{INK}" stroke-width="1.2"/>')
        p.add(f'<circle cx="{cx-5}" cy="{top+44}" r="2.5" fill="#E8C547"/><circle cx="{cx+5}" cy="{top+44}" r="2.5" fill="#E8C547"/>')
    else:
        w = 36
        p.add(f'<rect x="{cx-w/2-5}" y="{top-5}" width="{w+10}" height="{bot-top+5}" fill="{INK}"/>'
              f'<rect x="{cx-w/2}" y="{top}" width="{w}" height="{bot-top}" fill="{door}" stroke="{INK}" stroke-width="2"/>'
              f'<rect x="{cx-w/2+7}" y="{top+8}" width="{w-14}" height="26" fill="{p.glass}" stroke="{INK}" stroke-width="1.2"/>'
              f'<circle cx="{cx+w/2-7}" cy="{top+46}" r="2.5" fill="#E8C547"/>')
        if kind == "boarded":
            boards(p, cx, (top + bot) / 2, w + 14, bot - top)


def boards(p, cx, cy, w, h):
    for a in (-1, 1):
        p.add(f'<rect x="{cx-w/2}" y="{cy-6}" width="{w}" height="12" fill="#B07A45" stroke="{INK}" stroke-width="2" '
              f'transform="rotate({a*35},{cx},{cy})"/>')


def king_window(p, cx, cy, kind):
    """Upstairs king spot (Black): tall window(s)."""
    if kind == "double":
        for dx in (-15, 15):
            p.add(f'<rect x="{cx+dx-12}" y="{cy-32}" width="24" height="64" rx="12" fill="{p.frame}" stroke="{INK}" stroke-width="2.5"/>'
                  f'<rect x="{cx+dx-8}" y="{cy-28}" width="16" height="56" rx="8" fill="{p.glass}" stroke="{INK}" stroke-width="1.2"/>')
    else:
        p.add(f'<rect x="{cx-14}" y="{cy-32}" width="28" height="64" rx="14" fill="{p.frame}" stroke="{INK}" stroke-width="2.5"/>'
              f'<rect x="{cx-10}" y="{cy-28}" width="20" height="56" rx="10" fill="{p.glass}" stroke="{INK}" stroke-width="1.2"/>')
        if kind == "boarded":
            boards(p, cx, cy, 40, 64)


def floor(p, color):
    f = p.f
    cy = GF_Y if color == "white" else UF_Y
    slots = f[color]
    for name, cx in zip(SLOTS, SLOT_X):
        if name == "K":
            if color == "white":
                front_door(p, cx, f["wking"])
            else:
                king_window(p, cx, cy, f["bking"])
            continue
        st = slots[name]
        if st == "home":
            shutters(p, cx, cy)
        elif st == "gone":
            continue
        elif name.startswith("N"):
            round_window(p, cx, cy)
        elif name.startswith("B"):
            square_window(p, cx, cy)
        else:
            bay_window(p, cx, cy)


def flower_boxes(p):
    for i in range(p.f["boxes"]):
        cx = SLOT_X[1] if i == 0 else SLOT_X[4]
        y = UF_Y + 33
        p.add(f'<rect x="{cx-30}" y="{y}" width="60" height="13" fill="#8B5A2B" stroke="{INK}" stroke-width="2"/>')
        for k, c in enumerate(("#E84855", "#FFFFFF", "#F9DC5C", "#E84855", "#FFFFFF")):
            p.add(f'<circle cx="{cx-22+k*11}" cy="{y-3}" r="5" fill="{c}" stroke="{INK}" stroke-width="1"/>')


def railing(p):
    if not p.f["railing"]:
        return
    y0, y1 = MID_FLOOR - 26, MID_FLOOR - 2
    p.add(f'<rect x="{HX0+6}" y="{y0}" width="{HX1-HX0-12}" height="5" fill="#FFFFFF" stroke="{INK}" stroke-width="1.5"/>')
    for x in range(HX0 + 10, HX1 - 6, 12):
        p.add(f'<rect x="{x}" y="{y0+5}" width="4" height="{y1-y0-5}" fill="#FFFFFF" stroke="{INK}" stroke-width="1"/>')


def porch(p):
    if not p.f["porch"]:
        return
    x0, x1 = SLOT_X[3] - 54, SLOT_X[3] + 54 + 14
    top = MID_FLOOR + 4
    p.add(f'<path d="M{x0-10},{top+16} L{x0},{top} L{x1},{top} L{x1+10},{top+16} Z" fill="{ROOF_COLOR.get(p.f["roof"],"#777")}" stroke="{INK}" stroke-width="2.5"/>')
    for x in (x0, x1 - 14):
        p.add(f'<rect x="{x}" y="{top+16}" width="14" height="{GROUND-12-top-16}" fill="#FFFFFF" stroke="{INK}" stroke-width="2.5"/>'
              f'<rect x="{x-3}" y="{top+16}" width="20" height="6" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>'
              f'<rect x="{x-3}" y="{GROUND-18}" width="20" height="6" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>')


def garage(p):
    side = p.f["garage"]
    if not side:
        return
    gx0, gx1 = (HX1, HX1 + 150) if side == "K" else (HX0 - 150, HX0)
    top = GROUND - 110
    roofc = ROOF_COLOR.get(p.f["roof"], "#777")
    p.add(f'<rect x="{gx0}" y="{top}" width="{gx1-gx0}" height="{GROUND-top}" fill="{shade(p.f["wall"],0.95)}" stroke="{INK}" stroke-width="3"/>')
    p.add(f'<path d="M{gx0-10},{top} L{(gx0+gx1)/2},{top-40} L{gx1+10},{top} Z" fill="{roofc}" stroke="{INK}" stroke-width="3"/>')
    dx0, dx1 = gx0 + 18, gx1 - 18
    p.add(f'<rect x="{dx0}" y="{top+22}" width="{dx1-dx0}" height="{GROUND-top-22}" fill="#EDEDED" stroke="{INK}" stroke-width="2.5"/>')
    for y in range(top + 36, GROUND, 14):
        p.add(f'<line x1="{dx0}" y1="{y}" x2="{dx1}" y2="{y}" stroke="#9A9A9A" stroke-width="2"/>')
    # driveway
    p.add(f'<path d="M{dx0},{GROUND} L{dx1},{GROUND} L{dx1+14},{H} L{dx0-14},{H} Z" fill="#B8B8B8" stroke="{INK}" stroke-width="2"/>')


def steps_and_path(p):
    cx = SLOT_X[3]
    n = p.f["steps"]
    if p.f["path"]:
        y = GROUND - 2 + 12 * n
        p.add(f'<path d="M{cx-26},{y} L{cx+26},{y} L{cx+44},{H} L{cx-44},{H} Z" fill="#D9C7A3" stroke="{INK}" stroke-width="2"/>')
        for k, yy in enumerate(range(int(y) + 18, H, 26)):
            p.add(f'<line x1="{cx-30-k*2}" y1="{yy}" x2="{cx+30+k*2}" y2="{yy}" stroke="#B49B6E" stroke-width="2"/>')
    for i in range(n):  # stone steps
        w = 76 + i * 14
        p.add(f'<rect x="{cx-w/2}" y="{GROUND-2+i*12}" width="{w}" height="12" fill="#C9C9C9" stroke="{INK}" stroke-width="2"/>')


def flag(p):
    d = p.f["diff"]
    x = 44
    p.add(f'<rect x="{x-3}" y="250" width="6" height="{GROUND-250}" fill="#C8C8C8" stroke="{INK}" stroke-width="1.5"/>'
          f'<circle cx="{x}" cy="248" r="6" fill="#E8C547" stroke="{INK}" stroke-width="1.5"/>')
    if d == 0:
        return
    fill, dot = ("#FFFFFF", "#D62839") if d > 0 else ("#222222", "#F9DC5C")
    p.add(f'<path d="M{x+3},258 L{x+93},258 L{x+83},288 L{x+93},318 L{x+3},318 Z" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
    for i in range(min(abs(d), 9)):
        r_, c_ = divmod(i, 3)
        p.add(f'<circle cx="{x+20+c_*20}" cy="{272+r_*16}" r="5" fill="{dot}"/>')


def sign(p):
    name = p.f["name"]
    x = 908
    p.add(f'<rect x="{x-3}" y="{GROUND+20}" width="6" height="100" fill="#8B5A2B"/>'
          f'<rect x="{x-88}" y="{GROUND+8}" width="176" height="34" rx="6" fill="#FFF8E7" stroke="{INK}" stroke-width="2"/>'
          f'<text x="{x}" y="{GROUND+31}" font-size="{14 if len(name) < 20 else (12 if len(name) < 25 else 10.5)}" text-anchor="middle" {FONT} fill="{INK}">{name}</text>')


def render_real(board, op, label=True):
    return render_features(features(board, op), label)


def render_features(f, label=True):
    p = Pen(f)
    sky(p)
    flag(p)
    roof_and_chimney(p)
    garage(p)
    siding(p)
    railing(p)
    floor(p, "black")
    flower_boxes(p)
    floor(p, "white")
    porch(p)
    steps_and_path(p)
    if label:
        sign(p)
    return "\n".join(p.s)


def svg_doc(inner, w=W, h=H, crop=True):
    """House documents hide the empty top strip of sky (CROP)."""
    y0 = CROP if crop and (w, h) == (W, H) else 0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h-y0}" '
            f'viewBox="0 {y0} {w} {h-y0}">\n{inner}\n</svg>\n')


def main():
    from house import parse_moves
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fen"); g.add_argument("--moves"); g.add_argument("--legend", action="store_true")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--no-label", action="store_true")
    a = ap.parse_args()
    if a.legend:
        from real_legend import legend_svg
        svg = legend_svg()
    elif a.fen:
        b = chess.Board(a.fen)
        svg = svg_doc(render_real(b, classify_by_resemblance(b), not a.no_label))
    else:
        boards, _ = parse_moves(a.moves)
        svg = svg_doc(render_real(boards[-1], classify(boards), not a.no_label))
    with open(a.out, "w") as fh:
        fh.write(svg)
    if a.png:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=a.out[:-4] + ".png")


if __name__ == "__main__":
    main()
