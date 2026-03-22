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

.. code-block:: python

   from pytheory import Fretboard

   guitar  = Fretboard.guitar()                # Standard EADGBE
   twelve  = Fretboard.twelve_string()          # 12-string (6 doubled courses)
   bass    = Fretboard.bass()                  # Standard 4-string EADG
   bass5   = Fretboard.bass(five_string=True)  # 5-string with low B

**Alternate tunings** — 8 built-in presets:

.. code-block:: python

   Fretboard.guitar("drop d")          # DADGBE — heavy riffs, metal
   Fretboard.guitar("open g")          # DGDGBD — slide guitar, Keith Richards
   Fretboard.guitar("open d")          # DADF#AD — slide, folk
   Fretboard.guitar("open e")          # EBEG#BE — slide blues
   Fretboard.guitar("open a")          # EAC#EAE
   Fretboard.guitar("dadgad")          # DADGAD — Celtic, fingerstyle
   Fretboard.guitar("half step down")  # Eb standard — Hendrix, SRV

   # Custom tuning with any notes
   Fretboard.guitar(("C4", "G3", "C3", "G2", "C2", "G1"))

The Mandolin Family
-------------------

The `mandolin family <https://en.wikipedia.org/wiki/Mandolin_family>`_
mirrors the `violin family <https://en.wikipedia.org/wiki/Violin_family>`_
— all tuned in perfect fifths, with each member a fifth or octave
lower than the last:

.. code-block:: python

   Fretboard.mandolin()          # E5 A4 D4 G3  — soprano (= violin)
   Fretboard.mandola()           # A4 D4 G3 C3  — alto (= viola)
   Fretboard.octave_mandolin()   # E4 A3 D3 G2  — tenor (octave below mandolin)
   Fretboard.mandocello()        # A3 D3 G2 C2  — bass (= cello)

The mandolin's doubled courses (pairs of strings) create a natural
chorus effect. The `octave mandolin <https://en.wikipedia.org/wiki/Octave_mandolin>`_
is popular in Irish and Celtic folk music.

The Bowed String Family
-----------------------

The orchestral `string family <https://en.wikipedia.org/wiki/String_section>`_
is tuned in perfect fifths (except the double bass, which uses fourths):

.. code-block:: python

   Fretboard.violin()       # E5 A4 D4 G3  — soprano
   Fretboard.viola()        # A4 D4 G3 C3  — alto (5th below violin)
   Fretboard.cello()        # A3 D3 G2 C2  — tenor/bass (octave below viola)
   Fretboard.double_bass()  # G2 D2 A1 E1  — bass (tuned in 4ths!)

Bowed strings have no frets — the player can produce any pitch along
the fingerboard, enabling continuous
`vibrato <https://en.wikipedia.org/wiki/Vibrato>`_ and microtonal
inflections not possible on fretted instruments.

The `erhu <https://en.wikipedia.org/wiki/Erhu>`_ — a 2-stringed Chinese
bowed instrument with a hauntingly vocal quality:

.. code-block:: python

   Fretboard.erhu()         # A4 D4  — tuned a 5th apart, no fingerboard

Plucked Strings
---------------

.. code-block:: python

   Fretboard.ukulele()      # A4 E4 C4 G4  — re-entrant tuning
   Fretboard.banjo()        # Open G (bluegrass, 5th string is high drone)
   Fretboard.banjo("open d")  # Open D (clawhammer, old-time)
   Fretboard.harp()         # 47 strings, C1 to G7 (concert pedal harp)

The `banjo <https://en.wikipedia.org/wiki/Banjo>`_'s short 5th string
is a high drone — a defining feature of the instrument's sound.

The `harp <https://en.wikipedia.org/wiki/Harp>`_ has one string per
diatonic note across nearly 7 octaves. Pedals alter each note name
by up to two semitones across all octaves simultaneously.

World Instruments
-----------------

