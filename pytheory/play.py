from enum import Enum
import time

import numpy
import scipy.signal

from .tones import Tone


def _get_sd():
    """Lazy import sounddevice — only needed for actual audio playback."""
    import sounddevice as sd
    return sd

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


def square_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of a square wave — classic chiptune / 8-bit sound.

    Hollow and buzzy, containing only odd harmonics (1, 3, 5, 7...) each
    at amplitude 1/n. The building block of NES and Game Boy music.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = peak * numpy.sign(numpy.sin(xvalues))
    return numpy.resize(onecycle, (n_samples,)).astype(numpy.int16)


def pulse_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE, duty=0.25):
    """Compute N samples of a pulse wave with variable duty cycle.

    A generalized square wave. Duty cycle controls the timbre:

    - 50% = square wave (hollow)
    - 25% = nasal, reedy (NES pulse channel default)
    - 12.5% = thin, buzzy (NES narrow pulse)

    Width changes dramatically affect the harmonic content — narrower
    pulses emphasize higher harmonics, producing a brighter, more
    cutting sound.
    """
    length = SAMPLE_RATE / float(hz)
    omega = numpy.pi * 2 / length
    xvalues = numpy.arange(int(length)) * omega
    onecycle = scipy.signal.square(xvalues, duty=duty)
    onecycle = (peak * onecycle).astype(numpy.int16)
    return numpy.resize(onecycle, (n_samples,))


def fm_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE,
            mod_ratio=2.0, mod_index=3.0):
    """Compute N samples of an FM synthesis wave.

    One sine wave (the carrier) has its frequency modulated by another
    sine wave (the modulator). This is the basis of the Yamaha DX7 —
    the most commercially successful synthesizer ever made.

    Args:
        hz: Carrier frequency.
        mod_ratio: Modulator frequency as a multiple of carrier.
            Integer ratios (1, 2, 3) produce harmonic timbres (bells,
            electric piano). Non-integer ratios (1.41, 2.76) produce
            inharmonic, metallic sounds.
        mod_index: Modulation depth. Higher = more harmonics = brighter.
            0 = pure sine. 1-3 = warm. 5+ = harsh/metallic.

    Common presets:
        - Electric piano: ratio=1, index=1.5
        - Bell: ratio=3.5, index=5
        - Brass: ratio=1, index=3
        - Metallic: ratio=1.41, index=8
    """
    t = numpy.arange(n_samples, dtype=numpy.float64) / SAMPLE_RATE
    mod_freq = hz * mod_ratio
    modulator = mod_index * numpy.sin(2 * numpy.pi * mod_freq * t)
    carrier = numpy.sin(2 * numpy.pi * hz * t + modulator)
    return (peak * carrier).astype(numpy.int16)


def noise_wave(hz=0, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """Compute N samples of white noise.

    Unpitched — the ``hz`` parameter is accepted for API compatibility
    but ignored. Useful for percussion textures, wind effects, and
    hi-hat-like sounds in melodic parts.
    """
    return (peak * numpy.random.uniform(-1, 1, n_samples)).astype(numpy.int16)


def supersaw_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE,
                  voices=7, detune_cents=15):
    """Compute N samples of a supersaw — multiple detuned saws summed.

    The signature sound of trance and EDM. Multiple sawtooth oscillators
    are slightly detuned from each other, creating a fat, shimmering,
    chorus-like wall of sound. The Roland JP-8000 (1997) popularized
    this as "SuperSaw."

    Args:
        voices: Number of saw oscillators (default 7). More = fatter.
        detune_cents: Maximum detune spread in cents (default 15).
            Each voice is spread evenly across ±detune_cents.
    """
    spread = numpy.linspace(-detune_cents, detune_cents, voices)
    mixed = numpy.zeros(n_samples, dtype=numpy.float64)
    for offset in spread:
        detuned_hz = hz * (2 ** (offset / 1200))
        length = SAMPLE_RATE / float(detuned_hz)
        omega = numpy.pi * 2 / length
        xvalues = numpy.arange(int(length)) * omega
        onecycle = scipy.signal.sawtooth(xvalues, width=1)
        wave = numpy.resize(onecycle, (n_samples,))
        mixed += wave
    mixed /= voices  # normalize
    return (peak * mixed).astype(numpy.int16)


def pwm_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE, lfo_rate=0.3):
    """Compute N samples of a pulse-width modulated wave.

    A pulse wave whose duty cycle sweeps back and forth via an LFO,
    creating a rich, evolving timbre. This is the signature sound of
    the Roland Juno-106 and many classic analog polysynths.

    As the pulse width changes, different harmonics fade in and out,
    producing a natural chorus-like shimmer without any detuning.
    At 50% width it's a square wave; at narrow widths it thins to a
    bright, reedy tone. The constant motion between these extremes
    is what makes PWM so alive-sounding.

    Args:
        lfo_rate: Speed of the width sweep in Hz.
            0.1–0.5 = slow, lush pads.
            1–5 = faster, more vibrato/chorus-like.
    """
    t = numpy.arange(n_samples, dtype=numpy.float64) / SAMPLE_RATE
    # LFO sweeps duty cycle between 0.15 and 0.85
    duty = 0.5 + 0.35 * numpy.sin(2 * numpy.pi * lfo_rate * t)
    # Generate pulse wave sample-by-sample with varying duty
    phase = (t * hz) % 1.0
    wave = numpy.where(phase < duty, 1.0, -1.0)
    return (peak * wave).astype(numpy.int16)


def pwm_slow_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """PWM with slow LFO (0.3 Hz) — lush Juno-style pads."""
    return pwm_wave(hz, peak, n_samples, lfo_rate=0.3)


def pwm_fast_wave(hz, peak=SAMPLE_PEAK, n_samples=SAMPLE_RATE):
    """PWM with fast LFO (3 Hz) — chorused, vibrato-like texture."""
    return pwm_wave(hz, peak, n_samples, lfo_rate=3.0)


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
    _sd = _get_sd()
    _sd.play(normalized_wave, SAMPLE_RATE)
    _sd.wait()


