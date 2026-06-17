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


def test_orientation_is_a_reversal():
    """The two orientations are exact reverses of each other."""
    lo = Fretboard.guitar().chord("Am7")
    hi = Fretboard.guitar(high_to_low=True).chord("Am7")
    assert lo.positions == tuple(reversed(hi.positions))
    # ...and identify to the same chord.
    assert lo.identify() == hi.identify()


def test_orientation_cache_no_collision():
    """The two orientations must not collide in the fingering cache."""
    lo = Fretboard.guitar().chord("C")
    hi = Fretboard.guitar(high_to_low=True).chord("C")
    assert lo.positions != hi.positions
    assert lo.positions == tuple(reversed(hi.positions))


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


def test_indian_bilawal_equals_western_major():
    """Bilawal intervals should match Western major."""
    indian = SYSTEMS["indian"]
    western = SYSTEMS["western"]
    bilawal = indian.scales["thaat"]["bilawal"]["intervals"]
    major = western.scales["heptatonic"]["major"]["intervals"]
    assert bilawal == major


def test_indian_chromatic_walk():
    """Walk all 12 swaras from Sa4."""
    sa = Tone.from_string("Sa4", system="indian")
    expected = ["Sa", "komal Re", "Re", "komal Ga", "Ga", "Ma",
                "tivra Ma", "Pa", "komal Dha", "Dha", "komal Ni", "Ni", "Sa"]
    for i, name in enumerate(expected):
        result = sa + i
        assert result.name == name, f"step {i}: expected {name}, got {result.name}"


def test_arabic_ajam_equals_western_major():
    arabic = SYSTEMS["arabic"]
    western = SYSTEMS["western"]
    ajam = arabic.scales["maqam"]["ajam"]["intervals"]
    major = western.scales["heptatonic"]["major"]["intervals"]
    assert ajam == major


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


def test_identify_diminished():
    chord = Chord(tones=[
        Tone.from_string("B4", system="western"),
        Tone.from_string("D5", system="western"),
        Tone.from_string("F5", system="western"),
    ])
    assert chord.identify() == "B diminished"


def test_version():
    import pytheory
    assert pytheory.__version__


def test_all_exports():
    import pytheory
    assert not hasattr(pytheory, "ceil")
    assert not hasattr(pytheory, "floor")
    assert "Tone" in pytheory.__all__


def test_note_from_string():
    n = Note.from_string("C4", system="western")
    assert n.name == "C"
    assert n.frequency == Tone.from_string("C4", system="western").frequency


def test_instruments_list():
    assert len(Fretboard.INSTRUMENTS) == 25
    assert "guitar" in Fretboard.INSTRUMENTS
    assert "sitar" in Fretboard.INSTRUMENTS
    assert "keyboard" in Fretboard.INSTRUMENTS


def test_from_symbol_major():
    c = Chord.from_symbol("C")
    assert c.identify() == "C major"


def test_from_symbol_minor():
    c = Chord.from_symbol("Am")
    assert c.identify() == "A minor"


def test_from_symbol_dominant_7th():
    c = Chord.from_symbol("G7")
    assert c.identify() == "G dominant 7th"


def test_from_symbol_major_7th():
    c = Chord.from_symbol("Cmaj7")
    assert c.identify() == "C major 7th"


def test_from_symbol_minor_7th():
    c = Chord.from_symbol("Dm7")
    assert c.identify() == "D minor 7th"


def test_from_symbol_diminished():
    c = Chord.from_symbol("Bdim")
    assert c.identify() == "B diminished"


def test_from_symbol_augmented():
    c = Chord.from_symbol("Caug")
    assert c.identify() == "C augmented"


def test_from_symbol_sus4():
    c = Chord.from_symbol("Csus4")
    assert c.identify() == "C sus4"


def test_from_symbol_sus2():
    c = Chord.from_symbol("Dsus2")
    assert c.identify() == "D sus2"


def test_from_symbol_power():
    c = Chord.from_symbol("C5")
    assert c.identify() == "C power"


def test_from_symbol_half_diminished():
    c = Chord.from_symbol("Bm7b5")
    assert c.identify() == "B half-diminished 7th"


def test_from_symbol_flat_root():
    c = Chord.from_symbol("Bbmaj7")
    assert c.symbol == "Bbmaj7"


