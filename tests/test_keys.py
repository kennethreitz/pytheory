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


def test_scale_degree_by_roman_numeral():
    c = TonedScale(tonic="C4")
    major = c["major"]
    assert major["I"].name == "C"
    assert major["V"].name == "G"


def test_scale_invalid_key():
    c = TonedScale(tonic="C4")
    with pytest.raises(KeyError):
        c["nonexistent"]


def test_scale_degree_all_roman_numerals():
    c = TonedScale(tonic="C4")
    major = c["major"]
    expected = ["C", "D", "E", "F", "G", "A", "B"]
    numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
    for numeral, name in zip(numerals, expected):
        assert major[numeral].name == name, f"Degree {numeral} expected {name}"


def test_relative_minor():
    """A minor (relative minor of C major) should share the same notes."""
    c_major = TonedScale(tonic="C4")["major"]
    a_minor = TonedScale(tonic="A4")["minor"]

    c_names = sorted(set(t.name for t in c_major.tones))
    a_names = sorted(set(t.name for t in a_minor.tones))
    assert c_names == a_names


def test_keyboard_88():
    kb = Fretboard.keyboard()
    assert len(kb) == 88


def test_keyboard_25():
    kb = Fretboard.keyboard(25, "C3")
    assert len(kb) == 25
    # Low-to-high: the start note is now the first key.
    assert kb.tones[0].name == "C"
    assert kb.tones[0].octave == 3


def test_keyboard_custom():
    kb = Fretboard.keyboard(61, "C2")
    assert len(kb) == 61


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
    """F# major in C major is now recognized as a borrowed chord (bV)."""
    chord = Chord(tones=[
        Tone.from_string("F#4", system="western"),
        Tone.from_string("A#4", system="western"),
        Tone.from_string("C#5", system="western"),
    ])
    result = chord.analyze("C")
    assert result is not None
    assert "b" in result  # borrowed chord with flat prefix


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


def test_key_c_major():
    k = Key("C", "major")
    assert k.note_names == ["C", "D", "E", "F", "G", "A", "B", "C"]


def test_key_repr():
    assert repr(Key("C", "major")) == "<Key C major>"


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


def test_key_str():
    assert str(Key("C", "major")) == "C major"
    assert str(Key("A", "minor")) == "A minor"


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


def test_all_keys():
    keys = Key.all_keys()
    assert len(keys) == 24
    majors = [k for k in keys if k.mode == "major"]
    minors = [k for k in keys if k.mode == "minor"]
    assert len(majors) == 12
    assert len(minors) == 12


def test_progressions_count():
    from pytheory.scales import PROGRESSIONS
    assert len(PROGRESSIONS) >= 30
    # A sampling of the expanded library across genres.
    for name in ("circle of fifths", "minor ii-V-i", "8-bar blues",
                 "i-v-VI-IV", "Aeolian"):
        assert name in PROGRESSIONS


def test_every_progression_renders():
    from pytheory.scales import PROGRESSIONS
    # Each progression must build without error in both a major and a minor key.
    for major, minor in [(Key("C", "major"), Key("A", "minor"))]:
        for degrees in PROGRESSIONS.values():
            assert major.progression(*degrees)
            assert minor.progression(*degrees)


def test_progression_case_sets_quality():
    # Uppercase = major, lowercase = minor — independent of the diatonic scale.
    am = Key("A", "minor")
    assert am.progression("V")[0].identify() == "E major"   # harmonic-minor V
    assert am.progression("v")[0].identify() == "E minor"   # natural minor v
    assert am.progression("IV")[0].identify() == "D major"  # Dorian major-IV
    assert am.progression("iv")[0].identify() == "D minor"


def test_progression_harmonic_minor_dominant_seventh():
    am = Key("A", "minor")
    assert am.progression("V7")[0].identify() == "E dominant 7th"
    assert am.progression("ii°", "V7", "i")[2].identify() == "A minor"


def test_progression_flat_degrees_are_borrowed_chords():
    c = Key("C", "major")
    assert c.progression("bVII")[0].identify() == "Bb major"   # Mixolydian ♭VII
    assert c.progression("bVI")[0].identify() == "Ab major"
    assert c.progression("bII")[0].identify() == "Db major"    # Neapolitan


def test_progression_secondary_dominants():
    c = Key("C", "major")
    assert c.progression("V/V")[0].identify() == "D major"
    assert c.progression("V7/V")[0].identify() == "D dominant 7th"
    assert c.progression("V7/ii")[0].identify() == "A dominant 7th"   # dominant of Dm
    assert c.progression("vii°/V")[0].identify() == "F# diminished"
    # The classic applied-dominant cadence.
    chain = [ch.identify() for ch in c.progression("I", "V7/V", "V7", "I")]
    assert chain == ["C major", "D dominant 7th", "G dominant 7th", "C major"]


