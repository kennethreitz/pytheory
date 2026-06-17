"""Twelve-tone serialism — tone rows and the row matrix.

A **tone row** is simply an ordering of all twelve pitch classes
(C, C#, D, … B) in which each appears exactly once. It isn't a melody —
there's no rhythm — it's the raw pitch material a twelve-tone piece draws
on. By always running through all twelve before repeating any, no single
note can act as a tonal "home", which is how Schoenberg's method produces
atonal music on purpose.

From one row you derive **48 forms** via four operations, each at any of
the twelve transpositions:

- **Prime (P)** — the row as written.
- **Retrograde (R)** — the row backwards.
- **Inversion (I)** — every interval flipped upside-down.
- **Retrograde-Inversion (RI)** — the inversion, backwards.

Everything here is plain arithmetic on the numbers 0–11 (mod 12), so the
results are easy to verify: every form is still a permutation of all twelve
pitch classes, and every row and column of the matrix contains each pitch
class exactly once.

Example::

    >>> row = ToneRow.from_names("C", "C#", "E", "D", "F", "D#",
    ...                          "F#", "A", "G#", "G", "B", "A#")
    >>> row.P(0)[:4]          # prime starting on C
    [0, 1, 4, 2]
    >>> row.I(0)[:4]          # inversion starting on C — intervals mirrored
    [0, 11, 8, 10]
    >>> row.R(0) == row.P(0)[::-1]
    True
"""
from __future__ import annotations

from typing import List

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
               "F#", "G", "G#", "A", "A#", "B"]
_NAME_TO_PC = {}
for _pc, _nm in enumerate(_NOTE_NAMES):
    _NAME_TO_PC[_nm] = _pc
# Accept flat spellings too.
_NAME_TO_PC.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10,
                    "Cb": 11, "Fb": 4, "E#": 5, "B#": 0})


def _pc_of(value) -> int:
    """Coerce a note name or number to a pitch class (0–11)."""
    if isinstance(value, str):
        name = value.strip()
        if name not in _NAME_TO_PC:
            raise ValueError(f"Unknown note name: {value!r}")
        return _NAME_TO_PC[name]
    return int(value) % 12


