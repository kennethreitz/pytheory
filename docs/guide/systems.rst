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
organizes scales into **thaats** — the 10 parent scales from which ragas
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
and organizes scales into **maqamat** (plural of maqam).

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
