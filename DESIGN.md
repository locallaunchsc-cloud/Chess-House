# Chess Houses: Design (draft v0.1)

> **Every chess position is a house.** Openings give the house its *family look*
> (color, roof, trim), and the exact position is written into the *facade*: which
> windows, doors, bricks and balconies are where. Same position, same house, every time.

---

## 1. Goals

1. **Recognizable at a glance (gestalt).** A kid should be able to say "that's a yellow pointy-roof house, so it's a Sicilian" before they can read notation.
2. **Exactly decodable (reversible).** A kid (or a program) who knows the rules can rebuild the real chess position from the picture.
3. **Deterministic.** Same position always gives the same house. No randomness, no artist's choices.
4. **Grows with the child.** Little kids use Layer 1 (the family look). Older kids read Layer 2 (the facade) and eventually read the board straight from the house.

## 2. The core tension: gestalt vs. reversibility

| Approach | Pros | Cons |
|---|---|---|
| **Pure gestalt.** Each opening is a hand-designed house ("Najdorf = yellow house with two windows") | Very memorable. Feels like a picture book. | Only works for a finite list of named positions. After move 10 every house is "unknown". You can't decode the position from it. |
| **Pure encoding.** The house *is* the 8×8 board drawn as a facade | Works for every position and is fully reversible | Every house has the same skeleton, so openings blur together without help |
| **Layered (chosen).** Family look from the opening, facade from the exact position | Memorable *and* exact. Kids notice that the family look stays put while details change | Needs an opening table, plus a fallback once you leave book |

We use the **layered** approach. The facade grid also turns out to be a gestalt
signal: **pawns are drawn as bricks**, so every opening's **pawn structure becomes a
recognizable brick pattern** (e.g. the Sicilian's "missing brick on c" or the QGD's
"brick staircase d5/e6"). Pawn structure is exactly what strong players use to
recognize openings, so this teaches the real skill.

## 3. The encoding

### Layer 1: Family look (which opening?)

| Chess feature | House feature | Rule |
|---|---|---|
| Opening family | **Wall color** | Sicilian = yellow, Italian = red, Ruy Lopez = orange, other 1.e4 e5 = salmon, French = purple, Caro-Kann = pink, QGD = blue, QGA = sky blue, Slav = teal, Indian defences = green, other 1.d4 = grey, English/Réti = brown, start = off-white, unknown = stone grey |
| First move | **Roof shape** | 1.e4 = pointed gable roof, 1.d4 = castle battlements, 1.c4 = mansard, 1.Nf3 = dome, start/other = flat |
| Variation within family | **Trim color** (roof edge and facade outline) | e.g. Sicilian: brown (early), green (Open Sicilian), blue (Najdorf), red (Dragon) |
| Name (optional) | **Street sign** under the house | Shows the name + ECO code. Hidden in quiz mode |

**How the opening is identified:** each named line in the opening table is replayed
and its *position* (FEN without move counters) is stored. While a game is played,
the house takes the look of the **most recent book position reached**, and keeps it
after leaving book (the house "remembers where it grew up"). Because we match
positions, not move orders, transpositions are handled automatically.

**FEN-only input (no move history):** if the position isn't in the table, we use
*family resemblance*: find the book position with the most similar pawn skeleton
(≤ 4 pawn differences). The sign then reads "~ Italian family". Otherwise the house is
stone grey ("Unknown").

### Layer 2: The facade (exact position)

The front of the house is an **8 columns × 8 floors** grid.

