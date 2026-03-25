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
