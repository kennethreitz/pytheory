import pytuning
import numeral

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
        ("leading tone", ("loocrian", "mixolydian")),
        ("octave", ("ionian", "aeolian")),
    ]
}

SCALES = {
    # Number of semitones.
    12: {
        # scale type: number of tones.
        "chromatic": (12, {}),
        "octatonic": (8, {}),
        "heptatonic": (
            7,
            {
                "major": {"major": True, "hemitonic": True},
                "minor": {"minor": True, "hemitonic": True},
                "harmonic minor": {"minor": True, "harmonic": True, "hemitonic": True},
                "melodic minor": {"minor": True, "melodic": True, "hemitonic": True},
            },
        ),
        # TODO: understand this
        "hexatonic": (
            6,
            {
                # name, arguments to scale generator.
                "wholetone": {},
                "augmented": {},
                "prometheus": {},
                "blues": {},
            },
        ),
        "pentatonic": (5, {}),
        "tetratonic": (4, {}),
        "monotonic": (1, {}),
    }
}


class Pitch:
    def __init__(self, *, frequency):
        self.frequency = frequency


class Tone:
    def __init__(self, *, name, octave=None):
        self.name = name
        self.octave = octave

    def __repr__(self):
        if self.octave:
            return f"<Tone {self.name}{self.octave}>"
        else:
            return f"<Tone {self.name}>"

    @classmethod
    def from_string(klass, s):
        tone = "".join([c for c in filter(str.isalpha, s)])
        try:
            octave = int("".join([c for c in filter(str.isdigit, s)]))
        except ValueError:
            octave = None

        return klass(name=tone, octave=octave)


class Scale:
    def __init__(self, *, system, tonic, semitones=12):
        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(tonic)

        self.tonic = tonic


class System:
    def __init__(self, *, tones, degrees, scales=None):
        self.tones = [Tone.from_string(tone) for tone in tones]
        self.degrees = degrees
        self._scales = scales

        if scales is None:
            self._scales = SCALES[self.semitones]

    @property
    def semitones(self):
        return len(self.tones)

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
                scales[scale_type][scale_name] = (
                    (
                        self.generate_scale(
                            tones=tones, semitones=self.semitones, **scale[1]
                        )
                    ),
                )
        return scales

    @property
    def modes(self):
        def gen():
            for i, degree in enumerate(self.degrees):
                for mode in degree[1]:
                    yield {"degree": (i + 1), "mode": mode}

        return [g for g in gen()]

    # @property
    # def primary_scale(self):
    # return generate_primary_scale(tones=)

    @staticmethod
    def generate_scale(
        *,
        tones=7,
        semitones=12,
        major=False,
        minor=False,
        # Contains semitones.
        hemitonic=False,
        harmonic=False,
        melodic=False,
    ):
        """Generates the primary scale for a given number of semitones/tones."""
        # TODO: Support minor, support harmonic, support melodic.

        # Sanity check.
        if major and minor:
            raise ValueError("Scale cannot be both major and minor. Choose one.")

        def gen(tones, semitones, major, minor, harmonic, melodic):
            # Assume chromatic scale, if neither major nor minor.
            if not (major or minor) and not hemitonic:
                for i in range(tones):
                    yield 1
            else:
                if semitones:
                    first_halfstep_index = round((semitones / 2) - 1)
                    whole_step = 2
                    half_step = 1
                else:
                    first_halfstep_index = None
                    whole_step = 1
                    half_step = 0

                step_count = 0
                for i in range(semitones or tones):
                    if not (i % whole_step):
                        step_count += whole_step
                        if step_count < (semitones or tones):
                            yield whole_step
                        else:
                            if half_step:
                                yield half_step
                    else:
                        if i == first_halfstep_index:
                            step_count += half_step
                            if half_step:
                                yield half_step

        return tuple(
            [
                g
                for g in gen(
                    tones=tones,
                    semitones=semitones,
                    major=major,
                    minor=minor,
                    harmonic=harmonic,
                    melodic=melodic,
                )
            ]
        )

    def __repr__(self):
        return f"<System semitones={self.semitones!r}>"


SYSTEMS = {"western": System(tones=TONES["western"], degrees=DEGREES["western"])}


# print(numeral.int2roman(2018))
western = SYSTEMS["western"]
print(western.scales)
