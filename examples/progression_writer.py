"""Build and analyze chord progressions in any key."""

from pytheory import Key, Chord

def show_progression(key, numerals, label=""):
    chords = key.progression(*numerals)
    if label:
        print(f"  {label}")
    print(f"    Key: {key}")
    print(f"    Progression: {' – '.join(numerals)}")
    print()
    for numeral, chord in zip(numerals, chords):
        t = chord.tension
        print(
            f"      {numeral:6s}  {chord.identify():20s}  "
            f"tension={t['score']:.2f}  "
            f"{'*** DOMINANT ***' if t['has_dominant_function'] else ''}"
        )
    print()


# ── Famous Progressions ─────────────────────────────────────────────────

print("Famous Chord Progressions")
print("=" * 65)
print()

key_c = Key("C", "major")

show_progression(key_c, ("I", "V", "vi", "IV"),
    "The Pop Progression (Let It Be, No Woman No Cry, Someone Like You)")

show_progression(key_c, ("I", "vi", "IV", "V"),
    "The 50s Progression (Stand By Me, Every Breath You Take)")

show_progression(key_c, ("ii", "V", "I"),
    "Jazz ii–V–I (the backbone of jazz harmony)")

show_progression(key_c, ("I", "IV", "V", "I"),
    "The Three-Chord Trick (blues, rock, country)")

# ── Same Progression in Different Keys ──────────────────────────────────

print("─" * 65)
print()
print("I – V – vi – IV in every key:")
print()

for tonic in ["C", "G", "D", "A", "E", "F", "Bb", "Eb"]:
    key = Key(tonic, "major")
    chords = key.progression("I", "V", "vi", "IV")
    names = [c.identify() for c in chords]
    print(f"  {tonic} major:  {' → '.join(names)}")

# ── Nashville Number System ─────────────────────────────────────────────

print()
print("─" * 65)
print()
print("Nashville Number System:")
print("  (Same thing as Roman numerals, but with integers)")
print()

key_g = Key("G", "major")
chords = key_g.nashville(1, 5, 6, 4)
names = [c.identify() for c in chords]
print(f"  G major: 1 – 5 – 6 – 4  →  {' → '.join(names)}")

# ── Random Progression Generator ────────────────────────────────────────

print()
print("─" * 65)
print()
print("Random 8-bar progressions:")
print()

for _ in range(3):
    key = Key("C", "major")
    chords = key.random_progression(8)
    names = [c.identify().split()[0] for c in chords]  # Just root names
    print(f"  | {'  | '.join(names)}  |")
