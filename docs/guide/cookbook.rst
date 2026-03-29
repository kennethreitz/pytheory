Cookbook
=======

Real-world recipes for common musical tasks. Each recipe is self-contained
and ready to paste into a Python session.

Analyze a Song
--------------

Take the chord progression from "Let It Be" (C G Am F) and analyze it
in the key of C major:

.. code-block:: pycon

   >>> from pytheory import Chord, Key

   >>> C  = Chord.from_name("C")
   >>> G  = Chord.from_name("G")
   >>> Am = Chord.from_name("Am")
   >>> F  = Chord.from_name("F")

   >>> [c.identify() for c in [C, G, Am, F]]
   ['C major', 'G major', 'A minor', 'F major']

   >>> [c.analyze("C") for c in [C, G, Am, F]]
   ['I', 'V', 'vi', 'IV']

   >>> key = Key("C", "major")
   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['C major', 'G major', 'A minor', 'F major']

Write a 12-Bar Blues
--------------------

The `12-bar blues <https://en.wikipedia.org/wiki/Twelve-bar_blues>`_ is
built from the I, IV, and V chords. Here it is in the key of A:

.. code-block:: pycon

   >>> from pytheory import Key, Chord

   >>> key = Key("A", "major")
   >>> [c.identify() for c in key.progression("I", "IV", "V")]
   ['A major', 'D major', 'E major']

   >>> bars = ["I","I","I","I", "IV","IV","I","I", "V","IV","I","V"]
   >>> [c.identify() for c in key.progression(*bars)]
   ['A major', 'A major', 'A major', 'A major', 'D major', 'D major', 'A major', 'A major', 'E major', 'D major', 'A major', 'E major']

   >>> Chord.from_name("A7").identify()
   'A dominant 7th'
   >>> Chord.from_name("D7").identify()
   'D dominant 7th'
   >>> Chord.from_name("E7").identify()
   'E dominant 7th'

Find Chords in a Key
--------------------

The :class:`~pytheory.scales.Key` class builds diatonic chords for any
key and lets you pull progressions by Roman numeral or Nashville number:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> key = Key("G", "major")
   >>> key.chords
   ['G major', 'A minor', 'B minor', 'C major', 'D major', 'E minor', 'F# diminished']

   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['G major', 'D major', 'E minor', 'C major']

   >>> [c.identify() for c in key.nashville(1, 5, 6, 4)]
   ['G major', 'D major', 'E minor', 'C major']

Compare Scales
--------------

