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
    velocity: int = 100

    @property
    def beats(self) -> float:
        return self.duration.value


class _RawDuration:
    """A duck-typed Duration wrapper for raw float beat values."""
    __slots__ = ("value",)

    def __init__(self, beats: float):
        self.value = float(beats)

    def __repr__(self):
        return f"{self.value} beats"


def Rest(duration=Duration.QUARTER) -> Note:
    """Create a rest (silent note) with the given duration."""
    if isinstance(duration, (int, float)):
        duration = _RawDuration(duration)
    return Note(tone=None, duration=duration, velocity=0)


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
        score.add_pattern(self, repeats=repeats)
        return score

    # ── Fills ─────────────────────────────────────────────────────────

    _FILLS: dict[str, dict] = {}

    @classmethod
    def fill(cls, name: str) -> "Pattern":
        """Load a named 1-bar drum fill.

        Available fills: rock, rock crash, jazz, jazz brush, salsa, samba,
        funk, metal, blast, buildup, breakdown.

        Example::

            >>> Pattern.fill("rock")
            <Pattern 'rock fill' 4/4 4.0 beats ...>
        """
        if name not in cls._FILLS:
            raise ValueError(
                f"Unknown fill: {name!r}. "
                f"Available: {', '.join(cls.list_fills())}")
        data = cls._FILLS[name]
        return cls(**data)

    @classmethod
    def list_fills(cls) -> list[str]:
        """Return a list of all available fill names."""
        return sorted(cls._FILLS.keys())

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
HT = DrumSound.HIGH_TOM
MT = DrumSound.MID_TOM
LT = DrumSound.LOW_TOM

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

Pattern._PRESETS["country"] = dict(
    name="country",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Train beat variant: kick on 1 and 3, rimshot on 2 and 4, hats on 8ths
        _h(K, 0.0), _h(CH, 0.0), _h(CH, 0.5),
        _h(RS, 1.0), _h(CH, 1.0), _h(CH, 1.5),
        _h(K, 2.0), _h(CH, 2.0), _h(CH, 2.5),
        _h(RS, 3.0), _h(CH, 3.0), _h(CH, 3.5),
        # Ghost snare on the "and" of 4
        _h(S, 3.5, 40),
    ],
)

Pattern._PRESETS["ska"] = dict(
    name="ska",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Offbeat skank: kick on 1 and 3, snare on offbeats, hats on 8ths
        _h(K, 0.0), _h(CH, 0.0), _h(S, 0.5), _h(CH, 0.5),
        _h(CH, 1.0), _h(S, 1.5), _h(CH, 1.5),
        _h(K, 2.0), _h(CH, 2.0), _h(S, 2.5), _h(CH, 2.5),
        _h(CH, 3.0), _h(S, 3.5), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["dub"] = dict(
    name="dub",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Sparse and heavy
        _h(K, 0.0),
        _h(CH, 0.5), _h(CH, 1.5),
        _h(S, 2.0, 110),
        _h(OH, 2.5),
    ],
)

Pattern._PRESETS["jungle"] = dict(
    name="jungle",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Chopped breakbeat at double-time feel
        _h(K, 0.0), _h(K, 1.25), _h(K, 2.5),
        _h(S, 1.0), _h(S, 2.25), _h(S, 3.0), _h(S, 3.5),
        _h(RD, 0.0), _h(RD, 0.5), _h(RD, 1.0), _h(RD, 1.5),
        _h(RD, 2.0), _h(RD, 2.5), _h(RD, 3.0), _h(RD, 3.5),
    ],
)

Pattern._PRESETS["techno"] = dict(
    name="techno",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Minimal four-on-the-floor
        _h(K, 0.0), _h(K, 1.0), _h(K, 2.0), _h(K, 3.0),
        _h(CH, 0.0, 70), _h(CH, 0.5, 70), _h(CH, 1.0, 70), _h(CH, 1.5, 70),
        _h(CH, 2.0, 70), _h(CH, 2.5, 70), _h(CH, 3.0, 70), _h(CH, 3.5, 70),
        _h(OH, 0.5, 50), _h(OH, 1.5, 50), _h(OH, 2.5, 50), _h(OH, 3.5, 50),
        _h(DrumSound.CLAP, 1.0), _h(DrumSound.CLAP, 3.0),
    ],
)

Pattern._PRESETS["gospel"] = dict(
    name="gospel",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Shuffle feel with triplet hats
        _h(K, 0.0), _h(K, 2.67),
        _h(S, 1.0), _h(S, 3.0),
        _h(CH, 0.0), _h(CH, 0.67), _h(CH, 1.0), _h(CH, 1.67),
        _h(CH, 2.0), _h(CH, 2.67), _h(CH, 3.0), _h(CH, 3.67),
        # Ghost snares
        _h(S, 1.67, 35), _h(S, 3.67, 35),
    ],
)

Pattern._PRESETS["swing"] = dict(
    name="swing",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Big band swing
        _h(RD, 0.0), _h(RD, 0.67), _h(RD, 1.0), _h(RD, 1.67),
        _h(RD, 2.0), _h(RD, 2.67), _h(RD, 3.0),
        # Hi-hat foot on 2 and 4
        _h(DrumSound.PEDAL_HAT, 1.0), _h(DrumSound.PEDAL_HAT, 3.0),
        # Light kick on 1 and 3
        _h(K, 0.0, 60), _h(K, 2.0, 60),
        # Snare accent on 4
        _h(S, 3.0, 80),
    ],
)

