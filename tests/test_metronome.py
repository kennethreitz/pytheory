import sys
import types

import numpy
import pytest

from pytheory.metronome import Metronome
from pytheory.play import SAMPLE_RATE


class _FakeStream:
    """Stand-in for sounddevice.OutputStream — records bar lengths."""
    written = []

    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def write(self, buf):
        _FakeStream.written.append(len(buf))


@pytest.fixture
def fake_sd(monkeypatch):
    _FakeStream.written = []
    mod = types.ModuleType("sounddevice")
    mod.OutputStream = _FakeStream
    monkeypatch.setitem(sys.modules, "sounddevice", mod)
    return _FakeStream


def test_bar_length_matches_tempo():
    bar = Metronome(bpm=120, beats=4)._bar(None)
    assert len(bar) == int(SAMPLE_RATE * 60 / 120) * 4


def test_downbeat_is_accented():
    m = Metronome(bpm=120, beats=4)
    bar = m._bar(None)
    beat_len = int(SAMPLE_RATE * 0.5)
    downbeat = float(numpy.max(numpy.abs(bar[:1000])))
    beat_two = float(numpy.max(numpy.abs(bar[beat_len:beat_len + 1000])))
    assert downbeat > beat_two


def test_no_accent_makes_beats_even():
    m = Metronome(bpm=120, beats=4, accent=False)
    bar = m._bar(None)
    beat_len = int(SAMPLE_RATE * 0.5)
    downbeat = float(numpy.max(numpy.abs(bar[:1000])))
    beat_two = float(numpy.max(numpy.abs(bar[beat_len:beat_len + 1000])))
    assert downbeat == pytest.approx(beat_two)


def test_subdivision_adds_inner_clicks():
    plain = Metronome(bpm=120, beats=1, subdivide=1)._bar(None)
    eighths = Metronome(bpm=120, beats=1, subdivide=2)._bar(None)
    # Same length, but the subdivided bar has a click at the halfway point.
    assert len(plain) == len(eighths)
    mid = len(eighths) // 2
    assert numpy.any(eighths[mid:mid + 500])
    assert not numpy.any(plain[mid:mid + 500])


def test_chord_stab_mixes_in():
    m = Metronome(bpm=120, beats=2, progression=["Am"])
    bar = m._bar("Am")
    # The chord sustains into the gaps between clicks.
    assert numpy.any(bar[20000:30000])


def test_bar_never_clips():
    bar = Metronome(bpm=100, beats=4, progression=["Cmaj7"])._bar("Cmaj7")
    assert float(numpy.max(numpy.abs(bar))) <= 0.95 + 1e-6


def test_invalid_args():
    with pytest.raises(ValueError):
        Metronome(bpm=0)
    with pytest.raises(ValueError):
        Metronome(bpm=120, beats=0)
    with pytest.raises(ValueError):
        Metronome(bpm=120, subdivide=0)
    with pytest.raises(ValueError, match="end_bpm must be positive"):
        Metronome(bpm=120, end_bpm=0)
    with pytest.raises(ValueError, match="step must be positive"):
        Metronome(bpm=120, end_bpm=140, step=0)


def test_tempo_trainer_ramps_up_and_stops(fake_sd):
    seen = []
    m = Metronome(bpm=80, beats=4, end_bpm=100, step=5, every=8, hold=False)
    m.start(on_bar=lambda i, bpm, sym: seen.append(bpm))
    assert seen[0] == 80
    assert seen[-1] == 100          # a bar sounds at the target
    assert m.bpm == 100
    assert seen == sorted(seen)     # monotonic non-decreasing ramp


def test_tempo_trainer_ramps_down(fake_sd):
    seen = []
    m = Metronome(bpm=120, beats=4, end_bpm=100, step=10, every=4, hold=False)
    m.start(on_bar=lambda i, bpm, sym: seen.append(bpm))
    assert seen[0] == 120
    assert seen[-1] == 100
    assert seen == sorted(seen, reverse=True)


def test_progression_cycles_per_bar(fake_sd):
    syms = []
    # Ramp long enough to sound at least four bars (one per chord).
    m = Metronome(bpm=200, beats=4, progression=["Am", "F", "C", "G"],
                  end_bpm=240, step=10, every=4, hold=False)
    m.start(on_bar=lambda i, bpm, sym: syms.append(sym))
    assert syms[:4] == ["Am", "F", "C", "G"]


def test_cli_metronome_dispatch(fake_sd, monkeypatch):
    """`pytheory metronome` wires through to a real ramp."""
    from pytheory import cli
    monkeypatch.setattr(sys, "argv",
                        ["pytheory", "metronome", "90", "--to", "100",
                         "--step", "5", "--every", "4", "--no-hold"])
    cli.main()
    assert _FakeStream.written  # bars were streamed
