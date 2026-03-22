import numeral

from .systems import SYSTEMS
from .tones import Tone


class Scale:
    def __init__(self, *, tones, degrees=None, system='western'):
        self.tones = tones
        self.degrees = degrees

        if isinstance(system, str):
            self.system_name = system
            self._system = None
        else:
            self.system_name = None
            self._system = system

        if self.degrees:
            if not len(self.tones) == len(self.degrees):
                raise ValueError("The number of tones and degrees must be equal!")

    @property
    def system(self):
        if self._system:
            return self._system

        if self.system_name:
            return SYSTEMS[self.system_name]

    def __repr__(self):
        r = []
        for (i, tone) in enumerate(self.tones):
            degree = numeral.int2roman(i + 1, only_ascii=True)
            r += [f"{degree}={tone.full_name}"]

        r = " ".join(r)
        return f"<Scale {r}>"

    def __iter__(self):
        return iter(self.tones)

    def __len__(self):
        return len(self.tones)

    def __contains__(self, item):
        if isinstance(item, str):
            return any(item == t.name for t in self.tones)
        return item in self.tones

    @property
    def note_names(self):
        """List of note names in this scale."""
        return [t.name for t in self.tones]

    def chord(self, *degrees):
        """Build a Chord from scale degrees (0-indexed).

        Wraps around if degrees exceed the scale length, transposing
        up by an octave as needed.

        Example: scale.chord(0, 2, 4) builds a triad from the 1st, 3rd, 5th.
        """
        from .chords import Chord
        # Scale has N tones where the last is the octave of the first,
        # so the unique tones are tones[:-1] (length N-1).
        unique = len(self.tones) - 1
        result = []
        for d in degrees:
            idx = d % unique
            octaves_up = d // unique
            tone = self.tones[idx]
            if octaves_up > 0:
                tone = tone.add(12 * octaves_up)
            result.append(tone)
        return Chord(tones=result)

    def transpose(self, semitones):
        """Return a new Scale transposed by the given number of semitones.

        Every tone is shifted by the same interval, preserving the
        scale's interval pattern.

        Example::

            >>> c_major = TonedScale(tonic="C4")["major"]
            >>> d_major = c_major.transpose(2)
            >>> d_major.note_names
            ['D', 'E', 'F#', 'G', 'A', 'B', 'C#', 'D']
        """
        from .chords import Chord
        new_tones = tuple(t.add(semitones) for t in self.tones)
        return Scale(tones=new_tones)

    def triad(self, root=0):
        """Build a triad starting from the given scale degree (0-indexed).

        Returns a chord with the root, 3rd, and 5th above it.
        """
        return self.chord(root, root + 2, root + 4)

    def seventh(self, root=0):
        """Build a seventh chord from the given scale degree (0-indexed).

        Returns a chord with the root, 3rd, 5th, and 7th.
        """
        return self.chord(root, root + 2, root + 4, root + 6)

    def progression(self, *numerals):
        """Build a chord progression from Roman numeral strings.

        Accepts Roman numerals like ``"I"``, ``"IV"``, ``"V"``,
        ``"ii"``, ``"vi"``. Lowercase = minor triad, uppercase = major
        triad. Add ``"7"`` suffix for seventh chords.

        Example::

            >>> scale.progression("I", "IV", "V", "I")
            [<Chord (C,E,G)>, <Chord (F,A,C)>, <Chord (G,B,D)>, <Chord (C,E,G)>]
        """
        import numeral as numeral_mod
        chords = []
        for num in numerals:
            is_seventh = num.endswith("7")
            clean = num.rstrip("7")
            degree = numeral_mod.roman2int(clean.upper()) - 1
            if is_seventh:
                chords.append(self.seventh(degree))
            else:
                chords.append(self.triad(degree))
        return chords

    def nashville(self, *numbers):
        """Build a chord progression using Nashville number system.

        The `Nashville number system <https://en.wikipedia.org/wiki/Nashville_Number_System>`_
        uses Arabic numerals instead of Roman numerals.
        It's the standard chart system in Nashville recording studios.

        Numbers 1-7 build diatonic triads. Suffix ``"7"`` for seventh
        chords, ``"m"`` to force minor.

        Example::

            >>> scale.nashville(1, 4, 5, 1)
            [<Chord C major>, <Chord F major>, <Chord G major>, <Chord C major>]
        """
        from .chords import Chord
        chords = []
        for num in numbers:
            s = str(num)
            is_seventh = s.endswith("7")
            clean = s.rstrip("7m")
            degree = int(clean) - 1
            if is_seventh:
                chords.append(self.seventh(degree))
            else:
                chords.append(self.triad(degree))
        return chords

    @staticmethod
    def detect(*note_names):
        """Detect the most likely scale from a set of note names.

        Tries all scales in the Western system and returns the best
        match as a ``(tonic, scale_name, match_count)`` tuple.

        Example::

            >>> Scale.detect("C", "D", "E", "F", "G", "A", "B")
            ('C', 'major', 7)
            >>> Scale.detect("C", "D", "Eb", "F", "G", "Ab", "Bb")
            ('C', 'minor', 7)
        """
        if not note_names:
            return None

        notes = set(note_names)
        best = None

        chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        scale_names = ["major", "minor", "harmonic minor",
                       "dorian", "phrygian", "lydian", "mixolydian",
                       "aeolian", "locrian"]

        for tonic in chromatic:
            ts = TonedScale(tonic=f"{tonic}4")
            for scale_name in ts.scales:
                try:
                    scale = ts[scale_name]
                    scale_notes = set(scale.note_names)
                    match = len(notes & scale_notes)
                    score = (match, 1 if scale_name == "major" else 0)
                    if best is None or score > best[0]:
                        best = (score, tonic, scale_name, match)
                except (KeyError, ValueError):
                    continue

        if best:
            return (best[1], best[2], best[3])
        return None

    def harmonize(self):
        """Build diatonic triads on every scale degree.

        Returns a list of Chords — one triad for each degree of the
        scale. In a major scale this produces: I, ii, iii, IV, V, vi, vii°.

        Example::

            >>> [c.identify() for c in TonedScale(tonic="C4")["major"].harmonize()]
            ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']
        """
        unique = len(self.tones) - 1
        return [self.triad(i) for i in range(unique)]

    def degree(self, item, major=None, minor=False):
        # TODO: cleanup degrees.

        # Ensure that both major and minor aren't passed.
        if all((major, minor)):
            raise ValueError("You can only specify one of the following: major, minor.")

        # Roman–style degree reference (e.g. "IV").
        if isinstance(item, str):
            degrees = []
            for (i, tone) in enumerate(self.tones):
                degrees.append(numeral.int2roman(i + 1, only_ascii=True))

            if item in degrees:
                item = degrees.index(item)

            # If we're still a string, attempt to grab degree name.
            if isinstance(item, str):
                for i, _degree in enumerate(self.system.degrees):
                    # Match degree name (e.g. "tonic", "dominant")
                    if item == _degree[0]:
                        item = i
                        break

                    # Also match mode name (e.g. "ionian", "dorian")
                    if item in _degree[1]:
                        item = i
                        break

        # List/Tuple–style reference.
        if isinstance(item, int) or isinstance(item, slice):
            return self.tones[item]

    def __getitem__(self, item):
        result = self.degree(item)
        if result is None:
            raise KeyError(item)
        return result


