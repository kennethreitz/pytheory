Working with Chords
===================

A `chord <https://en.wikipedia.org/wiki/Chord_(music)>`_ is two or more tones sounding simultaneously. Chords are the
vertical dimension of music — while melody moves horizontally through
time, harmony stacks tones on top of each other.

Chord Construction
------------------

Chords are built by stacking **intervals** above a **root** note. The
most common chord type is the `triad <https://en.wikipedia.org/wiki/Triad_(music)>`_ — three notes built from
alternating scale degrees (root, 3rd, 5th).

The four triad types::

    Major       root + major 3rd (4) + perfect 5th (7)    Bright, stable
    Minor       root + minor 3rd (3) + perfect 5th (7)    Dark, sad
    Diminished  root + minor 3rd (3) + diminished 5th (6) Tense, unstable
    Augmented   root + major 3rd (4) + augmented 5th (8)  Eerie, unresolved

Adding a 7th creates a `seventh chord <https://en.wikipedia.org/wiki/Seventh_chord>`_ — the foundation of jazz
harmony::

    Dominant 7th   root + 4 + 7 + 10   Bluesy, wants to resolve (G7)
    Major 7th      root + 4 + 7 + 11   Dreamy, sophisticated (Cmaj7)
    Minor 7th      root + 3 + 7 + 10   Warm, mellow (Am7)
    Diminished 7th root + 3 + 6 + 9    Dramatic, symmetrical

Inversions
----------

A chord is in **root position** when the root is the lowest note.
When a different chord tone is in the bass, the chord is `inverted <https://en.wikipedia.org/wiki/Inversion_(music)>`_:

- **Root position**: C E G (root in bass)
- **First inversion**: E G C (3rd in bass) — notated C/E
- **Second inversion**: G C E (5th in bass) — notated C/G

Inversions change the color and weight of a chord without changing its
identity. First inversion sounds lighter; second inversion sounds
suspended, often used as a passing chord.

For seventh chords, there's also **third inversion** (7th in bass):

- G7 in third inversion: F G B D (notated G7/F)

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> root   = Chord([Tone.from_string(n, system="western") for n in ["C4", "E4", "G4"]])
   >>> first  = Chord([Tone.from_string(n, system="western") for n in ["E3", "G3", "C4"]])
   >>> second = Chord([Tone.from_string(n, system="western") for n in ["G3", "C4", "E4"]])

   >>> root.identify()
   'C major'
   >>> first.identify()
   'C major'
   >>> second.identify()
   'C major'

Extended Chords
---------------

Beyond seventh chords, jazz harmony builds `extended chords <https://en.wikipedia.org/wiki/Extended_chord>`_ by
continuing to stack thirds:

- **9th chord**: adds the 9th (= 2nd, one octave up)
- **11th chord**: adds the 9th and 11th (= 4th)
- **13th chord**: adds the 9th, 11th, and 13th (= 6th)

A full 13th chord contains all 7 notes of the scale! In practice,
tones are usually omitted — the 5th is typically dropped first, then
the 11th (which clashes with the 3rd in dominant chords).

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> scale = TonedScale(tonic="C4")["major"]

   >>> cmaj9 = scale.chord(0, 2, 4, 6, 8)
   >>> c13 = scale.chord(0, 2, 4, 6, 8, 10, 12)

Using the Chord Chart
---------------------

PyTheory includes 144 pre-built chords (12 roots x 12 qualities):

.. code-block:: pycon

   >>> from pytheory import Fretboard

   >>> fb = Fretboard.guitar()
   >>> fb.chord("C")
   Fingering(E=x, A=3, D=2, G=0, B=1, e=0)
   >>> fb.chord("Am")
   Fingering(E=x, A=0, D=2, G=2, B=1, e=0)
   >>> fb.chord("G7")
   Fingering(E=3, A=2, D=0, G=0, B=0, e=1)

You can also build chords directly with ``Chord.from_name()``:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_name("G7").identify()
   'G dominant 7th'
   >>> Chord.from_name("Ddim").identify()
   'D diminished'

Available qualities:

