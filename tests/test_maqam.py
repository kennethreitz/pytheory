import sys
from fractions import Fraction

import pytest

from pytheory import Maqam


def test_catalog_size_and_lookup():
    assert len(Maqam.all()) >= 10
    assert Maqam.get("rast").name == "Rast"
    assert Maqam.get("Bayat").name == "Bayati"          # alias
    assert Maqam.get("nihavend").name == "Nahawand"     # alias
    with pytest.raises(KeyError):
        Maqam.get("not-a-maqam")


def test_rast_degrees_and_quartertones():
    rast = Maqam.get("Rast")
    assert rast.degree_names() == ["Do", "Re", "Mi↓", "Fa", "Sol", "La", "Si↓"]
    assert rast.has_quartertones
    # The neutral third is the just 27/22.
    assert rast.just_ratios()["Mi↓"] == Fraction(27, 22)


def test_maqam_table_cents_off_12tet():
    rows = {r["degree"]: r for r in Maqam.get("Rast").maqam_table("C")}
    # The Rast neutral 3rd sits ~45 cents below the tempered E.
    assert rows["Mi↓"]["cents_off"] == pytest.approx(-45.5, abs=0.3)
    # The neutral 7th (awj) is ~49 cents above Bb.
    assert rows["Si↓"]["cents_off"] == pytest.approx(49.4, abs=0.3)
    assert rows["Do"]["cents_off"] == 0.0


def test_hijaz_has_augmented_second_no_quartertones():
    hijaz = Maqam.get("Hijaz")
    assert hijaz.note_names("C") == ["C", "Db", "E", "F", "G", "Ab", "Bb"]
    assert not hijaz.has_quartertones        # Hijaz is fully 12-TET


def test_ajam_is_major():
    assert Maqam.get("Ajam").note_names("C") == [
        "C", "D", "E", "F", "G", "A", "B"]


def test_just_frequencies_ascend_then_descend():
    freqs = Maqam.get("Rast").just_frequencies("C4")
    # 7 degrees + octave = 8 up, then 7 down (octave not repeated) = 15.
    assert len(freqs) == 15
    assert freqs[0] == pytest.approx(freqs[-1])           # starts and ends on Do
    assert freqs[7] == pytest.approx(freqs[0] * 2)        # the octave at the top


def test_movable_tonic():
    c = Maqam.get("Bayati").just_frequencies("C4")
    d = Maqam.get("Bayati").just_frequencies("D4")
    assert d[0] > c[0]                                     # whole thing transposes up


def test_by_family():
    assert Maqam.get("Suznak") in Maqam.by_family("Rast")
    assert all(m.family == "Hijaz" for m in Maqam.by_family("Hijaz"))


def test_render_buffer():
    import numpy as np
    buf = Maqam.get("Hijaz").render("C4", synth="sine", t=60, reverb=0.2)
    assert len(buf) > 0 and np.all(np.isfinite(buf))


def test_cli_maqam_info(capsys, monkeypatch):
    from pytheory import cli
    monkeypatch.setattr(sys, "argv", ["pytheory", "maqam", "rast", "--tuning"])
    cli.main()
    out = capsys.readouterr().out
    assert "Rast" in out and "27/22" in out and "Mi↓" in out


def test_cli_maqam_list(capsys, monkeypatch):
    from pytheory import cli
    monkeypatch.setattr(sys, "argv", ["pytheory", "maqam", "--family", "Hijaz"])
    cli.main()
    out = capsys.readouterr().out
    assert "Hijaz" in out and "Hijazkar" in out
