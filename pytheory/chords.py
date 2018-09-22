class Chord:
    def __init__(self, *, tones):
        self.tones = tones

    def __repr__(self):
        l = tuple((tone.full_name for tone in self.tones))
        return f"<Chord tones={l!r}>"

    # @property
    # def harmony(self):
    #     pass

class NamedChord:
    def __init__(self, *, name, system):
        self.name
        self.system

class Fretboard:
    def __init__(self, *, tones):
        self.tones = tones

    def __repr__(self):
        l = tuple((tone.full_name for tone in self.tones))
        return f"<Fretboard tones={l!r}>"

    def fingering(self, *positions):
        if not len(positions) == len(self.tones):
            raise ValueError("The number of positions must match the number of tones (strings).")

        tones = []
        for (i, tone) in enumerate(self.tones):
            tones.append(tone.add(positions[i]))

        return Chord(tones=tones)