============  ================  ================================
Quality       Intervals         Example tones (from C)
============  ================  ================================
``""``        4, 7              C E G (major triad)
``"maj"``     4, 7              C E G (explicit major)
``"m"``       3, 7              C Eb G (minor triad)
``"5"``       7                 C G (power chord)
``"7"``       4, 7, 10          C E G Bb (dominant 7th)
``"9"``       4, 7, 10, 14      C E G Bb D (dominant 9th)
``"dim"``     3, 6              C Eb Gb (diminished)
``"m6"``      3, 7, 9           C Eb G A (minor 6th)
``"m7"``      3, 7, 10          C Eb G Bb (minor 7th)
``"m9"``      3, 7, 10, 14      C Eb G Bb D (minor 9th)
``"maj7"``    4, 7, 11          C E G B (major 7th)
``"maj9"``    4, 7, 11, 14      C E G B D (major 9th)
============  ================  ================================

.. code-block:: pycon

   >>> from pytheory import CHARTS
   >>> chart = CHARTS["western"]

   >>> chart["C"].acceptable_tone_names
   ('C', 'E', 'G')

   >>> chart["Cm7"].acceptable_tone_names
   ('C', 'Eb', 'G', 'Bb')

Building Chords
---------------

Several convenience constructors make chord creation concise:

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_tones("C", "E", "G").identify()
   'C major'
   >>> Chord.from_tones("A", "C", "E").identify()
   'A minor'

   >>> Chord.from_name("Am7").identify()
   'A minor 7th'
   >>> Chord.from_name("G7").identify()
   'G dominant 7th'

   >>> Chord.from_intervals("C", 4, 7).identify()
   'C major'
   >>> Chord.from_intervals("G", 4, 7, 10).identify()
   'G dominant 7th'

   >>> Chord.from_midi_message(60, 64, 67).identify()
   'C major'

   >>> len(Chord.from_name("C"))
   3
   >>> "C" in Chord.from_name("C")
   True

Chords also compare and hash by their voicing, so they slot into sets and
dictionary keys, and ``==`` compares the notes rather than object
identity. Two chords are equal when they hold the same tones in the same
octaves and order, so different inversions of the same notes compare
unequal:

.. code-block:: pycon

   >>> Chord.from_name("C") == Chord.from_tones("C", "E", "G")
   True
   >>> len({Chord.from_name("C"), Chord.from_name("C"), Chord.from_name("Am")})
   2

Intervals
---------

The ``intervals`` property returns semitone distances between adjacent
tones — these are musically meaningful and octave-invariant:

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").intervals
   [4, 3]

   >>> Chord.from_tones("C", "Eb", "G").intervals
   [3, 4]

Consonance and Dissonance
-------------------------

**Consonance** is the perception of stability and "pleasantness" when
tones sound together. **Dissonance** is the perception of tension and
roughness. Neither is inherently good or bad — music needs both.

Harmony Score
~~~~~~~~~~~~~

The ``harmony`` property measures consonance using **frequency ratio
simplicity**. The insight dates back to Pythagoras (6th century BC):
intervals whose frequencies form simple integer ratios sound consonant.

===========  =====  ====================
Interval     Ratio  Why it sounds "good"
===========  =====  ====================
Octave       2:1    Every 2nd wave aligns
Perfect 5th  3:2    Every 3rd wave aligns
Perfect 4th  4:3    Every 4th wave aligns
Major 3rd    5:4    Every 5th wave aligns
Minor 3rd    6:5    Every 6th wave aligns
Tritone      45:32  Waves rarely align
===========  =====  ====================

.. code-block:: pycon

   >>> from pytheory import Chord, Tone
   >>> C4 = Tone.from_string("C4", system="western")
   >>> G4 = Tone.from_string("G4", system="western")

   >>> fifth = Chord([C4, G4])
   >>> tritone = Chord([C4, C4 + 6])
   >>> fifth.harmony > tritone.harmony
   True

Dissonance Score
~~~~~~~~~~~~~~~~

The ``dissonance`` property uses the Plomp-Levelt `roughness <https://en.wikipedia.org/wiki/Roughness_(psychoacoustics)>`_ model
(1965). When two frequencies are close together, their sound waves
interfere and produce rapid amplitude fluctuations called `beating <https://en.wikipedia.org/wiki/Beat_(acoustics)>`_.
This beating is perceived as roughness — the physiological basis of
dissonance.

