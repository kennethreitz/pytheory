"""Generate audio samples for documentation.

Renders code examples from the docs as WAV files so they can be
embedded as <audio> players on the website.

Usage:
    uv run python docs/generate_audio.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pytheory import Score, Duration, Key, Chord, Fretboard, DrumSound
from pytheory.play import render_score, SAMPLE_RATE

import numpy
import struct

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "_static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


def save_wav(buf, path):
    """Save a float32 buffer as 16-bit WAV."""
    # Normalize
    peak = numpy.abs(buf).max()
    if peak > 0:
        buf = buf / peak * 0.9
    samples = (buf * 32767).astype(numpy.int16)
    with open(path, "wb") as f:
        n = len(samples)
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + n * 2))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", n * 2))
        f.write(samples.tobytes())
    print(f"  {os.path.basename(path)} ({len(buf)/SAMPLE_RATE:.1f}s)")


def render(name, score):
    """Render a score to WAV in the audio directory."""
    buf = render_score(score)
    save_wav(buf, os.path.join(AUDIO_DIR, f"{name}.wav"))


# ── Piano hold (polyphonic overlap) ──────────────────────────────────────

def gen_piano_hold():
    score = Score("4/4", bpm=85)
    piano = score.part("piano", instrument="piano", reverb=0.3)
    piano.hold("C3", Duration.WHOLE * 2, velocity=60)
    piano.hold("E3", Duration.WHOLE * 2, velocity=55)
    piano.hold("G3", Duration.WHOLE * 2, velocity=55)
    for n in ["E4", "G4", "C5", "G4", "E4", "D4", "C4", "E4"]:
        piano.add(n, Duration.QUARTER, velocity=80)
    render("piano_hold", score)


# ── Articulations ────────────────────────────────────────────────────────

def gen_articulations():
    score = Score("4/4", bpm=90)
    piano = score.part("piano", instrument="piano", reverb=0.25)
    for n in ["C4", "E4", "G4", "C5"]:
        piano.add(n, Duration.QUARTER, velocity=80)
    for n in ["C4", "E4", "G4", "C5"]:
        piano.add(n, Duration.QUARTER, velocity=80, articulation="staccato")
    for n in ["C5", "G4", "E4", "C4"]:
        piano.add(n, Duration.QUARTER, velocity=80, articulation="legato")
    for n in ["C4", "E4", "G4", "C5"]:
        piano.add(n, Duration.QUARTER, velocity=80, articulation="marcato")
    render("articulations", score)


# ── Dynamic curves ───────────────────────────────────────────────────────

def gen_dynamics():
    score = Score("4/4", bpm=90)
    piano = score.part("piano", instrument="piano", reverb=0.3)
    piano.crescendo(["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"],
                    Duration.QUARTER, start_vel=30, end_vel=110)
    piano.decrescendo(["C5", "B4", "A4", "G4", "F4", "E4", "D4", "C4"],
                      Duration.QUARTER, start_vel=110, end_vel=30)
    render("dynamics", score)


# ── Filter ramp ──────────────────────────────────────────────────────────

def gen_filter_ramp():
    score = Score("4/4", bpm=130)
    score.drums("house", repeats=8, fill="house", fill_every=8)
    score.set_drum_effects(volume=0.4)
    acid = score.part("acid", synth="saw", volume=0.6,
                      lowpass=300, lowpass_q=8.0, distortion=0.3,
                      legato=True, glide=0.03)
    acid.ramp(over=Duration.WHOLE * 4, curve="ease_in", lowpass=5000)
    for _ in range(4):
        for n in ["C2", "C3", "C2", "Eb2", "C2", "G2", "Bb2", "C2"]:
            acid.add(n, Duration.EIGHTH, velocity=90)
    acid.ramp(over=Duration.WHOLE * 4, curve="ease_out", lowpass=300)
    for _ in range(4):
        for n in ["C2", "C3", "C2", "Eb2", "C2", "G2", "Bb2", "C2"]:
            acid.add(n, Duration.EIGHTH, velocity=88)
    render("filter_ramp", score)


# ── Rock beat ────────────────────────────────────────────────────────────

def gen_rock_beat():
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=4, fill="rock", fill_every=4)
    render("rock_beat", score)


# ── Bossa nova ───────────────────────────────────────────────────────────

def gen_bossa_nova():
    score = Score("4/4", bpm=140)
    score.drums("bossa nova", repeats=4)
    rhodes = score.part("rhodes", synth="fm", envelope="piano", volume=0.3,
                        reverb=0.4, reverb_decay=1.8)
    for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
        rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)
    render("bossa_nova", score)


# ── Djembe ───────────────────────────────────────────────────────────────

def gen_djembe():
    score = Score("4/4", bpm=110)
    score.drums("tiriba", repeats=4, fill="djembe call", fill_every=4)
    score.set_drum_effects(reverb=0.2)
    render("djembe", score)


# ── Tabla ────────────────────────────────────────────────────────────────

def gen_tabla():
    score = Score("4/4", bpm=80)
    score.drums("teental", repeats=2)
    score.drums("chakradar", repeats=1)
    score.set_drum_effects(reverb=0.2)
    render("tabla", score)


# ── Marching snare ───────────────────────────────────────────────────────

def gen_march_snare():
    score = Score("4/4", bpm=120)
    p = score.part("snare", synth="sine", volume=0.8, reverb=0.15)
    S = DrumSound.MARCH_SNARE
    R = DrumSound.MARCH_RIMSHOT
    C = DrumSound.MARCH_CLICK

    for _ in range(4):
        p.hit(C, Duration.QUARTER, velocity=95)

    for _ in range(4):
        p.hit(R, Duration.SIXTEENTH, velocity=118)
        p.hit(S, Duration.SIXTEENTH, velocity=30)
        p.hit(S, Duration.SIXTEENTH, velocity=32)
        p.hit(S, Duration.SIXTEENTH, velocity=28)
        p.hit(R, Duration.SIXTEENTH, velocity=115)
        p.hit(S, Duration.SIXTEENTH, velocity=30)
        p.hit(S, Duration.SIXTEENTH, velocity=28)
        p.hit(S, Duration.SIXTEENTH, velocity=32)
        p.hit(R, Duration.SIXTEENTH, velocity=118)
        p.hit(S, Duration.SIXTEENTH, velocity=35)
        p.hit(S, Duration.SIXTEENTH, velocity=28)
        p.hit(S, Duration.SIXTEENTH, velocity=30)
        p.hit(R, Duration.SIXTEENTH, velocity=120)
        p.hit(S, Duration.SIXTEENTH, velocity=30)
        p.hit(S, Duration.SIXTEENTH, velocity=28)
        p.hit(S, Duration.SIXTEENTH, velocity=32)
    render("march_snare", score)


# ── Ensemble comparison ──────────────────────────────────────────────────

def gen_ensemble():
    score = Score("4/4", bpm=120)
    S = DrumSound.MARCH_SNARE
    R = DrumSound.MARCH_RIMSHOT

    # Solo first
    solo = score.part("solo", synth="sine", volume=0.7, reverb=0.15)
    for _ in range(2):
        solo.hit(R, Duration.SIXTEENTH, velocity=118)
        solo.hit(S, Duration.SIXTEENTH, velocity=30)
        solo.hit(S, Duration.SIXTEENTH, velocity=32)
        solo.hit(S, Duration.SIXTEENTH, velocity=28)
        solo.hit(R, Duration.SIXTEENTH, velocity=115)
        solo.hit(S, Duration.SIXTEENTH, velocity=30)
        solo.hit(S, Duration.SIXTEENTH, velocity=28)
        solo.hit(S, Duration.SIXTEENTH, velocity=32)
        solo.hit(R, Duration.SIXTEENTH, velocity=118)
        solo.hit(S, Duration.SIXTEENTH, velocity=35)
        solo.hit(S, Duration.SIXTEENTH, velocity=28)
        solo.hit(S, Duration.SIXTEENTH, velocity=30)
        solo.hit(R, Duration.SIXTEENTH, velocity=120)
        solo.hit(S, Duration.SIXTEENTH, velocity=30)
        solo.hit(S, Duration.SIXTEENTH, velocity=28)
        solo.hit(S, Duration.SIXTEENTH, velocity=32)

    # Then ensemble
    line = score.part("line", synth="sine", volume=0.7, reverb=0.15, ensemble=8)
    for _ in range(8):
        line.rest(Duration.QUARTER)
    for _ in range(4):
        line.hit(R, Duration.SIXTEENTH, velocity=118)
        line.hit(S, Duration.SIXTEENTH, velocity=30)
        line.hit(S, Duration.SIXTEENTH, velocity=32)
        line.hit(S, Duration.SIXTEENTH, velocity=28)
        line.hit(R, Duration.SIXTEENTH, velocity=115)
        line.hit(S, Duration.SIXTEENTH, velocity=30)
        line.hit(S, Duration.SIXTEENTH, velocity=28)
        line.hit(S, Duration.SIXTEENTH, velocity=32)
        line.hit(R, Duration.SIXTEENTH, velocity=118)
        line.hit(S, Duration.SIXTEENTH, velocity=35)
        line.hit(S, Duration.SIXTEENTH, velocity=28)
        line.hit(S, Duration.SIXTEENTH, velocity=30)
        line.hit(R, Duration.SIXTEENTH, velocity=120)
        line.hit(S, Duration.SIXTEENTH, velocity=30)
        line.hit(S, Duration.SIXTEENTH, velocity=28)
        line.hit(S, Duration.SIXTEENTH, velocity=32)
    render("ensemble", score)


# ── Guitar strum ─────────────────────────────────────────────────────────

def gen_strum():
    score = Score("4/4", bpm=100)
    guitar = score.part("guitar", instrument="acoustic_guitar",
                        fretboard=Fretboard.guitar())
    for ch in ["G", "D", "Em", "C"] * 2:
        guitar.strum(ch, duration=Duration.WHOLE, velocity=75)
    render("strum", score)


# ── Swell ────────────────────────────────────────────────────────────────

def gen_swell():
    score = Score("4/4", bpm=80)
    strings = score.part("strings", instrument="string_ensemble",
                         reverb=0.4, ensemble=12)
    strings.swell(["C4", "D4", "E4", "F4", "G4", "F4", "E4", "D4",
                   "C4", "D4", "E4", "F4", "G4", "A4", "G4", "E4"],
                  Duration.QUARTER, low_vel=30, peak_vel=100)
    render("swell", score)


# ── Generate all ─────────────────────────────────────────────────────────

GENERATORS = [
    gen_piano_hold,
    gen_articulations,
    gen_dynamics,
    gen_filter_ramp,
    gen_rock_beat,
    gen_bossa_nova,
    gen_djembe,
    gen_tabla,
    gen_march_snare,
    gen_ensemble,
    gen_strum,
    gen_swell,
]


if __name__ == "__main__":
    print("Generating audio samples for docs...")
    print()
    for gen in GENERATORS:
        gen()
    print()
    print(f"Done. {len(GENERATORS)} files in {AUDIO_DIR}")
