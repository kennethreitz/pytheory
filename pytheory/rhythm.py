"""Rhythm and duration primitives for PyTheory."""

import math
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Duration(Enum):
    """Note durations in beats (quarter note = 1 beat)."""

    WHOLE = 4.0
    HALF = 2.0
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25
    DOTTED_HALF = 3.0
    DOTTED_QUARTER = 1.5
    TRIPLET_QUARTER = 2 / 3


class TimeSignature:
    """A musical time signature like 4/4 or 6/8."""

    def __init__(self, beats: int = 4, unit: int = 4):
        self.beats = beats
        self.unit = unit

    @classmethod
    def from_string(cls, s: str) -> "TimeSignature":
        """Parse '4/4', '3/4', '6/8' etc."""
        top, bottom = s.split("/")
        return cls(beats=int(top), unit=int(bottom))

    @property
    def beats_per_measure(self) -> float:
        """Total beats in one measure (in quarter-note units)."""
        return self.beats * (4 / self.unit)

    def __repr__(self):
        return f"{self.beats}/{self.unit}"

    def __eq__(self, other):
        if isinstance(other, TimeSignature):
            return self.beats == other.beats and self.unit == other.unit
        return NotImplemented


@dataclass
class Note:
    """A pairing of a sound (Tone, Chord, or None for rest) with a duration."""

    tone: object
    duration: Duration

    @property
    def beats(self) -> float:
        return self.duration.value


def Rest(duration: Duration = Duration.QUARTER) -> Note:
    """Create a rest (silent note) with the given duration."""
    return Note(tone=None, duration=duration)


# ---------------------------------------------------------------------------
# MIDI variable-length quantity encoder (copied from play.py to avoid
# pulling in the PortAudio dependency).
# ---------------------------------------------------------------------------

def _vlq(value):
    """Encode an integer as MIDI variable-length quantity bytes."""
    result = []
    result.append(value & 0x7F)
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


# ── Drum patterns ─────────────────────────────────────────────────────────


class DrumSound(Enum):
    """General MIDI percussion note numbers (channel 10).

    These map to the GM drum map standard supported by virtually
    all MIDI devices and DAWs.
    """
    KICK = 36
    SNARE = 38
    RIMSHOT = 37
    CLAP = 39
    CLOSED_HAT = 42
    OPEN_HAT = 46
    PEDAL_HAT = 44
    LOW_TOM = 45
    MID_TOM = 47
    HIGH_TOM = 50
    CRASH = 49
    RIDE = 51
    RIDE_BELL = 53
    COWBELL = 56
    CLAVE = 75
    SHAKER = 70
    TAMBOURINE = 54
    CONGA_HIGH = 63
    CONGA_LOW = 64
    BONGO_HIGH = 60
    BONGO_LOW = 61
    TIMBALE_HIGH = 65
    TIMBALE_LOW = 66
    AGOGO_HIGH = 67
    AGOGO_LOW = 68
    GUIRO = 73
    MARACAS = 70


class _Hit:
    """A single drum hit at a specific position in a pattern."""
    __slots__ = ("sound", "position", "velocity")

    def __init__(self, sound: DrumSound, position: float, velocity: int = 100):
        self.sound = sound
        self.position = position  # in beats
        self.velocity = velocity

    def __repr__(self):
        return f"Hit({self.sound.name}, beat={self.position}, vel={self.velocity})"


