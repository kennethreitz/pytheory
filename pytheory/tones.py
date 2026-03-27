from __future__ import annotations

from typing import Optional, Union

from ._statics import REFERENCE_A, TEMPERAMENTS, C_INDEX


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
        name,
        *,
        alt_names: Optional[list[str]] = None,
        octave: Optional[int] = None,
        system: Union[str, object] = "western",
        _validate: bool = True,
    ) -> None:
        """Initialize a Tone with a name, optional octave, and musical system.

        Args:
            name: The note name as a string (``"C"``, ``"C#4"``) or an int
                for numbered systems (``0``, ``11``). Ints are converted to
                strings and wrapped to the system's range (e.g. 22 in a
                22-tone system becomes 0 at octave+1).
            alt_names: Alternate spellings for this tone (e.g. enharmonics).
            octave: The octave number. Overrides any octave parsed from *name*.
            system: The tuning system, either as a string key (``"western"``)
                or a ``ToneSystem`` instance.
        """
        if alt_names is None:
            alt_names = []

        # Int tone names: wrap to system range, adjust octave
        if isinstance(name, int):
            if isinstance(system, str):
                from .systems import SYSTEMS
                _sys = SYSTEMS[system]
            else:
                _sys = system
            n_tones = len(_sys.tone_names)
            if name < 0 or name >= n_tones:
                extra_octaves = name // n_tones
                name = name % n_tones
                if octave is None:
                    octave = 4 + extra_octaves
                else:
                    octave += extra_octaves
            name = str(name)

        if isinstance(name, str):
            # Normalize unicode music symbols to ASCII equivalents
            name = (name
                    .replace('\u266f', '#')   # ♯ → #
                    .replace('\u266d', 'b')   # ♭ → b
                    .replace('\U0001d12a', '##')  # 𝄪 → ##
                    .replace('\U0001d12b', 'bb')  # 𝄫 → bb
                    )
            # Normalize 'x' / 'X' as double sharp (only after letter name)
            if len(name) >= 2 and name[1] in ('x', 'X') and name[0].isalpha():
                name = name[0] + '##' + name[2:]

            # Only parse trailing digits as octave (e.g. "C4" → "C", octave=4).
            # Digits embedded in the name (e.g. "Mib+1") are NOT octaves.
            # Numeric pitch class names ("0", "11") are also left alone.
            if name and name[0].isalpha():
                import re as _re
                m = _re.search(r'(\d+)$', name)
                if m:
                    parsed_octave = int(m.group(1))
                    name = name[:m.start()]
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

        # Validate tone name against the system early (fixes #39).
        if _validate and self.system.resolve_name(name) is None:
            raise ValueError(
                f"Unknown tone name: {name!r}. "
                f"Not found in the {system!r} system."
            )

    @property
    def exists(self) -> bool:
        """True if this tone's name is found in the associated system."""
        return self.system.resolve_name(self.name) is not None

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
    def scientific(self) -> str:
        """Scientific pitch notation (e.g. ``'C4'``, ``'A#3'``).

        This is the default notation used throughout PyTheory —
        note name followed by octave number. Middle C is C4.
        Same as ``full_name``.
        """
        return self.full_name

    @property
    def helmholtz(self) -> str:
        """Helmholtz pitch notation.

        The older European convention still used in some contexts:

        - C2 → ``CC``  (sub-contra)
        - C3 → ``C``   (great octave)
        - C4 → ``c``   (small octave / middle C)
        - C5 → ``c'``  (one-line)
        - C6 → ``c''`` (two-line)
        - C7 → ``c'''``

        Accidentals are preserved as-is (e.g. ``c#'``).

        Example::

            >>> Tone.from_string("C4").helmholtz
            'c'
            >>> Tone.from_string("C3").helmholtz
            'C'
            >>> Tone.from_string("C5").helmholtz
            "c'"
            >>> Tone.from_string("A2").helmholtz
            'AA'
        """
        if self.octave is None:
            return self.name
        letter = self.name[0]
        accidental = self.name[1:]
        if self.octave <= 2:
            # Contra and sub-contra: uppercase repeated
            # Octave 2 = contra (CC), 1 = sub-contra (CCC), 0 = (CCCC)
            repeats = 4 - self.octave
            return (letter.upper() * repeats) + accidental
        elif self.octave == 3:
            # Great octave: single uppercase
            return letter.upper() + accidental
        else:
            # Octave 4+: lowercase with tick marks
            ticks = self.octave - 4
            tick_str = "'" * ticks if ticks > 0 else ""
            return letter.lower() + accidental + tick_str

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
    def letter(self) -> str:
        """The letter name without any accidental.

        Example::

            >>> Tone.from_string("C#4").letter
            'C'
            >>> Tone.from_string("Bb4").letter
            'B'
            >>> Tone.from_string("G4").letter
            'G'
        """
        return self.name[0]

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

    _SOLFEGE_MAP = {
        "C": "Do", "D": "Re", "E": "Mi", "F": "Fa",
        "G": "Sol", "A": "La", "B": "Ti",
    }

    _SOLFEGE_SHARP_MAP = {
        "C#": "Di", "D#": "Ri", "F#": "Fi", "G#": "Si", "A#": "Li",
        "E#": "Mi", "B#": "Do",
    }

    _SOLFEGE_FLAT_MAP = {
        "Db": "Ra", "Eb": "Me", "Gb": "Se", "Ab": "Le", "Bb": "Te",
        "Fb": "Mi", "Cb": "Ti",
    }

    @property
    def solfege(self) -> str:
        """Map Western note names to fixed-Do solfege syllables.

        Uses fixed Do system where C is always Do regardless of key.

        - C->Do, D->Re, E->Mi, F->Fa, G->Sol, A->La, B->Ti
        - Sharps: C#->Di, D#->Ri, F#->Fi, G#->Si, A#->Li
        - Flats: Db->Ra, Eb->Me, Gb->Se, Ab->Le, Bb->Te

        Returns the note name unchanged if the system isn't western
        or the name isn't recognized.

        Example::

            >>> Tone.from_string("C4").solfege
            'Do'
            >>> Tone.from_string("F#4").solfege
            'Fi'
        """
        # Check system
        sys_name = self.system_name
        if sys_name is not None and sys_name != "western":
            return self.name
        if self._system is not None:
            try:
                if hasattr(self._system, 'name') and self._system.name != "western":
                    return self.name
            except (AttributeError, TypeError):
                pass

        name = self.name
        if name in self._SOLFEGE_MAP:
            return self._SOLFEGE_MAP[name]
        if name in self._SOLFEGE_SHARP_MAP:
            return self._SOLFEGE_SHARP_MAP[name]
        if name in self._SOLFEGE_FLAT_MAP:
            return self._SOLFEGE_FLAT_MAP[name]
        return name

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
            try:
                mod = len(self.system.tones)
            except AttributeError:
                raise ValueError("Tone math can only be computed with an associated system!")
            self_from_c0 = ((self._index - C_INDEX) % mod) + ((self.octave or 0) * mod)
            other_from_c0 = ((other._index - C_INDEX) % mod) + ((other.octave or 0) * mod)
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
        import re as _re
        octave = None
        tone = s
        # Only parse trailing digits as octave
        if s and s[0].isalpha():
            m = _re.search(r'(\d+)$', s)
            if m:
                octave = int(m.group(1))
                tone = s[:m.start()]

        if system:
            return klass(name=tone, octave=octave, system=system)
        else:
            return klass(name=tone, octave=octave, _validate=False)

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
        if isinstance(system, str):
            from .systems import SYSTEMS
            system = SYSTEMS[system]
        n = len(system.tone_names)
        c_idx = getattr(system, 'c_index', C_INDEX)
        # Steps from A4 in this EDO
        steps_from_a4 = n * math.log2(hz / REFERENCE_A)
        steps = round(steps_from_a4)
        # A4 is index 0, octave 4. Convert to absolute position from C0.
        a4_from_c0 = ((0 - c_idx) % n) + (4 * n)
        abs_pos = a4_from_c0 + steps
        octave = abs_pos // n
        relative = abs_pos % n
        index = (relative + c_idx) % n
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
        if isinstance(system, str):
            from .systems import SYSTEMS
            system = SYSTEMS[system]
        # MIDI is a 12-TET standard. Convert to Hz and use from_frequency
        # for non-12 systems.
        n = len(system.tone_names)
        if n != 12:
            hz = REFERENCE_A * (2 ** ((note_number - 69) / 12))
            return klass.from_frequency(hz, system=system)
        adjusted = note_number - 12  # MIDI C0=12
        octave = adjusted // 12
        relative = adjusted % 12
        index = (relative + C_INDEX) % 12
        return klass.from_index(index, octave=octave, system=system)

    @classmethod
    def from_index(klass, i: int, *, octave: int, system: object, prefer_flats: bool = False) -> Tone:
        """Create a Tone from its index within a tuning system.

        Args:
            i: The index of the tone in the system's tone list.
            octave: The octave number.
            system: The ``ToneSystem`` instance.
            prefer_flats: If True and the tone has a flat spelling,
                use it instead of the default sharp spelling.

        Returns:
            A new ``Tone`` instance.
        """
        tone_names = system.tone_names[i]
        if prefer_flats and len(tone_names) > 1:
            # Find the first flat spelling (contains 'b' but isn't just 'B')
            tone = tone_names[0]  # fallback to primary
            for tn in tone_names[1:]:
                if 'b' in tn and tn != 'B':
                    tone = tn
                    break
        else:
            tone = tone_names[0]  # primary spelling
        # Bypass parsing and validation — name comes from a known system index
        obj = klass.__new__(klass)
        obj.name = tone
        obj.octave = octave
        obj.alt_names = list(tone_names[1:]) if len(tone_names) > 1 else []
        obj._frequency = None
        if isinstance(system, str):
            obj.system_name = system
            obj._system = None
        else:
            obj.system_name = None
            obj._system = system
        return obj

    @property
    def _index(self) -> int:
        """The index of this tone within its associated system's tone list.

        Resolves enharmonic names (e.g. 'Db' → 'C#') before lookup.

        Raises:
            ValueError: If no system is associated with this tone or
                the name is not found.
        """
        try:
            canonical = self.system.resolve_name(self.name)
            if canonical is None:
                raise ValueError(f"Tone {self.name!r} not found in system")
            # Use _name_to_index for direct lookup (avoids creating Tone objects)
            idx = self.system._name_to_index(canonical)
            if idx is not None:
                return idx
            # Fallback: linear search through tone_names
            for i, names in enumerate(self.system.tone_names):
                if canonical in names:
                    return i
            raise ValueError(f"Tone {self.name!r} not found in system")
        except AttributeError:
            raise ValueError("Tone index cannot be referenced without a system!")

    def _math(self, interval: int) -> tuple[int, int]:
        """Returns (new index, new octave).

        Octave boundaries follow scientific pitch notation, where the
        octave number increments at C (index 3 in the Western system).
        """

        octave = self.octave or 0

        try:
            mod = len(self.system.tone_names)
        except AttributeError:
            raise ValueError(
                "Tone math can only be computed with an associated system!"
            )

        c_idx = getattr(self.system, 'c_index', C_INDEX)

        # Convert to absolute steps from C0
        note_from_c0 = ((self._index - c_idx) % mod) + (octave * mod)
        note_from_c0 += interval

        new_octave = note_from_c0 // mod
        relative = note_from_c0 % mod
        new_index = (relative + c_idx) % mod

        return (new_index, new_octave)

    def add(self, interval: int, *, prefer_flats: bool = False) -> Tone:
        """Return a new Tone that is *interval* semitones above this one.

        Args:
            interval: Number of semitones to add (positive = up).
            prefer_flats: If True, use flat spellings (Bb, Eb) instead
                of sharp spellings (A#, D#) for accidentals.

        Returns:
            A new ``Tone`` instance.
        """
        index, octave = self._math(interval)
        return self.from_index(index, octave=octave, system=self.system, prefer_flats=prefer_flats)

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
        n = len(self.system.tones)
        octaves = semitones // n
        remainder = semitones % n
        name = self._INTERVAL_NAMES.get(remainder, f"{remainder} steps")
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
        n = len(self.system.tones)
        if n != 12:
            # Non-12-TET: approximate MIDI via frequency
            import math
            hz = self.pitch()
            return round(69 + 12 * math.log2(hz / REFERENCE_A))
        semitones_from_c0 = ((self._index - C_INDEX) % 12) + (self.octave * 12)
        return semitones_from_c0 + 12  # MIDI C0 = 12 (C-1 = 0)

    def transpose(self, semitones: int) -> Tone:
        """Return a new Tone transposed by the given number of semitones.

        Alias for ``tone + semitones`` / ``tone - semitones``. Positive
        values transpose up, negative values transpose down.
        """
        return self.add(semitones)

    def cents_difference(self, other: Tone, *, temperament: str = "equal") -> float:
        """Difference in cents between this tone and another.

        One semitone = 100 cents. Musicians use cents to measure fine
        pitch differences — e.g. comparing equal temperament to
        Pythagorean tuning, or checking how far out of tune a note is.

        Args:
            other: The tone to compare against.
            temperament: Tuning temperament for both tones.

        Returns:
            Signed float — positive means *other* is higher.

        Example::

            >>> a4 = Tone.from_string("A4", system="western")
            >>> a4.cents_difference(a4 + 1)  # one semitone
            100.0
            >>> a4_pyth = a4.pitch(temperament="pythagorean")
            >>> a4_equal = a4.pitch(temperament="equal")
        """
        import math
        f1 = self.pitch(temperament=temperament)
        f2 = other.pitch(temperament=temperament)
        if f1 <= 0 or f2 <= 0:
            raise ValueError("Both tones must have positive frequencies")
        return 1200 * math.log2(f2 / f1)

    def circle_of_fifths(self) -> list[Tone]:
        """The circle of fifths starting from this tone.

        Each step ascends by a perfect fifth (7 semitones in 12-TET).
        After N steps (where N = number of tones in the system) you
        return to the starting tone. The circle of fifths is the
        backbone of Western harmony — it determines key signatures,
        chord relationships, and modulation paths.

        Returns:
            A list of Tones (12 for Western, N for other systems).
        """
        n = len(self.system.tones)
        # Perfect fifth: the closest approximation to 3:2 ratio
        fifth = round(n * 7 / 12)  # 7 in 12-TET, 11 in 19-TET, 18 in 31-TET
        tones: list[Tone] = []
        t = self
        for _ in range(n):
            tones.append(t)
            t = t.add(fifth)
        return tones

    def circle_of_fourths(self) -> list[Tone]:
        """The circle of fourths starting from this tone.

        Each step ascends by a perfect fourth — the reverse direction
        of the circle of fifths.

        Returns:
            A list of Tones (12 for Western, N for other systems).
        """
        n = len(self.system.tones)
        fourth = round(n * 5 / 12)  # 5 in 12-TET, 8 in 19-TET, 13 in 31-TET
        tones: list[Tone] = []
        t = self
        for _ in range(n):
            tones.append(t)
            t = t.add(fourth)
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
            tones = len(self.system.tone_names)
        except AttributeError:
            raise ValueError("Pitches can only be computed with an associated system!")

        # Period ratio: 2.0 for standard octave-based systems,
        # 3.0 for Bohlen-Pierce (tritave), configurable per system.
        period = getattr(self.system, 'period', 2.0)
        c_idx = getattr(self.system, 'c_index', C_INDEX)

        # Custom ratios override temperament (e.g. shruti just ratios)
        custom_ratios = getattr(self.system, 'ratios', None)
        if custom_ratios is not None:
            pitch_scale = list(custom_ratios) + [period]
        elif period != 2.0 and temperament == "equal":
            # Non-octave period (e.g. Bohlen-Pierce tritave=3.0)
            import sympy
            pitch_scale = [period ** sympy.Rational(i, tones) for i in range(tones + 1)]
        else:
            pitch_scale = TEMPERAMENTS[temperament](tones)
        octave = self.octave if self.octave is not None else 4

        note_from_c0 = ((self._index - c_idx) % tones) + (octave * tones)
        a4_from_c0 = ((0 - c_idx) % tones) + (4 * tones)  # A4

        diff = note_from_c0 - a4_from_c0
        octave_shift = diff // tones
        within_octave = diff % tones

        ratio = pitch_scale[within_octave] * (period ** octave_shift)

        if symbolic:
            return reference_pitch * ratio
        else:
            result = reference_pitch * ratio
            if precision:
                return float(result.evalf(precision))
            return float(result)
