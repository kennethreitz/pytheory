Musical Systems
===============

PyTheory supports four musical systems, each with its own tone names
and scale patterns.

Western
-------

The standard 12-tone equal temperament system with major/minor scales
and all seven modes.

.. code-block:: python

   from pytheory import TonedScale

   c = TonedScale(tonic="C4")
   c["major"].note_names
   # ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

   c["dorian"].note_names
   # ['C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'C']

**Scales:** major, minor, harmonic minor, ionian, dorian, phrygian,
lydian, mixolydian, aeolian, locrian, chromatic

Indian Classical (Hindustani)
-----------------------------

The Hindustani system uses **swaras** (Sa, Re, Ga, Ma, Pa, Dha, Ni) and
organizes scales into **`thaats <https://en.wikipedia.org/wiki/Thaat>`_** — the 10 parent scales from which `ragas <https://en.wikipedia.org/wiki/Raga>`_
are derived.

.. code-block:: python

   from pytheory import TonedScale
   from pytheory.systems import SYSTEMS

   sa = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])

   sa["bilawal"].note_names   # = major scale
   # ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni', 'Sa']

   sa["bhairav"].note_names   # unique to Indian music
   # ['Sa', 'komal Re', 'Ga', 'Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

   sa["todi"].note_names
   # ['Sa', 'komal Re', 'komal Ga', 'tivra Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

**Thaats:** bilawal, khamaj, kafi, asavari, bhairavi, kalyan, bhairav,
poorvi, marwa, todi

**Swara notation:**

- Uppercase = shuddha (natural): Sa, Re, Ga, Ma, Pa, Dha, Ni
- ``komal`` prefix = flat: komal Re, komal Ga, komal Dha, komal Ni
- ``tivra`` prefix = sharp: tivra Ma

Arabic Maqam
------------

The Arabic system uses **solfège-based names** (Do, Re, Mi, Fa, Sol, La, Si)
and organizes scales into **maqamat** (plural of `maqam <https://en.wikipedia.org/wiki/Maqam>`_).

.. note::

   True maqam music uses quarter-tones that cannot be represented in
   12-tone equal temperament. These scales are the closest 12-TET
   approximations.

.. code-block:: python

   from pytheory import TonedScale
   from pytheory.systems import SYSTEMS

   do = TonedScale(tonic="Do4", system=SYSTEMS["arabic"])

   do["ajam"].note_names     # = major scale
   # ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si', 'Do']

   do["hijaz"].note_names    # characteristic augmented 2nd
   # ['Do', 'Reb', 'Mi', 'Fa', 'Sol', 'Solb', 'Sib', 'Do']

   do["nikriz"].note_names
   # ['Do', 'Re', 'Mib', 'Fa#', 'Sol', 'La', 'Sib', 'Do']

**Maqamat:** ajam, nahawand, kurd, hijaz, nikriz, bayati, rast, saba,
sikah, jiharkah

Japanese
--------

The Japanese system uses Western note names with traditional pentatonic
and heptatonic scales from Japanese music.

.. code-block:: python

   from pytheory import TonedScale
   from pytheory.systems import SYSTEMS

   c = TonedScale(tonic="C4", system=SYSTEMS["japanese"])

   c["hirajoshi"].note_names  # most iconic Japanese scale
   # ['C', 'D', 'D#', 'G', 'G#', 'C']

   c["in"].note_names         # Miyako-bushi, used in koto music
   # ['C', 'C#', 'F', 'G', 'G#', 'C']

   c["yo"].note_names         # folk music scale
   # ['C', 'D', 'F', 'G', 'A#', 'C']

   c["ritsu"].note_names      # gagaku court music (= Dorian)
   # ['C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'C']

**Pentatonic scales:** hirajoshi, in, yo, iwato, kumoi, insen

**Heptatonic scales:** ritsu, ryo

Blues and Pentatonic
-------------------

