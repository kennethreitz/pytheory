from ._statics import (
    TEMPERAMENTS, TONES, DEGREES, SCALES,
    INDIAN_SCALES, ARABIC_SCALES, JAPANESE_SCALES,
    BLUES_SCALES, GAMELAN_SCALES, SYSTEMS,
    TONES_SHRUTI, DEGREES_SHRUTI, SHRUTI_SCALES, SHRUTI_RATIOS,
    TONES_ARABIC_24, DEGREES_ARABIC_24, ARABIC_24_SCALES, MAQAM_RATIOS,
    TONES_SLENDRO, DEGREES_SLENDRO, SLENDRO_SCALES,
    TONES_PELOG, DEGREES_PELOG, PELOG_SCALES,
    TONES_THAI, DEGREES_THAI, THAI_SCALES,
    TONES_TURKISH, DEGREES_TURKISH, TURKISH_SCALES,
    TONES_CARNATIC, DEGREES_CARNATIC, CARNATIC_SCALES,
)


class System:
    def __init__(self, *, tone_names, degrees, scales=None, c_index=None,
                 period=2.0, ratios=None):
        self.tone_names = tone_names

        self.degrees = degrees
        self._scales = scales

        # Period: the frequency ratio of one "octave" in this system.
        # 2.0 for standard octave-based systems.
        # 3.0 for Bohlen-Pierce (tritave).
        self.period = period

        # Custom frequency ratios: if set, overrides equal temperament.
        # A list of N floats (one per tone), each relative to the first
        # tone (1.0). For example, just intonation shruti ratios.
        self.ratios = ratios

        # c_index: the index of the "reference C" in the tone list.
        # For octave arithmetic — scientific pitch changes octave at C.
        # Default 3 for 12-TET western (A=0, A#=1, B=2, C=3).
        # For non-12-TET systems, this is the index of the tone nearest C,
        # or 0 if no C equivalent exists.
        if c_index is not None:
            self.c_index = c_index
        else:
            # Try to find C in the tone names, fall back to 0
            self.c_index = 0
            for i, names in enumerate(tone_names):
                if "C" in names:
                    self.c_index = i
                    break

        if scales is None:
            n = self.semitones
            if n in SCALES:
                self._scales = SCALES[n]
            else:
                # Generate chromatic scale for unknown sizes
                self._scales = {
                    "chromatic": (n, {}),
                }

    @property
    def semitones(self):
        return len(self.tone_names)

    @property
    def tones(self):
        from . import Tone
        return tuple([Tone.from_tuple(tone) for tone in self.tone_names])

    def resolve_name(self, name: str) -> str | None:
        """Resolve a note name (including flats, double sharps/flats) to the canonical name.

        Handles enharmonic equivalents:
        - Standard names and their alternates (e.g. Bb, C#)
        - Double sharps (C## = D, F## = G)
        - Double flats (Dbb = C, Ebb = D)

        Returns the primary name if found, or None if not recognized.
        """
        # Direct lookup first
        for names in self.tone_names:
            if name in names:
                return names[0]

        # Handle double sharps (e.g. C## → D, F## → G)
        if name.endswith('##') and len(name) >= 3:
            base = name[:-2]
            base_idx = self._name_to_index(base)
            if base_idx is not None:
                resolved_idx = (base_idx + 2) % len(self.tone_names)
                return self.tone_names[resolved_idx][0]

        # Handle double flats (e.g. Dbb → C, Ebb → D)
        if name.endswith('bb') and len(name) >= 3 and name[0] != 'b':
            base = name[:-2]
            base_idx = self._name_to_index(base)
            if base_idx is not None:
                resolved_idx = (base_idx - 2) % len(self.tone_names)
                return self.tone_names[resolved_idx][0]

        # Handle single sharps/flats on natural notes (e.g. Cb → B, E# → F)
        if len(name) == 2:
            base = name[0]
            modifier = name[1]
            base_idx = self._name_to_index(base)
            if base_idx is not None:
                if modifier == '#':
                    resolved_idx = (base_idx + 1) % len(self.tone_names)
                    return self.tone_names[resolved_idx][0]
                elif modifier == 'b':
                    resolved_idx = (base_idx - 1) % len(self.tone_names)
                    return self.tone_names[resolved_idx][0]

        return None

    def _name_to_index(self, name: str) -> int | None:
        """Return the index of a tone name, or None if not found."""
        for i, names in enumerate(self.tone_names):
            if name in names:
                return i
        return None


    @property
    def scales(self):
        scales = {}

        for (scale_type, scale_properties) in self._scales.items():
            scales[scale_type] = {}

            tones = scale_properties[0]
            new_scales = scale_properties[1]

            if not new_scales:
                new_scales = {scale_type: {}}

            for scale in new_scales.items():
                scale_name = scale[0]
                scales[scale_type][scale_name] = self.generate_scale(
                    tones=tones, semitones=self.semitones, **scale[1]
                )
        return scales

    @property
    def modes(self):
        def gen():
            for i, degree in enumerate(self.degrees):
                for mode in degree[1]:
                    yield {"degree": (i + 1), "mode": mode}

        return [g for g in gen()]

    @staticmethod
    def generate_scale(
        *,
        tones=7,
        semitones=12,
        intervals=None,
        major=False,
        minor=False,
        hemitonic=False,  # Contains semitones.
        harmonic=False,
        melodic=False,
        offset=None,
    ):
        """Generates the primary scale for a given number of semitones/tones."""

        # Direct interval pattern — bypass generation logic.
        if intervals is not None:
            scale = list(intervals)
            if offset:
                scale = scale[offset:] + scale[:offset]
            return {"intervals": scale, "hemitonic": 1 in scale, "meta": {}}

        # Sanity check.
        if major and minor:
            raise ValueError("Scale cannot be both major and minor. Choose one.")

        def gen(tones, semitones, major, minor, harmonic, melodic, hemitonic):
            if major or minor:
                hemitonic = True
            # Assume chromatic scale, if neither major nor minor.
            if not (major or minor) and not hemitonic:
                for i in range(tones):
                    yield 1
            else:
                if hemitonic:
                    if major:
                        pattern = (2, 2, 1, 2, 2, 2, 1)
                    elif minor:
                        pattern = (2, 1, 2, 2, 1, 2, 2)
                        if harmonic:
                            pattern = (2, 1, 2, 2, 1, 3, 1)
                else:
                    pattern = None

                step_count = 0

                if pattern:
                    for step in pattern:
                        yield step
                else:
                    for i in range(tones):
                        yield 1

        scale = [
            g
            for g in gen(
                tones=tones,
                semitones=semitones,
                major=major,
                minor=minor,
                harmonic=harmonic,
                melodic=melodic,
                hemitonic=hemitonic,
            )
        ]

        if offset:
            scale = scale[offset:] + scale[:offset]

        # descending goes in meta?
        return {"intervals": scale, "hemitonic": hemitonic, "meta": {}}

    def tone(self, name, octave=4):
        """Create a Tone in this system. Shorthand for ``Tone(name, octave=octave, system=self)``.

        Example::

            >>> edo19 = TET(19)
            >>> edo19.tone(5, octave=4).frequency
        """
        from . import Tone
        return Tone(name, octave=octave, system=self)

    def __repr__(self):
        return f"<System semitones={self.semitones!r}>"


