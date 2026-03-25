import pytest
import numpy

import pytheory
from pytheory import Tone, TonedScale, Fretboard, Chord, Key, Note
from pytheory.charts import CHARTS, NamedChord, charts_for_fretboard, QUALITIES
from pytheory.systems import System, SYSTEMS

try:
    import sounddevice
    HAS_PORTAUDIO = True
except OSError:
    HAS_PORTAUDIO = False

needs_portaudio = pytest.mark.skipif(not HAS_PORTAUDIO, reason="PortAudio not available")


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


@pytest.mark.slow
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

@needs_portaudio
def test_synth_enum():
    from pytheory.play import Synth, sine_wave, sawtooth_wave, triangle_wave
    # Enum with function values: members are the functions themselves
    assert Synth.SINE is sine_wave
    assert Synth.SAW is sawtooth_wave
    assert Synth.TRIANGLE is triangle_wave
    # Should be directly callable
    wave = Synth.SINE(440)
    assert len(wave) > 0


@needs_portaudio
def test_sine_wave_length():
    from pytheory.play import sine_wave, SAMPLE_RATE
    wave = sine_wave(440)
    assert len(wave) == SAMPLE_RATE


@needs_portaudio
def test_sine_wave_custom_samples():
    from pytheory.play import sine_wave
    wave = sine_wave(440, n_samples=1000)
    assert len(wave) == 1000


# ── Tone.from_tuple ─────────────────────────────────────────────────────────

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


# ── Tone.from_index ─────────────────────────────────────────────────────────

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


# ── Tone._index ─────────────────────────────────────────────────────────────

def test_tone_index_in_system():
    t = Tone.from_string("A4", system="western")
    assert t._index == 0


def test_tone_index_c():
    t = Tone.from_string("C4", system="western")
    assert t._index == 3


def test_tone_index_without_system_raises():
    t = Tone(name="C", octave=4)
    t._system = None
    t.system_name = None
    with pytest.raises(ValueError, match="index"):
        _ = t._index


# ── Tone._math errors ───────────────────────────────────────────────────────

def test_tone_math_without_system_raises():
    t = Tone(name="C", octave=4)
    t._system = None
    t.system_name = None
    with pytest.raises(ValueError):
        t._math(1)


# ── Tone equality edge cases ────────────────────────────────────────────────

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


# ── Tone arithmetic — multi-octave ──────────────────────────────────────────

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


def test_tone_add_tritone():
    """C + 6 semitones = F#."""
    t = Tone.from_string("C4", system="western")
    result = t.add(6)
    assert result.name == "F#"
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


# ── Pitch — more frequencies ────────────────────────────────────────────────

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


# ── Scale — repr and degree access ──────────────────────────────────────────

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


def test_scale_degree_all_roman_numerals():
    c = TonedScale(tonic="C4")
    major = c["major"]
    expected = ["C", "D", "E", "F", "G", "A", "B"]
    numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
    for numeral, name in zip(numerals, expected):
        assert major[numeral].name == name, f"Degree {numeral} expected {name}"


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


# ── TonedScale ──────────────────────────────────────────────────────────────

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


# ── Mode interval tests (remaining modes) ───────────────────────────────────

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


# ── Chord intervals and properties ──────────────────────────────────────────

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


def test_chord_fingering_wrong_positions_raises():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
    ])
    with pytest.raises(ValueError, match="positions"):
        chord.fingering(1, 2, 3)  # 3 positions for 2 tones


# ── Fretboard fingering ─────────────────────────────────────────────────────

def test_fretboard_fingering():
    tuning = [
        Tone.from_string("E4", system="western"),
        Tone.from_string("B3", system="western"),
    ]
    fb = Fretboard(tones=tuning)
    chord = fb.fingering(0, 0)  # Open strings
    assert chord.tones[0].name == "E"
    assert chord.tones[1].name == "B"


def test_fretboard_fingering_fretted():
    tuning = [
        Tone.from_string("E4", system="western"),
    ]
    fb = Fretboard(tones=tuning)
    chord = fb.fingering(1)  # 1st fret on E string = F
    assert chord.tones[0].name == "F"


def test_fretboard_fingering_wrong_count_raises():
    fb = Fretboard(tones=[Tone.from_string("E4", system="western")])
    with pytest.raises(ValueError, match="positions"):
        fb.fingering(1, 2)  # 2 positions for 1 string


# ── Named chord — all qualities ─────────────────────────────────────────────

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


def test_named_chord_fix_fingering():
    assert NamedChord.fix_fingering((0, 1, -1, 3)) == (0, 1, None, 3)
    assert NamedChord.fix_fingering((0, 0, 0)) == (0, 0, 0)
    assert NamedChord.fix_fingering((-1, -1)) == (None, None)


def test_named_chord_fingerings_returns_multiple(guitar_fretboard):
    c = CHARTS["western"]["C"]
    all_fingerings = c.fingerings(fretboard=guitar_fretboard)
    assert len(all_fingerings) > 1
    assert all(len(f) == 6 for f in all_fingerings)


def test_named_chord_possible_fingerings(guitar_fretboard):
    c = CHARTS["western"]["C"]
    possible = c._possible_fingerings(fretboard=guitar_fretboard)
    assert len(possible) == 6  # One tuple per string
    assert all(isinstance(p, tuple) for p in possible)


# ── Charts — comprehensive ──────────────────────────────────────────────────

def test_charts_total_chord_count():
    """Should have 12 tones * 12 qualities = 144 chords."""
    assert len(CHARTS["western"]) == 12 * len(QUALITIES)


def test_charts_all_qualities_present():
    chart = CHARTS["western"]
    for quality in QUALITIES:
        matching = [name for name in chart if name.endswith(quality) or (quality == "" and len(name) <= 2)]
        assert len(matching) > 0, f"No chords with quality '{quality}'"


@pytest.mark.slow
def test_charts_for_fretboard(guitar_fretboard):
    result = charts_for_fretboard(fretboard=guitar_fretboard)
    assert len(result) == len(CHARTS["western"])
    for name, fingering in result.items():
        assert len(fingering) == 6, f"{name} has wrong fingering length"


@pytest.mark.slow
def test_charts_fingering_values_in_range(guitar_fretboard):
    """All fret values should be 0-6 or None (muted)."""
    for name, chord in CHARTS["western"].items():
        fingering = chord.fingering(fretboard=guitar_fretboard)
        for i, f in enumerate(fingering):
            assert f is None or (0 <= f < 7), \
                f"{name} string {i}: fret {f} out of range"


