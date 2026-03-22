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
    def harmony(self):
        if len(self.tones) < 2:
            return 0  # No harmony for a single tone or empty chord

        # Simple harmony calculation: sum of inverse intervals
        # Smaller intervals contribute more to harmony
        harmony_value = sum(
            1 / interval for interval in self.intervals if interval != 0
        )

        return harmony_value

    @property
    def dissonance(self):
        if len(self.tones) < 2:
            return 0  # No dissonance for a single tone or empty chord

        # Simple dissonance calculation: sum of intervals
        # Larger intervals contribute more to dissonance
        dissonance_value = sum(interval for interval in self.intervals if interval != 0)

        return dissonance_value

    @property
    def intervals(self):
        if len(self.tones) < 2:
            return []  # No intervals for a single tone or empty chord

        # Calculate intervals between adjacent tones
        intervals = [
            abs(self.tones[i].pitch() - self.tones[i - 1].pitch())
            for i in range(1, len(self.tones))
        ]

        return intervals

    @property
    def beat_pulse(self):
        """Calculate the beat pulse (frequency of amplitude modulation) between tones.

        Returns:
            float: The beat frequency in Hz between the closest pair of tones.
                  Returns 0 if there are fewer than 2 tones.
        """
        if len(self.tones) < 2:
            return 0

        # Calculate beat frequencies between all pairs of tones
        beat_frequencies = []
        for i in range(len(self.tones)):
            for j in range(i + 1, len(self.tones)):
                freq1 = self.tones[i].pitch()
                freq2 = self.tones[j].pitch()
                beat_freq = abs(freq1 - freq2)
                beat_frequencies.append(beat_freq)

        # Return the smallest non-zero beat frequency
        return min(beat_frequencies) if beat_frequencies else 0

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

    @classmethod
    def guitar(cls):
        """Standard guitar tuning (E4 B3 G3 D3 A2 E2)."""
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("E4", system="western"),
            Tone.from_string("B3", system="western"),
            Tone.from_string("G3", system="western"),
            Tone.from_string("D3", system="western"),
            Tone.from_string("A2", system="western"),
            Tone.from_string("E2", system="western"),
        ])

    @classmethod
    def bass(cls):
        """Standard bass guitar tuning (G2 D2 A1 E1)."""
        from .tones import Tone
        return cls(tones=[
            Tone.from_string("G2", system="western"),
            Tone.from_string("D2", system="western"),
            Tone.from_string("A1", system="western"),
            Tone.from_string("E1", system="western"),
        ])

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
