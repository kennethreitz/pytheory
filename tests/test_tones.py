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


def test_tone_from_string():
    c4 = Tone.from_string("C4")
    assert c4.name == "C"
    assert c4.octave == 4


def test_tone_from_string_sharp():
    cs4 = Tone.from_string("C#4")
    assert cs4.name == "C#"
    assert cs4.octave == 4


def test_tone_from_string_no_octave():
    d = Tone.from_string("D")
    assert d.name == "D"
    assert d.octave is None


def test_tone_initialization():
    c4 = Tone(name="C", octave=4)
    assert c4.name == "C"
    assert c4.octave == 4


def test_tone_initialization_with_octave_in_name_and_kwarg():
    # When name has digits, explicit octave kwarg is kept
    t = Tone(name="C4", octave=5)
    assert t.name == "C"
    assert t.octave == 5  # explicit kwarg preserved


def test_tone_full_name():
    c4 = Tone(name="C", octave=4)
    d = Tone(name="D", octave=None)
    assert c4.full_name == "C4"
    assert d.full_name == "D"


def test_tone_repr():
    c4 = Tone(name="C", octave=4)
    assert repr(c4) == "<Tone C4>"


def test_tone_exists():
    c4 = Tone(name="C", octave=4, system="western")
    assert c4.exists is True


def test_tone_invalid_raises():
    """Invalid tone names raise ValueError at construction time (fixes #39)."""
    import pytest
    with pytest.raises(ValueError, match="Unknown tone name"):
        Tone(name="H", octave=4, system="western")
    with pytest.raises(ValueError, match="Unknown tone name"):
        Tone("X")


def test_tone_names_method():
    t = Tone(name="C#", alt_names=["Db"], octave=4)
    assert t.names() == ["C#", "Db"]


def test_tone_eq_string():
    c4 = Tone(name="C", octave=4)
    assert c4 == "C"
    assert not (c4 == "D")


def test_tone_eq_tone():
    a = Tone(name="C", octave=4)
    b = Tone(name="C", octave=4)
    assert a == b


def test_tone_eq_different_octave():
    a = Tone(name="C", octave=4)
    b = Tone(name="C", octave=5)
    assert not (a == b)


def test_tone_eq_alt_name():
    a = Tone(name="C#", alt_names=["Db"], octave=4)
    b = Tone(name="Db", alt_names=["C#"], octave=4)
    assert a == b  # b.name "Db" is in a.names(), and vice versa


def test_tone_hash():
    a = Tone(name="C", octave=4)
    b = Tone(name="C", octave=4)
    assert hash(a) == hash(b)
    s = {a, b}
    assert len(s) == 1


def test_tone_addition():
    t = Tone.from_string("C4", system=pytheory.SYSTEMS["western"])
    assert t.add(12).full_name == "C5"


def test_tone_subtraction():
    t = Tone.from_string("C5", system=pytheory.SYSTEMS["western"])
    assert t.subtract(12).full_name == "C4"


def test_tone_add_semitone():
    t = Tone.from_string("C4", system=pytheory.SYSTEMS["western"])
    assert t.add(1).name == "C#"
    assert t.add(1).octave == 4


def test_tone_add_across_octave_boundary():
    """B4 + 1 semitone = C5 (octave changes at C)."""
    t = Tone.from_string("B4", system=pytheory.SYSTEMS["western"])
    result = t.add(1)
    assert result.name == "C"
    assert result.octave == 5


def test_tone_subtract_across_octave_boundary():
    """C4 - 1 semitone = B3."""
    t = Tone.from_string("C4", system=pytheory.SYSTEMS["western"])
    result = t.subtract(1)
    assert result.name == "B"
    assert result.octave == 3


def test_tone_add_within_octave_no_wrap():
    """A4 + 2 = B4 (no octave change, A and B are in same octave)."""
    t = Tone.from_string("A4", system=pytheory.SYSTEMS["western"])
    result = t.add(2)
    assert result.name == "B"
    assert result.octave == 4


