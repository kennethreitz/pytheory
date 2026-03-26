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
                        volume=0.15, reverb=0.7, reverb_decay=3.0,
                        lowpass=1200)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.6, lowpass=350, lowpass_q=1.5)
    siren = score.part("siren", synth="pwm_slow", envelope="pad",
                       volume=0.12, reverb=0.8, reverb_decay=4.0,
                       delay=0.4, delay_time=0.88, delay_feedback=0.6,
                       lowpass=900)
    # Melodica stabs — sparse, lots of delay
    melodica = score.part("melodica", synth="triangle", envelope="pluck",
                          volume=0.35, delay=0.6, delay_time=0.66,
                          delay_feedback=0.55, reverb=0.5, reverb_decay=2.5)

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

    pads = score.part("pads", synth="supersaw", envelope="pad",
                      volume=0.25, reverb=0.5, reverb_decay=2.5,
                      lowpass=4000)
    lead = score.part("lead", synth="triangle", envelope="strings",
                      volume=0.4, delay=0.3, delay_time=0.172,
                      delay_feedback=0.4, reverb=0.25)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.55, lowpass=300)

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

    pads = score.part("pads", synth="supersaw", envelope="pad",
                      volume=0.2, reverb=0.5, reverb_decay=3.0,
                      lowpass=2500)
    bells = score.part("bells", synth="fm", envelope="bell",
                       volume=0.3, reverb=0.4, reverb_decay=2.0,
                       delay=0.25, delay_time=0.44,
                       delay_feedback=0.35)
    lead = score.part("lead", synth="pwm_slow", envelope="strings",
                      volume=0.35, reverb=0.3, lowpass=2000,
                      delay=0.2, delay_time=0.88, delay_feedback=0.3)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.6, lowpass=200, lowpass_q=1.8,
                      distortion=0.4, distortion_drive=2.0)

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
        "sky", synth="supersaw", envelope="pad",
        volume=0.18, pan=0.0,
        detune=30, spread=1.0,
        reverb=0.6, reverb_decay=3.5,
        chorus=0.3, sidechain=0.5,
    )
    acid_l = score.part(
        "acid_l", synth="saw", envelope="pad",
        volume=0.35, pan=-0.7,
        legato=True, glide=0.025,
        distortion=0.9, distortion_drive=12.0,
        lowpass=800, lowpass_q=6.0,
        delay=0.2, delay_time=0.227, delay_feedback=0.35,
    )
    acid_l.lfo("lowpass", rate=0.5, min=400, max=3000, bars=8, shape="sine")

    acid_r = score.part(
        "acid_r", synth="saw", envelope="pad",
        volume=0.3, pan=0.7,
        legato=True, glide=0.02,
        distortion=0.85, distortion_drive=10.0,
        lowpass=1000, lowpass_q=5.0,
        delay=0.25, delay_time=0.341, delay_feedback=0.4,
    )
    acid_r.lfo("lowpass", rate=0.33, min=500, max=2500, bars=8, shape="triangle")

    sub = score.part(
        "sub", synth="sine", envelope="pluck",
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
        "bell_l", synth="fm", envelope="bell",
        volume=0.1, pan=-1.0,
        reverb=0.7, reverb_decay=3.0,
    )
    bell_r = score.part(
        "bell_r", synth="fm", envelope="bell",
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

    bass = score.part("bass", synth="square", envelope="pluck",
                      volume=0.45, lowpass=500, lowpass_q=1.3,
                      sidechain=0.75, sidechain_release=0.12)
    sparkle = score.part("sparkle", synth="fm", envelope="bell",
                         volume=0.3, pan=0.4, reverb=0.3, reverb_decay=1.5,
                         delay=0.2, delay_time=0.234, delay_feedback=0.3)
    chords_part = score.part("chords", synth="supersaw", envelope="pad",
                             volume=0.2, detune=12, spread=0.7,
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

    koto = score.part("koto", synth="triangle", envelope="pluck",
                      volume=0.45, pan=0.2,
                      reverb=0.5, reverb_type="taj_mahal",
                      humanize=0.3)
    drone = score.part("drone", synth="sine", envelope="pad",
                       volume=0.15, reverb=0.6, reverb_type="taj_mahal",
                       chorus=0.15, chorus_rate=0.2)
    bell = score.part("bell", synth="fm", envelope="bell",
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
        choice = input("  Pick a song (1-20, or 'all'): ").strip()
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
