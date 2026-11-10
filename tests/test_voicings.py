"""Several playable chord grips, in any tuning or capo.

The single-fingering default in standard tuning stays on the curated
shapes. ``multiple=True`` searches the neck and ranks what a hand can
actually play. See ``pytheory.voicings`` for the cost.
"""

import pytest

from pytheory import Fretboard, CHARTS
from pytheory.charts import GUITAR_OVERRIDES
from pytheory.voicings import (
    DEFAULT_VOICING_LIMIT,
    MAX_SPAN,
    pitch_class,
    plan_fingers,
    relative_shape,
    required_pitch_classes,
    score_voicing,
)


# Textbook grips, low string first. These are also the curated overrides.
_STANDARD = {
    "C": (None, 3, 2, 0, 1, 0),
    "G": (3, 2, 0, 0, 0, 3),
    "D": (None, None, 0, 2, 3, 2),
    "Am": (None, 0, 2, 2, 1, 0),
    "F": (1, 3, 3, 2, 1, 1),
    "Bm": (None, 2, 4, 4, 3, 2),
    "G7": (3, 2, 0, 0, 0, 1),
}


def _spec(name):
    chord = CHARTS["western"][name]
    pcs = {pitch_class(t) for t in chord.acceptable_tones}
    return pcs, pitch_class(chord.tone)


def _pcs(shape):
    return {t.midi % 12 for t in shape.tones}


def _assert_playable(shape, target, root):
    """A grip the search is allowed to return."""
    positions = shape._positions  # canonical, so adjacent indexes are adjacent strings
    plan = plan_fingers(positions)
    assert plan is not None
    assert plan.n_fingers <= 4
    assert plan.span <= MAX_SPAN
    sounding = [i for i, p in enumerate(positions) if p is not None]
    assert sounding, "a grip has to sound something"
    # Mutes only at the edges: the sounding strings are one contiguous run.
    assert sounding == list(range(sounding[0], sounding[-1] + 1))
    present = _pcs(shape)
    assert required_pitch_classes(target, root) <= present
    assert present <= target


def test_standard_single_fingering_is_unchanged():
    """``chord(name)`` in standard tuning is still the curated grip, not a tuple."""
    fb = Fretboard.guitar()
    for name, positions in _STANDARD.items():
        shape = fb.chord(name)
        assert shape.positions == positions
        assert not isinstance(shape, tuple)


def test_curated_shapes_rank_first():
    fb = Fretboard.guitar()
    for name in GUITAR_OVERRIDES:
        shapes = fb.chord(name, multiple=True)
        assert shapes[0] == fb.chord(name)


def test_multiple_returns_distinct_playable_voicings():
    fb = Fretboard.guitar()
    for name in ["C", "G", "D", "Am", "F", "Bm", "G7", "C7"]:
        target, root = _spec(name)
        shapes = fb.chord(name, multiple=True)
        assert 3 <= len(shapes) <= DEFAULT_VOICING_LIMIT
        assert len({s.positions for s in shapes}) == len(shapes)
        relatives = [relative_shape(s._positions) for s in shapes]
        assert len(set(relatives)) == len(relatives)
        for shape in shapes:
            _assert_playable(shape, target, root)
        lowest = min(shapes[0].tones, key=lambda t: t.midi)
        assert lowest.midi % 12 == root


def test_results_follow_the_cost_order():
    fb = Fretboard.guitar()
    chord = CHARTS["western"]["Am"]
    target, root = _spec("Am")
    shapes = chord.fingering(fretboard=fb, multiple=True)
    costs = [
        score_voicing(s._positions, fb._tones, target_pcs=target, root_pc=root)
        for s in shapes
    ]
    assert costs == sorted(costs)
    # The open Am beats its E-shape barre on that cost.
    assert shapes[0].positions == (None, 0, 2, 2, 1, 0)


def test_movable_shapes_sit_alongside_open_chords():
    fb = Fretboard.guitar()
    c = [s.positions for s in fb.chord("C", multiple=True)]
    assert (None, 3, 2, 0, 1, 0) in c          # open C
    assert (None, 3, 5, 5, 5, 3) in c          # A-shape barre
    g = [s.positions for s in fb.chord("G", multiple=True)]
    assert (3, 2, 0, 0, 0, 3) in g             # open G
    assert (3, 5, 5, 4, 3, 3) in g             # E-shape barre
    f = [s.positions for s in fb.chord("F", multiple=True)]
    assert (1, 3, 3, 2, 1, 1) in f             # full barre
    assert (None, None, 3, 2, 1, 1) in f       # small F
    c7 = fb.chord("C7", multiple=True)
    assert (None, 3, 2, 3, 1, 0) in [s.positions for s in c7]
    seventh = (pitch_class(CHARTS["western"]["C7"].tone) + 10) % 12
    for shape in c7:
        assert seventh in _pcs(shape)


