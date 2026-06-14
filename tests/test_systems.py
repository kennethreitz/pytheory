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


def test_tone_system():
    c4 = Tone(name="C", octave=4, system="western")
    assert c4.system_name == "western"
    assert c4.system == pytheory.SYSTEMS["western"]


def test_western_system_has_12_tones():
    system = pytheory.SYSTEMS["western"]
    assert system.semitones == 12


def test_western_system_tones():
    system = pytheory.SYSTEMS["western"]
    tone_names = [t.name for t in system.tones]
    assert "A" in tone_names
    assert "C" in tone_names
    assert "G" in tone_names


def test_tone_index_in_system():
    t = Tone.from_string("A4", system="western")
    assert t._index == 0


def test_tone_index_without_system_raises():
    t = Tone(name="C", octave=4)
    t._system = None
    t.system_name = None
    with pytest.raises(ValueError, match="index"):
        _ = t._index


def test_tone_math_without_system_raises():
    t = Tone(name="C", octave=4)
    t._system = None
    t.system_name = None
    with pytest.raises(ValueError):
        t._math(1)


def test_pitch_without_system_raises():
    t = Tone(name="C", octave=4)
    t._system = None
    t.system_name = None
    with pytest.raises(ValueError, match="Pitches"):
        t.pitch()


def test_pitch_pythagorean_temperament():
    """Pythagorean A4 should still be 440 (it's the reference)."""
    t = Tone.from_string("A4", system="western")
    assert abs(t.pitch(temperament="pythagorean") - 440.0) < 0.01


def test_system_repr():
    system = SYSTEMS["western"]
    assert repr(system) == "<System semitones=12>"


def test_system_semitones():
    system = SYSTEMS["western"]
    assert system.semitones == 12


def test_system_tones_are_tone_objects():
    system = SYSTEMS["western"]
    for tone in system.tones:
        assert isinstance(tone, Tone)


def test_system_tones_have_alt_names():
    """Tones with enharmonic equivalents should have alt names."""
    system = SYSTEMS["western"]
    cs = [t for t in system.tones if t.name == "C#"]
    assert len(cs) == 1
    assert "Db" in cs[0].alt_names


def test_indian_system_exists():
    assert "indian" in SYSTEMS
    assert SYSTEMS["indian"].semitones == 12


def test_indian_system_tones():
    indian = SYSTEMS["indian"]
    names = [t.name for t in indian.tones]
    assert "Sa" in names
    assert "Pa" in names
    assert "Dha" in names
    assert len(names) == 12


def test_arabic_system_exists():
    assert "arabic" in SYSTEMS
    assert SYSTEMS["arabic"].semitones == 12


def test_japanese_system_exists():
    assert "japanese" in SYSTEMS
    assert SYSTEMS["japanese"].semitones == 12


def test_blues_system_exists():
    assert "blues" in SYSTEMS
    assert SYSTEMS["blues"].semitones == 12


def test_gamelan_system_exists():
    assert "gamelan" in SYSTEMS
    assert SYSTEMS["gamelan"].semitones == 12


def test_gamelan_tones():
    gamelan = SYSTEMS["gamelan"]
    names = [t.name for t in gamelan.tones]
    assert "ji" in names
    assert "ro" in names
    assert "mo" in names


def test_gamelan_slendro():
    ji = TonedScale(tonic="ji4", system=SYSTEMS["gamelan"])
    s = ji["slendro"]
    assert s.note_names == ["ji", "ro", "pat", "mo", "pi", "ji"]


def test_gamelan_pelog():
    ji = TonedScale(tonic="ji4", system=SYSTEMS["gamelan"])
    s = ji["pelog"]
    assert len(s) == 8  # 7 notes + octave


def test_gamelan_all_intervals_sum_to_12():
    gamelan = SYSTEMS["gamelan"]
    for scale_type in gamelan.scales:
        for name, scale in gamelan.scales[scale_type].items():
            total = sum(scale["intervals"])
            assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_system_resolve_name_sharp():
    assert SYSTEMS["western"].resolve_name("C#") == "C#"


def test_system_resolve_name_flat():
    assert SYSTEMS["western"].resolve_name("Db") == "C#"


def test_system_resolve_name_natural():
    assert SYSTEMS["western"].resolve_name("C") == "C"


def test_system_resolve_name_unknown():
    assert SYSTEMS["western"].resolve_name("X") is None


def test_cli_tone_pythagorean(capsys):
    from pytheory.cli import cmd_tone
    import argparse
    args = argparse.Namespace(note="C5", temperament="pythagorean")
    cmd_tone(args)
    out = capsys.readouterr().out
    assert "Equal temp" in out
    assert "cents" in out


def test_tet_factory_creates_system():
    edo17 = TET(17)
    assert len(edo17.tone_names) == 17
    assert edo17.semitones == 17


