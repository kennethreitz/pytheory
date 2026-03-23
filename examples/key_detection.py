"""Detect the key of a melody or chord progression."""

from pytheory import Key, Chord

print("Key Detection")
print("=" * 55)
print()

# ── Detect from Melody Notes ────────────────────────────────────────────

melodies = [
    ("Twinkle Twinkle",    ["C", "G", "A", "F", "E", "D"]),
    ("Happy Birthday",     ["G", "A", "B", "C", "D", "F#"]),
    ("Yesterday",          ["F", "E", "D", "C", "Bb", "A", "G"]),
    ("Minor melody",       ["A", "B", "C", "D", "E", "F", "G"]),
    ("Blues lick",         ["E", "G", "A", "B", "D"]),
    ("Chromatic fragment",  ["C", "C#", "D", "D#", "E"]),
]

print("Detecting key from melody notes:")
print()
for label, notes in melodies:
    key = Key.detect(*notes)
    print(f"  {label:22s}  {', '.join(notes):30s}  →  {key}")

# ── Detect from Chord Progression ──────────────────────────────────────

print()
print("Detecting key from chord tones:")
print()

progressions = [
    ("I-IV-V",      [("C", "E", "G"), ("F", "A", "C"), ("G", "B", "D")]),
    ("Pop in G",    [("G", "B", "D"), ("D", "F#", "A"), ("E", "G", "B"), ("C", "E", "G")]),
    ("Jazz ii-V-I", [("D", "F", "A"), ("G", "B", "D", "F"), ("C", "E", "G", "B")]),
]

for label, chord_tones in progressions:
    # Collect all unique note names
    all_notes = set()
    for tones in chord_tones:
        all_notes.update(tones)

    key = Key.detect(*all_notes)
    chord_names = [Chord.from_tones(*t).identify() for t in chord_tones]
    print(f"  {label:15s}  {' → '.join(chord_names):40s}  →  {key}")

# ── All 24 Keys ─────────────────────────────────────────────────────────

print()
print("All 24 Major and Minor Keys")
print("=" * 55)
print()

for key in Key.all_keys():
    sig = key.signature
    acc = ", ".join(sig["accidentals"]) if sig["accidentals"] else "none"
    rel = key.relative
    print(
        f"  {str(key):12s}  "
        f"{sig['sharps']}# {sig['flats']}b  "
        f"({acc:15s})  "
        f"rel: {rel}"
    )
