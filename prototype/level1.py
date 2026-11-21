#!/usr/bin/env python3
"""Chess Houses, LEVEL 1: one opening = one house.

No position encoding at all. Each main opening is its own house type with a
distinct silhouette, main colour and 1-2 signature features, so kids learn
"the Sicilian is THIS house, the French is THAT house" by sight.

Usage:
  python level1.py --list
  python level1.py --opening sicilian -o sicilian.svg [--png] [--no-label]
  python level1.py --all                       # every house + quiz + overview + flashcards
  python level1.py --all -o ../examples/level1 # same, with an explicit output directory
"""
import argparse
import math
import os

W, H = 600, 460
GROUND = 390
INK = "#2B2B2B"
GLASS = "#BFE3F5"
FONT = 'font-family="DejaVu Sans, sans-serif"'


# ------------------------------------------------------------------ helpers
def R(x, y, w, h, fill, rx=0, sw=3, stroke=INK, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def P(d, fill, sw=3, stroke=INK, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'


def C(cx, cy, r, fill, sw=3, stroke=INK):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def L(x1, y1, x2, y2, col=INK, sw=3):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>'


def win(x, y, w, h, frame="#FFFFFF", glass=GLASS, cross=True, sill=True):
    s = R(x - 4, y - 4, w + 8, h + 8, frame, sw=2.5) + R(x, y, w, h, glass, sw=1.5)
    if cross:
        s += L(x + w / 2, y, x + w / 2, y + h, frame, 3) + L(x, y + h / 2, x + w, y + h / 2, frame, 3)
    if sill:
        s += R(x - 8, y + h + 3, w + 16, 6, frame, sw=2)
    return s


def arch_d(x, y, w, h):
    """Path for a round-top arch, top-left (x, y)."""
    r = w / 2
    return f"M{x},{y+h} L{x},{y+r} A{r},{r} 0 0 1 {x+w},{y+r} L{x+w},{y+h} Z"


def arch_win(x, y, w, h, frame="#FFFFFF", glass=GLASS):
    return (P(arch_d(x - 4, y - 4, w + 8, h + 8), frame, sw=2.5) + P(arch_d(x, y, w, h), glass, sw=1.5)
            + L(x + w / 2, y, x + w / 2, y + h, frame, 3))


def shutters(x, y, w, h, col):
    sw_ = w * 0.45
    return R(x - sw_ - 6, y - 2, sw_, h + 4, col, sw=2) + R(x + w + 6, y - 2, sw_, h + 4, col, sw=2)


def door(x, y, w, h, col, arch=False, double=False, knob="#E8C547"):
    s = P(arch_d(x, y, w, h), col) if arch else R(x, y, w, h, col)
    if double:
        s += L(x + w / 2, y + (w / 2 if arch else 0), x + w / 2, y + h, INK, 2.5)
        s += C(x + w / 2 - 6, y + h * 0.6, 3, knob, 1.5) + C(x + w / 2 + 6, y + h * 0.6, 3, knob, 1.5)
    else:
        s += C(x + w - 9, y + h * 0.58, 3.5, knob, 1.5)
    return s


def tree(cx, base, h, col="#4F9A48", trunk="#7A4E2D", r=None):
    r = r or h * 0.32
    return R(cx - 6, base - h * 0.45, 12, h * 0.45, trunk, sw=2) + C(cx, base - h * 0.62, r, col, 2.5)


def cypress(cx, base, h):
    return (R(cx - 4, base - 14, 8, 14, "#6B4423", sw=2)
            + P(f"M{cx},{base-h} C{cx+22},{base-h*0.6} {cx+20},{base-20} {cx},{base-12} "
                f"C{cx-20},{base-20} {cx-22},{base-h*0.6} {cx},{base-h} Z", "#2F5D3A", 2.5))


def bush(cx, base, col="#5DAA52"):
    return C(cx - 14, base - 10, 14, col, 2) + C(cx + 14, base - 10, 14, col, 2) + C(cx, base - 20, 16, col, 2)


# ------------------------------------------------------------------ houses
def sicilian():
    """Mediterranean farmhouse (masseria): wide, low, yellow, outside stone staircase."""
    Y, Rf, Bl = "#F5CF3F", "#C8553D", "#2F6DB5"
    s = []
    # side wing with roof terrace
    s.append(R(430, 300, 110, 90, Y))
    s.append(R(426, 292, 118, 10, "#E9E2D0", sw=2.5))
    for x in range(432, 542, 12):
        s.append(L(x, 292, x, 278, INK, 2))
    s.append(L(428, 278, 542, 278, INK, 3))
    s.append(win(462, 322, 40, 40, "#FFFFFF") + shutters(462, 322, 40, 40, Bl))
    # main block
    s.append(R(110, 220, 330, 170, Y))
    roof = "M95,222 L150,182 L400,182 L455,222 Z"
    s.append(P(roof, Rf))
    s.append(f'<defs><clipPath id="sicroof"><path d="{roof}"/></clipPath></defs>')
    for x in range(100, 460, 14):                                   # roof tiles
        s.append(f'<line x1="{x}" y1="222" x2="{x + (x-275)*0.25}" y2="182" stroke="#A8432F" stroke-width="2" clip-path="url(#sicroof)"/>')
    s.append(P(roof, "none"))
    for x in (150, 330):
        s.append(win(x, 246, 40, 44) + shutters(x, 246, 40, 44, Bl))
    s.append(door(235, 232, 50, 66, Bl, arch=True))                 # upper door
    s.append(door(150, 316, 56, 74, Bl, arch=True, double=True))   # ground door
    # signature: outside stone staircase to the upper door
    st = "#E9E2D0"
    # landing under the upper door, then 7 steps down to the right
    d = "M220,298 L292,298"
    x, y = 292, 298
    for i in range(7):
        x += 0; d += f" L{x},{y+13} L{x+13},{y+13}"; x += 13; y += 13
    d += f" L{x},390 L220,390 Z"
    s.append(P(d, st))
    s.append(R(214, 294, 84, 8, st, sw=2.5))
    s.append(L(296, 286, 296 + 7 * 13, 286 + 7 * 13, INK, 3))      # handrail
    for k in range(8):
        s.append(L(296 + k * 13, 286 + k * 13, 296 + k * 13, 298 + k * 13, INK, 2))
    # lemon tree in a pot
    s.append(R(500, 362, 34, 28, "#C8553D", sw=2.5) + R(504, 330, 6, 34, "#7A4E2D", sw=2)
             + C(510, 318, 22, "#4F9A48", 2.5))
    for dx, dy in ((-8, -6), (6, -12), (10, 4), (-4, 8)):
        s.append(C(510 + dx, 318 + dy, 4.5, "#FFE14D", 1.5))
    return "".join(s)


def french():
    """Parisian townhouse: tall, narrow, blue-grey mansard roof, iron balconies."""
    wall, roof, iron = "#D7DDEB", "#34405A", "#1E1E1E"
    s = []
    s.append(R(235, 40, 22, 56, "#B85C42") + R(343, 40, 22, 56, "#B85C42"))   # chimney stacks
    for x in (239, 247, 347, 355):
        s.append(R(x, 32, 8, 10, "#D9774F", sw=1.5))
    # mansard roof
    s.append(P("M205,150 L222,92 L378,92 L395,150 Z", roof))
    s.append(R(218, 84, 164, 10, "#4A5878", sw=2.5))
    for cx in (262, 338):                                           # round dormers
        s.append(C(cx, 122, 18, "#E9EDF5", 3) + C(cx, 122, 12, GLASS, 1.5) + L(cx - 12, 122, cx + 12, 122, "#E9EDF5", 2.5))
    s.append(R(215, 150, 170, 240, wall))
    s.append(R(209, 146, 182, 10, "#FFFFFF", sw=2.5))               # cornice
    for y in (168, 238):                                            # 2 floors of French windows
        for x in (238, 322):
            s.append(win(x, y, 40, 54, "#FFFFFF", sill=False))
        s.append(R(222, y + 52, 156, 6, iron, sw=1.5))              # iron balcony
        for x in range(224, 378, 8):
            s.append(L(x, y + 58, x, y + 72, iron, 2))
        s.append(L(222, y + 72, 378, y + 72, iron, 3))
        for cx in (258, 342):
            s.append(C(cx - 10, y + 50, 5, "#E84855", 1) + C(cx + 10, y + 50, 5, "#E84855", 1))
    s.append(R(215, 312, 170, 6, "#FFFFFF", sw=2))
    s.append(door(268, 322, 64, 68, "#2F4F8A", arch=True, double=True))
    s.append(win(232, 330, 24, 40, "#FFFFFF", cross=False) + win(344, 330, 24, 40, "#FFFFFF", cross=False))
    # street lamp
    s.append(R(447, 250, 6, 140, iron, sw=1.5) + P("M436,250 L464,250 L458,228 L442,228 Z", "#FFE9A3")
             + R(440, 222, 20, 8, iron, sw=1.5))
    return "".join(s)


def caro_kann():
    """Cape Cod cottage: low, pink, two dormers, central chimney, picket fence."""
    wall, roof = "#F4A3B5", "#6E6E7A"
    s = []
    s.append(R(285, 170, 30, 60, "#B85C42"))                        # central chimney
    s.append(P("M130,290 L205,212 L395,212 L470,290 Z", roof))
    for x in range(140, 470, 22):
        pass
    for y in range(225, 290, 14):
        s.append(L(140, y, 460, y, "#5C5C66", 2))
    s.append(P("M130,290 L205,212 L395,212 L470,290 Z", "none"))
    for cx in (225, 375):                                           # two dormers
        s.append(R(cx - 30, 228, 60, 50, "#FFFFFF") + P(f"M{cx-38},{230} L{cx},{200} L{cx+38},{230} Z", roof))
        s.append(win(cx - 16, 240, 32, 30, "#FFFFFF"))
    s.append(R(140, 290, 320, 100, wall))
    s.append(R(134, 286, 332, 8, "#FFFFFF", sw=2.5))
    for x in (170, 380):
        s.append(win(x, 312, 50, 48) + shutters(x, 312, 50, 48, "#3D5A80"))
    s.append(door(272, 306, 56, 84, "#C0392B"))
    s.append(R(262, 298, 76, 8, "#FFFFFF", sw=2))
    # signature: white picket fence
    for x in list(range(70, 250, 16)) + list(range(350, 532, 16)):
        s.append(P(f"M{x},400 L{x},372 L{x+5},364 L{x+10},372 L{x+10},400 Z", "#FFFFFF", 2))
    s.append(R(66, 378, 184, 6, "#FFFFFF", sw=2) + R(346, 378, 190, 6, "#FFFFFF", sw=2))
    return "".join(s)


def italian():
    """Tuscan villa: terracotta, square tower with belfry, arched loggia, cypress trees."""
    wall, roof = "#D9784A", "#9E3B26"
    s = []
    # tower
    s.append(R(110, 130, 80, 260, wall))
    s.append(P("M100,132 L150,100 L200,132 Z", roof))
    s.append(P(arch_d(132, 146, 36, 46), "#5A2E1E", sw=2.5))
    s.append(C(150, 176, 8, "#E8C547", 2))
    s.append(win(134, 236, 32, 40, "#F5E6C8"))
    # main block
    s.append(R(190, 220, 230, 170, wall))
    s.append(P("M178,222 L215,192 L395,192 L432,222 Z", roof))
    for x in (210, 290, 370):
        s.append(arch_win(x, 236, 30, 46, "#F5E6C8") + shutters(x, 236, 30, 46, "#5E7B4C"))
    # signature: arched loggia (3 open arches with columns)
    s.append(R(190, 304, 230, 86, shade_hex(wall, 0.92)))
    for i in range(3):
        x = 204 + i * 72
        s.append(P(arch_d(x, 312, 58, 78), "#5A2E1E", sw=2.5))
    for i in range(4):
        x = 197 + i * 72
        s.append(R(x, 316, 8, 74, "#F5E6C8", sw=2))
    s.append(R(186, 300, 238, 8, "#F5E6C8", sw=2.5))
    s.append(cypress(460, 390, 190) + cypress(510, 390, 150))
    s.append(R(70, 362, 30, 28, "#C8553D", sw=2.5) + C(85, 352, 15, "#6DA34D", 2))
    return "".join(s)


def ruy_lopez():
    """Spanish hacienda: long, low, sandy adobe, curvy bell gable, big wooden doors."""
    wall, tile, wood = "#EBCB9B", "#C8553D", "#7A4A2A"
    s = []
    # signature: curvy mission bell gable
    g = ("M230,300 L230,250 C230,230 250,232 252,214 C254,196 270,196 272,182 "
         "C276,160 324,160 328,182 C330,196 346,196 348,214 C350,232 370,230 370,250 L370,300 Z")
    s.append(P(g, wall))
    s.append(P(arch_d(285, 186, 30, 38), "#4A3424", sw=2.5))
    s.append(P(f"M292,214 Q300,196 308,214 Z", "#E8C547", 2))
    s.append(C(300, 154, 6, "#E8C547", 2) + L(300, 148, 300, 138, INK, 3))
    # long low walls + tile roofs either side
    s.append(R(90, 300, 420, 90, wall))
    for x0, x1 in ((84, 232), (368, 516)):
        s.append(P(f"M{x0},{304} L{x0+6},{284} L{x1-6},{284} L{x1},{304} Z", tile))
        for x in range(x0 + 10, x1 - 14, 12):
            s.append(f'<path d="M{x},{304} q6,-10 12,0" fill="none" stroke="#9E3B26" stroke-width="2"/>')
    s.append(R(230, 296, 140, 8, "#D8B07A", sw=2.5))
    # big arched wooden double door
    s.append(door(262, 302, 76, 88, wood, arch=True, double=True))
    for y in (330, 352, 374):
        s.append(L(266, y, 334, y, "#5A3420", 2))
    # windows with iron grilles
    for x in (128, 186, 418, 476):
        s.append(R(x - 4, 322, 34, 44, wood, sw=2.5) + R(x, 326, 26, 36, "#3A3A4A", sw=1.5))
        for k in range(1, 4):
            s.append(L(x + k * 6.5, 326, x + k * 6.5, 362, "#1E1E1E", 2))
    for x in (100, 500):                                            # wooden roof beams (vigas)
        pass
    # agave in pot
    s.append(R(536, 362, 32, 28, "#C8553D", sw=2.5))
    for a in (-60, -30, 0, 30, 60):
        rx = 552 + 24 * math.sin(math.radians(a))
        ry = 362 - 30 * math.cos(math.radians(a))
        s.append(P(f"M548,362 L{rx},{ry} L556,362 Z", "#6FA37A", 2))
    return "".join(s)


def scandinavian():
    """Nordic cabin: Falu red, white trim, grass roof, birch tree."""
    red, white = "#A8322B", "#FFFFFF"
    s = []
    s.append(R(205, 248, 190, 142, red))
    for x in range(216, 394, 14):                                   # vertical boards
        s.append(L(x, 250, x, 388, "#8E2823", 2))
    s.append(R(205, 248, 10, 142, white, sw=2) + R(385, 248, 10, 142, white, sw=2))   # corner boards
    # signature: steep roof with a grass (sod) top
    s.append(P("M180,252 L300,150 L420,252 Z", "#5B3A29"))
    s.append(P("M168,258 L300,140 L432,258 L404,258 L300,170 L196,258 Z", "#5FAF4B", 2.5))
    for k in range(13):
        t = k / 12
        for sgn in (-1, 1):
            x = 300 + sgn * (6 + t * 124); y = 144 + t * 112
            s.append(P(f"M{x-6},{y} l3,-11 l3,8 l3,-12 l3,12 Z", "#4C9A3C", 1.2))

    s.append(P("M300,162 L408,254 L192,254 Z", red))
    s.append(win(282, 196, 36, 36, white))
    s.append(win(230, 290, 44, 44, white) + win(326, 290, 44, 44, white))
    s.append(R(276, 314, 48, 76, white, sw=2.5) + door(282, 320, 36, 70, "#2B5F8A"))
    # birch tree
    s.append(R(474, 230, 12, 160, "#F3F3F3", sw=2))
    for y in (250, 280, 316, 350):
        s.append(L(476, y, 484, y, INK, 3))
    s.append(C(480, 222, 34, "#8CC63F", 2.5) + C(458, 246, 20, "#8CC63F", 2.5) + C(504, 248, 20, "#8CC63F", 2.5))
    return "".join(s)


def queens_gambit():
    """Royal castle: grey stone, two towers with purple cone roofs and flags."""
    stone, purple = "#A7AEBB", "#6A3FA0"
    s = []
    def battlements(x0, x1, y, h=14, w=16):
        out = []
        x = x0
        while x + w <= x1 + 1:
            out.append(R(x, y - h, w, h, stone, sw=2.5))
            x += 2 * w
        return "".join(out)
    s.append(battlements(206, 394, 230))
    s.append(R(200, 230, 200, 160, stone))
    for x in (130, 410):                                            # towers
        s.append(R(x, 170, 60, 220, stone))
        s.append(P(f"M{x-8},{172} L{x+30},{88} L{x+68},{172} Z", purple))
        s.append(L(x + 30, 88, x + 30, 58, INK, 3) + P(f"M{x+30},{58} L{x+58},{66} L{x+30},{74} Z", "#F2C14E", 2))
        s.append(arch_win(x + 18, 200, 24, 36, "#E0E0E0") + arch_win(x + 18, 280, 24, 36, "#E0E0E0"))
    for y in range(244, 390, 18):                                   # stone lines
        off = 0 if (y // 18) % 2 else 20
        s.append(L(202, y, 398, y, "#8E95A3", 1.5))
        for x in range(212 + off, 398, 40):
            s.append(L(x, y, x, y + 18 if y + 18 < 390 else 390, "#8E95A3", 1.5))
    s.append(R(200, 230, 200, 160, "none"))
    # crown banner
    s.append(P("M276,244 L324,244 L324,300 L300,288 L276,300 Z", purple))
    s.append(P("M286,276 L286,262 L293,270 L300,258 L307,270 L314,262 L314,276 Z", "#F2C14E", 2))
    # gate
    s.append(P(arch_d(264, 316, 72, 74), "#6B4423"))
    for x in range(274, 334, 12):
        s.append(L(x, 322 if abs(x - 300) < 24 else 340, x, 390, "#3A3A3A", 2.5))
    for y in (346, 366):
        s.append(L(266, y, 334, y, "#3A3A3A", 2.5))
    s.append(arch_win(222, 270, 26, 40, "#E0E0E0") + arch_win(352, 270, 26, 40, "#E0E0E0"))
    return "".join(s)


def london():
    """London Georgian terrace: dark brick, white sash windows, black door, red phone box."""
    brick = "#7B4732"
    s = []
    for x in (186, 396):                                            # chimney stacks with pots
        s.append(R(x, 128, 34, 46, "#6A3B28"))
        for k in range(3):
            s.append(R(x + 3 + k * 10, 116, 8, 14, "#D9774F", sw=1.5))
    s.append(R(170, 170, 260, 220, brick))
    for y in range(180, 390, 10):
        s.append(L(172, y, 428, y, "#6A3B28", 1))
    s.append(R(164, 166, 272, 14, "#F2F2F2", sw=2.5))               # parapet cornice
    for y in (196, 260):
        for x in (196, 280, 364):
            s.append(win(x, y, 40, 48, "#FFFFFF"))
    s.append(win(196, 324, 40, 48, "#FFFFFF") + win(364, 324, 40, 48, "#FFFFFF"))
    # signature: black door with fanlight + white columns
    s.append(P("M272,322 A28,28 0 0 1 328,322 Z", GLASS, 2.5))
    for k in range(5):
        a = math.radians(180 + k * 45)
        s.append(L(300, 322, 300 + 26 * math.cos(a), 322 + 26 * math.sin(a), "#FFFFFF", 2))
    s.append(R(276, 324, 48, 66, "#1A1A1A") + C(300, 356, 3.5, "#E8C547", 1.5))
    s.append(R(262, 300, 76, 8, "#F2F2F2", sw=2))
    for x in (262, 330):
        s.append(R(x, 308, 8, 82, "#F2F2F2", sw=2))
    for x in range(176, 256, 9):                                    # iron railings
        s.append(L(x, 390, x, 372, "#1A1A1A", 2))
    for x in range(346, 428, 9):
        s.append(L(x, 390, x, 372, "#1A1A1A", 2))
    # red phone box
    s.append(R(462, 270, 52, 120, "#D62828", rx=3) + P("M458,272 Q488,252 518,272 Z", "#D62828"))
    s.append(R(468, 282, 40, 12, "#1A1A1A", sw=1.5))
    for y in (302, 324, 346):
        s.append(R(470, y, 36, 18, GLASS, sw=1.5))
    return "".join(s)


def kings_indian():
    """Palace: white marble, big teal onion dome, two minarets, pointed arches."""
    marble, teal, gold = "#F7F2E6", "#1F9A8A", "#E8B83A"
    s = []
    def onion(cx, base, w, h, col):
        return P(f"M{cx-w/2},{base} C{cx-w/2-w*0.25},{base-h*0.45} {cx-w*0.1},{base-h*0.75} {cx},{base-h} "
                 f"C{cx+w*0.1},{base-h*0.75} {cx+w/2+w*0.25},{base-h*0.45} {cx+w/2},{base} Z", col)
    for x in (128, 450):                                            # minarets
        s.append(R(x, 178, 22, 212, marble))
        s.append(R(x - 6, 220, 34, 8, marble, sw=2.5) + R(x - 6, 290, 34, 8, marble, sw=2.5))
        s.append(onion(x + 11, 180, 30, 44, teal) + L(x + 11, 136, x + 11, 124, gold, 3))
    s.append(R(150, 270, 300, 120, marble))
    s.append(R(244, 220, 112, 52, marble))                          # drum
    s.append(onion(300, 222, 116, 120, teal))
    s.append(L(300, 102, 300, 80, gold, 4) + C(300, 78, 5, gold, 2))
    def ogee(x, y, w, h, fill):
        return P(f"M{x},{y+h} L{x},{y+h*0.4} Q{x},{y+h*0.18} {x+w/2},{y} Q{x+w},{y+h*0.18} {x+w},{y+h*0.4} L{x+w},{y+h} Z", fill, 2.5)
    for x in (176, 236, 334, 394):
        s.append(ogee(x, 300, 30, 54, "#2E4A62"))
    s.append(ogee(270, 290, 60, 100, "#1F6E8C"))
    s.append(R(146, 264, 308, 8, gold, sw=2))
    for x in (262, 290, 318):
        s.append(ogee(x, 232, 20, 30, "#2E4A62"))
    # reflecting pool
    s.append(f'<ellipse cx="300" cy="420" rx="110" ry="14" fill="#8FD3E8" stroke="{INK}" stroke-width="2"/>')
    return "".join(s)


def english():
    """Tudor cottage: cream walls with black timber beams, steep gables, tall chimney."""
    cream, beam, roof = "#F3E7C9", "#2B211C", "#7A5236"
    s = []
    s.append(R(370, 120, 30, 140, "#A6503A"))                       # tall brick chimney
    s.append(R(366, 112, 38, 12, "#8E4231", sw=2.5))
    s.append(P("M300,252 L340,190 L455,190 L470,252 Z", roof))      # side roof
    s.append(R(170, 250, 270, 140, cream))
    # signature: steep front gable with half-timbering
    s.append(P("M150,252 L240,126 L330,252 Z", roof))
    s.append(P("M170,252 L240,154 L310,252 Z", cream))
    s.append(L(240, 154, 240, 252, beam, 6) + L(205, 203, 205, 252, beam, 6) + L(275, 203, 275, 252, beam, 6)
             + L(190, 230, 290, 230, beam, 5))
    s.append(L(170, 252, 440, 252, beam, 7))
    for x in (170, 240, 310, 370, 440):
        s.append(L(x, 252, x, 390, beam, 6))
    s.append(L(170, 318, 440, 318, beam, 5))
    for x0, x1 in ((170, 240), (310, 370), (370, 440)):
        s.append(L(x0, 252, x1, 318, beam, 4))
    # diamond-pane windows
    def lattice(x, y, w, h):
        out = R(x - 4, y - 4, w + 8, h + 8, beam, sw=2) + R(x, y, w, h, "#CFE4E8", sw=1.5)
        for k in range(-h, w, 10):
            out += L(max(x, x + k), y + max(0, -k), min(x + w, x + k + h), y + min(h, h - (k + h - w) if k + h > w else h), "#6E6E6E", 1)
        return out
    s.append(lattice(186, 332, 40, 40) + lattice(386, 332, 40, 40) + lattice(386, 266, 40, 40))
    s.append(P(arch_d(254, 326, 42, 64), "#6B4423") + C(288, 362, 3.5, "#E8C547", 1.5))
    # roses
    for x in (160, 450):
        s.append(bush(x, 392, "#3E7D3A"))
        for dx, dy in ((-10, -14), (8, -20), (14, -6)):
            s.append(C(x + dx, 392 + dy, 4.5, "#E84855", 1.2))
    return "".join(s)


def modern():
    """Modern house: stacked charcoal and wood boxes, flat roofs, big glass."""
    char, wood, glass = "#3B4049", "#C68B59", "#9FD3EA"
    s = []
    s.append(R(130, 290, 260, 100, char))
    s.append(R(140, 302, 150, 78, glass, sw=2))
    for x in (190, 240):
        s.append(L(x, 302, x, 380, INK, 2))
    s.append(R(310, 310, 60, 80, "#E8E8E8", sw=2.5))                # door panel
    s.append(L(318, 350, 330, 350, INK, 3))
    # signature: cantilevered upper box
    s.append(R(220, 196, 270, 96, wood))
    for x in range(232, 490, 12):
        s.append(L(x, 198, x, 290, "#A9733F", 1.5))
    s.append(R(250, 214, 210, 60, glass, sw=2))
    s.append(L(355, 214, 355, 274, INK, 2))
    s.append(R(212, 188, 286, 10, "#E8E8E8", sw=2.5) + R(122, 282, 100, 10, "#E8E8E8", sw=2.5))
    s.append(L(470, 292, 470, 390, INK, 4))                         # steel post
    # minimal planter + tree
    s.append(R(500, 360, 60, 30, "#E8E8E8", sw=2.5) + tree(530, 362, 90, "#6DBF6A"))
    return "".join(s)


def scotch():
    """Lighthouse cottage: red and white striped lighthouse with a white keeper's cottage."""
    red, white, slate = "#D62828", "#FFFFFF", "#4B5563"
    s = []
    # keeper's cottage
    for x in (150, 310):                                            # end chimneys
        s.append(R(x, 238, 22, 50, "#BDBDBD") + R(x + 3, 230, 7, 10, "#D9774F", sw=1.5) + R(x + 12, 230, 7, 10, "#D9774F", sw=1.5))
    s.append(P("M128,312 L170,262 L310,262 L352,312 Z", slate))
    s.append(R(140, 310, 200, 80, white))
    s.append(win(166, 330, 34, 34, "#2B5F8A") + win(280, 330, 34, 34, "#2B5F8A"))
    s.append(door(226, 326, 34, 64, "#2B5F8A"))
    # signature: striped lighthouse
    tb, tt, top, bot = 112, 72, 110, 390
    cx = 420
    def xat(y):
        t = (y - top) / (bot - top)
        return (tt + (tb - tt) * t) / 2
    ys = [top + k * (bot - top) / 7 for k in range(8)]
    for k in range(7):
        y0, y1 = ys[k], ys[k + 1]
        s.append(P(f"M{cx-xat(y0)},{y0} L{cx+xat(y0)},{y0} L{cx+xat(y1)},{y1} L{cx-xat(y1)},{y1} Z",
                   red if k % 2 == 0 else white, 2.5))
    s.append(R(cx - 50, top - 10, 100, 12, "#1E1E1E", sw=2))        # gallery
    for x in range(int(cx - 46), int(cx + 48), 9):
        s.append(L(x, top - 10, x, top - 24, "#1E1E1E", 2))
    s.append(L(cx - 48, top - 24, cx + 48, top - 24, "#1E1E1E", 3))
    s.append(R(cx - 26, top - 60, 52, 50, "#FFF3B0", sw=2.5))       # lantern room
    s.append(L(cx, top - 60, cx, top - 10, INK, 2))
    s.append(P(f"M{cx-32},{top-60} Q{cx},{top-96} {cx+32},{top-60} Z", "#1E1E1E"))
    s.append(L(cx, top - 88, cx, top - 100, INK, 3))
    for k in range(5):
        s.append(R(cx - 10, top + 30 + k * 0, 0, 0, white))
    s.append(arch_win(cx - 9, 200, 18, 26, "#1E1E1E", GLASS) + door(cx - 15, 336, 30, 54, "#1E1E1E", arch=True))
    # light beams
    s.append(P(f"M{cx-26},{top-40} L{cx-120},{top-70} L{cx-120},{top-20} Z", "#FFF3B0", 0, extra='opacity="0.7"'))
    s.append(P(f"M{cx+26},{top-40} L{cx+120},{top-70} L{cx+120},{top-20} Z", "#FFF3B0", 0, extra='opacity="0.7"'))
    # rocks
    s.append(P("M470,390 Q490,360 520,372 Q545,360 560,390 Z", "#8A8F98", 2.5))
    return "".join(s)


def shade_hex(hexcol, k):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * k))) for c in (r, g, b))


