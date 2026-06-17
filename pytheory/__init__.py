"""PyTheory: Music Theory for Humans."""

__version__ = "0.54.0"

from .tones import Tone, Interval
from .systems import System, SYSTEMS, TET
from .scales import TonedScale, Key, PROGRESSIONS
from .ragas import Raga
from .chords import (Chord, Fretboard, analyze_progression,
                     detect_secondary_dominant, detect_cadence, find_cadences,
                     check_voice_leading,
                     analyze_non_chord_tones, chord_scales, chord_scale_notes,
                     avoid_notes, reharmonize, reharmonize_progression)
from .charts import CHARTS, Fingering, charts_for_fretboard
from .serialism import ToneRow

from .rhythm import Duration, TimeSignature, Rest, Score, Part, Section, DrumSound, Pattern, Hit, INSTRUMENTS
from .rhythm import Note as RhythmNote  # rhythm.Note (tone + duration pairing)

from .play import (play, save, save_midi, play_progression, play_pattern,
                   play_score, render_score, Synth, Envelope)

# Aliases for discoverability.
Note = Tone
Scale = TonedScale

__all__ = [
    "Tone", "Note", "Interval", "Scale", "TonedScale", "Key",
    "PROGRESSIONS", "Raga", "Chord", "Fretboard", "Fingering", "analyze_progression",
    "detect_secondary_dominant", "detect_cadence", "find_cadences", "check_voice_leading",
    "analyze_non_chord_tones", "chord_scales", "chord_scale_notes",
    "avoid_notes", "reharmonize", "reharmonize_progression", "ToneRow",
    "System", "SYSTEMS", "TET", "CHARTS", "charts_for_fretboard",
    "play", "save", "save_midi", "play_progression", "play_pattern",
    "play_score", "render_score", "Synth", "Envelope",
    "Duration", "TimeSignature", "RhythmNote", "Rest", "Score", "Part",
    "DrumSound", "Pattern", "Hit", "Section", "INSTRUMENTS",
]