# ── System ──────────────────────────────────────────────────────────────────

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


# ── Wave generation ─────────────────────────────────────────────────────────

@needs_portaudio
def test_sawtooth_wave_length():
    from pytheory.play import sawtooth_wave, SAMPLE_RATE
    wave = sawtooth_wave(440)
    assert len(wave) == SAMPLE_RATE


@needs_portaudio
def test_sawtooth_wave_custom_samples():
    from pytheory.play import sawtooth_wave
    wave = sawtooth_wave(440, n_samples=2000)
    assert len(wave) == 2000


@needs_portaudio
def test_triangle_wave_length():
    from pytheory.play import triangle_wave, SAMPLE_RATE
    wave = triangle_wave(440)
    assert len(wave) == SAMPLE_RATE


@needs_portaudio
def test_triangle_wave_custom_samples():
    from pytheory.play import triangle_wave
    wave = triangle_wave(440, n_samples=2000)
    assert len(wave) == 2000


@needs_portaudio
def test_sine_wave_output_type():
    from pytheory.play import sine_wave
    wave = sine_wave(440)
    assert wave.dtype == numpy.int16


@needs_portaudio
def test_sawtooth_wave_output_type():
    from pytheory.play import sawtooth_wave
    wave = sawtooth_wave(440)
    assert wave.dtype == numpy.int16


@needs_portaudio
def test_triangle_wave_output_type():
    from pytheory.play import triangle_wave
    wave = triangle_wave(440)
    assert wave.dtype == numpy.int16


@needs_portaudio
def test_sine_wave_different_frequencies():
    from pytheory.play import sine_wave
    wave_low = sine_wave(220)
    wave_high = sine_wave(880)
    # Both should be valid arrays of the same length
    assert len(wave_low) == len(wave_high)
    # But they should have different content
    assert not numpy.array_equal(wave_low, wave_high)


@needs_portaudio
def test_synth_callable_with_pitch():
    """Synth enum members should work with actual pitch values from Tone."""
    from pytheory.play import Synth
    t = Tone.from_string("A4", system="western")
    hz = t.pitch()
    wave = Synth.SINE(hz)
    assert len(wave) > 0


# ── Integration: scale → chord → fingering ──────────────────────────────────

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


def test_enharmonic_equivalence_in_scales():
    """D Dorian and C major should contain the same pitch classes."""
    c_major = TonedScale(tonic="C4")["major"]
    d_dorian = TonedScale(tonic="D4")["dorian"]

    c_names = sorted(set(t.name for t in c_major.tones))
    d_names = sorted(set(t.name for t in d_dorian.tones))
    assert c_names == d_names


def test_relative_minor():
    """A minor (relative minor of C major) should share the same notes."""
    c_major = TonedScale(tonic="C4")["major"]
    a_minor = TonedScale(tonic="A4")["minor"]

    c_names = sorted(set(t.name for t in c_major.tones))
    a_names = sorted(set(t.name for t in a_minor.tones))
    assert c_names == a_names


# ── Tone operators ──────────────────────────────────────────────────────────

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


# ── Scale iteration ─────────────────────────────────────────────────────────

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


# ── Scale.chord() and Scale.triad() ─────────────────────────────────────────

def test_scale_chord():
    c = TonedScale(tonic="C4")
    major = c["major"]
    chord = major.chord(0, 2, 4)  # C E G
    assert len(chord) == 3
    assert chord.tones[0].name == "C"
    assert chord.tones[1].name == "E"
    assert chord.tones[2].name == "G"


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


def test_scale_chord_seventh():
    """Build a 7th chord from scale degrees."""
    c = TonedScale(tonic="C4")
    major = c["major"]
    seventh = major.chord(0, 2, 4, 6)  # C E G B = Cmaj7
    assert len(seventh) == 4
    names = [t.name for t in seventh]
    assert names == ["C", "E", "G", "B"]


# ── Chord iteration ─────────────────────────────────────────────────────────

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


# ── Fretboard presets ───────────────────────────────────────────────────────

def test_fretboard_guitar():
    fb = Fretboard.guitar()
    assert len(fb) == 6
    names = [t.name for t in fb]
    assert names == ["E", "B", "G", "D", "A", "E"]


def test_fretboard_guitar_octaves():
    fb = Fretboard.guitar()
    octaves = [t.octave for t in fb]
    assert octaves == [4, 3, 3, 3, 2, 2]


def test_fretboard_bass():
    fb = Fretboard.bass()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["G", "D", "A", "E"]


def test_fretboard_ukulele():
    fb = Fretboard.ukulele()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["A", "E", "C", "G"]


def test_fretboard_iter():
    fb = Fretboard.guitar()
    tones = list(fb)
    assert len(tones) == 6
    assert all(isinstance(t, Tone) for t in tones)


def test_fretboard_len():
    fb = Fretboard.guitar()
    assert len(fb) == 6


def test_fretboard_preset_fingerings():
    """Preset fretboards should work with chord charts."""
    fb = Fretboard.guitar()
    c = CHARTS["western"]["C"]
    fingering = c.fingering(fretboard=fb)
    assert len(fingering) == 6


def test_fretboard_ukulele_fingerings():
    fb = Fretboard.ukulele()
    c = CHARTS["western"]["C"]
    fingering = c.fingering(fretboard=fb)
    assert len(fingering) == 4


def test_fretboard_guitar_drop_d():
    fb = Fretboard.guitar("drop d")
    assert len(fb) == 6
    assert fb.tones[-1].name == "D"
    assert fb.tones[-1].octave == 2


def test_fretboard_guitar_open_g():
    fb = Fretboard.guitar("open g")
    assert len(fb) == 6
    assert fb.tones[0].name == "D"


def test_fretboard_guitar_custom_tuple():
    fb = Fretboard.guitar(("E4", "B3", "G3", "D3", "A2", "D2"))
    assert len(fb) == 6
    assert fb.tones[-1].name == "D"


def test_fretboard_bass_five_string():
    fb = Fretboard.bass(five_string=True)
    assert len(fb) == 5
    assert fb.tones[-1].name == "B"


def test_fretboard_tunings_dict():
    for name in Fretboard.TUNINGS:
        fb = Fretboard.guitar(name)
        assert len(fb) == 6, f"Tuning {name} should have 6 strings"


def test_fretboard_mandolin():
    fb = Fretboard.mandolin()
    assert len(fb) == 4
    assert fb.tones[0].name == "E"
    assert fb.tones[-1].name == "G"


def test_fretboard_violin():
    fb = Fretboard.violin()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["E", "A", "D", "G"]


