Working with Scales
===================

A **scale** is an ordered set of tones spanning an octave, defined by a
pattern of intervals. Scales are the foundation of melody and harmony --
they determine which notes "belong" in a piece of music and shape its
emotional character.

Scale Construction
------------------

Every scale is defined by its **interval pattern** -- the sequence of
whole steps (W = 2 semitones) and half steps (H = 1 semitone) between
consecutive tones.

The `major scale <https://en.wikipedia.org/wiki/Major_scale>`_::

    W  W  H  W  W  W  H
    C  D  E  F  G  A  B  C
      2  2  1  2  2  2  1    ← semitones between each note

The `natural minor scale <https://en.wikipedia.org/wiki/Minor_scale>`_::

    W  H  W  W  H  W  W
    C  D  Eb F  G  Ab Bb C
      2  1  2  2  1  2  2

Building Scales
---------------

Use :class:`~pytheory.scales.TonedScale` to generate scales in any key.
Index it by scale name to get a :class:`~pytheory.scales.Scale`:

.. code-block:: pycon

   >>> from pytheory import TonedScale
   >>> c = TonedScale(tonic="C4")
   >>> c.scales
   ('chromatic', 'major', 'minor', 'harmonic minor', 'ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian')
   >>> major = c["major"]
   >>> major.note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
   >>> c["harmonic minor"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'B', 'C']

The default Western system covers the major and minor scales, the
harmonic minor, and all seven modes. Pentatonic and blues scales live in
the dedicated ``blues`` system (see :doc:`nashville-blues-tabs`), and the
ragas, maqamat, and microtonal grids live in their own systems (see
:doc:`systems`).

Major and Minor
---------------

The **major scale** (`Ionian <https://en.wikipedia.org/wiki/Ionian_mode>`_ mode) is the foundation of Western tonal
music. Its pattern of whole and half steps creates a bright, resolved
sound. Every major key has a `relative minor <https://en.wikipedia.org/wiki/Relative_key>`_ that shares the same
notes but starts from the 6th degree:

- C major → A minor (both use only white keys)
- G major → E minor (both have one sharp: F#)
- F major → D minor (both have one flat: Bb)

.. code-block:: pycon

   >>> c_major = TonedScale(tonic="C4")["major"]
   >>> a_minor = TonedScale(tonic="A4")["minor"]
   >>> set(c_major.note_names) == set(a_minor.note_names)
   True

The `harmonic minor <https://en.wikipedia.org/wiki/Harmonic_minor_scale>`_ raises the 7th degree of the natural minor,
creating an augmented 2nd interval (3 semitones) between the 6th and
7th degrees. This gives it a distinctive "Middle Eastern" or "classical"
sound and provides the leading tone needed for dominant harmony::

    Natural minor:   C  D  Eb  F  G  Ab  Bb  C
    Harmonic minor:  C  D  Eb  F  G  Ab  B   C
                                          ↑ raised 7th

Modes
-----

The seven `modes <https://en.wikipedia.org/wiki/Mode_(music)>`_ of the major scale are rotations of the same interval
pattern, each starting from a different degree. Each mode has a distinct
emotional character:

.. code-block:: pycon

   >>> c = TonedScale(tonic="C4")

**Ionian** (I) -- the major scale itself. Bright, happy, resolved:

.. code-block:: pycon

   >>> c["ionian"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

`Dorian <https://en.wikipedia.org/wiki/Dorian_mode>`_ (ii) -- minor with a raised 6th. Jazzy, soulful (So What,
Scarborough Fair):

.. code-block:: pycon

   >>> c["dorian"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb', 'C']

`Phrygian <https://en.wikipedia.org/wiki/Phrygian_mode>`_ (iii) -- minor with a flat 2nd. Spanish, flamenco, dark
(White Rabbit):

.. code-block:: pycon

   >>> c["phrygian"].note_names
   ['C', 'Db', 'Eb', 'F', 'G', 'Ab', 'Bb', 'C']

`Lydian <https://en.wikipedia.org/wiki/Lydian_mode>`_ (IV) -- major with a raised 4th. Dreamy, floating, ethereal
(The Simpsons theme, Flying by ET):

.. code-block:: pycon

   >>> c["lydian"].note_names
   ['C', 'D', 'E', 'F#', 'G', 'A', 'B', 'C']

`Mixolydian <https://en.wikipedia.org/wiki/Mixolydian_mode>`_ (V) -- major with a flat 7th. Bluesy, rock, dominant
(Norwegian Wood, Sweet Home Alabama):

.. code-block:: pycon

   >>> c["mixolydian"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'Bb', 'C']

`Aeolian <https://en.wikipedia.org/wiki/Aeolian_mode>`_ (vi) -- the natural minor scale. Sad, dark, introspective
(Stairway to Heaven, Losing My Religion):

.. code-block:: pycon

   >>> c["aeolian"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb', 'C']

`Locrian <https://en.wikipedia.org/wiki/Locrian_mode>`_ (vii) -- minor with flat 2nd and flat 5th. Unstable,
rarely used as a home key (used in metal and jazz over diminished
chords):

.. code-block:: pycon

   >>> c["locrian"].note_names
   ['C', 'Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C']

Scale Degrees
-------------

Each note in a scale has a **degree name** that describes its function:

============  ======  =======================================
Degree        Number  Function
============  ======  =======================================
Tonic         I       Home base — the key center
Supertonic    II      One step above tonic
Mediant       III     Halfway between tonic and dominant
Subdominant   IV      A fifth below tonic (or fourth above)
Dominant      V       The strongest pull back to tonic
Submediant    VI      Root of the relative minor (or major)
Leading Tone  VII     One semitone below tonic — pulls upward
============  ======  =======================================

Access degrees by index, Roman numeral, or name -- each returns the
:class:`~pytheory.tones.Tone` at that position:

.. code-block:: pycon

   >>> major = TonedScale(tonic="C4")["major"]
   >>> major[0]
   <Tone C4>
   >>> major["I"]
   <Tone C4>
   >>> major["tonic"]
   <Tone C4>
   >>> major["V"]
   <Tone G4>
   >>> major["dominant"]
   <Tone G4>
   >>> major[0:3]
   (<Tone C4>, <Tone D4>, <Tone E4>)

To go the other way -- from an index to its traditional function name --
use :meth:`~pytheory.scales.Scale.degree_name`. Pass ``minor=True`` to
get "subtonic" instead of "leading tone" for the flattened 7th:

.. code-block:: pycon

   >>> major.degree_name(0)
   'tonic'
   >>> major.degree_name(4)
   'dominant'
   >>> major.degree_name(6)
   'leading tone'
   >>> major.degree_name(6, minor=True)
   'subtonic'

Iteration
---------

Scales are iterable and support ``len()`` and ``in``:

.. code-block:: pycon

   >>> for tone in major:
   ...     print(f"{tone.name}: {tone.frequency:.1f} Hz")
   C: 261.6 Hz
   D: 293.7 Hz
   E: 329.6 Hz
   F: 349.2 Hz
   G: 392.0 Hz
   A: 440.0 Hz
   B: 493.9 Hz
   C: 523.3 Hz
   >>> len(major)
   8
   >>> "C" in major
   True
   >>> "C#" in major
   False

Scale Utilities
---------------

A :class:`~pytheory.scales.Scale` can do more than list its notes. These
helpers transpose it, score how well a melody fits it, and figure out
which scale a phrase belongs to.

Transposition
~~~~~~~~~~~~~~

Transpose an entire scale by a number of semitones, preserving its
interval pattern:

.. code-block:: pycon

   >>> c_major = TonedScale(tonic="C4")["major"]
   >>> c_major.transpose(2).note_names
   ['D', 'E', 'F#', 'G', 'A', 'B', 'C#', 'D']

Parallel Modes
~~~~~~~~~~~~~~

:meth:`~pytheory.scales.Scale.parallel_modes` returns all seven modes
that share the same notes as a scale -- the "white-key" family for
C major:

.. code-block:: pycon

   >>> for name, notes in c_major.parallel_modes().items():
   ...     print(f"{name}: {' '.join(notes)}")
   C ionian: C D E F G A B C
   D dorian: D E F G A B C D
   E phrygian: E F G A B C D E
   F lydian: F G A B C D E F
   G mixolydian: G A B C D E F G
   A aeolian: A B C D E F G A
   B locrian: B C D E F G A B

Scale Fitness
~~~~~~~~~~~~~

Score how well a set of notes fits a scale, from 0.0 to 1.0 -- the
fraction of your notes the scale contains. Handy for melody analysis or
testing which scale a phrase belongs to:

.. code-block:: pycon

   >>> major = TonedScale(tonic="C4")["major"]
   >>> major.fitness("C", "D", "E", "G")
   1.0
   >>> major.fitness("C", "D", "F#", "G")
   0.75

Scale Recommendation
~~~~~~~~~~~~~~~~~~~~

Given a melody or set of notes, :meth:`~pytheory.scales.Scale.recommend`
finds the best-matching scales, ranked by fitness. Useful for figuring
out what key you're in, or finding alternative scales to improvise over:

.. code-block:: pycon

   >>> from pytheory.scales import Scale
   >>> Scale.recommend("C", "D", "E", "F", "G", "A", "B", top=3)
   [('A', 'aeolian', 1.0), ('D', 'dorian', 1.0), ('C', 'ionian', 1.0)]
   >>> Scale.recommend("C", "Eb", "G", "Bb", top=3)
   [('C', 'aeolian', 1.0), ('F', 'aeolian', 1.0), ('G', 'aeolian', 1.0)]

How it works: ``recommend()`` tests your notes against every scale in
every key of the Western system (all 12 tonics times every scale type),
scoring each with ``fitness()``. Results are ranked by fitness, the
all-matching chromatic scale is pushed down, and remaining ties are
broken alphabetically by scale name and then by tonic -- which is why a
complete C-major collection surfaces its whole modal family (``aeolian``
before ``dorian`` before ``ionian``) at fitness 1.0. It returns
``(tonic, scale_name, fitness)`` tuples; pass ``top=`` to control how
many you get back (default 5).

For a single best guess rather than a ranked list,
:meth:`~pytheory.scales.Scale.detect` returns one
``(tonic, scale_name, match_count)`` tuple:

.. code-block:: pycon

   >>> Scale.detect("C", "D", "E", "F", "G", "A", "B")
   ('C', 'major', 7)

``detect()`` counts matching pitch classes and breaks ties toward a major
spelling, so a natural-minor set comes back as its relative major. Reach
for :meth:`Key.detect <pytheory.scales.Key.detect>` (below) when you want
the key itself.

Building Chords from Scales
---------------------------

`Diatonic <https://en.wikipedia.org/wiki/Diatonic_and_chromatic>`_ harmony builds chords by stacking every other note of the
scale. A **triad** takes the 1st, 3rd, and 5th; a **seventh chord** adds
the 7th.

In the C major scale, the diatonic triads are::

    I    C  E  G    = C major
    ii   D  F  A    = D minor
    iii  E  G  B    = E minor
    IV   F  A  C    = F major
    V    G  B  D    = G major
    vi   A  C  E    = A minor
    vii° B  D  F    = B diminished

Notice the pattern: **major** triads on I, IV, V; **minor** triads on
ii, iii, vi; **diminished** on vii°. This pattern holds for every major
key.

.. code-block:: pycon

   >>> major = TonedScale(tonic="C4")["major"]
   >>> major.triad(0)
   <Chord C major>
   >>> major.triad(1)
   <Chord D minor>
   >>> major.triad(4)
   <Chord G major>
   >>> major.chord(0, 2, 4, 6)
   <Chord C major 7th>
   >>> major.chord(4, 6, 8, 10)
   <Chord G dominant 7th>

:meth:`~pytheory.scales.Scale.triad` and
:meth:`~pytheory.scales.Scale.seventh` are shorthand for the right
``chord()`` call; degrees past the octave wrap around and climb a
register. For everything you can do *with* a chord once you have it --
inversions, voicings, identification, analysis -- see :doc:`chords`.

Harmonizing a Scale
~~~~~~~~~~~~~~~~~~~~

Rather than building triads one at a time,
:meth:`~pytheory.scales.Scale.harmonize` returns every diatonic triad at
once:

.. code-block:: pycon

   >>> harmony = TonedScale(tonic="C4")["major"].harmonize()
   >>> [c.identify() for c in harmony]
   ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']

Keys and Harmony
----------------

The :class:`~pytheory.scales.Key` class is the friendly front door to a
scale and everything you can build on it -- diatonic triads, seventh
chords, and Roman-numeral progressions:

.. code-block:: pycon

   >>> from pytheory import Key
   >>> key = Key("C", "major")
   >>> key.note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
   >>> key.chords
   ['C major', 'D minor', 'E minor', 'F major', 'G major', 'A minor', 'B diminished']
   >>> key.seventh_chords
   ['C major 7th', 'D minor 7th', 'E minor 7th', 'F major 7th', 'G dominant 7th', 'A minor 7th', 'B half-diminished 7th']

Build a progression from Roman numerals with
:meth:`~pytheory.scales.Key.progression`, or from Arabic numbers with
:meth:`~pytheory.scales.Key.nashville`:

.. code-block:: pycon

   >>> key = Key("G", "major")
   >>> [c.identify() for c in key.progression("I", "V", "vi", "IV")]
   ['G major', 'D major', 'E minor', 'C major']
   >>> key.nashville(1, 5, 6, 4)
   [<Chord G major>, <Chord D major>, <Chord E minor>, <Chord C major>]

The numeral says exactly what you mean. **Case** sets the quality --
uppercase is major, lowercase minor -- so an uppercase ``"V"`` in a minor
key gives the harmonic-minor dominant, and ``"IV"`` the Dorian major-IV.
Quality markers (``"°"``, ``"ø"``, ``"+"``, ``"maj"``) and a flat/sharp
prefix for **borrowed chords** work too:

.. code-block:: pycon

   >>> Key("A", "minor").progression("i", "iv", "V7", "i")   # harmonic-minor cadence
   [<Chord A minor>, <Chord D minor>, <Chord E dominant 7th>, <Chord A minor>]
   >>> [c.identify() for c in Key("C", "major").progression("I", "bVII", "IV")]
   ['C major', 'Bb major', 'F major']

Slash notation builds **secondary (applied) dominants** -- ``"V7/V"`` is
the dominant of the dominant:

.. code-block:: pycon

   >>> [c.identify() for c in Key("C", "major").progression("I", "V7/V", "V7", "I")]
   ['C major', 'D dominant 7th', 'G dominant 7th', 'C major']

Build a seventh chord on any individual degree with
:meth:`~pytheory.scales.Key.seventh` -- the single-degree version of
``seventh_chords``:

.. code-block:: pycon

   >>> key = Key("G", "major")
   >>> key.seventh(0)   # Imaj7
   <Chord G major 7th>
   >>> key.seventh(4)   # V7
   <Chord D dominant 7th>
   >>> key.seventh(6)   # vii ø7
   <Chord F# half-diminished 7th>

Detecting a Key
~~~~~~~~~~~~~~~

Hand :meth:`~pytheory.scales.Key.detect` a pile of notes and it returns
the most likely key, comparing pitch classes so enharmonic spellings
don't matter:

.. code-block:: pycon

   >>> Key.detect("C", "E", "G", "A", "D")
   <Key C major>

Common Progressions
~~~~~~~~~~~~~~~~~~~

Some of the most-used chord progressions in Western music:

- **I–IV–V–I** -- the foundation of blues, rock, country, folk
- **I–V–vi–IV** -- the "pop progression" (Let It Be, No Woman No Cry,
  With or Without You, Someone Like You)
- **ii–V–I** -- the backbone of jazz harmony
- **I–vi–IV–V** -- the "50s progression" (Stand By Me, Every Breath You Take)
- **i–bVI–bIII–bVII** -- the "epic" minor progression (Stairway to Heaven,
  My Heart Will Go On)
- **I–IV–vi–V** -- axis of awesome (many, many pop songs)

Those highlights are just the start -- :data:`~pytheory.PROGRESSIONS` is a
library of 34 named progressions spanning pop, blues (12-bar,
quick-change, 8-bar, minor), jazz (ii–V–I and turnarounds), classical
(Pachelbel, the circle of fifths), flamenco, and a range of minor and
modal loops. Look one up by name and feed it straight to
``progression()``:

.. code-block:: pycon

   >>> from pytheory import PROGRESSIONS, Key
   >>> Key("C", "major").progression(*PROGRESSIONS["circle of fifths"])
   [<Chord C major>, <Chord F major>, <Chord B diminished>, ...]

To realize every named progression in your key at once, call
:meth:`~pytheory.scales.Key.common_progressions`:

.. code-block:: pycon

   >>> key = Key("C", "major")
   >>> for name, chords in list(key.common_progressions().items())[:3]:
   ...     print(f"{name}: {' → '.join(c.symbol for c in chords)}")
   I-IV-V-I: C → F → G → C
   I-V-vi-IV: C → G → Am → F
   I-vi-IV-V: C → Am → F → G

The 12-Bar Blues
~~~~~~~~~~~~~~~~

The `12-bar blues <https://en.wikipedia.org/wiki/Twelve-bar_blues>`_ is the most influential chord progression in
American music. It's 12 measures long and uses only three chords
(I, IV, V)::

    | I  | I  | I  | I  |
    | IV | IV | I  | I  |
    | V  | IV | I  | V  |

Every blues, early rock and roll, and much of jazz is built on this
structure. In the key of A::

    | A  | A  | A  | A  |
    | D  | D  | A  | A  |
    | E  | D  | A  | E  |

.. code-block:: pycon

   >>> from pytheory import TonedScale
   >>> a = TonedScale(tonic="A4")["major"]
   >>> I, IV, V = a.triad(0), a.triad(3), a.triad(4)
   >>> blues_12 = [I, I, I, I, IV, IV, I, I, V, IV, I, V]

For the blues *scale* and pentatonics to solo over those changes, see
:doc:`nashville-blues-tabs`.

Key Signatures
~~~~~~~~~~~~~~

The ``signature`` property tells you how many sharps or flats a key has:

.. code-block:: pycon

   >>> Key("G", "major").signature
   {'sharps': 1, 'flats': 0, 'accidentals': ['F#']}
   >>> Key("F", "major").signature
   {'sharps': 0, 'flats': 1, 'accidentals': ['Bb']}
   >>> Key("C", "major").signature
   {'sharps': 0, 'flats': 0, 'accidentals': []}

Relative and Parallel Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~

Two keys are **relative** if they share the same notes (C major and
A minor). Two keys are `parallel <https://en.wikipedia.org/wiki/Parallel_key>`_ if they share the same tonic but
have different notes (C major and C minor). Both properties return
:class:`~pytheory.scales.Key` objects:

.. code-block:: pycon

   >>> Key("C", "major").relative
   <Key A minor>
   >>> Key("A", "minor").relative
   <Key C major>
   >>> Key("C", "major").parallel
   <Key C minor>

The Circle of Fifths
~~~~~~~~~~~~~~~~~~~~~

:meth:`~pytheory.scales.Key.circle_of_fifths` maps a key's
neighborhood. Adjacent keys differ by a single accidental and share most
of their chords, which is exactly what makes them feel close:

.. code-block:: pycon

   >>> cof = Key("C", "major").circle_of_fifths()
   >>> cof["position"]            # sharps minus flats; C is 0
   0
   >>> str(cof["dominant"]["key"]), str(cof["subdominant"]["key"])
   ('G major', 'F major')
   >>> cof["dominant"]["shared_chords"]
   ['A minor', 'C major', 'E minor', 'G major']
   >>> [str(k) for k in cof["circle"]]
   ['C major', 'G major', 'D major', 'A major', 'E major', 'B major', 'Gb major', 'Db major', 'Ab major', 'Eb major', 'Bb major', 'F major']

Borrowed Chords
~~~~~~~~~~~~~~~

`Modal interchange <https://en.wikipedia.org/wiki/Borrowed_chord>`_ --
borrowing chords from the parallel key -- is one of the most powerful
tools in songwriting. The bVI and bVII chords (Ab and Bb in C major)
are borrowed from C minor and appear constantly in rock and film music:

.. code-block:: pycon

   >>> Key("C", "major").borrowed_chords
   ['C minor', 'D diminished', 'Eb major', 'F minor', 'G minor', 'Ab major', 'Bb major']

Secondary Dominants
~~~~~~~~~~~~~~~~~~~

A `secondary dominant <https://en.wikipedia.org/wiki/Secondary_dominant>`_
is the V chord *of* a non-tonic chord. It creates a momentary pull
toward that chord, adding harmonic color. The degree argument is
1-indexed:

.. code-block:: pycon

   >>> key = Key("C", "major")
   >>> key.secondary_dominant(5)   # V/V
   <Chord D dominant 7th>
   >>> key.secondary_dominant(2)   # V/ii
   <Chord A dominant 7th>

Chord Functions
~~~~~~~~~~~~~~~

Functional harmony sorts the seven diatonic chords into three families by
how they behave: **tonic** chords feel like home (I, iii, vi),
**subdominant** chords move away (ii, IV), and **dominant** chords pull
back (V, vii°). Chords in the same family are largely interchangeable:

.. code-block:: pycon

   >>> key = Key("C", "major")
   >>> {fn: [c.symbol for c in cs] for fn, cs in key.chords_by_function().items()}
   {'tonic': ['C', 'Em', 'Am'], 'subdominant': ['Dm', 'F'], 'dominant': ['G', 'Bdim']}

The grouping is by scale degree, so it holds in minor keys too. The
shortcuts :meth:`~pytheory.scales.Key.tonic_chords`,
:meth:`~pytheory.scales.Key.subdominant_chords`, and
:meth:`~pytheory.scales.Key.dominant_chords` return one family at a time.

Chord Suggestions
~~~~~~~~~~~~~~~~~

Given a chord in a key, :meth:`~pytheory.scales.Key.suggest_next` returns
likely next chords based on functional voice-leading tendencies:

.. code-block:: pycon

   >>> key = Key("C", "major")
   >>> g_major = key.triad(4)   # V chord
   >>> [c.symbol for c in key.suggest_next(g_major)]
   ['C', 'Am', 'F']

Modulation
~~~~~~~~~~

:meth:`~pytheory.scales.Key.modulation_path` suggests a chord-by-chord
route from one key to another, using a pivot chord when one is available:

.. code-block:: pycon

   >>> path = Key("C", "major").modulation_path(Key("G", "major"))
   >>> [c.symbol for c in path]
   ['C', 'Em', 'D', 'G']

:meth:`~pytheory.scales.Key.pivot_chords` shows which chords are shared
between two keys -- the more they share, the smoother the modulation:

.. code-block:: pycon

   >>> Key("C", "major").pivot_chords(Key("G", "major"))
   ['A minor', 'C major', 'E minor', 'G major']

Negative Harmony
~~~~~~~~~~~~~~~~

:meth:`~pytheory.scales.Key.negative_harmony` mirrors every pitch across
the axis running between the tonic and the dominant (Ernst Levy's
reflection). Major becomes minor while the gravitational pull toward the
tonic is preserved:

.. code-block:: pycon

   >>> neg = Key("C", "major").negative_harmony()
   >>> neg["axis"]
   ('C', 'G')
   >>> neg["negative_dominant"].symbol
   'Fm'
   >>> neg["scale"]
   ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb']
   >>> [c.symbol for c in neg["chords"]]
   ['Cm', 'Bb', 'Ab', 'Gm', 'Fm', 'Eb', 'Ddim']

Random Progressions
~~~~~~~~~~~~~~~~~~~

Need inspiration? :meth:`~pytheory.scales.Key.random_progression`
generates weighted-random progressions. The weights favor common chord
functions (I and vi most likely, vii least), and the progression always
starts on I:

.. code-block:: pycon

   >>> key = Key("C", "major")
   >>> [c.symbol for c in key.random_progression(4)]   # output varies
   ['C', 'Dm', 'F', 'C']

All Keys
~~~~~~~~

Enumerate all 24 major and minor keys:

.. code-block:: pycon

   >>> Key.all_keys()
   [<Key C major>, <Key C minor>, <Key C# major>, <Key C# minor>, ...]

Scales are the map; the key is the territory. Once you know the landscape, you can wander freely -- and you'll always know how to get home.
