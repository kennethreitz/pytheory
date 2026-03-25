Rhythm and Scores
=================

The rhythm module lets you pair tones and chords with durations,
organize them into measures, and export measure-aware MIDI files.

Duration
--------

A ``Duration`` represents a note length in beats (quarter note = 1 beat):

.. code-block:: pycon

   >>> from pytheory import Duration

   >>> Duration.WHOLE.value
   4.0
   >>> Duration.HALF.value
   2.0
   >>> Duration.QUARTER.value
   1.0
   >>> Duration.EIGHTH.value
   0.5
   >>> Duration.SIXTEENTH.value
   0.25
   >>> Duration.DOTTED_HALF.value
   3.0
   >>> Duration.DOTTED_QUARTER.value
   1.5
   >>> Duration.TRIPLET_QUARTER.value    # 2/3 of a beat
   0.6666666666666666

Time Signatures
---------------

A ``TimeSignature`` holds the meter of a piece — how many beats per
measure and which note value gets one beat:

.. code-block:: pycon

   >>> from pytheory.rhythm import TimeSignature

   >>> ts = TimeSignature.from_string("4/4")
   >>> ts.beats_per_measure
   4.0

   >>> TimeSignature.from_string("3/4").beats_per_measure
   3.0

   >>> TimeSignature.from_string("6/8").beats_per_measure
   3.0

   >>> TimeSignature.from_string("12/8").beats_per_measure
   6.0

The ``beats_per_measure`` is always in quarter-note units. In 6/8,
there are 6 eighth notes per bar = 3 quarter-note beats.

Building a Score
----------------

A ``Score`` is a sequence of notes and rests with a time signature and
tempo. Use ``.add()`` and ``.rest()`` for fluent chaining:

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Tone

   >>> score = Score("4/4", bpm=120)
   >>> score.add(Tone.from_string("C4", system="western"), Duration.QUARTER)
   <Score 4/4 120bpm ...>
   >>> score.add(Tone.from_string("E4", system="western"), Duration.QUARTER)
   <Score 4/4 120bpm ...>
   >>> score.add(Tone.from_string("G4", system="western"), Duration.HALF)
   <Score 4/4 120bpm ...>

   >>> score.total_beats
   4.0
   >>> score.measures
   1.0
   >>> score.duration_ms
   2000.0

Rests
~~~~~

Add silence with ``.rest()`` or the ``Rest()`` helper:

.. code-block:: pycon

   >>> score = Score("4/4", bpm=120)
   >>> score.add(Tone.from_string("C4", system="western"), Duration.HALF)
   <Score 4/4 120bpm ...>
   >>> score.rest(Duration.HALF)
   <Score 4/4 120bpm ...>
   >>> score.measures
   1.0

Chords with Rhythm
~~~~~~~~~~~~~~~~~~

Chords work just like tones — pass any ``Chord`` object:

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Key

   >>> key = Key("C", "major")
   >>> chords = key.progression("I", "V", "vi", "IV")

   >>> score = Score("4/4", bpm=120)
   >>> for chord in chords:
   ...     score.add(chord, Duration.WHOLE)

   >>> score.measures
   4.0
   >>> score.duration_ms
   8000.0

Compound Time
~~~~~~~~~~~~~

12/8 is a compound meter — 12 eighth notes per bar grouped in four
groups of three. Each group feels like one "big beat":

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Key

   >>> key = Key("A", "minor")
   >>> chords = key.random_progression(4)

   >>> score = Score("12/8", bpm=120)
   >>> for c in chords:
   ...     # Two dotted halves = one bar of 12/8
   ...     score.add(c, Duration.DOTTED_HALF)
   ...     score.add(c, Duration.DOTTED_HALF)

   >>> score.measures
   4.0

MIDI Export
-----------

``Score.save_midi()`` writes a Standard MIDI File with proper time
signature and tempo meta events:

.. code-block:: pycon

   >>> from pytheory import Score, Duration, Key

   >>> key = Key("G", "major")
   >>> score = Score("4/4", bpm=140)
   >>> for chord in key.progression("I", "IV", "V", "I"):
   ...     score.add(chord, Duration.WHOLE)
   >>> score.save_midi("progression.mid")

