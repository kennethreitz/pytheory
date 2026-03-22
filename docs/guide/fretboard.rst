Fretboard and Fingerings
========================

The :class:`~pytheory.chords.Fretboard` class represents a fretted instrument's
tuning and generates chord fingerings.

How Frets Work
--------------

Each `fret <https://en.wikipedia.org/wiki/Fret>`_ on a guitar (or any fretted instrument) raises the pitch by
exactly **one semitone**. The open string is fret 0; fret 1 is one
semitone up, fret 2 is two semitones up, and so on.

`Standard guitar tuning <https://en.wikipedia.org/wiki/Guitar_tunings>`_ (high to low)::

    String 1: E4  (highest)
    String 2: B3
    String 3: G3
    String 4: D3
    String 5: A2
    String 6: E2  (lowest)

This tuning uses intervals of a perfect 4th (5 semitones) between most
strings, except between G and B which is a major 3rd (4 semitones). This
asymmetry is why guitar chord shapes shift when they cross the G-B pair.

Preset Tunings
--------------

.. code-block:: python

   from pytheory import Fretboard

   guitar  = Fretboard.guitar()             # Standard EADGBE
   bass    = Fretboard.bass()               # Standard EADG
   bass5   = Fretboard.bass(five_string=True)  # 5-string BEADG
   ukulele = Fretboard.ukulele()            # GCEA (re-entrant)

Alternate Guitar Tunings
~~~~~~~~~~~~~~~~~~~~~~~~

PyTheory supports several common alternate tunings, including
`open tunings <https://en.wikipedia.org/wiki/Open_tuning>`_,
`Drop D <https://en.wikipedia.org/wiki/Drop_D_tuning>`_, and
`DADGAD <https://en.wikipedia.org/wiki/DADGAD>`_:

.. code-block:: python

   # Built-in alternate tunings
   drop_d = Fretboard.guitar("drop d")       # DADGBE — heavy riffs
   open_g = Fretboard.guitar("open g")       # DGDGBD — slide guitar, Keith Richards
   open_d = Fretboard.guitar("open d")       # DADF#AD — slide, folk
   open_e = Fretboard.guitar("open e")       # EBEG#BE — slide blues
   open_a = Fretboard.guitar("open a")       # EAC#EAE
   dadgad = Fretboard.guitar("dadgad")       # DADGAD — Celtic, fingerstyle
   half_down = Fretboard.guitar("half step down")  # Eb standard — Hendrix, SRV

   # Custom tuning with any notes
   custom = Fretboard.guitar(("D4", "A3", "F#3", "D3", "A2", "D2"))

Custom Instruments
------------------

Any fretted instrument can be modeled, including `banjo <https://en.wikipedia.org/wiki/Banjo>`_,
`mandolin <https://en.wikipedia.org/wiki/Mandolin>`_, and more:

.. code-block:: python

   from pytheory import Tone, Fretboard

   # Banjo (open G tuning)
   banjo = Fretboard(tones=[
       Tone.from_string("D4"),
       Tone.from_string("B3"),
       Tone.from_string("G3"),
       Tone.from_string("D3"),
       Tone.from_string("G4"),  # 5th string (high drone)
   ])

   # Mandolin
   mandolin = Fretboard(tones=[
       Tone.from_string("E5"),
       Tone.from_string("A4"),
       Tone.from_string("D4"),
       Tone.from_string("G3"),
   ])

Getting Fingerings
------------------

The fingering algorithm finds the most playable voicing for any chord on
any fretboard. It scores each possibility by:

1. Preferring **open strings** (fret 0) — they ring freely
2. Preferring **ascending** fret patterns — easier hand position
3. Minimizing the number of **fingers needed**

.. code-block:: python

   from pytheory import Fretboard, CHARTS

   fb = Fretboard.guitar()
   c = CHARTS["western"]["C"]

   # Best single fingering
   print(c.fingering(fretboard=fb))
   # (0, 1, 0, 2, 3, 0)
   # String: E4=0  B3=1  G3=0  D3=2  A2=3  E2=0

   # All equally-scored fingerings
   all_c = c.fingering(fretboard=fb, multiple=True)

   # Muted strings appear as None
   f = CHARTS["western"]["F"]
   print(f.fingering(fretboard=fb))

Reading Fingerings
~~~~~~~~~~~~~~~~~~

The tuple ``(0, 1, 0, 2, 3, 0)`` reads from the highest string to the
lowest::

    e|--0--    (open — E)
    B|--1--    (fret 1 — C)
    G|--0--    (open — G)
    D|--2--    (fret 2 — E)
    A|--3--    (fret 3 — C)
    E|--0--    (open — E)

A value of ``None`` means the string is muted (not played).

Generating Full Charts
----------------------

Generate fingerings for every chord at once:

.. code-block:: python

   from pytheory import Fretboard, charts_for_fretboard

   fb = Fretboard.guitar()
   chart = charts_for_fretboard(fretboard=fb)

   for name, fingering in chart.items():
       print(f"{name:6s} {fingering}")

`Ukulele <https://en.wikipedia.org/wiki/Ukulele>`_ Example
---------------

.. code-block:: python

   fb = Fretboard.ukulele()
   c = CHARTS["western"]["C"]
   print(c.fingering(fretboard=fb))  # 4-string fingering
