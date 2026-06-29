Instruments and Fingerings
==========================

The :class:`~pytheory.chords.Fretboard` class models any stringed
instrument and generates chord fingerings. PyTheory includes **25
instrument presets** spanning Western, Asian, Middle Eastern, Latin
American, and Russian traditions.

How It Works
------------

Each `fret <https://en.wikipedia.org/wiki/Fret>`_ on a stringed
instrument raises the pitch by exactly **one semitone**. The open
string is fret 0; fret 1 is one semitone up, and so on. Even fretless
instruments (violin, oud, erhu) can be modeled this way — the "fret"
positions are just semitone steps along the fingerboard.

Guitars
-------

`Standard guitar tuning <https://en.wikipedia.org/wiki/Guitar_tunings>`_::

    String 6: E2  (lowest)
    String 5: A2
    String 4: D3
    String 3: G3
    String 2: B3
    String 1: E4  (highest)

This tuning uses intervals of a perfect 4th (5 semitones) between most
strings, except between G and B which is a major 3rd (4 semitones).

.. note::

   Since **v0.43.0**, fingerings and string lists read **low to high**
   (lowest-pitched string first) by default — matching how chord
   diagrams and tab are conventionally written. To get the pre-0.43
   high-to-low order, pass ``high_to_low=True`` to any fretboard
   constructor, e.g. ``Fretboard.guitar(high_to_low=True)``. A custom
   tuning tuple and manual ``fingering()`` positions are likewise read
   in the board's orientation.

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> guitar  = Fretboard.guitar()                # Standard EADGBE
   >>> twelve  = Fretboard.twelve_string()          # 12-string (6 doubled courses)
   >>> bass    = Fretboard.bass()                  # Standard 4-string EADG
   >>> bass5   = Fretboard.bass(five_string=True)  # 5-string with low B

**Alternate tunings** — 7 built-in presets (plus ``standard``):

.. code-block:: pycon

   >>> Fretboard.guitar("drop d")          # DADGBE — heavy riffs, metal
   >>> Fretboard.guitar("open g")          # DGDGBD — slide guitar, Keith Richards
   >>> Fretboard.guitar("open d")          # DADF#AD — slide, folk
   >>> Fretboard.guitar("open e")          # EBEG#BE — slide blues
   >>> Fretboard.guitar("open a")          # EAEAC#E — slide
   >>> Fretboard.guitar("dadgad")          # DADGAD — Celtic, fingerstyle
   >>> Fretboard.guitar("half step down")  # Eb standard — Hendrix, SRV

   >>> # Custom tuning with any notes
   >>> Fretboard.guitar(("C4", "G3", "C3", "G2", "C2", "G1"))

**Capo** — a `capo <https://en.wikipedia.org/wiki/Capo>`_ raises all
strings by a number of frets, letting you play open chord shapes in
higher keys:

.. code-block:: pycon

   >>> # Capo on fret 2 — open G shape now sounds as A major
   >>> fb = Fretboard.guitar(capo=2)

   >>> # Or apply a capo to an existing fretboard
   >>> fb = Fretboard.guitar()
   >>> fb_capo3 = fb.capo(3)

The Mandolin Family
-------------------

The `mandolin family <https://en.wikipedia.org/wiki/Mandolin_family>`_
mirrors the `violin family <https://en.wikipedia.org/wiki/Violin_family>`_
— all tuned in perfect fifths, with each member a fifth or octave
lower than the last:

.. code-block:: pycon

   >>> Fretboard.mandolin()          # E5 A4 D4 G3  — soprano (= violin)
   >>> Fretboard.mandola()           # A4 D4 G3 C3  — alto (= viola)
   >>> Fretboard.octave_mandolin()   # E4 A3 D3 G2  — tenor (octave below mandolin)
   >>> Fretboard.mandocello()        # A3 D3 G2 C2  — bass (= cello)

The mandolin's doubled courses (pairs of strings) create a natural
chorus effect. The `octave mandolin <https://en.wikipedia.org/wiki/Octave_mandolin>`_
is popular in Irish and Celtic folk music.

The Bowed String Family
-----------------------

The orchestral `string family <https://en.wikipedia.org/wiki/String_section>`_
is tuned in perfect fifths (except the double bass, which uses fourths):