def test_unplayable_grips_are_left_out():
    fb = Fretboard.guitar()
    a = [s.positions for s in fb.chord("A", multiple=True)]
    assert (5, 0, 2, 2, 2, 0) not in a         # thumb-wrap duplicate of x02220
    g = [s.positions for s in fb.chord("G", multiple=True)]
    assert (3, None, 0, 0, 0, 3) not in g      # mute trapped between sounding strings


def test_limit_slices_the_ranked_list():
    fb = Fretboard.guitar()
    two = fb.chord("C", multiple=True, limit=2)
    full = fb.chord("C", multiple=True)
    assert len(two) == 2
    assert list(two) == list(full[:2])
    assert len(full) <= DEFAULT_VOICING_LIMIT
    # limit does not turn the default call into a list
    assert fb.chord("C", limit=3).positions == _STANDARD["C"]
    named = CHARTS["western"]["C"].fingering(fretboard=fb, multiple=True, limit=2)
    assert list(named) == list(two)
    with pytest.raises(ValueError):
        fb.chord("C", multiple=True, limit=0)


def test_drop_d_d_major_uses_the_open_low_string():
    fb = Fretboard.guitar("drop d")
    shapes = fb.chord("D", multiple=True)
    assert shapes[0].positions == (0, 0, 0, 2, 3, 2)
    assert fb.chord("D") == shapes[0]
    target, root = _spec("D")
    assert len(shapes) >= 3
    for shape in shapes:
        _assert_playable(shape, target, root)


def test_open_g_prefers_a_root_and_keeps_the_open_strum():
    fb = Fretboard.guitar("open g")
    shapes = fb.chord("G", multiple=True)
    # Mute the low D and the rest is a G with G in the bass.
    assert shapes[0].positions == (None, 0, 0, 0, 0, 0)
    # The open strum is G with D in the bass, and it is the next grip.
    assert shapes[1].positions == (0, 0, 0, 0, 0, 0)
    assert fb.chord("G") == shapes[0]
    target, root = _spec("G")
    for shape in shapes:
        _assert_playable(shape, target, root)


def test_dadgad_d_major():
    fb = Fretboard.guitar("dadgad")
    shapes = fb.chord("D", multiple=True)
    assert shapes[0].positions == (0, 0, 4, 2, 0, 0)
    assert fb.chord("D") == shapes[0]
    target, root = _spec("D")
    assert len(shapes) >= 3
    for shape in shapes:
        _assert_playable(shape, target, root)


def test_capo_rewrites_open_shapes_into_the_sounding_key():
    """Fret 0 is the capo. A G shape sounds as A, C as D, Am as Bm."""
    fb = Fretboard.guitar(capo=2)
    expect = {
        "A": (3, 2, 0, 0, 0, 3),
        "D": (None, 3, 2, 0, 1, 0),
        "Bm": (None, 0, 2, 2, 1, 0),
    }
    for name, positions in expect.items():
        shapes = fb.chord(name, multiple=True)
        assert shapes[0].positions == positions
        assert fb.chord(name) == shapes[0]
        assert len(shapes) >= 3
        target, root = _spec(name)
        for shape in shapes:
            _assert_playable(shape, target, root)


def test_high_to_low_is_the_same_grips_reversed():
    lo = Fretboard.guitar().chord("F", multiple=True)
    hi = Fretboard.guitar(high_to_low=True).chord("F", multiple=True)
    assert len(lo) == len(hi)
    for a, b in zip(lo, hi):
        assert tuple(a.positions) == tuple(reversed(b.positions))


def test_ukulele_c_is_the_open_shape():
    shape = Fretboard.ukulele().chord("C")
    assert shape.positions == (0, 0, 0, 3)
    shapes = Fretboard.ukulele().chord("C", multiple=True)
    assert shapes[0] == shape
    assert len(shapes) >= 2


def test_uncharted_symbol_can_list_several_grips():
    from pytheory import Chord

    fb = Fretboard.guitar()
    single = fb.chord("F#m7b5")
    assert not isinstance(single, tuple)
    shapes = fb.chord("F#m7b5", multiple=True)
    assert len(shapes) >= 2
    # The diminished fifth is not optional the way a perfect fifth is.
    chord = Chord.from_symbol("F#m7b5")
    target = {t.midi % 12 for t in chord.tones}
    root = chord.root.midi % 12
    assert required_pitch_classes(target, root) == target
    for shape in shapes:
        _assert_playable(shape, target, root)
