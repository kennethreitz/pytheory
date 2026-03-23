"""Explore a key — its chords, progressions, and relationships."""

from pytheory import Key

def explore_key(tonic, mode="major"):
    key = Key(tonic, mode)
    sig = key.signature
    acc = ", ".join(sig["accidentals"]) or "none"

    print(f"{'=' * 60}")
    print(f"  {key}")
    print(f"{'=' * 60}")
    print()
    print(f"  Scale:       {' '.join(key.note_names)}")
    print(f"  Signature:   {sig['sharps']} sharps, {sig['flats']} flats ({acc})")
    print(f"  Relative:    {key.relative}")
    print(f"  Parallel:    {key.parallel}")
    print()

    # Diatonic triads
    print("  Diatonic Triads:")
    for chord in key.scale.harmonize():
        numeral = chord.analyze(tonic, mode) or "?"
        print(f"    {numeral:6s}  {chord.identify()}")
    print()

    # Seventh chords
    print("  Seventh Chords:")
    for name in key.seventh_chords:
        print(f"    {name}")
    print()

    # Common progressions
    print("  Common Progressions:")
    progressions = {
        "Pop":     ("I", "V", "vi", "IV"),
        "Blues":   ("I", "IV", "V"),
        "50s":     ("I", "vi", "IV", "V"),
        "Jazz":    ("ii", "V", "I"),
    }
    for label, numerals in progressions.items():
        chords = key.progression(*numerals)
        names = [c.identify() for c in chords]
        print(f"    {label:8s}  {' → '.join(numerals):20s}  {' → '.join(names)}")
    print()

    # Borrowed chords
    borrowed = key.borrowed_chords
    if borrowed:
        print(f"  Borrowed from {key.parallel}:")
        for name in borrowed[:4]:
            print(f"    {name}")
        print()


# Explore several keys
for tonic, mode in [("C", "major"), ("G", "major"), ("A", "minor"), ("E", "major")]:
    explore_key(tonic, mode)
