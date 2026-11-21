# Chess Houses: Design (draft v0.3)

> **Level 1: every main opening is its own house.** Kids learn "the Sicilian is the yellow
> farmhouse with the outside staircase, the French is the tall Paris house with the slate
> roof" just by looking. Levels 2+ add houses that change with the actual position.

## Levels at a glance

| Level | What the house shows | Script |
|---|---|---|
| **Level 1** | **Which opening** it is. One fixed, hand-designed house per opening. No position details | `prototype/level1.py` |
| Level 2+ | The **position**: real-house encoding (windows = developed pieces, garage = castled, ...) | `prototype/real_house.py` |
| Alternates | Facade-grid styles that encode the exact board | `prototype/house.py`, `prototype/simple.py` |

---

# Level 1: The Opening Neighborhood

## Rules for Level 1 houses

1. **One opening = one house, always the same picture.** Nothing changes with the moves.
2. **Recognizable from far away.** Every house has a different **silhouette** (tower, dome, lighthouse, mansard, castle, A-shape, stacked boxes ...), a different **main colour**, and 1–2 **signature features**.
3. **Memorable story.** Where possible the house comes from the opening's name or character (French = Paris, Spanish = hacienda, London = London, Modern = modern house).
4. **Same scale and ground line** for every house, flat picture-book style, no grid, no labels except an optional name sign.

## The houses

| Opening | House type | Main colour | Signature features | Why |
|---|---|---|---|---|
| **Sicilian Defence** (`1.e4 c5`) | Mediterranean farmhouse | sunny yellow | outside stone staircase, blue shutters, lemon tree | Sicily is a sunny Mediterranean island of yellow farmhouses and lemon groves. |
| **French Defence** (`1.e4 e6`) | Parisian townhouse | Paris blue-grey | mansard roof with round dormers, iron balconies | Tall, narrow Paris buildings with slate mansard roofs are the picture of France. |
| **Caro-Kann Defence** (`1.e4 c6`) | Cape Cod cottage | pink | two roof dormers, central chimney, white picket fence | A small, tidy, very solid cottage, like the Caro-Kann: safe and sturdy. |
| **Italian Game** (`1.e4 e5 2.Nf3 Nc6 3.Bc4`) | Tuscan villa | terracotta | square bell tower, arched loggia, cypress trees | Classic Italian countryside villa with a tower, as old and classic as the opening. |
| **Ruy Lopez (Spanish)** (`1.e4 e5 2.Nf3 Nc6 3.Bb5`) | Spanish hacienda | adobe sand | curvy bell gable, big arched wooden doors, iron window grilles | Ruy Lopez was a Spanish priest: a mission-style hacienda with a bell gable. |
| **Scandinavian Defence** (`1.e4 d5`) | Nordic cabin | Falu red | grass (sod) roof, white corner trim, birch tree | Red cabins with white trim and grass roofs are iconic in Sweden and Norway. |
| **Queen's Gambit** (`1.d4 d5 2.c4`) | royal castle | stone grey + royal purple | twin towers with purple cone roofs and flags, crown banner | A queen lives in a castle. The Queen's Gambit is the royal, classical 1.d4 opening. |
| **London System** (`1.d4 + Bf4`) | London Georgian terrace | dark brick | red phone box, black door with fanlight and white columns | A real London street house, complete with a red telephone box. |
| **King's Indian Defence** (`1.d4 Nf6 2.c4 g6`) | Indian palace | white marble + teal | huge onion dome, two minarets, pointed arches | A palace fit for an Indian king: big dome, towers, and a reflecting pool. |
| **English Opening** (`1.c4`) | Tudor cottage | cream + black beams | black-and-white timber beams, steep gable, tall chimney, roses | Old English villages are full of black-and-white Tudor cottages. |
| **Pirc / Modern Defence** (`1.e4 d6 / 1.e4 g6`) | modern house | charcoal + wood | stacked boxes, flat roofs, floor-to-ceiling glass | It's called the 'Modern' Defence, so it gets a modern house. |
| **Scotch Game** (`1.e4 e5 2.Nf3 Nc6 3.d4`) | lighthouse cottage | red and white stripes | tall striped lighthouse with a keeper's cottage | Scotland's coast is famous for its lighthouses. |

Sibling idea for later: the **Queen's Gambit Declined / Accepted** can be two versions of
the same castle (gate closed vs. drawbridge down, "accepting the gift").

## Files

* `examples/level1/neighborhood.png`: all 12 houses with their names (overview poster)
* `examples/level1/flashcards.png`: printable cards (fold the name under to quiz)
* `examples/level1/<opening>.png`: each house with its name sign
* `examples/level1/<opening>_quiz.png`: the same house without the sign

## How kids use Level 1

1. **Meet the neighbors:** walk through the neighborhood poster, one house per opening, with its story ("the French lives in Paris").
2. **Flashcard quiz:** show a quiz card and the kid names the opening.
3. **Play the first moves on a real board.** When the moves reach that opening, the kid points to its house.
4. **Graduate to Level 2:** the same opening family now changes its house as the game goes on.

