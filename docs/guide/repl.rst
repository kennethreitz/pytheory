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
     iidim   B diminished
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

Build progressions. Roman numerals are **case-sensitive** — an uppercase
numeral is a major triad on that scale degree, a lowercase one is minor — so
the same numerals give you different chords depending on case::

   pytheory> prog I V vi IV
     A → E → Fm → D

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

Other musical systems — Indian, Arabic, Japanese, blues, gamelan — each with
their own scales and note names. The third line shows the notes of the first
scale listed::

   pytheory> system indian
     system: indian
     scales: chromatic, bilawal, khamaj, kafi, ...
     chromatic: Sa komal Re Re komal Ga Ga Ma tivra Ma Pa komal Dha Dha komal Ni Ni Sa

   pytheory> system arabic
     system: arabic
     scales: chromatic, ajam, nahawand, kurd, hijaz, ...
     chromatic: Do Reb Re Mib Mi Fa Fa# Sol Solb La Sib Si Do

These are 12-TET approximations. For true quarter-tone maqamat and
shruti-based ragas, see :doc:`systems`.

Guitar::

   pytheory> fingering Am
     Am
     E|--x--
     A|--0--
     D|--2--
     G|--2--
     B|--1--
     e|--0--

   pytheory> diagram minor 5
       0   1   2   3   4   5
   E| E | F | - | G | - | A |
   ...

Tuning
------

By default the REPL is 12-tone equal temperament tuned to A4 = 440 Hz. Change
either with ``temperament`` and ``reference``::

   pytheory> temperament just
     temperament=just

   pytheory> reference 432
     reference=432.0 Hz

   pytheory> temperament
     temperament=just  reference=432.0 Hz
     available: equal, pythagorean, meantone, just

The temperaments are ``equal``, ``pythagorean``, ``meantone``, and ``just``.
Both settings show up in ``status`` and carry through to playback and export.

Composition Commands
--------------------

When you're ready to make sound, set the groove, then add drums and parts.

Tempo, meter, and feel::

   pytheory> bpm 140
     bpm=140

   pytheory> time 3/4
     time=3/4

   pytheory> swing 0.5
     swing=0.5

``time`` rebuilds the score around the new signature; ``swing`` (0–1) pushes
the off-beats into a shuffle.

Drums::

   pytheory> drums bossa nova
     score.drums("bossa nova", repeats=4)

   pytheory> drums
     (lists all 100 presets)

Parts — each with its own voice. Build one from a raw synth waveform plus an
envelope, or from a ready-made instrument preset::

   pytheory> part lead saw pluck
     score.part("lead", synth="saw", envelope="pluck")

   pytheory> part chords fm pad
     score.part("chords", synth="fm", envelope="pad")

   pytheory> part bass sine pluck
     score.part("bass", synth="sine", envelope="pluck")

   pytheory> part keys piano
     score.part("keys", instrument="piano")

   pytheory> part strings instrument violin
     score.part("strings", instrument="violin")

A bare instrument name (``part keys piano``) and the explicit ``instrument``
keyword do the same thing. List every preset with ``instruments``::

   pytheory> instruments
     piano                 electric_piano        organ
     harpsichord           celesta               music_box
     violin                viola                 cello
     ...

List the parts you've made — the arrow (``←``) marks the active one, and you
switch with ``part <name>``::

   pytheory> part
     lead: synth=saw envelope=pluck vol=0.5 ←
     chords: synth=fm envelope=pad vol=0.5
     bass: synth=sine envelope=pluck vol=0.5

See :doc:`synths` for what each preset sounds like.

Add notes, chords, and arpeggios to the active part::

   pytheory> add C4 1
     .add("C4", 1.0)

   pytheory> add Am 4
     .add(Chord.from_symbol("Am"), 4.0)

   pytheory> add E4 0.67 110
     .add("E4", 0.67, velocity=110)

   pytheory> rest 2
     .rest(2.0)

   pytheory> arp Am updown 2 2
     .arpeggio("Am", pattern="updown", bars=2.0, octaves=2)

   pytheory> prog i iv V i
     Am → Dm → E → Am

``add`` reads its first argument as a chord symbol before falling back to a
single note, so a few octave numbers collide with chord qualities — ``add C5``
makes a C power chord, not the note C5. Stick to octaves like 3 and 4 (or
spell the chord out, e.g. ``add Cmaj7 4``) and you'll never trip on it.

Expressive performance — rolls and pitch bends::

   pytheory> roll C3 4
     .roll("C3", 4.0, velocity_start=40, velocity_end=100)

   pytheory> roll C3 4 30 110
     .roll("C3", 4.0, velocity_start=30, velocity_end=110)

   pytheory> bend C5 1 2
     .add("C5", 1.0, bend=2.0, bend_type="smooth")

   pytheory> bend C5 1 -1
     .add("C5", 1.0, bend=-1.0, bend_type="smooth")

``roll`` repeats a note with a velocity ramp — perfect for timpani swells or
tremolo. ``bend`` adds a note that slides ``<semitones>`` up (positive) or
down (negative), with an optional ``smooth``, ``linear``, or ``late`` curve.

There's also a ``strum`` command, but it needs a part with a fretboard
attached, which today you set up in Python via ``score.part(..., fretboard=...)``.
On a plain synth or instrument part it just reminds you::

   pytheory> strum Am 2 down
     error: Cannot strum without a fretboard. Set fretboard= when creating the part.

See :doc:`fretboard` for fretboard-driven strumming and tab.

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
     .set(lowpass=3000.0)

LFO modulation::

   pytheory> lfo lowpass 0.5 400 3000 8 sine
     .lfo("lowpass", rate=0.5, min=400.0, max=3000.0, bars=8.0, shape="sine")

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
     temperament=equal  reference=440.0 Hz
     drums=bossa nova  parts=[lead, chords, bass]  active=lead

   pytheory> clear
     cleared (C major, 120 bpm)

Where the REPL Stops
--------------------

The REPL is a sketchpad — it covers the commands above and nothing more.
Several of PyTheory's bigger features have no REPL command and live in the
Python API and CLI instead:

- Notation export to LilyPond, MusicXML, and ABC — see :doc:`playback`.
- Harmonic analysis (Roman numerals, cadences, reharmonization) — see :doc:`theory`.
- Lyrics and the full effects rack — see :doc:`sequencing` and :doc:`effects`.
- Quarter-tone maqamat and shruti-based ragas — see :doc:`systems`.
- Audio transcription with ``Score.from_wav`` — see :doc:`listening`.
- Live performance and Ableton Link — see :doc:`live`.

From the REPL itself you can render audio (``render``) and save MIDI
(``save_midi``); reach for a script when you need the rest.

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