The MIDI file can be opened in any DAW (Logic, Ableton, GarageBand,
Reaper, etc.), notation software (MuseScore, Sibelius), or MIDI player.

Drum Patterns
=============

PyTheory includes 48 drum pattern presets spanning genres from rock to
Afro-Cuban to electronic. Each pattern is defined as a set of hits at
specific beat positions, using General MIDI percussion sounds.

Listing Presets
---------------

.. code-block:: pycon

   >>> from pytheory import Pattern
   >>> Pattern.list_presets()
   ['12/8 blues', '6/8 afro-cuban', 'afrobeat', 'baiao', 'bebop', ...]

Loading a Pattern
-----------------

.. code-block:: pycon

   >>> rock = Pattern.preset("rock")
   >>> rock
   <Pattern 'rock' 4/4 4.0 beats 12 hits>

   >>> salsa = Pattern.preset("salsa")
   >>> salsa
   <Pattern 'salsa' 4/4 8.0 beats 29 hits>

   >>> bebop = Pattern.preset("bebop")
   >>> waltz = Pattern.preset("waltz")

Available Genres
~~~~~~~~~~~~~~~~

**Rock/Pop**: rock, half time, double time, disco, motown, train beat

**Jazz**: jazz, bebop, shuffle, linear, paradiddle

**Latin**: salsa, bossa nova, samba, cumbia, merengue, baiao, maracatu

**Afro-Cuban**: son clave 3-2, son clave 2-3, rumba clave 3-2, rumba clave 2-3,
cascara, guaguanco, mozambique, nanigo, bembe, 6/8 afro-cuban, tresillo, habanera

**African**: afrobeat, highlife

**Caribbean**: reggae, dancehall

**Electronic**: house, trap, drum and bass, breakbeat

**Metal/Punk**: metal, blast beat, punk

**Other**: funk, hip hop, bo diddley, second line, new orleans, waltz, 12/8 blues

Exporting to MIDI
-----------------

Convert any pattern to a Score, then export:

.. code-block:: pycon

   >>> pattern = Pattern.preset("bossa nova")
   >>> score = pattern.to_score(repeats=8, bpm=140)
   >>> score.save_midi("bossa.mid")

   >>> Pattern.preset("salsa").to_score(repeats=4, bpm=180).save_midi("salsa.mid")
   >>> Pattern.preset("afrobeat").to_score(repeats=8, bpm=110).save_midi("afrobeat.mid")

Combining Drums with Chords
----------------------------

You can layer a drum pattern with a chord progression by adding chord
notes to the same Score:

.. code-block:: pycon

   >>> from pytheory import Pattern, Key, Duration

   >>> key = Key("A", "minor")
   >>> chords = key.random_progression(4)

   >>> score = Pattern.preset("bossa nova").to_score(repeats=2, bpm=140)
   >>> for chord in chords:
   ...     score.add(chord, Duration.WHOLE)
   ...     score.add(chord, Duration.WHOLE)
   >>> score.save_midi("bossa_with_chords.mid")

Drum Sounds
-----------

The ``DrumSound`` enum maps to General MIDI percussion note numbers:

.. code-block:: pycon

   >>> from pytheory import DrumSound

   >>> DrumSound.KICK.value
   36
   >>> DrumSound.SNARE.value
   38
   >>> DrumSound.CLOSED_HAT.value
   42
   >>> DrumSound.RIDE.value
   51
   >>> DrumSound.CLAVE.value
   75
   >>> DrumSound.CONGA_HIGH.value
   63

Available sounds: KICK, SNARE, RIMSHOT, CLAP, CLOSED_HAT, OPEN_HAT,
PEDAL_HAT, LOW_TOM, MID_TOM, HIGH_TOM, CRASH, RIDE, RIDE_BELL, COWBELL,
CLAVE, SHAKER, TAMBOURINE, CONGA_HIGH, CONGA_LOW, BONGO_HIGH, BONGO_LOW,
TIMBALE_HIGH, TIMBALE_LOW, AGOGO_HIGH, AGOGO_LOW, GUIRO, MARACAS.