def test_from_symbol_sharp_root():
    c = Chord.from_symbol("F#m")
    assert c.identify() == "F# minor"


def test_from_symbol_dim7():
    c = Chord.from_symbol("Cdim7")
    assert c.identify() == "C diminished 7th"


def test_from_symbol_9th():
    c = Chord.from_symbol("G9")
    assert c.identify() == "G dominant 9th"


def test_from_symbol_roundtrip():
    """from_symbol → symbol should round-trip."""
    for sym in ["C", "Am", "G7", "Dmaj7", "Em7", "Bdim", "Fsus4"]:
        c = Chord.from_symbol(sym)
        assert c.symbol == sym, f"Round-trip failed for {sym}: got {c.symbol}"


def test_from_symbol_invalid_raises():
    with pytest.raises(ValueError):
        Chord.from_symbol("Xmaj7")


def test_from_symbol_unknown_quality_raises():
    with pytest.raises(ValueError):
        Chord.from_symbol("Czzz")


def test_c_index_constant():
    from pytheory._statics import C_INDEX
    assert C_INDEX == 3


def test_fitness_perfect():
    c = TonedScale(tonic="C4")["major"]
    assert c.fitness("C", "D", "E", "F", "G") == 1.0


def test_fitness_none():
    c = TonedScale(tonic="C4")["major"]
    assert c.fitness("C#", "D#", "F#") == 0.0


def test_fitness_empty():
    c = TonedScale(tonic="C4")["major"]
    assert c.fitness() == 0.0


def test_fitness_single_match():
    c = TonedScale(tonic="C4")["major"]
    assert c.fitness("C") == 1.0


def test_fitness_single_miss():
    c = TonedScale(tonic="C4")["major"]
    assert c.fitness("C#") == 0.0


def test_scientific_is_full_name():
    t = Tone.from_string("A4", system="western")
    assert t.scientific == t.full_name


def test_slash_name_different_bass():
    c = Chord.from_symbol("C")
    c_over_e = c.slash("E")
    assert c_over_e.slash_name == "C/E"


def test_slash_name_root_bass():
    c = Chord.from_symbol("C")
    c_over_c = c.slash("C")
    assert c_over_c.slash_name == "C"


def test_degree_name_tonic():
    scale = TonedScale(tonic="C4")["major"]
    assert scale.degree_name(0) == "tonic"


def test_degree_name_dominant():
    scale = TonedScale(tonic="C4")["major"]
    assert scale.degree_name(4) == "dominant"


def test_degree_name_subtonic_minor():
    scale = TonedScale(tonic="C4")["minor"]
    assert scale.degree_name(6, minor=True) == "subtonic"


def test_degree_name_all_major():
    scale = TonedScale(tonic="C4")["major"]
    expected = ["tonic", "supertonic", "mediant", "subdominant",
                "dominant", "submediant", "leading tone"]
    for i, name in enumerate(expected):
        assert scale.degree_name(i) == name


def test_degree_name_out_of_range():
    scale = TonedScale(tonic="C4")["major"]
    assert scale.degree_name(10) == "degree 10"


def test_rhythm_note_creation():
    t = Tone.from_string("C4")
    n = RhythmNote(tone=t, duration=Duration.QUARTER)
    assert n.tone is t
    assert n.duration is Duration.QUARTER
    assert n.beats == 1.0


def test_backwards_compat_add():
    """Score.add() still works without named parts."""
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    score.add(Chord.from_symbol("C"), Duration.WHOLE)
    assert len(score.notes) == 1
    assert score.total_beats == 4.0


@needs_portaudio
def test_square_wave():
    from pytheory.play import square_wave, SAMPLE_RATE
    wave = square_wave(440)
    assert len(wave) == SAMPLE_RATE
    # Square wave should only have values at +peak and -peak
    unique = set(numpy.unique(wave))
    assert len(unique) <= 3  # +peak, -peak, possibly 0 at zero crossings


@needs_portaudio
def test_pulse_wave():
    from pytheory.play import pulse_wave, SAMPLE_RATE
    wave = pulse_wave(440, duty=0.25)
    assert len(wave) == SAMPLE_RATE