class Synth(Enum):
    """Waveform types for synthesis.

    Each waveform has a distinct timbre based on its harmonic content:

    - **SINE** — pure tone, no harmonics. Smooth and clean.
    - **SAW** — all harmonics at 1/n amplitude. Bright, buzzy, aggressive.
    - **TRIANGLE** — odd harmonics at 1/n². Mellow, woody, hollow.
    - **SQUARE** — odd harmonics at 1/n. Hollow, chiptune, 8-bit.
    - **PULSE** — variable duty cycle square. Nasal, reedy (NES sound).
    - **FM** — frequency modulation synthesis. Bell-like, metallic, DX7.
    - **NOISE** — white noise, unpitched. Percussion, wind, texture.
    - **SUPERSAW** — 7 detuned saws. Fat, shimmery, trance/EDM pads.
    """
    SINE = "sine"
    SAW = "saw"
    TRIANGLE = "triangle"
    SQUARE = "square"
    PULSE = "pulse"
    FM = "fm"
    NOISE = "noise"
    SUPERSAW = "supersaw"
    PWM_SLOW = "pwm_slow"
    PWM_FAST = "pwm_fast"

    def __call__(self, hz, **kwargs):
        """Make Synth members callable — dispatches to the wave function."""
        return _SYNTH_FUNCTIONS[self.value](hz, **kwargs)


_SYNTH_FUNCTIONS = {
    "sine": sine_wave, "saw": sawtooth_wave, "triangle": triangle_wave,
    "square": square_wave, "pulse": pulse_wave, "fm": fm_wave,
    "noise": noise_wave, "supersaw": supersaw_wave,
    "pwm_slow": pwm_slow_wave, "pwm_fast": pwm_fast_wave,
}


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
    """Synthesize a kick drum: 808-style sine with pitch sweep + transient punch."""
    t = numpy.arange(n_samples, dtype=numpy.float32) / SAMPLE_RATE
    # Pitch sweeps from 200 Hz down to 45 Hz — fast sweep for punch
    freq = 45 + 155 * numpy.exp(-50 * t)
    phase = 2 * numpy.pi * numpy.cumsum(freq) / SAMPLE_RATE
    # Main body with longer sustain
    body = numpy.sin(phase) * _exp_decay(n_samples, 6)
    # Hard transient click — the "beater" hitting the head
    click_len = min(300, n_samples)
    click = _noise(click_len) * _exp_decay(click_len, 100)
    body[:click_len] += click * 0.5
    # Sub thump — a brief low sine for chest punch
    sub_len = min(int(SAMPLE_RATE * 0.08), n_samples)
    sub = _sine_f32(50, sub_len) * _exp_decay(sub_len, 20)
    body[:sub_len] += sub * 0.4
    # Soft saturation for warmth and presence
    body = numpy.tanh(body * 1.5) / 1.5
    return body


def _synth_snare(n_samples):
    """Synthesize a snare: pitched body + noise snap + transient click."""
    # Body: 220 Hz (was 180) — brighter, more present
    body = _sine_f32(220, n_samples) * _exp_decay(n_samples, 25) * 0.5
    # Noise rattle: faster decay for snap (was 12)
    noise = _noise(n_samples) * _exp_decay(n_samples, 20) * 0.8
    # Transient click — the stick hitting the head
    click_len = min(150, n_samples)
    click = _noise(click_len) * _exp_decay(click_len, 120)
    body[:click_len] += click * 0.4
    # Soft saturation for presence and density
    return numpy.tanh(body + noise)


def _synth_hat_closed(n_samples):
    """Closed hi-hat: short, crisp, metallic."""
    n = min(n_samples, int(SAMPLE_RATE * 0.03))  # 30ms (was 50ms)
    t = numpy.arange(n, dtype=numpy.float32) / SAMPLE_RATE
    # Metallic harmonics — inharmonic frequencies that make cymbals shimmer
    metallic = (numpy.sin(2 * numpy.pi * 6000 * t) * 0.3 +
                numpy.sin(2 * numpy.pi * 8500 * t) * 0.2 +
                numpy.sin(2 * numpy.pi * 12000 * t) * 0.15)
    noise = _noise(n) * 0.6
    wave = (metallic + noise) * _exp_decay(n, 100)  # fast decay (was 60)
    out = numpy.zeros(n_samples, dtype=numpy.float32)
    out[:n] = wave
    return out


def _synth_hat_open(n_samples):
    """Open hi-hat: bright, metallic, controlled decay."""
    n = min(n_samples, int(SAMPLE_RATE * 0.15))  # 150ms (was 250ms)
    t = numpy.arange(n, dtype=numpy.float32) / SAMPLE_RATE
    metallic = (numpy.sin(2 * numpy.pi * 6000 * t) * 0.3 +
                numpy.sin(2 * numpy.pi * 8500 * t) * 0.2 +
                numpy.sin(2 * numpy.pi * 12000 * t) * 0.15)
    noise = _noise(n) * 0.5
    wave = (metallic + noise) * _exp_decay(n, 18)  # tighter (was 12)
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
    _sd = _get_sd()
    _sd.play(rendered, SAMPLE_RATE)
    _sd.wait()


# ── Audio effects ───────────────────────────────────────────────────────────


def _apply_sidechain(samples, trigger_samples, amount=0.8, attack=0.001, release=0.1, sample_rate=SAMPLE_RATE):
    """Apply sidechain compression — duck the signal when the trigger is loud.

    Args:
        samples: The signal to duck (float32 array).
        trigger_samples: The trigger signal, usually kick drum (float32 array).
        amount: How much to duck, 0.0-1.0 (1.0 = full duck to silence).
        attack: How fast the duck kicks in, in seconds.
        release: How fast the volume comes back, in seconds.

    Returns:
        Float32 array with sidechain applied.
    """
    # Match lengths
    min_len = min(len(samples), len(trigger_samples))
    trigger = trigger_samples[:min_len]
    out = samples.copy()

    # Compute trigger envelope
    trigger_env = numpy.abs(trigger)
    # Smooth the envelope
    alpha_attack = 1.0 - numpy.exp(-1.0 / (attack * sample_rate))
    alpha_release = 1.0 - numpy.exp(-1.0 / (release * sample_rate))
    smoothed = numpy.zeros(len(trigger_env), dtype=numpy.float32)
    for i in range(1, len(trigger_env)):
        if trigger_env[i] > smoothed[i - 1]:
            smoothed[i] = alpha_attack * trigger_env[i] + (1 - alpha_attack) * smoothed[i - 1]
        else:
            smoothed[i] = alpha_release * trigger_env[i] + (1 - alpha_release) * smoothed[i - 1]
    # Normalize envelope to 0-1
    peak = numpy.max(smoothed)
    if peak > 0:
        smoothed /= peak
    # Apply ducking
    gain = 1.0 - smoothed * amount
    out[:min_len] = out[:min_len] * gain
    return out


