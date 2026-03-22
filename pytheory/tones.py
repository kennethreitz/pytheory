from __future__ import annotations

from typing import Optional, Union

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

    def __init__(
        self,
        name: str,
        *,
        alt_names: Optional[list[str]] = None,
        octave: Optional[int] = None,
        system: Union[str, object] = "western",
    ) -> None:
        """Initialize a Tone with a name, optional octave, and musical system.

        Args:
            name: The note name (e.g. ``"C"``, ``"C#4"``). If the name
                contains a digit, it is parsed as the octave.
            alt_names: Alternate spellings for this tone (e.g. enharmonics).
            octave: The octave number. Overrides any octave parsed from *name*.
            system: The tuning system, either as a string key (``"western"``)
                or a ``ToneSystem`` instance.
        """
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
        self._frequency: Optional[float] = None

        if isinstance(system, str):
            self.system_name = system
            self._system = None
        else:
            self.system_name = None
            self._system = system

    @property
    def exists(self) -> bool:
        """True if this tone's name is found in the associated system."""
        return self.name in self.system.tones

    @property
    def system(self) -> object:
        """The ``ToneSystem`` associated with this tone.

        Lazily resolved from ``system_name`` on first access and cached.
        """
        from .systems import SYSTEMS

        if self._system:
            return self._system

        if self.system_name:
            self._system = SYSTEMS[self.system_name]
            return self.system

    @property
    def full_name(self) -> str:
        """The tone name with octave appended, e.g. ``'C4'`` or ``'C'``."""
        if self.octave is not None:
            return f"{self.name}{self.octave}"
        else:
            return self.name

    def names(self) -> list[str]:
        """Return a list containing the primary name and all alternate names."""
        return [self.name] + self.alt_names

    @property
    def is_natural(self) -> bool:
        """True if this is a natural note (no sharp or flat)."""
        return not self.is_sharp and not self.is_flat

    @property
    def is_sharp(self) -> bool:
        """True if this tone has a sharp (#)."""
        return "#" in self.name

    @property
    def is_flat(self) -> bool:
        """True if this tone has a flat (b after the first character)."""
        return "b" in self.name[1:]

    @property
    def enharmonic(self) -> Optional[str]:
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

    def __repr__(self) -> str:
        return f"<Tone {self.full_name}>"

    def __str__(self) -> str:
        return self.full_name

    def __add__(self, interval: int) -> Tone:
        return self.add(interval)

    def __sub__(self, other: Union[int, Tone]) -> Union[Tone, int]:
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

    def __lt__(self, other: Tone) -> bool:
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() < other.pitch()

    def __le__(self, other: Tone) -> bool:
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() <= other.pitch()

    def __gt__(self, other: Tone) -> bool:
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() > other.pitch()

    def __ge__(self, other: Tone) -> bool:
        if not isinstance(other, Tone):
            return NotImplemented
        return self.pitch() >= other.pitch()

    def __eq__(self, other: object) -> bool:

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

    def __hash__(self) -> int:
        return hash((self.name, self.octave))

    @classmethod
    def from_string(klass, s: str, system: Optional[Union[str, object]] = None) -> Tone:
        """Create a Tone by parsing a string like ``'C#4'`` or ``'Bb'``.

        Args:
            s: A note string, optionally including an octave number.
            system: The tuning system to associate with the tone.

        Returns:
            A new ``Tone`` instance.
        """
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
    def from_tuple(klass, t: tuple[str, ...]) -> Tone:
        """Create a Tone from a tuple of ``(name, *alt_names)``.

        Args:
            t: A tuple where the first element is the primary name and
                any remaining elements are alternate names (enharmonics).

        Returns:
            A new ``Tone`` instance.
        """
        if len(t) == 1:
            return klass.from_string(s=t[0])
        else:
            tone = klass.from_string(s=t[0])
            tone.alt_names = t[1:]
            return tone

    @classmethod
    def from_frequency(klass, hz: float, system: Union[str, object] = "western") -> Tone:
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
    def from_midi(klass, note_number: int, system: Union[str, object] = "western") -> Tone:
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
    def from_index(klass, i: int, *, octave: int, system: object) -> Tone:
        """Create a Tone from its index within a tuning system.

        Args:
            i: The index of the tone in the system's tone list.
            octave: The octave number.
            system: The ``ToneSystem`` instance.

        Returns:
            A new ``Tone`` instance.
        """
        tone = system.tones[i].name
        return klass(name=tone, octave=octave, system=system)

    @property
    def _index(self) -> int:
        """The index of this tone within its associated system's tone list.

        Raises:
            ValueError: If no system is associated with this tone.
        """
        try:
            return self.system.tones.index(self.name)
        except AttributeError:
            raise ValueError("Tone index cannot be referenced without a system!")

    def _math(self, interval: int) -> tuple[int, int]:
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

    def add(self, interval: int) -> Tone:
        """Return a new Tone that is *interval* semitones above this one.

        Args:
            interval: Number of semitones to add (positive = up).

        Returns:
            A new ``Tone`` instance.
        """
        index, octave = self._math(interval)
        return self.from_index(index, octave=octave, system=self.system)

    def subtract(self, interval: int) -> Tone:
        """Return a new Tone that is *interval* semitones below this one.

        Args:
            interval: Number of semitones to subtract (positive = down).

        Returns:
            A new ``Tone`` instance.
        """
        return self.add((-1 * interval))

    _INTERVAL_NAMES = {
        0: "unison", 1: "minor 2nd", 2: "major 2nd", 3: "minor 3rd",
        4: "major 3rd", 5: "perfect 4th", 6: "tritone", 7: "perfect 5th",
        8: "minor 6th", 9: "major 6th", 10: "minor 7th", 11: "major 7th",
        12: "octave",
    }

    def interval_to(self, other: Tone) -> str:
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
    def midi(self) -> Optional[int]:
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

    def transpose(self, semitones: int) -> Tone:
        """Return a new Tone transposed by the given number of semitones.

        Alias for ``tone + semitones`` / ``tone - semitones``. Positive
        values transpose up, negative values transpose down.
        """
        return self.add(semitones)

    def circle_of_fifths(self) -> list[Tone]:
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
        tones: list[Tone] = []
        t = self
        for _ in range(12):
            tones.append(t)
            t = t.add(7)
        return tones

    def circle_of_fourths(self) -> list[Tone]:
        """The 12 tones of the circle of fourths starting from this tone.

        Each step ascends by a perfect fourth (5 semitones) — the
        reverse direction of the circle of fifths.

        Clockwise = add flats: C → F → Bb → Eb → Ab → ...

        Returns:
            A list of 12 Tones.
        """
        tones: list[Tone] = []
        t = self
        for _ in range(12):
            tones.append(t)
            t = t.add(5)
        return tones

    @property
    def frequency(self) -> float:
        """The frequency of this tone in Hz (equal temperament, A4=440).

        The result is cached after the first computation.
        """
        if self._frequency is None:
            self._frequency = self.pitch()
        return self._frequency

    def overtones(self, n: int = 8) -> list[float]:
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
        reference_pitch: float = REFERENCE_A,
        temperament: str = "equal",
        symbolic: bool = False,
        precision: Optional[int] = None,
    ) -> float:
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
