import pytest

import pytheory
from pytheory import Tone, TonedScale, Fretboard, Chord
from pytheory.charts import CHARTS, NamedChord


# ── Tone basics ──────────────────────────────────────────────────────────────

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


def test_tone_system():
    c4 = Tone(name="C", octave=4, system="western")
    assert c4.system_name == "western"
    assert c4.system == pytheory.SYSTEMS["western"]


def test_tone_exists():
    c4 = Tone(name="C", octave=4, system="western")
    invalid_tone = Tone(name="H", octave=4, system="western")
    assert c4.exists is True
    assert invalid_tone.exists is False


def test_tone_names_method():
    t = Tone(name="C#", alt_names=["Db"], octave=4)
    assert t.names() == ["C#", "Db"]


# ── Tone equality ────────────────────────────────────────────────────────────

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


# ── Tone arithmetic ─────────────────────────────────────────────────────────

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


# ── Pitch frequencies ────────────────────────────────────────────────────────

def test_pitch_a4_is_440():
    t = Tone.from_string("A4", system="western")
    assert abs(t.pitch() - 440.0) < 0.01


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


# ── Scales ───────────────────────────────────────────────────────────────────

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
    # C D Eb F G Ab Bb C (using sharps: D#, G#, A#)
    assert names == ["C", "D", "D#", "F", "G", "G#", "A#", "C"]


def test_c_harmonic_minor_scale():
    c = TonedScale(tonic="C4")
    hminor = c["harmonic minor"]
    names = [t.name for t in hminor.tones]
    # C D Eb F G Ab B C (raised 7th)
    assert names == ["C", "D", "D#", "F", "G", "G#", "B", "C"]


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


def test_scale_degree_by_roman_numeral():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert major["I"].name == "C"
    assert major["V"].name == "G"


def test_scale_degree_by_index():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert major[0].name == "C"
    assert major[4].name == "G"


def test_scale_invalid_key():
    c = TonedScale(tonic="C4")
    with pytest.raises(KeyError):
        c["nonexistent"]


# ── Modes ────────────────────────────────────────────────────────────────────

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
    assert names == ["C", "D", "D#", "F", "G", "A", "A#", "C"]


def test_c_phrygian():
    c = TonedScale(tonic="C4")
    phrygian = c["phrygian"]
    names = [t.name for t in phrygian.tones]
    # Phrygian: H W W W H W W → C Db Eb F G Ab Bb C
    assert names == ["C", "C#", "D#", "F", "G", "G#", "A#", "C"]


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
    assert names == ["C", "D", "E", "F", "G", "A", "A#", "C"]


def test_c_locrian():
    c = TonedScale(tonic="C4")
    locrian = c["locrian"]
    names = [t.name for t in locrian.tones]
    # Locrian: H W W H W W W → C Db Eb F Gb Ab Bb C
    assert names == ["C", "C#", "D#", "F", "F#", "G#", "A#", "C"]


# ── Chords ───────────────────────────────────────────────────────────────────

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


# ── Named chords (acceptable tones / music theory) ──────────────────────────

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
    assert "D#" in names  # Eb enharmonic
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
    assert "A#" in names  # minor 7th (Bb)


def test_named_chord_diminished():
    cdim = NamedChord(tone_name="C", quality="dim")
    names = cdim.acceptable_tone_names
    assert "C" in names
    assert "D#" in names  # minor 3rd (Eb)
    assert "F#" in names  # diminished 5th (Gb)


def test_named_chord_minor_7th():
    cm7 = NamedChord(tone_name="C", quality="m7")
    names = cm7.acceptable_tone_names
    assert "C" in names
    assert "D#" in names  # minor 3rd
    assert "G" in names   # perfect 5th
    assert "A#" in names  # minor 7th


def test_named_chord_major_7th():
    cmaj7 = NamedChord(tone_name="C", quality="maj7")
    names = cmaj7.acceptable_tone_names
    assert "C" in names
    assert "E" in names  # major 3rd
    assert "G" in names  # perfect 5th
    assert "B" in names  # major 7th


# ── Fretboard ────────────────────────────────────────────────────────────────

