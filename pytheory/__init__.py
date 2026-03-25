"""PyTheory: Music Theory for Humans."""

__version__ = "0.11.0"

from .tones import Tone, Interval
from .systems import System, SYSTEMS
from .scales import TonedScale, Key, PROGRESSIONS
from .chords import Chord, Fretboard, analyze_progression
from .charts import CHARTS, Fingering, charts_for_fretboard

try:
    from .play import play, save, save_midi, play_progression, Synth, Envelope
except OSError:
    play = None
    save = None
    save_midi = None
    play_progression = None
    Synth = None
    Envelope = None

# Aliases for discoverability.
Note = Tone
Scale = TonedScale

__all__ = [
    "Tone", "Note", "Interval", "Scale", "TonedScale", "Key",
    "PROGRESSIONS", "Chord", "Fretboard", "Fingering", "analyze_progression",
    "System", "SYSTEMS", "CHARTS", "charts_for_fretboard",
    "play", "save", "save_midi", "play_progression", "Synth", "Envelope",
]
