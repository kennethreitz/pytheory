from pytheory import Fretboard, CHARTS


def test_p4_tuning_preset():
    fb = Fretboard.guitar("p4")
    assert [t.full_name for t in fb.tones] == ["E2", "A2", "D3", "G3", "C4", "F4"]
    assert Fretboard.guitar("all fourths").tones == fb.tones


def test_p4_fingering():
    fb = Fretboard.guitar("p4")
    assert CHARTS["western"]["C"].fingering(fretboard=fb) is not None
