Musical Systems
===============

PyTheory supports **16 musical systems** — 6 core systems mapped onto
12-tone equal temperament, plus 10 microtonal systems with their own
native tunings. The core systems let you compare scales across cultures;
the microtonal systems go beyond 12-TET into genuinely different pitch
universes.

Western
-------

The standard 12-tone equal temperament system — the common language of
European classical music, American popular music, and virtually all
commercially recorded music since the early 20th century. Its
major/minor tonality system, seven diatonic modes, and rich harmonic
vocabulary form the foundation that most listeners around the world
grew up hearing. If you've ever hummed along to a pop song, played
piano, or picked up a guitar, you've been working within this system.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4")
   >>> c["major"].note_names
   ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']

   >>> c["dorian"].note_names
   ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb', 'C']

**Scales:** major, minor, harmonic minor, ionian, dorian, phrygian,
lydian, mixolydian, aeolian, locrian, chromatic

Indian Classical (Hindustani)
-----------------------------

One of the oldest and most sophisticated musical traditions on earth,
`Hindustani classical music <https://en.wikipedia.org/wiki/Hindustani_classical_music>`_
dates back over two thousand years to the *Natya Shastra*. Where Western
music emphasizes harmony (chords), Indian music emphasizes *raga* —
melodic frameworks that evoke specific moods, times of day, and seasons.
The sound is meditative, ornamental, and deeply expressive. You'll hear
it in classical sitar and tabla performances, Bollywood film scores,
and the improvisatory traditions that influenced musicians from
George Harrison to John Coltrane.

The Hindustani system uses **swaras** (Sa, Re, Ga, Ma, Pa, Dha, Ni) and
organizes scales into `thaats <https://en.wikipedia.org/wiki/Thaat>`_ — the 10 parent scales from which `ragas <https://en.wikipedia.org/wiki/Raga>`_
are derived.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> sa = TonedScale(tonic="Sa4", system="indian")

   >>> sa["bilawal"].note_names   # = major scale
   ['Sa', 'Re', 'Ga', 'Ma', 'Pa', 'Dha', 'Ni', 'Sa']

   >>> sa["bhairav"].note_names   # unique to Indian music
   ['Sa', 'komal Re', 'Ga', 'Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

   >>> sa["todi"].note_names
   ['Sa', 'komal Re', 'komal Ga', 'tivra Ma', 'Pa', 'komal Dha', 'Ni', 'Sa']

**Thaats:** bilawal, khamaj, kafi, asavari, bhairavi, kalyan, bhairav,
poorvi, marwa, todi

**Swara notation:**

- Uppercase = shuddha (natural): Sa, Re, Ga, Ma, Pa, Dha, Ni
- ``komal`` prefix = flat: komal Re, komal Ga, komal Dha, komal Ni
- ``tivra`` prefix = sharp: tivra Ma

Arabic Maqam
------------

The `maqam <https://en.wikipedia.org/wiki/Arabic_maqam>`_ tradition spans
the entire Arab world, Turkey, Iran, and Central Asia — a vast musical
heritage stretching from medieval Andalusia to modern Cairo. Maqam music
is melodically rich, often featuring microtonal inflections, elaborate
ornamentation, and a sense of yearning that's unmistakable once you've
heard it. Think of the oud-driven classical traditions of Umm Kulthum
and Fairuz, the call to prayer, Sufi devotional music, and the
underpinning of much Middle Eastern and North African popular music
today.

The Arabic system uses **solfège-based names** (Do, Re, Mi, Fa, Sol, La, Si)
and organizes scales into **maqamat** (plural of `maqam <https://en.wikipedia.org/wiki/Maqam>`_).

.. note::

   True maqam music uses quarter-tones that cannot be represented in
   12-tone equal temperament. These scales are the closest 12-TET
   approximations.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> do = TonedScale(tonic="Do4", system="arabic")

   >>> do["ajam"].note_names     # = major scale
   ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si', 'Do']

   >>> do["hijaz"].note_names    # characteristic augmented 2nd
   ['Do', 'Reb', 'Mi', 'Fa', 'Sol', 'Solb', 'Sib', 'Do']

   >>> do["nikriz"].note_names
   ['Do', 'Re', 'Mib', 'Fa#', 'Sol', 'La', 'Sib', 'Do']

**Maqamat:** ajam, nahawand, kurd, hijaz, nikriz, bayati, rast, saba,
sikah, jiharkah

Japanese
--------

Japan's traditional scales have a hauntingly beautiful quality that is
immediately recognizable — dark, sparse, and full of tension. The
pentatonic scales (especially *hirajoshi* and *in*) use semitone steps
that give them an unmistakably Japanese character, distinct from the
wider-spaced pentatonics found in Chinese and Western folk music.
You'll hear these scales in `koto <https://en.wikipedia.org/wiki/Koto_(instrument)>`_
and `shamisen <https://en.wikipedia.org/wiki/Shamisen>`_ music, the
`gagaku <https://en.wikipedia.org/wiki/Gagaku>`_ court orchestra,
Kabuki and Noh theater, taiko drumming, anime and video game
soundtracks, and the compositions of Toru Takemitsu.

The Japanese system uses Western note names with traditional pentatonic
and heptatonic scales from Japanese music.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4", system="japanese")

   >>> c["hirajoshi"].note_names  # most iconic Japanese scale
   ['C', 'D', 'Eb', 'G', 'Ab', 'C']

   >>> c["in"].note_names         # Miyako-bushi, used in koto music
   ['C', 'Db', 'F', 'G', 'Ab', 'C']

   >>> c["yo"].note_names         # folk music scale
   ['C', 'D', 'F', 'G', 'A#', 'C']

   >>> c["ritsu"].note_names      # gagaku court music (= Dorian)
   ['C', 'D', 'Eb', 'F', 'G', 'A', 'Bb', 'C']

**Pentatonic scales:** hirajoshi, in, yo, iwato, kumoi, insen

**Heptatonic scales:** ritsu, ryo

Blues and Pentatonic
--------------------

The blues is America's deepest musical root — born from the African
American experience in the Mississippi Delta, it gave rise to jazz,
rock and roll, R&B, soul, funk, and hip-hop. The *blue note* (a
flattened 5th that bends between major and minor) is the sound of
emotional truth in music, from Robert Johnson to B.B. King to
Jimi Hendrix.

The blues system provides the scales foundational to blues, rock, jazz,
and folk music worldwide. `Pentatonic scales <https://en.wikipedia.org/wiki/Pentatonic_scale>`_ (5 notes) are the oldest
known musical scales, found independently in cultures across every
continent.

The `blues scale <https://en.wikipedia.org/wiki/Blues_scale>`_ adds the "`blue note <https://en.wikipedia.org/wiki/Blue_note>`_" (flat 5th / sharp 4th) to the
minor pentatonic — this chromatic passing tone is the defining sound
of the blues.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> c = TonedScale(tonic="C4", system="blues")

   >>> c["major pentatonic"].note_names  # the "happy" pentatonic
   ['C', 'D', 'E', 'G', 'A', 'C']

   >>> c["minor pentatonic"].note_names  # the "sad" pentatonic
   ['C', 'D#', 'F', 'G', 'A#', 'C']

   >>> c["blues"].note_names             # minor pentatonic + blue note
   ['C', 'Eb', 'F', 'Gb', 'G', 'Bb', 'C']

   >>> c["major blues"].note_names       # major pentatonic + blue note
   ['C', 'D', 'Eb', 'E', 'G', 'A', 'C']

**Pentatonic:** major pentatonic, minor pentatonic

**Hexatonic:** blues, major blues

**Heptatonic:** dominant (Mixolydian — the dominant 7th sound),
minor (Dorian — the jazz minor sound)


Javanese Gamelan
----------------

`Gamelan <https://en.wikipedia.org/wiki/Gamelan>`_ is the shimmering,
interlocking percussion orchestra of Java and Bali — one of the most
otherworldly sounds in all of music. Ensembles of bronze metallophones,
gongs, drums, and bamboo flutes create waves of resonance that
influenced Claude Debussy, Steve Reich, and countless ambient and
electronic artists. Each gamelan is tuned uniquely, so no two
ensembles sound exactly alike. The music is communal, ceremonial, and
deeply tied to Javanese and Balinese culture — it accompanies
shadow puppet theater (*wayang*), dance, and religious ritual.

The gamelan system approximates the scales of the Javanese and Balinese
gamelan orchestra in 12-tone equal temperament. True gamelan tuning is
unique to each ensemble and does not conform to Western intonation —
these are the closest 12-TET approximations.

`Slendro <https://en.wikipedia.org/wiki/Slendro>`_ is a roughly equal 5-tone division of the octave, producing
an ethereal, floating quality. `Pelog <https://en.wikipedia.org/wiki/Pelog>`_ is a 7-tone scale with unequal
intervals, typically performed using 5-note subsets called *pathet*.

.. code-block:: pycon

   >>> from pytheory import TonedScale

   >>> ji = TonedScale(tonic="ji4", system="gamelan")

   >>> ji["slendro"].note_names      # the 5-tone equidistant scale
   ['ji', 'ro', 'pat', 'mo', 'pi', 'ji']

   >>> ji["pelog"].note_names         # full 7-tone pelog
   ['ji', 'ro-', 'lu', 'pat', 'mo', 'nem-', 'barang', 'ji']

   >>> ji["pelog nem"].note_names     # pathet nem subset
   ['ji', 'ro-', 'lu', 'pat', 'mo', 'ji']

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

.. code-block:: pycon

   >>> from pytheory import TonedScale, Tone

   >>> # These are all the same scale with different names
   >>> western = TonedScale(tonic="C4")["major"]
   >>> indian  = TonedScale(tonic="Sa4", system="indian")["bilawal"]
   >>> arabic  = TonedScale(tonic="Do4", system="arabic")["ajam"]

   >>> # Same pitches
   >>> c4 = Tone.from_string("C4", system="western")
   >>> sa4 = Tone.from_string("Sa4", system="indian")
   >>> do4 = Tone.from_string("Do4", system="arabic")

   >>> c4.frequency
   261.6255653005986
   >>> sa4.frequency
   261.6255653005986
   >>> do4.frequency
   261.6255653005986

Microtonal Systems
------------------

Beyond the six 12-TET core systems, PyTheory includes 10 microtonal
systems that use their own native tunings — more notes per octave,
just intonation ratios, or entirely alien pitch structures.

Shruti (22 tones per octave)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Indian 22-shruti system divides the octave into 22 unequal steps
using just intonation ratios. These microtonal inflections are what
give classical Indian music its characteristic expressiveness — pitches
that fall "between the cracks" of the piano.

.. code-block:: python

   score = Score("4/4", bpm=75, system="shruti")

Maqam (24 tones per octave)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Arabic 24-tone system adds Zalzalian quarter-tone intervals
(derived from just intonation ratios of 11 and 13) to the standard
12 tones. These "neutral" intervals — halfway between major and minor —
are the soul of maqam music.

.. code-block:: python

   score = Score("4/4", bpm=90, system="maqam")

Slendro (5-TET)
~~~~~~~~~~~~~~~~

The Javanese slendro scale — 5 equal divisions of the octave. Each
step is 240 cents, wider than any Western interval. Ethereal and
floating.

Pelog (9-TET)
~~~~~~~~~~~~~

Approximation of the Javanese pelog tuning as 9 equal divisions of
the octave.

Thai (7-TET)
~~~~~~~~~~~~~

Thai classical music divides the octave into 7 equal steps of ~171
cents each — every interval is the same size.

Makam (53-TET)
~~~~~~~~~~~~~~

Turkish makam music uses 53 equal divisions of the octave — fine
enough to approximate virtually any just interval. The system that
underlies Ottoman classical music.

Carnatic (72-TET)
~~~~~~~~~~~~~~~~~

South Indian Carnatic music theory describes 72 melakarta ragas.
The 72-TET system provides enough resolution to represent all the
microtonal inflections of Carnatic practice.

19-TET and 31-TET
~~~~~~~~~~~~~~~~~~

Extended equal temperaments that offer better approximations of
just intonation intervals than 12-TET. 19-TET has excellent major
thirds; 31-TET closely matches quarter-comma meantone.

.. code-block:: python

   score = Score("4/4", bpm=100, system="19-tet")

Bohlen-Pierce (13 equal divisions of the tritave)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A genuinely alien tuning system — 13 equal divisions of the
**tritave** (3:1 ratio) instead of the octave (2:1). No octaves, no
fifths, built on 3:5:7 harmonics. Used by experimental composers.

.. code-block:: python

   score = Score("4/4", bpm=100, system="bohlen-pierce")

The TET() Factory
~~~~~~~~~~~~~~~~~

Create any equal temperament on the fly with the ``TET()`` factory:

.. code-block:: python

   from pytheory import TET

   edo19 = TET(19)   # 19-tone equal temperament
   edo31 = TET(31)   # 31-tone equal temperament
   score = Score("4/4", bpm=100, system=edo19)

Tone names in custom TET systems are integers (0, 1, 2, ..., n-1).

System.tone() Method
~~~~~~~~~~~~~~~~~~~~

Any system can create a Tone directly:

.. code-block:: python

   from pytheory import SYSTEMS

   western = SYSTEMS["western"]
   c4 = western.tone("C", octave=4)

Music is universal, but every culture hears it differently. These systems are different maps of the same territory -- explore one you've never played in before and see what you find.
