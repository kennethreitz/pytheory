"""PyTheory: Music Theory for Humans."""

__version__ = "0.3.0"

from .tones import Tone
from .systems import System, SYSTEMS
from .scales import Scale, TonedScale
from .chords import Chord, Fretboard
from .charts import CHARTS, charts_for_fretboard

try:
    from .play import play, Synth
except OSError:
    play = None
    Synth = None

__all__ = [
    "Tone", "Scale", "TonedScale", "Chord", "Fretboard",
    "System", "SYSTEMS", "CHARTS", "charts_for_fretboard",
    "play", "Synth",
]
