"""Play melodies and chord progressions with PyTheory.

Requires PortAudio: brew install portaudio (macOS)
"""

from pytheory import Tone, Chord, Key, TonedScale, play, Synth

# ── Helpers ─────────────────────────────────────────────────────────────

BPM = 180
BEAT = 60_000 // BPM  # ms per beat


def play_melody(notes, synth=Synth.SINE):
    """Play a sequence of (note_string, beats) tuples."""
    try:
        for note, beats in notes:
            if note == "REST":
                import time
                time.sleep(beats * BEAT / 1000)
            else:
                tone = Tone.from_string(note, system="western")
                play(tone, synth=synth, t=int(beats * BEAT))
    except KeyboardInterrupt:
        print("\n  Stopped.")


def play_progression(chords, beats_each=2, synth=Synth.TRIANGLE):
    """Play a list of Chord objects."""
    try:
        for chord in chords:
            name = chord.identify() or "?"
            tones = " ".join(t.full_name for t in chord.tones)
            print(f"  {name:20s}  {tones}")
            play(chord, synth=synth, t=int(beats_each * BEAT))
    except KeyboardInterrupt:
        print("\n  Stopped.")


# ── Songs ───────────────────────────────────────────────────────────────

def twinkle_twinkle():
    """Twinkle Twinkle Little Star — C major."""
    print("Twinkle Twinkle Little Star")
    print("=" * 40)

    melody = [
        # Twinkle twinkle little star
        ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
        ("A4", 1), ("A4", 1), ("G4", 2),
        # How I wonder what you are
        ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
        ("D4", 1), ("D4", 1), ("C4", 2),
        # Up above the world so high
        ("G4", 1), ("G4", 1), ("F4", 1), ("F4", 1),
        ("E4", 1), ("E4", 1), ("D4", 2),
        # Like a diamond in the sky
        ("G4", 1), ("G4", 1), ("F4", 1), ("F4", 1),
        ("E4", 1), ("E4", 1), ("D4", 2),
        # Twinkle twinkle little star
        ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
        ("A4", 1), ("A4", 1), ("G4", 2),
        # How I wonder what you are
        ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
        ("D4", 1), ("D4", 1), ("C4", 2),
    ]

    play_melody(melody)


def ode_to_joy():
    """Ode to Joy — Beethoven's 9th Symphony, D major."""
    print("Ode to Joy (Beethoven)")
    print("=" * 40)

    melody = [
        # Main theme
        ("F#4", 1), ("F#4", 1), ("G4", 1), ("A4", 1),
        ("A4", 1), ("G4", 1), ("F#4", 1), ("E4", 1),
        ("D4", 1), ("D4", 1), ("E4", 1), ("F#4", 1),
        ("F#4", 1.5), ("E4", 0.5), ("E4", 2),
        # Repeat with variation
        ("F#4", 1), ("F#4", 1), ("G4", 1), ("A4", 1),
        ("A4", 1), ("G4", 1), ("F#4", 1), ("E4", 1),
        ("D4", 1), ("D4", 1), ("E4", 1), ("F#4", 1),
        ("E4", 1.5), ("D4", 0.5), ("D4", 2),
    ]

    play_melody(melody)


def happy_birthday():
    """Happy Birthday — G major."""
    print("Happy Birthday")
    print("=" * 40)

    melody = [
        # Happy birthday to you
        ("G4", 0.75), ("G4", 0.25), ("A4", 1), ("G4", 1),
        ("C5", 1), ("B4", 2),
        # Happy birthday to you
        ("G4", 0.75), ("G4", 0.25), ("A4", 1), ("G4", 1),
        ("D5", 1), ("C5", 2),
        # Happy birthday dear [name]
        ("G4", 0.75), ("G4", 0.25), ("G5", 1), ("E5", 1),
        ("C5", 1), ("B4", 1), ("A4", 2),
        # Happy birthday to you
        ("F5", 0.75), ("F5", 0.25), ("E5", 1), ("C5", 1),
        ("D5", 1), ("C5", 2),
    ]

    play_melody(melody)


def fur_elise():
    """Fur Elise — opening bars (A minor)."""
    print("Fur Elise (opening)")
    print("=" * 40)

    melody = [
        ("E5", 0.5), ("D#5", 0.5), ("E5", 0.5), ("D#5", 0.5),
        ("E5", 0.5), ("B4", 0.5), ("D5", 0.5), ("C5", 0.5),
        ("A4", 1), ("REST", 0.5),
        ("C4", 0.5), ("E4", 0.5), ("A4", 0.5),
        ("B4", 1), ("REST", 0.5),
        ("E4", 0.5), ("G#4", 0.5), ("B4", 0.5),
        ("C5", 1), ("REST", 0.5),
        ("E4", 0.5), ("E5", 0.5), ("D#5", 0.5),
        ("E5", 0.5), ("D#5", 0.5), ("E5", 0.5), ("B4", 0.5),
        ("D5", 0.5), ("C5", 0.5),
        ("A4", 1),
    ]

    play_melody(melody)


def pop_progression():
    """The I–V–vi–IV pop progression in C major."""
    print("Pop Progression (I-V-vi-IV in C)")
    print("=" * 40)
    print()

    key = Key("C", "major")
    chords = key.progression("I", "V", "vi", "IV")

    # Play it twice
    play_progression(chords * 2)


def blues_in_a():
    """12-bar blues in A."""
    print("12-Bar Blues in A")
    print("=" * 40)
    print()

    key = Key("A", "major")
    I = key.triad(0)
    IV = key.triad(3)
    V = key.triad(4)

    bars = [I, I, I, I, IV, IV, I, I, V, IV, I, V]

    play_progression(bars, beats_each=1.5)


def jazz_ii_v_i():
    """Jazz ii–V–I turnaround through several keys."""
    print("Jazz ii-V-I Turnaround")
    print("=" * 40)
    print()

    for tonic in ["C", "F", "Bb", "Eb"]:
        key = Key(tonic, "major")
        chords = key.progression("ii", "V", "I")
        print(f"  Key of {tonic}:")
        play_progression(chords, beats_each=1.5)
        print()


# ── Main ────────────────────────────────────────────────────────────────

SONGS = {
    "1": ("Twinkle Twinkle Little Star", twinkle_twinkle),
    "2": ("Ode to Joy", ode_to_joy),
    "3": ("Happy Birthday", happy_birthday),
    "4": ("Fur Elise (opening)", fur_elise),
    "5": ("Pop Progression (I-V-vi-IV)", pop_progression),
    "6": ("12-Bar Blues in A", blues_in_a),
    "7": ("Jazz ii-V-I Turnaround", jazz_ii_v_i),
}

if __name__ == "__main__":
    try:
        print("PyTheory Song Player")
        print("=" * 40)
        print()

        for key, (name, _) in SONGS.items():
            print(f"  {key}. {name}")

        print()
        choice = input("Pick a song (1-7, or 'all'): ").strip()

        if choice == "all":
            for _, (_, fn) in SONGS.items():
                fn()
                print()
        elif choice in SONGS:
            SONGS[choice][1]()
        else:
            print("Playing all melodies...")
            for _, (_, fn) in SONGS.items():
                fn()
                print()
    except KeyboardInterrupt:
        print("\n\nBye!")