@needs_portaudio
def test_pulse_wave_duty_affects_timbre():
    from pytheory.play import pulse_wave
    narrow = pulse_wave(440, duty=0.125, n_samples=1000)
    wide = pulse_wave(440, duty=0.5, n_samples=1000)
    # Different duty cycles produce different waveforms
    assert not numpy.array_equal(narrow, wide)


@needs_portaudio
def test_fm_wave():
    from pytheory.play import fm_wave, SAMPLE_RATE
    wave = fm_wave(440)
    assert len(wave) == SAMPLE_RATE
    # FM should produce a more complex waveform than sine
    assert len(numpy.unique(wave)) > 100


@needs_portaudio
def test_fm_wave_params():
    from pytheory.play import fm_wave
    bell = fm_wave(440, mod_ratio=3.5, mod_index=5, n_samples=1000)
    piano = fm_wave(440, mod_ratio=1, mod_index=1.5, n_samples=1000)
    assert not numpy.array_equal(bell, piano)


@needs_portaudio
def test_noise_wave():
    from pytheory.play import noise_wave, SAMPLE_RATE
    wave = noise_wave(n_samples=SAMPLE_RATE)
    assert len(wave) == SAMPLE_RATE
    # Still broadband noise: wide amplitude spread, near-zero mean.
    assert wave.std() > 1000
    assert abs(float(wave.mean())) < 200
    # Now seeded by pitch: reproducible for a given hz...
    assert numpy.array_equal(noise_wave(220, n_samples=SAMPLE_RATE),
                             noise_wave(220, n_samples=SAMPLE_RATE))
    # ...but a different note gives a different noise realisation.
    assert not numpy.array_equal(noise_wave(220, n_samples=SAMPLE_RATE),
                                 noise_wave(440, n_samples=SAMPLE_RATE))


@needs_portaudio
def test_supersaw_wave():
    from pytheory.play import supersaw_wave, sawtooth_wave, SAMPLE_RATE
    wave = supersaw_wave(440)
    assert len(wave) == SAMPLE_RATE


@needs_portaudio
def test_lowpass_filter():
    from pytheory.play import _apply_lowpass, SAMPLE_RATE
    t = numpy.arange(44100, dtype=numpy.float32) / SAMPLE_RATE
    signal = numpy.sin(2 * numpy.pi * 100 * t) + numpy.sin(2 * numpy.pi * 5000 * t)
    filtered = _apply_lowpass(signal.astype(numpy.float32), cutoff=500)
    rms_orig = numpy.sqrt(numpy.mean(signal[22050:] ** 2))
    rms_filt = numpy.sqrt(numpy.mean(filtered[22050:] ** 2))
    assert rms_filt < rms_orig


@needs_portaudio
def test_lowpass_with_resonance():
    from pytheory.play import _apply_lowpass
    t = numpy.arange(44100, dtype=numpy.float32) / 44100
    signal = numpy.sin(2 * numpy.pi * 1000 * t).astype(numpy.float32)
    flat = _apply_lowpass(signal, cutoff=1000, q=0.707)
    resonant = _apply_lowpass(signal, cutoff=1000, q=5.0)
    assert numpy.max(numpy.abs(resonant)) > numpy.max(numpy.abs(flat))


def test_note_velocity_default():
    from pytheory.rhythm import Note, Duration
    n = Note(tone=None, duration=Duration.QUARTER)
    assert n.velocity == 100


def test_note_velocity_custom():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead")
    lead.add("C5", Duration.QUARTER, velocity=60)
    assert lead.notes[0].velocity == 60


def test_fade_in():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", volume=0.8)
    lead.fade_in(bars=2)
    # Should generate automation points with ascending volume
    volumes = [p["volume"] for _, p in lead._automation]
    assert len(volumes) > 0
    assert volumes[0] == pytest.approx(0.0)
    assert volumes[-1] == pytest.approx(0.8)
    # Check ascending order
    for i in range(1, len(volumes)):
        assert volumes[i] >= volumes[i - 1]


def test_fade_out():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    lead = score.part("lead", volume=0.8)
    lead.fade_out(bars=2)
    # Should generate automation points with descending volume
    volumes = [p["volume"] for _, p in lead._automation]
    assert len(volumes) > 0
    assert volumes[0] == pytest.approx(0.8)
    assert volumes[-1] == pytest.approx(0.0)
    # Check descending order
    for i in range(1, len(volumes)):
        assert volumes[i] <= volumes[i - 1]


