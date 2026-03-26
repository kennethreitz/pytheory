Musical Systems
===============

PyTheory supports **six musical systems**, each with its own tone names,
scale patterns, and centuries of tradition behind them. Every system
maps onto the same 12-tone equal temperament backbone, so you can
compare scales across cultures and even combine them in your own music.

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

Music is universal, but every culture hears it differently. These systems are different maps of the same territory -- explore one you've never played in before and see what you find.
