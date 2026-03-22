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

   # Create a tone — A4 is the tuning standard (440 Hz)
   a4 = Tone.from_string("A4", system="western")
   print(a4.frequency)  # 440.0

   # Tone arithmetic — add semitones to move up the chromatic scale
   c4 = Tone.from_string("C4", system="western")
   e4 = c4 + 4          # Major third up (4 semitones)
   g4 = c4 + 7          # Perfect fifth up (7 semitones)
   print(e4, g4)         # E4 G4

   # Measure intervals between tones
   print(g4 - c4)        # 7 (semitones — a perfect fifth)

   # Build a C major scale
   c_major = TonedScale(tonic="C4")["major"]
   print(c_major.note_names)
   # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

   # Build diatonic triads from the scale
   I  = c_major.triad(0)   # C E G  (C major)
   IV = c_major.triad(3)   # F A C  (F major)
   V  = c_major.triad(4)   # G B D  (G major)

   # Guitar chord fingerings — labeled with string names
   fb = Fretboard.guitar()
   fingering = CHARTS["western"]["Am"].fingering(fretboard=fb)
   print(fingering)  # Fingering(e=0, B=1, G=2, D=2, A=0, E=0)

   # Identify a chord from fret positions
   f = fb.fingering(0, 1, 0, 2, 3, 0)
   print(f.identify())  # C major

What's Included
---------------

- **6 musical systems**: Western, Indian (Hindustani), Arabic (Maqam),
  Japanese, Blues/Pentatonic, Javanese Gamelan
- **40+ scales**: major, minor, harmonic minor, 7 modes, 10 thaats,
  10 maqamat, 6 Japanese pentatonic scales, blues, pentatonic,
  slendro, pelog, and more
- **Pitch calculation** in equal, Pythagorean, and meantone temperaments
- **Chord identification**: name any chord from its notes, intervals, or
  MIDI numbers (17 chord types recognized)
- **Chord charts** with 144 pre-built chords (12 roots x 12 qualities)
- **Chord analysis**: consonance scoring, Plomp-Levelt dissonance,
  beat frequency calculation, harmonic tension, voice leading
- **Key detection** and **Roman numeral analysis** (I-IV-V-I progressions)
- **Fingering generation** for 25 instruments with labeled string names,
  including guitar (8 tunings), bass, ukulele, mandolin, and more
- **Audio playback** with sine, sawtooth, and triangle wave synthesis
