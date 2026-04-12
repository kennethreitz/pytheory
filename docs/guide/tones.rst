Working with Tones
==================

A :class:`~pytheory.tones.Tone` represents a single musical note, optionally
with an octave number in `scientific pitch notation <https://en.wikipedia.org/wiki/Scientific_pitch_notation>`_ (e.g. C4 = middle C).

What is a Tone?
---------------

A musical tone is a sound with a definite pitch — a periodic vibration at
a specific frequency. In the Western 12-tone system, the octave (a 2:1
frequency ratio) is divided into 12 equal steps called **semitones** or
**half steps**. Two semitones make a **whole step** (whole tone).

The 12 chromatic tones are::

    C  C#/Db  D  D#/Eb  E  F  F#/Gb  G  G#/Ab  A  A#/Bb  B

Notes with two names (like C# and Db) are `enharmonic equivalents <https://en.wikipedia.org/wiki/Enharmonic>`_ —
different names for the same pitch. Whether you call it C# or Db depends
on the musical context (key signature, harmonic function).

Scientific Pitch Notation
-------------------------

Each tone can be assigned an octave number. The standard is **scientific
pitch notation**, where the octave number increments at C::

    ... B3  C4  C#4  D4 ... A4  B4  C5  C#5 ...
             ^                        ^
         middle C              one octave up

Key reference points:

- `A4 = 440 Hz <https://en.wikipedia.org/wiki/A440_(pitch_standard)>`_ — the international tuning standard (ISO 16)
- **C4 = 261.63 Hz** — middle C on the piano
- **A0 = 27.5 Hz** — the lowest A on a standard piano
- **C8 = 4186 Hz** — the highest C on a standard piano

Creating Tones
--------------

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> c4 = Tone.from_string("C4")
   >>> cs4 = Tone.from_string("C#4")
   >>> db4 = Tone.from_string("Db4")

   >>> d = Tone(name="D", octave=3)

   >>> a4 = Tone.from_string("A4", system="western")

   >>> Tone.from_frequency(440)
   <Tone A4>
   >>> Tone.from_frequency(261.63)
   <Tone C4>

   >>> Tone.from_midi(60)
   <Tone C4>
   >>> Tone.from_midi(69)
   <Tone A4>

Properties
----------

.. code-block:: pycon

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4.name
   'C'
   >>> c4.octave
   4
   >>> c4.full_name
   'C4'
   >>> c4.letter
   'C'
   >>> c4.midi
   60
   >>> c4.exists
   True

Pitch and Frequency
-------------------

Every tone vibrates at a specific frequency measured in Hertz (Hz —
cycles per second). The relationship between pitch and frequency is
**logarithmic**: each octave doubles the frequency, and each semitone
multiplies by the 12th root of 2 (~1.05946).

.. code-block:: pycon

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.frequency
   440.0

   >>> Tone.from_string("A3", system="western").frequency
   220.0

   >>> Tone.from_string("C4", system="western").frequency
   261.6255653005986

Temperament
~~~~~~~~~~~

**Temperament** is the system used to tune the intervals between notes.
Different temperaments produce slightly different frequencies for the
same note name:

- `Equal temperament <https://en.wikipedia.org/wiki/Equal_temperament>`_ (default): Every semitone has an identical
  frequency ratio of 2^(1/12). This is the modern standard — it allows
  free modulation between all keys but no interval is acoustically
  "pure" except the octave.

- `Pythagorean temperament <https://en.wikipedia.org/wiki/Pythagorean_tuning>`_: Built entirely from pure perfect fifths
  (3:2 ratio). Produces beatless fifths but introduces the "Pythagorean
  comma" — a small discrepancy when 12 fifths don't quite equal 7
  octaves. Used in medieval European music.

- `Quarter-comma meantone <https://en.wikipedia.org/wiki/Quarter-comma_meantone>`_: Tunes major thirds to the pure ratio of
  5:4, distributing the resulting error across the fifths. Dominant in
  Renaissance and Baroque music (15th–18th century). Sounds beautiful
  in closely related keys but "wolf intervals" make distant keys
  unusable.

.. code-block:: pycon

   >>> a4.pitch(temperament="equal")
   440.0
   >>> a4.pitch(temperament="pythagorean")
   440.0

   >>> c5 = Tone.from_string("C5", system="western")
   >>> c5.pitch(temperament="equal")
   523.2511306011972
   >>> c5.pitch(temperament="pythagorean")
   521.4814814814815

Symbolic Pitch
~~~~~~~~~~~~~~

Pass ``symbolic=True`` to get exact pitch ratios as
`SymPy <https://en.wikipedia.org/wiki/SymPy>`_ expressions instead of
floating-point approximations. This is useful for mathematical analysis,
proving tuning relationships, or comparing temperaments with exact
arithmetic.

.. code-block:: pycon

   >>> a4 = Tone.from_string("A4", system="western")

   >>> a4.pitch(symbolic=True)
   440
   >>> Tone.from_string("C5", system="western").pitch(symbolic=True)
   440*2**(1/4)

   >>> Tone.from_string("G4", system="western").pitch(
   ...     temperament="pythagorean", symbolic=True)
   391.111111111111

   >>> e4 = Tone.from_string("E4", system="western")
   >>> e4.pitch(temperament="equal", symbolic=True)
   220.0*2**(7/12)
   >>> e4.pitch(temperament="pythagorean", symbolic=True)
   330.000000000000
   >>> e4.pitch(temperament="meantone", symbolic=True)
   220.0*5**(1/4)

   >>> e4.pitch(symbolic=True).evalf(50)
   329.62755691286992973584176104655507518647334182098

The symbolic output reveals *why* temperaments differ: equal temperament
uses irrational numbers (roots of 2), Pythagorean uses powers of 3/2
(rational but accumulating error), and meantone tunes thirds to the
pure 5/4 ratio (sacrificing fifths).

Intervals and Arithmetic
-------------------------

An **interval** is the distance between two pitches, measured in
semitones. Intervals have both a **quantity** (number of scale steps)
and a **quality** (perfect, major, minor, augmented, diminished).

Common intervals::

    Semitones   Name              Sound
    ─────────   ────              ─────
    0           Unison            Same note
    1           Minor 2nd         Tense, dissonant (Jaws theme)
    2           Major 2nd         A whole step (Do-Re)
    3           Minor 3rd         Sad, dark (Greensleeves)
    4           Major 3rd         Happy, bright (Kumbaya)
    5           Perfect 4th       Open, hollow (Here Comes the Bride)
    6           Tritone           Unstable, tense (The Simpsons)
    7           Perfect 5th       Strong, stable (Star Wars)
    8           Minor 6th         Bittersweet
    9           Major 6th         Warm (My Bonnie)
    10          Minor 7th         Bluesy (Star Trek TOS)
    11          Major 7th         Dreamy, yearning
    12          Octave            Same note, higher

Tones support ``+`` and ``-`` operators for semitone math:

.. code-block:: pycon

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4 + 4
   <Tone E4>
   >>> c4 + 7
   <Tone G4>
   >>> c4 + 12
   <Tone C5>

Subtracting two tones gives the semitone distance:

.. code-block:: pycon

   >>> g4 = Tone.from_string("G4", system="western")
   >>> g4 - c4
   7

   >>> c5 = Tone.from_string("C5", system="western")
   >>> c5 - c4
   12

Naming Intervals
~~~~~~~~~~~~~~~~

The ``interval_to`` method gives the musical name of the interval
between two tones, including compound intervals that span more than
one octave:

.. code-block:: pycon

   >>> c4.interval_to(g4)
   'perfect 5th'
   >>> c4.interval_to(c4 + 4)
   'major 3rd'
   >>> c4.interval_to(c5)
   'octave'

   >>> c4.interval_to(c4 + 19)
   'perfect 5th + 1 octave'

Transposition
~~~~~~~~~~~~~

The ``transpose`` method returns a new tone shifted by a number of
semitones — equivalent to the ``+`` operator but reads more clearly
in some contexts:

.. code-block:: pycon

   >>> c4.transpose(7)
   <Tone G4>
   >>> c4.transpose(-2)
   <Tone A#3>

MIDI
~~~~

Every tone maps to a `MIDI note number <https://en.wikipedia.org/wiki/MIDI>`_
(0–127), the standard for communicating with synthesizers, DAWs, and
digital instruments:

.. code-block:: pycon

   >>> c4.midi
   60
   >>> Tone.from_string("A4", system="western").midi
   69

   >>> Tone.from_midi(60).midi
   60

Comparison and Sorting
----------------------

Tones can be compared and sorted by pitch frequency:

.. code-block:: pycon

   >>> c4 < g4
   True
   >>> sorted([g4, c4, e4])
   [<Tone C4>, <Tone E4>, <Tone G4>]

Equality checks note name and octave:

.. code-block:: pycon

   >>> c4 == "C"
   True
   >>> c4 == Tone(name="C", octave=4)
   True

The Overtone Series
-------------------

Every tone you hear is actually a composite of many frequencies. When
a string vibrates, it doesn't just vibrate as a whole — it also vibrates
in halves, thirds, quarters, and so on, producing the `harmonic series <https://en.wikipedia.org/wiki/Harmonic_series_(music)>`_:

.. code-block:: pycon

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.overtones(8)
   [440.0, 880.0, 1320.0, 1760.0, 2200.0, 2640.0, 3080.0, 3520.0]

These harmonics correspond to musical intervals::

    Harmonic  Frequency  Interval from fundamental
    1st       440 Hz     Unison (A4)
    2nd       880 Hz     Octave (A5)
    3rd       1320 Hz    Octave + perfect 5th (E6)
    4th       1760 Hz    Two octaves (A6)
    5th       2200 Hz    Two octaves + major 3rd (C#7)
    6th       2640 Hz    Two octaves + perfect 5th (E7)
    7th       3080 Hz    Two octaves + minor 7th (≈G7, slightly flat)
    8th       3520 Hz    Three octaves (A7)

The overtone series is why a perfect fifth sounds consonant — the 3rd
harmonic of the lower note matches the 2nd harmonic of the upper note.
It's also why the major triad (root, major 3rd, perfect 5th) feels
"natural" — these intervals appear in the first 6 harmonics.

Different instruments emphasize different harmonics, which is why a
violin and a flute playing the same note sound different. This quality
is called `timbre <https://en.wikipedia.org/wiki/Timbre>`_.

Enharmonic Equivalents
----------------------

In equal temperament, C# and Db are the same pitch (they have the
same frequency). They're called **enharmonic equivalents**. Which name
you use depends on context:

- In the key of **D major** (2 sharps), you write **C#**
- In the key of **Gb major** (6 flats), you write **Db**

The rule: each letter name should appear exactly once in a scale. The
D major scale is D E F# G A B C# — not D E Gb G A B Db, even though
F#=Gb and C#=Db.

PyTheory uses sharps by default (following the tone list ordering), but
every tone knows its enharmonic spelling:

.. code-block:: pycon

   >>> Tone.from_string("C#4", system="western").enharmonic
   'Db'

   >>> Tone.from_string("A#4", system="western").enharmonic
   'Bb'

   >>> Tone.from_string("C4", system="western").enharmonic is None
   True

Accidental Properties
~~~~~~~~~~~~~~~~~~~~~

Check whether a tone is natural, sharp, or flat:

.. code-block:: pycon

   >>> c = Tone.from_string("C4", system="western")
   >>> c.is_natural
   True
   >>> c.is_sharp
   False

   >>> cs = Tone.from_string("C#4", system="western")
   >>> cs.is_sharp
   True
   >>> cs.is_natural
   False

   >>> bb = Tone.from_string("Bb4", system="western")
   >>> bb.is_flat
   True

Useful for filtering — for example, finding all natural notes in a
scale, or counting accidentals in a melody.

Extended Enharmonics
~~~~~~~~~~~~~~~~~~~~

PyTheory supports the full range of enharmonic spellings used in real
music theory:

- **Cb** and **Fb** — musically valid flats (Cb = B, Fb = E)
- **E#** and **B#** — musically valid sharps (E# = F, B# = C)
- **Double sharps** (``##`` or ``x``) — e.g. F## = G
- **Double flats** (``bb``) — e.g. Dbb = C
- **Unicode symbols** — ``♯`` (sharp), ``♭`` (flat), ``𝄪`` (double sharp),
  ``𝄫`` (double flat) are all recognized and normalized to ASCII

.. code-block:: pycon

   >>> Tone.from_string("Cb4")   # resolves to B3 (octave boundary fix)
   <Tone B3>
   >>> Tone.from_string("B#4")   # resolves to C5 (octave boundary fix)
   <Tone C5>
   >>> Tone.from_string("E#4")   # resolves to F4
   <Tone F4>
   >>> Tone.from_string("Fb4")   # resolves to E4
   <Tone E4>

The octave boundary is correctly handled: B# crosses up to the next
octave (B#4 = C5), and Cb crosses down (Cb4 = B3), matching standard
scientific pitch notation where the octave number increments at C.

Tone Validation
~~~~~~~~~~~~~~~

Tones are validated on construction — if a tone name is not recognized
in its system, a ``ValueError`` is raised:

.. code-block:: pycon

   >>> Tone.from_string("X4")   # not a valid tone name
   ValueError: ...

The Circle of Fifths
--------------------

The `circle of fifths <https://en.wikipedia.org/wiki/Circle_of_fifths>`_ is the most important diagram in Western music
theory. Starting from any note and ascending by perfect fifths (7
semitones), you pass through all 12 chromatic tones before returning
to the starting note:

.. code-block:: pycon

   >>> c4 = Tone.from_string("C4", system="western")

   >>> [t.name for t in c4.circle_of_fifths()]
   ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

   >>> [t.name for t in c4.circle_of_fourths()]
   ['C', 'F', 'A#', 'D#', 'G#', 'C#', 'F#', 'B', 'E', 'A', 'D', 'G']

Each step clockwise adds one sharp to the key signature; each step
counter-clockwise (ascending by fourths = 5 semitones) adds one flat.

Solfege
-------

The fixed-Do `solfege <https://en.wikipedia.org/wiki/Solf%C3%A8ge>`_ system
maps each note to a singable syllable. PyTheory uses fixed Do (C is always Do):

.. code-block:: pycon

   >>> Tone.from_string("C4").solfege
   'Do'
   >>> Tone.from_string("D4").solfege
   'Re'
   >>> Tone.from_string("F#4").solfege
   'Fi'
   >>> Tone.from_string("Bb4").solfege
   'Te'

Helmholtz Notation
------------------

The older `Helmholtz notation <https://en.wikipedia.org/wiki/Helmholtz_pitch_notation>`_
uses case and tick marks instead of numbers:

.. code-block:: pycon

   >>> Tone.from_string("C3").helmholtz    # Great octave
   'C'
   >>> Tone.from_string("C4").helmholtz    # Middle C
   'c'
   >>> Tone.from_string("C5").helmholtz    # One-line octave
   "c'"
   >>> Tone.from_string("C2").helmholtz    # Contra octave
   'CC'

Cents
-----

A **cent** is 1/100th of a semitone — the standard unit for measuring
fine pitch differences. Use ``cents_difference`` to compare tones or
temperaments:

.. code-block:: pycon

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4.cents_difference(c4 + 1)    # One semitone = 100 cents
   100.0
   >>> c4.cents_difference(c4 + 7)    # Perfect fifth
   700.0

Tones are the atoms of music -- everything else is built from them. Get comfortable here, and chords, scales, and harmony all start to make intuitive sense.