PROGRESSIONS = {
    # Rock / Pop / Folk
    "I-IV-V-I": ("I", "IV", "V", "I"),
    "I-V-vi-IV": ("I", "V", "vi", "IV"),
    "I-vi-IV-V": ("I", "vi", "IV", "V"),
    "I-IV-vi-V": ("I", "IV", "vi", "V"),
    "vi-IV-I-V": ("vi", "IV", "I", "V"),
    # Blues
    "12-bar blues": ("I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"),
    # Jazz
    "ii-V-I": ("ii", "V7", "I"),
    "I-vi-ii-V": ("I", "vi", "ii", "V"),  # rhythm changes A section
    "iii-vi-ii-V": ("iii", "vi", "ii", "V"),  # jazz turnaround
    # Classical / Film
    "i-bVI-bIII-bVII": ("i", "VI", "III", "VII"),
    "Pachelbel": ("I", "V", "vi", "iii", "IV", "I", "IV", "V"),
    # Flamenco / Spanish
    "Andalusian": ("i", "VII", "VI", "V"),
    # Modal
    "Dorian vamp": ("i", "IV"),
    "Mixolydian vamp": ("I", "VII"),
}
"""Common chord progressions as Roman numeral tuples.

Use with :meth:`Scale.progression` or :meth:`Key.progression`::

    Key("C", "major").progression(*PROGRESSIONS["I-V-vi-IV"])
"""