class Pattern:
    """A drum pattern — a repeating rhythmic figure.

    Patterns are defined as a list of hits within a fixed number of beats.
    They can be rendered to a Score for MIDI export, or combined with
    chord progressions.

    Example::

        >>> pattern = Pattern.preset("rock")
        >>> print(pattern)
        <Pattern 'rock' 4/4 4.0 beats 12 hits>
    """

    def __init__(self, name: str, hits: list[_Hit], beats: float = 4.0,
                 time_signature: str = "4/4"):
        self.name = name
        self.hits = hits
        self.beats = beats
        self.time_signature_str = time_signature

    def __repr__(self):
        return (f"<Pattern {self.name!r} {self.time_signature_str} "
                f"{self.beats} beats {len(self.hits)} hits>")

    def to_score(self, repeats: int = 4, bpm: int = 120) -> "Score":
        """Render this pattern to a Score for MIDI export.

        Args:
            repeats: Number of times to repeat the pattern.
            bpm: Tempo in beats per minute.

        Returns:
            A Score containing drum hits as MIDI percussion notes.
        """
        score = Score(self.time_signature_str, bpm=bpm)
        for r in range(repeats):
            offset = r * self.beats
            for hit in self.hits:
                score._drum_hits.append(
                    _Hit(hit.sound, hit.position + offset, hit.velocity))
            score._drum_pattern_beats += self.beats
        return score

    # ── Presets ───────────────────────────────────────────────────────

    _PRESETS: dict[str, dict] = {}

    @classmethod
    def preset(cls, name: str) -> "Pattern":
        """Load a named drum pattern preset.

        Available presets:

        - **rock** — standard 4/4 rock beat (kick-snare-hat)
        - **jazz** — swing ride pattern with ghost notes
        - **bebop** — fast jazz ride with syncopated kick/snare
        - **bossa nova** — Brazilian 2-bar pattern with cross-stick
        - **salsa** — clave-driven Afro-Cuban pattern
        - **funk** — syncopated 16th-note groove
        - **reggae** — one-drop pattern (snare on 3)
        - **waltz** — 3/4 pattern (oom-pah-pah)
        - **12/8 blues** — slow blues shuffle
        - **samba** — Brazilian carnival pattern
        - **son clave 3-2** — the Afro-Cuban rhythmic key
        - **son clave 2-3** — reversed clave

        Example::

            >>> Pattern.preset("salsa")
            <Pattern 'salsa' 4/4 8.0 beats ...>
        """
        if name not in cls._PRESETS:
            raise ValueError(
                f"Unknown preset: {name!r}. "
                f"Available: {', '.join(cls.list_presets())}")
        data = cls._PRESETS[name]
        return cls(**data)

    @classmethod
    def list_presets(cls) -> list[str]:
        """Return a list of all available preset names."""
        return sorted(cls._PRESETS.keys())


def _h(sound, position, velocity=100):
    """Shorthand for building hit lists."""
    return _Hit(sound, position, velocity)


K = DrumSound.KICK
S = DrumSound.SNARE
CH = DrumSound.CLOSED_HAT
OH = DrumSound.OPEN_HAT
RD = DrumSound.RIDE
RB = DrumSound.RIDE_BELL
RS = DrumSound.RIMSHOT
CR = DrumSound.CRASH
CL = DrumSound.CLAVE
CB = DrumSound.COWBELL
CGA = DrumSound.CONGA_HIGH
CGB = DrumSound.CONGA_LOW
BGH = DrumSound.BONGO_HIGH
BGL = DrumSound.BONGO_LOW
TB = DrumSound.TAMBOURINE
TBH = DrumSound.TIMBALE_HIGH
TBL = DrumSound.TIMBALE_LOW
SH = DrumSound.SHAKER

# ── Pattern presets ───────────────────────────────────────────────────────

Pattern._PRESETS["rock"] = dict(
    name="rock",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.5),
        _h(S, 1.0), _h(CH, 1.0), _h(CH, 1.5),
        _h(K, 2.0), _h(CH, 2.0), _h(CH, 2.5),
        _h(S, 3.0), _h(CH, 3.0), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["jazz"] = dict(
    name="jazz",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Ride: swing pattern (1, 2-and, 3, 4-and)
        _h(RD, 0.0), _h(RD, 1.0), _h(CH, 1.67, 60),
        _h(RD, 2.0), _h(RD, 3.0), _h(CH, 3.67, 60),
        # Kick feathered on 1 and 3
        _h(K, 0.0, 50), _h(K, 2.0, 50),
        # Hi-hat foot on 2 and 4
        _h(DrumSound.PEDAL_HAT, 1.0), _h(DrumSound.PEDAL_HAT, 3.0),
    ],
)

Pattern._PRESETS["bebop"] = dict(
    name="bebop",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Ride: all four beats + swing upbeats
        _h(RD, 0.0), _h(RD, 0.67, 70),
        _h(RD, 1.0), _h(RD, 1.67, 70),
        _h(RD, 2.0), _h(RD, 2.67, 70),
        _h(RD, 3.0), _h(RD, 3.67, 70),
        # Hi-hat on 2 and 4
        _h(DrumSound.PEDAL_HAT, 1.0), _h(DrumSound.PEDAL_HAT, 3.0),
        # Syncopated kick
        _h(K, 0.0, 60), _h(K, 2.67, 50),
        # Ghost snare
        _h(S, 3.5, 40),
    ],
)

Pattern._PRESETS["bossa nova"] = dict(
    name="bossa nova",
    time_signature="4/4",
    beats=8.0,  # 2-bar pattern
    hits=[
        # Bar 1
        _h(RS, 0.0), _h(K, 0.0, 80),
        _h(CH, 0.5), _h(CH, 1.0), _h(CH, 1.5),
        _h(RS, 2.0), _h(CH, 2.5),
        _h(RS, 3.0), _h(CH, 3.0), _h(CH, 3.5),
        # Bar 2
        _h(CH, 4.0), _h(K, 4.0, 80), _h(CH, 4.5),
        _h(RS, 5.0), _h(CH, 5.5),
        _h(CH, 6.0), _h(RS, 6.5),
        _h(CH, 7.0), _h(CH, 7.5),
    ],
)

