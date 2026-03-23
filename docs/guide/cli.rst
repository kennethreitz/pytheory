Command-Line Interface
======================

PyTheory includes a CLI for quick music theory lookups from the terminal.

Tone Lookup
-----------

Look up any note's frequency, MIDI number, enharmonic spelling, and
overtones::

    $ pytheory tone A4
      Note:        A4
      Frequency:   440.00 Hz (equal temperament)
      MIDI:        69
      Overtones:   440.0, 880.0, 1320.0, 1760.0, 2200.0, 2640.0

Compare temperaments with ``--temperament``::

    $ pytheory tone C5 --temperament pythagorean
      Note:        C5
      Frequency:   521.48 Hz (pythagorean temperament)
      Equal temp:  523.25 Hz (diff: -5.9 cents)

Scale Display
-------------

Show any scale in any system::

    $ pytheory scale C major
      C major: C D E F G A B C
      Intervals:  C4 -2- D4 -2- E4 -1- F4 -2- G4 -2- A4 -2- B4 -1- C5

    $ pytheory scale C dorian
    $ pytheory scale Sa bhairav --system indian

Chord Identification
--------------------

Identify a chord from its notes::

    $ pytheory chord C E G
      Chord:     C major
      Tones:     C4 E4 G4
      Intervals: [4, 3]
      Harmony:   0.5833
      Dissonance: 0.0712
      Tension:   0.00 (tritones=0)

    $ pytheory chord G B D F
      Chord:     G dominant 7th

Key Explorer
------------

Get a complete breakdown of any key — signature, diatonic triads,
seventh chords, relative and parallel keys::

    $ pytheory key G major
      Key: G major
      Signature: 1 sharps, 0 flats (F#)
      Scale: G A B C D E F#
      Triads:
        I       G major
        ii      A minor
        iii     B minor
        IV      C major
        V       D major
        vi      E minor
        vii°    F# diminished
      7th chords:
        G major 7th
        A minor 7th
        ...
      Relative: <Key E minor>
      Parallel: <Key G minor>

Guitar Fingerings
-----------------

Get tablature for any of the 144 built-in chords::

    $ pytheory fingering Am
    Am
    E|--0--
    B|--1--
    G|--2--
    D|--2--
    A|--0--
    E|--0--

Use ``--capo`` to see fingerings with a capo::

    $ pytheory fingering G --capo 2

Chord Progressions
------------------

Build progressions from Roman numerals::

    $ pytheory progression G major I V vi IV
      Key: G major
      Progression: I → V → vi → IV

        I       G major
        V       D major
        vi      E minor
        IV      C major

Key Detection
-------------

Detect the most likely key from a set of notes::

    $ pytheory detect C E G A D
      Detected key: C major
      Scale: C D E F G A B C

Audio Playback
--------------

Play individual notes or chords (requires PortAudio)::

    $ pytheory play A4                         # Single note
    $ pytheory play C E G                      # Notes as chord
    $ pytheory play Am7                        # Chord by name
    $ pytheory play C E G --synth saw          # Sawtooth wave
    $ pytheory play A4 --duration 2000         # 2 seconds
    $ pytheory play C E G --temperament meantone
