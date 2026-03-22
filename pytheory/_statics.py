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
    ],
    # Indian classical (Hindustani) system.
    # Ordered A-based to match Western index positions (Sa = index 3 = C).
    "indian": [
        ("Dha",),           # A  — shuddha dhaivat
        ("komal Ni",),      # Bb — komal nishad
        ("Ni",),            # B  — shuddha nishad
        ("Sa",),            # C  — shadja
        ("komal Re",),      # Db — komal rishabh
        ("Re",),            # D  — shuddha rishabh
        ("komal Ga",),      # Eb — komal gandhar
        ("Ga",),            # E  — shuddha gandhar
        ("Ma",),            # F  — shuddha madhyam
        ("tivra Ma",),      # F# — tivra madhyam
        ("Pa",),            # G  — pancham
        ("komal Dha",),     # Ab — komal dhaivat
    ],
    # Arabic maqam system — Arabic solfège names.
    "arabic": [
        ("La",),            # A
        ("Sib",),           # Bb — Si bemol
        ("Si",),            # B
        ("Do",),            # C
        ("Reb",),           # Db — Re bemol
        ("Re",),            # D
        ("Mib",),           # Eb — Mi bemol
        ("Mi",),            # E
        ("Fa",),            # F
        ("Fa#",),           # F#
        ("Sol",),           # G
        ("Solb",),          # Ab — Sol bemol
    ],
    # Japanese system — uses Western names; scales are the unique part.
    "japanese": [
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
    ],
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
    ],
    "indian": [
        ("shadja", ()),      # Sa — the tonic
        ("rishabh", ()),     # Re — 2nd
        ("gandhar", ()),     # Ga — 3rd
        ("madhyam", ()),     # Ma — 4th
        ("pancham", ()),     # Pa — 5th
        ("dhaivat", ()),     # Dha — 6th
        ("nishad", ()),      # Ni — 7th
        ("saptak", ()),      # Sa — octave
    ],
    "arabic": [
        ("qarar", ()),       # 1st — root
        ("nawa", ()),        # 2nd
        ("thalth", ()),      # 3rd
        ("arba", ()),        # 4th
        ("khamis", ()),      # 5th
        ("sadis", ()),       # 6th
        ("sabi", ()),        # 7th
        ("jawab", ()),       # octave
    ],
    "japanese": [
        ("ichi", ()),        # 1st
        ("ni", ()),          # 2nd
        ("san", ()),         # 3rd
        ("shi", ()),         # 4th
        ("go", ()),          # 5th
        ("roku", ()),        # 6th (pentatonic scales skip some)
    ],
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

# Indian scales — the 10 thaats of Hindustani classical music.
# Each thaat defines a parent scale from which ragas are derived.
INDIAN_SCALES = {
    12: {
        "chromatic": (12, {}),
        "thaat": [
            7,
            {
                # Bilawal = Western major / Ionian
                "bilawal": {"intervals": (2, 2, 1, 2, 2, 2, 1)},
                # Khamaj = Western Mixolydian
                "khamaj": {"intervals": (2, 2, 1, 2, 2, 1, 2)},
                # Kafi = Western Dorian
                "kafi": {"intervals": (2, 1, 2, 2, 2, 1, 2)},
                # Asavari = Western natural minor / Aeolian
                "asavari": {"intervals": (2, 1, 2, 2, 1, 2, 2)},
                # Bhairavi = Western Phrygian
                "bhairavi": {"intervals": (1, 2, 2, 2, 1, 2, 2)},
                # Kalyan = Western Lydian
                "kalyan": {"intervals": (2, 2, 2, 1, 2, 2, 1)},
                # Bhairav — unique to Indian music (no Western equivalent)
                # Sa re Ga Ma Pa dha Ni
                "bhairav": {"intervals": (1, 3, 1, 2, 1, 3, 1)},
                # Poorvi — unique to Indian music
                # Sa re Ga tivra-Ma Pa dha Ni
                "poorvi": {"intervals": (1, 3, 2, 1, 1, 3, 1)},
                # Marwa — unique to Indian music
                # Sa re Ga tivra-Ma Pa Dha Ni
                "marwa": {"intervals": (1, 3, 2, 1, 2, 2, 1)},
                # Todi — unique to Indian music
                # Sa re komal-Ga tivra-Ma Pa dha Ni
                "todi": {"intervals": (1, 2, 3, 1, 1, 3, 1)},
            },
        ],
    }
}

# Arabic maqam scales (12-TET approximations).
# True maqam uses quarter-tones; these are the closest 12-tone equivalents.
ARABIC_SCALES = {
    12: {
        "chromatic": (12, {}),
        "maqam": [
            7,
            {
                # Ajam = Western major
                "ajam": {"intervals": (2, 2, 1, 2, 2, 2, 1)},
                # Nahawand = Western harmonic minor
                "nahawand": {"intervals": (2, 1, 2, 2, 1, 3, 1)},
                # Kurd = Western Phrygian
                "kurd": {"intervals": (1, 2, 2, 2, 1, 2, 2)},
                # Hijaz — augmented 2nd between 2nd and 3rd degrees
                "hijaz": {"intervals": (1, 3, 1, 2, 1, 2, 2)},
                # Nikriz — augmented 2nd between 3rd and 4th
                "nikriz": {"intervals": (2, 1, 3, 1, 2, 1, 2)},
                # Bayati (12-TET approx) — true bayati has quarter-flat 2nd
                "bayati": {"intervals": (1, 2, 2, 2, 1, 2, 2)},
                # Rast (12-TET approx) — true rast has quarter-flat 3rd and 7th
                "rast": {"intervals": (2, 1, 2, 2, 2, 1, 2)},
                # Saba (12-TET approx) — true saba has quarter-flat 2nd
                "saba": {"intervals": (1, 2, 1, 3, 1, 2, 2)},
                # Sikah (12-TET approx) — true sikah starts on quarter-flat
                "sikah": {"intervals": (1, 2, 2, 2, 1, 2, 2)},
                # Jiharkah
                "jiharkah": {"intervals": (2, 2, 1, 2, 2, 1, 2)},
            },
        ],
    }
}

# Japanese pentatonic scales.
JAPANESE_SCALES = {
    12: {
        "chromatic": (12, {}),
        "pentatonic": [
            5,
            {
                # Hirajoshi — the most well-known Japanese scale
                # C D Eb G Ab
                "hirajoshi": {"intervals": (2, 1, 4, 1, 4)},
                # In (Miyako-bushi) — used in koto music
                # C Db F G Ab
                "in": {"intervals": (1, 4, 2, 1, 4)},
                # Yo — folk music scale
                # C D F G Bb
                "yo": {"intervals": (2, 3, 2, 3, 2)},
                # Iwato — dark, dissonant pentatonic
                # C Db F Gb Bb
                "iwato": {"intervals": (1, 4, 1, 4, 2)},
                # Kumoi — similar to minor pentatonic
                # C D Eb G A
                "kumoi": {"intervals": (2, 1, 4, 2, 3)},
                # Insen — modern Japanese scale
                # C Db F G Bb
                "insen": {"intervals": (1, 4, 2, 3, 2)},
            },
        ],
        "heptatonic": [
            7,
            {
                # Ritsu — gagaku court music scale
                # C D Eb F G A Bb (= Dorian)
                "ritsu": {"intervals": (2, 1, 2, 2, 2, 1, 2)},
                # Ryo — gagaku court music scale
                # C D E F# G A B (= Lydian)
                "ryo": {"intervals": (2, 2, 2, 1, 2, 2, 1)},
            },
        ],
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
