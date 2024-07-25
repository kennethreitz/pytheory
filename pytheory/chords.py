class Chord:
    def __init__(self, *, tones):
        self.tones = tones

    def __repr__(self):
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Chord tones={l!r}>"

    @property
    def harmony(self):
        if len(self.tones) < 2:
            return 0  # No harmony for a single tone or empty chord

        # Simple harmony calculation: sum of inverse intervals
        # Smaller intervals contribute more to harmony
        harmony_value = sum(1 / interval for interval in self.intervals if interval != 0)

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
        intervals = [abs(self.tones[i].pitch() - self.tones[i-1].pitch()) for i in range(1, len(self.tones))]

        return intervals





class NamedChord:
    def __init__(self, *, name, system):
        self.name
        self.system

class Fretboard:
    def __init__(self, *, tones):
        self.tones = tones

    def __repr__(self):
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Fretboard tones={l!r}>"

    def fingering(self, *positions):
        if not len(positions) == len(self.tones):
            raise ValueError("The number of positions must match the number of tones (strings).")

        tones = []
        for (i, tone) in enumerate(self.tones):
            tones.append(tone.add(positions[i]))

        return Chord(tones=tones)
