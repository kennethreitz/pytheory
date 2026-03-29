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
    """Save a float32 buffer as 16-bit stereo WAV, trimming trailing silence."""
    # Trim trailing silence (below -60dB threshold)
    threshold = 0.001
    if buf.ndim == 2:
        amplitude = numpy.abs(buf).max(axis=1)
    else:
        amplitude = numpy.abs(buf)
    # Find last sample above threshold
    above = numpy.where(amplitude > threshold)[0]
    if len(above) > 0:
        # Keep 0.2s of tail after last audible sample for natural decay
        tail = min(int(SAMPLE_RATE * 0.2), len(buf) - above[-1])
        buf = buf[:above[-1] + tail]

    # Handle both mono (n,) and stereo (n, 2) buffers
    if buf.ndim == 1:
        channels = 1
        n_frames = len(buf)
    else:
        channels = buf.shape[1]
        n_frames = buf.shape[0]
    peak = numpy.abs(buf).max()
    if peak > 0:
        buf = buf / peak * 0.9
    samples = (buf * 32767).astype(numpy.int16)
    byte_rate = SAMPLE_RATE * channels * 2
    block_align = channels * 2
    data_size = n_frames * channels * 2
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, channels, SAMPLE_RATE,
                            byte_rate, block_align, 16))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(samples.tobytes())
    label = "stereo" if channels == 2 else "mono"
    print(f"  {os.path.basename(path)} ({n_frames/SAMPLE_RATE:.1f}s, {label})")


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


def gen_bossa_nova_pattern():
    score = Score("4/4", bpm=140)
    score.drums("bossa nova", repeats=4)
    render("bossa_nova_pattern", score)


def gen_salsa_pattern():
    score = Score("4/4", bpm=180)
    score.drums("salsa", repeats=4)
    render("salsa_pattern", score)


def gen_afrobeat_pattern():
    score = Score("4/4", bpm=110)
    score.drums("afrobeat", repeats=8)
    render("afrobeat_pattern", score)


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
    score.set_drum_effects(reverb=0.3, reverb_type="hall")
    render("tabla", score)


# ── Marching snare ───────────────────────────────────────────────────────

def gen_metal_blast():
    score = Score("4/4", bpm=190)
    # Showcase all metal patterns: groove → gallop → triplet fill → blast
    score.drums("metal groove", repeats=2)
    score.drums("metal gallop", repeats=4, fill="metal triplet", fill_every=4)
    score.drums("metal blast", repeats=2, fill="metal cascade", fill_every=2)
    score.drums("double kick", repeats=2, fill="metal blast", fill_every=2)
    render("metal_blast", score)


def gen_cajon():
    score = Score("4/4", bpm=100)
    score.drums("cajon", repeats=8, fill="cajon flam", fill_every=4)
    render("cajon", score)


def gen_tabla_teental():
    score = Score("4/4", bpm=160)
    score.drums("teental", repeats=3)
    score.drums("teental", repeats=1, fill="bayan", fill_every=1)
    score.set_drum_effects(reverb=0.3, reverb_type="hall")
    render("tabla_teental", score)


def gen_tabla_keherwa():
    score = Score("4/4", bpm=180)
    # Manual part so we can add ge_bend hits
    tabla = score.part("tabla", synth="sine", volume=0.5, reverb=0.3, reverb_type="hall")
    DHA = DrumSound.TABLA_DHA
    NA = DrumSound.TABLA_NA
    TIN = DrumSound.TABLA_TIN
    TIT = DrumSound.TABLA_TIT
    GE = DrumSound.TABLA_GE
    GB = DrumSound.TABLA_GE_BEND
    # Keherwa with ge_bend accents
    for _ in range(3):
        tabla.hit(DHA, Duration.EIGHTH, velocity=90, articulation="accent")
        tabla.hit(GE, Duration.EIGHTH, velocity=65)
        tabla.hit(NA, Duration.EIGHTH, velocity=72)
        tabla.hit(TIT, Duration.EIGHTH, velocity=45)
        tabla.hit(NA, Duration.EIGHTH, velocity=68)
        tabla.hit(TIT, Duration.EIGHTH, velocity=42)
        tabla.hit(DHA, Duration.EIGHTH, velocity=85, articulation="accent")
        tabla.hit(NA, Duration.EIGHTH, velocity=70)
    # Last bar with bayan bends
    tabla.hit(DHA, Duration.EIGHTH, velocity=95, articulation="marcato")
    tabla.hit(GB, Duration.EIGHTH, velocity=80)
    tabla.hit(NA, Duration.EIGHTH, velocity=72)
    tabla.hit(GB, Duration.EIGHTH, velocity=82)
    tabla.hit(DHA, Duration.EIGHTH, velocity=100, articulation="accent")
    tabla.hit(GB, Duration.EIGHTH, velocity=85)
    tabla.hit(DHA, Duration.QUARTER, velocity=110, articulation="fermata")
    render("tabla_keherwa", score)