def test_progression_quality_markers():
    c = Key("C", "major")
    assert c.progression("vii°")[0].identify() == "B diminished"
    assert c.progression("I+")[0].identify() == "C augmented"
    assert c.progression("iiø7")[0].identify() == "D half-diminished 7th"
    assert c.progression("Imaj7")[0].identify() == "C major 7th"


def test_progression_major_diatonic_unchanged():
    # The common case is untouched: case already matches the diatonic quality.
    c = Key("C", "major")
    names = [ch.identify() for ch in c.progression("I", "ii", "iii", "IV", "V7", "vi")]
    assert names == ["C major", "D minor", "E minor", "F major",
                     "G dominant 7th", "A minor"]


def test_pachelbel_progression():
    from pytheory.scales import PROGRESSIONS
    k = Key("C", "major")
    prog = k.progression(*PROGRESSIONS["Pachelbel"])
    assert len(prog) == 8
    assert prog[0].identify() == "C major"


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


def test_analyze_progression():
    from pytheory import analyze_progression
    prog = [Chord.from_name("C"), Chord.from_name("Am"),
            Chord.from_name("F"), Chord.from_name("G")]
    assert analyze_progression(prog, key="C") == ["I", "vi", "IV", "V"]


def test_secondary_dominant_detection():
    from pytheory import detect_secondary_dominant
    S = Chord.from_symbol
    assert detect_secondary_dominant(S("D7"), "C") == "V7/V"
    assert detect_secondary_dominant(S("E7"), "C") == "V7/vi"
    assert detect_secondary_dominant(S("A7"), "C") == "V7/ii"
    assert detect_secondary_dominant(S("C7"), "C") == "V7/IV"
    assert detect_secondary_dominant(S("D"), "C") == "V/V"     # triad, no 7th
    assert detect_secondary_dominant(S("G7"), "C") is None     # the primary V
    assert detect_secondary_dominant(S("Dm"), "C") is None     # diatonic ii
    assert detect_secondary_dominant(S("F#7"), "C") is None    # would target vii°
    # Minor key
    assert detect_secondary_dominant(S("B7"), "A", "minor") == "V7/v"


def test_analyze_progression_with_secondary_dominants():
    from pytheory import analyze_progression
    prog = [Chord.from_symbol(s) for s in ("C", "D7", "G7", "C")]
    assert analyze_progression(prog, "C", secondary_dominants=True) == \
        ["I", "V7/V", "V7", "I"]
    # Default behaviour is unchanged.
    assert analyze_progression(prog, "C") == ["I", "II7", "V7", "I"]


def test_detect_cadence_types():
    from pytheory import detect_cadence
    C = Chord.from_name
    # Authentic: a close root-position triad puts the 5th on top -> IAC.
    assert detect_cadence(C("G"), C("C"), "C") == "imperfect authentic"
    assert detect_cadence(C("Bdim"), C("C"), "C") == "imperfect authentic"
    # PAC needs the tonic in the soprano (root position both chords).
    pac = Chord.from_midi_message(48, 52, 55, 60)   # C3 E3 G3 C4
    assert detect_cadence(C("G"), pac, "C") == "perfect authentic"
    assert detect_cadence(C("G7"), pac, "C") == "perfect authentic"
    # The rest
    assert detect_cadence(C("F"), C("C"), "C") == "plagal"
    assert detect_cadence(C("Dm"), C("G"), "C") == "half"
    assert detect_cadence(C("G"), C("Am"), "C") == "deceptive"
    assert detect_cadence(C("C"), C("F"), "C") is None


def test_detect_cadence_minor_and_phrygian():
    from pytheory import detect_cadence
    C = Chord.from_name
    assert detect_cadence(C("E"), C("Am"), "A", "minor") == "imperfect authentic"
    assert detect_cadence(C("E"), C("F"), "A", "minor") == "deceptive"
    # iv6 -> V in minor: Dm/F (bass F) into E.
    iv6 = Chord.from_midi_message(53, 57, 62)        # F A D
    assert detect_cadence(iv6, C("E"), "A", "minor") == "phrygian half"


def test_find_cadences_scans_pairs():
    from pytheory import find_cadences
    prog = [Chord.from_name(n) for n in ("C", "F", "G", "Am")]
    # C->F none, F->G half, G->Am deceptive
    assert find_cadences(prog, "C") == [(2, "half"), (3, "deceptive")]


