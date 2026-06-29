Command-Line Interface
======================

Sometimes you don't want to open Python — you're mid-practice and just
need to know what's in a B7 chord, or which key has those three sharps.
The ``pytheory`` command answers theory questions, plays notes, and
exports MIDI straight from your shell prompt — no session required.

JSON and audio output
---------------------

The theory commands (``tone``, ``scale``, ``chord``, ``key``,
``progression``, ``analyze``, ``reharmonize``, ``identify``, ``detect``,
``modes``, ``circle``, ``fingering``) all take two extra flags:

- ``--json`` prints a structured result instead of the pretty table —
  handy for piping into ``jq`` or another tool.
- ``--play`` plays the result as audio (the note, chord, scale, or
  progression).

::

    $ pytheory scale C dorian --json
    {
      "tonic": "C",
      "mode": "dorian",
      "notes": [
        "C",
        "D",
        "Eb",
        "F",
        "G",
        "A",
        "Bb",
        "C"
      ]
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
         Bb major | 108 bpm
         Bb → Gm → Cm → F
         jazz | triangle lead | fm pad | plate reverb

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
      Frequency:   528.60 Hz (pythagorean temperament)
      Equal temp:  523.25 Hz (diff: +17.6 cents)
      MIDI:        72
      Overtones:   523.3, 1046.5, 1569.8, 2093.0, 2616.3, 3139.5

Scale Display
-------------

Show any scale in any system::

    $ pytheory scale C major
      C major: C D E F G A B C
      Intervals:  C4 -2- D4 -2- E4 -1- F4 -2- G4 -2- A4 -2- B4 -1- C5

    $ pytheory scale C dorian
    $ pytheory scale Sa bhairav --system indian

Ragas
-----

Hindustani and Carnatic ragas, with their ascending and descending lines,
the signature ``pakad`` phrase, and the just-intonation *shruti* tuning a
fixed-pitch instrument can only approximate. The theory lives in
:doc:`systems` — here you just ask::

    $ pytheory raga yaman
      Raga Yaman  (aka Kalyan)
      thaat kalyan · shadav-sampurna · evening · serene, romantic
      vadi G  samvadi N
      aroha  : N. R G M D N S'
      avaroha: S' N D P M G R S
      pakad  : N. R G, R, P M G R S
      scale (Sa=C): C D E F# G A B

Set the tonic with ``--sa``, and add ``--shruti`` to see each swara's just
ratio and how far it lands from equal temperament::

    $ pytheory raga yaman --shruti
      ...
      shruti intonation (just vs 12-TET):
        S     1/1  C     261.63 Hz    +0.0¢
        R     9/8  D     294.33 Hz    +3.9¢
        G     5/4  E     327.03 Hz   -13.7¢
        M   45/32  F#    367.91 Hz    -9.8¢
        P     3/2  G     392.44 Hz    +2.0¢
        D     5/3  A     436.04 Hz   -15.6¢
        N    15/8  B     490.55 Hz   -11.7¢

Bare ``pytheory raga`` (or ``--list``) lists all 54 ragas; narrow it with
``--thaat``, ``--time``, or ``--tradition hindustani|carnatic``::

    $ pytheory raga --tradition carnatic
      18 ragas:

        Abhogi               Kharaharapriya (22)          any           pleasing, tender
        Bilahari             Dheerashankarabharanam (29)  any           joyful, festive
        Charukesi            Charukesi (26)               any           bittersweet
        ...

Add ``--play`` to hear the aroha and avaroha — just intonation by default,
``--equal`` for 12-TET, ``--reverb`` to set the wet mix.

Maqamat
-------

Arabic maqamat use true quarter tones — the half-flats (marked ``↓``) that
a piano simply doesn't have. ``maqam`` shows the ajnas, the *seyir* melodic
path, and the nearest 12-TET spelling; :doc:`systems` covers the theory::

    $ pytheory maqam rast
      Maqam Rast
      family Rast · dignified, sober, the 'mother' maqam
      ajnas: Jins Rast on Do + Jins Rast on Sol
      seyir: ascending from the tonic; rests on Sol and the neutral 3rd
      scale: Do Re Mi↓ Fa Sol La Si↓
      ≈ 12-TET (tonic=C): C D E F G A Bb

``--tuning`` prints each degree's just ratio against equal temperament —
watch Rast's neutral third sit 45.5 cents below E::

    $ pytheory maqam rast --tuning
      ...
      quarter-tone intonation (just vs 12-TET):
        Do      1/1  ~C     261.63 Hz    +0.0¢
        Re      9/8  ~D     294.33 Hz    +3.9¢
        Mi↓   27/22  ~E     321.09 Hz   -45.5¢
        Fa      4/3  ~F     348.83 Hz    -2.0¢
        Sol     3/2  ~G     392.44 Hz    +2.0¢
        La      5/3  ~A     436.04 Hz   -15.6¢
        Si↓    11/6  ~Bb    479.65 Hz   +49.4¢

Bare ``pytheory maqam`` (or ``--list``) lists all ten; ``--family`` filters
them, ``--tonic`` sets the root, and ``--play`` (with ``--reverb``) plays
the maqam ascending and descending::

    $ pytheory maqam --list
      10 maqamat:

        Ajam         Ajam       Do Re Mi Fa Sol La Si              bright, celebratory
        Bayati       Bayati     Do Re↓ Mib Fa Sol Lab Sib          tender, intimate, the everyday maqam
        Hijaz        Hijaz      Do Reb Mi Fa Sol Lab Sib           yearning, devotional, desert-evening
        ...

Chord Identification
--------------------

Identify a chord from its notes::

    $ pytheory chord C E G
      Chord:     C major
      Tones:     C4 E4 G4
      Intervals: [4, 3]
      Harmony:   0.2381
      Dissonance: 2.7786
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
      Scale: G A B C D E F# G
      Triads:
        I       G major
        ii      A minor
        iii     B minor
        IV      C major
        V       D major
        vi      E minor
        viidim  F# diminished
      7th chords:
        G major 7th
        A minor 7th
        B minor 7th
        C major 7th
        D dominant 7th
        E minor 7th
        F# half-diminished 7th
      Relative: E minor
      Parallel: G minor

Guitar Fingerings
-----------------

Get tablature for any of the 144 built-in chords (high string at the top,
standard tab orientation; ``x`` for a muted string)::

    $ pytheory fingering Am
    Am
    e|--0--
    B|--1--
    G|--2--
    D|--2--
    A|--0--
    E|--x--

Use ``--capo`` to see fingerings with a capo::

    $ pytheory fingering G --capo 2

The CLI looks chords up in the built-in chart. To voice *any* parseable
symbol — and to export SVG/PNG chord boxes or scale shapes — reach for the
:class:`~pytheory.chords.Fretboard` API in :doc:`fretboard`.

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

Hand it a ``.mid`` (or ``.midi``) file instead of chord symbols and it
reads the harmony straight off the notes — detected key, tempo, time
signature, and a beat-by-beat chord timeline. ``--key``/``--mode`` and
``--json`` work here too::

    $ pytheory analyze song.mid
      File: song.mid
      Key: C major  (detected)
      Tempo: 120 BPM    Time: 4/4
      4 chord change(s)

        beat 0.00    I        C major
        beat 1.00    V        G major
        beat 2.00    vi       A minor
        beat 3.00    IV       F major

Reharmonize a Chord
-------------------

Ask for substitution ideas — tritone subs, diatonic swaps, the secondary
dominant, and the negative-harmony mirror (aliased ``reharm``)::

    $ pytheory reharmonize G7 --key C
      Reharmonizing G dominant 7th in C major:

        tritone substitution   C# dominant 7th
          The dominant a tritone away — same tritone, chromatic bass descent.
        diatonic substitution  D minor
          Shares 2 notes — a smooth diatonic swap.
        ...

Add ``--play`` to hear the original followed by each option.

Give it **several** chords and it reharmonizes the whole progression with a
chosen ``--technique`` (``secondary_dominants``, ``tritone``, or
``diatonic``)::

    $ pytheory reharmonize C Am Dm G7 C --key C
      Reharmonizing in C major (secondary_dominants):

        original:      C → Am → Dm → G7 → C
        reharmonized:  C → E7 → Am → A7 → Dm → D7 → G7 → C

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
      Harmony:    0.4930
      Dissonance: 5.3347
      Tension:    score=0.15 tritones=0 minor_2nds=1 dominant=False

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
        I-vi-IV-V             C → Am → F → G
        I-IV-vi-V             C → F → Am → G
        vi-IV-I-V             Am → F → C → G
        ...

The full list runs to dozens of forms — pop turnarounds, jazz ``ii-V-I``
families, and 8-, 12-, and minor-blues structures among them.

Metronome & Tempo Trainer
-------------------------

A practice metronome that lives in your terminal. Give it a tempo and a bar
length with ``--beats``; ``--subdivide`` adds eighths (``2``), triplets
(``3``), or sixteenths (``4``), and ``--no-accent`` flattens the downbeat.
The command is aliased ``metro``::

    $ pytheory metronome 90 --chords C major I V vi IV
      Metronome: 90.0 BPM  (4/4)
      Cycling: C | G | Am | F
      Press Ctrl-C to stop.

      bar   1      90 BPM  C
      bar   2      90 BPM  G
      ...

``--chords`` cycles a chord under the click so you can drill changes —
either literal symbols (``Am F C G``) or a key plus Roman numerals
(``C major I V vi IV``, as above).

To build speed, point ``--to`` at a target tempo and it ramps there,
nudging up ``--step`` BPM every ``--every`` beats — then holds the target
unless you pass ``--no-hold``::

    $ pytheory metronome 80 --to 120
      Tempo trainer: 80.0 → 120.0 BPM, +5 every 8 beats  (4/4)
      Press Ctrl-C to stop.

      bar   1      80 BPM

Performance & Audio Tools
-------------------------

Four more commands open whole apps rather than answering a lookup.
Each has its own guide::

    $ pytheory tune --instrument guitar    # real-time terminal tuner
    $ pytheory tune --serve                # browser strobe tuner + JS pitch stream
    $ pytheory studio                      # browser: recording → sheet music
    $ pytheory transcribe hum.m4a hum.mid  # recording → notes/MIDI
    $ pytheory live --link                 # MIDI synth rig in the terminal

The tuner, studio, and transcriber are covered in :doc:`listening`;
the live rig in :doc:`live`.

The CLI is there for quick lookups when you don't want to open a Python session -- just ask your question and get back to playing.
