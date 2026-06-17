from __future__ import annotations

from typing import Iterator, Optional, Union


class Chord:
    def __init__(self, tones: list[Tone]) -> None:
        """Initialize a Chord from a list of Tone objects.

        Args:
            tones: A list of :class:`Tone` instances that make up the chord.
        """
        self.tones = tones
        self._identify_cache: Optional[str] = None

    @classmethod
    def from_tones(cls, *note_names: str, octave: int = 4) -> Chord:
        """Create a Chord from note name strings.

        Example::

            >>> Chord.from_tones("C", "E", "G")
            <Chord C major>
            >>> Chord.from_tones("A", "C", "E", octave=3)
            <Chord A minor>
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string(f"{n}{octave}", system="western")
            for n in note_names
        ])

    @classmethod
    def from_name(cls, name: str, octave: int = 4) -> Chord:
        """Create a Chord from a chord name like ``"Cmaj7"`` or ``"Am"``.

        Uses the built-in chord chart to find the correct tones,
        then builds the chord at the given octave.

        Example::

            >>> Chord.from_name("C")
            <Chord C major>
            >>> Chord.from_name("Am7")
            <Chord A minor 7th>
            >>> Chord.from_name("G7", octave=3)
            <Chord G dominant 7th>
        """
        from .charts import CHARTS
        from .tones import Tone

        chart = CHARTS.get("western", {})
        if name not in chart:
            raise ValueError(f"Unknown chord: {name!r}")

        named = chart[name]
        tones = []
        for t in named.acceptable_tones:
            tones.append(Tone.from_string(
                f"{t.name}{octave}", system="western"))
        return cls(tones=tones)

    @classmethod
    def from_intervals(cls, root: str, *intervals: int, octave: int = 4) -> Chord:
        """Create a Chord from a root note and semitone intervals.

        Example::

            >>> Chord.from_intervals("C", 4, 7)          # C major
            <Chord C major>
            >>> Chord.from_intervals("G", 4, 7, 10)      # G7
            <Chord G dominant 7th>
            >>> Chord.from_intervals("D", 3, 7)           # D minor
            <Chord D minor>
        """
        from .tones import Tone
        root_tone = Tone.from_string(f"{root}{octave}", system="western")
        tones = [root_tone] + [root_tone.add(i) for i in intervals]
        return cls(tones=tones)

    @classmethod
    def from_midi_message(cls, *note_numbers: int) -> Chord:
        """Create a Chord from MIDI note numbers.

        Example::

            >>> Chord.from_midi_message(60, 64, 67)   # C4, E4, G4
            <Chord C major>
        """
        from .tones import Tone
        return cls(tones=[Tone.from_midi(n) for n in note_numbers])

    # ── Symbol parsing ────────────────────────────────────────────────
    # Maps chord suffix patterns to semitone interval tuples from root.
    _SYMBOL_INTERVALS = {
        # Triads
        "maj": (4, 7),
        "m": (3, 7),
        "min": (3, 7),
        "dim": (3, 6),
        "aug": (4, 8),
        "+": (4, 8),
        "sus2": (2, 7),
        "sus4": (5, 7),
        "5": (7,),
        # Seventh chords
        "maj7": (4, 7, 11),
        "M7": (4, 7, 11),
        "m7": (3, 7, 10),
        "min7": (3, 7, 10),
        "7": (4, 7, 10),
        "dom7": (4, 7, 10),
        "dim7": (3, 6, 9),
        "m7b5": (3, 6, 10),
        "mMaj7": (3, 7, 11),
        "aug7": (4, 8, 10),
        # Ninth chords
        "9": (4, 7, 10, 14),
        "maj9": (4, 7, 11, 14),
        "m9": (3, 7, 10, 14),
        "min9": (3, 7, 10, 14),
        # Sixth chords
        "6": (4, 7, 9),
        "m6": (3, 7, 9),
        # Add chords
        "add9": (4, 7, 14),
        "add11": (4, 7, 17),
        # Eleventh / thirteenth
        "11": (4, 7, 10, 14, 17),
        "13": (4, 7, 10, 14, 17, 21),
    }

    # Root note names — try longest match first (e.g. "C#" before "C").
    _ROOT_NAMES = [
        "A#", "Ab", "A", "Bb", "B", "C#", "Cb", "C",
        "D#", "Db", "D", "Eb", "E", "F#", "Fb", "F",
        "G#", "Gb", "G",
    ]

    @classmethod
    def from_symbol(cls, symbol: str, octave: int = 4) -> Chord:
        """Create a Chord by parsing a standard chord symbol.

        Parses symbols like ``"Cmaj7"``, ``"F#m7b5"``, ``"Bbdim"``,
        ``"Gsus4"``, ``"Dadd9"`` — any root note followed by a quality
        suffix. Unlike ``from_name()``, this doesn't rely on a lookup
        table and can handle any combination.

        Slash chords are voiced with the named bass note lowest:
        ``"C/E"`` gives the first inversion (E4 G4 C5), and a bass
        note from outside the chord (``"C/D"``) is added below the
        root.

        Args:
            symbol: A chord symbol string (e.g. ``"Am7"``, ``"Ebmaj9"``).
            octave: The octave for the root note (default 4).

        Returns:
            A new :class:`Chord` instance.

        Raises:
            ValueError: If the symbol can't be parsed.

        Example::

            >>> Chord.from_symbol("C").identify()
            'C major'
            >>> Chord.from_symbol("F#m7b5").identify()
            'F# half-diminished 7th'
            >>> Chord.from_symbol("Bbmaj7").symbol
            'Bbmaj7'
        """
        from .tones import Tone

        # Slash chord: parse the main symbol, then re-voice so the
        # named bass note is lowest.
        if "/" in symbol:
            main_sym, bass_name = symbol.split("/", 1)
            chord = cls.from_symbol(main_sym, octave=octave)
            bass_ref = Tone.from_string(f"{bass_name}{octave}",
                                        system="western")
            bass_pc = bass_ref.midi % 12
            for n, tone in enumerate(chord.tones):
                if tone.midi is not None and tone.midi % 12 == bass_pc:
                    return chord.inversion(n)
            bass = bass_ref
            while (chord.tones and chord.tones[0].midi is not None
                   and bass.midi >= chord.tones[0].midi):
                bass = bass.subtract(12)
            return cls(tones=[bass] + list(chord.tones))

        # Parse root note
        root_name = None
        suffix = symbol
        for name in cls._ROOT_NAMES:
            if symbol.startswith(name):
                root_name = name
                suffix = symbol[len(name):]
                break

        if root_name is None:
            raise ValueError(f"Cannot parse root note from: {symbol!r}")

        # Empty suffix or just "maj" = major triad
        if suffix == "" or suffix == "M":
            intervals = (4, 7)
        else:
            # Try longest suffix match first
            intervals = None
            for length in range(len(suffix), 0, -1):
                candidate = suffix[:length]
                if candidate in cls._SYMBOL_INTERVALS:
                    intervals = cls._SYMBOL_INTERVALS[candidate]
                    break

            if intervals is None:
                raise ValueError(
                    f"Unknown chord quality: {suffix!r} in {symbol!r}")

        root = Tone.from_string(f"{root_name}{octave}", system="western")
        tones = [root] + [root.add(i) for i in intervals]
        return cls(tones=tones)

    def __repr__(self) -> str:
        name = self.identify()
        if name:
            return f"<Chord {name}>"
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Chord tones={l!r}>"

    def __str__(self) -> str:
        name = self.identify()
        if name:
            return name
        return " ".join(t.full_name for t in self.tones)

    def __iter__(self) -> Iterator[Tone]:
        """Iterate over the tones in this chord."""
        return iter(self.tones)

    def __len__(self) -> int:
        """Return the number of tones in this chord."""
        return len(self.tones)

    def __contains__(self, item: Union[str, Tone]) -> bool:
        """Check if a tone (by name or Tone object) is in this chord."""
        if isinstance(item, str):
            return any(item == t.name for t in self.tones)
        return item in self.tones

    def __add__(self, other: Chord) -> Chord:
        """Merge two chords into one (layer their tones).

        Example::

            >>> c_major = Chord.from_tones("C", "E", "G")
            >>> g_bass = Chord.from_tones("G", octave=2)
            >>> slash = c_major + g_bass  # C/G
        """
        if isinstance(other, Chord):
            return Chord(tones=list(self.tones) + list(other.tones))
        return NotImplemented

    def tritone_sub(self) -> Chord:
        """Return the tritone substitution of this chord.

        In jazz harmony, any dominant chord can be replaced by the
        dominant chord a tritone (6 semitones) away. G7 → Db7,
        C7 → F#7. This works because the two chords share the same
        tritone interval (the 3rd and 7th swap roles).

        Returns a new Chord transposed by 6 semitones.
        """
        return self.transpose(6)

    def negative_harmony(self, key="C") -> Chord:
        """Reflect this chord across the negative-harmony axis of a key.

        Negative harmony (Ernst Levy, popularized by Jacob Collier)
        mirrors every pitch across the axis running between a key's
        tonic and its dominant. The reflection swaps the bright and
        dark worlds: in C major a C major triad becomes C minor, and
        the dominant G becomes a minor subdominant (Fm) that resolves
        home just as strongly — its "negative dominant."

        Reflected tones are placed in the nearest octave to the
        originals, so the result keeps a compact voicing, then sorted
        low to high.

        Args:
            key: The tonal center to mirror around — a :class:`Key`, a
                :class:`Tone`, or a tonic name like ``"C"`` or ``"Eb"``
                (default ``"C"``).

        Returns:
            A new :class:`Chord`, the negative-harmony reflection.

        Example::

            >>> Chord.from_symbol("C").negative_harmony("C").identify()
            'C minor'
            >>> # the dominant's reflection — same four notes as Fm6
            >>> Chord.from_symbol("G7").negative_harmony("C").identify()
            'D half-diminished 7th'
        """
        from .tones import Tone

        if hasattr(key, "tonic_name"):        # a Key
            tonic_name = key.tonic_name
        elif isinstance(key, Tone):
            tonic_name = key.name
        else:
            tonic_name = str(key)
        tonic_pc = Tone.from_string(f"{tonic_name}4", system="western").midi % 12
        axis_sum = (2 * tonic_pc + 7) % 12

        new_tones = []
        for t in self.tones:
            if t.midi is None:
                new_tones.append(t)
                continue
            m = t.midi
            refl_pc = (axis_sum - (m % 12)) % 12
            base = (m // 12) * 12 + refl_pc
            nearest = min((base - 12, base, base + 12),
                          key=lambda x: abs(x - m))
            new_tones.append(Tone.from_midi(nearest))

        new_tones.sort(key=lambda t: t.midi if t.midi is not None else 0)
        result = Chord(tones=new_tones)
        result._identify_cache = None
        return result

    def inversion(self, n: int = 1) -> Chord:
        """Return the nth inversion of this chord.

        An inversion moves the lowest tone(s) up by one octave:

        - 0th inversion = root position (unchanged)
        - 1st inversion = move root up an octave
        - 2nd inversion = move root and 3rd up an octave

        Example::

            >>> c_major = Chord([C4, E4, G4])
            >>> c_major.inversion(1)   # E4, G4, C5
            >>> c_major.inversion(2)   # G4, C5, E5
        """
        if n == 0:
            return Chord(tones=list(self.tones))
        tones = list(self.tones)
        for _ in range(n):
            if not tones:
                break
            tone = tones.pop(0)
            tones.append(tone.add(12))
        result = Chord(tones=tones)
        result._identify_cache = None
        return result

    # ── Neo-Riemannian transformations ────────────────────────────────
    # The P/L/R operations turn one consonant triad into another by moving
    # a single voice, flipping major <-> minor each time. Generated
    # together they reach all 24 major/minor triads — the group behind the
    # Tonnetz and a lot of chromatic / film-score harmony.

    @staticmethod
    def _triad(root_pc: int, quality: str) -> "Chord":
        """Build a close-position major or minor triad on a pitch class."""
        third = 4 if quality == "major" else 3
        base = 60 + (root_pc % 12)
        return Chord.from_midi_message(base, base + third, base + 7)

    def _plr_state(self) -> tuple:
        """This chord as a ``(root_pc, quality)`` pair, or raise if it isn't
        a plain major/minor triad."""
        from ._statics import C_INDEX
        quality = self.quality
        if quality not in ("major", "minor") or len(self.pitch_classes) != 3:
            raise ValueError(
                "Neo-Riemannian transformations require a major or minor triad."
            )
        root_pc = (self.root._index - C_INDEX) % 12
        return root_pc, quality

    def parallel(self) -> "Chord":
        """**P** — the parallel transformation: swap major ↔ minor on the
        same root (C major ↔ C minor). Moves the third by a semitone.

        Example::

            >>> Chord.from_name("C").parallel().identify()
            'C minor'
        """
        root_pc, quality = self._plr_state()
        return Chord._triad(root_pc, "minor" if quality == "major" else "major")

    def relative(self) -> "Chord":
        """**R** — the relative transformation: a triad to its relative
        (C major ↔ A minor). Moves one voice by a whole tone.

        Example::

            >>> Chord.from_name("C").relative().identify()
            'A minor'
        """
        root_pc, quality = self._plr_state()
        if quality == "major":
            return Chord._triad((root_pc + 9) % 12, "minor")
        return Chord._triad((root_pc + 3) % 12, "major")

    def leading_tone_exchange(self) -> "Chord":
        """**L** — the *Leittonwechsel*: exchange a triad with the one a
        major third away of opposite quality (C major → E minor, A minor →
        F major). Moves one voice by a semitone.

        Example::

            >>> Chord.from_name("C").leading_tone_exchange().identify()
            'E minor'
        """
        root_pc, quality = self._plr_state()
        if quality == "major":
            return Chord._triad((root_pc + 4) % 12, "minor")
        return Chord._triad((root_pc + 8) % 12, "major")

    def transform(self, sequence: str) -> "Chord":
        """Apply a sequence of ``P``/``L``/``R`` transformations, left to right.

        Args:
            sequence: A string like ``"LPR"`` or ``"PLR"`` (spaces ignored,
                case-insensitive).

        Example::

            >>> Chord.from_name("C").transform("LP").identify()
            'E major'
        """
        ops = {
            "P": Chord.parallel,
            "L": Chord.leading_tone_exchange,
            "R": Chord.relative,
        }
        chord = self
        for ch in sequence.upper().replace(" ", ""):
            if ch not in ops:
                raise ValueError(
                    f"Unknown transformation {ch!r}; use P, L, and R."
                )
            chord = ops[ch](chord)
        return chord

    def tonnetz_path(self, other: "Chord") -> str:
        """Shortest sequence of P/L/R transformations turning this triad into
        ``other`` — their distance on the Tonnetz.

        Returns:
            A string of ``P``/``L``/``R`` (empty if the triads are already
            equal). Both chords must be major or minor triads.

        Example::

            >>> Chord.from_name("C").tonnetz_path(Chord.from_name("Am"))
            'R'
            >>> Chord.from_name("C").tonnetz_path(Chord.from_name("E"))
            'LP'
        """
        from collections import deque

        start, goal = self._plr_state(), other._plr_state()
        if start == goal:
            return ""

        def neighbors(state):
            root_pc, quality = state
            if quality == "major":
                yield "P", (root_pc, "minor")
                yield "L", ((root_pc + 4) % 12, "minor")
                yield "R", ((root_pc + 9) % 12, "minor")
            else:
                yield "P", (root_pc, "major")
                yield "L", ((root_pc + 8) % 12, "major")
                yield "R", ((root_pc + 3) % 12, "major")

        queue = deque([(start, "")])
        seen = {start}
        while queue:
            state, path = queue.popleft()
            for op, nxt in neighbors(state):
                if nxt == goal:
                    return path + op
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + op))
        return ""  # unreachable: PLR connects all 24 triads

    def transpose(self, semitones: int) -> Chord:
        """Return a new Chord transposed by the given number of semitones.

        Every tone in the chord is shifted up (positive) or down
        (negative) by the same interval, preserving the chord's
        quality and voicing.

        Example::

            >>> c_major = Chord([C4, E4, G4])
            >>> c_major.transpose(7).identify()
            'G major'
        """
        result = Chord(tones=[t.add(semitones) for t in self.tones])
        result._identify_cache = None
        return result

    def close_voicing(self) -> Chord:
        """Rearrange tones so they are packed within one octave ascending from root.

        All tones are brought into the same octave as the root and sorted
        ascending by pitch class.

        Example::

            >>> Chord.from_symbol("C").inversion(2).close_voicing().identify()
            'C major'
        """
        if not self.tones:
            return Chord(tones=[])
        root = self.tones[0]
        root_octave = root.octave or 4
        result = [root]
        for t in self.tones[1:]:
            # Bring into root octave, above root
            interval = (t - root) % 12
            if interval == 0:
                interval = 12
            new_tone = root.add(interval)
            result.append(new_tone)
        # Sort by interval from root (skip root itself)
        result = [result[0]] + sorted(result[1:], key=lambda t: (t - root) % 12)
        return Chord(tones=result)

    def open_voicing(self) -> Chord:
        """Spread tones across two octaves by moving alternating tones up an octave.

        Starting from close voicing, every other non-root tone (indices 1, 3, ...)
        is raised by an octave, creating a wider, more open sound.

        Example::

            >>> c = Chord.from_symbol("Cmaj7").open_voicing()
            >>> len(c.tones)
            4
        """
        closed = self.close_voicing()
        tones = list(closed.tones)
        for i in range(1, len(tones)):
            if i % 2 == 1:
                tones[i] = tones[i].add(12)
        return Chord(tones=tones)

    def drop2(self) -> Chord:
        """Drop-2 voicing: take the second-highest voice and drop it down an octave.

        A standard jazz guitar voicing technique that creates wider spacing
        between voices while maintaining harmonic function.

        Example::

            >>> Chord.from_symbol("Cmaj7").drop2()
            <Chord C major 7th>
        """
        closed = self.close_voicing()
        tones = list(closed.tones)
        if len(tones) < 2:
            return Chord(tones=tones)
        # Second-highest is index -2
        dropped = tones[-2].add(-12)
        new_tones = [dropped] + tones[:-2] + [tones[-1]]
        return Chord(tones=new_tones)

    def drop3(self) -> Chord:
        """Drop-3 voicing: take the third-highest voice and drop it down an octave.

        Creates an even wider voicing than drop-2. Common in big band
        arranging and guitar chord melody.

        Example::

            >>> Chord.from_symbol("Cmaj7").drop3()
            <Chord C major 7th>
        """
        closed = self.close_voicing()
        tones = list(closed.tones)
        if len(tones) < 3:
            return Chord(tones=tones)
        # Third-highest is index -3
        dropped = tones[-3].add(-12)
        new_tones = [dropped] + tones[:-3] + tones[-2:]
        return Chord(tones=new_tones)

    def extensions(self, scale=None) -> list:
        """Suggest available chord extensions (9th, 11th, 13th).

        If a scale is provided, extensions are checked against the scale.
        Otherwise, extensions are checked to be at least a whole step from
        existing chord tones (the "avoid note" rule).

        Args:
            scale: Optional Scale object to check extensions against.

        Returns:
            A list of Tone objects representing valid extensions.

        Example::

            >>> Chord.from_symbol("C").extensions()
            [<Tone D5>, <Tone A5>]
        """
        from .tones import Tone

        if not self.tones:
            return []

        root = self.tones[0]
        # Extension intervals from root in semitones
        ext_intervals = {
            "9th": 14,   # major 9th
            "11th": 17,  # perfect 11th
            "13th": 21,  # major 13th
        }

        chord_pcs = set()
        for t in self.tones:
            chord_pcs.add((t - root) % 12)

        result = []
        for name, interval in ext_intervals.items():
            ext_tone = root.add(interval)
            ext_pc = interval % 12

            if scale is not None:
                # Check if the extension is in the scale
                scale_names = [st.name for st in scale.tones]
                if ext_tone.name in scale_names:
                    result.append(ext_tone)
            else:
                # "Avoid note" rule: extension must be at least 2 semitones
                # from every existing chord tone (pitch class)
                is_available = True
                for pc in chord_pcs:
                    diff = min((ext_pc - pc) % 12, (pc - ext_pc) % 12)
                    if diff < 2:
                        is_available = False
                        break
                if is_available:
                    result.append(ext_tone)

        return result

    @property
    def root(self) -> Optional[Tone]:
        """The root of this chord (if identifiable).

        Returns the Tone that serves as the root based on chord
        identification, or None if the chord can't be identified.
        """
        chord_id = self.identify()
        if not chord_id:
            return None
        root_name = chord_id.split(" ", 1)[0]
        for t in self.tones:
            if t.name == root_name:
                return t
        return None

    @property
    def quality(self) -> Optional[str]:
        """The quality of this chord (e.g. 'major', 'minor 7th').

        Returns the quality string from chord identification, or
        None if the chord can't be identified.
        """
        chord_id = self.identify()
        if not chord_id:
            return None
        parts = chord_id.split(" ", 1)
        return parts[1] if len(parts) > 1 else None

    @property
    def intervals(self) -> list[int]:
        """Semitone distances between adjacent tones in the chord.

        Returns a list of integers, where each value is the absolute
        number of semitones between consecutive tones. This is
        octave-invariant — a major third is always 4 semitones whether
        it's C4→E4 or C6→E6.

        Common interval values::

            1  = minor 2nd (half step)
            2  = major 2nd (whole step)
            3  = minor 3rd
            4  = major 3rd
            5  = perfect 4th
            6  = tritone
            7  = perfect 5th
            12 = octave

        Example::

            >>> c_major = Chord(tones=[C4, E4, G4])
            >>> c_major.intervals
            [4, 3]  # major 3rd + minor 3rd

        Returns an empty list for chords with fewer than 2 tones.
        """
        if len(self.tones) < 2:
            return []
        return [abs(self.tones[i] - self.tones[i - 1])
                for i in range(1, len(self.tones))]

    @property
    def harmony(self) -> float:
        """Consonance score based on frequency ratio simplicity.

        Computed by examining the frequency ratio between every pair of
        tones, reducing it to its simplest fractional form (limited to
        denominators ≤ 32), and summing ``1 / (numerator + denominator)``.

        The psychoacoustic basis: intervals whose frequencies form simple
        integer ratios are perceived as consonant. A perfect fifth (3:2)
        scores higher than a tritone (45:32) because simpler ratios
        produce fewer interfering overtones.

        Reference consonance scores for common intervals::

            Octave (2:1)     → 1/(2+1)  = 0.333
            Perfect 5th (3:2) → 1/(3+2)  = 0.200
            Perfect 4th (4:3) → 1/(4+3)  = 0.143
            Major 3rd (5:4)  → 1/(5+4)  = 0.111
            Tritone (45:32)  → 1/(45+32) = 0.013

        For chords with multiple tones, all pairwise ratios are summed —
        a C major triad (C-E-G) scores higher than C-E-Gb because the
        C-G fifth contributes a large consonance term.

        Returns 0 for chords with fewer than 2 tones.
        """
        if len(self.tones) < 2:
            return 0

        from fractions import Fraction
        score = 0.0
        for i in range(len(self.tones)):
            for j in range(i + 1, len(self.tones)):
                f1 = self.tones[i].pitch()
                f2 = self.tones[j].pitch()
                if f1 == 0 or f2 == 0:
                    continue
                ratio = Fraction(f2 / f1).limit_denominator(32)
                score += 1.0 / (ratio.numerator + ratio.denominator)
        return score

    @property
    def dissonance(self) -> float:
        """Sensory dissonance score using the Plomp-Levelt roughness model.

        When two tones are close in frequency, their waveforms interfere
        and produce a perceived "roughness." This roughness peaks when
        the frequency difference is about 25% of the critical bandwidth
        (roughly 1/4 of the lower frequency) and diminishes for wider
        or narrower separations.

        The model: for each pair of tones, compute
        ``x = freq_diff / critical_bandwidth`` using the Bark-scale
        critical bandwidth formula (Zwicker & Terhardt, 1980):
        ``CB = 25 + 75 * (1 + 1.4 * (f/1000)^2)^0.69``
        then apply the Plomp-Levelt curve ``x * e^(1-x)``. This peaks
        at x=1 (maximum roughness) and decays for larger intervals.

        Practical implications:

        - A minor 2nd (C4-Db4, ~15 Hz apart) produces high roughness
        - A major 3rd (C4-E4, ~68 Hz apart) produces moderate roughness
        - A perfect 5th (C4-G4, ~130 Hz apart) produces low roughness
        - Roughness is frequency-dependent: the same interval sounds
          rougher in lower registers because the critical bandwidth is
          narrower relative to the frequency difference

        Based on: Plomp, R. & Levelt, W.J.M. (1965). "Tonal consonance
        and critical bandwidth." *Journal of the Acoustical Society of
        America*, 38(4), 548-560.

        Returns 0 for chords with fewer than 2 tones.
        """
        if len(self.tones) < 2:
            return 0

        import math
        roughness = 0.0
        for i in range(len(self.tones)):
            for j in range(i + 1, len(self.tones)):
                f1 = self.tones[i].pitch()
                f2 = self.tones[j].pitch()
                f_min = min(f1, f2)
                f_max = max(f1, f2)
                if f_min == 0:
                    continue
                # Bark-scale critical bandwidth (Zwicker & Terhardt, 1980)
                cb = 25 + 75 * (1 + 1.4 * (f_min / 1000) ** 2) ** 0.69
                diff = f_max - f_min
                if cb > 0:
                    x = diff / cb
                    roughness += x * math.exp(1 - x) if x > 0 else 0
        return roughness

    @property
    def beat_frequencies(self) -> list[tuple[Tone, Tone, float]]:
        """Beat frequencies (Hz) between all pairs of tones in the chord.

        When two tones with frequencies f1 and f2 are played together,
        their waveforms interfere and produce an amplitude modulation
        at the *beat frequency*: ``|f1 - f2|`` Hz.

        Perceptual ranges:

        - **< 1 Hz**: very slow pulsing, used in tuning (e.g. tuning a
          guitar string against a reference — you hear the beats slow
          down as you approach the correct pitch)
        - **1–15 Hz**: audible beating, perceived as a rhythmic pulse
        - **15–30 Hz**: transition zone — too fast for individual beats,
          perceived as roughness/buzzing
        - **> 30 Hz**: no longer perceived as beating; becomes part of
          the perceived timbre or is heard as a difference tone

        Returns a list of ``(tone_a, tone_b, beat_hz)`` tuples sorted
        by beat frequency ascending (slowest/most perceptible first).

        Example::

            >>> chord = Chord(tones=[A4, A4_slightly_sharp])
            >>> chord.beat_frequencies
            [(A4, A4+, 2.5)]  # 2.5 Hz beating — clearly audible

        Returns an empty list for chords with fewer than 2 tones.
        """
        if len(self.tones) < 2:
            return []

        beats = []
        for i in range(len(self.tones)):
            for j in range(i + 1, len(self.tones)):
                f1 = self.tones[i].pitch()
                f2 = self.tones[j].pitch()
                beats.append((self.tones[i], self.tones[j], abs(f1 - f2)))
        return sorted(beats, key=lambda b: b[2])

    @property
    def beat_pulse(self) -> float:
        """The slowest (most perceptible) beat frequency in the chord, in Hz.

        This is the beat frequency between the two tones closest in
        pitch — the pair that produces the most audible amplitude
        modulation. In a well-tuned chord this value is typically 0
        (unison pairs) or very large (distinct intervals); a non-zero
        value under ~15 Hz indicates perceptible beating that may
        suggest the chord is slightly out of tune.

        Returns 0 for chords with fewer than 2 tones, or when all
        tones are identical (perfect unison).
        """
        beats = self.beat_frequencies
        if not beats:
            return 0
        for _, _, hz in beats:
            if hz > 0:
                return hz
        return 0

    # ── Chord quality patterns (semitones from root) ──────────────────
    _CHORD_PATTERNS = {
        "major": {0, 4, 7},
        "minor": {0, 3, 7},
        "diminished": {0, 3, 6},
        "augmented": {0, 4, 8},
        "sus2": {0, 2, 7},
        "sus4": {0, 5, 7},
        "power": {0, 7},
        "dominant 7th": {0, 4, 7, 10},
        "major 7th": {0, 4, 7, 11},
        "minor 7th": {0, 3, 7, 10},
        "diminished 7th": {0, 3, 6, 9},
        "half-diminished 7th": {0, 3, 6, 10},
        "minor-major 7th": {0, 3, 7, 11},
        "augmented 7th": {0, 4, 8, 10},
        "dominant 9th": {0, 2, 4, 7, 10},
        "major 9th": {0, 2, 4, 7, 11},
        "minor 9th": {0, 2, 3, 7, 10},
    }

    def identify(self) -> Optional[str]:
        """Identify this chord by name (root + quality).

        Tries each tone as a potential root and checks if the remaining
        intervals match a known chord pattern. Returns the name with the
        simplest match (fewest tones in the pattern preferred for ties).

        Known patterns include major, minor, diminished, augmented,
        sus2, sus4, power chords, and all common 7th/9th chords.

        Returns:
            A string like ``"C major"``, ``"A minor 7th"``, or ``None``
            if no known pattern matches.

        Example::

            >>> Chord([C4, E4, G4]).identify()
            'C major'
            >>> Chord([A4, C5, E5]).identify()
            'A minor'
        """
        if self._identify_cache is not None:
            return self._identify_cache

        if len(self.tones) < 2:
            return None

        from .tones import Tone

        for root in self.tones:
            pitch_classes = set()
            for tone in self.tones:
                interval = (tone - root) % 12
                pitch_classes.add(interval)

            for name, pattern in self._CHORD_PATTERNS.items():
                if pitch_classes == pattern:
                    self._identify_cache = f"{root.name} {name}"
                    return self._identify_cache
        return None

    _SYMBOL_MAP = {
        "major": "",
        "minor": "m",
        "diminished": "dim",
        "augmented": "aug",
        "sus2": "sus2",
        "sus4": "sus4",
        "power": "5",
        "dominant 7th": "7",
        "major 7th": "maj7",
        "minor 7th": "m7",
        "diminished 7th": "dim7",
        "half-diminished 7th": "m7b5",
        "minor-major 7th": "mMaj7",
        "augmented 7th": "aug7",
        "dominant 9th": "9",
        "major 9th": "maj9",
        "minor 9th": "m9",
    }

    @property
    def symbol(self) -> Optional[str]:
        """Standard chord symbol (e.g. ``"Cmaj7"``, ``"Dm"``, ``"G7"``).

        Returns the compact notation used in lead sheets and fake books,
        or ``None`` if the chord can't be identified.

        Example::

            >>> Chord([C4, E4, G4]).symbol
            'C'
            >>> Chord([C4, E4, G4, B4]).symbol
            'Cmaj7'
            >>> Chord([A4, C5, E5]).symbol
            'Am'
            >>> Chord([G4, B4, D5, F5]).symbol
            'G7'
        """
        name = self.identify()
        if not name:
            return None
        parts = name.split(" ", 1)
        root = parts[0]
        quality = parts[1] if len(parts) > 1 else "major"
        suffix = self._SYMBOL_MAP.get(quality, quality)
        return f"{root}{suffix}"

    def voice_leading(self, other: Chord) -> list[tuple[Tone, Tone, int]]:
        """Find the smoothest voice leading to another chord.

        Voice leading is the art of moving individual voices (tones)
        from one chord to the next with minimal motion. Good voice
        leading prefers stepwise motion (1-2 semitones) and contrary
        motion between voices.

        This method finds the assignment of tones that minimizes the
        total semitone movement. For chords of different sizes, extra
        tones are held or dropped as needed.

        Args:
            other: The target :class:`Chord` to voice-lead to.

        Returns:
            A list of ``(from_tone, to_tone, semitones)`` tuples
            describing how each voice moves. Sorted by voice (highest
            to lowest). ``semitones`` is signed: positive = up,
            negative = down.

        Example::

            >>> c_major = Chord([C4, E4, G4])
            >>> f_major = Chord([C4, F4, A4])
            >>> c_major.voice_leading(f_major)
            [(<Tone G4>, <Tone A4>, 2),
             (<Tone E4>, <Tone F4>, 1),
             (<Tone C4>, <Tone C4>, 0)]
        """
        import itertools

        src = list(self.tones)
        dst = list(other.tones)

        while len(src) < len(dst):
            src.append(src[-1])
        while len(dst) < len(src):
            dst.append(dst[-1])

        best_cost = float("inf")
        best_assignment = None

        for perm in itertools.permutations(range(len(dst))):
            cost = sum(abs(src[i] - dst[perm[i]]) for i in range(len(src)))
            if cost < best_cost:
                best_cost = cost
                best_assignment = perm

        result = []
        for i, j in enumerate(best_assignment):
            movement = dst[j] - src[i]
            result.append((src[i], dst[j], movement))
        return sorted(result, key=lambda v: v[0].pitch(), reverse=True)

    def analyze(self, key_tonic: Union[str, Tone], mode: str = "major") -> Optional[str]:
        """Roman numeral analysis of this chord relative to a key.

        In tonal music, every chord has a **function** determined by
        its relationship to the key center. The Roman numeral system
        describes this: uppercase for major chords, lowercase for minor,
        with degree symbols for diminished.

        Args:
            key_tonic: The tonic note name (e.g. ``"C"``) or a Tone.
            mode: ``"major"`` or ``"minor"`` (default ``"major"``).

        Returns:
            A string like ``"I"``, ``"IV"``, ``"V7"``, ``"ii"``,
            ``"vi"``, or ``None`` if the chord doesn't fit the key.

        Example::

            >>> Chord([C4, E4, G4]).analyze("C")
            'I'
            >>> Chord([G4, B4, D5]).analyze("C")
            'V'
            >>> Chord([D4, F4, A4]).analyze("C")
            'ii'
        """
        from ._statics import int2roman
        from .scales import TonedScale
        from .systems import SYSTEMS
        from .tones import Tone

        if isinstance(key_tonic, str):
            key_tonic_tone = Tone.from_string(key_tonic + "4", system="western")
        else:
            key_tonic_tone = key_tonic

        system = key_tonic_tone._system or SYSTEMS.get(
            key_tonic_tone.system_name, SYSTEMS["western"])
        scale = TonedScale(tonic=key_tonic_tone.full_name, system=system)[mode]

        chord_id = self.identify()
        if not chord_id:
            return None

        parts = chord_id.split(" ", 1)
        root_name = parts[0]
        quality = parts[1] if len(parts) > 1 else ""

        scale_names = [t.name for t in scale.tones[:-1]]

        def _build_numeral(root, quality, degree_idx, prefix=""):
            numeral_str = int2roman(degree_idx + 1)
            suffix = ""
            if "minor" in quality:
                numeral_str = numeral_str.lower()
            if "diminished" in quality:
                numeral_str = numeral_str.lower()
                suffix = "dim"
            if "augmented" in quality:
                suffix = "+"
            if "7th" in quality:
                suffix += "7"
            if "9th" in quality:
                suffix += "9"
            return prefix + numeral_str + suffix

        # Diatonic match
        if root_name in scale_names:
            degree_idx = scale_names.index(root_name)
            return _build_numeral(root_name, quality, degree_idx)

        # Chromatic / borrowed chord — find by semitone distance from tonic
        tonic_tone = scale.tones[0]
        root_tone = Tone.from_string(root_name + "4", system="western")
        semitones = (root_tone - tonic_tone) % 12

        # Map semitone distances to flat-degree labels
        chromatic_degrees = {
            1: ("b", 1), 3: ("b", 2), 6: ("b", 4),
            8: ("b", 5), 10: ("b", 6),
        }
        if semitones in chromatic_degrees:
            prefix, deg_idx = chromatic_degrees[semitones]
            return _build_numeral(root_name, quality, deg_idx, prefix=prefix)

        return None

    @property
    def tension(self) -> dict:
        """Harmonic tension score and resolution suggestions.

        Tension in tonal music arises from specific intervallic
        content — primarily the **tritone** (6 semitones), the most
        unstable interval in Western harmony. The dominant 7th chord
        (e.g. G7 = G-B-D-F) contains a tritone between B and F,
        which "wants" to resolve: B pulls up to C, F pulls down to E.

        This property analyzes:

        - **Tritone count**: each tritone adds significant tension
        - **Minor 2nd count**: semitone clashes add dissonance
        - **Dominant function**: the combination of major 3rd + minor 7th
          is the strongest tendency tone pattern in Western music

        Returns:
            A dict with:

            - ``score`` (float): 0.0 = fully resolved, 1.0 = max tension
            - ``tritones`` (int): number of tritone intervals
            - ``minor_seconds`` (int): number of semitone clashes
            - ``has_dominant_function`` (bool): contains the 3-7 tritone

        Example::

            >>> g7 = Chord([G4, B4, D5, F5])
            >>> g7.tension['has_dominant_function']
            True
            >>> g7.tension['tritones']
            1
        """
        if len(self.tones) < 2:
            return {"score": 0.0, "tritones": 0, "minor_seconds": 0,
                    "has_dominant_function": False}

        tritones = 0
        minor_seconds = 0

        for i in range(len(self.tones)):
            for j in range(i + 1, len(self.tones)):
                interval = abs(self.tones[i] - self.tones[j]) % 12
                if interval == 6:
                    tritones += 1
                if interval == 1 or interval == 11:
                    minor_seconds += 1

        has_dominant = False
        chord_id = self.identify()
        if chord_id and "dominant" in chord_id:
            has_dominant = True

        score = min(1.0, (tritones * 0.35) + (minor_seconds * 0.15) +
                    (0.25 if has_dominant else 0.0))

        return {
            "score": score,
            "tritones": tritones,
            "minor_seconds": minor_seconds,
            "has_dominant_function": has_dominant,
        }

    def slash(self, bass_note: str, *, octave: int = 3) -> Chord:
        """Return a slash chord — this chord over a different bass note.

        Slash chords (e.g. C/G, Am/E) place a specific note in the
        bass voice below the rest of the chord. They're written as
        ``Chord/Bass`` in lead sheets and are used for bass lines that
        move stepwise beneath held chords.

        Common uses:

        - **C/E** — first inversion, smooth bass line C→D→E
        - **C/G** — second inversion, strong bass on the fifth
        - **D/F#** — passing tone in bass, very common in pop

        Args:
            bass_note: Note name for the bass (e.g. ``"G"``, ``"F#"``).
            octave: Octave for the bass note (default 3, one below middle).

        Returns:
            A new Chord with the bass note prepended.

        Example::

            >>> Chord.from_symbol("C").slash("G")
            <Chord C major>
        """
        from .tones import Tone
        bass = Tone.from_string(f"{bass_note}{octave}", system="western")
        return Chord(tones=[bass] + list(self.tones))

    @property
    def slash_name(self) -> Optional[str]:
        """Slash chord name if the lowest tone isn't the root.

        Returns ``"C/G"`` style notation when the bass differs from
        the chord root, or the plain symbol otherwise.

        Example::

            >>> Chord.from_symbol("C").slash("E").slash_name
            'C/E'
        """
        sym = self.symbol
        if not sym:
            return None
        root = self.root
        if root is None:
            return sym
        bass = self.tones[0]
        if bass.name != root.name:
            return f"{sym}/{bass.name}"
        return sym

    def add_tone(self, tone) -> Chord:
        """Return a new Chord with an additional tone.

        Example::

            >>> c_major = Chord.from_tones("C", "E", "G")
            >>> c_major.add_tone(Tone.from_string("B4", system="western"))
            <Chord C major 7th>
        """
        return Chord(tones=list(self.tones) + [tone])

    def remove_tone(self, tone_name: str) -> Chord:
        """Return a new Chord with tones of the given name removed.

        Args:
            tone_name: The note name to remove (e.g. "G").

        Example::

            >>> cmaj7 = Chord.from_name("Cmaj7")
            >>> cmaj7.remove_tone("B")   # Remove the 7th
            <Chord C major>
        """
        return Chord(tones=[t for t in self.tones if t.name != tone_name])

    # ── Figured Bass ─────────────────────────────────────────────────

    @property
    def figured_bass(self) -> Optional[str]:
        """Return figured bass notation for this chord.

        Figured bass describes the intervals above the lowest note.
        Used in classical music theory and continuo playing.

        Returns:
            A string like ``"6"``, ``"6/4"``, ``"7"``, ``"6/5"``,
            ``"4/3"``, ``"2"``, or ``""`` for root position triads.
            None if the chord can't be identified.

        Example::

            >>> Chord([C4, E4, G4]).figured_bass  # root position
            ''
            >>> Chord([E4, G4, C5]).figured_bass  # first inversion
            '6'
            >>> Chord([G4, C5, E5]).figured_bass  # second inversion
            '6/4'
        """
        chord_id = self.identify()
        if not chord_id:
            return None

        # Find root name from identification
        root_name = chord_id.split(" ", 1)[0]
        quality = chord_id.split(" ", 1)[1] if " " in chord_id else ""
        is_seventh = "7th" in quality or "9th" in quality

        # Find the bass note (lowest by pitch)
        bass = min(self.tones, key=lambda t: t.pitch())
        bass_name = bass.name

        # Check if bass is the root (handle enharmonics)
        if bass_name == root_name:
            # Root position
            if is_seventh:
                return "7"
            return ""

        # Find root tone object
        root_tone = None
        for t in self.tones:
            if t.name == root_name:
                root_tone = t
                break

        if root_tone is None:
            return None

        # Determine which chord degree the bass is
        bass_interval = (bass - root_tone) % 12

        # Get the pattern for this quality
        pattern = self._CHORD_PATTERNS.get(quality)
        if pattern is None:
            return None

        sorted_pattern = sorted(pattern)
        if bass_interval not in sorted_pattern:
            return None

        inversion = sorted_pattern.index(bass_interval)

        if is_seventh:
            fb_map = {0: "7", 1: "6/5", 2: "4/3", 3: "2"}
            return fb_map.get(inversion, None)
        else:
            fb_map = {0: "", 1: "6", 2: "6/4"}
            return fb_map.get(inversion, None)

    def analyze_figured(self, key_tonic, mode="major") -> Optional[str]:
        """Roman numeral analysis with figured bass inversion symbols.

        Combines the Roman numeral from :meth:`analyze` with the
        figured bass symbol from :attr:`figured_bass`.

        Args:
            key_tonic: The tonic note name (e.g. ``"C"``) or a Tone.
            mode: ``"major"`` or ``"minor"`` (default ``"major"``).

        Returns:
            A string like ``"V7"``, ``"ii6"``, or ``None``.

        Example::

            >>> Chord([G4, B4, D5, F5]).analyze_figured("C")
            'V7'
        """
        roman = self.analyze(key_tonic, mode)
        if roman is None:
            return None
        fb = self.figured_bass
        if fb is None:
            return roman
        # Don't duplicate "7" — if the Roman numeral already ends with "7"
        # and figured bass is just "7" (root position seventh), skip it.
        if fb == "7" and roman.endswith("7"):
            return roman
        if fb:
            return f"{roman}{fb}"
        return roman

    # ── Pitch Class Set Theory ─────────────────────────────────────

    # Forte number catalog for trichords and tetrachords.
    _FORTE_NUMBERS = {
        # Trichords (3 notes)
        (0, 1, 2): "3-1",
        (0, 1, 3): "3-2",
        (0, 1, 4): "3-3",
        (0, 1, 5): "3-4",
        (0, 1, 6): "3-5",
        (0, 2, 4): "3-6",
        (0, 2, 5): "3-7",
        (0, 2, 6): "3-8",
        (0, 2, 7): "3-9",
        (0, 3, 6): "3-10",
        (0, 3, 7): "3-11",    # major/minor triad
        (0, 4, 8): "3-12",    # augmented triad
        # Tetrachords (4 notes)
        (0, 1, 2, 3): "4-1",
        (0, 1, 2, 4): "4-2",
        (0, 1, 3, 4): "4-3",
        (0, 1, 2, 5): "4-4",
        (0, 1, 2, 6): "4-5",
        (0, 1, 2, 7): "4-6",
        (0, 1, 4, 5): "4-7",
        (0, 1, 5, 6): "4-8",
        (0, 1, 6, 7): "4-9",
        (0, 2, 3, 5): "4-10",
        (0, 1, 3, 5): "4-11",
        (0, 2, 3, 6): "4-12",
        (0, 1, 3, 6): "4-13",
        (0, 2, 3, 7): "4-14",
        (0, 1, 4, 6): "4-z15",
        (0, 1, 5, 7): "4-16",
        (0, 3, 4, 7): "4-17",
        (0, 1, 4, 7): "4-18",
        (0, 1, 4, 8): "4-19",
        (0, 1, 5, 8): "4-20",
        (0, 2, 4, 6): "4-21",
        (0, 2, 4, 7): "4-22",
        (0, 2, 5, 7): "4-23",
        (0, 2, 4, 8): "4-24",
        (0, 2, 6, 8): "4-25",
        (0, 3, 5, 8): "4-26",
        (0, 2, 5, 8): "4-27",
        (0, 3, 6, 9): "4-28",    # diminished 7th
        (0, 1, 3, 7): "4-z29",
    }

    @property
    def pitch_classes(self) -> set:
        """Return the set of pitch classes (0-11) in this chord.

        Pitch class 0 = C, 1 = C#/Db, 2 = D, ..., 11 = B.
        Octave information is removed.

        Example::

            >>> Chord([C4, E4, G4]).pitch_classes
            {0, 4, 7}
        """
        from ._statics import C_INDEX
        result = set()
        for tone in self.tones:
            pc = (tone._index - C_INDEX) % 12
            result.add(pc)
        return result

    @staticmethod
    def _find_normal_form(pcs_sorted):
        """Find the normal form of a sorted list of pitch classes."""
        n = len(pcs_sorted)
        if n <= 1:
            return tuple(pcs_sorted)

        best = None
        best_span = 13

        for start in range(n):
            rotation = [pcs_sorted[(start + i) % n] for i in range(n)]
            span = (rotation[-1] - rotation[0]) % 12

            if span < best_span:
                best_span = span
                best = rotation
            elif span == best_span:
                # Tiebreak: compare intervals from bottom
                for k in range(1, n):
                    a = (rotation[k] - rotation[0]) % 12
                    b = (best[k] - best[0]) % 12
                    if a < b:
                        best = rotation
                        break
                    elif a > b:
                        break

        return tuple(best)

    @property
    def normal_form(self) -> tuple:
        """Return the normal form -- most compact ascending arrangement.

        The normal form is the rotation of pitch classes that spans
        the smallest interval. This is used in set theory analysis.

        Example::

            >>> Chord([C4, E4, G4]).normal_form
            (0, 4, 7)
        """
        pcs = sorted(self.pitch_classes)
        return self._find_normal_form(pcs)

    @property
    def prime_form(self) -> tuple:
        """Return the prime form -- transposed to start on 0, most compact.

        Prime form is the canonical representation used for Forte number
        lookup. It compares the normal form of the set and its inversion,
        picks whichever is more compact, and transposes to start on 0.

        Example::

            >>> Chord([C4, E4, G4]).prime_form
            (0, 4, 7)
            >>> Chord([A4, C5, E5]).prime_form  # minor triad
            (0, 3, 7)
        """
        nf = self.normal_form
        if len(nf) <= 1:
            return (0,) * len(nf) if nf else ()

        # Transpose normal form to start on 0
        t0 = nf[0]
        nf_transposed = tuple((pc - t0) % 12 for pc in nf)

        # Compute inversion: 12 - each pc
        inv_pcs = sorted(set((12 - pc) % 12 for pc in self.pitch_classes))
        inv_nf = self._find_normal_form(inv_pcs)
        inv_t0 = inv_nf[0]
        inv_transposed = tuple((pc - inv_t0) % 12 for pc in inv_nf)

        # Pick whichever is more compact (smaller intervals from bottom)
        for a, b in zip(nf_transposed, inv_transposed):
            if a < b:
                return nf_transposed
            elif a > b:
                return inv_transposed
        return nf_transposed

    @property
    def forte_number(self) -> Optional[str]:
        """Return the Forte number for this pitch class set.

        Forte numbers catalog all possible pitch class sets by cardinality
        and ordering. They are the standard reference in post-tonal theory.

        Example::

            >>> Chord([C4, E4, G4]).forte_number
            '3-11'
            >>> Chord([C4, E4, G4, Bb4]).forte_number
            '4-27'
        """
        pf = self.prime_form
        return self._FORTE_NUMBERS.get(pf, None)

    @property
    def interval_vector(self) -> tuple:
        """Return the interval-class vector ``<ic1 ic2 ic3 ic4 ic5 ic6>``.

        Each entry counts how many times an interval class (1–6 semitones,
        folding 7–11 down to their complements) appears among all pairs of
        pitch classes. It's a fingerprint of a set's sonority — e.g. the
        major triad and its inversion the minor triad share ``(0,0,1,1,1,0)``,
        which is why they sound related.

        Example::

            >>> Chord.from_name("C").interval_vector
            (0, 0, 1, 1, 1, 0)
            >>> Chord.from_name("Cdim7").interval_vector   # symmetrical
            (0, 0, 4, 0, 0, 2)
        """
        pcs = sorted(self.pitch_classes)
        vector = [0, 0, 0, 0, 0, 0]
        for i in range(len(pcs)):
            for j in range(i + 1, len(pcs)):
                ic = (pcs[j] - pcs[i]) % 12
                if ic > 6:
                    ic = 12 - ic
                if ic >= 1:
                    vector[ic - 1] += 1
        return tuple(vector)

    @property
    def complement(self) -> "Chord":
        """Return the literal complement — a Chord of every pitch class
        *not* in this one (voiced from C4 upward).

        Together a set and its complement fill the twelve-note aggregate.
        Complements have a close set-theoretic relationship (their interval
        vectors differ by a fixed amount), which underlies a lot of
        twelve-tone and atonal writing.

        Raises:
            ValueError: if this chord already contains all twelve pitch
                classes (its complement is empty).

        Example::

            >>> Chord.from_name("C").complement.pitch_classes
            {1, 2, 3, 5, 6, 8, 9, 10, 11}
        """
        present = self.pitch_classes
        missing = sorted(pc for pc in range(12) if pc not in present)
        if not missing:
            raise ValueError("The aggregate (all 12 pitch classes) has no complement.")
        return Chord.from_midi_message(*(60 + pc for pc in missing))

    def _tn_type(self) -> tuple:
        """Transpositional set type: normal form transposed to start on 0.

        Two sets are transpositions of each other iff their Tn-types match.
        Unlike :pyattr:`prime_form`, this does *not* fold in inversion.
        """
        nf = self.normal_form
        if not nf:
            return ()
        t0 = nf[0]
        return tuple((pc - t0) % 12 for pc in nf)

    def is_transposition_of(self, other: "Chord") -> bool:
        """Is this set a pure transposition (Tₙ) of ``other``?

        Example::

            >>> Chord.from_name("C").is_transposition_of(Chord.from_name("G"))
            True
            >>> Chord.from_name("C").is_transposition_of(Chord.from_name("Cm"))
            False
        """
        return self._tn_type() == other._tn_type()

    def is_set_class_equivalent(self, other: "Chord") -> bool:
        """Are the two sets in the same set class — related by transposition
        and/or inversion (TₙI)? Equivalent to sharing a prime form / Forte
        number.

        Example::

            >>> # major and minor triads are inversions of one another
            >>> Chord.from_name("C").is_set_class_equivalent(Chord.from_name("Cm"))
            True
        """
        return self.prime_form == other.prime_form

    def is_z_related(self, other: "Chord") -> bool:
        """Are the two sets Z-related — same interval vector but *different*
        set class? Z-related sets share an interval content yet can't be
        mapped onto each other by transposition or inversion (the smallest
        pair is Forte 4-z15 / 4-z29).
        """
        return (self.interval_vector == other.interval_vector
                and self.prime_form != other.prime_form)

    def is_subset_of(self, other: "Chord") -> bool:
        """Are this chord's pitch classes a literal subset of ``other``'s?"""
        return self.pitch_classes <= other.pitch_classes

    def is_superset_of(self, other: "Chord") -> bool:
        """Are this chord's pitch classes a literal superset of ``other``'s?"""
        return self.pitch_classes >= other.pitch_classes

    def fingering(self, *positions: int) -> "Fingering":
        """Apply fret positions to each tone, returning a Fingering.

        Each position value is added (in semitones) to the corresponding
        tone. The number of positions must match the number of tones.

        Args:
            *positions: One integer per tone indicating the fret offset.

        Returns:
            A :class:`Fingering` labeled with tone names.

        Raises:
            ValueError: If the number of positions doesn't match the
                number of tones.
        """
        from .charts import Fingering

        if not len(positions) == len(self.tones):
            raise ValueError(
                "The number of positions must match the number of tones (strings)."
            )

        string_names = tuple(t.name for t in self.tones)
        return Fingering(positions, string_names)


class Fretboard:
    def __init__(self, *, tones: list[Tone], high_to_low: bool = False,
                 _canonical: bool = False) -> None:
        """Initialize a Fretboard from a list of open-string Tone objects.

        Args:
            tones: A list of :class:`Tone` instances representing the
                open strings. By default these are read **low to high**
                (low string first) — pass ``high_to_low=True`` if your
                list runs high to low instead.
            high_to_low: Orientation of this fretboard. When ``False``
                (the default since v0.43.0), strings and fingerings read
                low to high; when ``True``, they read high to low (the
                pre-0.43 behavior).
            _canonical: Internal flag — when ``True``, *tones* are already
                in canonical (high-to-low) order and are stored as-is.
                Used by the instrument presets.
        """
        self.high_to_low = high_to_low
        # Internally we always store strings high-to-low; this keeps the
        # fingering scorer and chord-override tables (which assume that
        # order) untouched. User-facing access is re-oriented on the way out.
        if _canonical or high_to_low:
            self._tones = list(tones)
        else:
            self._tones = list(reversed(tones))

    def _orient(self, seq):
        """Re-orient a canonical (high-to-low) sequence for display.

        Returns *seq* unchanged when this board reads high-to-low, or
        reversed when it reads low-to-high. Self-inverse, so it also maps
        user-supplied (oriented) input back to canonical order.
        """
        return list(seq) if self.high_to_low else list(reversed(seq))

    @property
    def tones(self) -> list[Tone]:
        """The open-string tones in this board's orientation.

        Low-to-high by default; high-to-low when ``high_to_low=True``.
        """
        return self._orient(self._tones)

    @classmethod
    def _from_canonical(cls, tone_strings, high_to_low: bool = False) -> Fretboard:
        """Build a board from canonical (high-to-low) tone-name strings.

        Used by the instrument presets, whose tunings are written in the
        conventional high-to-low order. *high_to_low* sets only the
        board's display orientation.
        """
        from .tones import Tone
        return cls(
            tones=[Tone.from_string(t, system="western") for t in tone_strings],
            high_to_low=high_to_low,
            _canonical=True,
        )

    def __repr__(self) -> str:
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Fretboard tones={l!r}>"

    def capo(self, fret: int) -> Fretboard:
        """Return a new Fretboard with a capo at the given fret.

        A `capo <https://en.wikipedia.org/wiki/Capo>`_ clamps across
        all strings at a fret, raising every string's pitch by that
        many semitones. This lets you play open chord shapes in
        higher keys.

        Common uses:

        - Capo 2 + G shapes = A major voicings
        - Capo 4 + C shapes = E major voicings
        - Capo 7 + D shapes = A major voicings (bright, high register)

        Example::

            >>> fb = Fretboard.guitar(capo=2)
            >>> # Open strings are now F#4 C#4 A3 E3 B2 F#2
            >>> # Playing a "G shape" sounds as A major

        Args:
            fret: The fret number to place the capo (1-12).

        Returns:
            A new Fretboard with all strings raised by ``fret`` semitones.
        """
        return Fretboard(
            tones=[t.add(fret) for t in self._tones],
            high_to_low=self.high_to_low,
            _canonical=True,
        )

    def __iter__(self) -> Iterator[Tone]:
        """Iterate over the open-string tones of this fretboard."""
        return iter(self.tones)

    def __len__(self) -> int:
        """Return the number of strings on this fretboard."""
        return len(self._tones)

    INSTRUMENTS = [
        "guitar", "twelve_string", "bass", "ukulele",
        "mandolin", "mandola", "octave_mandolin", "mandocello",
        "violin", "viola", "cello", "double_bass",
        "banjo", "harp", "pedal_steel", "keyboard",
        "bouzouki", "oud", "sitar", "shamisen", "erhu",
        "charango", "pipa", "balalaika", "lute",
    ]
    """List of all available instrument preset names."""

    TUNINGS = {
        "standard": ("E4", "B3", "G3", "D3", "A2", "E2"),
        "drop d": ("E4", "B3", "G3", "D3", "A2", "D2"),
        "open g": ("D4", "B3", "G3", "D3", "G2", "D2"),
        "open d": ("D4", "A3", "F#3", "D3", "A2", "D2"),
        "open e": ("E4", "B3", "G#3", "E3", "B2", "E2"),
        "open a": ("E4", "C#4", "A3", "E3", "A2", "E2"),
        "dadgad": ("D4", "A3", "G3", "D3", "A2", "D2"),
        "half step down": ("D#4", "A#3", "F#3", "C#3", "G#2", "D#2"),
    }

    @classmethod
    def guitar(cls, tuning: Union[str, tuple[str, ...]] = "standard", capo: int = 0,
               high_to_low: bool = False) -> Fretboard:
        """Guitar with the given tuning and optional capo.

        Args:
            tuning: Tuning name, or a tuple of tone strings. A custom
                tuple is read **low to high** by default (pass
                ``high_to_low=True`` to give it high to low instead).
                Built-in tunings: standard, drop d, open g, open d,
                open e, open a, dadgad, half step down.
            capo: Fret number for the capo (0 = no capo). Raises all
                strings by this many semitones.
            high_to_low: When ``True``, the resulting board reads high to
                low (pre-0.43 behavior); otherwise low to high.
        """
        from .tones import Tone
        if isinstance(tuning, str):
            # Built-in tunings are defined canonically (high to low).
            canonical = [Tone.from_string(t, system="western") for t in cls.TUNINGS[tuning]]
            fb = cls(tones=canonical, high_to_low=high_to_low, _canonical=True)
        else:
            # A user-supplied tuple is in the board's orientation.
            fb = cls(tones=[Tone.from_string(t, system="western") for t in tuning],
                     high_to_low=high_to_low)
        if capo:
            fb = fb.capo(capo)
        return fb

    @classmethod
    def bass(cls, five_string: bool = False, high_to_low: bool = False) -> Fretboard:
        """Standard bass guitar tuning.

        Args:
            five_string: If True, adds a low B string (B0).
            high_to_low: When ``True``, the board reads high to low.
        """
        strings = ["G2", "D2", "A1", "E1"]
        if five_string:
            strings.append("B0")
        return cls._from_canonical(strings, high_to_low)

    @classmethod
    def ukulele(cls, high_to_low: bool = False) -> Fretboard:
        """Standard ukulele tuning (A4 E4 C4 G4).

        Re-entrant tuning: the G4 string is higher than C4.
        """
        return cls._from_canonical(["A4", "E4", "C4", "G4"], high_to_low)

    @classmethod
    def mandolin(cls, high_to_low: bool = False) -> Fretboard:
        """Standard mandolin tuning (E5 A4 D4 G3).

        Tuned in fifths, same as a violin but one octave relationship.
        Strings are typically doubled (paired courses).
        """
        return cls._from_canonical(["E5", "A4", "D4", "G3"], high_to_low)

    @classmethod
    def mandola(cls, high_to_low: bool = False) -> Fretboard:
        """Standard mandola tuning (A4 D4 G3 C3).

        The mandola (or tenor mandola) is to the mandolin what the
        viola is to the violin — a fifth lower, with a warmer,
        darker tone. Tuned in fifths like all the mandolin family.
        """
        return cls._from_canonical(["A4", "D4", "G3", "C3"], high_to_low)

    @classmethod
    def octave_mandolin(cls, high_to_low: bool = False) -> Fretboard:
        """Octave mandolin tuning (E4 A3 D3 G2).

        Also called the octave mandola in European terminology.
        One octave below the mandolin — same tuning as the violin
        family's cello-to-violin relationship. Popular in Irish
        and Celtic folk music.
        """
        return cls._from_canonical(["E4", "A3", "D3", "G2"], high_to_low)

    @classmethod
    def mandocello(cls, high_to_low: bool = False) -> Fretboard:
        """Mandocello tuning (A3 D3 G2 C2).

        The bass of the mandolin family. Tuned like a cello — an
        octave below the mandola. Rare but beautiful; used in
        mandolin orchestras.
        """
        return cls._from_canonical(["A3", "D3", "G2", "C2"], high_to_low)

    @classmethod
    def violin(cls, high_to_low: bool = False) -> Fretboard:
        """Standard violin tuning (E5 A4 D4 G3).

        Tuned in perfect fifths. The violin has no frets — intonation
        is continuous, allowing vibrato and microtonal inflections
        not possible on fretted instruments.
        """
        return cls._from_canonical(["E5", "A4", "D4", "G3"], high_to_low)

    @classmethod
    def viola(cls, high_to_low: bool = False) -> Fretboard:
        """Standard viola tuning (A4 D4 G3 C3).

        A perfect fifth below the violin. The viola's darker, warmer
        tone comes from its larger body and lower register.
        """
        return cls._from_canonical(["A4", "D4", "G3", "C3"], high_to_low)

    @classmethod
    def cello(cls, high_to_low: bool = False) -> Fretboard:
        """Standard cello tuning (A3 D3 G2 C2).

        An octave below the viola. Tuned in fifths. The cello spans
        the range of the human voice — tenor through bass.
        """
        return cls._from_canonical(["A3", "D3", "G2", "C2"], high_to_low)

    @classmethod
    def banjo(cls, tuning: Union[str, tuple[str, ...]] = "open g",
              high_to_low: bool = False) -> Fretboard:
        """Banjo with the given tuning.

        Args:
            tuning: ``"open g"`` (default, bluegrass) or ``"open d"``
                (old-time, clawhammer). The 5th string is a high
                drone — a defining feature of the banjo sound. A custom
                tuple is read low to high unless ``high_to_low=True``.
            high_to_low: When ``True``, the board reads high to low.

        Standard open G: G4 D3 G3 B3 D4 (5th string is the short
        high G4 drone).
        """
        from .tones import Tone
        tunings = {
            "open g": ("D4", "B3", "G3", "D3", "G4"),
            "open d": ("D4", "A3", "F#3", "D3", "A4"),
            "double c": ("D4", "C4", "G3", "C3", "G4"),
        }
        if isinstance(tuning, str):
            return cls._from_canonical(tunings[tuning], high_to_low)
        return cls(tones=[Tone.from_string(t, system="western") for t in tuning],
                   high_to_low=high_to_low)

    @classmethod
    def double_bass(cls, high_to_low: bool = False) -> Fretboard:
        """Standard double bass (upright bass) tuning (G2 D2 A1 E1).

        The largest and lowest-pitched bowed string instrument in the
        orchestra. Unlike the rest of the string family, the double
        bass is tuned in fourths (like a bass guitar) rather than
        fifths.

        The 5-string double bass adds a low B0 or C1.
        """
        return cls._from_canonical(["G2", "D2", "A1", "E1"], high_to_low)

    @classmethod
    def harp(cls, high_to_low: bool = False) -> Fretboard:
        """Concert harp strings — 47 strings spanning C1 to G7.

        The pedal harp has 7 strings per octave (one per note name),
        tuned to Cb major. Pedals alter each note name by up to two
        semitones across all octaves simultaneously.

        This returns the full set of 47 strings in the default
        Cb (enharmonic B) tuning.
        """
        # 47 strings: C1 to G7, one per diatonic note
        notes = ["C", "D", "E", "F", "G", "A", "B"]
        strings = []
        # Start from bottom: C1 D1 E1 ... up to G7
        for octave in range(1, 8):
            for note in notes:
                strings.append(f"{note}{octave}")
                if note == "G" and octave == 7:
                    break
            else:
                continue
            break
        # Canonical (high to low)
        strings.reverse()
        return cls._from_canonical(strings, high_to_low)

    @classmethod
    def pedal_steel(cls, high_to_low: bool = False) -> Fretboard:
        """Pedal steel guitar — E9 Nashville tuning (10 strings).

        The standard tuning for country music. The pedal steel has
        foot pedals and knee levers that change string pitches during
        play, enabling its signature swooping, crying sound.
        """
        # E9 Nashville tuning (canonical: high to low)
        strings = ["F#4", "D#4", "G#3", "E3", "B3", "G#3",
                    "F#3", "E3", "D3", "B2"]
        return cls._from_canonical(strings, high_to_low)

    @classmethod
    def bouzouki(cls, variant: Union[str, tuple[str, ...]] = "irish",
                 high_to_low: bool = False) -> Fretboard:
        """Bouzouki tuning.

        Args:
            variant: ``"irish"`` (default, GDAD) or ``"greek"`` (CFAD).
                A custom tuple is read low to high unless
                ``high_to_low=True``.
            high_to_low: When ``True``, the board reads high to low.

        The Irish bouzouki is a staple of Celtic music, usually tuned
        in unison or octave pairs. The Greek bouzouki traditionally
        has 3 or 4 courses and a brighter, more metallic sound.
        """
        from .tones import Tone
        tunings = {
            "irish": ("D4", "A3", "D3", "G2"),
            "greek": ("D4", "A3", "F3", "C3"),
        }
        if isinstance(variant, str):
            return cls._from_canonical(tunings[variant], high_to_low)
        return cls(tones=[Tone.from_string(t, system="western") for t in variant],
                   high_to_low=high_to_low)

    @classmethod
    def oud(cls, high_to_low: bool = False) -> Fretboard:
        """Standard Arabic oud tuning (C4 G3 D3 A2 G2 C2).

        The oud is the ancestor of the European lute and the defining
        instrument of Arabic, Turkish, and Persian classical music.
        It is fretless, allowing the quarter-tone inflections
        essential to maqam performance. 6 courses (11 strings),
        typically tuned in fourths.
        """
        strings = ["C4", "G3", "D3", "A2", "G2", "C2"]
        return cls._from_canonical(strings, high_to_low)

    @classmethod
    def sitar(cls, high_to_low: bool = False) -> Fretboard:
        """Sitar main playing strings (approximation).

        The sitar typically has 6-7 main strings and 11-13 sympathetic
        strings (taraf). This models the main playing strings in a
        common tuning. The actual tuning varies by raga and tradition.

        Main strings: Sa Sa Pa Sa Re Sa Ma (approximated in 12-TET).
        Represented here as the most common Ravi Shankar school tuning.
        """
        # Common Ravi Shankar tuning mapped to Western notes
        # (sitar is tuned relative to Sa, typically C# or D)
        strings = ["C4", "C3", "G3", "C3", "D3", "C2", "F2"]
        return cls._from_canonical(strings, high_to_low)

    @classmethod
    def shamisen(cls, high_to_low: bool = False) -> Fretboard:
        """Standard shamisen tuning — honchoshi (C4 G3 C3).

        The shamisen is a 3-stringed Japanese instrument played with
        a large plectrum (bachi). Three standard tunings:

        - honchoshi (本調子): root-5th-root
        - niagari (二上り): root-5th-2nd (raises 2nd string)
        - sansagari (三下り): root-5th-b7th (lowers 3rd string)
        """
        return cls._from_canonical(["C4", "G3", "C3"], high_to_low)

    @classmethod
    def erhu(cls, high_to_low: bool = False) -> Fretboard:
        """Standard erhu tuning (A4 D4).

        The erhu is a 2-stringed Chinese bowed instrument with a
        hauntingly vocal quality. Tuned a fifth apart. No fingerboard
        — the player presses the strings without touching the neck,
        allowing continuous pitch bending.
        """
        return cls._from_canonical(["A4", "D4"], high_to_low)

    @classmethod
    def charango(cls, high_to_low: bool = False) -> Fretboard:
        """Standard charango tuning (E5 A4 E5 C5 G4).

        A small Andean stringed instrument, traditionally made from
        an armadillo shell. 5 doubled courses with re-entrant tuning
        — the 3rd course (E5) is the highest pitched, creating the
        charango's bright, sparkling sound.
        """
        return cls._from_canonical(["E5", "A4", "E5", "C5", "G4"], high_to_low)

    @classmethod
    def pipa(cls, high_to_low: bool = False) -> Fretboard:
        """Standard pipa tuning (D4 A3 E3 A2).

        The pipa is a 4-stringed Chinese lute with a pear-shaped
        body, dating back over 2000 years. Known for its percussive
        attack and rapid tremolo technique.
        """
        return cls._from_canonical(["D4", "A3", "E3", "A2"], high_to_low)

    @classmethod
    def balalaika(cls, high_to_low: bool = False) -> Fretboard:
        """Standard balalaika prima tuning (A4 E4 E4).

        The Russian balalaika has a distinctive triangular body and
        3 strings. The two lower strings are tuned in unison — a
        unique feature that gives it a natural chorus effect.
        """
        return cls._from_canonical(["A4", "E4", "E4"], high_to_low)

    @classmethod
    def keyboard(cls, keys: int = 88, start: str = "A0",
                 high_to_low: bool = False) -> Fretboard:
        """Piano or keyboard with the given number of keys.

        Args:
            keys: Number of keys (default 88 for a full piano).
                Common sizes: 25, 37, 49, 61, 76, 88.
            start: The lowest note (default ``"A0"`` for standard piano).
            high_to_low: When ``True``, the board reads high to low.

        A full 88-key piano spans A0 (27.5 Hz) to C8 (4186 Hz) —
        the widest range of any standard acoustic instrument.
        Smaller MIDI controllers typically start at C.

        Examples::

            Fretboard.keyboard()            # 88-key piano
            Fretboard.keyboard(61, "C2")    # 61-key controller
            Fretboard.keyboard(25, "C3")    # 25-key mini controller
        """
        from .tones import Tone
        start_tone = Tone.from_string(start, system="western")
        # Built high-to-low (canonical): highest key first, down to `start`.
        tones = [start_tone.add(i) for i in range(keys - 1, -1, -1)]
        return cls(tones=tones, high_to_low=high_to_low, _canonical=True)

    @classmethod
    def lute(cls, high_to_low: bool = False) -> Fretboard:
        """Renaissance lute in G tuning (6 courses).

        The European lute was the dominant instrument of the
        Renaissance (15th-17th century). Tuned in fourths with
        a major third between the 3rd and 4th courses — the
        same intervallic pattern as a modern guitar.
        """
        strings = ["G4", "D4", "A3", "F3", "C3", "G2"]
        return cls._from_canonical(strings, high_to_low)

    @classmethod
    def twelve_string(cls, high_to_low: bool = False) -> Fretboard:
        """12-string guitar in standard tuning.

        The lower 4 courses are doubled at the octave; the upper 2
        are doubled in unison. This creates the characteristic
        shimmering, chorus-like sound.

        Represented as 12 strings (canonical: high to low, pairs together).
        """
        strings = [
            "E4", "E4",      # 1st course (unison)
            "B3", "B3",      # 2nd course (unison)
            "G4", "G3",      # 3rd course (octave)
            "D4", "D3",      # 4th course (octave)
            "A3", "A2",      # 5th course (octave)
            "E3", "E2",      # 6th course (octave)
        ]
        return cls._from_canonical(strings, high_to_low)

    def scale_diagram(self, scale, frets: int = 12, chord=None) -> str:
        """Render an ASCII diagram showing where scale notes fall on the neck.

        Each string is shown with note names on frets where scale notes
        appear. When a *chord* is provided, its tones are shown in
        UPPERCASE and scale-only tones in lowercase, making chord
        tones visually distinct from passing tones.

        Args:
            scale: A Scale object (or anything with a ``note_names`` attribute).
            frets: Number of frets to display (default 12).
            chord: Optional Chord object. Its tones are highlighted in
                uppercase; other scale tones appear in lowercase.

        Returns:
            A multi-line string showing the fretboard diagram.

        Example::

            >>> fb = Fretboard.guitar()
            >>> pentatonic = TonedScale(tonic="A4")["minor"]
            >>> print(fb.scale_diagram(pentatonic, frets=5))

            >>> # Highlight Am chord tones within the scale:
            >>> am = Chord.from_symbol("Am")
            >>> print(fb.scale_diagram(pentatonic, frets=5, chord=am))
        """
        # Match notes enharmonically: the fretboard spells tones with
        # sharps (e.g. D#), but a scale may use flats (e.g. Eb). Compare
        # via the system's canonical name so Eb and D# count as the same
        # pitch — and display using the scale's own spelling.
        _system = self._tones[0].system
        def _resolve(name):
            resolved = _system.resolve_name(name)
            return resolved if resolved is not None else name

        # Map canonical pitch -> the scale's preferred spelling for display.
        scale_display = {}
        for n in scale.note_names:
            scale_display.setdefault(_resolve(n), n)
        scale_notes = set(scale_display)

        chord_notes = set()
        if chord is not None:
            chord_notes = {_resolve(t.name) for t in chord.tones}

        max_name = max(len(t.name) for t in self.tones)
        lines = []

        header_parts = []
        for f in range(frets + 1):
            header_parts.append(f"{f:>2} ")
        header = " " * (max_name + 2) + " ".join(header_parts)
        lines.append(header)

        for tone in self.tones:
            fret_marks = []
            for f in range(frets + 1):
                note = tone.add(f)
                key = _resolve(note.name)
                if key in scale_notes:
                    label = scale_display[key]
                    if chord_notes and key in chord_notes:
                        fret_marks.append(f" {label.upper():<2s}")
                    elif chord_notes:
                        fret_marks.append(f" {label.lower():<2s}")
                    else:
                        fret_marks.append(f" {label:<2s}")
                else:
                    fret_marks.append(" - ")
            line = f"{tone.name:>{max_name}}|{'|'.join(fret_marks)}|"
            lines.append(line)

        return "\n".join(lines)

    def chord(self, name: str, *, system: str = "western") -> "Fingering":
        """Look up a chord by name and return its best fingering.

        Args:
            name: Chord name like ``"G"``, ``"Am7"``, ``"Bb"``, ``"Dm"``.
            system: Tonal system to use (default ``"western"``).

        Returns:
            A :class:`Fingering` for that chord on this fretboard.

        Example::

            >>> fb = Fretboard.guitar()
            >>> fb.chord("G")
            Fingering(E=3, A=2, D=0, G=0, B=0, e=3)
        """
        from .charts import CHARTS
        return CHARTS[system][name].fingering(fretboard=self)

    def __getitem__(self, name: str) -> "Fingering":
        """Shorthand for :meth:`chord` — ``fb["G"]`` equals ``fb.chord("G")``.

        Args:
            name: Chord name like ``"G"``, ``"Am7"``, ``"Bb"``.

        Returns:
            A :class:`Fingering` for that chord on this fretboard.

        Example::

            >>> fb = Fretboard.guitar()
            >>> fb["G"]
            Fingering(E=3, A=2, D=0, G=0, B=0, e=3)
        """
        return self.chord(name)

    def tab(self, name: str, *, system: str = "western") -> str:
        """Look up a chord by name and return its ASCII tablature.

        Args:
            name: Chord name like ``"G"``, ``"Am7"``, ``"Bb"``.
            system: Tonal system to use (default ``"western"``).

        Returns:
            A multi-line string showing the chord as tablature.

        Example::

            >>> fb = Fretboard.guitar()
            >>> print(fb.tab("Am"))
            A minor
            E|--x--
            A|--0--
            D|--2--
            G|--2--
            B|--1--
            e|--0--
        """
        return self.chord(name, system=system).tab()

    def tab_image(self, name: str, path=None, *, system: str = "western",
                  fmt: str = "svg", **kw):
        """Render a chord as an SVG (or PNG) chord-box image.

        The graphical counterpart of :meth:`tab` — a vertical chord
        diagram you can embed in a video, slide, or worksheet. Returns
        the SVG string, or writes ``path`` and returns it when given.

        Args:
            name: chord name like ``"Am"``, ``"G"``, ``"F#m7b5"``.
            path: optional file to write (``.svg`` or ``.png``).
            fmt: ``"svg"`` (default) or ``"png"`` (needs ``cairosvg``).

        Example::

            >>> fb = Fretboard.guitar()
            >>> fb.tab_image("Am", "Am.svg")
            'Am.svg'
            >>> for n in ["C", "Am", "F", "G"]:
            ...     fb.tab_image(n, f"{n}.svg")
        """
        from .diagrams import chord_svg
        try:
            fingering = self.chord(name, system=system)
        except KeyError:
            raise ValueError(
                f"No charted fingering for {name!r}. tab_image covers the "
                "charted chords (major/minor/5/6/7/9/dim/m6/m7/m9/maj7/maj9 "
                "on each root). For an uncharted voicing, build a Fingering "
                "yourself and call .to_svg().")
        return chord_svg(fingering, name, path=path, fmt=fmt, **kw)

    def scale_shapes(self, scale, **kw):
        """Split a scale into positional boxes (e.g. the 5 pentatonic shapes).

        Returns a list of :class:`~pytheory.diagrams.ScaleShape`, each a
        small fret window with the roots marked. Render one with
        ``shape.to_svg(path=...)``.

        Example::

            >>> fb = Fretboard.guitar()
            >>> scale = TonedScale(tonic="A4", system="blues")["minor pentatonic"]
            >>> shapes = fb.scale_shapes(scale)
            >>> len(shapes)
            5
            >>> shapes[0].to_svg(path="A_pent_pos1.svg")
        """
        from .diagrams import scale_shapes
        return scale_shapes(self, scale, **kw)

    def scale_shape_image(self, scale, position: int, path=None, **kw):
        """Render a single scale position to SVG/PNG (``position`` is 1-based)."""
        from .diagrams import scale_shape_svg
        return scale_shape_svg(self, scale, position, path=path, **kw)

    def arpeggio_diagram(self, chord, path=None, **kw):
        """Map a chord's tones across the neck, labelled by role (R/3/5/7…).

        For practising arpeggios — see where the root, 3rd, 5th and 7th
        of a chord fall everywhere on the fretboard, roots highlighted.

        Args:
            chord: a :class:`Chord` or a chord-symbol string (``"Am"``).
            path: optional ``.svg``/``.png`` file to write.

        Example::

            >>> Fretboard.guitar().arpeggio_diagram("Am", "Am_arp.svg")
            'Am_arp.svg'
        """
        from .diagrams import arpeggio_svg
        return arpeggio_svg(self, chord, path=path, **kw)

    def chart(self, *, system: str = "western") -> dict:
        """Generate fingerings for every chord in the given system.

        Returns:
            A dict mapping chord names to :class:`Fingering` objects.

        Example::

            >>> fb = Fretboard.guitar()
            >>> chart = fb.chart()
            >>> chart["Am7"]
            Fingering(E=0, A=0, D=2, G=0, B=1, e=0)
        """
        from .charts import charts_for_fretboard, CHARTS
        return charts_for_fretboard(chart=CHARTS[system], fretboard=self)

    def fingering(self, *positions: int) -> "Fingering":
        """Apply fret positions to each string, returning a Fingering.

        Each position value is added (in semitones) to the corresponding
        open-string tone. The number of positions must match the number
        of strings.

        Args:
            *positions: One integer per string indicating the fret number.

        Returns:
            A :class:`Fingering` labeled with string names. Call
            ``.to_chord(fretboard)`` or use the resulting chord directly.

        Raises:
            ValueError: If the number of positions doesn't match the
                number of strings.
        """
        from .charts import Fingering

        if not len(positions) == len(self._tones):
            raise ValueError(
                "The number of positions must match the number of tones (strings)."
            )

        # Positions arrive in this board's orientation; canonicalise them
        # (high-to-low) to match the internal tone order Fingering expects.
        string_names = tuple(t.name for t in self._tones)
        return Fingering(self._orient(positions), string_names, fretboard=self,
                         high_to_low=self.high_to_low)


def analyze_progression(chords: list[Chord], key: str = "C", mode: str = "major") -> list[str | None]:
    """Analyze a list of chords and return their Roman numeral functions.

    Example::

        >>> chords = [Chord.from_name("C"), Chord.from_name("Am"), Chord.from_name("F"), Chord.from_name("G")]
        >>> analyze_progression(chords, key="C")
        ['I', 'vi', 'IV', 'V']
    """
    return [c.analyze(key, mode) for c in chords]


def _cadence_degree(roman: Optional[str]) -> Optional[str]:
    """Reduce a Roman numeral to its bare scale-degree token.

    Drops accidentals, sevenths, inversions, and quality suffixes, so
    ``"V7"`` -> ``"V"``, ``"viidim"`` -> ``"vii"``, ``"bVI"`` -> ``"VI"``.
    """
    if not roman:
        return None
    stripped = roman.lstrip("b#♭♯")
    i = 0
    while i < len(stripped) and stripped[i] in "iIvV":
        i += 1
    return stripped[:i] or None


def _pc(tone) -> int:
    from ._statics import C_INDEX
    return (tone._index - C_INDEX) % 12


def _in_root_position(chord: Chord) -> bool:
    root = chord.root
    return root is not None and _pc(chord.tones[0]) == _pc(root)


def detect_cadence(penultimate: Chord, final: Chord,
                   key: str = "C", mode: str = "major") -> Optional[str]:
    """Classify the cadential motion from ``penultimate`` to ``final``.

    A cadence is the harmonic "punctuation" that ends a phrase. Given the
    last two chords of a phrase (and the key), this names the gesture:

    - ``"perfect authentic"`` — V → I, both root position, with the tonic
      in the top voice. The strongest, most conclusive ending (PAC).
    - ``"imperfect authentic"`` — also V → I (or vii° → I), but weakened by
      an inversion or a non-tonic soprano (IAC).
    - ``"half"`` — the phrase ends *on* the dominant (… → V). Sounds
      unfinished, like a comma.
    - ``"phrygian half"`` — in minor, iv⁶ → V, the bass falling a semitone
      into the dominant.
    - ``"deceptive"`` — V → vi instead of the expected tonic: the surprise.
    - ``"plagal"`` — IV → I, the "Amen" cadence.
    - ``None`` — the motion isn't a recognised cadence.

    Note that perfect-authentic detection needs real voicing: a close
    root-position triad puts the fifth on top, which is (correctly) an
    *imperfect* authentic cadence. Voice the final chord with the tonic in
    the soprano to get a PAC.

    Example::

        >>> from pytheory import Chord
        >>> detect_cadence(Chord.from_name("G"), Chord.from_name("C"), "C")
        'imperfect authentic'
        >>> detect_cadence(Chord.from_name("G"), Chord.from_name("Am"), "C")
        'deceptive'
        >>> detect_cadence(Chord.from_name("F"), Chord.from_name("C"), "C")
        'plagal'
        >>> detect_cadence(Chord.from_name("Dm"), Chord.from_name("G"), "C")
        'half'
    """
    from .tones import Tone

    a = _cadence_degree(penultimate.analyze(key, mode))
    b = _cadence_degree(final.analyze(key, mode))
    if not a or not b:
        return None
    a_deg, b_deg = a.upper(), b.upper()

    # Half cadence — the phrase ends on the dominant.
    if b_deg == "V":
        if mode == "minor" and a_deg == "IV" and not _in_root_position(penultimate):
            return "phrygian half"      # iv6 -> V
        return "half"

    # Authentic — a dominant-function chord resolving to the tonic.
    if b_deg == "I" and a_deg in ("V", "VII"):
        tonic_pc = _pc(Tone.from_string(f"{key}4", system="western"))
        soprano_on_tonic = _pc(final.tones[-1]) == tonic_pc
        if (a_deg == "V"
                and _in_root_position(penultimate)
                and _in_root_position(final)
                and soprano_on_tonic):
            return "perfect authentic"
        return "imperfect authentic"

    # Deceptive — the dominant lands on the submediant instead.
    if a_deg == "V" and b_deg == "VI":
        return "deceptive"

    # Plagal — the "Amen" cadence.
    if a_deg == "IV" and b_deg == "I":
        return "plagal"

    return None


def find_cadences(chords: list[Chord], key: str = "C",
                  mode: str = "major") -> list[tuple]:
    """Scan a progression for cadences.

    Returns a list of ``(index, cadence_type)`` for every adjacent chord
    pair that forms a cadence, where ``index`` is the position of the
    *final* chord of the pair. Without phrase markings this reports every
    cadential motion, so the most musically meaningful one is usually the
    last.

    Example::

        >>> from pytheory import Chord
        >>> prog = [Chord.from_name(n) for n in ("C", "F", "G", "C")]
        >>> find_cadences(prog, "C")
        [(1, 'plagal'), (3, 'imperfect authentic')]
    """
    found = []
    for i in range(1, len(chords)):
        cadence = detect_cadence(chords[i - 1], chords[i], key, mode)
        if cadence:
            found.append((i, cadence))
    return found


def _abs_pitch(tone) -> int:
    """Absolute semitone height of a Tone (MIDI-like; only used for
    comparisons, so the exact origin doesn't matter)."""
    from ._statics import C_INDEX
    return (tone._index - C_INDEX) % 12 + 12 * tone.octave


# Voice labels for a four-part (SATB) texture, low to high.
_SATB = ("bass", "tenor", "alto", "soprano")


def _voice_name(index: int, n_voices: int) -> str:
    if n_voices == 4:
        return _SATB[index]
    return f"voice {index + 1}"


def check_voice_leading(voicings: list) -> list:
    """Check a sequence of chord voicings for common part-writing errors.

    Each voicing is read as a stack of **voices in order** — lowest
    (``tones[0]``) to highest — so a :class:`Chord` built with its tones in
    voice order works directly (as do plain lists of :class:`~pytheory.Tone`
    or MIDI numbers). The classic common-practice prohibitions are checked:

    - **parallel fifths** — two voices a perfect fifth apart moving, in the
      same direction, to another perfect fifth;
    - **parallel octaves** — the same, an octave (or unison) apart;
    - **voice crossing** — a lower voice ending up above a higher one.

    Args:
        voicings: A list of voicings (Chords, or lists of Tones / MIDI
            numbers). Voicings may have any number of parts; pairs are
            compared over the parts they share.

    Returns:
        A list of issue dicts, each with ``type``, ``chords`` (the indices
        involved), ``voices`` (the voice indices involved), and a
        human-readable ``description``. An empty list means clean
        part-writing.

    Example::

        >>> from pytheory import Chord
        >>> # Parallel fifths: C+G rising to D+A
        >>> a = Chord.from_midi_message(48, 55)   # C3, G3
        >>> b = Chord.from_midi_message(50, 57)   # D3, A3
        >>> [i["type"] for i in check_voice_leading([a, b])]
        ['parallel fifths']
    """
    from .tones import Tone

    seqs = []
    for v in voicings:
        if isinstance(v, Chord):
            seqs.append([_abs_pitch(t) for t in v.tones])
        else:
            seqs.append([_abs_pitch(t) if isinstance(t, Tone) else int(t)
                         for t in v])

    issues = []
    for i in range(len(seqs) - 1):
        a, b = seqs[i], seqs[i + 1]
        n = min(len(a), len(b))

        # Parallel perfect fifths / octaves between any pair of voices.
        for x in range(n):
            for y in range(x + 1, n):
                if a[x] == b[x] or a[y] == b[y]:
                    continue                       # a voice held = oblique
                if (b[x] - a[x]) * (b[y] - a[y]) <= 0:
                    continue                       # not similar motion
                iv1, iv2 = (a[y] - a[x]) % 12, (b[y] - b[x]) % 12
                if iv1 == 7 and iv2 == 7:
                    kind = "parallel fifths"
                elif iv1 == 0 and iv2 == 0:
                    kind = "parallel octaves"
                else:
                    continue
                vx, vy = _voice_name(x, n), _voice_name(y, n)
                issues.append({
                    "type": kind,
                    "chords": (i, i + 1),
                    "voices": (x, y),
                    "description": f"{kind} between {vx} and {vy} "
                                   f"(chords {i}→{i + 1})",
                })

        # Voice crossing — a lower-numbered voice ending above a higher one.
        for x in range(n - 1):
            if b[x] > b[x + 1]:
                vx, vy = _voice_name(x, n), _voice_name(x + 1, n)
                issues.append({
                    "type": "voice crossing",
                    "chords": (i + 1,),
                    "voices": (x, x + 1),
                    "description": f"voice crossing: {vx} is above {vy} "
                                   f"in chord {i + 1}",
                })

    return issues
