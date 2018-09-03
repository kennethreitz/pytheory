from math import ceil, floor
import numeral

from ._statics import REFERENCE_A, TEMPERAMENTS, TONES, DEGREES, SCALES


class Pitch:
    def __init__(self, *, frequency):
        self.frequency = frequency


class Tone:
    # __slots__ = ("name", "octave", "system")

    def __init__(self, *, name, octave=None, system=None):
        self.name = name
        self.octave = octave
        self.system = system

        if self.system:
            try:
                assert self.name in self.system.tones
            except AssertionError:
                raise ValueError(
                    f"Tone {self.name!r} was not found in system: {self.system.tones!r}"
                )

    @property
    def full_name(self):
        if self.octave:
            return f"{self.name}{self.octave}"
        else:
            return self.name

    def __repr__(self):
        return f"<Tone {self.full_name}>"

    def __eq__(self, other):

        # Comparing string literals.
        if self.name == other:
            return True

        # Comparing against other Tones.
        try:
            if (self.name == other.name) and (self.octave == other.octave):
                return True
        except AttributeError:
            pass

    @classmethod
    def from_string(klass, s, system=None):
        tone = "".join([c for c in filter(str.isalpha, s)])
        try:
            octave = int("".join([c for c in filter(str.isdigit, s)]))
        except ValueError:
            octave = None

        return klass(name=tone, octave=octave, system=system)

    @classmethod
    def from_index(klass, i, *, octave, system):
        tone = system.tones[i].name
        return klass(name=tone, octave=octave, system=system)

    @property
    def _index(self):
        try:
            return self.system.tones.index(self.name)
        except AttributeError:
            raise ValueError("Tone index cannot be referenced without a system!")

    def _math(self, interval):
        """Returns (new index, new octave)."""

        try:
            mod = len(self.system.tones)
        except AttributeError:
            raise ValueError(
                "Tone math can only be computed with an associated system!"
            )
        result = self._index + interval
        index = result % mod
        octave = result // mod + self.octave
        return (index, octave)

    def add(self, interval):
        index, octave = self._math(interval)
        return self.from_index(index, octave=octave, system=self.system)

    def subtract(self, interval):
        return self.add((-1 * interval))

    def pitch(
        self,
        *,
        reference_pitch=REFERENCE_A,
        temperament="equal",
        symbolic=False,
        precision=None,
    ):
        try:
            tones = len(self.system.tones)
        except AttributeError:
            raise ValueError("Pitches can only be computed with an associated system!")
        pitch_scale = TEMPERAMENTS[temperament](tones)
        pitch = pitch_scale[self._index]
        if symbolic:
            return reference_pitch * pitch
        else:
            return reference_pitch * pitch.evalf(precision)


class System:
    def __init__(self, *, tones, degrees, scales=None):
        self.tones = [Tone.from_string(tone) for tone in tones]

        # Add current system to tones (a bit of a hack).
        for tone in self.tones:
            tone.system = self

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


SYSTEMS = {"western": System(tones=TONES["western"], degrees=DEGREES["western"])}


class Scale:
    def __init__(self, *, tones, degrees=None, system=None):
        self.tones = tones
        self.degrees = degrees
        self.system = system

        if self.degrees:
            if not len(self.tones) == len(self.degrees):
                raise ValueError("The number of tones and degrees must be equal!")

    def __repr__(self):
        r = []
        for (i, tone) in enumerate(self.tones):
            degree = numeral.int2roman(i + 1, only_ascii=True)
            r += [f"{degree}={tone.full_name}"]

        r = " ".join(r)
        return f"<Scale {r}>"

    def __getitem__(self, item):
        # Degree–style reference (e.g. "IV").
        if isinstance(item, str):
            degrees = []
            for (i, tone) in enumerate(self.tones):
                degrees.append(numeral.int2roman(i + 1, only_ascii=True))

            if item in degrees:
                item = degrees.index(item)

        # List/Tuple–style reference.
        if isinstance(item, int) or isinstance(item, slice):
            return self.tones[item]


class TonedScale:
    def __init__(self, *, system=SYSTEMS["western"], tonic):
        self.system = system

        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(tonic, system=self.system)

        self.tonic = tonic

    def __repr__(self):
        return f"<TonedScale system={self.system!r} tonic={self.tonic}>"

    def __getitem__(self, scale):
        return self._scales[scale]

    @property
    def scales(self):
        return tuple(self._scales().keys())

    @property
    def _scales(self):
        scales = {}

        for scale_type in self.system.scales:
            for scale in self.system.scales[scale_type]:

                working_scale = []
                reference_scale = self.system.scales[scale_type][scale]["intervals"]

                current_tone = self.tonic
                working_scale.append(current_tone)

                for interval in reference_scale:
                    current_tone = current_tone.add(interval)
                    working_scale.append(current_tone)

                scales[scale] = Scale(tones=tuple(working_scale))

        return scales


class Chord:
    def __init__(self, *, tones):
        self.tones = tones

    # @property
    # def harmony(self):
    #     pass
