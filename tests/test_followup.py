"""Follow-up correctness fixes after 0.58.0.

Covers octave spelling, Roman-numeral spelling, transposition, analysis
round-trips, key signatures, enharmonics, and chord-symbol aliases.
"""

import pytest

from pytheory import Chord, Key, Tone, TonedScale


def names(chord):
    return [t.name for t in chord.tones]


# ── Octave arithmetic keeps the written note ──────────────────────────

@pytest.mark.parametrize("source, interval, expected", [
    ("Db4", 0, "Db4"),
    ("Eb4", 0, "Eb4"),
    ("Cb4", 0, "Cb4"),
    ("B#3", 0, "B#3"),
    ("Eb4", 12, "Eb5"),
    ("Eb4", -12, "Eb3"),
    ("Cb4", 12, "Cb5"),
    ("B#3", -12, "B#2"),
    ("F##4", 12, "F##5"),
    ("Bbb4", -12, "Bbb3"),
])
def test_octave_shift_preserves_spelling(source, interval, expected):
    tone = Tone(source)
    assert (tone + interval).full_name == expected
    assert tone.add(interval, prefer_flats=not tone.is_flat).full_name == expected


def test_flat_chord_transpose_zero_is_identity():
    chord = Chord.from_symbol("Eb")
    assert [t.full_name for t in chord.transpose(0)] == ["Eb4", "G4", "Bb4"]


def test_flat_scale_transpose_zero_is_identity():
    names_ = [t.name for t in TonedScale(tonic="F4")["major"].transpose(0).tones]
    assert names_ == ["F", "G", "A", "Bb", "C", "D", "E", "F"]


def test_inversion_keeps_flat_root():
    chord = Chord.from_symbol("Eb")
    assert [t.full_name for t in chord.inversion(1)] == ["G4", "Bb4", "Eb5"]
    assert chord.inversion(1).identify() == "Eb major"
    assert chord.inversion(1).slash_name == "Eb/G"
    assert [t.full_name for t in chord.inversion(2)] == ["Bb4", "Eb5", "G5"]


def test_close_and_drop_voicings_keep_spelling():
    chord = Chord.from_symbol("Ebm7")
    assert names(chord.close_voicing()) == ["Eb", "Gb", "Bb", "Db"]
    assert names(chord.drop2()) == ["Bb", "Eb", "Gb", "Db"]
    assert "D#" not in names(chord.open_voicing())
    assert "A#" not in names(chord.open_voicing())


# ── Roman numerals and secondary dominants ────────────────────────────

@pytest.mark.parametrize("key, numeral, expected", [
    ("F", "ii", ["G", "Bb", "D"]),
    ("F", "V7", ["C", "E", "G", "Bb"]),
    ("Bb", "IV", ["Eb", "G", "Bb"]),
    ("Eb", "I", ["Eb", "G", "Bb"]),
    ("Gb", "I", ["Gb", "Bb", "Db"]),
    ("C#", "I", ["C#", "E#", "G#"]),
    ("C#", "V", ["G#", "B#", "D#"]),
    ("F", "iiø7", ["G", "Bb", "Db", "F"]),
    ("C", "vii°7", ["B", "D", "F", "Ab"]),
    ("C", "Imaj7", ["C", "E", "G", "B"]),
    ("C", "Imaj9", ["C", "E", "G", "B", "D"]),
    ("C", "V9", ["G", "B", "D", "F", "A"]),
])
def test_numeral_spelling(key, numeral, expected):
    assert names(Key(key).progression(numeral)[0]) == expected


def test_minor_major_seventh_spelling():
    chord = Key("C", "minor").progression("imMaj7")[0]
    assert names(chord) == ["C", "Eb", "G", "B"]
    assert chord.identify() == "C minor-major 7th"


def test_secondary_dominant_spelling_in_flat_keys():
    # V/IV in Bb is the dominant of Eb, which is Bb7 — not A#7.
    chord = Key("Bb").secondary_dominant(4)
    assert names(chord) == ["Bb", "D", "F", "Ab"]
    assert chord.identify() == "Bb dominant 7th"
    # V/I in C spells the 7th as Bb, not A#.
    assert names(Key("C").secondary_dominant(4)) == ["C", "E", "G", "Bb"]


