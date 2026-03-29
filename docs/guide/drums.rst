Drums
=====

Drums are the foundation of almost everything. Change the drum pattern
and you change the genre. The same four chords over a bossa nova
pattern sound like you're in a cafe in Rio. Put those same chords over
a rock beat and you're in a garage in Seattle. Over a trap beat, you're
in Atlanta. Over a dancehall pattern, you're in Kingston. The drums ARE
the genre -- they tell the listener's body how to move before a single
melodic note is played.

PyTheory includes a complete drum system -- 51 synthesized percussion
sounds, 95+ pattern presets across dozens of genres, and 30 fill presets.
Every sound is generated from waveforms; no samples needed.

Drum Sounds
-----------

Drum hits are **humanized by default** — each hit gets a tiny random
timing offset and velocity wobble, just like a real drummer who's never
perfectly on the grid. Control the amount with ``drum_humanize`` on the
Score:

.. code-block:: python

   score = Score("4/4", bpm=120, drum_humanize=0.4)   # natural feel
   score = Score("4/4", bpm=120, drum_humanize=0.0)   # perfectly quantized
   score = Score("4/4", bpm=120, drum_humanize=0.1)   # studio tight

The default is 0.15 — just enough to feel alive without sounding loose.

Drums Are Parts
~~~~~~~~~~~~~~~~

Drums are a real Part — the same as any melodic voice. You can set
effects on them the same way:

.. code-block:: python

   score.drums("rock", repeats=4)
   score.parts["drums"].reverb_mix = 0.2
   score.parts["drums"].reverb_type = "plate"

Or use the shorthand:

.. code-block:: python

   score.set_drum_effects(reverb=0.2, reverb_type="plate", lowpass=8000)

Split Drums
~~~~~~~~~~~

For maximum control, split the kit into separate Parts — kick, snare,
hats, toms, cymbals, and percussion — each with independent effects:

.. code-block:: python

   score.drums("rock", repeats=4, split=True)

   # Now each group is its own Part
   score.parts["snare"].reverb_mix = 0.3
   score.parts["snare"].reverb_type = "plate"
   score.parts["hats"].lowpass = 7000
   score.parts["kick"]  # dry, no effects

   # set_drum_effects still works — applies to all drum Parts
   score.set_drum_effects(reverb=0.1)

This is how real studios work — the snare gets its own reverb send,
the hats get their own EQ, the kick stays dry and punchy. Now you
can do the same thing in Python.

Sidechain compression triggers on kick hits only — hi-hats and snares
don't duck the pad.

Every drum sound is stereo-panned like a real kit — kick and snare
center, hi-hat right, crash left, toms spread across the field,
percussion instruments placed naturally. Put on headphones and you'll
hear the kit in front of you.

The ``DrumSound`` enum maps to General MIDI percussion note numbers:

.. code-block:: pycon

   >>> from pytheory import DrumSound

   >>> DrumSound.KICK.value
   36
   >>> DrumSound.SNARE.value
   38
   >>> DrumSound.CLOSED_HAT.value
   42

All 51 sounds, organized by type:

**Kicks:** KICK (36)

**Snares:** SNARE (38), RIMSHOT (37), CLAP (39)

**Hi-hats:** CLOSED_HAT (42), OPEN_HAT (46), PEDAL_HAT (44)

**Toms:** LOW_TOM (45), MID_TOM (47), HIGH_TOM (50)

**Cymbals:** CRASH (49), RIDE (51), RIDE_BELL (53)

**Percussion:** COWBELL (56), CLAVE (75), SHAKER (70), TAMBOURINE (54),
CONGA_HIGH (63), CONGA_LOW (64), BONGO_HIGH (60), BONGO_LOW (61),
TIMBALE_HIGH (65), TIMBALE_LOW (66), AGOGO_HIGH (67), AGOGO_LOW (68),
GUIRO (73)

**Tabla:** TABLA_NA (86), TABLA_TIN (87), TABLA_GE (88), TABLA_DHA (89),
TABLA_TIT (90), TABLA_KE (91), TABLA_GE_BEND (108 -- bayan with upward
pitch bend from palm pressing into the head)

**Dhol:** DHOL_DAGGA (92), DHOL_TILLI (93), DHOL_BOTH (94)

**Dholak:** DHOLAK_GE (95), DHOLAK_NA (96), DHOLAK_TIT (97)

**Mridangam:** MRIDANGAM_THAM (98), MRIDANGAM_NAM (99), MRIDANGAM_DIN (100),
MRIDANGAM_THA (101)

**Djembe:** DJEMBE_BASS (102), DJEMBE_TONE (103), DJEMBE_SLAP (104)

