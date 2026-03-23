"""Analyze harmonic tension and resolution across chords."""

from pytheory import Chord

print("Chord Tension Analysis")
print("=" * 70)
print()
print(f"{'Chord':>20s}  {'Tension':>8s}  {'Harmony':>8s}  {'Dissonance':>11s}  {'Notes'}")
print(f"{'─' * 20}  {'─' * 8}  {'─' * 8}  {'─' * 11}  {'─' * 15}")

chords = [
    # Stable chords
    "C", "Am",
    # Moderate tension
    "Dm7", "Cmaj7",
    # High tension
    "G7", "Bdim",
    # Extended
    "Am7", "Cmaj9",
]

for name in chords:
    chord = Chord.from_name(name)
    t = chord.tension
    tones = " ".join(tone.name for tone in chord.tones)
    print(
        f"{name:>20s}  {t['score']:>8.2f}  {chord.harmony:>8.4f}"
        f"  {chord.dissonance:>11.4f}  {tones}"
    )

# Show the V7 → I resolution
print()
print("─" * 70)
print()
print("The V7 → I resolution (the strongest pull in tonal music):")
print()

g7 = Chord.from_name("G7")
c = Chord.from_name("C")

print(f"  G7 (dominant):  tension={g7.tension['score']:.2f}  "
      f"tritones={g7.tension['tritones']}  "
      f"dominant_function={g7.tension['has_dominant_function']}")
print(f"  C  (tonic):     tension={c.tension['score']:.2f}  "
      f"tritones={c.tension['tritones']}  "
      f"dominant_function={c.tension['has_dominant_function']}")

print()
print("Voice leading (G7 → C):")
for src, dst, motion in g7.voice_leading(c):
    direction = "↑" if motion > 0 else "↓" if motion < 0 else "="
    print(f"  {src.name:3s} → {dst.name:3s}  ({direction} {abs(motion)} semitones)")
