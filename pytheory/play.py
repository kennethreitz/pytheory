from enum import Enum
import time

import numpy
import scipy.signal
import sounddevice as sd

from .tones import Tone

SAMPLE_RATE = 44_100   # CD-quality sample rate (Hz)
SAMPLE_PEAK = 4_096    # Peak amplitude for 16-bit integer samples


def sine_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a sine wave with given frequency and peak amplitude.
    Defaults to one second.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = peak * numpy.sin(xvalues)
    return numpy.resize(onecycle, (n_samples,)).astype(numpy.int16)


def sawtooth_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a sawtooth wave with given frequency and peak amplitude.
    Defaults to one second.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = scipy.signal.sawtooth(xvalues, width=1)
    onecycle = (peak * onecycle).astype(numpy.int16)
    return numpy.resize(onecycle, (n_samples,))


def triangle_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a triangle wave with given frequency and peak amplitude.
    Defaults to one second.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = scipy.signal.sawtooth(xvalues, width=0.5)
    onecycle = (peak * onecycle).astype(numpy.int16)
    return numpy.resize(onecycle, (n_samples,))


def _apply_envelope(samples, attack, decay, sustain, release, sample_rate=SAMPLE_RATE):
    """Apply an ADSR amplitude envelope to a sample array.

    Args:
        samples: NumPy array of audio samples.
        attack: Attack time in seconds.
        decay: Decay time in seconds.
        sustain: Sustain level (0.0 to 1.0).
        release: Release time in seconds.
        sample_rate: Sample rate in Hz.

    Returns:
        NumPy float32 array with envelope applied.
    """
    n = len(samples)
    envelope = numpy.ones(n, dtype=numpy.float32)

    a_samples = int(attack * sample_rate)
    d_samples = int(decay * sample_rate)
    r_samples = int(release * sample_rate)

    # Clamp to available length
    a_samples = min(a_samples, n)
    r_samples = min(r_samples, max(0, n - a_samples))
    d_samples = min(d_samples, max(0, n - a_samples - r_samples))

    # Attack: 0 → 1
    if a_samples > 0:
        envelope[:a_samples] = numpy.linspace(0.0, 1.0, a_samples)

    # Decay: 1 → sustain
    if d_samples > 0:
        d_start = a_samples
        envelope[d_start:d_start + d_samples] = numpy.linspace(1.0, sustain, d_samples)

    # Sustain: hold at sustain level
    s_start = a_samples + d_samples
    s_end = n - r_samples
    if s_end > s_start:
        envelope[s_start:s_end] = sustain

    # Release: sustain → 0
    if r_samples > 0:
        envelope[n - r_samples:] = numpy.linspace(sustain, 0.0, r_samples)

    return samples.astype(numpy.float32) * envelope


class Envelope(Enum):
    """ADSR envelope presets for shaping note amplitude over time.

    Each preset is a tuple of ``(attack, decay, sustain, release)``
    in seconds (sustain is a 0–1 level, not a time).

    Example::

        >>> play(tone, envelope=Envelope.PIANO)
        >>> play(chord, envelope=Envelope.PAD, t=3_000)
    """
    NONE = (0.0, 0.0, 1.0, 0.0)
    PIANO = (0.005, 0.1, 0.4, 0.15)
    ORGAN = (0.02, 0.0, 1.0, 0.02)
    PLUCK = (0.002, 0.15, 0.0, 0.1)
    PAD = (0.4, 0.2, 0.7, 0.5)
    STRINGS = (0.15, 0.1, 0.8, 0.3)
    BELL = (0.001, 0.3, 0.0, 0.5)
    STACCATO = (0.005, 0.05, 0.0, 0.02)


def _play_for(sample_wave, ms):
    """Play the given NumPy sample array through the speakers."""
    normalized_wave = sample_wave.astype(numpy.float32) / SAMPLE_PEAK
    sd.play(normalized_wave, SAMPLE_RATE)
    sd.wait()


class Synth(Enum):
    SINE = sine_wave
    SAW = sawtooth_wave
    TRIANGLE = triangle_wave


def _render(tone_or_chord, temperament="equal", synth=Synth.SINE, t=1_000,
            envelope=Envelope.PIANO):
    """Render a tone or chord to a NumPy sample array.

    Args:
        tone_or_chord: A :class:`Tone` or :class:`Chord` to render.
        temperament: Tuning temperament (``"equal"``, ``"pythagorean"``,
            or ``"meantone"``).
        synth: Waveform type — ``Synth.SINE``, ``Synth.SAW``, or
            ``Synth.TRIANGLE``.
        t: Duration in milliseconds.
        envelope: ADSR envelope preset. Use ``Envelope.NONE`` for raw
            output (old behavior).

    Returns:
        A NumPy int16 array of audio samples.
    """
    n_samples = int(SAMPLE_RATE * t / 1_000)

    if isinstance(tone_or_chord, Tone):
        waves = [synth(tone_or_chord.pitch(temperament=temperament), n_samples=n_samples)]
    else:
        waves = [
            synth(tone.pitch(temperament=temperament), n_samples=n_samples)
            for tone in tone_or_chord.tones
        ]

    mixed = sum(waves)

    # Apply ADSR envelope
    attack, decay, sustain, release = envelope.value
    if attack > 0 or decay > 0 or sustain < 1.0 or release > 0:
        mixed = _apply_envelope(mixed, attack, decay, sustain, release)

    return mixed


def play(tone_or_chord, temperament="equal", synth=Synth.SINE, t=1_000,
         envelope=Envelope.PIANO):
    """Play a tone or chord through the speakers.

    Args:
        tone_or_chord: A :class:`Tone` or :class:`Chord` to play.
        temperament: Tuning temperament (``"equal"``, ``"pythagorean"``,
            or ``"meantone"``).
        synth: Waveform type — ``Synth.SINE``, ``Synth.SAW``, or
            ``Synth.TRIANGLE``.
        t: Duration in milliseconds (default 1000).
        envelope: ADSR envelope preset (default ``Envelope.PIANO``).
            Use ``Envelope.NONE`` for raw waveform.

    Example::

        >>> play(Tone.from_string("A4"), t=1_000)
        >>> play(Chord.from_name("Am7"), synth=Synth.TRIANGLE, t=2_000)
        >>> play(tone, envelope=Envelope.PAD, t=3_000)
    """
    _play_for(_render(tone_or_chord, temperament=temperament, synth=synth,
                      t=t, envelope=envelope), ms=t)


def save(tone_or_chord, path, temperament="equal", synth=Synth.SINE, t=1_000,
         envelope=Envelope.PIANO):
    """Render a tone or chord and save it as a WAV file.

    Args:
        tone_or_chord: A :class:`Tone` or :class:`Chord` to render.
        path: Output file path (e.g. ``"chord.wav"``).
        temperament: Tuning temperament.
        synth: Waveform type.
        t: Duration in milliseconds (default 1000).
        envelope: ADSR envelope preset (default ``Envelope.PIANO``).

    Example::

        >>> save(Chord.from_name("C"), "c_major.wav", t=2_000)
        >>> save(tone, "bell.wav", envelope=Envelope.BELL, t=3_000)
    """
    import scipy.io.wavfile

    samples = _render(tone_or_chord, temperament=temperament, synth=synth,
                      t=t, envelope=envelope)
    normalized = samples.astype(numpy.float32) / SAMPLE_PEAK
    # Convert to 16-bit PCM
    pcm = (normalized * 32767).astype(numpy.int16)
    scipy.io.wavfile.write(path, SAMPLE_RATE, pcm)


def play_progression(chords, *, t=1000, synth=Synth.SINE, gap=100,
                     envelope=Envelope.PIANO):
    """Play a list of chords in sequence.

    Args:
        chords: List of Chord objects to play in order.
        t: Duration of each chord in milliseconds.
        synth: Waveform type (Synth.SINE, etc). Defaults to sine.
        gap: Silence between chords in milliseconds.
        envelope: ADSR envelope preset (default ``Envelope.PIANO``).

    Example::

        >>> from pytheory import Key, play_progression
        >>> chords = Key("C", "major").progression("I", "V", "vi", "IV")
        >>> play_progression(chords, t=800)
        >>> play_progression(chords, t=2000, envelope=Envelope.PAD)
    """
    for i, chord in enumerate(chords):
        play(chord, synth=synth, t=t, envelope=envelope)
        if gap > 0 and i < len(chords) - 1:
            time.sleep(gap / 1000.0)


# ── Drum synthesis ──────────────────────────────────────────────────────────

def _noise(n_samples):
    """White noise array."""
    return numpy.random.uniform(-1.0, 1.0, n_samples).astype(numpy.float32)


def _sine_f32(hz, n_samples):
    """Float32 sine wave, normalized to ±1."""
    t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
    return numpy.sin(2 * numpy.pi * hz * t)


def _exp_decay(n_samples, decay_rate):
    """Exponential decay envelope from 1→0."""
    t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
    return numpy.exp(-decay_rate * t)


def _synth_kick(n_samples):
    """Synthesize a kick drum: sine with pitch sweep + sub thump."""
    t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
    # Pitch sweeps from 150 Hz down to 50 Hz
    freq = 50 + 100 * numpy.exp(-30 * t)
    phase = 2 * numpy.pi * numpy.cumsum(freq) / SAMPLE_RATE
    wave = numpy.sin(phase) * _exp_decay(n_samples, 8)
    # Add a sub click at the start
    click = _noise(min(200, n_samples)) * _exp_decay(min(200, n_samples), 80)
    wave[:len(click)] += click * 0.3
    return wave


def _synth_snare(n_samples):
    """Synthesize a snare: pitched body + noise rattle."""
    body = _sine_f32(180, n_samples) * _exp_decay(n_samples, 15) * 0.6
    noise = _noise(n_samples) * _exp_decay(n_samples, 12) * 0.7
    return body + noise


def _synth_hat_closed(n_samples):
    """Closed hi-hat: filtered noise, very short."""
    n = min(n_samples, int(SAMPLE_RATE * 0.05))
    wave = _noise(n) * _exp_decay(n, 60)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_hat_open(n_samples):
    """Open hi-hat: filtered noise, longer."""
    n = min(n_samples, int(SAMPLE_RATE * 0.25))
    wave = _noise(n) * _exp_decay(n, 12)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_clap(n_samples):
    """Handclap: layered noise bursts."""
    wave = numpy.zeros(n_samples, dtype=numpy.float32)
    for offset_ms in [0, 10, 20, 30]:
        start = int(offset_ms * SAMPLE_RATE / 1000)
        burst_len = min(int(SAMPLE_RATE * 0.03), n_samples - start)
        if burst_len > 0:
            wave[start:start + burst_len] += (
                _noise(burst_len) * _exp_decay(burst_len, 40) * 0.4)
    # Tail
    tail_len = min(int(SAMPLE_RATE * 0.15), n_samples)
    wave[:tail_len] += _noise(tail_len) * _exp_decay(tail_len, 18) * 0.3
    return wave


def _synth_rimshot(n_samples):
    """Rimshot: short bright click."""
    n = min(n_samples, int(SAMPLE_RATE * 0.03))
    wave = (_sine_f32(800, n) + _noise(n) * 0.5) * _exp_decay(n, 80)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_tom(hz, n_samples):
    """Generic tom: pitched sine with decay."""
    t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
    freq = hz + 30 * numpy.exp(-20 * t)
    phase = 2 * numpy.pi * numpy.cumsum(freq) / SAMPLE_RATE
    return numpy.sin(phase) * _exp_decay(n_samples, 6)


def _synth_crash(n_samples):
    """Crash cymbal: long noise decay."""
    n = min(n_samples, int(SAMPLE_RATE * 1.5))
    wave = _noise(n) * _exp_decay(n, 3)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_ride(n_samples):
    """Ride cymbal: metallic ring + noise."""
    ring = _sine_f32(3500, n_samples) * _exp_decay(n_samples, 6) * 0.3
    ring += _sine_f32(5100, n_samples) * _exp_decay(n_samples, 8) * 0.2
    noise = _noise(n_samples) * _exp_decay(n_samples, 10) * 0.2
    return ring + noise


def _synth_ride_bell(n_samples):
    """Ride bell: brighter, more sustain."""
    ring = _sine_f32(3000, n_samples) * _exp_decay(n_samples, 4) * 0.5
    ring += _sine_f32(4200, n_samples) * _exp_decay(n_samples, 5) * 0.3
    return ring


def _synth_cowbell(n_samples):
    """Cowbell: two detuned tones."""
    n = min(n_samples, int(SAMPLE_RATE * 0.3))
    wave = (_sine_f32(545, n) * 0.6 + _sine_f32(815, n) * 0.4) * _exp_decay(n, 12)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_clave(n_samples):
    """Clave: short high-pitched click."""
    n = min(n_samples, int(SAMPLE_RATE * 0.025))
    wave = _sine_f32(2500, n) * _exp_decay(n, 100)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_conga(hz, n_samples):
    """Conga/bongo: pitched membrane with slap."""
    t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
    freq = hz + 50 * numpy.exp(-25 * t)
    phase = 2 * numpy.pi * numpy.cumsum(freq) / SAMPLE_RATE
    body = numpy.sin(phase) * _exp_decay(n_samples, 10)
    slap = _noise(min(500, n_samples)) * _exp_decay(min(500, n_samples), 60)
    body[:len(slap)] += slap * 0.2
    return body


def _synth_shaker(n_samples):
    """Shaker/maracas: short noise burst."""
    n = min(n_samples, int(SAMPLE_RATE * 0.04))
    wave = _noise(n) * _exp_decay(n, 50)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave * 0.5
    return out


def _synth_tambourine(n_samples):
    """Tambourine: noise + jingle ring."""
    noise = _noise(n_samples) * _exp_decay(n_samples, 15) * 0.4
    jingle = _sine_f32(7000, n_samples) * _exp_decay(n_samples, 20) * 0.2
    return noise + jingle


def _synth_timbale(hz, n_samples):
    """Timbale: bright metallic ring."""
    n = min(n_samples, int(SAMPLE_RATE * 0.2))
    wave = _sine_f32(hz, n) * _exp_decay(n, 15)
    # Add overtone brightness
    wave += _sine_f32(hz * 2.3, n) * _exp_decay(n, 25) * 0.3
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_agogo(hz, n_samples):
    """Agogo bell: pitched metallic ring."""
    n = min(n_samples, int(SAMPLE_RATE * 0.3))
    wave = (_sine_f32(hz, n) * 0.7 + _sine_f32(hz * 1.5, n) * 0.3) * _exp_decay(n, 10)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_guiro(n_samples):
    """Guiro: scraped noise bursts."""
    wave = numpy.zeros(n_samples, dtype=numpy.float32)
    scrape_len = min(int(SAMPLE_RATE * 0.01), n_samples)
    for i in range(0, min(n_samples, int(SAMPLE_RATE * 0.15)), scrape_len * 2):
        end = min(i + scrape_len, n_samples)
        wave[i:end] += _noise(end - i) * 0.6
    wave *= _exp_decay(n_samples, 8)
    return wave


def _render_drum_hit(sound_value, n_samples):
    """Render a single drum sound to a float32 array.

    Args:
        sound_value: A DrumSound enum value (MIDI note number).
        n_samples: Number of samples to render.

    Returns:
        Float32 numpy array.
    """
    from .rhythm import DrumSound

    _dispatch = {
        DrumSound.KICK.value: lambda n: _synth_kick(n),
        DrumSound.SNARE.value: lambda n: _synth_snare(n),
        DrumSound.RIMSHOT.value: lambda n: _synth_rimshot(n),
        DrumSound.CLAP.value: lambda n: _synth_clap(n),
        DrumSound.CLOSED_HAT.value: lambda n: _synth_hat_closed(n),
        DrumSound.OPEN_HAT.value: lambda n: _synth_hat_open(n),
        DrumSound.PEDAL_HAT.value: lambda n: _synth_hat_closed(n),
        DrumSound.LOW_TOM.value: lambda n: _synth_tom(100, n),
        DrumSound.MID_TOM.value: lambda n: _synth_tom(150, n),
        DrumSound.HIGH_TOM.value: lambda n: _synth_tom(200, n),
        DrumSound.CRASH.value: lambda n: _synth_crash(n),
        DrumSound.RIDE.value: lambda n: _synth_ride(n),
        DrumSound.RIDE_BELL.value: lambda n: _synth_ride_bell(n),
        DrumSound.COWBELL.value: lambda n: _synth_cowbell(n),
        DrumSound.CLAVE.value: lambda n: _synth_clave(n),
        DrumSound.SHAKER.value: lambda n: _synth_shaker(n),
        DrumSound.TAMBOURINE.value: lambda n: _synth_tambourine(n),
        DrumSound.CONGA_HIGH.value: lambda n: _synth_conga(300, n),
        DrumSound.CONGA_LOW.value: lambda n: _synth_conga(200, n),
        DrumSound.BONGO_HIGH.value: lambda n: _synth_conga(450, n),
        DrumSound.BONGO_LOW.value: lambda n: _synth_conga(350, n),
        DrumSound.TIMBALE_HIGH.value: lambda n: _synth_timbale(800, n),
        DrumSound.TIMBALE_LOW.value: lambda n: _synth_timbale(600, n),
        DrumSound.AGOGO_HIGH.value: lambda n: _synth_agogo(900, n),
        DrumSound.AGOGO_LOW.value: lambda n: _synth_agogo(700, n),
        DrumSound.GUIRO.value: lambda n: _synth_guiro(n),
        DrumSound.MARACAS.value: lambda n: _synth_shaker(n),
    }

    renderer = _dispatch.get(sound_value, lambda n: _synth_clave(n))
    return renderer(n_samples)


def _render_pattern(pattern, bpm=120):
    """Render a drum Pattern to a float32 audio buffer.

    Args:
        pattern: A Pattern object from rhythm module.
        bpm: Tempo in beats per minute.

    Returns:
        Float32 numpy array of mixed audio.
    """
    samples_per_beat = int(SAMPLE_RATE * 60.0 / bpm)
    total_samples = int(pattern.beats * samples_per_beat)
    buf = numpy.zeros(total_samples, dtype=numpy.float32)

    for hit in pattern.hits:
        start = int(hit.position * samples_per_beat)
        if start >= total_samples:
            continue
        remaining = total_samples - start
        # Render each hit for up to 0.5 seconds
        hit_len = min(int(SAMPLE_RATE * 0.5), remaining)
        wave = _render_drum_hit(hit.sound.value, hit_len)
        vel_scale = hit.velocity / 127.0
        buf[start:start + hit_len] += wave * vel_scale

    # Normalize to prevent clipping
    peak = numpy.max(numpy.abs(buf))
    if peak > 0:
        buf = buf / peak * 0.9
    return buf


def play_pattern(pattern, repeats=1, bpm=120):
    """Play a drum pattern through the speakers.

    Synthesizes each drum sound in real-time and mixes them into a
    single audio buffer. Every ``DrumSound`` has its own synthesized
    voice — kicks have pitch sweeps, snares have noise bursts, hats
    are filtered noise, etc.

    Args:
        pattern: A :class:`Pattern` object.
        repeats: Number of times to loop the pattern (default 1).
        bpm: Tempo in beats per minute (default 120).

    Example::

        >>> from pytheory import Pattern
        >>> play_pattern(Pattern.preset("rock"), repeats=4, bpm=120)
        >>> play_pattern(Pattern.preset("bossa nova"), repeats=4, bpm=140)
    """
    rendered = _render_pattern(pattern, bpm=bpm)
    if repeats > 1:
        rendered = numpy.tile(rendered, repeats)
    sd.play(rendered, SAMPLE_RATE)
    sd.wait()


def play_score(score):
    """Play an entire Score through the speakers.

    Renders both tonal notes (tones/chords) and drum hits, mixed
    together. This is the function to use when you've built a Score
    that combines a chord progression with a drum pattern.

    Args:
        score: A :class:`Score` object with notes and/or drum hits.

    Example::

        >>> from pytheory import Pattern, Key, Duration, Score
        >>> key = Key("A", "minor")
        >>> score = Pattern.preset("bossa nova").to_score(repeats=4, bpm=140)
        >>> for chord in key.progression("i", "iv", "V", "i"):
        ...     score.add(chord, Duration.WHOLE)
        >>> play_score(score)
    """
    samples_per_beat = int(SAMPLE_RATE * 60.0 / score.bpm)
    total_beats = score.total_beats
    total_samples = int(total_beats * samples_per_beat)
    buf = numpy.zeros(total_samples, dtype=numpy.float32)

    # Render tonal notes
    beat_pos = 0.0
    for note in score.notes:
        if note.tone is not None:
            start = int(beat_pos * samples_per_beat)
            dur_ms = note.beats * 60_000 / score.bpm
            rendered = _render(note.tone, t=dur_ms, envelope=Envelope.PIANO)
            rendered_f32 = rendered.astype(numpy.float32) / SAMPLE_PEAK
            end = min(start + len(rendered_f32), total_samples)
            buf[start:end] += rendered_f32[:end - start] * 0.5
        beat_pos += note.beats

    # Render drum hits
    for hit in score._drum_hits:
        start = int(hit.position * samples_per_beat)
        if start >= total_samples:
            continue
        remaining = total_samples - start
        hit_len = min(int(SAMPLE_RATE * 0.5), remaining)
        wave = _render_drum_hit(hit.sound.value, hit_len)
        vel_scale = hit.velocity / 127.0
        buf[start:start + hit_len] += wave * vel_scale * 0.7

    # Normalize
    peak = numpy.max(numpy.abs(buf))
    if peak > 0:
        buf = buf / peak * 0.9

    sd.play(buf, SAMPLE_RATE)
    sd.wait()


