"""PyTheory: Music Theory for Humans."""

__version__ = "0.8.0"

from .tones import Tone, Interval
from .systems import System, SYSTEMS
from .scales import TonedScale, Key, PROGRESSIONS
from .chords import Chord, Fretboard, analyze_progression
from .charts import CHARTS, Fingering, charts_for_fretboard

try:
    from .play import play, save, play_progression, Synth
except OSError:
    play = None
    save = None
    play_progression = None
    Synth = None

# Aliases for discoverability.
Note = Tone
Scale = TonedScale

__all__ = [
    "Tone", "Note", "Interval", "Scale", "TonedScale", "Key",
    "PROGRESSIONS", "Chord", "Fretboard", "Fingering", "analyze_progression",
    "System", "SYSTEMS", "CHARTS", "charts_for_fretboard",
    "play", "save", "play_progression", "Synth",
]
