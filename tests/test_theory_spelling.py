"""Regression tests for notation, chord parsing and spelled intervals."""

import pytest

from pytheory import Chord, Tone, TonedScale, TET


@pytest.mark.parametrize("symbol, names", [
    ("Ebm", ["Eb", "Gb", "Bb"]),
    ("Bb7", ["Bb", "D", "F", "Ab"]),
    ("Db", ["Db", "F", "Ab"]),
    ("F#7", ["F#", "A#", "C#", "E"]),
    ("Cdim7", ["C", "Eb", "Gb", "Bbb"]),
    ("Caug", ["C", "E", "G#"]),
    ("Cbmaj7", ["Cb", "Eb", "Gb", "Bb"]),
    ("B#aug", ["B#", "D##", "F###"]),
    ("F♯7", ["F#", "A#", "C#", "E"]),
    ("E♭m", ["Eb", "Gb", "Bb"]),
])
@pytest.mark.parametrize("factory", [Chord.from_name, Chord.from_symbol])
def test_exact_chord_spelling(factory, symbol, names):
    assert [t.name for t in factory(symbol)] == names


# Independently specified chromatic offsets and diatonic degrees. Every
# requested quality is checked against every natural, sharp and flat root.
QUALITIES = {
    "": ((4, 7), (3, 5)),
    "maj": ((4, 7), (3, 5)),
    "m": ((3, 7), (3, 5)),
    "min": ((3, 7), (3, 5)),
    "dim": ((3, 6), (3, 5)),
    "aug": ((4, 8), (3, 5)),
    "+": ((4, 8), (3, 5)),
    "sus2": ((2, 7), (2, 5)),
    "sus4": ((5, 7), (4, 5)),
    "6": ((4, 7, 9), (3, 5, 6)),
    "m6": ((3, 7, 9), (3, 5, 6)),
    "7": ((4, 7, 10), (3, 5, 7)),
    "maj7": ((4, 7, 11), (3, 5, 7)),
    "m7": ((3, 7, 10), (3, 5, 7)),
    "mMaj7": ((3, 7, 11), (3, 5, 7)),
    "m7b5": ((3, 6, 10), (3, 5, 7)),
    "ø": ((3, 6, 10), (3, 5, 7)),
    "ø7": ((3, 6, 10), (3, 5, 7)),
    "dim7": ((3, 6, 9), (3, 5, 7)),
    "°7": ((3, 6, 9), (3, 5, 7)),
    "9": ((4, 7, 10, 14), (3, 5, 7, 9)),
    "maj9": ((4, 7, 11, 14), (3, 5, 7, 9)),
    "m9": ((3, 7, 10, 14), (3, 5, 7, 9)),
    "add9": ((4, 7, 14), (3, 5, 9)),
    "7sus4": ((5, 7, 10), (4, 5, 7)),
}
ROOTS = [letter + accidental for letter in "CDEFGAB" for accidental in ("", "#", "b")]


@pytest.mark.parametrize("root", ROOTS)
@pytest.mark.parametrize("quality", QUALITIES)
def test_all_roots_and_qualities(root, quality):
    semitones, degrees = QUALITIES[quality]
    symbol_chord = Chord.from_symbol(root + quality, octave=3)
    named_chord = Chord.from_name(root + quality, octave=3)
    root_tone = Tone(root, octave=3)
    assert symbol_chord.tones[0].full_name == root + "3"
    assert [t.midi - root_tone.midi for t in symbol_chord] == [0, *semitones]
    assert [t.name for t in named_chord] == [t.name for t in symbol_chord]
    assert all(t.octave == 3 for t in named_chord)  # legacy from_name voicing
    letters = "CDEFGAB"
    start = letters.index(root[0])
    assert [t.letter for t in symbol_chord] == [root[0]] + [
        letters[(start + degree - 1) % 7] for degree in degrees
    ]
    assert [t.midi % 12 for t in named_chord] == [t.midi % 12 for t in symbol_chord]


@pytest.mark.parametrize("symbol", ["C7b9", "Cmajgarbage", "F#wat", "H7", "Cøjunk", ""])
@pytest.mark.parametrize("factory", [Chord.from_name, Chord.from_symbol])
def test_unknown_quality_is_rejected(factory, symbol):
    with pytest.raises(ValueError):
        factory(symbol)


@pytest.mark.parametrize("name, octave, midi", [
    ("Cb4", 4, 59), ("B#3", 3, 60),
    ("Cbb4", 4, 58), ("B##3", 3, 61),
    ("Cb0", 0, 11), ("B#-1", -1, 12),
])
@pytest.mark.parametrize("factory", [Tone, Tone.from_string])
def test_boundary_octaves_keep_pitch(name, octave, midi, factory):
    t = factory(name)
    assert t.full_name == name
    assert t.octave == octave
    assert t.midi == midi
    assert t.frequency == pytest.approx(440 * 2 ** ((midi - 69) / 12))
    assert (t + 0).midi == midi
    assert (t + 12).midi == midi + 12
    assert (t - 12).midi == midi - 12
    assert t - Tone.from_midi(midi) == 0
    assert t.interval_to(Tone.from_midi(midi)) == "unison"


def test_boundary_octave_override():
    assert Tone("Cb9", octave=4).full_name == "Cb4"
    assert Tone("Cb9", octave=4).midi == 59


