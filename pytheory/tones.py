from ._statics import REFERENCE_A

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
