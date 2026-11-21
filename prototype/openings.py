"""Opening families -> house "family look" (Layer 1).

Each entry: (moves in SAN, name, ECO, wall colour, trim colour).
Longer (more specific) lines inherit the family wall colour and change the
trim (shutters / door frame / roof edge) so siblings look related.
Detection is done by *position* (EPD), so transpositions are recognised.
"""
import chess

# family wall colours
YELLOW = "#F6C945"   # Sicilian
RED = "#D9614C"      # Italian
ORANGE = "#F09A3E"   # Ruy Lopez
SALMON = "#F2A28F"   # other 1.e4 e5
PURPLE = "#A58BD6"   # French
PINK = "#F3A6C8"     # Caro-Kann
CREAM = "#EFE3C2"    # other 1.e4
BLUE = "#6C9BE8"     # Queen's Gambit Declined
SKY = "#9CCBF0"      # Queen's Gambit Accepted
TEAL = "#5CC2B0"     # Slav
GREEN = "#6DBF6A"    # Indian defences
GREY = "#B9C2CF"     # other 1.d4
BROWN = "#B98A62"    # English / flank
WHITE = "#E9E4D8"    # start position
UNKNOWN_WALL = "#CFCAC0"  # unknown

OPENINGS = [
    ("", "Starting Position", "A00", WHITE, "#888888"),
    # --- 1.e4 ---------------------------------------------------------
    ("e4", "King's Pawn Opening", "B00", CREAM, "#9C7A3C"),
    ("e4 c5", "Sicilian Defence", "B20", YELLOW, "#8A5A00"),
    ("e4 c5 Nf3", "Sicilian Defence", "B27", YELLOW, "#8A5A00"),
    ("e4 c5 Nf3 d6", "Sicilian Defence", "B50", YELLOW, "#8A5A00"),
    ("e4 c5 Nf3 d6 d4 cxd4", "Sicilian, Open", "B53", YELLOW, "#2E7D32"),
    ("e4 c5 Nf3 d6 d4 cxd4 Nxd4", "Sicilian, Open", "B53", YELLOW, "#2E7D32"),
    ("e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6", "Sicilian, Open", "B54", YELLOW, "#2E7D32"),
    ("e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3", "Sicilian, Open", "B56", YELLOW, "#2E7D32"),
    ("e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6", "Sicilian, Najdorf", "B90", YELLOW, "#1565C0"),
    ("e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6", "Sicilian, Dragon", "B70", YELLOW, "#C62828"),
    ("e4 c5 Nf3 Nc6", "Sicilian Defence", "B30", YELLOW, "#8A5A00"),
    ("e4 c5 Nf3 e6", "Sicilian Defence", "B40", YELLOW, "#8A5A00"),
    ("e4 e5", "Open Game", "C20", SALMON, "#8E3B2E"),
    ("e4 e5 Nf3", "Open Game", "C40", SALMON, "#8E3B2E"),
    ("e4 e5 Nf3 Nc6", "Open Game", "C44", SALMON, "#8E3B2E"),
    ("e4 e5 Nf3 Nc6 Bc4", "Italian Game", "C50", RED, "#F5E6C8"),
    ("e4 e5 Nf3 Nc6 Bc4 Bc5", "Italian, Giuoco Piano", "C50", RED, "#2E7D32"),
    ("e4 e5 Nf3 Nc6 Bc4 Nf6", "Italian, Two Knights", "C55", RED, "#1565C0"),
    ("e4 e5 Nf3 Nc6 Bb5", "Ruy Lopez", "C60", ORANGE, "#5D2E0C"),
    ("e4 e5 Nf3 Nc6 Bb5 a6", "Ruy Lopez, Morphy", "C70", ORANGE, "#1565C0"),
    ("e4 e6", "French Defence", "C00", PURPLE, "#3E2A6B"),
    ("e4 e6 d4 d5", "French Defence", "C01", PURPLE, "#3E2A6B"),
    ("e4 c6", "Caro-Kann Defence", "B10", PINK, "#7A2350"),
    ("e4 c6 d4 d5", "Caro-Kann Defence", "B12", PINK, "#7A2350"),
    # --- 1.d4 ---------------------------------------------------------
    ("d4", "Queen's Pawn Opening", "A40", GREY, "#3B4A5E"),
    ("d4 d5", "Queen's Pawn Game", "D00", GREY, "#3B4A5E"),
    ("d4 d5 c4", "Queen's Gambit", "D06", BLUE, "#F5E6C8"),
    ("d4 d5 c4 e6", "Queen's Gambit Declined", "D30", BLUE, "#0D2C6B"),
    ("d4 d5 c4 e6 Nc3", "Queen's Gambit Declined", "D31", BLUE, "#0D2C6B"),
    ("d4 d5 c4 e6 Nc3 Nf6", "QGD, Three Knights", "D35", BLUE, "#C62828"),
    ("d4 d5 c4 dxc4", "Queen's Gambit Accepted", "D20", SKY, "#0D2C6B"),
    ("d4 d5 c4 c6", "Slav Defence", "D10", TEAL, "#0B4F45"),
    ("d4 Nf6", "Indian Defence", "A45", GREEN, "#1B5E20"),
    ("d4 Nf6 c4 g6", "King's Indian Defence", "E60", GREEN, "#C62828"),
    ("d4 Nf6 c4 e6", "Indian Defence", "E00", GREEN, "#1565C0"),
    # --- flank --------------------------------------------------------
    ("c4", "English Opening", "A10", BROWN, "#4E2E12"),
    ("Nf3", "Reti Opening", "A04", BROWN, "#1B5E20"),
]