**Cajón:** CAJON_BASS (108), CAJON_SLAP (109), CAJON_TAP (110)

**Metal Kit:** METAL_KICK (105), METAL_SNARE (106), METAL_HAT (107)

**Marching Snare:** MARCH_SNARE (115), MARCH_RIMSHOT (116), MARCH_CLICK (118)

**Quads (Tenors):** QUAD_1 (119), QUAD_2 (120), QUAD_3 (121), QUAD_4 (122),
QUAD_SPOCK (123)

**Marching Bass:** BASS_1 (124), BASS_2 (125), BASS_3 (126), BASS_4 (127),
BASS_5 (80)

Drum Synthesis
--------------

Every drum sound here is synthesized from scratch using the same
techniques that real drum machines use. This isn't a shortcut -- it's
the real thing. The 808 kick that defined hip hop is literally a sine
wave with a pitch envelope sweeping from 150 Hz down to 50 Hz. The 909
snare that powered techno is a sine wave body mixed with white noise
rattle. The hi-hat is just filtered noise with a short decay. When
Roland built the TR-808 and TR-909, they weren't sampling real drums;
they were synthesizing them from basic waveforms. PyTheory does the
same thing.

Each sound has a dedicated synthesizer:

- **KICK** -- sine wave with pitch envelope sweep (150 to 50 Hz) + sub click
- **SNARE** -- pitched body (180 Hz) + white noise rattle
- **CLOSED_HAT** -- high-frequency noise, 50ms decay
- **OPEN_HAT** -- high-frequency noise, 250ms decay
- **CLAP** -- layered noise bursts with spacers
- **RIMSHOT** -- bright 800 Hz click + noise
- **TOMS** -- pitched sine with sweep (low=100, mid=150, high=200 Hz)
- **CRASH** -- long noise decay (1.5s)
- **RIDE** -- metallic ring (3500+5100 Hz) + noise
- **RIDE_BELL** -- brighter ring, more sustain
- **COWBELL** -- two detuned tones (545+815 Hz)
- **CLAVE** -- short 2500 Hz click
- **CONGAS/BONGOS** -- pitched membrane with slap transient
- **TIMBALES** -- bright metallic ring with overtones
- **AGOGO** -- pitched bell with harmonics
- **SHAKER/MARACAS** -- short noise burst
- **TAMBOURINE** -- noise + 7000 Hz jingle ring
- **GUIRO** -- scraped noise bursts

Pattern Presets
---------------

80+ patterns spanning genres from rock to Afro-Cuban to electronic to
world percussion. Load them with ``Pattern.preset()``:

.. code-block:: pycon

   >>> from pytheory import Pattern

   >>> Pattern.list_presets()
   ['12/8 blues', '6/8 afro-cuban', 'afrobeat', 'baiao', 'bebop', ...]

   >>> rock = Pattern.preset("rock")
   >>> rock
   <Pattern 'rock' 4/4 4.0 beats 12 hits>

**Rock/Pop:** rock, half time, double time, disco, motown, train beat
-- The backbone of Western popular music. Kick on 1 and 3, snare on 2
and 4. Simple, effective, universal.

**Jazz:** jazz, bebop, shuffle, swing, linear, paradiddle -- The ride
cymbal drives everything. The kick and snare comp and converse rather
than keeping strict time. These patterns swing.

**Latin:** salsa, bossa nova, samba, cumbia, merengue, baiao, maracatu,
bolero, tango -- Rich, layered patterns built on clave rhythms, with
congas, timbales, and shakers creating interlocking polyrhythmic webs.
Some of the most sophisticated drumming traditions on the planet.

**Afro-Cuban:** son clave 3-2, son clave 2-3, rumba clave 3-2,
rumba clave 2-3, cascara, guaguanco, mozambique, nanigo, bembe,
6/8 afro-cuban, tresillo, habanera -- The clave is the key that
unlocks all Latin and Afro-Cuban music. It's a five-note rhythmic
cell that everything else revolves around. If you learn one concept
from world music, learn the clave.

**African:** afrobeat, highlife -- Born in West Africa. Fela Kuti's
afrobeat layers multiple percussion voices into hypnotic,
polyrhythmic grooves that can go on for twenty minutes.

**Caribbean:** reggae, dancehall, ska, dub -- The offbeat is king.
Reggae flips rock drumming inside out by emphasizing the "and" of each
beat instead of the beat itself. Ska doubles the tempo, dancehall
adds syncopation.

