import xml.dom.minidom as minidom

import pytest

from pytheory import Fretboard, TonedScale, Chord
from pytheory.diagrams import (chord_svg, scale_shapes, arpeggio_svg,
                               ScaleShape, _ROOT)


def _valid(svg):
    minidom.parseString(svg)   # raises on malformed XML
    assert svg.startswith("<svg")
    return svg


# ── chord diagrams ───────────────────────────────────────────────────

def test_chord_image_is_valid_svg():
    svg = Fretboard.guitar().tab_image("Am")
    _valid(svg)
    assert "Am" in svg


def test_chord_image_marks_root_in_red():
    # C major has two C roots (A string fret 3, B string fret 1).
    svg = Fretboard.guitar().tab_image("C")
    assert svg.count(_ROOT) == 2


def test_chord_image_detects_barre():
    # F is a full barre — expect a rect (the bar) in the output.
    assert "<rect" in Fretboard.guitar().tab_image("F").replace(
        '<rect width', '')  # ignore the background rect


def test_chord_image_writes_file(tmp_path):
    out = tmp_path / "Am.svg"
    ret = Fretboard.guitar().tab_image("Am", str(out))
    assert ret == str(out)
    assert out.read_text().startswith("<svg")


def test_fingering_to_svg():
    svg = Fretboard.guitar().chord("G").to_svg("G")
    _valid(svg)


def test_iterate_chord_images(tmp_path):
    fb = Fretboard.guitar()
    for name in ["C", "Am", "F", "G"]:
        out = tmp_path / f"{name}.svg"
        fb.tab_image(name, str(out))
        assert out.exists()


# ── scale shapes ─────────────────────────────────────────────────────

def _a_minor_pentatonic():
    return TonedScale(tonic="A4", system="blues")["minor pentatonic"]


def test_pentatonic_has_five_positions():
    shapes = Fretboard.guitar().scale_shapes(_a_minor_pentatonic())
    assert len(shapes) == 5
    assert all(isinstance(s, ScaleShape) for s in shapes)


def test_pentatonic_two_notes_per_string():
    """Each pentatonic box is two notes on every string."""
    from collections import Counter
    for shape in Fretboard.guitar().scale_shapes(_a_minor_pentatonic()):
        per_string = Counter(s for (s, _, _, _) in shape.notes)
        assert set(per_string.values()) == {2}


def test_scale_shape_marks_roots():
    shapes = Fretboard.guitar().scale_shapes(_a_minor_pentatonic())
    # Every box contains at least one A root.
    for shape in shapes:
        assert any(is_root for (_, _, _, is_root) in shape.notes)
    svg = shapes[0].to_svg()
    assert _ROOT in svg
    _valid(svg)


def test_scale_shape_window_is_small():
    for shape in Fretboard.guitar().scale_shapes(_a_minor_pentatonic()):
        lo, hi = shape.fret_range
        assert hi - lo <= 4          # a comfortable hand span


def test_diatonic_three_notes_per_string():
    from collections import Counter
    cmaj = TonedScale(tonic="C4")["major"]
    shapes = Fretboard.guitar().scale_shapes(cmaj)
    assert len(shapes) == 7
    counts = Counter(s for (s, _, _, _) in shapes[1].notes)
    assert set(counts.values()) == {3}


def test_scale_shape_image_position_bounds():
    fb = Fretboard.guitar()
    scale = _a_minor_pentatonic()
    _valid(fb.scale_shape_image(scale, 1))
    with pytest.raises(ValueError):
        fb.scale_shape_image(scale, 99)


# ── arpeggio diagrams ────────────────────────────────────────────────

def test_arpeggio_diagram_valid_and_labelled():
    svg = Fretboard.guitar().arpeggio_diagram("Am")
    _valid(svg)
    assert ">R<" in svg          # root label
    assert ">5<" in svg          # fifth label


def test_arpeggio_accepts_chord_object():
    svg = Fretboard.guitar().arpeggio_diagram(Chord.from_symbol("Cmaj7"))
    _valid(svg)


def test_arpeggio_note_labels():
    svg = Fretboard.guitar().arpeggio_diagram("Am", labels="note")
    assert ">A<" in svg and ">C<" in svg


def test_arpeggio_respects_max_fret():
    narrow = Fretboard.guitar().arpeggio_diagram("Am", max_fret=5)
    wide = Fretboard.guitar().arpeggio_diagram("Am", max_fret=12)
    assert len(narrow) < len(wide)


# ── other instruments ────────────────────────────────────────────────

def test_works_on_ukulele():
    svg = Fretboard.ukulele().tab_image("C")
    _valid(svg)


def test_png_export_requires_cairosvg(tmp_path):
    pytest.importorskip("cairosvg")
    out = tmp_path / "Am.png"
    Fretboard.guitar().tab_image("Am", str(out), fmt="png")
    assert out.exists()


# ── arbitrary (uncharted) chord voicings ─────────────────────────────

def test_uncharted_chord_voicing_covers_tones():
    """Symbols outside the 144 charts get a computed voicing of their notes."""
    fb = Fretboard.guitar()
    for sym in ["F#m7b5", "Csus2", "Dsus4", "Aaug", "Gadd9", "Cdim7", "E7sus4"]:
        fg = fb.chord(sym)
        want = {t.midi % 12 for t in Chord.from_symbol(sym).tones}
        got = {t.midi % 12 for t in fg.tones}
        assert want.issubset(got), f"{sym}: missing tones {want - got}"
        assert got.issubset(want), f"{sym}: foreign tones {got - want}"


def test_uncharted_chord_image_is_valid_svg():
    _valid(Fretboard.guitar().tab_image("F#m7b5"))
    _valid(Fretboard.guitar().tab_image("Csus2"))


def test_uncharted_voicing_is_playable():
    """The computed shape fits a hand: <= 4-fret span, >= 2 sounding strings."""
    fg = Fretboard.guitar().chord("Bbsus4")
    fretted = [f for f in fg.positions if f not in (None, 0)]
    assert sum(1 for f in fg.positions if f is not None) >= 2
    if fretted:
        assert max(fretted) - min(fretted) <= 4


def test_unparseable_chord_still_raises():
    with pytest.raises(ValueError):
        Fretboard.guitar().tab_image("not-a-chord")