Play the same tonic through different scales to hear how each mode
reshapes the palette. The western modes share the same notes but start
on different degrees; the blues scale adds the "blue note" (flat 5th):

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4")
   >>> c["major"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
   >>> c["minor"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb', 'C']
   >>> c["dorian"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb', 'C']
   >>> c["mixolydian"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'Bb', 'C']

   >>> c_blues = TonedScale(tonic="C4", system="blues")
   >>> c_blues["blues"].note_names
   ['C', 'Eb', 'F', 'Gb', 'G', 'Bb', 'C']

Guitar Chord Chart
------------------

Generate fingerings for guitar and ukulele with
:class:`~pytheory.tones.Fretboard`:

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> fb.chord("C")
   Fingering(e=0, B=1, G=0, D=2, A=3, E=x)
   >>> fb.chord("G")
   Fingering(e=3, B=0, G=0, D=0, A=2, E=3)
   >>> fb.chord("Am")
   Fingering(e=0, B=1, G=2, D=2, A=0, E=x)
   >>> fb.chord("D")
   Fingering(e=2, B=3, G=2, D=0, A=x, E=x)

   >>> uke = Fretboard.ukulele()
   >>> uke.chord("C")
   Fingering(A=3, E=0, C=0, G=0)
   >>> uke.chord("G")
   Fingering(A=2, E=3, C=2, G=0)

Explore an Interval
-------------------

Start from A4 (440 Hz) and walk through intervals, checking names and
frequency ratios:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> a4 = Tone.from_string("A4", system="western")
   >>> a4.frequency
   440.0

   >>> minor_3rd = a4 + 3
   >>> a4.interval_to(minor_3rd)
   'minor 3rd'

   >>> p5 = a4 + 7
   >>> a4.interval_to(p5)
   'perfect 5th'
   >>> round(p5.frequency / a4.frequency, 4)
   1.4983

   >>> octave = a4 + 12
   >>> a4.interval_to(octave)
   'octave'
   >>> round(octave.frequency / a4.frequency, 4)
   2.0

Walk the Circle of Fifths
-------------------------

The `circle of fifths <https://en.wikipedia.org/wiki/Circle_of_fifths>`_
is the backbone of Western harmony — each step adds one sharp or flat:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> c = Tone.from_string("C4", system="western")
   >>> [t.name for t in c.circle_of_fifths()]
   ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

   >>> g = Tone.from_string("G4", system="western")
   >>> [t.name for t in g.circle_of_fifths()]
   ['G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F', 'C']

Voice Leading Between Chords
-----------------------------

Find the smoothest path from one chord to the next — each voice moves
the minimum distance:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> c_maj = Chord.from_tones("C", "E", "G")
   >>> f_maj = Chord.from_tones("F", "A", "C")

   >>> for src, dst, motion in c_maj.voice_leading(f_maj):
   ...     print(f"{src} -> {dst}  ({motion:+d} semitones)")
   G4 -> A4  (+2 semitones)
   E4 -> F4  (+1 semitones)
   C4 -> C4  (+0 semitones)

Measure Harmonic Tension
------------------------

Quantify how much a chord "wants to resolve." Dominant 7ths have
the most tension — the tritone between the 3rd and 7th pulls toward
resolution:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> for name in ["C", "Am", "G7", "Cmaj7"]:
   ...     ch = Chord.from_name(name)
   ...     t = ch.tension
   ...     print(f"{name:6s} tension={t['score']:.2f}  tritones={t['tritones']}  dominant={t['has_dominant_function']}")
   C      tension=0.00  tritones=0  dominant=False
   Am     tension=0.00  tritones=0  dominant=False
   G7     tension=0.60  tritones=1  dominant=True
   Cmaj7  tension=0.15  tritones=0  dominant=False

Tritone Substitution (Jazz)
---------------------------

Replace any dominant chord with the one a
`tritone <https://en.wikipedia.org/wiki/Tritone_substitution>`_ away —
they share the same tritone interval:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> g7 = Chord.from_name("G7")
   >>> g7.tritone_sub().identify()
   'C# dominant 7th'

   >>> # ii-V-I with tritone sub:
   >>> #   Dm7 -> G7  -> Cmaj7   (standard)
   >>> #   Dm7 -> Db7 -> Cmaj7   (chromatic bass line!)

Key Signatures and Detection
-----------------------------

View the accidentals in any key, or detect the key from a set of notes:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> Key("C", "major").signature
   {'sharps': 0, 'flats': 0, 'accidentals': []}
   >>> Key("G", "major").signature
   {'sharps': 1, 'flats': 0, 'accidentals': ['F#']}
   >>> Key("D", "major").signature
   {'sharps': 2, 'flats': 0, 'accidentals': ['F#', 'C#']}

   >>> Key.detect("C", "E", "G", "A", "D")
   <Key C major>

Relative and Parallel Keys
--------------------------

Every major key has a **relative minor** (same notes, different root)
and a **parallel minor** (same root, different notes):

.. code-block:: pycon

   >>> from pytheory import Key

   >>> c = Key("C", "major")
   >>> c.relative
   'A minor'
   >>> c.parallel
   'C minor'

Borrowed Chords and Secondary Dominants
---------------------------------------

Add color by borrowing from the parallel key or building secondary
dominants that approach other scale degrees:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> c = Key("C", "major")

   >>> c.borrowed_chords[:4]
   ['C minor', 'D diminished', 'Eb major', 'F minor']

   >>> c.secondary_dominant(5).identify()
   'D dominant 7th'
   >>> c.secondary_dominant(2).identify()
   'A dominant 7th'
   >>> c.secondary_dominant(6).identify()
   'E dominant 7th'

The Overtone Series
-------------------

Every musical tone contains a stack of harmonics — the physics behind
why intervals sound consonant:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> a4 = Tone.from_string("A4", system="western")
   >>> [round(f, 1) for f in a4.overtones(6)]
   [440.0, 880.0, 1320.0, 1760.0, 2200.0, 2640.0]

   >>> # Harmonic 2 = octave (2:1)
   >>> # Harmonic 3 = perfect 5th + octave (3:1)
   >>> # Harmonic 5 = major 3rd + two octaves (5:1)

Enharmonic Spellings
--------------------

Find the alternate name for any sharp or flat:

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> for name in ["C#4", "D#4", "F#4", "G#4"]:
   ...     t = Tone.from_string(name, system="western")
   ...     print(f"{t.name} = {t.enharmonic}")
   C# = Db
   D# = Eb
   F# = Gb
   G# = Ab

World Scales
------------

Explore scales from Indian, Arabic, and Japanese traditions:

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> indian = TonedScale(tonic="Sa", system="indian")
   >>> indian["bhairav"].note_names
   ['Sa', 'komal Re', 'Ga', 'Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

   >>> arabic = TonedScale(tonic="Do", system="arabic")
   >>> arabic["hijaz"].note_names
   ['Do', 'Reb', 'Mi', 'Fa', 'Sol', 'Solb', 'Sib', 'Do']

   >>> japanese = TonedScale(tonic="C4", system="japanese")
   >>> japanese["hirajoshi"].note_names
   ['C', 'D', 'Eb', 'G', 'Ab', 'C']

Visualize a Scale on Guitar
----------------------------

See where the notes fall across the fretboard — E minor pentatonic,
the most-played scale in rock:

.. code-block:: pycon

   >>> from pytheory import Fretboard, Scale

   >>> fb = Fretboard.guitar()
   >>> pent = Scale(tonic="E4", system="blues")["minor pentatonic"]
   >>> print(fb.scale_diagram(pent, frets=12))
       0   1   2   3   4   5   6   7   8   9  10  11  12
   E| E | - | - | G | - | A | - | B | - | - | D | - | E |
   B| B | - | - | D | - | E | - | - | G | - | A | - | B |
   G| G | - | A | - | B | - | - | D | - | E | - | - | G |
   D| D | - | E | - | - | G | - | A | - | B | - | - | D |
   A| A | - | B | - | - | D | - | E | - | - | G | - | A |
   E| E | - | - | G | - | A | - | B | - | - | D | - | E |

Composition Recipes
-------------------

These recipes go beyond theory into actual music-making.

Acid House Track
~~~~~~~~~~~~~~~~

303-style acid with sidechain pump:

.. code-block:: python

   from pytheory import Score, Pattern, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=132)
   score.drums("house", repeats=8, fill="house", fill_every=8)

   pad = score.part(
       "pad",
       synth="supersaw",
       envelope="pad",
       reverb=0.4,
       chorus=0.3,
       sidechain=0.85,
   )
   acid = score.part(
       "acid",
       synth="saw",
       envelope="pad",
       legato=True,
       glide=0.03,
       distortion=0.8,
       distortion_drive=8.0,
       lowpass=1000,
       lowpass_q=5.0,
   )
   acid.lfo("lowpass", rate=0.5, min=600, max=2500, bars=8)

   for sym in ["Cm", "Fm", "Abm", "Gm"]:
       pad.add(Chord.from_symbol(sym), Duration.WHOLE)
       pad.add(Chord.from_symbol(sym), Duration.WHOLE)
       acid.arpeggio(sym, bars=2, pattern="up", octaves=2)

   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/acid_house.wav" type="audio/wav"></audio>

Dub Reggae with Delay Madness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sparse notes into infinite echo:

.. code-block:: python

   score = Score("4/4", bpm=72)
   score.drums("dub", repeats=8)

   melodica = score.part(
       "melodica",
       synth="triangle",
       envelope="pluck",
       delay=0.5,
       delay_time=0.66,
       delay_feedback=0.55,
       reverb=0.4,
       reverb_type="cathedral",
   )
   bass = score.part("bass", synth="sine", lowpass=400, lowpass_q=1.5)

   # Play almost nothing — let the delay do the work
   melodica.add("A4", 2).rest(6)
   melodica.add("E5", 1.5).rest(6.5)
   melodica.add("D5", 1).add("C5", 1).add("A4", 2).rest(4)

   for n in ["A1"] * 16:
       bass.add(n, Duration.HALF)

   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/dub_reggae.wav" type="audio/wav"></audio>

Jazz Ballad with Humanize
~~~~~~~~~~~~~~~~~~~~~~~~~~

The difference between a robot and a musician:

.. code-block:: python

   score = Score("4/4", bpm=72, swing=0.5)
   score.drums("jazz", repeats=8)

   rhodes = score.part(
       "rhodes",
       synth="fm",
       envelope="piano",
       reverb=0.4,
       reverb_type="plate",
       humanize=0.3,
   )
   lead = score.part(
       "lead",
       synth="triangle",
       envelope="strings",
       delay=0.25,
       reverb=0.3,
       humanize=0.35,
   )

   key = Key("Bb", "major")
   for chord in key.progression("I", "vi", "ii", "V") * 2:
       rhodes.add(chord, Duration.WHOLE)

   for n, d in [("D5", 1.5), ("F5", 0.5), ("Bb5", 2), (None, 4),
                ("A5", 1), ("G5", 1), ("F5", 2), (None, 4)]:
       lead.rest(d) if n is None else lead.add(n, d)

   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/jazz_ballad.wav" type="audio/wav"></audio>

Song with Sections
~~~~~~~~~~~~~~~~~~~

Define once, arrange freely:

.. code-block:: python

   score = Score("4/4", bpm=120)
   score.drums("rock", repeats=16, fill="rock", fill_every=4)

   chords = score.part("chords", synth="saw", envelope="pad")
   lead = score.part("lead", synth="triangle", envelope="pluck")

   score.section("verse")
   for sym in ["Am", "F", "C", "G"]:
       chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   lead.add("A4", 1).add("C5", 1).add("E5", 1).rest(1)
   lead.add("F5", 1).add("E5", 1).add("C5", 2)

   score.section("chorus")
   lead.set(reverb=0.4, lowpass=5000)
   for sym in ["F", "G", "Am", "C"]:
       chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   lead.add("C6", 2).add("A5", 1).add("G5", 1)
   lead.add("F5", 2).add("E5", 2)
   score.end_section()

   score.repeat("verse")
   score.repeat("chorus", times=2)

   play_score(score)
   score.save_midi("my_song.mid")

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/song_sections.wav" type="audio/wav"></audio>

Export Everything to MIDI
~~~~~~~~~~~~~~~~~~~~~~~~~~

The whole point — sketch fast, finish in your DAW:

.. code-block:: python

   # Any Score can be saved as MIDI
   score.save_midi("track.mid")

   # Simple progressions too
   from pytheory import save_midi
   chords = Key("C", "major").progression("I", "V", "vi", "IV")
   save_midi(chords, "pop.mid", t=500, bpm=120)

These are all starting points. Change the key, swap the chords, layer in your own ideas -- the best way to learn is to take something that works and make it yours.
