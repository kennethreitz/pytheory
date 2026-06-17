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


def test_chord_creation():
    c_major = Chord(
        tones=[
            Tone(name="C", octave=4),
            Tone(name="E", octave=4),
            Tone(name="G", octave=4),
        ]
    )
    assert len(c_major.tones) == 3
    assert c_major.tones[0].full_name == "C4"
    assert c_major.tones[1].full_name == "E4"
    assert c_major.tones[2].full_name == "G4"


def test_chord_harmony():
    c_major = Chord(
        tones=[
            Tone(name="C", octave=4),
            Tone(name="E", octave=4),
            Tone(name="G", octave=4),
        ]
    )
    assert c_major.harmony > 0


def test_chord_dissonance():
    c_major = Chord(
        tones=[
            Tone(name="C", octave=4),
            Tone(name="E", octave=4),
            Tone(name="G", octave=4),
        ]
    )
    assert c_major.dissonance > 0


def test_chord_single_tone():
    single = Chord(tones=[Tone(name="C", octave=4)])
    assert single.harmony == 0
    assert single.dissonance == 0
    assert single.beat_pulse == 0
    assert single.intervals == []


def test_chord_repr():
    c = Chord(tones=[Tone(name="C", octave=4), Tone(name="E", octave=4)])
    assert "C4" in repr(c)
    assert "E4" in repr(c)


def test_named_chord_c_major_tones():
    c = NamedChord(tone_name="C", quality="")
    names = c.acceptable_tone_names
    assert "C" in names
    assert "E" in names
    assert "G" in names


def test_named_chord_c_major_explicit_tones():
    c = NamedChord(tone_name="C", quality="maj")
    names = c.acceptable_tone_names
    assert "C" in names
    assert "E" in names
    assert "G" in names


def test_named_chord_c_minor_tones():
    cm = NamedChord(tone_name="C", quality="m")
    names = cm.acceptable_tone_names
    assert "C" in names
    assert "Eb" in names  # minor 3rd
    assert "G" in names


def test_named_chord_power_chord():
    c5 = NamedChord(tone_name="C", quality="5")
    names = c5.acceptable_tone_names
    assert "C" in names
    assert "G" in names
    assert len(names) == 2


def test_named_chord_dominant_7th():
    c7 = NamedChord(tone_name="C", quality="7")
    names = c7.acceptable_tone_names
    assert "C" in names
    assert "E" in names   # major 3rd
    assert "G" in names   # perfect 5th
    assert "Bb" in names  # minor 7th


def test_named_chord_diminished():
    cdim = NamedChord(tone_name="C", quality="dim")
    names = cdim.acceptable_tone_names
    assert "C" in names
    assert "Eb" in names  # minor 3rd
    assert "Gb" in names  # diminished 5th


def test_named_chord_minor_7th():
    cm7 = NamedChord(tone_name="C", quality="m7")
    names = cm7.acceptable_tone_names
    assert "C" in names
    assert "Eb" in names  # minor 3rd
    assert "G" in names   # perfect 5th
    assert "Bb" in names  # minor 7th


def test_named_chord_major_7th():
    cmaj7 = NamedChord(tone_name="C", quality="maj7")
    names = cmaj7.acceptable_tone_names
    assert "C" in names
    assert "E" in names  # major 3rd
    assert "G" in names  # perfect 5th
    assert "B" in names  # major 7th


def test_tone_add_tritone():
    """C + 6 semitones = F#."""
    t = Tone.from_string("C4", system="western")
    result = t.add(6)
    assert result.name == "F#"
    assert result.octave == 4


def test_chord_intervals_c_major():
    """C4-E4-G4 intervals should be 4 and 3 semitones (major 3rd + minor 3rd)."""
    c_major = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert c_major.intervals == [4, 3]


def test_chord_intervals_octave():
    c_oct = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("C5", system="western"),
    ])
    assert c_oct.intervals == [12]


def test_chord_intervals_minor_triad():
    a_minor = Chord(tones=[
        Tone.from_string("A4", system="western"),
        Tone.from_string("C5", system="western"),
        Tone.from_string("E5", system="western"),
    ])
    assert a_minor.intervals == [3, 4]  # minor 3rd + major 3rd


def test_chord_beat_pulse_unison():
    """Two identical tones should have beat pulse of 0."""
    chord = Chord(tones=[
        Tone.from_string("A4", system="western"),
        Tone.from_string("A4", system="western"),
    ])
    assert chord.beat_pulse == 0


def test_chord_beat_pulse_octave():
    """Two tones an octave apart should have beat pulse = 440 Hz."""
    chord = Chord(tones=[
        Tone.from_string("A4", system="western"),
        Tone.from_string("A5", system="western"),
    ])
    assert abs(chord.beat_pulse - 440.0) < 0.01


def test_chord_beat_frequencies():
    """beat_frequencies returns sorted (tone, tone, hz) tuples."""
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    beats = chord.beat_frequencies
    assert len(beats) == 3  # 3 pairs from 3 tones
    # Should be sorted ascending by Hz
    assert beats[0][2] <= beats[1][2] <= beats[2][2]


def test_chord_empty():
    chord = Chord(tones=[])
    assert chord.harmony == 0
    assert chord.dissonance == 0
    assert chord.beat_pulse == 0
    assert chord.intervals == []
    assert chord.beat_frequencies == []


