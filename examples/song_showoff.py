"""PyTheory Showoff — a generative composition that's different every time.

Demonstrates every feature of the library in one elegant piece:
- Key detection and modulation
- Chord progressions with Roman numerals
- 58 drum patterns with genre-matched fills
- 10 synth waveforms and 8 envelope presets
- Arpeggiator with legato and glide
- Per-part effects: reverb, delay, lowpass filter, distortion
- Random but musically coherent — always sounds good, never repeats

Usage:
    python examples/song_showoff.py
"""

import random
import sounddevice as sd

from pytheory import Chord, Key, Pattern, Duration, Score
from pytheory.play import render_score, SAMPLE_RATE


# ── Musical building blocks ────────────────────────────────────────────────

MOODS = {
    "dark": {
        "keys": [("D", "minor"), ("A", "minor"), ("E", "minor"),
                 ("B", "minor"), ("G", "minor"), ("C", "minor")],
        "progressions": [
            ("i", "iv", "V", "i"),
            ("i", "bVI", "bVII", "i"),
            ("i", "iv", "bVI", "V"),
            ("i", "bVII", "bVI", "V"),
        ],
        "drums": ["afrobeat", "dub", "trap", "reggae", "techno",
                  "hip hop", "drum and bass"],
        "fills": ["afrobeat", "trap", "buildup", "breakdown"],
        "tempo_range": (70, 140),
    },
    "bright": {
        "keys": [("C", "major"), ("G", "major"), ("D", "major"),
                 ("A", "major"), ("F", "major"), ("Bb", "major")],
        "progressions": [
            ("I", "V", "vi", "IV"),
            ("I", "IV", "V", "I"),
            ("I", "vi", "ii", "V"),
            ("I", "IV", "vi", "V"),
        ],
        "drums": ["bossa nova", "samba", "funk", "disco", "gospel",
                  "ska", "swing", "country"],
        "fills": ["rock", "funk", "samba", "buildup"],
        "tempo_range": (100, 170),
    },
    "ethereal": {
        "keys": [("Eb", "minor"), ("Ab", "minor"), ("F", "minor"),
                 ("Bb", "minor"), ("Db", "major"), ("Gb", "major")],
        "progressions": [
            ("I", "V", "vi", "IV"),
            ("i", "bVI", "bIII", "bVII"),
            ("i", "iv", "V", "i"),
            ("I", "vi", "IV", "V"),
        ],
        "drums": ["jazz", "waltz", "house", "bebop", "bolero"],
        "fills": ["jazz", "jazz brush", "house", "bossa nova"],
        "tempo_range": (68, 120),
    },
    "aggressive": {
        "keys": [("E", "minor"), ("A", "minor"), ("D", "minor"),
                 ("B", "minor"), ("F#", "minor"), ("C", "minor")],
        "progressions": [
            ("i", "bVII", "bVI", "V"),
            ("i", "iv", "V", "i"),
            ("i", "bVI", "bVII", "i"),
            ("i", "V", "bVI", "iv"),
        ],
        "drums": ["metal", "punk", "drum and bass", "jungle",
                  "breakbeat", "techno"],
        "fills": ["metal", "blast", "rock crash", "buildup"],
        "tempo_range": (130, 180),
    },
}

SYNTH_PALETTES = [
    # (lead_synth, pad_synth, bass_synth, arp_synth)
    ("saw", "supersaw", "sine", "saw"),
    ("triangle", "pwm_slow", "sine", "fm"),
    ("fm", "supersaw", "pulse", "saw"),
    ("square", "pwm_slow", "sine", "square"),
    ("saw", "pwm_fast", "pulse", "fm"),
    ("triangle", "supersaw", "sine", "saw"),
]

ARP_PATTERNS = ["up", "down", "updown", "downup"]


# ── The generator ──────────────────────────────────────────────────────────