# ── MIDI export ─────────────────────────────────────────────────────────────

def _vlq(value):
    """Encode an integer as MIDI variable-length quantity bytes."""
    result = []
    result.append(value & 0x7F)
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(result))


def save_midi(tone_or_chords, path, *, t=500, velocity=100, bpm=120, gap=0):
    """Save a tone, chord, or progression as a Standard MIDI File.

    Writes a Type 0 (single-track) MIDI file that any DAW, notation
    software, or MIDI player can open. Far more useful than WAV for
    musicians — you can edit the notes, change the tempo, transpose,
    and assign any instrument.

    Args:
        tone_or_chords: A Tone, Chord, or list of Tones/Chords.
            A single Tone or Chord is written as one event.
            A list is written as a sequence (progression).
        path: Output file path (e.g. ``"progression.mid"``).
        t: Duration of each note/chord in milliseconds (default 500).
        velocity: MIDI velocity 1-127 (default 100).
        bpm: Tempo in beats per minute (default 120).
        gap: Silence between chords in milliseconds (default 0).

    Example::

        >>> from pytheory import Key, save_midi
        >>> chords = Key("C", "major").progression("I", "V", "vi", "IV")
        >>> save_midi(chords, "pop.mid", t=500, bpm=120)

        >>> save_midi(Tone.from_string("C4"), "middle_c.mid", t=1000)
    """
    import struct

    ticks_per_beat = 480
    us_per_beat = int(60_000_000 / bpm)
    ticks_per_ms = ticks_per_beat * bpm / 60_000

    # Normalize input to a list of items
    if isinstance(tone_or_chords, list):
        items = tone_or_chords
    else:
        items = [tone_or_chords]

    # Build track events
    events = bytearray()

    # Tempo meta event: FF 51 03 <3 bytes of microseconds per beat>
    events += _vlq(0)  # delta time
    events += b'\xFF\x51\x03'
    events += struct.pack('>I', us_per_beat)[1:]  # 3 bytes

    duration_ticks = int(t * ticks_per_ms)
    gap_ticks = int(gap * ticks_per_ms)

    for item in items:
        # Get MIDI note numbers
        if hasattr(item, 'tones'):
            notes = [tone.midi for tone in item.tones if tone.midi is not None]
        else:
            midi = item.midi
            notes = [midi] if midi is not None else []

        if not notes:
            continue

        # Note On events (delta=0 for all)
        for note in notes:
            events += _vlq(0)
            events += bytes([0x90, note & 0x7F, velocity & 0x7F])

        # Note Off events after duration
        for i, note in enumerate(notes):
            delta = duration_ticks if i == 0 else 0
            events += _vlq(delta)
            events += bytes([0x80, note & 0x7F, 0])

        # Gap between chords
        if gap_ticks > 0:
            events += _vlq(gap_ticks)
            events += bytes([0x90, 0, 0])  # silent note-on as spacer
            events += _vlq(0)
            events += bytes([0x80, 0, 0])

    # End of track
    events += _vlq(0)
    events += b'\xFF\x2F\x00'

    # Write MIDI file
    with open(path, 'wb') as f:
        # Header: MThd, length=6, format=0, tracks=1, ticks_per_beat
        f.write(b'MThd')
        f.write(struct.pack('>I', 6))
        f.write(struct.pack('>HHH', 0, 1, ticks_per_beat))
        # Track chunk
        f.write(b'MTrk')
        f.write(struct.pack('>I', len(events)))
        f.write(events)