def test_nashville_minor_spelling():
    chord = TonedScale(tonic="C4")["major"].nashville("4m7")[0]
    assert names(chord) == ["F", "Ab", "C", "Eb"]


# ── Scale transposition ───────────────────────────────────────────────

@pytest.mark.parametrize("tonic, scale, semitones, expected", [
    ("C4", "major", 1, ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"]),
    ("C4", "major", 2, ["D", "E", "F#", "G", "A", "B", "C#"]),
    ("C4", "major", 5, ["F", "G", "A", "Bb", "C", "D", "E"]),
    ("C4", "major", 6, ["F#", "G#", "A#", "B", "C#", "D#", "E#"]),
    ("C4", "major", -7, ["F", "G", "A", "Bb", "C", "D", "E"]),
    ("F4", "major", 1, ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"]),
    ("F4", "major", 5, ["Bb", "C", "D", "Eb", "F", "G", "A"]),
    ("Eb4", "major", 1, ["E", "F#", "G#", "A", "B", "C#", "D#"]),
    ("A4", "harmonic minor", 2, ["B", "C#", "D", "E", "F#", "G", "A#"]),
])
def test_heptatonic_transpose_spelling(tonic, scale, semitones, expected):
    transposed = TonedScale(tonic=tonic)[scale].transpose(semitones)
    assert [t.name for t in transposed.tones[:7]] == expected
    letters = [t.letter for t in transposed.tones[:7]]
    assert len(letters) == len(set(letters))


def test_blues_transpose_prefers_existing_flats():
    blues = TonedScale(tonic="C4", system="blues")["blues"].transpose(2)
    assert [t.name for t in blues.tones] == ["D", "F", "G", "Ab", "A", "C", "D"]


def test_chromatic_octave_repeat_matches_tonic():
    scale = TonedScale(tonic="F#4")["chromatic"]
    assert scale.tones[0].name == "F#"
    assert scale.tones[-1].name == "F#"
    assert scale.tones[-1].octave == scale.tones[0].octave + 1


# ── Analysis round-trip ───────────────────────────────────────────────

@pytest.mark.parametrize("symbol, key, mode, numeral", [
    ("Cmaj7", "C", "major", "Imaj7"),
    ("Bm7b5", "C", "major", "viiø7"),
    ("Bdim7", "C", "major", "viidim7"),
    ("C9", "C", "major", "I9"),
    ("Cmaj9", "C", "major", "Imaj9"),
    ("Dm9", "C", "major", "ii9"),
    ("G7", "C", "major", "V7"),
    ("CmMaj7", "C", "minor", "imMaj7"),
    ("F#", "C", "major", "#IV"),
    ("Gb", "C", "major", "bV"),
    ("Ab", "C", "major", "bVI"),
    ("Bb", "C", "major", "bVII"),
])
def test_analyze_round_trip(symbol, key, mode, numeral):
    chord = Chord.from_symbol(symbol)
    assert chord.analyze(key, mode) == numeral
    rebuilt = Key(key, mode).progression(numeral)[0]
    assert [t.midi % 12 for t in rebuilt] == [t.midi % 12 for t in chord]
    assert rebuilt.identify() == chord.identify()


# ── Keys ──────────────────────────────────────────────────────────────

def test_theoretical_signature_counts_double_sharps():
    sig = Key("D#", "major").signature
    assert sig["sharps"] == 9
    assert sig["flats"] == 0
    assert sig["accidentals"] == [
        "F#", "C#", "G#", "D#", "A#", "E#", "B#", "F##", "C##",
    ]


@pytest.mark.parametrize("tonic, sharps, flats", [
    ("C", 0, 0), ("G", 1, 0), ("D", 2, 0), ("A", 3, 0),
    ("E", 4, 0), ("B", 5, 0), ("F#", 6, 0), ("C#", 7, 0),
    ("F", 0, 1), ("Bb", 0, 2), ("Eb", 0, 3), ("Ab", 0, 4),
    ("Db", 0, 5), ("Gb", 0, 6), ("Cb", 0, 7),
])
def test_standard_key_signatures(tonic, sharps, flats):
    sig = Key(tonic).signature
    assert sig["sharps"] == sharps
    assert sig["flats"] == flats
    assert len(sig["accidentals"]) == sharps + flats


def test_all_keys_use_conventional_spellings():
    names_ = [(k.tonic_name, k.mode) for k in Key.all_keys()]
    assert ("Bb", "major") in names_
    assert ("Eb", "major") in names_
    assert ("Eb", "minor") in names_
    assert ("A#", "major") not in names_
    assert ("D#", "major") not in names_
    assert ("D#", "minor") not in names_
    assert len(names_) == 24


# ── Enharmonics, solfege ──────────────────────────────────────────────

def test_enharmonic_is_symmetric_for_flats():
    assert Tone("Db4").enharmonic == "C#"
    assert Tone("C#4").enharmonic == "Db"
    assert Tone("E#4").enharmonic == "F"
    assert Tone("Cb4").enharmonic == "B"
    assert Tone("B#3").enharmonic == "C"
    assert Tone("Fb4").enharmonic == "E"
    assert Tone("C4").enharmonic is None


def test_flat_midi_note_keeps_sharp_alias_and_compares_equal():
    sharp = Tone.from_midi(61)
    flat = Tone.from_midi(61, prefer_flats=True)
    assert sharp.name == "C#"
    assert flat.name == "Db"
    assert flat.enharmonic == "C#"
    assert sharp == flat
    assert flat == sharp
    assert hash(sharp) == hash(flat)
    assert len({sharp, flat}) == 1


@pytest.mark.parametrize("note, syllable", [
    ("C", "Do"), ("C#", "Di"), ("Db", "Ra"), ("F#", "Fi"), ("Bb", "Te"),
    ("E#", "Fa"), ("B#", "Do"), ("Fb", "Mi"), ("Cb", "Ti"),
    ("F##", "Sol"), ("Bbb", "La"), ("C##", "Re"),
])
def test_solfege_pitch(note, syllable):
    assert Tone(note + "4").solfege == syllable


# ── Chord symbol aliases ──────────────────────────────────────────────

@pytest.mark.parametrize("symbol, expected, identified", [
    ("C6/9", ["C", "E", "G", "A", "D"], "C major 6/9"),
    ("Cm6/9", ["C", "Eb", "G", "A", "D"], "C minor 6/9"),
    ("F#6/9", ["F#", "A#", "C#", "D#", "G#"], "F# major 6/9"),
    ("Csus", ["C", "F", "G"], "C sus4"),
    ("C-", ["C", "Eb", "G"], "C minor"),
    ("C-7", ["C", "Eb", "G", "Bb"], "C minor 7th"),
    ("Bb-7", ["Bb", "Db", "F", "Ab"], "Bb minor 7th"),
    ("C°", ["C", "Eb", "Gb"], "C diminished"),
    ("CΔ7", ["C", "E", "G", "B"], "C major 7th"),
    ("CΔ", ["C", "E", "G", "B"], "C major 7th"),
])
def test_chord_symbol_aliases(symbol, expected, identified):
    chord = Chord.from_symbol(symbol)
    assert names(chord) == expected
    assert chord.identify() == identified


def test_six_nine_is_not_a_slash_chord():
    chord = Chord.from_name("C6/9")
    assert names(chord) == ["C", "E", "G", "A", "D"]
    assert chord.symbol == "C6/9"


def test_slash_degree_is_rejected():
    with pytest.raises(ValueError, match="quality"):
        Chord.from_symbol("C/9")


def test_real_slash_chord_still_inverts():
    chord = Chord.from_symbol("Eb/G")
    assert [t.full_name for t in chord] == ["G4", "Bb4", "Eb5"]
    assert chord.identify() == "Eb major"
