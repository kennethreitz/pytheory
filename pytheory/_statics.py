from pytuning import scales

REFERENCE_A = 440

# Index of C in the Western tone list (A=0, A#=1, B=2, C=3, ...).
# Scientific pitch notation changes octave at C, not A, so this offset
# is needed for all octave arithmetic.
C_INDEX = 3
def _create_just_intonation_scale(n):
    """5-limit just intonation ratios for 12-tone systems.

    These are the pure frequency ratios derived from the harmonic series —
    the way intervals "want" to sound before equal temperament imposed
    compromise. Each ratio is mathematically exact: a perfect fifth is
    exactly 3/2, a major third is exactly 5/4.

    For non-12 systems, falls back to equal temperament.
    """
    from fractions import Fraction
    if n != 12:
        return scales.create_edo_scale(n)
    # Standard 5-limit JI ratios (A-based: A=1/1)
    ratios = [
        Fraction(1, 1),       # A  — unison
        Fraction(16, 15),     # A# — minor second
        Fraction(9, 8),       # B  — major second
        Fraction(6, 5),       # C  — minor third
        Fraction(5, 4),       # C# — major third
        Fraction(4, 3),       # D  — perfect fourth
        Fraction(45, 32),     # D# — augmented fourth
        Fraction(3, 2),       # E  — perfect fifth
        Fraction(8, 5),       # F  — minor sixth
        Fraction(5, 3),       # F# — major sixth
        Fraction(9, 5),       # G  — minor seventh
        Fraction(15, 8),      # G# — major seventh
        Fraction(2, 1),       # A  — octave
    ]
    return [float(r) for r in ratios]