Pattern._PRESETS["salsa"] = dict(
    name="salsa",
    time_signature="4/4",
    beats=8.0,  # 2-bar clave cycle
    hits=[
        # Son clave 3-2
        _h(CL, 0.0), _h(CL, 1.5), _h(CL, 3.0),
        _h(CL, 5.0), _h(CL, 6.5),
        # Congas (tumbao)
        _h(CGB, 0.0, 80), _h(CGA, 0.5, 70), _h(CGA, 1.0, 90),
        _h(CGB, 2.0, 80), _h(CGA, 2.5, 70), _h(CGA, 3.0, 90),
        _h(CGB, 4.0, 80), _h(CGA, 4.5, 70), _h(CGA, 5.0, 90),
        _h(CGB, 6.0, 80), _h(CGA, 6.5, 70), _h(CGA, 7.0, 90),
        # Cowbell (campana)
        _h(CB, 0.0), _h(CB, 1.0), _h(CB, 2.0), _h(CB, 3.0),
        _h(CB, 4.0), _h(CB, 5.0), _h(CB, 6.0), _h(CB, 7.0),
        # Kick on 1 and the-and-of-2
        _h(K, 0.0, 90), _h(K, 2.5, 70),
        _h(K, 4.0, 90), _h(K, 6.5, 70),
    ],
)

Pattern._PRESETS["funk"] = dict(
    name="funk",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.25, 60),
        _h(CH, 0.5), _h(CH, 0.75, 60),
        _h(S, 1.0), _h(CH, 1.0), _h(CH, 1.25, 60),
        _h(K, 1.5), _h(CH, 1.5), _h(CH, 1.75, 60),
        _h(CH, 2.0), _h(K, 2.25, 80), _h(CH, 2.25, 60),
        _h(CH, 2.5), _h(CH, 2.75, 60),
        _h(S, 3.0), _h(CH, 3.0), _h(CH, 3.25, 60),
        _h(CH, 3.5), _h(K, 3.75, 70), _h(CH, 3.75, 60),
    ],
)

Pattern._PRESETS["reggae"] = dict(
    name="reggae",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # One-drop: kick + snare on beat 3
        _h(CH, 0.0), _h(CH, 0.5),
        _h(CH, 1.0), _h(CH, 1.5),
        _h(K, 2.0), _h(S, 2.0), _h(CH, 2.0), _h(CH, 2.5),
        _h(CH, 3.0), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["waltz"] = dict(
    name="waltz",
    time_signature="3/4",
    beats=3.0,
    hits=[
        _h(K, 0.0), _h(CR, 0.0, 60),
        _h(CH, 1.0), _h(CH, 2.0),
    ],
)

Pattern._PRESETS["12/8 blues"] = dict(
    name="12/8 blues",
    time_signature="12/8",
    beats=6.0,  # 12 eighth notes = 6 quarter beats
    hits=[
        # Shuffle feel
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.67, 70), _h(CH, 1.0),
        _h(S, 1.5), _h(CH, 1.67, 70), _h(CH, 2.0),
        _h(K, 3.0), _h(CH, 3.0), _h(CH, 3.67, 70), _h(CH, 4.0),
        _h(S, 4.5), _h(CH, 4.67, 70), _h(CH, 5.0),
    ],
)

Pattern._PRESETS["samba"] = dict(
    name="samba",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(SH, 0.0), _h(SH, 0.25),
        _h(SH, 0.5), _h(SH, 0.75),
        _h(S, 1.0, 80), _h(SH, 1.0), _h(SH, 1.25),
        _h(K, 1.5), _h(SH, 1.5), _h(SH, 1.75),
        _h(SH, 2.0), _h(K, 2.25, 70), _h(SH, 2.25),
        _h(SH, 2.5), _h(SH, 2.75),
        _h(S, 3.0, 80), _h(SH, 3.0), _h(SH, 3.25),
        _h(K, 3.5), _h(SH, 3.5), _h(SH, 3.75),
    ],
)

Pattern._PRESETS["son clave 3-2"] = dict(
    name="son clave 3-2",
    time_signature="4/4",
    beats=8.0,
    hits=[
        _h(CL, 0.0), _h(CL, 1.5), _h(CL, 3.0),
        _h(CL, 5.0), _h(CL, 6.5),
    ],
)

Pattern._PRESETS["son clave 2-3"] = dict(
    name="son clave 2-3",
    time_signature="4/4",
    beats=8.0,
    hits=[
        _h(CL, 1.0), _h(CL, 2.5),
        _h(CL, 4.0), _h(CL, 5.5), _h(CL, 7.0),
    ],
)

Pattern._PRESETS["rumba clave 3-2"] = dict(
    name="rumba clave 3-2",
    time_signature="4/4",
    beats=8.0,
    hits=[
        _h(CL, 0.0), _h(CL, 1.5), _h(CL, 3.5),
        _h(CL, 5.0), _h(CL, 6.5),
    ],
)

Pattern._PRESETS["rumba clave 2-3"] = dict(
    name="rumba clave 2-3",
    time_signature="4/4",
    beats=8.0,
    hits=[
        _h(CL, 1.0), _h(CL, 2.5),
        _h(CL, 4.0), _h(CL, 5.5), _h(CL, 7.5),
    ],
)

Pattern._PRESETS["cascara"] = dict(
    name="cascara",
    time_signature="4/4",
    beats=8.0,
    hits=[
        # Shell pattern played on timbale shell — the backbone of salsa
        _h(TBH, 0.0), _h(TBH, 0.5), _h(TBH, 1.5),
        _h(TBH, 2.0), _h(TBH, 3.0), _h(TBH, 3.5),
        _h(TBH, 4.5), _h(TBH, 5.0), _h(TBH, 5.5),
        _h(TBH, 6.5), _h(TBH, 7.0),
    ],
)

Pattern._PRESETS["mozambique"] = dict(
    name="mozambique",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CB, 0.0), _h(CB, 0.5),
        _h(CB, 1.0), _h(S, 1.0, 80), _h(CB, 1.5),
        _h(K, 2.0), _h(CB, 2.0), _h(CB, 2.5),
        _h(CB, 3.0), _h(S, 3.0, 80), _h(CB, 3.5),
        _h(CGA, 0.5, 70), _h(CGB, 1.0, 80),
        _h(CGA, 2.5, 70), _h(CGB, 3.0, 80),
    ],
)

Pattern._PRESETS["nanigo"] = dict(
    name="nanigo",
    time_signature="6/8",
    beats=3.0,
    hits=[
        # 6/8 Afro-Cuban bell pattern
        _h(CB, 0.0), _h(CB, 0.5), _h(CB, 1.0),
        _h(CB, 1.5), _h(CB, 2.5),
    ],
)

Pattern._PRESETS["guaguanco"] = dict(
    name="guaguanco",
    time_signature="4/4",
    beats=8.0,
    hits=[
        # Rumba guaguanco conga pattern
        _h(CGB, 0.0, 90), _h(CGA, 0.5, 60), _h(CGB, 1.0, 70),
        _h(CGA, 1.5, 90), _h(CGB, 2.0, 60), _h(CGA, 2.5, 80),
        _h(CGA, 3.0, 60), _h(CGB, 3.5, 90),
        _h(CGB, 4.0, 90), _h(CGA, 4.5, 60), _h(CGB, 5.0, 70),
        _h(CGA, 5.5, 90), _h(CGB, 6.0, 60), _h(CGA, 6.5, 80),
        _h(CGA, 7.0, 60), _h(CGB, 7.5, 90),
        # Clave underneath
        _h(CL, 0.0), _h(CL, 1.5), _h(CL, 3.5),
        _h(CL, 5.0), _h(CL, 6.5),
    ],
)

Pattern._PRESETS["tresillo"] = dict(
    name="tresillo",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # 3+3+2 — the most fundamental Afro-Latin cell
        _h(K, 0.0), _h(K, 1.5), _h(K, 3.0),
    ],
)

Pattern._PRESETS["habanera"] = dict(
    name="habanera",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Habanera / tango rhythm
        _h(K, 0.0), _h(K, 1.5), _h(K, 2.0), _h(K, 3.0),
    ],
)

Pattern._PRESETS["second line"] = dict(
    name="second line",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # New Orleans second line snare pattern
        _h(S, 0.0), _h(S, 0.5, 60), _h(S, 0.75, 50),
        _h(S, 1.0), _h(S, 1.5, 60),
        _h(S, 2.0), _h(S, 2.5, 60), _h(S, 2.75, 50),
        _h(S, 3.0), _h(S, 3.5, 60),
        _h(K, 0.0), _h(K, 2.0),
    ],
)

Pattern._PRESETS["train beat"] = dict(
    name="train beat",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Country train beat — cross-stick on every beat, kick on 1 and 3
        _h(RS, 0.0), _h(CH, 0.0), _h(CH, 0.25), _h(CH, 0.5), _h(CH, 0.75),
        _h(RS, 1.0), _h(CH, 1.0), _h(CH, 1.25), _h(CH, 1.5), _h(CH, 1.75),
        _h(RS, 2.0), _h(CH, 2.0), _h(CH, 2.25), _h(CH, 2.5), _h(CH, 2.75),
        _h(RS, 3.0), _h(CH, 3.0), _h(CH, 3.25), _h(CH, 3.5), _h(CH, 3.75),
        _h(K, 0.0), _h(K, 2.0),
    ],
)