class ToneRow:
    """A twelve-tone row and the 48 forms derived from it.

    Construct from pitch-class numbers (0–11) or note names::

        ToneRow([0, 1, 4, 2, 5, 3, 6, 9, 8, 7, 11, 10])
        ToneRow.from_names("C", "C#", "E", "D", ...)

    The transposition index ``n`` in :meth:`P`, :meth:`I`, :meth:`R`, and
    :meth:`RI` is **the pitch class the form begins on** (the common
    textbook convention). So ``P(0)`` starts on C, ``P(7)`` starts on G,
    and the row you passed in is ``P(row[0])``.
    """

    def __init__(self, pitches):
        pcs = [_pc_of(p) for p in pitches]
        if len(pcs) != 12 or sorted(pcs) != list(range(12)):
            raise ValueError(
                "A tone row must list all 12 pitch classes exactly once; "
                f"got {pitches!r}."
            )
        self.row: List[int] = pcs
        # P0: the row transposed so it starts on pitch class 0.
        self._p0 = [(pc - pcs[0]) % 12 for pc in pcs]
        # I0: invert P0 around 0 (negate each interval from the start).
        self._i0 = [(-pc) % 12 for pc in self._p0]

    # ── Construction ──────────────────────────────────────────────────

    @classmethod
    def from_names(cls, *names: str) -> "ToneRow":
        """Build a row from twelve note names, e.g.
        ``ToneRow.from_names("C", "C#", "E", ...)``."""
        return cls(list(names))

    # ── The four operations (each begins on pitch class n) ────────────

    def P(self, n: int = 0) -> List[int]:
        """**Prime** form beginning on pitch class ``n`` — the row,
        transposed."""
        return [(pc + n) % 12 for pc in self._p0]

    def I(self, n: int = 0) -> List[int]:
        """**Inversion** beginning on pitch class ``n`` — every interval of
        the prime flipped upside-down."""
        return [(pc + n) % 12 for pc in self._i0]

    def R(self, n: int = 0) -> List[int]:
        """**Retrograde** of ``P(n)`` — the prime form played backwards.

        (It *ends* on pitch class ``n``, since it's ``P(n)`` reversed.)
        """
        return self.P(n)[::-1]

    def RI(self, n: int = 0) -> List[int]:
        """**Retrograde-inversion** — ``I(n)`` played backwards."""
        return self.I(n)[::-1]

    def form(self, label: str) -> List[int]:
        """Look up a form by label, e.g. ``"P0"``, ``"I7"``, ``"R5"``,
        ``"RI11"``.

        Example::

            >>> ToneRow(range(12)).form("R0")
            [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        """
        text = label.strip().upper()
        for prefix, op in (("RI", self.RI), ("R", self.R),
                           ("I", self.I), ("P", self.P)):
            if text.startswith(prefix):
                number = text[len(prefix):]
                if not number.isdigit():
                    break
                n = int(number)
                if not 0 <= n <= 11:
                    raise ValueError(f"Transposition must be 0–11, got {n}.")
                return op(n)
        raise ValueError(
            f"Unrecognised row form {label!r}; use P/I/R/RI + 0–11, e.g. 'P0'."
        )

    def all_forms(self) -> dict:
        """Return all 48 forms as a ``{label: [pitch classes]}`` dict
        (``P0``–``P11``, ``I0``–``I11``, ``R0``–``R11``, ``RI0``–``RI11``)."""
        forms = {}
        for n in range(12):
            forms[f"P{n}"] = self.P(n)
            forms[f"I{n}"] = self.I(n)
            forms[f"R{n}"] = self.R(n)
            forms[f"RI{n}"] = self.RI(n)
        return forms

    # ── The matrix ────────────────────────────────────────────────────

    def matrix(self) -> List[List[int]]:
        """The 12×12 row matrix as a list of rows of pitch classes.

        ``P0`` runs along the top, ``I0`` down the left, and the top-left
        to bottom-right diagonal is all zeros. Read a **row** left-to-right
        for a Prime form, right-to-left for a Retrograde; read a **column**
        top-to-bottom for an Inversion, bottom-to-top for a
        Retrograde-Inversion.
        """
        return [[(self._p0[j] + self._i0[i]) % 12 for j in range(12)]
                for i in range(12)]

    def matrix_str(self, names: bool = True) -> str:
        """A printable matrix, labelled with the P/I/R/RI transpositions.

        With ``names=True`` cells show note names; otherwise pitch-class
        numbers. The left edge labels each row's Prime form and the right
        edge its Retrograde; the top labels each column's Inversion and the
        bottom its Retrograde-Inversion.
        """
        grid = self.matrix()
        cell = (lambda pc: _NOTE_NAMES[pc]) if names else (lambda pc: str(pc))
        w = 4  # uniform column width keeps everything aligned

        def fmt_row(values):
            return "".join(f"{v:>{w}}" for v in values)

        edge = " " * 5
        lines = [edge + fmt_row([f"I{grid[0][j]}" for j in range(12)])]
        for r in grid:
            cells = fmt_row([cell(pc) for pc in r])
            lines.append(f"{('P' + str(r[0])):>4} {cells}   {'R' + str(r[0])}")
        lines.append(edge + fmt_row([f"RI{grid[0][j]}" for j in range(12)]))
        return "\n".join(lines)

    # ── Names + analysis ──────────────────────────────────────────────

    def note_names(self, form: str = "P0") -> List[str]:
        """Note names for a given form label (default ``"P0"``)."""
        return [_NOTE_NAMES[pc] for pc in self.form(form)]

    @property
    def interval_succession(self) -> List[int]:
        """The eleven ordered intervals (1–11 semitones) between successive
        notes of the row."""
        return [(self.row[k + 1] - self.row[k]) % 12 for k in range(11)]

    @property
    def is_all_interval(self) -> bool:
        """``True`` if this is an *all-interval row* — its eleven successive
        intervals use each of the intervals 1–11 exactly once.

        Example::

            >>> ToneRow([0, 11, 1, 10, 2, 9, 3, 8, 4, 7, 5, 6]).is_all_interval
            True
        """
        return sorted(self.interval_succession) == list(range(1, 12))

    def __repr__(self) -> str:
        return f"<ToneRow {' '.join(_NOTE_NAMES[pc] for pc in self.row)}>"

    def __eq__(self, other) -> bool:
        return isinstance(other, ToneRow) and self.row == other.row

    def __len__(self) -> int:
        return 12