def gen_tabla_chakradar():
    score = Score("4/4", bpm=200)
    score.drums("teental", repeats=1)
    score.drums("teental", repeats=1, fill="bayan", fill_every=1)
    score.drums("chakradar", repeats=1)
    score.set_drum_effects(reverb=0.3, reverb_type="hall")
    render("tabla_chakradar", score)


def gen_dhol():
    score = Score("4/4", bpm=160)
    score.drums("bhangra", repeats=4)
    render("dhol", score)


def gen_dholak():
    score = Score("4/4", bpm=120)
    score.drums("qawwali", repeats=4)
    render("dholak", score)


def gen_mridangam():
    score = Score("4/4", bpm=90)
    score.drums("adi talam", repeats=4)
    render("mridangam", score)


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

# ── Cookbook: Acid House ───────────────────────────────────────────────────

def gen_acid_house():
    score = Score("4/4", bpm=132)
    score.drums("house", repeats=8, fill="house", fill_every=8)
    pad = score.part("pad", synth="supersaw", envelope="pad",
                     reverb=0.4, chorus=0.3, sidechain=0.85)
    acid = score.part("acid", synth="saw", envelope="pad",
                      legato=True, glide=0.03, distortion=0.8,
                      distortion_drive=8.0, lowpass=1000, lowpass_q=5.0)
    acid.lfo("lowpass", rate=0.5, min=600, max=2500, bars=8)
    for sym in ["Cm", "Fm", "Abm", "Gm"]:
        pad.add(Chord.from_symbol(sym), Duration.WHOLE)
        pad.add(Chord.from_symbol(sym), Duration.WHOLE)
        acid.arpeggio(sym, bars=2, pattern="up", octaves=2)
    render("acid_house", score)


# ── Cookbook: Dub Reggae ──────────────────────────────────────────────────

def gen_dub_reggae():
    score = Score("4/4", bpm=72)
    score.drums("dub", repeats=8)
    melodica = score.part("melodica", synth="triangle", envelope="pluck",
                          delay=0.5, delay_time=0.66, delay_feedback=0.55,
                          reverb=0.4, reverb_type="cathedral")
    bass = score.part("bass", synth="sine", lowpass=400, lowpass_q=1.5)
    melodica.add("A4", 2).rest(6)
    melodica.add("E5", 1.5).rest(6.5)
    melodica.add("D5", 1).add("C5", 1).add("A4", 2).rest(4)
    for _ in range(16):
        bass.add("A1", Duration.HALF)
    render("dub_reggae", score)


# ── Cookbook: Jazz Ballad ─────────────────────────────────────────────────

def gen_jazz_ballad():
    score = Score("4/4", bpm=72, swing=0.5)
    score.drums("jazz", repeats=8)
    rhodes = score.part("rhodes", synth="fm", envelope="piano",
                        reverb=0.4, reverb_type="plate", humanize=0.3)
    lead = score.part("lead", synth="triangle", envelope="strings",
                      delay=0.25, reverb=0.3, humanize=0.35)
    key = Key("Bb", "major")
    for chord in key.progression("I", "vi", "ii", "V") * 2:
        rhodes.add(chord, Duration.WHOLE)
    for n, d in [("D5", 1.5), ("F5", 0.5), ("Bb5", 2), (None, 4),
                 ("A5", 1), ("G5", 1), ("F5", 2), (None, 4)]:
        lead.rest(d) if n is None else lead.add(n, d)
    render("jazz_ballad", score)


# ── Quickstart example ───────────────────────────────────────────────────

# ── Synth waveform demos ──────────────────────────────────────────────────