Pattern._PRESETS["half time"] = dict(
    name="half time",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.5),
        _h(CH, 1.0), _h(CH, 1.5),
        _h(S, 2.0), _h(CH, 2.0), _h(CH, 2.5),
        _h(CH, 3.0), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["double time"] = dict(
    name="double time",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.25), _h(CH, 0.5), _h(CH, 0.75),
        _h(S, 1.0), _h(CH, 1.0), _h(CH, 1.25), _h(CH, 1.5), _h(CH, 1.75),
        _h(K, 2.0), _h(CH, 2.0), _h(CH, 2.25), _h(CH, 2.5), _h(CH, 2.75),
        _h(S, 3.0), _h(CH, 3.0), _h(CH, 3.25), _h(CH, 3.5), _h(CH, 3.75),
    ],
)

Pattern._PRESETS["blast beat"] = dict(
    name="blast beat",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Metal blast beat — everything on every 16th
        *[_h(K, i * 0.25) for i in range(16)],
        *[_h(S, i * 0.25) for i in range(16)],
        *[_h(CH, i * 0.25) for i in range(16)],
    ],
)

Pattern._PRESETS["metal"] = dict(
    name="metal",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Double kick metal pattern
        _h(K, 0.0), _h(K, 0.25), _h(K, 0.5), _h(K, 0.75),
        _h(S, 1.0), _h(K, 1.0), _h(K, 1.25), _h(K, 1.5), _h(K, 1.75),
        _h(K, 2.0), _h(K, 2.25), _h(K, 2.5), _h(K, 2.75),
        _h(S, 3.0), _h(K, 3.0), _h(K, 3.25), _h(K, 3.5), _h(K, 3.75),
        _h(CH, 0.0), _h(CH, 0.5), _h(CH, 1.0), _h(CH, 1.5),
        _h(CH, 2.0), _h(CH, 2.5), _h(CH, 3.0), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["punk"] = dict(
    name="punk",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Fast D-beat: ride on 8ths, kick+snare alternating
        _h(K, 0.0), _h(S, 0.5), _h(K, 1.0), _h(S, 1.5),
        _h(K, 2.0), _h(S, 2.5), _h(K, 3.0), _h(S, 3.5),
        _h(RD, 0.0), _h(RD, 0.5), _h(RD, 1.0), _h(RD, 1.5),
        _h(RD, 2.0), _h(RD, 2.5), _h(RD, 3.0), _h(RD, 3.5),
    ],
)

Pattern._PRESETS["disco"] = dict(
    name="disco",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Four-on-the-floor kick, open hat on upbeats
        _h(K, 0.0), _h(CH, 0.0), _h(OH, 0.5),
        _h(K, 1.0), _h(S, 1.0), _h(CH, 1.0), _h(OH, 1.5),
        _h(K, 2.0), _h(CH, 2.0), _h(OH, 2.5),
        _h(K, 3.0), _h(S, 3.0), _h(CH, 3.0), _h(OH, 3.5),
    ],
)

Pattern._PRESETS["house"] = dict(
    name="house",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Four-on-the-floor, offbeat hats, clap on 2 and 4
        _h(K, 0.0), _h(OH, 0.5),
        _h(K, 1.0), _h(DrumSound.CLAP, 1.0), _h(OH, 1.5),
        _h(K, 2.0), _h(OH, 2.5),
        _h(K, 3.0), _h(DrumSound.CLAP, 3.0), _h(OH, 3.5),
    ],
)

Pattern._PRESETS["hip hop"] = dict(
    name="hip hop",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.5),
        _h(S, 1.0), _h(CH, 1.0), _h(CH, 1.5),
        _h(CH, 2.0), _h(K, 2.25), _h(CH, 2.5),
        _h(S, 3.0), _h(CH, 3.0), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["trap"] = dict(
    name="trap",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.25), _h(CH, 0.5), _h(CH, 0.75),
        _h(DrumSound.CLAP, 1.0), _h(CH, 1.0), _h(CH, 1.25), _h(CH, 1.5),
        _h(CH, 1.75),
        _h(CH, 2.0), _h(CH, 2.25), _h(K, 2.5), _h(CH, 2.5), _h(CH, 2.75),
        _h(DrumSound.CLAP, 3.0), _h(CH, 3.0), _h(CH, 3.25), _h(CH, 3.5),
        _h(OH, 3.75),
    ],
)