The roughness depends on the frequency difference relative to the
**critical bandwidth** of the human ear (~25% of the frequency at
that register). Maximum roughness occurs when the difference equals
the critical bandwidth.

.. code-block:: pycon

   >>> E4 = Tone.from_string("E4", system="western")
   >>> octave = Chord([C4, C4 + 12])
   >>> third = Chord([C4, E4])
   >>> octave.dissonance < third.dissonance
   True

Beat Frequencies
~~~~~~~~~~~~~~~~

When two tones with slightly different frequencies are played together,
you hear a pulsing at the **beat frequency**: ``|f1 - f2|`` Hz.

- **< 1 Hz**: Slow pulsing, used for tuning instruments
- **1–15 Hz**: Audible rhythmic beating
- **15–30 Hz**: Perceived as buzzing/roughness
- **> 30 Hz**: No longer beating — becomes part of the timbre

.. code-block:: pycon

   >>> A4 = Tone.from_string("A4", system="western")
   >>> chord = Chord([A4, A4 + 7, A4 + 12])

   >>> chord.beat_frequencies
   [...]

   >>> round(chord.beat_pulse, 1)
   219.3

Transposition
-------------

Shift an entire chord up or down by any number of semitones:

.. code-block:: pycon

   >>> Chord.from_name("C").transpose(7).identify()
   'G major'

   >>> Chord.from_name("Am7").transpose(-2).identify()
   'G minor 7th'

Chord Manipulation
------------------

Add or remove individual tones from a chord:

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> c_major = Chord.from_tones("C", "E", "G")

   >>> b4 = Tone.from_string("B4", system="western")
   >>> cmaj7 = c_major.add_tone(b4)
   >>> cmaj7.identify()
   'C major 7th'

   >>> c_again = cmaj7.remove_tone("B")
   >>> c_again.identify()
   'C major'

Chord Identification
--------------------

Give PyTheory any set of tones and it will tell you what chord it is.
It tries every tone as a potential root and matches the interval pattern
against 19 known chord types (triads, 6ths, 7ths, 9ths, sus, power chords).

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> Chord.from_tones("A", "C", "E").identify()
   'A minor'
   >>> Chord.from_tones("G", "B", "D", "F").identify()
   'G dominant 7th'

   >>> Chord.from_tones("E", "G", "C").identify()
   'C major'

   >>> Chord.from_tones("Bb", "D", "F").identify()
   'Bb major'

Enharmonic spellings are fully supported — Cb, Fb, E#, B#, double
sharps/flats, and unicode symbols (see :doc:`tones` for details).
``identify()`` keeps the root spelling you gave it, so a Cb major triad
comes back as ``"Cb major"`` rather than being normalized to B:

.. code-block:: pycon

   >>> Chord.from_tones("Cb", "Eb", "Gb").identify()
   'Cb major'

You can also access the root and quality separately:

.. code-block:: pycon

   >>> chord = Chord.from_name("Am7")
   >>> chord.root
   <Tone A4>
   >>> chord.quality
   'minor 7th'

Harmonic Analysis
-----------------

`Roman numeral analysis <https://en.wikipedia.org/wiki/Roman_numeral_analysis>`_ labels each chord by its function within a
key. This is how musicians describe chord progressions independent of
key — "I-IV-V" means the same thing in C major (C-F-G) as in G major
(G-C-D).

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> C4 = Tone.from_string("C4", system="western")
   >>> E4 = Tone.from_string("E4", system="western")
   >>> G4 = Tone.from_string("G4", system="western")

   >>> Chord([C4, E4, G4]).analyze("C")
   'I'
   >>> Chord.from_tones("D", "F", "A").analyze("C")
   'ii'
   >>> Chord([G4, G4+4, G4+7]).analyze("C")
   'V'
   >>> Chord([G4, G4+4, G4+7, G4+10]).analyze("C")
   'V7'

Analyzing a progression
~~~~~~~~~~~~~~~~~~~~~~~~~

``analyze`` works one chord at a time; ``analyze_progression`` labels a
whole list at once — which is how you usually read a tune:

.. code-block:: pycon

   >>> from pytheory import Chord, analyze_progression

   >>> prog = [Chord.from_name(x) for x in ("C", "Am", "F", "G")]
   >>> analyze_progression(prog, key="C")
   ['I', 'vi', 'IV', 'V']

