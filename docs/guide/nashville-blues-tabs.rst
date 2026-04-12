Nashville Numbers, Blues Scales, and Tablature
===============================================

Three tools that work together: the Nashville number system for writing
chord charts, blues scales for improvisation, and tablature for seeing
where to put your fingers. This guide covers all three and shows how
they connect.

The Nashville Number System
---------------------------

The `Nashville number system <https://en.wikipedia.org/wiki/Nashville_Number_System>`_
replaces chord names with Arabic numerals (1, 2, 3...) so that a chart
works in **any key**. It's the standard chart format in Nashville
recording studios — a session musician can read a number chart and
transpose on the fly without rewriting anything.

The idea is simple: each number refers to a **scale degree**. In any
major key, 1 is the tonic chord, 4 is the subdominant, 5 is the
dominant, and so on. The chord quality (major, minor, diminished) is
determined by the key — you don't need to write it out.

In C major::

    1 = C major      5 = G major
    2 = D minor      6 = A minor
    3 = E minor      7 = B diminished
    4 = F major

In G major::

    1 = G major      5 = D major
    2 = A minor      6 = E minor
    3 = B minor      7 = F# diminished
    4 = C major

Same numbers, different key, different chords — but the same harmonic
relationships.

Using Nashville Numbers in PyTheory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both :class:`~pytheory.scales.Key` and :class:`~pytheory.scales.TonedScale`
support the ``nashville()`` method:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> key = Key("C", "major")
   >>> [c.identify() for c in key.nashville(1, 4, 5, 1)]
   ['C major', 'F major', 'G major', 'C major']

   >>> # Same progression, different key — just change the Key
   >>> key_g = Key("G", "major")
   >>> [c.identify() for c in key_g.nashville(1, 4, 5, 1)]
   ['G major', 'C major', 'D major', 'G major']

Nashville numbers and Roman numerals produce the same result — they're
two notations for the same concept:

.. code-block:: pycon

   >>> key = Key("G", "major")
   >>> nash = [c.identify() for c in key.nashville(1, 5, 6, 4)]
   >>> roman = [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   >>> nash == roman
   True

Seventh Chords
~~~~~~~~~~~~~~

Suffix ``"7"`` to get seventh chords — essential for jazz and blues
charts:

.. code-block:: pycon

   >>> key = Key("C", "major")
   >>> [c.identify() for c in key.nashville("17", "47", "57")]
   ['C major 7th', 'F major 7th', 'G dominant 7th']

Nashville vs. Roman Numerals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When should you use which?

- **Nashville numbers** — faster to type, easier to read at a glance,
  standard in studio sessions. Use ``key.nashville(1, 4, 5, 1)``.
- **Roman numerals** — encode chord quality (uppercase = major,
  lowercase = minor), standard in theory textbooks. Use
  ``key.progression("I", "IV", "V", "I")``.

Both are fully supported. Use whichever fits your workflow.

Blues Scales
------------

The `blues scale <https://en.wikipedia.org/wiki/Blues_scale>`_ is a
six-note scale built from the minor pentatonic plus one chromatic
passing tone — the **blue note** (flat 5th). That single added note
gives the blues its tension and character.

The blues system in PyTheory includes several related scales:

====================  =====  ==================================
Scale                 Notes  Character
====================  =====  ==================================
minor pentatonic      5      Foundation of rock and blues soloing
major pentatonic      5      Bright, country, pop
blues                 6      Minor pentatonic + blue note (b5)
major blues           6      Major pentatonic + blue note (b3)
dominant              7      Mixolydian — dominant 7th sound
minor                 7      Dorian-like — minor with natural 6th
====================  =====  ==================================

Building Blues Scales
~~~~~~~~~~~~~~~~~~~~~

Use ``system="blues"`` when creating a :class:`~pytheory.scales.TonedScale`:

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4", system="blues")

   >>> c["minor pentatonic"].note_names
   ['C', 'Eb', 'F', 'G', 'Bb', 'C']

   >>> c["blues"].note_names
   ['C', 'Eb', 'F', 'Gb', 'G', 'Bb', 'C']

   >>> c["major pentatonic"].note_names
   ['C', 'D', 'E', 'G', 'A', 'C']

   >>> c["major blues"].note_names
   ['C', 'D', 'Eb', 'E', 'G', 'A', 'C']

The Anatomy of a Blues Scale
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The blues scale in C::

    C  Eb  F  Gb  G  Bb  C
    1  b3  4  b5  5  b7  8

    Root ──┐
           ├── minor 3rd (3 semitones)
           ├── perfect 4th (5 semitones)
           ├── diminished 5th (6 semitones) ← the "blue note"
           ├── perfect 5th (7 semitones)
           ├── minor 7th (10 semitones)
           └── octave (12 semitones)

The blue note (Gb/F#) sits between the 4th and 5th — a dissonant,
unstable pitch that resolves up or down. It's what makes blues sound
like blues.

The 12-Bar Blues
~~~~~~~~~~~~~~~~

The `12-bar blues <https://en.wikipedia.org/wiki/Twelve-bar_blues>`_ is
the most important chord progression in American music. It uses the
Nashville numbers 1, 4, and 5::

    | 1  | 1  | 1  | 1  |
    | 4  | 4  | 1  | 1  |
    | 5  | 4  | 1  | 5  |

In the key of A:

.. code-block:: pycon

   >>> from pytheory import Key

   >>> key = Key("A", "major")
   >>> bars = key.nashville(1,1,1,1, 4,4,1,1, 5,4,1,5)
   >>> [c.identify() for c in bars]
   ['A major', 'A major', 'A major', 'A major', 'D major', 'D major', 'A major', 'A major', 'E major', 'D major', 'A major', 'E major']

For an authentic blues sound, use dominant 7th chords:

.. code-block:: pycon

   >>> bars_7 = key.nashville("17","17","17","17", "47","47","17","17", "57","47","17","57")
   >>> [c.identify() for c in bars_7]
   ['A major 7th', 'A major 7th', 'A major 7th', 'A major 7th', 'D major 7th', 'D major 7th', 'A major 7th', 'A major 7th', 'E dominant 7th', 'D major 7th', 'A major 7th', 'E dominant 7th']

Or use the built-in named progression:

.. code-block:: pycon

   >>> key = Key("A", "major")
   >>> blues = key.common_progressions()["12-bar blues"]
   >>> [c.identify() for c in blues]
   ['A major', 'A major', 'A major', 'A major', 'D major', 'D major', 'A major', 'A major', 'E major', 'D major', 'A major', 'E major']

Blues Scale on the Fretboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Visualize the blues scale on guitar to see the patterns:

.. code-block:: pycon

   >>> from pytheory import Fretboard, TonedScale

   >>> fb = Fretboard.guitar()
   >>> blues = TonedScale(tonic="A4", system="blues")["blues"]
   >>> print(fb.scale_diagram(blues, frets=12))
       0   1   2   3   4   5   6   7   8   9  10  11  12
   E| - | - | - | - | - | A | - | - | C | - | D | Eb| E |
   B| - | - | - | D | Eb| E | - | - | - | - | A | - | - |
   G| - | - | A | - | - | C | - | D | Eb| E | - | - | - |
   D| - | - | - | - | A | - | - | C | - | D | Eb| E | - |
   A| A | - | - | C | - | D | Eb| E | - | - | - | - | A |
   E| - | - | - | - | - | A | - | - | C | - | D | Eb| E |

The minor pentatonic (same scale without the Eb) is the most-played
scale in rock guitar. Add the blue note and you have the full blues
scale — the same shapes, one extra fret.

Tablature
---------

`Tablature <https://en.wikipedia.org/wiki/Tablature>`_ (tab) shows
**where to put your fingers** rather than what notes to play. Each line
represents a string; numbers indicate fret positions. PyTheory generates
tabs at three levels:

1. **Chord tabs** — single chord fingerings
2. **Part tabs** — full melody/sequence notation
3. **Score tabs** — extract a part from a multi-part score

Chord Tablature
~~~~~~~~~~~~~~~~

Get the tab for any chord on any instrument:

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> print(fb.tab("C"))
   C major
   e|--0--
   B|--1--
   G|--0--
   D|--2--
   A|--3--
   E|--x--

   >>> print(fb.tab("Am"))
   A minor
   e|--0--
   B|--1--
   G|--2--
   D|--2--
   A|--0--
   E|--x--

   >>> print(fb.tab("E7"))
   E dominant 7th
   e|--0--
   B|--0--
   G|--1--
   D|--0--
   A|--2--
   E|--0--

Works with any instrument:

.. code-block:: pycon

   >>> uke = Fretboard.ukulele()
   >>> print(uke.tab("C"))
   C major
   A|--3--
   E|--0--
   C|--0--
   G|--0--

Reading Tab Notation
~~~~~~~~~~~~~~~~~~~~~

::

    e|--0--    ← open string (don't fret, just pluck)
    B|--1--    ← press fret 1
    G|--0--    ← open string
    D|--2--    ← press fret 2
    A|--3--    ← press fret 3
    E|--x--    ← muted (don't play this string)

- Each line is a string (highest pitch at top, lowest at bottom)
- Numbers are fret positions (0 = open, 1-24 = fretted)
- ``x`` means the string is muted / not played
- ``|`` marks measure boundaries in sequence tabs

Part Tablature
~~~~~~~~~~~~~~~

Generate tab from a composed part using ``to_tab()``:

.. code-block:: python

   from pytheory import Score, Key, Duration

   score = Score("4/4", bpm=120)
   lead = score.part("lead", synth="saw")

   # A simple blues lick
   for note in ["A4", "C5", "D5", "Eb5", "E5", "G5", "A5"]:
       lead.add(note, Duration.QUARTER)

   print(lead.to_tab())

This outputs standard ASCII tab with measure lines, mapping each note
to the most playable string and fret position.

Tuning Options
~~~~~~~~~~~~~~

The ``to_tab()`` method supports multiple tunings:

.. code-block:: python

   # Standard guitar (default)
   lead.to_tab(tuning="guitar")

   # 4-string bass
   lead.to_tab(tuning="bass")

   # Drop D guitar
   lead.to_tab(tuning="drop_d")

   # Any Fretboard object — use any of the 25+ instrument presets
   from pytheory import Fretboard
   lead.to_tab(tuning=Fretboard.mandolin())
   lead.to_tab(tuning=Fretboard.banjo())

   # Custom tuning as MIDI note numbers (low string first)
   lead.to_tab(tuning=[40, 45, 50, 55, 59, 64])

Score Tablature
~~~~~~~~~~~~~~~~

Extract tab from a multi-part score:

.. code-block:: python

   score = Score("4/4", bpm=120)
   rhythm = score.part("rhythm", synth="saw")
   lead = score.part("lead", synth="triangle")
   bass = score.part("bass", synth="sine")

   # ... compose parts ...

   # Tab the lead part
   print(score.to_tab("lead"))

   # Tab the first non-drum part (if no name given)
   print(score.to_tab())

   # Bass tab
   print(score.to_tab("bass", tuning="bass"))

Putting It All Together
-----------------------

Here's a complete example that uses all three features — Nashville
numbers for the chord progression, the blues scale for the melody, and
tab export to see the fingering:

.. code-block:: python

   from pytheory import Key, TonedScale, Fretboard, Score, Duration

   # 1. Nashville numbers for the progression
   key = Key("A", "major")
   chords = key.nashville(1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5)

   # 2. Blues scale for the melody
   blues = TonedScale(tonic="A4", system="blues")["blues"]

   # 3. Compose a score
   score = Score("4/4", bpm=120)
   rhythm = score.part("rhythm", synth="saw", envelope="pad")
   lead = score.part("lead", synth="triangle", envelope="pluck")

   for chord in chords:
       rhythm.add(chord, Duration.WHOLE)

   for note_name in blues.note_names[:-1]:  # walk up the scale
       lead.add(f"{note_name}4", Duration.HALF)

   # 4. See it as tablature
   print(lead.to_tab())

   # 5. See the scale on the fretboard
   fb = Fretboard.guitar()
   print(fb.scale_diagram(blues, frets=12))

Nashville numbers tell you *what chords to play*. The blues scale tells you *what notes to solo with*. Tablature tells you *where to put your fingers*. Together, they're everything you need to play the blues.
