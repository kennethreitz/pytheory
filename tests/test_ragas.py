import sys
import types
from fractions import Fraction

import pytest

from pytheory import Raga
from pytheory.ragas import _JustNote, _parse, _SWARA_JI


# ── parsing ──────────────────────────────────────────────────────────

def test_swara_parse_octaves():
    assert _parse("S") == 0
    assert _parse("S'") == 12       # upper octave
    assert _parse("N.") == -1       # lower-octave Ni (11 - 12)
    assert _parse("M") == 6         # tivra Ma
    assert _parse("m") == 5         # shuddha Ma
    assert _parse("g") == 3 and _parse("G") == 4


def test_swara_parse_ignores_separators():
    assert _parse("R,") == 2
    assert _parse("|") is None


# ── data integrity ───────────────────────────────────────────────────

def test_all_ragas_well_formed():
    for r in Raga.all():
        assert r.aroha_swaras() and r.avaroha_swaras()
        assert r.thaat and r.time and r.rasa and r.vadi and r.samvadi
        assert r.note_names("C")        # renders without error


def test_known_raga_count():
    assert len(Raga.all()) >= 54


def test_carnatic_ragas():
    carnatic = Raga.by_tradition("carnatic")
    assert len(carnatic) >= 18
    assert all(r.tradition == "carnatic" for r in carnatic)
    # Shankarabharanam is the Carnatic major scale.
    assert Raga.get("Shankarabharanam").note_names("C") == [
        "C", "D", "E", "F", "G", "A", "B"]
    # Mohanam is the major pentatonic.
    assert len(Raga.get("Mohanam").note_names("C")) == 5
    # Kirwani is an alias for Keeravani.
    assert Raga.get("Kirwani").name == "Keeravani"
    # Hindustani ragas are still tagged hindustani.
    assert Raga.get("Yaman").tradition == "hindustani"


def test_new_ragas_present_and_correct():
    # A few of the extended set, by their distinctive note sets.
    assert Raga.get("ahir bhairav").note_names("C") == [
        "C", "C#", "E", "F", "G", "A", "A#"]
    assert Raga.get("sohni").note_names("C") == [
        "C", "C#", "E", "F#", "A", "B"]            # no Pa
    assert Raga.get("brindabani sarang").note_names("C") == [
        "C", "D", "F", "G", "A#", "B"]             # no Ga, no Dha
    assert Raga.get("Sarang").name == "Brindabani Sarang"   # alias


def test_yaman_scale_is_lydian():
    # Yaman uses tivra Ma → the Lydian set.
    assert Raga.get("yaman").note_names("C") == [
        "C", "D", "E", "F#", "G", "A", "B"]


def test_bhairav_has_komal_re_and_dha():
    assert Raga.get("bhairav").note_names("C") == [
        "C", "C#", "E", "F", "G", "G#", "B"]


def test_malkauns_is_pentatonic():
    mk = Raga.get("malkauns")
    assert len(mk.note_names("C")) == 5
    assert mk.jati == "audav-audav"


def test_bhimpalasi_asymmetric():
    """Aroha omits Re/Dha; avaroha is full — audav-sampurna."""
    bp = Raga.get("bhimpalasi")
    assert bp.jati == "audav-sampurna"
    assert len(bp.aroha_swaras()) < len(bp.avaroha_swaras())


# ── lookup ───────────────────────────────────────────────────────────

def test_lookup_by_alias():
    assert Raga.get("Bhoop").name == "Bhupali"
    assert Raga.get("malkosh").name == "Malkauns"
    assert Raga.get("DES").name == "Desh"


def test_lookup_unknown_raises():
    with pytest.raises(KeyError):
        Raga.get("not-a-raga")


def test_by_thaat_and_time():
    assert Raga.get("kafi") in Raga.by_thaat("kafi")
    assert all(r.thaat == "kafi" for r in Raga.by_thaat("kafi"))
    assert all("night" in r.time for r in Raga.by_time("night"))


# ── tones ────────────────────────────────────────────────────────────

def test_aroha_tones_pitched():
    tones = Raga.get("bhupali").aroha_tones("C4")
    assert [t.full_name for t in tones] == ["C4", "D4", "E4", "G4", "A4", "C5"]


def test_movable_sa():
    c = Raga.get("yaman").aroha_tones("C4")
    d = Raga.get("yaman").aroha_tones("D4")
    # Every tone shifts up a whole step.
    assert all(b.midi - a.midi == 2 for a, b in zip(c, d))


# ── just intonation / shruti ─────────────────────────────────────────

def test_just_ratios_are_5_limit():
    jr = Raga.get("yaman").just_ratios()
    assert jr["G"] == Fraction(5, 4)        # just major 3rd
    assert jr["M"] == Fraction(45, 32)      # just tritone (tivra Ma)


def test_shruti_table_cents_off_12tet():
    rows = {r["swara"]: r for r in Raga.get("yaman").shruti_table("C")}
    # The just major third is ~14 cents flat of equal temperament.
    assert rows["G"]["cents_off"] == pytest.approx(-13.7, abs=0.2)
    assert rows["S"]["cents_off"] == 0.0


def test_just_frequencies_movable_sa():
    y = Raga.get("yaman")
    # Sa itself (after the opening lower-Ni) lands on the tonic frequency.
    from pytheory import Tone
    sa_hz = Tone.from_string("C4").frequency
    freqs = y.just_frequencies("C4")
    assert any(abs(f - sa_hz) < 0.01 for f in freqs)


def test_just_note_renders():
    from pytheory.play import _render, Synth, Envelope
    buf = _render(_JustNote(261.63), synth=Synth.SINE, t=50,
                  envelope=Envelope.PLUCK)
    assert len(buf) > 0


def test_render_with_reverb():
    import numpy
    y = Raga.get("yaman")
    wet = y.render("C4", synth="sine", t=80, reverb=0.4)
    dry = y.render("C4", synth="sine", t=80, reverb=0)
    assert numpy.all(numpy.isfinite(wet))
    assert len(wet) > len(dry)        # reverb pads a tail
    assert len(dry) > 0


# ── CLI ──────────────────────────────────────────────────────────────

def test_cli_raga_info(capsys, monkeypatch):
    from pytheory import cli
    monkeypatch.setattr(sys, "argv", ["pytheory", "raga", "yaman", "--shruti"])
    cli.main()
    out = capsys.readouterr().out
    assert "Yaman" in out and "kalyan" in out
    assert "5/4" in out          # shruti table rendered


def test_cli_raga_list(capsys, monkeypatch):
    from pytheory import cli
    monkeypatch.setattr(sys, "argv", ["pytheory", "raga", "--thaat", "kafi"])
    cli.main()
    out = capsys.readouterr().out
    assert "Bhimpalasi" in out and "Kafi" in out
