Working with Chords
===================

A `chord <https://en.wikipedia.org/wiki/Chord_(music)>`_ is two or more tones sounding simultaneously. Chords are the
vertical dimension of music — while melody moves horizontally through
time, harmony stacks tones on top of each other.

Chord Construction
------------------

Chords are built by stacking **intervals** above a **root** note. The
most common chord type is the `triad <https://en.wikipedia.org/wiki/Triad_(music)>`_ — three notes built from
alternating scale degrees (root, 3rd, 5th).

The four triad types::

    Major       root + major 3rd (4) + perfect 5th (7)    Bright, stable
    Minor       root + minor 3rd (3) + perfect 5th (7)    Dark, sad
    Diminished  root + minor 3rd (3) + diminished 5th (6) Tense, unstable
    Augmented   root + major 3rd (4) + augmented 5th (8)  Eerie, unresolved

Adding a 7th creates a `seventh chord <https://en.wikipedia.org/wiki/Seventh_chord>`_ — the foundation of jazz
harmony::

    Dominant 7th   root + 4 + 7 + 10   Bluesy, wants to resolve (G7)
    Major 7th      root + 4 + 7 + 11   Dreamy, sophisticated (Cmaj7)
    Minor 7th      root + 3 + 7 + 10   Warm, mellow (Am7)
    Diminished 7th root + 3 + 6 + 9    Dramatic, symmetrical

Inversions
----------

A chord is in **root position** when the root is the lowest note.
When a different chord tone is in the bass, the chord is `inverted <https://en.wikipedia.org/wiki/Inversion_(music)>`_:

- **Root position**: C E G (root in bass)
- **First inversion**: E G C (3rd in bass) — notated C/E
- **Second inversion**: G C E (5th in bass) — notated C/G

Inversions change the color and weight of a chord without changing its
identity. First inversion sounds lighter; second inversion sounds
suspended, often used as a passing chord.

For seventh chords, there's also **third inversion** (7th in bass):

- G7 in third inversion: F G B D (notated G7/F)

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> root   = Chord([Tone.from_string(n, system="western") for n in ["C4", "E4", "G4"]])
   >>> first  = Chord([Tone.from_string(n, system="western") for n in ["E3", "G3", "C4"]])
   >>> second = Chord([Tone.from_string(n, system="western") for n in ["G3", "C4", "E4"]])

   >>> root.identify()
   'C major'
   >>> first.identify()
   'C major'
   >>> second.identify()
   'C major'

Extended Chords
---------------

Beyond seventh chords, jazz harmony builds `extended chords <https://en.wikipedia.org/wiki/Extended_chord>`_ by
continuing to stack thirds:

- **9th chord**: adds the 9th (= 2nd, one octave up)
- **11th chord**: adds the 9th and 11th (= 4th)
- **13th chord**: adds the 9th, 11th, and 13th (= 6th)

A full 13th chord contains all 7 notes of the scale! In practice,
tones are usually omitted — the 5th is typically dropped first, then
the 11th (which clashes with the 3rd in dominant chords).

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> scale = TonedScale(tonic="C4")["major"]

   >>> cmaj9 = scale.chord(0, 2, 4, 6, 8)
   >>> c13 = scale.chord(0, 2, 4, 6, 8, 10, 12)

Using the Chord Chart
---------------------

PyTheory includes 144 pre-built chords (12 roots x 12 qualities):

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> fb.chord("C")
   Fingering(e=0, B=1, G=0, D=2, A=3, E=x)
   >>> fb.chord("Am")
   Fingering(e=0, B=1, G=2, D=2, A=0, E=x)
   >>> fb.chord("G7")
   Fingering(e=1, B=0, G=0, D=0, A=2, E=3)

You can also build chords directly with ``Chord.from_name()``:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_name("G7").identify()
   'G dominant 7th'
   >>> Chord.from_name("Ddim").identify()
   'D diminished'

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

.. code-block:: pycon

   >>> from pytheory import CHARTS
   >>> chart = CHARTS["western"]

   >>> chart["C"].acceptable_tone_names
   ('C', 'E', 'G')

   >>> chart["Cm7"].acceptable_tone_names
   ('C', 'Eb', 'G', 'Bb')

