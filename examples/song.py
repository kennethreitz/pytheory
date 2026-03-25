"""Play songs with PyTheory — drums, chords, bass, and synth leads.

Requires PortAudio: brew install portaudio (macOS)

Each song uses the multi-part Score API:
- Drum pattern presets (48 genres)
- Named parts with independent synth voices and envelopes
- Chord pads, walking bass lines, and melody leads

Usage:
    python examples/song.py
"""

import sounddevice as sd

from pytheory import (
    Chord, Key, Pattern, Duration, Score,
)
from pytheory.play import play_score, render_score, SAMPLE_RATE


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
    """Bossa nova in A minor — full arrangement."""
    print("  Bossa Nova in A minor")
    print("  Drums: bossa nova | Lead: triangle | Bass: triangle")

    score = Score("4/4", bpm=140)
    score.add_pattern(Pattern.preset("bossa nova"), repeats=4)

    chords = score.part("chords", synth="sine", envelope="pad", volume=0.35)
    lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.5)
    bass = score.part("bass", synth="triangle", envelope="pluck", volume=0.45)

    for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

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

    for n in ["A2","B2","C3","E3","D3","E3","F3","E3",
              "E3","D3","C3","B2","A2","G2","A2","B2",
              "A2","B2","C3","E3","D3","E3","F3","E3",
              "E3","D3","C3","B2","A2","E2","A2","A2"]:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def bebop_in_bb():
    """Bebop in Bb — rhythm changes with horn lead and walking bass."""
    print("  Bebop in Bb major")
    print("  Drums: bebop | Lead: sawtooth | Bass: triangle")

    score = Score("4/4", bpm=160)
    score.add_pattern(Pattern.preset("bebop"), repeats=8)

    chords = score.part("chords", synth="sine", envelope="piano", volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.45)
    bass = score.part("bass", synth="triangle", envelope="pluck", volume=0.4)

    for sym in ["Bb", "Gm", "Cm", "F7"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

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
    """Salsa descarga in D minor — clave-driven jam."""
    print("  Salsa Descarga in D minor")
    print("  Drums: salsa | Lead: sawtooth | Bass: sine")

    score = Score("4/4", bpm=180)
    score.add_pattern(Pattern.preset("salsa"), repeats=4)

    chords = score.part("chords", synth="sine", envelope="pad", volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)

    for sym in ["Em7b5", "A7", "Dm7", "Bbmaj7"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

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

    # Salsa bass: tumbao pattern
    for n in ["E2","E3","A2","A3","D2","D3","Bb2","Bb3"] * 4:
        bass.add(n, Duration.QUARTER)

    play_song(score)


def afrobeat_groove():
    """Afrobeat in E minor — Fela Kuti-inspired."""
    print("  Afrobeat in E minor")
    print("  Drums: afrobeat | Lead: sawtooth | Bass: sine")

    score = Score("4/4", bpm=115)
    score.add_pattern(Pattern.preset("afrobeat"), repeats=8)

    chords = score.part("chords", synth="sine", envelope="pad", volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)

    for sym in ["Em", "Am", "D", "C"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

    # Hypnotic pentatonic riff
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
    """Reggae one-drop in G major."""
    print("  Reggae One-Drop in G major")
    print("  Drums: reggae | Lead: triangle | Bass: sine")

    score = Score("4/4", bpm=80)
    score.add_pattern(Pattern.preset("reggae"), repeats=8)

    chords = score.part("chords", synth="sine", envelope="organ", volume=0.35)
    lead = score.part("lead", synth="triangle", envelope="pad", volume=0.45)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.5)

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
    """Funk in E minor — syncopated groove."""
    print("  Funk Workout in E minor")
    print("  Drums: funk | Lead: sawtooth | Bass: sine")

    score = Score("4/4", bpm=100)
    score.add_pattern(Pattern.preset("funk"), repeats=8)

    chords = score.part("chords", synth="sine", envelope="staccato", volume=0.3)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.5)

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
    """12/8 blues in A — slow shuffle."""
    print("  12/8 Blues Shuffle in A")
    print("  Drums: 12/8 blues | Lead: sawtooth | Bass: sine")

    score = Score("12/8", bpm=70)
    score.add_pattern(Pattern.preset("12/8 blues"), repeats=6)

    chords = score.part("chords", synth="sine", envelope="piano", volume=0.35)
    lead = score.part("lead", synth="saw", envelope="pluck", volume=0.45)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)

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
    """Samba in G major — carnival energy."""
    print("  Samba in G major")
    print("  Drums: samba | Lead: triangle | Bass: sine")

    score = Score("4/4", bpm=170)
    score.add_pattern(Pattern.preset("samba"), repeats=8)

    chords = score.part("chords", synth="sine", envelope="pad", volume=0.3)
    lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.45)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)

    for sym in ["G", "Em", "Am", "D7"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

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
    """Jazz waltz in F major — 3/4 time."""
    print("  Jazz Waltz in F major")
    print("  Drums: waltz | Lead: triangle | Bass: sine")

    score = Score("3/4", bpm=150)
    score.add_pattern(Pattern.preset("waltz"), repeats=16)

    chords = score.part("chords", synth="sine", envelope="pad", volume=0.35)
    lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.45)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.4)

    for _ in range(2):
        for sym in ["Fmaj7", "Gm", "C7", "Fmaj7"]:
            for _ in range(4):
                chords.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)

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
    print("  Drums: house | Lead: sawtooth (acid) | Bass: sine")

    score = Score("4/4", bpm=124)
    score.add_pattern(Pattern.preset("house"), repeats=8)

    chords = score.part("chords", synth="sine", envelope="pad", volume=0.35)
    lead = score.part("lead", synth="saw", envelope="staccato", volume=0.4)
    bass = score.part("bass", synth="sine", envelope="pluck", volume=0.5)

    for sym in ["Cm", "Ab", "Bb", "Cm"] * 2:
        chords.add(Chord.from_symbol(sym), Duration.WHOLE)

    # Acid arpeggios
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

    # Pumping bass
    for n in ["C2","C2","C2","C2","Ab1","Ab1","Ab1","Ab1",
              "Bb1","Bb1","Bb1","Bb1","C2","C2","C2","C2"] * 2:
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
        choice = input("  Pick a song (1-10, or 'all'): ").strip()
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
