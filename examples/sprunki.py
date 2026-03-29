"""Sprunki Simon Phase 1 — melody reference.

Notes transcribed from MIDI. Use as a base for arrangements.

Usage:
    python examples/sprunki.py
"""

import sounddevice as sd

from pytheory import Score, Duration
from pytheory.play import render_score, SAMPLE_RATE


def sprunki_simon():
    score = Score("4/4", bpm=200)

    lead = score.part("lead", synth="square", envelope="pluck", volume=0.5,
                      lowpass=4500, detune=3, reverb=0.1)

    # Phrase A
    lead.add("E4", 1.0)
    lead.add("G4", 1.0)
    lead.rest(1.5)
    lead.add("A4", 0.5)
    lead.add("B4", 1.0)
    lead.add("A4", 1.0)
    lead.add("G4", 1.0)
    lead.add("D4", 1.0)

    # Phrase B
    lead.add("E4", 1.0)
    lead.add("G4", 1.0)
    lead.rest(1.5)
    lead.add("A4", 0.5)
    lead.add("D4", 2.0)
    lead.add("B3", 1.0)
    lead.add("A3", 0.5)
    lead.add("D4", 0.5)

    # Phrase C
    lead.add("E4", 1.0)
    lead.add("G4", 1.0)
    lead.rest(1.5)
    lead.add("A4", 0.5)
    lead.add("B4", 1.0)
    lead.add("A4", 1.0)
    lead.add("G4", 1.0)
    lead.add("B4", 1.0)

    # Phrase D
    lead.add("A4", 2.0)
    lead.add("G4", 1.0)
    lead.add("E4", 1.0)
    lead.add("B3", 2.0)
    lead.add("D4", 2.0)

    return score


if __name__ == "__main__":
    score = sprunki_simon()
    print("  Sprunki Simon Phase 1")
    try:
        buf = render_score(score)
        sd.play(buf, SAMPLE_RATE)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
