"""One-page legend for real-house mode, in plain kid language.
Every icon is a crop of a real rendered house, so the legend can never drift
from what the renderer actually draws."""
import copy

import openings as OP
from real_house import (BODY_TOP, GF_Y, GROUND, HX0, HX1, MID_FLOOR, SLOT_X, UF_Y, W, H,
                        render_features, svg_doc)

F = 'font-family="DejaVu Sans, sans-serif"'
HOME = {k: "home" for k in ("Nb", "Bc", "Q", "Bf", "Ng")}
BASE = dict(night=False, white=dict(HOME), black=dict(HOME), wking="double", bking="double",
            garage=None, chimney=None, porch=False, railing=False, steps=0, boxes=0, path=False,
            diff=0, wall=OP.YELLOW, trim="#1565C0", roof="gable", siding="clapboard", name="")


def var(**kw):
    f = copy.deepcopy(BASE)
    for k, v in kw.items():
        if k in ("white", "black"):
            f[k].update(v)
        else:
            f[k] = v
    return f


def crop(f, x, y, w, h, bx, by, bw, bh):
    inner = render_features(f, label=False)
    return (f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="#FFFFFF" stroke="#BBB" stroke-width="2"/>'
            f'<svg x="{bx+4}" y="{by+4}" width="{bw-8}" height="{bh-8}" viewBox="{x} {y} {w} {h}">{inner}</svg>')


def wrap(text, n):
    out, line = [], ""
    for w_ in text.split():
        if len(line) + len(w_) + 1 > n:
            out.append(line); line = ""
        line += ("" if not line else " ") + w_
    out.append(line)
    return out


def card(f, region, title, body, x, y):
    s = [crop(f, *region, x, y, 150, 124)]
    s.append(f'<text x="{x+164}" y="{y+26}" font-size="17" font-weight="bold" {F}>{title}</text>')
    for i, ln in enumerate(wrap(body, 21)):
        s.append(f'<text x="{x+164}" y="{y+52+i*21}" font-size="16" fill="#333" {F}>{ln}</text>')
    return "".join(s)


SPOT = lambda i, cy: (SLOT_X[i] - 48, cy - 48, 96, 96)
DOOR = (SLOT_X[3] - 55, GROUND - 110, 110, 120)
KWIN = (SLOT_X[3] - 48, UF_Y - 48, 96, 96)

CARDS = [
    (var(white={"Nb": "out"}), SPOT(0, GF_Y), "Round window", "A knight came out."),
    (var(white={"Bc": "out"}), SPOT(1, GF_Y), "Square window", "A bishop came out."),
    (var(white={"Q": "out"}), (SLOT_X[2] - 52, GF_Y - 60, 104, 104), "Bay window", "The window that sticks out: the queen came out."),
    (var(), SPOT(0, GF_Y), "Closed shutters", "That piece is still at home. It hasn't moved yet."),
    (var(white={"Nb": "gone"}), SPOT(0, GF_Y), "Bare wall", "No window at all: that piece was captured."),
    (var(wking="double"), DOOR, "Double doors", "White's king can still castle both ways."),
    (var(wking="single"), DOOR, "Single door", "White's king can castle one way, or already castled."),
    (var(wking="boarded"), DOOR, "Boarded-up door", "White's king can't castle any more. Uh-oh!"),
    (var(bking="double"), KWIN, "Two tall windows", "Upstairs middle: Black's king can castle both ways."),
    (var(bking="single"), KWIN, "One tall window", "Black's king can castle one way, or already castled."),
    (var(bking="boarded"), KWIN, "Boarded window", "Black's king can't castle any more."),
    (var(garage="K"), (HX1 - 30, GROUND - 170, 210, 200), "Garage", "White castled. On the right = short castle, on the left = long castle."),
    (var(chimney="K"), (HX1 - 190, BODY_TOP - 200, 230, 210), "Chimney", "Black castled. On the right = short castle, on the left = long castle."),
    (var(porch=True), (SLOT_X[3] - 100, MID_FLOOR - 10, 200, 150), "Porch + columns", "White's two rooks can see each other (connected)."),
    (var(railing=True), (HX0 - 10, MID_FLOOR - 90, 220, 110), "Balcony railing", "Black's two rooks can see each other (connected)."),
    (var(steps=2), (SLOT_X[3] - 80, GROUND - 100, 160, 140), "Front steps", "White pushed a middle pawn (d or e). One step for each."),
    (var(boxes=1), (SLOT_X[1] - 55, UF_Y - 45, 110, 110), "Flower box", "Black pushed a middle pawn (d or e). One box for each."),
    (var(path=True), (SLOT_X[3] - 90, GROUND - 40, 180, 140), "Garden path", "Some pawns were captured: the game has opened up."),
    (var(diff=2), (0, 230, 170, 280), "White flag", "White is ahead. Each dot = one pawn's worth more."),
    (var(diff=-3), (0, 230, 170, 280), "Dark flag", "Black is ahead. Each dot = one pawn's worth more."),
    (var(), (0, 230, 170, 280), "Empty flagpole", "Nobody is ahead. Same stuff on both sides."),
    (var(night=False), (W - 220, 70, 220, 160), "Sun", "It's White's turn to move."),
    (var(night=True), (W - 220, 70, 220, 160), "Moon (lights on)", "It's Black's turn to move."),
]