.. code-block:: pycon

   >>> Fretboard.violin()       # E5 A4 D4 G3  — soprano
   >>> Fretboard.viola()        # A4 D4 G3 C3  — alto (5th below violin)
   >>> Fretboard.cello()        # A3 D3 G2 C2  — tenor/bass (octave below viola)
   >>> Fretboard.double_bass()  # G2 D2 A1 E1  — bass (tuned in 4ths!)

Bowed strings have no frets — the player can produce any pitch along
the fingerboard, enabling continuous
`vibrato <https://en.wikipedia.org/wiki/Vibrato>`_ and microtonal
inflections not possible on fretted instruments.

The `erhu <https://en.wikipedia.org/wiki/Erhu>`_ — a 2-stringed Chinese
bowed instrument with a hauntingly vocal quality:

.. code-block:: pycon

   >>> Fretboard.erhu()         # A4 D4  — tuned a 5th apart, no fingerboard

Plucked Strings
---------------

.. code-block:: pycon

   >>> Fretboard.ukulele()         # A4 E4 C4 G4  — re-entrant tuning
   >>> Fretboard.banjo()           # open G (bluegrass) — 5th string is a high drone
   >>> Fretboard.banjo("open d")   # open D (clawhammer, old-time)
   >>> Fretboard.banjo("double c") # G C G C D (old-time)
   >>> Fretboard.harp()            # 47 strings, C1 to G7 (concert pedal harp)

The `banjo <https://en.wikipedia.org/wiki/Banjo>`_'s short 5th string
is a high drone — a defining feature of the instrument's sound.

The `harp <https://en.wikipedia.org/wiki/Harp>`_ has one string per
diatonic note across nearly 7 octaves. Pedals alter each note name
by up to two semitones across all octaves simultaneously.

World Instruments
-----------------

.. code-block:: pycon

   >>> # Middle Eastern
   >>> Fretboard.oud()          # C4 G3 D3 A2 G2 C2 — fretless, ancestor of the lute
   >>> Fretboard.sitar()        # 7 main strings — Indian classical

   >>> # East Asian
   >>> Fretboard.shamisen()     # C4 G3 C3 — 3-string Japanese, honchoshi tuning
   >>> Fretboard.pipa()         # D4 A3 E3 A2 — 4-string Chinese lute
   >>> Fretboard.erhu()         # A4 D4 — 2-string Chinese bowed

   >>> # European
   >>> Fretboard.bouzouki()     # D4 A3 D3 G2 — Irish (Celtic music)
   >>> Fretboard.bouzouki("greek")  # D4 A3 F3 C3 — Greek
   >>> Fretboard.lute()         # G4 D4 A3 F3 C3 G2 — Renaissance (6 courses)
   >>> Fretboard.balalaika()    # A4 E4 E4 — Russian (2 unison strings)

   >>> # Latin American
   >>> Fretboard.charango()     # E5 A4 E5 C5 G4 — Andean (re-entrant tuning)

   >>> # Steel guitar
   >>> Fretboard.pedal_steel()  # 10 strings, E9 Nashville — country music

The `oud <https://en.wikipedia.org/wiki/Oud>`_ is fretless, allowing
the quarter-tone inflections essential to
`maqam <https://en.wikipedia.org/wiki/Maqam>`_ performance. The
`sitar <https://en.wikipedia.org/wiki/Sitar>`_ has moveable frets and
sympathetic strings that resonate in harmony with the played notes.

Keyboards
---------

.. code-block:: pycon

   >>> Fretboard.keyboard()             # 88-key piano (A0 to C8)
   >>> Fretboard.keyboard(61, "C2")     # 61-key synth controller
   >>> Fretboard.keyboard(49, "C2")     # 49-key controller
   >>> Fretboard.keyboard(25, "C3")     # 25-key mini MIDI controller

While keyboards don't have strings or frets, they map naturally to a
sequence of tones. A full 88-key piano spans over 7 octaves — the
widest range of any standard acoustic instrument.

Getting Fingerings
------------------

Common chords come from a library of curated voicings, so ``fb.chord("C")``
returns the open shape a guitarist actually plays. Anything not in that
library — any symbol :func:`~pytheory.Chord.from_symbol` can parse, such
as ``"F#m7b5"`` or ``"Csus2"`` — is voiced automatically: PyTheory searches
the neck for its notes and scores each candidate hand position by