# ── Convolution reverb impulse responses ───────────────────────────────────

def _generate_ir(preset="taj_mahal", sample_rate=SAMPLE_RATE):
    """Generate a synthetic impulse response for convolution reverb.

    These model the acoustic properties of real spaces — early reflections
    pattern, decay envelope, frequency-dependent absorption, and diffusion.

    Available presets:
        taj_mahal: Massive marble dome — 12s decay, bright early reflections,
                   long diffuse tail with high-frequency rolloff.
        cathedral: Gothic stone cathedral — 6s decay, strong early reflections
                   off parallel walls, dark reverberant tail.
        plate: EMT 140 plate reverb — 4s, dense, bright, smooth.
                The studio classic.
        spring: Spring reverb tank — 3s, metallic, boingy, lo-fi character.
        cave: Natural cave — 8s, very dark, irregular reflections.
        parking_garage: Concrete box — 3s, bright, flutter echoes.
        canyon: Open canyon — 5s, sparse discrete echoes then diffuse tail.
    """
    presets = {
        "taj_mahal": dict(
            duration=12.0,
            early_delays=[0.018, 0.037, 0.052, 0.071, 0.089, 0.112, 0.134,
                          0.158, 0.183, 0.211, 0.243, 0.278, 0.315],
            early_gains=[0.8, 0.72, 0.65, 0.58, 0.52, 0.46, 0.41,
                         0.36, 0.32, 0.28, 0.24, 0.20, 0.17],
            decay_time=12.0,
            hf_damping=0.7,       # marble absorbs highs slowly
            density=8000,         # very dense tail (huge dome)
            brightness=0.6,
            modulation=0.003,     # subtle pitch modulation from dome shape
        ),
        "cathedral": dict(
            duration=6.0,
            early_delays=[0.012, 0.024, 0.041, 0.058, 0.073, 0.095,
                          0.118, 0.145, 0.172],
            early_gains=[0.85, 0.75, 0.65, 0.55, 0.48, 0.40,
                         0.33, 0.27, 0.22],
            decay_time=6.0,
            hf_damping=0.8,       # stone absorbs highs
            density=5000,
            brightness=0.4,
            modulation=0.002,
        ),
        "plate": dict(
            duration=4.0,
            early_delays=[0.003, 0.007, 0.011, 0.016, 0.022, 0.029],
            early_gains=[0.9, 0.85, 0.78, 0.70, 0.62, 0.54],
            decay_time=4.0,
            hf_damping=0.3,       # metal plate — bright
            density=12000,        # very dense, smooth
            brightness=0.85,
            modulation=0.001,
        ),
        "spring": dict(
            duration=3.0,
            early_delays=[0.005, 0.032, 0.064, 0.097, 0.131],
            early_gains=[0.95, 0.7, 0.5, 0.35, 0.25],
            decay_time=3.0,
            hf_damping=0.6,
            density=2000,         # sparse — you hear the spring
            brightness=0.5,
            modulation=0.012,     # springy wobble
        ),
        "cave": dict(
            duration=8.0,
            early_delays=[0.025, 0.058, 0.094, 0.138, 0.189, 0.248, 0.312],
            early_gains=[0.7, 0.55, 0.42, 0.32, 0.24, 0.18, 0.13],
            decay_time=8.0,
            hf_damping=0.9,       # rock absorbs highs aggressively
            density=3000,
            brightness=0.2,       # very dark
            modulation=0.005,
        ),
        "parking_garage": dict(
            duration=3.0,
            early_delays=[0.008, 0.016, 0.024, 0.033, 0.041, 0.050,
                          0.058, 0.067],
            early_gains=[0.9, 0.82, 0.75, 0.68, 0.62, 0.56, 0.50, 0.45],
            decay_time=3.0,
            hf_damping=0.3,       # concrete — bright
            density=6000,
            brightness=0.8,
            modulation=0.0005,
        ),
        "canyon": dict(
            duration=5.0,
            early_delays=[0.12, 0.28, 0.45, 0.67, 0.91],
            early_gains=[0.6, 0.4, 0.28, 0.18, 0.11],
            decay_time=5.0,
            hf_damping=0.5,
            density=1500,         # sparse — open air
            brightness=0.5,
            modulation=0.002,
        ),
    }

    if preset not in presets:
        raise ValueError(
            f"Unknown IR preset {preset!r}. "
            f"Available: {', '.join(sorted(presets))}"
        )

    p = presets[preset]
    n_samples = int(p["duration"] * sample_rate)
    ir = numpy.zeros(n_samples, dtype=numpy.float32)

    # 1. Early reflections — discrete taps
    for delay, gain in zip(p["early_delays"], p["early_gains"]):
        idx = int(delay * sample_rate)
        if idx < n_samples:
            ir[idx] += gain

    # 2. Diffuse tail — shaped noise with exponential decay
    rng = numpy.random.RandomState(42)  # deterministic for reproducibility
    noise = rng.randn(n_samples).astype(numpy.float32)

    # Exponential decay envelope
    t = numpy.arange(n_samples, dtype=numpy.float32) / sample_rate
    decay_env = numpy.exp(-6.91 / p["decay_time"] * t)  # -60dB at decay_time

    # HF damping — apply progressive lowpass to the tail
    # Simulate frequency-dependent absorption: highs decay faster
    if p["hf_damping"] > 0:
        # Simple 1-pole lowpass applied cumulatively
        alpha = p["hf_damping"] * 0.15
        filtered = numpy.zeros_like(noise)
        filtered[0] = noise[0]
        for i in range(1, n_samples):
            # Time-varying cutoff: gets darker over time
            a = min(alpha * (1 + t[i] / p["decay_time"]), 0.95)
            filtered[i] = filtered[i - 1] * a + noise[i] * (1 - a)
        noise = filtered

    # Brightness control — overall spectral tilt
    if p["brightness"] < 0.5:
        cutoff = 1000 + p["brightness"] * 8000
        b, a = scipy.signal.butter(1, cutoff / (sample_rate / 2), btype='low')
        noise = scipy.signal.lfilter(b, a, noise).astype(numpy.float32)
    elif p["brightness"] > 0.7:
        # Add a gentle high shelf boost
        cutoff = 2000
        b, a = scipy.signal.butter(1, cutoff / (sample_rate / 2), btype='high')
        hf = scipy.signal.lfilter(b, a, noise).astype(numpy.float32)
        noise = noise + hf * (p["brightness"] - 0.5)

    # Subtle pitch modulation (simulates irregular surfaces)
    if p["modulation"] > 0:
        mod_freq = 0.5 + rng.rand() * 1.5
        mod = numpy.sin(2 * numpy.pi * mod_freq * t) * p["modulation"]
        # Apply as sample-offset jitter
        indices = numpy.arange(n_samples, dtype=numpy.float32) + mod * sample_rate
        indices = numpy.clip(indices, 0, n_samples - 1)
        noise = numpy.interp(indices, numpy.arange(n_samples), noise).astype(
            numpy.float32
        )

    # Build the tail — start after early reflections end
    early_end = int(max(p["early_delays"]) * sample_rate) if p["early_delays"] else 0
    tail_onset = numpy.zeros(n_samples, dtype=numpy.float32)
    tail_onset[early_end:] = 1.0
    # Smooth crossfade
    fade_len = min(int(0.02 * sample_rate), n_samples - early_end)
    if fade_len > 0:
        tail_onset[early_end:early_end + fade_len] = numpy.linspace(
            0, 1, fade_len
        )

    density_scale = p["density"] / 8000.0
    ir += noise * decay_env * tail_onset * density_scale * 0.15

    # 3. Normalize
    peak = numpy.max(numpy.abs(ir))
    if peak > 0:
        ir /= peak

    return ir


