Cookbook
=======

Real-world recipes for common musical tasks. Each recipe is self-contained
and ready to paste into a Python session.

Analyze a Song
--------------

Take the chord progression from "Let It Be" (C G Am F) and analyze it
in the key of C major:

.. code-block:: pycon

   >>> from pytheory import Chord, Key

   >>> C  = Chord.from_name("C")
   >>> G  = Chord.from_name("G")
   >>> Am = Chord.from_name("Am")
   >>> F  = Chord.from_name("F")

   >>> [c.identify() for c in [C, G, Am, F]]
   ['C major', 'G major', 'A minor', 'F major']

   >>> [c.analyze("C") for c in [C, G, Am, F]]
   ['I', 'V', 'vi', 'IV']

   >>> key = Key("C", "major")
   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['C major', 'G major', 'A minor', 'F major']

Write a 12-Bar Blues
--------------------

The `12-bar blues <https://en.wikipedia.org/wiki/Twelve-bar_blues>`_ is
built from the I, IV, and V chords. Here it is in the key of A:

.. code-block:: pycon

   >>> from pytheory import Key, Chord

   >>> key = Key("A", "major")
   >>> [c.identify() for c in key.progression("I", "IV", "V")]
   ['A major', 'D major', 'E major']

   >>> bars = ["I","I","I","I", "IV","IV","I","I", "V","IV","I","V"]
   >>> [c.identify() for c in key.progression(*bars)]
   ['A major', 'A major', 'A major', 'A major', 'D major', 'D major', 'A major', 'A major', 'E major', 'D major', 'A major', 'E major']

   >>> Chord.from_name("A7").identify()
   'A dominant 7th'
   >>> Chord.from_name("D7").identify()
   'D dominant 7th'
   >>> Chord.from_name("E7").identify()
   'E dominant 7th'

Find Chords in a Key
--------------------

The :class:`~pytheory.scales.Key` class builds diatonic chords for any
key and lets you pull progressions by Roman numeral or Nashville number:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> key = Key("G", "major")
   >>> key.chords
   ['G major', 'A minor', 'B minor', 'C major', 'D major', 'E minor', 'F# diminished']

   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['G major', 'D major', 'E minor', 'C major']

   >>> [c.identify() for c in key.nashville(1, 5, 6, 4)]
   ['G major', 'D major', 'E minor', 'C major']

Compare Scales
--------------

Play the same tonic through different scales to hear how each mode
reshapes the palette. The western modes share the same notes but start
on different degrees; the blues scale adds the "blue note" (flat 5th):

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4")
   >>> c["major"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
   >>> c["minor"].note_names
   ['C', 'D', 'D#', 'F', 'G', 'G#', 'A#', 'C']
   >>> c["dorian"].note_names
   ['C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'C']
   >>> c["mixolydian"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'A#', 'C']

   >>> c_blues = TonedScale(tonic="C4", system="blues")
   >>> c_blues["blues"].note_names
   ['C', 'D#', 'F', 'F#', 'G', 'A#', 'C']

Guitar Chord Chart
------------------

Generate fingerings for guitar and ukulele with
:class:`~pytheory.tones.Fretboard`:

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> fb.chord("C")
   Fingering(e=0, B=1, G=0, D=2, A=3, E=x)
   >>> fb.chord("G")
   Fingering(e=3, B=0, G=0, D=0, A=2, E=3)
   >>> fb.chord("Am")
   Fingering(e=0, B=1, G=2, D=2, A=0, E=x)
   >>> fb.chord("D")
   Fingering(e=2, B=3, G=2, D=0, A=x, E=x)

   >>> uke = Fretboard.ukulele()
   >>> uke.chord("C")
   Fingering(A=3, E=0, C=0, G=0)
   >>> uke.chord("G")
   Fingering(A=2, E=3, C=2, G=0)

Explore an Interval
-------------------

Start from A4 (440 Hz) and walk through intervals, checking names and
frequency ratios:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.frequency
   440.0

   >>> minor_3rd = a4 + 3
   >>> a4.interval_to(minor_3rd)
   'minor 3rd'

   >>> p5 = a4 + 7
   >>> a4.interval_to(p5)
   'perfect 5th'
   >>> round(p5.frequency / a4.frequency, 4)
   1.4983

   >>> octave = a4 + 12
   >>> a4.interval_to(octave)
   'octave'
   >>> round(octave.frequency / a4.frequency, 4)
   2.0
