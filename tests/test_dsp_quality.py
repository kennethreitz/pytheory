"""Real DSP assertions for the synth/effects/render core.

Unlike the "renders non-empty" smoke tests, these check *actual signal
properties* — pitch, spectral tilt, envelope shape, filter response, echo
timing, reverb tails, stereo width — so the audio engine is locked down and
safe to optimise or refactor without silently changing the sound.

Pure numpy/scipy; no audio device needed.
"""
import numpy as np
import pytest

from pytheory.play import (
    SAMPLE_RATE,
    sine_wave,
    square_wave,
    triangle_wave,
    _apply_envelope,
    _apply_lowpass,
    _apply_highpass,
    _apply_delay,
    _apply_reverb,
    _apply_convolution_reverb_stereo,
    _generate_ir,
    _pan_to_stereo,
    _master_compress,
    _master_bus,
    _soft_clip,
    _GENERATED_IR_CACHE,
    _IR_DURATIONS,
)


def _dominant_freq(signal, sample_rate=SAMPLE_RATE):
    """Return the frequency (Hz) of the largest spectral peak."""
    sig = np.asarray(signal, dtype=np.float64)
    spectrum = np.abs(np.fft.rfft(sig))
    freqs = np.fft.rfftfreq(len(sig), 1.0 / sample_rate)
    return freqs[np.argmax(spectrum)]


def _band_energy(signal, lo, hi, sample_rate=SAMPLE_RATE):
    """Energy of a signal within a [lo, hi] Hz band."""
    sig = np.asarray(signal, dtype=np.float64)
    spectrum = np.abs(np.fft.rfft(sig)) ** 2
    freqs = np.fft.rfftfreq(len(sig), 1.0 / sample_rate)
    return float(spectrum[(freqs >= lo) & (freqs < hi)].sum())


def _rms(signal):
    return float(np.sqrt(np.mean(np.asarray(signal, dtype=np.float64) ** 2)))


# ── Oscillators ────────────────────────────────────────────────────────

@pytest.mark.parametrize("hz", [110.0, 440.0, 1000.0])
def test_sine_wave_has_correct_pitch(hz):
    wave = sine_wave(hz, n_samples=SAMPLE_RATE)
    assert abs(_dominant_freq(wave) - hz) < 5.0  # a few FFT bins (fade spreads it)


def test_square_is_richer_in_harmonics_than_sine():
    # A square wave's odd harmonics put far more energy above the
    # fundamental than a pure sine of the same pitch.
    f0 = 220.0
    sine_hi = _band_energy(sine_wave(f0), 2 * f0, 20000)
    square_hi = _band_energy(square_wave(f0), 2 * f0, 20000)
    assert square_hi > 50 * sine_hi


def test_triangle_pitch_matches_fundamental():
    assert abs(_dominant_freq(triangle_wave(330.0)) - 330.0) < 5.0


# ── Envelope ───────────────────────────────────────────────────────────

def test_envelope_decays_to_a_quiet_tail():
    wave = sine_wave(440.0, n_samples=SAMPLE_RATE).astype(np.float64)
    enveloped = _apply_envelope(wave, attack=0.005, decay=0.1,
                                sustain=0.0, release=0.2)
    head = _rms(enveloped[:2205])          # first 50 ms
    tail = _rms(enveloped[-2205:])         # last 50 ms
    assert tail < 0.2 * head               # clearly decayed away


def test_envelope_attack_ramps_up_from_silence():
    wave = sine_wave(440.0, n_samples=SAMPLE_RATE).astype(np.float64)
    enveloped = _apply_envelope(wave, attack=0.2, decay=0.1,
                                sustain=0.8, release=0.1)
    assert _rms(enveloped[:441]) < _rms(enveloped[4410:8820])  # 10ms vs ~150ms


# ── Filters ────────────────────────────────────────────────────────────

def test_lowpass_attenuates_highs_keeps_lows():
    t = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    low = np.sin(2 * np.pi * 200 * t).astype(np.float32)
    high = np.sin(2 * np.pi * 8000 * t).astype(np.float32)
    assert _rms(_apply_lowpass(low, 1000)) > 0.6        # low passes through
    assert _rms(_apply_lowpass(high, 1000)) < 0.1       # high is killed


def test_highpass_attenuates_lows_keeps_highs():
    t = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    low = np.sin(2 * np.pi * 80 * t).astype(np.float32)
    high = np.sin(2 * np.pi * 6000 * t).astype(np.float32)
    assert _rms(_apply_highpass(low, 1500)) < 0.15
    assert _rms(_apply_highpass(high, 1500)) > 0.6


# ── Delay ──────────────────────────────────────────────────────────────

def test_delay_produces_an_echo_at_the_set_time():
    n = SAMPLE_RATE
    impulse = np.zeros(n, dtype=np.float32)
    impulse[0] = 1.0
    out = _apply_delay(impulse, mix=0.5, time=0.25, feedback=0.5)
    echo_idx = int(0.25 * SAMPLE_RATE)
    # There should be a clear echo around the delay time, and near-silence
    # just before it.
    assert abs(out[echo_idx]) > 0.1
    assert _rms(out[echo_idx - 2000:echo_idx - 500]) < 0.01