def TET(n, *, names=None, reference_index=0, period=2.0):
    """Create an N-tone equal temperament system.

    Each step divides the period into *n* equal parts. The frequency
    ratio between adjacent tones is ``period^(1/n)``.

    For standard tunings the period is 2.0 (octave). For exotic systems
    like Bohlen-Pierce, set ``period=3.0`` (tritave).

    Args:
        n: Number of equal divisions of the octave (e.g. 19, 24, 31, 53).
        names: Optional list of *n* tone name strings. If omitted,
            tones are numbered ``"0"`` through ``"n-1"``.
        reference_index: Index of the tone that corresponds to A440
            (default 0, meaning tone "0" = A4 = 440 Hz).

    Returns:
        A :class:`System` instance.

    Example::

        >>> edo19 = TET(19)
        >>> from pytheory import Tone
        >>> t = Tone("0", octave=4, system=edo19)
        >>> t.frequency  # 440.0 Hz (tone 0 = A4)
        440.0

        >>> edo31 = TET(31)
        >>> t = Tone("18", octave=4, system=edo31)
        >>> t.frequency  # 18 steps above A in 31-TET
    """
    if names is not None:
        if len(names) != n:
            raise ValueError(f"Expected {n} names, got {len(names)}")
        tone_names = [(name,) for name in names]
    else:
        tone_names = [(str(i),) for i in range(n)]

    # Degrees: numbered, with no modal names
    degrees = [(f"degree {i+1}", ()) for i in range(n)]

    # Scales: chromatic (all steps = 1) plus MOS scales for common EDOs
    scale_data = {
        "chromatic": (n, {}),
    }

    # Add well-known scales for specific EDOs
    if n == 19:
        # 19-TET: major and minor have different step sizes
        # Major: 3 3 2 3 3 3 2 (sums to 19)
        # Minor: 3 2 3 3 2 3 3
        scale_data["heptatonic"] = [7, {
            "major": {"intervals": (3, 3, 2, 3, 3, 3, 2)},
            "minor": {"intervals": (3, 2, 3, 3, 2, 3, 3)},
            "harmonic minor": {"intervals": (3, 2, 3, 3, 2, 4, 2)},
        }]
        scale_data["pentatonic"] = [5, {
            "major pentatonic": {"intervals": (3, 3, 5, 3, 5)},
            "minor pentatonic": {"intervals": (5, 3, 3, 5, 3)},
        }]
    elif n == 24:
        # 24-TET (quarter-tone): standard 12-TET scales with doubled steps
        scale_data["heptatonic"] = [7, {
            "major": {"intervals": (4, 4, 2, 4, 4, 4, 2)},
            "minor": {"intervals": (4, 2, 4, 4, 2, 4, 4)},
        }]
    elif n == 31:
        # 31-TET: excellent approximation of quarter-comma meantone
        # Major: 5 5 3 5 5 5 3 (sums to 31)
        # Minor: 5 3 5 5 3 5 5
        scale_data["heptatonic"] = [7, {
            "major": {"intervals": (5, 5, 3, 5, 5, 5, 3)},
            "minor": {"intervals": (5, 3, 5, 5, 3, 5, 5)},
            "harmonic minor": {"intervals": (5, 3, 5, 5, 3, 7, 3)},
        }]
        scale_data["pentatonic"] = [5, {
            "major pentatonic": {"intervals": (5, 5, 8, 5, 8)},
            "minor pentatonic": {"intervals": (8, 5, 5, 8, 5)},
        }]
    elif n == 53:
        # 53-TET: nearly perfect fifths and thirds
        # Major: 9 9 4 9 9 9 4 (sums to 53)
        scale_data["heptatonic"] = [7, {
            "major": {"intervals": (9, 9, 4, 9, 9, 9, 4)},
            "minor": {"intervals": (9, 4, 9, 9, 4, 9, 9)},
        }]

    # Find C equivalent for c_index (reference_index is A, C is 3 steps in 12-TET)
    # Proportionally: C is 3/12 of the way around from A
    c_idx = round(n * 3 / 12) if n != 12 else 3

    return System(
        tone_names=tone_names,
        degrees=degrees,
        scales=scale_data,
        c_index=c_idx,
        period=period,
    )


