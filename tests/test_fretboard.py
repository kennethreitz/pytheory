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


def test_fretboard_creation():
    standard_tuning = [
        Tone(name="E", octave=4),
        Tone(name="B", octave=3),
        Tone(name="G", octave=3),
        Tone(name="D", octave=3),
        Tone(name="A", octave=2),
        Tone(name="E", octave=2),
    ]
    # Literal is written high-to-low, so declare that orientation.
    fretboard = Fretboard(tones=standard_tuning, high_to_low=True)
    assert len(fretboard.tones) == 6
    assert fretboard.tones[0].full_name == "E4"
    assert fretboard.tones[-1].full_name == "E2"


def test_fretboard_repr():
    fretboard = Fretboard(tones=[Tone(name="E", octave=4)])
    assert "E4" in repr(fretboard)


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


def test_chord_fingering_wrong_positions_raises():
    chord = Chord(tones=[
        Tone.from_string("C4", system="western"),
        Tone.from_string("E4", system="western"),
    ])
    with pytest.raises(ValueError, match="positions"):
        chord.fingering(1, 2, 3)  # 3 positions for 2 tones


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


def test_fretboard_guitar():
    fb = Fretboard.guitar()
    assert len(fb) == 6
    # Low-to-high by default (v0.43.0).
    names = [t.name for t in fb]
    assert names == ["E", "A", "D", "G", "B", "E"]
    # high_to_low=True restores the pre-0.43 order.
    assert [t.name for t in Fretboard.guitar(high_to_low=True)] == \
        ["E", "B", "G", "D", "A", "E"]


def test_fretboard_guitar_octaves():
    fb = Fretboard.guitar()
    octaves = [t.octave for t in fb]
    assert octaves == [2, 2, 3, 3, 3, 4]


def test_fretboard_bass():
    fb = Fretboard.bass()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["E", "A", "D", "G"]


def test_fretboard_ukulele():
    fb = Fretboard.ukulele()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["G", "C", "E", "A"]


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
    # Low-to-high: the dropped low D is now the first string.
    assert fb.tones[0].name == "D"
    assert fb.tones[0].octave == 2


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
    # Low-to-high: the added low B is the first string.
    assert fb.tones[0].name == "B"


def test_fretboard_tunings_dict():
    for name in Fretboard.TUNINGS:
        fb = Fretboard.guitar(name)
        assert len(fb) == 6, f"Tuning {name} should have 6 strings"


def test_fretboard_mandolin():
    fb = Fretboard.mandolin()
    assert len(fb) == 4
    # Low-to-high.
    assert fb.tones[0].name == "G"
    assert fb.tones[-1].name == "E"


def test_fretboard_violin():
    fb = Fretboard.violin()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["G", "D", "A", "E"]


def test_fretboard_viola():
    fb = Fretboard.viola()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["C", "G", "D", "A"]


def test_fretboard_cello():
    fb = Fretboard.cello()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["C", "G", "D", "A"]
    assert fb.tones[0].octave == 2


def test_fretboard_banjo():
    fb = Fretboard.banjo()
    assert len(fb) == 5
    assert fb.tones[0].name == "G"  # high drone string (now first, low-to-high)


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
        # Low-to-high: each next string is a 5th higher.
        interval = fb.tones[i + 1] - fb.tones[i]
        assert interval == 7, f"Strings {i} and {i+1} not a 5th apart"


def test_fretboard_octave_mandolin():
    fb = Fretboard.octave_mandolin()
    assert len(fb) == 4
    assert fb.tones[-1].name == "E"
    assert fb.tones[-1].octave == 4


def test_fretboard_mandocello():
    fb = Fretboard.mandocello()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["C", "G", "D", "A"]
    assert fb.tones[0].octave == 2


def test_fretboard_double_bass():
    fb = Fretboard.double_bass()
    assert len(fb) == 4
    names = [t.name for t in fb]
    assert names == ["E", "A", "D", "G"]


def test_fretboard_double_bass_tuned_in_fourths():
    fb = Fretboard.double_bass()
    for i in range(len(fb.tones) - 1):
        # Low-to-high: each next string is a 4th higher.
        interval = fb.tones[i + 1] - fb.tones[i]
        assert interval == 5, f"Strings {i} and {i+1} not a 4th apart"


