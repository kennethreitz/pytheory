"""Tests for twelve-tone tone rows and the row matrix.

These lean on the fact that serialism is pure mod-12 arithmetic: the
results are *self-verifying* — every derived form is a permutation of all
twelve pitch classes, and every row and column of the matrix contains each
pitch class exactly once.
"""
import pytest

from pytheory import ToneRow


CHROMATIC = list(range(12))
WEDGE = [0, 11, 1, 10, 2, 9, 3, 8, 4, 7, 5, 6]   # a classic all-interval row
EXAMPLE = [0, 1, 4, 2, 5, 3, 6, 9, 8, 7, 11, 10]


# ── Construction & validation ──────────────────────────────────────────

def test_row_must_be_a_permutation_of_all_twelve():
    with pytest.raises(ValueError, match="all 12 pitch classes"):
        ToneRow([0, 1, 2])                       # too short
    with pytest.raises(ValueError, match="all 12 pitch classes"):
        ToneRow([0] * 12)                        # repeats
    with pytest.raises(ValueError, match="all 12 pitch classes"):
        ToneRow([0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])


def test_from_names_matches_numbers():
    named = ToneRow.from_names("C", "C#", "E", "D", "F", "D#",
                               "F#", "A", "G#", "G", "B", "A#")
    assert named.row == EXAMPLE


# ── The four operations ────────────────────────────────────────────────

def test_each_form_is_a_permutation_of_all_twelve():
    row = ToneRow(EXAMPLE)
    for n in range(12):
        for form in (row.P(n), row.I(n), row.R(n), row.RI(n)):
            assert sorted(form) == CHROMATIC


def test_forms_begin_on_their_transposition():
    row = ToneRow(EXAMPLE)
    for n in range(12):
        assert row.P(n)[0] == n
        assert row.I(n)[0] == n


def test_retrograde_and_ri_are_reversals():
    row = ToneRow(EXAMPLE)
    for n in range(12):
        assert row.R(n) == row.P(n)[::-1]
        assert row.RI(n) == row.I(n)[::-1]


def test_inversion_mirrors_intervals():
    row = ToneRow(EXAMPLE)
    p = row.P(0)
    inv = row.I(0)
    for k in range(1, 12):
        up = (p[k] - p[0]) % 12
        down = (inv[k] - inv[0]) % 12
        assert (up + down) % 12 == 0          # mirror-image intervals


def test_form_lookup_by_label():
    row = ToneRow(CHROMATIC)
    assert row.form("P0") == CHROMATIC
    assert row.form("R0") == CHROMATIC[::-1]
    assert row.form("I7") == row.I(7)
    assert row.form("RI11") == row.RI(11)
    with pytest.raises(ValueError):
        row.form("Q3")
    with pytest.raises(ValueError):
        row.form("P12")


def test_all_forms_has_forty_eight():
    forms = ToneRow(EXAMPLE).all_forms()
    assert len(forms) == 48
    assert forms["P0"] == ToneRow(EXAMPLE).P(0)


# ── The matrix (self-verifying properties) ─────────────────────────────

def test_matrix_rows_and_columns_are_permutations():
    m = ToneRow(EXAMPLE).matrix()
    assert len(m) == 12 and all(len(r) == 12 for r in m)
    for r in m:
        assert sorted(r) == CHROMATIC              # every row
    for col in zip(*m):
        assert sorted(col) == CHROMATIC            # every column


def test_matrix_diagonal_is_zero_and_edges_are_p0_i0():
    row = ToneRow(EXAMPLE)
    m = row.matrix()
    assert all(m[i][i] == 0 for i in range(12))    # main diagonal
    assert m[0] == row.P(0)                         # top row = P0
    assert [m[i][0] for i in range(12)] == row.I(0) # left column = I0


def test_matrix_str_is_printable():
    text = ToneRow(EXAMPLE).matrix_str()
    assert text.count("\n") == 13                  # 12 rows + 2 label lines
    assert "P0" in text and "I0" in text and "RI" in text


# ── Analysis ───────────────────────────────────────────────────────────

def test_all_interval_row_detection():
    assert ToneRow(WEDGE).is_all_interval
    assert sorted(ToneRow(WEDGE).interval_succession) == list(range(1, 12))
    # The plain chromatic scale is *not* all-interval (every step is 1).
    assert not ToneRow(CHROMATIC).is_all_interval


def test_note_names():
    assert ToneRow(CHROMATIC).note_names("P0")[:3] == ["C", "C#", "D"]