Building Chords
---------------

Several convenience constructors make chord creation concise:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_tones("C", "E", "G").identify()
   'C major'
   >>> Chord.from_tones("A", "C", "E").identify()
   'A minor'

   >>> Chord.from_name("Am7").identify()
   'A minor 7th'
   >>> Chord.from_name("G7").identify()
   'G dominant 7th'

   >>> Chord.from_intervals("C", 4, 7).identify()
   'C major'
   >>> Chord.from_intervals("G", 4, 7, 10).identify()
   'G dominant 7th'

   >>> Chord.from_midi_message(60, 64, 67).identify()
   'C major'

   >>> len(Chord.from_name("C"))
   3
   >>> "C" in Chord.from_name("C")
   True

Intervals
---------

The ``intervals`` property returns semitone distances between adjacent
tones — these are musically meaningful and octave-invariant:

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").intervals
   [4, 3]

   >>> Chord.from_tones("C", "Eb", "G").intervals
   [3, 4]

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

.. code-block:: pycon

   >>> from pytheory import Chord, Tone
   >>> C4 = Tone.from_string("C4", system="western")
   >>> G4 = Tone.from_string("G4", system="western")

   >>> fifth = Chord([C4, G4])
   >>> tritone = Chord([C4, C4 + 6])
   >>> fifth.harmony > tritone.harmony
   True

Dissonance Score
~~~~~~~~~~~~~~~~

The ``dissonance`` property uses the Plomp-Levelt `roughness <https://en.wikipedia.org/wiki/Roughness_(psychoacoustics)>`_ model
(1965). When two frequencies are close together, their sound waves
interfere and produce rapid amplitude fluctuations called `beating <https://en.wikipedia.org/wiki/Beat_(acoustics)>`_.
This beating is perceived as roughness — the physiological basis of
dissonance.

The roughness depends on the frequency difference relative to the
**critical bandwidth** of the human ear (~25% of the frequency at
that register). Maximum roughness occurs when the difference equals
the critical bandwidth.

.. code-block:: pycon

   >>> E4 = Tone.from_string("E4", system="western")
   >>> octave = Chord([C4, C4 + 12])
   >>> third = Chord([C4, E4])
   >>> octave.dissonance < third.dissonance
   True

Beat Frequencies
~~~~~~~~~~~~~~~~

When two tones with slightly different frequencies are played together,
you hear a pulsing at the **beat frequency**: ``|f1 - f2|`` Hz.

- **< 1 Hz**: Slow pulsing, used for tuning instruments
- **1–15 Hz**: Audible rhythmic beating
- **15–30 Hz**: Perceived as buzzing/roughness
- **> 30 Hz**: No longer beating — becomes part of the timbre

.. code-block:: pycon

   >>> A4 = Tone.from_string("A4", system="western")
   >>> chord = Chord([A4, A4 + 7, A4 + 12])

   >>> chord.beat_frequencies
   [...]

   >>> round(chord.beat_pulse, 1)
   219.3

Transposition
-------------

Shift an entire chord up or down by any number of semitones:

.. code-block:: pycon

   >>> Chord.from_name("C").transpose(7).identify()
   'G major'

   >>> Chord.from_name("Am7").transpose(-2).identify()
   'G minor 7th'

Chord Manipulation
------------------

Add or remove individual tones from a chord:

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> c_major = Chord.from_tones("C", "E", "G")

   >>> b4 = Tone.from_string("B4", system="western")
   >>> cmaj7 = c_major.add_tone(b4)
   >>> cmaj7.identify()
   'C major 7th'

   >>> c_again = cmaj7.remove_tone("B")
   >>> c_again.identify()
   'C major'

Chord Identification
--------------------

Give PyTheory any set of tones and it will tell you what chord it is.
It tries every tone as a potential root and matches the interval pattern
against 17 known chord types (triads, 7ths, 9ths, sus, power chords).

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_tones("A", "C", "E").identify()
   'A minor'
   >>> Chord.from_tones("G", "B", "D", "F").identify()
   'G dominant 7th'

   >>> Chord.from_tones("E", "G", "C").identify()
   'C major'

   >>> Chord.from_tones("Bb", "D", "F").identify()
   'Bb major'

