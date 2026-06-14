import pytest
import numpy

from pytheory import Chord

try:
    import sounddevice
    HAS_PORTAUDIO = True
except OSError:
    HAS_PORTAUDIO = False

needs_portaudio = pytest.mark.skipif(
    not HAS_PORTAUDIO, reason="PortAudio not available")


def _write_test_wav(buf, path):
    import wave as wavemod
    data = (numpy.clip(buf, -1, 1) * 32767).astype(numpy.int16)
    with wavemod.open(path, "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(data.tobytes())

def _roundtrip_melody(melody, synth="sine", bpm=120, **kw):
    import tempfile, os
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    s = Score(bpm=bpm)
    p = s.part("m", synth=synth, volume=0.7)
    for note, beats in melody:
        if note == "rest":
            p.rest(beats)
        else:
            p.add(note, beats)
    path = tempfile.mktemp(suffix=".wav")
    _write_test_wav(render_score(s), path)
    try:
        out = Score.from_wav(path, bpm=bpm, **kw)
    finally:
        os.unlink(path)
    return [str(n.tone) for n in out.parts["melody"].notes
            if n.tone is not None]

def _render_test_mix(tmp_path=None):
    """Four-track mix at 110 BPM with known bass/lead lines."""
    import tempfile
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    from pytheory import Chord
    s = Score(bpm=110)
    s.drums("rock", repeats=2)
    chords = s.part("chords", synth="rhodes", volume=0.5)
    bass = s.part("bass", synth="bass_guitar", volume=0.6)
    lead = s.part("lead", synth="saw", volume=0.5)
    for sym, b in [("Am", "A2"), ("F", "F2")]:
        chords.add(Chord.from_symbol(sym), 4)
        for _ in range(4):
            bass.add(b, 1)
    for n in ["A4", "C5", "B4", "G4", "A4", "F4", "E4", "C4"]:
        lead.add(n, 1)
    path = tempfile.mktemp(suffix=".wav")
    _write_test_wav(render_score(s), path)
    return path

def _chords_roundtrip(symbols, beats=4):
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    from pytheory import Chord
    from pytheory.audio import detect_chords
    s = Score(bpm=120)
    p = s.part("p", synth="rhodes", volume=0.6)
    for sym in symbols:
        p.add(Chord.from_symbol(sym), beats)
    buf = render_score(s).mean(axis=1).astype(numpy.float64)
    return [sym for _, _, sym in
            detect_chords(buf, 44100, bpm=120, beats_per_chord=beats)]

def _chord_buffer(symbol, synth="acoustic_guitar_synth", octave=4):
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    s = Score(bpm=120)
    p = s.part("p", synth=synth, volume=0.6)
    p.add(Chord.from_symbol(symbol, octave=octave), 2)
    return render_score(s).mean(axis=1).astype(numpy.float64)[:44100]

def _progression_score():
    from pytheory import Score, Key, Duration
    score = Score("4/4", bpm=120)
    chords = score.part("chords")
    for c in Key("C", "major").progression("I", "V", "vi", "IV"):
        chords.add(c, Duration.WHOLE)
    return score
