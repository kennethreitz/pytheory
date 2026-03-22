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

   # Guitars
   guitar  = Fretboard.guitar()             # Standard EADGBE
   twelve  = Fretboard.twelve_string()       # 12-string (6 doubled courses)
   bass    = Fretboard.bass()               # Standard EADG
   bass5   = Fretboard.bass(five_string=True)  # 5-string BEADG

   # Plucked strings
   ukulele  = Fretboard.ukulele()            # GCEA (re-entrant)
   mandolin = Fretboard.mandolin()           # GDAE (tuned in 5ths)
   banjo    = Fretboard.banjo()              # Open G (5-string with drone)

   # Bowed strings
   violin = Fretboard.violin()              # GDAE
   viola  = Fretboard.viola()               # CGDA (5th below violin)
   cello  = Fretboard.cello()               # CGDA (octave below viola)

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

The String Family
-----------------

All four members of the orchestral string family are tuned in
`perfect fifths <https://en.wikipedia.org/wiki/Perfect_fifth>`_
(7 semitones between adjacent strings):

.. code-block:: python

   violin = Fretboard.violin()   # E5 A4 D4 G3  — soprano
   viola  = Fretboard.viola()    # A4 D4 G3 C3  — alto (5th below violin)
   cello  = Fretboard.cello()    # A3 D3 G2 C2  — tenor/bass (octave below viola)

Unlike fretted instruments, bowed strings have no frets — the player
can produce any pitch along the fingerboard, enabling vibrato and
microtonal inflections.

Other String Instruments
------------------------

.. code-block:: python

   mandolin = Fretboard.mandolin()          # E5 A4 D4 G3 (violin tuning)
   banjo    = Fretboard.banjo()             # Open G (with high drone string)
   banjo_d  = Fretboard.banjo("open d")     # Open D (clawhammer)
   twelve   = Fretboard.twelve_string()     # 12 strings (6 doubled courses)

Custom Instruments
------------------

Any stringed instrument can be modeled:

.. code-block:: python

   from pytheory import Tone, Fretboard

   # Mandola (octave below mandolin, like viola to violin)
   mandola = Fretboard(tones=[
       Tone.from_string("E4"),
       Tone.from_string("A3"),
       Tone.from_string("D3"),
       Tone.from_string("G2"),
   ])

   # Baritone ukulele (DGBE — like the top 4 guitar strings)
   bari_uke = Fretboard(tones=[
       Tone.from_string("E4"),
       Tone.from_string("B3"),
       Tone.from_string("G3"),
       Tone.from_string("D3"),
   ])

   # Double bass / upright bass
   upright = Fretboard(tones=[
       Tone.from_string("G2"),
       Tone.from_string("D2"),
       Tone.from_string("A1"),
       Tone.from_string("E1"),
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