* **Columns a–h**, left to right (as seen from White's side).
* **Floors 1–8**, bottom to top. White "lives downstairs", Black "lives upstairs".

Each piece is a building part with a shape that hints at the piece:

| Piece | House part | Why kids remember it |
|---|---|---|
| Pawn | **Brick block** | Pawns are the building's bricks, i.e. its structure |
| Knight | **Horseshoe-arch window** | Horses wear horseshoes |
| Bishop | **Pointed (church) arch window** with a diagonal bar | A bishop's pointy hat, and the slash = moves diagonally |
| Rook | **Square tower window with battlements** | Rooks look like castle towers |
| Queen | **Round rose window with a flower balcony** | The fanciest window in the house |
| King | **Front door with a golden crown** | Everybody goes through the king's door |

**Color of the piece = lighting of the window:**
White pieces are **light glass / cream bricks** ("lights on"). Black pieces are **dark glass / dark-brown bricks** with a white frame.
An empty square is plain wall.

### Layer 3: Surroundings (the rest of the FEN)

| FEN field | House feature |
|---|---|
| Side to move | **Day (sun) = White to move, night (moon & stars) = Black to move** |
| White castling rights | **Garden fence**: left fence = O-O-O still allowed, right fence = O-O still allowed. A fence disappears when the right is lost |
| Black castling rights | **Chimneys with smoke**: left chimney = O-O-O, right chimney = O-O |
| En-passant square | **Blue puddle** in front of that column (only when an en-passant capture is actually possible) |
| Full-move number | **House number** plaque beside the front door |
| Material balance (derived) | **Flag on the roof**: bare pole = equal; white flag with red stripes = White ahead; black flag with yellow stripes = Black ahead; number of stripes = pawns' worth ahead (P=1, N/B=3, R=5, Q=9, max 9) |
| Halfmove clock | *not shown* (only matters for the 50-move rule; candidate: "grass length") |

With layers 2 and 3 the picture encodes everything in a FEN except the halfmove clock, so
**house → position is fully reversible.**

## 4. Worked examples

PNG renders live in `examples/`. `*_quiz.png` versions hide the street sign.

### 4a. Sicilian Najdorf, move by move
`1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6` (see `examples/sicilian_sequence_sheet.png`)

| Ply | Move | What changes on the house |
|---|---|---|
| 0 | start | Off-white house, flat roof, daytime. Full brick rows on floors 2 and 7, both fences, both chimneys |
| 1 | 1.e4 | Night falls (Black to move). **Roof turns into a pointed gable** (1.e4 family). Walls go cream. The cream brick climbs from e2 to e4 |
| 2 | 1…c5 | Day. **The house turns YELLOW: it's a Sicilian.** A dark brick jumps from c7 to c5, and the gap in the top brick row on column c is the Sicilian's signature |
| 3 | 2.Nf3 | Night. A light horseshoe window moves to f3 |
| 4 | 2…d6 | Day. Dark brick from d7 to d6 |
| 5 | 3.d4 | Night. Cream brick to d4. White now has two cream bricks in the middle (d4, e4) |
| 6 | 3…cxd4 | Day. **Trim turns green (Open Sicilian).** Dark brick takes the cream one on d4. **Flag goes up: black, 1 stripe** (Black is a pawn ahead for a moment) |
| 7 | 4.Nxd4 | Night. Horseshoe window from f3 to d4, flag comes down (equal) |
| 8 | 4…Nf6 | Day. Dark horseshoe window g8 to f6 |
| 9 | 5.Nc3 | Night. Second light horseshoe to c3 |
| 10 | 5…a6 | Day. **Trim turns blue: Najdorf.** Dark brick a7 to a6 |

**How a kid remembers the Najdorf:** *"Yellow pointy house with blue trim. Up top, the
dark bricks have a gap at c, with little steps down on a6 and d6. Downstairs there's only
one cream brick in the middle (e4), and two light horseshoe windows guard it (c3, d4)."*
The user's original idea was "the mainline Sicilian = a yellow house with two windows".
Here those two windows are White's knights on c3 and d4.

### 4b. Italian Game: `1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5`
**Red** house, gable roof, **green trim** (Giuoco Piano). Mirror-image brick pattern: a
cream brick on e4 faces a dark brick on e5. Two pointed church windows stand on the same column c
(c4 light, c5 dark), the "twin bishops" look. Horseshoe windows on f3 and c6. White to move, so it's daytime. Both fences, both chimneys. House number 4.

### 4c. Queen's Gambit Declined: `1.d4 d5 2.c4 e6 3.Nc3 Nf6`
**Blue castle** (battlement roof = 1.d4), **red trim** (Three Knights line). Cream bricks side by
side on c4/d4, and dark bricks make a **staircase** d5/e6, the classic QGD
"solid wall" look. Dark horseshoe on f6, light horseshoe on c3.

## 5. Learning path for kids

1. **"House Families" (age 4+).** Colors and roofs only. Match the house to its opening name. Sorting cards game.
2. **"Who lives here?" (5+).** Learn the six building parts (brick = pawn … door with crown = king). Build the starting house with stickers or magnetic tiles.
3. **"The house grows" (6+).** Play the first moves of an opening on a real board while an adult flips through the house cards. Kid narrates: "the brick climbed two floors!"
4. **"Spot the difference" (7+).** Two houses one move apart. What changed? (This *is* reading a move.)
5. **"Guess the family" quiz (7+).** Signless houses (`*_quiz.png`). Name the opening from colors + brick pattern.
6. **"Rebuild the board" (8+).** Look at a house and set up the real chessboard. This gives full decoding.
7. **"Bricks tell the plan" (9+).** Same brick pattern = same plans. Introduce pawn structures (isolated pawn, Maroczy bind, Carlsbad) as "house styles".

Physical tie-ins: printable house cards, a magnetic facade board, a "street" poster where each
opening tree branch is a street of related houses (same color, different trim).

## 6. Software roadmap

* **v0 (this repo).** Python prototype (`prototype/house.py`, python-chess + SVG + cairosvg).
* **v1 Web app.** TypeScript + `chess.js` for PGN/FEN parsing and the same deterministic SVG renderer (port of `house.py`). Includes a play-a-move board beside a live house, and smooth SVG transitions (bricks slide between floors) so kids *see* the move.
* **v2 Opening data.** Replace the hand table with the open Lichess `chess-openings` dataset (ECO/name/PGN, CC0). Then assign family colors per ECO family and trim per sub-variation automatically, with a curated palette checked for color-blind safety.
* **v3 Games & modes.** Quiz mode, spot-the-difference, rebuild-the-board, "street" view of an opening tree, printable card PDFs.
* **v4 Art pass.** Illustrated building-part sprites, with the same grid and the same rules. Test with real kids and iterate on which cues they actually use.

## 7. Open design questions

1. **Perspective:** always draw from White's side, or flip for a kid playing Black?
2. **Color budget:** there are ~500 ECO lines but only ~12 clearly distinct kid-friendly colors. Is it OK for the family to come only from *first-level* openings, with variations shown through trim/accents?
3. **Hand-crafted "hero houses":** should famous positions (Najdorf, Dragon, Ruy Lopez) get special decorations (a dragon weather vane for the Dragon) on top of the rules?
4. **Leaving book:** keep the last family look forever (current rule), or slowly "fade" the paint as the game drifts from theory?
5. **Color-blind safety:** add a pattern per family (stripes, polka dots, wood siding) as well as color.
6. **Halfmove clock** isn't shown yet. Is it worth adding (e.g. grass grows taller)?