Pattern._PRESETS["bolero"] = dict(
    name="bolero",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Slow romantic bolero
        _h(K, 0.0),
        _h(RS, 2.5), _h(RS, 3.5),
        _h(S, 2.0),
        _h(DrumSound.MARACAS, 0.0, 50), _h(DrumSound.MARACAS, 0.5, 50),
        _h(DrumSound.MARACAS, 1.0, 50), _h(DrumSound.MARACAS, 1.5, 50),
        _h(DrumSound.MARACAS, 2.0, 50), _h(DrumSound.MARACAS, 2.5, 50),
        _h(DrumSound.MARACAS, 3.0, 50), _h(DrumSound.MARACAS, 3.5, 50),
    ],
)

Pattern._PRESETS["tango"] = dict(
    name="tango",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Based on habanera rhythm
        _h(K, 0.0), _h(K, 1.5), _h(K, 2.0), _h(K, 3.0),
        _h(S, 1.0, 90), _h(S, 3.0, 90),
        _h(CH, 0.0), _h(CH, 0.5), _h(CH, 1.0), _h(CH, 1.5),
        _h(CH, 2.0), _h(CH, 2.5), _h(CH, 3.0), _h(CH, 3.5),
    ],
)

Pattern._PRESETS["flamenco"] = dict(
    name="flamenco",
    time_signature="12/8",
    beats=3.0,  # 6 eighth notes = 3 quarter beats
    hits=[
        # Palmas (clap) pattern
        _h(DrumSound.CLAP, 0.0), _h(DrumSound.CLAP, 0.5),
        _h(DrumSound.CLAP, 1.5), _h(DrumSound.CLAP, 2.0), _h(DrumSound.CLAP, 2.5),
        # Cajon low (kick) on 0 and 1.5
        _h(K, 0.0), _h(K, 1.5),
        # Cajon slap (rimshot) on 1.0 and 2.0
        _h(RS, 1.0), _h(RS, 2.0),
    ],
)

# ── Fill presets ──────────────────────────────────────────────────────────

Pattern._FILLS["rock"] = dict(
    name="rock fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Classic descending toms: high tom → mid tom → low tom → crash
        _h(HT, 0.0), _h(HT, 0.5),
        _h(MT, 1.0), _h(MT, 1.5),
        _h(LT, 2.0), _h(LT, 2.5),
        _h(CR, 3.0), _h(K, 3.0),
    ],
)

Pattern._FILLS["rock crash"] = dict(
    name="rock crash fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare buildup into crash on beat 4
        _h(S, 0.0), _h(S, 0.5),
        _h(S, 1.0), _h(S, 1.25), _h(S, 1.5), _h(S, 1.75),
        _h(S, 2.0), _h(S, 2.25), _h(S, 2.5), _h(S, 2.75),
        _h(CR, 3.0), _h(K, 3.0),
    ],
)

Pattern._FILLS["jazz"] = dict(
    name="jazz fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare press roll crescendo with ride accent
        _h(S, 0.0, 40), _h(S, 0.25, 45), _h(S, 0.5, 50), _h(S, 0.75, 55),
        _h(S, 1.0, 60), _h(S, 1.25, 65), _h(S, 1.5, 70), _h(S, 1.75, 75),
        _h(S, 2.0, 80), _h(S, 2.25, 85), _h(S, 2.5, 90), _h(S, 2.75, 95),
        _h(RD, 3.0, 110), _h(S, 3.0, 100),
    ],
)

Pattern._FILLS["jazz brush"] = dict(
    name="jazz brush fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Subtle snare ghost notes leading to ride bell
        _h(S, 0.0, 30), _h(S, 0.67, 35),
        _h(S, 1.0, 40), _h(S, 1.67, 45),
        _h(S, 2.0, 50), _h(S, 2.67, 60),
        _h(RB, 3.0, 100), _h(S, 3.0, 70),
    ],
)

Pattern._FILLS["salsa"] = dict(
    name="salsa fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Timbale cascade (high to low) with cowbell accent
        _h(TBH, 0.0), _h(TBH, 0.25), _h(TBH, 0.5), _h(TBH, 0.75),
        _h(TBH, 1.0), _h(TBL, 1.25), _h(TBL, 1.5), _h(TBL, 1.75),
        _h(TBL, 2.0), _h(TBL, 2.25), _h(TBL, 2.5), _h(TBL, 2.75),
        _h(CB, 3.0, 120), _h(CR, 3.5),
    ],
)

Pattern._FILLS["samba"] = dict(
    name="samba fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare rolls with kick accents
        _h(K, 0.0, 100), _h(S, 0.0, 80), _h(S, 0.25, 60), _h(S, 0.5, 70),
        _h(K, 1.0, 90), _h(S, 1.0, 80), _h(S, 1.25, 60), _h(S, 1.5, 70), _h(S, 1.75, 80),
        _h(K, 2.0, 100), _h(S, 2.0, 90), _h(S, 2.25, 70), _h(S, 2.5, 80), _h(S, 2.75, 90),
        _h(CR, 3.0), _h(K, 3.0),
    ],
)

Pattern._FILLS["funk"] = dict(
    name="funk fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Syncopated 16th-note snare/kick pattern ending on crash
        _h(S, 0.0), _h(K, 0.25), _h(S, 0.5), _h(S, 0.75),
        _h(K, 1.0), _h(S, 1.25), _h(K, 1.5), _h(S, 1.75),
        _h(S, 2.0), _h(K, 2.25), _h(S, 2.5), _h(K, 2.75),
        _h(S, 3.0), _h(S, 3.25), _h(K, 3.5), _h(CR, 3.75),
    ],
)