def test_fretboard_harp():
    fb = Fretboard.harp()
    assert len(fb) == 47
    # Low-to-high.
    assert fb.tones[0].name == "C"
    assert fb.tones[0].octave == 1
    assert fb.tones[-1].name == "G"
    assert fb.tones[-1].octave == 7


def test_fretboard_pedal_steel():
    fb = Fretboard.pedal_steel()
    assert len(fb) == 10


def test_mandolin_family_fifths():
    """All mandolin family instruments should be tuned in 5ths."""
    for name in ["mandolin", "mandola", "octave_mandolin", "mandocello"]:
        fb = getattr(Fretboard, name)()
        for i in range(len(fb.tones) - 1):
            interval = fb.tones[i + 1] - fb.tones[i]
            assert interval == 7, f"{name} strings {i},{i+1} not a 5th apart"


def test_fretboard_oud():
    fb = Fretboard.oud()
    assert len(fb) == 6


def test_fretboard_shamisen():
    fb = Fretboard.shamisen()
    assert len(fb) == 3


def test_fretboard_erhu():
    fb = Fretboard.erhu()
    assert len(fb) == 2
    assert fb.tones[1] - fb.tones[0] == 7  # tuned in 5ths (low-to-high)


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
    # Two unison strings (now the lowest two, low-to-high)
    assert fb.tones[0].name == fb.tones[1].name


def test_fretboard_lute():
    fb = Fretboard.lute()
    assert len(fb) == 6


def test_fretboard_sitar():
    fb = Fretboard.sitar()
    assert len(fb) == 7


def test_fretboard_pipa():
    fb = Fretboard.pipa()
    assert len(fb) == 4


def test_manual_fingering_input_orientation():
    """Manual fret positions are read in the board's orientation."""
    lo = Fretboard.guitar()
    hi = Fretboard.guitar(high_to_low=True)
    # Same physical G voicing, expressed in each orientation.
    assert lo.fingering(3, 2, 0, 0, 0, 3) == lo.chord("G")
    assert hi.fingering(3, 0, 0, 0, 2, 3) == hi.chord("G")


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


def test_scale_diagram():
    fb = Fretboard.guitar()
    scale = TonedScale(tonic="C4")["major"]
    diagram = fb.scale_diagram(scale, frets=5)
    assert "E|" in diagram
    lines = diagram.strip().split("\n")
    assert len(lines) == 7


def test_scale_diagram_enharmonic_flat_note():
    """A flat-spelled scale note (e.g. the blues Eb) must render even
    though the fretboard spells that pitch as D#."""
    fb = Fretboard.guitar()
    blues = TonedScale(tonic="A4", system="blues")["blues"]
    assert "Eb" in blues.note_names
    diagram = fb.scale_diagram(blues, frets=12)
    # The blue note shows up using the scale's own (flat) spelling,
    # never the fretboard's sharp spelling.
    assert "Eb" in diagram
    assert "D#" not in diagram


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


def _tab_string_order(tab):
    """The string labels of a tab block, top line to bottom line."""
    return [line.split("|", 1)[0] for line in tab.strip().splitlines()[1:]]


def test_tab_high_string_on_top():
    """ASCII tab must put the highest-pitched string (high e) on top and
    the lowest (low E) on the bottom — the standard tab convention."""
    fb = Fretboard.guitar()
    order = _tab_string_order(fb.chord("C").tab())
    assert order == ["e", "B", "G", "D", "A", "E"]


def test_tab_orientation_independent_of_board():
    """Tab orientation is a fixed display convention: a high_to_low board
    and the default board render the same chord identically."""
    lo = Fretboard.guitar().chord("G").tab()
    hi = Fretboard.guitar(high_to_low=True).chord("G").tab()
    assert lo == hi
    assert _tab_string_order(lo)[0] == "e"  # high e on top either way


