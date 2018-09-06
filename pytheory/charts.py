import itertools

from .systems import SYSTEMS
from .tones import Tone

MODS = ('', 'm', '5', '7', '9', 'dim', 'm6', 'm7', 'maj7', 'sus')

CHARTS = {}
CHARTS['western'] = []

class NamedChord:
    def __init__(self, *, tone_name, mod):
        self.tone_name = tone_name
        self.mod = mod

    @property
    def name(self):
        return f"{self.tone_name}{self.mod}"

    @property
    def tone(self):
        return Tone(name=self.tone_name)

    def __repr__(self):
        return f"<NamedChord name={self.name!r}>"

    @property
    def acceptable_tones(self):
        acceptable = [self.tone]

        acceptable += [self.tone.add(5)]
        # acceptable += [self.tone.add(3)]
        acceptable += [self.tone.subtract(5)]
        # acceptable += [self.tone.subtract(3)]

        return tuple(acceptable)

    @property
    def acceptable_tone_names(self):
        return tuple([tone.name for tone in self.acceptable_tones])

    def possible_fingerings(self, *, fretboard):
        def find_fingerings(tone):
            fingerings = []
            for j in range(7):
                fingered_tone = tone.add(j)
                for acceptable_tone in self.acceptable_tones:
                    if fingered_tone.name == acceptable_tone:
                        fingerings.append(j)

            return tuple(fingerings)

        fingering = []
        for i, tone in enumerate(fretboard.tones):
            fingering.append(find_fingerings(tone))
        return tuple(fingering)

    def fingerings(self, *, fretboard):
        return tuple(itertools.product(*self.possible_fingerings(fretboard=fretboard)))

    def fingering(self, *, freboard):
        possible_fingerings = self.possible_fingerings(freboard=fretboard)
        return posible_fingerings



western_chart = {}
for tone_titles in SYSTEMS['western'].tone_names:
    # Take the second tone name, if it's available.
    if len(tone_titles) == 2:
        tone_name = tone_titles[1]
    else:
        tone_name = tone_titles[0]

    for mod in MODS:
        named_chord = NamedChord(tone_name=tone_name, mod=mod)
        western_chart.update({f"{tone_name}{mod}": named_chord})

CHARTS['western'] = western_chart