# id, name, moves, house type, main colour (name, hex), signature, why, draw function
HOUSES = [
    ("sicilian", "Sicilian Defence", "1.e4 c5", "Mediterranean farmhouse", ("sunny yellow", "#F5CF3F"),
     "outside stone staircase, blue shutters, lemon tree",
     "Sicily is a sunny Mediterranean island of yellow farmhouses and lemon groves.", sicilian),
    ("french", "French Defence", "1.e4 e6", "Parisian townhouse", ("Paris blue-grey", "#D7DDEB"),
     "mansard roof with round dormers, iron balconies",
     "Tall, narrow Paris buildings with slate mansard roofs are the picture of France.", french),
    ("caro_kann", "Caro-Kann Defence", "1.e4 c6", "Cape Cod cottage", ("pink", "#F4A3B5"),
     "two roof dormers, central chimney, white picket fence",
     "A small, tidy, very solid cottage, like the Caro-Kann: safe and sturdy.", caro_kann),
    ("italian", "Italian Game", "1.e4 e5 2.Nf3 Nc6 3.Bc4", "Tuscan villa", ("terracotta", "#D9784A"),
     "square bell tower, arched loggia, cypress trees",
     "Classic Italian countryside villa with a tower, as old and classic as the opening.", italian),
    ("ruy_lopez", "Ruy Lopez (Spanish)", "1.e4 e5 2.Nf3 Nc6 3.Bb5", "Spanish hacienda", ("adobe sand", "#EBCB9B"),
     "curvy bell gable, big arched wooden doors, iron window grilles",
     "Ruy Lopez was a Spanish priest: a mission-style hacienda with a bell gable.", ruy_lopez),
    ("scandinavian", "Scandinavian Defence", "1.e4 d5", "Nordic cabin", ("Falu red", "#A8322B"),
     "grass (sod) roof, white corner trim, birch tree",
     "Red cabins with white trim and grass roofs are iconic in Sweden and Norway.", scandinavian),
    ("queens_gambit", "Queen's Gambit", "1.d4 d5 2.c4", "royal castle", ("stone grey + royal purple", "#A7AEBB"),
     "twin towers with purple cone roofs and flags, crown banner",
     "A queen lives in a castle. The Queen's Gambit is the royal, classical 1.d4 opening.", queens_gambit),
    ("london", "London System", "1.d4 + Bf4", "London Georgian terrace", ("dark brick", "#7B4732"),
     "red phone box, black door with fanlight and white columns",
     "A real London street house, complete with a red telephone box.", london),
    ("kings_indian", "King's Indian Defence", "1.d4 Nf6 2.c4 g6", "Indian palace", ("white marble + teal", "#1F9A8A"),
     "huge onion dome, two minarets, pointed arches",
     "A palace fit for an Indian king: big dome, towers, and a reflecting pool.", kings_indian),
    ("english", "English Opening", "1.c4", "Tudor cottage", ("cream + black beams", "#F3E7C9"),
     "black-and-white timber beams, steep gable, tall chimney, roses",
     "Old English villages are full of black-and-white Tudor cottages.", english),
    ("modern", "Pirc / Modern Defence", "1.e4 d6 / 1.e4 g6", "modern house", ("charcoal + wood", "#3B4049"),
     "stacked boxes, flat roofs, floor-to-ceiling glass",
     "It's called the 'Modern' Defence, so it gets a modern house.", modern),
    ("scotch", "Scotch Game", "1.e4 e5 2.Nf3 Nc6 3.d4", "lighthouse cottage", ("red and white stripes", "#D62828"),
     "tall striped lighthouse with a keeper's cottage",
     "Scotland's coast is famous for its lighthouses.", scotch),
]
BY_ID = {h[0]: h for h in HOUSES}


