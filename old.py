class Tone:
    MAX = 12
    TONE_DICT = {
        0: ("C",),
        1: ("C#", "Db"),
        2: ("D",),
        3: ("D#", "Eb"),
        4: ("E",),
        5: ("F",),
        6: ("F#", "Gb"),
        7: ("G",),
        8: ("G#", "Ab"),
        9: ("A",),
        10: ("A#", "Bb"),
        11: ("B",),
    }

    def __init__(self, index):
        if not isinstance(index, int):
            raise ValueError("Tone indexes must be integers.")

        # Correct misappropriated indexes.
        self.index = index % self.MAX

    def add(self, interval):
        return Tone((self.index + interval) % self.MAX)

    def subtract(self, interval):
        return Tone((self.index - interval) % self.MAX)

    @classmethod
    def get_all(klass):
        tones = []
        for (k, v) in klass.TONE_DICT.items():
            tones.append(klass(k))

        return tones

    @property
    def name(self):
        # Prefer sharps to flats, for now.
        return self.TONE_DICT[self.index][0]

    @classmethod
    def from_string(klass, s):
        for (k, v) in klass.TONE_DICT.items():
            if s in v:
                return klass(k)

        raise ValueError(f"Tone {s!r} not found.")

    def __repr__(self):
        return f"<Tone {self.name}>"


class IntervalSet:
    def __init__(self, *, intervals):
        try:
            assert sum(intervals) == 12
        except AssertionError:
            raise ValueError("IntervalSets must contain a total of 12 total steps.")
        self.intervals = (0,) + intervals

    def __iter__(self):
        return self.intervals.__iter__()

    def __repr__(self):
        return f"<IntervalSet {self.intervals!r}>"


class Scale:
    INTERVALS = {
        # Major.
        "ionian": IntervalSet(intervals=(2, 2, 1, 2, 2, 2, 1)),
        # Minor.
        "aeolian": IntervalSet(intervals=(2, 1, 2, 2, 1, 2, 2)),
        "chromatic": IntervalSet(intervals=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)),
    }

    def __init__(self, tonic):
        self.tonic = Tone.from_string(tonic)

    def __repr__(self):
        return f"<Scale tonic={self.tonic!r}>"

    def produce_scale(self, *, interval_set, octave):
        def gen(octave):
            offset = 0
            for interval in interval_set:
                offset = offset + interval
                yield self.tonic.add(offset)

        return [g for g in gen(octave=octave)]

    def get_mode(self, mode, *, octave=4):
        return self.produce_scale(interval_set=self.INTERVALS[mode], octave=octave)

    def major(self, octave=4):
        return self.get_mode("ionian")

    def minor(self, octave=4):
        return self.get_mode("aeolian")

    def chromatic(self, octave=4):
        return self.get_mode("chromatic")


minor = {tonic: Scale(tonic=tonic.name).minor() for tonic in Tone.get_all()}
major = {tonic: Scale(tonic=tonic.name).major() for tonic in Tone.get_all()}
# print(major)
