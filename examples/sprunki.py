"""Sprunki Simon Phase 1 — full arrangement.

The melody from Incredibox Sprunki's Simon Phase 1, arranged with
drums, bass, pads, and a solo section. Three-octave square wave
lead like the original.

Usage:
    python examples/sprunki.py
"""

import sounddevice as sd

from pytheory import Score, Duration, Chord
from pytheory.rhythm import DrumSound
from pytheory.play import render_score, SAMPLE_RATE


def add_melody(part, events, base_oct):
    """Add a melody phrase, inserting rests for gaps."""
    pos = 0.0
    for beat, note, dur in events:
        if beat > pos:
            part.rest(beat - pos)
        oct = base_oct
        if note.endswith("-"):
            note = note[:-1]
            oct -= 1
        part.add(f"{note}{oct}", dur, velocity=80)
        pos = beat + dur
    if pos < 8.0:
        part.rest(8.0 - pos)


def sprunki_simon():
    score = Score("4/4", bpm=200)

    # ── Drums ──
    drums = score.part("drums", synth="sine", volume=0.4)

    def beat_basic():
        drums.hit(DrumSound.KICK, Duration.QUARTER, velocity=90)
        drums.hit(DrumSound.CLOSED_HAT, Duration.QUARTER, velocity=55)
        drums.hit(DrumSound.SNARE, Duration.QUARTER, velocity=85)
        drums.hit(DrumSound.CLOSED_HAT, Duration.QUARTER, velocity=50)

    def beat_hype():
        drums.hit(DrumSound.KICK, Duration.QUARTER, velocity=100, articulation="accent")
        drums.hit(DrumSound.OPEN_HAT, Duration.QUARTER, velocity=60)
        drums.hit(DrumSound.SNARE, Duration.QUARTER, velocity=95, articulation="accent")
        drums.hit(DrumSound.CLOSED_HAT, Duration.QUARTER, velocity=55)

    def fill():
        drums.hit(DrumSound.SNARE, Duration.EIGHTH, velocity=85)
        drums.hit(DrumSound.SNARE, Duration.EIGHTH, velocity=90)
        drums.hit(DrumSound.HIGH_TOM, Duration.EIGHTH, velocity=95)
        drums.hit(DrumSound.MID_TOM, Duration.EIGHTH, velocity=100)
        drums.hit(DrumSound.LOW_TOM, Duration.EIGHTH, velocity=105)
        drums.hit(DrumSound.LOW_TOM, Duration.EIGHTH, velocity=110)
        drums.hit(DrumSound.CRASH, Duration.QUARTER, velocity=115, articulation="accent")

    # Melody phrases (beat, note, duration) — 8 beats each
    melody_A = [
        (0.0, "E", 1.0), (1.0, "G", 1.0),
        (3.5, "A", 0.5), (4.0, "B", 1.0), (5.0, "A", 1.0),
        (6.0, "G", 1.0), (7.0, "D", 1.0),
    ]
    melody_B = [
        (0.0, "E", 1.0), (1.0, "G", 1.0),
        (3.5, "A", 0.5), (4.0, "D", 2.0),
        (6.0, "B-", 1.0), (7.0, "A-", 0.5), (7.5, "D", 0.5),
    ]
    melody_C = [
        (0.0, "E", 1.0), (1.0, "G", 1.0),
        (3.5, "A", 0.5), (4.0, "B", 1.0), (5.0, "A", 1.0),
        (6.0, "G", 1.0), (7.0, "B", 1.0),
    ]
    melody_D = [
        (0.0, "A", 2.0), (2.0, "G", 1.0), (3.0, "E", 1.0),
        (4.0, "B-", 2.0), (6.0, "D", 2.0),
    ]

    # Three-octave square wave lead
    hi = score.part("hi", synth="square", envelope="pluck", volume=0.35,
                    lowpass=5000, detune=3, reverb=0.1)
    mid = score.part("mid", synth="square", envelope="pluck", volume=0.3,
                     lowpass=3500, detune=3, reverb=0.1)
    lo = score.part("lo", synth="square", envelope="pluck", volume=0.25,
                    lowpass=1500, detune=3, reverb=0.1)

    bass = score.part("bass", synth="triangle", envelope="pluck", volume=0.35,
                      lowpass=800, sub_osc=0.15)
    pad = score.part("pad", synth="supersaw", envelope="pad", volume=0.0,
                     reverb=0.3, chorus=0.15, detune=8, lowpass=3000)
    solo = score.part("solo", synth="saw", envelope="pluck", volume=0.0,
                      lowpass=4000, detune=5, delay=0.15, delay_time=0.25,
                      delay_feedback=0.2, reverb=0.15)

    bass_A = ["E2", "E2", "G2", "G2", "A2", "B2", "A2", "G2"]
    bass_B = ["E2", "E2", "G2", "A2", "D2", "D2", "B1", "D2"]

    # == INTRO (8 bars): melody alone, drums enter bar 5 ==
    for _ in range(4):
        for p in [drums, bass, pad, solo]:
            p.rest(Duration.WHOLE)
    for _ in range(4):
        beat_basic()
        for p in [bass, pad, solo]:
            p.rest(Duration.WHOLE)

    for part, oct in [(hi, 4), (mid, 3), (lo, 2)]:
        add_melody(part, melody_A, oct)
        add_melody(part, melody_B, oct)

    # == VERSE (8 bars): full band ==
    for i in range(8):
        fill() if i == 7 else beat_basic()

    for part, oct in [(hi, 4), (mid, 3), (lo, 2)]:
        add_melody(part, melody_A, oct)
        add_melody(part, melody_B, oct)

    for n in bass_A + bass_B:
        bass.add(n, Duration.WHOLE, velocity=80)
    for _ in range(32):
        pad.rest(Duration.QUARTER)
        solo.rest(Duration.QUARTER)

    # == CHORUS (8 bars): pad enters ==
    for i in range(8):
        if i in (3, 7):
            fill()
        else:
            beat_hype()

    for part, oct in [(hi, 4), (mid, 3), (lo, 2)]:
        add_melody(part, melody_C, oct)
        add_melody(part, melody_D, oct)

    for n in bass_A + ["A2", "A2", "G2", "E2", "B1", "B1", "D2", "D2"]:
        bass.add(n, Duration.WHOLE, velocity=85)

    pad.ramp(over=Duration.WHOLE * 4, curve="ease_in", volume=0.15)
    for ch in ["Em", "G", "Am", "Bm", "Am", "G", "Em", "D"]:
        pad.add(Chord.from_symbol(ch), Duration.WHOLE * 2, velocity=55)
    for _ in range(32):
        solo.rest(Duration.QUARTER)

    # == SOLO (8 bars) ==
    for i in range(8):
        fill() if i == 7 else beat_hype()

    for part, oct in [(hi, 4), (mid, 3), (lo, 2)]:
        add_melody(part, melody_A, oct)
        add_melody(part, melody_B, oct)

    for n in bass_A + bass_B:
        bass.add(n, Duration.WHOLE, velocity=85)

    for ch in ["Em", "G", "Am", "D"] * 2:
        pad.add(Chord.from_symbol(ch), Duration.WHOLE * 2, velocity=55)

    solo.ramp(over=2.0, volume=0.4)
    solo.add("B5", Duration.QUARTER, velocity=95)
    solo.add("A5", Duration.QUARTER, velocity=90)
    solo.add("G5", Duration.HALF, velocity=100, bend=0.5, bend_type="late")
    solo.add("E5", Duration.QUARTER, velocity=88)
    solo.add("G5", Duration.QUARTER, velocity=92)
    solo.add("A5", Duration.QUARTER, velocity=95)
    solo.add("B5", Duration.QUARTER, velocity=100, articulation="accent")
    solo.crescendo(["E5", "G5", "A5", "B5", "D6", "E6", "D6", "B5"],
                   Duration.QUARTER, start_vel=88, end_vel=115)
    solo.add("A5", Duration.QUARTER, velocity=105)
    solo.add("G5", Duration.QUARTER, velocity=100)
    solo.add("E5", Duration.HALF, velocity=95)
    solo.rest(Duration.WHOLE)
    solo.add("E6", Duration.EIGHTH, velocity=110, articulation="accent")
    solo.add("D6", Duration.EIGHTH, velocity=108)
    solo.add("B5", Duration.EIGHTH, velocity=105)
    solo.add("A5", Duration.EIGHTH, velocity=102)
    solo.add("G5", Duration.EIGHTH, velocity=100)
    solo.add("E5", Duration.EIGHTH, velocity=98)
    solo.add("D5", Duration.EIGHTH, velocity=95)
    solo.add("E5", Duration.EIGHTH, velocity=100)
    solo.add("G5", Duration.HALF, velocity=105, bend=1, bend_type="smooth")
    solo.add("B5", Duration.HALF, velocity=110, articulation="accent")
    solo.crescendo(["E5", "G5", "B5", "E6"], Duration.QUARTER,
                   start_vel=100, end_vel=120)
    solo.add("E6", Duration.WHOLE, velocity=127, articulation="fermata",
             bend=2, bend_type="smooth")

    # == OUTRO (4 bars): fade ==
    for _ in range(4):
        beat_basic()

    for part, oct in [(hi, 4), (mid, 3), (lo, 2)]:
        add_melody(part, melody_A, oct)

    for n in ["E2", "E2", "G2", "G2"]:
        bass.add(n, Duration.WHOLE, velocity=65)

    pad.ramp(over=Duration.WHOLE * 4, curve="ease_out", volume=0.0)
    for ch in ["Em", "G"]:
        pad.add(Chord.from_symbol(ch), Duration.WHOLE * 2, velocity=40)

    solo.ramp(over=Duration.WHOLE * 2, curve="ease_out", volume=0.0)
    solo.add("E5", Duration.WHOLE * 4, velocity=60)

    return score


if __name__ == "__main__":
    score = sprunki_simon()
    print(f"  Sprunki Simon Phase 1 — Full Arrangement")
    print(f"  {score}")
    print()
    try:
        buf = render_score(score)
        sd.play(buf, SAMPLE_RATE)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