def test_normal_form():
    chord = Chord.from_tones("C", "E", "G")
    assert chord.normal_form == (0, 4, 7)


def test_prime_form_major():
    # Major and minor triads share the same prime form (0, 3, 7)
    # because C major (0,4,7) inverts to (0,5,8) -> normal form (0,3,7)
    chord = Chord.from_tones("C", "E", "G")
    assert chord.prime_form == (0, 3, 7)


def test_prime_form_minor():
    # Minor triad: A C E has intervals 0,3,7 which inverts to 0,5,9
    # Normal form of inversion: best compact = (0,3,7) via inversion check
    chord = Chord.from_tones("A", "C", "E")
    assert chord.prime_form == (0, 3, 7)


def test_recommend_c_major_notes():
    from pytheory.scales import Scale
    results = Scale.recommend("C", "D", "E", "F", "G", "A", "B")
    assert len(results) > 0
    assert results[0][2] == 1.0  # perfect match
    # Chromatic should NOT be the top result
    assert "chromatic" not in results[0][1]


def test_recommend_returns_top():
    from pytheory.scales import Scale
    results = Scale.recommend("C", "E", "G", top=3)
    assert len(results) <= 3


def test_recommend_empty():
    from pytheory.scales import Scale
    assert Scale.recommend() == []


def test_recommend_fitness_descending():
    from pytheory.scales import Scale
    results = Scale.recommend("C", "D", "E", "F#", "G")
    for i in range(len(results) - 1):
        assert results[i][2] >= results[i + 1][2]


def test_instrument_piano():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    p = score.part("p", instrument="piano")
    assert p.synth == "piano_synth"
    assert p.vel_to_filter == 3000


def test_instrument_violin():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    p = score.part("v", instrument="violin")
    assert p.synth == "strings_synth"
    assert p.envelope == "bowed"
    assert p.humanize == 0.15
    assert p.lowpass == 5000
    assert p.detune == 2


def test_instrument_override():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    # Explicit synth overrides the preset
    p = score.part("p", instrument="piano", synth="saw")
    assert p.synth == "saw"


def test_instrument_unknown_raises():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    with pytest.raises(ValueError, match="Unknown instrument"):
        score.part("x", instrument="kazoo")


def test_list_instruments():
    from pytheory import Score, INSTRUMENTS
    result = Score.list_instruments()
    assert isinstance(result, list)
    assert result == sorted(result)
    assert "piano" in result
    assert "violin" in result
    assert "808_bass" in result
    assert len(result) == len(INSTRUMENTS)


def test_instrument_808_bass():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    p = score.part("b", instrument="808_bass")
    assert p.distortion_mix == 0.4
    assert p.distortion_drive == 2.5
    assert p.lowpass == 200
    assert p.lowpass_q == 1.5
    assert p.synth == "sine"
    assert p.envelope == "piano"


def test_cello_has_vibrato():
    """Cello synth should produce pitch variation (vibrato)."""
    from pytheory.play import cello_wave
    wave = cello_wave(220, n_samples=44100)
    assert len(wave) == 44100
    assert numpy.abs(wave).max() > 0


def test_cabinet_reduces_highs():
    """Cabinet sim should reduce high-frequency content."""
    from pytheory.play import _apply_cabinet
    # White noise has flat spectrum
    noise = numpy.random.uniform(-1, 1, 44100).astype(numpy.float32)
    cabbed = _apply_cabinet(noise, brightness=0.5)
    # RMS of cabbed should be lower (energy removed by filters)
    assert numpy.sqrt(numpy.mean(cabbed ** 2)) < numpy.sqrt(numpy.mean(noise ** 2))


def test_cabinet_brightness_param():
    """Higher brightness = more high-frequency content passes through."""
    from pytheory.play import _apply_cabinet
    noise = numpy.random.uniform(-1, 1, 44100).astype(numpy.float32)
    dark = _apply_cabinet(noise, brightness=0.0)
    bright = _apply_cabinet(noise, brightness=1.0)
    # Bright should have more energy than dark
    assert numpy.sqrt(numpy.mean(bright ** 2)) > numpy.sqrt(numpy.mean(dark ** 2))


