class Chord:
    def __init__(self, tones):
        self.tones = tones

    def __repr__(self):
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Chord tones={l!r}>"

    def __iter__(self):
        return iter(self.tones)

    def __len__(self):
        return len(self.tones)

    def __contains__(self, item):
        if isinstance(item, str):
            return any(item == t.name for t in self.tones)
        return item in self.tones

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

    def __iter__(self):
        return iter(self.tones)

    def __len__(self):
        return len(self.tones)

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
    def guitar(cls, tuning="standard"):
        """Guitar with the given tuning.

        Args:
            tuning: Tuning name or tuple of tone strings (high to low).
                Built-in tunings: standard, drop d, open g, open d,
                open e, open a, dadgad, half step down.
        """
        from .tones import Tone
        if isinstance(tuning, str):
            tuning = cls.TUNINGS[tuning]
        return cls(tones=[Tone.from_string(t, system="western") for t in tuning])

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
        """Standard ukulele tuning (A4 E4 C4 G4)."""
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("A4", system="western"),
            Tone.from_string("E4", system="western"),
            Tone.from_string("C4", system="western"),
            Tone.from_string("G4", system="western"),
        ])

    def fingering(self, *positions):
        if not len(positions) == len(self.tones):
            raise ValueError(
                "The number of positions must match the number of tones (strings)."
            )

        tones = []
        for i, tone in enumerate(self.tones):
            tones.append(tone.add(positions[i]))

        return Chord(tones=tones)
