class Chord:
    def __init__(self, tones):
        self.tones = tones

    @classmethod
    def from_tones(cls, *note_names, octave=4):
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
    def from_name(cls, name, octave=4):
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

    def __repr__(self):
        name = self.identify()
        if name:
            return f"<Chord {name}>"
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Chord tones={l!r}>"

    def __str__(self):
        name = self.identify()
        if name:
            return name
        return " ".join(t.full_name for t in self.tones)

    def __iter__(self):
        return iter(self.tones)

    def __len__(self):
        return len(self.tones)

    def __contains__(self, item):
        if isinstance(item, str):
            return any(item == t.name for t in self.tones)
        return item in self.tones

    def __add__(self, other):
        """Merge two chords into one (layer their tones).

        Example::

            >>> c_major = Chord.from_tones("C", "E", "G")
            >>> g_bass = Chord.from_tones("G", octave=2)
            >>> slash = c_major + g_bass  # C/G
        """
        if isinstance(other, Chord):
            return Chord(tones=list(self.tones) + list(other.tones))
        return NotImplemented

    def tritone_sub(self):
        """Return the tritone substitution of this chord.

        In jazz harmony, any dominant chord can be replaced by the
        dominant chord a tritone (6 semitones) away. G7 → Db7,
        C7 → F#7. This works because the two chords share the same
        tritone interval (the 3rd and 7th swap roles).

        Returns a new Chord transposed by 6 semitones.
        """
        return self.transpose(6)

    def inversion(self, n=1):
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
        return Chord(tones=tones)

    def transpose(self, semitones):
        """Return a new Chord transposed by the given number of semitones.

        Every tone in the chord is shifted up (positive) or down
        (negative) by the same interval, preserving the chord's
        quality and voicing.

        Example::

            >>> c_major = Chord([C4, E4, G4])
            >>> c_major.transpose(7).identify()
            'G major'
        """
        return Chord(tones=[t.add(semitones) for t in self.tones])

    @property
    def root(self):
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
    def quality(self):
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
    def intervals(self):
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
    def harmony(self):
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
    def dissonance(self):
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
    def beat_frequencies(self):
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
    def beat_pulse(self):
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

    def identify(self):
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
                    return f"{root.name} {name}"
        return None

    def voice_leading(self, other):
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

    def analyze(self, key_tonic, mode="major"):
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
        import numeral as numeral_mod
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
        if root_name not in scale_names:
            return None
        degree_idx = scale_names.index(root_name)

        numeral_str = numeral_mod.int2roman(degree_idx + 1, only_ascii=True)

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

        return numeral_str + suffix

    @property
    def tension(self):
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

    def fingering(self, *positions):
        if not len(positions) == len(self.tones):
            raise ValueError(
                "The number of positions must match the number of tones (strings)."
            )

        tones = []
        for i, tone in enumerate(self.tones):
            tones.append(tone.add(positions[i]))

        return Chord(tones=tones)