.. code-block:: python

   # Middle Eastern
   Fretboard.oud()          # C4 G3 D3 A2 G2 C2 — fretless, ancestor of the lute
   Fretboard.sitar()        # 7 main strings — Indian classical

   # East Asian
   Fretboard.shamisen()     # C4 G3 C3 — 3-string Japanese, honchoshi tuning
   Fretboard.pipa()         # D4 A3 E3 A2 — 4-string Chinese lute
   Fretboard.erhu()         # A4 D4 — 2-string Chinese bowed

   # European
   Fretboard.bouzouki()     # D4 A3 D3 G2 — Irish (Celtic music)
   Fretboard.bouzouki("greek")  # D4 A3 F3 C3 — Greek
   Fretboard.lute()         # G4 D4 A3 F3 C3 G2 — Renaissance (6 courses)
   Fretboard.balalaika()    # A4 E4 E4 — Russian (2 unison strings)

   # Latin American
   Fretboard.charango()     # E5 A4 E5 C5 G4 — Andean (re-entrant tuning)

   # Steel guitar
   Fretboard.pedal_steel()  # 10 strings, E9 Nashville — country music

The `oud <https://en.wikipedia.org/wiki/Oud>`_ is fretless, allowing
the quarter-tone inflections essential to
`maqam <https://en.wikipedia.org/wiki/Maqam>`_ performance. The
`sitar <https://en.wikipedia.org/wiki/Sitar>`_ has moveable frets and
sympathetic strings that resonate in harmony with the played notes.

Keyboards
---------

.. code-block:: python

   Fretboard.keyboard()             # 88-key piano (A0 to C8)
   Fretboard.keyboard(61, "C2")     # 61-key synth controller
   Fretboard.keyboard(49, "C2")     # 49-key controller
   Fretboard.keyboard(25, "C3")     # 25-key mini MIDI controller

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

.. code-block:: python

   from pytheory import Fretboard, CHARTS

   fb = Fretboard.guitar()
   c = CHARTS["western"]["C"]

   # Best single fingering
   print(c.fingering(fretboard=fb))
   # (0, 1, 0, 2, 3, 0)

   # All equally-scored fingerings
   all_c = c.fingering(fretboard=fb, multiple=True)

   # Muted strings appear as None
   f = CHARTS["western"]["F"]
   print(f.fingering(fretboard=fb))

Reading Fingerings
~~~~~~~~~~~~~~~~~~

The tuple ``(0, 1, 0, 2, 3, 0)`` reads from the highest string to the
lowest::

    e|--0--    (open — E)
    B|--1--    (fret 1 — C)
    G|--0--    (open — G)
    D|--2--    (fret 2 — E)
    A|--3--    (fret 3 — C)
    E|--0--    (open — E)

A value of ``None`` means the string is muted (not played).

Generating Full Charts
----------------------

Generate fingerings for every chord at once:

.. code-block:: python

   from pytheory import Fretboard, charts_for_fretboard

   fb = Fretboard.guitar()
   chart = charts_for_fretboard(fretboard=fb)

   for name, fingering in chart.items():
       print(f"{name:6s} {fingering}")

   # Works with any instrument
   uke_chart = charts_for_fretboard(fretboard=Fretboard.ukulele())
   mando_chart = charts_for_fretboard(fretboard=Fretboard.mandolin())

Custom Instruments
------------------

Any instrument can be modeled with custom string tunings:

.. code-block:: python

   from pytheory import Tone, Fretboard

   # Baritone ukulele (DGBE — top 4 guitar strings)
   bari_uke = Fretboard(tones=[
       Tone.from_string("E4"),
       Tone.from_string("B3"),
       Tone.from_string("G3"),
       Tone.from_string("D3"),
   ])

   # Tres cubano (Cuban guitar, 3 doubled courses)
   tres = Fretboard(tones=[
       Tone.from_string("E4"),
       Tone.from_string("B3"),
       Tone.from_string("G3"),
   ])
