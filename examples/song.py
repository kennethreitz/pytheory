"""Play songs with PyTheory — drums, chords, and synth leads.

Requires PortAudio: brew install portaudio (macOS)

Each song demonstrates a different combination of:
- Drum pattern presets (48 genres available)
- Chord progressions (Roman numeral or symbol-based)
- Monosynth melody lines (sine, saw, triangle waveforms)
- ADSR envelope shaping (piano, pluck, pad, bell, etc.)
"""

import numpy
import sounddevice as sd

from pytheory import (
    Tone, Chord, Key, Pattern, Duration, Score,
    Synth, Envelope,
)
from pytheory.play import (
    _render, _render_drum_hit, _apply_envelope,
    sawtooth_wave, triangle_wave, sine_wave,
    SAMPLE_RATE, SAMPLE_PEAK,
)


# ── Engine ─────────────────────────────────────────────────────────────────

def render_score(score, melody=None, melody_synth=sawtooth_wave,
                 melody_envelope=(0.003, 0.05, 0.6, 0.08),
                 melody_volume=0.4, chord_volume=0.35, drum_volume=0.5):
    """Render a full arrangement to a float32 buffer.

    Args:
        score: Score with drum hits and chord notes.
        melody: Optional list of (note_string_or_None, beats) tuples.
        melody_synth: Wave function for the lead voice.
        melody_envelope: (attack, decay, sustain, release) for the lead.
        melody_volume: Lead mix level (0-1).
        chord_volume: Chord mix level (0-1).
        drum_volume: Drum mix level (0-1).

    Returns:
        Float32 numpy array of mixed audio.
    """
    samples_per_beat = int(SAMPLE_RATE * 60.0 / score.bpm)
    total_beats = score.total_beats

    # If melody extends beyond score, expand
    if melody:
        melody_beats = sum(b for _, b in melody)
        total_beats = max(total_beats, melody_beats)

    total_samples = int(total_beats * samples_per_beat)
    buf = numpy.zeros(total_samples, dtype=numpy.float32)

    # Chords
    beat_pos = 0.0
    for note in score.notes:
        if note.tone is not None:
            start = int(beat_pos * samples_per_beat)
            dur_ms = note.beats * 60_000 / score.bpm
            rendered = _render(note.tone, t=dur_ms, envelope=Envelope.PIANO)
            rendered_f32 = rendered.astype(numpy.float32) / SAMPLE_PEAK
            end = min(start + len(rendered_f32), total_samples)
            buf[start:end] += rendered_f32[:end - start] * chord_volume
        beat_pos += note.beats

    # Drums
    for hit in score._drum_hits:
        start = int(hit.position * samples_per_beat)
        if start >= total_samples:
            continue
        remaining = total_samples - start
        hit_len = min(int(SAMPLE_RATE * 0.5), remaining)
        wave = _render_drum_hit(hit.sound.value, hit_len)
        vel_scale = hit.velocity / 127.0
        buf[start:start + hit_len] += wave * vel_scale * drum_volume

    # Melody
    if melody:
        a, d, s, r = melody_envelope
        lead_pos = 0.0
        for note_name, beats in melody:
            start = int(lead_pos * samples_per_beat)
            dur_ms = beats * 60_000 / score.bpm
            n_samples = int(SAMPLE_RATE * dur_ms / 1000)

            if note_name is not None and start + n_samples <= total_samples:
                tone = Tone.from_string(note_name, system="western")
                hz = tone.pitch()
                wave = melody_synth(hz, n_samples=n_samples)
                wave_f32 = wave.astype(numpy.float32) / SAMPLE_PEAK
                wave_f32 = _apply_envelope(wave_f32, a, d, s, r)
                end = min(start + len(wave_f32), total_samples)
                buf[start:end] += wave_f32[:end - start] * melody_volume

            lead_pos += beats

    # Normalize
    peak = numpy.max(numpy.abs(buf))
    if peak > 0:
        buf = buf / peak * 0.9

    return buf


def play_song(buf):
    """Play a rendered buffer. Ctrl-C to skip."""
    try:
        sd.play(buf, SAMPLE_RATE)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
        print("  (skipped)")


# ── Songs ──────────────────────────────────────────────────────────────────