class Fretboard:
    def __init__(self, *, tones):
        self.tones = tones

    def __repr__(self):
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Fretboard tones={l!r}>"

    def capo(self, fret):
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
        return Fretboard(tones=[t.add(fret) for t in self.tones])

    def __iter__(self):
        return iter(self.tones)

    def __len__(self):
        return len(self.tones)

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
    def guitar(cls, tuning="standard", capo=0):
        """Guitar with the given tuning and optional capo.

        Args:
            tuning: Tuning name or tuple of tone strings (high to low).
                Built-in tunings: standard, drop d, open g, open d,
                open e, open a, dadgad, half step down.
            capo: Fret number for the capo (0 = no capo). Raises all
                strings by this many semitones.
        """
        from .tones import Tone
        if isinstance(tuning, str):
            tuning = cls.TUNINGS[tuning]
        fb = cls(tones=[Tone.from_string(t, system="western") for t in tuning])
        if capo:
            fb = fb.capo(capo)
        return fb

    @classmethod
    def bass(cls, five_string=False):
        """Standard bass guitar tuning.

        Args:
            five_string: If True, adds a low B string (B0).
        """
        from .tones import Tone
        strings = ["G2", "D2", "A1", "E1"]
        if five_string:
            strings.append("B0")
        return cls(tones=[Tone.from_string(t, system="western") for t in strings])

    @classmethod
    def ukulele(cls):
        """Standard ukulele tuning (A4 E4 C4 G4).

        Re-entrant tuning: the G4 string is higher than C4.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A4", system="western"),
            Tone.from_string("E4", system="western"),
            Tone.from_string("C4", system="western"),
            Tone.from_string("G4", system="western"),
        ])

    @classmethod
    def mandolin(cls):
        """Standard mandolin tuning (E5 A4 D4 G3).

        Tuned in fifths, same as a violin but one octave relationship.
        Strings are typically doubled (paired courses).
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("E5", system="western"),
            Tone.from_string("A4", system="western"),
            Tone.from_string("D4", system="western"),
            Tone.from_string("G3", system="western"),
        ])

    @classmethod
    def mandola(cls):
        """Standard mandola tuning (A4 D4 G3 C3).

        The mandola (or tenor mandola) is to the mandolin what the
        viola is to the violin — a fifth lower, with a warmer,
        darker tone. Tuned in fifths like all the mandolin family.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A4", system="western"),
            Tone.from_string("D4", system="western"),
            Tone.from_string("G3", system="western"),
            Tone.from_string("C3", system="western"),
        ])

    @classmethod
    def octave_mandolin(cls):
        """Octave mandolin tuning (E4 A3 D3 G2).

        Also called the octave mandola in European terminology.
        One octave below the mandolin — same tuning as the violin
        family's cello-to-violin relationship. Popular in Irish
        and Celtic folk music.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("E4", system="western"),
            Tone.from_string("A3", system="western"),
            Tone.from_string("D3", system="western"),
            Tone.from_string("G2", system="western"),
        ])

    @classmethod
    def mandocello(cls):
        """Mandocello tuning (A3 D3 G2 C2).

        The bass of the mandolin family. Tuned like a cello — an
        octave below the mandola. Rare but beautiful; used in
        mandolin orchestras.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A3", system="western"),
            Tone.from_string("D3", system="western"),
            Tone.from_string("G2", system="western"),
            Tone.from_string("C2", system="western"),
        ])

    @classmethod
    def violin(cls):
        """Standard violin tuning (E5 A4 D4 G3).

        Tuned in perfect fifths. The violin has no frets — intonation
        is continuous, allowing vibrato and microtonal inflections
        not possible on fretted instruments.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("E5", system="western"),
            Tone.from_string("A4", system="western"),
            Tone.from_string("D4", system="western"),
            Tone.from_string("G3", system="western"),
        ])

    @classmethod
    def viola(cls):
        """Standard viola tuning (A4 D4 G3 C3).

        A perfect fifth below the violin. The viola's darker, warmer
        tone comes from its larger body and lower register.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A4", system="western"),
            Tone.from_string("D4", system="western"),
            Tone.from_string("G3", system="western"),
            Tone.from_string("C3", system="western"),
        ])

    @classmethod
    def cello(cls):
        """Standard cello tuning (A3 D3 G2 C2).

        An octave below the viola. Tuned in fifths. The cello spans
        the range of the human voice — tenor through bass.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A3", system="western"),
            Tone.from_string("D3", system="western"),
            Tone.from_string("G2", system="western"),
            Tone.from_string("C2", system="western"),
        ])

    @classmethod
    def banjo(cls, tuning="open g"):
        """Banjo with the given tuning.

        Args:
            tuning: ``"open g"`` (default, bluegrass) or ``"open d"``
                (old-time, clawhammer). The 5th string is a high
                drone — a defining feature of the banjo sound.

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
            tuning = tunings[tuning]
        return cls(tones=[Tone.from_string(t, system="western") for t in tuning])

    @classmethod
    def double_bass(cls):
        """Standard double bass (upright bass) tuning (G2 D2 A1 E1).

        The largest and lowest-pitched bowed string instrument in the
        orchestra. Unlike the rest of the string family, the double
        bass is tuned in fourths (like a bass guitar) rather than
        fifths.

        The 5-string double bass adds a low B0 or C1.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("G2", system="western"),
            Tone.from_string("D2", system="western"),
            Tone.from_string("A1", system="western"),
            Tone.from_string("E1", system="western"),
        ])

    @classmethod
    def harp(cls):
        """Concert harp strings — 47 strings spanning C1 to G7.

        The pedal harp has 7 strings per octave (one per note name),
        tuned to Cb major. Pedals alter each note name by up to two
        semitones across all octaves simultaneously.

        This returns the full set of 47 strings in the default
        Cb (enharmonic B) tuning.
        """
        from .tones import Tone
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
        # Harp strings are high to low
        strings.reverse()
        return cls(tones=[Tone.from_string(s, system="western") for s in strings])

    @classmethod
    def pedal_steel(cls):
        """Pedal steel guitar — E9 Nashville tuning (10 strings).

        The standard tuning for country music. The pedal steel has
        foot pedals and knee levers that change string pitches during
        play, enabling its signature swooping, crying sound.
        """
        from .tones import Tone
        # E9 Nashville tuning (high to low)
        strings = ["F#4", "D#4", "G#3", "E3", "B3", "G#3",
                    "F#3", "E3", "D3", "B2"]
        return cls(tones=[Tone.from_string(s, system="western") for s in strings])

    @classmethod
    def bouzouki(cls, variant="irish"):
        """Bouzouki tuning.

        Args:
            variant: ``"irish"`` (default, GDAD) or ``"greek"`` (CFAD).

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
            variant = tunings[variant]
        return cls(tones=[Tone.from_string(t, system="western") for t in variant])

    @classmethod
    def oud(cls):
        """Standard Arabic oud tuning (C4 G3 D3 A2 G2 C2).

        The oud is the ancestor of the European lute and the defining
        instrument of Arabic, Turkish, and Persian classical music.
        It is fretless, allowing the quarter-tone inflections
        essential to maqam performance. 6 courses (11 strings),
        typically tuned in fourths.
        """
        from .tones import Tone
        strings = ["C4", "G3", "D3", "A2", "G2", "C2"]
        return cls(tones=[Tone.from_string(t, system="western") for t in strings])

    @classmethod
    def sitar(cls):
        """Sitar main playing strings (approximation).

        The sitar typically has 6-7 main strings and 11-13 sympathetic
        strings (taraf). This models the main playing strings in a
        common tuning. The actual tuning varies by raga and tradition.

        Main strings: Sa Sa Pa Sa Re Sa Ma (approximated in 12-TET).
        Represented here as the most common Ravi Shankar school tuning.
        """
        from .tones import Tone
        # Common Ravi Shankar tuning mapped to Western notes
        # (sitar is tuned relative to Sa, typically C# or D)
        strings = ["C4", "C3", "G3", "C3", "D3", "C2", "F2"]
        return cls(tones=[Tone.from_string(t, system="western") for t in strings])

    @classmethod
    def shamisen(cls):
        """Standard shamisen tuning — honchoshi (C4 G3 C3).

        The shamisen is a 3-stringed Japanese instrument played with
        a large plectrum (bachi). Three standard tunings:

        - honchoshi (本調子): root-5th-root
        - niagari (二上り): root-5th-2nd (raises 2nd string)
        - sansagari (三下り): root-5th-b7th (lowers 3rd string)
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("C4", system="western"),
            Tone.from_string("G3", system="western"),
            Tone.from_string("C3", system="western"),
        ])

    @classmethod
    def erhu(cls):
        """Standard erhu tuning (A4 D4).

        The erhu is a 2-stringed Chinese bowed instrument with a
        hauntingly vocal quality. Tuned a fifth apart. No fingerboard
        — the player presses the strings without touching the neck,
        allowing continuous pitch bending.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A4", system="western"),
            Tone.from_string("D4", system="western"),
        ])

    @classmethod
    def charango(cls):
        """Standard charango tuning (E5 A4 E5 C5 G4).

        A small Andean stringed instrument, traditionally made from
        an armadillo shell. 5 doubled courses with re-entrant tuning
        — the 3rd course (E5) is the highest pitched, creating the
        charango's bright, sparkling sound.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("E5", system="western"),
            Tone.from_string("A4", system="western"),
            Tone.from_string("E5", system="western"),
            Tone.from_string("C5", system="western"),
            Tone.from_string("G4", system="western"),
        ])

    @classmethod
    def pipa(cls):
        """Standard pipa tuning (D4 A3 E3 A2).

        The pipa is a 4-stringed Chinese lute with a pear-shaped
        body, dating back over 2000 years. Known for its percussive
        attack and rapid tremolo technique.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("D4", system="western"),
            Tone.from_string("A3", system="western"),
            Tone.from_string("E3", system="western"),
            Tone.from_string("A2", system="western"),
        ])

    @classmethod
    def balalaika(cls):
        """Standard balalaika prima tuning (A4 E4 E4).

        The Russian balalaika has a distinctive triangular body and
        3 strings. The two lower strings are tuned in unison — a
        unique feature that gives it a natural chorus effect.
        """
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A4", system="western"),
            Tone.from_string("E4", system="western"),
            Tone.from_string("E4", system="western"),
        ])

    @classmethod
    def keyboard(cls, keys=88, start="A0"):
        """Piano or keyboard with the given number of keys.

        Args:
            keys: Number of keys (default 88 for a full piano).
                Common sizes: 25, 37, 49, 61, 76, 88.
            start: The lowest note (default ``"A0"`` for standard piano).

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
        tones = []
        for i in range(keys - 1, -1, -1):
            tones.append(start_tone.add(i))
        return cls(tones=tones)

    @classmethod
    def lute(cls):
        """Renaissance lute in G tuning (6 courses).

        The European lute was the dominant instrument of the
        Renaissance (15th-17th century). Tuned in fourths with
        a major third between the 3rd and 4th courses — the
        same intervallic pattern as a modern guitar.
        """
        from .tones import Tone
        strings = ["G4", "D4", "A3", "F3", "C3", "G2"]
        return cls(tones=[Tone.from_string(t, system="western") for t in strings])

    @classmethod
    def twelve_string(cls):
        """12-string guitar in standard tuning.

        The lower 4 courses are doubled at the octave; the upper 2
        are doubled in unison. This creates the characteristic
        shimmering, chorus-like sound.

        Represented as 12 strings (high to low, pairs together).
        """
        from .tones import Tone
        strings = [
            "E4", "E4",      # 1st course (unison)
            "B3", "B3",      # 2nd course (unison)
            "G4", "G3",      # 3rd course (octave)
            "D4", "D3",      # 4th course (octave)
            "A3", "A2",      # 5th course (octave)
            "E3", "E2",      # 6th course (octave)
        ]
        return cls(tones=[Tone.from_string(t, system="western") for t in strings])

    def fingering(self, *positions):
        if not len(positions) == len(self.tones):
            raise ValueError(
                "The number of positions must match the number of tones (strings)."
            )

        tones = []
        for i, tone in enumerate(self.tones):
            tones.append(tone.add(positions[i]))

        return Chord(tones=tones)