## Open questions (Level 1)

1. Is this the right set of 12? Candidates to swap in: Vienna, King's Gambit, Dutch, Nimzo-Indian, Grünfeld, Catalan, Petrov.
2. Should sibling openings share a house (QGD/QGA castles, Pirc vs. Modern)?
3. Should Level 2 reuse these Level 1 house shapes instead of the generic two-storey house? (Recommended: a French position would then always be the Paris townhouse with its windows changing.)

---

# Level 2+: Real-house mode (position encoding)


## 1.1 Idea

The house does **not** try to store the exact board. It tells you the *story* of the
position in house language: which pieces came out, whether the kings castled, whether the
centre pawns moved, who is ahead. Those are exactly the things a beginner should
notice about a chess position. The opening family gives the house its overall look, so
different openings make clearly different houses.

## 1.2 The mapping

**Whole house**

| House feature | Chess meaning |
|---|---|
| Wall colour + wall pattern (clapboard, brick, stone, shingle, stucco, board-and-batten) | Opening family (Sicilian = yellow clapboard, Italian = red brick, QGD = blue stone ...) |
| Roof shape | White's first move: pointy gable = 1.e4, hip roof = 1.d4, barn (gambrel) roof = 1.c4, flat roof = 1.Nf3, slanted shed = no move yet |
| Trim colour (window frames, shutters, door, gutter, floor band) | Which variation of the opening (Najdorf = blue trim on a yellow Sicilian house) |
| Sun / moon (windows glow at night) | White / Black to move |
| Name sign in the yard | Optional. Hidden in quiz mode (`--no-label`) |

**The two floors: downstairs = White, upstairs = Black.** Each floor has 6 spots,
left to right in the order the pieces start on the board: **knight · bishop · queen · king · bishop · knight**.

| In a piece's spot | Meaning |
|---|---|
| Closed shutters | That piece is still at home |
| **Round window** | A knight came out |
| **Square window** | A bishop came out |
| **Bay window** (sticks out, own little roof) | The queen came out |
| Bare wall (no window) | That piece was captured |
| King spot, downstairs = **front door** | **Double doors** = White can still castle both ways; **single door** = one way left, or already castled; **boarded door** = can't castle any more (king stuck in the middle) |
| King spot, upstairs = **tall arched window(s)** | Same for Black: two tall windows / one / boarded |

**Extras (always in the same place)**

| House feature | Chess meaning |
|---|---|
| **Garage** (right side / left side) | White castled short / long |
| **Chimney** (right / left of the roof) | Black castled short / long |
| **Front porch with two columns** | White's rooks are connected (nothing between them on the back rank) |
| **Upstairs balcony railing** | Black's rooks are connected |
| **Front steps** (0-2) | White's centre pawns (d/e) that moved forward |
| **Flower boxes** under the upstairs windows (0-2) | Black's centre pawns (d/e) that moved forward |
| **Garden path** to the street | At least one pawn has been captured: the position has opened up |
| **Flag in the yard** | Material balance: no flag = equal, white flag = White ahead, dark flag = Black ahead; dots = pawns' worth ahead (P1 N3 B3 R5 Q9) |

Castling is read from the move history. For a bare FEN it is guessed: no rights left and
the king on a castled square.

**Why these choices.** Round window/knight and square window/bishop come from the user's own
examples ("three square windows", "three round windows"). The door is the king because everyone
goes through it, and "double doors = two ways to castle" is easy to remember. A garage on the side
the king tucked into is a strong visual for "king is safe". Columns hold up the porch the way
connected rooks protect each other. Steps and flower boxes grow as centre pawns advance, a path
opens when pawns are traded, and a flag means someone is winning the material battle.

## 1.3 Worked examples (`examples/real/`)

| Opening | What the house looks like |
|---|---|
| **Sicilian Najdorf** `1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6` | Yellow clapboard, pointy roof, blue trim. Downstairs: **two round windows** (Nc3, Nd4), bishops' and queen's shutters closed, **double doors**, **one step** (e4). Upstairs: one round window (Nf6), rest shuttered, two tall windows, **one flower box** (d6). **Garden path** (pawns traded on d4). Daytime (White to move). |
| **Italian Game** `1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5` | Red brick, pointy roof, green trim. Downstairs: **square window + round window on the right** (Bc4, Nf3), double doors, one step. Upstairs: **round window on the left + square window on the right** (Nc6, Bc5), one flower box. No path. |
| **Queen's Gambit Declined** `1.d4 d5 2.c4 e6 3.Nc3 Nf6` | Blue stone, **hip roof** (1.d4), red trim. Downstairs: round window on the left (Nc3), one step (d4). Upstairs: round window on the right (Nf6), **two flower boxes** (d5 + e6: the solid QGD centre). No path. |

`examples/real/three_openings.png` shows the three side by side without name signs.

### The Najdorf house being built (`examples/real/sicilian_sequence_sheet.png`)

