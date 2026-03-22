PyTheory: Music Theory for Humans
=================================

**PyTheory** is a Python library that makes exploring music theory approachable.
Work with tones, scales, chords, and fretboards using a clean, Pythonic API.

.. code-block:: python

   from pytheory import TonedScale, Fretboard, CHARTS

   # Build a C major scale
   c_major = TonedScale(tonic="C4")["major"]
   print(c_major.note_names)
   # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

   # Build a triad from the scale
   chord = c_major.triad(0)  # C major triad
   for tone in chord:
       print(f"{tone}: {tone.frequency:.1f} Hz")

   # Get guitar fingerings
   fb = Fretboard.guitar()
   print(CHARTS["western"]["C"].fingering(fretboard=fb))

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/quickstart
   guide/tones
   guide/scales
   guide/chords
   guide/fretboard
   guide/playback

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/tones
   api/scales
   api/chords
   api/charts
   api/play
   api/systems
