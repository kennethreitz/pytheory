Sequencing
==========

The sequencing system lets you compose multi-part arrangements with
durations, time signatures, and instrument voices. This is where
PyTheory goes from theory tool to composition tool.

At the center of everything is the ``Score``. Think of it as your
arrangement, your song, your sketch pad. It holds the tempo, the time
signature, the drum pattern, and every instrument part you create. If
you've ever used a DAW, the Score is your session file. If you haven't,
it's the sheet of paper where the whole piece lives. Everything you
compose -- melodies, chord progressions, bass lines, arpeggios -- gets
added to a Score before you can hear it, export it, or do anything
useful with it.

Duration
--------

In music, all rhythm boils down to one convention: the quarter note
equals one beat. Everything else is relative to that. A whole note is
four beats. An eighth note is half a beat. This is how musicians have
communicated timing for centuries, and it's how PyTheory works too.
Once you internalize "quarter note = 1 beat," durations become
intuitive arithmetic.

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
   >>> Duration.TRIPLET_QUARTER.value
   0.6666666666666666

Time Signatures
---------------

If you're not a musician, time signatures can seem mysterious. They're
not. The top number tells you how many beats are in a bar. The bottom
number tells you which note value gets one beat. That's it.

In practice, you only need to know a handful:

- **4/4** -- four beats per bar. This is the default. Almost all pop,
  rock, hip hop, electronic, and R&B music is in 4/4. If you're not
  sure, use this.
- **3/4** -- three beats per bar. The waltz feel. Think "Blue Danube"
  or Radiohead's "Everything in Its Right Place."
- **6/8** -- six eighth notes per bar, grouped in two sets of three.
  Each group feels like one big swaying beat. Folk music, slow jams,
  ballads.
- **12/8** -- twelve eighth notes per bar, grouped in four sets of
  three. The slow blues shuffle, the gospel feel, "At Last" by Etta
  James. Each "big beat" has a triplet swing baked into it.

A ``TimeSignature`` holds the meter of a piece -- how many beats per
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
there are 6 eighth notes per bar = 3 quarter-note beats. In 12/8,
12 eighth notes = 6 quarter-note beats, grouped in four dotted-quarter
pulses.

Score Basics
------------

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

Add silence with ``.rest()``:

.. code-block:: pycon

   >>> score = Score("4/4", bpm=120)
   >>> score.add(Tone.from_string("C4", system="western"), Duration.HALF)
   <Score 4/4 120bpm ...>
   >>> score.rest(Duration.HALF)
   <Score 4/4 120bpm ...>
   >>> score.measures
   1.0

Chords
~~~~~~

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
   ...     score.add(c, Duration.DOTTED_HALF)
   ...     score.add(c, Duration.DOTTED_HALF)

   >>> score.measures
   4.0

Parts
-----

Parts are like tracks in a DAW. Each one has its own instrument sound
(synth waveform + envelope), its own volume level, and its own effects
chain. When you call ``play_score()``, all the parts get mixed together
into a single audio stream -- just like hitting play in Logic or
Ableton. You might have a pad part holding down chords, a lead part
playing a melody, and a bass part holding down the low end. Each one
is independent: different synth, different envelope, different effects.

The ``Part`` class lets you layer multiple instrument voices -- each with
its own synth waveform, ADSR envelope, and volume level. Create parts
with ``Score.part()``:

.. code-block:: pycon

   >>> from pytheory import Score, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)

   >>> chords = score.part("chords", synth="sine", envelope="pad", volume=0.35)
   >>> lead   = score.part("lead",   synth="saw",  envelope="pluck", volume=0.5)
   >>> bass   = score.part("bass",   synth="triangle", envelope="pluck", volume=0.45)

Adding Notes to Parts
~~~~~~~~~~~~~~~~~~~~~

Parts accept note strings directly — no need to wrap in
``Tone.from_string()``. ``.add()`` and ``.rest()`` return self for
fluent chaining:

.. code-block:: pycon

   >>> lead.add("E5", Duration.QUARTER).add("D5", Duration.EIGHTH).rest(Duration.EIGHTH)
   <Part 'lead' ...>

Raw float beats work too — useful for swing and tuplets:

.. code-block:: pycon

   >>> lead.add("C5", 0.67).add("B4", 0.33).add("A4", 1.0)
   <Part 'lead' ...>

Chords and Tone objects work the same way:

.. code-block:: pycon

   >>> for chord in Key("A", "minor").progression("i", "iv", "V", "i"):
   ...     chords.add(chord, Duration.WHOLE)

   >>> for note in ["A2", "C3", "E3", "A2", "D2", "F2", "A2", "D2"]:
   ...     bass.add(note, Duration.QUARTER)

Arpeggiator
------------

An arpeggiator takes a chord and plays its notes one at a time, in a
pattern, automatically. You hold down a chord and it ripples through
the notes -- up, down, up-and-down, random. It's one of the most
iconic sounds in electronic music. The bubbly bass lines of acid house,
the cascading runs of 80s synth pop (think "Jump" or "Take On Me"),
the hypnotic patterns of trance -- all arpeggiators. It turns a simple
three-note chord into a rhythmic, melodic engine.

``Part.arpeggio()`` takes a chord and sequences through its notes
automatically -- like a hardware arpeggiator on a synth:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", legato=True, glide=0.03,
   ...                   distortion=0.8, lowpass=1000, lowpass_q=5.0)
   >>> lead.arpeggio(Chord.from_symbol("Cm"), bars=2, pattern="up",
   ...              division=Duration.SIXTEENTH, octaves=2)

Parameters:

- ``chord``: A Chord object or string like ``"Am"``.
- ``bars``: Number of bars to fill (default 1).
- ``pattern``: ``"up"``, ``"down"``, ``"updown"``, ``"downup"``, ``"random"``.
- ``division``: Step length (default ``Duration.SIXTEENTH``).
- ``octaves``: Octave span (default 1). With 2, the pattern repeats one octave up.

Chain arpeggios through a progression:

.. code-block:: pycon

   >>> for sym in ["Cm", "Fm", "Abm", "Gm"]:
   ...     lead.arpeggio(sym, bars=2, pattern="updown", octaves=2)

Combined with legato, glide, distortion, and a resonant lowpass, this
produces the classic acid/trance arpeggiator sound.

Legato and Glide
----------------

Normally, every note you play has its own life cycle -- the sound
attacks, sustains, and releases before the next note begins. You hear
each note as a separate event. Legato changes that. The Italian word
means "tied together," and that's exactly what it does: the envelope
flows continuously from one note to the next with no retriggering. The
pitch changes, but the sound never dies and restarts.

Glide (also called portamento) takes this further. Instead of the pitch
jumping instantly from one note to the next, it *slides* -- a smooth,
continuous pitch sweep. This is THE sound of the Roland TB-303, the
little silver box that accidentally invented acid house. A saw wave
with legato, glide, a resonant lowpass filter, and some distortion --
that's the entire genre right there.

By default, each note gets its own attack/release envelope. ``legato=True``
renders the entire part as one continuous waveform -- the pitch changes
at note boundaries but the envelope flows unbroken. Add ``glide`` for
portamento (pitch slides between notes):

.. code-block:: pycon

   >>> acid = score.part("acid", synth="saw", envelope="pad",
   ...                   legato=True, glide=0.04)
   >>> acid.add("C2", 0.25).add("C3", 0.25).add("G2", 0.25).add("C2", 0.25)

- ``legato``: If True, no envelope retrigger between notes (default False).
- ``glide``: Portamento time in seconds (default 0, instant).
  0.03--0.05 = quick 303 slide, 0.1--0.2 = slow glide.

Complete Example
----------------

A full multi-part arrangement built from scratch — bossa nova with FM
rhodes, triangle lead, and filtered bass:

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)
   >>> score.drums("bossa nova", repeats=4)

   >>> # FM rhodes with reverb
   >>> rhodes = score.part("rhodes", synth="fm", envelope="piano",
   ...                     volume=0.3, reverb=0.4, reverb_decay=1.8)

   >>> # Triangle lead with delay
   >>> lead = score.part("lead", synth="triangle", envelope="pluck",
   ...                   volume=0.45, delay=0.25, delay_time=0.32,
   ...                   delay_feedback=0.35, reverb=0.2)

   >>> # Filtered bass
   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   volume=0.45, lowpass=600)

   >>> for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
   ...     rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)

   >>> for n, d in [("E5",.67),("D5",.33),("C5",.67),("B4",.33),
   ...              ("A4",1),("C5",.67),("E5",.33),("D5",.67),("C5",.33),
   ...              ("A4",1)]:
   ...     lead.add(n, d)

   >>> for n in ["A2","E2","A2","C3","D2","A2","D2","F2"]:
   ...     bass.add(n, Duration.QUARTER)

   >>> play_score(score)
