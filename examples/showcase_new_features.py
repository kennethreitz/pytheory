"""Showcase of the features added in this round.

Run it::

    uv run python examples/showcase_new_features.py

It prints the theory features, writes the guitar diagrams as SVG into
``./showcase_out/``, and lists the metronome commands to try (those make
sound, so they're left for you to run).
"""
import os

from pytheory import Key, Chord, Fretboard, TonedScale, Raga


def hr(title):
    print(f"\n\033[1m{title}\033[0m\n" + "─" * len(title))


# ── 1. Key-level circle of fifths ────────────────────────────────────
hr("1. Key.circle_of_fifths()  —  relational map of a key")
cof = Key("C", "major").circle_of_fifths()
print(f"  C major sits at position {cof['position']} (0 = no sharps/flats)")
print(f"  relative: {cof['relative']}      parallel: {cof['parallel']}")
print(f"  dominant neighbour : {cof['dominant']['key']}  "
      f"(shares {len(cof['dominant']['shared_chords'])} chords)")
print(f"  subdominant neighbour: {cof['subdominant']['key']}  "
      f"(shares {len(cof['subdominant']['shared_chords'])} chords)")
print("  full circle:", "  ".join(str(k).replace(" major", "")
                                  for k in cof["circle"]))


# ── 2. Chord families by harmonic function ───────────────────────────
hr("2. chords_by_function()  —  interchangeable chords by role")
for key in (Key("C", "major"), Key("A", "minor")):
    fams = key.chords_by_function()
    print(f"  {key}:")
    for role in ("tonic", "subdominant", "dominant"):
        print(f"    {role:<12} {', '.join(c.symbol for c in fams[role])}")


# ── 3. Negative harmony ──────────────────────────────────────────────
hr("3. negative_harmony()  —  mirror across the tonic↔dominant axis")
neg = Key("C", "major").negative_harmony()
print(f"  axis runs between {neg['axis'][0]} and {neg['axis'][1]}, "
      f"hinging on {neg['axis_notes'][0]}/{neg['axis_notes'][1]}")
print(f"  negative scale : {' '.join(neg['scale'])}")
print(f"  C major  →  {Chord.from_symbol('C').negative_harmony('C').identify()}")
print(f"  G7 (the V) → {Chord.from_symbol('G7').negative_harmony('C').identify()}"
      f"   ← the negative dominant ({neg['negative_dominant'].symbol}), the bridge chord")


# ── 4. Guitar diagrams (SVG) ─────────────────────────────────────────
hr("4. SVG fretboard diagrams  —  written to ./showcase_out/")
out = os.path.join(os.path.dirname(__file__), "showcase_out")
os.makedirs(out, exist_ok=True)
fb = Fretboard.guitar()

# chord diagrams — iterate a progression
for name in ["C", "Am", "F", "G", "Em7"]:
    fb.tab_image(name, os.path.join(out, f"chord_{name}.svg"))
print("  chord diagrams : chord_C/Am/F/G/Em7.svg")

# the five pentatonic position shapes
pent = TonedScale(tonic="A4", system="blues")["minor pentatonic"]
for shape in fb.scale_shapes(pent):
    lo, hi = shape.fret_range
    shape.to_svg(path=os.path.join(out, f"Apent_pos{shape.index}.svg"))
print("  scale shapes   : Apent_pos1..5.svg  (the five pentatonic boxes)")

# arpeggio map
fb.arpeggio_diagram("Am", os.path.join(out, "Am_arpeggio.svg"))
print("  arpeggio map   : Am_arpeggio.svg")
print(f"\n  → open {out}/ in a browser to view them")


# ── 5. Hindustani ragas (with shruti just intonation) ────────────────
hr("5. Hindustani ragas  —  living forms, intoned in shruti")
for name in ["Yaman", "Bhairav", "Malkauns"]:
    r = Raga.get(name)
    print(f"  {r.name} ({r.thaat}, {r.time}, {r.rasa})")
    print(f"    aroha {' '.join(r.aroha_swaras())}  /  "
          f"avaroha {' '.join(r.avaroha_swaras())}")
yaman = Raga.get("Yaman")
print("\n  Yaman in just intonation (Sa=C) — note the flat shruti thirds:")
for row in yaman.shruti_table("C"):
    print(f"    {row['swara']:<2} {row['ratio']:>6}  {row['note']:<3} "
          f"{row['cents_off']:+6.1f}¢ vs 12-TET")
print("\n  hear it:  pytheory raga yaman --play     (just intonation, sitar)")
print(f"  ({len(Raga.all())} ragas across all ten thaats — Raga.names())")


# ── 6. Metronome / tempo trainer (commands to try) ───────────────────
hr("6. Metronome + tempo trainer  —  these make sound, so run them yourself")
print("  pytheory metronome 120")
print("  pytheory metronome 90 --chords Am F C G        # practice a loop")
print("  pytheory metronome 100 --subdivide 2           # eighth-note clicks")
print("  pytheory metronome 80 --to 120 --step 5 --every 8   # tempo trainer")
print("\n  or from Python:")
print("  >>> from pytheory.metronome import Metronome")
print("  >>> Metronome(bpm=90, progression=['Am','F','C','G']).start()")
