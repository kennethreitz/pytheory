from __future__ import annotations

from typing import Optional, Union

from .systems import SYSTEMS, System
from .tones import Tone

_PC_LETTERS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _pitch_classes(names):
    """Note names → set of pitch-class ints (enharmonic-aware).

    Accepts a letter plus any run of sharps/flats ("C", "A#", "Bb",
    "C##"); a trailing octave digit is ignored, and names that don't
    parse as Western notes are skipped.
    """
    out = set()
    for name in names:
        name = str(name).strip()
        if not name or name[0].upper() not in _PC_LETTERS:
            continue
        pc = _PC_LETTERS[name[0].upper()]
        for ch in name[1:]:
            if ch in "#♯":
                pc += 1
            elif ch in "b♭":
                pc -= 1
            else:
                break
        out.add(pc % 12)
    return out


class Scale:
    def __init__(self, *, tones: tuple[Tone, ...], degrees: Optional[tuple[str, ...]] = None, system: Union[str, System] = 'western') -> None:
        """Initialize a Scale from a sequence of Tones.

        Args:
            tones: The tones that make up the scale.
            degrees: Optional names for each scale degree (must match length of *tones*).
            system: A tone system name or :class:`System` instance.

        Raises:
            ValueError: If *degrees* is provided but its length differs from *tones*.
        """
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
    def system(self) -> Optional[System]:
        """Return the tone system for this scale.

        Resolves a system name to a :class:`System` object on first access.
        """
        if self._system:
            return self._system

        if self.system_name:
            return SYSTEMS[self.system_name]

    def __repr__(self) -> str:
        r = []
        for (i, tone) in enumerate(self.tones):
            from ._statics import int2roman
            degree = int2roman(i + 1)
            r += [f"{degree}={tone.full_name}"]

        r = " ".join(r)
        return f"<Scale {r}>"

    def __iter__(self):
        """Iterate over the tones in this scale."""
        return iter(self.tones)

    def __len__(self) -> int:
        """Return the number of tones in this scale (including the octave)."""
        return len(self.tones)

    def __contains__(self, item: Union[str, Tone]) -> bool:
        """Check whether a tone or note name belongs to this scale."""
        if isinstance(item, str):
            return any(item == t.name for t in self.tones)
        return item in self.tones

    @property
    def note_names(self) -> list[str]:
        """List of note names in this scale."""
        return [t.name for t in self.tones]

    def fitness(self, *note_names: str) -> float:
        """Score how well a set of notes fits this scale (0.0–1.0).

        Returns the fraction of the given notes that appear in the
        scale. Useful for melody analysis — testing whether a phrase
        belongs to a particular scale or mode.

        Args:
            *note_names: Note name strings (e.g. ``"C"``, ``"F#"``).

        Returns:
            A float from 0.0 (no notes match) to 1.0 (all notes match).

        Example::

            >>> c_major = TonedScale(tonic="C4")["major"]
            >>> c_major.fitness("C", "D", "E", "G")
            1.0
            >>> c_major.fitness("C", "D", "F#", "G")
            0.75
            >>> c_major.fitness("C#", "D#", "F#")
            0.0
        """
        if not note_names:
            return 0.0
        scale_notes = set(self.note_names)
        matches = sum(1 for n in note_names if n in scale_notes)
        return matches / len(note_names)

    _DEGREE_NAMES = [
        "tonic", "supertonic", "mediant", "subdominant",
        "dominant", "submediant", "leading tone",
    ]

    _MINOR_DEGREE_NAMES = [
        "tonic", "supertonic", "mediant", "subdominant",
        "dominant", "submediant", "subtonic",
    ]

    def degree_name(self, n: int, *, minor: bool = False) -> str:
        """Return the traditional name for the nth scale degree (0-indexed).

        Args:
            n: The scale degree index (0 = tonic, 1 = supertonic, etc.).
            minor: If True, use "subtonic" instead of "leading tone" for degree 6.

        Returns:
            A string like "tonic", "dominant", etc.

        Example::

            >>> TonedScale(tonic="C4")["major"].degree_name(0)
            'tonic'
            >>> TonedScale(tonic="C4")["major"].degree_name(4)
            'dominant'
        """
        names = self._MINOR_DEGREE_NAMES if minor else self._DEGREE_NAMES
        if 0 <= n < len(names):
            return names[n]
        return f"degree {n}"

    def chord(self, *degrees: int) -> Chord:
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

    def transpose(self, semitones: int) -> Scale:
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

    def triad(self, root: int = 0) -> Chord:
        """Build a triad starting from the given scale degree (0-indexed).

        Returns a chord with the root, 3rd, and 5th above it.
        """
        return self.chord(root, root + 2, root + 4)

    def seventh(self, root: int = 0) -> Chord:
        """Build a seventh chord from the given scale degree (0-indexed).

        Returns a chord with the root, 3rd, 5th, and 7th.
        """
        return self.chord(root, root + 2, root + 4, root + 6)

    def progression(self, *numerals: str) -> list[Chord]:
        """Build a chord progression from Roman numeral strings.

        The chord's **quality follows the numeral**, not just the scale, so
        the notation says exactly what you mean:

        - **case** sets major vs minor — ``"V"`` is a major triad, ``"v"`` a
          minor one (so an uppercase ``"V"`` in a minor key gives the
          harmonic-minor dominant, and ``"IV"`` in minor gives the Dorian
          major-IV);
        - **quality markers** ``"°"``/``"o"`` (diminished), ``"ø"``
          (half-diminished), ``"+"`` (augmented), ``"maj"`` (major 7th);
        - a **flat/sharp prefix** borrows from outside the key —
          ``"bVII"`` is a major triad on the lowered 7th degree (the
          Mixolydian/​rock ♭VII), ``"bII"`` the Neapolitan, and so on;
        - a trailing **``"7"``** makes it a seventh chord (dominant for an
          uppercase numeral, minor for lowercase);
        - a **slash** marks a secondary/applied chord — ``"V7/V"`` is the
          dominant of the dominant, ``"vii°/ii"`` the leading-tone chord of
          ``ii`` (the part before the slash is read in a major key rooted on
          the target).

        Example::

            >>> scale.progression("I", "IV", "V7", "I")
            [<Chord C major>, <Chord F major>, <Chord G dominant 7th>, <Chord C major>]
            >>> scale.progression("I", "bVII")           # Mixolydian vamp
            [<Chord C major>, <Chord Bb major>]
            >>> scale.progression("I", "V7/V", "V7", "I")
            [<Chord C major>, <Chord D dominant 7th>, <Chord G dominant 7th>, <Chord C major>]
        """
        return [self._chord_from_numeral(num) for num in numerals]

    def _chord_from_numeral(self, numeral: str) -> Chord:
        """Resolve a single Roman-numeral string to a Chord (see
        :meth:`progression`)."""
        from ._statics import roman2int
        from .chords import Chord

        s = numeral.strip()

        # Secondary / applied chords: "V7/V", "V/ii", "vii°/V". The part
        # after the slash names the target; the part before is interpreted
        # in a major key rooted on that target's root.
        if "/" in s:
            applied, target = s.split("/", 1)
            target_root = self._chord_from_numeral(target).tones[0]
            return TonedScale(tonic=target_root)["major"]._chord_from_numeral(applied)

        # Accidental prefix — borrow from outside the key.
        offset = 0
        if s[:1] in ("b", "♭"):
            offset, s = -1, s[1:]
        elif s[:1] in ("#", "♯"):
            offset, s = 1, s[1:]

        # Trailing seventh.
        is_seventh = s.endswith("7")
        if is_seventh:
            s = s[:-1]

        # Quality markers (stripped to leave the bare roman numeral).
        quality = "case"
        low = s.lower()
        if s.endswith(("°", "o")):
            quality, s = "dim", s[:-1]
        elif low.endswith("dim"):
            quality, s = "dim", s[:-3]
        elif s.endswith("ø"):
            quality, s = "halfdim", s[:-1]
        elif s.endswith("+"):
            quality, s = "aug", s[:-1]
        elif low.endswith("aug"):
            quality, s = "aug", s[:-3]
        elif low.endswith("maj"):
            quality, s = "maj", s[:-3]

        degree = roman2int(s.upper()) - 1
        is_major = s.isupper()

        # Root = the scale degree, shifted by any accidental.
        unique = len(self.tones) - 1
        root = self.tones[degree % unique]
        if degree >= unique:
            root = root.add(12 * (degree // unique))
        if offset:
            # Spell a borrowed root with the accidental it was written with
            # (bVII → Bb, not A#).
            root = root.add(offset, prefer_flats=(offset < 0))

        # Intervals above the root for the requested quality.
        if quality == "dim":
            intervals = [3, 6, 9] if is_seventh else [3, 6]
        elif quality == "halfdim":
            intervals = [3, 6, 10]
        elif quality == "aug":
            intervals = [4, 8, 10] if is_seventh else [4, 8]
        elif quality == "maj":
            intervals = [4, 7, 11] if is_seventh else [4, 7]
        elif is_major:
            intervals = [4, 7, 10] if is_seventh else [4, 7]   # dominant 7th
        else:
            intervals = [3, 7, 10] if is_seventh else [3, 7]   # minor 7th

        return Chord(tones=[root] + [root.add(i) for i in intervals])

    def nashville(self, *numbers: Union[int, str]) -> list[Chord]:
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
    def detect(*note_names: str) -> Optional[tuple[str, str, int]]:
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

        # Compare pitch classes, not spellings — "A#" and "Bb" are the
        # same note, and some scales render with mixed spellings.
        notes = _pitch_classes(note_names)
        if not notes:
            return None
        best = None

        chromatic = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        for tonic in chromatic:
            ts = TonedScale(tonic=f"{tonic}4")
            for scale_name in ts.scales:
                try:
                    scale = ts[scale_name]
                    scale_pcs = _pitch_classes(scale.note_names)
                    match = len(notes & scale_pcs)
                    score = (match, 1 if scale_name == "major" else 0)
                    if best is None or score > best[0]:
                        best = (score, tonic, scale_name, match)
                except (KeyError, ValueError):
                    continue

        if best:
            return (best[1], best[2], best[3])
        return None

    @staticmethod
    def recommend(*note_names: str, top: int = 5) -> list[tuple[str, str, float]]:
        """Recommend the best-matching scales for a set of notes, ranked by fitness.

        Tests the given notes against every scale in the Western system
        and returns the top matches. Useful for figuring out what scale
        a melody or chord progression belongs to, or finding alternative
        scales to play over a set of changes.

        Args:
            *note_names: Note name strings (e.g. ``"C"``, ``"E"``, ``"G"``).
            top: Number of results to return (default 5).

        Returns:
            A list of ``(tonic, scale_name, fitness)`` tuples sorted
            by fitness descending. Fitness is 0.0–1.0.

        Example::

            >>> Scale.recommend("C", "D", "E", "G", "A")
            [('C', 'major', 1.0), ('G', 'major', 1.0), ...]
            >>> Scale.recommend("C", "Eb", "F", "Gb", "G", "Bb")
            [('C', 'blues', 1.0), ...]
        """
        if not note_names:
            return []

        results = []
        chromatic = ["C", "C#", "D", "D#", "E", "F",
                     "F#", "G", "G#", "A", "A#", "B"]

        for tonic in chromatic:
            ts = TonedScale(tonic=f"{tonic}4")
            for scale_name in ts.scales:
                try:
                    scale = ts[scale_name]
                    fit = scale.fitness(*note_names)
                    if fit > 0:
                        results.append((tonic, scale_name, fit))
                except (KeyError, ValueError):
                    continue

        # Penalize chromatic scale — it matches everything but tells you nothing
        # Also prefer scales whose length is closer to the input length
        input_len = len(note_names)

        def _score(r):
            tonic, name, fit = r
            penalty = 0.5 if "chromatic" in name else 0
            return (-fit + penalty, abs(input_len - 7), name, tonic)

        results.sort(key=_score)
        return results[:top]

    def harmonize(self) -> list[Chord]:
        """Build diatonic triads on every scale degree.

        Returns a list of Chords — one triad for each degree of the
        scale. In a major scale this produces: I, ii, iii, IV, V, vi, vii°.

        Example::

            >>> [c.identify() for c in TonedScale(tonic="C4")["major"].harmonize()]
            ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']
        """
        unique = len(self.tones) - 1
        return [self.triad(i) for i in range(unique)]

    def parallel_modes(self) -> dict[str, list[str]]:
        """All modes that share the same notes as this scale.

        For example, C major shares its notes with D dorian,
        E phrygian, F lydian, G mixolydian, A aeolian, and
        B locrian.

        Returns:
            A dict mapping ``"tonic mode"`` to note name lists.

        Example::

            >>> c_major = TonedScale(tonic="C4")["major"]
            >>> c_major.parallel_modes()
            {'C ionian': ['C', 'D', 'E', ...], 'D dorian': ['D', 'E', 'F', ...], ...}
        """
        mode_names = ["ionian", "dorian", "phrygian", "lydian",
                      "mixolydian", "aeolian", "locrian"]
        unique = len(self.tones) - 1
        if unique != 7:
            return {}

        result = {}
        for i, mode in enumerate(mode_names):
            if i >= unique:
                break
            tonic = self.tones[i]
            ts = TonedScale(tonic=tonic.full_name)
            try:
                scale = ts[mode]
                result[f"{tonic.name} {mode}"] = scale.note_names
            except KeyError:
                continue
        return result

    def degree(self, item: Union[str, int, slice], major: Optional[bool] = None, minor: bool = False) -> Optional[Union[Tone, tuple[Tone, ...]]]:

        # Ensure that both major and minor aren't passed.
        if all((major, minor)):
            raise ValueError("You can only specify one of the following: major, minor.")

        # Roman–style degree reference (e.g. "IV").
        if isinstance(item, str):
            degrees = []
            for (i, tone) in enumerate(self.tones):
                from ._statics import int2roman
                degrees.append(int2roman(i + 1))

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

    def __getitem__(self, item: Union[str, int, slice]) -> Union[Tone, tuple[Tone, ...]]:
        """Retrieve a tone by scale degree (integer, Roman numeral, or degree name).

        Raises:
            KeyError: If the given degree is not found in this scale.
        """
        result = self.degree(item)
        if result is None:
            raise KeyError(item)
        return result


PROGRESSIONS = {
    # Rock / Pop / Folk
    "I-IV-V-I": ("I", "IV", "V", "I"),
    "I-V-vi-IV": ("I", "V", "vi", "IV"),       # the "four-chord song"
    "I-vi-IV-V": ("I", "vi", "IV", "V"),       # 50s doo-wop
    "I-IV-vi-V": ("I", "IV", "vi", "V"),
    "vi-IV-I-V": ("vi", "IV", "I", "V"),
    "I-iii-IV-V": ("I", "iii", "IV", "V"),
    "I-IV-I-V": ("I", "IV", "I", "V"),         # "La Bamba", "Twist and Shout"
    "I-iii-vi-IV": ("I", "iii", "vi", "IV"),
    "I-IV-V-vi": ("I", "IV", "V", "vi"),       # deceptive pop
    "vi-V-IV-V": ("vi", "V", "IV", "V"),
    # Blues
    "12-bar blues": ("I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"),
    "12-bar quick change": ("I", "IV", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"),
    "8-bar blues": ("I", "I", "IV", "IV", "I", "V", "I", "V"),
    "minor 12-bar blues": ("i", "i", "i", "i", "iv", "iv", "i", "i",
                           "V7", "iv", "i", "V7"),
    # Jazz
    "ii-V-I": ("ii", "V7", "I"),
    "vi-ii-V-I": ("vi", "ii", "V7", "I"),      # extended turnaround
    "I-vi-ii-V": ("I", "vi", "ii", "V"),       # rhythm changes A section
    "iii-vi-ii-V": ("iii", "vi", "ii", "V"),   # jazz turnaround
    "minor ii-V-i": ("ii°", "V7", "i"),
    "ragtime": ("I", "V7/ii", "V7/V", "V7"),   # Sweet Georgia Brown
    "rhythm changes bridge": ("V7/vi", "V7/ii", "V7/V", "V7"),
    # Classical / Film
    "i-bVI-bIII-bVII": ("i", "VI", "III", "VII"),
    "Pachelbel": ("I", "V", "vi", "iii", "IV", "I", "IV", "V"),
    "I-V-vi-iii-IV": ("I", "V", "vi", "iii", "IV"),
    "circle of fifths": ("I", "IV", "vii°", "iii", "vi", "ii", "V", "I"),
    # Flamenco / Spanish
    "Andalusian": ("i", "VII", "VI", "V"),
    # Minor
    "i-iv-v-i": ("i", "iv", "v", "i"),
    "i-iv-VII-III": ("i", "iv", "VII", "III"),
    "i-VI-VII-i": ("i", "VI", "VII", "i"),
    "i-v-VI-IV": ("i", "v", "VI", "IV"),       # "epic" minor
    "i-VII-i": ("i", "VII", "i"),
    # Modal
    "Dorian vamp": ("i", "IV"),
    "Mixolydian vamp": ("I", "bVII"),
    "Aeolian": ("i", "VI", "VII"),
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

    def __init__(self, tonic: str, mode: str = "major", system: Optional[Union[str, System]] = None) -> None:
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
    def detect(cls, *note_names: str) -> Optional[Key]:
        """Detect the most likely key from a set of note names.

        Tries every possible major and minor key and returns the one
        whose scale contains the most of the given notes.

        Notes are compared as pitch classes, so enharmonic spellings
        don't matter — ``"A#"`` and ``"Bb"`` count the same. Ties go
        to the key whose tonic (then fifth) is actually among the
        notes, then to major over minor.

        Example::

            >>> Key.detect("C", "D", "E", "F", "G", "A", "B")
            <Key C major>
            >>> Key.detect("A", "B", "C", "D", "E", "F", "G")
            <Key C major>
            >>> Key.detect("A", "C", "E")
            <Key A minor>

        Returns:
            The best-matching Key, or None if no notes given.
        """
        if not note_names:
            return None

        # Compare pitch classes, not spellings — "A#" and "Bb" are the
        # same note, and a key whose scale renders with mixed spellings
        # must not get extra name-matches for it.
        notes = _pitch_classes(note_names)
        if not notes:
            return None
        best_key = None
        best_score = (-1, 0, 0, 0)

        # Conventional key spellings — Bb major, not the theoretical
        # A# major; C# minor, not Db minor.
        tonics = {
            "major": ["C", "Db", "D", "Eb", "E", "F",
                      "F#", "G", "Ab", "A", "Bb", "B"],
            "minor": ["C", "C#", "D", "Eb", "E", "F",
                      "F#", "G", "G#", "A", "Bb", "B"],
        }
        for mode in ("major", "minor"):
            for tonic_pc, tonic in enumerate(tonics[mode]):
                try:
                    k = cls(tonic, mode)
                    scale_pcs = _pitch_classes(k.note_names)
                    match = len(notes & scale_pcs)
                    # Tiebreaks: a key is more plausible when its tonic
                    # (then its fifth) actually occurs in the notes;
                    # prefer major over minor last.
                    score = (match,
                             1 if tonic_pc in notes else 0,
                             1 if (tonic_pc + 7) % 12 in notes else 0,
                             1 if mode == "major" else 0)
                    if score > best_score:
                        best_score = score
                        best_key = k
                except (KeyError, ValueError):
                    continue

        return best_key

    def __repr__(self) -> str:
        return f"<Key {self.tonic_name} {self.mode}>"

    def __str__(self) -> str:
        return f"{self.tonic_name} {self.mode}"

    @property
    def scale(self) -> Scale:
        """The scale for this key."""
        return self._scale

    @property
    def note_names(self) -> list[str]:
        """Note names in this key's scale."""
        return self._scale.note_names

    @property
    def chords(self) -> list[str]:
        """Names of all diatonic triads in this key."""
        return [c.identify() for c in self._scale.harmonize()]

    @property
    def seventh_chords(self) -> list[str]:
        """Names of all diatonic seventh chords in this key."""
        unique = len(self._scale.tones) - 1
        return [self._scale.seventh(i).identify() for i in range(unique)]

    def triad(self, degree: int) -> Chord:
        """Build a diatonic triad on the given degree (0-indexed)."""
        return self._scale.triad(degree)

    def seventh(self, degree: int) -> Chord:
        """Build a diatonic seventh chord on the given degree (0-indexed)."""
        return self._scale.seventh(degree)

    def progression(self, *numerals: str) -> list[Chord]:
        """Build a chord progression from Roman numerals.

        Example::

            >>> Key("G", "major").progression("I", "IV", "V7", "I")
        """
        return self._scale.progression(*numerals)

    def nashville(self, *numbers: Union[int, str]) -> list[Chord]:
        """Build a chord progression using Nashville numbers.

        Example::

            >>> Key("G", "major").nashville(1, 4, 5, 1)
        """
        return self._scale.nashville(*numbers)

    def secondary_dominant(self, degree: int) -> Chord:
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

    def common_progressions(self) -> dict[str, list]:
        """Named chord progressions realized in this key.

        Returns a dict mapping progression names (from ``PROGRESSIONS``)
        to lists of Chord objects built in this key.

        Example::

            >>> key = Key("C", "major")
            >>> for name, chords in key.common_progressions().items():
            ...     symbols = [c.symbol or str(c) for c in chords]
            ...     print(f"{name}: {' → '.join(symbols)}")
            I-IV-V-I: C → F → G → C
            I-V-vi-IV: C → G → Am → F
            ...
        """
        result = {}
        for name, numerals in PROGRESSIONS.items():
            try:
                result[name] = self.progression(*numerals)
            except (KeyError, ValueError, IndexError):
                continue
        return result

    @classmethod
    def all_keys(cls) -> list[Key]:
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
    def signature(self) -> dict:
        """The key signature — number and names of sharps or flats.

        In Western music, each key has a unique key signature that tells
        you which notes are sharped or flatted throughout a piece.

        Returns:
            A dict with:
            - ``sharps`` (int): number of sharps (0 if flat key)
            - ``flats`` (int): number of flats (0 if sharp key)
            - ``accidentals`` (list[str]): the sharped/flatted note names

        Example::

            >>> Key("G", "major").signature
            {'sharps': 1, 'flats': 0, 'accidentals': ['F#']}
            >>> Key("F", "major").signature
            {'sharps': 0, 'flats': 1, 'accidentals': ['Bb']}
            >>> Key("C", "major").signature
            {'sharps': 0, 'flats': 0, 'accidentals': []}
        """
        # Compare scale notes against the natural notes C D E F G A B
        naturals = {"C", "D", "E", "F", "G", "A", "B"}
        scale_notes = set(self.note_names[:-1])  # exclude octave

        sharps = [n for n in scale_notes if "#" in n]
        flats = [n for n in scale_notes if "b" in n[1:]]  # skip first char for B

        # Order sharps: F C G D A E B
        sharp_order = ["F#", "C#", "G#", "D#", "A#", "E#", "B#"]
        flat_order = ["Bb", "Eb", "Ab", "Db", "Gb", "Cb", "Fb"]

        sharps_sorted = [s for s in sharp_order if s in sharps]
        flats_sorted = [f for f in flat_order if f in flats]

        if sharps_sorted:
            return {"sharps": len(sharps_sorted), "flats": 0, "accidentals": sharps_sorted}
        elif flats_sorted:
            return {"sharps": 0, "flats": len(flats_sorted), "accidentals": flats_sorted}
        else:
            return {"sharps": 0, "flats": 0, "accidentals": []}

    @property
    def borrowed_chords(self) -> list[str]:
        """Chords borrowed from the parallel key.

        Modal interchange (or modal mixture) borrows chords from the
        parallel major or minor key. In C major, the parallel minor
        is C minor, which provides chords like Ab major, Bb major,
        and Eb major — commonly heard in rock, film, and pop music.

        Returns:
            A list of chord names from the parallel key that are NOT
            in the current key's diatonic chords.

        Example::

            >>> Key("C", "major").borrowed_chords
            ['C minor', 'D diminished', 'D# major', ...]
        """
        par = self.parallel
        if par is None:
            return []
        own = set(self.chords)
        return [c for c in par.chords if c not in own]

    def random_progression(self, length: int = 4) -> list:
        """Generate a random diatonic chord progression.

        Uses weighted probabilities based on common chord function:
        I and vi are most common, IV and V are very common, ii is
        common, iii and viidim are rare. Always starts on I and
        ends on I or V.

        Args:
            length: Number of chords (default 4).

        Returns:
            A list of Chord objects.

        Example::

            >>> Key("C", "major").random_progression(4)
            [<Chord C major>, <Chord F major>, <Chord G major>, <Chord C major>]
        """
        import random

        harmonized = self._scale.harmonize()
        unique = len(harmonized)
        # Weights: I=high, ii=med, iii=low, IV=high, V=high, vi=med, vii=low
        weights = [10, 5, 2, 8, 8, 5, 1]
        if unique < len(weights):
            weights = weights[:unique]

        chords = [harmonized[0]]  # Start on I
        for _ in range(length - 2):
            chords.append(random.choices(harmonized, weights=weights, k=1)[0])
        if length > 1:
            # End on I or V
            chords.append(random.choice([harmonized[0], harmonized[4 % unique]]))
        return chords

    # Common chord movement tendencies in major keys (0-indexed degrees).
    # Maps each degree to a list of likely next degrees, ordered by frequency.
    _TENDENCY = {
        0: [3, 4, 5, 1],       # I  → IV, V, vi, ii
        1: [4, 0, 6],           # ii → V, I, vii
        2: [5, 3, 1],           # iii → vi, IV, ii
        3: [4, 0, 1],           # IV → V, I, ii
        4: [0, 5, 3],           # V  → I, vi, IV
        5: [1, 3, 4],           # vi → ii, IV, V
        6: [0, 5],              # vii° → I, vi
    }

    def suggest_next(self, chord) -> list:
        """Suggest likely next chords based on voice-leading tendencies.

        Given a chord in this key, returns a ranked list of chords
        that commonly follow it, based on standard functional harmony
        rules (e.g. V → I, ii → V, IV → V).

        Args:
            chord: A Chord object currently being played.

        Returns:
            A list of Chord objects, most likely first.

        Example::

            >>> key = Key("C", "major")
            >>> g = key.triad(4)  # G major (V)
            >>> [c.symbol for c in key.suggest_next(g)]
            ['C', 'Am', 'F']
        """
        harmonized = self._scale.harmonize()
        unique = len(harmonized)

        # Find which degree this chord is
        chord_id = chord.identify()
        if not chord_id:
            return harmonized[:3]

        degree = None
        for i, h in enumerate(harmonized):
            if h.identify() == chord_id:
                degree = i
                break

        if degree is None:
            return harmonized[:3]

        tendencies = self._TENDENCY.get(degree, [0])
        return [harmonized[d % unique] for d in tendencies]

    @property
    def relative(self) -> Optional[Key]:
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
    def parallel(self) -> Optional[Key]:
        """The parallel major or minor key (same tonic, different mode)."""
        if self.mode == "major":
            return Key(self.tonic_name, "minor")
        elif self.mode in ("minor", "aeolian"):
            return Key(self.tonic_name, "major")
        return None

    def modulation_path(self, target: Key) -> list:
        """Suggest a chord-by-chord path from this key to a target key.

        Strategy:

        - Find pivot chords (common to both keys)
        - Build: [I of current key, pivot chord, V of target key, I of target key]
        - If no pivot chord exists, use chromatic approach:
          [current I, target V, target I]

        Args:
            target: The target Key to modulate to.

        Returns:
            A list of Chord objects forming a modulation path.

        Example::

            >>> path = Key("C", "major").modulation_path(Key("G", "major"))
            >>> len(path)
            4
        """
        from .chords import Chord

        current_I = self.triad(0)
        target_V = target.triad(4)
        target_I = target.triad(0)

        # Find pivot chords
        own_chords = self._scale.harmonize()
        target_chord_names = set(target.chords)

        pivot = None
        for c in own_chords:
            cid = c.identify()
            if cid and cid in target_chord_names and cid != current_I.identify():
                pivot = c
                break

        if pivot is not None:
            return [current_I, pivot, target_V, target_I]
        else:
            # Chromatic approach - no pivot chord
            return [current_I, target_V, target_I]

    def pivot_chords(self, target: Key) -> list[str]:
        """Find chords common to this key and a target key.

        Pivot chords are the bridge for modulation — they belong to
        both keys, so a listener accepts them in either context. The
        more pivot chords two keys share, the smoother the modulation.

        Closely related keys (e.g. C major → G major) share many
        pivot chords. Distant keys (e.g. C major → F# major) share
        few or none.

        Args:
            target: The key to modulate to.

        Returns:
            A list of chord name strings common to both keys.

        Example::

            >>> Key("C", "major").pivot_chords(Key("G", "major"))
            ['G major', 'A minor', 'B minor', 'C major', 'D major', 'E minor']
        """
        own = set(self.chords)
        other = set(target.chords)
        return sorted(own & other)

    # Functional grouping of scale degrees (0-indexed). The same degree
    # positions carry tonic / subdominant / dominant function in both
    # major and minor keys — function follows scale degree, not quality.
    _FUNCTION_DEGREES = {
        "tonic": (0, 2, 5),        # I/i, iii/III, vi/VI
        "subdominant": (1, 3),     # ii/ii°, IV/iv
        "dominant": (4, 6),        # V/v, vii°/VII
    }

    def chords_by_function(self) -> dict[str, list[Chord]]:
        """Group the diatonic triads by harmonic function.

        Functional harmony sorts the seven diatonic chords into three
        families by how they behave: **tonic** chords feel like home
        (I, iii, vi), **subdominant** chords move away from it (ii, IV),
        and **dominant** chords pull back toward it (V, vii°). Chords in
        the same family are largely interchangeable — swapping vi for I,
        or ii for IV, keeps a progression's function intact while
        changing its color.

        The grouping is by scale degree, so it holds for minor keys too
        (i/III/VI are tonic, ii°/iv subdominant, V/VII dominant).

        Returns:
            A dict with ``"tonic"``, ``"subdominant"`` and ``"dominant"``
            keys, each mapping to a list of :class:`Chord` objects.

        Example::

            >>> fams = Key("C", "major").chords_by_function()
            >>> [c.symbol for c in fams["tonic"]]
            ['C', 'Em', 'Am']
            >>> [c.symbol for c in fams["dominant"]]
            ['G', 'Bdim']
        """
        harmonized = self._scale.harmonize()
        n = len(harmonized)
        result: dict[str, list[Chord]] = {}
        for function, degrees in self._FUNCTION_DEGREES.items():
            result[function] = [harmonized[d] for d in degrees if d < n]
        return result

    def tonic_chords(self) -> list[Chord]:
        """Diatonic chords with tonic function (I, iii, vi)."""
        return self.chords_by_function()["tonic"]

    def subdominant_chords(self) -> list[Chord]:
        """Diatonic chords with subdominant function (ii, IV)."""
        return self.chords_by_function()["subdominant"]

    def dominant_chords(self) -> list[Chord]:
        """Diatonic chords with dominant function (V, vii°)."""
        return self.chords_by_function()["dominant"]

    def circle_of_fifths(self) -> dict:
        """Map this key's neighborhood on the circle of fifths.

        The circle of fifths arranges keys so that immediate neighbors
        differ by a single accidental and share most of their diatonic
        chords — which is exactly what makes them feel close and easy to
        modulate between.

        Returns relational data centered on this key:

        - ``key`` — this Key
        - ``position`` — signed place on the circle: number of sharps,
          or negative for flats (C major = 0, G major = 1, F major = -1)
        - ``relative`` — the relative minor/major (shares all notes)
        - ``parallel`` — the parallel minor/major (shares the tonic)
        - ``dominant`` — neighbor a fifth up (sharp side), with the
          diatonic chords shared with it
        - ``subdominant`` — neighbor a fifth down (flat side), with the
          diatonic chords shared with it
        - ``circle`` — the twelve keys of this mode, clockwise from here

        Example::

            >>> cof = Key("C", "major").circle_of_fifths()
            >>> str(cof["dominant"]["key"]), str(cof["subdominant"]["key"])
            ('G major', 'F major')
            >>> str(cof["relative"]), str(cof["parallel"])
            ('A minor', 'C minor')
            >>> len(cof["dominant"]["shared_chords"])
            4
        """
        # The key's own spelling gives conventional neighbor names:
        # the 5th scale degree is the dominant, the 4th the subdominant.
        dominant = Key(self._scale.tones[4].name, self.mode, self._system)
        subdominant = Key(self._scale.tones[3].name, self.mode, self._system)

        sig = self.signature
        position = sig["sharps"] - sig["flats"]

        circle = self._circle_keys()

        return {
            "key": self,
            "position": position,
            "relative": self.relative,
            "parallel": self.parallel,
            "dominant": {"key": dominant,
                         "shared_chords": self.pivot_chords(dominant)},
            "subdominant": {"key": subdominant,
                            "shared_chords": self.pivot_chords(subdominant)},
            "circle": circle,
        }

    # Conventional key-name spelling for each pitch class around the
    # circle, so the twelve-key tour avoids double accidentals.
    _CIRCLE_NAMES = {
        "major": {0: "C", 7: "G", 2: "D", 9: "A", 4: "E", 11: "B",
                  6: "Gb", 1: "Db", 8: "Ab", 3: "Eb", 10: "Bb", 5: "F"},
        "minor": {9: "A", 4: "E", 11: "B", 6: "F#", 1: "C#", 8: "G#",
                  3: "Eb", 10: "Bb", 5: "F", 0: "C", 7: "G", 2: "D"},
    }

    def _circle_keys(self) -> list[Key]:
        """The twelve keys of this mode, clockwise (by fifths) from here."""
        tonic_pc = Tone.from_string(
            f"{self.tonic_name}4", system=self._system).midi % 12
        names = self._CIRCLE_NAMES.get(
            "minor" if self.mode in ("minor", "aeolian") else
            "major" if self.mode == "major" else None)
        keys = []
        for i in range(12):
            pc = (tonic_pc + 7 * i) % 12
            if names is not None:
                keys.append(Key(names[pc], self.mode, self._system))
            else:
                # Unusual mode: step by fifths, accept default spelling.
                name = Tone.from_string(
                    f"{self.tonic_name}4", system=self._system).add(7 * i).name
                keys.append(Key(name, self.mode, self._system))
        return keys

    def negative_harmony(self) -> dict:
        """Negative-harmony map of this key (Ernst Levy reflection).

        Negative harmony mirrors every pitch across the axis that runs
        between the tonic and the dominant. The reflection turns a major
        key's harmony into its "shadow" — major becomes minor, the
        dominant becomes a minor subdominant — while preserving the
        gravitational pull toward the tonic.

        Returns:
            A dict with:

            - ``axis`` — the tonic↔dominant pair the mirror runs between
            - ``axis_notes`` — the two pitches the mirror actually
              bisects (the "hinge": where major and minor third meet)
            - ``negative_dominant`` — the reflection of V, the chord
              that does the dominant's job in the negative world and so
              **bridges** the two harmonic families (e.g. C major → Fm)
            - ``scale`` — the negative scale's note names, from the tonic
            - ``chords`` — each diatonic triad's negative reflection

        Example::

            >>> neg = Key("C", "major").negative_harmony()
            >>> neg["axis"]
            ('C', 'G')
            >>> neg["negative_dominant"].symbol
            'Fm'
            >>> neg["scale"]
            ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']
        """
        tonic_pc = Tone.from_string(
            f"{self.tonic_name}4", system=self._system).midi % 12
        axis_sum = (2 * tonic_pc + 7) % 12

        # Negative harmony darkens toward minor, so flat spellings read
        # more naturally than sharps (Eb, not D#).
        _FLATS = ["C", "Db", "D", "Eb", "E", "F",
                  "Gb", "G", "Ab", "A", "Bb", "B"]

        def pc_name(pc: int) -> str:
            return _FLATS[pc % 12]

        hinge_a, hinge_b = axis_sum // 2, axis_sum - axis_sum // 2

        harmonized = self._scale.harmonize()
        neg_chords = [c.negative_harmony(self) for c in harmonized]

        # Negative scale, spelled from the tonic upward.
        scale_pcs = sorted(
            {(axis_sum - (t.midi % 12)) % 12 for t in self._scale.tones},
            key=lambda pc: (pc - tonic_pc) % 12)
        scale = [pc_name(pc) for pc in scale_pcs]

        return {
            "axis": (self.tonic_name, self._scale.tones[4].name),
            "axis_notes": (pc_name(hinge_a), pc_name(hinge_b)),
            "negative_dominant": self.triad(4).negative_harmony(self),
            "scale": scale,
            "chords": neg_chords,
        }


class TonedScale:
    def __init__(self, *, system: Union[str, System] = SYSTEMS["western"], tonic: Union[str, Tone]) -> None:
        """Initialize a TonedScale with a tonic note and tone system.

        Args:
            system: A tone system name or :class:`System` instance.
            tonic: The tonic note as a string (e.g. ``"C4"``) or :class:`Tone`.
        """
        if isinstance(system, str):
            system = SYSTEMS[system]
        self.system = system

        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(tonic, system=self.system)

        self.tonic = tonic
        self._cached_scales: Optional[dict[str, Scale]] = None

    def __repr__(self) -> str:
        return f"<TonedScale system={self.system!r} tonic={self.tonic}>"

    def __getitem__(self, scale: str) -> Scale:
        """Retrieve a scale by name.

        Raises:
            KeyError: If the named scale is not found in this system.
        """
        result = self.get(scale)
        if result is None:
            raise KeyError(scale)
        return result

    def get(self, scale: str) -> Optional[Scale]:
        """Look up a scale by name, returning ``None`` if not found."""
        try:
            return self._scales[scale]
        except KeyError:
            return None

    @property
    def scales(self) -> tuple[str, ...]:
        """Tuple of all available scale names in this system."""
        return tuple(self._scales.keys())

    @staticmethod
    def _should_prefer_flats(tones: list) -> bool:
        """Determine if a scale should use flat spellings.

        Uses the "no duplicate letters" rule: build the scale with sharps
        first, and if any letter name appears twice (excluding the octave
        repeat at the end), try flats instead. This correctly handles all
        keys on the circle of fifths.
        """
        # Exclude the last tone (octave repeat of the tonic)
        unique_tones = tones[:-1] if len(tones) > 1 else tones
        letters = [t.name[0] for t in unique_tones]
        return len(letters) != len(set(letters))

    @property
    def _scales(self) -> dict[str, Scale]:
        """Lazily computed (and cached) mapping of scale names to Scale objects."""
        if self._cached_scales is not None:
            return self._cached_scales

        # Also check if tonic itself is a flat (always prefer flats then)
        tonic_is_flat = "b" in self.tonic.name and self.tonic.name != "B"

        scales = {}

        for scale_type in self.system.scales:
            for scale in self.system.scales[scale_type]:

                reference_scale = self.system.scales[scale_type][scale]["intervals"]

                # First pass: build with sharps (default)
                working_scale = [self.tonic]
                current_tone = self.tonic
                for interval in reference_scale:
                    current_tone = current_tone.add(interval)
                    working_scale.append(current_tone)

                # Check if we need flats (duplicate letter names)
                if tonic_is_flat or self._should_prefer_flats(working_scale):
                    working_scale = [self.tonic]
                    current_tone = self.tonic
                    for interval in reference_scale:
                        current_tone = current_tone.add(interval, prefer_flats=True)
                        working_scale.append(current_tone)

                scales[scale] = Scale(tones=tuple(working_scale))

        self._cached_scales = scales
        return scales