You can also access the root and quality separately:

.. code-block:: pycon

   >>> chord = Chord.from_name("Am7")
   >>> chord.root
   <Tone A4>
   >>> chord.quality
   'minor 7th'

Harmonic Analysis
-----------------

`Roman numeral analysis <https://en.wikipedia.org/wiki/Roman_numeral_analysis>`_ labels each chord by its function within a
key. This is how musicians describe chord progressions independent of
key — "I-IV-V" means the same thing in C major (C-F-G) as in G major
(G-C-D).

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> C4 = Tone.from_string("C4", system="western")
   >>> E4 = Tone.from_string("E4", system="western")
   >>> G4 = Tone.from_string("G4", system="western")

   >>> Chord([C4, E4, G4]).analyze("C")
   'I'
   >>> Chord.from_tones("D", "F", "A").analyze("C")
   'ii'
   >>> Chord([G4, G4+4, G4+7]).analyze("C")
   'V'
   >>> Chord([G4, G4+4, G4+7, G4+10]).analyze("C")
   'V7'

Tension and Resolution
----------------------

**Tension** is what makes music move forward. Without it, there's no
desire to resolve — no drama, no narrative. The ``tension`` property
quantifies this based on:

- **Tritones** (6 semitones): the most unstable interval. The tritone
  between the 3rd and 7th of a dominant chord (e.g. B and F in G7)
  creates the strongest pull toward resolution.
- **Minor 2nds**: semitone clashes that add bite and urgency.
- **Dominant function**: the specific combination of a major 3rd and
  minor 7th above the root — the hallmark of the V7 chord.

.. code-block:: pycon

   >>> c_major = Chord([C4, E4, G4])
   >>> c_major.tension['score']
   0.0
   >>> c_major.tension['tritones']
   0

   >>> g7 = Chord([G4, G4+4, G4+7, G4+10])
   >>> g7.tension['score']
   0.6
   >>> g7.tension['tritones']
   1
   >>> g7.tension['has_dominant_function']
   True

Voice Leading
-------------

`Voice leading <https://en.wikipedia.org/wiki/Voice_leading>`_ is the art of connecting chords smoothly. Instead of
jumping all voices to new positions, good voice leading moves each note
the minimum distance to reach the next chord. Bach's chorales are the
gold standard — every voice moves by step whenever possible.

.. code-block:: pycon

   >>> c_maj = Chord.from_tones("C", "E", "G")
   >>> f_maj = Chord.from_tones("F", "A", "C")

   >>> for src, dst, motion in c_maj.voice_leading(f_maj):
   ...     print(f"{src} -> {dst}  ({motion:+d} semitones)")
   G4 -> A4  (+2 semitones)
   E4 -> F4  (+1 semitones)
   C4 -> C4  (+0 semitones)

Tritone Substitution
--------------------

In jazz harmony, any `dominant chord <https://en.wikipedia.org/wiki/Dominant_seventh_chord>`_
can be replaced by the dominant chord a
`tritone <https://en.wikipedia.org/wiki/Tritone_substitution>`_ (6
semitones) away. This works because the two chords share the same
tritone interval — the 3rd and 7th simply swap roles.

Common tritone subs: G7 <-> Db7, C7 <-> F#7, D7 <-> Ab7.

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> g7 = Chord.from_name("G7")
   >>> sub = g7.tritone_sub()
   >>> sub.identify()
   'C# dominant 7th'

The Overtone Series
-------------------

Every musical tone is actually a stack of frequencies — the
**fundamental** plus its `overtones <https://en.wikipedia.org/wiki/Overtone>`_ (harmonics). The overtone series
is nature's chord: it contains the octave, perfect fifth, perfect
fourth, major third, and more, in that order.

This is *why* consonance exists. When you play C and G together, the
overtones of C already contain G. The two tones share acoustic energy,
reinforcing each other. A dissonant interval like C and C# shares
almost no overtones — the waves clash.

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> a4 = Tone.from_string("A4", system="western")
   >>> [round(f, 1) for f in a4.overtones(8)]
   [440.0, 880.0, 1320.0, 1760.0, 2200.0, 2640.0, 3080.0, 3520.0]