def test_chord_harmony_fifth_beats_tritone():
    """A perfect fifth (3:2) should score higher harmony than a tritone."""
    fifth = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    tritone = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("F#4", system="western"),
    ])
    assert fifth.harmony > tritone.harmony


def test_chord_harmony_octave_highest():
    """An octave (2:1) should score highest harmony."""
    octave = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("C5", system="western"),
    ])
    fifth = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert octave.harmony > fifth.harmony


def test_chord_dissonance_tritone_vs_fifth():
    """A tritone should produce more roughness than a perfect fifth."""
    tritone = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("F#4", system="western"),
    ])
    fifth = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert tritone.dissonance > fifth.dissonance


def test_chord_dissonance_wide_interval_low():
    """Very wide intervals (octave+) should have low roughness."""
    octave = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("C5", system="western"),
    ])
    third = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
    ])
    # Octave exceeds critical bandwidth → less roughness than a 3rd
    assert octave.dissonance < third.dissonance


def test_chord_dissonance_positive():
    """Any two distinct tones should produce non-zero roughness."""
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert chord.dissonance > 0


def test_named_chord_repr():
    c = NamedChord(tone_name="C", quality="m7")
    assert repr(c) == "<NamedChord name='Cm7'>"


def test_named_chord_name_property():
    c = NamedChord(tone_name="A", quality="maj7")
    assert c.name == "Amaj7"


def test_named_chord_flat_to_sharp_conversion():
    """Flat tone names should be converted to sharp equivalents internally."""
    bb = NamedChord(tone_name="Bb", quality="")
    assert bb.tone.name == "A#"

    ab = NamedChord(tone_name="Ab", quality="")
    assert ab.tone.name == "G#"

    db = NamedChord(tone_name="Db", quality="")
    assert db.tone.name == "C#"

    eb = NamedChord(tone_name="Eb", quality="")
    assert eb.tone.name == "D#"

    gb = NamedChord(tone_name="Gb", quality="")
    assert gb.tone.name == "F#"


def test_named_chord_m6_tones():
    cm6 = NamedChord(tone_name="C", quality="m6")
    names = cm6.acceptable_tone_names
    assert "C" in names
    assert "Eb" in names  # minor 3rd
    assert "G" in names   # perfect 5th
    assert "A" in names   # major 6th
    assert len(names) == 4


def test_named_chord_m9_tones():
    cm9 = NamedChord(tone_name="C", quality="m9")
    names = cm9.acceptable_tone_names
    assert "C" in names
    assert "Eb" in names  # minor 3rd
    assert "G" in names   # perfect 5th
    assert "Bb" in names  # minor 7th
    assert "D" in names   # major 9th
    assert len(names) == 5


def test_named_chord_maj9_tones():
    cmaj9 = NamedChord(tone_name="C", quality="maj9")
    names = cmaj9.acceptable_tone_names
    assert "C" in names
    assert "E" in names   # major 3rd
    assert "G" in names   # perfect 5th
    assert "B" in names   # major 7th
    assert "D" in names   # major 9th
    assert len(names) == 5


def test_named_chord_9_tones():
    c9 = NamedChord(tone_name="C", quality="9")
    names = c9.acceptable_tone_names
    assert "C" in names
    assert "E" in names   # major 3rd
    assert "G" in names   # perfect 5th
    assert "Bb" in names  # minor 7th
    assert "D" in names   # major 9th
    assert len(names) == 5


def test_build_chord_from_scale(guitar_fretboard):
    """Build a I-IV-V progression from C major and verify fingerings."""
    c = TonedScale(tonic="C4")
    major = c["major"]

    tonic = major["I"].name       # C
    subdominant = major["IV"].name  # F
    dominant = major["V"].name     # G

    chart = CHARTS["western"]
    for name in [tonic, subdominant, dominant]:
        fingering = chart[name].fingering(fretboard=guitar_fretboard)
        assert len(fingering) == 6


def test_scale_chord():
    c = TonedScale(tonic="C4")
    major = c["major"]
    chord = major.chord(0, 2, 4)  # C E G
    assert len(chord) == 3
    assert chord.tones[0].name == "C"
    assert chord.tones[1].name == "E"
    assert chord.tones[2].name == "G"


def test_scale_chord_seventh():
    """Build a 7th chord from scale degrees."""
    c = TonedScale(tonic="C4")
    major = c["major"]
    seventh = major.chord(0, 2, 4, 6)  # C E G B = Cmaj7
    assert len(seventh) == 4
    names = [t.name for t in seventh]
    assert names == ["C", "E", "G", "B"]


def test_chord_iter():
    chord = Chord(tones=[
        Tone(name="C", octave=4),
        Tone(name="E", octave=4),
        Tone(name="G", octave=4),
    ])
    names = [t.name for t in chord]
    assert names == ["C", "E", "G"]


def test_chord_len():
    chord = Chord(tones=[
        Tone(name="C", octave=4),
        Tone(name="E", octave=4),
    ])
    assert len(chord) == 2


def test_chord_contains_name():
    chord = Chord(tones=[
        Tone(name="C", octave=4),
        Tone(name="E", octave=4),
        Tone(name="G", octave=4),
    ])
    assert "C" in chord
    assert "E" in chord
    assert "D" not in chord


def test_chord_contains_tone():
    c4 = Tone(name="C", octave=4)
    chord = Chord(tones=[c4, Tone(name="E", octave=4)])
    assert c4 in chord


