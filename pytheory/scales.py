import numeral

from .systems import SYSTEMS
from .tones import Tone


class Scale:
    def __init__(self, *, tones, degrees=None, system='western'):
        self.tones = tones
        self.degrees = degrees

        if isinstance(system, str):
            self.system_name = system
            self._system = None
        else:
            self.system_name = None
            self._system = system

        if self.degrees:
            if not len(self.tones) == len(self.degrees):
                raise ValueError("The number of tones and degrees must be equal!")

    @property
    def system(self):
        if self._system:
            return self._system

        if self.system_name:
            return SYSTEMS[self.system_name]

    def __repr__(self):
        r = []
        for (i, tone) in enumerate(self.tones):
            degree = numeral.int2roman(i + 1, only_ascii=True)
            r += [f"{degree}={tone.full_name}"]

        r = " ".join(r)
        return f"<Scale {r}>"

    def degree(self, item, major=None, minor=False):
        # TODO: cleanup degrees.

        # Ensure that both major and minor aren't passed.
        if all((major, minor)):
            raise ValueError("You can only specify one of the following: major, minor.")

        # Roman–style degree reference (e.g. "IV").
        if isinstance(item, str):
            degrees = []
            for (i, tone) in enumerate(self.tones):
                degrees.append(numeral.int2roman(i + 1, only_ascii=True))

            if item in degrees:
                item = degrees.index(item)

            # If we're still a string, attempt to grab degree name.
            if isinstance(item, str):
                # Default to major mode, because that's how people do it, I think.
                if not minor and major is None:
                    major = True

                for i, _degree in enumerate(self.system.degrees):
                    # "tonic / octave"
                    comp = _degree[0]

                    if major:
                        comp = _degree[1][0]
                    elif minor:
                        comp = _degree[1][1]

                    if item == comp:
                        item = i

        # List/Tuple–style reference.
        if isinstance(item, int) or isinstance(item, slice):
            return self.tones[item]

    def __getitem__(self, item):
        result = self.degree(item)
        if result is None:
            raise KeyError(item)
        return result


class TonedScale:
    def __init__(self, *, system=SYSTEMS["western"], tonic):
        self.system = system

        if not isinstance(tonic, Tone):
            tonic = Tone.from_string(tonic, system=self.system)

        self.tonic = tonic

    def __repr__(self):
        return f"<TonedScale system={self.system!r} tonic={self.tonic}>"

    def __getitem__(self, scale):
        result = self.get(scale)
        if result is None:
            raise KeyError(scale)
        return result

    def get(self, scale):
        try:
            return self._scales[scale]
        except KeyError:
            pass

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
