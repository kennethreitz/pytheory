import numeral

from .systems import SYSTEMS
from .tones import Tone


class Scale:
    def __init__(self, *, tones, degrees=None, system=None):
        self.tones = tones
        self.degrees = degrees
        self.system = system

        if self.degrees:
            if not len(self.tones) == len(self.degrees):
                raise ValueError("The number of tones and degrees must be equal!")

    def __repr__(self):
        r = []
        for (i, tone) in enumerate(self.tones):
            degree = numeral.int2roman(i + 1, only_ascii=True)
            r += [f"{degree}={tone.full_name}"]

        r = " ".join(r)
        return f"<Scale {r}>"

    def __getitem__(self, item):
        # Degree–style reference (e.g. "IV").
        if isinstance(item, str):
            degrees = []
            for (i, tone) in enumerate(self.tones):
                degrees.append(numeral.int2roman(i + 1, only_ascii=True))

            if item in degrees:
                item = degrees.index(item)

        # List/Tuple–style reference.
        if isinstance(item, int) or isinstance(item, slice):
            return self.tones[item]


class TonedScale:
    def __init__(self, *, system=SYSTEMS["western"], tonic):
        self.system = system

        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(tonic, system=self.system)

        self.tonic = tonic

    def __repr__(self):
        return f"<TonedScale system={self.system!r} tonic={self.tonic}>"

    def __getitem__(self, scale):
        return self._scales[scale]

    @property
    def scales(self):
        return tuple(self._scales().keys())

    @property
    def _scales(self):
        scales = {}

        for scale_type in self.system.scales:
            for scale in self.system.scales[scale_type]:

                working_scale = []
                reference_scale = self.system.scales[scale_type][scale]["intervals"]

                current_tone = self.tonic
                working_scale.append(current_tone)

                for interval in reference_scale:
                    current_tone = current_tone.add(interval)
                    working_scale.append(current_tone)

                scales[scale] = Scale(tones=tuple(working_scale))

        return scales
