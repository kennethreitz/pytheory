Working with Scales
===================

Scales are sequences of tones following a specific interval pattern.

Building Scales
---------------

Use :class:`~pytheory.scales.TonedScale` to generate scales in any key:

.. code-block:: python

   from pytheory import TonedScale

   c = TonedScale(tonic="C4")

   # Access scales by name
   major = c["major"]
   minor = c["minor"]
   harmonic_minor = c["harmonic minor"]

   print(major.note_names)
   # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

Available Scales
----------------

.. code-block:: python

   >>> c = TonedScale(tonic="C4")
   >>> c.scales
   ('chromatic', 'major', 'minor', 'harmonic minor',
    'ionian', 'dorian', 'phrygian', 'lydian',
    'mixolydian', 'aeolian', 'locrian')

Modes
-----

All seven modes of the major scale are supported:

.. code-block:: python

   c = TonedScale(tonic="C4")

   c["ionian"]      # Same as major: C D E F G A B C
   c["dorian"]       # C D Eb F G A Bb C
   c["phrygian"]     # C Db Eb F G Ab Bb C
   c["lydian"]       # C D E F# G A B C
   c["mixolydian"]   # C D E F G A Bb C
   c["aeolian"]      # Same as minor: C D Eb F G Ab Bb C
   c["locrian"]      # C Db Eb F Gb Ab Bb C

Accessing Degrees
-----------------

Scale tones can be accessed by index, Roman numeral, or degree name:

.. code-block:: python

   major = TonedScale(tonic="C4")["major"]

   # By index
   major[0]           # C4
   major[4]           # G4

   # By Roman numeral
   major["I"]         # C4
   major["V"]         # G4

   # By degree name
   major["tonic"]     # C4
   major["dominant"]  # G4

   # Slicing
   major[0:3]         # (C4, D4, E4)

Iteration
---------

Scales are iterable:

.. code-block:: python

   for tone in major:
       print(f"{tone.name}: {tone.frequency:.1f} Hz")

   len(major)         # 8 (7 notes + octave)
   "C" in major       # True
   "C#" in major      # False

Building Chords from Scales
----------------------------

Build chords directly from scale degrees:

.. code-block:: python

   major = TonedScale(tonic="C4")["major"]

   # Build a triad (root, 3rd, 5th)
   I  = major.triad(0)   # C E G  (C major)
   ii = major.triad(1)   # D F A  (D minor)
   V  = major.triad(4)   # G B D  (G major)

   # Custom chord voicings
   cmaj7 = major.chord(0, 2, 4, 6)  # C E G B
