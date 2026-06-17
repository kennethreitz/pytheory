Command-Line Interface
======================

Sometimes you don't want to open Python — you're mid-practice and just
need to know what's in a B7 chord, or which key has those three sharps.
The ``pytheory`` command answers theory questions, plays notes, and
exports MIDI straight from your shell prompt — no session required.

JSON and audio output
---------------------

The theory commands (``tone``, ``scale``, ``chord``, ``key``,
``progression``, ``identify``, ``analyze``, ``detect``, ``modes``,
``circle``, ``fingering``) all take two extra flags:

- ``--json`` prints a structured result instead of the pretty table —
  handy for piping into ``jq`` or another tool.
- ``--play`` plays the result as audio (the note, chord, scale, or
  progression).

::

    $ pytheory scale C dorian --json
    {
      "tonic": "C",
      "mode": "dorian",
      "notes": ["C", "D", "Eb", "F", "G", "A", "Bb", "C"]
    }

    $ pytheory progression C major I V vi IV --play     # hear the chords

Interactive REPL
----------------

For extended exploration, the REPL is a music theory scratchpad with
tab completion. See the :doc:`repl` guide for details::

    $ pytheory repl

Demo
----

The fastest way to hear what PyTheory can do. Generates and plays a
random multi-part track — different every time::

    $ pytheory demo
      ♫  Jazz Club
         Bb major | 105 bpm
         Bb → Gm → Cm → F
         jazz drums | saw lead | fm pad

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

Analyze a Progression
---------------------

Go the other way — hand it the chords and it works out the harmony. The key
is auto-detected (or pass ``--key``/``--mode``), applied dominants are
labelled, and cadences are flagged::

    $ pytheory analyze C D7 G7 C
      Key: C major  (detected)

        C        I        C major
        D7       V7/V     D dominant 7th  (secondary dominant)
        G7       V7       G dominant 7th
        C        I        C major

      Cadences:
        D7 → G7: half
        G7 → C: imperfect authentic

Use ``--key`` and ``--mode`` to analyze in a specific key::

    $ pytheory analyze --key A --mode minor Am Dm E Am

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
    $ pytheory play Am7 --envelope pad         # With ADSR envelope
    $ pytheory play C4 --envelope bell         # Bell-like ring

Chord Identification (from symbol)
-----------------------------------

Parse any chord symbol and get a full analysis::

    $ pytheory identify Cmaj7
      Chord:      C major 7th
      Symbol:     Cmaj7
      Tones:      C4 E4 G4 B4
      Intervals:  [4, 3, 4]
      Harmony:    0.5833
      Dissonance: 1.2345
      Tension:    score=0.00 tritones=0 minor_2nds=0 dominant=False

    $ pytheory identify F#m7b5

MIDI Export
-----------

Export a chord progression to a Standard MIDI File::

    $ pytheory midi C major I V vi IV -o pop.mid
      Key:        C major
      Progression: I V vi IV
      BPM:        120
      Duration:   500 ms
      Output:     pop.mid

    $ pytheory midi G major ii V I -o jazz.mid --bpm 140 --duration 800

Modes
-----

Show all 7 modes starting from a note::

    $ pytheory modes C
      Modes of C:

        ionian        C D E F G A B C
        dorian        C D Eb F G A Bb C
        phrygian      C Db Eb F G Ab Bb C
        lydian        C D E F# G A B C
        mixolydian    C D E F G A Bb C
        aeolian       C D Eb F G Ab Bb C
        locrian       C Db Eb F Gb Ab Bb C

Circle of Fifths
----------------

Display the circle of fifths and fourths from any note::

    $ pytheory circle C
      Circle of fifths from C:
        → C → G → D → A → E → B → F# → C# → G# → D# → A# → F

      Circle of fourths from C:
        → C → F → A# → D# → G# → C# → F# → B → E → A → D → G

Common Progressions
-------------------

Show all named progressions realized in a key::

    $ pytheory progressions C major
      Common progressions in C major:

        I-IV-V-I              C → F → G → C
        I-V-vi-IV             C → G → Am → F
        12-bar blues          C → C → C → C → F → F → C → C → G → F → C → G
        ii-V-I                Dm → G7 → C
        ...

Performance & Audio Tools
-------------------------

Four more commands open whole apps rather than answering a lookup.
Each has its own guide::

    $ pytheory tune --instrument guitar    # real-time strobe tuner
    $ pytheory studio                      # browser: recording → sheet music
    $ pytheory transcribe hum.m4a hum.mid  # recording → notes/MIDI
    $ pytheory live --link                 # MIDI synth rig in the terminal

The tuner, studio, and transcriber are covered in :doc:`listening`;
the live rig in :doc:`live`.

The CLI is there for quick lookups when you don't want to open a Python session -- just ask your question and get back to playing.
