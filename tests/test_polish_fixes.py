"""Regression tests for the quality/DX polish sweep.

Each test pins a robustness or developer-experience fix so it can't
silently regress: friendly errors instead of bare exceptions, value-type
dunder contracts, malformed-input guards, and boundary handling.
"""
import pytest

from pytheory import Tone, Chord, Fretboard
from pytheory.scales import Key
from pytheory.rhythm import TimeSignature


# ── Key.secondary_dominant: no crash on out-of-range / wrapping degrees ──

def test_secondary_dominant_wraps_past_octave():
    k = Key("C", "major")
    # V/9 wraps to V/2 (degree 9 -> degree 2), no IndexError.
    assert k.secondary_dominant(9).identify() == k.secondary_dominant(2).identify()


def test_secondary_dominant_rejects_nonpositive_degree():
    k = Key("C", "major")
    with pytest.raises(ValueError, match="positive integer"):
        k.secondary_dominant(0)


# ── TimeSignature: hashable (defines __eq__, so must define __hash__) ──

def test_time_signature_hashable():
    d = {TimeSignature(4, 4): "common", TimeSignature(6, 8): "compound"}
    assert d[TimeSignature(4, 4)] == "common"
    assert hash(TimeSignature(3, 4)) == hash(TimeSignature(3, 4))


def test_time_signature_from_string_friendly_error():
    with pytest.raises(ValueError, match="Invalid time signature"):
        TimeSignature.from_string("bogus")


# ── Friendly errors instead of bare exceptions ──

def test_fretboard_chord_unparseable_raises_value_error():
    fb = Fretboard(tones=[Tone.from_string(n)
                          for n in ("E2", "A2", "D3", "G3", "B3", "E4")])
    with pytest.raises(ValueError, match="chord symbol"):
        fb.chord("NotAChord!")


def test_scale_getitem_unknown_degree_message():
    scale = Key("C", "major").scale
    with pytest.raises(KeyError, match="scale degree"):
        scale["ZZ"]


# ── Tone.pitch stays correct (now documented) ──

def test_tone_pitch_reference():
    assert Tone.from_string("A4").pitch() == 440.0
    assert Tone.from_string("A4").pitch(reference_pitch=432.0) == 432.0