def _synth_demo(name, synth, envelope="none", **kwargs):
    """Short C major melody on a given synth."""
    score = Score("4/4", bpm=100)
    p = score.part("demo", synth=synth, envelope=envelope, volume=0.5,
                   reverb=0.2, **kwargs)
    for n in ["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render(f"synth_{name}", score)


def gen_synth_sine():
    _synth_demo("sine", "sine")

def gen_synth_saw():
    _synth_demo("saw", "saw")

def gen_synth_triangle():
    _synth_demo("triangle", "triangle")

def gen_synth_square():
    _synth_demo("square", "square")

def gen_synth_piano():
    score = Score("4/4", bpm=85)
    p = score.part("demo", instrument="piano", volume=0.5, reverb=0.3)
    # Hold chords with melody on top
    p.hold("C3", Duration.WHOLE * 2, velocity=60)
    p.hold("E3", Duration.WHOLE * 2, velocity=55)
    p.hold("G3", Duration.WHOLE * 2, velocity=55)
    for n in ["E4", "G4", "C5", "G4", "E4", "D4", "C4", "E4"]:
        p.add(n, Duration.QUARTER, velocity=80)
    render("synth_piano", score)

def gen_synth_acoustic_guitar():
    from pytheory import Fretboard
    score = Score("4/4", bpm=100)
    p = score.part("demo", instrument="acoustic_guitar", volume=0.5,
                   reverb=0.25, fretboard=Fretboard.guitar())
    for ch in ["G", "D", "Em", "C"]:
        p.strum(ch, Duration.WHOLE, velocity=75)
    render("synth_acoustic_guitar", score)

def gen_synth_pulse():
    _synth_demo("pulse", "pulse")

def gen_synth_noise():
    score = Score("4/4", bpm=100)
    p = score.part("demo", synth="noise", envelope="pad", volume=0.3,
                   lowpass=2000, reverb=0.3)
    p.add("C4", Duration.WHOLE * 2, velocity=80)
    render("synth_noise", score)

def gen_synth_pwm_slow():
    _synth_demo("pwm_slow", "pwm_slow", envelope="pad")

def gen_synth_pwm_fast():
    _synth_demo("pwm_fast", "pwm_fast")

def gen_synth_fm():
    score = Score("4/4", bpm=100)
    p = score.part("demo", synth="fm", envelope="bell", volume=0.5,
                   fm_ratio=3.0, fm_index=5.0, reverb=0.3)
    for n in ["C5", "E5", "G5", "C6", "G5", "E5", "C5", "E5"]:
        p.add(n, Duration.QUARTER, velocity=80)
    render("synth_fm", score)

def gen_synth_rhodes():
    score = Score("4/4", bpm=80)
    p = score.part("demo", instrument="electric_piano", volume=0.5, reverb=0.3)
    # Jazz chords with hold
    p.hold("C3", Duration.WHOLE * 2, velocity=60)
    p.hold("E3", Duration.WHOLE * 2, velocity=55)
    p.hold("Bb3", Duration.WHOLE * 2, velocity=55)
    for n in ["G4", "Bb4", "C5", "Bb4", "G4", "F4", "E4", "G4"]:
        p.add(n, Duration.QUARTER, velocity=75)
    render("synth_rhodes", score)

def gen_synth_supersaw():
    _synth_demo("supersaw", "supersaw", envelope="pad")

def gen_synth_bass_guitar():
    score = Score("4/4", bpm=100)
    p = score.part("demo", synth="bass_guitar_synth", envelope="none",
                   volume=0.5, reverb=0.2)
    for n in ["C2", "E2", "G2", "C3", "G2", "E2", "C2", "E2"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_bass_guitar", score)

def gen_synth_flute():
    _synth_demo("flute", "flute_synth", envelope="none")

def gen_synth_trumpet():
    _synth_demo("trumpet", "trumpet_synth", envelope="none")

def gen_synth_clarinet():
    _synth_demo("clarinet", "clarinet_synth", envelope="none")

def gen_synth_oboe():
    _synth_demo("oboe", "oboe_synth", envelope="none")

def gen_synth_cello():
    score = Score("4/4", bpm=70)
    p = score.part("demo", instrument="cello", volume=0.5, reverb=0.3, ensemble=3)
    for n in ["C3", "E3", "G3", "C4"]:
        p.add(n, Duration.WHOLE, velocity=80)
    render("synth_cello", score)

def gen_synth_harpsichord():
    score = Score("4/4", bpm=100)
    p = score.part("demo", synth="harpsichord_synth", envelope="none",
                   volume=0.5, reverb=0.25)
    # Baroque ornamental runs
    p.hold("C3", Duration.WHOLE, velocity=70)
    for n in ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]:
        p.add(n, Duration.EIGHTH, velocity=80)
    p.hold("G3", Duration.WHOLE, velocity=70)
    for n in ["C5", "B4", "A4", "G4", "F4", "E4", "D4", "C4"]:
        p.add(n, Duration.EIGHTH, velocity=78)
    render("synth_harpsichord", score)

def gen_synth_electric_guitar():
    from pytheory import Fretboard
    score = Score("4/4", bpm=110)
    p = score.part("demo", instrument="electric_guitar", volume=0.5,
                   reverb=0.15, fretboard=Fretboard.guitar())
    for ch in ["Am", "F", "C", "G"]:
        p.strum(ch, Duration.WHOLE, velocity=80)
    render("synth_electric_guitar", score)

def gen_synth_kalimba():
    score = Score("4/4", bpm=100)
    p = score.part("demo", instrument="kalimba", volume=0.5, reverb=0.3)
    for n in ["C5", "E5", "G5", "C6", "G5", "E5", "C5", "E5"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_kalimba", score)

def gen_synth_organ():
    _synth_demo("organ", "organ_synth", envelope="organ")

def gen_synth_marimba():
    _synth_demo("marimba", "marimba_synth", envelope="mallet")

def gen_synth_sitar():
    score = Score("4/4", bpm=80)
    p = score.part("demo", instrument="sitar", volume=0.4, reverb=0.35)
    # Drone under melody
    p.hold("C3", Duration.WHOLE * 4, velocity=55)
    for n, d in [("C4", 1.0), ("D4", 0.5), ("E4", 0.5), ("G4", 1.0),
                 ("A4", 0.5), ("G4", 0.5), ("E4", 1.0), ("D4", 0.5),
                 ("C4", 0.5), ("D4", 1.0), ("C4", 2.0)]:
        p.add(n, d, velocity=75)
    render("synth_sitar", score)


def gen_synth_harp():
    score = Score("4/4", bpm=80)
    p = score.part("demo", synth="harp_synth", envelope="none",
                   volume=0.5, reverb=0.3)
    # Arpeggiated chords with hold — harp style
    p.hold("C3", Duration.WHOLE * 2, velocity=70)
    for n in ["E4", "G4", "C5", "E5", "G5", "C5", "G4", "E4"]:
        p.add(n, Duration.QUARTER, velocity=75)
    render("synth_harp", score)

def gen_synth_upright_bass():
    score = Score("4/4", bpm=100)
    p = score.part("demo", synth="upright_bass_synth", envelope="none",
                   volume=0.5, reverb=0.2)
    for n in ["C2", "E2", "G2", "C3", "G2", "E2", "C2", "E2"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_upright_bass", score)

def gen_synth_timpani():
    score = Score("4/4", bpm=140)
    timp = score.part("timp", synth="timpani_synth", volume=0.5, reverb=0.25)
    timp.roll("C3", Duration.WHOLE, velocity_start=20, velocity_end=110, speed=0.125)
    timp.add("C3", Duration.HALF, velocity=127)
    timp.rest(Duration.HALF)
    timp.roll("G2", Duration.WHOLE, velocity_start=20, velocity_end=110, speed=0.125)
    timp.add("G2", Duration.HALF, velocity=127)
    render("synth_timpani", score)

def gen_synth_strings():
    score = Score("4/4", bpm=70)
    p = score.part("demo", synth="strings_synth", envelope="bowed",
                   volume=0.5, reverb=0.35, ensemble=8)
    for n in ["C4", "E4", "G4", "C5"]:
        p.add(n, Duration.WHOLE, velocity=75)
    render("synth_strings", score)

def gen_synth_saxophone():
    score = Score("4/4", bpm=100)
    p = score.part("demo", instrument="tenor_sax", volume=0.5, reverb=0.2)
    for n in ["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_saxophone", score)

def gen_synth_pedal_steel():
    score = Score("4/4", bpm=100)
    p = score.part("demo", instrument="pedal_steel", volume=0.5, reverb=0.3)
    for n in ["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_pedal_steel", score)

def gen_synth_theremin():
    score = Score("4/4", bpm=100)
    p = score.part("demo", instrument="theremin", volume=0.5, reverb=0.3)
    for n in ["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_theremin", score)

def gen_synth_steel_drum():
    score = Score("4/4", bpm=100)
    p = score.part("demo", instrument="steel_drum", volume=0.5, reverb=0.2)
    for n in ["C5", "E5", "G5", "C6", "G5", "E5", "C5", "E5"]:
        p.add(n, Duration.QUARTER, velocity=85)
    render("synth_steel_drum", score)

def gen_synth_accordion():
    score = Score("4/4", bpm=110)
    p = score.part("demo", instrument="accordion", volume=0.5, reverb=0.2)
    # Waltz feel with held chords
    p.hold("C3", Duration.WHOLE, velocity=65)
    p.hold("E3", Duration.WHOLE, velocity=60)
    p.hold("G3", Duration.WHOLE, velocity=60)
    for n in ["E4", "G4", "C5", "G4"]:
        p.add(n, Duration.QUARTER, velocity=78)
    p.hold("F3", Duration.WHOLE, velocity=65)
    p.hold("A3", Duration.WHOLE, velocity=60)
    p.hold("C4", Duration.WHOLE, velocity=60)
    for n in ["A4", "C5", "F5", "C5"]:
        p.add(n, Duration.QUARTER, velocity=78)
    render("synth_accordion", score)

def gen_synth_didgeridoo():
    score = Score("4/4", bpm=80)
    p = score.part("demo", instrument="didgeridoo", volume=0.5, reverb=0.3)
    p.add("C2", Duration.WHOLE * 2, velocity=85)
    render("synth_didgeridoo", score)

def gen_synth_bagpipe():
    score = Score("4/4", bpm=90)
    p = score.part("demo", instrument="bagpipe", volume=0.4, reverb=0.2)
    # Drone on low A + E (like real Highland pipes)
    p.hold("A3", Duration.WHOLE * 4, velocity=70)
    p.hold("E3", Duration.WHOLE * 4, velocity=65)
    # Chanter melody on top
    for n, d in [("A4", 1.0), ("B4", 0.5), ("C5", 0.5), ("D5", 1.0),
                 ("E5", 1.0), ("D5", 0.5), ("C5", 0.5), ("B4", 1.0),
                 ("A4", 1.0), ("G4", 1.0), ("A4", 2.0)]:
        p.add(n, d, velocity=80)
    render("synth_bagpipe", score)

def gen_synth_banjo():
    from pytheory import Fretboard
    score = Score("4/4", bpm=130)
    p = score.part("demo", instrument="banjo", volume=0.5, reverb=0.15,
                   fretboard=Fretboard.guitar())
    # Strum into a picking lick
    p.strum("G", Duration.WHOLE, velocity=80)
    p.strum("C", Duration.WHOLE, velocity=78)
    # Bluegrass lick — 16th note picking
    for n in ["G4", "B4", "D5", "G5", "D5", "B4", "A4", "G4",
              "D4", "G4", "B4", "D5", "B4", "G4", "D4", "G4"]:
        p.add(n, Duration.SIXTEENTH, velocity=82)
    render("synth_banjo", score)

def gen_synth_mandolin():
    score = Score("4/4", bpm=110)
    p = score.part("demo", instrument="mandolin", volume=0.5, reverb=0.2)
    # Tremolo rolls on held notes — the mandolin signature
    p.roll("G4", Duration.WHOLE, velocity_start=65, velocity_end=85, speed=Duration.SIXTEENTH)
    p.roll("A4", Duration.WHOLE, velocity_start=65, velocity_end=85, speed=Duration.SIXTEENTH)
    # Quick melody
    for n in ["B4", "C5", "D5", "C5", "B4", "A4", "G4", "A4"]:
        p.add(n, Duration.EIGHTH, velocity=80)
    # End on a roll
    p.roll("G4", Duration.WHOLE, velocity_start=70, velocity_end=90, speed=Duration.SIXTEENTH)
    render("synth_mandolin", score)

def gen_synth_ukulele():
    from pytheory import Fretboard
    score = Score("4/4", bpm=110)
    p = score.part("demo", instrument="ukulele", volume=0.5, reverb=0.25,
                   fretboard=Fretboard.ukulele())
    for ch in ["C", "Am", "F", "G"]:
        p.strum(ch, Duration.WHOLE, velocity=72)
    render("synth_ukulele", score)

def gen_synth_granular():
    score = Score("4/4", bpm=80)
    p = score.part("demo", instrument="granular_pad", volume=0.5, reverb=0.4)
    for n in ["C4", "E4", "G4", "C5"]:
        p.add(n, Duration.WHOLE, velocity=75)
    render("synth_granular", score)


def gen_arpeggio():
    score = Score("4/4", bpm=132)
    score.drums("house", repeats=8)
    score.set_drum_effects(volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.5,
                      lowpass=5000, detune=8, chorus=0.15, reverb=0.25,
                      delay=0.2, delay_time=0.33, delay_feedback=0.3)
    for sym in ["Cm", "Fm", "Abm", "Gm"]:
        lead.arpeggio(sym, bars=2, pattern="updown", octaves=2)
    render("arpeggio", score)


def gen_legato_glide():
    score = Score("4/4", bpm=132)
    score.drums("house", repeats=4)
    score.set_drum_effects(volume=0.35)
    acid = score.part("acid", synth="saw", volume=0.6,
                      legato=True, glide=0.04,
                      lowpass=3000, lowpass_q=6.0,
                      distortion=0.3, distortion_drive=3.0)
    acid.lfo("lowpass", rate=0.5, min=800, max=4000, bars=4)
    for _ in range(4):
        acid.add("C2", 0.25).add("C3", 0.25).add("G2", 0.25).add("C2", 0.25)
        acid.add("C2", 0.25).add("Eb2", 0.25).add("G2", 0.25).add("Bb2", 0.25)
    render("legato_glide", score)


def gen_quickstart():
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=8, fill="rock", fill_every=4)
    piano = score.part("piano", instrument="piano", reverb=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4,
                      delay=0.2, reverb=0.2, lowpass=4000)
    bass = score.part("bass", synth="triangle", lowpass=900)
    for chord in Key("G", "major").progression("I", "V", "vi", "IV") * 2:
        piano.add(chord, Duration.WHOLE)
    lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5)
    lead.add("G5", 1).add("E5", 1)
    lead.add("D5", 0.5).add("B4", 0.5).add("A4", 1)
    lead.add("G4", 2).rest(2)
    lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5)
    lead.add("G5", 1).add("A5", 1)
    lead.add("G5", 0.5).add("E5", 0.5).add("D5", 1)
    lead.add("B4", 2).rest(2)
    for n in ["G2", "G2", "D2", "D2", "E2", "E2", "C2", "C2"] * 2:
        bass.add(n, Duration.HALF)
    render("quickstart", score)


