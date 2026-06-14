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


def test_from_wav_roundtrips_melody():
    names = _roundtrip_melody([("C4", 1), ("E4", 1), ("G4", 1), ("C5", 1)])
    assert names == ["C4", "E4", "G4", "C5"]


def test_from_wav_splits_repeated_notes():
    names = _roundtrip_melody([("G4", 0.5), ("G4", 0.5), ("G4", 1)])
    assert names == ["G4", "G4", "G4"]


def test_from_wav_handles_inharmonic_piano_timbre():
    names = _roundtrip_melody([("C4", 1), ("F4", 1), ("A4", 1)],
                              synth="piano_synth")
    assert names == ["C4", "F4", "A4"]


def test_from_wav_bass_register():
    names = _roundtrip_melody([("E2", 1), ("G2", 1), ("A2", 2)],
                              synth="bass_guitar", fmin=40, fmax=400)
    assert names == ["E2", "G2", "A2"]


def test_from_wav_quantize_snaps_durations():
    import tempfile, os
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    s = Score(bpm=120)
    p = s.part("m", synth="sine", volume=0.7)
    p.add("C4", 1.04)
    p.add("D4", 0.49)
    path = tempfile.mktemp(suffix=".wav")
    _write_test_wav(render_score(s), path)
    try:
        out = Score.from_wav(path, quantize=0.25)
    finally:
        os.unlink(path)
    beats = [n.beats for n in out.parts["melody"].notes if n.tone is not None]
    assert beats == [1.0, 0.5]


def test_detect_pitch_pure_tone():
    from pytheory.audio import detect_pitch
    t = numpy.arange(44100) / 44100
    sig = numpy.sin(2 * numpy.pi * 440 * t)
    times, freqs, voiced = detect_pitch(sig, 44100)
    assert voiced.sum() > 50
    assert abs(freqs[voiced].mean() - 440) < 1.0


def test_detect_pitch_silence_is_unvoiced():
    from pytheory.audio import detect_pitch
    sig = numpy.zeros(44100)
    times, freqs, voiced = detect_pitch(sig, 44100)
    assert not voiced.any()


def test_from_wav_split_recovers_bass_and_melody():
    import os
    from pytheory.rhythm import Score
    path = _render_test_mix()
    try:
        score = Score.from_wav(path, bpm=110, split=True, quantize=0.5)
    finally:
        os.unlink(path)
    assert set(score.parts) >= {"melody", "bass"}
    # Bass: pitch classes must walk A → F in order
    bass_pcs = [str(n.tone)[:-1].rstrip("#b")
                for n in score.parts["bass"].notes if n.tone is not None]
    deduped = [pc for i, pc in enumerate(bass_pcs)
               if i == 0 or pc != bass_pcs[i - 1]]
    a_idx = deduped.index("A") if "A" in deduped else -1
    f_idx = deduped.index("F") if "F" in deduped else -1
    assert a_idx != -1 and f_idx != -1 and a_idx < f_idx
    # Melody: most detected notes belong to the true lead line
    truth = {"A4", "C5", "B4", "G4", "F4", "E4", "C4"}
    mel = [str(n.tone) for n in score.parts["melody"].notes
           if n.tone is not None]
    assert len(mel) >= 6
    hits = sum(1 for n in mel if n in truth)
    assert hits / len(mel) > 0.6


def test_from_wav_auto_bpm_sets_score_tempo():
    import os
    from pytheory.rhythm import Score
    path = _render_test_mix()
    try:
        score = Score.from_wav(path)     # no bpm — estimate
    finally:
        os.unlink(path)
    assert 55 <= score.bpm <= 224


def test_tuner_analyze_frame_in_tune():
    import json
    from pytheory.tuner import analyze_frame
    t = numpy.arange(4096) / 44100
    r = analyze_frame(numpy.sin(2 * numpy.pi * 440 * t), 44100)
    assert r["note"] == "A" and r["octave"] == 4
    assert abs(r["cents"]) < 2
    assert r["in_tune"] is True
    json.dumps(r)  # must be JSON-serializable for the SSE stream