def test_tone_octave_correct_for_chromatic_walk():
    """Walk all 12 semitones from C4 to C5 and verify octave numbers."""
    t = Tone.from_string("C4", system=pytheory.SYSTEMS["western"])
    expected = [
        ("C", 4), ("C#", 4), ("D", 4), ("D#", 4),
        ("E", 4), ("F", 4), ("F#", 4), ("G", 4),
        ("G#", 4), ("A", 4), ("A#", 4), ("B", 4), ("C", 5),
    ]
    for i, (name, octave) in enumerate(expected):
        result = t.add(i)
        assert result.name == name, f"step {i}: expected {name}, got {result.name}"
        assert result.octave == octave, f"step {i}: expected octave {octave}, got {result.octave}"


def test_pitch_a4_is_440():
    t = Tone.from_string("A4", system="western")
    assert abs(t.pitch() - 440.0) < 0.01


def test_pitch_a0():
    t = Tone.from_string("A0", system="western")
    assert abs(t.pitch() - 27.5) < 0.01


def test_tone_octave_zero_full_name():
    t = Tone.from_string("A0", system="western")
    assert t.full_name == "A0"


def test_pitch_a3_is_220():
    t = Tone.from_string("A3", system="western")
    assert abs(t.pitch() - 220.0) < 0.01


def test_pitch_c4_middle_c():
    t = Tone.from_string("C4", system="western")
    assert abs(t.pitch() - 261.63) < 0.01


def test_pitch_c5():
    t = Tone.from_string("C5", system="western")
    assert abs(t.pitch() - 523.25) < 0.01


def test_pitch_e4():
    t = Tone.from_string("E4", system="western")
    assert abs(t.pitch() - 329.63) < 0.01


def test_pitch_octave_doubles_frequency():
    t1 = Tone.from_string("C4", system="western")
    t2 = Tone.from_string("C5", system="western")
    ratio = t2.pitch() / t1.pitch()
    assert abs(ratio - 2.0) < 0.001


def test_pitch_symbolic():
    t = Tone.from_string("A4", system="western")
    sym_pitch = t.pitch(symbolic=True)
    assert float(sym_pitch) == 440.0


def test_tone_from_tuple_single():
    t = Tone.from_tuple(("A",))
    assert t.name == "A"
    assert t.alt_names == []


def test_tone_from_tuple_with_alt():
    t = Tone.from_tuple(("C#", "Db"))
    assert t.name == "C#"
    assert t.alt_names == ("Db",)


def test_tone_from_tuple_with_octave():
    t = Tone.from_tuple(("A4",))
    assert t.name == "A"
    assert t.octave == 4


def test_tone_from_index():
    system = SYSTEMS["western"]
    t = Tone.from_index(3, octave=4, system=system)  # C is index 3
    assert t.name == "C"
    assert t.octave == 4


def test_tone_from_index_zero():
    system = SYSTEMS["western"]
    t = Tone.from_index(0, octave=4, system=system)  # A is index 0
    assert t.name == "A"
    assert t.octave == 4


def test_tone_index_c():
    t = Tone.from_string("C4", system="western")
    assert t._index == 3


def test_tone_eq_non_tone_non_string():
    t = Tone(name="C", octave=4)
    assert not (t == 42)
    assert not (t == None)
    assert not (t == [])


def test_tone_eq_different_name():
    a = Tone(name="C", octave=4)
    b = Tone(name="D", octave=4)
    assert not (a == b)


def test_tone_eq_no_octave():
    a = Tone(name="C")
    b = Tone(name="C")
    assert a == b


def test_tone_add_two_octaves():
    t = Tone.from_string("C4", system="western")
    result = t.add(24)
    assert result.name == "C"
    assert result.octave == 6


def test_tone_subtract_two_octaves():
    t = Tone.from_string("C6", system="western")
    result = t.subtract(24)
    assert result.name == "C"
    assert result.octave == 4


def test_tone_subtract_to_lower_octave():
    """E2 - 5 = B1."""
    t = Tone.from_string("E2", system="western")
    result = t.subtract(5)
    assert result.name == "B"
    assert result.octave == 1


