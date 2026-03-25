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

from pytheory import Chord, Key, Pattern, Duration, Score
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

    rhodes = score.part("rhodes", synth="fm", envelope="piano",
                        volume=0.3, reverb=0.4, reverb_decay=1.8)
    lead = score.part("lead", synth="triangle", envelope="pluck",
                      volume=0.45, delay=0.25, delay_time=0.32,
                      delay_feedback=0.35, reverb=0.2)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.45, lowpass=600)

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

    rhodes = score.part("rhodes", synth="fm", envelope="piano",
                        volume=0.25, reverb=0.35, reverb_decay=1.2)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      volume=0.4, lowpass=4000, lowpass_q=1.1)
    bass = score.part("bass", synth="triangle", envelope="pluck",
                      volume=0.4, lowpass=900)

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
                      volume=0.2, reverb=0.3, lowpass=2000)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      volume=0.4, delay=0.2, delay_time=0.167,
                      delay_feedback=0.3)
    bass = score.part("bass", synth="pulse", envelope="pluck",
                      volume=0.45, lowpass=500, lowpass_q=1.3)

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

    pads = score.part("pads", synth="supersaw", envelope="pad",
                      volume=0.2, reverb=0.4, reverb_decay=2.0,
                      lowpass=3000)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      volume=0.4, lowpass=3000, lowpass_q=1.0)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.5, lowpass=500)

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
                        volume=0.2, reverb=0.5, reverb_decay=2.0,
                        lowpass=2000)
    lead = score.part("lead", synth="triangle", envelope="strings",
                      volume=0.4, delay=0.35, delay_time=0.5625,
                      delay_feedback=0.45, reverb=0.3)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.55, lowpass=400, lowpass_q=1.3)

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
                        volume=0.25, lowpass=2500, reverb=0.15)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      volume=0.4, lowpass=3500, lowpass_q=1.5,
                      delay=0.15, delay_time=0.15, delay_feedback=0.25)
    bass = score.part("bass", synth="pulse", envelope="pluck",
                      volume=0.5, lowpass=600, lowpass_q=1.2)

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

    chords = score.part("chords", synth="fm", envelope="piano",
                        volume=0.3, reverb=0.3, reverb_decay=1.5)
    lead = score.part("lead", synth="saw", envelope="pluck",
                      volume=0.45, reverb=0.3, reverb_decay=1.2,
                      delay=0.2, delay_time=0.43, delay_feedback=0.3,
                      lowpass=3500)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.5, lowpass=500)

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

    pads = score.part("pads", synth="supersaw", envelope="pad",
                      volume=0.2, reverb=0.45, reverb_decay=2.0,
                      lowpass=4000)
    lead = score.part("lead", synth="triangle", envelope="pluck",
                      volume=0.45, delay=0.2, delay_time=0.176,
                      delay_feedback=0.3)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.45, lowpass=700)

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

    rhodes = score.part("rhodes", synth="fm", envelope="piano",
                        volume=0.3, reverb=0.4, reverb_decay=2.0)
    lead = score.part("lead", synth="triangle", envelope="strings",
                      volume=0.4, reverb=0.3, reverb_decay=1.5,
                      delay=0.2, delay_time=0.4, delay_feedback=0.3)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.4, lowpass=600)

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

    pads = score.part("pads", synth="supersaw", envelope="pad",
                      volume=0.25, reverb=0.5, reverb_decay=2.5,
                      lowpass=5000)
    lead = score.part("lead", synth="saw", envelope="staccato",
                      volume=0.35, lowpass=2000, lowpass_q=2.0,
                      delay=0.2, delay_time=0.242,
                      delay_feedback=0.35)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.55, lowpass=300)

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
                        volume=0.2, reverb=0.6, reverb_decay=2.5,
                        lowpass=1500, lowpass_q=0.9)
    lead = score.part("lead", synth="triangle", envelope="strings",
                      volume=0.4, delay=0.45, delay_time=0.625,
                      delay_feedback=0.5, reverb=0.35, reverb_decay=2.0)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.6, lowpass=400, lowpass_q=1.5)
    siren = score.part("siren", synth="pwm_slow", envelope="pad",
                       volume=0.15, reverb=0.7, reverb_decay=3.0,
                       lowpass=1200)

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

    pad = score.part("pad", synth="supersaw", envelope="pad",
                     volume=0.2, reverb=0.5, reverb_decay=3.0,
                     lowpass=3000)
    lead = score.part("lead", synth="pwm_fast", envelope="staccato",
                      volume=0.35, lowpass=1500, lowpass_q=3.0,
                      delay=0.3, delay_time=0.231,
                      delay_feedback=0.4)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.55, lowpass=250)

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

    organ = score.part("organ", synth="fm", envelope="organ",
                       volume=0.3, reverb=0.45, reverb_decay=2.0)
    lead = score.part("lead", synth="triangle", envelope="pluck",
                      volume=0.4, delay=0.2, delay_time=0.278,
                      delay_feedback=0.3, reverb=0.2)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.45, lowpass=500)

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


# ── Main ───────────────────────────────────────────────────────────────────

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
        choice = input("  Pick a song (1-13, or 'all'): ").strip()
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
