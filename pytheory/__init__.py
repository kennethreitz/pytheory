from math import ceil, floor

from .tones import Tone
from .systems import System, SYSTEMS
from .scales import Scale, TonedScale
from .chords import Chord, Fretboard
from .charts import CHARTS, charts_for_fretboard
try:
    from .play import play, Synth
except OSError:
    # sounddevice requires PortAudio; gracefully degrade if unavailable
    play = None
    Synth = None
