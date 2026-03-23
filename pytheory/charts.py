import functools
import itertools
from typing import Optional

from .systems import SYSTEMS
from .tones import Tone

QUALITIES = ("", "maj", "m", "5", "7", "9", "dim", "m6", "m7", "m9", "maj7", "maj9")
MAX_FRET = 7

# Standard guitar tuning (high to low): E4 B3 G3 D3 A2 E2
STANDARD_GUITAR_TUNING = ("E4", "B3", "G3", "D3", "A2", "E2")

# Curated override fingerings for common guitar chords in standard tuning.
# Key: chord name, Value: tuple of fret positions (-1 = muted string).
# Order is high-to-low (matching Fretboard.guitar() string order).
GUITAR_OVERRIDES = {
    "C":    (0, 1, 0, 2, 3, -1),
    "D":    (2, 3, 2, 0, -1, -1),
    "Dm":   (1, 3, 2, 0, -1, -1),
    "D7":   (2, 1, 2, 0, -1, -1),
    "E":    (0, 0, 1, 2, 2, 0),
    "Em":   (0, 0, 0, 2, 2, 0),
    "F":    (1, 1, 2, 3, 3, 1),
    "G":    (3, 0, 0, 0, 2, 3),
    "G7":   (1, 0, 0, 0, 2, 3),
    "A":    (0, 2, 2, 2, 0, -1),
    "Am":   (0, 1, 2, 2, 0, -1),
    "Am7":  (0, 1, 0, 2, 0, -1),
    "B":    (2, 4, 4, 4, 2, -1),
    "Bm":   (2, 3, 4, 4, 2, -1),
    "B7":   (2, 0, 2, 1, 2, -1),
}

