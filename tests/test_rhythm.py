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


def test_fitness_partial():
    c = TonedScale(tonic="C4")["major"]
    assert c.fitness("C", "D", "F#", "G") == 0.75


def test_duration_values():
    assert Duration.WHOLE.value == 4.0
    assert Duration.HALF.value == 2.0
    assert Duration.QUARTER.value == 1.0
    assert Duration.EIGHTH.value == 0.5
    assert Duration.SIXTEENTH.value == 0.25
    assert Duration.DOTTED_HALF.value == 3.0
    assert Duration.DOTTED_QUARTER.value == 1.5
    assert abs(Duration.TRIPLET_QUARTER.value - 2 / 3) < 1e-9


def test_duration_arithmetic():
    # Multiplication
    assert Duration.WHOLE * 2 == 8.0
    assert 2 * Duration.HALF == 4.0
    assert Duration.QUARTER * 3 == 3.0
    # Division
    assert Duration.WHOLE / 2 == 2.0
    # Addition
    assert Duration.HALF + Duration.QUARTER == 3.0
    assert Duration.HALF + 1.0 == 3.0
    assert 1.0 + Duration.HALF == 3.0


def test_time_signature_from_string_4_4():
    ts = TimeSignature.from_string("4/4")
    assert ts.beats == 4
    assert ts.unit == 4
    assert ts.beats_per_measure == 4.0


def test_time_signature_from_string_3_4():
    ts = TimeSignature.from_string("3/4")
    assert ts.beats == 3
    assert ts.unit == 4
    assert ts.beats_per_measure == 3.0


def test_time_signature_from_string_6_8():
    ts = TimeSignature.from_string("6/8")
    assert ts.beats == 6
    assert ts.unit == 8
    assert ts.beats_per_measure == 3.0  # 6 * (4/8) = 3


def test_time_signature_repr():
    assert repr(TimeSignature(3, 4)) == "3/4"


def test_rest_creation():
    r = Rest(Duration.HALF)
    assert r.tone is None
    assert r.duration is Duration.HALF
    assert r.beats == 2.0


def test_rest_default_duration():
    r = Rest()
    assert r.duration is Duration.QUARTER


def test_score_add_chaining():
    t1 = Tone.from_string("C4")
    t2 = Tone.from_string("E4")
    score = Score("4/4", bpm=120)
    result = score.add(t1, Duration.QUARTER).add(t2, Duration.QUARTER)
    assert result is score
    assert len(score) == 2


def test_score_measures_complete():
    score = Score("4/4", bpm=120)
    for _ in range(4):
        score.add(Tone.from_string("C4"), Duration.QUARTER)
    assert score.measures == 1.0


def test_score_measures_fractional():
    score = Score("4/4", bpm=120)
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.QUARTER)
    assert score.measures == 0.5


def test_score_measures_3_4():
    score = Score("3/4", bpm=100)
    for _ in range(3):
        score.add(Tone.from_string("C4"), Duration.QUARTER)
    assert score.measures == 1.0


def test_score_duration_ms():
    score = Score("4/4", bpm=120)
    # At 120 bpm, one beat = 500 ms
    score.add(Tone.from_string("C4"), Duration.QUARTER)  # 1 beat = 500 ms
    score.add(Tone.from_string("E4"), Duration.HALF)      # 2 beats = 1000 ms
    assert score.duration_ms == 1500.0


def test_score_duration_ms_with_tempo_changes():
    score = Score("4/4", bpm=60)
    score.add(Tone.from_string("C4"), Duration.WHOLE)  # 4 beats = 4000 ms
    score.set_tempo(120)
    score.add(Tone.from_string("D4"), Duration.WHOLE)  # 4 beats = 2000 ms
    assert score.duration_ms == 6000.0


def test_score_iteration():
    score = Score("4/4", bpm=120)
    t = Tone.from_string("C4")
    score.add(t, Duration.QUARTER)
    score.rest(Duration.QUARTER)
    notes = list(score)
    assert len(notes) == 2
    assert notes[0].tone is t
    assert notes[1].tone is None


def test_score_repr():
    score = Score("4/4", bpm=120)
    for _ in range(4):
        score.add(Tone.from_string("C4"), Duration.QUARTER)
    r = repr(score)
    assert "4/4" in r
    assert "120bpm" in r
    assert "1.0 measures" in r


def test_score_with_rests():
    score = Score("4/4", bpm=60)
    score.add(Tone.from_string("C4"), Duration.QUARTER)
    score.rest(Duration.QUARTER)
    score.add(Tone.from_string("E4"), Duration.QUARTER)
    score.rest(Duration.QUARTER)
    assert score.total_beats == 4.0
    assert score.measures == 1.0
    # At 60 bpm, 1 beat = 1000 ms, 4 beats = 4000 ms
    assert score.duration_ms == 4000.0


def test_part_creation():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="saw", envelope="pluck")
    assert lead.name == "lead"
    assert lead.synth == "saw"
    assert lead.envelope == "pluck"
    assert "lead" in score.parts