@pytest.mark.parametrize("source, interval, expected", [
    ("C4", "m3", "Eb4"), ("C4", "A2", "D#4"),
    ("C4", "M3", "E4"), ("C4", "d5", "Gb4"), ("C4", "A4", "F#4"),
    ("C4", "P8", "C5"), ("C4", "M10", "E5"), ("C4", "m9", "Db5"),
    ("C4", "-m3", "A3"), ("C4", "-M3", "Ab3"),
    ("Cb4", "P8", "Cb5"), ("B#3", "P8", "B#4"),
    ("F#4", "M3", "A#4"), ("C4", "d7", "Bbb4"),
    ("C4", "AA4", "F##4"), ("C4", "dd5", "Gbb4"),
    ("C", "m3", "Eb"), ("B#3", "M3", "D##4"),
])
def test_interval_aware_transposition(source, interval, expected):
    tone = Tone(source)
    assert tone.transpose_interval(interval).full_name == expected
    assert tone.transpose(interval).full_name == expected


@pytest.mark.parametrize("interval", ["", "m0", "m-3", "Q3", "M4", "P3", "m8", "m3junk"])
def test_invalid_spelled_interval(interval):
    with pytest.raises(ValueError):
        Tone("C4").transpose_interval(interval)


def test_context_aware_semitones_is_opt_in():
    # Keep operators backward compatible; a raw integer has no diatonic intent.
    assert str(Tone("C4") + 3) == "D#4"
    assert str(Tone("Db4") + 2) == "D#4"
    assert str(Tone("Eb4").add(3, prefer_flats=None)) == "Gb4"
    assert str(Tone("F#4").add(3, prefer_flats=None)) == "A4"
    assert str(Tone("Db4").add(2, prefer_flats=None)) == "Eb4"
    assert str(Tone("Db4").add(2, prefer_flats=False)) == "D#4"
    assert str(Tone("C4").add(3, prefer_flats=True)) == "Eb4"
    assert str(Tone("C4").transpose(3)) == "D#4"


@pytest.mark.parametrize("target, name, steps", [
    ("E4", "major third", 4), ("Eb4", "minor third", 3),
    ("D#4", "augmented second", 3), ("Gb4", "diminished fifth", 6),
    ("F#4", "augmented fourth", 6), ("C5", "perfect octave", 12),
    ("E5", "major tenth", 16), ("Eb5", "minor tenth", 15),
    ("C6", "perfect fifteenth", 24), ("Db5", "minor ninth", 13),
    ("C4", "perfect unison", 0), ("C#4", "augmented unison", 1),
    ("Cb4", "diminished unison", -1), ("Ebb4", "diminished third", 2),
    ("F##4", "doubly augmented fourth", 7),
    ("Gbb4", "doubly diminished fifth", 5),
    ("Ab3", "major third", -4), ("A3", "minor third", -3),
    ("C7", "perfect 22nd", 36),
])
def test_spelling_aware_interval_names(target, name, steps):
    c = Tone("C4")
    other = Tone(target)
    assert c.interval_name_to(other) == name
    assert other - c == steps
    assert isinstance(other - c, int)


def test_interval_naming_does_not_break_legacy_api():
    c = Tone("C4")
    assert c.interval_to(Tone("E4")) == "major 3rd"
    assert c.interval_to(Tone("D#4")) == "minor 3rd"
    assert c.interval_to(Tone("F#4")) == "tritone"
    assert c.interval_to(Tone("C5")) == "octave"
    assert c.interval_to(Tone("E5")) == "major 3rd + 1 octave"
    assert Tone("C").interval_name_to(Tone("Eb")) == "minor third"
    assert Tone("Cb4").interval_name_to(Tone("B3")) == "diminished second"
    assert Tone("B#3").interval_name_to(Tone("C4")) == "diminished second"


def test_spelled_intervals_reject_non_western_systems():
    tone = Tone(0, octave=4, system=TET(19))
    with pytest.raises(ValueError, match="Western"):
        tone.transpose_interval("m3")
    with pytest.raises(ValueError, match="Western"):
        tone.interval_name_to(tone)
    assert isinstance(tone + 3, Tone)


@pytest.mark.parametrize("tonic, scale, expected", [
    ("F4", "major", ["F", "G", "A", "Bb", "C", "D", "E"]),
    ("F#4", "major", ["F#", "G#", "A#", "B", "C#", "D#", "E#"]),
    ("Eb4", "minor", ["Eb", "F", "Gb", "Ab", "Bb", "Cb", "Db"]),
    ("A4", "harmonic minor", ["A", "B", "C", "D", "E", "F", "G#"]),
])
def test_scale_spelling_regressions(tonic, scale, expected):
    tones = TonedScale(tonic=tonic)[scale].tones
    assert [t.name for t in tones[:7]] == expected
    root_midi = Tone(tonic).midi
    assert tones[0].midi == root_midi
    assert all(a.midi < b.midi for a, b in zip(tones, tones[1:]))


@pytest.mark.parametrize("tonic", ["Cb4", "B#3"])
def test_boundary_tonic_scale_register(tonic):
    scale = TonedScale(tonic=tonic)["major"]
    assert scale.tones[0].full_name == tonic
    assert [t.midi - Tone(tonic).midi for t in scale.tones] == [0, 2, 4, 5, 7, 9, 11, 12]


def test_harmony_identification_regressions():
    assert Chord.from_tones("C", "E", "G").identify() == "C major"
    assert Chord.from_tones("C", "E", "G", "A").identify() == "C major 6th"
    assert [chord.symbol for chord in TonedScale(tonic="C4")["major"].harmonize()] == [
        "C", "Dm", "Em", "F", "G", "Am", "Bdim"
    ]
