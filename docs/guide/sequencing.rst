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

Duration supports arithmetic — multiply, divide, and add to create
compound durations:

.. code-block:: pycon

   >>> Duration.WHOLE * 2
   8.0
   >>> Duration.HALF + Duration.QUARTER
   3.0
   >>> Duration.WHOLE / 2
   2.0

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

.. code-block:: python

   from pytheory import Score, Duration, Tone

   score = Score("4/4", bpm=120)
   score.add(Tone.from_string("C4", system="western"), Duration.QUARTER)
   score.add(Tone.from_string("E4", system="western"), Duration.QUARTER)
   score.add(Tone.from_string("G4", system="western"), Duration.HALF)

.. code-block:: pycon

   >>> score.total_beats
   4.0
   >>> score.measures
   1.0
   >>> score.duration_ms
   2000.0

Rests
~~~~~

Add silence with ``.rest()``:

.. code-block:: python

   score = Score("4/4", bpm=120)
   score.add(Tone.from_string("C4", system="western"), Duration.HALF)
   score.rest(Duration.HALF)

.. code-block:: pycon

   >>> score.measures
   1.0

Chords
~~~~~~

Chords work just like tones — pass any ``Chord`` object:

.. code-block:: python

   from pytheory import Score, Duration, Key

   key = Key("C", "major")
   chords = key.progression("I", "V", "vi", "IV")

   score = Score("4/4", bpm=120)
   for chord in chords:
       score.add(chord, Duration.WHOLE)

.. code-block:: pycon

   >>> score.measures
   4.0
   >>> score.duration_ms
   8000.0

Compound Time
~~~~~~~~~~~~~

12/8 is a compound meter — 12 eighth notes per bar grouped in four
groups of three. Each group feels like one "big beat":

.. code-block:: python

   from pytheory import Score, Duration, Key

   key = Key("A", "minor")
   chords = key.random_progression(4)

   score = Score("12/8", bpm=120)
   for c in chords:
       score.add(c, Duration.DOTTED_HALF)
       score.add(c, Duration.DOTTED_HALF)

.. code-block:: pycon

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

.. code-block:: python

   from pytheory import Score, Key, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=140)

   chords = score.part("chords", synth="sine", envelope="pad", volume=0.35)
   lead = score.part("lead", synth="saw", envelope="pluck", volume=0.5)
   bass = score.part("bass", synth="triangle", envelope="pluck", volume=0.45)

Adding Notes to Parts
~~~~~~~~~~~~~~~~~~~~~

Parts accept note strings directly — no need to wrap in
``Tone.from_string()``. ``.add()`` and ``.rest()`` return self for
fluent chaining:

.. code-block:: python

   lead.add("E5", Duration.QUARTER).add("D5", Duration.EIGHTH).rest(Duration.EIGHTH)

Raw float beats work too — useful for swing and tuplets:

.. code-block:: python

   lead.add("C5", 0.67).add("B4", 0.33).add("A4", 1.0)

Chords and Tone objects work the same way:

.. code-block:: python

   for chord in Key("A", "minor").progression("i", "iv", "V", "i"):
       chords.add(chord, Duration.WHOLE)

   for note in ["A2", "C3", "E3", "A2", "D2", "F2", "A2", "D2"]:
       bass.add(note, Duration.QUARTER)

Polyphonic Hold
---------------

``Part.hold()`` adds a note without advancing the beat position —
the next note starts at the *same* time. This enables polyphonic
overlap on a single part: piano sustain, sitar drone under melody,
guitar strum texture.

.. code-block:: python

   piano = score.part("piano", instrument="piano", reverb=0.3)

   # Hold a C major chord for 8 beats
   piano.hold("C3", Duration.WHOLE * 2, velocity=60)
   piano.hold("E3", Duration.WHOLE * 2, velocity=55)
   piano.hold("G3", Duration.WHOLE * 2, velocity=55)

   # Melody plays simultaneously on top
   for n in ["E4", "G4", "C5", "G4", "E4", "D4", "C4", "E4"]:
       piano.add(n, Duration.QUARTER, velocity=80)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/piano_hold.wav" type="audio/wav"></audio>

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