The blues system provides the scales foundational to blues, rock, jazz,
and folk music worldwide. `Pentatonic scales <https://en.wikipedia.org/wiki/Pentatonic_scale>`_ (5 notes) are the oldest
known musical scales, found independently in cultures across every
continent.

The **`blues scale <https://en.wikipedia.org/wiki/Blues_scale>`_** adds the "`blue note <https://en.wikipedia.org/wiki/Blue_note>`_" (flat 5th / sharp 4th) to the
minor pentatonic — this chromatic passing tone is the defining sound
of the blues.

.. code-block:: python

   from pytheory import TonedScale
   from pytheory.systems import SYSTEMS

   c = TonedScale(tonic="C4", system=SYSTEMS["blues"])

   c["major pentatonic"].note_names  # the "happy" pentatonic
   # ['C', 'D', 'E', 'G', 'A', 'C']

   c["minor pentatonic"].note_names  # the "sad" pentatonic
   # ['C', 'D#', 'F', 'G', 'A#', 'C']

   c["blues"].note_names             # minor pentatonic + blue note
   # ['C', 'D#', 'F', 'F#', 'G', 'A#', 'C']

   c["major blues"].note_names       # major pentatonic + blue note
   # ['C', 'D', 'D#', 'E', 'G', 'A', 'C']

**Pentatonic:** major pentatonic, minor pentatonic

**Hexatonic:** blues, major blues

**Heptatonic:** dominant (Mixolydian — the dominant 7th sound),
minor (Dorian — the jazz minor sound)


Javanese Gamelan
----------------

The `gamelan <https://en.wikipedia.org/wiki/Gamelan>`_ system approximates the scales of the Javanese and Balinese
gamelan orchestra in 12-tone equal temperament. True gamelan tuning is
unique to each ensemble and does not conform to Western intonation —
these are the closest 12-TET approximations.

**`Slendro <https://en.wikipedia.org/wiki/Slendro>`_** is a roughly equal 5-tone division of the octave, producing
an ethereal, floating quality. **`Pelog <https://en.wikipedia.org/wiki/Pelog>`_** is a 7-tone scale with unequal
intervals, typically performed using 5-note subsets called *pathet*.

.. code-block:: python

   from pytheory import TonedScale
   from pytheory.systems import SYSTEMS

   ji = TonedScale(tonic="ji4", system=SYSTEMS["gamelan"])

   ji["slendro"].note_names      # the 5-tone equidistant scale
   # ['ji', 'ro', 'pat', 'mo', 'pi', 'ji']

   ji["pelog"].note_names         # full 7-tone pelog
   # ['ji', 'ro-', 'lu', 'pat', 'mo', 'nem-', 'barang', 'ji']

   ji["pelog nem"].note_names     # pathet nem subset
   # ['ji', 'ro-', 'lu', 'pat', 'mo', 'ji']

**Pentatonic:** slendro, pelog nem, pelog barang, pelog lima

**Heptatonic:** pelog (full 7-tone)

.. note::

   Gamelan tone names follow Javanese numbering: ji (1), ro (2),
   lu (3), pat (4), mo (5), nem (6), pi/barang (7). Suffixes
   indicate microtonal variants approximated to the nearest semitone.


Cross-System Comparison
-----------------------

Since all systems use 12-tone equal temperament, equivalent scales
produce the same pitches:

.. code-block:: python

   from pytheory import TonedScale, Tone
   from pytheory.systems import SYSTEMS

   # These are all the same scale with different names
   western = TonedScale(tonic="C4")["major"]
   indian  = TonedScale(tonic="Sa4", system=SYSTEMS["indian"])["bilawal"]
   arabic  = TonedScale(tonic="Do4", system=SYSTEMS["arabic"])["ajam"]

   # Same pitches
   c4 = Tone.from_string("C4", system="western")
   sa4 = Tone.from_string("Sa4", system="indian")
   do4 = Tone.from_string("Do4", system="arabic")

   c4.frequency   # 261.63
   sa4.frequency  # 261.63
   do4.frequency  # 261.63
