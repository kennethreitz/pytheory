"""Compare equal, Pythagorean, and meantone temperaments."""

import math
from pytheory import Tone

a4 = Tone.from_string("A4", system="western")

print("Temperament Comparison")
print("=" * 75)
print()
print(f"{'Note':>5s}  {'Equal (Hz)':>12s}  {'Pythag (Hz)':>12s}  {'Meantone (Hz)':>14s}  {'P diff':>8s}  {'M diff':>8s}")
print(f"{'─' * 5}  {'─' * 12}  {'─' * 12}  {'─' * 14}  {'─' * 8}  {'─' * 8}")

for semitones in range(13):
    tone = a4 + semitones

    equal = tone.pitch(temperament="equal")
    pyth = tone.pitch(temperament="pythagorean")
    mean = tone.pitch(temperament="meantone")

    # Difference in cents (1 cent = 1/100 of a semitone)
    pyth_cents = 1200 * math.log2(pyth / equal) if pyth > 0 else 0
    mean_cents = 1200 * math.log2(mean / equal) if mean > 0 else 0

    print(
        f"{tone.name:>5s}  {equal:>12.3f}  {pyth:>12.3f}  {mean:>14.3f}"
        f"  {pyth_cents:>+7.1f}¢  {mean_cents:>+7.1f}¢"
    )

print()
print("Key intervals to listen for:")
print()

intervals = [
    (4, "Major 3rd", "Meantone is pure (5:4), equal is sharp, Pythagorean sharper still"),
    (7, "Perfect 5th", "Pythagorean is pure (3:2), equal is slightly flat, meantone flatter"),
    (6, "Tritone", "The 'devil's interval' — all three temperaments handle it differently"),
]

for semitones, name, note in intervals:
    tone = a4 + semitones
    equal = tone.pitch(temperament="equal")
    pyth = tone.pitch(temperament="pythagorean")
    mean = tone.pitch(temperament="meantone")

    print(f"  {name} ({a4.name}→{tone.name}):")
    print(f"    Equal: {equal:.3f} Hz  |  Pythagorean: {pyth:.3f} Hz  |  Meantone: {mean:.3f} Hz")
    print(f"    {note}")
    print()
