from ._statics import REFERENCE_A, TEMPERAMENTS


class Interval:
    """Named constants for common musical intervals (in semitones)."""
    UNISON = 0
    MINOR_SECOND = 1
    MAJOR_SECOND = 2
    MINOR_THIRD = 3
    MAJOR_THIRD = 4
    PERFECT_FOURTH = 5
    TRITONE = 6
    PERFECT_FIFTH = 7
    MINOR_SIXTH = 8
    MAJOR_SIXTH = 9
    MINOR_SEVENTH = 10
    MAJOR_SEVENTH = 11
    OCTAVE = 12


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
        if self.octave is not None:
            return f"{self.name}{self.octave}"
        else:
            return self.name

    def names(self):
        return [self.name] + self.alt_names

    @property
    def is_natural(self):
        """True if this is a natural note (no sharp or flat)."""
        return not self.is_sharp and not self.is_flat

    @property
    def is_sharp(self):
        """True if this tone has a sharp (#)."""
        return "#" in self.name

    @property
    def is_flat(self):
        """True if this tone has a flat (b after the first character)."""
        return "b" in self.name[1:]

    @property
    def enharmonic(self):
        """The enharmonic equivalent of this tone, or None if there isn't one.

        Returns the alternate spelling: C# → Db, Db → C#, etc.
        Natural notes (C, D, E, F, G, A, B) have no enharmonic.

        Example::

            >>> Tone.from_string("C#4").enharmonic
            'Db'
        """
        if self.alt_names:
            return self.alt_names[0] if isinstance(self.alt_names, (list, tuple)) else self.alt_names
        # Check the system for alt names
        try:
            for tone in self.system.tones:
                if tone.name == self.name and tone.alt_names:
                    return tone.alt_names[0]
        except (AttributeError, TypeError):
            pass
        return None

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
    def from_frequency(klass, hz, system="western"):
        """Create a Tone from a frequency in Hz.

        Finds the nearest note in 12-TET tuning (A4=440Hz).

        Example::

            >>> Tone.from_frequency(440)
            <Tone A4>
            >>> Tone.from_frequency(261.63)
            <Tone C4>
        """
        import math
        if hz <= 0:
            raise ValueError("Frequency must be positive")
        # Semitones from A4
        semitones_from_a4 = 12 * math.log2(hz / REFERENCE_A)
        semitones = round(semitones_from_a4)
        # A4 is index 0 in the Western system, octave 4
        # Convert to absolute position from C0
        c_index = 3
        a4_from_c0 = ((0 - c_index) % 12) + (4 * 12)  # = 57
        abs_pos = a4_from_c0 + semitones
        octave = abs_pos // 12
        relative = abs_pos % 12
        index = (relative + c_index) % 12
        if isinstance(system, str):
            from .systems import SYSTEMS
            system = SYSTEMS[system]
        return klass.from_index(index, octave=octave, system=system)

    @classmethod
    def from_midi(klass, note_number, system="western"):
        """Create a Tone from a MIDI note number.

        MIDI note 60 = C4 (middle C), 69 = A4 (440 Hz).

        Example::

            >>> Tone.from_midi(60)
            <Tone C4>
            >>> Tone.from_midi(69)
            <Tone A4>
        """
        c_index = 3
        adjusted = note_number - 12  # MIDI C0=12
        octave = adjusted // 12
        relative = adjusted % 12
        index = (relative + c_index) % 12
        if isinstance(system, str):
            from .systems import SYSTEMS
            system = SYSTEMS[system]
        return klass.from_index(index, octave=octave, system=system)

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

    _INTERVAL_NAMES = {
        0: "unison", 1: "minor 2nd", 2: "major 2nd", 3: "minor 3rd",
        4: "major 3rd", 5: "perfect 4th", 6: "tritone", 7: "perfect 5th",
        8: "minor 6th", 9: "major 6th", 10: "minor 7th", 11: "major 7th",
        12: "octave",
    }

    def interval_to(self, other):
        """Name the interval between this tone and another.

        Returns a string like ``"perfect 5th"``, ``"major 3rd"``, or
        ``"octave"``. For intervals larger than an octave, returns
        the compound form (e.g. ``"minor 2nd + 1 octave"``).

        Example::

            >>> C4.interval_to(G4)
            'perfect 5th'
            >>> C4.interval_to(C5)
            'octave'
        """
        semitones = abs(self - other)
        octaves = semitones // 12
        remainder = semitones % 12
        name = self._INTERVAL_NAMES.get(remainder, f"{remainder} semitones")
        if octaves == 0:
            return name
        if remainder == 0:
            if octaves == 1:
                return "octave"
            return f"{octaves} octaves"
        if octaves == 1:
            return f"{name} + 1 octave"
        return f"{name} + {octaves} octaves"

    @property
    def midi(self):
        """MIDI note number (C4 = 60, A4 = 69).

        The MIDI standard assigns integer note numbers from 0–127.
        Middle C (C4) is 60, and each semitone increments by 1.

        Returns:
            int: the MIDI note number, or None if no octave is set.
        """
        if self.octave is None:
            return None
        c_index = 3
        semitones_from_c0 = ((self._index - c_index) % 12) + (self.octave * 12)
        return semitones_from_c0 + 12  # MIDI C0 = 12 (C-1 = 0)

    def transpose(self, semitones):
        """Return a new Tone transposed by the given number of semitones.

        Alias for ``tone + semitones`` / ``tone - semitones``. Positive
        values transpose up, negative values transpose down.
        """
        return self.add(semitones)

    def circle_of_fifths(self):
        """The 12 tones of the circle of fifths starting from this tone.

        Each step ascends by a perfect fifth (7 semitones). After 12
        steps you return to the starting tone. The circle of fifths
        is the backbone of Western harmony — it determines key
        signatures, chord relationships, and modulation paths.

        Clockwise = add sharps: C → G → D → A → E → B → F# → ...
        Counter-clockwise = add flats (see ``circle_of_fourths``).

        Returns:
            A list of 12 Tones.
        """
        tones = []
        t = self
        for _ in range(12):
            tones.append(t)
            t = t.add(7)
        return tones

    def circle_of_fourths(self):
        """The 12 tones of the circle of fourths starting from this tone.

        Each step ascends by a perfect fourth (5 semitones) — the
        reverse direction of the circle of fifths.

        Clockwise = add flats: C → F → Bb → Eb → Ab → ...

        Returns:
            A list of 12 Tones.
        """
        tones = []
        t = self
        for _ in range(12):
            tones.append(t)
            t = t.add(5)
        return tones

    @property
    def frequency(self):
        """The frequency of this tone in Hz (equal temperament, A4=440)."""
        return self.pitch()

    def overtones(self, n=8):
        """The first *n* overtones (harmonic series) of this tone.

        The harmonic series is the foundation of timbre and consonance.
        When a string or air column vibrates, it produces not just the
        fundamental frequency but also integer multiples: 2f, 3f, 4f...

        The intervals between consecutive harmonics form the basis of
        Western harmony::

            Harmonic  Ratio  Interval from fundamental
            1         1:1    Unison (the fundamental)
            2         2:1    Octave
            3         3:1    Octave + perfect 5th
            4         4:1    Two octaves
            5         5:1    Two octaves + major 3rd
            6         6:1    Two octaves + perfect 5th
            7         7:1    Two octaves + minor 7th (slightly flat)
            8         8:1    Three octaves

        The reason a perfect fifth sounds consonant is that the 3rd
        harmonic of the lower note aligns with the 2nd harmonic of the
        upper note (when the upper note is a fifth above). More shared
        harmonics = more consonance.

        Args:
            n: Number of harmonics to return (default 8).

        Returns:
            List of frequencies in Hz.
        """
        f = self.pitch()
        return [f * i for i in range(1, n + 1)]

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
        octave = self.octave if self.octave is not None else 4

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
