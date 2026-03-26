Interactive REPL
================

PyTheory includes an interactive scratchpad for exploring music theory,
hearing ideas instantly, and building arrangements — all without writing
a Python script.

::

   $ pytheory repl

The REPL is two things at once: a **theory calculator** (what chords
are in this key? what's the interval between these notes?) and a
**composition sketchpad** (add drums, layer parts, tweak effects, hear
it, export MIDI). Use whichever side you need.

Getting Started
---------------

The welcome screen tells you everything you need::

   ♫  PyTheory REPL
   ════════════════════════════════════════

   try:  key Am          — set a key
         chords          — see its chords
         prog I V vi IV  — hear a progression
         drums bossa nova
         play_score      — hear it all

   help for all commands, quit to exit

Type those five things in order and you'll have music playing in
30 seconds.

The Prompt
----------

The prompt shows your current state — key, tempo, drums, active part,
and effects. It starts compact and grows as you add context::

   pytheory[key=C | bpm=120]>

   pytheory[key=Am | bpm=140]>

   pytheory[key=Am | bpm=140 | drums=bossa nova]>

   pytheory[key=Am | bpm=140 | drums=bossa nova | →lead(saw)]>

When it gets long, it stacks into two lines::

     key=Am | bpm=140 | drums=bossa nova | →lead(saw) rev=0.3 lp=2000
   ♫>

You always know where you are.

Theory Commands
---------------

These work without any audio setup. Pure theory exploration.

Set a key and explore it::

   pytheory> key Am
     A minor: A B C D E F G A

   pytheory> chords
     i       A minor
     ii°     B diminished
     III     C major
     iv      D minor
     v       E minor
     VI      F major
     VII     G major

   pytheory> modes
     ionian        A B C# D E F# G# A
     dorian        A B C D E F# G A
     phrygian      A Bb C D E F G A
     ...

   pytheory> scales
     major                 A B C# D E F# G# A
     minor                 A B C D E F G A
     harmonic minor        A B C D E F G# A
     ...

Build progressions::

   pytheory> prog I V vi IV
     Am → Em → F → Dm

   pytheory> progression i iv V i
     Am → Dm → E → Am

Explore intervals and chords::

   pytheory> interval C4 G4
     C4 → G4: perfect 5th
     7 semitones

   pytheory> identify C E G
     C major
     symbol: C

   pytheory> identify F#m7b5
     F# half-diminished 7th
     symbol: F#m7b5
     tones: F#4 A4 C5 E5
     intervals: [3, 3, 4]

Circle of fifths::

   pytheory> circle
     fifths:  A → E → B → F# → C# → G# → D# → A# → F → C → G → D
     fourths: A → D → G → C → F → A# → D# → G# → C# → F# → B → E

Other musical systems::

   pytheory> system indian
     system: indian
     scales: chromatic, bilawal, khamaj, kafi, ...

   pytheory> system arabic
     system: arabic
     scales: chromatic, ajam, nahawand, kurd, hijaz, ...

Guitar::

   pytheory> fingering Am
     Am
     E|--0--
     B|--1--
     G|--2--
     D|--2--
     A|--0--
     E|--x--

   pytheory> diagram minor 5
       0   1   2   3   4   5
   E| E | F | - | G | - | A |
   ...

Composition Commands
--------------------

When you're ready to make sound, add drums and parts.

Drums::

   pytheory> drums bossa nova
     score.drums("bossa nova", repeats=4)

   pytheory> drums
     (lists all 58 presets)

Parts — each with its own synth and envelope::

   pytheory> part lead saw pluck
     score.part("lead", synth="saw", envelope="pluck")

   pytheory> part chords fm pad
     score.part("chords", synth="fm", envelope="pad")

   pytheory> part bass sine pluck
     score.part("bass", synth="sine", envelope="pluck")

   pytheory> part
     lead: synth=saw envelope=pluck vol=0.5 ←
     chords: synth=fm envelope=pad vol=0.5
     bass: synth=sine envelope=pluck vol=0.5

The arrow (``←``) shows which part is active. Switch with
``part <name>``.

Add notes, chords, arpeggios::

   pytheory> add C5 1
     .add("C5", 1.0)

   pytheory> add Am 4
     .add(Chord.from_symbol("Am"), 4.0)

   pytheory> add E5 0.67 110
     .add("E5", 0.67, velocity=110)

   pytheory> rest 2
     .rest(2.0)

   pytheory> arp Am updown 2 2
     .arpeggio("Am", pattern="updown", bars=2.0, octaves=2)

   pytheory> prog i iv V i
     Am → Dm → E → Am

Effects
-------

Set effects on the active part — mirrors the Python API::

   pytheory> reverb 0.4
   pytheory> delay 0.3 0.375
   pytheory> lowpass 2000 3
   pytheory> dist 0.5
   pytheory> chorus 0.3
   pytheory> sidechain 0.8
   pytheory> humanize 0.3
   pytheory> legato on
   pytheory> glide 0.04
   pytheory> volume 0.4

Automation — change effects mid-song::

   pytheory> set lowpass 3000
     .set(lowpass=3000)

LFO modulation::

   pytheory> lfo lowpass 0.5 400 3000 8 sine
     .lfo("lowpass", rate=0.5, min=400, max=3000, bars=8, shape="sine")

Playback and Export
-------------------

Hear your work::

   pytheory> play_score
     ♫ play_score()

   pytheory> play_pattern
     ♫ play_pattern("bossa nova")

Export::

   pytheory> save_midi sketch.mid
     save_midi("sketch.mid")

   pytheory> render sketch.wav
     saved: sketch.wav

Session management::

   pytheory> show
     <Score 4/4 140bpm 3 parts 8.0 measures>
       lead: saw+pluck 32 notes reverb=0.3 delay=0.25 ←
       chords: fm+pad 8 notes
       drums: bossa nova (76 hits)

   pytheory> status
     key=A minor  bpm=140  swing=0.0
     drums=bossa nova  parts=[lead, chords, bass]  active=lead

   pytheory> clear
     cleared (C major, 120 bpm)

Complete Example
----------------

A full session from start to playable track::

   pytheory[key=C | bpm=120]> key Am
   pytheory[key=Am | bpm=120]> bpm 140
   pytheory[key=Am | bpm=140]> drums bossa nova
   pytheory[key=Am | bpm=140 | drums=bossa nova]> part chords fm pad
   pytheory[...| →chords(fm)]> prog i iv V i
   pytheory[...| →chords(fm)]> part lead saw pluck
   pytheory[...| →lead(saw)]> reverb 0.3
   pytheory[...| →lead(saw) rev=0.3]> delay 0.25
   pytheory[...| →lead(saw) rev=0.3 del=0.25]> arp Am updown 4 2
   pytheory[...]> play_score
     ♫ play_score()
   pytheory[...]> save_midi my_bossa.mid
     save_midi("my_bossa.mid")

Every command you typed maps 1:1 to the Python API. When you're
ready to move from the REPL to a script, the translation is direct.
