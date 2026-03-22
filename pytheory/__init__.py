"""PyTheory: Music Theory for Humans."""

__version__ = "0.4.1"

from .tones import Tone, Interval
from .systems import System, SYSTEMS
from .scales import Scale, TonedScale, Key, PROGRESSIONS
from .chords import Chord, Fretboard, analyze_progression
from .charts import CHARTS, charts_for_fretboard

try:
    from .play import play, Synth
except OSError:
    play = None
    Synth = None

# Aliases for discoverability.
Note = Tone

__all__ = [
    "Tone", "Note", "Interval", "Scale", "TonedScale", "Key",
    "PROGRESSIONS", "Chord", "Fretboard", "analyze_progression",
    "System", "SYSTEMS", "CHARTS", "charts_for_fretboard",
    "play", "Synth",
]