def test_part_add_string():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.add("C5", Duration.QUARTER)
    assert len(lead) == 1
    assert lead.notes[0].tone.name == "C"
    assert lead.notes[0].tone.octave == 5


def test_part_add_chaining():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    result = lead.add("C5", Duration.QUARTER).add("E5", Duration.QUARTER).rest(Duration.HALF)
    assert result is lead
    assert len(lead) == 3
    assert lead.total_beats == 4.0


def test_multiple_parts():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="saw")
    bass = score.part("bass", synth="triangle")
    lead.add("C5", Duration.WHOLE)
    bass.add("C2", Duration.WHOLE).add("G2", Duration.WHOLE)
    assert len(score.parts) == 2
    assert score.total_beats == 8.0  # bass is longer


def test_part_repr():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="saw")
    lead.add("C5", Duration.QUARTER)
    r = repr(lead)
    assert "lead" in r
    assert "saw" in r


def test_score_repr_with_parts():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    score.part("lead")
    score.part("bass")
    r = repr(score)
    assert "2 parts" in r


def test_part_set_stores_automation():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.add("C5", Duration.WHOLE)
    lead.set(lowpass=2000)
    lead.add("E5", Duration.WHOLE)
    assert len(lead._automation) == 1
    assert lead._automation[0][0] == 4.0


def test_part_set_chaining():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    result = lead.set(lowpass=1000, reverb=0.3)
    assert result is lead


def test_part_get_params_at():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", lowpass=500)
    lead.add("C5", Duration.WHOLE)
    lead.set(lowpass=2000, reverb=0.4)
    lead.add("E5", Duration.WHOLE)
    p0 = lead._get_params_at(0)
    assert p0["lowpass"] == 500
    assert p0["reverb_mix"] == 0
    p4 = lead._get_params_at(4.0)
    assert p4["lowpass"] == 2000
    assert p4["reverb_mix"] == 0.4


@needs_portaudio
def test_automation_changes_output():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    s1 = Score("4/4", bpm=120)
    s1.part("lead", synth="saw", lowpass=500).add("C5", Duration.WHOLE).add("C5", Duration.WHOLE)
    buf1 = render_score(s1)
    s2 = Score("4/4", bpm=120)
    p2 = s2.part("lead", synth="saw", lowpass=500)
    p2.add("C5", Duration.WHOLE)
    p2.set(lowpass=5000)
    p2.add("C5", Duration.WHOLE)
    buf2 = render_score(s2)
    assert not numpy.allclose(buf1, buf2, atol=0.01)


def test_part_set_multiple():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", lowpass=400)
    lead.add("C5", Duration.WHOLE)
    lead.set(lowpass=1000)
    lead.add("C5", Duration.WHOLE)
    lead.set(lowpass=3000, distortion=0.5)
    lead.add("C5", Duration.WHOLE)
    assert len(lead._automation) == 2
    p8 = lead._get_params_at(8.0)
    assert p8["lowpass"] == 3000
    assert p8["distortion_mix"] == 0.5


def test_lfo_generates_automation():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.lfo("lowpass", rate=1.0, min=400, max=2000, bars=2)
    # 2 bars * 4 beats / 0.25 resolution = 32 points
    assert len(lead._automation) == 32


def test_lfo_sine_shape():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", lowpass=500)
    lead.lfo("lowpass", rate=1.0, min=200, max=1000, bars=1, shape="sine")
    # Check values stay in range
    for beat, params in lead._automation:
        assert 200 <= params["lowpass"] <= 1000


def test_lfo_all_shapes():
    from pytheory import Score
    for shape in ["sine", "triangle", "saw", "square"]:
        score = Score("4/4", bpm=120)
        lead = score.part(f"lead_{shape}")
        lead.lfo("lowpass", rate=1.0, min=100, max=5000, bars=1, shape=shape)
        assert len(lead._automation) > 0


def test_lfo_chaining():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    result = lead.lfo("lowpass", rate=1.0, min=400, max=2000, bars=1)
    assert result is lead


def test_lfo_multiple_params():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.lfo("lowpass", rate=1.0, min=400, max=2000, bars=2)
    lead.lfo("distortion", rate=0.5, min=0.0, max=0.8, bars=2)
    # Both sets of automation points should exist
    lp_points = [p for _, p in lead._automation if "lowpass" in p]
    dist_points = [p for _, p in lead._automation if "distortion_mix" in p]
    assert len(lp_points) > 0
    assert len(dist_points) > 0


def test_score_swing_default():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    assert score.swing == 0.0


def test_score_swing_set():
    from pytheory import Score
    score = Score("4/4", bpm=120, swing=0.5)
    assert score.swing == 0.5


def test_set_tempo():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.add("C4", Duration.WHOLE)
    score.set_tempo(140)
    assert len(score._tempo_changes) == 1
    beat_pos, new_bpm = score._tempo_changes[0]
    assert new_bpm == 140
    assert beat_pos == 4.0  # after one WHOLE note


