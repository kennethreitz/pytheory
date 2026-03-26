Music Theory Fundamentals
=========================

This page covers the essential concepts of music theory — the framework
behind everything PyTheory does. Don't worry if you're new to this:
music theory isn't a set of rules you have to memorize, it's a
vocabulary for describing what you already hear. Every concept below
connects to something you've felt while listening to music — this page
just gives it a name.

Sound and Pitch
---------------

All sound is vibration. When an object vibrates, it pushes air molecules
back and forth, creating pressure waves that travel to your ears. The
speed of this vibration — measured in cycles per second
(`Hertz <https://en.wikipedia.org/wiki/Hertz>`_, Hz) — determines the
`pitch <https://en.wikipedia.org/wiki/Pitch_(music)>`_ you hear.

- **20 Hz**: the lowest pitch most humans can hear
- **60–250 Hz**: the range of the human voice (speaking)
- **261.63 Hz**: `middle C <https://en.wikipedia.org/wiki/C_(musical_note)#Middle_C>`_ (C4)
- **440 Hz**: the `concert pitch <https://en.wikipedia.org/wiki/Concert_pitch>`_ tuning standard A (A4)
- **4186 Hz**: the highest C on a piano (C8)
- **20,000 Hz**: the upper limit of `human hearing <https://en.wikipedia.org/wiki/Hearing_range>`_

The relationship between pitch and frequency is **logarithmic** — each
`octave <https://en.wikipedia.org/wiki/Octave>`_ doubles the frequency.
This means the distance from A3 (220 Hz) to A4 (440 Hz) is 220 Hz, but
the distance from A4 to A5 (880 Hz) is 440 Hz. Both sound like "one
octave" to our ears.

Why Twelve Notes?
-----------------

The Western `chromatic scale <https://en.wikipedia.org/wiki/Chromatic_scale>`_
has 12 notes per octave. This isn't arbitrary — it emerges from the
physics of vibrating strings and air columns.

The `harmonic series <https://en.wikipedia.org/wiki/Harmonic_series_(music)>`_
is the sequence of frequencies produced when a string vibrates: f, 2f,
3f, 4f, 5f... The relationships between these harmonics create the
intervals we perceive as `consonant <https://en.wikipedia.org/wiki/Consonance_and_dissonance>`_:

- 2:1 = `octave <https://en.wikipedia.org/wiki/Octave>`_ (the most fundamental)
- 3:2 = `perfect fifth <https://en.wikipedia.org/wiki/Perfect_fifth>`_
- 4:3 = `perfect fourth <https://en.wikipedia.org/wiki/Perfect_fourth>`_
- 5:4 = `major third <https://en.wikipedia.org/wiki/Major_third>`_
- 6:5 = `minor third <https://en.wikipedia.org/wiki/Minor_third>`_

If you stack perfect fifths (multiply by 3/2 repeatedly) and reduce to
within one octave, you get 12 roughly evenly-spaced notes before the
cycle almost closes. The tiny gap where it doesn't close perfectly is
the `Pythagorean comma <https://en.wikipedia.org/wiki/Pythagorean_comma>`_
— the reason we need `temperament <https://en.wikipedia.org/wiki/Musical_temperament>`_.

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> c = Tone.from_string("C4", system="western")
   >>> [t.name for t in c.circle_of_fifths()]
   ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

Other cultures divide the octave differently: Indonesian
`gamelan <https://en.wikipedia.org/wiki/Gamelan>`_ uses 5 or 7 unequal
divisions; Indian classical music theoretically has 22
`shrutis <https://en.wikipedia.org/wiki/Shruti_(music)>`_ (microtones);
Arabic `maqam <https://en.wikipedia.org/wiki/Maqam>`_ uses
`quarter-tones <https://en.wikipedia.org/wiki/Quarter_tone>`_.

Intervals: The Atoms of Music
------------------------------

An `interval <https://en.wikipedia.org/wiki/Interval_(music)>`_ is the
distance between two pitches. Intervals are the building blocks of
everything — melodies are sequences of intervals, chords are stacks
of intervals, and scales are patterns of intervals.

Every interval has two properties:

**Size** (how many scale steps)::

    Unison → 2nd → 3rd → 4th → 5th → 6th → 7th → Octave

**Quality** (exact number of semitones)::

    Perfect:     unison (0), 4th (5), 5th (7), octave (12)
    Major:       2nd (2), 3rd (4), 6th (9), 7th (11)
    Minor:       2nd (1), 3rd (3), 6th (8), 7th (10)
    Augmented:   one semitone larger than perfect or major
    Diminished:  one semitone smaller than perfect or minor

The "`perfect <https://en.wikipedia.org/wiki/Perfect_fifth>`_" intervals
(unison, 4th, 5th, octave) are called perfect because they appear in
both major AND minor scales unchanged. They've been considered consonant
across virtually all musical cultures throughout history.

The `tritone <https://en.wikipedia.org/wiki/Tritone>`_ (augmented 4th /
diminished 5th = 6 semitones) divides the octave exactly in half.
Medieval theorists called it *diabolus in musica* ("the devil in music")
because of its extreme instability. Today it's the foundation of
`dominant harmony <https://en.wikipedia.org/wiki/Dominant_(music)>`_
and the `blues <https://en.wikipedia.org/wiki/Blue_note>`_.

Keys and Key Signatures
-----------------------

A `key <https://en.wikipedia.org/wiki/Key_(music)>`_ is a group of
notes that form the tonal center of a piece. The key of C major uses
only the white keys on the piano: C D E F G A B. The key of G major
uses the same notes except F becomes F#.

`Key signatures <https://en.wikipedia.org/wiki/Key_signature>`_ tell
you which notes are sharped or flatted throughout a piece. They follow
the `circle of fifths <https://en.wikipedia.org/wiki/Circle_of_fifths>`_:

**Sharp keys** (add one sharp per step clockwise)::

    C major:  no sharps or flats
    G major:  F#
    D major:  F# C#
    A major:  F# C# G#
    E major:  F# C# G# D#
    B major:  F# C# G# D# A#

**Flat keys** (add one flat per step counter-clockwise)::

    C major:  no sharps or flats
    F major:  Bb
    Bb major: Bb Eb
    Eb major: Bb Eb Ab
    Ab major: Bb Eb Ab Db
    Db major: Bb Eb Ab Db Gb

The order of sharps is always F C G D A E B (Father Charles Goes Down
And Ends Battle). The order of flats is the reverse: B E A D G C F.

Harmony: How Chords Work
-------------------------

`Harmony <https://en.wikipedia.org/wiki/Harmony>`_ is the art of
combining tones simultaneously. While
`melody <https://en.wikipedia.org/wiki/Melody>`_ is horizontal (tones
in sequence), harmony is vertical (tones stacked).

The simplest harmony is the `triad <https://en.wikipedia.org/wiki/Triad_(music)>`_
— three notes built by stacking `thirds <https://en.wikipedia.org/wiki/Third_(music)>`_.
The quality of each third determines the chord type:

- **Major triad** = major 3rd + minor 3rd (e.g. C-E-G)
- **Minor triad** = minor 3rd + major 3rd (e.g. C-Eb-G)
- `Diminished triad <https://en.wikipedia.org/wiki/Diminished_triad>`_ = minor 3rd + minor 3rd (e.g. B-D-F)
- `Augmented triad <https://en.wikipedia.org/wiki/Augmented_triad>`_ = major 3rd + major 3rd (e.g. C-E-G#)

In any major key, the triads built on each
`scale degree <https://en.wikipedia.org/wiki/Degree_(music)>`_ always
follow the same pattern::

    Degree   Quality        Function
    I        Major          Tonic (home)
    ii       Minor          Pre-dominant
    iii      Minor          Tonic substitute
    IV       Major          Subdominant (departure)
    V        Major          Dominant (tension, wants to go home)
    vi       Minor          Tonic substitute, relative minor
    vii°     Diminished     Dominant substitute (leading tone chord)

This pattern is the DNA of Western harmony. Pop songs, classical
sonatas, jazz standards, and church hymns all derive from it.

Functional Harmony
~~~~~~~~~~~~~~~~~~

Chords don't just have names — they have
`functions <https://en.wikipedia.org/wiki/Function_(music)>`_:

- **Tonic function** (I, iii, vi): stability, rest, home
- **Subdominant function** (ii, IV): motion away from home
- **Dominant function** (V, vii°): tension, desire to return home

The most fundamental progression in Western music is **T → S → D → T**
(tonic → subdominant → dominant → tonic). The classic
`I-IV-V-I <https://en.wikipedia.org/wiki/I%E2%80%93IV%E2%80%93V%E2%80%93I>`_
is exactly this pattern. Every "Louie Louie" and every
`Bach chorale <https://en.wikipedia.org/wiki/Bach_chorale>`_ follows
this basic tonal gravity.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> scale = TonedScale(tonic="C4")["major"]

   >>> scale.triad(0).identify()
   'C major'
   >>> scale.triad(3).identify()
   'F major'
   >>> scale.triad(4).identify()
   'G major'

The Dominant Seventh
~~~~~~~~~~~~~~~~~~~~

The most important chord in `tonal music <https://en.wikipedia.org/wiki/Tonality>`_
is the `dominant seventh <https://en.wikipedia.org/wiki/Dominant_seventh_chord>`_
— the V7 chord. In C major, this is G-B-D-F. It contains:

- A `leading tone <https://en.wikipedia.org/wiki/Leading-tone>`_ (B) that pulls up to the tonic (C) by half step
- A `tritone <https://en.wikipedia.org/wiki/Tritone>`_ (B-F) that wants to resolve inward (B→C, F→E)
- The `dominant note <https://en.wikipedia.org/wiki/Dominant_(music)>`_ (G) that falls to the tonic by a fifth

This combination creates the strongest possible pull toward
`resolution <https://en.wikipedia.org/wiki/Resolution_(music)>`_.
When you hear V7→I, you feel arrival.

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> C4 = Tone.from_string("C4", system="western")
   >>> G4 = Tone.from_string("G4", system="western")

   >>> g7 = Chord([G4, G4+4, G4+7, G4+10])
   >>> g7.identify()
   'G dominant 7th'
   >>> g7.tension['has_dominant_function']
   True
   >>> g7.tension['tritones']
   1

   >>> c_major = Chord([C4, C4+4, C4+7])
   >>> c_major.tension['score']
   0.0

Rhythm and Meter
----------------

While PyTheory focuses on pitch,
`rhythm <https://en.wikipedia.org/wiki/Rhythm>`_ is the other half
of music.

**Rhythm** is the pattern of durations.
`Meter <https://en.wikipedia.org/wiki/Metre_(music)>`_ is the recurring
pattern of strong and weak beats that organizes rhythm.

- `4/4 time <https://en.wikipedia.org/wiki/Time_signature#Simple_time_signatures>`_: the most common meter. Strong-weak-medium-weak.
  Used in rock, pop, hip-hop, most Western music.
- `3/4 time <https://en.wikipedia.org/wiki/Triple_metre>`_: waltz time. Strong-weak-weak. A lilting, circular feel.
- `6/8 time <https://en.wikipedia.org/wiki/Compound_meter_(music)>`_: compound duple. Two groups of three. Irish jigs, many
  ballads.
- `12/8 time <https://en.wikipedia.org/wiki/Compound_meter_(music)>`_: compound quadruple. Four groups of three. Slow blues,
  doo-wop, gospel. Has a triplet feel over a 4/4 pulse — the shuffle
  groove of "Stormy Monday" and "Oh! Darling."
- 5/4 time: asymmetric. "`Take Five <https://en.wikipedia.org/wiki/Take_Five>`_"
  by Dave Brubeck. Creates constant forward momentum because it never
  fully settles.
- `7/8 time <https://en.wikipedia.org/wiki/Additive_rhythm_and_divisive_rhythm>`_: common in Balkan folk music. Often felt as 2+2+3 or
  3+2+2.

The Physics of Consonance
-------------------------

Why do some intervals sound "good" and others "bad"? The answer lies
in the physics of sound waves and the
`Plomp-Levelt <https://en.wikipedia.org/wiki/Consonance_and_dissonance#Physiological_basis>`_
model of sensory dissonance.

When two frequencies are related by a simple ratio (like 3:2 for a
perfect fifth), their waveforms align regularly. The combined wave
is smooth and periodic — the brain perceives this as consonant.

When two frequencies are related by a complex ratio (like 45:32 for
a tritone), their waveforms rarely align. The combined wave is
irregular and the brain perceives
`roughness <https://en.wikipedia.org/wiki/Roughness_(psychoacoustics)>`_
— dissonance.

But `consonance and dissonance <https://en.wikipedia.org/wiki/Consonance_and_dissonance>`_
are also cultural. The
`major third <https://en.wikipedia.org/wiki/Major_third>`_ (5:4) was
considered dissonant in medieval European music but consonant since the
Renaissance. The tritone was forbidden in church music but is the
foundation of blues and jazz. Indonesian gamelan embraces
`beating <https://en.wikipedia.org/wiki/Beat_(acoustics)>`_ between
paired instruments as a core aesthetic.

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> C4 = Tone.from_string("C4", system="western")
   >>> E4 = Tone.from_string("E4", system="western")
   >>> G4 = Tone.from_string("G4", system="western")

   >>> [round(f, 2) for f in C4.overtones(6)]
   [261.63, 523.25, 784.88, 1046.5, 1308.13, 1569.75]

   >>> fifth = Chord([C4, G4])
   >>> tritone = Chord([C4, C4 + 6])
   >>> fifth.harmony > tritone.harmony
   True

   >>> octave = Chord([C4, C4 + 12])
   >>> third = Chord([C4, E4])
   >>> octave.dissonance < third.dissonance
   True

   >>> c_major = Chord([C4, E4, G4])
   >>> c_major.tension['score']
   0.0

   >>> g7 = Chord([G4, G4+4, G4+7, G4+10])
   >>> g7.tension['score']
   0.6
   >>> g7.tension['tritones']
   1
   >>> g7.tension['has_dominant_function']
   True

From Theory to Composition
--------------------------

Everything on this page — tones, intervals, chords, scales, keys — is
the foundation. But PyTheory goes further: you can use these building
blocks to compose and play actual music. See the :doc:`sequencing`
guide to learn how to arrange multi-part scores with melodies, chord
pads, bass lines, drum patterns, and audio effects — all driven by the
theory concepts you've just learned.

Further Reading
---------------

- `Music theory <https://en.wikipedia.org/wiki/Music_theory>`_ — Wikipedia overview
- `Equal temperament <https://en.wikipedia.org/wiki/Equal_temperament>`_ — the modern tuning system
- `Circle of fifths <https://en.wikipedia.org/wiki/Circle_of_fifths>`_ — key relationships
- `Chord progression <https://en.wikipedia.org/wiki/Chord_progression>`_ — common patterns
- `Voice leading <https://en.wikipedia.org/wiki/Voice_leading>`_ — smooth chord connections
- `Raga <https://en.wikipedia.org/wiki/Raga>`_ — Indian melodic framework
- `Maqam <https://en.wikipedia.org/wiki/Maqam>`_ — Arabic melodic system
- `Gamelan <https://en.wikipedia.org/wiki/Gamelan>`_ — Indonesian ensemble music
- `Blues <https://en.wikipedia.org/wiki/Blues>`_ — the foundation of American popular music
- `Twelve-bar blues <https://en.wikipedia.org/wiki/Twelve-bar_blues>`_ — the most common blues form