.. code-block:: python

   lead = score.part(
       "lead",
       synth="saw",
       legato=True,
       glide=0.03,
       distortion=0.8,
       lowpass=1000,
       lowpass_q=5.0,
   )
   lead.arpeggio(
       Chord.from_symbol("Cm"),
       bars=2,
       pattern="up",
       division=Duration.SIXTEENTH,
       octaves=2,
   )

Parameters:

- ``chord``: A Chord object or string like ``"Am"``.
- ``bars``: Number of bars to fill (default 1).
- ``pattern``: ``"up"``, ``"down"``, ``"updown"``, ``"downup"``, ``"random"``.
- ``division``: Step length (default ``Duration.SIXTEENTH``).
- ``octaves``: Octave span (default 1). With 2, the pattern repeats one octave up.

Chain arpeggios through a progression:

.. code-block:: python

   for sym in ["Cm", "Fm", "Abm", "Gm"]:
       lead.arpeggio(sym, bars=2, pattern="updown", octaves=2)

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

.. code-block:: python

   acid = score.part(
       "acid",
       synth="saw",
       envelope="pad",
       legato=True,
       glide=0.04,
   )
   acid.add("C2", 0.25).add("C3", 0.25).add("G2", 0.25).add("C2", 0.25)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/legato_glide.wav" type="audio/wav"></audio>

- ``legato``: If True, no envelope retrigger between notes (default False).
- ``glide``: Portamento time in seconds (default 0, instant).
  0.03--0.05 = quick 303 slide, 0.1--0.2 = slow glide.

Complete Example
----------------

A full multi-part arrangement built from scratch — bossa nova with FM
rhodes, triangle lead, and filtered bass:

.. code-block:: python

   from pytheory import Score, Pattern, Key, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=140)
   score.drums("bossa nova", repeats=4)

   # FM rhodes with reverb
   rhodes = score.part(
       "rhodes",
       synth="fm",
       envelope="piano",
       volume=0.3,
       reverb=0.4,
       reverb_decay=1.8,
   )

   # Triangle lead with delay
   lead = score.part(
       "lead",
       synth="triangle",
       envelope="pluck",
       volume=0.45,
       delay=0.25,
       delay_time=0.32,
       delay_feedback=0.35,
       reverb=0.2,
   )

   # Filtered bass
   bass = score.part(
       "bass",
       synth="sine",
       envelope="pluck",
       volume=0.45,
       lowpass=600,
   )

   for sym in ["Am", "Am", "Dm", "Dm", "E7", "E7", "Am", "Am"]:
       rhodes.add(Chord.from_symbol(sym), Duration.WHOLE)

   for n, d in [
       ("E5", 0.67), ("D5", 0.33), ("C5", 0.67), ("B4", 0.33),
       ("A4", 1), ("C5", 0.67), ("E5", 0.33), ("D5", 0.67), ("C5", 0.33),
       ("A4", 1),
   ]:
       lead.add(n, d)

   for n in ["A2", "E2", "A2", "C3", "D2", "A2", "D2", "F2"]:
       bass.add(n, Duration.QUARTER)

   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/sequencing_bossa.wav" type="audio/wav"></audio>

Velocity
--------

Real music has dynamics — accents are louder, ghost notes are barely
there, phrases crescendo and decrescendo. Every note can have its own
velocity (1–127, where 100 is the default):

.. code-block:: python

   lead.add("C5", Duration.QUARTER, velocity=120)   # loud accent
   lead.add("D5", Duration.QUARTER, velocity=40)    # ghost note
   lead.add("E5", Duration.QUARTER)                 # default (100)

The arpeggiator also accepts velocity:

.. code-block:: python

   lead.arpeggio("Am", bars=2, pattern="up", velocity=80)

Articulations
-------------

Articulations change *how* a note is played — its attack, duration, and
weight. A staccato note is short and bouncy. A marcato note hits hard.
A legato note melts into the next one. This is the difference between
a melody that sounds like a MIDI file and one that sounds like a
musician played it.

Pass ``articulation=`` to ``Part.add()``:

.. code-block:: python

   piano.add("C4", Duration.QUARTER, articulation="staccato")   # short, bouncy
   piano.add("D4", Duration.QUARTER, articulation="legato")     # smooth, overlaps
   piano.add("E4", Duration.QUARTER, articulation="marcato")    # heavy accent
   piano.add("F4", Duration.QUARTER, articulation="tenuto")     # held, soft attack
   piano.add("G4", Duration.QUARTER, articulation="accent")     # louder
   piano.add("C5", Duration.HALF, articulation="fermata")       # held longer

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/articulations.wav" type="audio/wav"></audio>

What each articulation does:

- **staccato** — plays ~40% of the note duration with a quick fade-out. Short and detached.
- **legato** — extends ~15% into the next note. Smooth and connected.
- **marcato** — 25% velocity boost + sharper attack. Heavy and accented.
- **tenuto** — full duration with a softer attack ramp. Held and deliberate.
- **accent** — 20% velocity boost, no duration change.
- **fermata** — stretches the note 50% longer.

Articulations work on ``Part.hold()`` and ``Part.hit()`` too.

Dynamic Curves
--------------

Real music breathes — phrases get louder, get quieter, swell and
recede. Dynamic curves let you shape the velocity across a sequence
of notes instead of setting each one manually.

.. code-block:: python

   # Crescendo: quiet to loud
   piano.crescendo(["C4","D4","E4","F4","G4","A4","B4","C5"],
                   Duration.QUARTER, start_vel=30, end_vel=110)

   # Decrescendo: loud to quiet
   piano.decrescendo(["C5","B4","A4","G4","F4","E4","D4","C4"],
                     Duration.QUARTER, start_vel=110, end_vel=30)

   # Swell: up then back down (orchestral < > shape)
   strings.swell(["C4","D4","E4","F4","G4","F4","E4","D4"],
                 Duration.QUARTER, low_vel=35, peak_vel=110)

   # Custom curve: explicit velocity per note
   piano.dynamics(["C4","E4","G4","C5"], Duration.QUARTER,
                  velocities=[50, 80, 110, 90])

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/dynamics.wav" type="audio/wav"></audio>

Four methods:

- **crescendo()** — linear velocity ramp from ``start_vel`` to ``end_vel``.
- **decrescendo()** — same thing, but typically loud to quiet.
- **swell()** — ramps up to the midpoint, then back down. The classic
  orchestral crescendo-decrescendo.
- **dynamics()** — the general form. Pass a ``(start, end)`` tuple for
  a linear ramp, or a list of velocities for a custom curve.

All four accept ``articulation=`` to combine dynamics with articulations:

.. code-block:: python

   # Staccato crescendo — bouncy notes getting louder
   piano.crescendo(["C4","E4","G4","C5","E5","G5","C6","E6"],
                   Duration.EIGHTH, start_vel=40, end_vel=110,
                   articulation="staccato")

Part.hit() — Manual Drum Placement
-----------------------------------

The pattern system is great for grooves, but sometimes you want to
place individual drum hits with full control — articulations, effects,
and all. ``Part.hit()`` puts a drum sound into a Part's note stream:

.. code-block:: python

   from pytheory import DrumSound

   kit = score.part("kit", synth="sine", volume=0.7)

   kit.hit(DrumSound.KICK, Duration.QUARTER, articulation="accent")
   kit.hit(DrumSound.CLOSED_HAT, Duration.EIGHTH, velocity=60)
   kit.hit(DrumSound.SNARE, Duration.EIGHTH, articulation="marcato")

Because hits go through the normal Part renderer, they get humanize,
effects, and articulations for free. Use this for custom beats that
don't fit a preset pattern, or for one-shot accent hits layered on
top of a pattern.

Rudiments — Flam, Diddle, Cheese
---------------------------------

Marching percussion rudiments as methods on any Part:

.. code-block:: python

   from pytheory import DrumSound

   p = score.part("snares", synth="sine", volume=0.9)

   # Flam: grace note + main hit (gap controls tightness)
   p.flam(DrumSound.MARCH_SNARE, Duration.QUARTER, velocity=120)

   # Diddle: two equal strokes in one note duration
   p.diddle(DrumSound.MARCH_SNARE, Duration.EIGHTH, velocity=60)

   # Cheese: flam + diddle combined
   p.cheese(DrumSound.MARCH_SNARE, Duration.QUARTER, velocity=120)

Ensemble
--------

Any Part can be rendered as an ensemble — multiple players with
per-player timing tendencies and micro pitch drift:

.. code-block:: python

   # 8-player snare line
   snares = score.part("snares", synth="sine", volume=0.9, ensemble=8)

   # 20-player string section
   strings = score.part("strings", instrument="string_ensemble", ensemble=20)

   # Single player (default)
   solo = score.part("solo", instrument="violin")

Each ensemble voice gets a consistent timing personality (some rush,
some drag) plus small per-note wobble, and slightly different tuning.
The result sounds like a real section — together but alive.

Solo snare, then an 8-player section plays the same pattern:

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/ensemble.wav" type="audio/wav"></audio>

Swing and Groove
----------------

Perfectly quantized music sounds robotic. Swing delays every other
subdivision by a percentage, giving the rhythm a human, shuffled feel.
Jazz swings hard. Bossa nova swings gently. Hip hop has its own pocket.

Set swing on the Score (applies to everything) or per-Part:

.. code-block:: python

   # Triplet swing — lazy jazz feel
   score = Score("4/4", bpm=100, swing=0.55)

   # Per-part override — the lead swings harder than the bass
   lead = score.part("lead", synth="saw", swing=0.6)
   bass = score.part("bass", synth="sine", swing=0.4)

Swing values:

- **0.0** = perfectly straight (default)
- **0.3** = subtle shuffle (pop, R&B)
- **0.5** = triplet feel (jazz, blues)
- **0.67** = hard swing (bebop)

Tempo Changes
-------------

Real music doesn't stay at one tempo. Songs speed up for energy,
slow down for endings, and sometimes shift abruptly. Use
``score.set_tempo()`` to change BPM at the current position:

.. code-block:: python

   score = Score("4/4", bpm=90)

   # Verse: slow and moody
   lead.add("D5", Duration.WHOLE)
   lead.add("F5", Duration.WHOLE)

   # Chorus: speeds up
   score.set_tempo(110)
   lead.add("A5", Duration.WHOLE)
   lead.add("D6", Duration.WHOLE)

   # Outro: slows way down
   score.set_tempo(70)
   lead.add("D5", Duration.WHOLE)

The tempo map engine handles the math — beat positions are converted
to sample positions accounting for every tempo change.

Fades
-----

``Part.fade_in()`` and ``Part.fade_out()`` ramp the volume over a
number of bars. They work by generating automation points, so they
integrate naturally with the rest of the automation system:

.. code-block:: python

   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       volume=0.3,
       reverb=0.5,
   )

   # Fade in over first 4 bars
   pad.fade_in(bars=4)
   for chord in chords:
       pad.add(chord, Duration.WHOLE)

   # Fade out over last 2 bars
   pad.fade_out(bars=2)
   pad.rest(Duration.WHOLE)
   pad.rest(Duration.WHOLE)

Parameter Ramps
---------------

Fades only control volume. ``Part.ramp()`` smoothly sweeps *any*
parameter from its current value to a target — filters, reverb,
distortion, chorus, delay, anything ``.set()`` accepts. This is how
you build filter sweeps, gradual effect sends, and EDM buildups.

.. code-block:: python

   lead = score.part("lead", synth="saw", lowpass=200, lowpass_q=3.0)

   # Open the filter over 8 bars
   lead.ramp(over=Duration.WHOLE * 8, lowpass=8000)

   # Ramp multiple params at once
   pad.ramp(over=Duration.WHOLE * 4, reverb=0.5, chorus=0.3)

   # Close the filter with distortion fading in
   lead.ramp(over=Duration.WHOLE * 4, lowpass=400, distortion=0.5)

Four interpolation curves:

- **linear** — constant rate of change (default).
- **ease_in** — starts slow, accelerates. Good for buildups.
- **ease_out** — starts fast, decelerates. Good for releases.
- **ease_in_out** — slow at both ends. Smooth and natural.

