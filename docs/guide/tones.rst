Working with Tones
==================

A :class:`~pytheory.tones.Tone` represents a single musical note, optionally
with an octave number in scientific pitch notation (e.g. C4 = middle C).

What is a Tone?
---------------

A musical tone is a sound with a definite pitch — a periodic vibration at
a specific frequency. In the Western 12-tone system, the octave (a 2:1
frequency ratio) is divided into 12 equal steps called **semitones** or
**half steps**. Two semitones make a **whole step** (whole tone).

The 12 chromatic tones are::

    C  C#/Db  D  D#/Eb  E  F  F#/Gb  G  G#/Ab  A  A#/Bb  B

Notes with two names (like C# and Db) are **enharmonic equivalents** —
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

- **A4 = 440 Hz** — the international tuning standard (ISO 16)
- **C4 = 261.63 Hz** — middle C on the piano
- **A0 = 27.5 Hz** — the lowest A on a standard piano
- **C8 = 4186 Hz** — the highest C on a standard piano

Creating Tones
--------------

.. code-block:: python

   from pytheory import Tone

   # From a string (most common)
   c4 = Tone.from_string("C4")
   cs4 = Tone.from_string("C#4")

   # Direct construction
   d = Tone(name="D", octave=3)

   # With a specific system
   a4 = Tone.from_string("A4", system="western")

Properties
----------

.. code-block:: python

   >>> c4 = Tone.from_string("C4")
   >>> c4.name
   'C'
   >>> c4.octave
   4
   >>> c4.full_name
   'C4'
   >>> str(c4)
   'C4'

Pitch and Frequency
-------------------

Every tone vibrates at a specific frequency measured in Hertz (Hz —
cycles per second). The relationship between pitch and frequency is
**logarithmic**: each octave doubles the frequency, and each semitone
multiplies by the 12th root of 2 (~1.05946).

.. code-block:: python

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.frequency
   440.0

   >>> Tone.from_string("A3", system="western").frequency
   220.0    # One octave down = half the frequency

   >>> Tone.from_string("C4", system="western").frequency
   261.63   # Middle C

Temperament
~~~~~~~~~~~

**Temperament** is the system used to tune the intervals between notes.
Different temperaments produce slightly different frequencies for the
same note name:

- **Equal temperament** (default): Every semitone has an identical
  frequency ratio of 2^(1/12). This is the modern standard — it allows
  free modulation between all keys but no interval is acoustically
  "pure" except the octave.

- **Pythagorean temperament**: Built entirely from pure perfect fifths
  (3:2 ratio). Produces beatless fifths but introduces the "Pythagorean
  comma" — a small discrepancy when 12 fifths don't quite equal 7
  octaves. Used in medieval European music.

- **Quarter-comma meantone**: Tunes major thirds to the pure ratio of
  5:4, distributing the resulting error across the fifths. Dominant in
  Renaissance and Baroque music (15th–18th century). Sounds beautiful
  in closely related keys but "wolf intervals" make distant keys
  unusable.

.. code-block:: python

   >>> a4.pitch(temperament="equal")
   440.0
   >>> a4.pitch(temperament="pythagorean")
   440.0    # A4 is always 440 (it's the reference)

   >>> c5 = Tone.from_string("C5", system="western")
   >>> c5.pitch(temperament="equal")
   523.25
   >>> c5.pitch(temperament="pythagorean")
   521.48   # Slightly different!

   # Symbolic output (SymPy expression)
   >>> a4.pitch(symbolic=True)
   440

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

.. code-block:: python

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4 + 4        # Major third up
   <Tone E4>
   >>> c4 + 7        # Perfect fifth up
   <Tone G4>
   >>> c4 + 12       # Octave up
   <Tone C5>

Subtracting two tones gives the semitone distance:

.. code-block:: python

   >>> g4 = Tone.from_string("G4", system="western")
   >>> g4 - c4       # Perfect fifth = 7 semitones
   7

   >>> c5 = Tone.from_string("C5", system="western")
   >>> c5 - c4       # Octave = 12 semitones
   12

Comparison and Sorting
----------------------

Tones can be compared and sorted by pitch frequency:

.. code-block:: python

   >>> c4 < g4
   True
   >>> sorted([g4, c4, e4])
   [<Tone C4>, <Tone E4>, <Tone G4>]

Equality checks note name and octave:

.. code-block:: python

   >>> c4 == "C"      # Compare with string (name only)
   True
   >>> c4 == Tone(name="C", octave=4)
   True

The Circle of Fifths
--------------------

The **circle of fifths** is the most important diagram in Western music
theory. Starting from any note and ascending by perfect fifths (7
semitones), you pass through all 12 chromatic tones before returning
to the starting note:

.. code-block:: python

   >>> t = Tone.from_string("C4", system="western")
   >>> for i in range(12):
   ...     print(t.name, end=" ")
   ...     t = t + 7
   C G D A E B F# C# G# D# A# F

Each step clockwise adds one sharp to the key signature; each step
counter-clockwise (ascending by fourths = 5 semitones) adds one flat.