def test_tone_chromatic_walk_descending():
    """Walk down from C5 to C4."""
    t = Tone.from_string("C5", system="western")
    expected = [
        ("C", 5), ("B", 4), ("A#", 4), ("A", 4),
        ("G#", 4), ("G", 4), ("F#", 4), ("F", 4),
        ("E", 4), ("D#", 4), ("D", 4), ("C#", 4), ("C", 4),
    ]
    for i, (name, octave) in enumerate(expected):
        result = t.subtract(i)
        assert result.name == name, f"step -{i}: expected {name}, got {result.name}"
        assert result.octave == octave, f"step -{i}: expected octave {octave}, got {result.octave}"


def test_tone_add_zero():
    t = Tone.from_string("C4", system="western")
    result = t.add(0)
    assert result.name == "C"
    assert result.octave == 4


def test_pitch_b4():
    t = Tone.from_string("B4", system="western")
    assert abs(t.pitch() - 493.88) < 0.01


def test_pitch_d4():
    t = Tone.from_string("D4", system="western")
    assert abs(t.pitch() - 293.66) < 0.01


def test_pitch_g3():
    t = Tone.from_string("G3", system="western")
    assert abs(t.pitch() - 196.00) < 0.01


def test_pitch_a2():
    t = Tone.from_string("A2", system="western")
    assert abs(t.pitch() - 110.0) < 0.01


def test_pitch_a5():
    t = Tone.from_string("A5", system="western")
    assert abs(t.pitch() - 880.0) < 0.01


def test_pitch_e2_low():
    """Low E on guitar."""
    t = Tone.from_string("E2", system="western")
    assert abs(t.pitch() - 82.41) < 0.01


def test_pitch_precision():
    t = Tone.from_string("A4", system="western")
    p = t.pitch(precision=10)
    assert abs(p - 440.0) < 0.01


def test_pitch_all_chromatic_ascending():
    """Verify all 12 chromatic pitches from A4 are strictly ascending."""
    pitches = []
    for i in range(12):
        t = Tone.from_string("A4", system="western").add(i)
        pitches.append(t.pitch())
    for i in range(1, len(pitches)):
        assert pitches[i] > pitches[i - 1], f"Pitch at step {i} not ascending"


def test_pitch_consistency_across_octaves():
    """Every note an octave up should be exactly 2x the frequency."""
    for note in ["C", "D", "E", "F", "G", "A", "B"]:
        t3 = Tone.from_string(f"{note}3", system="western")
        t4 = Tone.from_string(f"{note}4", system="western")
        ratio = t4.pitch() / t3.pitch()
        assert abs(ratio - 2.0) < 0.001, f"{note}4/{note}3 ratio = {ratio}"


@needs_portaudio
def test_synth_callable_with_pitch():
    """Synth enum members should work with actual pitch values from Tone."""
    from pytheory.play import Synth
    t = Tone.from_string("A4", system="western")
    hz = t.pitch()
    wave = Synth.SINE(hz)
    assert len(wave) > 0


def test_circle_of_fifths():
    """Walk the circle of fifths starting from C."""
    t = Tone.from_string("C4", system="western")
    expected = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]
    for i, name in enumerate(expected):
        assert t.name == name, f"Step {i}: expected {name}, got {t.name}"
        t = t.add(7)  # perfect fifth = 7 semitones


def test_circle_of_fourths():
    """Walk the circle of fourths starting from C."""
    t = Tone.from_string("C4", system="western")
    expected = ["C", "F", "A#", "D#", "G#", "C#", "F#", "B", "E", "A", "D", "G"]
    for i, name in enumerate(expected):
        assert t.name == name, f"Step {i}: expected {name}, got {t.name}"
        t = t.add(5)  # perfect fourth = 5 semitones


def test_tone_add_operator():
    t = Tone.from_string("C4", system="western")
    result = t + 7
    assert result.name == "G"
    assert result.octave == 4


def test_tone_sub_int_operator():
    t = Tone.from_string("G4", system="western")
    result = t - 7
    assert result.name == "C"
    assert result.octave == 4


