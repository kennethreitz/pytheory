"""Play songs with PyTheory — drums, chords, bass, leads, and effects.

Requires PortAudio: brew install portaudio (macOS)

Each song showcases the full Score API:
- 58 drum pattern presets with genre-matched fills
- 10 synth waveforms (sine, saw, triangle, square, pulse, FM, noise, supersaw, PWM slow/fast)
- 8 ADSR envelope presets
- Per-part effects: reverb, delay, lowpass filter with resonance
- Named parts with independent voices mixed together

Usage:
    python examples/song.py
"""

import sounddevice as sd

from pytheory import Chord, Key, Pattern, Duration, Score, Tone, TonedScale, SYSTEMS
from pytheory.rhythm import DrumSound, _Hit
from pytheory.play import render_score, SAMPLE_RATE


def play_song(score, label=""):
    """Render and play. Ctrl-C to skip."""
    if label:
        print(f"  {label}")
    print(f"  {score}")
    print()
    try:
        buf = render_score(score)
        sd.play(buf, SAMPLE_RATE)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
        print("  (skipped)")


# ── Songs ──────────────────────────────────────────────────────────────────

def bossa_nova_girl():
    """Bossa nova in A minor — Ipanema vibes with reverb-washed chords."""
    print("  Bossa Nova in A minor")
    print("  bossa nova drums | FM rhodes + reverb | triangle lead + delay")
    print("  sine bass + LP 600Hz")

    score = Score("4/4", bpm=140)
    score.drums("bossa nova", repeats=4)

    rhodes = score.part("rhodes", instrument="electric_piano",
                        volume=0.3, pan=-0.3,
                        reverb=0.4, reverb_decay=1.8, reverb_type="plate")
    lead = score.part("lead", instrument="flute",
                      volume=0.45, pan=0.3,
                      delay=0.25, delay_time=0.32, delay_feedback=0.35,
                      reverb=0.2, reverb_type="plate")
    bass = score.part("bass", instrument="upright_bass",
                      volume=0.45, pan=0.0, lowpass=600)

    for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
        rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("E5",.67),("D5",.33),("C5",.67),("B4",.33),("A4",1),("C5",.67),("E5",.33),
        ("D5",.67),("C5",.33),("A4",1),(None,1),
        ("F5",.67),("E5",.33),("D5",.67),("C5",.33),("D5",1),("F5",.67),("A5",.33),
        ("G5",.67),("F5",.33),("D5",1),(None,1),
        ("G#5",.67),("F5",.33),("E5",.67),("D5",.33),("E5",1),(None,.5),("B4",.5),
        ("D5",.67),("E5",.33),("G#4",1),(None,1),
        ("A4",1),("C5",.67),("E5",.33),("A5",1.5),(None,.5),
        ("G5",.67),("E5",.33),("C5",.67),("A4",.33),("A4",2),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["A2","E2","A2","C3","D2","A2","D2","F2",
              "E2","B2","E2","G#2","A2","E2","A2","C3",
              "A2","E2","A2","C3","D2","A2","D2","F2",
              "E2","B2","E2","G#2","A2","E2","A2","A2"]:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def bebop_in_bb():
    """Bebop in Bb — horn lead over rhythm changes with walking bass."""
    print("  Bebop in Bb major")
    print("  bebop drums + fill | saw lead + LP 4kHz | FM rhodes + reverb")

    score = Score("4/4", bpm=160)
    score.drums("bebop", repeats=8, fill="jazz", fill_every=8)

    rhodes = score.part("rhodes", instrument="electric_piano",
                        volume=0.25, pan=-0.3,
                        reverb=0.35, reverb_decay=1.2, reverb_type="plate")
    lead = score.part("lead", instrument="trumpet",
                      volume=0.4, pan=0.25,
                      lowpass=4000, lowpass_q=1.1,
                      delay=0.15, delay_time=0.19, delay_feedback=0.25,
                      reverb=0.15, reverb_type="plate")
    bass = score.part("bass", instrument="upright_bass",
                      volume=0.4, pan=0.0, lowpass=500)

    for sym in ["Bb", "Gm", "Cm", "F7"] * 2:
        rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("Bb4",.67),("D5",.33),("F5",.67),("D5",.33),
        ("Bb4",.67),("C5",.33),("D5",.67),("F5",.33),
        ("G5",.67),("F5",.33),("D5",.67),("Bb4",.33),
        ("A4",.67),("Bb4",.33),("D5",.67),("G4",.33),
        ("C5",.67),("Eb5",.33),("G5",.67),("Eb5",.33),
        ("C5",.67),("D5",.33),("Eb5",.67),("F5",.33),
        ("A5",.67),("G5",.33),("F5",.67),("Eb5",.33),
        ("D5",.67),("C5",.33),("A4",.5),(None,.5),
        ("Bb4",1),("D5",.67),("F5",.33),
        ("G5",.67),("F5",.33),("D5",.67),("Bb4",.33),
        ("Bb5",.67),("A5",.33),("G5",.67),("F5",.33),
        ("Eb5",.67),("D5",.33),("Bb4",.67),("G4",.33),
        ("C5",.5),(None,.5),("Eb5",.67),("G5",.33),
        ("F5",.67),("Eb5",.33),("D5",.67),("C5",.33),
        ("A4",.67),("C5",.33),("Eb5",.67),("F5",.33),
        ("G5",.67),("A5",.33),("Bb5",1),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["Bb2","D3","F3","A3","G3","F3","D3","Bb2",
              "C3","Eb3","G3","Bb3","F3","A3","C4","Eb3",
              "Bb2","D3","F3","A3","G3","F3","D3","Bb2",
              "C3","Eb3","G3","Bb3","F3","C3","F2","F3"]:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def salsa_descarga():
    """Salsa descarga in D minor — clave-driven with timbale lead."""
    print("  Salsa Descarga in D minor")
    print("  salsa drums + fill | saw lead + delay | pulse bass + LP 500Hz")

    score = Score("4/4", bpm=180)
    score.drums("salsa", repeats=8, fill="salsa", fill_every=4)

    pads = score.part("pads", synth="pwm_slow", envelope="pad",
                      volume=0.2, pan=-0.35,
                      reverb=0.3, reverb_type="plate", lowpass=2000,
                      detune=10, humanize=0.2)
    lead = score.part("lead", instrument="trumpet",
                      volume=0.4, pan=0.3,
                      delay=0.2, delay_time=0.167, delay_feedback=0.3,
                      reverb=0.15, reverb_type="plate")
    bass = score.part("bass", instrument="synth_bass",
                      volume=0.45, pan=0.0, lowpass=500, lowpass_q=1.3)

    for sym in ["Em7b5", "A7", "Dm7", "Bbmaj7"] * 2:
        pads.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("E5",.67),("G5",.33),("Bb5",.67),("A5",.33),
        ("G5",.67),("F5",.33),("E5",.67),("D5",.33),
        ("C#5",.67),("D5",.33),("E5",.67),("G5",.33),
        ("F5",.67),("E5",.33),("C#5",.5),(None,.5),
        ("D5",.5),(None,.17),("F5",.67),("A5",.33),
        ("G5",.67),("F5",.33),("E5",.67),("D5",.33),
        ("Bb4",1),("D5",.67),("F5",.33),("A5",1),(None,1),
        ("E5",.5),("F5",.5),("G5",.67),("A5",.33),
        ("Bb5",.67),("A5",.33),("G5",.67),("E5",.33),
        ("C#5",.67),("E5",.33),("A5",.67),("G5",.33),
        ("F5",.67),("E5",.33),("C#5",.67),("A4",.33),
        ("D5",1),("F5",.67),("A5",.33),("G5",.67),("F5",.33),("D5",1),(None,1),
        ("Bb4",.67),("D5",.33),("F5",.67),("Bb5",.33),("A5",1.5),(None,.5),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["E2","E3","A2","A3","D2","D3","Bb2","Bb3"] * 4:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def afrobeat_groove():
    """Afrobeat in E minor — Fela-inspired hypnotic groove."""
    print("  Afrobeat in E minor")
    print("  afrobeat drums + fill | saw lead + LP 3kHz | supersaw pads + reverb")

    score = Score("4/4", bpm=115)
    score.drums("afrobeat", repeats=8, fill="afrobeat", fill_every=8)

    pads = score.part("pads", instrument="synth_pad",
                      volume=0.2, pan=-0.3,
                      reverb=0.4, reverb_decay=2.0, reverb_type="cathedral",
                      lowpass=3000)
    lead = score.part("lead", instrument="trumpet",
                      volume=0.4, pan=0.3,
                      lowpass=3000, lowpass_q=1.0,
                      delay=0.2, delay_time=0.26, delay_feedback=0.3,
                      reverb=0.15, reverb_type="plate")
    bass = score.part("bass", instrument="bass_guitar",
                      volume=0.5, pan=0.0, lowpass=500)

    for sym in ["Em", "Am", "D", "C"] * 2:
        pads.add(Chord.from_symbol(sym), Duration.WHOLE)

    riff = [("E5",.5),("G5",.5),("A5",.5),("G5",.5),
            ("E5",.5),("D5",.5),("E5",1),
            ("E5",.5),("G5",.5),("A5",.5),("B5",.5),
            ("A5",.5),("G5",.5),("E5",1),
            (None,.5),("A5",.5),("G5",.5),("E5",.5),
            ("D5",1),("E5",.5),("G5",.5),
            ("A5",.5),("B5",.5),("A5",.5),("G5",.5),
            ("E5",1.5),(None,.5)]
    for n, d in riff * 2:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["E2","E2","G2","A2","A2","G2","E2","D2",
              "D2","D2","F#2","A2","C3","C3","B2","G2"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def reggae_one_drop():
    """Reggae one-drop in G major — roots vibes with dub effects."""
    print("  Reggae One-Drop in G major")
    print("  reggae drums + fill | triangle lead + delay + reverb")
    print("  square chords + reverb | sine bass + LP 400Hz")

    score = Score("4/4", bpm=80)
    score.drums("reggae", repeats=8, fill="reggae", fill_every=8)

    chords = score.part("chords", synth="square", envelope="staccato",
                        volume=0.2, pan=-0.4,
                        reverb=0.5, reverb_decay=2.0, reverb_type="cathedral",
                        lowpass=2000, detune=8,
                        humanize=0.2)
    lead = score.part("lead", instrument="flute",
                      volume=0.4, pan=0.3,
                      delay=0.35, delay_time=0.5625, delay_feedback=0.45,
                      reverb=0.3, reverb_type="cathedral")
    bass = score.part("bass", instrument="bass_guitar",
                      volume=0.55, pan=0.0, lowpass=400, lowpass_q=1.3)

    for sym in ["G", "C", "D", "C"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("G5",1.5),(None,.5),("B5",1),("A5",1),
        ("G5",2),("E5",1),("D5",1),
        ("C5",1.5),(None,.5),("E5",1),("G5",1),
        ("A5",1.5),(None,.5),("G5",2),
        ("D5",1.5),(None,.5),("E5",1),("G5",1),
        ("A5",2),("B5",1),("A5",1),
        ("G5",1.5),(None,.5),("E5",1),("D5",1),
        ("G4",3),(None,1),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["G2","G2","B2","D3","C3","C3","E3","G3",
              "D3","D3","F#3","A3","C3","C3","E3","G3",
              "G2","G2","B2","D3","C3","C3","E3","G3",
              "D3","D3","F#3","A3","C3","G2","C3","D3"]:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def funk_workout():
    """Funk in E minor — syncopated 16ths with filtered everything."""
    print("  Funk Workout in E minor")
    print("  funk drums + fill | saw lead + LP 3.5kHz Q=1.5 | pulse bass")

    score = Score("4/4", bpm=100)
    score.drums("funk", repeats=8, fill="funk", fill_every=4)

    chords = score.part("chords", synth="square", envelope="staccato",
                        volume=0.25, pan=-0.4,
                        lowpass=2500, reverb=0.15, reverb_type="plate",
                        sidechain=0.4, humanize=0.2)
    lead = score.part("lead", instrument="synth_lead",
                      volume=0.4, pan=0.35,
                      lowpass=3500, lowpass_q=1.5,
                      delay=0.15, delay_time=0.15, delay_feedback=0.25,
                      reverb=0.1, reverb_type="plate")
    bass = score.part("bass", instrument="synth_bass",
                      volume=0.5, pan=0.0, lowpass=600, lowpass_q=1.2)

    for sym in ["Em", "Am", "D", "B7"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("E5",.25),("E5",.25),(None,.25),("G5",.25),
        (None,.25),("A5",.25),("G5",.25),("E5",.25),
        ("D5",.5),("E5",.5),(None,.5),("B4",.5),
        ("E5",.25),("E5",.25),(None,.25),("G5",.25),
        (None,.25),("A5",.25),("B5",.25),("A5",.25),
        ("G5",.5),("E5",.5),(None,1),
        ("A4",.25),("C5",.25),("E5",.25),("A5",.25),
        ("G5",.5),("E5",.5),(None,.5),("C5",.5),
        ("A4",.5),("C5",.5),("D5",.5),("E5",.5),
        ("E5",1),(None,1),
        ("D5",.25),("F#5",.25),("A5",.25),("D5",.25),
        ("F#5",.5),("D5",.5),("A4",.5),("D5",.5),
        ("D#5",.5),("F#5",.5),("B4",.5),("D#5",.5),
        ("F#5",1),(None,1),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["E2","E2","G2","E2","A2","A2","C3","A2",
              "D2","D2","F#2","D2","B1","B1","D#2","F#2"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def blues_shuffle():
    """12/8 blues in A — slow shuffle with wailing lead."""
    print("  12/8 Blues Shuffle in A")
    print("  12/8 blues drums | saw lead + reverb + delay | sine bass + LP 500Hz")

    score = Score("12/8", bpm=70)
    score.drums("12/8 blues", repeats=6)

    chords = score.part("chords", instrument="electric_piano",
                        volume=0.3, pan=-0.3,
                        reverb=0.3, reverb_decay=1.5, reverb_type="plate")
    lead = score.part("lead", instrument="trumpet",
                      volume=0.45, pan=0.25,
                      reverb=0.3, reverb_decay=1.2, reverb_type="plate",
                      delay=0.2, delay_time=0.43, delay_feedback=0.3,
                      lowpass=3500)
    bass = score.part("bass", instrument="upright_bass",
                      volume=0.5, pan=0.0, lowpass=500)

    for sym in ["A", "A", "D", "D", "E7", "A"]:
        chords.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)
        chords.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)

    for n, d in [
        ("A4",1),("C5",.67),("A4",.33),("E4",1),
        (None,.5),("A4",.5),("C5",.67),("D5",.33),
        ("E5",1.5),("D5",.5),("C5",.5),("A4",.5),
        ("E4",1.5),(None,.5),("A4",1),
        ("D5",1),("F5",.67),("D5",.33),("A4",1),
        (None,1),("D5",.67),("F5",.33),("A5",1),
        ("G5",.67),("F5",.33),("D5",1),(None,1),
        ("E5",.67),("G#4",.33),("B4",.67),("E5",.33),
        ("D5",1),("A4",1),(None,1),
        ("A4",.67),("C5",.33),("E5",.67),("A5",.33),
        ("A5",2),(None,1),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["A1","A1","E2","A2","A1","A1","E2","A2","A1","A1","E2","A2",
              "D2","D2","A2","D2","D2","D2","A2","D2",
              "E2","E2","B2","E2","A1","A1","E2","A2",
              "E2","E2","B2","E2","A1","A1","E2","A2"]:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def samba_de_janeiro():
    """Samba in G major — carnival energy with shimmering pads."""
    print("  Samba in G major")
    print("  samba drums + fill | triangle lead + delay | supersaw pads + reverb")

    score = Score("4/4", bpm=170)
    score.drums("samba", repeats=8, fill="samba", fill_every=8)

    pads = score.part("pads", instrument="synth_pad",
                      volume=0.2, pan=-0.3,
                      reverb=0.45, reverb_decay=2.0, reverb_type="plate",
                      lowpass=4000)
    lead = score.part("lead", instrument="flute",
                      volume=0.45, pan=0.3,
                      delay=0.2, delay_time=0.176, delay_feedback=0.3,
                      reverb=0.15, reverb_type="plate")
    bass = score.part("bass", instrument="bass_guitar",
                      volume=0.45, pan=0.0, lowpass=500)

    for sym in ["G", "Em", "Am", "D7"] * 2:
        pads.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("B5",.33),("A5",.33),("G5",.34),("F#5",.5),("E5",.5),
        ("D5",.5),("G5",.5),("B5",.5),("A5",.5),
        ("G5",.67),("E5",.33),("D5",.67),("B4",.33),("G4",1),(None,1),
        ("E5",.5),("G5",.5),("B5",.5),("A5",.5),
        ("G5",.67),("F#5",.33),("E5",.67),("D5",.33),("E5",1),(None,1),
        ("A5",.5),("C6",.5),("B5",.5),("A5",.5),
        ("G5",.67),("E5",.33),("C5",.67),("A4",.33),("A4",1),(None,1),
        ("D5",.5),("F#5",.5),("A5",.5),("C5",.5),
        ("B4",.67),("A4",.33),("G4",.67),("F#4",.33),("G4",2),(None,2),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["G2","B2","D3","G2","E2","G2","B2","E2",
              "A2","C3","E3","A2","D2","F#2","A2","D3"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def jazz_waltz():
    """Jazz waltz in F major — 3/4 with brushes and space."""
    print("  Jazz Waltz in F major")
    print("  waltz drums | triangle lead + reverb + delay | FM rhodes")

    score = Score("3/4", bpm=150)
    score.drums("waltz", repeats=16)

    rhodes = score.part("rhodes", instrument="electric_piano",
                        volume=0.3, pan=-0.3,
                        reverb=0.4, reverb_decay=2.0, reverb_type="cathedral")
    lead = score.part("lead", instrument="flute",
                      volume=0.4, pan=0.25,
                      reverb=0.3, reverb_decay=1.5, reverb_type="plate",
                      delay=0.2, delay_time=0.4, delay_feedback=0.3)
    bass = score.part("bass", instrument="upright_bass",
                      volume=0.4, pan=0.0, lowpass=500)

    for _ in range(2):
        for sym in ["Fmaj7", "Gm", "C7", "Fmaj7"]:
            for _ in range(4):
                rhodes.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)

    for n, d in [
        ("A5",1.5),("G5",.5),("F5",1),("E5",1),("C5",1),("F5",1),
        ("A5",2),(None,1),("G5",2),(None,1),
        ("Bb5",1),("A5",.5),("G5",.5),("F5",1),("D5",1),("G5",1),
        ("Bb5",2),(None,1),("A5",1.5),("G5",.5),("F5",1),
        ("E5",1),("G5",1),("Bb5",1),("A5",1.5),("G5",.5),("E5",1),
        ("C5",2),(None,1),("E5",1),("G5",1),("C5",1),
        ("F5",2),("A5",1),("C6",2),(None,1),
        ("A5",1),("F5",1),("C5",1),("F5",3),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["F2","A2","C3","G2","Bb2","D3","C2","E2","G2","F2","A2","C3"] * 4:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def house_anthem():
    """House in C minor — four-on-the-floor with acid lead."""
    print("  House Anthem in C minor")
    print("  house drums + fill | saw acid lead + LP 2kHz Q=2 + delay")
    print("  supersaw pads + reverb | sine bass")

    score = Score("4/4", bpm=124)
    score.drums("house", repeats=8, fill="house", fill_every=8)

    pads = score.part("pads", instrument="synth_pad",
                      volume=0.25, pan=-0.3,
                      reverb=0.5, reverb_decay=2.5, reverb_type="cathedral",
                      lowpass=5000,
                      sidechain=0.6)
    lead = score.part("lead", instrument="synth_lead",
                      volume=0.35, pan=0.3,
                      lowpass=2000, lowpass_q=2.0,
                      delay=0.2, delay_time=0.242, delay_feedback=0.35,
                      reverb=0.15, reverb_type="plate")
    bass = score.part("bass", instrument="808_bass",
                      volume=0.55, pan=0.0,
                      sidechain=0.5)

    for sym in ["Cm", "Ab", "Bb", "Cm"] * 2:
        pads.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("C5",.25),("Eb5",.25),("G5",.25),("C5",.25),
        ("Eb5",.25),("G5",.25),("C5",.25),("Eb5",.25),
        ("G5",.25),("Eb5",.25),("C5",.25),("G4",.25),
        ("C5",.5),(None,.5),("Eb5",.5),("G5",.5),
        ("Ab4",.25),("C5",.25),("Eb5",.25),("Ab4",.25),
        ("C5",.25),("Eb5",.25),("Ab4",.25),("C5",.25),
        ("Eb5",.25),("C5",.25),("Ab4",.25),("Eb4",.25),
        ("Ab4",.5),(None,.5),("C5",.5),("Eb5",.5),
        ("Bb4",.25),("D5",.25),("F5",.25),("Bb4",.25),
        ("D5",.25),("F5",.25),("Bb4",.25),("D5",.25),
        ("F5",.5),("D5",.5),("Bb4",.5),("F5",.5),
        ("C5",.25),("Eb5",.25),("G5",.25),("C6",.25),
        ("G5",.25),("Eb5",.25),("C5",.25),(None,.25),
        ("C5",1.5),(None,.5),
        ("G5",.25),("G5",.25),("Eb5",.25),("C5",.25),
        ("G5",.25),("G5",.25),("Eb5",.25),("C5",.25),
        ("Eb5",.5),("C5",.5),("G4",.5),("C5",.5),
        ("Eb5",1),(None,1),
        ("Ab4",.5),("C5",.5),("Eb5",.5),("Ab5",.5),
        ("G5",.5),("Eb5",.5),("C5",1),
        ("Bb4",.5),("D5",.5),("F5",.5),("Bb5",.5),
        ("F5",.5),("D5",.5),("Bb4",1),
        ("C5",.5),("Eb5",.5),("G5",.5),("C6",.5),("C6",2),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["C2","C2","C2","C2","Ab1","Ab1","Ab1","Ab1",
              "Bb1","Bb1","Bb1","Bb1","C2","C2","C2","C2"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def dub_kingston():
    """Dub in A minor — deep, sparse, drenched in effects."""
    print("  Kingston After Dark")
    print("  dub drums | triangle melodica + delay + reverb")
    print("  square skank + reverb + LP 1.5kHz | sine bass + LP 400Hz")
    print("  PWM siren + reverb + LP 1.2kHz")

    score = Score("4/4", bpm=72)
    score.drums("dub", repeats=8)

    chords = score.part("chords", synth="square", envelope="staccato",
                        volume=0.2, pan=-0.4,
                        reverb=0.6, reverb_decay=2.5, reverb_type="cathedral",
                        lowpass=1500, lowpass_q=0.9, detune=8,
                        humanize=0.2)
    lead = score.part("lead", instrument="flute",
                      volume=0.4, pan=0.3,
                      delay=0.45, delay_time=0.625, delay_feedback=0.5,
                      reverb=0.35, reverb_decay=2.0, reverb_type="cathedral")
    bass = score.part("bass", instrument="bass_guitar",
                      volume=0.6, pan=0.0, lowpass=400, lowpass_q=1.5)
    siren = score.part("siren", synth="pwm_slow", envelope="pad",
                       volume=0.15, pan=0.5,
                       reverb=0.7, reverb_decay=3.0, reverb_type="cathedral",
                       lowpass=1200, detune=10)

    for sym in ["Am", "Am", "Dm", "Dm", "Am", "Am", "Em", "Am"]:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("A4", 2), (None, 2), ("C5", 1.5), (None, 2.5),
        ("D5", 1), ("C5", 1), ("A4", 2), (None, 4),
        ("E5", 2), (None, 2), ("D5", 1.5), ("C5", 1.5), (None, 3),
        ("A4", 1), ("G4", 1), ("A4", 3), (None, 3),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["A1","A1","A1","A1","D1","D1","D1","D1",
              "A1","A1","A1","A1","E1","E1","A1","A1"]:
        bass.add(n, Duration.HALF)

    for n, d in [
        (None, 8), ("A5", 4), (None, 4),
        (None, 4), ("E5", 3), (None, 5),
        ("D5", 4), (None, 4),
    ]:
        siren.rest(d) if n is None else siren.add(n, d)

    play_song(score)


def techno_minimal():
    """Minimal techno in F minor — hypnotic and relentless."""
    print("  Minimal Techno in F minor")
    print("  techno drums | PWM fast lead + LP 1.5kHz Q=3 + delay")
    print("  supersaw pad + reverb | sine sub bass")

    score = Score("4/4", bpm=130)
    score.drums("techno", repeats=8, fill="house", fill_every=8)

    pad = score.part("pad", instrument="synth_pad",
                     volume=0.2, pan=-0.3,
                     reverb=0.5, reverb_decay=3.0, reverb_type="cathedral",
                     lowpass=3000,
                     sidechain=0.6)
    lead = score.part("lead", synth="pwm_fast", envelope="staccato",
                      volume=0.35, pan=0.3,
                      lowpass=1500, lowpass_q=3.0,
                      delay=0.3, delay_time=0.231, delay_feedback=0.4,
                      reverb=0.1, reverb_type="plate",
                      humanize=0.2)
    bass = score.part("bass", instrument="808_bass",
                      volume=0.55, pan=0.0,
                      sidechain=0.5)

    for sym in ["Fm", "Db", "Eb", "Fm"] * 2:
        pad.add(Chord.from_symbol(sym), Duration.WHOLE)

    # Minimal arpeggiated sequence — hypnotic repetition
    seq = [("F4",.25),("Ab4",.25),("C5",.25),("F4",.25),
           ("Ab4",.25),("C5",.25),("Eb5",.25),("C5",.25)]
    for n, d in seq * 8:
        lead.add(n, d)

    for n in ["F1","F1","F1","F1","Db1","Db1","Db1","Db1",
              "Eb1","Eb1","Eb1","Eb1","F1","F1","F1","F1"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def gospel_shuffle():
    """Gospel in C major — joyful shuffle with FM organ."""
    print("  Gospel Shuffle in C major")
    print("  gospel drums + fill | FM organ + reverb | triangle lead + delay")

    score = Score("4/4", bpm=108)
    score.drums("gospel", repeats=8, fill="buildup", fill_every=8)

    organ = score.part("organ", instrument="organ",
                       volume=0.3, pan=-0.3,
                       reverb=0.45, reverb_decay=2.0, reverb_type="cathedral")
    lead = score.part("lead", instrument="flute",
                      volume=0.4, pan=0.3,
                      delay=0.2, delay_time=0.278, delay_feedback=0.3,
                      reverb=0.2, reverb_type="plate")
    bass = score.part("bass", instrument="upright_bass",
                      volume=0.45, pan=0.0, lowpass=500)

    for sym in ["C", "Am", "F", "G"] * 2:
        organ.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n, d in [
        ("E5",.67),("G5",.33),("C6",1),("B5",.67),("A5",.33),
        ("G5",1),(None,1),
        ("A5",.67),("C6",.33),("E5",1),("D5",.67),("C5",.33),
        ("A4",1),(None,1),
        ("F5",.67),("A5",.33),("C6",1),("B5",.67),("A5",.33),
        ("G5",.67),("E5",.33),("C5",1),(None,1),
        ("D5",.67),("E5",.33),("G5",.67),("B5",.33),
        ("C6",2),(None,2),
        # Second half: more intense
        ("C6",.67),("B5",.33),("A5",.67),("G5",.33),
        ("E5",1),("C5",.67),("E5",.33),
        ("A5",1),("G5",.67),("E5",.33),("C5",1),(None,1),
        ("F5",1),("A5",.67),("C6",.33),("E6",2),
        ("D6",.67),("C6",.33),("B5",.67),("G5",.33),
        ("C6",3),(None,1),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    for n in ["C2","E2","G2","C3","A1","C2","E2","A2",
              "F2","A2","C3","F2","G2","B2","D3","G2"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def dub_delay_madness():
    """Dub with separate delay snare track — King Tubby style."""
    print("  Dub Delay Madness in E minor")
    print("  dub drums + separate snare w/ massive delay + reverb")
    print("  square skank + reverb | sine sub bass | PWM siren")

    score = Score("4/4", bpm=68)
    score.drums("dub", repeats=8)

    # Separate snare hits — fed through massive delay and reverb
    # This is how Tubby did it: mute the snare from the main mix,
    # then send it to a separate channel drowning in effects
    from pytheory.rhythm import _Hit, DrumSound
    for bar in range(8):
        offset = bar * 4.0
        # Snare on beat 3 of every bar
        score._drum_hits.append(_Hit(DrumSound.SNARE, offset + 2.0, 110))
        # Occasional rimshot ghost that the delay catches
        if bar % 2 == 1:
            score._drum_hits.append(_Hit(DrumSound.RIMSHOT, offset + 3.5, 60))

    chords = score.part("skank", synth="square", envelope="staccato",
                        volume=0.15, pan=-0.4,
                        reverb=0.7, reverb_decay=3.0, reverb_type="cathedral",
                        lowpass=1200, detune=8, humanize=0.2)
    bass = score.part("bass", instrument="bass_guitar",
                      volume=0.6, pan=0.0, lowpass=350, lowpass_q=1.5)
    siren = score.part("siren", synth="pwm_slow", envelope="pad",
                       volume=0.12, pan=0.5,
                       reverb=0.8, reverb_decay=4.0, reverb_type="cathedral",
                       delay=0.4, delay_time=0.88, delay_feedback=0.6,
                       lowpass=900, detune=10)
    # Melodica stabs — sparse, lots of delay
    melodica = score.part("melodica", instrument="flute",
                          volume=0.35, pan=0.3,
                          delay=0.6, delay_time=0.66, delay_feedback=0.55,
                          reverb=0.5, reverb_decay=2.5, reverb_type="cathedral")

    for sym in ["Em", "Em", "Am", "Am", "Em", "Em", "Bm", "Em"]:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n in ["E1","E1","E1","E1","A1","A1","A1","A1",
              "E1","E1","E1","E1","B1","B1","E1","E1"]:
        bass.add(n, Duration.HALF)

    # Melodica: very sparse — let the delay do the work
    for n, d in [
        ("E5", 1.5), (None, 6.5),
        ("G5", 1), ("A5", 1), (None, 6),
        (None, 4), ("B5", 2), (None, 6),
        ("E5", 1), (None, 3), ("D5", 1.5), (None, 2.5),
    ]:
        melodica.rest(d) if n is None else melodica.add(n, d)

    # Siren: long notes that disappear into the void
    for n, d in [
        (None, 12), ("B5", 6), (None, 6),
        ("E5", 4), (None, 4),
    ]:
        siren.rest(d) if n is None else siren.add(n, d)

    play_song(score)


def drum_and_bass():
    """Drum and bass in A minor — 174 bpm liquid rollers."""
    print("  Liquid DnB in A minor")
    print("  drum and bass drums + fill | supersaw pads + reverb")
    print("  triangle lead + delay | sine sub bass + LP 300Hz")

    score = Score("4/4", bpm=174)
    score.drums("drum and bass", repeats=8, fill="buildup", fill_every=8)

    pads = score.part("pads", instrument="synth_pad",
                      volume=0.25, pan=-0.3,
                      reverb=0.5, reverb_decay=2.5, reverb_type="plate",
                      lowpass=4000)
    lead = score.part("lead", instrument="flute",
                      volume=0.4, pan=0.3,
                      delay=0.3, delay_time=0.172, delay_feedback=0.4,
                      reverb=0.25, reverb_type="plate")
    bass = score.part("bass", instrument="808_bass",
                      volume=0.55, pan=0.0)

    for sym in ["Am", "F", "C", "G"] * 2:
        pads.add(Chord.from_symbol(sym), Duration.WHOLE)

    # Liquid melody — flowing, emotional
    for n, d in [
        ("A5", 1), ("G5", .5), ("E5", .5), ("C5", 1), (None, 1),
        ("D5", .5), ("E5", .5), ("G5", 1), ("A5", 1.5), (None, .5),
        ("C6", 1), ("B5", .5), ("A5", .5), ("G5", 1), ("E5", 1),
        ("F5", .5), ("G5", .5), ("A5", 1.5), (None, .5), ("G5", 1),
        ("A5", 1), ("G5", .5), ("E5", .5), ("C5", 1), (None, 1),
        ("E5", .5), ("G5", .5), ("B5", 1), ("A5", 2),
        ("G5", 1), ("E5", .5), ("D5", .5), ("C5", 1.5), (None, .5),
        ("E5", .5), ("G5", .5), ("A5", 2), (None, 1),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    # Sub bass — half note roots, deep
    for n in ["A1","A1","F1","F1","C1","C1","G1","G1"] * 2:
        bass.add(n, Duration.HALF)

    play_song(score)


def drake_vibes():
    """Drake-style moody hip hop — 808s, pads, and melancholy."""
    print("  Late Night Texts (Drake-style)")
    print("  trap drums | FM bells + reverb + delay | supersaw pads + LP")
    print("  sine 808 bass + distortion | PWM slow lead")

    score = Score("4/4", bpm=68)
    score.drums("trap", repeats=8, fill="trap", fill_every=8)

    pads = score.part("pads", instrument="synth_pad",
                      volume=0.2, pan=-0.25,
                      reverb=0.5, reverb_decay=3.0, reverb_type="cathedral",
                      lowpass=2500,
                      sidechain=0.4)
    bells = score.part("bells", instrument="vibraphone",
                       volume=0.3, pan=0.4,
                       reverb=0.4, reverb_decay=2.0, reverb_type="plate",
                       delay=0.25, delay_time=0.44, delay_feedback=0.35)
    lead = score.part("lead", synth="pwm_slow", envelope="strings",
                      volume=0.35, pan=-0.2,
                      reverb=0.3, reverb_type="cathedral", lowpass=2000,
                      delay=0.2, delay_time=0.88, delay_feedback=0.3,
                      humanize=0.2)
    bass = score.part("bass", instrument="808_bass",
                      volume=0.6, pan=0.0,
                      distortion=0.4, distortion_drive=2.0,
                      sidechain=0.3)

    for sym in ["Ebm", "B", "Gb", "Db"] * 2:
        pads.add(Chord.from_symbol(sym), Duration.WHOLE)

    # FM bells — sparse, melancholy arpeggios
    for n, d in [
        ("Eb5", .5), ("Gb5", .5), ("Bb5", 1), (None, 2),
        ("Db5", .5), ("F5", .5), ("Ab5", 1), (None, 2),
        ("Gb5", .5), ("Bb5", .5), ("Db6", 1), (None, 2),
        ("F5", .5), ("Ab5", .5), ("Db6", 1.5), (None, 1.5),
        ("Eb5", .5), ("Gb5", .5), ("Bb5", 1), (None, 2),
        ("B4", .5), ("Eb5", .5), ("Gb5", 1), (None, 2),
        ("Gb5", 1), ("F5", .5), ("Eb5", .5), ("Db5", 2),
        (None, 4),
    ]:
        bells.rest(d) if n is None else bells.add(n, d)

    # PWM lead — long held notes, moody
    for n, d in [
        (None, 4), ("Bb5", 3), (None, 1),
        (None, 2), ("Ab5", 2), ("Gb5", 2), (None, 2),
        ("Db6", 4), (None, 4),
        ("Bb5", 2), ("Ab5", 2), (None, 4),
    ]:
        lead.rest(d) if n is None else lead.add(n, d)

    # 808 bass — sustained with distortion warmth
    for n in ["Eb1","Eb1","Eb1","Eb1","B0","B0","B0","B0",
              "Gb1","Gb1","Gb1","Gb1","Db1","Db1","Db1","Db1"] * 2:
        bass.add(n, Duration.QUARTER)

    play_song(score)


# ── Main ───────────────────────────────────────────────────────────────────

def neon_grid():
    """Cyberpunk electronic — stereo acid, wide pads, ping-pong bells."""
    print("  Neon Grid in F minor")
    print("  techno drums | dual acid L/R + LFO | supersaw pad spread=1.0")
    print("  FM stabs | ping-pong bells | sine sub + sidechain")

    score = Score("4/4", bpm=132)
    score.drums("techno", repeats=8, fill="house", fill_every=8)

    from pytheory.rhythm import _Hit, DrumSound
    for bar in range(8):
        for beat in range(4):
            score._drum_hits.append(_Hit(DrumSound.KICK, bar * 4.0 + beat, 120))
    score._drum_pattern_beats = max(score._drum_pattern_beats, 32.0)

    sky = score.part(
        "sky", instrument="synth_pad",
        volume=0.18, pan=0.0,
        detune=30, spread=1.0,
        reverb=0.6, reverb_decay=3.5,
        chorus=0.3, sidechain=0.5,
    )
    acid_l = score.part(
        "acid_l", instrument="acid_bass",
        volume=0.35, pan=-0.7,
        legato=True, glide=0.025,
        distortion=0.9, distortion_drive=12.0,
        lowpass=800, lowpass_q=6.0,
        delay=0.2, delay_time=0.227, delay_feedback=0.35,
    )
    acid_l.lfo("lowpass", rate=0.5, min=400, max=3000, bars=8, shape="sine")

    acid_r = score.part(
        "acid_r", instrument="acid_bass",
        volume=0.3, pan=0.7,
        legato=True, glide=0.02,
        distortion=0.85, distortion_drive=10.0,
        lowpass=1000, lowpass_q=5.0,
        delay=0.25, delay_time=0.341, delay_feedback=0.4,
    )
    acid_r.lfo("lowpass", rate=0.33, min=500, max=2500, bars=8, shape="triangle")

    sub = score.part(
        "sub", instrument="808_bass",
        volume=0.55, pan=0.0,
        lowpass=160, sidechain=0.85, sidechain_release=0.08,
    )
    stab = score.part(
        "stab", synth="fm", envelope="staccato",
        volume=0.2, pan=-0.4,
        reverb=0.4, reverb_decay=1.5,
        detune=15, spread=0.7,
    )
    bell_l = score.part(
        "bell_l", instrument="vibraphone",
        volume=0.1, pan=-1.0,
        reverb=0.7, reverb_decay=3.0,
    )
    bell_r = score.part(
        "bell_r", instrument="vibraphone",
        volume=0.1, pan=1.0,
        reverb=0.7, reverb_decay=3.0,
        delay=0.2, delay_time=0.8, delay_feedback=0.4,
    )

    chords = ["Fm", "Dbm", "Abm", "Ebm"]

    for sym in chords * 2:
        sky.add(Chord.from_symbol(sym), Duration.WHOLE)

    for sym in chords:
        acid_l.arpeggio(Chord.from_symbol(sym, octave=2), bars=2,
                        pattern="up", octaves=2, division=Duration.SIXTEENTH)
    for sym in chords:
        acid_r.arpeggio(Chord.from_symbol(sym, octave=2), bars=2,
                        pattern="down", octaves=2, division=Duration.SIXTEENTH)

    for n in ["F1"] * 8 + ["Db1"] * 8 + ["Ab1"] * 8 + ["Eb1"] * 8:
        sub.add(n, Duration.QUARTER)

    for sym in chords * 2:
        stab.rest(1)
        stab.add(Chord.from_symbol(sym), 0.5)
        stab.rest(0.5)
        stab.add(Chord.from_symbol(sym), 0.5)
        stab.rest(1.5)

    for n, v, d in [
        ("F6", 50, 2), (None, 0, 6), ("Ab6", 45, 2), (None, 0, 6),
        ("Eb7", 55, 3), (None, 0, 13),
    ]:
        bell_l.rest(d) if n is None else bell_l.add(n, d, velocity=v)

    for n, v, d in [
        (None, 0, 4), ("Db7", 45, 2), (None, 0, 6),
        ("F7", 50, 2), (None, 0, 6),
        (None, 0, 4), ("Ab6", 40, 4), (None, 0, 8),
    ]:
        bell_r.rest(d) if n is None else bell_r.add(n, d, velocity=v)

    play_song(score)


def glass_and_silk():
    """Pure sine and triangle — smooth shapes in a stereo cathedral."""
    print("  Glass and Silk in Ab major")
    print("  sine + triangle only | waltz 72bpm | cathedral + Taj Mahal reverb")

    score = Score("3/4", bpm=72, swing=0.2)
    score.drums("waltz", repeats=16)

    sub = score.part("sub", synth="sine", envelope="pad",
                     volume=0.3, pan=0.0, lowpass=120)
    voice = score.part("voice", synth="triangle", envelope="strings",
                       volume=0.45, pan=0.2, legato=True, glide=0.07,
                       reverb=0.5, reverb_type="cathedral",
                       delay=0.2, delay_time=0.56, delay_feedback=0.4,
                       humanize=0.3)
    pad = score.part("pad", synth="sine", envelope="pad",
                     volume=0.2, pan=0.0, detune=10, spread=0.6,
                     reverb=0.6, reverb_type="taj_mahal",
                     chorus=0.2, chorus_rate=0.3)
    counter = score.part("counter", synth="triangle", envelope="strings",
                         volume=0.2, pan=-0.5,
                         reverb=0.4, reverb_type="plate",
                         delay=0.15, delay_time=0.83, delay_feedback=0.35,
                         humanize=0.25)

    chords = [Chord.from_symbol(s) for s in ["Ab", "Fm", "Db", "Eb"]]
    for c in chords * 2:
        for _ in range(3):
            pad.add(c, Duration.DOTTED_HALF)

    for n in (["Ab2"] * 9 + ["F2"] * 9 + ["Db2"] * 9 + ["Eb2"] * 9) * 2:
        sub.add(n, Duration.QUARTER)

    for n, v, d in [
        ("Ab4", 60, 3), ("C5", 70, 1.5), ("Eb5", 75, 1.5),
        ("Ab5", 85, 4.5), (None, 0, 1.5),
        ("F5", 75, 1.5), ("Ab5", 80, 1.5), ("C6", 90, 3),
        ("Bb5", 80, 1.5), ("Ab5", 70, 1.5), (None, 0, 3),
        ("Db5", 70, 1.5), ("Eb5", 80, 1.5), ("Ab5", 95, 3),
        ("Bb5", 100, 3), ("C6", 105, 4.5), (None, 0, 1.5),
        ("Bb5", 85, 1.5), ("Ab5", 75, 1.5), ("Eb5", 70, 3),
        ("C5", 60, 3), ("Ab4", 55, 6), (None, 0, 3),
        ("Eb5", 65, 3), ("Ab5", 80, 3), ("C6", 90, 4.5), (None, 0, 1.5),
        ("Bb5", 85, 1.5), ("Ab5", 75, 1.5), ("F5", 70, 3),
        ("Eb5", 65, 1.5), ("Db5", 60, 1.5), (None, 0, 3),
        ("Eb5", 70, 1.5), ("F5", 80, 1.5), ("Ab5", 90, 3),
        ("Bb5", 95, 3), ("Ab5", 85, 3),
        ("Eb5", 70, 3), ("Ab4", 55, 9),
    ]:
        voice.rest(d) if n is None else voice.add(n, d, velocity=v)

    for _ in range(24):
        counter.rest(Duration.QUARTER)
    for n, v, d in [
        (None, 0, 3), ("C6", 55, 3), ("Eb6", 60, 4.5), (None, 0, 1.5),
        ("Db6", 50, 3), ("C6", 45, 3), (None, 0, 6),
        ("Eb6", 55, 4.5), ("Db6", 50, 1.5), ("C6", 45, 3),
        ("Ab5", 40, 6), (None, 0, 3),
        ("Bb5", 50, 3), ("C6", 55, 4.5), (None, 0, 1.5),
        ("Ab5", 45, 9),
    ]:
        counter.rest(d) if n is None else counter.add(n, d, velocity=v)

    play_song(score)


def dance_party():
    """Dance party — bouncy, joyful, impossible not to move."""
    print("  Dance Party at the Reitz House")
    print("  disco 128bpm | FM sparkle | square chiptune arps | supersaw pump")

    from pytheory.rhythm import _Hit, DrumSound

    score = Score("4/4", bpm=128)
    score.drums("disco", repeats=8, fill="buildup", fill_every=8)

    for bar in range(8):
        for beat in range(4):
            score._drum_hits.append(_Hit(DrumSound.KICK, bar * 4.0 + beat, 120))
    score._drum_pattern_beats = max(score._drum_pattern_beats, 32.0)

    bass = score.part("bass", instrument="synth_bass",
                      volume=0.45, lowpass=500, lowpass_q=1.3,
                      sidechain=0.75, sidechain_release=0.12)
    sparkle = score.part("sparkle", instrument="vibraphone",
                         volume=0.3, pan=0.4, reverb=0.3, reverb_decay=1.5,
                         delay=0.2, delay_time=0.234, delay_feedback=0.3)
    chords_part = score.part("chords", instrument="synth_pad",
                             volume=0.2,
                             reverb=0.4, reverb_type="plate", sidechain=0.7)
    fun = score.part("fun", synth="square", envelope="staccato",
                     volume=0.2, pan=-0.5, delay=0.15, delay_time=0.117,
                     delay_feedback=0.25, reverb=0.2)

    for sym in ["C", "Am", "F", "G"] * 2:
        chords_part.add(Chord.from_symbol(sym), Duration.WHOLE)

    for n in ["C2", "C2", "C3", "C2", "A1", "A1", "A2", "A1",
              "F1", "F1", "F2", "F1", "G1", "G1", "G2", "G1"] * 2:
        bass.add(n, Duration.QUARTER)

    for n, v, d in [
        ("E5", 100, 0.5), ("G5", 110, 0.5), ("C6", 120, 1), (None, 0, 0.5),
        ("B5", 100, 0.5), ("G5", 90, 0.5), ("E5", 100, 0.5),
        ("C5", 90, 0.5), ("E5", 100, 0.5), ("G5", 110, 1), (None, 0, 0.5),
        ("A5", 100, 0.5),
        ("C6", 120, 0.5), ("A5", 100, 0.5), ("F5", 90, 0.5), ("A5", 100, 0.5),
        ("C6", 110, 1), (None, 0, 1),
        ("B5", 100, 0.5), ("D6", 120, 0.5), ("B5", 100, 0.5), ("G5", 90, 0.5),
        ("D5", 80, 0.5), ("G5", 100, 1), (None, 0, 0.5),
        ("E5", 100, 0.5), ("G5", 110, 0.5), ("C6", 120, 1),
        ("E6", 125, 1), (None, 0, 0.5),
        ("D6", 110, 0.5), ("C6", 100, 0.5), ("B5", 90, 0.5),
        ("A5", 100, 0.5), ("G5", 110, 0.5), ("E5", 90, 1), (None, 0, 0.5),
        ("F5", 100, 0.5), ("A5", 110, 0.5), ("C6", 120, 1), (None, 0, 0.5),
        ("B5", 100, 0.5), ("G5", 110, 0.5), ("D6", 120, 0.5),
        ("C6", 110, 1), ("G5", 90, 0.5), ("C6", 120, 1), (None, 0, 0.5),
    ]:
        sparkle.rest(d) if n is None else sparkle.add(n, d, velocity=v)

    for sym in ["C", "Am", "F", "G", "C", "Am", "F", "G"]:
        pat = "up" if sym in ("C", "F") else "updown"
        fun.arpeggio(sym, bars=1, pattern=pat, octaves=2, division=Duration.EIGHTH)

    play_song(score)


def temple_bell():
    """Japanese-inspired — sparse koto, Taj Mahal reverb, silence as instrument."""
    print("  Temple Bell")
    print("  E hirajoshi | 65 bpm | triangle koto + Taj Mahal reverb")

    score = Score("4/4", bpm=65)
    score.drums("bolero", repeats=8)

    koto = score.part("koto", instrument="koto",
                      volume=0.45, pan=0.2,
                      reverb=0.5, reverb_type="taj_mahal")
    drone = score.part("drone", synth="sine", envelope="pad",
                       volume=0.15, reverb=0.6, reverb_type="taj_mahal",
                       chorus=0.15, chorus_rate=0.2)
    bell = score.part("bell", instrument="vibraphone",
                      volume=0.1, pan=-0.6,
                      reverb=0.8, reverb_type="taj_mahal")

    for _ in range(8):
        drone.add("E2", Duration.WHOLE)

    for n, v, d in [
        ("E4", 70, 2), (None, 0, 2), ("A4", 60, 1.5), (None, 0, 2.5),
        ("B4", 75, 2), ("A4", 60, 1), ("E4", 55, 1), (None, 0, 4),
        ("C5", 80, 3), (None, 0, 1), ("B4", 65, 1.5), ("A4", 55, 1.5),
        ("E4", 50, 3), (None, 0, 5),
        ("F4", 60, 1), ("A4", 70, 1.5), ("B4", 80, 2.5), (None, 0, 3),
        ("E5", 85, 4), (None, 0, 4),
        ("C5", 65, 1.5), ("B4", 55, 1.5), ("A4", 50, 2),
        ("E4", 45, 5), (None, 0, 3),
    ]:
        koto.rest(d) if n is None else koto.add(n, d, velocity=v)

    for n, v, d in [
        (None, 0, 8), ("E6", 30, 4), (None, 0, 8),
        ("B6", 25, 3), (None, 0, 9),
        ("A6", 30, 4), (None, 0, 12),
    ]:
        bell.rest(d) if n is None else bell.add(n, d, velocity=v)

    play_song(score)


def cinematic_showcase():
    """Cinematic orchestral showcase — tubular bells, strings, organ, harp, acid bass."""
    score = Score("4/4", bpm=100)

    # Tubular bells — dramatic intro
    bells = score.part("bells", instrument="tubular_bells",
                       reverb=0.5, reverb_type="cathedral")
    bells.add("A3", Duration.WHOLE)
    for _ in range(7):
        bells.rest(Duration.WHOLE)

    # String ensemble — lush wide pad
    strings = score.part("strings", instrument="string_ensemble",
                         reverb=0.4, reverb_type="hall")
    strings.rest(Duration.WHOLE)
    for sym in ["Am", "F", "C", "G", "Dm", "Am", "E"]:
        strings.add(Chord.from_symbol(sym), Duration.WHOLE)

    # Cello — deep foundation
    cello = score.part("cello", instrument="cello",
                       reverb=0.3, reverb_type="hall")
    cello.rest(Duration.WHOLE)
    for n in ["A2", "F2", "C3", "G2", "D3", "A2", "E2"]:
        cello.add(n, Duration.WHOLE)

    # Violin — legato melody enters bar 3
    violin = score.part("violin", instrument="violin",
                        reverb=0.25, reverb_type="hall", legato=True)
    violin.rest(Duration.WHOLE)
    violin.rest(Duration.WHOLE)
    for note, dur in [
        ("E5", Duration.HALF), ("C5", Duration.HALF),
        ("D5", Duration.QUARTER), ("E5", Duration.QUARTER), ("G5", Duration.HALF),
        ("A5", Duration.HALF), ("G5", Duration.QUARTER), ("E5", Duration.QUARTER),
        ("F5", Duration.WHOLE),
        ("E5", Duration.HALF), ("D5", Duration.HALF),
        ("C5", Duration.HALF), ("B4", Duration.HALF),
        ("A4", Duration.WHOLE),
    ]:
        violin.add(note, dur)

    # Organ — enters halfway, cathedral weight
    organ = score.part("organ", instrument="organ",
                       reverb=0.3, reverb_type="cathedral")
    for _ in range(4):
        organ.rest(Duration.WHOLE)
    for sym in ["Dm", "Am", "E", "Am"]:
        organ.add(Chord.from_symbol(sym), Duration.WHOLE)

    # Harp — arpeggiated flourishes bars 3-4
    harp = score.part("harp", instrument="harp")
    harp.rest(Duration.WHOLE)
    harp.rest(Duration.WHOLE)
    for n in ["A3", "C4", "E4", "A4", "C5", "E5", "A5", "E5",
              "G3", "B3", "D4", "G4", "B4", "D5", "G5", "D5"]:
        harp.add(n, Duration.EIGHTH)
    for _ in range(4):
        harp.rest(Duration.WHOLE)

    # Vibraphone — shimmer in last bars with delay
    vib = score.part("vib", instrument="vibraphone",
                     delay=0.25, delay_time=0.375, delay_feedback=0.35)
    for _ in range(5):
        vib.rest(Duration.WHOLE)
    for note, dur in [
        ("E5", Duration.QUARTER), ("D5", Duration.QUARTER),
        ("C5", Duration.QUARTER), ("A4", Duration.QUARTER),
        ("B4", Duration.HALF), ("E5", Duration.HALF),
        ("A5", Duration.WHOLE),
    ]:
        vib.add(note, dur)

    # Acid bass — gritty texture bars 4-5
    acid = score.part("acid", instrument="acid_bass")
    for _ in range(3):
        acid.rest(Duration.WHOLE)
    for n in ["C2", "C2", "E2", "G2", "G2", "G2", "A2", "E2",
              "D2", "D2", "F2", "A2", "A2", "A2", "E2", "E2"]:
        acid.add(n, Duration.EIGHTH)
    for _ in range(2):
        acid.rest(Duration.WHOLE)

    # Half time drums
    score.drums("half time", repeats=8)

    play_song(score, "Cinematic Showcase — A minor")


def greensleeves():
    """Greensleeves — Renaissance lute, meantone tuning, A=415 Hz."""
    score = Score("3/4", bpm=120, temperament="meantone", reference_pitch=415.0)

    lute = score.part("lute", instrument="acoustic_guitar",
                      reverb=0.3, reverb_type="taj_mahal")

    melody = [
        ("A4", 1.0, 80),
        ("C5", 2.0, 85),   ("D5", 1.0, 80),
        ("E5", 3.0, 90),
        ("F5", 1.0, 75),   ("E5", 2.0, 85),
        ("D5", 1.0, 80),
        ("B4", 3.0, 85),
        ("G4", 1.0, 70),   ("B4", 2.0, 80),
        ("C5", 1.0, 75),
        ("A4", 3.0, 85),
        ("A4", 1.0, 70),   ("A4", 2.0, 75),
        ("G#4", 1.0, 70),
        ("A4", 2.0, 80),   ("B4", 1.0, 75),
        ("G4", 3.0, 85),
        ("E4", 1.0, 70),
        ("A4", 3.0, 90),
    ]

    for note, dur, vel in melody:
        lute.add(note, dur, velocity=vel)

    play_song(score, "Greensleeves — Renaissance Lute (Meantone, A=415)")


def tabla_solo_yaman():
    """Tabla solo with tanpura drone, sitar, and Raga Yaman — 22-shruti tuning."""
    shruti = SYSTEMS["shruti"]
    score = Score("4/4", bpm=160, system=shruti)
    h = _Hit

    NA = DrumSound.TABLA_NA
    TI = DrumSound.TABLA_TIN
    GE = DrumSound.TABLA_GE
    DH = DrumSound.TABLA_DHA
    TT = DrumSound.TABLA_TIT
    KE = DrumSound.TABLA_KE
    GB = DrumSound.TABLA_GE_BEND

    # Tanpura drone — Sa + Pa
    tanpura_sa = score.part("tanpura_sa", synth="strings_synth", envelope="pad",
                             detune=3, lowpass=1000, volume=0.18,
                             reverb=0.5, reverb_type="taj_mahal")
    tanpura_pa = score.part("tanpura_pa", synth="strings_synth", envelope="pad",
                             detune=3, lowpass=1400, volume=0.14,
                             reverb=0.5, reverb_type="taj_mahal")
    sa3 = Tone("Sa", octave=3, system=shruti)
    pa3 = Tone("Pa", octave=3, system=shruti)
    for _ in range(16):
        tanpura_sa.add(sa3, Duration.WHOLE)
        tanpura_pa.add(pa3, Duration.WHOLE)

    # Quiet sitar — Raga Yaman (Kalyan thaat)
    sitar = score.part("sitar", instrument="sitar", volume=0.12,
                        reverb=0.4, reverb_type="taj_mahal")
    ts = TonedScale(system=shruti, tonic=Tone("Sa", octave=4, system=shruti))
    y = list(ts["kalyan"].tones)
    S, R, G, M, P, D, N, S2 = y
    sitar.rest(Duration.WHOLE)
    sitar.rest(Duration.WHOLE)
    for tone, dur, vel in [
        (S, 3.0, 55), (R, 1.0, 50), (G, 3.0, 58), (R, 1.0, 48),
        (S, 4.0, 55), (G, 1.0, 50), (M, 1.0, 52), (P, 3.0, 58),
        (M, 1.0, 48), (G, 1.0, 50), (R, 1.0, 48), (S, 4.0, 55),
        (P, 2.0, 52), (D, 1.0, 55), (N, 2.0, 58), (S2, 3.0, 60),
        (N, 1.0, 52), (D, 1.0, 50), (P, 1.0, 52), (G, 1.0, 48),
        (R, 1.0, 48), (S, 4.0, 55),
    ]:
        sitar.add(tone, dur, velocity=vel)

    # 4 bars drone intro (silence for drums)
    silence = Pattern(name="silence", time_signature="4/4", beats=16.0, hits=[])
    score.add_pattern(silence, repeats=1)

    # Gentle opening
    p1 = Pattern(name="gentle", time_signature="4/4", beats=8.0, hits=[
        h(DH, 0.0, 80), h(NA, 2.0, 60),
        h(DH, 4.0, 85), h(NA, 5.0, 55), h(NA, 6.0, 60), h(DH, 7.0, 80),
    ])

    # Building with ghost notes
    p2 = Pattern(name="build", time_signature="4/4", beats=16.0, hits=[
        h(DH, 0.0, 95), h(TT, 0.5, 35), h(NA, 1.0, 70), h(TT, 1.5, 30),
        h(NA, 2.0, 65), h(DH, 3.0, 90),
        h(DH, 4.0, 100), h(TT, 4.25, 35), h(TT, 4.5, 40), h(NA, 5.0, 75),
        h(TT, 5.5, 35), h(NA, 6.0, 70), h(TT, 6.5, 30), h(DH, 7.0, 95),
        h(DH, 8.0, 95), h(TI, 9.0, 70), h(TI, 10.0, 72), h(NA, 11.0, 80),
        h(TT, 11.25, 40), h(TT, 11.5, 42), h(KE, 11.75, 45),
        h(TT, 12.0, 50), h(TT, 12.25, 55), h(KE, 12.5, 58), h(NA, 12.75, 70),
        h(DH, 13.0, 100), h(TT, 13.25, 40), h(TT, 13.5, 45), h(KE, 13.75, 50),
        h(NA, 14.0, 75), h(KE, 14.25, 50), h(DH, 14.5, 85), h(NA, 14.75, 70),
        h(DH, 15.0, 110), h(GB, 15.5, 100),
    ])

    # Full intensity
    p3 = Pattern(name="fire", time_signature="4/4", beats=16.0, hits=[
        h(TT, 0.0, 50), h(TT, 0.125, 35), h(TT, 0.25, 45), h(KE, 0.5, 55),
        h(NA, 0.75, 85),
        h(DH, 1.0, 115), h(TT, 1.25, 38), h(DH, 1.5, 70), h(NA, 1.75, 60),
        h(TT, 2.0, 50), h(TT, 2.125, 35), h(TT, 2.25, 48), h(KE, 2.5, 55),
        h(NA, 2.75, 88),
        h(DH, 3.0, 115), h(GB, 3.5, 105), h(NA, 3.75, 72),
        h(NA, 4.0, 115), h(NA, 4.25, 60), h(TT, 4.5, 40), h(NA, 4.75, 105),
        h(GE, 5.0, 105), h(GE, 5.25, 55), h(GB, 5.5, 95), h(GE, 5.75, 50),
        h(NA, 6.0, 115), h(TT, 6.125, 30), h(TT, 6.25, 38), h(NA, 6.5, 100),
        h(TT, 6.625, 32), h(TT, 6.75, 42),
        h(GB, 7.0, 115), h(KE, 7.25, 52), h(GE, 7.5, 72), h(KE, 7.75, 48),
        # Tihai
        h(DH, 8.0, 115), h(NA, 8.25, 78), h(TT, 8.5, 52), h(KE, 8.75, 58),
        h(DH, 9.0, 105),
        h(DH, 9.5, 110), h(NA, 9.75, 78), h(TT, 10.0, 52), h(KE, 10.25, 58),
        h(DH, 10.5, 105),
        h(DH, 11.0, 120), h(NA, 11.25, 82), h(TT, 11.5, 58), h(KE, 11.75, 62),
        h(DH, 12.0, 120),
        # Silence... then finish
        h(GB, 14.5, 120),
        h(DH, 15.5, 127), h(DH, 15.75, 127),
    ])

    score.add_pattern(p1, repeats=1)
    score.add_pattern(p2, repeats=1)
    score.add_pattern(p3, repeats=1)
    score.set_drum_effects(reverb=0.4, reverb_type="taj_mahal")

    play_song(score, "Tabla Solo — Raga Yaman (22-Shruti, Taj Mahal)")


def journey():
    """Journey — piano → orchestra → world → sitar EDM.

    One reverb space (Taj Mahal), tanpura drone throughout. Piano opens
    alone, cello joins, harp/oboe/flute take over with djembe, sitar
    arrives over tabla, builds to an EDM section with house drums.
    """
    REV = "taj_mahal"
    score = Score("4/4", bpm=72)

    # ── Drone — runs the entire piece ──
    tanpura = score.part("tanpura", synth="strings_synth", envelope="pad",
                          detune=3, lowpass=1000, volume=0.12,
                          reverb=0.6, reverb_type=REV)
    for _ in range(40):
        tanpura.add("A2", Duration.WHOLE)

    # ── Bars 1-8: Piano alone, then cello ──
    piano = score.part("piano", instrument="piano", volume=0.35,
                        reverb=0.6, reverb_type=REV)
    for notes in [
        ["A2","E3","A3","C4","E4","C4","A3","E3"],
        ["F2","C3","F3","A3","C4","A3","F3","C3"],
        ["G2","D3","G3","B3","D4","B3","G3","D3"],
        ["E2","B2","E3","G#3","B3","G#3","E3","B2"],
        ["A2","E3","A3","C4","E4","C4","A3","E3"],
        ["D2","A2","D3","F3","A3","F3","D3","A2"],
        ["E2","B2","E3","G#3","B3","G#3","E3","B2"],
        ["A2","E3","A3","C4","E4","A4","E4","C4"],
    ]:
        for n in notes:
            piano.add(n, Duration.EIGHTH, velocity=68)

    cello = score.part("cello", instrument="cello", volume=0.2,
                        reverb=0.55, reverb_type=REV)
    cello.rest(Duration.WHOLE)
    for note, dur, vel in [
        ("A3", 4.0, 55), ("C4", 4.0, 58),
        ("B3", 2.0, 52), ("A3", 2.0, 50), ("G3", 4.0, 55),
        ("F3", 4.0, 52), ("E3", 4.0, 55), ("A3", 4.0, 58),
    ]:
        cello.add(note, dur, velocity=vel)

    # ── Bars 9-16: Harp + oboe + flute + djembe ──
    harp = score.part("harp", instrument="harp", volume=0.28,
                       reverb=0.6, reverb_type=REV)
    oboe = score.part("oboe", instrument="oboe", volume=0.22,
                       reverb=0.55, reverb_type=REV)
    flute = score.part("flute", instrument="flute", volume=0.18,
                        reverb=0.55, reverb_type=REV)
    for _ in range(8):
        harp.rest(Duration.WHOLE)
    for notes in [
        ["A3","C4","E4","A4","C5","E5","A5","E5"],
        ["D3","F3","A3","D4","F4","A4","D5","A4"],
        ["E3","G3","B3","E4","G4","B4","E5","B4"],
        ["A3","C4","E4","A4","E5","C5","A4","E4"],
        ["F3","A3","C4","F4","A4","C5","F5","C5"],
        ["E3","G#3","B3","E4","G#4","B4","E5","B4"],
    ]:
        for n in notes:
            harp.add(n, Duration.EIGHTH, velocity=58)
    for _ in range(9):
        oboe.rest(Duration.WHOLE)
    for note, dur, vel in [
        ("E5", 1.5, 62), ("D5", 0.5, 55), ("C5", 1.0, 58),
        ("A4", 1.0, 62), ("G4", 1.0, 55), ("A4", 1.5, 58),
        ("B4", 0.5, 52), ("C5", 2.0, 62), ("A4", 4.0, 58),
    ]:
        oboe.add(note, dur, velocity=vel)
    for _ in range(10):
        flute.rest(Duration.WHOLE)
    for note, dur, vel in [
        ("A5", 2.0, 50), ("G5", 1.0, 45), ("E5", 1.0, 48),
        ("D5", 2.0, 50), ("C5", 1.0, 45), ("A4", 1.0, 48),
        ("G4", 2.0, 50), ("A4", 2.0, 52),
    ]:
        flute.add(note, dur, velocity=vel)

    # ── Bars 15-20: Sitar + tabla ──
    sitar = score.part("sitar", instrument="sitar", volume=0.2,
                        reverb=0.6, reverb_type=REV)
    for _ in range(14):
        sitar.rest(Duration.WHOLE)
    for note, dur, vel in [
        ("A4", 1.0, 70), ("Bb4", 0.5, 60), ("A4", 0.5, 65),
        ("C5", 1.5, 75), ("Bb4", 0.5, 60),
        ("D5", 1.0, 70), ("E5", 1.5, 78),
        ("F5", 0.5, 62), ("E5", 1.0, 70),
        ("D5", 0.5, 62), ("C5", 0.5, 65), ("Bb4", 0.5, 58),
        ("A4", 2.0, 75),
        ("Bb4", 0.25, 55), ("C5", 0.25, 58), ("D5", 0.25, 62),
        ("E5", 0.25, 68),
        ("F5", 0.25, 65), ("G5", 0.25, 70), ("A5", 0.5, 80),
        ("G5", 0.25, 62), ("F5", 0.25, 58), ("E5", 0.5, 62),
        ("C5", 0.5, 58), ("Bb4", 0.5, 55), ("A4", 2.0, 75),
    ]:
        sitar.add(note, dur, velocity=vel)

    # ── EDM section — sitar over house beat ──
    # Solo sections: 8+8+8+12 = 36 beats = 9 bars
    # Total bars before EDM: 8 piano + 6 harp + 6 djembe + 4 tabla + 9 solo = 33
    edm_start = 33
    pad = score.part("pad", instrument="synth_pad", volume=0.18,
                      reverb=0.6, reverb_type=REV,
                      sidechain=0.6, sidechain_release=0.15)
    for _ in range(edm_start):
        pad.rest(Duration.WHOLE)
    for sym in ["Am", "F", "G", "Em"] * 2:
        pad.add(Chord.from_symbol(sym), Duration.WHOLE)

    sub = score.part("sub", instrument="808_bass", volume=0.4)
    for _ in range(edm_start):
        sub.rest(Duration.WHOLE)
    for n in ["A1","A1","F1","F1","G1","G1","E1","E1"] * 2:
        sub.add(n, Duration.HALF)

    sitar2 = score.part("sitar2", instrument="sitar", volume=0.4,
                         reverb=0.3, reverb_type=REV)
    for _ in range(edm_start + 2):
        sitar2.rest(Duration.WHOLE)
    for note, dur, vel in [
        ("A4", 0.25, 75), ("C5", 0.25, 78), ("E5", 0.5, 85),
        ("D5", 0.25, 72), ("C5", 0.25, 70), ("A4", 0.5, 75),
        ("G4", 0.25, 68), ("A4", 0.25, 72), ("C5", 0.5, 78),
        ("A4", 0.5, 72),
        ("E5", 0.5, 82), ("D5", 0.25, 72), ("C5", 0.25, 70),
        ("A4", 0.5, 75), ("G4", 0.5, 68), ("A4", 1.0, 78),
    ] * 2:
        sitar2.add(note, dur, velocity=vel)

    # Drums: djembe bars 9-14, tabla bars 15-20, house bars 21-28
    DJB = DrumSound.DJEMBE_BASS
    DJT = DrumSound.DJEMBE_TONE
    DJS = DrumSound.DJEMBE_SLAP
    NA = DrumSound.TABLA_NA
    DH = DrumSound.TABLA_DHA
    TT = DrumSound.TABLA_TIT
    GB = DrumSound.TABLA_GE_BEND

    silence = Pattern(name="s", time_signature="4/4", beats=32.0, hits=[])
    score.add_pattern(silence, repeats=1)
    p_dj = Pattern(name="dj", time_signature="4/4", beats=8.0, hits=[
        _Hit(DJB, 0.0, 48), _Hit(DJT, 1.0, 40), _Hit(DJT, 1.5, 35),
        _Hit(DJS, 2.0, 45), _Hit(DJT, 3.0, 40),
        _Hit(DJB, 4.0, 52), _Hit(DJT, 5.0, 42), _Hit(DJT, 5.5, 38),
        _Hit(DJS, 6.0, 48), _Hit(DJT, 6.5, 35), _Hit(DJS, 7.0, 45),
    ])
    score.add_pattern(p_dj, repeats=3)
    p_tab = Pattern(name="tab", time_signature="4/4", beats=8.0, hits=[
        _Hit(DH, 0.0, 80), _Hit(TT, 0.5, 30), _Hit(NA, 1.0, 65),
        _Hit(NA, 2.0, 60), _Hit(DH, 3.0, 80),
        _Hit(DH, 4.0, 85), _Hit(TT, 4.25, 32), _Hit(TT, 4.5, 35),
        _Hit(NA, 5.0, 68), _Hit(TT, 5.5, 30), _Hit(NA, 6.0, 65),
        _Hit(DH, 7.0, 85),
    ])
    score.add_pattern(p_tab, repeats=2)

    # Tabla solo — everything drops out, just tabla and drone
    KE = DrumSound.TABLA_KE
    TI = DrumSound.TABLA_TIN
    GE = DrumSound.TABLA_GE
    T3 = 1.0 / 12.0   # 32nd triplet
    T9 = 1.0 / 9.0    # ninth note

    # Part 1: whisper — space, breath, single hits
    p_solo1 = Pattern(name="solo1", time_signature="4/4", beats=8.0, hits=[
        _Hit(DH, 0.0, 78),
        _Hit(NA, 2.0, 55),
        _Hit(DH, 4.0, 82),
        _Hit(TT, 5.0, 30), _Hit(NA, 5.5, 52), _Hit(TT, 6.0, 28),
        _Hit(DH, 7.0, 78),
    ])
    score.add_pattern(p_solo1, repeats=1)

    # Part 2: ghosts emerge — 16th note ghost fills between accents
    p_solo2 = Pattern(name="solo2", time_signature="4/4", beats=8.0, hits=[
        _Hit(DH, 0.0, 92), _Hit(TT, 0.25, 32), _Hit(TT, 0.5, 35),
        _Hit(NA, 1.0, 68), _Hit(TT, 1.25, 30), _Hit(TT, 1.5, 28),
        _Hit(NA, 2.0, 62), _Hit(TT, 2.5, 32), _Hit(DH, 3.0, 88),
        _Hit(TT, 3.25, 35), _Hit(TT, 3.5, 38),
        _Hit(DH, 4.0, 95), _Hit(TT, 4.25, 38), _Hit(TT, 4.5, 42),
        _Hit(NA, 5.0, 72), _Hit(TT, 5.25, 32), _Hit(TT, 5.5, 35),
        _Hit(KE, 5.75, 40),
        _Hit(NA, 6.0, 68), _Hit(TT, 6.25, 35), _Hit(KE, 6.5, 38),
        _Hit(DH, 7.0, 95), _Hit(GB, 7.5, 88),
    ])
    score.add_pattern(p_solo2, repeats=1)

    # Part 3: call and response — dayan vs bayan, dynamics wide open
    p_solo3 = Pattern(name="solo3", time_signature="4/4", beats=8.0, hits=[
        # Dayan speaks
        _Hit(NA, 0.0, 110), _Hit(NA, 0.25, 55), _Hit(TT, 0.5, 38),
        _Hit(NA, 0.75, 100),
        # Bayan answers
        _Hit(GE, 1.0, 100), _Hit(GE, 1.25, 50), _Hit(GB, 1.5, 90),
        _Hit(GE, 1.75, 45),
        # Dayan louder
        _Hit(NA, 2.0, 115), _Hit(TT, 2.125, 30), _Hit(TT, 2.25, 35),
        _Hit(NA, 2.5, 105), _Hit(TT, 2.625, 32), _Hit(TT, 2.75, 38),
        # Bayan louder
        _Hit(GB, 3.0, 112), _Hit(KE, 3.25, 50), _Hit(GE, 3.5, 68),
        _Hit(KE, 3.75, 45),
        # Together — explosion
        _Hit(DH, 4.0, 120), _Hit(TT, 4.25, 45), _Hit(TT, 4.5, 48),
        _Hit(DH, 5.0, 115), _Hit(TT, 5.25, 42), _Hit(NA, 5.5, 72),
        # 9-tuplet — the weird one, breaks the grid
        *[_Hit(TT if i % 2 == 0 else KE, 6.0 + i * T9, 38 + i * 5)
          for i in range(9)],
        _Hit(DH, 7.0, 118),
    ])
    score.add_pattern(p_solo3, repeats=1)

    # Part 4: blazing — 32nd triplets, cascades, tihai finale
    p_solo4 = Pattern(name="solo4", time_signature="4/4", beats=12.0, hits=[
        # 32nd triplet opening flourish
        *[_Hit(TT, 0.0 + i * T3, 40 + i * 2) for i in range(12)],
        _Hit(DH, 1.0, 120), _Hit(GB, 1.5, 108),
        # Rapid alternating hands
        _Hit(NA, 2.0, 110), _Hit(KE, 2.125, 45), _Hit(NA, 2.25, 105),
        _Hit(KE, 2.375, 48), _Hit(NA, 2.5, 108), _Hit(KE, 2.625, 50),
        _Hit(NA, 2.75, 112),
        _Hit(DH, 3.0, 118),
        # Another 32nd triplet burst — longer, crescendo
        *[_Hit(TT, 3.5 + i * T3, 32 + i * 4) for i in range(18)],
        _Hit(DH, 5.0, 122), _Hit(DH, 5.25, 118), _Hit(GB, 5.5, 115),
        # 9 against 4 polyrhythm moment
        _Hit(GE, 6.0, 88), _Hit(GE, 7.0, 85),
        *[_Hit(NA if i % 3 == 0 else TT, 6.0 + i * (2.0 / 9.0), 42 + (i % 3) * 15)
          for i in range(9)],
        # Grand tihai — 3x pattern, each louder
        _Hit(DH, 8.0, 108), _Hit(NA, 8.25, 72), _Hit(TT, 8.5, 48),
        _Hit(KE, 8.75, 52), _Hit(DH, 9.0, 100),
        _Hit(DH, 9.25, 112), _Hit(NA, 9.5, 78), _Hit(TT, 9.75, 52),
        _Hit(KE, 10.0, 58), _Hit(DH, 10.25, 108),
        _Hit(DH, 10.5, 120), _Hit(NA, 10.75, 85), _Hit(TT, 11.0, 58),
        _Hit(KE, 11.25, 62), _Hit(DH, 11.5, 127),
        # Silence.....
        # SLAM
        _Hit(GB, 11.875, 127),
    ])
    score.add_pattern(p_solo4, repeats=1)

    score.drums("house", repeats=8)
    score.set_drum_effects(reverb=0.3, reverb_type=REV)

    play_song(score, "Journey — Piano → World → Sitar EDM (Taj Mahal)")


def epic_bhairav():
    """Epic Bhairav — orchestral + choir + tabla with extended solo finale."""
    shruti = SYSTEMS["shruti"]
    score = Score("4/4", bpm=90, system=shruti)
    REV = "taj_mahal"
    T3 = 1.0 / 12.0
    T9 = 1.0 / 9.0

    ts = TonedScale(system=shruti, tonic=Tone("Sa", octave=4, system=shruti))
    bh = list(ts["bhairav"].tones)
    S, kR, G, M, P, kD, N, S2 = bh

    NA = DrumSound.TABLA_NA
    DH = DrumSound.TABLA_DHA
    TT = DrumSound.TABLA_TIT
    KE = DrumSound.TABLA_KE
    GB = DrumSound.TABLA_GE_BEND
    GE = DrumSound.TABLA_GE
    DJB = DrumSound.DJEMBE_BASS
    DJT = DrumSound.DJEMBE_TONE
    DJS = DrumSound.DJEMBE_SLAP

    # Tanpura
    tanpura = score.part("tanpura", synth="strings_synth", envelope="pad",
                          detune=3, lowpass=900, volume=0.14, reverb=0.4, reverb_type=REV)
    tanpura_pa = score.part("tanpura_pa", synth="strings_synth", envelope="pad",
                             detune=3, lowpass=1200, volume=0.1, reverb=0.4, reverb_type=REV)
    sa = Tone("Sa", octave=3, system=shruti)
    pa = Tone("Pa", octave=3, system=shruti)
    for _ in range(34):
        tanpura.add(sa, Duration.WHOLE)
        tanpura_pa.add(pa, Duration.WHOLE)

    # Timpani
    timp = score.part("timp", instrument="timpani")
    timp.roll(Tone("Sa", octave=2, system=shruti), Duration.WHOLE,
              velocity_start=20, velocity_end=90, speed=0.125)
    timp.add(Tone("Sa", octave=2, system=shruti), Duration.HALF, velocity=105)
    timp.rest(Duration.HALF)
    for _ in range(8):
        timp.rest(Duration.WHOLE)
    timp.roll(Tone("Sa", octave=2, system=shruti), Duration.WHOLE,
              velocity_start=25, velocity_end=115, speed=0.125)
    timp.add(Tone("Sa", octave=2, system=shruti), Duration.HALF, velocity=120)
    timp.add(Tone("Pa", octave=2, system=shruti), Duration.HALF, velocity=115)

    # Choir — bar 3
    choir = score.part("choir", synth="vocal_synth", envelope="pad",
                        detune=8, spread=0.4, reverb=0.4, reverb_type=REV, volume=0.2)
    for _ in range(2):
        choir.rest(Duration.WHOLE)
    for tone, dur, lyric, vel in [
        (S, 4.0, "ah", 60), (M, 4.0, "oh", 62), (P, 4.0, "ah", 68),
        (S, 4.0, "ee", 65), (kD, 4.0, "oh", 70), (P, 4.0, "ah", 72),
    ]:
        choir.add(tone, dur, velocity=vel, lyric=lyric)

    # Bansuri — bar 5
    bansuri = score.part("bansuri", instrument="flute", volume=0.22,
                          reverb=0.4, reverb_type=REV)
    for _ in range(4):
        bansuri.rest(Duration.WHOLE)
    for tone, dur, vel in [
        (P, 2.0, 58), (kD, 1.0, 50), (P, 1.0, 55),
        (M, 2.0, 55), (G, 1.0, 50), (kR, 1.0, 48), (S, 4.0, 58),
    ]:
        bansuri.add(tone, dur, velocity=vel)

    # Cello — bar 3
    cello = score.part("cello", instrument="cello", volume=0.22, reverb=0.4, reverb_type=REV)
    for _ in range(2):
        cello.rest(Duration.WHOLE)
    for name, dur, vel in [
        ("Sa", 4.0, 55), ("Ma", 4.0, 52), ("Pa", 4.0, 58),
        ("Sa", 4.0, 55), ("komal Dha", 4.0, 58), ("Pa", 4.0, 55),
    ]:
        cello.add(Tone(name, octave=2, system=shruti), dur, velocity=vel)

    # Sitar — bar 9
    sitar = score.part("sitar", instrument="sitar", volume=0.25, reverb=0.4, reverb_type=REV)
    for _ in range(8):
        sitar.rest(Duration.WHOLE)
    for tone, dur, vel in [
        (S, 1.0, 72), (kR, 0.5, 62), (S, 0.5, 68), (G, 2.0, 78),
        (M, 1.0, 72), (P, 2.0, 82), (kD, 0.5, 65), (P, 1.0, 75),
        (M, 0.5, 65), (G, 0.5, 68), (kR, 0.5, 60), (S, 2.0, 78),
        (kR, 0.25, 62), (G, 0.25, 65), (M, 0.25, 70), (P, 0.25, 75),
        (kD, 0.25, 70), (N, 0.25, 78), (S2, 0.5, 88),
        (N, 0.25, 68), (kD, 0.25, 62), (P, 0.5, 68),
        (M, 0.5, 62), (G, 0.5, 65), (kR, 0.5, 58), (S, 2.0, 80),
    ]:
        sitar.add(tone, dur, velocity=vel)

    # Strings — bar 13
    strings = score.part("strings", instrument="string_ensemble", volume=0.18,
                          reverb=0.4, reverb_type=REV)
    for _ in range(12):
        strings.rest(Duration.WHOLE)
    for name, dur, vel in [("Sa", 4.0, 58), ("Ma", 4.0, 62), ("Pa", 4.0, 68), ("Sa", 4.0, 72)]:
        strings.add(Tone(name, octave=3, system=shruti), dur, velocity=vel)

    # Harp — bar 14
    harp = score.part("harp", instrument="harp", volume=0.15, reverb=0.4, reverb_type=REV)
    for _ in range(13):
        harp.rest(Duration.WHOLE)
    for name in ["Sa", "komal Ga", "Pa", "Sa", "Pa", "komal Ga", "Sa", "Sa"]:
        oct = 4 if name == "Sa" and harp.total_beats > 55 else 3
        harp.add(Tone(name, octave=oct, system=shruti), Duration.EIGHTH, velocity=50)

    # Drums
    silence = Pattern(name="s", time_signature="4/4", beats=16.0, hits=[])
    score.add_pattern(silence, repeats=1)
    p_dj = Pattern(name="dj", time_signature="4/4", beats=8.0, hits=[
        _Hit(DJB, 0.0, 45), _Hit(DJT, 1.0, 38), _Hit(DJT, 1.5, 32),
        _Hit(DJS, 2.0, 42), _Hit(DJT, 3.0, 38),
        _Hit(DJB, 4.0, 50), _Hit(DJT, 5.0, 42), _Hit(DJT, 5.5, 35),
        _Hit(DJS, 6.0, 48), _Hit(DJT, 6.5, 32), _Hit(DJS, 7.0, 45),
    ])
    score.add_pattern(p_dj, repeats=2)
    p_tab = Pattern(name="tab", time_signature="4/4", beats=8.0, hits=[
        _Hit(DH, 0.0, 82), _Hit(TT, 0.5, 30), _Hit(NA, 1.0, 65),
        _Hit(NA, 2.0, 60), _Hit(DH, 3.0, 82),
        _Hit(DH, 4.0, 88), _Hit(TT, 4.25, 32), _Hit(TT, 4.5, 35),
        _Hit(NA, 5.0, 68), _Hit(TT, 5.5, 30), _Hit(NA, 6.0, 65),
        _Hit(DH, 7.0, 88),
    ])
    score.add_pattern(p_tab, repeats=3)

    # Extended tabla finale — whisper → ghosts → call/response → blazing
    p_f1 = Pattern(name="f1", time_signature="4/4", beats=8.0, hits=[
        _Hit(DH, 0.0, 78), _Hit(NA, 2.0, 55),
        _Hit(DH, 4.0, 82), _Hit(TT, 5.0, 30), _Hit(NA, 5.5, 52),
        _Hit(DH, 7.0, 78),
    ])
    score.add_pattern(p_f1, repeats=1)
    p_f2 = Pattern(name="f2", time_signature="4/4", beats=8.0, hits=[
        _Hit(DH, 0.0, 95), _Hit(TT, 0.25, 35), _Hit(TT, 0.5, 38),
        _Hit(NA, 1.0, 70), _Hit(TT, 1.25, 30), _Hit(NA, 2.0, 65),
        _Hit(TT, 2.5, 35), _Hit(DH, 3.0, 90),
        _Hit(DH, 4.0, 98), _Hit(TT, 4.25, 38), _Hit(TT, 4.5, 42),
        _Hit(NA, 5.0, 75), _Hit(KE, 5.5, 40), _Hit(NA, 6.0, 70),
        _Hit(KE, 6.5, 42), _Hit(DH, 7.0, 100), _Hit(GB, 7.5, 92),
    ])
    score.add_pattern(p_f2, repeats=1)
    p_f3 = Pattern(name="f3", time_signature="4/4", beats=8.0, hits=[
        _Hit(NA, 0.0, 112), _Hit(NA, 0.25, 58), _Hit(TT, 0.5, 40), _Hit(NA, 0.75, 105),
        _Hit(GE, 1.0, 105), _Hit(GE, 1.25, 52), _Hit(GB, 1.5, 95), _Hit(GE, 1.75, 48),
        _Hit(NA, 2.0, 115), _Hit(TT, 2.125, 32), _Hit(TT, 2.25, 38),
        _Hit(NA, 2.5, 108), _Hit(TT, 2.625, 35), _Hit(TT, 2.75, 42),
        _Hit(GB, 3.0, 115), _Hit(KE, 3.25, 52), _Hit(GE, 3.5, 70),
        _Hit(DH, 4.0, 118),
        *[_Hit(TT if i % 2 == 0 else KE, 5.0 + i * T9, 40 + i * 5) for i in range(9)],
        _Hit(DH, 7.0, 120),
    ])
    score.add_pattern(p_f3, repeats=1)

    # Part 3.5: polyrhythm — space and conversation, not density
    T5 = 4.0 / 5.0
    p_poly = Pattern(name="poly", time_signature="4/4", beats=16.0, hits=[
        # Bar 1: single Dha, let reverb ring. Bayan answers.
        _Hit(DH, 0.0, 95),
        _Hit(GB, 3.0, 88),
        # Bar 2: one 5-group phrase, then breathe
        _Hit(NA, 4.0, 75), _Hit(TT, 4.0 + T5, 42),
        _Hit(NA, 4.0 + 2*T5, 70), _Hit(TT, 4.0 + 3*T5, 40),
        _Hit(DH, 4.0 + 4*T5, 88),
        # Bar 3: bayan, pause, one floating 9-group
        _Hit(GB, 8.0, 100),
        _Hit(NA, 9.0, 62),
        *[_Hit(TT if i % 2 == 0 else KE, 10.0 + i * T9, 35 + i * 4)
          for i in range(9)],
        _Hit(DH, 11.0, 105),
        # Bar 4: simple question-answer into sam
        _Hit(DH, 12.0, 100), _Hit(NA, 12.5, 62),
        _Hit(GE, 13.0, 88),
        _Hit(NA, 14.0, 72), _Hit(TT, 14.25, 40), _Hit(NA, 14.5, 70),
        _Hit(DH, 15.0, 112), _Hit(GB, 15.5, 105),
    ])
    score.add_pattern(p_poly, repeats=1)

    p_f4 = Pattern(name="f4", time_signature="4/4", beats=12.0, hits=[
        *[_Hit(TT, 0.0 + i * T3, 38 + i * 2) for i in range(12)],
        _Hit(DH, 1.0, 118), _Hit(GB, 1.5, 110),
        _Hit(NA, 2.0, 112), _Hit(KE, 2.125, 48), _Hit(NA, 2.25, 108),
        _Hit(KE, 2.375, 50), _Hit(NA, 2.5, 110), _Hit(KE, 2.625, 52), _Hit(NA, 2.75, 115),
        _Hit(DH, 3.0, 120),
        *[_Hit(TT, 3.5 + i * T3, 30 + i * 4) for i in range(18)],
        _Hit(DH, 5.0, 122), _Hit(DH, 5.25, 118), _Hit(GB, 5.5, 115),
        _Hit(GE, 6.0, 90), _Hit(GE, 7.0, 88),
        *[_Hit(NA if i % 3 == 0 else TT, 6.0 + i * (2.0/9.0), 42 + (i%3)*15) for i in range(9)],
        _Hit(DH, 8.0, 110), _Hit(NA, 8.25, 75), _Hit(TT, 8.5, 50),
        _Hit(KE, 8.75, 55), _Hit(DH, 9.0, 105),
        _Hit(DH, 9.25, 115), _Hit(NA, 9.5, 80), _Hit(TT, 9.75, 55),
        _Hit(KE, 10.0, 60), _Hit(DH, 10.25, 110),
        _Hit(DH, 10.5, 122), _Hit(NA, 10.75, 85), _Hit(TT, 11.0, 60),
        _Hit(KE, 11.25, 65), _Hit(DH, 11.5, 127),
        _Hit(GB, 11.875, 127),
    ])
    score.add_pattern(p_f4, repeats=1)
    score.set_drum_effects(reverb=0.4, reverb_type=REV)

    play_song(score, "Epic Bhairav — Orchestra + Choir + Tabla (22-Shruti JI)")


def acoustic_ensemble():
    """Acoustic Ensemble — guitar, ukulele, mandolin, cajón."""
    import random
    from pytheory import Fretboard
    random.seed(7)
    score = Score("4/4", bpm=115)

    fb_g = Fretboard.guitar()
    guitar = score.part("guitar", instrument="acoustic_guitar", fretboard=fb_g,
                         reverb=0.3, reverb_type="plate", humanize=0.2, pan=-0.3)

    fb_u = Fretboard.ukulele()
    uke = score.part("uke", instrument="ukulele", fretboard=fb_u,
                      reverb=0.25, reverb_type="plate", humanize=0.25, pan=0.3)

    fb_m = Fretboard.mandolin()
    mando = score.part("mando", instrument="mandolin", fretboard=fb_m,
                        reverb=0.25, reverb_type="plate", humanize=0.2, pan=0.15)

    for sym in ["C", "G", "Am", "F"] * 3:
        vd = random.randint(75, 95)
        vu = random.randint(58, 78)
        guitar.strum(sym, Duration.QUARTER, direction="down", velocity=vd)
        guitar.strum(sym, Duration.EIGHTH, direction="up", velocity=vu)
        guitar.strum(sym, Duration.EIGHTH, direction="down", velocity=vd - 8)
        guitar.strum(sym, Duration.QUARTER, direction="up", velocity=vu)
        guitar.strum(sym, Duration.QUARTER, direction="down", velocity=vd)

        vd2 = random.randint(65, 88)
        vu2 = random.randint(50, 72)
        uke.rest(Duration.EIGHTH)
        uke.strum(sym, Duration.EIGHTH, direction="up", velocity=vu2)
        uke.strum(sym, Duration.QUARTER, direction="down", velocity=vd2)
        uke.strum(sym, Duration.EIGHTH, direction="up", velocity=vu2)
        uke.strum(sym, Duration.EIGHTH, direction="down", velocity=vd2 - 5)
        uke.strum(sym, Duration.QUARTER, direction="up", velocity=vu2)

        mando.strum(sym, Duration.EIGHTH, direction="down",
                    velocity=random.randint(65, 82))
        mando.strum(sym, Duration.EIGHTH, direction="up",
                    velocity=random.randint(55, 72))
        mando.strum(sym, Duration.EIGHTH, direction="down",
                    velocity=random.randint(65, 82))
        mando.rest(Duration.EIGHTH)
        mando.strum(sym, Duration.EIGHTH, direction="up",
                    velocity=random.randint(55, 72))
        mando.strum(sym, Duration.EIGHTH, direction="down",
                    velocity=random.randint(68, 85))
        mando.strum(sym, Duration.QUARTER, direction="down",
                    velocity=random.randint(70, 85))

    score.drums("cajon", repeats=6)
    score.set_drum_effects(reverb=0.15)

    play_song(score, "Acoustic Ensemble — Guitar, Uke, Mandolin, Cajón")


SONGS = {
    "1": ("Bossa Nova in A minor", bossa_nova_girl),
    "2": ("Bebop in Bb major", bebop_in_bb),
    "3": ("Salsa Descarga in D minor", salsa_descarga),
    "4": ("Afrobeat in E minor", afrobeat_groove),
    "5": ("Reggae One-Drop in G major", reggae_one_drop),
    "6": ("Funk Workout in E minor", funk_workout),
    "7": ("12/8 Blues Shuffle in A", blues_shuffle),
    "8": ("Samba in G major", samba_de_janeiro),
    "9": ("Jazz Waltz in F major", jazz_waltz),
    "10": ("House Anthem in C minor", house_anthem),
    "11": ("Kingston After Dark (Dub)", dub_kingston),
    "12": ("Minimal Techno in F minor", techno_minimal),
    "13": ("Gospel Shuffle in C major", gospel_shuffle),
    "14": ("Dub Delay Madness in E minor", dub_delay_madness),
    "15": ("Liquid DnB in A minor", drum_and_bass),
    "16": ("Late Night Texts (Drake-style)", drake_vibes),
    "17": ("Neon Grid (Stereo Acid)", neon_grid),
    "18": ("Glass and Silk (Sine+Triangle)", glass_and_silk),
    "19": ("Dance Party at the Reitz House", dance_party),
    "20": ("Temple Bell (Japanese)", temple_bell),
    "21": ("Cinematic Showcase (Orchestral)", cinematic_showcase),
    "22": ("Greensleeves (Renaissance Lute)", greensleeves),
    "23": ("Tabla Solo (Raga Yaman)", tabla_solo_yaman),
    "24": ("Journey (Western → World → Indian)", journey),
    "25": ("Epic Bhairav (Orchestral + Tabla)", epic_bhairav),
    "26": ("Acoustic Ensemble (Guitar+Uke+Mando+Cajón)", acoustic_ensemble),
}

if __name__ == "__main__":
    try:
        print()
        print("  PyTheory Song Player")
        print("  " + "=" * 40)
        print()

        for key, (name, _) in SONGS.items():
            print(f"    {key:>2}. {name}")

        print()
        choice = input("  Pick a song (1-26, or 'all'): ").strip()
        print()

        if choice == "all":
            for _, (_, fn) in SONGS.items():
                fn()
                print()
        elif choice in SONGS:
            SONGS[choice][1]()
        else:
            print("  Playing all songs...")
            for _, (_, fn) in SONGS.items():
                fn()
                print()
    except KeyboardInterrupt:
        sd.stop()
        print("\n\n  Bye!")