def test_tuner_analyze_frame_sharp():
    from pytheory.tuner import analyze_frame
    t = numpy.arange(4096) / 44100
    # 440 * 2^(25/1200) ≈ 446.40 Hz — 25 cents sharp of A4
    r = analyze_frame(numpy.sin(2 * numpy.pi * 446.40 * t), 44100)
    assert r["note"] == "A"
    assert 20 < r["cents"] < 30
    assert r["in_tune"] is False


def test_tuner_reference_pitch():
    from pytheory.tuner import analyze_frame
    t = numpy.arange(4096) / 44100
    r = analyze_frame(numpy.sin(2 * numpy.pi * 442 * t), 44100,
                      reference_pitch=442)
    assert r["note"] == "A" and abs(r["cents"]) < 2


def test_tuner_noise_returns_none():
    from pytheory.tuner import analyze_frame
    noise = numpy.random.default_rng(0).uniform(-1, 1, 4096)
    assert analyze_frame(noise, 44100) is None


def test_detect_chords_on_rendered_progression():
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    from pytheory import Chord
    from pytheory.audio import detect_chords
    s = Score(bpm=120)
    p = s.part("p", synth="rhodes", volume=0.6)
    for sym in ["Am", "F", "C", "G"]:
        p.add(Chord.from_symbol(sym), 4)
    buf = render_score(s).mean(axis=1).astype(numpy.float64)
    track = detect_chords(buf, 44100, bpm=120, beats_per_chord=4)
    symbols = [sym for _, _, sym in track]
    assert symbols == ["Am", "F", "C", "G"]


def test_from_wav_split_full_arrangement():
    import os
    from pytheory.rhythm import Score
    path = _render_test_mix()   # Am, F over rock drums at 110
    try:
        score = Score.from_wav(path, bpm=110, split=True, quantize=0.5)
    finally:
        os.unlink(path)
    assert set(score.parts) >= {"melody", "bass", "chords", "drums"}
    chord_syms = [str(n.tone) for n in score.parts["chords"].notes
                  if n.tone is not None]
    assert any("A minor" in c for c in chord_syms)
    assert any("F major" in c for c in chord_syms)
    drum_sounds = {h.sound.name for h in score._drum_hits}
    assert "CLOSED_HAT" in drum_sounds
    assert "SNARE" in drum_sounds or "KICK" in drum_sounds
    assert score.detected_key is not None


def test_detect_chords_sevenths():
    assert _chords_roundtrip(["Dm7", "G7", "Cmaj7"]) == ["Dm7", "G7", "Cmaj7"]


def test_detect_chords_triads_not_promoted_to_sevenths():
    assert _chords_roundtrip(["Am", "F", "C", "G"]) == ["Am", "F", "C", "G"]


def test_detect_chords_sus():
    assert _chords_roundtrip(["Csus4", "Am", "G"]) == ["Csus4", "Am", "G"]


def test_detect_chords_inversion_slash():
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    from pytheory import Chord
    from pytheory.audio import detect_chords
    s = Score(bpm=120)
    p = s.part("p", synth="rhodes", volume=0.6)
    b = s.part("b", synth="sine", volume=0.6)
    for sym, bass in [("C", "C2"), ("C", "E2"), ("G", "G2")]:
        p.add(Chord.from_symbol(sym, octave=4), 4)
        b.add(bass, 4)
    buf = render_score(s).mean(axis=1).astype(numpy.float64)
    track = detect_chords(buf, 44100, bpm=120, beats_per_chord=4)
    symbols = [sym for _, _, sym in track]
    assert symbols == ["C", "C/E", "G"]


def test_detect_chords_beat_aligned_lead_in():
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    from pytheory import Chord
    from pytheory.audio import detect_chords
    s = Score(bpm=120)
    p = s.part("p", synth="rhodes", volume=0.6)
    for sym in ["Am", "F", "C", "G"]:
        p.add(Chord.from_symbol(sym), 4)
    buf = render_score(s).mean(axis=1).astype(numpy.float64)
    # Half a beat of near-silence up front — the grid must realign
    lead = numpy.zeros(int(44100 * 0.25))
    track = detect_chords(numpy.concatenate([lead, buf]), 44100,
                          bpm=120, beats_per_chord=4)
    symbols = [sym for _, _, sym in track]
    assert symbols == ["Am", "F", "C", "G"]
    assert 0.25 <= track[0][0] <= 0.75   # starts near the real downbeat


