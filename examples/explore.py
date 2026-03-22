"""Explore music theory with PyTheory."""

from pytheory import Key, Chord, Tone, Interval, PROGRESSIONS, Fretboard

# ── Keys and Scales ──────────────────────────────────────────────────────

key = Key("C", "major")
print(f"Key: {key}")
print(f"Notes: {key.note_names}")
print()

# ── Diatonic Harmony ─────────────────────────────────────────────────────

print("Diatonic triads:")
for i, chord in enumerate(key.scale.harmonize()):
    analysis = chord.analyze("C")
    print(f"  {analysis:4s}  {chord}")

print()
print("Diatonic seventh chords:")
for name in key.seventh_chords:
    print(f"  {name}")

# ── Progressions ─────────────────────────────────────────────────────────

print()
print("Common progressions in C major:")
for name, numerals in PROGRESSIONS.items():
    chords = key.progression(*numerals)
    chord_names = [str(c) for c in chords]
    print(f"  {name:20s}  {' → '.join(chord_names)}")

# ── Intervals ────────────────────────────────────────────────────────────

print()
c4 = Tone.from_string("C4", system="western")
print("Intervals from C4:")
for semitones in range(13):
    tone = c4 + semitones
    name = c4.interval_to(tone)
    print(f"  {semitones:2d} semitones = {tone.name:3s}  ({name})")

# ── Circle of Fifths ─────────────────────────────────────────────────────

print()
print("Circle of fifths:", " → ".join(t.name for t in c4.circle_of_fifths()))

# ── Chord Analysis ───────────────────────────────────────────────────────

print()
g7 = Chord.from_name("G7")
print(f"Chord: {g7}")
print(f"  Intervals: {g7.intervals}")
print(f"  Tension: {g7.tension}")
print(f"  Analysis in C: {g7.analyze('C')}")

# ── Guitar Fingerings ────────────────────────────────────────────────────

print()
fb = Fretboard.guitar()
print("Guitar fingerings:")
for name in ["C", "G", "Am", "F", "Dm", "E7"]:
    from pytheory import CHARTS
    fingering = CHARTS["western"][name].fingering(fretboard=fb)
    print(f"  {name:4s}  {fingering}")

# ── Overtone Series ──────────────────────────────────────────────────────

print()
a4 = Tone.from_string("A4", system="western")
print(f"Overtone series of {a4}:")
for i, hz in enumerate(a4.overtones(8), 1):
    nearest = Tone.from_frequency(hz)
    print(f"  Harmonic {i}: {hz:8.1f} Hz  ≈ {nearest.full_name}")
