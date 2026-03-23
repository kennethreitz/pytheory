"""Identify chords from notes or guitar fingerings."""

from pytheory import Chord, Fretboard

print("=== Chord Identification from Notes ===")
print()

test_chords = [
    ("C", "E", "G"),
    ("A", "C", "E"),
    ("G", "B", "D", "F"),
    ("D", "F#", "A"),
    ("Bb", "D", "F"),
    ("E", "G#", "B"),
    ("C", "Eb", "Gb"),
    ("C", "G"),
    ("C", "F", "G"),
    ("C", "D", "G"),
]

for notes in test_chords:
    chord = Chord.from_tones(*notes)
    name = chord.identify() or "Unknown"
    print(f"  {', '.join(notes):20s}  →  {name}")

print()
print("=== Chord Identification from Guitar Fingerings ===")
print()

fb = Fretboard.guitar()

# Common guitar chord shapes
shapes = [
    ("Open C",    (0, 1, 0, 2, 3, 0)),
    ("Open G",    (3, 0, 0, 0, 2, 3)),
    ("Open D",    (2, 3, 2, 0, 0, 0)),
    ("Open Am",   (0, 1, 2, 2, 0, 0)),
    ("Open Em",   (0, 0, 0, 2, 2, 0)),
    ("Barre F",   (1, 1, 2, 3, 3, 1)),
    ("Power E5",  (0, 0, 0, 0, 2, 0)),
]

for label, positions in shapes:
    f = fb.fingering(*positions)
    name = f.identify() or "Unknown"
    print(f"  {label:12s}  {f}  →  {name}")
