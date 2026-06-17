"""Regression tests for the correctness/theory audit fixes.

Each test pins a specific bug found in the adversarial audit so it can't
silently come back. Grouped by the original issue numbers.
"""
import random

import pytest

from pytheory import Tone, Chord, Fretboard, Maqam
from pytheory.scales import TonedScale, Key


def _ts(tonic, scale="major"):
    return TonedScale(tonic=Tone.from_string(tonic))[scale]


# ── #14+15: fretboard matches chord tones by pitch class, not spelling ──

@pytest.mark.parametrize("sym", ["Eb", "Ab", "Db", "Gb", "Fm", "Cm",
                                 "Ebm7", "Abmaj7", "Bb", "C", "G", "Am"])
def test_flat_key_chords_cover_all_tones(sym):
    fb = Fretboard.guitar()
    want = {t.midi % 12 for t in Chord.from_symbol(sym).tones}
    got = {t.midi % 12 for t in fb.chord(sym).tones}
    assert want.issubset(got), f"{sym}: missing {want - got}"


# ── #1/2/17: Maqam Saba has its diminished 4th (Fab), no major 3rd ──

def test_saba_has_diminished_fourth():
    saba = Maqam.get("Saba")
    assert saba.degree_names() == ["Do", "Re↓", "Mib", "Fab", "Sol", "Lab", "Sib"]
    # The signature flat 4th, not a major 3rd; on C it reads as Fb (≈E).
    assert saba.note_names("C") == ["C", "D", "Eb", "E", "G", "Ab", "Bb"]


# ── #9: accidental Roman numerals are chromatic from the parallel major ──

def test_accidental_numerals_in_minor():
    minor = _ts("C", "minor")
    assert minor.progression("bVI")[0].tones[0].name == "Ab"   # not G
    assert minor.progression("bIII")[0].tones[0].name == "Eb"  # not D
    assert minor.progression("bVII")[0].tones[0].name == "Bb"  # not A
    # bare diatonic numerals are unchanged
    assert minor.progression("VI")[0].tones[0].name == "Ab"


def test_accidental_numerals_in_major_unchanged():
    major = _ts("C")
    assert major.progression("bVII")[0].tones[0].name == "Bb"
    assert major.progression("#IV")[0].tones[0].name == "F#"


# ── #10: extreme-key scales spell one letter per degree ──

@pytest.mark.parametrize("key,expected", [
    ("Gb", ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"]),
    ("F#", ["F#", "G#", "A#", "B", "C#", "D#", "E#"]),
    ("C#", ["C#", "D#", "E#", "F#", "G#", "A#", "B#"]),
    ("Cb", ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"]),
])
def test_extreme_key_spelling(key, expected):
    names = [t.name for t in _ts(key).tones[:7]]
    assert names == expected
    assert len({n[0] for n in names}) == 7  # each letter exactly once


def test_extreme_key_signature():
    assert Key("C#", "major").signature["sharps"] == 7
    assert Key("Cb", "major").signature["flats"] == 7


# octave-transpose in scale.chord() keeps the flat spelling (no Eb→D#)
def test_flat_key_triad_fifth_spelling():
    assert [t.name for t in _ts("Eb").triad(3)] == ["Ab", "C", "Eb"]
    assert [t.name for t in _ts("Gb").triad(3)] == ["Cb", "Eb", "Gb"]


# ── #5: from_symbol requires the whole suffix to be consumed ──

def test_from_symbol_rejects_unconsumed_suffix():
    with pytest.raises(ValueError):
        Chord.from_symbol("C7b9")
    with pytest.raises(ValueError):
        Chord.from_symbol("Cmajgarbage")


def test_from_symbol_supports_suspended_dominants():
    assert [t.name for t in Chord.from_symbol("E7sus4").tones] == ["E", "A", "B", "D"]


# ── #6: 13th chord drops the avoid-note 11th ──

def test_thirteenth_omits_eleventh():
    pcs = {t.midi % 12 for t in Chord.from_symbol("C13").tones}
    assert (5 + 0) % 12 not in {(p - 0) % 12 for p in pcs}  # no F (natural 11th)


# ── #8: 6th chords identify by root order, not as the relative 7th ──

def test_sixth_chords_identify():
    assert Chord.from_symbol("C6").identify() == "C major 6th"
    assert Chord.from_symbol("Cm6").identify() == "C minor 6th"
    assert Chord.from_symbol("Am7").identify() == "A minor 7th"


# ── #11: Nashville 'm' forces minor with readable spelling ──

def test_nashville_m_forces_minor():
    major = _ts("C")
    assert [t.name for t in major.nashville("4m")[0].tones] == ["F", "Ab", "C"]
    assert [t.name for t in major.nashville("5m")[0].tones] == ["G", "Bb", "D"]


# ── #18: garbage Roman numerals are rejected ──

@pytest.mark.parametrize("bad", ["XYZ", "", "IIII", "VIII", "foo"])
def test_numeral_garbage_rejected(bad):
    with pytest.raises(ValueError):
        _ts("C").progression(bad)


# ── #4: negative harmony spells reflected chords with flats ──

def test_negative_harmony_flat_spelling():
    neg = Chord.from_symbol("G7").negative_harmony("C")
    assert {t.name for t in neg.tones} == {"D", "F", "Ab", "C"}


# ── #19: from_midi → full_name → from_string roundtrips at octave -1 ──

@pytest.mark.parametrize("midi", [0, 5, 11, 12, 60, 127])
def test_octave_minus_one_roundtrip(midi):
    t = Tone.from_midi(midi)
    assert Tone.from_string(t.full_name).midi == midi


# ── #23: harmony/dissonance/beat_pulse return floats, even when empty ──

def test_empty_chord_metrics_are_floats():
    c = Chord(tones=[Tone.from_string("C4")])
    assert isinstance(c.harmony, float)
    assert isinstance(c.dissonance, float)
    assert isinstance(c.beat_pulse, float)


# ── #12: ensemble render never reseeds the global RNG ──

def test_ensemble_render_preserves_global_rng():
    from pytheory.rhythm import Score
    from pytheory.play import render_score

    random.seed(1234)
    before = [random.random() for _ in range(5)]

    random.seed(1234)
    s = Score(bpm=120)
    p = s.part("strings", synth="saw", ensemble=4)
    for n in ("C4", "E4", "G4"):
        p.add(n, 0.5)
    render_score(s)
    after = [random.random() for _ in range(5)]

    # The render must not have advanced/reseeded the global RNG stream.
    assert before == after


# ── #22: play()/save() reject a Score with a helpful TypeError ──

def test_play_rejects_score():
    from pytheory import play
    from pytheory.rhythm import Score
    s = Score(bpm=120)
    s.part("p").add("C4", 1)
    with pytest.raises(TypeError, match="play_score|render_score|save_midi"):
        play(s)