Pattern._FILLS["metal"] = dict(
    name="metal fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Double kick 16ths with descending tom pattern
        *[_h(K, i * 0.25) for i in range(16)],
        _h(HT, 0.0), _h(HT, 0.5),
        _h(MT, 1.0), _h(MT, 1.5),
        _h(LT, 2.0), _h(LT, 2.5),
        _h(CR, 3.0), _h(LT, 3.0), _h(LT, 3.5),
    ],
)

Pattern._FILLS["blast"] = dict(
    name="blast fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # All drums 16th notes building to crash
        *[_h(K, i * 0.25, 80 + i) for i in range(14)],
        *[_h(S, i * 0.25, 80 + i) for i in range(14)],
        *[_h(CH, i * 0.25, 70 + i) for i in range(14)],
        _h(CR, 3.5), _h(K, 3.5), _h(S, 3.5),
        _h(CR, 3.75), _h(K, 3.75), _h(S, 3.75),
    ],
)

Pattern._FILLS["buildup"] = dict(
    name="buildup fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare hits accelerating: quarter → eighth → 16th → crash
        # Quarter notes (beat 0)
        _h(S, 0.0),
        # Eighth notes (beat 1)
        _h(S, 1.0), _h(S, 1.5),
        # 16th notes (beats 2-3)
        _h(S, 2.0), _h(S, 2.25), _h(S, 2.5), _h(S, 2.75),
        _h(S, 3.0), _h(S, 3.25), _h(S, 3.5),
        _h(CR, 3.75), _h(K, 3.75),
    ],
)

Pattern._FILLS["breakdown"] = dict(
    name="breakdown fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Sparse: just kick on 1, silence, crash on 4+
        _h(K, 0.0, 110),
        _h(CR, 3.5), _h(K, 3.5),
    ],
)

Pattern._FILLS["reggae"] = dict(
    name="reggae fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Rimshot flams into kick+snare crash
        _h(RS, 0.0, 70), _h(RS, 0.5, 70), _h(RS, 1.0, 70), _h(RS, 1.5, 70),
        _h(K, 2.0), _h(S, 2.0),
        _h(CR, 3.5),
    ],
)

Pattern._FILLS["afrobeat"] = dict(
    name="afrobeat fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Tony Allen style: open hats, descending toms, kick, snare, crash
        _h(OH, 0.0), _h(OH, 0.5),
        _h(HT, 1.0), _h(MT, 1.5), _h(LT, 2.0),
        _h(K, 2.5), _h(S, 3.0), _h(CR, 3.75),
    ],
)

Pattern._FILLS["bossa nova"] = dict(
    name="bossa nova fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Subtle cross-stick fill
        _h(RS, 0.5, 60), _h(RS, 1.5, 60), _h(RS, 2.5, 60),
        _h(K, 3.0), _h(RB, 3.5),
    ],
)

Pattern._FILLS["house"] = dict(
    name="house fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare roll into clap with ascending velocity
        _h(S, 0.0, 40), _h(S, 0.25, 47), _h(S, 0.5, 54), _h(S, 0.75, 61),
        _h(S, 1.0, 68), _h(S, 1.25, 75), _h(S, 1.5, 82), _h(S, 1.75, 90),
        _h(DrumSound.CLAP, 2.0), _h(DrumSound.CLAP, 3.0),
        _h(K, 2.5), _h(K, 3.5),
    ],
)

Pattern._FILLS["trap"] = dict(
    name="trap fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Hi-hat roll accelerating then open hat, kick, clap
        *[_h(CH, i * 0.25, 50 + i * 4) for i in range(8)],
        _h(OH, 2.5), _h(K, 3.0), _h(DrumSound.CLAP, 3.5),
    ],
)

Pattern._FILLS["hip hop"] = dict(
    name="hip hop fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Snare + open hat stutter
        _h(S, 0.0, 80), _h(S, 0.5, 80),
        _h(OH, 1.0), _h(OH, 1.5),
        _h(K, 2.0), _h(S, 2.5),
        _h(OH, 3.0), _h(CR, 3.75),
    ],
)

Pattern._FILLS["disco"] = dict(
    name="disco fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Tom cascade with open hat
        _h(OH, 0.0), _h(HT, 0.5), _h(MT, 1.0), _h(LT, 1.5),
        _h(K, 2.0), _h(K, 2.5),
        _h(OH, 3.0), _h(CR, 3.75),
    ],
)

Pattern._FILLS["cumbia"] = dict(
    name="cumbia fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Guiro scrape accent
        _h(DrumSound.GUIRO, 0.0, 70), _h(DrumSound.GUIRO, 0.5, 70),
        _h(DrumSound.GUIRO, 1.0, 70), _h(DrumSound.GUIRO, 1.5, 70),
        _h(K, 2.0), _h(K, 2.5),
        _h(S, 3.0), _h(CR, 3.75),
    ],
)

Pattern._FILLS["highlife"] = dict(
    name="highlife fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Bell pattern variation
        _h(CB, 0.0), _h(CB, 0.5), _h(CB, 1.5), _h(CB, 2.0),
        _h(RB, 2.5), _h(RB, 3.0), _h(CR, 3.75),
    ],
)

