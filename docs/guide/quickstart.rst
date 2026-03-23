Quickstart
==========

Installation
------------

::

   $ pip install pytheory

For audio playback, you'll also need `PortAudio <http://www.portaudio.com/>`_:

- macOS: ``brew install portaudio``
- Ubuntu: ``apt install libportaudio2``
- Windows: included with the ``sounddevice`` package

Tones
-----

A :class:`~pytheory.tones.Tone` is a single musical note:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.frequency
   440.0

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4.midi
   60

   >>> Tone.from_frequency(440)
   <Tone A4>
   >>> Tone.from_midi(60)
   <Tone C4>

   >>> c4 + 4
   <Tone E4>
   >>> c4 + 7
   <Tone G4>

   >>> g4 = c4 + 7
   >>> g4 - c4
   7
   >>> c4.interval_to(g4)
   'perfect 5th'

   >>> Tone.from_string("C#4", system="western").enharmonic
   'Db'

Scales
------

Build scales in any key and mode:

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4")

   >>> c["major"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

   >>> c["minor"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb', 'C']

   >>> c["dorian"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb', 'C']

   >>> major = c["major"]
   >>> major["tonic"]
   C4
   >>> major["dominant"]
   G4
   >>> major["V"]
   G4

Keys and Chords
---------------

The :class:`~pytheory.scales.Key` class ties everything together —
scales, chords, and progressions:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> key = Key("G", "major")
   >>> key.note_names
   ['G', 'A', 'B', 'C', 'D', 'E', 'F#', 'G']

   >>> key.chords
   ['G major', 'A minor', 'B minor', 'C major', 'D major', 'E minor', 'F# diminished']

   >>> chords = key.progression("I", "V", "vi", "IV")
   >>> [c.identify() for c in chords]
   ['G major', 'D major', 'E minor', 'C major']

   >>> Key.detect("C", "E", "G", "A", "D")
   <Key C major>

Build chords directly:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_tones("C", "E", "G")
   <Chord C major>
   >>> Chord.from_name("Am7")
   <Chord A minor 7th>
   >>> Chord.from_intervals("G", 4, 7, 10)
   <Chord G dominant 7th>

   >>> Chord.from_tones("Bb", "D", "F").identify()
   'Bb major'

   >>> Chord.from_name("G7").analyze("C")
   'V7'

Guitar Fingerings
-----------------

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()

   >>> fb.chord("C")
   Fingering(e=0, B=1, G=0, D=2, A=3, E=x)

   >>> fb.chord("C")['A']
   3

   >>> fb.fingering(0, 0, 0, 2, 2, 0).identify()
   'E minor'

   >>> print(fb.tab("Am"))
   A minor
   e|--0--
   B|--1--
   G|--2--
   D|--2--
   A|--0--
   E|--x--

   >>> from pytheory import Scale
   >>> pentatonic = Scale(tonic="A4", system="blues")["minor pentatonic"]
   >>> print(fb.scale_diagram(pentatonic, frets=5))
       0   1   2   3   4   5
   E| E | - | - | G | - | A |
   B| - | C | - | D | - | E |
   G| G | - | A | - | - | C |
   D| D | - | E | - | - | G |
   A| A | - | - | C | - | D |
   E| E | - | - | G | - | A |

Audio Playback
--------------

.. code-block:: pycon

   >>> from pytheory import Tone, Chord, play, save, Synth

   >>> play(Tone.from_string("A4"), t=1_000)

   >>> play(Chord.from_name("Am7"), synth=Synth.TRIANGLE, t=2_000)

   >>> save(Chord.from_name("C"), "c_major.wav", t=2_000)

Command Line
------------

PyTheory also works from the terminal::

   $ pytheory tone A4
   $ pytheory chord C E G
   $ pytheory key G major
   $ pytheory scale C dorian
   $ pytheory fingering Am
   $ pytheory progression C major I V vi IV
   $ pytheory detect C E G A D
   $ pytheory play Am7 --synth triangle

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
- **WAV export** for saving rendered audio to disk
