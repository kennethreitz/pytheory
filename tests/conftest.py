import pytest

from pytheory import Tone, Fretboard


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
    # Literal is written high-to-low, so declare that orientation.
    return Fretboard(tones=tuning, high_to_low=True)
