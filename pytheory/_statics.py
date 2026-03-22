from pytuning import scales

REFERENCE_A = 440
TEMPERAMENTS = {
    "equal": scales.create_edo_scale,
    "pythagorean": scales.create_pythagorean_scale,
    "meantone": scales.create_quarter_comma_meantone_scale,
}

TONES = {
    "western": [
        ("A",),
        ("A#", "Bb"),
        ("B",),
        ("C",),
        ("C#", "Db"),
        ("D",),
        ("D#", "Eb"),
        ("E",),
        ("F",),
        ("F#", "Gb"),
        ("G",),
        ("G#", "Ab"),
    ]
}

DEGREES = {
    "western": [
        ("tonic", ("ionian", "aeolian")),
        ("supertonic", ("dorian", "locrian")),
        ("mediant", ("phrygian", "ionian")),
        ("subdominant", ("lydian", "dorian")),
        ("dominant", ("mixolydian", "phrygian")),
        ("submediant", ("aeolian", "lydian")),
        ("leading tone", ("locrian", "mixolydian")),
        ("octave", ("ionian", "aeolian")),
    ]
}

SCALES = {
    # Number of semitones.
    12: {
        # scale type: number of tones.
        "chromatic": (12, {}),
        # "octatonic": (8, {}),
        "heptatonic": [
            7,
            {
                "major": {"major": True, "hemitonic": True},
                "minor": {"minor": True, "hemitonic": True},
                "harmonic minor": {"minor": True, "harmonic": True, "hemitonic": True},
                # "melodic minor": {"minor": True, "melodic": True, "hemitonic": True},
            },
        ],
        # TODO: understand this
        # "hexatonic": (
        #     6,
        #     {
        #         # name, arguments to scale generator.
        #         "wholetone": {},
        #         "augmented": {},
        #         "prometheus": {},
        #         "blues": {},
        #     },
        # ),
        # "pentatonic": (5, {}),
        # "tetratonic": (4, {}),
        # "monotonic": (1, {"monotonic": {"hemitonic": False}}),
    }
}

SYSTEMS = NotImplemented

# Modes are rotations of the major scale pattern.
# Each mode's offset is its position in the major scale.
_MODES = {
    "ionian": 0,
    "dorian": 1,
    "phrygian": 2,
    "lydian": 3,
    "mixolydian": 4,
    "aeolian": 5,
    "locrian": 6,
}

for mode_name, offset in _MODES.items():
    SCALES[12]["heptatonic"][1][mode_name] = {
        "major": True, "hemitonic": True, "offset": offset
    }