def test_chord_low_to_high_default():
    """By default, chord fingerings read low-to-high (low E first)."""
    fb = Fretboard.guitar()
    g = fb.chord("G")
    assert g.string_names == ("E", "A", "D", "G", "B", "e")
    assert g.positions == (3, 2, 0, 0, 0, 3)


def test_chord_high_to_low_opt_out():
    """high_to_low=True restores the pre-0.43 high-to-low order."""
    fb = Fretboard.guitar(high_to_low=True)
    g = fb.chord("G")
    assert g.string_names == ("e", "B", "G", "D", "A", "E")
    assert g.positions == (3, 0, 0, 0, 2, 3)


def test_identify_power_chord():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert chord.identify() == "C power"


def test_voice_leading_same_chord():
    c_maj = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    vl = c_maj.voice_leading(c_maj)
    total = sum(abs(v[2]) for v in vl)
    assert total == 0


def test_voice_leading_returns_tuples():
    c = Chord([Tone.from_string("C4", system="western")])
    d = Chord([Tone.from_string("D4", system="western")])
    vl = c.voice_leading(d)
    assert len(vl) == 1
    assert vl[0][2] == 2


def test_tension_c_major_low():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert chord.tension["score"] == 0.0
    assert chord.tension["tritones"] == 0


def test_tension_g7_high():
    chord = Chord(tones=[
        Tone.from_string("G4", system="western"),
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
        Tone.from_string("F5", system="western"),
    ])
    t = chord.tension
    assert t["tritones"] == 1
    assert t["has_dominant_function"] is True
    assert t["score"] > 0.5


def test_tension_empty():
    chord = Chord(tones=[])
    assert chord.tension["score"] == 0.0


def test_chord_transpose():
    c_maj = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    g_maj = c_maj.transpose(7)
    assert g_maj.identify() == "G major"


def test_chord_transpose_preserves_quality():
    am = Chord(tones=[
        Tone.from_string("A4", system="western"),
        Tone.from_string("C5", system="western"),
        Tone.from_string("E5", system="western"),
    ])
    dm = am.transpose(5)
    assert dm.identify() == "D minor"


def test_chord_transpose_negative():
    g_maj = Chord(tones=[
        Tone.from_string("G4", system="western"),
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
    ])
    c_maj = g_maj.transpose(-7)
    assert c_maj.identify() == "C major"


def test_chord_root():
    c_maj = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert c_maj.root.name == "C"


def test_chord_quality():
    c_maj = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert c_maj.quality == "major"


def test_chord_quality_minor():
    am = Chord(tones=[
        Tone.from_string("A4", system="western"),
        Tone.from_string("C5", system="western"),
        Tone.from_string("E5", system="western"),
    ])
    assert am.quality == "minor"


def test_chord_root_unknown():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("D4", system="western"),
    ])
    assert chord.root is None
    assert chord.quality is None


def test_chord_inversion_0():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    inv0 = c.inversion(0)
    assert [t.full_name for t in inv0] == ["C4", "E4", "G4"]


def test_chord_inversion_1():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    inv1 = c.inversion(1)
    assert inv1.tones[0].name == "E"
    assert inv1.tones[-1].name == "C"
    assert inv1.tones[-1].octave == 5


def test_chord_inversion_2():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    inv2 = c.inversion(2)
    assert inv2.tones[0].name == "G"
    assert inv2.tones[0].octave == 4


def test_chord_inversion_preserves_identity():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert c.inversion(1).identify() == "C major"
    assert c.inversion(2).identify() == "C major"


def test_key_chords():
    k = Key("C", "major")
    assert k.chords == [
        "C major", "D minor", "E minor", "F major",
        "G major", "A minor", "B diminished",
    ]


def test_key_seventh_chords():
    k = Key("C", "major")
    sevenths = k.seventh_chords
    assert sevenths[0] == "C major 7th"
    assert sevenths[4] == "G dominant 7th"


def test_chord_from_name_c():
    c = Chord.from_name("C")
    assert c.identify() == "C major"


def test_chord_from_name_am7():
    am7 = Chord.from_name("Am7")
    assert am7.identify() == "A minor 7th"


def test_chord_from_name_g7():
    g7 = Chord.from_name("G7")
    assert g7.identify() == "G dominant 7th"


def test_chord_from_name_unknown_raises():
    with pytest.raises(ValueError):
        Chord.from_name("Xmaj13")


def test_chord_str():
    c = Chord.from_name("C")
    assert str(c) == "C major"


def test_chord_from_tones():
    c = Chord.from_tones("C", "E", "G")
    assert c.identify() == "C major"


def test_chord_from_tones_minor():
    am = Chord.from_tones("A", "C", "E")
    assert am.identify() == "A minor"


def test_chord_from_tones_octave():
    c = Chord.from_tones("C", "E", "G", octave=3)
    assert c.tones[0].octave == 3


def test_chord_add():
    c = Chord.from_tones("C", "E", "G")
    bass = Chord.from_tones("G", octave=2)
    merged = c + bass
    assert len(merged) == 4


def test_chord_add_preserves_tones():
    a = Chord.from_tones("C", "E")
    b = Chord.from_tones("G", "B")
    merged = a + b
    names = [t.name for t in merged]
    assert "C" in names and "G" in names


def test_tritone_sub():
    g7 = Chord.from_name("G7")
    sub = g7.tritone_sub()
    assert sub.identify() == "C# dominant 7th"


def test_tritone_sub_is_6_semitones():
    c = Chord.from_tones("C", "E", "G")
    sub = c.tritone_sub()
    assert sub.root.name == "F#"