| Move | What changes |
|---|---|
| start | Grey-white house, slanted roof, every shutter closed, double doors, two tall windows |
| 1.e4 | Night. **Roof becomes pointy** (1.e4), walls cream, **one front step** appears |
| 1...c5 | Day. **House turns yellow: Sicilian.** (c-pawn is not a centre pawn, so no flower box) |
| 2.Nf3 | Night. Right-hand downstairs shutters open into a **round window** |
| 2...d6 | Day. **Flower box** appears upstairs |
| 3.d4 | Night. A second front step |
| 3...cxd4 | Day. Trim turns green (Open Sicilian). **Garden path** appears. **Dark flag** goes up (Black is a pawn ahead). Back to one step (d-pawn gone) |
| 4.Nxd4 | Night. The flag comes down (equal again). The f3 knight moved but is still "out", so the house stays the same apart from the flag |
| 4...Nf6 | Day. Upstairs right shutters open into a **round window** |
| 5.Nc3 | Night. Downstairs left shutters open into a **round window**: two round windows now |
| 5...a6 | Day. **Trim turns blue: Najdorf** |

## 1.4 Learning path (real-house mode)

1. **Open the shutters (4+).** Play the first moves; each time a knight or bishop comes out a shutter opens into a round or square window.
2. **Doors and garages (5+).** Castle and watch the garage appear; lose castling rights and the door gets boarded up.
3. **House families (6+).** Match house colour and roof to the opening name with signs hidden (`*_quiz.png`).
4. **Tell the story (7+).** Look at a house and tell what happened: "both knights out, White castled short, Black hasn't castled, pawns were traded".
5. **Build it yourself (8+).** Given a house, play moves on a real board that make that house.

## 1.5 Open questions (real-house mode)

1. **House styles per family.** Right now families differ by colour, wall pattern and roof. Should each family also get its own building shape (cottage, colonial, ranch, townhouse)?
2. **Pawn structure detail.** Fianchetto, doubled/isolated pawns and open files aren't shown yet. Candidates are a round tower (fianchetto), a fence (pawn chain) and a mailbox (passed pawn).
3. **Rooks on open files** could add extra columns (currently columns mean "connected" only).
4. Should a piece that came out and went **back home** close its shutters again? It currently does, because the house shows the position, not the history.
5. Does the sign belong in the yard or above the door?

---

# Alternates: facade grid and kid-mode grid

The text below is the v0.1 design. It still describes `house.py` and `simple.py`.


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


## 3b. Kid mode ("simple" renderer): built for pattern-recognition brains

Some kids, often autistic kids, recognize patterns extremely well. They do best when the
picture is **strictly consistent**. `prototype/simple.py` draws the same encoding under
these rules:

1. **One feature = one meaning, always in the same fixed spot.** Every house uses the
   identical layout (top to bottom): *flag slot → roof box with 2 chimney slots → trim band →
   8×8 wall → en-passant strip → 2 fence slots*. The house never moves or resizes.
   Every roof shape fills the same roof box.
2. **Nothing decorative.** No sun/moon/stars, smoke, flowers, mortar lines, grid lines,
   letters, numbers or name sign. If something is drawn, it means something.
3. **"Gone" stays visible.** A lost castling right or an equal-material flag is drawn as an
   **empty dashed box in its slot**. It never just disappears, so two houses can be
   compared slot by slot.
4. **Flat, high-contrast shapes.** Mid-tone, saturated wall colors. White pieces = white
   silhouettes with a black edge. Black pieces = black silhouettes with a white edge. Every piece
   is centered in its (invisible) square.
5. **One silhouette per piece:** pawn = small square, knight = round arch, bishop = pointed
   arch, rook = square with 3 battlements, queen = circle, king = tall door with a 3-point crown.
6. **Small changes are instantly spottable.** One move changes exactly: one shape moves (or
   disappears on a capture), the sky flips light/dark, and *sometimes* the trim band, flag,
   chimney, fence or en-passant dot changes. See `examples/simple/spot_the_difference.png`
   (before/after 5...a6: the a7 square moves down one floor, the band turns green → blue, the sky flips).

The house number (move count) is deliberately **not** shown in kid mode: it doesn't describe
the position. The one-page legend is `examples/simple/legend.png`.

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

## 7. Open design questions (grid styles)

1. **Perspective:** always draw from White's side, or flip for a kid playing Black?
2. **Color budget:** there are ~500 ECO lines but only ~12 clearly distinct kid-friendly colors. Is it OK for the family to come only from *first-level* openings, with variations shown through trim/accents?
3. **Hand-crafted "hero houses":** should famous positions (Najdorf, Dragon, Ruy Lopez) get special decorations (a dragon weather vane for the Dragon) on top of the rules?
4. **Leaving book:** keep the last family look forever (current rule), or slowly "fade" the paint as the game drifts from theory?
5. **Kid mode details:** should kid mode be the *default* look, with the illustrated house as an optional "fancy" skin? Should the start position get a fixed neutral roof instead of the flat one?
6. **Color-blind safety:** add a pattern per family (stripes, polka dots, wood siding) as well as color.
7. **Halfmove clock** isn't shown yet. Is it worth adding (e.g. grass grows taller)?