# ── Sequencing complete example (bossa nova) ─────────────────────────────

def gen_chords_basic():
    score = Score("4/4", bpm=120)
    key = Key("C", "major")
    chords = key.progression("I", "V", "vi", "IV")
    for chord in chords:
        score.add(chord, Duration.WHOLE)
    render("chords_basic", score)


def gen_complete_rock():
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=8, fill="rock", fill_every=4)
    piano = score.part("piano", instrument="piano", volume=0.4, reverb=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4,
                      delay=0.2, delay_time=0.33, reverb=0.2, lowpass=3000)
    bass = score.part("bass", synth="triangle", envelope="pluck", volume=0.45,
                      lowpass=1200)
    for chord in Key("G", "major").progression("I", "V", "vi", "IV") * 2:
        piano.add(chord, Duration.WHOLE)
    lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5)
    lead.add("G5", 1).add("E5", 1)
    lead.add("D5", 0.5).add("B4", 0.5).add("A4", 1)
    lead.add("G4", 2).rest(2)
    lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5)
    lead.add("G5", 1).add("A5", 1)
    lead.add("G5", 0.5).add("E5", 0.5).add("D5", 1)
    lead.add("B4", 2).rest(2)
    for n in ["G2", "G2", "D2", "D2", "E2", "E2", "C2", "C2"] * 2:
        bass.add(n, Duration.HALF)
    render("complete_rock", score)