def test_chord_from_intervals_major():
    assert Chord.from_intervals("C", 4, 7).identify() == "C major"


def test_chord_from_intervals_dom7():
    assert Chord.from_intervals("G", 4, 7, 10).identify() == "G dominant 7th"


def test_chord_add_tone():
    c = Chord.from_tones("C", "E", "G")
    cmaj7 = c.add_tone(Tone("B", octave=4))
    assert cmaj7.identify() == "C major 7th"


def test_chord_remove_tone():
    cmaj7 = Chord.from_name("Cmaj7")
    c = cmaj7.remove_tone("B")
    assert c.identify() == "C major"


def test_borrowed_chords():
    borrowed = Key("C", "major").borrowed_chords
    assert len(borrowed) > 0


def test_chord_repr_unidentified():
    """Chord with no known pattern should show raw tones in repr."""
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("D4", system="western"),
    ])
    assert "tones=" in repr(c)


def test_chord_str_unidentified():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("D4", system="western"),
    ])
    assert "C4" in str(c)


def test_chord_add_not_implemented():
    c = Chord.from_tones("C", "E", "G")
    assert c.__add__("not a chord") is NotImplemented


def test_chord_identify_returns_none_for_unknown():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("C#4", system="western"),
        Tone.from_string("D4", system="western"),
    ])
    assert c.identify() is None


def test_chord_voice_leading_different_sizes():
    """Voice leading should pad shorter chord."""
    c3 = Chord.from_tones("C", "E", "G")
    c4 = Chord.from_intervals("C", 4, 7, 10)
    vl = c3.voice_leading(c4)
    assert len(vl) == 4  # padded to match


def test_chord_analyze_with_tone_key():
    """analyze() should accept a Tone as key_tonic."""
    c = Chord.from_tones("C", "E", "G")
    key_tone = Tone.from_string("C4", system="western")
    assert c.analyze(key_tone) == "I"


def test_chord_analyze_unknown_chord():
    c = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("D4", system="western"),
    ])
    assert c.analyze("C") is None


def test_chord_analyze_diminished():
    b_dim = Chord.from_intervals("B", 3, 6)
    result = b_dim.analyze("C")
    assert "dim" in result


def test_chord_analyze_augmented():
    c_aug = Chord.from_intervals("C", 4, 8)
    result = c_aug.analyze("C")
    assert "+" in result


def test_chord_analyze_9th():
    c9 = Chord.from_intervals("C", 2, 4, 7, 10)
    result = c9.analyze("C")
    assert "9" in result


def test_key_borrowed_chords_minor():
    """Minor key should borrow from parallel major."""
    borrowed = Key("A", "minor").borrowed_chords
    assert len(borrowed) > 0


def test_flat_chord_from_tones():
    chord = Chord.from_tones("Db", "F", "Ab")
    assert chord.identify() == "Db major"


def test_flat_chord_from_tones_minor():
    chord = Chord.from_tones("Bb", "Db", "F")
    assert chord.identify() == "Bb minor"


def test_flat_chord_from_tones_seventh():
    chord = Chord.from_tones("Eb", "G", "Bb", "Db")
    assert chord.identify() == "Eb dominant 7th"


def test_cli_chord(capsys):
    from pytheory.cli import cmd_chord
    import argparse
    args = argparse.Namespace(notes=["C", "E", "G"])
    cmd_chord(args)
    out = capsys.readouterr().out
    assert "C major" in out
    assert "Harmony" in out
    assert "Tension" in out


@needs_portaudio
def test_play_render_chord():
    from pytheory.play import _render, Synth
    chord = Chord.from_tones("C", "E", "G")
    samples = _render(chord, synth=Synth.SINE, t=200)
    assert len(samples) > 0


@needs_portaudio
def test_play_save_chord(tmp_path):
    from pytheory.play import save
    path = tmp_path / "chord.wav"
    chord = Chord.from_tones("C", "E", "G")
    save(chord, str(path), t=200)
    assert path.exists()


def test_chord_symbol_major():
    c = Chord.from_tones("C", "E", "G")
    assert c.symbol == "C"


def test_chord_symbol_minor():
    c = Chord.from_tones("A", "C", "E")
    assert c.symbol == "Am"


def test_chord_symbol_dominant_7th():
    c = Chord.from_intervals("G", 4, 7, 10)
    assert c.symbol == "G7"


def test_chord_symbol_major_7th():
    c = Chord.from_intervals("C", 4, 7, 11)
    assert c.symbol == "Cmaj7"


def test_chord_symbol_minor_7th():
    c = Chord.from_intervals("D", 3, 7, 10)
    assert c.symbol == "Dm7"


def test_chord_symbol_diminished():
    c = Chord.from_intervals("B", 3, 6)
    assert c.symbol == "Bdim"


def test_chord_symbol_augmented():
    c = Chord.from_intervals("C", 4, 8)
    assert c.symbol == "Caug"


def test_chord_symbol_sus2():
    c = Chord.from_intervals("C", 2, 7)
    assert c.symbol == "Csus2"


def test_chord_symbol_sus4():
    c = Chord.from_intervals("C", 5, 7)
    assert c.symbol == "Csus4"


def test_chord_symbol_power():
    c = Chord.from_intervals("C", 7)
    assert c.symbol == "C5"


def test_chord_symbol_half_diminished():
    c = Chord.from_intervals("B", 3, 6, 10)
    assert c.symbol == "Bm7b5"


