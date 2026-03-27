from pytuning import scales

REFERENCE_A = 440

# Index of C in the Western tone list (A=0, A#=1, B=2, C=3, ...).
# Scientific pitch notation changes octave at C, not A, so this offset
# is needed for all octave arithmetic.
C_INDEX = 3
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
    # Blues/Pentatonic — Western names with blues and pentatonic scales.
    "blues": [
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
    # Javanese gamelan — pelog approximation in 12-TET.
    # True gamelan uses non-Western intonation; these are closest 12-TET fits.
    "gamelan": [
        ("nem",),           # A  — 6
        ("pi",),            # Bb — 7 (barang in some)
        ("barang",),        # B  — 7
        ("ji",),            # C  — 1
        ("ro-",),           # Db — 2b
        ("ro",),            # D  — 2
        ("lu-",),           # Eb — 3b
        ("lu",),            # E  — 3
        ("pat",),           # F  — 4
        ("pat+",),          # F# — 4#
        ("mo",),            # G  — 5
        ("nem-",),          # Ab — 6b
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
        ("roku", ()),        # 6th
    ],
    "blues": [
        ("tonic", ()),
        ("supertonic", ()),
        ("mediant", ()),
        ("subdominant", ()),
        ("dominant", ()),
        ("submediant", ()),
        ("subtonic", ()),
    ],
    "gamelan": [
        ("ji", ()),          # 1
        ("ro", ()),          # 2
        ("lu", ()),          # 3
        ("pat", ()),         # 4
        ("mo", ()),          # 5
        ("nem", ()),         # 6
        ("pi", ()),          # 7
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

# ── 22-shruti Indian system ──────────────────────────────────────────────────
# The shruti system divides the octave into 22 microtonal steps, capturing
# the melodic nuances that 12-TET cannot represent. Each of the 7 swaras
# has multiple shruti positions (e.g. komal Re at shruti 2, shuddha Re at
# shruti 4). 22-TET is the standard equal-tempered approximation.
#
# Ordered from Dha (=A) to match Western index positions (Sa at index 5 ≈ C).
TONES_SHRUTI = [
    ("Dha",),               #  0 — A  — shuddha dhaivat (reference = 440 Hz)
    ("atikomal Ni",),       #  1 — shruti between Dha and komal Ni
    ("komal Ni",),          #  2 — Bb — komal nishad
    ("shuddha Ni",),        #  3 — between komal Ni and Ni
    ("Ni",),                #  4 — B  — shuddha (kakali) nishad
    ("Sa",),                #  5 — C  — shadja (tonic)
    ("atikomal Re",),       #  6 — shruti between Sa and komal Re
    ("komal Re",),          #  7 — Db — komal rishabh
    ("shuddha Re",),        #  8 — between komal Re and Re
    ("Re",),                #  9 — D  — chatushruti rishabh
    ("atikomal Ga",),       # 10 — shruti between Re and komal Ga
    ("komal Ga",),          # 11 — Eb — komal gandhar
    ("Ga",),                # 12 — E  — antara gandhar
    ("tivra Ga",),          # 13 — shruti between Ga and Ma
    ("Ma",),                # 14 — F  — shuddha madhyam
    ("ekashruti Ma",),      # 15 — shruti between Ma and tivra Ma
    ("tivra Ma",),          # 16 — F# — tivra madhyam
    ("atitivra Ma",),       # 17 — shruti between tivra Ma and Pa
    ("Pa",),                # 18 — G  — pancham
    ("atikomal Dha",),      # 19 — shruti between Pa and komal Dha
    ("komal Dha",),         # 20 — Ab — komal dhaivat
    ("shuddha Dha",),       # 21 — shruti between komal Dha and Dha
]

DEGREES_SHRUTI = [
    ("shadja", ("bilawal",)),       # Sa — tonic
    ("rishabh", ("marwa",)),        # Re
    ("gandhar", ("bhairavi",)),     # Ga
    ("madhyam", ("kalyan",)),       # Ma
    ("pancham", ("kafi",)),         # Pa
    ("dhaivat", ("asavari",)),      # Dha
    ("nishad", ("khamaj",)),        # Ni
    ("shadja", ()),                 # Sa (octave)
]

# 22-shruti thaat scales with proper microtonal intervals.
# Each interval is counted in shrutis (22-TET steps).
# Compare to the 12-TET approximations in INDIAN_SCALES which lose
# the distinction between 2-shruti and 3-shruti steps.
SHRUTI_SCALES = {
    "chromatic": (22, {}),
    "thaat": [
        7,
        {
            # Bilawal (≈ Ionian) — Sa Re Ga Ma Pa Dha Ni
            "bilawal": {"intervals": (4, 3, 2, 4, 4, 3, 2)},
            # Khamaj (≈ Mixolydian) — Sa Re Ga Ma Pa Dha komal-Ni
            "khamaj": {"intervals": (4, 3, 2, 4, 4, 1, 4)},
            # Kafi (≈ Dorian) — Sa Re komal-Ga Ma Pa Dha komal-Ni
            "kafi": {"intervals": (4, 2, 3, 4, 4, 1, 4)},
            # Asavari (≈ Aeolian) — Sa Re komal-Ga Ma Pa komal-Dha komal-Ni
            "asavari": {"intervals": (4, 2, 3, 4, 2, 3, 4)},
            # Bhairavi (≈ Phrygian) — Sa komal-Re komal-Ga Ma Pa komal-Dha komal-Ni
            "bhairavi": {"intervals": (2, 4, 3, 4, 2, 3, 4)},
            # Bhairav — Sa komal-Re Ga Ma Pa komal-Dha Ni (unique to Indian music)
            "bhairav": {"intervals": (2, 5, 2, 4, 2, 5, 2)},
            # Kalyan (≈ Lydian) — Sa Re Ga tivra-Ma Pa Dha Ni
            "kalyan": {"intervals": (4, 3, 4, 2, 4, 3, 2)},
            # Marwa — Sa komal-Re Ga tivra-Ma Pa Dha Ni (unique)
            "marwa": {"intervals": (2, 5, 4, 2, 4, 3, 2)},
            # Poorvi — Sa komal-Re Ga tivra-Ma Pa komal-Dha Ni (unique)
            "poorvi": {"intervals": (2, 5, 4, 2, 2, 5, 2)},
            # Todi — Sa komal-Re komal-Ga tivra-Ma Pa komal-Dha Ni (unique)
            "todi": {"intervals": (2, 4, 5, 2, 2, 5, 2)},
        },
    ],
    "pentatonic": [
        5,
        {
            # Bhupali (≈ major pentatonic) — Sa Re Ga Pa Dha
            "bhupali": {"intervals": (4, 3, 6, 4, 5)},
            # Malkauns — Sa komal-Ga Ma komal-Dha komal-Ni
            "malkauns": {"intervals": (6, 3, 4, 5, 4)},
            # Durga — Sa Re Ma Pa Dha
            "durga": {"intervals": (4, 5, 4, 4, 5)},
            # Bhairavi pentatonic — Sa komal-Re Ma Pa komal-Ni
            "bhairavi pentatonic": {"intervals": (2, 7, 4, 2, 7)},
        },
    ],
}

# ── 24-TET Arabic maqam system ─────────────────────────────────────────────
# Arabic maqam uses quarter-tones (half-flat, half-sharp). 24-TET captures
# these intervals exactly. Each step = 50 cents (vs 100 in 12-TET).
# The half-flat (♭½) is the defining sound of Arabic music — it's what
# makes maqam Rast and Bayati sound distinctly Middle Eastern.
#
# Ordered from La (=A) to match Western index positions.
TONES_ARABIC_24 = [
    ("La",),                #  0 — A
    ("La↑",),               #  1 — A quarter-sharp
    ("Sib",),               #  2 — Bb
    ("Si↓",),               #  3 — B quarter-flat
    ("Si",),                #  4 — B
    ("Do",),                #  5 — C
    ("Do↑",),               #  6 — C quarter-sharp
    ("Reb",),               #  7 — Db
    ("Re↓",),               #  8 — D quarter-flat
    ("Re",),                #  9 — D
    ("Re↑",),               # 10 — D quarter-sharp
    ("Mib",),               # 11 — Eb
    ("Mi↓",),               # 12 — E quarter-flat
    ("Mi",),                # 13 — E
    ("Fa",),                # 14 — F
    ("Fa↑",),               # 15 — F quarter-sharp
    ("Fa#",),               # 16 — F#
    ("Sol↓",),              # 17 — G quarter-flat
    ("Sol",),               # 18 — G
    ("Sol↑",),              # 19 — G quarter-sharp
    ("Lab",),               # 20 — Ab
    ("La↓",),               # 21 — A quarter-flat
    ("La½b",),              # 22 — between Ab and A (rarely used)
    ("La♮",),               # 23 — enharmonic A (rarely used)
]

DEGREES_ARABIC_24 = [
    ("tonic", ()),
    ("second", ()),
    ("third", ()),
    ("fourth", ()),
    ("fifth", ()),
    ("sixth", ()),
    ("seventh", ()),
    ("octave", ()),
]

# 24-TET maqam scales with true quarter-tone intervals.
# Each step = 1 quarter-tone (50 cents). A 12-TET semitone = 2 steps.
ARABIC_24_SCALES = {
    "chromatic": (24, {}),
    "maqam": [
        7,
        {
            # Rast — the foundational maqam. E and B are quarter-flat.
            # Do Re Mi↓ Fa Sol La Si↓ Do
            "rast": {"intervals": (4, 3, 3, 4, 4, 3, 3)},
            # Bayati — starts on D with quarter-flat 2nd.
            # Re Mi↓ Fa Sol La Sib Do Re
            "bayati": {"intervals": (3, 3, 4, 4, 2, 4, 4)},
            # Saba — similar to Bayati with flattened 4th
            "saba": {"intervals": (3, 3, 2, 6, 2, 4, 4)},
            # Sikah — starts on E quarter-flat
            "sikah": {"intervals": (3, 4, 3, 4, 3, 4, 3)},
            # Hijaz — augmented 2nd (6 quarter-tones) between 2nd and 3rd
            "hijaz": {"intervals": (2, 6, 2, 4, 2, 4, 4)},
            # Nahawand (≈ harmonic minor)
            "nahawand": {"intervals": (4, 2, 4, 4, 2, 6, 2)},
            # Ajam (≈ major)
            "ajam": {"intervals": (4, 4, 2, 4, 4, 4, 2)},
            # Kurd (≈ Phrygian)
            "kurd": {"intervals": (2, 4, 4, 4, 2, 4, 4)},
            # Nikriz — augmented 2nd between 3rd and 4th
            "nikriz": {"intervals": (4, 2, 6, 2, 4, 2, 4)},
            # Jiharkah — like Rast but with natural B
            "jiharkah": {"intervals": (4, 4, 2, 4, 4, 3, 3)},
        },
    ],
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

# Blues and pentatonic scales — foundational to American music.
BLUES_SCALES = {
    12: {
        "chromatic": (12, {}),
        "pentatonic": [
            5,
            {
                # Major pentatonic — C D E G A
                "major pentatonic": {"intervals": (2, 2, 3, 2, 3)},
                # Minor pentatonic — C Eb F G Bb
                "minor pentatonic": {"intervals": (3, 2, 2, 3, 2)},
            },
        ],
        "hexatonic": [
            6,
            {
                # Blues scale — C Eb F F# G Bb
                "blues": {"intervals": (3, 2, 1, 1, 3, 2)},
                # Major blues — C D D# E G A
                "major blues": {"intervals": (2, 1, 1, 3, 2, 3)},
            },
        ],
        "heptatonic": [
            7,
            {
                # Mixolydian (dominant blues sound) — C D E F G A Bb
                "dominant": {"intervals": (2, 2, 1, 2, 2, 1, 2)},
                # Dorian (minor blues/jazz) — C D Eb F G A Bb
                "minor": {"intervals": (2, 1, 2, 2, 2, 1, 2)},
            },
        ],
    }
}

# Javanese gamelan scales — 12-TET approximations.
# True gamelan tuning varies between ensembles and does not conform
# to equal temperament. These approximations capture the melodic
# character of the scales.
GAMELAN_SCALES = {
    12: {
        "chromatic": (12, {}),
        "pentatonic": [
            5,
            {
                # Slendro — roughly equal 5-tone division of the octave
                # Approximated as: C D F G Bb
                "slendro": {"intervals": (2, 3, 2, 3, 2)},
                # Pelog pathet nem — C Db E F G (approx)
                "pelog nem": {"intervals": (1, 3, 1, 2, 5)},
                # Pelog pathet barang — C Db E F# B (approx)
                "pelog barang": {"intervals": (1, 3, 3, 4, 1)},
                # Pelog pathet lima — C Db E F Ab (approx)
                "pelog lima": {"intervals": (1, 3, 1, 3, 4)},
            },
        ],
        "heptatonic": [
            7,
            {
                # Full pelog — all 7 tones: C Db E F G Ab B (approx)
                "pelog": {"intervals": (1, 3, 1, 2, 1, 3, 1)},
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