# ------------------------------------------------------------------ scene
def scene(house_id, label=True):
    hid, name, moves, *_rest, fn = BY_ID[house_id]
    s = [f'<rect width="{W}" height="{H}" fill="#CDEBFA"/>',
         f'<rect x="0" y="{GROUND}" width="{W}" height="{H-GROUND}" fill="#86C96F"/>',
         L(0, GROUND, W, GROUND, "#5E9E4C", 3), fn()]
    if label:
        tw = max(200, len(name) * 11 + 40)
        s.append(R(W / 2 - tw / 2, GROUND + 18, tw, 36, "#FFF8E7", rx=8, sw=2.5))
        s.append(f'<text x="{W/2}" y="{GROUND+42}" font-size="19" font-weight="bold" text-anchor="middle" {FONT} fill="{INK}">{name}</text>')
    return "\n".join(s)


def svg_doc(inner, w=W, h=H):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n{inner}\n</svg>\n'


def neighborhood(cols=4, scale=0.5):
    cw, ch = W * scale, H * scale + 46
    rows = (len(HOUSES) + cols - 1) // cols
    parts = ['<rect width="100%" height="100%" fill="#FFFFFF"/>',
             f'<text x="{cols*cw/2}" y="44" font-size="32" font-weight="bold" text-anchor="middle" {FONT}>The Opening Neighborhood</text>']
    for i, h in enumerate(HOUSES):
        x, y = (i % cols) * cw, 66 + (i // cols) * ch
        parts.append(f'<svg x="{x}" y="{y}" width="{W*scale}" height="{H*scale}" viewBox="0 0 {W} {H}">{scene(h[0], label=False)}</svg>')
        parts.append(f'<text x="{x+cw/2}" y="{y+H*scale+22}" font-size="17" font-weight="bold" text-anchor="middle" {FONT}>{h[1]}</text>'
                     f'<text x="{x+cw/2}" y="{y+H*scale+40}" font-size="13" fill="#555" text-anchor="middle" {FONT}>{h[2]}</text>')
    return svg_doc("".join(parts), cols * cw, 66 + rows * ch + 10)


def flashcards(cols=3, scale=0.42):
    pad = 16
    cw, ch = W * scale + 2 * pad, H * scale + 2 * pad + 78
    rows = (len(HOUSES) + cols - 1) // cols
    parts = ['<rect width="100%" height="100%" fill="#FFFFFF"/>',
             f'<text x="{cols*(cw+20)/2}" y="40" font-size="28" font-weight="bold" text-anchor="middle" {FONT}>Chess Houses, Level 1: flashcards</text>',
             f'<text x="{cols*(cw+20)/2}" y="64" font-size="15" fill="#555" text-anchor="middle" {FONT}>Cut out the cards. Fold the name under to play "Which opening lives here?"</text>']
    for i, h in enumerate(HOUSES):
        x, y = 10 + (i % cols) * (cw + 20), 84 + (i // cols) * (ch + 16)
        parts.append(R(x, y, cw, ch, "#FFFFFF", rx=14, sw=2, stroke="#999", extra='stroke-dasharray="6,4"'))
        parts.append(f'<svg x="{x+pad}" y="{y+pad}" width="{W*scale}" height="{H*scale}" viewBox="0 0 {W} {H}">{scene(h[0], label=False)}</svg>')
        ty = y + pad + H * scale
        parts.append(L(x + 10, ty + 10, x + cw - 10, ty + 10, "#BBBBBB", 1.5))
        parts.append(f'<text x="{x+cw/2}" y="{ty+36}" font-size="19" font-weight="bold" text-anchor="middle" {FONT}>{h[1]}</text>'
                     f'<text x="{x+cw/2}" y="{ty+56}" font-size="13" fill="#444" text-anchor="middle" {FONT}>{h[2]}</text>'
                     f'<text x="{x+cw/2}" y="{ty+73}" font-size="12" fill="#777" text-anchor="middle" {FONT}>{h[3]}</text>')
    return svg_doc("".join(parts), cols * (cw + 20), 84 + rows * (ch + 16))


def write(svg, path, png):
    with open(path, "w") as fh:
        fh.write(svg)
    if png:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=path[:-4] + ".png")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--opening", choices=list(BY_ID))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-o", "--out")
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--no-label", action="store_true")
    a = ap.parse_args()
    if a.list:
        for h in HOUSES:
            print(f"{h[0]:14s} {h[1]:24s} {h[3]}")
        return
    if a.all:
        out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "level1")
        os.makedirs(out, exist_ok=True)
        for h in HOUSES:
            write(svg_doc(scene(h[0])), os.path.join(out, f"{h[0]}.svg"), True)
            write(svg_doc(scene(h[0], label=False)), os.path.join(out, f"{h[0]}_quiz.svg"), True)
        write(neighborhood(), os.path.join(out, "neighborhood.svg"), True)
        write(flashcards(), os.path.join(out, "flashcards.svg"), True)
        print("written to", os.path.abspath(out))
        return
    write(svg_doc(scene(a.opening, not a.no_label)), a.out, a.png)


if __name__ == "__main__":
    main()