def test_chord_symbol_dim7():
    c = Chord.from_intervals("B", 3, 6, 9)
    assert c.symbol == "Bdim7"


def test_chord_symbol_unidentifiable():
    c = Chord.from_intervals("C", 1)
    assert c.symbol is None


def test_common_progressions_chords_are_correct():
    key = Key("G", "major")
    progs = key.common_progressions()
    chords = progs["I-IV-V-I"]
    symbols = [c.symbol for c in chords]
    assert symbols == ["G", "C", "D", "G"]


def test_pivot_chords_closely_related():
    c = Key("C", "major")
    g = Key("G", "major")
    pivots = c.pivot_chords(g)
    assert len(pivots) > 0
    assert "G major" in pivots
    assert "E minor" in pivots


def test_pivot_chords_same_key():
    c = Key("C", "major")
    pivots = c.pivot_chords(c)
    assert set(pivots) == set(c.chords)


def test_pivot_chords_distant_keys():
    c = Key("C", "major")
    fs = Key("F#", "major")
    pivots = c.pivot_chords(fs)
    assert len(pivots) < len(c.chords)


def test_suggest_next_returns_chords():
    key = Key("G", "major")
    for i in range(7):
        chord = key.triad(i)
        suggestions = key.suggest_next(chord)
        assert len(suggestions) > 0
        for s in suggestions:
            assert s.identify() is not None


def test_slash_chord():
    c = Chord.from_symbol("C")
    c_over_g = c.slash("G")
    assert len(c_over_g.tones) == 4
    assert c_over_g.tones[0].name == "G"


def test_slash_chord_custom_octave():
    c = Chord.from_symbol("C")
    c_over_g2 = c.slash("G", octave=2)
    assert c_over_g2.tones[0].octave == 2


def test_close_voicing_c_major():
    """Close voicing packs tones within one octave."""
    chord = Chord.from_symbol("C")
    inv = chord.inversion(1)  # E4, G4, C5
    closed = inv.close_voicing()
    # Should be identifiable as C major
    assert closed.identify() == "C major"
    # All tones within one octave of root
    root = closed.tones[0]
    for t in closed.tones[1:]:
        diff = abs(t - root)
        assert diff <= 12


def test_close_voicing_seventh():
    chord = Chord.from_symbol("Cmaj7").inversion(2)
    closed = chord.close_voicing()
    assert closed.identify() == "C major 7th"


def test_open_voicing_c_major():
    chord = Chord.from_symbol("Cmaj7")
    opened = chord.open_voicing()
    assert len(opened.tones) == 4
    # The spread should be wider than close voicing for 4+ tones
    closed = chord.close_voicing()
    close_span = abs(closed.tones[-1] - closed.tones[0])
    open_span = max(t.pitch() for t in opened.tones) - min(t.pitch() for t in opened.tones)
    close_span_hz = max(t.pitch() for t in closed.tones) - min(t.pitch() for t in closed.tones)
    assert open_span > close_span_hz


def test_open_voicing_seventh():
    chord = Chord.from_symbol("Cmaj7")
    opened = chord.open_voicing()
    assert len(opened.tones) == 4


def test_drop2_voicing():
    chord = Chord.from_symbol("Cmaj7")
    d2 = chord.drop2()
    assert len(d2.tones) == 4
    # The lowest tone should be below the original root
    assert d2.tones[0] < chord.tones[0]


def test_drop2_identifies_same():
    chord = Chord.from_symbol("Cmaj7")
    d2 = chord.drop2()
    assert d2.identify() == "C major 7th"


def test_drop3_voicing():
    chord = Chord.from_symbol("Cmaj7")
    d3 = chord.drop3()
    assert len(d3.tones) == 4
    # The lowest tone should be below the original root
    assert d3.tones[0] < chord.tones[0]


def test_drop3_identifies_same():
    chord = Chord.from_symbol("Cmaj7")
    d3 = chord.drop3()
    assert d3.identify() == "C major 7th"


def test_drop2_small_chord():
    """Drop2 on a single-tone chord returns it unchanged."""
    chord = Chord(tones=[Tone.from_string("C4", system="western")])
    d2 = chord.drop2()
    assert len(d2.tones) == 1


def test_modulation_path_returns_chords():
    path = Key("C", "major").modulation_path(Key("F", "major"))
    for chord in path:
        assert isinstance(chord, Chord)


def test_extensions_c_major_triad():
    chord = Chord.from_symbol("C")
    exts = chord.extensions()
    ext_names = [t.name for t in exts]
    # 9th (D) and 13th (A) should be available; 11th (F) is avoid note on major
    assert "D" in ext_names
    assert "A" in ext_names


def test_extensions_returns_tones():
    chord = Chord.from_symbol("C")
    exts = chord.extensions()
    for t in exts:
        assert isinstance(t, Tone)


def test_extensions_with_scale():
    scale = TonedScale(tonic="C4")["major"]
    chord = Chord.from_symbol("C")
    exts = chord.extensions(scale=scale)
    ext_names = [t.name for t in exts]
    # D, F, A are all in C major scale
    assert "D" in ext_names
    assert "A" in ext_names


def test_extensions_minor_chord():
    chord = Chord.from_symbol("Am")
    exts = chord.extensions()
    # Should return some extensions
    assert len(exts) >= 1


def test_extensions_empty_chord():
    chord = Chord(tones=[])
    exts = chord.extensions()
    assert exts == []


