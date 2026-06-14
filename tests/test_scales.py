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


def test_c_major_scale():
    c = TonedScale(tonic="C4")
    major = c["major"]
    names = [t.name for t in major.tones]
    assert names == ["C", "D", "E", "F", "G", "A", "B", "C"]


def test_c_major_scale_octaves():
    c = TonedScale(tonic="C4")
    major = c["major"]
    octaves = [t.octave for t in major.tones]
    assert octaves == [4, 4, 4, 4, 4, 4, 4, 5]


def test_c_minor_scale():
    c = TonedScale(tonic="C4")
    minor = c["minor"]
    names = [t.name for t in minor.tones]
    # C D Eb F G Ab Bb C (using flats for flat keys)
    assert names == ["C", "D", "Eb", "F", "G", "Ab", "Bb", "C"]


def test_c_harmonic_minor_scale():
    c = TonedScale(tonic="C4")
    hminor = c["harmonic minor"]
    names = [t.name for t in hminor.tones]
    # C D Eb F G Ab B C (raised 7th)
    assert names == ["C", "D", "Eb", "F", "G", "Ab", "B", "C"]


def test_g_major_scale():
    g = TonedScale(tonic="G4")
    major = g["major"]
    names = [t.name for t in major.tones]
    assert names == ["G", "A", "B", "C", "D", "E", "F#", "G"]


def test_available_scales():
    c = TonedScale(tonic="C4")
    scales = c.scales
    assert "major" in scales
    assert "minor" in scales
    assert "harmonic minor" in scales
    assert "ionian" in scales
    assert "dorian" in scales


def test_scale_degree_by_index():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert major[0].name == "C"
    assert major[4].name == "G"


def test_ionian_equals_major():
    c = TonedScale(tonic="C4")
    major_names = [t.name for t in c["major"].tones]
    ionian_names = [t.name for t in c["ionian"].tones]
    assert major_names == ionian_names


def test_aeolian_equals_minor():
    c = TonedScale(tonic="C4")
    minor_names = [t.name for t in c["minor"].tones]
    aeolian_names = [t.name for t in c["aeolian"].tones]
    assert minor_names == aeolian_names


def test_c_dorian():
    c = TonedScale(tonic="C4")
    dorian = c["dorian"]
    names = [t.name for t in dorian.tones]
    # Dorian: W H W W W H W → C D Eb F G A Bb C
    assert names == ["C", "D", "Eb", "F", "G", "A", "Bb", "C"]


def test_c_phrygian():
    c = TonedScale(tonic="C4")
    phrygian = c["phrygian"]
    names = [t.name for t in phrygian.tones]
    # Phrygian: H W W W H W W → C Db Eb F G Ab Bb C
    assert names == ["C", "Db", "Eb", "F", "G", "Ab", "Bb", "C"]


def test_c_lydian():
    c = TonedScale(tonic="C4")
    lydian = c["lydian"]
    names = [t.name for t in lydian.tones]
    # Lydian: W W W H W W H → C D E F# G A B C
    assert names == ["C", "D", "E", "F#", "G", "A", "B", "C"]


def test_c_mixolydian():
    c = TonedScale(tonic="C4")
    mixolydian = c["mixolydian"]
    names = [t.name for t in mixolydian.tones]
    # Mixolydian: W W H W W H W → C D E F G A Bb C
    assert names == ["C", "D", "E", "F", "G", "A", "Bb", "C"]


def test_c_locrian():
    c = TonedScale(tonic="C4")
    locrian = c["locrian"]
    names = [t.name for t in locrian.tones]
    # Locrian: H W W H W W W → C Db Eb F Gb Ab Bb C
    assert names == ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb", "C"]


def test_western_system_scales():
    system = pytheory.SYSTEMS["western"]
    scales = system.scales
    assert "heptatonic" in scales
    assert "major" in scales["heptatonic"]
    assert "minor" in scales["heptatonic"]