def generate():
    """Generate a unique composition. Different every time."""

    # Pick a mood
    mood_name = random.choice(list(MOODS.keys()))
    mood = MOODS[mood_name]

    # Pick a key
    tonic, mode = random.choice(mood["keys"])
    key = Key(tonic, mode)

    # Pick a progression
    numerals = random.choice(mood["progressions"])

    # Pick tempo
    bpm = random.randint(*mood["tempo_range"])

    # Pick drum pattern and fill
    drum_preset = random.choice(mood["drums"])
    fill_preset = random.choice(mood["fills"])

    # Pick synth palette
    lead_synth, pad_synth, bass_synth, arp_synth = random.choice(SYNTH_PALETTES)

    # Pick time signature based on drum pattern
    waltz_patterns = {"waltz", "bolero"}
    time_sig = "3/4" if drum_preset in waltz_patterns else "4/4"
    bars_per_chord = 2
    total_bars = bars_per_chord * len(numerals) * 2  # play progression twice

    # Determine repeats based on time signature
    pattern_obj = Pattern.preset(drum_preset)
    beats_per_bar = 3.0 if time_sig == "3/4" else 4.0
    pattern_bars = pattern_obj.beats / beats_per_bar
    drum_repeats = max(1, int(total_bars / pattern_bars))

    # ── Build the score ──────────────────────────────────────────

    score = Score(time_sig, bpm=bpm)
    score.drums(drum_preset, repeats=drum_repeats,
                fill=fill_preset, fill_every=len(numerals) * bars_per_chord)

    # Effect amounts scale with mood intensity
    reverb_amount = {"dark": 0.35, "bright": 0.25,
                     "ethereal": 0.55, "aggressive": 0.2}[mood_name]
    delay_amount = {"dark": 0.3, "bright": 0.15,
                    "ethereal": 0.35, "aggressive": 0.15}[mood_name]
    dist_amount = {"dark": 0.3, "bright": 0.0,
                   "ethereal": 0.0, "aggressive": 0.7}[mood_name]
    filter_cutoff = {"dark": 2500, "bright": 5000,
                     "ethereal": 2000, "aggressive": 3500}[mood_name]

    # Pad — lush background
    pad = score.part("pad", synth=pad_synth, envelope="pad",
                     volume=0.2,
                     reverb=min(0.8, reverb_amount * 2),
                     reverb_decay=random.uniform(2.0, 4.0),
                     lowpass=filter_cutoff)

    # Lead melody
    lead_envelope = random.choice(["pluck", "strings", "piano"])
    lead = score.part("lead", synth=lead_synth, envelope=lead_envelope,
                      volume=0.4,
                      reverb=reverb_amount,
                      reverb_decay=random.uniform(1.0, 2.0),
                      delay=delay_amount,
                      delay_time=random.choice([0.25, 0.375, 0.5]) * 60 / bpm,
                      delay_feedback=random.uniform(0.25, 0.45),
                      lowpass=filter_cutoff,
                      distortion=dist_amount * 0.3,
                      distortion_drive=random.uniform(2.0, 5.0))

    # Arp layer
    arp_pattern = random.choice(ARP_PATTERNS)
    arp_octaves = random.choice([1, 2])
    arp_division = random.choice([Duration.EIGHTH, Duration.SIXTEENTH])
    use_legato = random.random() > 0.4
    glide_time = random.uniform(0.02, 0.06) if use_legato else 0.0
    arp = score.part("arp", synth=arp_synth,
                     envelope="staccato" if not use_legato else "pad",
                     volume=0.3,
                     legato=use_legato, glide=glide_time,
                     distortion=dist_amount,
                     distortion_drive=random.uniform(3.0, 10.0),
                     lowpass=random.uniform(800, 2000),
                     lowpass_q=random.uniform(1.0, 5.0),
                     delay=delay_amount * 0.7,
                     delay_time=random.uniform(0.15, 0.3),
                     delay_feedback=random.uniform(0.2, 0.4))

    # Bass
    bass = score.part("bass", synth=bass_synth, envelope="pluck",
                      volume=0.5,
                      lowpass=random.uniform(300, 600),
                      lowpass_q=random.uniform(1.0, 1.8),
                      distortion=dist_amount * 0.5,
                      distortion_drive=random.uniform(2.0, 4.0))

    # Bells / texture — sparse accents
    bells = score.part("bells", synth="fm", envelope="bell",
                       volume=0.15,
                       reverb=min(0.7, reverb_amount * 2.5),
                       reverb_decay=random.uniform(2.0, 4.0),
                       delay=0.2,
                       delay_time=random.uniform(0.3, 0.8),
                       delay_feedback=random.uniform(0.25, 0.4))

    # ── Compose the parts ────────────────────────────────────────

    chords = key.progression(*numerals)
    scale = key.scale

    # Get scale tones for melody generation
    scale_tones = [t.name for t in scale.tones[:-1]]

    for pass_num in range(2):
        for i, chord in enumerate(chords):
            chord_dur = Duration.DOTTED_HALF if time_sig == "3/4" else Duration.WHOLE

            # Pad: whole notes
            for _ in range(bars_per_chord):
                pad.add(chord, chord_dur)

            # Arp: arpeggiate the chord
            arp.arpeggio(chord, bars=bars_per_chord,
                         pattern=arp_pattern, division=arp_division,
                         octaves=arp_octaves)

            # Bass: root note pattern
            root = chord.root
            if root:
                bass_note = f"{root.name}2"
                fifth = root.add(7)
                bass_fifth = f"{fifth.name}2"
                if time_sig == "3/4":
                    for _ in range(bars_per_chord):
                        bass.add(bass_note, Duration.QUARTER)
                        bass.add(bass_fifth, Duration.QUARTER)
                        bass.add(bass_note, Duration.QUARTER)
                else:
                    for _ in range(bars_per_chord):
                        bass.add(bass_note, Duration.QUARTER)
                        bass.add(bass_note, Duration.QUARTER)
                        bass.add(bass_fifth, Duration.QUARTER)
                        bass.add(bass_note, Duration.QUARTER)

            # Lead: generate a melodic phrase from scale tones
            chord_tones = [t.name for t in chord.tones]
            beats_remaining = bars_per_chord * beats_per_bar

            while beats_remaining > 0.5:
                # Pick a note — prefer chord tones, allow scale tones
                if random.random() < 0.6:
                    note_name = random.choice(chord_tones)
                else:
                    note_name = random.choice(scale_tones)

                octave = random.choice([4, 5]) if pass_num == 0 else random.choice([5, 5, 6])

                # Pick a duration
                dur_choices = [0.5, 0.67, 1.0, 1.5, 2.0]
                dur = random.choice([d for d in dur_choices if d <= beats_remaining])

                # Occasional rest for breathing room
                if random.random() < 0.2:
                    rest_dur = random.choice([0.5, 1.0])
                    rest_dur = min(rest_dur, beats_remaining)
                    lead.rest(rest_dur)
                    beats_remaining -= rest_dur
                    if beats_remaining <= 0:
                        break

                lead.add(f"{note_name}{octave}", dur)
                beats_remaining -= dur

            # Bells: sparse accents on chord tones
            bell_beats = bars_per_chord * beats_per_bar
            bell_pos = 0
            while bell_pos < bell_beats:
                if random.random() < 0.25:
                    note_name = random.choice(chord_tones)
                    bells.add(f"{note_name}6", random.choice([1.5, 2.0, 3.0]))
                    bell_pos += 3
                else:
                    bells.rest(random.choice([1.0, 2.0]))
                    bell_pos += 2

    return score, {
        "mood": mood_name,
        "key": f"{tonic} {mode}",
        "progression": " → ".join(numerals),
        "bpm": bpm,
        "time_sig": time_sig,
        "drums": f"{drum_preset} + {fill_preset} fill",
        "lead": f"{lead_synth} ({lead_envelope})",
        "arp": f"{arp_synth} {'legato+glide' if use_legato else 'staccato'} {arp_pattern} {arp_octaves}oct",
        "pad": pad_synth,
        "bass": bass_synth,
    }


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        print()
        print("  PyTheory Showoff")
        print("  " + "=" * 50)
        print("  Generative composition — different every time")
        print()

        while True:
            score, info = generate()

            print(f"  ♫  Mood: {info['mood']}")
            print(f"     Key: {info['key']}")
            print(f"     Progression: {info['progression']}")
            print(f"     Tempo: {info['bpm']} bpm ({info['time_sig']})")
            print(f"     Drums: {info['drums']}")
            print(f"     Lead: {info['lead']}")
            print(f"     Arp: {info['arp']}")
            print(f"     Pad: {info['pad']} | Bass: {info['bass']}")
            print(f"     {score}")
            print()

            buf = render_score(score)
            sd.play(buf, SAMPLE_RATE)
            sd.wait()

            print()
            again = input("  Play another? (y/n): ").strip().lower()
            if again != "y":
                break
            print()

    except KeyboardInterrupt:
        sd.stop()
        print("\n\n  ♫")