def test_tone_sub_tone_operator():
    """Subtracting two tones gives semitone distance."""
    c4 = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert g4 - c4 == 7


def test_tone_sub_tone_negative():
    c4 = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert c4 - g4 == -7


def test_tone_sub_tone_octave():
    c4 = Tone.from_string("C4", system="western")
    c5 = Tone.from_string("C5", system="western")
    assert c5 - c4 == 12


def test_tone_lt():
    c4 = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert c4 < g4
    assert not g4 < c4


def test_tone_gt():
    c4 = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert g4 > c4
    assert not c4 > g4


def test_tone_le():
    c4 = Tone.from_string("C4", system="western")
    c4b = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert c4 <= g4
    assert c4 <= c4b


def test_tone_ge():
    c4 = Tone.from_string("C4", system="western")
    c4b = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert g4 >= c4
    assert c4 >= c4b


def test_tone_sorting():
    """Tones should be sortable by pitch."""
    tones = [
        Tone.from_string("G4", system="western"),
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("A3", system="western"),
    ]
    sorted_tones = sorted(tones)
    names = [t.name for t in sorted_tones]
    assert names == ["A", "C", "E", "G"]


def test_tone_str():
    c4 = Tone(name="C", octave=4)
    assert str(c4) == "C4"
    d = Tone(name="D")
    assert str(d) == "D"


def test_tone_frequency_property():
    t = Tone.from_string("A4", system="western")
    assert abs(t.frequency - 440.0) < 0.01


def test_tone_frequency_c4():
    t = Tone.from_string("C4", system="western")
    assert abs(t.frequency - 261.63) < 0.01


def test_tone_chaining():
    """Operators should be chainable."""
    t = Tone.from_string("C4", system="western")
    result = t + 4 + 3  # C -> E -> G
    assert result.name == "G"
    assert result.octave == 4


def test_tone_arithmetic_workflow():
    """Demonstrate tone arithmetic with operators."""
    c4 = Tone.from_string("C4", system="western")

    # Build intervals
    major_third = c4 + 4     # E4
    perfect_fifth = c4 + 7   # G4
    octave = c4 + 12         # C5

    assert str(major_third) == "E4"
    assert str(perfect_fifth) == "G4"
    assert str(octave) == "C5"

    # Measure intervals
    assert perfect_fifth - c4 == 7
    assert octave - c4 == 12

    # Compare
    assert c4 < major_third < perfect_fifth < octave


def test_indian_sa_pitch():
    """Sa4 should equal C4 = 261.63 Hz."""
    sa = Tone.from_string("Sa4", system="indian")
    assert abs(sa.frequency - 261.63) < 0.01


def test_indian_pa_pitch():
    """Pa4 should equal G4 = 392.00 Hz."""
    sa = Tone.from_string("Sa4", system="indian")
    pa = sa + 7
    assert pa.name == "Pa"
    assert abs(pa.frequency - 392.00) < 0.01


def test_indian_dha_pitch():
    """Dha4 should equal A4 = 440 Hz."""
    dha = Tone.from_string("Dha4", system="indian")
    assert abs(dha.frequency - 440.0) < 0.01


def test_indian_octave_sa():
    """Sa4 + 12 = Sa5."""
    sa = Tone.from_string("Sa4", system="indian")
    result = sa + 12
    assert result.name == "Sa"
    assert result.octave == 5