Pattern._PRESETS["breakbeat"] = dict(
    name="breakbeat",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Amen break inspired
        _h(K, 0.0), _h(RD, 0.0), _h(RD, 0.5),
        _h(S, 1.0), _h(RD, 1.0), _h(K, 1.5), _h(RD, 1.5),
        _h(K, 1.75), _h(RD, 2.0),
        _h(S, 2.5), _h(RD, 2.5), _h(K, 2.75), _h(RD, 3.0),
        _h(S, 3.25), _h(RD, 3.5), _h(S, 3.5),
    ],
)

Pattern._PRESETS["drum and bass"] = dict(
    name="drum and bass",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Two-step DnB
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.25), _h(CH, 0.5), _h(CH, 0.75),
        _h(S, 1.0), _h(CH, 1.0), _h(CH, 1.25), _h(CH, 1.5), _h(CH, 1.75),
        _h(CH, 2.0), _h(K, 2.25), _h(CH, 2.25), _h(CH, 2.5), _h(CH, 2.75),
        _h(S, 3.0), _h(CH, 3.0), _h(CH, 3.25), _h(K, 3.5), _h(CH, 3.5),
        _h(CH, 3.75),
    ],
)

Pattern._PRESETS["shuffle"] = dict(
    name="shuffle",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Triplet shuffle (Texas blues feel)
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.67),
        _h(S, 1.0), _h(CH, 1.0), _h(CH, 1.67),
        _h(K, 2.0), _h(CH, 2.0), _h(CH, 2.67),
        _h(S, 3.0), _h(CH, 3.0), _h(CH, 3.67),
    ],
)

Pattern._PRESETS["motown"] = dict(
    name="motown",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare on every beat (Motown signature)
        _h(K, 0.0), _h(S, 0.0), _h(TB, 0.0), _h(TB, 0.5),
        _h(S, 1.0), _h(TB, 1.0), _h(TB, 1.5),
        _h(K, 2.0), _h(S, 2.0), _h(TB, 2.0), _h(TB, 2.5),
        _h(S, 3.0), _h(TB, 3.0), _h(TB, 3.5),
    ],
)

Pattern._PRESETS["bo diddley"] = dict(
    name="bo diddley",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # 3+3+3+3+4 shave-and-a-haircut
        _h(K, 0.0), _h(DrumSound.MARACAS, 0.0),
        _h(K, 0.75), _h(DrumSound.MARACAS, 0.75),
        _h(K, 1.5), _h(DrumSound.MARACAS, 1.5),
        _h(K, 2.25), _h(DrumSound.MARACAS, 2.25),
        _h(K, 3.0), _h(DrumSound.MARACAS, 3.0),
    ],
)

Pattern._PRESETS["afrobeat"] = dict(
    name="afrobeat",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Tony Allen-style afrobeat
        _h(K, 0.0), _h(OH, 0.0), _h(CH, 0.5),
        _h(CH, 1.0), _h(S, 1.25, 70), _h(CH, 1.5),
        _h(K, 2.0), _h(OH, 2.0), _h(CH, 2.5),
        _h(S, 3.0), _h(CH, 3.0), _h(K, 3.5, 70), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["highlife"] = dict(
    name="highlife",
    time_signature="12/8",
    beats=6.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.5), _h(CH, 1.0),
        _h(S, 1.5), _h(CH, 1.5), _h(CH, 2.0), _h(CH, 2.5),
        _h(K, 3.0), _h(CH, 3.0), _h(CH, 3.5), _h(CH, 4.0),
        _h(S, 4.5), _h(CH, 4.5), _h(CH, 5.0), _h(CH, 5.5),
    ],
)

Pattern._PRESETS["cumbia"] = dict(
    name="cumbia",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.5),
        _h(K, 1.0), _h(CH, 1.0), _h(S, 1.5),
        _h(K, 2.0), _h(CH, 2.0), _h(CH, 2.5),
        _h(K, 3.0), _h(CH, 3.0), _h(S, 3.5),
        _h(DrumSound.GUIRO, 0.0), _h(DrumSound.GUIRO, 0.5),
        _h(DrumSound.GUIRO, 1.0), _h(DrumSound.GUIRO, 1.5),
        _h(DrumSound.GUIRO, 2.0), _h(DrumSound.GUIRO, 2.5),
        _h(DrumSound.GUIRO, 3.0), _h(DrumSound.GUIRO, 3.5),
    ],
)

Pattern._PRESETS["merengue"] = dict(
    name="merengue",
    time_signature="4/4",
    beats=4.0,
    hits=[
        _h(K, 0.0), _h(TB, 0.0), _h(TB, 0.25), _h(TB, 0.5), _h(TB, 0.75),
        _h(S, 1.0), _h(TB, 1.0), _h(TB, 1.25), _h(TB, 1.5), _h(TB, 1.75),
        _h(K, 2.0), _h(TB, 2.0), _h(TB, 2.25), _h(TB, 2.5), _h(TB, 2.75),
        _h(S, 3.0), _h(TB, 3.0), _h(TB, 3.25), _h(TB, 3.5), _h(TB, 3.75),
    ],
)

