"""Explore the overtone series — nature's chord."""

from pytheory import Tone, Chord

a4 = Tone.from_string("A4", system="western")

print("The Overtone Series")
print("=" * 65)
print()
print("When you play a note, you're actually hearing many frequencies")
print("at once. The fundamental plus its integer multiples:")
print()
print(f"{'Harmonic':>9s}  {'Frequency':>10s}  {'Nearest Note':>13s}  {'Interval from Root'}")
print(f"{'─' * 9}  {'─' * 10}  {'─' * 13}  {'─' * 25}")

overtones = a4.overtones(16)

for i, hz in enumerate(overtones, 1):
    nearest = Tone.from_frequency(hz)
    if i == 1:
        interval = "Fundamental"
    else:
        interval = a4.interval_to(nearest)
    print(f"{i:>9d}  {hz:>10.1f}  {nearest.full_name:>13s}  {interval}")

# ── Why Chords Sound Good ───────────────────────────────────────────────

print()
print("Why the Major Triad Sounds 'Natural'")
print("=" * 65)
print()
print("The first 6 harmonics contain: root, octave, 5th, 2nd octave, 3rd, 5th")
print("That's a major triad! The major chord is literally embedded in physics.")
print()

c4 = Tone.from_string("C4", system="western")
harmonics = c4.overtones(6)
harmonic_names = [Tone.from_frequency(hz).name for hz in harmonics]
unique = []
for n in harmonic_names:
    if n not in unique:
        unique.append(n)
print(f"  First 6 harmonics of C: {', '.join(harmonic_names)}")
print(f"  Unique pitch classes:   {', '.join(unique)}")
print(f"  C major triad:          C, E, G")
print()

# ── Shared Overtones = Consonance ───────────────────────────────────────

print("Shared Overtones Between Intervals")
print("=" * 65)
print()
print("The more overtones two notes share, the more consonant they sound.")
print()

root = Tone.from_string("C4", system="western")
root_overtones = set(round(h, 1) for h in root.overtones(12))

for semitones, label in [(7, "Perfect 5th (C→G)"),
                          (4, "Major 3rd (C→E)"),
                          (5, "Perfect 4th (C→F)"),
                          (3, "Minor 3rd (C→Eb)"),
                          (6, "Tritone (C→F#)"),
                          (1, "Minor 2nd (C→C#)")]:
    other = root + semitones
    other_overtones = set(round(h, 1) for h in other.overtones(12))
    shared = root_overtones & other_overtones
    print(f"  {label:25s}  {len(shared):2d} shared overtones (of first 12)")