def test_fretboard_creation():
    standard_tuning = [
        Tone(name="E", octave=4),
        Tone(name="B", octave=3),
        Tone(name="G", octave=3),
        Tone(name="D", octave=3),
        Tone(name="A", octave=2),
        Tone(name="E", octave=2),
    ]
    fretboard = Fretboard(tones=standard_tuning)
    assert len(fretboard.tones) == 6
    assert fretboard.tones[0].full_name == "E4"
    assert fretboard.tones[-1].full_name == "E2"


def test_fretboard_repr():
    fretboard = Fretboard(tones=[Tone(name="E", octave=4)])
    assert "E4" in repr(fretboard)


# ── Chord fingerings ─────────────────────────────────────────────────────────

@pytest.fixture
def guitar_fretboard():
    tuning = [
        Tone.from_string("E4"),
        Tone.from_string("B3"),
        Tone.from_string("G3"),
        Tone.from_string("D3"),
        Tone.from_string("A2"),
        Tone.from_string("E2"),
    ]
    return Fretboard(tones=tuning)


def test_chord_fingering_c(guitar_fretboard):
    c = CHARTS["western"]["C"]
    fingering = c.fingering(fretboard=guitar_fretboard)
    assert len(fingering) == 6
    # All fret values should be small integers or None
    for f in fingering:
        assert f is None or (isinstance(f, int) and f >= 0)


def test_chord_fingering_am(guitar_fretboard):
    am = CHARTS["western"]["Am"]
    fingering = am.fingering(fretboard=guitar_fretboard)
    assert len(fingering) == 6


def test_chord_fingering_em(guitar_fretboard):
    em = CHARTS["western"]["Em"]
    fingering = em.fingering(fretboard=guitar_fretboard)
    assert len(fingering) == 6
    # Em should be very open (lots of 0s)
    zeros = sum(1 for f in fingering if f == 0)
    assert zeros >= 3


def test_chord_fingering_all_western_chords(guitar_fretboard):
    """Every chord in the western chart should produce a valid fingering."""
    for name, chord in CHARTS["western"].items():
        fingering = chord.fingering(fretboard=guitar_fretboard)
        assert len(fingering) == 6, f"{name} produced wrong number of positions"


def test_chord_fingering_multiple(guitar_fretboard):
    c = CHARTS["western"]["C"]
    fingerings = c.fingering(fretboard=guitar_fretboard, multiple=True)
    assert len(fingerings) >= 1
    assert all(len(f) == 6 for f in fingerings)


# ── Charts ───────────────────────────────────────────────────────────────────

def test_charts_western_exists():
    assert "western" in CHARTS
    assert len(CHARTS["western"]) > 0


def test_charts_has_basic_chords():
    chart = CHARTS["western"]
    for name in ["C", "D", "E", "F", "G", "A", "B"]:
        assert name in chart, f"Missing chord: {name}"


def test_charts_has_minor_chords():
    chart = CHARTS["western"]
    for name in ["Am", "Dm", "Em"]:
        assert name in chart, f"Missing chord: {name}"


def test_charts_has_seventh_chords():
    chart = CHARTS["western"]
    for name in ["C7", "G7", "A7"]:
        assert name in chart, f"Missing chord: {name}"


# ── System ───────────────────────────────────────────────────────────────────

def test_western_system_has_12_tones():
    system = pytheory.SYSTEMS["western"]
    assert system.semitones == 12


def test_western_system_tones():
    system = pytheory.SYSTEMS["western"]
    tone_names = [t.name for t in system.tones]
    assert "A" in tone_names
    assert "C" in tone_names
    assert "G" in tone_names


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


# ── Scale intervals (music theory verification) ─────────────────────────────

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


# ── Play module (non-audio tests) ───────────────────────────────────────────

def test_synth_enum():
    from pytheory.play import Synth, sine_wave, sawtooth_wave, triangle_wave
    # Enum with function values: members are the functions themselves
    assert Synth.SINE is sine_wave
    assert Synth.SAW is sawtooth_wave
    assert Synth.TRIANGLE is triangle_wave
    # Should be directly callable
    wave = Synth.SINE(440)
    assert len(wave) > 0


def test_sine_wave_length():
    from pytheory.play import sine_wave, SAMPLE_RATE
    wave = sine_wave(440)
    assert len(wave) == SAMPLE_RATE


def test_sine_wave_custom_samples():
    from pytheory.play import sine_wave
    wave = sine_wave(440, n_samples=1000)
    assert len(wave) == 1000