class Key:
    """A musical key — a convenient entry point for scales and harmony.

    A Key represents a tonic note and a mode. It provides quick access
    to the scale, diatonic chords, and common progressions.

    Example::

        >>> key = Key("C", "major")
        >>> key.scale.note_names
        ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
        >>> key.chords
        ['C major', 'D minor', 'E minor', 'F major', ...]
        >>> key.progression("I", "V", "vi", "IV")
        [<Chord (C,E,G)>, <Chord (G,B,D)>, ...]
    """

    def __init__(self, tonic, mode="major", system=None):
        if system is None:
            system = SYSTEMS["western"]
        elif isinstance(system, str):
            system = SYSTEMS[system]
        self.tonic_name = tonic
        self.mode = mode
        self._system = system
        self._toned_scale = TonedScale(tonic=f"{tonic}4", system=system)
        self._scale = self._toned_scale[mode]

    @classmethod
    def detect(cls, *note_names):
        """Detect the most likely key from a set of note names.

        Tries every possible major and minor key and returns the one
        whose scale contains the most of the given notes.

        Example::

            >>> Key.detect("C", "D", "E", "F", "G", "A", "B")
            <Key C major>
            >>> Key.detect("A", "B", "C", "D", "E", "F", "G")
            <Key C major>
            >>> Key.detect("A", "C", "E")
            <Key C major>

        Returns:
            The best-matching Key, or None if no notes given.
        """
        if not note_names:
            return None

        notes = set(note_names)
        best_key = None
        best_score = (-1, 0)

        chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        for tonic in chromatic:
            for mode in ("major", "minor"):
                try:
                    k = cls(tonic, mode)
                    scale_notes = set(k.note_names)
                    match = len(notes & scale_notes)
                    # Tiebreak: prefer major over minor
                    score = (match, 1 if mode == "major" else 0)
                    if score > best_score:
                        best_score = score
                        best_key = k
                except (KeyError, ValueError):
                    continue

        return best_key

    def __repr__(self):
        return f"<Key {self.tonic_name} {self.mode}>"

    def __str__(self):
        return f"{self.tonic_name} {self.mode}"

    @property
    def scale(self):
        """The scale for this key."""
        return self._scale

    @property
    def note_names(self):
        """Note names in this key's scale."""
        return self._scale.note_names

    @property
    def chords(self):
        """Names of all diatonic triads in this key."""
        return [c.identify() for c in self._scale.harmonize()]

    @property
    def seventh_chords(self):
        """Names of all diatonic seventh chords in this key."""
        unique = len(self._scale.tones) - 1
        return [self._scale.seventh(i).identify() for i in range(unique)]

    def triad(self, degree):
        """Build a diatonic triad on the given degree (0-indexed)."""
        return self._scale.triad(degree)

    def seventh(self, degree):
        """Build a diatonic seventh chord on the given degree (0-indexed)."""
        return self._scale.seventh(degree)

    def progression(self, *numerals):
        """Build a chord progression from Roman numerals.

        Example::

            >>> Key("G", "major").progression("I", "IV", "V7", "I")
        """
        return self._scale.progression(*numerals)

    def nashville(self, *numbers):
        """Build a chord progression using Nashville numbers.

        Example::

            >>> Key("G", "major").nashville(1, 4, 5, 1)
        """
        return self._scale.nashville(*numbers)

    def secondary_dominant(self, degree):
        """Build a secondary dominant (V/x) for the given scale degree.

        A secondary dominant is the dominant chord of a non-tonic
        degree. For example, in C major, V/V is D major (the V chord
        of G). Secondary dominants create momentary tonicizations
        that add color and forward motion.

        Common secondary dominants:

        - V/V (e.g. D7 in C major) — approaches the dominant
        - V/ii (e.g. A7 in C major) — approaches the supertonic
        - V/vi (e.g. E7 in C major) — approaches the relative minor

        Args:
            degree: Scale degree to target (1-indexed). ``5`` means
                "build the V of the 5th degree."

        Returns:
            A dominant 7th Chord that resolves to the given degree.

        Example::

            >>> Key("C", "major").secondary_dominant(5)  # V/V = D7
            <Chord D dominant 7th>
        """
        target = self._scale.tones[degree - 1]
        # Build a dominant 7th a perfect 5th above the target
        from .chords import Chord
        root = target.add(7)
        return Chord(tones=[root, root.add(4), root.add(7), root.add(10)])

    @classmethod
    def all_keys(cls):
        """Return all 24 major and minor keys.

        Returns:
            A list of Key objects for all 12 major and 12 minor keys.

        Example::

            >>> for k in Key.all_keys():
            ...     print(k)
        """
        chromatic = ["C", "C#", "D", "D#", "E", "F",
                     "F#", "G", "G#", "A", "A#", "B"]
        keys = []
        for tonic in chromatic:
            keys.append(cls(tonic, "major"))
            keys.append(cls(tonic, "minor"))
        return keys

    @property
    def relative(self):
        """The relative major or minor key.

        If this is a major key, returns the relative minor (vi).
        If this is a minor key, returns the relative major (bIII).
        """
        if self.mode == "major":
            # Relative minor starts on the 6th degree
            minor_tonic = self._scale.tones[5].name
            return Key(minor_tonic, "minor")
        elif self.mode in ("minor", "aeolian"):
            # Relative major starts on the 3rd degree
            major_tonic = self._scale.tones[2].name
            return Key(major_tonic, "major")
        return None

    @property
    def parallel(self):
        """The parallel major or minor key (same tonic, different mode)."""
        if self.mode == "major":
            return Key(self.tonic_name, "minor")
        elif self.mode in ("minor", "aeolian"):
            return Key(self.tonic_name, "major")
        return None


class TonedScale:
    def __init__(self, *, system=SYSTEMS["western"], tonic):
        if isinstance(system, str):
            system = SYSTEMS[system]
        self.system = system

        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(tonic, system=self.system)

        self.tonic = tonic

    def __repr__(self):
        return f"<TonedScale system={self.system!r} tonic={self.tonic}>"

    def __getitem__(self, scale):
        result = self.get(scale)
        if result is None:
            raise KeyError(scale)
        return result

    def get(self, scale):
        try:
            return self._scales[scale]
        except KeyError:
            pass

    @property
    def scales(self):
        return tuple(self._scales.keys())

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
