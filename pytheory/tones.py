from ._statics import REFERENCE_A, TEMPERAMENTS


class Tone:

    def __init__(self, name, *, alt_names=None, octave=None, system="western"):
        if alt_names is None:
            alt_names = []

        if isinstance(name, str):
            try:
                parsed_octave = int("".join([c for c in filter(str.isdigit, name)]))
            except ValueError:
                parsed_octave = None

            if parsed_octave is not None:
                name = name.replace(str(parsed_octave), "")
                if octave is None:
                    octave = parsed_octave

        self.name = name
        self.octave = octave
        self.alt_names = alt_names

        if isinstance(system, str):
            self.system_name = system
            self._system = None
        else:
            self.system_name = None
            self._system = system

    @property
    def exists(self):
        return self.name in self.system.tones

    @property
    def system(self):
        from .systems import SYSTEMS

        if self._system:
            return self._system

        if self.system_name:
            self._system = SYSTEMS[self.system_name]
            return self.system

    @property
    def full_name(self):
        if self.octave:
            return f"{self.name}{self.octave}"
        else:
            return self.name

    def names(self):
        return [self.name] + self.alt_names

    def __repr__(self):
        return f"<Tone {self.full_name}>"

    def __str__(self):
        return self.full_name

    def __add__(self, interval):
        return self.add(interval)

    def __sub__(self, other):
        # Tone - int: subtract semitones
        if isinstance(other, int):
            return self.subtract(other)
        # Tone - Tone: semitone distance
        if isinstance(other, Tone):
            c_index = 3
            try:
                mod = len(self.system.tones)
            except AttributeError:
                raise ValueError("Tone math can only be computed with an associated system!")
            self_from_c0 = ((self._index - c_index) % mod) + ((self.octave or 0) * mod)
            other_from_c0 = ((other._index - c_index) % mod) + ((other.octave or 0) * mod)
            return self_from_c0 - other_from_c0
        return NotImplemented

    def __lt__(self, other):
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() < other.pitch()

    def __le__(self, other):
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() <= other.pitch()

    def __gt__(self, other):
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() > other.pitch()

    def __ge__(self, other):
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() >= other.pitch()

    def __eq__(self, other):

        # Comparing string literals.
        if isinstance(other, str):
            return self.name == other

        # Comparing against other Tones.
        try:
            if (self.name in other.names()) and (self.octave == other.octave):
                return True
        except AttributeError:
            pass

        return False

    def __hash__(self):
        return hash((self.name, self.octave))

    @classmethod
    def from_string(klass, s, system=None):
        try:
            octave = int("".join([c for c in filter(str.isdigit, s)]))
        except ValueError:
            octave = None

        tone = s.replace(str(octave), "") if octave else s

        if system:
            return klass(name=tone, octave=octave, system=system)
        else:
            return klass(name=tone, octave=octave)

    @classmethod
    def from_tuple(klass, t):
        if len(t) == 1:
            return klass.from_string(s=t[0])
        else:
            tone = klass.from_string(s=t[0])
            tone.alt_names = t[1:]
            return tone

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
        """Returns (new index, new octave).

        Octave boundaries follow scientific pitch notation, where the
        octave number increments at C (index 3 in the Western system).
        """

        octave = self.octave or 0

        try:
            mod = len(self.system.tones)
        except AttributeError:
            raise ValueError(
                "Tone math can only be computed with an associated system!"
            )

        # C is at index 3 in the Western tone list (A=0, A#=1, B=2, C=3, ...)
        # Scientific pitch notation changes octave at C, not A.
        c_index = 3

        # Convert to absolute semitones from C0
        note_from_c0 = ((self._index - c_index) % mod) + (octave * mod)
        note_from_c0 += interval

        new_octave = note_from_c0 // mod
        relative = note_from_c0 % mod
        new_index = (relative + c_index) % mod

        return (new_index, new_octave)

    def add(self, interval):
        index, octave = self._math(interval)
        return self.from_index(index, octave=octave, system=self.system)

    def subtract(self, interval):
        return self.add((-1 * interval))

    @property
    def frequency(self):
        """The frequency of this tone in Hz (equal temperament, A4=440)."""
        return self.pitch()

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
        octave = self.octave or 4

        # C is at index 3; convert to semitones from C0 for both
        # this note and the reference A4.
        c_index = 3
        note_from_c0 = ((self._index - c_index) % tones) + (octave * tones)
        a4_from_c0 = ((0 - c_index) % tones) + (4 * tones)  # A4

        diff = note_from_c0 - a4_from_c0
        octave_shift = diff // tones
        within_octave = diff % tones

        ratio = pitch_scale[within_octave] * (2 ** octave_shift)

        if symbolic:
            return reference_pitch * ratio
        else:
            result = reference_pitch * ratio
            if precision:
                return float(result.evalf(precision))
            return float(result)