Pattern._FILLS["second line"] = dict(
    name="second line fill",
    time_signature="4/4",
    beats=4.0,
    hits=[
        # Press roll buzz: snare at 16ths with ascending velocity
        *[_h(S, i * 0.25, 30 + int(i * 60 / 10)) for i in range(11)],
        _h(K, 3.0), _h(CR, 3.75),
    ],
)


class Part:
    """A named voice within a Score, with its own synth, envelope, and effects.

    Parts allow layering multiple instruments — lead, bass, pads, etc. —
    each with independent synth settings and effects, mixed together on playback.

    Don't instantiate directly — use ``Score.part()`` instead.

    Example::

        score = Score("4/4", bpm=140)
        lead = score.part("lead", synth="saw", envelope="pluck",
                          reverb=0.3, delay=0.25)
        lead.add("E5", Duration.QUARTER).add("D5", Duration.EIGHTH)
        bass = score.part("bass", synth="triangle", envelope="pluck")
        bass.add("A2", Duration.HALF)
    """

    def __init__(self, name: str, *, synth: str = "sine",
                 envelope: str = "piano", volume: float = 0.5,
                 reverb: float = 0.0, reverb_decay: float = 1.0,
                 reverb_type: str = "algorithmic",
                 delay: float = 0.0, delay_time: float = 0.375,
                 delay_feedback: float = 0.4,
                 lowpass: float = 0.0, lowpass_q: float = 0.707,
                 distortion: float = 0.0, distortion_drive: float = 3.0,
                 legato: bool = False, glide: float = 0.0,
                 chorus: float = 0.0, chorus_rate: float = 1.5,
                 chorus_depth: float = 0.003,
                 swing: Optional[float] = None,
                 humanize: float = 0.0,
                 sidechain: float = 0.0,
                 sidechain_release: float = 0.1,
                 detune: float = 0.0,
                 pan: float = 0.0,
                 spread: float = 0.0):
        self.name = name
        self.synth = synth
        self.envelope = envelope
        self.volume = volume
        self.swing = swing
        self.humanize = humanize
        self.sidechain = sidechain
        self.sidechain_release = sidechain_release
        self.reverb_mix = reverb
        self.reverb_decay = reverb_decay
        self.reverb_type = reverb_type
        self.delay_mix = delay
        self.delay_time = delay_time
        self.delay_feedback = delay_feedback
        self.lowpass = lowpass
        self.lowpass_q = lowpass_q
        self.distortion_mix = distortion
        self.distortion_drive = distortion_drive
        self.legato = legato
        self.glide = glide
        self.chorus_mix = chorus
        self.chorus_rate = chorus_rate
        self.chorus_depth = chorus_depth
        self.detune = detune
        self.pan = pan
        self.spread = spread
        self.notes: list[Note] = []
        self._automation: list[tuple[float, dict]] = []  # (beat, {param: value})

    def add(self, tone_or_string, duration=Duration.QUARTER, *, velocity: int = 100) -> "Part":
        """Add a note. Accepts Tone/Chord objects or note strings like ``"E5"``.

        Duration can be a ``Duration`` enum or a raw float (beats).
        Velocity controls loudness (1-127, default 100).

        Returns self for chaining.
        """
        if isinstance(tone_or_string, str):
            from .tones import Tone
            tone_or_string = Tone.from_string(tone_or_string, system="western")
        if isinstance(duration, (int, float)):
            duration = _RawDuration(duration)
        self.notes.append(Note(tone=tone_or_string, duration=duration, velocity=velocity))
        return self

    def set(self, **params) -> "Part":
        """Change effect parameters at the current beat position.

        Inserts an automation marker — from this point forward, the
        specified parameters take new values. Use this to open filters,
        add reverb, kick in distortion, or change volume mid-song.

        Args:
            **params: Any Part parameter — ``lowpass``, ``lowpass_q``,
                ``reverb``, ``reverb_decay``, ``delay``, ``delay_time``,
                ``delay_feedback``, ``distortion``, ``distortion_drive``,
                ``volume``, ``chorus``, ``chorus_rate``, ``chorus_depth``.

        Returns:
            Self for chaining.

        Example::

            >>> lead = score.part("lead", synth="saw", lowpass=800)
            >>> lead.add("C5", Duration.WHOLE)            # filtered
            >>> lead.set(lowpass=3000, reverb=0.4)        # filter opens
            >>> lead.add("E5", Duration.WHOLE)            # bright + reverb
            >>> lead.set(distortion=0.6, lowpass=1500)    # grit
            >>> lead.add("G5", Duration.WHOLE)
        """
        beat_pos = sum(n.beats for n in self.notes)
        # Map shorthand param names to internal attribute names
        param_map = {
            "reverb": "reverb_mix", "delay": "delay",
            "distortion": "distortion", "chorus": "chorus_mix",
        }
        mapped = {}
        for k, v in params.items():
            attr = param_map.get(k, k)
            # Handle the special naming conventions
            if k == "reverb":
                mapped["reverb_mix"] = v
            elif k == "delay":
                mapped["delay_mix"] = v
            elif k == "distortion":
                mapped["distortion_mix"] = v
            elif k == "chorus":
                mapped["chorus_mix"] = v
            else:
                mapped[k] = v
        self._automation.append((beat_pos, mapped))
        return self

    def _get_params_at(self, beat: float) -> dict:
        """Get the effective parameters at a given beat position."""
        # Start with initial values
        params = {
            "volume": self.volume,
            "reverb_mix": self.reverb_mix, "reverb_decay": self.reverb_decay,
            "reverb_type": self.reverb_type,
            "delay_mix": self.delay_mix, "delay_time": self.delay_time,
            "delay_feedback": self.delay_feedback,
            "lowpass": self.lowpass, "lowpass_q": self.lowpass_q,
            "distortion_mix": self.distortion_mix,
            "distortion_drive": self.distortion_drive,
            "chorus_mix": self.chorus_mix, "chorus_rate": self.chorus_rate,
            "chorus_depth": self.chorus_depth,
        }
        # Apply automation up to the given beat
        for auto_beat, changes in sorted(self._automation, key=lambda a: a[0]):
            if auto_beat <= beat:
                params.update(changes)
            else:
                break
        return params

    def _get_automation_points(self) -> list[float]:
        """Return sorted list of beat positions where parameters change."""
        points = sorted(set(beat for beat, _ in self._automation))
        return points

    def lfo(self, param: str, *, rate: float = 0.5, min: float = 0.0,
            max: float = 1.0, bars: float = 4, shape: str = "sine",
            resolution: float = 0.25) -> "Part":
        """Automate a parameter with an LFO (low-frequency oscillator).

        Generates automation points at regular intervals, sweeping a
        parameter smoothly between min and max values. This is how
        filter sweeps, tremolo, and auto-wah effects work.

        Args:
            param: Parameter name to modulate (e.g. ``"lowpass"``,
                ``"reverb"``, ``"distortion"``, ``"volume"``,
                ``"chorus"``, ``"delay"``).
            rate: LFO speed in cycles per bar (default 0.5 = one sweep
                every 2 bars). 0.25 = very slow, 1 = once per bar,
                4 = four times per bar.
            min: Minimum parameter value.
            max: Maximum parameter value.
            bars: Number of bars to run the LFO over (default 4).
            shape: Waveform shape — ``"sine"`` (smooth), ``"triangle"``
                (linear), ``"saw"`` (ramp up), ``"square"`` (on/off).
            resolution: How often to insert automation points, in beats
                (default 0.25 = every 16th note). Lower = smoother.

        Returns:
            Self for chaining.

        Example::

            >>> lead = score.part("lead", synth="saw", lowpass=400)
            >>> # Slow filter sweep: 400→3000 Hz over 8 bars
            >>> lead.lfo("lowpass", rate=0.125, min=400, max=3000, bars=8)
            >>> lead.arpeggio("Cm", bars=8, pattern="up", octaves=2)
        """
        import math

        current_beat = sum(n.beats for n in self.notes)
        beats_per_bar = 4.0  # assume 4/4
        total_beats = bars * beats_per_bar
        cycles_per_beat = rate / beats_per_bar

        beat = 0.0
        while beat < total_beats:
            # Normalized position in the LFO cycle (0-1)
            phase = (beat * cycles_per_beat) % 1.0

            # Shape the LFO
            if shape == "sine":
                # Sine: 0→1→0→-1→0 mapped to min→max→min
                value = 0.5 + 0.5 * math.sin(2 * math.pi * phase)
            elif shape == "triangle":
                # Triangle: linear up then down
                value = 2 * phase if phase < 0.5 else 2 * (1 - phase)
            elif shape == "saw":
                # Sawtooth: ramp up
                value = phase
            elif shape == "square":
                # Square: on/off
                value = 1.0 if phase < 0.5 else 0.0
            else:
                value = 0.5 + 0.5 * math.sin(2 * math.pi * phase)

            # Map 0-1 to min-max
            param_value = min + value * (max - min)

            # Insert automation point at the absolute beat position
            abs_beat = current_beat + beat

            # Map param name to internal name
            param_map = {
                "reverb": "reverb_mix", "delay": "delay_mix",
                "distortion": "distortion_mix", "chorus": "chorus_mix",
            }
            internal_name = param_map.get(param, param)
            self._automation.append((abs_beat, {internal_name: param_value}))

            beat += resolution

        return self

    def rest(self, duration=Duration.QUARTER) -> "Part":
        """Add a rest. Returns self for chaining."""
        if isinstance(duration, (int, float)):
            duration = _RawDuration(duration)
        self.notes.append(Note(tone=None, duration=duration, velocity=0))
        return self

    def fade_in(self, bars: float = 4) -> "Part":
        """Fade volume from 0 to current level over N bars."""
        beats = bars * 4.0  # assume 4/4
        current_beat = sum(n.beats for n in self.notes)
        steps = int(beats / 0.5)  # automate every half beat
        for i in range(steps + 1):
            frac = i / steps
            beat = current_beat + i * 0.5
            vol = self.volume * frac
            self._automation.append((beat, {"volume": vol}))
        return self

    def fade_out(self, bars: float = 4) -> "Part":
        """Fade volume from current level to 0 over N bars."""
        beats = bars * 4.0
        current_beat = sum(n.beats for n in self.notes)
        steps = int(beats / 0.5)
        for i in range(steps + 1):
            frac = 1.0 - (i / steps)
            beat = current_beat + i * 0.5
            vol = self.volume * frac
            self._automation.append((beat, {"volume": vol}))
        return self

    def arpeggio(self, chord, *, bars: float = 1, pattern: str = "up",
                 division=Duration.SIXTEENTH, octaves: int = 1,
                 velocity: int = 100) -> "Part":
        """Arpeggiate a chord into a rhythmic pattern.

        Takes a chord and sequences through its notes automatically,
        like a hardware arpeggiator on a synth. Combined with
        ``legato=True`` and ``glide``, this produces classic acid
        and trance arpeggiated lines.

        Args:
            chord: A Chord object (or string like ``"Am"``).
            bars: Number of bars to fill (default 1).
            pattern: Arpeggio pattern:
                - ``"up"`` — low to high, repeat
                - ``"down"`` — high to low, repeat
                - ``"updown"`` — up then down (bounce)
                - ``"downup"`` — down then up
                - ``"random"`` — random note order
            division: Note length for each step (default ``Duration.SIXTEENTH``).
            octaves: Number of octaves to span (default 1). With 2,
                the pattern repeats one octave higher before cycling.

        Returns:
            Self for chaining.

        Example::

            >>> lead = score.part("lead", synth="saw", legato=True, glide=0.03)
            >>> lead.arpeggio(Chord.from_symbol("Am"), bars=2, pattern="updown")
        """
        from .tones import Tone

        # Parse chord if string
        if isinstance(chord, str):
            from .chords import Chord as ChordClass
            chord = ChordClass.from_symbol(chord)

        # Get the pitches from the chord, sorted low to high
        tones = sorted(chord.tones, key=lambda t: t.pitch())

        # Expand across octaves
        all_tones = []
        for oct in range(octaves):
            for t in tones:
                if oct == 0:
                    all_tones.append(t)
                else:
                    all_tones.append(t.add(12 * oct))

        # Build the sequence based on pattern
        if pattern == "up":
            seq = list(all_tones)
        elif pattern == "down":
            seq = list(reversed(all_tones))
        elif pattern == "updown":
            seq = list(all_tones) + list(reversed(all_tones[1:-1]))
        elif pattern == "downup":
            seq = list(reversed(all_tones)) + list(all_tones[1:-1])
        elif pattern == "random":
            import random
            seq = list(all_tones)
            random.shuffle(seq)
        else:
            seq = list(all_tones)

        if not seq:
            return self

        # Calculate how many steps fit in the given bars
        if hasattr(division, 'value'):
            step_beats = division.value
        else:
            step_beats = float(division)

        # Get beats per bar from score's time signature if available
        total_beats = bars * 4.0  # default 4/4
        total_steps = int(total_beats / step_beats)

        # Fill the bars by cycling through the sequence
        for i in range(total_steps):
            tone = seq[i % len(seq)]
            self.add(tone, step_beats, velocity=velocity)

        return self

    @property
    def total_beats(self) -> float:
        return sum(n.beats for n in self.notes)

    def __len__(self):
        return len(self.notes)

    def __iter__(self):
        return iter(self.notes)

    def __repr__(self):
        return (f"<Part {self.name!r} synth={self.synth} "
                f"{len(self.notes)} notes {self.total_beats:.1f} beats>")


