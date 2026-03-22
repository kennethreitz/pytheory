Quickstart
==========

Installation
------------

::

   $ pip install pytheory

Basic Usage
-----------

Create tones, build scales, and explore music theory:

.. code-block:: python

   from pytheory import Tone, TonedScale, Fretboard, CHARTS

   # Create a tone
   c4 = Tone.from_string("C4")
   print(c4)           # C4
   print(c4.frequency)  # 261.63 Hz

   # Tone arithmetic
   e4 = c4 + 4          # Major third up
   g4 = c4 + 7          # Perfect fifth up
   print(e4, g4)        # E4 G4

   # Measure intervals
   print(g4 - c4)       # 7 (semitones)

   # Build a scale
   c_major = TonedScale(tonic="C4")["major"]
   print(c_major.note_names)
   # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

   # Build chords from the scale
   I  = c_major.triad(0)   # C major
   IV = c_major.triad(3)   # F major
   V  = c_major.triad(4)   # G major

   # Guitar chord fingerings
   fb = Fretboard.guitar()
   fingering = CHARTS["western"]["Am"].fingering(fretboard=fb)
   print(fingering)  # (0, 1, 2, 2, 0, 0)

What's Included
---------------

- **12-tone Western system** with all chromatic notes
- **Scales**: major, minor, harmonic minor, and all 7 modes
- **Pitch calculation** in equal, Pythagorean, and meantone temperaments
- **Chord charts** with 144 pre-built chords (12 roots x 12 qualities)
- **Fingering generation** for any fretted instrument
- **Audio playback** with sine, sawtooth, and triangle wave synthesis
