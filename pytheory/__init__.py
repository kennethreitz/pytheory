"""PyTheory: Music Theory for Humans."""

__version__ = "0.36.1"

from .tones import Tone, Interval
from .systems import System, SYSTEMS, TET
from .scales import TonedScale, Key, PROGRESSIONS
from .chords import Chord, Fretboard, analyze_progression
from .charts import CHARTS, Fingering, charts_for_fretboard

from .rhythm import Duration, TimeSignature, Rest, Score, Part, Section, DrumSound, Pattern, INSTRUMENTS
from .rhythm import Note as RhythmNote  # rhythm.Note (tone + duration pairing)

from .play import (play, save, save_midi, play_progression, play_pattern,
                   play_score, render_score, Synth, Envelope)

# Aliases for discoverability.
Note = Tone
Scale = TonedScale

__all__ = [
    "Tone", "Note", "Interval", "Scale", "TonedScale", "Key",
    "PROGRESSIONS", "Chord", "Fretboard", "Fingering", "analyze_progression",
    "System", "SYSTEMS", "TET", "CHARTS", "charts_for_fretboard",
    "play", "save", "save_midi", "play_progression", "play_pattern",
    "play_score", "Synth", "Envelope",
    "Duration", "TimeSignature", "RhythmNote", "Rest", "Score", "Part",
    "DrumSound", "Pattern", "Section", "INSTRUMENTS",
]