class Section:
    """A named section of a Score (verse, chorus, bridge, etc.)."""

    def __init__(self, name: str, score: "Score"):
        self.name = name
        self._score = score
        self._start_beat = score.total_beats
        # Snapshot current state
        self._part_starts: dict[str, int] = {
            n: len(p.notes) for n, p in score.parts.items()
        }
        self._default_start = len(score.notes)
        self._drum_start = len(score._drum_hits)
        self._drum_beat_start = score._drum_pattern_beats
        self._finalized = False
        self._part_notes: dict[str, list[Note]] = {}
        self._default_notes: list[Note] = []
        self._drum_hits: list[_Hit] = []
        self._drum_beat_duration: float = 0
        self._duration: float = 0

    @property
    def beats(self) -> float:
        if self._finalized:
            return self._duration
        return self._score.total_beats - self._start_beat

    def _finalize(self):
        if self._finalized:
            return
        s = self._score
        # Capture notes added since snapshot
        for pname, start_idx in self._part_starts.items():
            if pname in s.parts:
                self._part_notes[pname] = list(s.parts[pname].notes[start_idx:])
        self._default_notes = list(s.notes[self._default_start:])
        # Capture drum hits added since snapshot
        self._drum_hits = list(s._drum_hits[self._drum_start:])
        self._drum_beat_duration = s._drum_pattern_beats - self._drum_beat_start
        self._duration = s.total_beats - self._start_beat
        self._finalized = True