**Electronic:** house, techno, trap, drum and bass, breakbeat, jungle
-- Machine music. The four-on-the-floor kick of house and techno, the
rattling hi-hats of trap, the breakneck tempo of drum and bass. These
patterns were born in drum machines and they still live there.

**Metal/Punk:** metal, blast beat, punk, double kick, metal blast,
metal groove, metal gallop -- Speed and aggression. The blast beat is
both feet and both hands going as fast as humanly possible. Punk strips
everything to its essentials. The metal kit adds 3 dedicated sounds
(double kick, china cymbal, stack) and 4 patterns for extreme metal
subgenres.

**World Percussion:** tabla, dhol, dholak, mridangam, djembe, cajón --
Deep traditions from across the globe, each with authentic sound sets and
idiomatic patterns. See the World Percussion section below for details.

**Other:** funk, hip hop, bo diddley, second line, new orleans, waltz,
12/8 blues, country, gospel, flamenco -- Everything else. The syncopated
groove of funk, the sampled feel of hip hop, the street-parade swing
of New Orleans second line.

Playing Patterns
----------------

``play_pattern()`` synthesizes every drum sound in real-time:

.. code-block:: python

   from pytheory import Pattern
   from pytheory.play import play_pattern

   play_pattern(Pattern.preset("rock"), repeats=4, bpm=120)
   play_pattern(Pattern.preset("bossa nova"), repeats=4, bpm=140)
   play_pattern(Pattern.preset("salsa"), repeats=4, bpm=180)
   play_pattern(Pattern.preset("afrobeat"), repeats=8, bpm=110)

Rock:

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1em"><source src="../_static/audio/rock_beat.wav" type="audio/wav"></audio>

Bossa nova:

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1em"><source src="../_static/audio/bossa_nova_pattern.wav" type="audio/wav"></audio>

Salsa:

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1em"><source src="../_static/audio/salsa_pattern.wav" type="audio/wav"></audio>

Afrobeat:

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/afrobeat_pattern.wav" type="audio/wav"></audio>

Fills
-----

A fill is the drummer's way of saying "something's about to change."
It's that moment at the end of a verse where the drummer breaks the
pattern and rolls around the toms before crashing into the chorus. Fills
signal transitions -- they tell the listener's ear that the section is
ending and a new one is about to begin. Without fills, a drum pattern
just loops. With them, it breathes and has structure.

``Pattern.fill()`` loads a 1-bar drum fill -- a short break that
transitions between sections. 30 fill presets are available:

.. code-block:: pycon

   >>> Pattern.list_fills()
   ['afrobeat', 'blast', 'bossa nova', 'breakdown', 'buildup',
    'cajon breakdown', 'cajon flam', 'cajon rumble',
    'cumbia', 'disco', 'djembe break', 'djembe call', 'djembe roll',
    'funk', 'highlife', 'hip hop', 'house',
    'jazz', 'jazz brush', 'metal', 'metal blast', 'metal cascade',
    'metal triplet', 'reggae', 'rock', 'rock crash',
    'salsa', 'samba', 'second line', 'trap']

   >>> fill = Pattern.fill("rock")
   >>> fill
   <Pattern 'rock fill' 4/4 4.0 beats ...>

Score Integration
-----------------

The ``score.drums()`` shorthand attaches a drum pattern to a score:

.. code-block:: python

   from pytheory import Score

   score = Score("4/4", bpm=140)
   score.drums("bossa nova", repeats=4)

Auto-Fills
~~~~~~~~~~

The ``fill`` and ``fill_every`` parameters automatically insert drum
fills at regular intervals:

.. code-block:: python

   score = Score("4/4", bpm=120)
   score.drums("rock", repeats=8, fill="rock", fill_every=4)

This plays the rock pattern for 8 bars, replacing every 4th bar with
a rock fill. Useful for adding natural phrasing to longer sections.

.. code-block:: python

   # Jazz with brush fills every 8 bars
   score.drums("bebop", repeats=16, fill="jazz brush", fill_every=8)

   # Salsa with fills every 4 bars
   score.drums("salsa", repeats=8, fill="salsa", fill_every=4)

Layering Patterns
-----------------

Combine drum patterns with melodic parts for full arrangements. The
drum pattern and all named parts are mixed together by ``play_score()``:

.. code-block:: python

   from pytheory import Score, Key, Duration, Chord
   from pytheory.play import play_score

   score = Score("4/4", bpm=180)
   score.drums("salsa", repeats=4, fill="salsa", fill_every=4)

   pads = score.part("pads", synth="sine", envelope="pad", volume=0.3)
   lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
   bass = score.part("bass", synth="sine", envelope="pluck", volume=0.45)

   for chord in Key("D", "minor").progression("ii", "V", "i", "i") * 2:
       pads.add(chord, Duration.WHOLE)

   lead.add("A5", 0.67).add("G5", 0.33).add("F5", 0.67).add("E5", 0.33)

   for n in ["D2", "A2", "D2", "F2"] * 2:
       bass.add(n, Duration.QUARTER)

   play_score(score)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/salsa_layered.wav" type="audio/wav"></audio>

World Percussion
----------------

PyTheory includes dedicated sound sets and pattern presets for
traditional percussion instruments from around the world. Each
instrument has its own synthesized sounds that capture the timbral
character of the real instrument, plus idiomatic rhythmic patterns
drawn from their musical traditions.

Tabla
~~~~~

The tabla is a pair of hand drums from the Indian subcontinent -- the
smaller, higher-pitched *dayan* and the larger, bass *bayan*. It is
the rhythmic backbone of Hindustani classical music, and one of the
most expressive percussion instruments ever created. A single tabla
player can produce an astonishing range of tones by varying finger
placement, pressure, and striking technique.

**7 sounds** -- covering the primary tabla strokes (na, tin, tun, ge,
dha, ke, tit) plus a bayan pitch bend sound (TABLA_GE_BEND) that
models the technique of pressing the palm into the bayan head to bend
the pitch upward.

**7 patterns:** teental (16 beats, the most common taal), jhaptaal
(10 beats), rupak (7 beats), dadra (6 beats), keherwa (8 beats, folk
and light classical), tabla solo, and tiri kita (fast ornamental
pattern).

**5 fills:** tihai (3x crescendo landing on sam), chakkardar (32nd
triplet cascade into slam), tiri kita (rapid 16th-note dayan burst),
bayan (deep bass bends showcase), tabla call (dayan/bayan call-and-response).

.. code-block:: python

   score.drums("teental", repeats=4, fill="tihai")
   score.drums("keherwa", repeats=4, fill="chakkardar")

.. code-block:: python

   score = Score("4/4", bpm=80)
   score.drums("teental", repeats=4)

Dhol
~~~~

The dhol is a double-headed barrel drum from Punjab, played with
sticks. It is the driving force behind bhangra music -- loud,
energetic, and physically impossible to sit still to.

**3 sounds** -- bass stroke, treble stroke, and rimshot.

**2 patterns:** bhangra (the classic bhangra groove) and dhol chaal
(a processional rhythm).

.. code-block:: python

   score = Score("4/4", bpm=160)
   score.drums("bhangra", repeats=4)

Dholak
~~~~~~

The dholak is a smaller, lighter two-headed drum used across South
Asia in folk music, qawwali, and Bollywood. Played with bare hands,
it produces a warm, melodic tone.

**3 sounds** -- bass, treble, and slap.

**2 patterns:** qawwali (the rhythmic foundation of Sufi devotional
music) and dholak folk (a general folk groove).

.. code-block:: python

   score = Score("4/4", bpm=120)
   score.drums("qawwali", repeats=4)

Mridangam
~~~~~~~~~

The mridangam is a double-headed drum from South India, the
rhythmic anchor of Carnatic classical music. Its tuning system is
extraordinarily precise, and its rhythmic vocabulary is among the
most mathematically complex in the world.

**4 sounds** -- tha, thom, nam, and din.

**2 patterns:** adi talam (the most common Carnatic talam, 8 beats)
and mridangam korvai (a rhythmic cadence pattern).

.. code-block:: python

   score = Score("4/4", bpm=90)
   score.drums("adi talam", repeats=4)

Djembe
~~~~~~

The djembe is a rope-tuned goblet drum from West Africa, capable of
producing a wide range of tones from deep bass to sharp slaps. It is
central to the drum ensemble traditions of Mali, Guinea, and Senegal.

**3 sounds** -- bass (open center strike), tone (edge strike), and
slap (sharp edge strike).

