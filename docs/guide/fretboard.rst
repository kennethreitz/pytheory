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

`Standard guitar tuning <https://en.wikipedia.org/wiki/Guitar_tunings>`_
(high to low)::

    String 1: E4  (highest)
    String 2: B3
    String 3: G3
    String 4: D3
    String 5: A2
    String 6: E2  (lowest)

This tuning uses intervals of a perfect 4th (5 semitones) between most
strings, except between G and B which is a major 3rd (4 semitones).

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> guitar  = Fretboard.guitar()                # Standard EADGBE
   >>> twelve  = Fretboard.twelve_string()          # 12-string (6 doubled courses)
   >>> bass    = Fretboard.bass()                  # Standard 4-string EADG
   >>> bass5   = Fretboard.bass(five_string=True)  # 5-string with low B

**Alternate tunings** — 8 built-in presets:

.. code-block:: pycon

   >>> Fretboard.guitar("drop d")          # DADGBE — heavy riffs, metal
   >>> Fretboard.guitar("open g")          # DGDGBD — slide guitar, Keith Richards
   >>> Fretboard.guitar("open d")          # DADF#AD — slide, folk
   >>> Fretboard.guitar("open e")          # EBEG#BE — slide blues
   >>> Fretboard.guitar("open a")          # EAC#EAE
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

   >>> Fretboard.ukulele()      # A4 E4 C4 G4  — re-entrant tuning
   >>> Fretboard.banjo()        # Open G (bluegrass, 5th string is high drone)
   >>> Fretboard.banjo("open d")  # Open D (clawhammer, old-time)
   >>> Fretboard.harp()         # 47 strings, C1 to G7 (concert pedal harp)

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

The fingering algorithm finds the most playable voicing for any chord
on any instrument. It scores each possibility by:

1. Preferring **open strings** (fret 0) — they ring freely
2. Preferring **ascending** fret patterns — easier hand position
3. Minimizing the number of **fingers needed**

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> f = fb.chord("C")
   >>> f
   Fingering(e=0, B=1, G=0, D=2, A=3, E=x)

   >>> f['A']
   3
   >>> f[1]
   1

   >>> f.identify()
   'C major'

   >>> chord = f.to_chord()
   >>> chord.identify()
   'C major'

You can also go from fret positions to chord identification:

.. code-block:: pycon

   >>> # "What chord am I playing?"
   >>> fb = Fretboard.guitar()
   >>> f = fb.fingering(0, 0, 0, 2, 2, 0)
   >>> f
   Fingering(e=0, B=0, G=0, D=2, A=2, E=0)
   >>> f.identify()
   'E minor'

Reading Fingerings
~~~~~~~~~~~~~~~~~~

Each position is labeled with its string name. Duplicate string names
are disambiguated — on a standard guitar, high E appears as ``e`` and
low E as ``E``::

    e|--0--    (open — E)
    B|--1--    (fret 1 — C)
    G|--0--    (open — G)
    D|--2--    (fret 2 — E)
    A|--3--    (fret 3 — C)
    E|--x--    (muted)

A value of ``x`` (``None``) means the string is muted (not played).

ASCII Tablature
~~~~~~~~~~~~~~~

For a more visual representation, use ``tab()``:

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
   Fingering(e=0, B=1, G=0, D=2, A=3, E=x)

   >>> # Works with any instrument
   >>> uke_chart = Fretboard.ukulele().chart()
   >>> mando_chart = Fretboard.mandolin().chart()

Scale Diagrams with Chord Highlighting
---------------------------------------

The ``scale_diagram()`` method renders an ASCII fretboard showing where
scale notes fall on each string. Pass an optional ``chord`` argument to
highlight chord tones in UPPERCASE while scale-only tones appear in
lowercase — a quick way to visualize target notes for soloing:

.. code-block:: pycon

   >>> from pytheory import Fretboard, TonedScale, Chord

   >>> fb = Fretboard.guitar()
   >>> pentatonic = TonedScale(tonic="A4")["minor pentatonic"]
   >>> print(fb.scale_diagram(pentatonic, frets=5))

   >>> # Highlight Am chord tones within the scale:
   >>> am = Chord.from_symbol("Am")
   >>> print(fb.scale_diagram(pentatonic, frets=5, chord=am))

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

   >>> # Baritone ukulele (DGBE — top 4 guitar strings)
   >>> bari_uke = Fretboard(tones=[
   ...     Tone.from_string("E4"),
   ...     Tone.from_string("B3"),
   ...     Tone.from_string("G3"),
   ...     Tone.from_string("D3"),
   ... ])

   >>> # Tres cubano (Cuban guitar, 3 doubled courses)
   >>> tres = Fretboard(tones=[
   ...     Tone.from_string("E4"),
   ...     Tone.from_string("B3"),
   ...     Tone.from_string("G3"),
   ... ])

If it has strings, you can model it. Define the tuning, and PyTheory handles the rest -- fingerings, charts, scale diagrams, all of it. Got a weird instrument or a custom tuning? That's what the ``Fretboard`` constructor is for.
