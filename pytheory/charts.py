import itertools
from typing import Optional

from .systems import SYSTEMS
from .tones import Tone

QUALITIES = ("", "maj", "m", "5", "7", "9", "dim", "m6", "m7", "m9", "maj7", "maj9")
MAX_FRET = 7


class Fingering:
    """A chord fingering labeled with string names.

    Provides both index and named access to fret positions, making it
    clear which string each position corresponds to.

    Example::

        >>> f = Fingering(positions=(0, 3, 2, 0, 1, 0),
        ...               string_names=('E', 'A', 'D', 'G', 'B', 'e'))
        >>> f
        Fingering(E=0, A=3, D=2, G=0, B=1, e=0)
        >>> f['A']
        3
        >>> f[1]
        3
    """

    def __init__(self, positions: tuple, string_names: tuple[str, ...], *, fretboard=None) -> None:
        self.positions = tuple(positions)
        self._fretboard = fretboard
        # Disambiguate duplicate names: for standard guitar tuning
        # (high-to-low), the first occurrence of a duplicate becomes
        # lowercase (e.g. high E → 'e') while the last keeps uppercase.
        from collections import Counter
        name_counts = Counter(string_names)
        seen: dict[str, int] = {}
        unique_names: list[str] = []
        for name in string_names:
            seen[name] = seen.get(name, 0) + 1
            if name_counts[name] > 1 and seen[name] < name_counts[name]:
                unique_names.append(name.lower())
            else:
                unique_names.append(name)

        self.string_names = tuple(unique_names)
        self._map = dict(zip(self.string_names, self.positions))

    def __repr__(self) -> str:
        pairs = ", ".join(
            f"{name}={'x' if pos is None else pos}"
            for name, pos in zip(self.string_names, self.positions)
        )
        return f"Fingering({pairs})"

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.positions[key]
        return self._map[key]

    def __iter__(self):
        return iter(self.positions)

    def __len__(self):
        return len(self.positions)

    def __eq__(self, other):
        if isinstance(other, Fingering):
            return self.positions == other.positions and self.string_names == other.string_names
        if isinstance(other, tuple):
            return self.positions == other
        return NotImplemented

    @property
    def tones(self):
        """Return the sounding tones for this fingering.

        Requires that the Fingering was created with a fretboard reference.
        Muted strings (``None``) are excluded.
        """
        if self._fretboard is None:
            raise ValueError("Cannot resolve tones without a fretboard reference.")
        tones = []
        for pos, tone in zip(self.positions, self._fretboard.tones):
            if pos is not None:
                tones.append(tone.add(pos))
        return tones

    def to_chord(self, fretboard=None) -> "Chord":
        """Apply this fingering to a fretboard, returning a Chord.

        Strings with ``None`` positions (muted) are excluded.
        If no fretboard is given, uses the one stored at creation time.
        """
        from .chords import Chord

        fb = fretboard or self._fretboard
        if fb is None:
            raise ValueError("No fretboard provided.")
        tones = []
        for pos, tone in zip(self.positions, fb.tones):
            if pos is not None:
                tones.append(tone.add(pos))
        return Chord(tones=tones)

    def identify(self) -> Optional[str]:
        """Identify the chord name from this fingering."""
        return self.to_chord().identify()

    def tab(self) -> str:
        """Render this fingering as ASCII guitar tablature.

        Requires that the Fingering was created with a fretboard reference.

        Example::

            >>> fb = Fretboard.guitar()
            >>> print(fb.chord("C").tab())
            C
            e|--0--
            B|--1--
            G|--0--
            D|--2--
            A|--3--
            E|--0--
        """
        if self._fretboard is None:
            raise ValueError("Cannot render tab without a fretboard reference.")
        name = self.identify() or "?"
        lines = [name]
        max_name = max(len(n) for n in self.string_names)
        for sname, fret in zip(self.string_names, self.positions):
            fret_str = "x" if fret is None else str(fret)
            lines.append(f"{sname:>{max_name}}|--{fret_str}--")
        return "\n".join(lines)

CHARTS = {}
CHARTS["western"] = []