**8 patterns:** djembe (basic accompanying rhythm), kuku (Guinean harvest
dance), soli (powerful Mandinka rhythm), dununba (heavy bass-driven),
tiriba (joyful Susu rhythm), yankadi (gentle greeting/welcome), djansa
(fast Malinke dance), mendiani (women's celebratory dance).

**3 fills:** djembe call (bass-tone-slap conversation building to climax),
djembe roll (rapid slaps accelerating into bass), djembe break (syncopated
West African-style break).

.. code-block:: python

   score = Score("4/4", bpm=120)
   score.drums("djembe", repeats=8, fill="djembe call", fill_every=4)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/djembe.wav" type="audio/wav"></audio>

Metal Kit
~~~~~~~~~

A dedicated percussion kit for extreme metal subgenres, with
specialized sounds and patterns that go beyond the standard drum kit.

**3 sounds** -- double kick (triggered, tight attack), china cymbal,
and stack (a short, trashy cymbal choke).

**4 patterns:** double kick (relentless double bass drum pattern),
metal blast (blast beat with china cymbal accents), metal groove (a
half-time groove with double kick fills), and metal gallop (the
classic triplet-feel gallop rhythm).

**4 fills:** metal (double kick 16ths with descending toms), metal triplet
(double kick triplets with snare accents), metal blast (alternating
snare/kick 32nds into half-time crash), metal cascade (descending snare
roll → kick roll → alternating → crash ending).

.. code-block:: python

   score = Score("4/4", bpm=200)
   score.drums("metal blast", repeats=8, fill="metal cascade", fill_every=4)

Cajón
~~~~~

The cajón is a box-shaped percussion instrument from Peru, now
ubiquitous in acoustic and unplugged settings worldwide. Players sit
on the box and strike the front face with their hands.

**3 sounds** -- bass (deep center thump), slap (sharp, snare-like edge
hit with wire buzz), and tap (light finger tap).

**3 patterns:** cajon (basic groove), cajon rumba (flamenco-style rumba),
and cajon folk (folk/acoustic pattern).

**3 fills:** cajon flam (slaps accelerating into bass hits), cajon rumble
(fast taps building to slap accents), cajon breakdown (syncopated
bass-slap groove).

.. code-block:: python

   score = Score("4/4", bpm=100)
   score.drums("cajon", repeats=8, fill="cajon flam", fill_every=4)

Marching Percussion
~~~~~~~~~~~~~~~~~~~

A full drumline — snare, quads (tenors), and pitched bass drums.
Every sound is synthesized: kevlar snare heads, aluminum shell ting
on the quads, felt-beater thwack on the basses.

**Snare** -- 3 sounds: MARCH_SNARE (tight kevlar tap), MARCH_RIMSHOT
(woody-metallic crack), MARCH_CLICK (stick click for count-offs).

**Quads** -- 5 sounds: QUAD_1 through QUAD_4 (high to low pitched
tenors) plus QUAD_SPOCK (rim click on the shell).

**Bass drums** -- 5 pitched drums: BASS_1 (highest/smallest) through
BASS_5 (lowest/biggest), each with a prominent felt-beater thwack.

**6 patterns:** march (basic 4/4), cadence (8-beat street beat),
march paradiddle, march roll (buzz crescendo), quad sweep (run across
all 4 drums), quad groove, bass split (cascading across the line),
bass unison (all 5 hit together), drumline (snare + quads + bass).

**Rudiment methods:** ``Part.flam()``, ``Part.diddle()``, and
``Part.cheese()`` for marching rudiments on any drum sound.

**Ensemble rendering:** ``ensemble=N`` on any Part duplicates the
voice with per-player timing tendencies and micro pitch drift.
``ensemble=8`` for a snare line, ``ensemble=20`` for a massive section.

.. code-block:: python

   # Full drumline with ensemble
   snares = score.part("snares", synth="sine", volume=0.9,
                       reverb=0.2, ensemble=8)
   quads = score.part("quads", synth="sine", volume=0.5,
                      reverb=0.2, ensemble=4)
   basses = score.part("basses", synth="sine", volume=0.55,
                       reverb=0.2, ensemble=5)

   snares.flam(DrumSound.MARCH_SNARE, Duration.QUARTER, velocity=120)
   snares.diddle(DrumSound.MARCH_SNARE, Duration.EIGHTH, velocity=60)

   # Or use patterns
   score.drums("drumline", repeats=4)

.. raw:: html

   <audio controls style="width:100%;margin:0.5em 0 1.5em"><source src="../_static/audio/march_snare.wav" type="audio/wav"></audio>

**Sympathetic resonance:** The marching snare builds up snare wire
buzz as hits accumulate, and the buzz decays during rests — just like
a real drum.

MIDI Export
-----------

Convert any pattern to a Score, then export to MIDI (drums are written
to channel 10):

.. code-block:: python

   pattern = Pattern.preset("bossa nova")
   score = pattern.to_score(repeats=8, bpm=140)
   score.save_midi("bossa.mid")

   Pattern.preset("afrobeat").to_score(repeats=8, bpm=110).save_midi("afrobeat.mid")

Drums are the foundation. The same chords over a bossa nova feel like a different song than over a rock beat -- change the pattern and you change the genre. Try swapping presets under the same progression and hear how much the drums are really doing.