# IR cache — generate once, reuse
_IR_CACHE: dict[str, numpy.ndarray] = {}


def _get_ir(preset, sample_rate=SAMPLE_RATE):
    """Get a cached impulse response."""
    key = f"{preset}_{sample_rate}"
    if key not in _IR_CACHE:
        _IR_CACHE[key] = _generate_ir(preset, sample_rate)
    return _IR_CACHE[key]


def _apply_convolution_reverb(samples, preset="taj_mahal", mix=0.3,
                               sample_rate=SAMPLE_RATE):
    """Apply convolution reverb using a synthetic impulse response.

    Convolves the input signal with an IR that models the acoustic
    properties of a real space — far more realistic than algorithmic reverb.

    Args:
        samples: Float32 numpy array.
        preset: IR preset name (taj_mahal, cathedral, plate, spring,
                cave, parking_garage, canyon).
        mix: Wet/dry ratio 0.0–1.0.
        sample_rate: Sample rate in Hz.

    Returns:
        Float32 array with convolution reverb applied (same length as input).
    """
    if mix <= 0:
        return samples

    ir = _get_ir(preset, sample_rate)

    # FFT-based convolution — fast even for long IRs
    wet = scipy.signal.fftconvolve(samples, ir, mode='full')[:len(samples)]
    wet = wet.astype(numpy.float32)

    # Normalize wet signal to match dry RMS
    dry_rms = numpy.sqrt(numpy.mean(samples ** 2)) + 1e-10
    wet_rms = numpy.sqrt(numpy.mean(wet ** 2)) + 1e-10
    wet *= dry_rms / wet_rms

    return samples * (1 - mix) + wet * mix