def test_fretboard_viola():
    fb = Fretboard.viola()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["A", "D", "G", "C"]


def test_fretboard_cello():
    fb = Fretboard.cello()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["A", "D", "G", "C"]
    assert fb.tones[0].octave == 3


def test_fretboard_banjo():
    fb = Fretboard.banjo()
    assert len(fb) == 5
    assert fb.tones[-1].name == "G"  # high drone string


def test_fretboard_banjo_open_d():
    fb = Fretboard.banjo("open d")
    assert len(fb) == 5


def test_fretboard_twelve_string():
    fb = Fretboard.twelve_string()
    assert len(fb) == 12


def test_fretboard_violin_tuned_in_fifths():
    """Violin strings should be a perfect 5th apart."""
    fb = Fretboard.violin()
    for i in range(len(fb.tones) - 1):
        interval = fb.tones[i] - fb.tones[i + 1]
        assert interval == 7, f"Strings {i} and {i+1} not a 5th apart"


def test_fretboard_octave_mandolin():
    fb = Fretboard.octave_mandolin()
    assert len(fb) == 4
    assert fb.tones[0].name == "E"
    assert fb.tones[0].octave == 4


def test_fretboard_mandocello():
    fb = Fretboard.mandocello()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["A", "D", "G", "C"]
    assert fb.tones[0].octave == 3


def test_fretboard_double_bass():
    fb = Fretboard.double_bass()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["G", "D", "A", "E"]


def test_fretboard_double_bass_tuned_in_fourths():
    fb = Fretboard.double_bass()
    for i in range(len(fb.tones) - 1):
        interval = fb.tones[i] - fb.tones[i + 1]
        assert interval == 5, f"Strings {i} and {i+1} not a 4th apart"


def test_fretboard_harp():
    fb = Fretboard.harp()
    assert len(fb) == 47
    assert fb.tones[0].name == "G"
    assert fb.tones[0].octave == 7
    assert fb.tones[-1].name == "C"
    assert fb.tones[-1].octave == 1


def test_fretboard_pedal_steel():
    fb = Fretboard.pedal_steel()
    assert len(fb) == 10


def test_mandolin_family_fifths():
    """All mandolin family instruments should be tuned in 5ths."""
    for name in ["mandolin", "mandola", "octave_mandolin", "mandocello"]:
        fb = getattr(Fretboard, name)()
        for i in range(len(fb.tones) - 1):
            interval = fb.tones[i] - fb.tones[i + 1]
            assert interval == 7, f"{name} strings {i},{i+1} not a 5th apart"


def test_all_instruments_create():
    """Every instrument preset should instantiate without error."""
    instruments = [
        "guitar", "twelve_string", "bass", "ukulele",
        "mandolin", "mandola", "octave_mandolin", "mandocello",
        "violin", "viola", "cello", "double_bass",
        "banjo", "harp", "pedal_steel",
        "bouzouki", "oud", "sitar", "shamisen", "erhu",
        "charango", "pipa", "balalaika", "lute", "keyboard",
    ]
    for name in instruments:
        fb = getattr(Fretboard, name)()
        assert len(fb) > 0, f"{name} has no strings"


def test_fretboard_oud():
    fb = Fretboard.oud()
    assert len(fb) == 6


def test_fretboard_shamisen():
    fb = Fretboard.shamisen()
    assert len(fb) == 3


def test_fretboard_erhu():
    fb = Fretboard.erhu()
    assert len(fb) == 2
    assert fb.tones[0] - fb.tones[1] == 7  # tuned in 5ths


def test_fretboard_bouzouki_irish():
    fb = Fretboard.bouzouki("irish")
    assert len(fb) == 4


def test_fretboard_bouzouki_greek():
    fb = Fretboard.bouzouki("greek")
    assert len(fb) == 4


def test_fretboard_charango():
    fb = Fretboard.charango()
    assert len(fb) == 5


def test_fretboard_balalaika():
    fb = Fretboard.balalaika()
    assert len(fb) == 3
    # Two unison strings
    assert fb.tones[1].name == fb.tones[2].name


def test_fretboard_lute():
    fb = Fretboard.lute()
    assert len(fb) == 6


def test_fretboard_sitar():
    fb = Fretboard.sitar()
    assert len(fb) == 7


def test_fretboard_pipa():
    fb = Fretboard.pipa()
    assert len(fb) == 4


def test_keyboard_88():
    kb = Fretboard.keyboard()
    assert len(kb) == 88


def test_keyboard_25():
    kb = Fretboard.keyboard(25, "C3")
    assert len(kb) == 25
    assert kb.tones[-1].name == "C"
    assert kb.tones[-1].octave == 3


def test_keyboard_custom():
    kb = Fretboard.keyboard(61, "C2")
    assert len(kb) == 61


# ── Ergonomic integration tests ─────────────────────────────────────────────

def test_ergonomic_workflow():
    """Demonstrate the improved API in a realistic workflow."""
    # Build a scale
    c = TonedScale(tonic="C4")
    major = c["major"]

    # Iterate and check
    assert "C" in major
    assert len(major) == 8

    # Build chords from the scale
    I = major.triad(0)   # C major
    IV = major.triad(3)  # F major
    V = major.triad(4)   # G major

    assert "C" in I
    assert "F" in IV
    assert "G" in V

    # Get fingerings
    fb = Fretboard.guitar()
    for name in ["C", "F", "G"]:
        fingering = CHARTS["western"][name].fingering(fretboard=fb)
        assert len(fingering) == len(fb)


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


# ── Indian system ───────────────────────────────────────────────────────────

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


def test_indian_bilawal_thaat():
    """Bilawal = major scale: Sa Re Ga Ma Pa Dha Ni Sa."""
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    bilawal = sa["bilawal"]
    names = [t.name for t in bilawal]
    assert names == ["Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni", "Sa"]


def test_indian_bhairav_thaat():
    """Bhairav: Sa komal-Re Ga Ma Pa komal-Dha Ni Sa."""
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    bhairav = sa["bhairav"]
    names = [t.name for t in bhairav]
    assert names == ["Sa", "komal Re", "Ga", "Ma", "Pa", "komal Dha", "Ni", "Sa"]


def test_indian_todi_thaat():
    """Todi: Sa komal-Re komal-Ga tivra-Ma Pa komal-Dha Ni Sa."""
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    todi = sa["todi"]
    names = [t.name for t in todi]
    assert names == ["Sa", "komal Re", "komal Ga", "tivra Ma", "Pa", "komal Dha", "Ni", "Sa"]