def test_detect_chords_short_and_silent_input():
    from pytheory.audio import detect_chords
    assert detect_chords(numpy.zeros(100), 44100) == []
    assert detect_chords(numpy.zeros(44100), 44100) == []


def test_tuner_string_targets():
    from pytheory.tuner import string_targets
    targets = string_targets("guitar")
    assert [n for n, _ in targets] == ["E2", "A2", "D3", "G3", "B3", "E4"]
    assert abs(targets[0][1] - 82.41) < 0.01
    # Reference pitch shifts every string
    high = string_targets("guitar", reference_pitch=442.0)
    assert high[0][1] > targets[0][1]


def test_tuner_analyze_frame_locks_to_string():
    import json
    from pytheory.tuner import analyze_frame, string_targets
    t = numpy.arange(8192) / 44100
    # 145 Hz — 22 cents flat of the guitar D string (146.83 Hz)
    r = analyze_frame(numpy.sin(2 * numpy.pi * 145 * t), 44100,
                      targets=string_targets("guitar"))
    assert r["target"] == "D3"
    assert -30 < r["cents"] < -15
    assert r["in_tune"] is False
    json.dumps(r)


def test_tuner_instrument_widens_range():
    from pytheory.tuner import Tuner
    t = Tuner(instrument="bass")
    assert t.fmin < 41.3   # must reach the low E1 string
    assert t.targets[0][0] == "E1"


def test_tuner_unknown_instrument():
    from pytheory.tuner import Tuner
    with pytest.raises(ValueError):
        Tuner(instrument="kazoo")


def test_tuner_ws_frame_encoding():
    from pytheory.tuner import _ws_frame
    small = _ws_frame(b"x" * 10)
    assert small[0] == 0x81 and small[1] == 10
    medium = _ws_frame(b"x" * 200)
    assert medium[1] == 126
    assert int.from_bytes(medium[2:4], "big") == 200