class NamedChord:
    def __init__(self, *, tone_name, quality):
        self.tone_name = tone_name
        self.quality = quality
        self._tone = None

    @property
    def name(self):
        return f"{self.tone_name}{self.quality}"

    @property
    def tone(self):
        if self._tone is None:
            flat_to_sharp = {"Ab": "G#", "Bb": "A#", "Db": "C#", "Eb": "D#", "Gb": "F#"}
            tone_name = flat_to_sharp.get(self.tone_name, self.tone_name)
            self._tone = Tone(name=tone_name)
        return self._tone

    def __repr__(self):
        return f"<NamedChord name={self.name!r}>"

    @property
    def acceptable_tones(self):
        acceptable = [self.tone]

        if self.quality == "maj":
            # Major triad: root, major 3rd, perfect 5th
            acceptable += [self.tone.add(4), self.tone.add(7)]

        elif self.quality == "m":
            # Minor triad: root, minor 3rd, perfect 5th
            acceptable += [self.tone.add(3), self.tone.add(7)]

        elif self.quality == "5":
            # Power chord: root, perfect 5th
            acceptable += [self.tone.add(7)]

        elif self.quality == "7":
            # Dominant 7th: root, major 3rd, perfect 5th, minor 7th
            acceptable += [self.tone.add(4), self.tone.add(7), self.tone.add(10)]

        elif self.quality == "9":
            # Dominant 9th: root, major 3rd, perfect 5th, minor 7th, major 9th
            acceptable += [self.tone.add(4), self.tone.add(7), self.tone.add(10), self.tone.add(2)]

        elif self.quality == "dim":
            # Diminished: root, minor 3rd, diminished 5th
            acceptable += [self.tone.add(3), self.tone.add(6)]

        elif self.quality == "m6":
            # Minor 6th: root, minor 3rd, perfect 5th, major 6th
            acceptable += [self.tone.add(3), self.tone.add(7), self.tone.add(9)]

        elif self.quality == "m7":
            # Minor 7th: root, minor 3rd, perfect 5th, minor 7th
            acceptable += [self.tone.add(3), self.tone.add(7), self.tone.add(10)]

        elif self.quality == "m9":
            # Minor 9th: root, minor 3rd, perfect 5th, minor 7th, major 9th
            acceptable += [self.tone.add(3), self.tone.add(7), self.tone.add(10), self.tone.add(2)]

        elif self.quality == "maj7":
            # Major 7th: root, major 3rd, perfect 5th, major 7th
            acceptable += [self.tone.add(4), self.tone.add(7), self.tone.add(11)]

        elif self.quality == "maj9":
            # Major 9th: root, major 3rd, perfect 5th, major 7th, major 9th
            acceptable += [self.tone.add(4), self.tone.add(7), self.tone.add(11), self.tone.add(2)]

        else:
            # Default (no quality): major triad
            acceptable += [self.tone.add(4), self.tone.add(7)]

        return tuple(acceptable)

    @property
    def acceptable_tone_names(self):
        return tuple([tone.name for tone in self.acceptable_tones])

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
            frets = find_fingerings(tone)
            # Always allow muting as an option
            if frets:
                fingering.append((*frets, -1))
            else:
                fingering.append((-1,))

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
            score = 0.0
            fretted = [f for f in fingering if f not in (0, -1)]
            muted = sum(1 for f in fingering if f == -1)
            sounding = len(fingering) - muted

            # Must have at least 2 sounding strings
            if sounding < 2:
                return -100.0

            # Check that all chord tones are present in the voicing
            sounding_names = set()
            for i, f in enumerate(fingering):
                if f != -1:
                    sounding_names.add(fretboard.tones[i].add(f).name)
            required = set(t.name for t in self.acceptable_tones)
            missing = required - sounding_names
            score -= len(missing) * 5.0

            # Reward open strings
            open_strings = sum(1 for f in fingering if f == 0)
            score += open_strings * 2.0

            # Penalize muted strings, but only mildly
            score -= muted * 0.3

            # Penalize fret span (hard to stretch)
            if fretted:
                span = max(fretted) - min(fretted)
                score -= span * 2.0

            # Penalize high fret positions (prefer open position)
            if fretted:
                score -= (sum(fretted) / len(fretted)) * 0.8

            # Penalize many fingers needed
            score -= len(fretted) * 0.3

            # Reward root in bass — the lowest sounding string
            for i in range(len(fingering) - 1, -1, -1):
                f = fingering[i]
                if f == -1:
                    continue
                bass_tone = fretboard.tones[i].add(f)
                if bass_tone.name == self.tone.name:
                    score += 4.0
                else:
                    # Penalize non-root bass notes
                    score -= 1.5
                break

            # Prefer muting from the bass side (contiguous muting)
            # e.g. xx0232 is good, x0x232 is awkward
            mute_from_bass = 0
            for i in range(len(fingering) - 1, -1, -1):
                if fingering[i] == -1:
                    mute_from_bass += 1
                else:
                    break
            interior_mutes = muted - mute_from_bass
            score -= interior_mutes * 3.0

            return score

        def gen():
            fingerings = self.fingerings(fretboard=fretboard)
            scored = [(fingering_score(f), f) for f in fingerings]
            max_score = max(s for s, _ in scored)

            for s, possible_fingering in scored:
                if s == max_score:
                    yield possible_fingering

        string_names = tuple(t.name for t in fretboard.tones)
        best_fingerings = tuple([g for g in gen()])
        if not multiple:
            return Fingering(self.fix_fingering(best_fingerings[0]), string_names, fretboard=fretboard)
        else:
            return tuple([Fingering(self.fix_fingering(f), string_names, fretboard=fretboard) for f in best_fingerings])

    def tab(self, *, fretboard):
        """Render this chord as ASCII guitar tablature.

        Example::

            >>> print(CHARTS["western"]["C"].tab(fretboard=Fretboard.guitar()))
            C
            e|--0--
            B|--1--
            G|--0--
            D|--2--
            A|--3--
            E|--0--
        """
        fingering = self.fingering(fretboard=fretboard)
        string_names = [t.name for t in fretboard.tones]
        lines = [self.name]
        max_name = max(len(n) for n in string_names)
        for i, (name, fret) in enumerate(zip(string_names, fingering)):
            fret_str = "x" if fret is None else str(fret)
            lines.append(f"{name:>{max_name}}|--{fret_str}--")
        return "\n".join(lines)


western_chart = {}
for tone_titles in SYSTEMS["western"].tone_names:
    # Take the second tone name, if it's available.
    if len(tone_titles) == 2:
        tone_name = tone_titles[1]
    else:
        tone_name = tone_titles[0]

    for quality in QUALITIES:
        named_chord = NamedChord(tone_name=tone_name, quality=quality)
        western_chart.update({f"{tone_name}{quality}": named_chord})

CHARTS["western"] = western_chart


def charts_for_fretboard(*, chart=CHARTS["western"], fretboard):
    super_chart = {}
    for chord in chart:
        super_chart[chord] = chart[chord].fingering(fretboard=fretboard)
    return super_chart