Pattern._PRESETS["dancehall"] = dict(
    name="dancehall",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Steppers riddim
        _h(K, 0.0), _h(K, 1.0), _h(K, 2.0), _h(K, 3.0),
        _h(S, 1.5), _h(S, 3.5),
        _h(CH, 0.5), _h(CH, 1.5), _h(CH, 2.5), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["new orleans"] = dict(
    name="new orleans",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Swung with heavy syncopation
        _h(K, 0.0), _h(S, 0.0, 80), _h(CH, 0.0),
        _h(CH, 0.67, 70), _h(K, 1.0),
        _h(S, 1.67, 60), _h(CH, 2.0),
        _h(K, 2.67, 80), _h(S, 3.0), _h(CH, 3.0),
        _h(CH, 3.67, 70),
    ],
)

Pattern._PRESETS["linear"] = dict(
    name="linear",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # No two limbs hit simultaneously — Gadd/Weckl style
        _h(CH, 0.0), _h(K, 0.25), _h(CH, 0.5), _h(S, 0.75),
        _h(CH, 1.0), _h(K, 1.25), _h(CH, 1.5), _h(K, 1.75),
        _h(CH, 2.0), _h(K, 2.25), _h(CH, 2.5), _h(S, 2.75),
        _h(CH, 3.0), _h(K, 3.25), _h(CH, 3.5), _h(K, 3.75),
    ],
)

Pattern._PRESETS["paradiddle"] = dict(
    name="paradiddle",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # RLRR LRLL as hi-hat/snare
        _h(CH, 0.0), _h(S, 0.25), _h(CH, 0.5), _h(CH, 0.75),
        _h(S, 1.0), _h(CH, 1.25), _h(S, 1.5), _h(S, 1.75),
        _h(CH, 2.0), _h(S, 2.25), _h(CH, 2.5), _h(CH, 2.75),
        _h(S, 3.0), _h(CH, 3.25), _h(S, 3.5), _h(S, 3.75),
        _h(K, 0.0), _h(K, 1.0), _h(K, 2.0), _h(K, 3.0),
    ],
)

Pattern._PRESETS["6/8 afro-cuban"] = dict(
    name="6/8 afro-cuban",
    time_signature="6/8",
    beats=3.0,
    hits=[
        _h(CB, 0.0), _h(CB, 0.5), _h(CB, 1.0), _h(CB, 1.5), _h(CB, 2.5),
        _h(K, 0.0), _h(K, 2.0),
        _h(CGA, 0.5, 70), _h(CGB, 1.0, 80),
        _h(CGA, 2.0, 70), _h(CGB, 2.5, 80),
    ],
)

Pattern._PRESETS["bembe"] = dict(
    name="bembe",
    time_signature="6/8",
    beats=3.0,
    hits=[
        # 6/8 bell pattern — foundation of Afro-Cuban 6/8 feel
        _h(CB, 0.0), _h(CB, 0.33), _h(CB, 0.83),
        _h(CB, 1.33), _h(CB, 1.67), _h(CB, 2.17), _h(CB, 2.67),
    ],
)

Pattern._PRESETS["baiao"] = dict(
    name="baiao",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Brazilian baiao (Luiz Gonzaga)
        _h(K, 0.0), _h(TB, 0.0), _h(TB, 0.5),
        _h(TB, 1.0), _h(K, 1.5), _h(TB, 1.5),
        _h(TB, 2.0), _h(TB, 2.5),
        _h(TB, 3.0), _h(K, 3.0), _h(TB, 3.5),
        _h(S, 1.0, 80), _h(S, 3.0, 80),
    ],
)

Pattern._PRESETS["maracatu"] = dict(
    name="maracatu",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Brazilian maracatu (Recife)
        _h(K, 0.0), _h(K, 0.5), _h(S, 1.0),
        _h(K, 1.5), _h(K, 2.0), _h(S, 2.5),
        _h(K, 3.0), _h(S, 3.5),
        _h(DrumSound.AGOGO_HIGH, 0.0), _h(DrumSound.AGOGO_LOW, 0.5),
        _h(DrumSound.AGOGO_HIGH, 1.0), _h(DrumSound.AGOGO_LOW, 1.5),
        _h(DrumSound.AGOGO_HIGH, 2.0), _h(DrumSound.AGOGO_LOW, 2.5),
        _h(DrumSound.AGOGO_HIGH, 3.0), _h(DrumSound.AGOGO_LOW, 3.5),
    ],
)