Secondary dominants
~~~~~~~~~~~~~~~~~~~~

A secondary (applied) dominant is a chord that briefly acts as the
dominant of some chord *other* than the tonic, borrowing a chromatic
leading tone to tonicise it. In C major, ``D7`` (with its F#) pulls toward
G, so it's ``V7/V``. Pass ``secondary_dominants=True`` to label these
instead of spelling them as a bare chromatic degree:

.. code-block:: pycon

   >>> from pytheory import Chord, analyze_progression, detect_secondary_dominant

   >>> Chord.from_symbol("D7").analyze("C", secondary_dominants=True)
   'V7/V'

   >>> prog = [Chord.from_symbol(s) for s in ("C", "D7", "G7", "C")]
   >>> analyze_progression(prog, key="C", secondary_dominants=True)
   ['I', 'V7/V', 'V7', 'I']

``detect_secondary_dominant`` answers the question for a single chord,
returning the applied-dominant label or ``None`` when the chord is just a
plain diatonic dominant:

.. code-block:: pycon

   >>> detect_secondary_dominant(Chord.from_symbol("D7"), "C")
   'V7/V'
   >>> detect_secondary_dominant(Chord.from_symbol("E7"), "C")
   'V7/vi'
   >>> detect_secondary_dominant(Chord.from_symbol("G7"), "C") is None
   True

Cadences
~~~~~~~~

A `cadence <https://en.wikipedia.org/wiki/Cadence>`_ is the harmonic
punctuation that ends a phrase. ``detect_cadence`` classifies the motion
between a phrase's last two chords:

.. code-block:: pycon

   >>> from pytheory import Chord, detect_cadence, find_cadences

   >>> detect_cadence(Chord.from_name("G"), Chord.from_name("C"), "C")
   'imperfect authentic'
   >>> detect_cadence(Chord.from_name("G"), Chord.from_name("Am"), "C")
   'deceptive'
   >>> detect_cadence(Chord.from_name("F"), Chord.from_name("C"), "C")
   'plagal'
   >>> detect_cadence(Chord.from_name("Dm"), Chord.from_name("G"), "C")
   'half'

It recognizes perfect and imperfect authentic, half, phrygian half,
deceptive, and plagal cadences (and ``None`` when the motion isn't
cadential). A *perfect* authentic cadence needs real voicing — a close
root-position triad puts the fifth on top, which reads as *imperfect* — so
voice the tonic into the soprano to earn a PAC.

``find_cadences`` scans a whole progression, returning ``(index, type)``
for every cadential pair, where the index is the position of the pair's
final chord:

.. code-block:: pycon

   >>> prog = [Chord.from_name(n) for n in ("C", "F", "G", "C")]
   >>> find_cadences(prog, "C")
   [(2, 'half'), (3, 'imperfect authentic')]

Non-chord tones
~~~~~~~~~~~~~~~~

A **non-chord tone** is a melody note that isn't part of the harmony
underneath it — the passing notes, neighbors, and suspensions that give a
line its shape. ``analyze_non_chord_tones`` labels each note from its
melodic context and the chord beneath it. Pass one chord for the whole
melody, or a list with one chord per note:

.. code-block:: pycon

   >>> from pytheory import Chord, Tone, analyze_non_chord_tones

   >>> melody = [Tone.from_string(n) for n in ("C4", "D4", "E4")]
   >>> [r["type"] for r in analyze_non_chord_tones(melody, Chord.from_name("C"))]
   ['chord tone', 'passing', 'chord tone']

Each result is a dict with the ``tone``, an ``is_chord_tone`` flag, and a
``type`` — ``"chord tone"``, ``"passing"``, ``"upper neighbor"`` or
``"lower neighbor"``, ``"suspension"``, ``"anticipation"``,
``"appoggiatura"``, ``"escape tone"``, or ``"non-chord tone"``. Octaves
matter, since the classifier judges each note by how it's stepped into and
left.

Tension and Resolution
----------------------

**Tension** is what makes music move forward. Without it, there's no
desire to resolve — no drama, no narrative. The ``tension`` property
quantifies this based on:

- **Tritones** (6 semitones): the most unstable interval. The tritone
  between the 3rd and 7th of a dominant chord (e.g. B and F in G7)
  creates the strongest pull toward resolution.
- **Minor 2nds**: semitone clashes that add bite and urgency.
- **Dominant function**: the specific combination of a major 3rd and
  minor 7th above the root — the hallmark of the V7 chord.

.. code-block:: pycon

   >>> c_major = Chord([C4, E4, G4])
   >>> c_major.tension['score']
   0.0
   >>> c_major.tension['tritones']
   0

   >>> g7 = Chord([G4, G4+4, G4+7, G4+10])
   >>> g7.tension['score']
   0.6
   >>> g7.tension['tritones']
   1
   >>> g7.tension['has_dominant_function']
   True

Voice Leading
-------------

`Voice leading <https://en.wikipedia.org/wiki/Voice_leading>`_ is the art of connecting chords smoothly. Instead of
jumping all voices to new positions, good voice leading moves each note
the minimum distance to reach the next chord. Bach's chorales are the
gold standard — every voice moves by step whenever possible.

.. code-block:: pycon

   >>> c_maj = Chord.from_tones("C", "E", "G")
   >>> f_maj = Chord.from_tones("F", "A", "C")

   >>> for src, dst, motion in c_maj.voice_leading(f_maj):
   ...     print(f"{src} -> {dst}  ({motion:+d} semitones)")
   G4 -> A4  (+2 semitones)
   E4 -> F4  (+1 semitones)
   C4 -> C4  (+0 semitones)

Checking part-writing
~~~~~~~~~~~~~~~~~~~~~~

Common-practice part-writing forbids a handful of moves, and
``check_voice_leading`` flags them across a sequence of voicings. Each
voicing's tones are read low-to-high as the voices, so a four-note chord is
labelled bass / tenor / alto / soprano:

.. code-block:: pycon

   >>> from pytheory import Chord, check_voice_leading

   >>> a = Chord.from_midi_message(48, 55)   # C3 + G3 — a perfect fifth
   >>> b = Chord.from_midi_message(50, 57)   # D3 + A3 — a fifth, both rising
   >>> [issue["type"] for issue in check_voice_leading([a, b])]
   ['parallel fifths']

It catches **parallel fifths**, **parallel octaves**, and **voice
crossing** (a lower voice ending above a higher one). Smooth, contrary, or
oblique motion comes back clean:

.. code-block:: pycon

   >>> one = Chord.from_midi_message(48, 55, 64, 72)
   >>> two = Chord.from_midi_message(50, 55, 62, 71)   # contrary outer voices
   >>> check_voice_leading([one, two])
   []

Tritone Substitution
--------------------

In jazz harmony, any `dominant chord <https://en.wikipedia.org/wiki/Dominant_seventh_chord>`_
can be replaced by the dominant chord a
`tritone <https://en.wikipedia.org/wiki/Tritone_substitution>`_ (6
semitones) away. This works because the two chords share the same
tritone interval — the 3rd and 7th simply swap roles.

Common tritone subs: G7 <-> Db7, C7 <-> F#7, D7 <-> Ab7.

.. code-block:: pycon

   >>> from pytheory import Chord

   >>> g7 = Chord.from_name("G7")
   >>> sub = g7.tritone_sub()
   >>> sub.identify()
   'C# dominant 7th'

Reharmonization
---------------

Tritone substitution is one move in a larger toolkit. ``reharmonize``
gathers several at once — for a chord in a key it suggests the tritone sub
(for dominants), diatonic substitutes that share two or more notes, the
secondary dominant that tonicises it, and its negative-harmony mirror. Each
suggestion is a dict with a ``technique``, the substitute ``chord``, and a
short ``description``:

.. code-block:: pycon

   >>> from pytheory import Chord, reharmonize

   >>> for s in reharmonize(Chord.from_symbol("G7"), "C"):
   ...     print(f"{s['technique']:22s} {s['chord'].identify()}")
   tritone substitution   C# dominant 7th
   diatonic substitution  D minor
   diatonic substitution  E minor
   diatonic substitution  B diminished
   secondary dominant     D dominant 7th
   negative harmony       D half-diminished 7th

From the shell, ``pytheory reharmonize G7 --key C`` prints the same list
(add ``--json`` to pipe it, or ``--play`` to hear each option).

``reharmonize_progression`` reworks a *whole* progression at once. The
``"secondary_dominants"`` technique inserts the applied dominant before each
diatonic chord — the classic cycle-of-dominants reharmonization:

.. code-block:: pycon

   >>> from pytheory import Chord, reharmonize_progression

   >>> prog = [Chord.from_symbol(s) for s in ("C", "Am", "Dm", "G7", "C")]
   >>> out = reharmonize_progression(prog, "C", technique="secondary_dominants")
   >>> [c.symbol for c in out]
   ['C', 'E7', 'Am', 'A7', 'Dm', 'D7', 'G7', 'C']

The ``"tritone"`` technique swaps dominants for their tritone subs (chromatic
bass), and ``"diatonic"`` substitutes common-tone chords throughout. From
the shell: ``pytheory reharmonize C Am Dm G7 C --technique tritone``.

The Overtone Series
-------------------

Every musical tone is actually a stack of frequencies — the
**fundamental** plus its `overtones <https://en.wikipedia.org/wiki/Overtone>`_ (harmonics). The overtone series
is nature's chord: it contains the octave, perfect fifth, perfect
fourth, major third, and more, in that order.

This is *why* consonance exists. When you play C and G together, the
overtones of C already contain G. The two tones share acoustic energy,
reinforcing each other. A dissonant interval like C and C# shares
almost no overtones — the waves clash.

.. code-block:: pycon

   >>> from pytheory import Tone

   >>> a4 = Tone.from_string("A4", system="western")
   >>> [round(f, 1) for f in a4.overtones(8)]
   [440.0, 880.0, 1320.0, 1760.0, 2200.0, 2640.0, 3080.0, 3520.0]

Chord Symbols
-------------

The ``symbol`` property returns compact lead-sheet notation, while
``from_symbol()`` parses any standard chord symbol — no lookup table needed:

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").symbol
   'C'
   >>> Chord.from_name("Am7").symbol
   'Am7'
   >>> Chord.from_symbol("F#m7b5").identify()
   'F# half-diminished 7th'
   >>> Chord.from_symbol("Bbmaj9").symbol
   'Bbmaj9'

Slash Chords
------------

`Slash chords <https://en.wikipedia.org/wiki/Slash_chord>`_ place a specific
note in the bass below the chord. They're written as Chord/Bass in lead sheets:

.. code-block:: pycon

   >>> c = Chord.from_symbol("C")
   >>> c_over_g = c.slash("G")
   >>> c_over_g.slash_name
   'C/G'
   >>> c.slash("E").slash_name
   'C/E'

Drop Voicings
-------------

`Drop voicings <https://en.wikipedia.org/wiki/Voicing_(music)#Drop_voicings>`_
are standard arranging techniques for spreading chord tones across registers:

- **Close voicing** — all tones packed within one octave
- **Open voicing** — alternating tones raised an octave for wider spacing
- **Drop 2** — second-highest voice dropped an octave (standard jazz guitar)
- **Drop 3** — third-highest voice dropped an octave

.. code-block:: pycon

   >>> cmaj7 = Chord.from_symbol("Cmaj7")
   >>> cmaj7.close_voicing()
   <Chord C major 7th>
   >>> cmaj7.open_voicing()
   <Chord C major 7th>
   >>> cmaj7.drop2()
   <Chord C major 7th>

``open_voicing()`` takes the close voicing and raises every other
non-root tone by an octave, spreading the chord across two octaves.
The result is a wider, more spacious sound — common in orchestral
writing and piano ballads where you want the harmony to breathe.

Chord Extensions
----------------

The ``extensions()`` method suggests available extensions (9th, 11th, 13th)
that don't clash with existing chord tones:

.. code-block:: pycon

   >>> from pytheory import Chord, TonedScale
   >>> cm = Chord.from_symbol("C")
   >>> cm.extensions()
   [...]

   >>> # Filter extensions against a scale for diatonic correctness:
   >>> scale = TonedScale(tonic="C4")["major"]
   >>> cm.extensions(scale=scale)
   [...]

Chord-Scale Theory
------------------

Improvisers think in *chord-scales*: each chord implies a scale you can
solo with (the modes themselves live in :doc:`scales`). ``chord_scales``
recommends them, best fit first — from the chord quality alone, or with the
diatonic mode preferred when you supply a key:

.. code-block:: pycon

   >>> from pytheory import Chord, chord_scales, chord_scale_notes, avoid_notes

   >>> chord_scales(Chord.from_symbol("G7"))
   ['mixolydian']
   >>> chord_scales(Chord.from_symbol("Cm7"))
   ['dorian', 'aeolian', 'phrygian']

   >>> # In C major, an Em7 is the iii chord — its mode is Phrygian:
   >>> chord_scales(Chord.from_symbol("Em7"), key="C")
   ['phrygian', 'dorian', 'aeolian']

``chord_scale_notes`` spells the scale on the chord's root, and
``avoid_notes`` flags the scale tones that sit a half-step above a chord
tone — the notes you pass through rather than land on:

.. code-block:: pycon

   >>> [t.name for t in chord_scale_notes(Chord.from_symbol("Cmaj7"))]
   ['C', 'D', 'E', 'F', 'G', 'A', 'B']
   >>> [t.name for t in avoid_notes(Chord.from_symbol("Cmaj7"))]
   ['F']

Borrowed Chord Analysis
-----------------------

``analyze()`` now recognizes chromatic chords from modal interchange,
labeling them with flat-degree prefixes:

.. code-block:: pycon

   >>> Chord.from_symbol("Ab").analyze("C", "major")
   'bVI'
   >>> Chord.from_symbol("Bb").analyze("C", "major")
   'bVII'

Figured Bass
------------

`Figured bass <https://en.wikipedia.org/wiki/Figured_bass>`_ is the
classical notation for chord inversions — numbers below the bass note
describing the intervals above it. It's how Bach, Handel, and every
Baroque composer communicated harmony.

.. code-block:: pycon

   >>> from pytheory import Chord, Tone

   >>> root = Chord([Tone.from_string("C4"), Tone.from_string("E4"), Tone.from_string("G4")])
   >>> root.figured_bass
   ''

   >>> first_inv = Chord([Tone.from_string("E3"), Tone.from_string("G3"), Tone.from_string("C4")])
   >>> first_inv.figured_bass
   '6'

   >>> second_inv = Chord([Tone.from_string("G3"), Tone.from_string("C4"), Tone.from_string("E4")])
   >>> second_inv.figured_bass
   '6/4'

For seventh chords: root position → ``"7"``, first inversion → ``"6/5"``,
second inversion → ``"4/3"``, third inversion → ``"2"``.

Combine with Roman numeral analysis using ``analyze_figured()``:

.. code-block:: pycon

   >>> first_inv.analyze_figured("C")
   'I6'

Neo-Riemannian Transformations
------------------------------

`Neo-Riemannian theory <https://en.wikipedia.org/wiki/Neo-Riemannian_theory>`_
explains the smooth, chromatic triad-to-triad motion you hear in late
Romantic music and film scores — progressions that traditional Roman
numerals struggle to label. Its three basic operations each move a single
voice and flip a triad between major and minor:

- **P** (*parallel*) — same root, opposite quality: C major ↔ C minor.
- **R** (*relative*) — a triad and its relative: C major ↔ A minor.
- **L** (*Leittonwechsel*) — exchange a third away: C major ↔ E minor.

.. code-block:: pycon

   >>> from pytheory import Chord
   >>> Chord.from_name("C").parallel().identify()
   'C minor'
   >>> Chord.from_name("C").relative().identify()
   'A minor'
   >>> Chord.from_name("C").leading_tone_exchange().identify()
   'E minor'

Each transformation is its own inverse, and applying them in sequence
walks around the *Tonnetz* — the lattice of triads. Chain them with
``transform()``:

.. code-block:: pycon

   >>> Chord.from_name("C").transform("LP").identify()
   'E major'

``tonnetz_path()`` finds the shortest sequence of P/L/R moves between any
two triads — their distance on the Tonnetz. Together the three operations
reach all 24 major and minor triads:

.. code-block:: pycon

   >>> Chord.from_name("C").tonnetz_path(Chord.from_name("Am"))
   'R'
   >>> Chord.from_name("C").tonnetz_path(Chord.from_name("Abm"))   # hexatonic pole
   'PLP'

Pitch Class Sets
----------------

`Pitch class set theory <https://en.wikipedia.org/wiki/Set_theory_(music)>`_
is the framework for analyzing atonal and post-tonal music. It reduces
any collection of notes to abstract pitch classes (0–11, where C=0),
finds the most compact form, and catalogs it with a Forte number.

If you're studying Schoenberg, Webern, Bartók, or any 20th-century
music that doesn't follow traditional harmony, this is the tool.

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").pitch_classes
   {0, 4, 7}

   >>> Chord.from_tones("C", "E", "G").prime_form
   (0, 3, 7)

   >>> Chord.from_tones("A", "C", "E").prime_form
   (0, 3, 7)

Major and minor triads share the same prime form — they're inversions
of each other in pitch class space.

The **normal form** is the intermediate step — the most compact ascending
arrangement of pitch classes before transposition. It preserves the
actual pitch classes (not transposed to 0), so it tells you which
specific notes are in the set:

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").normal_form
   (0, 4, 7)

   >>> Chord.from_tones("A", "C", "E").normal_form
   (9, 0, 4)

Normal form keeps the original pitch classes; prime form transposes to 0
for comparison. Use ``normal_form`` when you care about which notes,
``prime_form`` when you care about the abstract shape.

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").forte_number
   '3-11'

   >>> Chord.from_tones("C", "E", "G", "B").forte_number
   '4-20'

   >>> Chord.from_tones("C", "E", "G#").forte_number
   '3-12'

Interval vector
~~~~~~~~~~~~~~~

The **interval-class vector** ``<ic1 ic2 ic3 ic4 ic5 ic6>`` counts how
many times each interval class (1–6 semitones) appears among all pairs of
notes. It's a fingerprint of a set's sonority — two sets with the same
vector have the same interval content, which is why they sound related:

.. code-block:: pycon

   >>> Chord.from_tones("C", "E", "G").interval_vector       # major triad
   (0, 0, 1, 1, 1, 0)

   >>> Chord.from_tones("A", "C", "E").interval_vector       # minor triad
   (0, 0, 1, 1, 1, 0)

   >>> Chord.from_tones("B", "D", "F", "Ab").interval_vector # diminished 7th
   (0, 0, 4, 0, 0, 2)

Symmetrical sets jump out: the diminished-7th chord is all minor-thirds
(ic3) and tritones (ic6), which is why it's so slippery and rootless.

Complement
~~~~~~~~~~

The **complement** is every pitch class *not* in the set. A set and its
complement together fill the twelve-note aggregate, and they share a deep
set-theoretic kinship used throughout twelve-tone writing:

.. code-block:: pycon

   >>> sorted(Chord.from_tones("C", "E", "G").complement.pitch_classes)
   [1, 2, 3, 5, 6, 8, 9, 10, 11]

``complement`` returns a playable :class:`Chord`, so you can hear it too.

Set-class relationships
~~~~~~~~~~~~~~~~~~~~~~~~~

Four predicates compare two chords as abstract sets:

.. code-block:: pycon

   >>> # Tn — a pure transposition?
   >>> Chord.from_tones("C", "E", "G").is_transposition_of(Chord.from_tones("G", "B", "D"))
   True

   >>> # TnI / same set class — related by transposition *or* inversion?
   >>> # (major and minor triads are inversions of one another)
   >>> Chord.from_tones("C", "E", "G").is_set_class_equivalent(Chord.from_tones("C", "Eb", "G"))
   True

   >>> # Literal containment
   >>> Chord.from_tones("C", "E", "G").is_subset_of(Chord.from_symbol("Cmaj7"))
   True

The **Z-relation** is the famous oddity: two sets with the *same* interval
vector that are *not* in the same set class — they share an interval
content yet can't be mapped onto each other. The smallest pair is the two
all-interval tetrachords:

.. code-block:: pycon

   >>> a = Chord.from_midi_message(0, 1, 4, 6)   # 4-z15
   >>> b = Chord.from_midi_message(0, 1, 3, 7)   # 4-z29
   >>> a.interval_vector == b.interval_vector
   True
   >>> a.is_z_related(b)
   True

Chords are the vertical dimension of music -- melody tells you where you're going, but harmony tells you how it feels to be there. Between construction, identification, voice leading, tension analysis, and pitch class sets, you've got tools to look at any chord from every angle. Pick a song you love, grab its chords, and start asking questions.