1. Preferring **open strings** (fret 0) — they ring freely
2. Preferring **ascending** fret patterns — easier hand position
3. Minimizing the number of **fingers needed**

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> f = fb.chord("C")
   >>> f
   Fingering(E=x, A=3, D=2, G=0, B=1, e=0)

   >>> f["A"]            # index by string name
   3
   >>> f[1]              # ...or by position (low to high)
   3

   >>> f.identify()
   'C major'

   >>> chord = f.to_chord()
   >>> chord.identify()
   'C major'

Subscripting the fretboard itself is shorthand for :meth:`~pytheory.Fretboard.chord`:

.. code-block:: pycon

   >>> fb["G"]
   Fingering(E=3, A=2, D=0, G=0, B=0, e=3)

Because uncharted symbols are voiced on the fly, you are not limited to
the common chords — any symbol that parses gets a computed shape:

.. code-block:: pycon

   >>> fb.chord("F#m7b5")
   Fingering(E=2, A=0, D=2, G=2, B=1, e=0)
   >>> fb.chord("Csus2")
   Fingering(E=x, A=3, D=0, G=0, B=3, e=3)
   >>> fb.chord("Gadd9")
   Fingering(E=3, A=0, D=0, G=0, B=0, e=3)
   >>> fb.chord("Cdim7")
   Fingering(E=8, A=0, D=7, G=8, B=7, e=8)

See :doc:`chords` for the chord vocabulary PyTheory understands.

You can also go from fret positions to chord identification:

.. code-block:: pycon

   >>> # "What chord am I playing?" (positions read low to high)
   >>> fb = Fretboard.guitar()
   >>> f = fb.fingering(0, 2, 2, 0, 0, 0)
   >>> f
   Fingering(E=0, A=2, D=2, G=0, B=0, e=0)
   >>> f.identify()
   'E minor'

Reading Fingerings
~~~~~~~~~~~~~~~~~~

Each position is labeled with its string name. Duplicate string names
are disambiguated — on a standard guitar, high E appears as ``e`` and
low E as ``E``. Strings read low to high (lowest first)::

    E|--x--    (muted — low E)
    A|--3--    (fret 3 — C)
    D|--2--    (fret 2 — E)
    G|--0--    (open — G)
    B|--1--    (fret 1 — C)
    e|--0--    (open — high E)

A value of ``x`` (``None``) means the string is muted (not played).

ASCII Tablature
~~~~~~~~~~~~~~~

For a more visual representation, use ``tab()``. Tablature follows the
standard convention — the highest-pitched string (high ``e``) is drawn on
top and the low ``E`` on the bottom, regardless of the board's data
orientation:

.. code-block:: pycon

   >>> print(fb.tab("C"))
   C major
   e|--0--
   B|--1--
   G|--0--
   D|--2--
   A|--3--
   E|--x--

Generating Full Charts
----------------------

Generate fingerings for every chord at once:

.. code-block:: pycon

   >>> fb = Fretboard.guitar()
   >>> chart = fb.chart()

   >>> chart["C"]
   Fingering(E=x, A=3, D=2, G=0, B=1, e=0)

   >>> # Works with any instrument
   >>> uke_chart = Fretboard.ukulele().chart()
   >>> mando_chart = Fretboard.mandolin().chart()

Scale Diagrams with Chord Highlighting
---------------------------------------

The ``scale_diagram()`` method renders an ASCII fretboard showing where
scale notes fall on each string:

.. code-block:: pycon

   >>> from pytheory import Fretboard, TonedScale, Chord

   >>> fb = Fretboard.guitar()
   >>> pentatonic = TonedScale(tonic="A4", system="blues")["minor pentatonic"]
   >>> print(fb.scale_diagram(pentatonic, frets=5))
       0   1   2   3   4   5
   E| E | - | - | G | - | A |
   A| A | - | - | C | - | D |
   D| D | - | E | - | - | G |
   G| G | - | A | - | - | C |
   B| - | C | - | D | - | E |
   E| E | - | - | G | - | A |

.. note::

   Pentatonic and blues scales live in the ``blues`` system, not the
   default ``western`` one — hence ``system="blues"`` above. See
   :doc:`scales` for the full catalogue.

Pass an optional ``chord`` argument to highlight chord tones in UPPERCASE
while scale-only tones appear in lowercase — a quick way to see your
target notes for soloing:

.. code-block:: pycon

   >>> am = Chord.from_symbol("Am")
   >>> print(fb.scale_diagram(pentatonic, frets=5, chord=am))
       0   1   2   3   4   5
   E| E | - | - | g | - | A |
   A| A | - | - | C | - | d |
   D| d | - | E | - | - | g |
   G| g | - | A | - | - | C |
   B| - | C | - | d | - | E |
   E| E | - | - | g | - | A |

Scalable Diagrams (SVG and PNG)
-------------------------------

ASCII tab is perfect in a terminal, but you can't drop it into a video, a
slide, or a worksheet. PyTheory renders the same fretboard data as clean,
scalable **SVG** — no extra dependencies. For PNG, install the optional
extra (``pip install pytheory[diagrams]``, which pulls in ``cairosvg``)
and pass ``fmt="png"`` or a ``.png`` path.

Every diagram method returns the SVG markup as a string, or — when you
give it a ``path`` — writes the file and returns the path.

Chord boxes
~~~~~~~~~~~

``tab_image()`` is the graphical counterpart of
:meth:`~pytheory.Fretboard.tab`: a vertical chord box like the ones in
songbooks, with open/muted markers, automatic barre detection, and the
root highlighted in red.

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()

   >>> # Write a chord box to a file...
   >>> fb.tab_image("Am", "Am.svg")
   'Am.svg'

   >>> # ...or get the SVG markup back as a string
   >>> svg = fb.tab_image("Am")
   >>> svg[:39]
   '<svg xmlns="http://www.w3.org/2000/svg"'

A :class:`~pytheory.charts.Fingering` can render itself the same way with
``to_svg()`` — handy when you built the voicing by hand. The barre in an
F major shape is detected automatically:

.. code-block:: pycon

   >>> fb.chord("F").to_svg(path="F.svg")
   'F.svg'

Scale shapes
~~~~~~~~~~~~

``scale_shapes()`` splits a scale into the positional boxes a player moves
between — for a pentatonic scale, the familiar five positions. Each is a
``ScaleShape`` you can render on its own:

.. code-block:: pycon

   >>> from pytheory import Fretboard, TonedScale

   >>> fb = Fretboard.guitar()
   >>> pentatonic = TonedScale(tonic="A4", system="blues")["minor pentatonic"]

   >>> shapes = fb.scale_shapes(pentatonic)
   >>> len(shapes)
   5
   >>> shapes[0]
   <ScaleShape A pos 1 frets 0-3>

   >>> shapes[0].to_svg(path="A_pent_pos1.svg")
   'A_pent_pos1.svg'

``scale_shape_image()`` is a shortcut for a single position (1-based):

.. code-block:: pycon

   >>> fb.scale_shape_image(pentatonic, 2, "A_pent_pos2.svg")
   'A_pent_pos2.svg'

Arpeggio maps
~~~~~~~~~~~~~

``arpeggio_diagram()`` maps every chord tone across the whole neck,
labelled by its role (``R``, ``3``, ``5``, ``7``…) with roots in red — for
practising where a chord's notes live. The chord can be a
:class:`~pytheory.Chord` or just a symbol string:

.. code-block:: pycon

   >>> Fretboard.guitar().arpeggio_diagram("Am", "Am_arp.svg")
   'Am_arp.svg'

Non-String Instruments
----------------------

Looking for drums and percussion? PyTheory also supports drum pattern
programming through the sequencing engine. See the :doc:`drums` guide
for drum kits, patterns, and fills.

Custom Instruments
------------------

Any instrument can be modeled with custom string tunings:

.. code-block:: pycon

   >>> from pytheory import Tone, Fretboard

   >>> # Baritone ukulele (DGBE — top 4 guitar strings, low to high)
   >>> bari_uke = Fretboard(tones=[
   ...     Tone.from_string("D3"),
   ...     Tone.from_string("G3"),
   ...     Tone.from_string("B3"),
   ...     Tone.from_string("E4"),
   ... ])

   >>> # Tres cubano (Cuban guitar, 3 doubled courses, low to high)
   >>> tres = Fretboard(tones=[
   ...     Tone.from_string("G3"),
   ...     Tone.from_string("B3"),
   ...     Tone.from_string("E4"),
   ... ])

If it has strings, you can model it. Define the tuning, and PyTheory handles the rest -- fingerings, charts, scale diagrams, all of it. Got a weird instrument or a custom tuning? That's what the ``Fretboard`` constructor is for.