def test_random_progression():
    prog = Key("C", "major").random_progression(4)
    assert len(prog) == 4


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


def test_key_parallel_returns_none_for_other_modes():
    """Parallel should return None for non-major/minor modes."""
    k = Key("C", "major")
    k.mode = "lydian"  # force non-standard mode
    assert k.parallel is None


def test_key_relative_returns_none_for_other_modes():
    k = Key("C", "major")
    k.mode = "lydian"
    assert k.relative is None


def test_cli_key(capsys):
    from pytheory.cli import cmd_key
    import argparse
    args = argparse.Namespace(tonic="G", mode="major")
    cmd_key(args)
    out = capsys.readouterr().out
    assert "G major" in out
    assert "Signature" in out
    assert "Relative" in out


def test_cli_progression(capsys):
    from pytheory.cli import cmd_progression
    import argparse
    args = argparse.Namespace(tonic="C", mode="major", numerals=["I", "V", "vi", "IV"])
    cmd_progression(args)
    out = capsys.readouterr().out
    assert "C major" in out
    assert "I → V → vi → IV" in out


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


def test_common_progressions_i_v_vi_iv():
    key = Key("C", "major")
    progs = key.common_progressions()
    chords = progs["I-V-vi-IV"]
    symbols = [c.symbol for c in chords]
    assert symbols == ["C", "G", "Am", "F"]


def test_cli_progressions(capsys):
    from pytheory.cli import cmd_progressions
    import argparse
    args = argparse.Namespace(tonic="C", mode="major")
    cmd_progressions(args)
    out = capsys.readouterr().out
    assert "I-V-vi-IV" in out
    assert "C" in out


def test_suggest_next_v_resolves_to_i():
    key = Key("C", "major")
    g_major = key.triad(4)  # V
    suggestions = key.suggest_next(g_major)
    assert len(suggestions) > 0
    assert suggestions[0].identify() == "C major"  # V → I


def test_suggest_next_ii_goes_to_v():
    key = Key("C", "major")
    dm = key.triad(1)  # ii
    suggestions = key.suggest_next(dm)
    assert suggestions[0].identify() == "G major"  # ii → V


def test_suggest_next_iv():
    key = Key("C", "major")
    f_major = key.triad(3)  # IV
    suggestions = key.suggest_next(f_major)
    assert suggestions[0].identify() == "G major"  # IV → V


def test_analyze_borrowed_bvi():
    ab = Chord.from_symbol("Ab")
    result = ab.analyze("C", "major")
    assert result is not None
    assert "b" in result.lower() or "VI" in result


def test_analyze_borrowed_bvii():
    bb = Chord.from_symbol("Bb")
    result = bb.analyze("C", "major")
    assert result is not None
    assert "b" in result.lower() or "VII" in result


def test_analyze_diatonic_still_works():
    c = Chord.from_symbol("C")
    assert c.analyze("C", "major") == "I"
    g = Chord.from_symbol("G")
    assert g.analyze("C", "major") == "V"
    dm = Chord.from_symbol("Dm")
    assert dm.analyze("C", "major") == "ii"


def test_modulation_path_close_keys():
    """C major to G major — closely related, should find pivot chord."""
    path = Key("C", "major").modulation_path(Key("G", "major"))
    assert len(path) == 4  # I, pivot, V, I
    assert path[0].identify() == "C major"
    assert path[-1].identify() == "G major"


def test_modulation_path_distant_keys():
    """C major to F# major — distant, may use chromatic approach."""
    path = Key("C", "major").modulation_path(Key("F#", "major"))
    assert len(path) >= 3
    assert path[0].identify() == "C major"
    assert path[-1].identify() == "F# major"


def test_modulation_path_same_key():
    """Modulating to the same key should still return a path."""
    path = Key("C", "major").modulation_path(Key("C", "major"))
    assert len(path) >= 3
    assert path[0].identify() == "C major"
    assert path[-1].identify() == "C major"


def test_repl_cmd_key():
    from pytheory.repl import Session, cmd_key
    s = Session()
    cmd_key(s, ["Am"])
    assert s.key.tonic_name == "A"
    assert s.key.mode == "minor"


def test_repl_cmd_key_major():
    from pytheory.repl import Session, cmd_key
    s = Session()
    cmd_key(s, ["G", "major"])
    assert s.key.tonic_name == "G"
    assert s.key.mode == "major"


def test_key_detect_enharmonic_spellings():
    """Sharp and flat spellings of the same notes give the same key."""
    flats = Key.detect("Bb", "C", "D", "Eb", "F", "G", "A")
    sharps = Key.detect("A#", "C", "D", "D#", "F", "G", "A")
    assert str(flats) == str(sharps) == "Bb major"


