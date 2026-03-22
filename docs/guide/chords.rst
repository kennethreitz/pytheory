Working with Chords
===================

Chords and Chord Charts
-----------------------

PyTheory provides two chord-related classes:

- :class:`~pytheory.chords.Chord` — a collection of tones played together
- :class:`~pytheory.charts.NamedChord` — a chord from the chart database with
  fingering support

Using the Chord Chart
---------------------

The built-in chart contains 144 chords (12 roots x 12 qualities):

.. code-block:: python

   from pytheory import CHARTS

   chart = CHARTS["western"]

   # Access a chord
   c_major = chart["C"]
   a_minor = chart["Am"]
   g_seven = chart["G7"]

   # Available qualities: "", "maj", "m", "5", "7", "9",
   # "dim", "m6", "m7", "m9", "maj7", "maj9"

Chord Tones
-----------

Each named chord knows which tones it contains:

.. code-block:: python

   >>> chart["C"].acceptable_tone_names
   ('C', 'E', 'G')

   >>> chart["Am"].acceptable_tone_names
   ('A', 'C', 'E')

   >>> chart["G7"].acceptable_tone_names
   ('G', 'B', 'D', 'F')

Building Chords Manually
-------------------------

.. code-block:: python

   from pytheory import Tone, Chord

   c_major = Chord(tones=[
       Tone.from_string("C4", system="western"),
       Tone.from_string("E4", system="western"),
       Tone.from_string("G4", system="western"),
   ])

   # Iteration
   for tone in c_major:
       print(tone)

   len(c_major)       # 3
   "C" in c_major     # True

Chord Properties
----------------

.. code-block:: python

   # Frequency intervals between adjacent tones (Hz)
   c_major.intervals

   # Harmony score (higher = more consonant intervals)
   c_major.harmony

   # Dissonance score (higher = wider intervals)
   c_major.dissonance

   # Beat frequency between closest tone pair
   c_major.beat_pulse