def bossa_nova_girl():
    """Bossa nova in A minor — The Girl from Ipanema vibe."""
    print("  Bossa Nova in A minor")
    print("  Drums: bossa nova | Chords: i-iv-V7-i | Lead: triangle")
    print()

    score = Pattern.preset("bossa nova").to_score(repeats=4, bpm=140)

    # Am → Dm → E7 → Am (x2)
    changes = ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Bar 1-2: floating line over Am
        ("E5", 0.67), ("D5", 0.33), ("C5", 0.67), ("B4", 0.33),
        ("A4", 1.0), ("C5", 0.67), ("E5", 0.33),
        ("D5", 0.67), ("C5", 0.33), ("A4", 1.0), (None, 1.0),
        # Bar 3-4: reaching up over Dm
        ("F5", 0.67), ("E5", 0.33), ("D5", 0.67), ("C5", 0.33),
        ("D5", 1.0), ("F5", 0.67), ("A5", 0.33),
        ("G5", 0.67), ("F5", 0.33), ("D5", 1.0), (None, 1.0),
        # Bar 5-6: tension over E7
        ("G#5", 0.67), ("F5", 0.33), ("E5", 0.67), ("D5", 0.33),
        ("E5", 1.0), (None, 0.5), ("B4", 0.5),
        ("D5", 0.67), ("E5", 0.33), ("G#4", 1.0), (None, 1.0),
        # Bar 7-8: resolve to Am
        ("A4", 1.0), ("C5", 0.67), ("E5", 0.33),
        ("A5", 1.5), (None, 0.5),
        ("G5", 0.67), ("E5", 0.33), ("C5", 0.67), ("A4", 0.33),
        ("A4", 2.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=triangle_wave,
                       melody_envelope=(0.01, 0.08, 0.7, 0.15),
                       melody_volume=0.45)
    play_song(buf)


