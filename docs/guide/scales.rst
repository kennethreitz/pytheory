Working with Scales
===================

A **scale** is an ordered set of tones spanning an octave, defined by a
pattern of intervals. Scales are the foundation of melody and harmony —
they determine which notes "belong" in a piece of music and shape its
emotional character.

Scale Construction
------------------

Every scale is defined by its **interval pattern** — the sequence of
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

Use :class:`~pytheory.scales.TonedScale` to generate scales in any key:

.. code-block:: python

   from pytheory import TonedScale

   c = TonedScale(tonic="C4")

   major = c["major"]
   minor = c["minor"]
   harmonic_minor = c["harmonic minor"]

   print(major.note_names)
   # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

Major and Minor
---------------

The **major scale** (`Ionian <https://en.wikipedia.org/wiki/Ionian_mode>`_ mode) is the foundation of Western tonal
music. Its pattern of whole and half steps creates a bright, resolved
sound. Every major key has a `relative minor <https://en.wikipedia.org/wiki/Relative_key>`_ that shares the same
notes but starts from the 6th degree:

- C major → A minor (both use only white keys)
- G major → E minor (both have one sharp: F#)
- F major → D minor (both have one flat: Bb)

.. code-block:: python

   c_major = TonedScale(tonic="C4")["major"]
   a_minor = TonedScale(tonic="A4")["minor"]

   # Same notes, different starting point
   set(c_major.note_names) == set(a_minor.note_names)  # True

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

.. code-block:: python

   c = TonedScale(tonic="C4")

**Ionian** (I) — the major scale itself. Bright, happy, resolved::

   c["ionian"]    # C D E F G A B C

`Dorian <https://en.wikipedia.org/wiki/Dorian_mode>`_ (ii) — minor with a raised 6th. Jazzy, soulful (So What,
Scarborough Fair)::

   c["dorian"]    # C D Eb F G A Bb C

`Phrygian <https://en.wikipedia.org/wiki/Phrygian_mode>`_ (iii) — minor with a flat 2nd. Spanish, flamenco, dark
(White Rabbit)::

   c["phrygian"]  # C Db Eb F G Ab Bb C

`Lydian <https://en.wikipedia.org/wiki/Lydian_mode>`_ (IV) — major with a raised 4th. Dreamy, floating, ethereal
(The Simpsons theme, Flying by ET)::

   c["lydian"]    # C D E F# G A B C

`Mixolydian <https://en.wikipedia.org/wiki/Mixolydian_mode>`_ (V) — major with a flat 7th. Bluesy, rock, dominant
(Norwegian Wood, Sweet Home Alabama)::

   c["mixolydian"]  # C D E F G A Bb C

`Aeolian <https://en.wikipedia.org/wiki/Aeolian_mode>`_ (vi) — the natural minor scale. Sad, dark, introspective
(Stairway to Heaven, Losing My Religion)::

   c["aeolian"]   # C D Eb F G Ab Bb C

`Locrian <https://en.wikipedia.org/wiki/Locrian_mode>`_ (vii) — minor with flat 2nd and flat 5th. Unstable,
rarely used as a home key (used in metal and jazz over diminished
chords)::

   c["locrian"]   # C Db Eb F Gb Ab Bb C

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

Access degrees by index, Roman numeral, or name:

.. code-block:: python

   major = TonedScale(tonic="C4")["major"]

   major[0]           # C4  (by index)
   major["I"]         # C4  (by Roman numeral)
   major["tonic"]     # C4  (by degree name)

   major["V"]         # G4  (dominant)
   major["dominant"]  # G4

   major[0:3]         # (C4, D4, E4) — slicing works too

Iteration
---------

Scales are iterable and support ``len()`` and ``in``:

.. code-block:: python

   for tone in major:
       print(f"{tone.name}: {tone.frequency:.1f} Hz")

   len(major)         # 8 (7 notes + octave)
   "C" in major       # True
   "C#" in major      # False

Building Chords from Scales
----------------------------

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

.. code-block:: python

   major = TonedScale(tonic="C4")["major"]

   # Build diatonic triads
   I   = major.triad(0)   # C E G  (C major)
   ii  = major.triad(1)   # D F A  (D minor)
   iii = major.triad(2)   # E G B  (E minor)
   IV  = major.triad(3)   # F A C  (F major)
   V   = major.triad(4)   # G B D  (G major)
   vi  = major.triad(5)   # A C E  (A minor)

   # Build seventh chords
   Imaj7 = major.chord(0, 2, 4, 6)  # C E G B = Cmaj7
   V7    = major.chord(4, 6, 8, 10) # G B D F = G7 (dominant 7th)

Common Progressions
~~~~~~~~~~~~~~~~~~~

Some of the most-used chord progressions in Western music:

- **I–IV–V–I** — the foundation of blues, rock, country, folk
- **I–V–vi–IV** — the "pop progression" (Let It Be, No Woman No Cry,
  With or Without You, Someone Like You)
- **ii–V–I** — the backbone of jazz harmony
- **I–vi–IV–V** — the "50s progression" (Stand By Me, Every Breath You Take)
- **i–bVI–bIII–bVII** — the "epic" minor progression (Stairway to Heaven,
  My Heart Will Go On)
- **I–IV–vi–V** — axis of awesome (many, many pop songs)

The :class:`~pytheory.scales.Key` class makes working with progressions
easy:

.. code-block:: python

   from pytheory import Key

   key = Key("G", "major")

   # Build a progression from Roman numerals
   chords = key.progression("I", "V", "vi", "IV")
   for c in chords:
       print(c.identify())
   # G major, D major, E minor, C major

   # Nashville number system (same thing, with integers)
   key.nashville(1, 5, 6, 4)

   # All diatonic triads in the key
   key.chords
   # ['G major', 'A minor', 'B minor', 'C major', ...]

   # All diatonic seventh chords
   key.seventh_chords
   # ['G major 7th', 'A minor 7th', ...]

   # Detect the key from a set of notes
   Key.detect("C", "E", "G", "A", "D")   # <Key C major>

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

.. code-block:: python

   from pytheory import TonedScale

   a = TonedScale(tonic="A4")["major"]
   I  = a.triad(0)   # A major
   IV = a.triad(3)   # D major
   V  = a.triad(4)   # E major

   # The 12-bar blues progression
   blues_12 = [I, I, I, I, IV, IV, I, I, V, IV, I, V]

Key Signatures
~~~~~~~~~~~~~~

The ``signature`` property tells you how many sharps or flats a key has:

.. code-block:: python

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
have different notes (C major and C minor):

.. code-block:: python

   >>> Key("C", "major").relative
   <Key A minor>

   >>> Key("A", "minor").relative
   <Key C major>

   >>> Key("C", "major").parallel
   <Key C minor>

Borrowed Chords
~~~~~~~~~~~~~~~

`Modal interchange <https://en.wikipedia.org/wiki/Borrowed_chord>`_ —
borrowing chords from the parallel key — is one of the most powerful
tools in songwriting. The bVI and bVII chords (Ab and Bb in C major)
are borrowed from C minor and appear constantly in rock and film music:

.. code-block:: python

   >>> Key("C", "major").borrowed_chords
   # Chords from C minor that aren't in C major

Secondary Dominants
~~~~~~~~~~~~~~~~~~~

A `secondary dominant <https://en.wikipedia.org/wiki/Secondary_dominant>`_
is the V chord *of* a non-tonic chord. It creates a momentary pull
toward that chord, adding harmonic color:

.. code-block:: python

   key = Key("C", "major")

   # V/V — the dominant of the dominant (D7 → G)
   key.secondary_dominant(5)     # D dominant 7th

   # V/ii — the dominant of the supertonic (A7 → Dm)
   key.secondary_dominant(2)     # A dominant 7th

Random Progressions
~~~~~~~~~~~~~~~~~~~

Need inspiration? Generate weighted random progressions. The weights
favor common chord functions (I and vi most likely, vii least):

.. code-block:: python

   key = Key("C", "major")
   chords = key.random_progression(4)    # 4 chords
   [c.identify() for c in chords]
   # e.g. ['C major', 'F major', 'A minor', 'G major']

All Keys
~~~~~~~~

Enumerate all 24 major and minor keys:

.. code-block:: python

   >>> Key.all_keys()
   [<Key C major>, <Key C minor>, <Key C# major>, <Key C# minor>, ...]

Scale Transposition
~~~~~~~~~~~~~~~~~~~

Transpose an entire scale by a number of semitones:

.. code-block:: python

   c_major = TonedScale(tonic="C4")["major"]
   d_major = c_major.transpose(2)    # Up a whole step
   d_major.note_names
   # ['D', 'E', 'F#', 'G', 'A', 'B', 'C#', 'D']
