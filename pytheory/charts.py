import itertools

from .systems import SYSTEMS
from .tones import Tone

CHORD_SYNONYMS = {
    'maj' : ['', 'M'],
    'm'   : ['min'],
    'aug' : ['+'],
    'dim' : ['0'],
    'maj6': ['6', 'M6'],
    'min6': ['m6'],
    'maj7': ['M7'],
    'min7': ['m7']
    'aug7': ['+7'],
    'dim7': ['07'],
    'mM7' : ['min/maj7', 'min(maj7)'],
}

CHORD_DEFINITIONS = {
    'maj' : (0, 4, 7),
    'm'   : (0, 3, 7),
    'aug' : (0, 4, 8),
    'dim' : (0, 3, 6),
    'maj6': (0, 4, 7, 9),
    'min6': (0, 3, 7, 9),
    '7'   : (0, 4, 7, 10),
    'maj7': (0, 4, 7, 11),
    'min7': (0, 3, 7, 10),
    'aug7': (0, 4, 8, 10),
    'dim7': (0, 3, 6, 9),
    'm7b5': (0, 3, 6, 10),
    'mM7' : (0, 3, 7, 11),
    'maj9': (0, 4, 7, 11, 14),
    '9'   : (0, 4, 7, 10, 14),
    'mM9' : (0, 3, 7, 11, 14),
    'min9': (0, 3, 7, 10, 14),
    '+M9' : (0, 4, 8, 11, 14),
    'aug9': (0, 4, 8, 10, 14),    
    '5'   : (0, 7),
}
for quality, synonym_list in CHORD_SYNONYMS.items():
    for synonym in synonym_list:
        CHORD_DEFINITIONS[synonym] = CHORD_DEFINITIONS[quality]

QUALITIES = CHORD_DEFINITIONS.keys()

MAX_FRET = 7

CHARTS = {}
CHARTS['western'] = []

class NamedChord:
    def __init__(self, *, tone_name, quality):
        self.tone_name = tone_name
        self.quality = quality

    @property
    def name(self):
        return f"{self.tone_name}{self.quality}"

    @property
    def tone(self):
        return Tone(name=self.tone_name)

    def __repr__(self):
        return f"<NamedChord name={self.name!r}>"

    @property
    def acceptable_tones(self):
        return tuple([self.tone.add(i) for i in CHORD_DEFINITIONS[self.quality]])

    @property
    def acceptable_tone_names(self):
        return tuple((tone.name for tone in self.acceptable_tones))

    def _possible_fingerings(self, *, fretboard):
        def find_fingerings(tone):
            fingerings = []
            for j in range(MAX_FRET):
                fingered_tone = tone.add(j)
                for acceptable_tone in self.acceptable_tones:
                    if fingered_tone.name == acceptable_tone:
                        fingerings.append(j)

            return tuple(fingerings)

        fingering = []
        for i, tone in enumerate(fretboard.tones):
            fingering.append(find_fingerings(tone))

        for i, finger in enumerate(fingering):
            if finger == ():
                fingering[i] = (-1,)

        return tuple(fingering)

    @staticmethod
    def fix_fingering(fingering):
        fingering = list(fingering)
        for i, finger in enumerate(fingering):
            if finger == -1:
                fingering[i] = None
        return tuple(fingering)

    def fingerings(self, *, fretboard):
        return tuple(itertools.product(*self._possible_fingerings(fretboard=fretboard)))

    def fingering(self, *, fretboard, multiple=False):
        def fingering_score(fingering):
            def number_of_fingers(fingering):
                zeros = 0
                for finger in fingering:
                    if finger == 0:
                        zeros += 1
                return len(fingering) - zeros

            def ascending(fingering):
                fingering = [f for f in fingering if f != 0]

                return sorted(fingering) == fingering

            ascending = int(ascending(fingering))
            finger_count = number_of_fingers(fingering)
            return ascending + (1 / finger_count)

        def gen():
            fingerings = self.fingerings(fretboard=fretboard)
            score_map = tuple(map(fingering_score, fingerings))
            max_score = max(score_map)

            for possible_fingering in fingerings:
                if fingering_score(possible_fingering) == max_score:
                    yield possible_fingering

        best_fingerings = tuple(g for g in gen())
        if not multiple:
            return self.fix_fingering(best_fingerings[0])
        else:
            return tuple((self.fix_fingering(f) for f in best_fingerings))



western_chart = {}
for tone_titles in SYSTEMS['western'].tone_names:
    # Take the second tone name, if it's available.
    if len(tone_titles) == 2:
        tone_name = tone_titles[1]
    else:
        tone_name = tone_titles[0]

    for quality in QUALITIES:
        named_chord = NamedChord(tone_name=tone_name, quality=quality)
        western_chart.update({f"{tone_name}{quality}": named_chord})

CHARTS['western'] = western_chart

def charts_for_fretboard(*, chart=CHARTS['western'], fretboard):
    super_chart = {}
    for chord in chart:
        super_chart[chord] = chart[chord].fingering(fretboard=fretboard)
    return super_chart