.. code-block:: python

   # EDM buildup: slow start, accelerating filter sweep
   lead.ramp(over=Duration.WHOLE * 8, curve="ease_in", lowpass=8000)

   # Smooth reverb wash fading in and settling
   pad.ramp(over=Duration.WHOLE * 4, curve="ease_in_out", reverb=0.6)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/filter_ramp.wav" type="audio/wav"></audio>

``ramp()`` generates automation points every quarter-beat by default.
Set ``resolution=0.125`` for smoother curves (every 32nd note), or
``resolution=1.0`` for lighter automation (every beat).

Combine with ``lfo()`` for cyclic modulation and ``ramp()`` for
one-shot sweeps — together they cover the full range of parameter
automation.

Humanize
--------

Perfectly quantized music sounds like a machine made it — because it
did. Real musicians are never exactly on the beat. Their timing drifts
by a few milliseconds, their velocity varies from note to note. These
imperfections are what make music feel *alive*.

The ``humanize`` parameter adds random micro-variations in both timing
and velocity at render time. The score data stays clean and
deterministic — the randomness is only applied during playback.

.. code-block:: python

   # Subtle — like a very tight session player
   lead = score.part("lead", synth="saw", humanize=0.1)

   # Natural — like a good live take
   rhodes = score.part("rhodes", synth="fm", humanize=0.3)

   # Loose — like a late-night jam after a few drinks
   bass = score.part("bass", synth="sine", humanize=0.5)

Humanize values:

- **0.0** = perfectly quantized (default)
- **0.1** = subtle, studio-tight
- **0.2–0.3** = natural, like a real player
- **0.4–0.5** = loose, relaxed, human
- **0.6+** = sloppy (sometimes that's what you want)

Combine with swing for the most realistic feel:

.. code-block:: python

   score = Score("4/4", bpm=95, swing=0.45)
   lead = score.part(
       "lead",
       synth="saw",
       envelope="pluck",
       humanize=0.3,
       delay=0.2,
       reverb=0.25,
   )

Song Structure
--------------

Real songs aren't one long stream of notes — they have verses,
choruses, bridges, drops. The section system lets you name blocks
of your arrangement, then repeat them without rewriting everything.

This is how actual songwriting works: you write a verse, you write
a chorus, then you arrange them — verse, verse, chorus, verse,
chorus, chorus, outro. The sections are the building blocks;
the arrangement is the order you play them in.

Define sections with ``score.section()`` and repeat them with
``score.repeat()``:

.. code-block:: python

   score = Score("4/4", bpm=124)
   score.drums("house", repeats=16)

   pad = score.part("pad", synth="supersaw", envelope="pad")
   lead = score.part("lead", synth="saw", envelope="pluck")
   bass = score.part("bass", synth="sine", lowpass=300)

   # ── Define the verse ──
   score.section("verse")
   for sym in ["Cm", "Ab", "Eb", "Bb"]:
       pad.add(Chord.from_symbol(sym), Duration.WHOLE)
   lead.add("C5", 1).add("Eb5", 1).rest(2)
   for n in ["C1", "C1", "Ab0", "Ab0", "Eb1", "Eb1", "Bb0", "Bb0"]:
       bass.add(n, Duration.HALF)

   # ── Define the chorus ──
   score.section("chorus")
   lead.set(lowpass=5000, reverb=0.3)
   for sym in ["Cm", "Fm", "Ab", "Gm"]:
       pad.add(Chord.from_symbol(sym), Duration.WHOLE)
   lead.add("C6", 1).add("Bb5", 1).add("G5", 1).rest(1)
   for n in ["C1", "C1", "F1", "F1", "Ab0", "Ab0", "G1", "G1"]:
       bass.add(n, Duration.HALF)
   score.end_section()

   # ── Arrange: verse, chorus, verse, chorus, chorus ──
   score.repeat("verse")
   score.repeat("chorus")
   score.repeat("verse")
   score.repeat("chorus", times=2)

Use any names you want — ``"intro"``, ``"verse"``, ``"chorus"``,
``"bridge"``, ``"drop"``, ``"breakdown"``, ``"outro"``, or anything
that makes sense for your song. The names are just labels.

Guitar Strumming
----------------

Any part with a fretboard can strum chords using real fingering
positions. The ``strum()`` method looks up the chord on the fretboard,
gets the correct voicing, and plays all strings as a chord.

.. code-block:: python

   from pytheory import Fretboard

   guitar = score.part("guitar", instrument="acoustic_guitar",
                       fretboard=Fretboard.guitar())

   guitar.strum("Am", Duration.HALF, direction="down")
   guitar.strum("G", Duration.HALF, direction="up")
   guitar.strum("F", Duration.WHOLE)

Works with any fretboard instrument — guitar, ukulele, banjo, mandolin.
Works with any guitar preset — clean, crunch, distorted, orange, metal.

Pitch Bends
-----------

Bend a note's pitch up or down over its duration. Essential for guitar
bends, sitar meends, trombone slides, and vocal-style expression.

.. code-block:: python

   # Guitar bend: D up to E (2 semitones)
   guitar.add("D4", Duration.HALF, bend=2, bend_type="smooth")

   # Release bend: E back down to D
   guitar.add("E4", Duration.HALF, bend=-2)

   # Blues curl: hold then bend at the end
   guitar.add("C4", Duration.HALF, bend=1, bend_type="late")

Three bend types:

- ``"smooth"`` — logarithmic (default). Perceptually even pitch change.
- ``"linear"`` — linear frequency interpolation. Mechanical/synth feel.
- ``"late"`` — holds the starting pitch for 60%, bends in the last 40%.
  The classic blues "curl."

Rolls
-----

Rapid repeated notes with a velocity ramp — perfect for timpani
rolls, snare rolls, tremolo on any instrument. The velocity ramps
from ``velocity_start`` to ``velocity_end`` for crescendo or
decrescendo effects.

.. code-block:: python

   # Timpani crescendo roll
   timp = score.part("timp", instrument="timpani")
   timp.roll("C3", Duration.WHOLE, velocity_start=20, velocity_end=110)
   timp.add("C3", Duration.HALF, velocity=127)  # big accent

   # Snare roll with 32nd notes
   snare = score.part("snare", synth="noise", envelope="pluck")
   snare.roll("C4", Duration.HALF, speed=0.125,
              velocity_start=40, velocity_end=100)

   # Decrescendo (loud to quiet)
   timp.roll("G2", Duration.WHOLE, velocity_start=100, velocity_end=30)

Parameters:

- ``velocity_start``: Starting velocity (default 40).
- ``velocity_end``: Ending velocity (default 100).
- ``speed``: Note subdivision (default ``Duration.SIXTEENTH``).
  Use ``0.125`` for 32nd notes, ``Duration.EIGHTH`` for 8th notes.

Tuning Systems
--------------

A Score can use any tuning system and temperament:

.. code-block:: python

   # Baroque harpsichord — meantone tuning, A=415
   score = Score("4/4", bpm=80, temperament="meantone",
                 reference_pitch=415.0)

   # Indian classical — 22-shruti system
   score = Score("4/4", bpm=75, system="shruti")

   # Just intonation — pure intervals
   score = Score("4/4", bpm=90, temperament="just")

The Score constructor accepts these tuning parameters:

- ``system``: Musical system name (default ``"western"``). Any system
  from :doc:`systems` works — ``"indian"``, ``"shruti"``, ``"maqam"``,
  ``"carnatic"``, etc. Note strings in ``Part.add()`` are parsed against
  this system.
- ``temperament``: Tuning temperament — ``"equal"`` (default),
  ``"pythagorean"``, ``"meantone"``, ``"just"``.
- ``reference_pitch``: Concert pitch in Hz (default 440.0). Use 415.0
  for Baroque tuning, 432.0 for "Verdi tuning", etc.

Custom equal temperaments via the ``TET()`` factory:

.. code-block:: python

   from pytheory import TET

   edo19 = TET(19)  # 19-tone equal temperament
   score = Score("4/4", bpm=100, system=edo19)