def test_strum_adds_notes():
    """Strumming should add notes to the part."""
    from pytheory import Score, Duration, Fretboard
    score = Score("4/4", bpm=120)
    fb = Fretboard.guitar()
    p = score.part("g", instrument="acoustic_guitar", fretboard=fb)
    p.strum("Am", Duration.HALF)
    assert len(p.notes) > 0


def test_strum_direction():
    """Both down and up strums should work."""
    from pytheory import Score, Duration, Fretboard
    score = Score("4/4", bpm=120)
    fb = Fretboard.guitar()
    p = score.part("g", instrument="acoustic_guitar", fretboard=fb)
    p.strum("G", Duration.QUARTER, direction="down")
    p.strum("G", Duration.QUARTER, direction="up")
    assert len(p.notes) >= 2  # grace notes + chord per strum


def test_vocal_different_vowels_differ():
    """Different vowels should produce different waveforms."""
    from pytheory.play import vocal_wave
    ah = vocal_wave(330, n_samples=22050, lyric="ah")
    ee = vocal_wave(330, n_samples=22050, lyric="ee")
    # They should differ (different formant peaks)
    assert not numpy.array_equal(ah, ee)


def test_all_instrument_presets_create():
    """Every instrument preset in INSTRUMENTS should create a valid Part."""
    from pytheory import Score
    from pytheory.rhythm import INSTRUMENTS
    for name in INSTRUMENTS:
        score = Score("4/4", bpm=120)
        p = score.part("test", instrument=name)
        assert p.synth is not None


def test_new_instrument_presets():
    """New instrument presets have correct synths."""
    from pytheory import Score
    presets = {
        "pedal_steel": "pedal_steel_synth",
        "theremin": "theremin_synth",
        "kalimba": "kalimba_synth",
        "steel_drum": "steel_drum_synth",
        "accordion": "accordion_synth",
        "didgeridoo": "didgeridoo_synth",
        "bagpipe": "bagpipe_synth",
        "banjo": "banjo_synth",
        "mandolin": "mandolin_synth",
        "ukulele": "ukulele_synth",
    }
    for name, expected_synth in presets.items():
        score = Score("4/4", bpm=120)
        p = score.part("t", instrument=name)
        assert p.synth == expected_synth, f"{name} has {p.synth}, expected {expected_synth}"


def test_roll_adds_notes():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    p = score.part("t", instrument="timpani")
    p.roll("C3", Duration.WHOLE, velocity_start=30, velocity_end=100)
    assert len(p.notes) > 4  # should be many 16th notes


def test_roll_velocity_ramp():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    p = score.part("t", instrument="timpani")
    p.roll("C3", Duration.WHOLE, velocity_start=20, velocity_end=100)
    velocities = [n.velocity for n in p.notes]
    # First should be quieter than last
    assert velocities[0] < velocities[-1]


def test_roll_custom_speed():
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    p = score.part("t", synth="sine")
    p.roll("A4", Duration.WHOLE, speed=0.125)  # 32nd notes
    # 4 beats / 0.125 = 32 notes
    assert len(p.notes) == 32


def test_articulation_field_on_note():
    from pytheory.rhythm import Note, Duration
    n = Note(tone=None, duration=Duration.QUARTER, articulation="staccato")
    assert n.articulation == "staccato"


def test_articulation_default_empty():
    from pytheory.rhythm import Note, Duration
    n = Note(tone=None, duration=Duration.QUARTER)
    assert n.articulation == ""


def test_crescendo_adds_notes():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine")
    p.crescendo(["C4", "D4", "E4", "F4"], Duration.QUARTER,
                start_vel=40, end_vel=100)
    assert len(p.notes) == 4
    assert p.notes[0].velocity == 40
    assert p.notes[3].velocity == 100


def test_decrescendo_adds_notes():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine")
    p.decrescendo(["C4", "D4", "E4", "F4"], Duration.QUARTER,
                  start_vel=110, end_vel=40)
    assert len(p.notes) == 4
    assert p.notes[0].velocity == 110
    assert p.notes[3].velocity == 40


