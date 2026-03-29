Quickstart
==========

PyTheory works at two levels — pick the one that fits what you need:

1. **Music theory** — explore scales, chords, keys, intervals, and
   harmony. No audio required. Works anywhere Python runs.

2. **Composition** — build multi-part arrangements with drums, synths,
   effects, and export to MIDI. Needs PortAudio for live playback.

Both are first-class. You can use PyTheory purely as a theory
reference and never touch the audio side, or you can jump straight
into composing. This guide covers both paths.

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

The theory layer is where most people start. No audio setup needed —
this works everywhere Python runs. Every concept in Western music
theory (and five other systems) has a clean Python API.

Tones and intervals:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4.frequency
   261.6255653005986
   >>> c4.midi
   60

   >>> c4 + 7
   <Tone G4>
   >>> c4.interval_to(c4 + 7)
   'perfect 5th'

   >>> Tone.from_frequency(440)
   <Tone A4>
   >>> Tone.from_midi(69)
   <Tone A4>

Keys, scales, and chords:

.. code-block:: pycon

   >>> from pytheory import Key, Chord

   >>> key = Key("C", "major")
   >>> key.chords
   ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

   >>> [c.symbol for c in key.progression("I", "V", "vi", "IV")]
   ['C', 'G', 'Am', 'F']

   >>> key.signature
   {'sharps': 0, 'flats': 0, 'accidentals': []}

   >>> Key("F", "major").signature
   {'sharps': 0, 'flats': 1, 'accidentals': ['Bb']}

   >>> Chord.from_symbol("Am7").identify()
   'A minor 7th'

   >>> Chord.from_tones("G", "B", "D", "F").analyze("C")
   'V7'

Harmonic analysis and modulation:

.. code-block:: pycon

   >>> Key("C", "major").pivot_chords(Key("G", "major"))
   ['A minor', 'B minor', 'C major', 'D major', 'E minor', 'G major']

   >>> Key("C", "major").relative
   <Key A minor>

   >>> key.suggest_next(key.triad(4))  # what follows V?
   [<Chord C major>, <Chord A minor>, <Chord F major>]

Scales across 6 musical systems:

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> TonedScale(tonic="Sa4", system="indian")["bhairav"].note_names
   ['Sa', 'komal Re', 'Ga', 'Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

   >>> TonedScale(tonic="Do4", system="arabic")["hijaz"].note_names
   ['Do', 'Reb', 'Mi', 'Fa', 'Sol', 'Solb', 'Sib', 'Do']

   >>> TonedScale(tonic="C4", system="japanese")["hirajoshi"].note_names
   ['C', 'D', 'D#', 'G', 'G#', 'C']

Guitar fingerings:

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> fb.chord("Am")
   Fingering(e=0, B=1, G=2, D=2, A=0, E=x)

All of the above works without PortAudio, without sounddevice,
without any audio setup at all. It's pure Python music theory.

Compose a Track
---------------

This is where it gets fun. A ``Score`` is your arrangement — drums,
chords, melody, bass, each with their own synth and effects:

.. code-block:: python

   from pytheory import Score, Key, Duration
   from pytheory.play import play_score

   score = Score("4/4", bpm=120)
   score.drums("rock", repeats=8, fill="rock", fill_every=4)

   piano = score.part("piano", instrument="piano", reverb=0.3)
   lead = score.part("lead", synth="saw", envelope="pluck",
                     delay=0.2, reverb=0.2, lowpass=4000)
   bass = score.part("bass", synth="triangle", lowpass=900)

   for chord in Key("G", "major").progression("I", "V", "vi", "IV") * 2:
       piano.add(chord, Duration.WHOLE)

   lead.add("D5", 1).add("B4", 0.5).add("D5", 0.5)
   lead.add("G5", 1).add("E5", 1)
   lead.add("D5", 0.5).add("B4", 0.5).add("A4", 1)
   lead.add("G4", 2).rest(2)

   for n in ["G2", "G2", "D2", "D2", "E2", "E2", "C2", "C2"] * 2:
       bass.add(n, Duration.HALF)

   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/quickstart.wav" type="audio/wav"></audio>

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
(17 types, Roman numeral analysis, figured bass, tension scoring,
voice leading, pitch class sets with Forte numbers), keys (detection,
signatures, modulation paths, borrowed chords), scale recommendation.

**Sequencing** — Score, Part, Duration, TimeSignature. Arpeggiator
with 5 patterns. Legato with pitch glide. Per-note velocity. Swing.
Tempo changes. Fade in/out. Song sections with repeat. Humanize.

**Synthesis** — 10 waveforms: sine, saw, triangle, square, pulse, FM,
noise, supersaw, PWM slow, PWM fast. 8 ADSR envelopes. Detune.
Stereo pan and spread.

**Effects** — distortion, chorus, lowpass filter (with resonance),
delay, reverb (algorithmic + 7 stereo convolution presets including
Taj Mahal with 12-second tail). All per-part with automation and
LFO modulation. Sidechain compression. Master bus compressor/limiter.

**Drums** — 58 pattern presets (rock, jazz, salsa, bossa nova,
afrobeat, house, trap, and 50+ more). 21 fill presets. 27 synthesized
drum voices with stereo panning.

**Instruments** — 25 presets (guitar with 8 tunings, bass, ukulele,
mandolin family, violin family, banjo, harp, oud, sitar, erhu, and
more) with chord fingering generation and scale diagrams.

**Output** — stereo playback, WAV export, MIDI import/export.

**Interface** — REPL with tab completion (``pytheory repl``), CLI with
15 commands. ``pytheory demo``, ``pytheory key``, ``pytheory chord``,
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