# ── Drums layering (salsa) ───────────────────────────────────────────────

def gen_salsa_layered():
    score = Score("4/4", bpm=180)
    score.drums("salsa", repeats=4, fill="salsa", fill_every=4)
    pads = score.part("pads", synth="sine", envelope="pad", volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)
    for chord in Key("D", "minor").progression("ii", "V", "i", "i") * 2:
        pads.add(chord, Duration.WHOLE)
    lead.add("A5", 0.67).add("G5", 0.33).add("F5", 0.67).add("E5", 0.33)
    for n in ["D2", "A2", "D2", "F2"] * 2:
        bass.add(n, Duration.QUARTER)
    render("salsa_layered", score)


# ── Playback basic ───────────────────────────────────────────────────────

def gen_playback_basic():
    score = Score("4/4", bpm=140)
    score.drums("bossa nova", repeats=4)
    chords = score.part("chords", synth="sine", envelope="pad")
    for sym in ["Am", "Dm", "E7", "Am"]:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)
    render("playback_basic", score)


# ── Cookbook: song with sections ──────────────────────────────────────────

def gen_song_sections():
    score = Score("4/4", bpm=120)
    score.drums("rock", repeats=16, fill="rock", fill_every=4)
    chords = score.part("chords", synth="saw", envelope="pad")
    lead = score.part("lead", synth="triangle", envelope="pluck")
    score.section("verse")
    for sym in ["Am", "F", "C", "G"]:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)
    lead.add("A4", 1).add("C5", 1).add("E5", 1).rest(1)
    lead.add("F5", 1).add("E5", 1).add("C5", 2)
    score.section("chorus")
    lead.set(reverb=0.4, lowpass=5000)
    for sym in ["F", "G", "Am", "C"]:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)
    lead.add("C6", 2).add("A5", 1).add("G5", 1)
    lead.add("F5", 2).add("E5", 2)
    score.end_section()
    score.repeat("verse")
    score.repeat("chorus", times=2)
    render("song_sections", score)