ROOF_BY_FIRST_MOVE = {"e4": "gable", "d4": "castle", "c4": "mansard", "Nf3": "dome"}


def _build_index():
    idx = {}
    for moves, name, eco, wall, trim in OPENINGS:
        b = chess.Board()
        first = None
        for san in moves.split():
            if first is None:
                first = san
            b.push_san(san)
        roof = ROOF_BY_FIRST_MOVE.get(first, "flat") if first else "flat"
        idx[b.epd()] = dict(name=name, eco=eco, wall=wall, trim=trim, roof=roof,
                            plies=len(moves.split()))
    return idx


INDEX = _build_index()
UNKNOWN = dict(name="Unknown Opening", eco="???", wall=UNKNOWN_WALL, trim="#555555",
               roof="flat", plies=0)


def classify(boards):
    """Return the most recent known opening along a sequence of boards
    (the house keeps its family look after the book runs out)."""
    found = UNKNOWN
    for b in boards:
        hit = INDEX.get(b.epd())
        if hit:
            found = hit
    return found


def _pawn_skeleton(board):
    return (board.pieces_mask(chess.PAWN, chess.WHITE), board.pieces_mask(chess.PAWN, chess.BLACK))


_SKELETONS = []
for _epd, _op in INDEX.items():
    _SKELETONS.append((_pawn_skeleton(chess.Board(_epd + " 0 1")), _op))


def classify_by_resemblance(board, max_diff=4):
    """FEN-only fallback: no exact book hit, so pick the book opening whose
    pawn skeleton (the 'bricks') is most similar. This is the family-resemblance
    rule: same bricks -> same family look, even after many moves."""
    exact = INDEX.get(board.epd())
    if exact:
        return exact
    w, b = _pawn_skeleton(board)
    best, best_d = None, 99
    for (sw, sb), op in _SKELETONS:
        d = bin(w ^ sw).count("1") + bin(b ^ sb).count("1")
        if d < best_d or (d == best_d and op["plies"] > best["plies"]):
            best, best_d = op, d
    if best is not None and best_d <= max_diff and best["plies"] > 0:
        guess = dict(best)
        guess["name"] = "~ " + best["name"] + " family"
        return guess
    return UNKNOWN
