from ._statics import (
    TEMPERAMENTS, TONES, DEGREES, SCALES,
    INDIAN_SCALES, ARABIC_SCALES, JAPANESE_SCALES,
    BLUES_SCALES, GAMELAN_SCALES, SYSTEMS,
)


class System:
    def __init__(self, *, tone_names, degrees, scales=None):
        self.tone_names = tone_names

        self.degrees = degrees
        self._scales = scales

        if scales is None:
            self._scales = SCALES[self.semitones]

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

    def __repr__(self):
        return f"<System semitones={self.semitones!r}>"

SYSTEMS = {
    "western": System(tone_names=TONES["western"], degrees=DEGREES["western"]),
    "indian": System(tone_names=TONES["indian"], degrees=DEGREES["indian"], scales=INDIAN_SCALES[12]),
    "arabic": System(tone_names=TONES["arabic"], degrees=DEGREES["arabic"], scales=ARABIC_SCALES[12]),
    "japanese": System(tone_names=TONES["japanese"], degrees=DEGREES["japanese"], scales=JAPANESE_SCALES[12]),
    "blues": System(tone_names=TONES["blues"], degrees=DEGREES["blues"], scales=BLUES_SCALES[12]),
    "gamelan": System(tone_names=TONES["gamelan"], degrees=DEGREES["gamelan"], scales=GAMELAN_SCALES[12]),
}