TEMPERAMENTS = {
    "equal": scales.create_edo_scale,
    "pythagorean": scales.create_pythagorean_scale,
    "meantone": scales.create_quarter_comma_meantone_scale,
    "just": _create_just_intonation_scale,
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

# 22-shruti frequency ratios — 5-limit just intonation.
# These are the REAL shruti intervals, NOT 22-TET approximations.
# Based on the traditional Pythagorean/harmonic ratios from Indian
# musicological treatises (Natya Shastra, Sangita Ratnakara).
#
# Ordered from Dha (A=1.0) to match our system indexing.
# Sa is at index 5 (ratio ≈ 6/5 from Dha).
from fractions import Fraction
_SHRUTI_RATIOS_FROM_SA = [
    Fraction(1, 1),       #  0: Sa        — 1/1
    Fraction(256, 243),   #  1: atikomal Re — Pythagorean limma
    Fraction(16, 15),     #  2: komal Re   — JI minor second
    Fraction(10, 9),      #  3: shuddha Re — minor whole tone
    Fraction(9, 8),       #  4: Re         — major whole tone
    Fraction(32, 27),     #  5: atikomal Ga — Pythagorean minor 3rd
    Fraction(6, 5),       #  6: komal Ga   — JI minor 3rd
    Fraction(5, 4),       #  7: Ga         — JI major 3rd
    Fraction(81, 64),     #  8: tivra Ga   — Pythagorean major 3rd
    Fraction(4, 3),       #  9: Ma         — perfect 4th
    Fraction(27, 20),     # 10: ekashruti Ma
    Fraction(45, 32),     # 11: tivra Ma   — augmented 4th
    Fraction(729, 512),   # 12: atitivra Ma — Pythagorean tritone
    Fraction(3, 2),       # 13: Pa         — perfect 5th
    Fraction(128, 81),    # 14: atikomal Dha — Pythagorean minor 6th
    Fraction(8, 5),       # 15: komal Dha  — JI minor 6th
    Fraction(5, 3),       # 16: shuddha Dha
    Fraction(27, 16),     # 17: Dha        — Pythagorean major 6th
    Fraction(16, 9),      # 18: komal Ni   — Pythagorean minor 7th
    Fraction(9, 5),       # 19: shuddha Ni — JI minor 7th
    Fraction(15, 8),      # 20: Ni         — JI major 7th
    Fraction(243, 128),   # 21: tivra Ni   — Pythagorean major 7th
]

# Rotate to start from Dha (index 17 in the Sa-based list above).
# Dha = 27/16 from Sa. We divide all ratios by 27/16 and wrap.
_dha_ratio = _SHRUTI_RATIOS_FROM_SA[17]
SHRUTI_RATIOS = []
for i in range(22):
    sa_idx = (i + 17) % 22  # rotate: Dha=0, komalNi=1, ..., Sa=5, ...
    r = _SHRUTI_RATIOS_FROM_SA[sa_idx] / _dha_ratio
    if r < 1:
        r *= 2  # wrap into the same octave
    SHRUTI_RATIOS.append(float(r))

# 22-shruti thaat scales with proper microtonal intervals.
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

# ── Arabic maqam system ───────────────────────────────────────────────────
# Arabic maqam uses quarter-tones with specific JI ratios, NOT equal
# 24-TET divisions. The neutral intervals (quarter-flat, quarter-sharp)
# are based on ratios involving the 11th partial, as theorized by
# Zalzal (8th century Baghdad). The quarter-flat E in Rast is 27/22,
# not simply halfway between Eb and E.
#
# 24 positions per octave, but with unequal JI spacing.
# Ordered from La (=A) to match Western index positions.

# Maqam JI ratios from Do (C). Based on traditional practice:
# - Standard JI intervals for the 12 chromatic positions
# - Zalzalian ratios (11-limit) for the quarter-tone positions
_MAQAM_RATIOS_FROM_DO = [
    Fraction(1, 1),       #  0: Do       — unison
    Fraction(33, 32),     #  1: Do↑      — quarter-sharp (~53¢, 33rd harmonic)
    Fraction(16, 15),     #  2: Reb      — JI minor 2nd
    Fraction(12, 11),     #  3: Re↓      — Zalzalian neutral 2nd (~151¢)
    Fraction(9, 8),       #  4: Re       — major whole tone
    Fraction(11, 9) * Fraction(1, 1),  #  5: Re↑  — undecimal (~347¢... too high)
    Fraction(6, 5),       #  6: Mib      — JI minor 3rd
    Fraction(27, 22),     #  7: Mi↓      — Zalzalian neutral 3rd (~355¢) THE Rast note
    Fraction(5, 4),       #  8: Mi       — JI major 3rd
    Fraction(4, 3),       #  9: Fa       — perfect 4th
    Fraction(11, 8),      # 10: Fa↑      — undecimal tritone (~551¢)
    Fraction(45, 32),     # 11: Fa#      — augmented 4th
    Fraction(22, 15),     # 12: Sol↓     — neutral (~663¢... adjusted)
    Fraction(3, 2),       # 13: Sol      — perfect 5th
    Fraction(99, 64),     # 14: Sol↑     — quarter-sharp 5th
    Fraction(8, 5),       # 15: Lab      — JI minor 6th
    Fraction(18, 11),     # 16: La↓      — Zalzalian neutral 6th
    Fraction(5, 3),       # 17: La       — JI major 6th
    Fraction(27, 16),     # 18: La↑/Sib↓ — Pythagorean major 6th
    Fraction(16, 9),      # 19: Sib      — Pythagorean minor 7th
    Fraction(11, 6),      # 20: Si↓      — undecimal neutral 7th
    Fraction(15, 8),      # 21: Si       — JI major 7th
    Fraction(243, 128),   # 22: Si↑      — Pythagorean major 7th
    Fraction(2, 1) * Fraction(33, 64),  # 23: near-octave (~1049¢)
]

# Ratios directly from La (A=1/1), each position defined explicitly.
# Standard JI intervals for chromatic positions, Zalzalian (11-limit)
# ratios for the quarter-tone positions.
MAQAM_RATIOS = [
    1.0,                              #  0: La       — A (unison)
    float(Fraction(256, 243)),        #  1: La↑      — Pythagorean comma up
    float(Fraction(16, 15)),          #  2: Sib      — Bb (JI minor 2nd)
    float(Fraction(12, 11)),          #  3: Si↓      — B quarter-flat (Zalzalian)
    float(Fraction(9, 8)),            #  4: Si       — B (major 2nd)
    float(Fraction(6, 5)),            #  5: Do       — C (minor 3rd from A)
    float(Fraction(11, 9)),           #  6: Do↑      — C quarter-sharp (undecimal)
    float(Fraction(5, 4)),            #  7: Reb      — Db (major 3rd from A...= JI Db)
    float(Fraction(9, 7)),            #  8: Re↓      — D quarter-flat (septimal)
    float(Fraction(4, 3)),            #  9: Re       — D (perfect 4th from A)
    float(Fraction(11, 8)),           # 10: Re↑      — D quarter-sharp (undecimal)
    float(Fraction(45, 32)),          # 11: Mib      — Eb (augmented 4th from A)
    float(Fraction(6, 5) * Fraction(27, 22)),  # 12: Mi↓ — E quarter-flat (Do × 27/22)
    float(Fraction(3, 2)),            # 13: Mi       — E (perfect 5th from A)
    float(Fraction(8, 5)),            # 14: Fa       — F (minor 6th from A)
    float(Fraction(18, 11)),          # 15: Fa↑      — F quarter-sharp (Zalzalian)
    float(Fraction(5, 3)),            # 16: Fa#      — F# (major 6th from A)
    float(Fraction(27, 16)),          # 17: Sol↓     — G quarter-flat
    float(Fraction(16, 9)),           # 18: Sol      — G (minor 7th from A)
    float(Fraction(11, 6)),           # 19: Sol↑     — G quarter-sharp (undecimal)
    float(Fraction(15, 8)),           # 20: Lab      — Ab (major 7th from A)
    float(Fraction(27, 14)),          # 21: La↓      — A quarter-flat (septimal)
    float(Fraction(243, 128)),        # 22: La½b     — near-octave
    float(Fraction(2, 1) * Fraction(256, 257)),  # 23: La♮  — near-octave
]
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

# ── 5-TET Gamelan Slendro ────────────────────────────────────────────────────
# Slendro is a 5-tone equal temperament — each step is 240 cents.
# The actual tuning varies between gamelans (each set is unique), but
# 5-TET is the theoretical ideal that all slendro tunings approximate.
# Ordered from nem (≈A) to loosely match Western indexing.
TONES_SLENDRO = [
    ("nem",),       # 0 — 6 (≈A)
    ("ji",),        # 1 — 1 (≈C)
    ("ro",),        # 2 — 2 (≈D)
    ("lu",),        # 3 — 3 (≈F)
    ("mo",),        # 4 — 5 (≈G)
]

DEGREES_SLENDRO = [
    ("nem", ()), ("ji", ()), ("ro", ()), ("lu", ()), ("mo", ()),
]

SLENDRO_SCALES = {
    "chromatic": (5, {}),
    "pentatonic": [5, {
        # The full slendro IS the pentatonic — all 5 tones
        "slendro": {"intervals": (1, 1, 1, 1, 1)},
    }],
}

# ── 9-TET Gamelan Pelog ─────────────────────────────────────────────────────
# Pelog uses 7 tones from a roughly 9-step division of the octave.
# 9-TET (133 cents/step) approximates the unequal pelog intervals.
# The 3 pathet (modes) select 5 tones from the 7.
TONES_PELOG = [
    ("nem",),       # 0 — 6
    ("pi",),        # 1 — 7
    ("ji",),        # 2 — 1
    ("ro",),        # 3 — 2
    ("lu",),        # 4 — 3
    ("pat",),       # 5 — 4
    ("barang",),    # 6 — complementary
    ("mo",),        # 7 — 5
    ("nem+",),      # 8 — auxiliary
]

DEGREES_PELOG = [
    ("nem", ()), ("pi", ()), ("ji", ()), ("ro", ()),
    ("lu", ()), ("pat", ()), ("barang", ()), ("mo", ()), ("nem+", ()),
]

PELOG_SCALES = {
    "chromatic": (9, {}),
    "heptatonic": [7, {
        # Full pelog — 7 tones from 9 steps
        "pelog": {"intervals": (1, 2, 1, 1, 2, 1, 1)},
    }],
    "pentatonic": [5, {
        # Pathet nem — the most common mode
        "pelog nem": {"intervals": (1, 2, 2, 2, 2)},
        # Pathet lima
        "pelog lima": {"intervals": (1, 2, 2, 1, 3)},
        # Pathet barang
        "pelog barang": {"intervals": (2, 1, 2, 2, 2)},
    }],
}

# ── 7-TET Thai classical ────────────────────────────────────────────────────
# Thai classical music divides the octave into 7 exactly equal steps
# (~171 cents each). This is unique — no Western equivalent exists.
# The 7 tones are numbered 1-7 in Thai theory.
TONES_THAI = [
    ("do",),        # 0 — 1st degree
    ("re",),        # 1 — 2nd
    ("mi",),        # 2 — 3rd
    ("fa",),        # 3 — 4th
    ("sol",),       # 4 — 5th
    ("la",),        # 5 — 6th
    ("si",),        # 6 — 7th
]

DEGREES_THAI = [
    ("thang 1", ()), ("thang 2", ()), ("thang 3", ()),
    ("thang 4", ()), ("thang 5", ()), ("thang 6", ()), ("thang 7", ()),
]

THAI_SCALES = {
    "chromatic": (7, {}),
    "pentatonic": [5, {
        # The standard Thai pentatonic — 5 of 7 equal steps
        "thai pentatonic": {"intervals": (1, 1, 2, 1, 2)},
        # Alternate selection
        "thai pentatonic 2": {"intervals": (2, 1, 1, 2, 1)},
    }],
    "heptatonic": [7, {
        # The full 7-TET scale
        "thai": {"intervals": (1, 1, 1, 1, 1, 1, 1)},
    }],
}

# ── 53-TET Turkish makam (Arel-Ezgi-Uzdilek) ───────────────────────────────
# The gold standard for Turkish music theory. 53-TET has nearly perfect
# fifths (31 steps = 701.89 cents vs 701.96 just) and excellent thirds.
# A comma (1 step) = 22.6 cents. The basic intervals:
#   Bakiye (B) = 4 commas ≈ 90 cents (like a limma)
#   Küçük mücenneb (S) = 5 commas ≈ 113 cents
#   Büyük mücenneb (K) = 8 commas ≈ 181 cents
#   Tanini (T) = 9 commas ≈ 204 cents (like a whole tone)
TONES_TURKISH = [
    ("La",),                #  0 — A (Dügah reference)
    ("La+1",),              #  1
    ("La+2",),              #  2
    ("La+3",),              #  3
    ("Sib",),               #  4 — Bb (4 commas from A)
    ("Sib+1",),             #  5
    ("Sib+2",),             #  6
    ("Sib+3",),             #  7
    ("Sib+4",),             #  8
    ("Si",),                #  9 — B
    ("Si+1",),              # 10
    ("Si+2",),              # 11
    ("Si+3",),              # 12
    ("Do",),                # 13 — C (Rast)
    ("Do+1",),              # 14
    ("Do+2",),              # 15
    ("Do+3",),              # 16
    ("Do+4",),              # 17
    ("Reb",),               # 18 — Db
    ("Reb+1",),             # 19
    ("Reb+2",),             # 20
    ("Reb+3",),             # 21
    ("Re",),                # 22 — D (Dügah)
    ("Re+1",),              # 23
    ("Re+2",),              # 24
    ("Re+3",),              # 25
    ("Re+4",),              # 26
    ("Mib",),               # 27 — Eb
    ("Mib+1",),             # 28
    ("Mib+2",),             # 29
    ("Mib+3",),             # 30
    ("Mi",),                # 31 — E (Segah)
    ("Mi+1",),              # 32
    ("Mi+2",),              # 33
    ("Mi+3",),              # 34
    ("Mi+4",),              # 35
    ("Fa",),                # 36 — F
    ("Fa+1",),              # 37
    ("Fa+2",),              # 38
    ("Fa+3",),              # 39
    ("Fa#",),               # 40 — F#
    ("Fa#+1",),             # 41
    ("Fa#+2",),             # 42
    ("Fa#+3",),             # 43
    ("Sol",),               # 44 — G (Neva)
    ("Sol+1",),             # 45
    ("Sol+2",),             # 46
    ("Sol+3",),             # 47
    ("Lab",),               # 48 — Ab
    ("Lab+1",),             # 49
    ("Lab+2",),             # 50
    ("Lab+3",),             # 51
    ("Lab+4",),             # 52
]

DEGREES_TURKISH = [(f"perde {i+1}", ()) for i in range(53)]

# Turkish makam scales in 53-TET commas.
# T=9 commas (whole tone), S=5 (small), K=8 (large), B=4 (limma)
TURKISH_SCALES = {
    "chromatic": (53, {}),
    "makam": [
        7,
        {
            # Rast — the foundational makam. Uses segah (≈ neutral 3rd)
            # T + T + S + T + T + T + S = 9+9+5+9+9+9+4 = 53...
            # Actually: 9+8+5+9+9+8+5 = 53
            "rast": {"intervals": (9, 8, 5, 9, 9, 8, 5)},
            # Nihavend (≈ harmonic minor)
            "nihavend": {"intervals": (9, 4, 9, 9, 4, 13, 5)},
            # Hicaz — the augmented 2nd makam
            "hicaz": {"intervals": (5, 12, 5, 9, 4, 9, 9)},
            # Ussak — one of the most common makams
            "ussak": {"intervals": (8, 5, 9, 9, 8, 5, 9)},
            # Huseyni
            "huseyni": {"intervals": (8, 5, 9, 9, 5, 8, 9)},
            # Kurdi (≈ Phrygian)
            "kurdi": {"intervals": (4, 9, 9, 9, 4, 9, 9)},
            # Segah — starts on the neutral 3rd
            "segah": {"intervals": (5, 9, 9, 8, 5, 9, 8)},
            # Saba — descending differs from ascending
            "saba": {"intervals": (8, 5, 4, 14, 4, 9, 9)},
            # Hüzzam
            "huzzam": {"intervals": (5, 9, 8, 5, 9, 8, 9)},
        },
    ],
}

# ── 72-TET Carnatic (South Indian) ───────────────────────────────────────────
# The 72 melakarta system classifies all possible 7-note scales with
# fixed Sa and Pa. 72-TET (16.67 cents/step) captures the srutis used
# in Carnatic music with high precision. Each 12-TET semitone = 6 steps.
#
# Tone names: 12 swaras × 6 microtonal variants each.
# Main swaras at positions: Sa=0, Ri1=6, Ri2=12, Ga1=12, Ga2=18,
# Ma1=30, Ma2=36, Pa=42, Da1=48, Da2=54, Ni1=60, Ni2=66
TONES_CARNATIC = []
_SWARA_NAMES = [
    "Sa", "atikomal Ri", "komal Ri", "shuddha Ri",
    "Ri", "tivra Ri", "komal Ga", "atikomal Ga",
    "Ga", "shuddha Ga", "tivra Ga", "antara Ga",
    "komal Ma", "shuddha Ma", "Ma", "tivra shuddha Ma",
    "ekashruti Ma", "chatushruti Ma", "tivra Ma", "atitivra Ma",
    "prati Ma", "tivratara Ma", "atikomal Pa-", "komal Pa-",
    "shuddha Pa-", "Pa-", "Pa-+1", "Pa-+2",
    "Pa-+3", "Pa-+4", "Pa", "Pa+1",
    "Pa+2", "Pa+3", "Pa+4", "Pa+5",
    "komal Da", "atikomal Da", "Da-", "shuddha Da-",
    "Da", "shuddha Da", "tivra Da", "atitivra Da",
    "komal Ni", "atikomal Ni", "Ni-", "shuddha Ni-",
    "Ni", "shuddha Ni", "tivra Ni", "chatushruti Ni",
    "kakali Ni", "atikakali Ni",
]
# Generate 72 tone names: use standard names for the 12 main positions,
# numbered variants for the intermediates
for i in range(72):
    main_pos = i // 6  # which semitone group (0-11)
    micro = i % 6      # microtonal position within group
    _base_names = ["Sa", "komal Ri", "Ri", "komal Ga", "Ga", "Ma",
                   "tivra Ma", "Pa", "komal Da", "Da", "komal Ni", "Ni"]
    if micro == 0:
        TONES_CARNATIC.append((_base_names[main_pos],))
    else:
        TONES_CARNATIC.append((f"{_base_names[main_pos]}+{micro}",))

DEGREES_CARNATIC = [(f"swara {i+1}", ()) for i in range(72)]

# A selection of important melakartas in 72-TET intervals.
# Each step = 1/72 of an octave ≈ 16.67 cents.
CARNATIC_SCALES = {
    "chromatic": (72, {}),
    "melakarta": [
        7,
        {
            # Kanakangi (melakarta 1) — Sa Ri1 Ga1 Ma1 Pa Da1 Ni1
            "kanakangi": {"intervals": (6, 6, 18, 12, 6, 6, 18)},
            # Shankarabharanam (melakarta 29) — Sa Ri2 Ga3 Ma1 Pa Da2 Ni3
            # The Carnatic equivalent of the major scale
            "shankarabharanam": {"intervals": (12, 12, 6, 12, 12, 12, 6)},
            # Kalyani (melakarta 65) — Sa Ri2 Ga3 Ma2 Pa Da2 Ni3
            # Carnatic Lydian equivalent
            "kalyani": {"intervals": (12, 12, 12, 6, 12, 12, 6)},
            # Kharaharapriya (melakarta 22) — Sa Ri2 Ga2 Ma1 Pa Da2 Ni2
            # Carnatic Dorian equivalent
            "kharaharapriya": {"intervals": (12, 6, 12, 12, 12, 6, 12)},
            # Hanumathodi (melakarta 8) — Sa Ri1 Ga2 Ma1 Pa Da1 Ni2
            # Carnatic Phrygian equivalent
            "hanumathodi": {"intervals": (6, 12, 12, 12, 6, 12, 12)},
            # Natabhairavi (melakarta 20) — Sa Ri2 Ga2 Ma1 Pa Da1 Ni2
            # Natural minor equivalent
            "natabhairavi": {"intervals": (12, 6, 12, 12, 6, 12, 12)},
            # Mayamalavagowla (melakarta 15) — Sa Ri1 Ga3 Ma1 Pa Da1 Ni3
            # The "lesson scale" — first raga taught to students
            "mayamalavagowla": {"intervals": (6, 18, 6, 12, 6, 18, 6)},
            # Simhendramadhyamam (melakarta 57) — Sa Ri2 Ga3 Ma2 Pa Da1 Ni3
            "simhendramadhyamam": {"intervals": (12, 12, 12, 6, 6, 18, 6)},
            # Charukesi (melakarta 26) — Sa Ri2 Ga3 Ma1 Pa Da1 Ni2
            "charukesi": {"intervals": (12, 12, 6, 12, 6, 12, 12)},
            # Harikambhoji (melakarta 28) — Sa Ri2 Ga3 Ma1 Pa Da2 Ni2
            # Mixolydian equivalent
            "harikambhoji": {"intervals": (12, 12, 6, 12, 12, 6, 12)},
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
