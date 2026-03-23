PyTheory: Music Theory for Humans
=================================

**PyTheory** is a Python library that makes exploring music theory
approachable and fun. Work with tones, scales, chords, keys, and
instruments using a clean, Pythonic API.

::

   $ pip install pytheory

.. code-block:: python

   from pytheory import Key, Chord, Tone, Fretboard

   # Explore a key
   key = Key("C", "major")
   key.chords
   # ['C major', 'D minor', 'E minor', 'F major',
   #  'G major', 'A minor', 'B diminished']

   # Build a chord progression
   [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   # ['C major', 'G major', 'A minor', 'F major']

   # Identify any chord
   Chord.from_tones("Bb", "D", "F").identify()   # 'Bb major'

   # Name the interval
   c4 = Tone.from_string("C4", system="western")
   c4.interval_to(c4 + 7)   # 'perfect 5th'

   # Guitar fingerings with labeled strings
   fb = Fretboard.guitar()
   fb.fingering(0, 1, 0, 2, 3, 0)
   # Fingering(e=0, B=1, G=0, D=2, A=3, E=0)  →  C major

It also works from the command line::

   $ pytheory key G major
   $ pytheory chord C E G
   $ pytheory play Am7 --synth triangle

Highlights
----------

- **Tones**: frequencies, MIDI, intervals, transposition, circle of fifths,
  overtone series, 3 temperaments (equal, Pythagorean, meantone)
- **Scales**: 40+ scales across 6 musical systems — Western, Indian,
  Arabic, Japanese, Blues, Javanese Gamelan
- **Chords**: 17 chord types identified automatically, Roman numeral
  analysis, tension scoring, voice leading, consonance/dissonance
- **Keys**: key detection, signatures, progressions (Roman numerals and
  Nashville numbers), borrowed chords, secondary dominants
- **Instruments**: 25 presets (guitar, bass, ukulele, mandolin, violin,
  banjo, oud, sitar, erhu, and more) with fingering generation
- **Audio**: sine, sawtooth, and triangle wave playback + WAV export

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/quickstart
   guide/theory
   guide/tones
   guide/scales
   guide/chords
   guide/fretboard
   guide/systems
   guide/playback
   guide/cli

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/tones
   api/scales
   api/chords
   api/charts
   api/play
   api/systems