# Memoization cache for fingering lookups.
# Key: (chord_name, fretboard_tuning_tuple)
# Value: Fingering object (single) or tuple of Fingerings (multiple)
# Bounded to _CACHE_MAX_SIZE entries; cleared entirely when full.
_CACHE_MAX_SIZE = 1024
_fingering_cache: dict[tuple, "Fingering"] = {}
_fingering_multi_cache: dict[tuple, tuple] = {}
_possible_cache: dict[tuple, tuple] = {}


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
    def _prefer_flats(self):
        """Determine whether this chord's tones should use flat spellings.

        Uses the circle-of-fifths convention:
        - Flat-root notes (Bb, Eb, Ab, Db, Gb) always prefer flats.
        - Major-type qualities prefer flats for roots: F, Bb, Eb, Ab, Db, Gb.
        - Minor-type qualities prefer flats for roots: D, G, C, F, Bb, Eb, Ab.
        """
        # Root is itself a flat note — always prefer flats
        if "b" in self.tone_name and self.tone_name != "B":
            return True

        _FLAT_MAJOR_ROOTS = {"F", "Bb", "Eb", "Ab", "Db", "Gb"}
        _FLAT_MINOR_ROOTS = {"D", "G", "C", "F", "Bb", "Eb", "Ab"}
        # Dominant 7th/9th chords contain a minor 7th (b7), so they
        # follow the same flat-preference roots as minor chords.
        _FLAT_DOMINANT_ROOTS = {"C", "F", "G", "Bb", "Eb", "Ab", "Db", "Gb"}

        minor_qualities = {"m", "m6", "m7", "m9", "dim"}
        dominant_qualities = {"7", "9"}
        major_qualities = {"", "maj", "5", "maj7", "maj9"}

        if self.quality in minor_qualities and self.tone_name in _FLAT_MINOR_ROOTS:
            return True
        if self.quality in dominant_qualities and self.tone_name in _FLAT_DOMINANT_ROOTS:
            return True
        if self.quality in major_qualities and self.tone_name in _FLAT_MAJOR_ROOTS:
            return True

        return False

    @property
    def acceptable_tones(self):
        acceptable = [self.tone]
        flats = self._prefer_flats

        if self.quality == "maj":
            # Major triad: root, major 3rd, perfect 5th
            acceptable += [self.tone.add(4, prefer_flats=flats), self.tone.add(7, prefer_flats=flats)]

        elif self.quality == "m":
            # Minor triad: root, minor 3rd, perfect 5th
            acceptable += [self.tone.add(3, prefer_flats=flats), self.tone.add(7, prefer_flats=flats)]

        elif self.quality == "5":
            # Power chord: root, perfect 5th
            acceptable += [self.tone.add(7, prefer_flats=flats)]

        elif self.quality == "7":
            # Dominant 7th: root, major 3rd, perfect 5th, minor 7th
            acceptable += [self.tone.add(4, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(10, prefer_flats=flats)]

        elif self.quality == "9":
            # Dominant 9th: root, major 3rd, perfect 5th, minor 7th, major 9th
            acceptable += [self.tone.add(4, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(10, prefer_flats=flats), self.tone.add(2, prefer_flats=flats)]

        elif self.quality == "dim":
            # Diminished: root, minor 3rd, diminished 5th
            acceptable += [self.tone.add(3, prefer_flats=flats), self.tone.add(6, prefer_flats=flats)]

        elif self.quality == "m6":
            # Minor 6th: root, minor 3rd, perfect 5th, major 6th
            acceptable += [self.tone.add(3, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(9, prefer_flats=flats)]

        elif self.quality == "m7":
            # Minor 7th: root, minor 3rd, perfect 5th, minor 7th
            acceptable += [self.tone.add(3, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(10, prefer_flats=flats)]

        elif self.quality == "m9":
            # Minor 9th: root, minor 3rd, perfect 5th, minor 7th, major 9th
            acceptable += [self.tone.add(3, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(10, prefer_flats=flats), self.tone.add(2, prefer_flats=flats)]

        elif self.quality == "maj7":
            # Major 7th: root, major 3rd, perfect 5th, major 7th
            acceptable += [self.tone.add(4, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(11, prefer_flats=flats)]

        elif self.quality == "maj9":
            # Major 9th: root, major 3rd, perfect 5th, major 7th, major 9th
            acceptable += [self.tone.add(4, prefer_flats=flats), self.tone.add(7, prefer_flats=flats), self.tone.add(11, prefer_flats=flats), self.tone.add(2, prefer_flats=flats)]

        else:
            # Default (no quality): major triad
            acceptable += [self.tone.add(4, prefer_flats=flats), self.tone.add(7, prefer_flats=flats)]

        return tuple(acceptable)

    @property
    def acceptable_tone_names(self):
        names = [tone.name for tone in self.acceptable_tones]
        # The root tone is stored internally with sharp spelling (e.g. A#
        # for Bb) via flat_to_sharp mapping; restore the original flat name.
        if names and names[0] != self.tone_name:
            names[0] = self.tone_name
        return tuple(names)

    def _possible_fingerings(self, *, fretboard):
        # Check the _possible_cache first
        key = self._cache_key(fretboard)
        if key in _possible_cache:
            return _possible_cache[key]

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

        result = tuple(fingering)

        # Bounded cache: clear entirely if over limit
        if len(_possible_cache) >= _CACHE_MAX_SIZE:
            _possible_cache.clear()
        _possible_cache[key] = result

        return result

    @staticmethod
    def fix_fingering(fingering):
        fingering = list(fingering)
        for i, finger in enumerate(fingering):
            if finger == -1:
                fingering[i] = None
        return tuple(fingering)

    def fingerings(self, *, fretboard):
        return tuple(itertools.product(*self._possible_fingerings(fretboard=fretboard)))

    def _cache_key(self, fretboard):
        """Return a hashable key for memoization."""
        return (self.name, tuple(t.full_name for t in fretboard.tones))

    def fingering(self, *, fretboard, multiple=False):
        # Check cache first
        key = self._cache_key(fretboard)
        if multiple:
            if key in _fingering_multi_cache:
                return _fingering_multi_cache[key]
        else:
            if key in _fingering_cache:
                return _fingering_cache[key]

        # Check for curated guitar chord overrides in standard tuning
        tuning = tuple(t.full_name for t in fretboard.tones)
        if tuning == STANDARD_GUITAR_TUNING and self.name in GUITAR_OVERRIDES:
            string_names = tuple(t.name for t in fretboard.tones)
            override = GUITAR_OVERRIDES[self.name]
            if not multiple:
                result = Fingering(self.fix_fingering(override), string_names, fretboard=fretboard)
                if len(_fingering_cache) >= _CACHE_MAX_SIZE:
                    _fingering_cache.clear()
                _fingering_cache[key] = result
                return result
            else:
                result = (Fingering(self.fix_fingering(override), string_names, fretboard=fretboard),)
                if len(_fingering_multi_cache) >= _CACHE_MAX_SIZE:
                    _fingering_multi_cache.clear()
                _fingering_multi_cache[key] = result
                return result

        MAX_SPAN = 4  # max fret span for a human hand

        def fingering_score(fingering):
            score = 0.0
            fretted = [f for f in fingering if f not in (0, -1)]
            muted = sum(1 for f in fingering if f == -1)
            sounding = len(fingering) - muted

            # Must have at least 2 sounding strings
            if sounding < 2:
                return -100.0

            # Hard constraint: fret span must be playable
            if fretted:
                span = max(fretted) - min(fretted)
                if span > MAX_SPAN:
                    return -100.0
            else:
                span = 0

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

            # Penalize fret span
            score -= span * 2.0

            # Penalize high fret positions (prefer open position)
            if fretted:
                score -= (sum(fretted) / len(fretted)) * 0.8

            # Barre chord detection: if multiple strings share the same
            # fret and it's the lowest fret in the shape, one finger can
            # cover them all — so they cost only 1 finger, not N.
            # Also check that barre strings are contiguous (no gaps).
            if fretted:
                min_fret = min(fretted)
                barre_indices = [i for i, f in enumerate(fingering) if f == min_fret and f > 0]
                barre_count = len(barre_indices)

                if barre_count >= 2:
                    unique_higher = len(set(f for f in fretted if f > min_fret))
                    fingers_needed = unique_higher + 1  # 1 for barre
                    # Mild reward for barre efficiency (saves fingers)
                    score += (barre_count - 1) * 0.5
                else:
                    fingers_needed = len(fretted)
            else:
                fingers_needed = 0

            # Penalize fingers needed (max 4 on a guitar)
            score -= fingers_needed * 0.3
            if fingers_needed > 4:
                score -= (fingers_needed - 4) * 5.0

            # Reward root in bass — the lowest sounding string
            for i in range(len(fingering) - 1, -1, -1):
                f = fingering[i]
                if f == -1:
                    continue
                bass_tone = fretboard.tones[i].add(f)
                if bass_tone.name == self.tone.name:
                    score += 4.0
                else:
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
            result = Fingering(self.fix_fingering(best_fingerings[0]), string_names, fretboard=fretboard)
            # Bounded cache: clear entirely if over limit
            if len(_fingering_cache) >= _CACHE_MAX_SIZE:
                _fingering_cache.clear()
            _fingering_cache[key] = result
            return result
        else:
            result = tuple([Fingering(self.fix_fingering(f), string_names, fretboard=fretboard) for f in best_fingerings])
            # Bounded cache: clear entirely if over limit
            if len(_fingering_multi_cache) >= _CACHE_MAX_SIZE:
                _fingering_multi_cache.clear()
            _fingering_multi_cache[key] = result
            return result

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