ROOFS = [("gable", "Pointy roof = 1.e4"), ("castle", "Hip roof = 1.d4"), ("mansard", "Barn roof = 1.c4"),
         ("dome", "Flat roof = 1.Nf3"), ("flat", "Slanted = no move yet")]

FAMILIES = [(OP.YELLOW, "Sicilian"), (OP.RED, "Italian"), (OP.ORANGE, "Ruy Lopez"), (OP.SALMON, "Open Game"),
            (OP.PURPLE, "French"), (OP.PINK, "Caro-Kann"), (OP.CREAM, "Other 1.e4"), (OP.BLUE, "Queen's Gambit Declined"),
            (OP.SKY, "Queen's Gambit Accepted"), (OP.TEAL, "Slav"), (OP.GREEN, "Indian Defences"), (OP.GREY, "Other 1.d4"),
            (OP.BROWN, "English / Reti"), (OP.WHITE, "Starting position"), (OP.UNKNOWN_WALL, "Unknown")]


def legend_svg():
    from real_house import SIDING
    LW = 1500
    s = [f'<text x="40" y="60" font-size="40" font-weight="bold" {F}>Chess Houses: what everything means</text>',
         f'<text x="40" y="96" font-size="20" fill="#333" {F}>Each thing on the house means one thing, and it is always in the same place.</text>']
    # layout diagram
    full = var(white={"Nb": "out", "Bc": "out", "Q": "out"}, black={"Ng": "out", "Bf": "out"}, steps=1, boxes=1)
    s.append(f'<svg x="30" y="120" width="700" height="381" viewBox="0 96 {W} {H-96}">{render_features(full, label=False)}</svg>')
    sc = 700 / W
    names = ["knight", "bishop", "queen", "king", "bishop", "knight"]
    tx = 760
    lines = [("Upstairs = Black's pieces.", True), ("Downstairs = White's pieces.", True), ("", False),
             ("Each floor has 6 spots. Left to right they are:", False),
             ("knight, bishop, queen, king, bishop, knight", True),
             ("(the same order the pieces start in on the board).", False), ("", False),
             ("The house's colour and wall pattern tell you the", False),
             ("opening family. The roof tells you White's first", False),
             ("move. The trim colour (window frames, door,", False),
             ("gutter) tells you which version of the opening.", False)]
    for i, (t, b) in enumerate(lines):
        fw = 'font-weight="bold"' if b else ""
        s.append(f'<text x="{tx}" y="{180+i*30}" font-size="20" {fw} {F}>{t}</text>')
    # cards
    y0 = 530
    for i, (f, region, title, body) in enumerate(CARDS):
        c, r = i % 4, i // 4
        s.append(card(f, region, title, body, 30 + c * 372, y0 + r * 150))
    y = y0 + ((len(CARDS) + 3) // 4) * 150 + 30
    # roofs
    s.append(f'<text x="40" y="{y}" font-size="28" font-weight="bold" {F}>Roof = White\'s first move</text>')
    for i, (st, t) in enumerate(ROOFS):
        f = var(roof=st, wall=OP.WHITE, trim="#666666", siding="clapboard")
        s.append(crop(f, HX0 - 60, BODY_TOP - 200, HX1 - HX0 + 120, 240, 30 + i * 285, y + 20, 270, 130))
        s.append(f'<text x="{165 + i*285}" y="{y+176}" font-size="18" text-anchor="middle" {F}>{t}</text>')
    y += 230
    s.append(f'<text x="40" y="{y}" font-size="28" font-weight="bold" {F}>Wall colour + pattern = opening family</text>')
    allgone = {k: "gone" for k in ("Nb", "Bc", "Q", "Bf", "Ng")}
    for i, (col, nm) in enumerate(FAMILIES):
        c, r = i % 3, i // 3
        x, yy = 30 + c * 480, y + 20 + r * 92
        f = var(wall=col, siding=SIDING[col], black=allgone, bking="single")
        s.append(crop(f, HX0 + 4, UF_Y - 40, 140, 80, x, yy, 120, 76))
        s.append(f'<text x="{x+134}" y="{yy+34}" font-size="19" font-weight="bold" {F}>{nm}</text>'
                 f'<text x="{x+134}" y="{yy+58}" font-size="15" fill="#555" {F}>{SIDING[col]} walls</text>')
    y += 20 + ((len(FAMILIES) + 2) // 3) * 92 + 20
    return svg_doc(f'<rect width="{LW}" height="{y}" fill="#FFFFFF"/>' + "".join(s), LW, y)