def test_fretboard_tab_method_orientation():
    """Fretboard.tab() and NamedChord.tab() share the high-e-on-top order."""
    from pytheory.charts import CHARTS
    fb = Fretboard.guitar()
    assert _tab_string_order(fb.tab("Am")) == ["e", "B", "G", "D", "A", "E"]
    named = CHARTS["western"]["Am"].tab(fretboard=fb)
    assert _tab_string_order(named) == ["e", "B", "G", "D", "A", "E"]


def test_cli_fingering(capsys):
    from pytheory.cli import cmd_fingering
    import argparse
    args = argparse.Namespace(chord="Am", capo=0)
    cmd_fingering(args)
    out = capsys.readouterr().out
    assert "Am" in out
    assert "|--" in out


def test_scale_diagram_chord_highlight():
    fb = Fretboard.guitar()
    scale = TonedScale(tonic="A4")["minor"]
    am = Chord.from_symbol("Am")
    diagram = fb.scale_diagram(scale, frets=5, chord=am)
    # Chord tones (A, C, E) should be uppercase
    assert "A " in diagram or "A|" in diagram
    assert "C " in diagram
    assert "E " in diagram
    # Non-chord scale tones should be lowercase
    assert "d " in diagram or "d|" in diagram


def test_scale_diagram_no_chord_unchanged():
    fb = Fretboard.guitar()
    scale = TonedScale(tonic="C4")["major"]
    diagram = fb.scale_diagram(scale, frets=3)
    # Without chord arg, should have normal case
    assert "C " in diagram
    assert "E " in diagram


def test_acoustic_guitar_body_resonance():
    """Acoustic guitar should produce richer spectrum than raw pluck."""
    from pytheory.play import acoustic_guitar_wave, pluck_wave
    ag = acoustic_guitar_wave(220, n_samples=22050)
    pk = pluck_wave(220, n_samples=22050)
    assert len(ag) == len(pk) == 22050


def test_strum_requires_fretboard():
    """Strumming without a fretboard should raise ValueError."""
    from pytheory import Score, Duration
    score = Score("4/4", bpm=120)
    p = score.part("g", synth="saw")
    with pytest.raises(ValueError, match="fretboard"):
        p.strum("Am", Duration.QUARTER)


def test_tabla_sounds_render():
    """All tabla drum sounds should produce valid audio."""
    from pytheory.play import _render_drum_hit
    from pytheory.rhythm import DrumSound
    for sound in [DrumSound.TABLA_NA, DrumSound.TABLA_TIN, DrumSound.TABLA_GE,
                  DrumSound.TABLA_DHA, DrumSound.TABLA_TIT, DrumSound.TABLA_KE]:
        wave = _render_drum_hit(sound.value, 22050)
        assert len(wave) == 22050
        assert wave.dtype == numpy.float32


def test_tabla_pattern_presets():
    """All tabla patterns should load without error."""
    from pytheory.rhythm import Pattern
    for name in ["teental", "jhaptaal", "rupak", "dadra",
                 "keherwa", "tabla solo", "tiri kita"]:
        p = Pattern.preset(name)
        assert p.beats > 0


def test_guitar_presets_have_cabinet():
    """Distorted guitar presets should have cabinet simulation."""
    from pytheory import Score
    for preset in ["distorted_guitar", "orange_crunch", "metal_guitar"]:
        score = Score("4/4", bpm=120)
        p = score.part("g", instrument=preset)
        assert p.cabinet > 0, f"{preset} should have cabinet sim"


def test_clean_guitar_preset():
    from pytheory import Score
    score = Score("4/4", bpm=120)
    p = score.part("g", instrument="clean_guitar")
    assert p.synth == "electric_guitar_synth"
    assert p.cabinet > 0


def test_live_sustaining_instrument_loops_past_wavetable():
    from pytheory.live import _Channel
    sr = 44100
    ch = _Channel(synth_name="organ", envelope_name="organ", volume=0.5)
    ch.note_on(60, 100)
    assert ch.voices[0].loop_end is not None
    blocks = [ch.render_stereo(512) for _ in range(int(4.5 * sr / 512))]
    audio = numpy.concatenate(blocks)
    late = audio[int(4.0 * sr):int(4.3 * sr)]
    assert numpy.sqrt((late ** 2).mean()) > 0.01  # still sounding at 4s
    assert len(ch.voices) == 1                    # voice never died