def test_swell_velocity_shape():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine")
    p.swell(["C4", "D4", "E4", "F4", "G4"], Duration.QUARTER,
            low_vel=30, peak_vel=110)
    assert len(p.notes) == 5
    # First and last should be near low_vel
    assert p.notes[0].velocity == 30
    assert p.notes[4].velocity == 30
    # Middle should be at or near peak
    assert p.notes[2].velocity == 110


def test_dynamics_custom_velocities():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine")
    p.dynamics(["C4", "D4", "E4"], Duration.QUARTER,
               velocities=[50, 100, 75])
    assert p.notes[0].velocity == 50
    assert p.notes[1].velocity == 100
    assert p.notes[2].velocity == 75


def test_dynamics_with_articulation():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="sine")
    p.crescendo(["C4", "D4"], Duration.QUARTER,
                start_vel=40, end_vel=100, articulation="staccato")
    assert p.notes[0].articulation == "staccato"
    assert p.notes[1].articulation == "staccato"


def test_ramp_easing_curves():
    score = pytheory.Score("4/4", bpm=120)
    for curve in ["linear", "ease_in", "ease_out", "ease_in_out"]:
        p = score.part(f"test_{curve}", synth="saw", lowpass=200)
        p.ramp(over=4.0, curve=curve, lowpass=8000)
        assert len(p._automation) > 0


def test_ramp_multiple_params():
    score = pytheory.Score("4/4", bpm=120)
    p = score.part("test", synth="saw", lowpass=200)
    p.ramp(over=4.0, lowpass=8000, reverb=0.5)
    # Should have both params in automation points
    last_point = p._automation[-1][1]
    assert "lowpass" in last_point
    assert "reverb_mix" in last_point  # mapped from "reverb"


def test_choir_vowel_morph_glides_formants():
    from pytheory.play import choir_wave, SAMPLE_RATE

    def f1_ratio(seg):
        spec = numpy.abs(numpy.fft.rfft(seg.astype(numpy.float64)))
        freqs = numpy.fft.rfftfreq(len(seg), 1 / SAMPLE_RATE)
        hi = spec[(freqs >= 550) & (freqs < 950)].sum()
        lo = spec[(freqs >= 200) & (freqs < 420)].sum()
        return hi / (lo + 1e-9)

    n = SAMPLE_RATE * 2
    morph = choir_wave(220, n_samples=n, lyric="ah>oo")
    start = morph[int(0.2 * SAMPLE_RATE):int(0.6 * SAMPLE_RATE)]
    end = morph[int(1.6 * SAMPLE_RATE):]
    # "ah" has F1 ≈ 730 Hz, "oo" has F1 ≈ 300 Hz: the energy balance
    # between those regions must flip across the note.
    assert f1_ratio(start) > 5.0
    assert f1_ratio(end) < 1.0


def test_choir_vowel_morph_three_vowel_chain():
    from pytheory.play import choir_wave, SAMPLE_RATE
    wave = choir_wave(220, n_samples=SAMPLE_RATE, lyric="ah>ee>oo")
    assert len(wave) == SAMPLE_RATE
    assert numpy.isfinite(wave.astype(numpy.float64)).all()
    assert numpy.abs(wave).max() > 0