def test_tet_factory_numbered_tones():
    edo17 = TET(17)
    t = Tone("0", octave=4, system=edo17)
    assert t.frequency == pytest.approx(440.0, rel=1e-3)
    # One octave up
    t_up = t.add(17)
    assert t_up.frequency == pytest.approx(880.0, rel=1e-3)


def test_tet_factory_custom_names():
    names = ["A", "B", "C", "D", "E"]
    edo5 = TET(5, names=names)
    assert len(edo5.tone_names) == 5
    t = Tone("A", octave=4, system=edo5)
    assert t.frequency == pytest.approx(440.0, rel=1e-3)


def test_tet_factory_wrong_name_count():
    with pytest.raises(ValueError):
        TET(5, names=["A", "B", "C"])


def test_19tet_system():
    sys19 = SYSTEMS["19-tet"]
    assert sys19.semitones == 19
    a = Tone("A", octave=4, system=sys19)
    assert a.frequency == pytest.approx(440.0, rel=1e-3)
    # Octave should double
    a5 = a.add(19)
    assert a5.frequency == pytest.approx(880.0, rel=1e-3)


def test_31tet_system():
    sys31 = SYSTEMS["31-tet"]
    assert sys31.semitones == 31
    a = Tone("A", octave=4, system=sys31)
    assert a.frequency == pytest.approx(440.0, rel=1e-3)


def test_shruti_system():
    shruti = SYSTEMS["shruti"]
    assert shruti.semitones == 22
    sa = Tone("Sa", octave=4, system=shruti)
    # Sa should be near C4 (261.63 Hz) — not exact due to 22-TET
    assert 250 < sa.frequency < 270


def test_shruti_octave():
    shruti = SYSTEMS["shruti"]
    sa4 = Tone("Sa", octave=4, system=shruti)
    sa5 = sa4.add(22)
    assert sa5.frequency == pytest.approx(sa4.frequency * 2, rel=1e-3)


def test_slendro_system():
    slendro = SYSTEMS["slendro"]
    assert slendro.semitones == 5
    ji = Tone("ji", octave=4, system=slendro)
    # 5 steps = octave
    ji_up = ji.add(5)
    assert ji_up.frequency == pytest.approx(ji.frequency * 2, rel=1e-3)


def test_pelog_system():
    pelog = SYSTEMS["pelog"]
    assert pelog.semitones == 9
    ts = TonedScale(system=pelog, tonic=Tone("ji", octave=4, system=pelog))
    full_pelog = ts["pelog"]
    assert len(full_pelog.tones) == 8


def test_thai_system():
    thai = SYSTEMS["thai"]
    assert thai.semitones == 7
    do = Tone("do", octave=4, system=thai)
    # 7 steps = octave
    do_up = do.add(7)
    assert do_up.frequency == pytest.approx(do.frequency * 2, rel=1e-3)


def test_turkish_makam_system():
    makam = SYSTEMS["makam"]
    assert makam.semitones == 53
    ts = TonedScale(system=makam, tonic=Tone("Do", octave=4, system=makam))
    rast = ts["rast"]
    assert len(rast.tones) == 8


def test_carnatic_system():
    carnatic = SYSTEMS["carnatic"]
    assert carnatic.semitones == 72
    ts = TonedScale(system=carnatic, tonic=Tone("Sa", octave=4, system=carnatic))
    shankarabharanam = ts["shankarabharanam"]
    assert len(shankarabharanam.tones) == 8


def test_circle_of_fifths_19tet():
    sys19 = SYSTEMS["19-tet"]
    c = Tone("C", octave=4, system=sys19)
    cof = c.circle_of_fifths()
    assert len(cof) == 19  # should cycle through all 19 tones


def test_score_system_param():
    """Score passes system to parts for string→Tone resolution."""
    from pytheory import Score, Duration
    shruti = SYSTEMS["shruti"]
    score = Score("4/4", bpm=120, system=shruti)
    p = score.part("test", synth="sine")
    assert p._system is shruti
    # String "Sa" should resolve via shruti system, not western
    p.add(Tone("Sa", octave=4, system=shruti), Duration.QUARTER)
    assert len(p.notes) == 1


def test_system_tone_method():
    from pytheory import TET
    edo = TET(19)
    t = edo.tone(5, octave=4)
    assert t.name == "5"
    assert t.octave == 4


def test_score_temperament():
    from pytheory import Score
    score = Score("4/4", bpm=120, temperament="just")
    assert score.temperament == "just"


def test_score_system_propagates():
    from pytheory import Score, SYSTEMS
    shruti = SYSTEMS["shruti"]
    score = Score("4/4", bpm=120, system=shruti)
    p = score.part("t", synth="sine")
    assert p._system is shruti