def test_arpeggio_basic():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.arpeggio(Chord.from_symbol("C"), bars=1, pattern="up",
                  division=Duration.SIXTEENTH)
    # 1 bar of 16ths = 16 notes
    assert len(lead) == 16


def test_arpeggio_patterns():
    from pytheory import Score, Duration
    for pat in ["up", "down", "updown", "downup", "random"]:
        score = Score("4/4", bpm=120)
        lead = score.part(f"lead_{pat}")
        lead.arpeggio(Chord.from_symbol("Am"), bars=1, pattern=pat)
        assert len(lead) > 0


def test_arpeggio_octaves():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.arpeggio(Chord.from_symbol("C"), bars=1, octaves=2,
                  division=Duration.EIGHTH)
    # C major = 3 tones, 2 octaves = 6 tones in the cycle
    assert len(lead) == 8  # 1 bar of 8ths


def test_arpeggio_string_chord():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.arpeggio("Dm7", bars=1)
    assert len(lead) > 0


def test_arpeggio_chaining():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    result = lead.arpeggio("C", bars=1).arpeggio("Am", bars=1)
    assert result is lead
    assert lead.total_beats == 8.0


def test_arpeggio_with_legato():
    from pytheory import Score, Duration
    from pytheory.play import render_score
    score = Score("4/4", bpm=120)
    lead = score.part("lead", synth="saw", legato=True, glide=0.03)
    lead.arpeggio("Cm", bars=2, pattern="updown", octaves=2)
    buf = render_score(score)
    assert len(buf) > 0


def test_arpeggio_updown_length():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.arpeggio(Chord.from_symbol("Am"), bars=2, pattern="updown",
                  division=Duration.EIGHTH)
    # 2 bars of 8ths = 16 notes
    assert len(lead) == 16


def test_arpeggio_velocity():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.arpeggio("Cm", bars=1, velocity=75)
    for n in lead.notes:
        assert n.velocity == 75


def test_repl_cmd_add_chord():
    from pytheory.repl import Session, cmd_add
    s = Session()
    cmd_add(s, ["Am", "4"])
    assert len(s.current_part.notes) == 1


def test_repl_chords(capsys):
    from pytheory.repl import Session, cmd_key, cmd_chords
    s = Session()
    cmd_key(s, ["C"])
    cmd_chords(s, [])
    out = capsys.readouterr().out
    assert "C major" in out
    assert "D minor" in out


def test_figured_bass_root_position():
    chord = Chord.from_tones("C", "E", "G")
    assert chord.figured_bass == ""


def test_figured_bass_first_inversion():
    # E in bass: first inversion of C major
    chord = Chord.from_symbol("C").inversion(1)
    assert chord.figured_bass == "6"


def test_figured_bass_second_inversion():
    # G in bass: second inversion of C major
    chord = Chord.from_symbol("C").inversion(2)
    assert chord.figured_bass == "6/4"


def test_figured_bass_seventh_root():
    # G7 in root position: G is the lowest note
    chord = Chord.from_symbol("G7", octave=4)
    assert chord.figured_bass == "7"


def test_figured_bass_seventh_first_inv():
    # First inversion of G7: B in bass
    chord = Chord.from_symbol("G7").inversion(1)
    assert chord.figured_bass == "6/5"


def test_figured_bass_seventh_second_inv():
    chord = Chord.from_symbol("G7").inversion(2)
    assert chord.figured_bass == "4/3"


def test_figured_bass_seventh_third_inv():
    chord = Chord.from_symbol("G7").inversion(3)
    assert chord.figured_bass == "2"


def test_analyze_figured():
    # V7 in root position
    chord = Chord.from_symbol("G7")
    result = chord.analyze_figured("C")
    assert result == "V7"


def test_analyze_figured_with_inversion():
    # V in first inversion
    chord = Chord.from_symbol("G").inversion(1)
    result = chord.analyze_figured("C")
    assert result == "V6"


def test_forte_number_triad():
    chord = Chord.from_tones("C", "E", "G")
    assert chord.forte_number == "3-11"


def test_forte_number_minor_triad():
    chord = Chord.from_tones("A", "C", "E")
    assert chord.forte_number == "3-11"


def test_forte_number_dom7():
    chord = Chord.from_symbol("G7")
    assert chord.forte_number == "4-27"


def test_forte_number_augmented():
    chord = Chord.from_tones("C", "E", "G#")
    assert chord.forte_number == "3-12"


def test_forte_number_diminished7():
    chord = Chord.from_tones("B", "D", "F", "Ab")
    assert chord.forte_number == "4-28"


# ── Pitch-class-set toolkit ────────────────────────────────────────────

def test_interval_vector_major_and_minor_triad_match():
    # Major and minor triads are inversions — identical interval content.
    assert Chord.from_tones("C", "E", "G").interval_vector == (0, 0, 1, 1, 1, 0)
    assert Chord.from_tones("A", "C", "E").interval_vector == (0, 0, 1, 1, 1, 0)


def test_interval_vector_symmetrical_sets():
    dim7 = Chord.from_midi_message(60, 63, 66, 69)   # fully-diminished 7th
    aug = Chord.from_midi_message(60, 64, 68)        # augmented triad
    assert dim7.interval_vector == (0, 0, 4, 0, 0, 2)
    assert aug.interval_vector == (0, 0, 0, 3, 0, 0)


