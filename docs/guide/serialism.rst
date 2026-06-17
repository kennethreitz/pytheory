Twelve-Tone Serialism
=====================

`Twelve-tone technique <https://en.wikipedia.org/wiki/Twelve-tone_technique>`_
(serialism), devised by Arnold Schoenberg in the 1920s, is a way of
writing music in which **no note is allowed to feel like "home."** It
sounds intimidating, but the mechanism is one of the simplest in all of
music theory — it's just arithmetic on the numbers 0–11.

The tone row
------------

A **tone row** is an ordering of all twelve pitch classes (C, C#, D, … B)
in which each one appears exactly once. It isn't a melody — there's no
rhythm — it's the raw pitch material the piece is built from. Because you
cycle through all twelve before any can repeat, no note gets the emphasis
that would make it a tonic, and the music floats free of any key.

.. code-block:: pycon

   >>> from pytheory import ToneRow
   >>> row = ToneRow.from_names("C", "C#", "E", "D", "F", "D#",
   ...                          "F#", "A", "G#", "G", "B", "A#")
   >>> row
   <ToneRow C C# E D F D# F# A G# G B A#>

You can also build one straight from pitch-class numbers (``0`` = C):

.. code-block:: pycon

   >>> ToneRow([0, 1, 4, 2, 5, 3, 6, 9, 8, 7, 11, 10])
   <ToneRow C C# E D F D# F# A G# G B A#>

PyTheory checks that what you pass really is a row — all twelve pitch
classes, no repeats — so a typo can't slip through.

The four operations
-------------------

From a single row you derive **48 forms**: four operations, each at any of
the twelve transpositions. Every operation is just list arithmetic:

- **Prime (P)** — the row as written.
- **Retrograde (R)** — the row backwards.
- **Inversion (I)** — every interval flipped upside-down (a step up
  becomes the same step down).
- **Retrograde-Inversion (RI)** — the inversion, backwards.

The number you pass is the **pitch class the form begins on**, so ``P(0)``
starts on C and ``P(7)`` starts on G:

.. code-block:: pycon

   >>> row.note_names("P0")
   ['C', 'C#', 'E', 'D', 'F', 'D#', 'F#', 'A', 'G#', 'G', 'B', 'A#']
   >>> row.note_names("I0")          # intervals mirrored
   ['C', 'B', 'G#', 'A#', 'G', 'A', 'F#', 'D#', 'E', 'F', 'C#', 'D']
   >>> row.R(0) == row.P(0)[::-1]    # retrograde really is "backwards"
   True

Look up any form by label with ``row.form("P0")`` (also ``"I7"``, ``"R5"``,
``"RI11"``), or grab all 48 at once with ``row.all_forms()``.

The matrix
----------

The **row matrix** is a 12×12 grid that holds all 48 forms at once. ``P0``
runs across the top, ``I0`` down the left side, and the rest is filled in
by addition. To read it:

- a **row**, left → right, is a **Prime** form (right → left, a Retrograde);
- a **column**, top → bottom, is an **Inversion** (bottom → top, a
  Retrograde-Inversion).

.. code-block:: pycon

   >>> print(row.matrix_str())
          I0  I1  I4  I2  I5  I3  I6  I9  I8  I7 I11 I10
     P0    C  C#   E   D   F  D#  F#   A  G#   G   B  A#   R0
    P11    B   C  D#  C#   E   D   F  G#   G  F#  A#   A   R11
     P8   G#   A   C  A#  C#   B   D   F   E  D#   G  F#   R8
    P10   A#   B   D   C  D#  C#   E   G  F#   F   A  G#   R10
     P7    G  G#   B   A   C  A#  C#   E  D#   D  F#   F   R7
     P9    A  A#  C#   B   D   C  D#  F#   F   E  G#   G   R9
     P6   F#   G  A#  G#   B   A   C  D#   D  C#   F   E   R6
     P3   D#   E   G   F  G#  F#   A   C   B  A#   D  C#   R3
     P4    E   F  G#  F#   A   G  A#  C#   C   B  D#   D   R4
     P5    F  F#   A   G  A#  G#   B   D  C#   C   E  D#   R5
     P1   C#   D   F  D#  F#   E   G  A#   A  G#   C   B   R1
     P2    D  D#  F#   E   G   F  G#   B  A#   A  C#   C   R2
         RI0 RI1 RI4 RI2 RI5 RI3 RI6 RI9 RI8 RI7RI11RI10

Why you can trust it
--------------------

You don't have to take the theory on faith — the matrix is **self-checking**.
Because every form is a rearrangement of the same twelve numbers, three
properties must always hold, and PyTheory's tests assert exactly these:

.. code-block:: pycon

   >>> m = row.matrix()
   >>> all(sorted(r) == list(range(12)) for r in m)        # every row complete
   True
   >>> all(sorted(c) == list(range(12)) for c in zip(*m))  # every column complete
   True
   >>> all(m[i][i] == 0 for i in range(12))                # diagonal all zeros
   True

If any of those failed, the matrix would be wrong — so a glance confirms
it's right.

All-interval rows
-----------------

Some rows are special. An **all-interval row** uses each of the eleven
intervals (1–11 semitones) exactly once as it steps from note to note — a
prized bit of craftsmanship. ``row.is_all_interval`` checks for it, and
``row.interval_succession`` shows the intervals:

.. code-block:: pycon

   >>> wedge = ToneRow([0, 11, 1, 10, 2, 9, 3, 8, 4, 7, 5, 6])
   >>> wedge.interval_succession
   [11, 2, 9, 4, 7, 6, 5, 8, 3, 10, 1]
   >>> wedge.is_all_interval
   True

That's the whole technique. Pick twelve notes, agree never to favour one,
and let these four operations spin the material into a piece.
