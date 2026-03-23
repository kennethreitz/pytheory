"""Explore instruments, tunings, and chord fingerings."""

from pytheory import Fretboard, CHARTS

# ── Compare Instruments ─────────────────────────────────────────────────

print("Instrument Tunings")
print("=" * 55)

instruments = [
    ("Guitar (standard)", Fretboard.guitar()),
    ("Guitar (drop D)",   Fretboard.guitar("drop d")),
    ("Guitar (open G)",   Fretboard.guitar("open g")),
    ("Guitar (DADGAD)",   Fretboard.guitar("dadgad")),
    ("Bass",              Fretboard.bass()),
    ("Ukulele",           Fretboard.ukulele()),
    ("Mandolin",          Fretboard.mandolin()),
    ("Violin",            Fretboard.violin()),
    ("Banjo",             Fretboard.banjo()),
    ("Bouzouki (Irish)",  Fretboard.bouzouki()),
]

for name, fb in instruments:
    tuning = " ".join(t.full_name for t in fb.tones)
    print(f"  {name:22s}  {tuning}")

# ── Guitar Chord Chart ──────────────────────────────────────────────────

print()
print("Guitar Chord Chart (standard tuning)")
print("=" * 55)

fb = Fretboard.guitar()
chart = CHARTS["western"]

for chord_name in ["C", "G", "D", "Am", "Em", "F", "A", "E", "Dm", "G7", "C7", "Am7"]:
    f = chart[chord_name].fingering(fretboard=fb)
    print(f"  {chord_name:5s}  {f}")

# ── Capo Magic ──────────────────────────────────────────────────────────

print()
print("Capo Transposition")
print("=" * 55)
print("  Playing open chord shapes with a capo changes the key:")
print()

open_shapes = ["C", "G", "D", "Am", "Em"]

for capo_fret in range(1, 6):
    fb_capo = Fretboard.guitar(capo=capo_fret)
    results = []
    for shape in open_shapes:
        f = chart[shape].fingering(fretboard=fb_capo)
        actual = f.identify() or "?"
        results.append(f"{shape}→{actual.split()[0]}")
    print(f"  Capo {capo_fret}:  {', '.join(results)}")

# ── Same Chord on Different Instruments ─────────────────────────────────

print()
print("C Major on Different Instruments")
print("=" * 55)

c_chord = chart["C"]
for name, fb in [("Guitar", Fretboard.guitar()),
                  ("Ukulele", Fretboard.ukulele()),
                  ("Mandolin", Fretboard.mandolin()),
                  ("Banjo", Fretboard.banjo())]:
    try:
        f = c_chord.fingering(fretboard=fb)
        print(f"  {name:12s}  {f}")
    except Exception:
        print(f"  {name:12s}  (not available for this tuning)")
