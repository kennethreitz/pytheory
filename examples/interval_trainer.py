"""Learn intervals — names, sounds, and relationships."""

from pytheory import Tone, Chord, Interval

c4 = Tone.from_string("C4", system="western")

# ── Interval Reference ──────────────────────────────────────────────────

print("Interval Reference (from C4)")
print("=" * 70)
print()
print(f"{'Semitones':>10s}  {'Note':>5s}  {'Interval Name':>18s}  {'Sound / Song'}")
print(f"{'─' * 10}  {'─' * 5}  {'─' * 18}  {'─' * 30}")

songs = {
    0:  "Same note",
    1:  "Jaws",
    2:  "Happy Birthday",
    3:  "Greensleeves",
    4:  "Here Comes the Sun",
    5:  "Here Comes the Bride",
    6:  "The Simpsons",
    7:  "Star Wars (main theme)",
    8:  "Love Story",
    9:  "My Bonnie Lies Over the Ocean",
    10: "Somewhere (West Side Story)",
    11: "Take On Me (chorus)",
    12: "Somewhere Over the Rainbow",
}

for semitones in range(13):
    tone = c4 + semitones
    name = c4.interval_to(tone)
    song = songs.get(semitones, "")
    print(f"{semitones:>10d}  {tone.name:>5s}  {name:>18s}  {song}")

# ── Interval Constants ──────────────────────────────────────────────────

print()
print("Interval Constants (pytheory.Interval)")
print("=" * 40)

constants = [
    ("UNISON", Interval.UNISON),
    ("MINOR_SECOND", Interval.MINOR_SECOND),
    ("MAJOR_SECOND", Interval.MAJOR_SECOND),
    ("MINOR_THIRD", Interval.MINOR_THIRD),
    ("MAJOR_THIRD", Interval.MAJOR_THIRD),
    ("PERFECT_FOURTH", Interval.PERFECT_FOURTH),
    ("TRITONE", Interval.TRITONE),
    ("PERFECT_FIFTH", Interval.PERFECT_FIFTH),
    ("MINOR_SIXTH", Interval.MINOR_SIXTH),
    ("MAJOR_SIXTH", Interval.MAJOR_SIXTH),
    ("MINOR_SEVENTH", Interval.MINOR_SEVENTH),
    ("MAJOR_SEVENTH", Interval.MAJOR_SEVENTH),
    ("OCTAVE", Interval.OCTAVE),
]

for name, value in constants:
    print(f"  Interval.{name:16s} = {value}")

# ── Compound Intervals ─────────────────────────────────────────────────

print()
print("Compound Intervals (beyond one octave)")
print("=" * 50)

for semitones in [13, 14, 15, 16, 19, 24]:
    tone = c4 + semitones
    name = c4.interval_to(tone)
    print(f"  {semitones:2d} semitones  {tone.full_name:5s}  {name}")

# ── Consonance Ranking ──────────────────────────────────────────────────

print()
print("Intervals Ranked by Consonance")
print("=" * 50)

intervals = []
for semitones in range(1, 13):
    tone = c4 + semitones
    dyad = Chord.from_tones("C", tone.name)
    name = c4.interval_to(tone)
    intervals.append((dyad.harmony, dyad.dissonance, semitones, name))

# Sort by harmony score (descending)
intervals.sort(key=lambda x: x[0], reverse=True)

print(f"{'Rank':>5s}  {'Interval':>18s}  {'Harmony':>8s}  {'Dissonance':>11s}")
print(f"{'─' * 5}  {'─' * 18}  {'─' * 8}  {'─' * 11}")

for rank, (harmony, dissonance, _, name) in enumerate(intervals, 1):
    print(f"{rank:>5d}  {name:>18s}  {harmony:>8.4f}  {dissonance:>11.4f}")
