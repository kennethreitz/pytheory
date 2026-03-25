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
        return sum(n.beats for n in self.notes)

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