def _apply_reverb(samples, mix=0.3, decay=1.0, sample_rate=SAMPLE_RATE):
    """Apply a simple Schroeder reverb to a float32 buffer.

    Uses 4 parallel comb filters + 2 series allpass filters —
    the classic algorithmic reverb topology from Manfred Schroeder (1962).

    Args:
        samples: Float32 numpy array.
        mix: Wet/dry ratio 0.0–1.0.
        decay: Tail length in seconds.
        sample_rate: Sample rate in Hz.

    Returns:
        Float32 array with reverb applied.
    """
    if mix <= 0:
        return samples

    n = len(samples)
    out = numpy.zeros(n, dtype=numpy.float32)

    # Comb filter delays (in samples) — tuned to avoid coloration
    comb_delays = [int(d * sample_rate) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
    # Feedback gains based on decay time
    comb_gains = [0.001 ** (d / sample_rate / decay) for d in comb_delays]

    for delay, gain in zip(comb_delays, comb_gains):
        buf = numpy.zeros(n + delay, dtype=numpy.float32)
        for i in range(n):
            buf[i + delay] += samples[i] + gain * buf[i]
        out += buf[:n]

    out /= len(comb_delays)

    # Allpass filters for diffusion
    for delay_sec in [0.005, 0.0017]:
        delay = int(delay_sec * sample_rate)
        gain = 0.7
        buf = numpy.zeros(n + delay, dtype=numpy.float32)
        result = numpy.zeros(n, dtype=numpy.float32)
        for i in range(n):
            buf[i + delay] = out[i] + gain * buf[i]
            result[i] = -gain * buf[i + delay] + buf[i]
        out = result

    return samples * (1 - mix) + out * mix


def _apply_delay(samples, mix=0.25, time=0.375, feedback=0.4,
                 sample_rate=SAMPLE_RATE):
    """Apply a tempo-synced delay effect.

    Args:
        samples: Float32 numpy array.
        mix: Wet/dry ratio 0.0–1.0.
        time: Delay time in seconds (0.375 = dotted 8th at 120bpm).
        feedback: How much each echo feeds back (0.0–1.0).
        sample_rate: Sample rate in Hz.

    Returns:
        Float32 array with delay applied.
    """
    if mix <= 0:
        return samples

    delay_samples = int(time * sample_rate)
    if delay_samples <= 0:
        return samples

    n = len(samples)
    wet = numpy.zeros(n, dtype=numpy.float32)
    buf = numpy.zeros(n, dtype=numpy.float32)
    buf[:] = samples

    # Generate echo taps
    max_echoes = 8
    gain = 1.0
    for _ in range(max_echoes):
        gain *= feedback
        if gain < 0.01:
            break
        shifted = numpy.zeros(n, dtype=numpy.float32)
        offset = delay_samples * (_ + 1)
        if offset >= n:
            break
        end = min(n, n - offset)
        if end > 0:
            shifted[offset:offset + end] = buf[:end] * gain
            wet += shifted

    return samples * (1 - mix) + wet * mix


def _apply_lowpass(samples, cutoff, q=0.707, sample_rate=SAMPLE_RATE):
    """Apply a 2nd-order Butterworth lowpass filter (12 dB/octave).

    A resonant lowpass filter — the sound of analog synthesizers.
    At Q=0.707 (Butterworth), the response is maximally flat. Higher
    Q values add a resonant peak at the cutoff frequency, emphasizing
    that frequency range before rolling off.

    Args:
        samples: Float32 numpy array.
        cutoff: Cutoff frequency in Hz.
        q: Resonance / Q factor (default 0.707 = Butterworth flat).
            1.0 = slight peak, 2.0 = pronounced peak, 5.0+ = aggressive.
        sample_rate: Sample rate in Hz.

    Returns:
        Float32 array with filter applied.
    """
    if cutoff <= 0 or cutoff >= sample_rate / 2:
        return samples

    # Biquad coefficient calculation
    w0 = 2 * numpy.pi * cutoff / sample_rate
    alpha = numpy.sin(w0) / (2 * q)

    b0 = (1 - numpy.cos(w0)) / 2
    b1 = 1 - numpy.cos(w0)
    b2 = (1 - numpy.cos(w0)) / 2
    a0 = 1 + alpha
    a1 = -2 * numpy.cos(w0)
    a2 = 1 - alpha

    # Normalize
    b = numpy.array([b0/a0, b1/a0, b2/a0])
    a = numpy.array([1.0, a1/a0, a2/a0])

    return scipy.signal.lfilter(b, a, samples).astype(numpy.float32)


def _apply_chorus(samples, mix=0.5, rate=1.5, depth=0.003,
                   sample_rate=SAMPLE_RATE):
    """Apply a chorus effect — slightly detuned delayed copy mixed in.

    Chorus works by duplicating the signal, modulating the copy's delay
    time with an LFO, and mixing it back. The varying delay creates
    pitch wobble that thickens the sound — like two musicians playing
    the same part slightly out of sync.

    This is the classic Roland Juno chorus, the Boss CE-1, and every
    string ensemble synth ever made.

    Args:
        samples: Float32 numpy array.
        mix: Wet/dry ratio 0.0–1.0.
        rate: LFO speed in Hz (default 1.5). 0.5–1 = slow shimmer,
            2–4 = fast vibrato, 5+ = Leslie speaker territory.
        depth: Modulation depth in seconds (default 0.003 = 3ms).
            Controls how far the pitch wobbles.
        sample_rate: Sample rate in Hz.

    Returns:
        Float32 array with chorus applied.
    """
    if mix <= 0:
        return samples

    n = len(samples)
    t = numpy.arange(n, dtype=numpy.float32) / sample_rate

    # LFO modulates the delay time
    base_delay = 0.007  # 7ms base delay
    lfo = depth * numpy.sin(2 * numpy.pi * rate * t)
    delay_samples = ((base_delay + lfo) * sample_rate).astype(numpy.int32)

    # Build the modulated delayed copy
    wet = numpy.zeros(n, dtype=numpy.float32)
    for i in range(n):
        read_pos = i - delay_samples[i]
        if 0 <= read_pos < n:
            wet[i] = samples[read_pos]

    return samples * (1 - mix * 0.5) + wet * mix * 0.5


def _apply_distortion(samples, drive=1.0, mix=1.0):
    """Apply soft-clip distortion (tanh waveshaping).

    Models the warm saturation of an overdriven tube amplifier.
    Low drive values add subtle harmonic warmth; high values
    produce aggressive fuzz.

    The tanh function is the classic soft clipper — it smoothly
    compresses peaks rather than hard-clipping them, which is
    why tube amps sound "warm" when overdriven while digital
    clipping sounds harsh.

    Args:
        samples: Float32 numpy array.
        drive: Gain before clipping, 0.5–20.0.
            0.5–2 = subtle warmth (tube preamp)
            3–8 = overdrive (cranked amp)
            10+ = fuzz/distortion
        mix: Wet/dry ratio 0.0–1.0.

    Returns:
        Float32 array with distortion applied.
    """
    if mix <= 0 or drive <= 0:
        return samples
    driven = numpy.tanh(samples * drive)
    return samples * (1 - mix) + driven * mix


def _apply_effects_with_params(samples, params):
    """Apply effects using a params dict. Used for both static and automated rendering."""
    # Signal chain: distortion → chorus → lowpass → delay → reverb
    if params.get("distortion_mix", 0) > 0:
        samples = _apply_distortion(samples,
                                    drive=params.get("distortion_drive", 3.0),
                                    mix=params["distortion_mix"])
    if params.get("chorus_mix", 0) > 0:
        samples = _apply_chorus(samples,
                                mix=params["chorus_mix"],
                                rate=params.get("chorus_rate", 1.5),
                                depth=params.get("chorus_depth", 0.003))
    if params.get("lowpass", 0) > 0:
        samples = _apply_lowpass(samples, params["lowpass"],
                                 params.get("lowpass_q", 0.707))
    if params.get("delay_mix", 0) > 0:
        samples = _apply_delay(samples, mix=params["delay_mix"],
                               time=params.get("delay_time", 0.375),
                               feedback=params.get("delay_feedback", 0.4))
    if params.get("reverb_mix", 0) > 0:
        reverb_type = params.get("reverb_type", "algorithmic")
        if reverb_type != "algorithmic" and reverb_type in (
            "taj_mahal", "cathedral", "plate", "spring",
            "cave", "parking_garage", "canyon",
        ):
            samples = _apply_convolution_reverb(
                samples, preset=reverb_type, mix=params["reverb_mix"])
        else:
            samples = _apply_reverb(samples, mix=params["reverb_mix"],
                                    decay=params.get("reverb_decay", 1.0))
    return samples


def _apply_part_effects(samples, part):
    """Apply all effects configured on a Part to a float32 buffer."""
    params = {
        "distortion_mix": part.distortion_mix,
        "distortion_drive": part.distortion_drive,
        "chorus_mix": part.chorus_mix,
        "chorus_rate": part.chorus_rate,
        "chorus_depth": part.chorus_depth,
        "lowpass": part.lowpass,
        "lowpass_q": part.lowpass_q,
        "delay_mix": part.delay_mix,
        "delay_time": part.delay_time,
        "delay_feedback": part.delay_feedback,
        "reverb_mix": part.reverb_mix,
        "reverb_decay": part.reverb_decay,
        "reverb_type": getattr(part, "reverb_type", "algorithmic"),
    }
    return _apply_effects_with_params(samples, params)


def _pan_to_stereo(mono, pan=0.0):
    """Pan a mono buffer into a stereo (N, 2) array.

    Args:
        mono: Float32 1D array.
        pan: -1.0 (full left) to 1.0 (full right). 0.0 = center.

    Returns:
        Float32 (N, 2) array.
    """
    # Constant-power panning (equal loudness across the field)
    angle = (pan + 1.0) * 0.25 * numpy.pi  # 0 to pi/2
    left_gain = numpy.cos(angle)
    right_gain = numpy.sin(angle)
    stereo = numpy.zeros((len(mono), 2), dtype=numpy.float32)
    stereo[:, 0] = mono * left_gain
    stereo[:, 1] = mono * right_gain
    return stereo


def _master_compress(samples, threshold=0.5, ratio=4.0, attack=0.002,
                     release=0.05, makeup=True, limiter=True,
                     sample_rate=SAMPLE_RATE):
    """Master bus compressor with brick-wall limiter.

    Makes the mix louder, punchier, and more cohesive. Reduces the
    dynamic range so quiet parts come up and loud parts are controlled —
    the difference between a bedroom demo and a finished mix.

    The compressor uses feed-forward gain reduction with envelope
    following. The limiter is a brick-wall at 0.95 to prevent clipping.

    Args:
        samples: Float32 numpy array (the full mix).
        threshold: Level above which compression kicks in (0.0–1.0).
            Lower = more compression. 0.3–0.5 is typical for a master.
        ratio: Compression ratio above threshold (default 4:1).
            2:1 = gentle, 4:1 = moderate, 10:1 = heavy, inf = limiter.
        attack: How fast the compressor reacts, in seconds.
        release: How fast it lets go, in seconds.
        makeup: If True, apply makeup gain to restore loudness.
        limiter: If True, apply brick-wall limiter at 0.95.
        sample_rate: Sample rate in Hz.

    Returns:
        Float32 array — compressed and limited.
    """
    if len(samples) == 0:
        return samples

    # Compute envelope (absolute value, smoothed)
    env = numpy.abs(samples)
    alpha_a = 1.0 - numpy.exp(-1.0 / (attack * sample_rate))
    alpha_r = 1.0 - numpy.exp(-1.0 / (release * sample_rate))

    smoothed = numpy.zeros(len(env), dtype=numpy.float32)
    smoothed[0] = env[0]
    for i in range(1, len(env)):
        if env[i] > smoothed[i - 1]:
            smoothed[i] = alpha_a * env[i] + (1 - alpha_a) * smoothed[i - 1]
        else:
            smoothed[i] = alpha_r * env[i] + (1 - alpha_r) * smoothed[i - 1]

    # Compute gain reduction
    gain = numpy.ones(len(samples), dtype=numpy.float32)
    above = smoothed > threshold
    if numpy.any(above):
        # dB domain compression
        over = smoothed[above] / threshold
        reduced = threshold * (over ** (1.0 / ratio))
        gain[above] = reduced / smoothed[above]

    # Apply gain
    compressed = samples * gain

    # Makeup gain — bring the level back up
    if makeup:
        peak = numpy.max(numpy.abs(compressed))
        if peak > 0:
            compressed = compressed / peak * 0.9

    # Brick-wall limiter — hard clip at 0.95
    if limiter:
        compressed = numpy.clip(compressed, -0.95, 0.95)

    return compressed


def _resolve_synth(name):
    """Map synth name string to wave function."""
    return _SYNTH_FUNCTIONS.get(name, sine_wave)


def _resolve_envelope(name):
    """Map envelope name string to Envelope enum value tuple."""
    _map = {e.name.lower(): e.value for e in Envelope}
    return _map.get(name, Envelope.PIANO.value)


def _build_tempo_map(score):
    """Return sorted list of (beat, samples_per_beat) tuples."""
    changes = [(0.0, int(SAMPLE_RATE * 60.0 / score.bpm))]
    for beat, bpm in sorted(score._tempo_changes):
        changes.append((beat, int(SAMPLE_RATE * 60.0 / bpm)))
    return changes


def _beat_to_sample(beat, tempo_map):
    """Convert a beat position to a sample position using tempo map."""
    sample = 0
    prev_beat = 0.0
    prev_spb = tempo_map[0][1]
    for change_beat, spb in tempo_map[1:]:
        if beat <= change_beat:
            break
        sample += int((change_beat - prev_beat) * prev_spb)
        prev_beat = change_beat
        prev_spb = spb
    sample += int((beat - prev_beat) * prev_spb)
    return sample


def _total_samples_from_tempo_map(total_beats, tempo_map):
    """Compute total samples accounting for tempo changes."""
    return _beat_to_sample(total_beats, tempo_map)


def _render_notes_to_buf(notes, buf, samples_per_beat, total_samples,
                         synth_fn, envelope_tuple, volume, bpm,
                         swing=0.0, tempo_map=None, humanize=0.0,
                         detune=0.0, spread=0.0, stereo_buf=None):
    """Render a list of Notes into an existing buffer at the correct positions."""
    import random as _rnd

    a, d, s, r = envelope_tuple
    beat_pos = 0.0
    for note_index, note in enumerate(notes):
        if note.tone is not None:
            if tempo_map and len(tempo_map) > 1:
                start = _beat_to_sample(beat_pos, tempo_map)
            else:
                start = int(beat_pos * samples_per_beat)
            # Apply swing: shift every other note later
            if swing > 0.0 and note_index % 2 == 1:
                swing_offset = int(swing * 0.5 * samples_per_beat)
                start += swing_offset
            # Humanize: random timing offset (±fraction of a beat)
            if humanize > 0.0:
                max_offset = int(humanize * 0.05 * samples_per_beat)
                start += _rnd.randint(-max_offset, max_offset)
                start = max(0, start)
            dur_ms = note.beats * 60_000 / bpm
            n_samples = int(SAMPLE_RATE * dur_ms / 1000)
            if start + n_samples > total_samples:
                n_samples = total_samples - start
            if n_samples > 0 and start >= 0:
                # Get pitches
                if hasattr(note.tone, 'tones'):
                    pitches = [t.pitch() for t in note.tone.tones]
                else:
                    pitches = [note.tone.pitch()]
                # Render oscillators
                waves = [synth_fn(hz, n_samples=n_samples) for hz in pitches]
                # Detune: add oscillators shifted by ±cents
                detune_up = None
                detune_down = None
                if detune > 0:
                    up_waves = []
                    down_waves = []
                    for hz in pitches:
                        hz_up = hz * (2 ** (detune / 1200))
                        hz_down = hz * (2 ** (-detune / 1200))
                        up_waves.append(synth_fn(hz_up, n_samples=n_samples))
                        down_waves.append(synth_fn(hz_down, n_samples=n_samples))
                    if spread > 0 and stereo_buf is not None:
                        # Spread: detuned oscillators go to opposite channels
                        detune_up = sum(w.astype(numpy.float32) for w in up_waves) / SAMPLE_PEAK
                        detune_down = sum(w.astype(numpy.float32) for w in down_waves) / SAMPLE_PEAK
                    else:
                        waves.extend(up_waves + down_waves)
                n_osc = len(waves)
                mixed = sum(w.astype(numpy.float32) for w in waves) / (SAMPLE_PEAK * max(1, n_osc))
                if a > 0 or d > 0 or s < 1.0 or r > 0:
                    mixed = _apply_envelope(mixed, a, d, s, r)
                # Apply per-note velocity scaling + humanize velocity
                vel = getattr(note, 'velocity', 100)
                if humanize > 0.0:
                    vel_jitter = int(humanize * 15)
                    vel = max(1, min(127, vel + _rnd.randint(-vel_jitter, vel_jitter)))
                vel_scale = vel / 127.0
                end = min(start + len(mixed), total_samples)
                buf[start:end] += mixed[:end - start] * volume * vel_scale
                # Spread detuned oscillators into stereo L/R
                if detune_up is not None and stereo_buf is not None:
                    spread_amt = spread
                    up_env = detune_up[:end - start]
                    down_env = detune_down[:end - start]
                    if a > 0 or d > 0 or s < 1.0 or r > 0:
                        up_env = _apply_envelope(up_env.copy(), a, d, s, r)
                        down_env = _apply_envelope(down_env.copy(), a, d, s, r)
                    gain = volume * vel_scale * 0.5
                    # Right channel gets up-detuned, left gets down-detuned
                    stereo_buf[start:end, 1] += up_env * gain * spread_amt
                    stereo_buf[start:end, 0] += down_env * gain * spread_amt
        beat_pos += note.beats


def _render_legato_to_buf(notes, buf, samples_per_beat, total_samples,
                          synth_fn, envelope_tuple, volume, bpm,
                          glide_time=0.0, swing=0.0, tempo_map=None):
    """Render notes as one continuous waveform with pitch glide.

    Instead of rendering each note separately with its own envelope,
    legato mode generates a single continuous oscillator whose
    frequency changes at note boundaries. The envelope is applied
    once over the entire phrase — attack at the start, release at
    the end, sustain throughout.

    When glide > 0, the frequency slides smoothly between consecutive
    pitches using exponential interpolation (so slides sound linear
    in pitch, not frequency — matching how humans perceive pitch).
    """
    # Build a frequency timeline: (sample_position, target_hz) pairs
    events = []  # (start_sample, end_sample, hz_or_none, velocity)
    beat_pos = 0.0
    for note_index, note in enumerate(notes):
        if tempo_map and len(tempo_map) > 1:
            start = _beat_to_sample(beat_pos, tempo_map)
        else:
            start = int(beat_pos * samples_per_beat)
        # Apply swing
        if swing > 0.0 and note_index % 2 == 1:
            swing_offset = int(swing * 0.5 * samples_per_beat)
            start += swing_offset
        dur_samples = int(note.beats * samples_per_beat)
        end = min(start + dur_samples, total_samples)
        vel = getattr(note, 'velocity', 100)
        if note.tone is not None:
            if hasattr(note.tone, 'tones'):
                hz = note.tone.tones[0].pitch()  # use root for chords
            else:
                hz = note.tone.pitch()
            events.append((start, end, hz, vel))
        else:
            events.append((start, end, 0, vel))  # rest
        beat_pos += note.beats

    if not events:
        return

    # Build the frequency curve with glide
    glide_samples = int(glide_time * SAMPLE_RATE)
    freq_curve = numpy.zeros(total_samples, dtype=numpy.float64)
    amp_curve = numpy.zeros(total_samples, dtype=numpy.float32)
    prev_hz = 0

    for start, end, hz, vel in events:
        if start >= total_samples:
            break
        end = min(end, total_samples)
        vel_scale = vel / 127.0
        if hz > 0:
            amp_curve[start:end] = vel_scale
            if glide_samples > 0 and prev_hz > 0 and prev_hz != hz:
                # Exponential glide from prev_hz to hz
                g_end = min(start + glide_samples, end)
                g_len = g_end - start
                if g_len > 0:
                    t = numpy.linspace(0, 1, g_len)
                    # Log interpolation for perceptually linear pitch slide
                    freq_curve[start:g_end] = prev_hz * (hz / prev_hz) ** t
                    freq_curve[g_end:end] = hz
                else:
                    freq_curve[start:end] = hz
            else:
                freq_curve[start:end] = hz
            prev_hz = hz
        else:
            # Rest: silence but keep prev_hz for next glide
            amp_curve[start:end] = 0.0
            freq_curve[start:end] = prev_hz if prev_hz > 0 else 440

    # Generate continuous waveform from frequency curve
    # Use phase accumulation for smooth frequency changes
    phase = numpy.cumsum(2 * numpy.pi * freq_curve / SAMPLE_RATE)
    wave = numpy.sin(phase).astype(numpy.float32)

    # Apply amplitude (on/off for notes vs rests, scaled by velocity)
    wave *= amp_curve

    # Apply single envelope over the entire active region
    # Find first and last non-zero samples
    active = numpy.nonzero(amp_curve)[0]
    if len(active) == 0:
        return

    first = active[0]
    last = active[-1] + 1
    a, d, s, r = envelope_tuple
    if a > 0 or d > 0 or s < 1.0 or r > 0:
        env_buf = wave[first:last].copy()
        env_buf = _apply_envelope(env_buf, a, d, s, r)
        wave[first:last] = env_buf

    end = min(len(wave), total_samples)
    buf[:end] += wave[:end] * volume


def render_score(score):
    """Render a Score to a float32 audio buffer.

    Mixes all parts (named and default), plus drum hits, into a
    single normalized buffer.

    Args:
        score: A :class:`Score` object.

    Returns:
        Float32 stereo numpy array (N, 2).
    """
    # Build tempo map for variable tempo support
    tempo_map = _build_tempo_map(score)
    has_tempo_changes = len(tempo_map) > 1

    samples_per_beat = int(SAMPLE_RATE * 60.0 / score.bpm)
    total_beats = score.total_beats

    if has_tempo_changes:
        total_samples = _total_samples_from_tempo_map(total_beats, tempo_map)
    else:
        total_samples = int(total_beats * samples_per_beat)
    # Stereo master buffer
    stereo_buf = numpy.zeros((total_samples, 2), dtype=numpy.float32)
    # Mono buffer for backwards-compat rendering
    buf = numpy.zeros(total_samples, dtype=numpy.float32)

    # Default notes (backwards-compatible .add() calls)
    if score.notes:
        _render_notes_to_buf(
            score.notes, buf, samples_per_beat, total_samples,
            sine_wave, Envelope.PIANO.value, 0.5, score.bpm,
            swing=score.swing, tempo_map=tempo_map if has_tempo_changes else None)

    # Named parts — each rendered to own buffer for per-part effects
    _pending_sidechain = []
    for part in score.parts.values():
        if part.notes:
            part_buf = numpy.zeros(total_samples, dtype=numpy.float32)
            synth_fn = _resolve_synth(part.synth)
            env_tuple = _resolve_envelope(part.envelope)
            # Use part swing if set, otherwise score swing
            effective_swing = part.swing if part.swing is not None else score.swing
            if part.legato:
                _render_legato_to_buf(
                    part.notes, part_buf, samples_per_beat, total_samples,
                    synth_fn, env_tuple, part.volume, score.bpm,
                    glide_time=part.glide, swing=effective_swing,
                    tempo_map=tempo_map if has_tempo_changes else None)
            else:
                _render_notes_to_buf(
                    part.notes, part_buf, samples_per_beat, total_samples,
                    synth_fn, env_tuple, part.volume, score.bpm,
                    swing=effective_swing,
                    tempo_map=tempo_map if has_tempo_changes else None,
                    humanize=part.humanize,
                    detune=part.detune,
                    spread=part.spread,
                    stereo_buf=stereo_buf)

            # Apply effects — segmented if automation exists
            auto_points = part._get_automation_points()
            if auto_points:
                # Split buffer at automation boundaries, process each segment
                boundaries = sorted(set([0.0] + auto_points + [total_beats]))
                for i in range(len(boundaries) - 1):
                    seg_start_beat = boundaries[i]
                    seg_end_beat = boundaries[i + 1]
                    seg_start = int(seg_start_beat * samples_per_beat)
                    seg_end = min(int(seg_end_beat * samples_per_beat),
                                  total_samples)
                    if seg_end <= seg_start:
                        continue
                    params = part._get_params_at(seg_start_beat)
                    segment = part_buf[seg_start:seg_end].copy()
                    has_fx = any(params.get(k, 0) > 0 for k in
                                ["distortion_mix", "chorus_mix", "lowpass",
                                 "delay_mix", "reverb_mix"])
                    if has_fx:
                        segment = _apply_effects_with_params(segment, params)
                    # Apply volume automation
                    seg_vol = params.get("volume", part.volume)
                    if seg_vol != part.volume:
                        segment = segment * (seg_vol / part.volume) if part.volume > 0 else segment
                    part_buf[seg_start:seg_end] = segment
            else:
                has_fx = (part.lowpass > 0 or part.delay_mix > 0
                          or part.reverb_mix > 0 or part.distortion_mix > 0
                          or part.chorus_mix > 0)
                if has_fx:
                    part_buf = _apply_part_effects(part_buf, part)
            # Apply sidechain compression if enabled
            if getattr(part, 'sidechain', 0) > 0:
                _pending_sidechain.append((part, part_buf))
            else:
                # Pan mono part into stereo
                stereo_buf += _pan_to_stereo(part_buf, part.pan)

    # Drum hits — render to separate buffer for sidechain trigger
    drum_buf = numpy.zeros(total_samples, dtype=numpy.float32)
    drum_swing = score.swing
    for hit in score._drum_hits:
        pos = hit.position
        # Apply swing: hits on offbeats get pushed later
        if drum_swing > 0:
            beat_frac = pos % 1.0
            # Offbeat = not on a downbeat (0.0) — shift 8th note upbeats
            if 0.1 < beat_frac < 0.9:
                pos += drum_swing * 0.15  # subtle swing on drum hits
        if has_tempo_changes:
            start = _beat_to_sample(pos, tempo_map)
        else:
            start = int(pos * samples_per_beat)
        if start >= total_samples or start < 0:
            continue
        remaining = total_samples - start
        hit_len = min(int(SAMPLE_RATE * 0.5), remaining)
        wave = _render_drum_hit(hit.sound.value, hit_len)
        vel_scale = hit.velocity / 127.0
        drum_buf[start:start + hit_len] += wave * vel_scale * 0.7

    # Apply sidechain compression to parts that request it
    for part, part_buf in _pending_sidechain:
        part_buf = _apply_sidechain(
            part_buf, drum_buf,
            amount=part.sidechain,
            release=part.sidechain_release)
        stereo_buf += _pan_to_stereo(part_buf, part.pan)

    # Default notes (mono, center)
    if score.notes:
        stereo_buf += _pan_to_stereo(buf, 0.0)

    # Drums: center
    stereo_buf += _pan_to_stereo(drum_buf, 0.0)

    # Master bus compressor/limiter (per channel)
    stereo_buf[:, 0] = _master_compress(stereo_buf[:, 0])
    stereo_buf[:, 1] = _master_compress(stereo_buf[:, 1])

    return stereo_buf


def play_score(score):
    """Play an entire Score through the speakers.

    Renders drums, default notes, and all named parts — each with
    its own synth voice and envelope — mixed into one audio buffer.

    Args:
        score: A :class:`Score` object with notes, parts, and/or drum hits.

    Example::

        >>> from pytheory import Pattern, Key, Duration, Score
        >>> key = Key("A", "minor")
        >>> score = Score("4/4", bpm=140)
        >>> score.add_pattern(Pattern.preset("bossa nova"), repeats=4)
        >>> chords = score.part("chords", synth="sine", envelope="pad")
        >>> lead = score.part("lead", synth="saw", envelope="pluck")
        >>> for chord in key.progression("i", "iv", "V", "i"):
        ...     chords.add(chord, Duration.WHOLE)
        >>> lead.add("E5", Duration.QUARTER).add("D5", Duration.QUARTER)
        >>> play_score(score)
    """
    buf = render_score(score)
    _sd = _get_sd()
    _sd.play(buf, SAMPLE_RATE)
    _sd.wait()


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