def test_tuner_serve_page_stream_and_websocket():
    import base64
    import hashlib
    import json
    import socket
    import threading
    import time
    import types
    import urllib.request
    from pytheory import tuner as tuner_mod

    fake = types.SimpleNamespace(
        instrument="guitar",
        targets=tuner_mod.string_targets("guitar"),
        reference_pitch=440.0,
        reading={"freq": 82.4, "note": "E", "octave": 2, "cents": -3.0,
                 "in_tune": True, "target": "E2", "target_freq": 82.41})
    port = 8342
    th = threading.Thread(target=tuner_mod.serve, args=(fake,),
                          kwargs={"port": port, "open_browser": False},
                          daemon=True)
    th.start()
    time.sleep(0.6)

    page = urllib.request.urlopen(
        f"http://localhost:{port}/", timeout=10).read().decode()
    assert "strobe" in page
    assert '"strings": ["E2", "A2", "D3", "G3", "B3", "E4"]' in page

    stream = urllib.request.urlopen(
        f"http://localhost:{port}/stream", timeout=10)
    line = stream.readline().decode()
    stream.close()
    assert line.startswith("data: ") and '"target": "E2"' in line

    # WebSocket handshake (RFC 6455 sample key) + one frame
    ws_key = "dGhlIHNhbXBsZSBub25jZQ=="
    expect = base64.b64encode(hashlib.sha1(
        (ws_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
    ).digest()).decode()
    s = socket.create_connection(("localhost", port), timeout=10)
    s.sendall((f"GET /ws HTTP/1.1\r\nHost: localhost\r\n"
               f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {ws_key}\r\n"
               f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += s.recv(4096)
    head, _, rest = buf.partition(b"\r\n\r\n")
    assert b"101" in head.splitlines()[0]
    assert f"Sec-WebSocket-Accept: {expect}".encode() in head
    buf = rest
    while len(buf) < 4:
        buf += s.recv(4096)
    assert buf[0] == 0x81
    if buf[1] == 126:
        need, off = int.from_bytes(buf[2:4], "big"), 4
    else:
        need, off = buf[1], 2
    while len(buf) < off + need:
        buf += s.recv(4096)
    reading = json.loads(buf[off:off + need].decode())
    assert reading["target"] == "E2"
    s.close()


def test_from_wav_detected_key_am_f_g():
    """An Am-F-G progression is C major / A minor territory —
    regression for the name-matching bug that returned A# major."""
    import os
    import tempfile
    import wave as wavemod
    from pytheory.rhythm import Score
    from pytheory.play import render_score

    s = Score(bpm=120)
    p = s.part("p", synth="rhodes", volume=0.6)
    for sym in ["Am", "F", "G"]:
        p.add(Chord.from_symbol(sym), 4)
    data = (numpy.clip(render_score(s), -1, 1) * 32767).astype(numpy.int16)
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        with wavemod.open(path, "wb") as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(44100)
            f.writeframes(data.tobytes())
        score = Score.from_wav(path, split=True, quantize=0.5)
    finally:
        os.unlink(path)
    assert str(score.detected_key) in ("C major", "A minor")


def test_identify_chord_triads_and_sevenths():
    from pytheory.audio import identify_chord
    for sym in ["Am", "C", "E", "Bm", "F#m", "Esus4"]:
        r = identify_chord(_chord_buffer(sym), 44100)
        assert r is not None and r["symbol"] == sym, (sym, r)
        assert r["confidence"] > 0.7
    r = identify_chord(_chord_buffer("Dm7", synth="rhodes"), 44100)
    assert r["symbol"] == "Dm7"
    assert r["notes"] == ["D", "F", "A", "C"]


def test_identify_chord_rejects_single_notes():
    from pytheory.audio import identify_chord
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    for note, synth in [("A4", "piano_synth"), ("C3", "saw"),
                        ("A3", "rhodes")]:
        s = Score(bpm=120)
        p = s.part("p", synth=synth, volume=0.6)
        p.add(note, 2)
        buf = render_score(s).mean(axis=1).astype(numpy.float64)[:44100]
        assert identify_chord(buf, 44100) is None, (note, synth)


def test_identify_chord_rejects_silence_and_noise():
    from pytheory.audio import identify_chord
    assert identify_chord(numpy.zeros(44100), 44100) is None
    noise = numpy.random.default_rng(0).normal(0, 0.1, 44100)
    assert identify_chord(noise, 44100) is None
    assert identify_chord(numpy.zeros(100), 44100) is None


def test_tuner_chord_mode_buffer_and_state():
    from pytheory.tuner import Tuner
    t = Tuner(chords=True)
    assert t.chords is True
    assert t._buf_len == 44100   # 1s buffer for the chromagram
    assert t.chord is None
    plain = Tuner()
    assert plain._buf_len == 4096


def test_tuner_serve_chord_payload():
    import json
    import threading
    import time
    import types
    import urllib.request
    from pytheory import tuner as tuner_mod

    fake = types.SimpleNamespace(
        instrument=None, targets=None, reference_pitch=440.0, chords=True,
        reading={"freq": 220.0, "note": "A", "octave": 3,
                 "cents": 1.0, "in_tune": True},
        chord={"symbol": "Am", "confidence": 0.91,
               "notes": ["A", "C", "E"]})
    port = 8343
    th = threading.Thread(target=tuner_mod.serve, args=(fake,),
                          kwargs={"port": port, "open_browser": False},
                          daemon=True)
    th.start()
    time.sleep(0.6)

    page = urllib.request.urlopen(
        f"http://localhost:{port}/", timeout=10).read().decode()
    assert "chordsym" in page and '"chords": true' in page

    stream = urllib.request.urlopen(
        f"http://localhost:{port}/stream", timeout=10)
    d = json.loads(stream.readline().decode()[6:])
    stream.close()
    assert d["chord"] == "Am"
    assert d["chord_notes"] == ["A", "C", "E"]
    assert d["note"] == "A"