class Score:
    """A sequence of notes with a time signature and tempo.

    Usage::

        score = Score("4/4", bpm=120)
        score.add(Tone.from_string("C4"), Duration.QUARTER)
        score.add(Tone.from_string("E4"), Duration.QUARTER)
        score.rest(Duration.HALF)
    """

    def __init__(self, time_signature="4/4", bpm=120):
        if isinstance(time_signature, str):
            self.time_signature = TimeSignature.from_string(time_signature)
        else:
            self.time_signature = time_signature
        self.bpm = bpm
        self.notes: list[Note] = []
        self._drum_hits: list[_Hit] = []
        self._drum_pattern_beats: float = 0.0

    def add(self, tone_or_chord, duration=Duration.QUARTER) -> "Score":
        """Add a note. Returns self for chaining."""
        self.notes.append(Note(tone=tone_or_chord, duration=duration))
        return self

    def rest(self, duration=Duration.QUARTER) -> "Score":
        """Add a rest. Returns self for chaining."""
        self.notes.append(Note(tone=None, duration=duration))
        return self

    @property
    def total_beats(self) -> float:
        note_beats = sum(n.beats for n in self.notes)
        return max(note_beats, self._drum_pattern_beats)

    @property
    def measures(self) -> float:
        """Number of measures (may be fractional if incomplete)."""
        return self.total_beats / self.time_signature.beats_per_measure

    @property
    def duration_ms(self) -> float:
        """Total duration in milliseconds."""
        ms_per_beat = 60_000 / self.bpm
        return self.total_beats * ms_per_beat

    def __len__(self):
        return len(self.notes)

    def __iter__(self):
        return iter(self.notes)

    def __repr__(self):
        return (
            f"<Score {self.time_signature} {self.bpm}bpm "
            f"{len(self.notes)} notes {self.measures:.1f} measures>"
        )

    def save_midi(self, path, velocity=100):
        """Export to Standard MIDI File, measure-aware."""
        ticks_per_beat = 480
        us_per_beat = int(60_000_000 / self.bpm)

        events = bytearray()

        # Tempo meta event
        events += _vlq(0)
        events += b"\xFF\x51\x03"
        events += struct.pack(">I", us_per_beat)[1:]

        # Time signature meta event: FF 58 04 nn dd cc bb
        ts = self.time_signature
        dd = int(math.log2(ts.unit))
        events += _vlq(0)
        events += b"\xFF\x58\x04"
        events += bytes([ts.beats, dd, 24, 8])

        accumulated_delta = 0

        for note in self.notes:
            duration_ticks = int(note.beats * ticks_per_beat)

            if note.tone is None:
                accumulated_delta += duration_ticks
                continue

            # Resolve MIDI note numbers
            if hasattr(note.tone, "tones"):
                # Chord-like object
                midi_notes = [
                    t.midi for t in note.tone.tones if t.midi is not None
                ]
            else:
                midi_val = note.tone.midi
                midi_notes = [midi_val] if midi_val is not None else []

            if not midi_notes:
                accumulated_delta += duration_ticks
                continue

            # Note On events
            for i, mn in enumerate(midi_notes):
                delta = accumulated_delta if i == 0 else 0
                events += _vlq(delta)
                events += bytes([0x90, mn & 0x7F, velocity & 0x7F])
            accumulated_delta = 0

            # Note Off events
            for i, mn in enumerate(midi_notes):
                delta = duration_ticks if i == 0 else 0
                events += _vlq(delta)
                events += bytes([0x80, mn & 0x7F, 0])

        # ── Drum hits (channel 10 = 0x99/0x89) ────────────────────────
        if self._drum_hits:
            # Sort by position, render as absolute-time events
            sorted_hits = sorted(self._drum_hits, key=lambda h: h.position)
            current_tick = 0
            for hit in sorted_hits:
                hit_tick = int(hit.position * ticks_per_beat)
                delta = max(0, hit_tick - current_tick)
                events += _vlq(delta)
                events += bytes([0x99, hit.sound.value & 0x7F,
                                 hit.velocity & 0x7F])
                # Immediate note-off (very short duration for percussion)
                events += _vlq(int(0.1 * ticks_per_beat))
                events += bytes([0x89, hit.sound.value & 0x7F, 0])
                current_tick = hit_tick + int(0.1 * ticks_per_beat)

        # End of track (flush any trailing rest delta)
        events += _vlq(accumulated_delta)
        events += b"\xFF\x2F\x00"

        with open(path, "wb") as f:
            f.write(b"MThd")
            f.write(struct.pack(">I", 6))
            f.write(struct.pack(">HHH", 0, 1, ticks_per_beat))
            f.write(b"MTrk")
            f.write(struct.pack(">I", len(events)))
            f.write(events)
