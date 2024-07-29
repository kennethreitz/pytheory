import pytest

import pytheory
from pytheory import Tone, TonedScale, Tone, Fretboard, Chord


def test_tone_from_string():
    c4 = Tone.from_string("C4")
    assert c4.name == "C"
    assert c4.octave == 4


def test_tone_initialization():
    c4 = Tone(name="C", octave=4)
    assert c4.name == "C"
    assert c4.octave == 4


def test_tone_addition():
    assert (
        Tone.from_string("C4", system=pytheory.SYSTEMS["western"]).add(12).full_name
        == "C5"
    )


def test_tone_subtraction():
    assert (
        Tone.from_string("C5", system=pytheory.SYSTEMS["western"])
        .subtract(12)
        .full_name
        == "C4"
    )


def test_tone_full_name():
    c4 = Tone(name="C", octave=4)
    d = Tone(name="D", octave=None)

    assert c4.full_name == "C4"
    assert d.full_name == "D"


def test_tone_system():
    c4 = Tone(name="C", octave=4, system="western")

    assert c4.system_name == "western"
    assert c4.system == pytheory.SYSTEMS["western"]


def test_tone_exists():
    c4 = Tone(name="C", octave=4, system="western")
    invalid_tone = Tone(name="H", octave=4, system="western")

    assert c4.exists == True
    assert invalid_tone.exists == False


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