# ── Reverb ─────────────────────────────────────────────────────────────

def test_reverb_adds_a_tail_after_the_dry_signal():
    n = SAMPLE_RATE
    burst = np.zeros(n, dtype=np.float32)
    burst[:1000] = sine_wave(440.0, n_samples=1000).astype(np.float32) / 4096
    dry_tail = _rms(burst[5000:])
    wet = _apply_reverb(burst, mix=0.6, decay=1.5)
    assert _rms(wet[5000:]) > 5 * (dry_tail + 1e-9)   # energy where dry had none


def test_stereo_convolution_reverb_has_real_width():
    # Regression guard: L and R IRs must differ, or the "stereo" reverb is
    # secretly mono (the seed bug).
    sig = np.zeros(SAMPLE_RATE, dtype=np.float32)
    sig[0] = 1.0
    stereo = _apply_convolution_reverb_stereo(sig, preset="hall", mix=1.0)
    assert stereo.shape[1] == 2
    assert np.abs(stereo[:, 0] - stereo[:, 1]).max() > 1e-3


# ── Impulse responses (caching + determinism) ──────────────────────────

def test_ir_length_matches_preset_duration():
    for name, dur in _IR_DURATIONS.items():
        ir = _generate_ir(name)
        assert abs(len(ir) / SAMPLE_RATE - dur) < 0.01


def test_ir_generation_is_cached_and_deterministic():
    _GENERATED_IR_CACHE.pop(("plate", SAMPLE_RATE, 42), None)
    first = _generate_ir("plate")
    second = _generate_ir("plate")
    assert second is first                      # served from cache, not rebuilt
    assert np.array_equal(_generate_ir("plate", seed=42), first)


def test_ir_different_seeds_produce_different_tails():
    a = _generate_ir("cathedral", seed=42)
    b = _generate_ir("cathedral", seed=4242)
    assert a.shape == b.shape
    assert not np.array_equal(a, b)


def test_ir_decays_over_time():
    ir = _generate_ir("cave")
    assert _rms(ir[-len(ir) // 4:]) < _rms(ir[: len(ir) // 4])


# ── Panning ────────────────────────────────────────────────────────────

def test_hard_pan_routes_to_one_channel():
    mono = sine_wave(440.0, n_samples=4410).astype(np.float32)
    left = _pan_to_stereo(mono, -1.0)
    right = _pan_to_stereo(mono, 1.0)
    assert _rms(left[:, 0]) > 0.5 and _rms(left[:, 1]) < 1e-6
    assert _rms(right[:, 1]) > 0.5 and _rms(right[:, 0]) < 1e-6


def test_center_pan_is_balanced():
    mono = sine_wave(440.0, n_samples=4410).astype(np.float32)
    center = _pan_to_stereo(mono, 0.0)
    assert _rms(center[:, 0]) == pytest.approx(_rms(center[:, 1]), rel=1e-3)


# ── Master bus ─────────────────────────────────────────────────────────

def test_master_compressor_tames_peaks_and_stays_finite():
    hot = np.random.uniform(-3.0, 3.0, SAMPLE_RATE).astype(np.float32)
    out = _master_compress(hot)
    assert np.all(np.isfinite(out))
    assert np.abs(out).max() <= 0.95          # limited below clipping


def test_soft_clip_is_transparent_below_the_knee():
    x = np.linspace(-0.7, 0.7, 101).astype(np.float32)   # all below knee=0.8
    assert np.allclose(_soft_clip(x, knee=0.8, ceiling=0.98), x)


def test_soft_clip_never_reaches_ceiling():
    x = np.linspace(-5.0, 5.0, 1001).astype(np.float32)
    out = _soft_clip(x, knee=0.8, ceiling=0.98)
    assert np.abs(out).max() <= 0.98          # asymptotes to, never exceeds
    assert np.all(np.isfinite(out))


def test_master_bus_preserves_stereo_image():
    # Regression guard: gain reduction must be stereo-linked. With R a fixed
    # fraction of L, the L/R balance must survive a loud, compression-
    # triggering burst — independent per-channel compression would shift it.
    n = SAMPLE_RATE
    t = np.arange(n) / SAMPLE_RATE
    left = (0.4 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    left[20000:30000] *= 4.0
    right = (0.5 * left).astype(np.float32)
    stereo = np.stack([left, right], axis=1)

    out = _master_bus(stereo.copy())
    src_ratio = np.abs(right).sum() / np.abs(left).sum()
    out_ratio = np.abs(out[:, 1]).sum() / np.abs(out[:, 0]).sum()
    assert out_ratio == pytest.approx(src_ratio, rel=1e-3)


def test_master_bus_soft_limits_and_stays_finite():
    hot = np.random.uniform(-2.0, 2.0, (SAMPLE_RATE, 2)).astype(np.float32)
    out = _master_bus(hot)
    assert out.shape == hot.shape
    assert np.all(np.isfinite(out))
    assert np.abs(out).max() < 0.98           # soft-limited, never clips
