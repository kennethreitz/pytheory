"""PyTheory: Music Theory for Humans."""

__version__ = "0.22.0"

from .tones import Tone, Interval
from .systems import System, SYSTEMS
from .scales import TonedScale, Key, PROGRESSIONS
from .chords import Chord, Fretboard, analyze_progression
from .charts import CHARTS, Fingering, charts_for_fretboard

from .rhythm import Duration, TimeSignature, Rest, Score, Part, DrumSound, Pattern
from .rhythm import Note as RhythmNote  # rhythm.Note (tone + duration pairing)

try:
    from .play import (play, save, save_midi, play_progression, play_pattern,
                       play_score, render_score, Synth, Envelope)
except OSError:
    play = None
    save = None
    save_midi = None
    play_progression = None
    play_pattern = None
    play_score = None
    Synth = None
    Envelope = None

# Aliases for discoverability.
Note = Tone
Scale = TonedScale

__all__ = [
    "Tone", "Note", "Interval", "Scale", "TonedScale", "Key",
    "PROGRESSIONS", "Chord", "Fretboard", "Fingering", "analyze_progression",
    "System", "SYSTEMS", "CHARTS", "charts_for_fretboard",
    "play", "save", "save_midi", "play_progression", "play_pattern",
    "play_score", "Synth", "Envelope",
    "Duration", "TimeSignature", "RhythmNote", "Rest", "Score", "Part",
    "DrumSound", "Pattern",
]
