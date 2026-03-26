PyTheory: Music Theory for Humans
=================================

**PyTheory** is a Python library for exploring music theory, composing
multi-part arrangements, and exporting them to MIDI for your DAW.

Use it to learn theory by doing — build chords from intervals and hear
the result. Use it to sketch song ideas faster than clicking through a
DAW. Use it with `Claude Code <https://claude.ai/code>`_ to prototype
music from natural language. Or just use it to answer "what chords are
in G major?" without opening a browser.

::

   $ pip install pytheory

Theory
------

The theory layer works everywhere Python runs — no audio setup needed.
Tones, scales, chords, keys, intervals, harmony, 6 musical systems,
25 instruments:

.. code-block:: pycon

   >>> from pytheory import Key, Chord, Tone

   >>> Key("C", "major").chords
   ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

   >>> [c.symbol for c in Key("G", "major").progression("I", "V", "vi", "IV")]
   ['G', 'D', 'Em', 'C']

   >>> Chord.from_symbol("F#m7b5").identify()
   'F# half-diminished 7th'

   >>> Tone.from_string("C4").interval_to(Tone.from_string("G4"))
   'perfect 5th'

Composition
-----------

When you're ready to make noise, the composition layer adds drums,
synths, effects, and multi-part arrangements. Sketch an idea, hear
it through your speakers, export MIDI, finish in your DAW:

.. code-block:: python

   from pytheory import Score, Pattern, Key, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=140)
   score.drums("bossa nova", repeats=4)

   chords = score.part("chords", synth="fm", envelope="pad", reverb=0.4)
   lead = score.part("lead", synth="saw", envelope="pluck", delay=0.3)
   bass = score.part("bass", synth="sine", lowpass=500)

   for chord in Key("A", "minor").progression("i", "iv", "V", "i"):
       chords.add(chord, Duration.WHOLE)

   lead.arpeggio("Am", bars=4, pattern="updown", octaves=2)

   play_score(score)
   score.save_midi("sketch.mid")

Or hear a randomly generated track from the command line — different
every time::

   $ pytheory demo

What's Inside
-------------

- **Theory** — tones, scales (40+ across 6 systems), chords (17 types),
  keys, Roman numeral analysis, modulation, voice leading
- **Sequencing** — Score, Parts, arpeggiator, legato/glide, velocity,
  swing, humanize, tempo changes, song sections
- **Synthesis** — 10 waveforms, 8 envelopes, 58 drum patterns, 21 fills
- **Effects** — reverb (algorithmic + 7 convolution IRs), delay, lowpass,
  distortion, chorus, sidechain, automation, LFOs
- **Instruments** — 25 presets with fingering generation
- **Export** — MIDI, WAV, real-time playback
- **CLI** — ``pytheory demo``, ``key``, ``chord``, ``midi``, ``play``, and more
- **AI-friendly** — `Claude Code <https://claude.ai/code>`_ can compose
  and play music through PyTheory from natural language

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