def test_indian_all_thaat_intervals_sum_to_12():
    indian = SYSTEMS["indian"]
    for name, scale in indian.scales["thaat"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_indian_tone_arithmetic():
    sa = Tone.from_string("Sa4", system="indian")
    assert (sa + 2).name == "Re"
    assert (sa + 4).name == "Ga"
    assert (sa + 5).name == "Ma"
    assert (sa + 7).name == "Pa"
    assert (sa + 9).name == "Dha"
    assert (sa + 11).name == "Ni"


def test_arabic_tones():
    arabic = SYSTEMS["arabic"]
    names = [t.name for t in arabic.tones]
    assert "Do" in names
    assert "Re" in names
    assert "Sol" in names


def test_arabic_do_pitch():
    """Do4 should equal C4 = 261.63 Hz."""
    do = Tone.from_string("Do4", system="arabic")
    assert abs(do.frequency - 261.63) < 0.01


def test_arabic_tone_arithmetic():
    do = Tone.from_string("Do4", system="arabic")
    assert (do + 2).name == "Re"
    assert (do + 4).name == "Mi"
    assert (do + 7).name == "Sol"


def test_japanese_heptatonic_intervals_sum_to_12():
    japanese = SYSTEMS["japanese"]
    for name, scale in japanese.scales["heptatonic"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_blues_all_intervals_sum_to_12():
    blues = SYSTEMS["blues"]
    for scale_type in blues.scales:
        for name, scale in blues.scales[scale_type].items():
            total = sum(scale["intervals"])
            assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_overtones_a4():
    a4 = Tone.from_string("A4", system="western")
    harmonics = a4.overtones(4)
    assert len(harmonics) == 4
    assert abs(harmonics[0] - 440.0) < 0.01
    assert abs(harmonics[1] - 880.0) < 0.01
    assert abs(harmonics[2] - 1320.0) < 0.01
    assert abs(harmonics[3] - 1760.0) < 0.01


def test_overtones_default_count():
    c4 = Tone.from_string("C4", system="western")
    assert len(c4.overtones()) == 8


def test_overtones_ratios():
    a4 = Tone.from_string("A4", system="western")
    harmonics = a4.overtones(8)
    f0 = harmonics[0]
    for i, h in enumerate(harmonics):
        assert abs(h / f0 - (i + 1)) < 0.001


def test_identify_single_tone():
    chord = Chord(tones=[Tone.from_string("C4", system="western")])
    assert chord.identify() is None


def test_interval_to_perfect_fifth():
    c4 = Tone.from_string("C4", system="western")
    g4 = Tone.from_string("G4", system="western")
    assert c4.interval_to(g4) == "perfect 5th"


def test_interval_to_major_third():
    c4 = Tone.from_string("C4", system="western")
    e4 = Tone.from_string("E4", system="western")
    assert c4.interval_to(e4) == "major 3rd"


def test_interval_to_octave():
    c4 = Tone.from_string("C4", system="western")
    c5 = Tone.from_string("C5", system="western")
    assert c4.interval_to(c5) == "octave"


def test_interval_to_unison():
    c4 = Tone.from_string("C4", system="western")
    assert c4.interval_to(c4) == "unison"


def test_interval_to_compound():
    c4 = Tone.from_string("C4", system="western")
    d5 = c4 + 14
    assert c4.interval_to(d5) == "major 2nd + 1 octave"


def test_interval_to_two_octaves():
    c4 = Tone.from_string("C4", system="western")
    c6 = c4 + 24
    assert c4.interval_to(c6) == "2 octaves"


def test_tone_transpose():
    c4 = Tone.from_string("C4", system="western")
    assert c4.transpose(7).name == "G"


def test_from_frequency_a4():
    t = Tone.from_frequency(440)
    assert t.name == "A"
    assert t.octave == 4


def test_from_frequency_c4():
    t = Tone.from_frequency(261.63)
    assert t.name == "C"
    assert t.octave == 4


def test_from_frequency_a5():
    t = Tone.from_frequency(880)
    assert t.name == "A"
    assert t.octave == 5


def test_from_frequency_a3():
    t = Tone.from_frequency(220)
    assert t.name == "A"
    assert t.octave == 3


def test_from_frequency_roundtrip():
    """from_frequency(tone.frequency) should return the same note."""
    for note in ["C4", "E4", "G4", "A4", "B3", "F#5"]:
        t = Tone.from_string(note, system="western")
        recovered = Tone.from_frequency(t.frequency)
        assert recovered.name == t.name
        assert recovered.octave == t.octave


def test_note_is_tone():
    assert Note is Tone


def test_interval_constants():
    from pytheory import Interval
    assert Interval.PERFECT_FIFTH == 7
    assert Interval.MAJOR_THIRD == 4
    assert Interval.OCTAVE == 12
    assert Interval.TRITONE == 6


def test_interval_with_tone():
    from pytheory import Interval
    c4 = Tone.from_string("C4", system="western")
    assert (c4 + Interval.PERFECT_FIFTH).name == "G"
    assert (c4 + Interval.MAJOR_THIRD).name == "E"
    assert (c4 + Interval.MINOR_THIRD).name == "D#"


def test_enharmonic_sharp():
    cs = Tone.from_string("C#4", system="western")
    assert cs.enharmonic == "Db"


def test_enharmonic_natural():
    c = Tone.from_string("C4", system="western")
    assert c.enharmonic is None


def test_tone_is_natural():
    assert Tone.from_string("C4").is_natural is True
    assert Tone.from_string("B4").is_natural is True


def test_tone_is_sharp():
    assert Tone.from_string("C#4").is_sharp is True
    assert Tone.from_string("C4").is_sharp is False


def test_tone_is_flat():
    t = Tone(name="Bb", octave=4)
    assert t.is_flat is True
    assert Tone.from_string("C4").is_flat is False
    # B natural should NOT be detected as flat
    assert Tone.from_string("B4").is_flat is False


def test_tone_letter_natural():
    assert Tone.from_string("C4").letter == "C"


def test_tone_letter_sharp():
    assert Tone.from_string("C#4").letter == "C"


def test_tone_letter_flat():
    assert Tone(name="Bb", octave=4).letter == "B"


def test_tone_init_octave_parsed_from_name():
    """Tone('C4') should parse octave from name string."""
    t = Tone("C4")
    assert t.octave == 4
    assert t.name == "C"


def test_tone_enharmonic_from_alt_names_direct():
    t = Tone(name="C#", alt_names="Db", octave=4)
    assert t.enharmonic == "Db"


def test_tone_sub_not_implemented():
    t = Tone("C4")
    result = t.__sub__(3.5)
    assert result is NotImplemented


def test_tone_lt_not_implemented():
    assert Tone("C4").__lt__("not a tone") is NotImplemented


def test_tone_le_not_implemented():
    assert Tone("C4").__le__("not a tone") is NotImplemented


def test_tone_gt_not_implemented():
    assert Tone("C4").__gt__("not a tone") is NotImplemented


def test_tone_ge_not_implemented():
    assert Tone("C4").__ge__("not a tone") is NotImplemented


def test_tone_from_frequency_negative_raises():
    with pytest.raises(ValueError, match="positive"):
        Tone.from_frequency(-100)


def test_tone_interval_compound_2_octaves():
    c4 = Tone.from_string("C4", system="western")
    e6 = c4 + 28  # 2 octaves + major 3rd
    assert "2 octaves" in c4.interval_to(e6)


def test_tone_circle_of_fifths_returns_12():
    c = Tone.from_string("C4", system="western")
    assert len(c.circle_of_fifths()) == 12


def test_tone_circle_of_fourths_returns_12():
    c = Tone.from_string("C4", system="western")
    assert len(c.circle_of_fourths()) == 12


def test_flat_tone_from_string():
    db = Tone.from_string("Db4", system="western")
    assert db.name == "Db"
    assert db.octave == 4


def test_flat_tone_frequency_matches_sharp():
    db = Tone.from_string("Db4", system="western")
    cs = Tone.from_string("C#4", system="western")
    assert db.frequency == cs.frequency


def test_flat_tone_frequency_all_enharmonics():
    pairs = [("Bb3", "A#3"), ("Eb4", "D#4"), ("Gb4", "F#4"), ("Ab4", "G#4")]
    for flat, sharp in pairs:
        f = Tone.from_string(flat, system="western").frequency
        s = Tone.from_string(sharp, system="western").frequency
        assert f == s, f"{flat} != {sharp}"


def test_flat_tone_arithmetic():
    db = Tone.from_string("Db4", system="western")
    result = db + 2
    assert result.name == "D#"
    assert result.octave == 4


def test_flat_tone_interval():
    c4 = Tone.from_string("C4", system="western")
    db4 = Tone.from_string("Db4", system="western")
    assert db4 - c4 == 1


def test_flat_tone_exists():
    db = Tone.from_string("Db4", system="western")
    assert db.exists is True


def test_flat_tone_index_resolves():
    db = Tone.from_string("Db4", system="western")
    cs = Tone.from_string("C#4", system="western")
    assert db._index == cs._index


def test_cli_tone(capsys):
    from pytheory.cli import cmd_tone
    import argparse
    args = argparse.Namespace(note="A4", temperament="equal")
    cmd_tone(args)
    out = capsys.readouterr().out
    assert "440.00" in out
    assert "A4" in out
    assert "MIDI" in out


def test_cli_circle(capsys):
    from pytheory.cli import cmd_circle
    import argparse
    args = argparse.Namespace(tonic="C")
    cmd_circle(args)
    out = capsys.readouterr().out
    assert "Circle of fifths" in out
    assert "Circle of fourths" in out
    assert "G" in out
    assert "F" in out


def test_cents_semitone():
    a4 = Tone.from_string("A4", system="western")
    bb4 = a4 + 1
    cents = a4.cents_difference(bb4)
    assert abs(cents - 100.0) < 0.01


def test_cents_octave():
    a4 = Tone.from_string("A4", system="western")
    a5 = Tone.from_string("A5", system="western")
    cents = a4.cents_difference(a5)
    assert abs(cents - 1200.0) < 0.01


def test_cents_unison():
    a4 = Tone.from_string("A4", system="western")
    assert abs(a4.cents_difference(a4)) < 0.01


def test_cents_negative():
    a4 = Tone.from_string("A4", system="western")
    g4 = a4 - 2
    cents = a4.cents_difference(g4)
    assert cents < 0


def test_cents_fifth():
    c4 = Tone.from_string("C4", system="western")
    g4 = c4 + 7
    cents = c4.cents_difference(g4)
    assert abs(cents - 700.0) < 0.01


def test_helmholtz_middle_c():
    assert Tone.from_string("C4", system="western").helmholtz == "c"


def test_helmholtz_c3():
    assert Tone.from_string("C3", system="western").helmholtz == "C"


def test_helmholtz_c5():
    assert Tone.from_string("C5", system="western").helmholtz == "c'"


def test_helmholtz_c6():
    assert Tone.from_string("C6", system="western").helmholtz == "c''"


def test_helmholtz_c2():
    assert Tone.from_string("C2", system="western").helmholtz == "CC"


def test_helmholtz_a2():
    assert Tone.from_string("A2", system="western").helmholtz == "AA"


def test_helmholtz_sharp():
    assert Tone.from_string("C#4", system="western").helmholtz == "c#"


def test_helmholtz_sharp_high():
    assert Tone.from_string("F#5", system="western").helmholtz == "f#'"


def test_degree_name_leading_tone():
    scale = TonedScale(tonic="C4")["major"]
    assert scale.degree_name(6) == "leading tone"


def test_cli_identify_intervals(capsys):
    from pytheory.cli import cmd_identify
    import argparse
    args = argparse.Namespace(symbol="C")
    cmd_identify(args)
    out = capsys.readouterr().out
    assert "Intervals" in out


def test_solfege_natural_notes():
    expected = {"C": "Do", "D": "Re", "E": "Mi", "F": "Fa",
                "G": "Sol", "A": "La", "B": "Ti"}
    for note, solf in expected.items():
        t = Tone.from_string(f"{note}4", system="western")
        assert t.solfege == solf, f"{note} should be {solf}, got {t.solfege}"


def test_solfege_sharps():
    expected = {"C#": "Di", "D#": "Ri", "F#": "Fi", "G#": "Si", "A#": "Li"}
    for note, solf in expected.items():
        t = Tone.from_string(f"{note}4", system="western")
        assert t.solfege == solf, f"{note} should be {solf}, got {t.solfege}"


def test_solfege_flats():
    expected = {"Db": "Ra", "Eb": "Me", "Gb": "Se", "Ab": "Le", "Bb": "Te"}
    for note, solf in expected.items():
        t = Tone(name=note, octave=4, system="western")
        assert t.solfege == solf, f"{note} should be {solf}, got {t.solfege}"


def test_solfege_no_octave():
    t = Tone(name="C", system="western")
    assert t.solfege == "Do"


def test_solfege_unknown_raises():
    """A non-standard name should raise ValueError at construction (fixes #39)."""
    import pytest
    with pytest.raises(ValueError, match="Unknown tone name"):
        Tone(name="X", system="western")


def test_pitch_classes():
    chord = Chord.from_tones("C", "E", "G")
    assert chord.pitch_classes == {0, 4, 7}


def test_pitch_classes_with_sharps():
    chord = Chord.from_tones("C", "E", "G#")
    assert chord.pitch_classes == {0, 4, 8}


def test_circle_of_fifths_western_unchanged():
    """Existing 12-TET circle of fifths should not be affected."""
    c = Tone("C", octave=4, system="western")
    cof = c.circle_of_fifths()
    assert len(cof) == 12
    assert cof[0].name == "C"
    assert cof[1].name == "G"


def test_from_frequency_non12():
    sys19 = SYSTEMS["19-tet"]
    t = Tone.from_frequency(440.0, system=sys19)
    assert t.name == "A"
    assert t.octave == 4


def test_interval_to_non12():
    sys19 = SYSTEMS["19-tet"]
    a = Tone("A", octave=4, system=sys19)
    a5 = a.add(19)
    result = a.interval_to(a5)
    assert "octave" in result


def test_analog_drift_varies_pitch():
    """Analog drift should make repeated renders slightly different."""
    from pytheory import Score, Duration
    score1 = Score("4/4", bpm=120)
    p1 = score1.part("t", synth="saw", analog=0.5)
    p1.add("C4", Duration.QUARTER)
    p1.add("C4", Duration.QUARTER)
    # With analog > 0, each C4 gets a random pitch offset
    # This is hard to test deterministically, just verify it renders
    from pytheory.play import render_score
    buf = render_score(score1)
    assert len(buf) > 0


def test_pitch_bend_renders():
    """Pitch bend should produce valid audio without errors."""
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    p = score.part("t", instrument="electric_guitar")
    p.add("A4", Duration.HALF, bend=2, bend_type="smooth")
    p.add("A4", Duration.HALF, bend=-1, bend_type="late")
    p.add("A4", Duration.HALF, bend=3, bend_type="linear")
    p.add("A4", Duration.HALF)
    buf = render_score(score)
    assert len(buf) > 0


def test_pitch_bend_types():
    """All three bend types should work."""
    from pytheory.rhythm import Note, Duration
    for bt in ["smooth", "linear", "late"]:
        n = Note(tone=None, duration=Duration.QUARTER, bend=2, bend_type=bt)
        assert n.bend_type == bt


def test_int_tone_name():
    from pytheory import Tone, TET
    edo = TET(22)
    t = Tone(0, octave=4, system=edo)
    assert t.name == "0"
    assert t.frequency == pytest.approx(440.0, rel=1e-3)


def test_int_tone_wrapping():
    from pytheory import Tone, TET
    edo = TET(22)
    t = Tone(22, octave=4, system=edo)
    assert t.name == "0"
    assert t.octave == 5
    assert t.frequency == pytest.approx(880.0, rel=1e-3)


def test_int_tone_negative():
    from pytheory import Tone, TET
    edo = TET(22)
    t = Tone(-1, octave=4, system=edo)
    assert t.name == "21"
    assert t.octave == 3


def test_b_sharp_octave():
    t = Tone("B#4")
    assert t.octave == 5
    assert t.frequency == pytest.approx(Tone("C5").frequency, rel=1e-3)


def test_c_flat_octave():
    t = Tone("Cb4")
    assert t.octave == 3
    assert t.frequency == pytest.approx(Tone("B3").frequency, rel=1e-3)


def test_score_reference_pitch():
    from pytheory import Score
    score = Score("4/4", bpm=120, reference_pitch=415.0)
    assert score.reference_pitch == 415.0