def test_complement_fills_the_aggregate():
    c = Chord.from_tones("C", "E", "G")
    comp = c.complement
    assert c.pitch_classes | comp.pitch_classes == set(range(12))
    assert c.pitch_classes & comp.pitch_classes == set()


def test_aggregate_has_no_complement():
    aggregate = Chord.from_midi_message(*range(60, 72))
    with pytest.raises(ValueError, match="aggregate"):
        aggregate.complement


def test_transposition_vs_inversion_equivalence():
    cmaj = Chord.from_tones("C", "E", "G")
    gmaj = Chord.from_tones("G", "B", "D")
    cmin = Chord.from_tones("C", "Eb", "G")
    # Major triads are transpositions of one another...
    assert cmaj.is_transposition_of(gmaj)
    # ...but major and minor are inversions, not transpositions.
    assert not cmaj.is_transposition_of(cmin)
    # Both relations live in the same set class (TnI / same Forte number).
    assert cmaj.is_set_class_equivalent(cmin)
    assert cmaj.is_set_class_equivalent(gmaj)


def test_z_related_all_interval_tetrachords():
    z15 = Chord.from_midi_message(60, 61, 64, 66)   # 0,1,4,6
    z29 = Chord.from_midi_message(60, 61, 63, 67)   # 0,1,3,7
    assert z15.interval_vector == z29.interval_vector == (1, 1, 1, 1, 1, 1)
    assert z15.is_z_related(z29)
    assert not z15.is_z_related(z15)                # same set class, not Z


def test_literal_subset_superset():
    triad = Chord.from_tones("C", "E", "G")
    seventh = Chord.from_symbol("Cmaj7")
    assert triad.is_subset_of(seventh)
    assert seventh.is_superset_of(triad)
    assert not seventh.is_subset_of(triad)


# ── Reharmonization ────────────────────────────────────────────────────

def test_reharmonize_techniques():
    from pytheory import reharmonize
    subs = reharmonize(Chord.from_symbol("G7"), "C")
    techniques = {s["technique"] for s in subs}
    assert "tritone substitution" in techniques
    assert "diatonic substitution" in techniques
    assert "negative harmony" in techniques
    # The tritone sub of G7 is Db7 (= C# dominant 7th).
    tts = next(s for s in subs if s["technique"] == "tritone substitution")
    assert "dominant 7th" in tts["chord"].identify()


def test_reharmonize_excludes_same_root_simplifications():
    from pytheory import reharmonize
    # G major (G7 minus the 7th) must not be offered as a "substitution".
    subs = reharmonize(Chord.from_symbol("G7"), "C")
    roots = {s["chord"].root.name for s in subs
             if s["technique"] == "diatonic substitution"}
    assert "G" not in roots


def test_reharmonize_non_dominant_has_no_tritone_sub():
    from pytheory import reharmonize
    subs = reharmonize(Chord.from_symbol("C"), "C")   # tonic triad
    assert all(s["technique"] != "tritone substitution" for s in subs)
    assert any(s["technique"] == "negative harmony" for s in subs)


# ── Chord-scale theory ─────────────────────────────────────────────────

def test_chord_scales_from_quality():
    from pytheory import chord_scales
    assert chord_scales(Chord.from_symbol("G7")) == ["mixolydian"]
    assert chord_scales(Chord.from_symbol("Cmaj7")) == ["ionian", "lydian"]
    assert chord_scales(Chord.from_symbol("Cm7")) == ["dorian", "aeolian", "phrygian"]
    assert chord_scales(Chord.from_symbol("Cm7b5")) == ["locrian"]


def test_chord_scales_prefer_diatonic_mode_in_key():
    from pytheory import chord_scales
    # In C major, each diatonic seventh resolves to its church mode first.
    assert chord_scales(Chord.from_symbol("Em7"), key="C")[0] == "phrygian"
    assert chord_scales(Chord.from_symbol("Dm7"), key="C")[0] == "dorian"
    assert chord_scales(Chord.from_symbol("Fmaj7"), key="C")[0] == "lydian"


def test_avoid_notes():
    from pytheory import avoid_notes
    # The 4th is a half-step above the 3rd -> avoid note.
    assert [t.name for t in avoid_notes(Chord.from_symbol("Cmaj7"))] == ["F"]
    assert [t.name for t in avoid_notes(Chord.from_symbol("G7"))] == ["C"]
    # Dorian over a minor 7th has no avoid note.
    assert avoid_notes(Chord.from_symbol("Dm7")) == []


def test_chord_scale_notes():
    from pytheory import chord_scale_notes
    notes = [t.name for t in chord_scale_notes(Chord.from_symbol("Cmaj7"))]
    assert notes == ["C", "D", "E", "F", "G", "A", "B"]   # one octave, no repeat


# ── Non-chord-tone analysis ────────────────────────────────────────────

def _nct_types(melody, chords):
    from pytheory import analyze_non_chord_tones, Tone
    notes = [Tone.from_string(n) for n in melody]
    return [r["type"] for r in analyze_non_chord_tones(notes, chords)]


def test_passing_and_neighbor_tones():
    C = Chord.from_name("C")
    assert _nct_types(["C4", "D4", "E4"], C) == ["chord tone", "passing", "chord tone"]
    assert _nct_types(["C4", "D4", "C4"], C) == ["chord tone", "upper neighbor", "chord tone"]
    assert _nct_types(["E4", "D4", "E4"], C) == ["chord tone", "lower neighbor", "chord tone"]


