import pytest

import pytheory
from pytheory import Tone, TonedScale, Tone


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
