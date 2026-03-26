Quickstart
==========

From zero to a multi-part arrangement in 5 minutes.

Installation
------------

::

   $ pip install pytheory

For audio playback through your speakers, you'll also need
`PortAudio <http://www.portaudio.com/>`_:

- macOS: ``brew install portaudio``
- Ubuntu: ``apt install libportaudio2``
- Windows: included with the ``sounddevice`` package

PortAudio is only needed for live playback. MIDI export, WAV export,
and all theory functions work without it.

Hear Something Immediately
--------------------------

::

   $ pytheory demo

This generates and plays a random track — different every time. It's
the fastest way to hear what PyTheory can do.

Explore Music Theory
--------------------

The theory layer is where most people start. Every concept in Western
music theory (and five other systems) has a clean Python API:

.. code-block:: pycon

   >>> from pytheory import Key, Chord, Tone

   >>> key = Key("C", "major")
   >>> key.chords
   ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

   >>> [c.symbol for c in key.progression("I", "V", "vi", "IV")]
   ['C', 'G', 'Am', 'F']

   >>> Chord.from_symbol("Am7").identify()
   'A minor 7th'

   >>> Tone.from_string("C4").interval_to(Tone.from_string("G4"))
   'perfect 5th'

   >>> Key("C", "major").pivot_chords(Key("G", "major"))
   ['A minor', 'B minor', 'C major', 'D major', 'E minor', 'G major']

Compose a Track
---------------

This is where it gets fun. A ``Score`` is your arrangement — drums,
chords, melody, bass, each with their own synth and effects:

.. code-block:: python

   from pytheory import Score, Pattern, Key, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=140)
   score.drums("bossa nova", repeats=4)

   chords = score.part(
       "chords",
       synth="fm",
       envelope="pad",
       reverb=0.4,
   )
   lead = score.part(
       "lead",
       synth="saw",
       envelope="pluck",
       delay=0.3,
       lowpass=3000,
       humanize=0.2,
   )
   bass = score.part(
       "bass",
       synth="sine",
       lowpass=500,
   )

   key = Key("A", "minor")
   for chord in key.progression("i", "iv", "V", "i"):
       chords.add(chord, Duration.WHOLE)
       chords.add(chord, Duration.WHOLE)

   lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)
   lead.arpeggio("Dm", bars=2, pattern="updown", octaves=2)
   lead.set(lowpass=5000, reverb=0.3)
   lead.arpeggio("E7", bars=2, pattern="up", octaves=2)
   lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)

   for n in ["A2", "E2", "A2", "C3"] * 4:
       bass.add(n, Duration.QUARTER)

   play_score(score)

Export to Your DAW
------------------

The whole point: sketch in Python, finish in Logic / Ableton / Reaper.

.. code-block:: python

   score.save_midi("my_sketch.mid")

Open that file in any DAW and you'll see all the notes laid out on
the timeline, ready to assign to real instruments and mix.

You can also save rendered audio:

.. code-block:: python

   from pytheory import save
   save(Chord.from_symbol("Am7"), "am7.wav", t=2_000)

What's in the Box
-----------------

**Theory** — tones, scales (40+ across 6 musical systems), chords
(17 types, Roman numeral analysis, tension scoring, voice leading),
keys (detection, signatures, modulation paths, borrowed chords).

**Sequencing** — Score, Part, Duration, TimeSignature. Arpeggiator
with 5 patterns. Legato with pitch glide. Per-note velocity. Swing.
Tempo changes. Fade in/out. Song sections with repeat. Humanize.

**Synthesis** — 10 waveforms: sine, saw, triangle, square, pulse, FM,
noise, supersaw, PWM slow, PWM fast. 8 ADSR envelopes.

**Effects** — distortion, chorus, lowpass filter (with resonance),
delay, reverb (algorithmic + 7 convolution presets including
Taj Mahal with 12-second tail). All per-part with automation and
LFO modulation. Sidechain compression.

**Drums** — 58 pattern presets (rock, jazz, salsa, bossa nova,
afrobeat, house, trap, and 50+ more). 21 fill presets. 27 synthesized
drum voices.

**Instruments** — 25 presets (guitar with 8 tunings, bass, ukulele,
mandolin family, violin family, banjo, harp, oud, sitar, erhu, and
more) with chord fingering generation and scale diagrams.

**Export** — MIDI, WAV, real-time playback.

**CLI** — ``pytheory demo``, ``pytheory key``, ``pytheory chord``,
``pytheory identify``, ``pytheory midi``, ``pytheory play``, and more.

Where to Go Next
-----------------

- :doc:`theory` — music theory fundamentals
- :doc:`tones` — working with individual notes
- :doc:`scales` — scales, modes, and keys
- :doc:`chords` — chord construction, analysis, and progressions
- :doc:`sequencing` — composing multi-part arrangements
- :doc:`synths` — the 10 waveforms and 8 envelopes
- :doc:`effects` — reverb, delay, distortion, chorus, lowpass, automation
- :doc:`drums` — 58 patterns, 21 fills, drum synthesis
- :doc:`playback` — play, save, export
