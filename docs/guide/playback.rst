Playback and Export
===================

This is the output layer. You've built your theory, composed your
arrangement, shaped your sounds -- now you need to hear it. PyTheory
gives you three ways to get your music out: speakers, WAV files, and
MIDI files.

Use **speakers** for immediate feedback while you're sketching and
experimenting. Use **WAV export** when you want to share actual audio
-- post it, send it, drop it into a video. Use **MIDI export** when you
want to bring your sketch into a real DAW and finish it with
professional instruments, mixing, and mastering. Each output serves a
different stage of the creative process.

PyTheory can play audio through your speakers, save to WAV, or export
to MIDI. Everything is synthesized from waveforms -- no samples or
external audio files needed.

.. note::

   Audio playback requires `PortAudio <http://www.portaudio.com/>`_ to be
   installed on your system. On macOS: ``brew install portaudio``.
   On Ubuntu: ``apt install libportaudio2``.

play() -- Single Tones and Chords
---------------------------------

The simplest way to hear something:

.. code-block:: python

   from pytheory import Tone, Chord, play

   play(Tone.from_string("A4"), t=1_000)          # A440 for 1 second
   play(Chord.from_symbol("Am7"), t=2_000)         # chord for 2 seconds

Optional parameters for synth, envelope, and temperament:

.. code-block:: python

   from pytheory import Synth, Envelope

   play(Tone.from_string("C4"), synth=Synth.SAW, envelope=Envelope.PLUCK, t=1_000)
   play(Tone.from_string("C4"), temperament="pythagorean", t=1_000)

play_score() -- Full Arrangements
---------------------------------

Plays a ``Score`` with all its parts and drums mixed together:

.. code-block:: python

   from pytheory import Score, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=140)
   score.drums("bossa nova", repeats=4)
   chords = score.part("chords", synth="sine", envelope="pad")
   for sym in ["Am", "Dm", "E7", "Am"]:
       chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   play_score(score)

See :doc:`sequencing` for how to build scores and parts.

render_score() -- Headless Rendering
------------------------------------

Returns a raw audio buffer (numpy float32 array) without playing it.
Useful for saving to WAV or further processing:

.. code-block:: pycon

   >>> from pytheory.play import render_score
   >>> buf = render_score(score)   # numpy float32 array
   >>> len(buf)
   604800

save() -- WAV Export
--------------------

Render tones or chords to a WAV file. Works without speakers or
PortAudio:

.. code-block:: python

   from pytheory import save, Chord, Tone, Synth

   save(Tone.from_string("A4"), "a440.wav", t=1_000)
   save(Chord.from_name("Am7"), "am7.wav", t=2_000)
   save(
       Chord.from_name("C"),
       "c_triangle.wav",
       synth=Synth.TRIANGLE,
       temperament="meantone",
       t=3_000,
   )

save_midi() -- MIDI Export
--------------------------

MIDI export is probably the most useful feature here for working
musicians. The idea is simple: sketch your ideas in Python -- where
iteration is fast, where you can use loops and randomness and music
theory functions -- and then export to MIDI. Open that MIDI file in
Logic, Ableton, Reaper, FL Studio, or whatever you use, and now you've
got your chord progressions, melodies, and bass lines on real tracks.
Swap in your favorite soft synths, add real mixing, finish the track
properly. Python is the sketchpad; the DAW is the canvas.

Export tones, chords, progressions, or full scores as Standard MIDI
Files. MIDI files can be opened in any DAW, edited, transposed, and
assigned to any instrument.

Simple export (single tone, chord, or progression):

.. code-block:: python

   from pytheory import save_midi, Key, Tone, Chord

   save_midi(Tone.from_string("C4"), "middle_c.mid", t=1000)
   save_midi(Chord.from_symbol("Am7"), "am7.mid")

   chords = Key("C", "major").progression("I", "V", "vi", "IV")
   save_midi(chords, "pop.mid", t=500, bpm=120)

Score-based export (with time signature, tempo, and parts):

.. code-block:: python

   from pytheory import Score, Duration, Key

   score = Score("4/4", bpm=140)
   for chord in Key("G", "major").progression("I", "IV", "V", "I"):
       score.add(chord, Duration.WHOLE)
   score.save_midi("progression.mid")

play_pattern() -- Drum Patterns
-------------------------------

Play a drum pattern through the speakers:

.. code-block:: python

   from pytheory import Pattern
   from pytheory.play import play_pattern

   play_pattern(Pattern.preset("rock"), repeats=4, bpm=120)
   play_pattern(Pattern.preset("bossa nova"), repeats=4, bpm=140)

See :doc:`drums` for the full list of 58 presets and 21 fills.

play_progression() -- Quick Chord Playback
------------------------------------------

Play a chord progression in sequence with a single call:

.. code-block:: python

   from pytheory import Key, play_progression

   chords = Key("C", "major").progression("I", "V", "vi", "IV")
   play_progression(chords, t=800)

Optional synth, envelope, and gap parameters:

.. code-block:: python

   from pytheory import Synth, Envelope

   play_progression(chords, t=1000, synth=Synth.TRIANGLE, gap=200)
   play_progression(chords, t=2000, envelope=Envelope.PAD)

That's the workflow: hear it, tweak it, hear it again. When it sounds right, export to WAV or MIDI and take it somewhere bigger.
