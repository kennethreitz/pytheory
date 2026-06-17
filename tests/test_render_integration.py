"""End-to-end integration assertions for the render pipeline.

Where test_dsp_quality.py checks individual DSP blocks, these render whole
Scores and assert that the *mix* behaves: pan placement, volume balance,
sidechain ducking, onset timing through effects, and that inert parts are
no-ops. This is the layer that catches a regression in how parts are
summed, panned, and mastered — not just in a single filter.

Pure numpy; no audio device needed.
"""
import numpy as np
import pytest

from pytheory import Score, Duration
from pytheory.play import render_score, _apply_sidechain


def _rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)))


def _band_energy(buf, lo, hi, sample_rate=44100):
    mono = buf.mean(axis=1).astype(np.float64)
    spec = np.abs(np.fft.rfft(mono)) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1.0 / sample_rate)
    return float(spec[(freqs >= lo) & (freqs < hi)].sum())


def _four_notes(part, pitch="C4"):
    for _ in range(4):
        part.add(pitch, Duration.QUARTER)


# ── Panning ────────────────────────────────────────────────────────────

def test_hard_pan_places_energy_on_one_side():
    left = Score("4/4", bpm=120)
    _four_notes(left.part("x", synth="saw", pan=-1.0))
    lbuf = render_score(left)
    assert _rms(lbuf[:, 0]) > 0.1 and _rms(lbuf[:, 1]) < 1e-4

    right = Score("4/4", bpm=120)
    _four_notes(right.part("x", synth="saw", pan=1.0))
    rbuf = render_score(right)
    assert _rms(rbuf[:, 1]) > 0.1 and _rms(rbuf[:, 0]) < 1e-4


def test_center_pan_is_balanced_in_the_mix():
    s = Score("4/4", bpm=120)
    _four_notes(s.part("x", synth="saw", pan=0.0))
    buf = render_score(s)
    assert _rms(buf[:, 0]) == pytest.approx(_rms(buf[:, 1]), rel=1e-3)


# ── Level balance ──────────────────────────────────────────────────────

def test_louder_part_dominates_the_mix():
    # Two parts at well-separated pitches; the one with higher volume should
    # contribute far more spectral energy in its own band.
    s = Score("4/4", bpm=120)
    loud = s.part("loud", synth="sine", volume=0.9)
    quiet = s.part("quiet", synth="sine", volume=0.1)
    for _ in range(4):
        loud.add("C4", Duration.QUARTER)     # ~261 Hz
        quiet.add("C6", Duration.QUARTER)    # ~1046 Hz
    buf = render_score(s)
    assert _band_energy(buf, 230, 300) > 5 * _band_energy(buf, 1000, 1100)


# ── Sidechain ──────────────────────────────────────────────────────────

def test_sidechain_ducks_under_the_trigger():
    tone = np.full(44100, 0.5, dtype=np.float32)
    trigger = np.zeros(44100, dtype=np.float32)
    trigger[1000:1500] = 1.0                 # a "kick" near the start
    ducked = _apply_sidechain(tone, trigger, amount=0.8)
    assert ducked[500] == pytest.approx(0.5, abs=0.02)   # before the kick
    assert ducked[2000] < 0.25                            # ducked right after
    assert ducked[40000] == pytest.approx(0.5, abs=0.02)  # recovered later


# ── Latency (the bus stays time-aligned) ───────────────────────────────

def test_effects_preserve_onset_timing():
    # Routing a part through reverb must not push its onset late relative to
    # a dry part — the mix bus is effectively zero-latency.
    def onset(reverb):
        s = Score("4/4", bpm=120)
        kw = dict(reverb=0.6, reverb_type="hall") if reverb else {}
        part = s.part("x", synth="sine", envelope="pluck", **kw)
        part.rest(Duration.QUARTER)
        part.add("C5", Duration.QUARTER)
        buf = render_score(s)
        return int(np.argmax(np.abs(buf[:, 0]) > 0.05))

    dry, wet = onset(False), onset(True)
    assert abs(dry - wet) < 50              # < ~1 ms; no meaningful delay


# ── Inert parts are no-ops ─────────────────────────────────────────────

def test_part_with_no_notes_does_not_change_the_mix():
    def render(add_ghost):
        s = Score("4/4", bpm=120)
        _four_notes(s.part("a", synth="sine"))
        if add_ghost:
            s.part("ghost", synth="saw")     # created but never played
        return render_score(s)

    assert np.array_equal(render(False), render(True))


# ── Arrangement length ─────────────────────────────────────────────────

def test_render_length_tracks_content():
    short = Score("4/4", bpm=120)
    _four_notes(short.part("a", synth="sine"))      # 4 beats
    longer = Score("4/4", bpm=120)
    a = longer.part("a", synth="sine")
    for _ in range(8):
        a.add("C4", Duration.QUARTER)               # 8 beats
    assert len(render_score(longer)) > len(render_score(short))