class Score:
    """A multi-part arrangement with drums, chords, and instrument voices.

    A Score combines:

    - **Drum patterns** via ``add_pattern()``
    - **Chord/tone notes** via ``add()`` (backwards-compatible default part)
    - **Named parts** via ``part()`` — each with its own synth and envelope

    Example::

        score = Score("4/4", bpm=140)
        score.add_pattern(Pattern.preset("bossa nova"), repeats=4)

        chords = score.part("chords", synth="sine", envelope="pad")
        lead   = score.part("lead",   synth="saw",  envelope="pluck")
        bass   = score.part("bass",   synth="triangle", envelope="pluck")

        for chord in key.progression("i", "iv", "V", "i"):
            chords.add(chord, Duration.WHOLE)

        lead.add("E5", Duration.QUARTER).add("D5", Duration.EIGHTH)
        bass.add("A2", Duration.HALF).add("D2", Duration.HALF)

        play_score(score)
    """

    def __init__(self, time_signature="4/4", bpm=120, swing: float = 0.0,
                 drum_humanize: float = 0.15):
        if isinstance(time_signature, str):
            self.time_signature = TimeSignature.from_string(time_signature)
        else:
            self.time_signature = time_signature
        self.bpm = bpm
        self.swing = swing
        self._drum_humanize = drum_humanize
        self.notes: list[Note] = []
        self.parts: dict[str, Part] = {}
        self._drum_hits: list[_Hit] = []
        self._drum_pattern_beats: float = 0.0
        self._tempo_changes: list[tuple[float, int]] = []
        self._sections: dict[str, Section] = {}
        self._current_section: Optional[Section] = None

    def part(self, name: str, *, synth: str = "sine",
             envelope: str = "piano", volume: float = 0.5,
             reverb: float = 0.0, reverb_decay: float = 1.0,
             reverb_type: str = "algorithmic",
             delay: float = 0.0, delay_time: float = 0.375,
             delay_feedback: float = 0.4,
             lowpass: float = 0.0, lowpass_q: float = 0.707,
             distortion: float = 0.0, distortion_drive: float = 3.0,
             legato: bool = False, glide: float = 0.0,
             chorus: float = 0.0, chorus_rate: float = 1.5,
             chorus_depth: float = 0.003,
             swing: Optional[float] = None,
             humanize: float = 0.0,
             sidechain: float = 0.0,
             sidechain_release: float = 0.1,
             detune: float = 0.0,
             pan: float = 0.0,
             spread: float = 0.0) -> Part:
        """Create a named part with its own synth voice and effects.

        Args:
            name: Part name (e.g. ``"lead"``, ``"bass"``, ``"pads"``).
            synth: Waveform — ``"sine"``, ``"saw"``, ``"triangle"``,
                ``"square"``, ``"pulse"``, ``"fm"``, ``"noise"``,
                ``"supersaw"``, ``"pwm_slow"``, ``"pwm_fast"``.
            envelope: ADSR preset name — ``"piano"``, ``"pluck"``,
                ``"pad"``, ``"organ"``, ``"bell"``, ``"strings"``,
                ``"staccato"``, or ``"none"``.
            volume: Mix level from 0.0 to 1.0 (default 0.5).
            reverb: Reverb wet/dry mix, 0.0–1.0 (default 0, off).
            reverb_decay: Reverb tail length in seconds (default 1.0).
            reverb_type: Reverb algorithm — ``"algorithmic"`` (Schroeder, default)
                or a convolution IR preset: ``"taj_mahal"``, ``"cathedral"``,
                ``"plate"``, ``"spring"``, ``"cave"``, ``"parking_garage"``,
                ``"canyon"``.
            delay: Delay wet/dry mix, 0.0–1.0 (default 0, off).
            delay_time: Delay time in seconds (default 0.375, dotted 8th).
            delay_feedback: Delay feedback 0.0–1.0 (default 0.4).
            lowpass: Lowpass filter cutoff in Hz (default 0, off).
                Try 800 for muffled bass, 2000 for warm lead,
                5000 for subtle brightness rolloff.
            lowpass_q: Filter resonance/Q factor (default 0.707, flat).
                Higher values add a resonant peak at the cutoff —
                1.0 = slight peak, 2.0 = pronounced, 5.0+ = aggressive.
            distortion: Distortion wet/dry mix, 0.0–1.0 (default 0, off).
            distortion_drive: Gain before soft clipping (default 3.0).
                0.5–2 = subtle warmth, 3–8 = overdrive, 10+ = fuzz.
            legato: If True, notes share a continuous waveform instead
                of retriggering the envelope on each note (default False).
            glide: Portamento time in seconds between consecutive pitches
                (default 0, instant). 0.03–0.05 = quick 303 slide,
                0.1–0.2 = slow glide.
            humanize: Random timing and velocity variation, 0.0–1.0
                (default 0, off). Adds micro-imperfections that make
                programmed parts feel like a real player.
                0.1 = subtle, 0.3 = natural, 0.5+ = loose/drunk.
            sidechain: Sidechain compression amount, 0.0–1.0 (default 0, off).
                How much the drum hits duck this part's volume.
                0.8 = typical EDM pumping effect.
            sidechain_release: How fast the volume comes back after ducking,
                in seconds (default 0.1).

        Returns:
            A :class:`Part` object. Add notes with ``.add()`` and ``.rest()``.

        Example::

            lead = score.part("lead", synth="saw", envelope="pluck",
                              reverb=0.3, delay=0.25, lowpass=3000)
        """
        p = Part(name, synth=synth, envelope=envelope, volume=volume,
                 reverb=reverb, reverb_decay=reverb_decay,
                 reverb_type=reverb_type,
                 delay=delay, delay_time=delay_time,
                 delay_feedback=delay_feedback,
                 lowpass=lowpass, lowpass_q=lowpass_q,
                 distortion=distortion, distortion_drive=distortion_drive,
                 legato=legato, glide=glide,
                 chorus=chorus, chorus_rate=chorus_rate,
                 chorus_depth=chorus_depth,
                 swing=swing, humanize=humanize,
                 sidechain=sidechain, sidechain_release=sidechain_release,
                 detune=detune, pan=pan, spread=spread)
        self.parts[name] = p
        return p

    def add_pattern(self, pattern, repeats: int = 1) -> "Score":
        """Add a drum pattern to this score.

        Args:
            pattern: A :class:`Pattern` object.
            repeats: Number of times to repeat.

        Returns:
            Self for chaining.
        """
        for r in range(repeats):
            offset = self._drum_pattern_beats + r * pattern.beats
            for hit in pattern.hits:
                self._drum_hits.append(
                    _Hit(hit.sound, hit.position + offset, hit.velocity))
        self._drum_pattern_beats += repeats * pattern.beats
        return self

    def fill(self, name: str = "rock") -> "Score":
        """Insert a 1-bar drum fill at the current position.

        Replaces what would be the next bar of drums with a genre-appropriate fill.
        """
        fill_pattern = Pattern.fill(name)
        return self.add_pattern(fill_pattern, repeats=1)

    def drums(self, preset: str, repeats: int = 4, fill: str = None,
              fill_every: int = None) -> "Score":
        """Add a drum pattern by preset name, with optional auto-fills.

        Shorthand for ``score.add_pattern(Pattern.preset(name), repeats=n)``.

        Args:
            preset: Pattern preset name (e.g. ``"bossa nova"``, ``"rock"``).
            repeats: Number of times to repeat (default 4).
            fill: Optional fill name. When provided, groove bars are
                periodically replaced with the named fill pattern.
            fill_every: Replace every Nth bar with a fill. If *fill* is
                provided but *fill_every* is not, defaults to filling only
                the last bar.

        Returns:
            Self for chaining.

        Example::

            >>> score = Score("4/4", bpm=140)
            >>> score.drums("bossa nova", repeats=4)
        """
        if fill is None:
            return self.add_pattern(Pattern.preset(preset), repeats=repeats)

        groove = Pattern.preset(preset)
        fill_pattern = Pattern.fill(fill)

        if fill_every is None:
            # Fill only the last bar
            fill_every = repeats

        for bar in range(1, repeats + 1):
            if bar % fill_every == 0:
                self.add_pattern(fill_pattern, repeats=1)
            else:
                self.add_pattern(groove, repeats=1)
        return self

    def add(self, tone_or_chord, duration=Duration.QUARTER) -> "Score":
        """Add a note to the default (unnamed) part.

        For simple scores without named parts. Returns self for chaining.
        """
        self.notes.append(Note(tone=tone_or_chord, duration=duration))
        return self

    def rest(self, duration=Duration.QUARTER) -> "Score":
        """Add a rest to the default part. Returns self for chaining."""
        self.notes.append(Note(tone=None, duration=duration))
        return self

    def set_tempo(self, bpm: int) -> "Score":
        """Insert a tempo change at the current beat position.

        The new tempo takes effect from the current total_beats position
        and remains until the next tempo change.

        Args:
            bpm: New tempo in beats per minute.

        Returns:
            Self for chaining.
        """
        self._tempo_changes.append((self.total_beats, bpm))
        return self

    def section(self, name: str) -> "Section":
        """Begin a named section. Everything added after this call until
        the next section() or end_section() belongs to this section.

        Example::

            score.section("verse")
            chords.add(chord, Duration.WHOLE)
            lead.add("C5", Duration.QUARTER)

            score.section("chorus")
            chords.add(chord, Duration.WHOLE)

            score.repeat("verse")
            score.repeat("chorus", times=2)
        """
        # Finalize the previous section if any
        if self._current_section is not None:
            self._current_section._finalize()
        sec = Section(name, self)
        self._sections[name] = sec
        self._current_section = sec
        return sec

    def end_section(self) -> "Score":
        """Close the current section explicitly.

        Returns:
            Self for chaining.
        """
        if self._current_section is not None:
            self._current_section._finalize()
            self._current_section = None
        return self

    def repeat(self, name: str, times: int = 1) -> "Score":
        """Repeat a previously defined section.

        Copies all notes, drum hits, and automation from the named section
        and appends them at the current position.

        Args:
            name: Name of a section defined with ``section()``.
            times: Number of times to repeat (default 1).

        Returns:
            Self for chaining.
        """
        if name not in self._sections:
            raise ValueError(f"Unknown section: {name!r}")
        sec = self._sections[name]
        # Ensure section is finalized
        if not sec._finalized:
            sec._finalize()
        for _ in range(times):
            # Copy notes to each part
            for pname, notes in sec._part_notes.items():
                if pname in self.parts:
                    for note in notes:
                        self.parts[pname].notes.append(
                            Note(tone=note.tone, duration=note.duration,
                                 velocity=note.velocity))
            # Copy default notes
            for note in sec._default_notes:
                self.notes.append(
                    Note(tone=note.tone, duration=note.duration,
                         velocity=note.velocity))
            # Copy drum hits with offset
            if sec._drum_hits:
                offset = self._drum_pattern_beats - sec._drum_beat_start
                for hit in sec._drum_hits:
                    self._drum_hits.append(
                        _Hit(hit.sound, hit.position + offset, hit.velocity))
                self._drum_pattern_beats += sec._drum_beat_duration
        return self

    @property
    def total_beats(self) -> float:
        beats = [sum(n.beats for n in self.notes), self._drum_pattern_beats]
        for p in self.parts.values():
            beats.append(p.total_beats)
        return max(beats) if beats else 0.0

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
        return len(self.notes) + sum(len(p) for p in self.parts.values())

    def __iter__(self):
        return iter(self.notes)

    def __repr__(self):
        part_info = ""
        if self.parts:
            part_info = f" {len(self.parts)} parts"
        return (
            f"<Score {self.time_signature} {self.bpm}bpm"
            f"{part_info} {self.measures:.1f} measures>"
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
