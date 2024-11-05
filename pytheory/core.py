from math import ceil, floor

from .tones import Tone
from .systems import System, SYSTEMS
from .scales import Scale, TonedScale
from .chords import Chord, Fretboard
from .charts import CHARTS, charts_for_fretboard
from .play import play, Synth
