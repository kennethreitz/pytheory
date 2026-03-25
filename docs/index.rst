PyTheory: Music Theory for Humans
=================================

**PyTheory** is a Python library that makes exploring music theory
approachable and fun. Work with tones, scales, chords, keys, and
instruments using a clean, Pythonic API.

::

   $ pip install pytheory

.. code-block:: pycon

   >>> from pytheory import Key, Chord, Tone, Scale, Fretboard

   >>> key = Key("C", "major")
   >>> key.chords
   ['C major', 'D minor', 'E minor', 'F major',
    'G major', 'A minor', 'B diminished']

   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['C major', 'G major', 'A minor', 'F major']

   >>> Chord.from_tones("Bb", "D", "F").identify()
   'Bb major'

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4.interval_to(c4 + 7)
   'perfect 5th'

   >>> fb = Fretboard.guitar()
   >>> fb.chord("G")
   Fingering(e=3, B=0, G=0, D=0, A=2, E=3)

   >>> pentatonic = Scale(tonic="A4", system="blues")["minor pentatonic"]
   >>> print(fb.scale_diagram(pentatonic, frets=5))
       0   1   2   3   4   5
   E| E | - | - | G | - | A |
   B| - | C | - | D | - | E |
   G| G | - | A | - | - | C |
   D| D | - | E | - | - | G |
   A| A | - | - | C | - | D |
   E| E | - | - | G | - | A |

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

It also works from the command line::

   $ pytheory key G major
     Key: G major
     Signature: 1 sharps, 0 flats (F#)
     Scale: G A B C D E F# G
     ...

   $ pytheory chord C E G
     Chord:     C major
     Tones:     C4 E4 G4
     Intervals: [4, 3]
     ...

   $ pytheory play Am7 --synth triangle
     Playing: A minor 7th (A4 C4 E4 G4)
     Synth:   triangle

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
   guide/rhythm
   guide/playback
   guide/cli
   guide/cookbook

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/tones
   api/scales
   api/chords
   api/charts
   api/play
   api/systems

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog
