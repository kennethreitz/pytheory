import pytest
import numpy

import pytheory
from pytheory import Tone, TonedScale, Fretboard, Chord, Key, Note, TET
from pytheory.charts import CHARTS, NamedChord, charts_for_fretboard, QUALITIES
from pytheory.systems import System, SYSTEMS
from pytheory.rhythm import Duration, TimeSignature, Note as RhythmNote, Rest, Score

from _util import (HAS_PORTAUDIO, needs_portaudio, _write_test_wav,
                   _roundtrip_melody, _render_test_mix, _chords_roundtrip,
                   _chord_buffer, _progression_score)


def test_live_percussive_instrument_stays_one_shot():
    from pytheory.live import _Channel
    sr = 44100
    ch = _Channel(synth_name="piano", envelope_name="piano", volume=0.5)
    ch.note_on(60, 100)
    assert ch.voices[0].loop_end is None
    for _ in range(int(4.0 * sr / 512)):
        last = ch.render_stereo(512)
    assert len(ch.voices) == 0                    # decayed and cleaned up
    assert numpy.abs(last).max() == 0.0


def test_live_note_off_releases_looping_voice():
    from pytheory.live import _Channel
    ch = _Channel(synth_name="organ", envelope_name="organ")
    ch.note_on(60, 100)
    for _ in range(10):
        ch.render_stereo(512)
    ch.note_off(60)
    for _ in range(20):
        tail = ch.render_stereo(512)
    assert len(ch.voices) == 0
    assert numpy.abs(tail).max() == 0.0


def test_live_cc_does_not_clear_cache_for_bus_params():
    from pytheory.live import LiveEngine
    engine = LiveEngine()
    engine.channel(1, instrument="electric_piano")
    ch = engine.channels[1]
    ch._get_wave(60, 44100 * 3)
    assert len(ch._cache) == 1
    engine.cc(11, "lowpass", min_val=200, max_val=8000)
    engine._apply_cc(1, 11, 64)
    assert len(ch._cache) == 1     # no re-render needed
    assert ch.lowpass > 200
    engine.cc(12, "detune", min_val=0, max_val=20)
    engine._apply_cc(1, 12, 64)
    assert len(ch._cache) == 0     # baked param → cache cleared


def test_live_engine_link_sync():
    pytest.importorskip("link")
    import time
    from pytheory.live import LiveEngine

    e = LiveEngine()
    e.channel(1, instrument="electric_piano")
    e.drums("rock", volume=0.5)
    e.enable_link(quantum=4)
    try:
        state = e._link.captureSessionState()
        now = e._link.clock().micros()
        state.setIsPlaying(True, now)
        state.setTempo(140, now)
        e._link.commitSessionState(state)
        time.sleep(0.05)

        hits = []
        e._drum_channel.note_on = lambda n, v: hits.append(n)
        for _ in range(120):
            e._on_link_audio(512)
            time.sleep(0.005)
        assert abs(e._bpm - 140) < 0.5   # tempo followed the session
        assert hits                       # drums fired on the Link grid
    finally:
        e.stop()
    assert e._link is None


def test_live_engine_link_stopped_transport_is_silent():
    pytest.importorskip("link")
    import time
    from pytheory.live import LiveEngine

    e = LiveEngine()
    e.channel(1, instrument="electric_piano")
    e.drums("rock", volume=0.5)
    e.enable_link(quantum=4)
    try:
        state = e._link.captureSessionState()
        state.setIsPlaying(False, e._link.clock().micros())
        e._link.commitSessionState(state)
        time.sleep(0.05)
        hits = []
        e._drum_channel.note_on = lambda n, v: hits.append(n)
        for _ in range(40):
            e._on_link_audio(512)
            time.sleep(0.002)
        assert hits == []
    finally:
        e.stop()