GENERATORS = [
    gen_piano_hold,
    gen_articulations,
    gen_dynamics,
    gen_filter_ramp,
    gen_rock_beat,
    gen_bossa_nova_pattern,
    gen_salsa_pattern,
    gen_afrobeat_pattern,
    gen_bossa_nova,
    gen_djembe,
    gen_tabla,
    gen_metal_blast,
    gen_cajon,
    gen_tabla_teental,
    gen_tabla_keherwa,
    gen_tabla_chakradar,
    gen_dhol,
    gen_dholak,
    gen_mridangam,
    gen_march_snare,
    gen_ensemble,
    gen_strum,
    gen_swell,
    gen_synth_sine,
    gen_synth_saw,
    gen_synth_triangle,
    gen_synth_square,
    gen_synth_pulse,
    gen_synth_noise,
    gen_synth_pwm_slow,
    gen_synth_pwm_fast,
    gen_synth_fm,
    gen_synth_rhodes,
    gen_synth_supersaw,
    gen_synth_piano,
    gen_synth_bass_guitar,
    gen_synth_flute,
    gen_synth_trumpet,
    gen_synth_clarinet,
    gen_synth_oboe,
    gen_synth_cello,
    gen_synth_harpsichord,
    gen_synth_acoustic_guitar,
    gen_synth_electric_guitar,
    gen_synth_sitar,
    gen_synth_kalimba,
    gen_synth_organ,
    gen_synth_marimba,
    gen_synth_harp,
    gen_synth_upright_bass,
    gen_synth_timpani,
    gen_synth_strings,
    gen_synth_saxophone,
    gen_synth_pedal_steel,
    gen_synth_theremin,
    gen_synth_steel_drum,
    gen_synth_accordion,
    gen_synth_didgeridoo,
    gen_synth_bagpipe,
    gen_synth_banjo,
    gen_synth_mandolin,
    gen_synth_ukulele,
    gen_synth_granular,
    gen_arpeggio,
    gen_legato_glide,
    gen_acid_house,
    gen_dub_reggae,
    gen_jazz_ballad,
    gen_quickstart,
    gen_chords_basic,
    gen_complete_rock,
    gen_salsa_layered,
    gen_playback_basic,
    gen_song_sections,
]


if __name__ == "__main__":
    print("Generating audio samples for docs...")
    print()
    for gen in GENERATORS:
        gen()
    print()
    print(f"Done. {len(GENERATORS)} files in {AUDIO_DIR}")
