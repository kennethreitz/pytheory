from ._statics import TEMPERAMENTS, TONES, DEGREES, SCALES, SYSTEMS


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
        major=False,
        minor=False,
        hemitonic=False,  # Contains semitones.
        harmonic=False,
        melodic=False,
        offset=None,
    ):
        """Generates the primary scale for a given number of semitones/tones."""
        # TODO: Support minor, support harmonic, support melodic.

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
                        # TODO: figure out how to make this work with monotonic.
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
            scale = scale[offset - 1 :] + scale[: offset - 1]

        # descending goes in meta?
        return {"intervals": scale, "hemitonic": hemitonic, "meta": {}}

    def __repr__(self):
        return f"<System semitones={self.semitones!r}>"

SYSTEMS = {"western": System(tone_names=TONES["western"], degrees=DEGREES["western"])}