# ── 19-TET named system ──
# Traditional note names for 19-TET: all 12 western notes plus
# 7 quarter-tone positions (enharmonic splits)
_19TET_NAMES = [
    "A", "A#", "Bb", "B", "B#",
    "C", "C#", "Db", "D", "D#",
    "Eb", "E", "E#", "F", "F#",
    "Gb", "G", "G#", "Ab",
]

# ── 31-TET named system ──
# Adriaan Fokker's naming: sharps and flats are distinct pitches
_31TET_NAMES = [
    "A", "A↑", "A#", "Bb", "B↓",
    "B", "B↑", "C", "C↑", "C#",
    "Db", "D↓", "D", "D↑", "D#",
    "Eb", "E↓", "E", "E↑", "E#",
    "F", "F↑", "F#", "Gb", "G↓",
    "G", "G↑", "G#", "Ab", "A↓",
    "A♮",  # enharmonic return (distinct from "A" by a diesis)
]


SYSTEMS = {
    "western": System(tone_names=TONES["western"], degrees=DEGREES["western"]),
    "indian": System(tone_names=TONES["indian"], degrees=DEGREES["indian"], scales=INDIAN_SCALES[12], c_index=3),
    "arabic": System(tone_names=TONES["arabic"], degrees=DEGREES["arabic"], scales=ARABIC_SCALES[12], c_index=3),
    "japanese": System(tone_names=TONES["japanese"], degrees=DEGREES["japanese"], scales=JAPANESE_SCALES[12]),
    "blues": System(tone_names=TONES["blues"], degrees=DEGREES["blues"], scales=BLUES_SCALES[12]),
    "gamelan": System(tone_names=TONES["gamelan"], degrees=DEGREES["gamelan"], scales=GAMELAN_SCALES[12], c_index=3),
    "19-tet": TET(19, names=_19TET_NAMES),
    "31-tet": TET(31, names=_31TET_NAMES),
    # Microtonal systems with proper intervals (not 12-TET approximations)
    "shruti": System(tone_names=TONES_SHRUTI, degrees=DEGREES_SHRUTI,
                     scales=SHRUTI_SCALES, c_index=5, ratios=SHRUTI_RATIOS),
    "maqam": System(tone_names=TONES_ARABIC_24, degrees=DEGREES_ARABIC_24,
                    scales=ARABIC_24_SCALES, c_index=5, ratios=MAQAM_RATIOS),
    "slendro": System(tone_names=TONES_SLENDRO, degrees=DEGREES_SLENDRO,
                      scales=SLENDRO_SCALES, c_index=1),
    "pelog": System(tone_names=TONES_PELOG, degrees=DEGREES_PELOG,
                    scales=PELOG_SCALES, c_index=2),
    "thai": System(tone_names=TONES_THAI, degrees=DEGREES_THAI,
                   scales=THAI_SCALES, c_index=0),
    "makam": System(tone_names=TONES_TURKISH, degrees=DEGREES_TURKISH,
                    scales=TURKISH_SCALES, c_index=13),
    "carnatic": System(tone_names=TONES_CARNATIC, degrees=DEGREES_CARNATIC,
                       scales=CARNATIC_SCALES, c_index=18),  # Sa ≈ C, 18 steps from A
    # Bohlen-Pierce: 13 equal divisions of the tritave (3:1).
    # Genuinely alien — no octaves, no fifths, built on 3:5:7 harmonics.
    # Used by composers like Heinz Bohlen, Kees van Prooijen, Georg Hajdu.
    "bohlen-pierce": TET(13, period=3.0, names=[
        "A", "B", "C", "D", "E", "F", "G",
        "H", "J", "K", "L", "M", "N",
    ]),
}
