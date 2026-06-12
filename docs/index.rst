PyTheory: Music Theory for Humans
=================================

**PyTheory** is a Python library for exploring music theory, composing
multi-part arrangements, and exporting them to MIDI, sheet music, or
audio — with nothing to install but Python packages. No DAW, no
samples, no plugins.

New to `uv <https://docs.astral.sh/uv/getting-started/installation/>`_?
It's the fast Python package manager — one command to install, no
virtualenv ceremony.

::

   $ uv add pytheory

Or skip installing entirely and try PyTheory in your browser at the
`playground <https://playground.pytheory.org>`_.

Why would I want this?
----------------------

Different people come to PyTheory for different reasons. You might be:

- **Learning theory** — you want to *see* what's inside a chord, why a
  progression works, or what makes Dorian sound different from minor.
  PyTheory answers in code you can poke at. Start with
  :doc:`guide/quickstart`, then :doc:`guide/theory`.
- **Playing guitar** — you want chord fingerings, scale diagrams,
  Nashville number charts, or tablature without opening a browser full
  of ads. Start with :doc:`guide/fretboard`.
- **Sketching songs** — you want to hear an idea *now*: four chords, a
  drum groove, a bass line, through your speakers in a dozen lines of
  Python. Export MIDI when it's good and finish in your DAW. Start
  with :doc:`guide/sequencing`.
- **Playing live** — you have a MIDI keyboard and want a synth rig in
  the terminal, with recording — or a session to join over Ableton
  Link. Start with :doc:`guide/live`.
- **Capturing ideas** — you hummed a melody into your phone and want
  it as notes, MIDI, or sheet music. ``Score.from_wav("hum.m4a")``
  transcribes it — or run ``pytheory studio`` and just drop the file
  in your browser. Start with :doc:`guide/listening`.
- **Tuning up** — ``pytheory tune --instrument guitar`` is a
  real-time strobe tuner that locks to your open strings. Also in
  :doc:`guide/listening`.
- **Composing with AI** — Claude Code can drive PyTheory from natural
  language: "write me a bossa nova in G minor" becomes a Score you can
  hear, edit, and export.

Theory
------

The theory layer works everywhere Python runs — no audio setup needed.
Tones, scales, chords, keys, intervals, harmony, 16 musical systems:

.. code-block:: pycon

   >>> from pytheory import Key, Chord, Tone

   >>> Key("C", "major").chords
   ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

   >>> [c.symbol for c in Key("G", "major").progression("I", "V", "vi", "IV")]
   ['G', 'D', 'Em', 'C']

   >>> Tone.from_string("C4").interval_to(Tone.from_string("G4"))
   'perfect 5th'

Guitar
------

Chord fingerings, identification, scale diagrams, and tablature —
for guitar and 24 other stringed instruments, in any tuning:

.. code-block:: pycon

   >>> from pytheory import Fretboard, Chord

   >>> print(Fretboard.guitar().tab("Am"))
   A minor
   E|--x--
   A|--0--
   D|--2--
   G|--2--
   B|--1--
   e|--0--

   >>> Chord.from_symbol("F#m7b5").identify()
   'F# half-diminished 7th'

   >>> Fretboard.guitar().chord("G")
   Fingering(E=3, A=2, D=0, G=0, B=0, e=3)

Melodies render to ASCII tablature too — write a line, print the tab,
hand it to a guitarist. See :doc:`guide/fretboard` for fingerings and
scale diagrams, and :doc:`guide/nashville-blues-tabs` for Nashville
number charts, blues scales, and full-song tabs.

Composition
-----------

When you're ready to make noise, the composition layer adds drums,
synths, effects, and multi-part arrangements. Sketch an idea, hear
it through your speakers, export MIDI, finish in your DAW:

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

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="_static/audio/quickstart.wav" type="audio/wav"></audio>

Everything you hear is synthesized from math — 56 waveforms, 83
instrument presets, 100 drum patterns, and a full effects rack
(reverb, delay, chorus, distortion, sidechain, automation). When it
sounds right, take it anywhere: WAV, MIDI, ABC notation, MusicXML,
LilyPond, or guitar tab.

Or hear a randomly generated track from the command line — different
every time::

   $ uv run pytheory demo

.. toctree::
   :maxdepth: 2
   :caption: Start Here

   guide/quickstart
   guide/theory

.. toctree::
   :maxdepth: 2
   :caption: Making Music

   guide/sequencing
   guide/synths
   guide/effects
   guide/drums
   guide/playback
   guide/listening
   guide/live

.. toctree::
   :maxdepth: 2
   :caption: Guitar & Strings

   guide/fretboard
   guide/nashville-blues-tabs

.. toctree::
   :maxdepth: 2
   :caption: Theory Reference

   guide/tones
   guide/scales
   guide/chords
   guide/systems

.. toctree::
   :maxdepth: 2
   :caption: Tools

   guide/repl
   guide/cli
   guide/cookbook

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/tones
   api/scales
   api/chords
   api/charts
   api/rhythm
   api/play
   api/audio
   api/tuner
   api/live
   api/systems

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog.md

Music is math that makes you feel something. PyTheory gives you the
math. What you feel is up to you.
