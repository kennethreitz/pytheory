Working with Chords
===================

A **chord** is two or more tones sounding simultaneously. Chords are the
vertical dimension of music — while melody moves horizontally through
time, harmony stacks tones on top of each other.

Chord Construction
------------------

Chords are built by stacking **intervals** above a **root** note. The
most common chord type is the **triad** — three notes built from
alternating scale degrees (root, 3rd, 5th).

The four triad types::

    Major       root + major 3rd (4) + perfect 5th (7)    Bright, stable
    Minor       root + minor 3rd (3) + perfect 5th (7)    Dark, sad
    Diminished  root + minor 3rd (3) + diminished 5th (6) Tense, unstable
    Augmented   root + major 3rd (4) + augmented 5th (8)  Eerie, unresolved

Adding a 7th creates a **seventh chord** — the foundation of jazz
harmony::

    Dominant 7th   root + 4 + 7 + 10   Bluesy, wants to resolve (G7)
    Major 7th      root + 4 + 7 + 11   Dreamy, sophisticated (Cmaj7)
    Minor 7th      root + 3 + 7 + 10   Warm, mellow (Am7)
    Diminished 7th root + 3 + 6 + 9    Dramatic, symmetrical

Using the Chord Chart
---------------------

PyTheory includes 144 pre-built chords (12 roots x 12 qualities):

.. code-block:: python

   from pytheory import CHARTS

   chart = CHARTS["western"]

   c_major = chart["C"]     # C major (root position)
   a_minor = chart["Am"]    # A minor
   g_seven = chart["G7"]    # G dominant 7th
   d_dim   = chart["Ddim"]  # D diminished

Available qualities:

============  ================  ================================
Quality       Intervals         Example tones (from C)
============  ================  ================================
``""``        4, 7              C E G (major triad)
``"maj"``     4, 7              C E G (explicit major)
``"m"``       3, 7              C Eb G (minor triad)
``"5"``       7                 C G (power chord)
``"7"``       4, 7, 10          C E G Bb (dominant 7th)
``"9"``       4, 7, 10, 14      C E G Bb D (dominant 9th)
``"dim"``     3, 6              C Eb Gb (diminished)
``"m6"``      3, 7, 9           C Eb G A (minor 6th)
``"m7"``      3, 7, 10          C Eb G Bb (minor 7th)
``"m9"``      3, 7, 10, 14      C Eb G Bb D (minor 9th)
``"maj7"``    4, 7, 11          C E G B (major 7th)
``"maj9"``    4, 7, 11, 14      C E G B D (major 9th)
============  ================  ================================

.. code-block:: python

   >>> chart["C"].acceptable_tone_names
   ('C', 'E', 'G')

   >>> chart["Cm7"].acceptable_tone_names
   ('C', 'D#', 'G', 'A#')    # Eb and Bb shown as sharps

Building Chords Manually
-------------------------

.. code-block:: python

   from pytheory import Tone, Chord

   c_major = Chord(tones=[
       Tone.from_string("C4", system="western"),
       Tone.from_string("E4", system="western"),
       Tone.from_string("G4", system="western"),
   ])

   for tone in c_major:
       print(tone)

   len(c_major)       # 3
   "C" in c_major     # True

Intervals
---------

The ``intervals`` property returns semitone distances between adjacent
tones — these are musically meaningful and octave-invariant:

.. code-block:: python

   >>> c_major.intervals
   [4, 3]    # major 3rd (4) + minor 3rd (3) = major triad

   >>> Chord(tones=[C4, Eb4, G4]).intervals
   [3, 4]    # minor 3rd + major 3rd = minor triad

Consonance and Dissonance
-------------------------

**Consonance** is the perception of stability and "pleasantness" when
tones sound together. **Dissonance** is the perception of tension and
roughness. Neither is inherently good or bad — music needs both.

Harmony Score
~~~~~~~~~~~~~

The ``harmony`` property measures consonance using **frequency ratio
simplicity**. The insight dates back to Pythagoras (6th century BC):
intervals whose frequencies form simple integer ratios sound consonant.

===========  =====  ====================
Interval     Ratio  Why it sounds "good"
===========  =====  ====================
Octave       2:1    Every 2nd wave aligns
Perfect 5th  3:2    Every 3rd wave aligns
Perfect 4th  4:3    Every 4th wave aligns
Major 3rd    5:4    Every 5th wave aligns
Minor 3rd    6:5    Every 6th wave aligns
Tritone      45:32  Waves rarely align
===========  =====  ====================

.. code-block:: python

   fifth = Chord([C4, G4])
   tritone = Chord([C4, F_sharp_4])

   fifth.harmony > tritone.harmony     # True
   # The perfect fifth's 3:2 ratio scores higher

Dissonance Score
~~~~~~~~~~~~~~~~

The ``dissonance`` property uses the **Plomp-Levelt roughness model**
(1965). When two frequencies are close together, their sound waves
interfere and produce rapid amplitude fluctuations called **beating**.
This beating is perceived as roughness — the physiological basis of
dissonance.

The roughness depends on the frequency difference relative to the
**critical bandwidth** of the human ear (~25% of the frequency at
that register). Maximum roughness occurs when the difference equals
the critical bandwidth.

.. code-block:: python

   # Octave: frequencies far apart → low roughness
   octave = Chord([C4, C5])
   # Major 3rd: closer frequencies → higher roughness
   third = Chord([C4, E4])

   octave.dissonance < third.dissonance  # True

Beat Frequencies
~~~~~~~~~~~~~~~~

When two tones with slightly different frequencies are played together,
you hear a pulsing at the **beat frequency**: ``|f1 - f2|`` Hz.

- **< 1 Hz**: Slow pulsing, used for tuning instruments
- **1–15 Hz**: Audible rhythmic beating
- **15–30 Hz**: Perceived as buzzing/roughness
- **> 30 Hz**: No longer beating — becomes part of the timbre

.. code-block:: python

   chord = Chord(tones=[A4, E5, A5])

   # All pairwise beat frequencies, sorted ascending
   chord.beat_frequencies
   # [(A4, E5, 189.6), (E5, A5, 220.0), (A4, A5, 440.0)]

   # The slowest (most perceptible) beat
   chord.beat_pulse  # 189.6 Hz