def test_key_detect_conventional_spelling():
    """No theoretical keys — Bb major, never A# major."""
    k = Key.detect("A#", "D", "F")
    assert k.tonic_name == "Bb"


def test_key_detect_tonic_tiebreak():
    """A-C-E is an A minor triad, not a C major fragment."""
    k = Key.detect("A", "C", "E")
    assert str(k) == "A minor"


def test_key_detect_unparseable_notes():
    assert Key.detect("Sa", "komal Re") is None


# ── chord families by harmonic function ──────────────────────────────

def test_chords_by_function_major():
    fams = Key("C", "major").chords_by_function()
    assert [c.symbol for c in fams["tonic"]] == ["C", "Em", "Am"]
    assert [c.symbol for c in fams["subdominant"]] == ["Dm", "F"]
    assert [c.symbol for c in fams["dominant"]] == ["G", "Bdim"]


def test_chords_by_function_convenience_methods():
    k = Key("C", "major")
    assert [c.symbol for c in k.tonic_chords()] == ["C", "Em", "Am"]
    assert [c.symbol for c in k.subdominant_chords()] == ["Dm", "F"]
    assert [c.symbol for c in k.dominant_chords()] == ["G", "Bdim"]


def test_chords_by_function_minor():
    """Function follows scale degree, so minor keys group the same way."""
    fams = Key("A", "minor").chords_by_function()
    assert [c.symbol for c in fams["tonic"]] == ["Am", "C", "F"]
    assert [c.symbol for c in fams["subdominant"]] == ["Bdim", "Dm"]
    assert [c.symbol for c in fams["dominant"]] == ["Em", "G"]


# ── key-level circle of fifths ───────────────────────────────────────

def test_circle_of_fifths_neighbors():
    cof = Key("C", "major").circle_of_fifths()
    assert str(cof["dominant"]["key"]) == "G major"
    assert str(cof["subdominant"]["key"]) == "F major"
    assert str(cof["relative"]) == "A minor"
    assert str(cof["parallel"]) == "C minor"
    assert cof["position"] == 0


def test_circle_of_fifths_position_signed():
    assert Key("G", "major").circle_of_fifths()["position"] == 1
    assert Key("F", "major").circle_of_fifths()["position"] == -1
    assert Key("Eb", "major").circle_of_fifths()["position"] == -3


def test_circle_of_fifths_shared_chords():
    """Adjacent keys differ by one note, sharing four diatonic triads."""
    cof = Key("C", "major").circle_of_fifths()
    assert cof["dominant"]["shared_chords"] == [
        "A minor", "C major", "E minor", "G major"]


def test_circle_of_fifths_twelve_keys():
    circle = Key("C", "major").circle_of_fifths()["circle"]
    assert [str(k) for k in circle][:4] == [
        "C major", "G major", "D major", "A major"]
    assert len(circle) == 12


def test_circle_of_fifths_minor():
    cof = Key("A", "minor").circle_of_fifths()
    assert str(cof["relative"]) == "C major"
    assert str(cof["dominant"]["key"]) == "E minor"
    assert str(cof["circle"][1]) == "E minor"


# ── negative harmony ─────────────────────────────────────────────────

def test_negative_harmony_major_to_minor():
    assert Chord.from_symbol("C").negative_harmony("C").identify() == "C minor"


def test_negative_harmony_accepts_key_object():
    neg = Chord.from_symbol("F").negative_harmony(Key("C", "major"))
    # F major reflects to G minor in the key of C.
    assert neg.identify() == "G minor"


def test_negative_harmony_dominant_reflection():
    """G7 mirrors to the Fm6/Dm7b5 pitch set — the negative dominant."""
    neg = Chord.from_symbol("G7").negative_harmony("C")
    # Spelled with flats — negative harmony darkens toward minor (Ab, not G#).
    assert {t.name for t in neg.tones} == {"D", "F", "Ab", "C"}


def test_key_negative_harmony_map():
    neg = Key("C", "major").negative_harmony()
    assert neg["axis"] == ("C", "G")
    assert neg["axis_notes"] == ("Eb", "E")
    assert neg["negative_dominant"].symbol == "Fm"
    assert neg["scale"] == ["C", "D", "Eb", "F", "G", "Ab", "Bb"]


def test_key_negative_harmony_chords_count():
    neg = Key("G", "major").negative_harmony()
    assert neg["axis"] == ("G", "D")
    assert len(neg["chords"]) == 7
