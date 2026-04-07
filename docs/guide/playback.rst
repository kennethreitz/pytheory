Playback and Export
===================

This is the output layer. You've built your theory, composed your
arrangement, shaped your sounds -- now you need to hear it. PyTheory
gives you four ways to get your music out: speakers, WAV files, MIDI
files, and sheet music.

Use **speakers** for immediate feedback while you're sketching and
experimenting. Use **WAV export** when you want to share actual audio
-- post it, send it, drop it into a video. Use **MIDI export** when you
want to bring your sketch into a real DAW and finish it with
professional instruments, mixing, and mastering. Use **ABC notation
export** when you want sheet music -- rendered in the browser or shared
as plain text. Each output serves a different stage of the creative
process.

PyTheory can play audio through your speakers, save to WAV, export to
MIDI, or generate sheet music as ABC notation. Everything is synthesized
from waveforms -- no samples or external audio files needed.

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

Synth-specific parameters are passed through as keyword arguments:

.. code-block:: python

   # Mellotron with flute tape
   play(Tone.from_string("C4"), synth=Synth.MELLOTRON, tape="choir", t=2_000)

   # Hard sync with custom slave ratio
   play(Tone.from_string("C4"), synth=Synth.HARD_SYNC, slave_ratio=2.5)

   # Wavefolding with 4 folds
   play(Tone.from_string("C4"), synth=Synth.WAVEFOLD, folds=4.0)

   # Drift oscillator with square shape
   play(Tone.from_string("C4"), synth=Synth.DRIFT, shape="square")

play_score() -- Full Arrangements
---------------------------------

Plays a ``Score`` with all its parts and drums mixed together.
Output is **stereo** — each part is panned according to its ``pan``
setting, drums are stereo-panned like a real kit, and reverb tails
have natural stereo width. A **master bus compressor/limiter** (4:1
ratio, brick-wall at 0.95) is applied to prevent clipping and make
the mix louder and punchier:

.. code-block:: python

   from pytheory import Score, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=140)
   score.drums("bossa nova", repeats=4)
   chords = score.part("chords", synth="sine", envelope="pad")
   for sym in ["Am", "Dm", "E7", "Am"]:
       chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/playback_basic.wav" type="audio/wav"></audio>

The render pipeline respects the Score's ``temperament`` and
``reference_pitch`` settings, so Baroque or microtonal scores play back
at the correct tuning:

.. code-block:: python

   score = Score("4/4", bpm=80, temperament="meantone", reference_pitch=415.0)

Press **Ctrl+C** at any time during playback to stop — PyTheory catches
``KeyboardInterrupt`` and stops audio cleanly.

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

to_abc() -- ABC Notation / Sheet Music
---------------------------------------

ABC notation is a human-readable text format for music that tools can
turn into staff notation and MIDI. It's widely used for folk tunes,
lead sheets, and quick sketches. PyTheory can export any Score as ABC
notation -- and optionally wrap it in an HTML page that renders
sheet music right in the browser using `abcjs <https://www.abcjs.net/>`_.

Basic export:

.. code-block:: python

   from pytheory import Score, Duration, Key

   score = Score("4/4", bpm=120)
   lead = score.part("lead")
   for chord in Key("C", "major").progression("I", "V", "vi", "IV"):
       lead.add(chord, Duration.WHOLE)

   print(score.to_abc(title="Pop Chords", key="C"))

Output:

.. code-block:: text

   X:1
   T:Pop Chords
   M:4/4
   Q:1/4=120
   L:1/8
   K:C
   [CEG]8 | [GBd]8 | [Ace]8 | [FAc]8 |

Open sheet music in the browser with ``html=True``:

.. code-block:: python

   html = score.to_abc(title="Pop Chords", key="C", html=True)

   with open("chords.html", "w") as f:
       f.write(html)

   import webbrowser
   webbrowser.open("chords.html")

This generates a self-contained HTML page with an embedded
``<script>`` tag that loads abcjs from a CDN and renders the notation
as SVG -- no build steps, no dependencies, just open the file.

Multi-part scores automatically get ``V:`` (voice) directives so each
instrument appears on its own staff. Bass parts (average note below C4)
get bass clef automatically. Drum-only parts are skipped. Notes longer
than one measure are split into tied notes across barlines.

Parameters:

- **title** -- Tune title for the ``T:`` header (default ``"Untitled"``).
- **key** -- ABC key signature string (default ``"C"``). Use ``"Am"`` for
  A minor, ``"Bb"`` for B-flat major, ``"F#m"`` for F-sharp minor, etc.
- **html** -- If ``True``, return a full HTML document instead of raw ABC
  (default ``False``).

play_pattern() -- Drum Patterns
-------------------------------

Play a drum pattern through the speakers:

.. code-block:: python

   from pytheory import Pattern
   from pytheory.play import play_pattern

   play_pattern(Pattern.preset("rock"), repeats=4, bpm=120)
   play_pattern(Pattern.preset("bossa nova"), repeats=4, bpm=140)

See :doc:`drums` for the full list of 80+ presets and 21 fills.

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

MIDI Import
-----------

Load any Standard MIDI File into a Score — then play it through
PyTheory's synth engine with effects, or analyze the theory:

.. code-block:: python

   from pytheory import Score
   from pytheory.play import play_score

   score = Score.from_midi("song.mid")

   # See what's inside
   for name, part in score.parts.items():
       print(f"{name}: {len(part.notes)} notes")

   # Change the synth and add effects
   score.parts["ch1"].synth = "saw"
   score.parts["ch1"].reverb_mix = 0.3

   play_score(score)

Each MIDI channel becomes a named Part (``ch1``, ``ch2``, etc.).
Channel 10 (drums) becomes drum hits. Tempo, time signature,
note durations, and velocities are all preserved.

Download any MIDI file from the internet, load it, play it through
the synth engine with reverb and delay. That's the whole idea.
