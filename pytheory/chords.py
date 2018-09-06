class Chord:
    def __init__(self, *, tones):
        self.tones = tones

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
        l = tuple([tone.full_name for tone in self.tones])
        return f"<Fretboard tones={l!r}>"
