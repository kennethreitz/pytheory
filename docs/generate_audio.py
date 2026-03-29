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
    """Save a float32 buffer as 16-bit stereo WAV."""
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
    score.set_drum_effects(reverb=0.2)
    render("tabla", score)


# ── Marching snare ───────────────────────────────────────────────────────

def gen_metal_blast():
    score = Score("4/4", bpm=200)
    score.drums("metal blast", repeats=8, fill="metal cascade", fill_every=4)
    render("metal_blast", score)


def gen_cajon():
    score = Score("4/4", bpm=100)
    score.drums("cajon", repeats=8, fill="cajon flam", fill_every=4)
    render("cajon", score)


def gen_tabla_teental():
    score = Score("4/4", bpm=160)
    score.drums("teental", repeats=4)
    score.set_drum_effects(reverb=0.2)
    render("tabla_teental", score)


def gen_tabla_keherwa():
    score = Score("4/4", bpm=180)
    score.drums("keherwa", repeats=4, fill="chakkardar", fill_every=4)
    score.set_drum_effects(reverb=0.2)
    render("tabla_keherwa", score)


def gen_tabla_chakradar():
    score = Score("4/4", bpm=200)
    score.drums("teental", repeats=2)
    score.drums("chakradar", repeats=1)
    score.set_drum_effects(reverb=0.2)
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

def gen_quickstart():
    score = Score("4/4", bpm=140)
    score.drums("bossa nova", repeats=4)
    chords = score.part("chords", synth="sine", envelope="pad",
                        reverb=0.4, volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      lowpass=2000, lowpass_q=3.0, distortion=0.8,
                      legato=True, glide=0.03, volume=0.4)
    bass = score.part("bass", synth="sine", lowpass=500)
    key = Key("A", "minor")
    for chord in key.progression("i", "iv", "V", "i"):
        chords.add(chord, Duration.WHOLE)
        chords.add(chord, Duration.WHOLE)
    lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)
    lead.arpeggio("Dm", bars=2, pattern="updown", octaves=2)
    lead.set(lowpass=5000, reverb=0.3)
    lead.arpeggio("E7", bars=2, pattern="up", octaves=2)
    lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)
    for n in ["A2", "E2", "A2", "C3"] * 4:
        bass.add(n, Duration.QUARTER)
    render("quickstart", score)


# ── Sequencing complete example (bossa nova) ─────────────────────────────

def gen_sequencing_bossa():
    score = Score("4/4", bpm=140)
    score.drums("bossa nova", repeats=4)
    rhodes = score.part("rhodes", synth="fm", envelope="piano", volume=0.3,
                        reverb=0.4, reverb_decay=1.8)
    lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.45,
                      delay=0.25, delay_time=0.32, delay_feedback=0.35, reverb=0.2)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45,
                      lowpass=600)
    for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
        rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)
    for n, d in [("E5", 0.67), ("D5", 0.33), ("C5", 0.67), ("B4", 0.33),
                 ("A4", 1), ("C5", 0.67), ("E5", 0.33), ("D5", 0.67),
                 ("C5", 0.33), ("A4", 1)]:
        lead.add(n, d)
    for n in ["A2", "E2", "A2", "C3", "D2", "A2", "D2", "F2"]:
        bass.add(n, Duration.QUARTER)
    render("sequencing_bossa", score)


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
    gen_acid_house,
    gen_dub_reggae,
    gen_jazz_ballad,
    gen_quickstart,
    gen_sequencing_bossa,
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