def test_choir_static_vowel_unchanged_by_morph_support():
    from pytheory.play import choir_wave, SAMPLE_RATE
    ah = choir_wave(220, n_samples=SAMPLE_RATE // 2, lyric="ah")
    morph = choir_wave(220, n_samples=SAMPLE_RATE // 2, lyric="ah>oo")
    assert not numpy.array_equal(ah, morph)


def test_piano_darkens_as_it_decays():
    from pytheory.play import piano_wave, SAMPLE_RATE
    n = SAMPLE_RATE * 2
    w = piano_wave(261.63, n_samples=n).astype(numpy.float64)

    def hi_lo(seg):
        spec = numpy.abs(numpy.fft.rfft(seg * numpy.hanning(len(seg)))) ** 2
        f = numpy.fft.rfftfreq(len(seg), 1 / SAMPLE_RATE)
        return (spec[(f > 1500) & (f < 8000)].sum()
                / spec[(f > 100) & (f < 800)].sum())

    early = w[int(0.05 * SAMPLE_RATE):int(0.55 * SAMPLE_RATE)]
    late = w[int(1.5 * SAMPLE_RATE):]
    assert hi_lo(late) < hi_lo(early) * 0.2


def test_piano_register_decay():
    """Treble notes die quickly; bass notes ring on."""
    from pytheory.play import piano_wave, SAMPLE_RATE
    n = SAMPLE_RATE * 2

    def late_over_early(hz):
        w = piano_wave(hz, n_samples=n).astype(numpy.float64)
        early = numpy.sqrt((w[:SAMPLE_RATE // 4] ** 2).mean())
        late = numpy.sqrt((w[int(1.5 * SAMPLE_RATE):] ** 2).mean())
        return late / early

    assert late_over_early(27.5) > 0.2     # A0 still blooming
    assert late_over_early(2093) < 0.05    # C7 essentially gone


def test_load_wav_normalizes_stereo_int16():
    import os, tempfile
    from pytheory.audio import load_wav
    sr = 44100
    t = numpy.arange(sr) / sr
    sig = numpy.sin(2 * numpy.pi * 440 * t) * 0.9
    stereo = numpy.stack([sig, sig], axis=1).astype(numpy.float32)
    path = tempfile.mktemp(suffix=".wav")
    _write_test_wav(stereo, path)
    try:
        samples, _ = load_wav(path)
    finally:
        os.unlink(path)
    assert 0.5 < numpy.abs(samples).max() <= 1.0


def test_load_m4a_via_converter():
    import os, shutil, subprocess, tempfile
    if not (shutil.which("afconvert") or shutil.which("ffmpeg")):
        import pytest
        pytest.skip("no audio converter available")
    from pytheory.audio import load_wav
    sr = 44100
    t = numpy.arange(sr) / sr
    sig = numpy.sin(2 * numpy.pi * 440 * t) * 0.8
    stereo = numpy.stack([sig, sig], axis=1).astype(numpy.float32)
    wav_path = tempfile.mktemp(suffix=".wav")
    m4a_path = tempfile.mktemp(suffix=".m4a")
    _write_test_wav(stereo, wav_path)
    try:
        if shutil.which("afconvert"):
            subprocess.run(["afconvert", "-f", "m4af", "-d", "aac",
                            wav_path, m4a_path],
                           check=True, capture_output=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-i", wav_path, m4a_path],
                           check=True, capture_output=True)
        samples, rate = load_wav(m4a_path)
    finally:
        os.unlink(wav_path)
        if os.path.exists(m4a_path):
            os.unlink(m4a_path)
    assert rate == 44100
    assert abs(len(samples) / rate - 1.0) < 0.15


def test_studio_server_endpoints():
    import io
    import json
    import threading
    import time
    import urllib.request
    import wave as wavemod
    from pytheory.studio import serve
    from pytheory.rhythm import Score
    from pytheory.play import render_score

    port = 8341
    th = threading.Thread(target=serve,
                          kwargs={"port": port, "open_browser": False},
                          daemon=True)
    th.start()
    time.sleep(0.6)
    base = f"http://localhost:{port}"

    page = urllib.request.urlopen(base + "/", timeout=10).read().decode()
    assert "PyTheory Studio" in page and "abcjs" in page

    s = Score(bpm=100)
    p = s.part("m", synth="sine", volume=0.7)
    for n in ["C4", "E4", "G4"]:
        p.add(n, 0.5)
    data = (numpy.clip(render_score(s), -1, 1) * 32767).astype(numpy.int16)
    out = io.BytesIO()
    with wavemod.open(out, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(data.tobytes())

    req = urllib.request.Request(
        base + "/transcribe?name=t.wav&bpm=100&quantize=0.25",
        data=out.getvalue(), method="POST")
    res = json.loads(urllib.request.urlopen(req, timeout=60).read())
    assert res["bpm"] == 100
    assert res["parts"]["melody"] == 3
    assert "T:t" in res["abc"]

    wav = urllib.request.urlopen(
        f"{base}/render?id={res['id']}", timeout=60).read()
    assert wav[:4] == b"RIFF"
    mid = urllib.request.urlopen(
        f"{base}/midi?id={res['id']}", timeout=30).read()
    assert mid[:4] == b"MThd"