def bebop_in_bb():
    """Bebop in Bb — rhythm changes with a horn-like lead."""
    print("  Bebop in Bb major")
    print("  Drums: bebop | Chords: I-vi-ii-V | Lead: sawtooth")
    print()

    score = Pattern.preset("bebop").to_score(repeats=8, bpm=160)

    changes = ["Bb", "Gm", "Cm", "F7"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Bar 1: Bb — arpeggio up
        ("Bb4", 0.67), ("D5", 0.33), ("F5", 0.67), ("D5", 0.33),
        ("Bb4", 0.67), ("C5", 0.33), ("D5", 0.67), ("F5", 0.33),
        # Bar 2: Gm — descending with chromatic approach
        ("G5", 0.67), ("F5", 0.33), ("D5", 0.67), ("Bb4", 0.33),
        ("A4", 0.67), ("Bb4", 0.33), ("D5", 0.67), ("G4", 0.33),
        # Bar 3: Cm — climbing
        ("C5", 0.67), ("Eb5", 0.33), ("G5", 0.67), ("Eb5", 0.33),
        ("C5", 0.67), ("D5", 0.33), ("Eb5", 0.67), ("F5", 0.33),
        # Bar 4: F7 — dominant tension
        ("A5", 0.67), ("G5", 0.33), ("F5", 0.67), ("Eb5", 0.33),
        ("D5", 0.67), ("C5", 0.33), ("A4", 0.5), (None, 0.5),
        # Bar 5: Bb — variation
        ("Bb4", 1.0), ("D5", 0.67), ("F5", 0.33),
        ("G5", 0.67), ("F5", 0.33), ("D5", 0.67), ("Bb4", 0.33),
        # Bar 6: Gm — bluesy
        ("Bb5", 0.67), ("A5", 0.33), ("G5", 0.67), ("F5", 0.33),
        ("Eb5", 0.67), ("D5", 0.33), ("Bb4", 0.67), ("G4", 0.33),
        # Bar 7: Cm — syncopated
        ("C5", 0.5), (None, 0.5), ("Eb5", 0.67), ("G5", 0.33),
        ("F5", 0.67), ("Eb5", 0.33), ("D5", 0.67), ("C5", 0.33),
        # Bar 8: F7 — turnaround lick
        ("A4", 0.67), ("C5", 0.33), ("Eb5", 0.67), ("F5", 0.33),
        ("G5", 0.67), ("A5", 0.33), ("Bb5", 1.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=sawtooth_wave,
                       melody_envelope=(0.003, 0.05, 0.6, 0.08),
                       melody_volume=0.4)
    play_song(buf)


def salsa_descarga():
    """Salsa descarga in D minor — clave-driven jam."""
    print("  Salsa Descarga in D minor")
    print("  Drums: salsa | Chords: ii-V-i-bVI | Lead: sawtooth")
    print()

    score = Pattern.preset("salsa").to_score(repeats=4, bpm=180)

    changes = ["Em7b5", "A7", "Dm7", "Bbmaj7"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Bar 1: Em7b5 — angular line
        ("E5", 0.67), ("G5", 0.33), ("Bb5", 0.67), ("A5", 0.33),
        ("G5", 0.67), ("F5", 0.33), ("E5", 0.67), ("D5", 0.33),
        # Bar 2: A7 — chromatic descent
        ("C#5", 0.67), ("D5", 0.33), ("E5", 0.67), ("G5", 0.33),
        ("F5", 0.67), ("E5", 0.33), ("C#5", 0.5), (None, 0.5),
        # Bar 3: Dm7 — syncopated
        ("D5", 0.5), (None, 0.17), ("F5", 0.67), ("A5", 0.33),
        ("G5", 0.67), ("F5", 0.33), ("E5", 0.67), ("D5", 0.33),
        # Bar 4: Bbmaj7 — resolution
        ("Bb4", 1.0), ("D5", 0.67), ("F5", 0.33),
        ("A5", 1.0), (None, 1.0),
        # Bar 5-8: second pass — variation
        ("E5", 0.5), ("F5", 0.5), ("G5", 0.67), ("A5", 0.33),
        ("Bb5", 0.67), ("A5", 0.33), ("G5", 0.67), ("E5", 0.33),
        ("C#5", 0.67), ("E5", 0.33), ("A5", 0.67), ("G5", 0.33),
        ("F5", 0.67), ("E5", 0.33), ("C#5", 0.67), ("A4", 0.33),
        ("D5", 1.0), ("F5", 0.67), ("A5", 0.33),
        ("G5", 0.67), ("F5", 0.33), ("D5", 1.0), (None, 1.0),
        ("Bb4", 0.67), ("D5", 0.33), ("F5", 0.67), ("Bb5", 0.33),
        ("A5", 1.5), (None, 0.5),
    ]

    buf = render_score(score, melody=melody, melody_synth=sawtooth_wave,
                       melody_envelope=(0.005, 0.06, 0.5, 0.1),
                       melody_volume=0.4, drum_volume=0.55)
    play_song(buf)


def afrobeat_groove():
    """Afrobeat in E minor — Fela Kuti-inspired groove."""
    print("  Afrobeat in E minor")
    print("  Drums: afrobeat | Chords: i-iv-bVII-bVI | Lead: saw")
    print()

    score = Pattern.preset("afrobeat").to_score(repeats=8, bpm=115)

    # 2 bars per chord, repeat once
    changes = ["Em", "Am", "D", "C"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Repetitive, hypnotic pentatonic riff
        ("E5", 0.5), ("G5", 0.5), ("A5", 0.5), ("G5", 0.5),
        ("E5", 0.5), ("D5", 0.5), ("E5", 1.0),
        ("E5", 0.5), ("G5", 0.5), ("A5", 0.5), ("B5", 0.5),
        ("A5", 0.5), ("G5", 0.5), ("E5", 1.0),
        # Variation with syncopation
        (None, 0.5), ("A5", 0.5), ("G5", 0.5), ("E5", 0.5),
        ("D5", 1.0), ("E5", 0.5), ("G5", 0.5),
        ("A5", 0.5), ("B5", 0.5), ("A5", 0.5), ("G5", 0.5),
        ("E5", 1.5), (None, 0.5),
        # Second half: octave higher accents
        ("E5", 0.5), ("G5", 0.5), ("A5", 0.5), ("G5", 0.5),
        ("E5", 0.5), ("D5", 0.5), ("B4", 1.0),
        ("E5", 0.5), ("G5", 0.5), ("A5", 0.5), ("B5", 0.5),
        ("A5", 0.5), ("G5", 0.5), ("E5", 1.0),
        (None, 0.5), ("B5", 0.5), ("A5", 0.5), ("G5", 0.5),
        ("E5", 1.0), ("D5", 0.5), ("E5", 0.5),
        ("E5", 2.0), (None, 2.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=sawtooth_wave,
                       melody_envelope=(0.005, 0.08, 0.5, 0.1),
                       melody_volume=0.35, drum_volume=0.55)
    play_song(buf)


def reggae_one_drop():
    """Reggae one-drop in G major — roots vibes."""
    print("  Reggae One-Drop in G major")
    print("  Drums: reggae | Chords: I-IV-V-IV | Lead: triangle")
    print()

    score = Pattern.preset("reggae").to_score(repeats=8, bpm=80)

    changes = ["G", "C", "D", "C"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Laid-back pentatonic melody
        ("G5", 1.5), (None, 0.5), ("B5", 1.0), ("A5", 1.0),
        ("G5", 2.0), ("E5", 1.0), ("D5", 1.0),
        ("C5", 1.5), (None, 0.5), ("E5", 1.0), ("G5", 1.0),
        ("A5", 1.5), (None, 0.5), ("G5", 2.0),
        # Second phrase
        ("D5", 1.5), (None, 0.5), ("E5", 1.0), ("G5", 1.0),
        ("A5", 2.0), ("B5", 1.0), ("A5", 1.0),
        ("G5", 1.5), (None, 0.5), ("E5", 1.0), ("D5", 1.0),
        ("G4", 3.0), (None, 1.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=triangle_wave,
                       melody_envelope=(0.02, 0.1, 0.7, 0.2),
                       melody_volume=0.45, drum_volume=0.45)
    play_song(buf)


def funk_workout():
    """Funk in E minor — syncopated 16th note groove."""
    print("  Funk Workout in E minor")
    print("  Drums: funk | Chords: i-iv-bVII-V | Lead: saw")
    print()

    score = Pattern.preset("funk").to_score(repeats=8, bpm=100)

    changes = ["Em", "Am", "D", "B7"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Funky 16th-note figure
        ("E5", 0.25), ("E5", 0.25), (None, 0.25), ("G5", 0.25),
        (None, 0.25), ("A5", 0.25), ("G5", 0.25), ("E5", 0.25),
        ("D5", 0.5), ("E5", 0.5), (None, 0.5), ("B4", 0.5),
        ("E5", 0.25), ("E5", 0.25), (None, 0.25), ("G5", 0.25),
        (None, 0.25), ("A5", 0.25), ("B5", 0.25), ("A5", 0.25),
        ("G5", 0.5), ("E5", 0.5), (None, 1.0),
        # Am phrase
        ("A4", 0.25), ("C5", 0.25), ("E5", 0.25), ("A5", 0.25),
        ("G5", 0.5), ("E5", 0.5), (None, 0.5), ("C5", 0.5),
        ("A4", 0.5), ("C5", 0.5), ("D5", 0.5), ("E5", 0.5),
        ("E5", 1.0), (None, 1.0),
        # D resolution
        ("D5", 0.25), ("F#5", 0.25), ("A5", 0.25), ("D5", 0.25),
        ("F#5", 0.5), ("D5", 0.5), ("A4", 0.5), ("D5", 0.5),
        # B7 turnaround
        ("D#5", 0.5), ("F#5", 0.5), ("B4", 0.5), ("D#5", 0.5),
        ("F#5", 1.0), (None, 1.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=sawtooth_wave,
                       melody_envelope=(0.002, 0.03, 0.5, 0.05),
                       melody_volume=0.4, drum_volume=0.55)
    play_song(buf)


def blues_shuffle():
    """12/8 blues in A — slow shuffle with a wailing lead."""
    print("  12/8 Blues Shuffle in A")
    print("  Drums: 12/8 blues | Chords: I-IV-V | Lead: saw (bluesy)")
    print()

    score = Pattern.preset("12/8 blues").to_score(repeats=6, bpm=70)

    # 12 bars: I I I I IV IV I I V IV I V (each bar = 6 beats in 12/8)
    bars = ["A", "A", "A", "A", "D", "D",
            "A", "A", "E7", "D", "A", "E7"]
    for sym in bars:
        score.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)
        score.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)

    # Wait, 12 bars * 6 beats = 72 beats, drums = 6 repeats * 6 = 36 beats
    # Need to match. Let's just do 6 bars of blues (half a chorus)
    # Actually, 6 repeats * 6 beats = 36 beats. 6 bars * 6 = 36. Perfect.

    melody = [
        # Bars 1-2 over A: classic blues opening
        ("A4", 1.0), ("C5", 0.67), ("A4", 0.33), ("E4", 1.0),
        (None, 0.5), ("A4", 0.5), ("C5", 0.67), ("D5", 0.33),
        ("E5", 1.5), ("D5", 0.5), ("C5", 0.5), ("A4", 0.5),
        ("E4", 1.5), (None, 0.5), ("A4", 1.0),
        # Bars 3-4 over D: reaching
        ("D5", 1.0), ("F5", 0.67), ("D5", 0.33), ("A4", 1.0),
        (None, 1.0), ("D5", 0.67), ("F5", 0.33), ("A5", 1.0),
        ("G5", 0.67), ("F5", 0.33), ("D5", 1.0), (None, 1.0),
        # Bars 5-6 over E7/D turnaround
        ("E5", 0.67), ("G#4", 0.33), ("B4", 0.67), ("E5", 0.33),
        ("D5", 1.0), ("A4", 1.0), (None, 1.0),
        ("A4", 0.67), ("C5", 0.33), ("E5", 0.67), ("A5", 0.33),
        ("A5", 2.0), (None, 1.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=sawtooth_wave,
                       melody_envelope=(0.01, 0.1, 0.6, 0.2),
                       melody_volume=0.45, drum_volume=0.45)
    play_song(buf)


def samba_de_janeiro():
    """Samba in G major — carnival energy."""
    print("  Samba in G major")
    print("  Drums: samba | Chords: I-vi-ii-V | Lead: triangle")
    print()

    score = Pattern.preset("samba").to_score(repeats=8, bpm=170)

    changes = ["G", "Em", "Am", "D7"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Fast, rhythmic melody
        ("B5", 0.33), ("A5", 0.33), ("G5", 0.34), ("F#5", 0.5), ("E5", 0.5),
        ("D5", 0.5), ("G5", 0.5), ("B5", 0.5), ("A5", 0.5),
        ("G5", 0.67), ("E5", 0.33), ("D5", 0.67), ("B4", 0.33),
        ("G4", 1.0), (None, 1.0),
        # Over Em
        ("E5", 0.5), ("G5", 0.5), ("B5", 0.5), ("A5", 0.5),
        ("G5", 0.67), ("F#5", 0.33), ("E5", 0.67), ("D5", 0.33),
        ("E5", 1.0), (None, 1.0),
        # Over Am
        ("A5", 0.5), ("C6", 0.5), ("B5", 0.5), ("A5", 0.5),
        ("G5", 0.67), ("E5", 0.33), ("C5", 0.67), ("A4", 0.33),
        ("A4", 1.0), (None, 1.0),
        # Over D7 — turnaround
        ("D5", 0.5), ("F#5", 0.5), ("A5", 0.5), ("C5", 0.5),
        ("B4", 0.67), ("A4", 0.33), ("G4", 0.67), ("F#4", 0.33),
        ("G4", 2.0), (None, 2.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=triangle_wave,
                       melody_envelope=(0.005, 0.05, 0.6, 0.1),
                       melody_volume=0.4, drum_volume=0.5)
    play_song(buf)


def jazz_waltz():
    """Jazz waltz in F major — 3/4 time with brushes feel."""
    print("  Jazz Waltz in F major")
    print("  Drums: waltz | Chords: I-ii-V-I | Lead: triangle")
    print()

    score = Pattern.preset("waltz").to_score(repeats=16, bpm=150)

    # 4 bars per change, 3 beats each = 12 beats per chord
    for _ in range(2):
        for sym in ["Fmaj7", "Gm", "C7", "Fmaj7"]:
            score.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)
            score.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)
            score.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)
            score.add(Chord.from_symbol(sym), Duration.DOTTED_HALF)

    melody = [
        # 3/4 phrases, lyrical
        ("A5", 1.5), ("G5", 0.5), ("F5", 1.0),
        ("E5", 1.0), ("C5", 1.0), ("F5", 1.0),
        ("A5", 2.0), (None, 1.0),
        ("G5", 2.0), (None, 1.0),
        # Over Gm
        ("Bb5", 1.0), ("A5", 0.5), ("G5", 0.5),
        ("F5", 1.0), ("D5", 1.0), ("G5", 1.0),
        ("Bb5", 2.0), (None, 1.0),
        ("A5", 1.5), ("G5", 0.5), ("F5", 1.0),
        # Over C7
        ("E5", 1.0), ("G5", 1.0), ("Bb5", 1.0),
        ("A5", 1.5), ("G5", 0.5), ("E5", 1.0),
        ("C5", 2.0), (None, 1.0),
        ("E5", 1.0), ("G5", 1.0), ("C5", 1.0),
        # Resolve to F
        ("F5", 2.0), ("A5", 1.0),
        ("C6", 2.0), (None, 1.0),
        ("A5", 1.0), ("F5", 1.0), ("C5", 1.0),
        ("F5", 3.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=triangle_wave,
                       melody_envelope=(0.02, 0.1, 0.7, 0.2),
                       melody_volume=0.45, drum_volume=0.4)
    play_song(buf)


def house_anthem():
    """House in C minor — four-on-the-floor with pad chords."""
    print("  House Anthem in C minor")
    print("  Drums: house | Chords: i-bVI-bVII-i | Lead: saw (acid)")
    print()

    score = Pattern.preset("house").to_score(repeats=8, bpm=124)

    changes = ["Cm", "Ab", "Bb", "Cm"] * 2
    for sym in changes:
        score.add(Chord.from_symbol(sym), Duration.WHOLE)

    melody = [
        # Acid-style arpeggiated lead
        ("C5", 0.25), ("Eb5", 0.25), ("G5", 0.25), ("C5", 0.25),
        ("Eb5", 0.25), ("G5", 0.25), ("C5", 0.25), ("Eb5", 0.25),
        ("G5", 0.25), ("Eb5", 0.25), ("C5", 0.25), ("G4", 0.25),
        ("C5", 0.5), (None, 0.5), ("Eb5", 0.5), ("G5", 0.5),
        # Over Ab
        ("Ab4", 0.25), ("C5", 0.25), ("Eb5", 0.25), ("Ab4", 0.25),
        ("C5", 0.25), ("Eb5", 0.25), ("Ab4", 0.25), ("C5", 0.25),
        ("Eb5", 0.25), ("C5", 0.25), ("Ab4", 0.25), ("Eb4", 0.25),
        ("Ab4", 0.5), (None, 0.5), ("C5", 0.5), ("Eb5", 0.5),
        # Over Bb
        ("Bb4", 0.25), ("D5", 0.25), ("F5", 0.25), ("Bb4", 0.25),
        ("D5", 0.25), ("F5", 0.25), ("Bb4", 0.25), ("D5", 0.25),
        ("F5", 0.5), ("D5", 0.5), ("Bb4", 0.5), ("F5", 0.5),
        # Back to Cm — resolution
        ("C5", 0.25), ("Eb5", 0.25), ("G5", 0.25), ("C6", 0.25),
        ("G5", 0.25), ("Eb5", 0.25), ("C5", 0.25), (None, 0.25),
        ("C5", 1.5), (None, 0.5),
        # Second half: more intense
        ("G5", 0.25), ("G5", 0.25), ("Eb5", 0.25), ("C5", 0.25),
        ("G5", 0.25), ("G5", 0.25), ("Eb5", 0.25), ("C5", 0.25),
        ("Eb5", 0.5), ("C5", 0.5), ("G4", 0.5), ("C5", 0.5),
        ("Eb5", 1.0), (None, 1.0),
        ("Ab4", 0.5), ("C5", 0.5), ("Eb5", 0.5), ("Ab5", 0.5),
        ("G5", 0.5), ("Eb5", 0.5), ("C5", 1.0),
        ("Bb4", 0.5), ("D5", 0.5), ("F5", 0.5), ("Bb5", 0.5),
        ("F5", 0.5), ("D5", 0.5), ("Bb4", 1.0),
        ("C5", 0.5), ("Eb5", 0.5), ("G5", 0.5), ("C6", 0.5),
        ("C6", 2.0),
    ]

    buf = render_score(score, melody=melody, melody_synth=sawtooth_wave,
                       melody_envelope=(0.001, 0.03, 0.4, 0.05),
                       melody_volume=0.35, chord_volume=0.4, drum_volume=0.5)
    play_song(buf)


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
