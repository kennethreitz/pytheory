PyTheory: Music Theory for Humans
=================================

**PyTheory** is a Python library for exploring music theory, composing
multi-part arrangements, and exporting them to MIDI for your DAW.

::

   $ pip install pytheory

Why Compose in Python?
----------------------

A DAW is great for tweaking sounds. But when you're *thinking about
music* — exploring a chord progression, trying every mode of a scale,
figuring out which chords two keys share for a modulation — code is
faster than clicking.

PyTheory lets you:

- **Sketch ideas in seconds**. Type ``Key("A", "minor").progression("i", "iv", "V", "i")``
  and hear it immediately. Change the key, the mode, the voicing — all
  in one line. No mouse, no menus.

- **Build arrangements programmatically**. Layer drums, bass, chords,
  and leads as named Parts with independent synths, effects, and
  automation. Then export to MIDI and finish in your DAW.

- **Generate music algorithmically**. Write a script that picks keys,
  progressions, and melodies from rules you define — every run produces
  something new. Use it for inspiration, ear training, or generative art.

- **Learn theory by doing**. Instead of reading about the circle of
  fifths, *call* it. Instead of memorizing chord formulas, *build* chords
  from intervals and hear the result.

The workflow: **sketch in Python → hear it instantly → export MIDI → finish in your DAW**.

Quick Example
~~~~~~~~~~~~~

From idea to MIDI in 10 lines:

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)
   >>> score.drums("bossa nova", repeats=4)

   >>> chords = score.part("chords", synth="fm", envelope="pad", reverb=0.4)
   >>> lead = score.part("lead", synth="saw", envelope="pluck",
   ...                   delay=0.3, lowpass=3000, legato=True, glide=0.03)
   >>> bass = score.part("bass", synth="sine", lowpass=500)

   >>> for sym in ["Am", "Dm", "E7", "Am"]:
   ...     chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   ...     chords.add(Chord.from_symbol(sym), Duration.WHOLE)

   >>> lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)
   >>> lead.arpeggio("Dm", bars=2, pattern="updown", octaves=2)
   >>> lead.set(lowpass=5000, reverb=0.4)
   >>> lead.arpeggio("E7", bars=2, pattern="up", octaves=2)
   >>> lead.arpeggio("Am", bars=2, pattern="updown", octaves=2)

   >>> for n in ["A2","E2","A2","C3"] * 4:
   ...     bass.add(n, Duration.QUARTER)

   >>> play_score(score)              # hear it now
   >>> score.save_midi("sketch.mid")  # open in your DAW

Theory
~~~~~~

.. code-block:: pycon

   >>> from pytheory import Key, Chord, Tone, Scale, Fretboard

   >>> key = Key("C", "major")
   >>> key.chords
   ['C major', 'D minor', 'E minor', 'F major',
    'G major', 'A minor', 'B diminished']

   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['C major', 'G major', 'A minor', 'F major']

   >>> Chord.from_symbol("F#m7b5").identify()
   'F# half-diminished 7th'

   >>> c4 = Tone.from_string("C4", system="western")
   >>> c4.interval_to(c4 + 7)
   'perfect 5th'

   >>> Key("C", "major").pivot_chords(Key("G", "major"))
   ['A minor', 'B minor', 'C major', 'D major', 'E minor', 'G major']

   >>> fb = Fretboard.guitar()
   >>> fb.chord("G")
   Fingering(e=3, B=0, G=0, D=0, A=2, E=3)

Highlights
----------

**Theory**

- **Tones**: frequencies, MIDI, intervals, transposition, circle of fifths,
  overtone series, solfege, Helmholtz notation, cents comparison,
  3 temperaments (equal, Pythagorean, meantone)
- **Scales**: 40+ scales across 6 musical systems — Western, Indian,
  Arabic, Japanese, Blues, Javanese Gamelan. Scale fitness scoring,
  degree names, parallel modes
- **Chords**: 17 types identified automatically, Roman numeral analysis
  (including borrowed chords: bVI, bVII), tension scoring, voice leading,
  consonance/dissonance, drop voicings, slash chords, extensions
- **Keys**: key detection, signatures, progressions (Roman numerals and
  Nashville numbers), borrowed chords, secondary dominants, modulation
  paths, chord suggestions

**Instruments**

- 25 instrument presets (guitar, bass, ukulele, mandolin, violin, banjo,
  oud, sitar, erhu, and more) with fingering generation
- 58 drum pattern presets (rock, jazz, salsa, bossa nova, afrobeat, funk,
  reggae, house, trap, metal, and 48 more)
- 21 drum fill presets with auto-fill support

**Synthesis and Effects**

- 10 synth waveforms: sine, saw, triangle, square, pulse, FM, noise,
  supersaw, PWM slow, PWM fast
- 8 ADSR envelope presets: piano, pluck, pad, organ, bell, strings,
  staccato, none
- 5 audio effects: distortion, chorus, lowpass filter (with resonance),
  delay, reverb — all per-part with independent settings
- Legato mode with pitch glide/portamento
- Arpeggiator with 5 patterns and octave spanning
- Effect automation via ``.set()`` and LFO modulation via ``.lfo()``
- 27 synthesized drum voices (no samples needed)

**Export**

- Standard MIDI File export — open in any DAW, notation software, or player
- WAV audio export
- Real-time playback through speakers

It also works from the command line::

   $ pytheory key G major
   $ pytheory chord C E G
   $ pytheory identify Cmaj7
   $ pytheory progression C major I V vi IV
   $ pytheory midi C major I V vi IV -o pop.mid
   $ pytheory play Am7 --synth saw --envelope pluck

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/quickstart
   guide/theory
   guide/tones
   guide/scales
   guide/chords
   guide/fretboard
   guide/systems
   guide/sequencing
   guide/synths
   guide/effects
   guide/drums
   guide/playback
   guide/cli
   guide/cookbook

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/tones
   api/scales
   api/chords
   api/charts
   api/play
   api/systems

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog
