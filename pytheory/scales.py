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

    def __iter__(self):
        return iter(self.tones)

    def __len__(self):
        return len(self.tones)

    def __contains__(self, item):
        if isinstance(item, str):
            return any(item == t.name for t in self.tones)
        return item in self.tones

    @property
    def note_names(self):
        """List of note names in this scale."""
        return [t.name for t in self.tones]

    def chord(self, *degrees):
        """Build a Chord from scale degrees (0-indexed).

        Wraps around if degrees exceed the scale length, transposing
        up by an octave as needed.

        Example: scale.chord(0, 2, 4) builds a triad from the 1st, 3rd, 5th.
        """
        from .chords import Chord
        # Scale has N tones where the last is the octave of the first,
        # so the unique tones are tones[:-1] (length N-1).
        unique = len(self.tones) - 1
        result = []
        for d in degrees:
            idx = d % unique
            octaves_up = d // unique
            tone = self.tones[idx]
            if octaves_up > 0:
                tone = tone.add(12 * octaves_up)
            result.append(tone)
        return Chord(tones=result)

    def transpose(self, semitones):
        """Return a new Scale transposed by the given number of semitones.

        Every tone is shifted by the same interval, preserving the
        scale's interval pattern.

        Example::

            >>> c_major = TonedScale(tonic="C4")["major"]
            >>> d_major = c_major.transpose(2)
            >>> d_major.note_names
            ['D', 'E', 'F#', 'G', 'A', 'B', 'C#', 'D']
        """
        from .chords import Chord
        new_tones = tuple(t.add(semitones) for t in self.tones)
        return Scale(tones=new_tones)

    def triad(self, root=0):
        """Build a triad starting from the given scale degree (0-indexed).

        Returns a chord with the root, 3rd, and 5th above it.
        """
        return self.chord(root, root + 2, root + 4)

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
                for i, _degree in enumerate(self.system.degrees):
                    # Match degree name (e.g. "tonic", "dominant")
                    if item == _degree[0]:
                        item = i
                        break

                    # Also match mode name (e.g. "ionian", "dorian")
                    if item in _degree[1]:
                        item = i
                        break

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
        return tuple(self._scales.keys())

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