def test_appoggiatura_and_escape_tone():
    C = Chord.from_name("C")
    assert _nct_types(["C4", "F4", "E4"], C)[1] == "appoggiatura"   # leap in, step out
    assert _nct_types(["C4", "D4", "G4"], C)[1] == "escape tone"    # step in, leap out


def test_suspension_and_anticipation():
    C, G = Chord.from_name("C"), Chord.from_name("G")
    # C held from a C chord into a G chord, resolving down to B.
    assert _nct_types(["C4", "C4", "B3"], [C, G, G])[1] == "suspension"
    # B steps to C, anticipating the coming C chord.
    assert _nct_types(["B3", "C4", "C4"], [G, G, C])[1] == "anticipation"


def test_nct_requires_one_chord_per_note_or_single():
    from pytheory import analyze_non_chord_tones, Tone
    notes = [Tone.from_string(n) for n in ("C4", "D4")]
    with pytest.raises(ValueError, match="one chord per"):
        analyze_non_chord_tones(notes, [Chord.from_name("C")])  # wrong length


# ── Voice-leading checker ──────────────────────────────────────────────

def test_parallel_fifths_detected():
    from pytheory import check_voice_leading
    a = Chord.from_midi_message(48, 55)        # C3 + G3 (a fifth)
    b = Chord.from_midi_message(50, 57)        # D3 + A3 (a fifth), both up
    issues = check_voice_leading([a, b])
    assert [i["type"] for i in issues] == ["parallel fifths"]
    assert issues[0]["chords"] == (0, 1)
    assert issues[0]["voices"] == (0, 1)


def test_parallel_octaves_detected():
    from pytheory import check_voice_leading
    a = Chord.from_midi_message(48, 60)        # C3 + C4
    b = Chord.from_midi_message(50, 62)        # D3 + D4
    assert [i["type"] for i in check_voice_leading([a, b])] == ["parallel octaves"]


def test_contrary_and_oblique_motion_is_clean():
    from pytheory import check_voice_leading
    # Contrary motion in the outer voices, inner voice held — textbook clean.
    one = Chord.from_midi_message(48, 55, 64, 72)
    two = Chord.from_midi_message(50, 55, 62, 71)
    assert check_voice_leading([one, two]) == []


def test_voice_crossing_detected():
    from pytheory import check_voice_leading
    a = Chord.from_midi_message(48, 52, 55)
    b = Chord.from_midi_message(48, 60, 55)    # voice 1 (60) ends above voice 2 (55)
    issues = check_voice_leading([a, b])
    assert any(i["type"] == "voice crossing" and i["voices"] == (1, 2)
               for i in issues)


def test_satb_voice_labels():
    from pytheory import check_voice_leading
    a = Chord.from_midi_message(48, 55, 64, 72)   # 4 voices -> SATB names
    b = Chord.from_midi_message(50, 57, 66, 74)
    issues = check_voice_leading([a, b])
    assert any("bass" in i["description"] and "tenor" in i["description"]
               for i in issues)


# ── Neo-Riemannian transformations ─────────────────────────────────────

def test_plr_basic_transformations():
    c = Chord.from_name("C")
    assert c.parallel().identify() == "C minor"             # P
    assert c.relative().identify() == "A minor"             # R
    assert c.leading_tone_exchange().identify() == "E minor"  # L
    # And from a minor triad:
    assert Chord.from_name("Am").relative().identify() == "C major"
    assert Chord.from_name("Am").leading_tone_exchange().identify() == "F major"


def test_plr_are_involutions():
    c = Chord.from_name("C")
    for op in ("parallel", "relative", "leading_tone_exchange"):
        twice = getattr(getattr(c, op)(), op)()
        assert twice.identify() == "C major"


def test_transform_sequence():
    assert Chord.from_name("C").transform("LP").identify() == "E major"
    assert Chord.from_name("C").transform("R").identify() == "A minor"
    with pytest.raises(ValueError, match="Unknown transformation"):
        Chord.from_name("C").transform("X")


def test_tonnetz_path_is_shortest_and_correct():
    c = Chord.from_name("C")
    assert c.tonnetz_path(c) == ""                       # identity
    assert c.tonnetz_path(Chord.from_name("Am")) == "R"  # one step
    # Whatever the path, applying it must reach the target.
    for target in ("E", "Gm", "Db", "Ab"):
        path = c.tonnetz_path(Chord.from_name(target))
        assert c.transform(path).identify() == Chord.from_name(target).identify()


def test_neo_riemannian_requires_a_triad():
    with pytest.raises(ValueError, match="major or minor triad"):
        Chord.from_symbol("C7").parallel()


def test_from_symbol_slash_chord_inversion():
    c = Chord.from_symbol("C/E")
    assert [t.full_name for t in c.tones] == ["E4", "G4", "C5"]


def test_from_symbol_slash_chord_second_inversion():
    c = Chord.from_symbol("C/G")
    assert [t.full_name for t in c.tones] == ["G4", "C5", "E5"]


def test_from_symbol_slash_chord_foreign_bass():
    c = Chord.from_symbol("C/D")
    assert [t.full_name for t in c.tones] == ["D3", "C4", "E4", "G4"]


def test_from_symbol_slash_chord_seventh():
    c = Chord.from_symbol("Am7/G")
    assert c.tones[0].name == "G"
    assert c.tones[0].midi == min(t.midi for t in c.tones)
    assert {t.name for t in c.tones} == {"A", "C", "E", "G"}