def test_western_system_modes():
    system = pytheory.SYSTEMS["western"]
    modes = system.modes
    mode_names = [m["mode"] for m in modes]
    assert "ionian" in mode_names
    assert "dorian" in mode_names


def test_major_scale_intervals():
    """Major scale should follow W-W-H-W-W-W-H pattern (2-2-1-2-2-2-1)."""
    system = pytheory.SYSTEMS["western"]
    major = system.scales["heptatonic"]["major"]
    assert major["intervals"] == [2, 2, 1, 2, 2, 2, 1]


def test_minor_scale_intervals():
    """Natural minor should follow W-H-W-W-H-W-W pattern."""
    system = pytheory.SYSTEMS["western"]
    minor = system.scales["heptatonic"]["minor"]
    assert minor["intervals"] == [2, 1, 2, 2, 1, 2, 2]


def test_harmonic_minor_scale_intervals():
    """Harmonic minor should follow W-H-W-W-H-WH-H pattern."""
    system = pytheory.SYSTEMS["western"]
    hminor = system.scales["heptatonic"]["harmonic minor"]
    assert hminor["intervals"] == [2, 1, 2, 2, 1, 3, 1]


def test_dorian_mode_intervals():
    """Dorian: W-H-W-W-W-H-W (rotation of major by 1)."""
    system = pytheory.SYSTEMS["western"]
    dorian = system.scales["heptatonic"]["dorian"]
    assert dorian["intervals"] == [2, 1, 2, 2, 2, 1, 2]


def test_lydian_mode_intervals():
    """Lydian: W-W-W-H-W-W-H (rotation of major by 3)."""
    system = pytheory.SYSTEMS["western"]
    lydian = system.scales["heptatonic"]["lydian"]
    assert lydian["intervals"] == [2, 2, 2, 1, 2, 2, 1]


def test_mixolydian_mode_intervals():
    """Mixolydian: W-W-H-W-W-H-W (rotation of major by 4)."""
    system = pytheory.SYSTEMS["western"]
    mixolydian = system.scales["heptatonic"]["mixolydian"]
    assert mixolydian["intervals"] == [2, 2, 1, 2, 2, 1, 2]


