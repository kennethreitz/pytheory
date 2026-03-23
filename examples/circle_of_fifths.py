"""Visualize the circle of fifths with key signatures."""

from pytheory import Tone, Key

c = Tone.from_string("C4", system="western")

print("╔══════════════════════════════════════════════╗")
print("║          THE CIRCLE OF FIFTHS                ║")
print("╠══════════════════════════════════════════════╣")
print("║  Key     Sig    Accidentals                  ║")
print("╠══════════════════════════════════════════════╣")

for tone in c.circle_of_fifths():
    key = Key(tone.name, "major")
    sig = key.signature
    relative = key.relative

    if sig["sharps"]:
        mark = f'{sig["sharps"]}#'
    elif sig["flats"]:
        mark = f'{sig["flats"]}b'
    else:
        mark = "--"

    accidentals = ", ".join(sig["accidentals"]) if sig["accidentals"] else "none"
    print(f"║  {tone.name:3s}     {mark:3s}   {accidentals:20s}  rel: {relative.tonic_name} {relative.mode:5s} ║")

print("╚══════════════════════════════════════════════╝")

# Show that 12 fifths returns to the start
print()
print("Proof: 12 perfect fifths cycle through all 12 tones")
names = [t.name for t in c.circle_of_fifths()]
print(f"  {' → '.join(names)} → {names[0]}")
