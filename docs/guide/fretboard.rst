Fretboard and Fingerings
========================

The :class:`~pytheory.chords.Fretboard` class represents a fretted instrument's
tuning and generates chord fingerings.

Preset Tunings
--------------

.. code-block:: python

   from pytheory import Fretboard

   guitar  = Fretboard.guitar()    # E4 B3 G3 D3 A2 E2
   bass    = Fretboard.bass()      # G2 D2 A1 E1
   ukulele = Fretboard.ukulele()   # A4 E4 C4 G4

Custom Tunings
--------------

.. code-block:: python

   from pytheory import Tone, Fretboard

   # Open D tuning
   open_d = Fretboard(tones=[
       Tone.from_string("D4"),
       Tone.from_string("A3"),
       Tone.from_string("F#3"),
       Tone.from_string("D3"),
       Tone.from_string("A2"),
       Tone.from_string("D2"),
   ])

Getting Fingerings
------------------

.. code-block:: python

   from pytheory import Fretboard, CHARTS

   fb = Fretboard.guitar()

   # Best fingering for a chord
   c = CHARTS["western"]["C"]
   print(c.fingering(fretboard=fb))
   # (0, 1, 0, 2, 3, 0)

   # All possible fingerings
   all_c = c.fingering(fretboard=fb, multiple=True)

   # Muted strings appear as None
   f = CHARTS["western"]["F"]
   print(f.fingering(fretboard=fb))

Generating Full Charts
----------------------

Generate fingerings for every chord at once:

.. code-block:: python

   from pytheory import Fretboard, charts_for_fretboard

   fb = Fretboard.guitar()
   chart = charts_for_fretboard(fretboard=fb)

   for name, fingering in chart.items():
       print(f"{name:6s} {fingering}")

Ukulele Example
---------------

.. code-block:: python

   fb = Fretboard.ukulele()
   c = CHARTS["western"]["C"]
   print(c.fingering(fretboard=fb))  # 4-string fingering
