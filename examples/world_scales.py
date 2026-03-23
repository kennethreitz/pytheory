"""Explore scales from six musical traditions around the world."""

from pytheory import TonedScale

systems = [
    ("western", "C4", [
        ("major", "The foundation of Western tonal music"),
        ("minor", "Natural minor — dark and introspective"),
        ("harmonic minor", "Raised 7th — classical, Middle Eastern flavor"),
        ("dorian", "Jazz, funk, soul (So What, Scarborough Fair)"),
        ("mixolydian", "Blues, rock (Norwegian Wood, Sweet Home Alabama)"),
        ("phrygian", "Flamenco, metal (White Rabbit)"),
        ("lydian", "Dreamy, floating (The Simpsons theme)"),
    ]),
    ("indian", "Sa4", [
        ("bilawal", "Equivalent to Western major scale"),
        ("bhairav", "Morning raga — devotional, meditative"),
        ("kafi", "Equivalent to Dorian mode — romantic, earthy"),
        ("bhairavi", "Equivalent to Phrygian — melancholic, devotional"),
        ("kalyan", "Equivalent to Lydian — serene, uplifting"),
    ]),
    ("arabic", "Do4", [
        ("ajam", "Equivalent to Western major scale"),
        ("hijaz", "The quintessential 'Middle Eastern' sound"),
        ("bayati", "Contemplative, spiritual — most common maqam"),
        ("rast", "Bright, festive — the 'mother' of maqamat"),
        ("nahawand", "Equivalent to Western minor — melancholic"),
    ]),
    ("japanese", "C4", [
        ("hirajoshi", "Haunting pentatonic — koto music"),
        ("in", "Dark pentatonic — court music, Buddhist chant"),
        ("yo", "Bright pentatonic — folk songs, festival music"),
        ("iwato", "Sparse, mysterious — zen atmosphere"),
        ("kumoi", "Gentle pentatonic — lyrical, nostalgic"),
        ("ritsu", "Elegant heptatonic — gagaku court music"),
    ]),
    ("blues", "C4", [
        ("blues", "The 6-note blues scale with the 'blue note'"),
        ("minor pentatonic", "The backbone of rock guitar solos"),
        ("major pentatonic", "Bright, open — country, folk, pop"),
    ]),
    ("gamelan", "nem4", [
        ("slendro", "5-note near-equal division — metallic, shimmering"),
        ("pelog", "7-note unequal — mysterious, otherworldly"),
        ("pelog nem", "Pelog mode on nem — the most common mode"),
        ("pelog barang", "Pelog mode on barang — bright, festive"),
    ]),
]

for system_name, tonic, scales in systems:
    print(f"{'═' * 65}")
    print(f"  {system_name.upper()}")
    print(f"{'═' * 65}")

    ts = TonedScale(tonic=tonic, system=system_name)

    for scale_name, description in scales:
        try:
            scale = ts[scale_name]
            notes = " ".join(scale.note_names)
            print(f"  {scale_name:20s}  {notes}")
            print(f"  {'':20s}  {description}")
            print()
        except (KeyError, IndexError, ValueError):
            print(f"  {scale_name:20s}  (not available)")
            print()

print(f"{'═' * 65}")