def test_section_basic():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="sine")

    score.section("verse")
    lead.add("C5", Duration.WHOLE)

    score.section("chorus")
    lead.add("E5", Duration.WHOLE)
    score.end_section()

    assert "verse" in score._sections
    assert "chorus" in score._sections
    assert score._sections["verse"]._finalized
    assert score._sections["chorus"]._finalized


def test_section_repeat():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="sine")

    score.section("verse")
    lead.add("C5", Duration.WHOLE)  # 4 beats
    score.end_section()

    beats_before = score.total_beats
    assert beats_before == 4.0

    score.repeat("verse")
    assert score.total_beats == 8.0


def test_section_repeat_parts():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="sine")
    bass = score.part("bass", synth="triangle")

    score.section("verse")
    lead.add("C5", Duration.QUARTER)
    lead.add("D5", Duration.QUARTER)
    bass.add("C3", Duration.HALF)
    score.end_section()

    assert len(lead.notes) == 2
    assert len(bass.notes) == 1

    score.repeat("verse")
    assert len(lead.notes) == 4
    assert len(bass.notes) == 2

    score.repeat("verse", times=2)
    assert len(lead.notes) == 8
    assert len(bass.notes) == 4


def test_section_unknown_raises():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    with pytest.raises(ValueError, match="Unknown section"):
        score.repeat("nonexistent")


def test_repl_cmd_bpm():
    from pytheory.repl import Session, cmd_bpm
    s = Session()
    cmd_bpm(s, ["140"])
    assert s.bpm == 140
    assert s.score.bpm == 140


def test_repl_cmd_swing():
    from pytheory.repl import Session, cmd_swing
    s = Session()
    cmd_swing(s, ["0.5"])
    assert s.swing == 0.5


def test_repl_cmd_part():
    from pytheory.repl import Session, cmd_part
    s = Session()
    cmd_part(s, ["lead", "saw", "pluck"])
    assert "lead" in s.parts
    assert s.current_part is not None
    assert s.current_part.synth == "saw"
    assert s.current_part.envelope == "pluck"


def test_repl_cmd_rest():
    from pytheory.repl import Session, cmd_rest
    s = Session()
    s.ensure_part("lead")
    s.current_part = s.parts["lead"]
    cmd_rest(s, ["2"])
    assert len(s.current_part.notes) == 1
    assert s.current_part.notes[0].tone is None


def test_repl_cmd_lfo():
    from pytheory.repl import Session, cmd_part, cmd_lfo
    s = Session()
    cmd_part(s, ["lead"])
    cmd_lfo(s, ["lowpass", "0.5", "400", "3000", "4"])
    assert len(s.current_part._automation) > 0


def test_repl_prompt_with_part():
    from pytheory.repl import Session, cmd_part, _prompt
    s = Session()
    cmd_part(s, ["lead", "saw"])
    p = _prompt(s)
    assert "→lead(saw)" in p


def test_part_add_articulation():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine")
    p.add("C4", Duration.QUARTER, articulation="staccato")
    p.add("D4", Duration.QUARTER, articulation="legato")
    p.add("E4", Duration.QUARTER, articulation="marcato")
    p.add("F4", Duration.QUARTER, articulation="tenuto")
    p.add("G4", Duration.QUARTER, articulation="accent")
    p.add("A4", Duration.QUARTER, articulation="fermata")
    assert len(p.notes) == 6
    assert p.notes[0].articulation == "staccato"
    assert p.notes[5].articulation == "fermata"


def test_ramp_generates_automation():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="saw", lowpass=200)
    p.ramp(over=4.0, lowpass=8000)
    # Should have generated automation points
    assert len(p._automation) > 0
    # First point should be near 200, last near 8000
    first_lp = p._automation[0][1].get("lowpass", 0)
    last_lp = p._automation[-1][1].get("lowpass", 0)
    assert first_lp < 1000  # near start
    assert last_lp > 7000  # near target


def test_choir_morph_through_score():
    from pytheory.rhythm import Score
    from pytheory.play import render_score
    s = Score(bpm=120)
    choir = s.part("choir", synth="choir_synth", envelope="strings")
    choir.add("C4", 1, lyric="ah>oo")
    buf = render_score(s)
    assert numpy.isfinite(buf).all()
    assert numpy.abs(buf).max() > 0


def test_piano_partials_are_inharmonic():
    """Piano partials must be stretched sharp by string stiffness."""
    from pytheory.play import piano_wave, SAMPLE_RATE
    f0 = 261.63
    n = SAMPLE_RATE * 2
    w = piano_wave(f0, n_samples=n).astype(numpy.float64)
    spec = numpy.abs(numpy.fft.rfft(w * numpy.hanning(n)))
    freqs = numpy.fft.rfftfreq(n, 1 / SAMPLE_RATE)
    # Find the actual 10th partial near its stretched position
    target = f0 * 10 * 1.011
    m = (freqs > target - 40) & (freqs < target + 40)
    measured = freqs[m][numpy.argmax(spec[m])]
    cents_sharp = 1200 * numpy.log2(measured / (f0 * 10))
    assert 10 < cents_sharp < 35   # ~19 cents in theory; 0 would be harmonic