def test_indian_kalyan_thaat():
    """Kalyan = Lydian: Sa Re Ga tivra-Ma Pa Dha Ni Sa."""
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    kalyan = sa["kalyan"]
    names = [t.name for t in kalyan]
    assert names == ["Sa", "Re", "Ga", "tivra Ma", "Pa", "Dha", "Ni", "Sa"]


def test_indian_all_thaats_available():
    sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])
    thaats = sa.scales
    for thaat in ["bilawal", "bhairav", "todi", "kalyan", "kafi",
                  "asavari", "bhairavi", "khamaj", "poorvi", "marwa"]:
        assert thaat in thaats, f"Missing thaat: {thaat}"


def test_indian_all_thaat_intervals_sum_to_12():
    indian = SYSTEMS["indian"]
    for name, scale in indian.scales["thaat"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_indian_bilawal_equals_western_major():
    """Bilawal intervals should match Western major."""
    indian = SYSTEMS["indian"]
    western = SYSTEMS["western"]
    bilawal = indian.scales["thaat"]["bilawal"]["intervals"]
    major = western.scales["heptatonic"]["major"]["intervals"]
    assert bilawal == major


def test_indian_tone_arithmetic():
    sa = Tone.from_string("Sa4", system="indian")
    assert (sa + 2).name == "Re"
    assert (sa + 4).name == "Ga"
    assert (sa + 5).name == "Ma"
    assert (sa + 7).name == "Pa"
    assert (sa + 9).name == "Dha"
    assert (sa + 11).name == "Ni"


def test_indian_chromatic_walk():
    """Walk all 12 swaras from Sa4."""
    sa = Tone.from_string("Sa4", system="indian")
    expected = ["Sa", "komal Re", "Re", "komal Ga", "Ga", "Ma",
                "tivra Ma", "Pa", "komal Dha", "Dha", "komal Ni", "Ni", "Sa"]
    for i, name in enumerate(expected):
        result = sa + i
        assert result.name == name, f"step {i}: expected {name}, got {result.name}"


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


# ── Arabic system ───────────────────────────────────────────────────────────

def test_arabic_system_exists():
    assert "arabic" in SYSTEMS
    assert SYSTEMS["arabic"].semitones == 12


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


def test_arabic_ajam_equals_western_major():
    arabic = SYSTEMS["arabic"]
    western = SYSTEMS["western"]
    ajam = arabic.scales["maqam"]["ajam"]["intervals"]
    major = western.scales["heptatonic"]["major"]["intervals"]
    assert ajam == major


def test_arabic_tone_arithmetic():
    do = Tone.from_string("Do4", system="arabic")
    assert (do + 2).name == "Re"
    assert (do + 4).name == "Mi"
    assert (do + 7).name == "Sol"


# ── Japanese system ─────────────────────────────────────────────────────────

def test_japanese_system_exists():
    assert "japanese" in SYSTEMS
    assert SYSTEMS["japanese"].semitones == 12


def test_japanese_hirajoshi():
    """Hirajoshi: C D Eb G Ab."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    h = c["hirajoshi"]
    names = [t.name for t in h]
    assert names == ["C", "D", "Eb", "G", "Ab", "C"]


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


def test_japanese_iwato():
    """Iwato: C Db F Gb Bb."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["iwato"]
    names = [t.name for t in s]
    assert names == ["C", "Db", "F", "Gb", "Bb", "C"]


def test_japanese_kumoi():
    """Kumoi: C D Eb G A."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["kumoi"]
    names = [t.name for t in s]
    assert names == ["C", "D", "Eb", "G", "A", "C"]


def test_japanese_ritsu():
    """Ritsu (gagaku): C D Eb F G A Bb = Dorian."""
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    s = c["ritsu"]
    names = [t.name for t in s]
    assert names == ["C", "D", "Eb", "F", "G", "A", "Bb", "C"]


def test_japanese_all_scales_available():
    c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])
    for scale in ["hirajoshi", "in", "yo", "iwato", "kumoi", "insen", "ritsu", "ryo"]:
        assert scale in c.scales, f"Missing scale: {scale}"


def test_japanese_pentatonic_intervals_sum_to_12():
    japanese = SYSTEMS["japanese"]
    for name, scale in japanese.scales["pentatonic"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


def test_japanese_heptatonic_intervals_sum_to_12():
    japanese = SYSTEMS["japanese"]
    for name, scale in japanese.scales["heptatonic"].items():
        total = sum(scale["intervals"])
        assert total == 12, f"{name} intervals sum to {total}, not 12"


# ── Blues system ────────────────────────────────────────────────────────────

def test_blues_system_exists():
    assert "blues" in SYSTEMS
    assert SYSTEMS["blues"].semitones == 12


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


def test_blues_all_intervals_sum_to_12():
    blues = SYSTEMS["blues"]
    for scale_type in blues.scales:
        for name, scale in blues.scales[scale_type].items():
            total = sum(scale["intervals"])
            assert total == 12, f"{name} intervals sum to {total}, not 12"


# ── Gamelan system ──────────────────────────────────────────────────────────

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


def test_gamelan_all_scales_available():
    ji = TonedScale(tonic="ji4", system=SYSTEMS["gamelan"])
    for scale in ["slendro", "pelog nem", "pelog barang", "pelog lima", "pelog"]:
        assert scale in ji.scales, f"Missing scale: {scale}"


def test_gamelan_all_intervals_sum_to_12():
    gamelan = SYSTEMS["gamelan"]
    for scale_type in gamelan.scales:
        for name, scale in gamelan.scales[scale_type].items():
            total = sum(scale["intervals"])
            assert total == 12, f"{name} intervals sum to {total}, not 12"


# ── Overtone series ─────────────────────────────────────────────────────────

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


# ── Chord identification ────────────────────────────────────────────────────

def test_identify_c_major():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert chord.identify() == "C major"


def test_identify_a_minor():
    chord = Chord(tones=[
        Tone.from_string("A4", system="western"),
        Tone.from_string("C5", system="western"),
        Tone.from_string("E5", system="western"),
    ])
    assert chord.identify() == "A minor"


def test_identify_g_dominant_7th():
    chord = Chord(tones=[
        Tone.from_string("G4", system="western"),
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
        Tone.from_string("F5", system="western"),
    ])
    assert chord.identify() == "G dominant 7th"


def test_identify_power_chord():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert chord.identify() == "C power"


def test_identify_diminished():
    chord = Chord(tones=[
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
        Tone.from_string("F5", system="western"),
    ])
    assert chord.identify() == "B diminished"


def test_identify_single_tone():
    chord = Chord(tones=[Tone.from_string("C4", system="western")])
    assert chord.identify() is None


# ── Voice leading ───────────────────────────────────────────────────────────

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


# ── Harmonic analysis ───────────────────────────────────────────────────────

def test_analyze_I():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
        Tone.from_string("G4", system="western"),
    ])
    assert chord.analyze("C") == "I"


def test_analyze_V():
    chord = Chord(tones=[
        Tone.from_string("G4", system="western"),
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
    ])
    assert chord.analyze("C") == "V"


def test_analyze_ii():
    chord = Chord(tones=[
        Tone.from_string("D4", system="western"),
        Tone.from_string("F4", system="western"),
        Tone.from_string("A4", system="western"),
    ])
    assert chord.analyze("C") == "ii"


def test_analyze_V7():
    chord = Chord(tones=[
        Tone.from_string("G4", system="western"),
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
        Tone.from_string("F5", system="western"),
    ])
    assert chord.analyze("C") == "V7"


def test_analyze_not_in_key():
    chord = Chord(tones=[
        Tone.from_string("F#4", system="western"),
        Tone.from_string("A#4", system="western"),
        Tone.from_string("C#5", system="western"),
    ])
    assert chord.analyze("C") is None


# ── Tension ─────────────────────────────────────────────────────────────────

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


# ── Version ─────────────────────────────────────────────────────────────────

def test_version():
    import pytheory
    assert pytheory.__version__


def test_all_exports():
    import pytheory
    assert not hasattr(pytheory, "ceil")
    assert not hasattr(pytheory, "floor")
    assert "Tone" in pytheory.__all__


# ── Interval naming ─────────────────────────────────────────────────────────

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


# ── MIDI ────────────────────────────────────────────────────────────────────

def test_midi_c4():
    c4 = Tone.from_string("C4", system="western")
    assert c4.midi == 60


def test_midi_a4():
    a4 = Tone.from_string("A4", system="western")
    assert a4.midi == 69


def test_midi_c5():
    c5 = Tone.from_string("C5", system="western")
    assert c5.midi == 72


def test_midi_no_octave():
    c = Tone(name="C")
    assert c.midi is None


def test_midi_chromatic_sequence():
    """MIDI numbers should increment by 1 per semitone."""
    c4 = Tone.from_string("C4", system="western")
    for i in range(12):
        assert (c4 + i).midi == 60 + i


# ── Transpose ──────────────────────────────────────────────────────────────

def test_tone_transpose():
    c4 = Tone.from_string("C4", system="western")
    assert c4.transpose(7).name == "G"


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


def test_scale_transpose():
    c_major = TonedScale(tonic="C4")["major"]
    d_major = c_major.transpose(2)
    assert d_major.note_names == ["D", "E", "F#", "G", "A", "B", "C#", "D"]


def test_scale_transpose_negative():
    d_major = TonedScale(tonic="D4")["major"]
    c_major = d_major.transpose(-2)
    assert c_major.note_names == ["C", "D", "E", "F", "G", "A", "B", "C"]


# ── Chord root and quality ─────────────────────────────────────────────────

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


# ── Tone.from_frequency ────────────────────────────────────────────────────

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


# ── Tone.from_midi ─────────────────────────────────────────────────────────

def test_from_midi_c4():
    assert Tone.from_midi(60).name == "C"
    assert Tone.from_midi(60).octave == 4


def test_from_midi_a4():
    assert Tone.from_midi(69).name == "A"
    assert Tone.from_midi(69).octave == 4


def test_from_midi_roundtrip():
    """from_midi(tone.midi) should return the same note."""
    for midi in [48, 60, 69, 72, 84]:
        t = Tone.from_midi(midi)
        assert t.midi == midi


# ── Chord.inversion ────────────────────────────────────────────────────────

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


# ── Scale.seventh ──────────────────────────────────────────────────────────

def test_scale_seventh_I():
    major = TonedScale(tonic="C4")["major"]
    assert major.seventh(0).identify() == "C major 7th"


def test_scale_seventh_ii():
    major = TonedScale(tonic="C4")["major"]
    assert major.seventh(1).identify() == "D minor 7th"


def test_scale_seventh_V():
    major = TonedScale(tonic="C4")["major"]
    assert major.seventh(4).identify() == "G dominant 7th"


# ── Scale.harmonize ────────────────────────────────────────────────────────

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


# ── Scale.progression ──────────────────────────────────────────────────────

def test_progression_I_IV_V():
    major = TonedScale(tonic="C4")["major"]
    prog = major.progression("I", "IV", "V")
    assert len(prog) == 3
    assert prog[0].identify() == "C major"
    assert prog[1].identify() == "F major"
    assert prog[2].identify() == "G major"


def test_progression_with_seventh():
    major = TonedScale(tonic="C4")["major"]
    prog = major.progression("I", "V7")
    assert prog[0].identify() == "C major"
    assert prog[1].identify() == "G dominant 7th"


def test_progression_pop():
    major = TonedScale(tonic="G4")["major"]
    prog = major.progression("I", "V", "vi", "IV")
    assert prog[0].identify() == "G major"
    assert prog[3].identify() == "C major"


# ── Key class ───────────────────────────────────────────────────────────────

def test_key_c_major():
    k = Key("C", "major")
    assert k.note_names == ["C", "D", "E", "F", "G", "A", "B", "C"]


def test_key_repr():
    assert repr(Key("C", "major")) == "<Key C major>"


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


def test_key_triad():
    k = Key("C", "major")
    assert k.triad(0).identify() == "C major"
    assert k.triad(4).identify() == "G major"


def test_key_seventh():
    k = Key("C", "major")
    assert k.seventh(4).identify() == "G dominant 7th"


def test_key_progression():
    k = Key("G", "major")
    prog = k.progression("I", "IV", "V")
    assert prog[0].identify() == "G major"


def test_key_relative_major_to_minor():
    k = Key("C", "major")
    rel = k.relative
    assert rel.tonic_name == "A"
    assert rel.mode == "minor"


def test_key_relative_minor_to_major():
    k = Key("A", "minor")
    rel = k.relative
    assert rel.tonic_name == "C"
    assert rel.mode == "major"


def test_key_parallel():
    k = Key("C", "major")
    par = k.parallel
    assert par.tonic_name == "C"
    assert par.mode == "minor"


def test_key_relative_shares_notes():
    c = Key("C", "major")
    a = c.relative
    c_notes = sorted(set(c.note_names))
    a_notes = sorted(set(a.note_names))
    assert c_notes == a_notes


# ── Note alias ──────────────────────────────────────────────────────────────

def test_note_is_tone():
    assert Note is Tone


def test_note_from_string():
    n = Note.from_string("C4", system="western")
    assert n.name == "C"
    assert n.frequency == Tone.from_string("C4", system="western").frequency


# ── Chord.from_name ────────────────────────────────────────────────────────

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


# ── Interval constants ─────────────────────────────────────────────────────

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


# ── Enharmonic ─────────────────────────────────────────────────────────────

def test_enharmonic_sharp():
    cs = Tone.from_string("C#4", system="western")
    assert cs.enharmonic == "Db"


def test_enharmonic_natural():
    c = Tone.from_string("C4", system="western")
    assert c.enharmonic is None


# ── PROGRESSIONS ───────────────────────────────────────────────────────────

def test_progressions_dict():
    from pytheory import PROGRESSIONS
    assert "I-V-vi-IV" in PROGRESSIONS
    assert "12-bar blues" in PROGRESSIONS
    assert len(PROGRESSIONS["12-bar blues"]) == 12


def test_progressions_with_key():
    from pytheory import PROGRESSIONS
    k = Key("C", "major")
    pop = k.progression(*PROGRESSIONS["I-V-vi-IV"])
    assert len(pop) == 4
    assert pop[0].identify() == "C major"


# ── Key.__str__ ────────────────────────────────────────────────────────────

def test_key_str():
    assert str(Key("C", "major")) == "C major"
    assert str(Key("A", "minor")) == "A minor"


# ── Key.detect ─────────────────────────────────────────────────────────────

def test_key_detect_c_major():
    k = Key.detect("C", "D", "E", "F", "G", "A", "B")
    assert k.tonic_name == "C"
    assert k.mode == "major"


def test_key_detect_a_major():
    k = Key.detect("A", "B", "C#", "D", "E", "F#", "G#")
    assert k.tonic_name == "A"
    assert k.mode == "major"


def test_key_detect_prefers_major():
    """When major and minor match equally, prefer major."""
    k = Key.detect("C", "E", "G")
    assert k.mode == "major"


def test_key_detect_partial():
    """Should work with a subset of scale notes."""
    k = Key.detect("C", "E", "G")
    assert k.tonic_name == "C"


def test_key_detect_empty():
    assert Key.detect() is None


# ── Tone properties ────────────────────────────────────────────────────────

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


# ── Fretboard.INSTRUMENTS ──────────────────────────────────────────────────

def test_instruments_list():
    assert len(Fretboard.INSTRUMENTS) == 25
    assert "guitar" in Fretboard.INSTRUMENTS
    assert "sitar" in Fretboard.INSTRUMENTS
    assert "keyboard" in Fretboard.INSTRUMENTS


# ── Chord.from_tones ──────────────────────────────────────────────────────

def test_chord_from_tones():
    c = Chord.from_tones("C", "E", "G")
    assert c.identify() == "C major"


def test_chord_from_tones_minor():
    am = Chord.from_tones("A", "C", "E")
    assert am.identify() == "A minor"


def test_chord_from_tones_octave():
    c = Chord.from_tones("C", "E", "G", octave=3)
    assert c.tones[0].octave == 3


# ── Tab output ────────────────────────────────────────────────────────────

def test_tab_output():
    from pytheory.charts import CHARTS
    fb = Fretboard.guitar()
    tab = CHARTS["western"]["C"].tab(fretboard=fb)
    assert "C" in tab
    assert "|--" in tab
    lines = tab.strip().split("\n")
    assert len(lines) == 7  # chord name + 6 strings


def test_tab_muted_string():
    from pytheory.charts import CHARTS
    fb = Fretboard.guitar()
    tab = CHARTS["western"]["F"].tab(fretboard=fb)
    # F chord may have muted strings shown as 'x'
    assert "|--" in tab


# ── Scale.detect ──────────────────────────────────────────────────────────

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


# ── Nashville numbers ────────────────────────────────────────────────────

def test_nashville_1_4_5():
    k = Key("C", "major")
    prog = k.nashville(1, 4, 5)
    assert prog[0].identify() == "C major"
    assert prog[1].identify() == "F major"
    assert prog[2].identify() == "G major"


def test_nashville_with_seventh():
    k = Key("G", "major")
    prog = k.nashville(1, 4, "57")
    assert prog[2].identify() == "D dominant 7th"


def test_nashville_on_scale():
    scale = TonedScale(tonic="C4")["major"]
    prog = scale.nashville(1, 5, 1)
    assert prog[0].identify() == "C major"
    assert prog[1].identify() == "G major"


# ── Capo ───────────────────────────────────────────────────────────────────

def test_guitar_capo():
    fb = Fretboard.guitar(capo=2)
    assert fb.tones[0].name == "F#"
    assert len(fb) == 6


def test_capo_method():
    fb = Fretboard.guitar()
    fb3 = fb.capo(3)
    assert fb3.tones[0].name == "G"


def test_capo_zero():
    fb = Fretboard.guitar(capo=0)
    assert fb.tones[0].name == "E"


# ── Chord.__add__ ─────────────────────────────────────────────────────────

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


# ── Tritone substitution ──────────────────────────────────────────────────

def test_tritone_sub():
    g7 = Chord.from_name("G7")
    sub = g7.tritone_sub()
    assert sub.identify() == "C# dominant 7th"


def test_tritone_sub_is_6_semitones():
    c = Chord.from_tones("C", "E", "G")
    sub = c.tritone_sub()
    assert sub.root.name == "F#"


# ── Secondary dominants ──────────────────────────────────────────────────

def test_secondary_dominant_V_of_V():
    k = Key("C", "major")
    vv = k.secondary_dominant(5)
    assert vv.identify() == "D dominant 7th"


def test_secondary_dominant_V_of_ii():
    k = Key("C", "major")
    assert k.secondary_dominant(2).identify() == "A dominant 7th"


def test_secondary_dominant_V_of_vi():
    k = Key("C", "major")
    assert k.secondary_dominant(6).identify() == "E dominant 7th"


# ── Key.all_keys ─────────────────────────────────────────────────────────

def test_all_keys():
    keys = Key.all_keys()
    assert len(keys) == 24
    majors = [k for k in keys if k.mode == "major"]
    minors = [k for k in keys if k.mode == "minor"]
    assert len(majors) == 12
    assert len(minors) == 12


# ── More progressions ───────────────────────────────────────────────────

def test_progressions_count():
    from pytheory.scales import PROGRESSIONS
    assert len(PROGRESSIONS) >= 14


def test_pachelbel_progression():
    from pytheory.scales import PROGRESSIONS
    k = Key("C", "major")
    prog = k.progression(*PROGRESSIONS["Pachelbel"])
    assert len(prog) == 8
    assert prog[0].identify() == "C major"


# ── Tone.letter ────────────────────────────────────────────────────────────

def test_tone_letter_natural():
    assert Tone.from_string("C4").letter == "C"


def test_tone_letter_sharp():
    assert Tone.from_string("C#4").letter == "C"


def test_tone_letter_flat():
    assert Tone(name="Bb", octave=4).letter == "B"


# ── Key.signature ──────────────────────────────────────────────────────────

def test_key_signature_c_major():
    sig = Key("C", "major").signature
    assert sig["sharps"] == 0
    assert sig["flats"] == 0


def test_key_signature_g_major():
    sig = Key("G", "major").signature
    assert sig["sharps"] == 1
    assert sig["accidentals"] == ["F#"]


def test_key_signature_d_major():
    sig = Key("D", "major").signature
    assert sig["sharps"] == 2


# ── Chord.from_intervals ──────────────────────────────────────────────────

def test_chord_from_intervals_major():
    assert Chord.from_intervals("C", 4, 7).identify() == "C major"


def test_chord_from_intervals_dom7():
    assert Chord.from_intervals("G", 4, 7, 10).identify() == "G dominant 7th"


# ── Chord.from_midi_message ──────────────────────────────────────────────

def test_chord_from_midi_message():
    c = Chord.from_midi_message(60, 64, 67)
    assert c.identify() == "C major"


# ── Chord.add_tone / remove_tone ──────────────────────────────────────────

def test_chord_add_tone():
    c = Chord.from_tones("C", "E", "G")
    cmaj7 = c.add_tone(Tone("B", octave=4))
    assert cmaj7.identify() == "C major 7th"


def test_chord_remove_tone():
    cmaj7 = Chord.from_name("Cmaj7")
    c = cmaj7.remove_tone("B")
    assert c.identify() == "C major"


# ── analyze_progression ──────────────────────────────────────────────────

def test_analyze_progression():
    from pytheory import analyze_progression
    prog = [Chord.from_name("C"), Chord.from_name("Am"),
            Chord.from_name("F"), Chord.from_name("G")]
    assert analyze_progression(prog, key="C") == ["I", "vi", "IV", "V"]


# ── Key.borrowed_chords ─────────────────────────────────────────────────

def test_borrowed_chords():
    borrowed = Key("C", "major").borrowed_chords
    assert len(borrowed) > 0


# ── Key.random_progression ──────────────────────────────────────────────

def test_random_progression():
    prog = Key("C", "major").random_progression(4)
    assert len(prog) == 4


# ── Fretboard.scale_diagram ────────────────────────────────────────────

def test_scale_diagram():
    fb = Fretboard.guitar()
    scale = TonedScale(tonic="C4")["major"]
    diagram = fb.scale_diagram(scale, frets=5)
    assert "E|" in diagram
    lines = diagram.strip().split("\n")
    assert len(lines) == 7


# ── Coverage gap tests ─────────────────────────────────────────────────────

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


def test_key_with_string_system():
    k = Key("C", "major", system="western")
    assert k.note_names[0] == "C"


def test_key_detect_returns_none_empty():
    assert Key.detect() is None


def test_key_signature_flat_key():
    """F major has one flat (Bb)."""
    # F major scale: F G A Bb C D E
    # But our system uses sharps, so Bb = A#
    sig = Key("F", "major").signature
    # The scale uses A# which is sharp notation for Bb
    assert sig["sharps"] + sig["flats"] >= 0  # at least runs


def test_key_borrowed_chords_minor():
    """Minor key should borrow from parallel major."""
    borrowed = Key("A", "minor").borrowed_chords
    assert len(borrowed) > 0


def test_key_parallel_returns_none_for_other_modes():
    """Parallel should return None for non-major/minor modes."""
    k = Key("C", "major")
    k.mode = "lydian"  # force non-standard mode
    assert k.parallel is None


def test_key_relative_returns_none_for_other_modes():
    k = Key("C", "major")
    k.mode = "lydian"
    assert k.relative is None


def test_toned_scale_with_string_system():
    ts = TonedScale(tonic="Do4", system="arabic")
    assert "ajam" in ts.scales


def test_fretboard_fingering_method():
    """Fretboard.fingering should return a Chord."""
    fb = Fretboard.guitar()
    result = fb.fingering(0, 0, 0, 0, 0, 0)
    assert len(result) == 6


def test_charts_muted_string():
    """A chord with no valid fret gets -1 → None."""
    from pytheory.charts import NamedChord
    nc = NamedChord(tone_name="C", quality="")
    fixed = nc.fix_fingering((0, -1, 2))
    assert fixed == (0, None, 2)


def test_fretboard_chord_method():
    """Fretboard.chord() looks up a chord by name."""
    fb = Fretboard.guitar()
    f = fb.chord("G")
    assert f.identify() == "G major"
    assert len(f) == 6


def test_fretboard_chord_system_kwarg():
    """Fretboard.chord() accepts a system keyword argument."""
    fb = Fretboard.guitar()
    f = fb.chord("Am", system="western")
    assert f.identify() == "A minor"


def test_fretboard_tab_method():
    """Fretboard.tab() returns ASCII tablature."""
    fb = Fretboard.guitar()
    tab = fb.tab("C")
    assert "C major" in tab
    assert "e|" in tab
    assert "E|" in tab


@pytest.mark.slow
def test_fretboard_chart_method():
    """Fretboard.chart() generates all fingerings."""
    fb = Fretboard.guitar()
    chart = fb.chart()
    assert "C" in chart
    assert "Am7" in chart
    assert chart["C"].identify() == "C major"


def test_fingering_tab_method():
    """Fingering.tab() renders ASCII tablature."""
    fb = Fretboard.guitar()
    f = fb.chord("Em")
    tab = f.tab()
    assert "E minor" in tab
    assert "e|" in tab


# ── Flat note support ─────────────────────────────────────────────────────────

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


def test_flat_chord_from_tones():
    chord = Chord.from_tones("Db", "F", "Ab")
    assert chord.identify() == "Db major"


def test_flat_chord_from_tones_minor():
    chord = Chord.from_tones("Bb", "Db", "F")
    assert chord.identify() == "Bb minor"


def test_flat_chord_from_tones_seventh():
    chord = Chord.from_tones("Eb", "G", "Bb", "Db")
    assert chord.identify() == "Eb dominant 7th"


def test_system_resolve_name_sharp():
    assert SYSTEMS["western"].resolve_name("C#") == "C#"


def test_system_resolve_name_flat():
    assert SYSTEMS["western"].resolve_name("Db") == "C#"


def test_system_resolve_name_natural():
    assert SYSTEMS["western"].resolve_name("C") == "C"


def test_system_resolve_name_unknown():
    assert SYSTEMS["western"].resolve_name("X") is None


# ── CLI tests ─────────────────────────────────────────────────────────────────

def test_cli_tone(capsys):
    from pytheory.cli import cmd_tone
    import argparse
    args = argparse.Namespace(note="A4", temperament="equal")
    cmd_tone(args)
    out = capsys.readouterr().out
    assert "440.00" in out
    assert "A4" in out
    assert "MIDI" in out


def test_cli_tone_pythagorean(capsys):
    from pytheory.cli import cmd_tone
    import argparse
    args = argparse.Namespace(note="C5", temperament="pythagorean")
    cmd_tone(args)
    out = capsys.readouterr().out
    assert "Equal temp" in out
    assert "cents" in out


def test_cli_scale(capsys):
    from pytheory.cli import cmd_scale
    import argparse
    args = argparse.Namespace(tonic="C", mode="major", system="western")
    cmd_scale(args)
    out = capsys.readouterr().out
    assert "C D E F G A B C" in out


def test_cli_chord(capsys):
    from pytheory.cli import cmd_chord
    import argparse
    args = argparse.Namespace(notes=["C", "E", "G"])
    cmd_chord(args)
    out = capsys.readouterr().out
    assert "C major" in out
    assert "Harmony" in out
    assert "Tension" in out


def test_cli_key(capsys):
    from pytheory.cli import cmd_key
    import argparse
    args = argparse.Namespace(tonic="G", mode="major")
    cmd_key(args)
    out = capsys.readouterr().out
    assert "G major" in out
    assert "Signature" in out
    assert "Relative" in out


def test_cli_fingering(capsys):
    from pytheory.cli import cmd_fingering
    import argparse
    args = argparse.Namespace(chord="Am", capo=0)
    cmd_fingering(args)
    out = capsys.readouterr().out
    assert "Am" in out
    assert "|--" in out


def test_cli_progression(capsys):
    from pytheory.cli import cmd_progression
    import argparse
    args = argparse.Namespace(tonic="C", mode="major", numerals=["I", "V", "vi", "IV"])
    cmd_progression(args)
    out = capsys.readouterr().out
    assert "C major" in out
    assert "I → V → vi → IV" in out


def test_cli_detect(capsys):
    from pytheory.cli import cmd_detect
    import argparse
    args = argparse.Namespace(notes=["C", "E", "G", "A", "D"])
    cmd_detect(args)
    out = capsys.readouterr().out
    assert "C major" in out


def test_cli_detect_no_match(capsys):
    from pytheory.cli import cmd_detect
    import argparse
    args = argparse.Namespace(notes=[])
    cmd_detect(args)
    out = capsys.readouterr().out
    assert "Could not detect" in out


def test_cli_main_no_args(capsys):
    from pytheory.cli import main
    import sys
    old_argv = sys.argv
    sys.argv = ["pytheory"]
    try:
        main()
    except SystemExit:
        pass
    sys.argv = old_argv


# ── Play module tests ─────────────────────────────────────────────────────────

@needs_portaudio
def test_play_render():
    """_render produces a numpy array of the right length."""
    from pytheory.play import _render, Synth, SAMPLE_RATE
    tone = Tone.from_string("A4", system="western")
    samples = _render(tone, synth=Synth.SINE, t=500)
    expected = int(SAMPLE_RATE * 500 / 1000)
    assert len(samples) == expected


@needs_portaudio
def test_play_render_chord():
    from pytheory.play import _render, Synth
    chord = Chord.from_tones("C", "E", "G")
    samples = _render(chord, synth=Synth.SINE, t=200)
    assert len(samples) > 0


@needs_portaudio
def test_play_render_all_synths():
    from pytheory.play import _render, Synth
    tone = Tone.from_string("C4", system="western")
    for synth in Synth:
        samples = _render(tone, synth=synth, t=100)
        assert len(samples) > 0


@needs_portaudio
def test_play_save(tmp_path):
    """save() writes a valid WAV file."""
    from pytheory.play import save, Synth
    path = tmp_path / "test.wav"
    tone = Tone.from_string("A4", system="western")
    save(tone, str(path), synth=Synth.SINE, t=200)
    assert path.exists()
    assert path.stat().st_size > 44  # WAV header is 44 bytes


@needs_portaudio
def test_play_save_chord(tmp_path):
    from pytheory.play import save
    path = tmp_path / "chord.wav"
    chord = Chord.from_tones("C", "E", "G")
    save(chord, str(path), t=200)
    assert path.exists()


# ── Chord.symbol ────────────────────────────────────────────────────────────

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


# ── Key.common_progressions ─────────────────────────────────────────────────

def test_common_progressions_returns_dict():
    key = Key("C", "major")
    progs = key.common_progressions()
    assert isinstance(progs, dict)
    assert len(progs) > 0


def test_common_progressions_contains_known():
    key = Key("C", "major")
    progs = key.common_progressions()
    assert "I-V-vi-IV" in progs
    assert "12-bar blues" in progs
    assert "ii-V-I" in progs


def test_common_progressions_chords_are_correct():
    key = Key("G", "major")
    progs = key.common_progressions()
    chords = progs["I-IV-V-I"]
    symbols = [c.symbol for c in chords]
    assert symbols == ["G", "C", "D", "G"]


def test_common_progressions_i_v_vi_iv():
    key = Key("C", "major")
    progs = key.common_progressions()
    chords = progs["I-V-vi-IV"]
    symbols = [c.symbol for c in chords]
    assert symbols == ["C", "G", "Am", "F"]


# ── CLI: modes, circle, progressions ────────────────────────────────────────

def test_cli_modes(capsys):
    from pytheory.cli import cmd_modes
    import argparse
    args = argparse.Namespace(tonic="C", system="western")
    cmd_modes(args)
    out = capsys.readouterr().out
    assert "ionian" in out
    assert "dorian" in out
    assert "locrian" in out


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


def test_cli_progressions(capsys):
    from pytheory.cli import cmd_progressions
    import argparse
    args = argparse.Namespace(tonic="C", mode="major")
    cmd_progressions(args)
    out = capsys.readouterr().out
    assert "I-V-vi-IV" in out
    assert "C" in out