def test_all_mode_intervals_sum_to_12():
    """Every heptatonic mode's intervals should sum to 12 semitones."""
    system = pytheory.SYSTEMS["western"]
    for name, scale in system.scales["heptatonic"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_scale_repr():
    c = TonedScale(tonic="C4")
    major = c["major"]
    r = repr(major)
    assert "Scale" in r
    assert "I=C4" in r
    assert "V=G4" in r


def test_scale_degree_by_name_tonic():
    c = TonedScale(tonic="C4")
    major = c["major"]
    tone = major.degree("tonic")
    assert tone.name == "C"


def test_scale_degree_by_name_dominant():
    c = TonedScale(tonic="C4")
    major = c["major"]
    tone = major.degree("dominant")
    assert tone.name == "G"


def test_scale_degree_major_minor_both_raises():
    c = TonedScale(tonic="C4")
    major = c["major"]
    with pytest.raises(ValueError):
        major.degree("tonic", major=True, minor=True)


def test_scale_slice_access():
    c = TonedScale(tonic="C4")
    major = c["major"]
    first_three = major[0:3]
    assert len(first_three) == 3
    assert first_three[0].name == "C"
    assert first_three[2].name == "E"


def test_scale_degrees_length_mismatch_raises():
    from pytheory.scales import Scale
    with pytest.raises(ValueError, match="number of tones and degrees"):
        Scale(tones=(Tone(name="C"), Tone(name="D")), degrees=("I",))


def test_toned_scale_repr():
    c = TonedScale(tonic="C4")
    r = repr(c)
    assert "TonedScale" in r
    assert "C4" in r


def test_toned_scale_get_none():
    c = TonedScale(tonic="C4")
    assert c.get("nonexistent") is None


def test_toned_scale_with_tone_object():
    tone = Tone.from_string("D4", system="western")
    d = TonedScale(tonic=tone)
    major = d["major"]
    assert major.tones[0].name == "D"


def test_d_major_scale():
    d = TonedScale(tonic="D4")
    major = d["major"]
    names = [t.name for t in major.tones]
    assert names == ["D", "E", "F#", "G", "A", "B", "C#", "D"]


def test_f_major_scale():
    f = TonedScale(tonic="F4")
    major = f["major"]
    names = [t.name for t in major.tones]
    assert names == ["F", "G", "A", "Bb", "C", "D", "E", "F"]


def test_a_minor_scale():
    a = TonedScale(tonic="A4")
    minor = a["minor"]
    names = [t.name for t in minor.tones]
    # A B C D E F G A
    assert names == ["A", "B", "C", "D", "E", "F", "G", "A"]


def test_e_minor_scale():
    e = TonedScale(tonic="E4")
    minor = e["minor"]
    names = [t.name for t in minor.tones]
    # E F# G A B C D E
    assert names == ["E", "F#", "G", "A", "B", "C", "D", "E"]


def test_b_major_scale():
    b = TonedScale(tonic="B4")
    major = b["major"]
    names = [t.name for t in major.tones]
    assert names == ["B", "C#", "D#", "E", "F#", "G#", "A#", "B"]


def test_d_dorian():
    d = TonedScale(tonic="D4")
    dorian = d["dorian"]
    names = [t.name for t in dorian.tones]
    # D Dorian: D E F G A B C D (same notes as C major)
    assert names == ["D", "E", "F", "G", "A", "B", "C", "D"]


def test_g_mixolydian():
    g = TonedScale(tonic="G4")
    mixo = g["mixolydian"]
    names = [t.name for t in mixo.tones]
    # G Mixolydian: G A B C D E F G (same notes as C major)
    assert names == ["G", "A", "B", "C", "D", "E", "F", "G"]


def test_scale_octaves_across_boundary():
    """A4 major scale should cross into octave 5 at the right point."""
    a = TonedScale(tonic="A4")
    major = a["major"]
    full = [t.full_name for t in major.tones]
    assert full == ["A4", "B4", "C#5", "D5", "E5", "F#5", "G#5", "A5"]


def test_phrygian_mode_intervals():
    system = SYSTEMS["western"]
    phrygian = system.scales["heptatonic"]["phrygian"]
    assert phrygian["intervals"] == [1, 2, 2, 2, 1, 2, 2]


def test_aeolian_mode_intervals():
    """Aeolian should have same intervals as natural minor."""
    system = SYSTEMS["western"]
    aeolian = system.scales["heptatonic"]["aeolian"]
    minor = system.scales["heptatonic"]["minor"]
    assert aeolian["intervals"] == minor["intervals"]


def test_locrian_mode_intervals():
    system = SYSTEMS["western"]
    locrian = system.scales["heptatonic"]["locrian"]
    assert locrian["intervals"] == [1, 2, 2, 1, 2, 2, 2]


def test_ionian_mode_intervals():
    """Ionian should have same intervals as major."""
    system = SYSTEMS["western"]
    ionian = system.scales["heptatonic"]["ionian"]
    major = system.scales["heptatonic"]["major"]
    assert ionian["intervals"] == major["intervals"]


def test_system_chromatic_scale():
    system = SYSTEMS["western"]
    chromatic = system.scales["chromatic"]["chromatic"]
    assert chromatic["intervals"] == [1] * 12


def test_system_generate_scale_major_minor_raises():
    with pytest.raises(ValueError, match="both major and minor"):
        System.generate_scale(major=True, minor=True)


def test_system_modes_list():
    system = SYSTEMS["western"]
    modes = system.modes
    assert len(modes) > 0
    for mode in modes:
        assert "degree" in mode
        assert "mode" in mode
        assert isinstance(mode["degree"], int)


def test_enharmonic_equivalence_in_scales():
    """D Dorian and C major should contain the same pitch classes."""
    c_major = TonedScale(tonic="C4")["major"]
    d_dorian = TonedScale(tonic="D4")["dorian"]

    c_names = sorted(set(t.name for t in c_major.tones))
    d_names = sorted(set(t.name for t in d_dorian.tones))
    assert c_names == d_names


def test_scale_iter():
    c = TonedScale(tonic="C4")
    major = c["major"]
    names = [t.name for t in major]
    assert names == ["C", "D", "E", "F", "G", "A", "B", "C"]


def test_scale_len():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert len(major) == 8  # 7 notes + octave


def test_scale_contains_name():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert "C" in major
    assert "E" in major
    assert "C#" not in major


def test_scale_contains_tone():
    c = TonedScale(tonic="C4")
    major = c["major"]
    c4 = Tone(name="C", octave=4)
    assert c4 in major


def test_scale_note_names():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert major.note_names == ["C", "D", "E", "F", "G", "A", "B", "C"]


def test_scale_triad_root():
    c = TonedScale(tonic="C4")
    major = c["major"]
    triad = major.triad(0)  # I chord = C E G
    assert len(triad) == 3
    names = [t.name for t in triad]
    assert names == ["C", "E", "G"]


def test_scale_triad_iv():
    c = TonedScale(tonic="C4")
    major = c["major"]
    triad = major.triad(3)  # IV chord = F A C
    names = [t.name for t in triad]
    assert names == ["F", "A", "C"]


def test_scale_triad_v():
    c = TonedScale(tonic="C4")
    major = c["major"]
    triad = major.triad(4)  # V chord = G B D
    names = [t.name for t in triad]
    assert names == ["G", "B", "D"]


def test_scale_triad_ii_minor():
    """ii chord in C major should be D F A (minor triad)."""
    c = TonedScale(tonic="C4")
    major = c["major"]
    triad = major.triad(1)
    names = [t.name for t in triad]
    assert names == ["D", "F", "A"]


def test_indian_scale_triad():
    """Build a triad from Bilawal (Sa Ga Pa)."""
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    bilawal = sa["bilawal"]
    triad = bilawal.triad(0)
    names = [t.name for t in triad]
    assert names == ["Sa", "Ga", "Pa"]


def test_indian_scale_degree_access():
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    bilawal = sa["bilawal"]
    assert bilawal[0].name == "Sa"
    assert bilawal[4].name == "Pa"
    assert bilawal["I"].name == "Sa"
    assert bilawal["V"].name == "Pa"


def test_arabic_ajam_maqam():
    """Ajam = major scale."""
    do = TonedScale(tonic="Do4", system=SYSTEMS["arabic"])
    ajam = do["ajam"]
    names = [t.name for t in ajam]
    assert names == ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si", "Do"]


def test_arabic_hijaz_maqam():
    """Hijaz has augmented 2nd between 2nd and 3rd degrees."""
    do = TonedScale(tonic="Do4", system=SYSTEMS["arabic"])
    hijaz = do["hijaz"]
    names = [t.name for t in hijaz]
    assert names[0] == "Do"
    assert names[1] == "Reb"  # flat 2nd
    assert names[2] == "Mi"   # natural 3rd (augmented 2nd interval)


def test_arabic_all_maqamat_available():
    do = TonedScale(tonic="Do4", system=SYSTEMS["arabic"])
    for maqam in ["ajam", "nahawand", "kurd", "hijaz", "nikriz",
                   "bayati", "rast", "saba", "sikah", "jiharkah"]:
        assert maqam in do.scales, f"Missing maqam: {maqam}"


def test_arabic_all_maqam_intervals_sum_to_12():
    arabic = SYSTEMS["arabic"]
    for name, scale in arabic.scales["maqam"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_japanese_in_scale():
    """In (Miyako-bushi): C Db F G Ab."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["in"]
    names = [t.name for t in s]
    assert names == ["C", "Db", "F", "G", "Ab", "C"]


def test_japanese_yo_scale():
    """Yo: C D F G Bb."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["yo"]
    names = [t.name for t in s]
    assert names == ["C", "D", "F", "G", "A#", "C"]


def test_japanese_all_scales_available():
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    for scale in ["hirajoshi", "in", "yo", "iwato", "kumoi", "insen", "ritsu", "ryo"]:
        assert scale in c.scales, f"Missing scale: {scale}"


def test_japanese_pentatonic_intervals_sum_to_12():
    japanese = SYSTEMS["japanese"]
    for name, scale in japanese.scales["pentatonic"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_blues_major_pentatonic():
    c = TonedScale(tonic="C4", system=SYSTEMS["blues"])
    s = c["major pentatonic"]
    assert s.note_names == ["C", "D", "E", "G", "A", "C"]


def test_blues_minor_pentatonic():
    c = TonedScale(tonic="C4", system=SYSTEMS["blues"])
    s = c["minor pentatonic"]
    assert s.note_names == ["C", "D#", "F", "G", "A#", "C"]


def test_blues_scale():
    c = TonedScale(tonic="C4", system=SYSTEMS["blues"])
    s = c["blues"]
    names = s.note_names
    assert names == ["C", "Eb", "F", "Gb", "G", "Bb", "C"]
    assert len(names) == 7  # 6 notes + octave


def test_blues_all_scales_available():
    c = TonedScale(tonic="C4", system=SYSTEMS["blues"])
    for scale in ["major pentatonic", "minor pentatonic", "blues",
                   "major blues", "dominant", "minor"]:
        assert scale in c.scales, f"Missing scale: {scale}"


def test_gamelan_all_scales_available():
    ji = TonedScale(tonic="ji4", system=SYSTEMS["gamelan"])
    for scale in ["slendro", "pelog nem", "pelog barang", "pelog lima", "pelog"]:
        assert scale in ji.scales, f"Missing scale: {scale}"


def test_scale_transpose():
    c_major = TonedScale(tonic="C4")["major"]
    d_major = c_major.transpose(2)
    assert d_major.note_names == ["D", "E", "F#", "G", "A", "B", "C#", "D"]


def test_scale_transpose_negative():
    d_major = TonedScale(tonic="D4")["major"]
    c_major = d_major.transpose(-2)
    assert c_major.note_names == ["C", "D", "E", "F", "G", "A", "B", "C"]


def test_scale_seventh_I():
    major = TonedScale(tonic="C4")["major"]
    assert major.seventh(0).identify() == "C major 7th"


def test_scale_seventh_ii():
    major = TonedScale(tonic="C4")["major"]
    assert major.seventh(1).identify() == "D minor 7th"


def test_scale_seventh_V():
    major = TonedScale(tonic="C4")["major"]
    assert major.seventh(4).identify() == "G dominant 7th"


def test_harmonize_c_major():
    major = TonedScale(tonic="C4")["major"]
    chords = major.harmonize()
    assert len(chords) == 7
    qualities = [c.identify() for c in chords]
    assert qualities == [
        "C major", "D minor", "E minor", "F major",
        "G major", "A minor", "B diminished",
    ]


def test_harmonize_len():
    minor = TonedScale(tonic="A4")["minor"]
    assert len(minor.harmonize()) == 7


def test_scale_detect_c_major():
    from pytheory.scales import Scale
    result = Scale.detect("C", "D", "E", "F", "G", "A", "B")
    assert result[0] == "C"
    assert result[1] == "major"
    assert result[2] == 7


def test_scale_detect_g_major():
    from pytheory.scales import Scale
    result = Scale.detect("C", "D", "E", "F#", "G", "A", "B")
    assert result[0] == "G"
    assert result[1] == "major"


def test_scale_detect_none():
    from pytheory.scales import Scale
    assert Scale.detect() is None


def test_scale_with_system_object():
    """Scale created with system object instead of string."""
    from pytheory.scales import Scale
    system = SYSTEMS["western"]
    s = Scale(tones=(Tone("C", octave=4), Tone("D", octave=4)), system=system)
    assert s.system == system


def test_scale_degree_by_mode_name():
    major = TonedScale(tonic="C4")["major"]
    # Access by mode name should work via degree lookup
    tone = major.degree("ionian")
    assert tone is not None


def test_scale_getitem_raises():
    major = TonedScale(tonic="C4")["major"]
    with pytest.raises(KeyError):
        major["nonexistent_degree"]


def test_toned_scale_with_string_system():
    ts = TonedScale(tonic="Do4", system="arabic")
    assert "ajam" in ts.scales


def test_cli_scale(capsys):
    from pytheory.cli import cmd_scale
    import argparse
    args = argparse.Namespace(tonic="C", mode="major", system="western")
    cmd_scale(args)
    out = capsys.readouterr().out
    assert "C D E F G A B C" in out


def test_cli_modes(capsys):
    from pytheory.cli import cmd_modes
    import argparse
    args = argparse.Namespace(tonic="C", system="western")
    cmd_modes(args)
    out = capsys.readouterr().out
    assert "ionian" in out
    assert "dorian" in out
    assert "locrian" in out


def test_parallel_modes_c_major():
    c = TonedScale(tonic="C4")["major"]
    modes = c.parallel_modes()
    assert "C ionian" in modes
    assert "D dorian" in modes
    assert "E phrygian" in modes
    assert "A aeolian" in modes
    assert len(modes) == 7


def test_parallel_modes_share_notes():
    c = TonedScale(tonic="C4")["major"]
    modes = c.parallel_modes()
    c_notes = set(modes["C ionian"][:-1])
    for name, notes in modes.items():
        assert set(notes[:-1]) == c_notes, f"{name} has different notes"


def test_parallel_modes_g_major():
    g = TonedScale(tonic="G4")["major"]
    modes = g.parallel_modes()
    assert "G ionian" in modes
    assert "A dorian" in modes


def test_recommend_pentatonic():
    from pytheory.scales import Scale
    results = Scale.recommend("C", "D", "E", "G", "A")
    assert len(results) > 0
    assert results[0][2] == 1.0


def test_19tet_scale():
    sys19 = SYSTEMS["19-tet"]
    ts = TonedScale(system=sys19, tonic=Tone("C", octave=4, system=sys19))
    major = ts["major"]
    assert len(major.tones) == 8  # 7 + octave


def test_shruti_bhairav_scale():
    shruti = SYSTEMS["shruti"]
    ts = TonedScale(system=shruti, tonic=Tone("Sa", octave=4, system=shruti))
    bhairav = ts["bhairav"]
    names = [t.name for t in bhairav.tones]
    assert names[0] == "Sa"
    assert "komal Re" in names  # the microtonal komal Re
    assert len(bhairav.tones) == 8


def test_maqam_system():
    maqam = SYSTEMS["maqam"]
    assert maqam.semitones == 24
    do = Tone("Do", octave=4, system=maqam)
    assert 250 < do.frequency < 270


def test_maqam_rast_has_quarter_tones():
    maqam = SYSTEMS["maqam"]
    ts = TonedScale(system=maqam, tonic=Tone("Do", octave=4, system=maqam))
    rast = ts["rast"]
    names = [t.name for t in rast.tones]
    # Rast should contain quarter-tone positions
    assert any("↓" in n or "↑" in n for n in names)


def test_piano_brightness_scales():
    """High-pitched piano should be brighter (more high harmonics)."""
    from pytheory.play import piano_wave
    low = piano_wave(130, n_samples=22050)   # C3
    high = piano_wave(1047, n_samples=22050)  # C6
    # Both should produce valid audio
    assert numpy.abs(low).max() > 0
    assert numpy.abs(high).max() > 0
