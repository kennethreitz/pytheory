Audio Playback
==============

PyTheory includes a complete audio engine — synthesize tones, chords,
drum patterns, and multi-part arrangements, then play them through your
speakers or save to WAV/MIDI. No samples or external audio files needed;
everything is generated from waveforms and envelopes.

.. note::

   Audio playback requires `PortAudio <http://www.portaudio.com/>`_ to be
   installed on your system. On macOS: ``brew install portaudio``.
   On Ubuntu: ``apt install libportaudio2``.

Quick Start
-----------

The simplest thing you can do:

.. code-block:: pycon

   >>> from pytheory import Tone, Chord, play
   >>> play(Tone.from_string("A4"), t=1_000)          # A440 for 1 second
   >>> play(Chord.from_symbol("Am7"), t=2_000)         # chord for 2 seconds

The most expressive thing you can do:

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score
   >>> score = Score("4/4", bpm=140)
   >>> score.add_pattern(Pattern.preset("bossa nova"), repeats=4)
   >>> chords = score.part("chords", synth="sine", envelope="pad")
   >>> lead = score.part("lead", synth="saw", envelope="pluck")
   >>> bass = score.part("bass", synth="triangle", envelope="pluck")
   >>> for sym in ["Am", "Dm", "E7", "Am"]:
   ...     chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   >>> lead.add("E5", 0.67).add("D5", 0.33).add("C5", 1.0)
   >>> bass.add("A2", Duration.HALF).add("E2", Duration.HALF)
   >>> play_score(score)

Everything between those two extremes is documented below.

Playing a Tone
--------------

.. code-block:: pycon

   >>> from pytheory import Tone, play

   >>> a4 = Tone.from_string("A4", system="western")
   >>> play(a4, t=1_000)   # Play A440 for 1 second

Playing a Chord
---------------

.. code-block:: pycon

   >>> from pytheory import Chord, play

   >>> # From a chord name
   >>> play(Chord.from_name("Am7"), t=2_000)

   >>> # From note names
   >>> play(Chord.from_tones("C", "E", "G"), t=2_000)

Waveform Types
--------------

The waveform shape determines the `timbre <https://en.wikipedia.org/wiki/Timbre>`_ (tonal color) of the sound.
Different waveforms contain different combinations of **harmonics** —
integer multiples of the fundamental frequency.

- `Sine wave <https://en.wikipedia.org/wiki/Sine_wave>`_ — the purest tone. Contains only the fundamental
  frequency with no harmonics. Sounds smooth, clear, and "electronic."
  This is the building block of all other waveforms (`Fourier's theorem <https://en.wikipedia.org/wiki/Fourier_series>`_).

- `Sawtooth wave <https://en.wikipedia.org/wiki/Sawtooth_wave>`_ — contains all harmonics (both odd and even),
  each at amplitude 1/n. Sounds bright, buzzy, and aggressive.
  Named for its shape. Used extensively in `additive synthesis <https://en.wikipedia.org/wiki/Additive_synthesis>`_ and analog synthesizers.

- `Triangle wave <https://en.wikipedia.org/wiki/Triangle_wave>`_ — contains only odd harmonics, each at amplitude
  1/n². Sounds softer and more mellow than sawtooth — somewhere between
  sine and sawtooth. Often described as "woody" or "hollow."

.. code-block:: pycon

   >>> from pytheory import play, Synth, Tone

   >>> tone = Tone.from_string("C4", system="western")

   >>> play(tone, synth=Synth.SINE)      # Pure, clean
   >>> play(tone, synth=Synth.SAW)       # Bright, buzzy
   >>> play(tone, synth=Synth.TRIANGLE)  # Mellow, hollow

Temperaments
------------

Hear the difference between tuning systems:

.. code-block:: pycon

   >>> play(tone, temperament="equal")        # Modern standard (since ~1917)
   >>> play(tone, temperament="pythagorean")  # Pure fifths, wolf intervals
   >>> play(tone, temperament="meantone")     # Pure thirds, Renaissance sound

Try playing a C major chord in each temperament — you'll hear subtle
differences in the "color" of the major third. Equal temperament is
a compromise; the other systems sacrifice some keys to make the good
keys sound better.

Chord Progressions
-------------------

Play an entire chord progression in sequence with a single call:

.. code-block:: pycon

   >>> from pytheory import Key, play_progression

   >>> chords = Key("C", "major").progression("I", "V", "vi", "IV")
   >>> play_progression(chords, t=800)

You can customize the waveform and the gap (silence) between chords:

.. code-block:: pycon

   >>> from pytheory import Synth

   >>> play_progression(chords, t=1000, synth=Synth.TRIANGLE, gap=200)

Saving to WAV
-------------

Render tones or chords to a WAV file instead of playing them live.
This works even without speakers or PortAudio:

.. code-block:: pycon

   >>> from pytheory import save, Chord, Tone, Synth

   >>> # Save a single tone
   >>> save(Tone.from_string("A4"), "a440.wav", t=1_000)

   >>> # Save a chord
   >>> save(Chord.from_name("Am7"), "am7.wav", t=2_000)

   >>> # Choose waveform and temperament
   >>> save(Chord.from_name("C"), "c_triangle.wav",
   ...      synth=Synth.TRIANGLE, temperament="meantone", t=3_000)

ADSR Envelopes
--------------

Raw waveforms click at the start and end of each note. An
`ADSR envelope <https://en.wikipedia.org/wiki/Envelope_(music)>`_ shapes
the amplitude over time for natural-sounding notes:

- **Attack** — how quickly the sound reaches full volume
- **Decay** — how quickly it drops to the sustain level
- **Sustain** — the held volume while the note is on
- **Release** — how quickly it fades to silence

PyTheory includes 8 presets:

.. code-block:: pycon

   >>> from pytheory import play, Envelope, Tone

   >>> tone = Tone.from_string("C4", system="western")
   >>> play(tone, envelope=Envelope.PIANO)     # Quick attack, natural decay
   >>> play(tone, envelope=Envelope.PAD)       # Slow fade in, lush
   >>> play(tone, envelope=Envelope.PLUCK)     # Sharp attack, fast decay
   >>> play(tone, envelope=Envelope.BELL)      # Instant attack, long ring
   >>> play(tone, envelope=Envelope.STRINGS)   # Gradual bow
   >>> play(tone, envelope=Envelope.ORGAN)     # Instant on/off
   >>> play(tone, envelope=Envelope.STACCATO)  # Short and punchy
   >>> play(tone, envelope=Envelope.NONE)      # Raw waveform (old behavior)

Envelopes work with all functions — ``play()``, ``save()``, and
``play_progression()``:

.. code-block:: pycon

   >>> from pytheory import Key, play_progression, Envelope
   >>> chords = Key("C", "major").progression("I", "V", "vi", "IV")
   >>> play_progression(chords, t=2000, envelope=Envelope.PAD)

Playing a Score
---------------

A ``Score`` combines drum patterns, chord pads, melody leads, bass lines,
and any number of named parts — each with its own synth voice — into a
single playable arrangement.

.. code-block:: pycon

   >>> from pytheory import Score, Pattern, Key, Duration, Chord
   >>> from pytheory.play import play_score

   >>> score = Score("4/4", bpm=140)
   >>> score.add_pattern(Pattern.preset("bossa nova"), repeats=4)

   >>> chords = score.part("chords", synth="sine", envelope="pad", volume=0.3)
   >>> lead   = score.part("lead",   synth="triangle", envelope="pluck", volume=0.5)
   >>> bass   = score.part("bass",   synth="sine", envelope="pluck", volume=0.45)

   >>> for sym in ["Am", "Dm", "E7", "Am"]:
   ...     chords.add(Chord.from_symbol(sym), Duration.WHOLE)
   ...     chords.add(Chord.from_symbol(sym), Duration.WHOLE)

   >>> lead.add("E5", 0.67).add("D5", 0.33).add("C5", 1.0).rest(0.5)

   >>> for n in ["A2", "E2", "A2", "C3", "D2", "A2", "D2", "F2"]:
   ...     bass.add(n, Duration.QUARTER)

   >>> play_score(score)

More examples:

.. code-block:: pycon

   >>> # Salsa with a ii-V-I — saw lead over clave
   >>> score = Score("4/4", bpm=180)
   >>> score.add_pattern(Pattern.preset("salsa"), repeats=4)
   >>> chords = score.part("chords", synth="sine", envelope="pad")
   >>> lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
   >>> for chord in Key("C", "major").progression("ii", "V", "I", "I") * 2:
   ...     chords.add(chord, Duration.WHOLE)
   >>> lead.add("D5", 0.67).add("F5", 0.33).add("A5", 1.0)
   >>> play_score(score)

   >>> # Jazz ballad — triangle lead, walking bass
   >>> score = Score("4/4", bpm=90)
   >>> score.add_pattern(Pattern.preset("jazz"), repeats=8)
   >>> pads = score.part("pads", synth="sine", envelope="pad", volume=0.3)
   >>> lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.5)
   >>> bass = score.part("bass", synth="sine", envelope="pluck", volume=0.4)
   >>> for chord in Key("Bb", "major").progression("I", "vi", "ii", "V") * 2:
   ...     pads.add(chord, Duration.WHOLE)
   >>> play_score(score)

MIDI Export
-----------

Export tones, chords, or progressions as Standard MIDI Files. Unlike WAV,
MIDI files can be opened in any DAW, edited, transposed, and assigned to
any instrument:

.. code-block:: pycon

   >>> from pytheory import save_midi, Key, Tone, Chord

   >>> # Export a single tone
   >>> save_midi(Tone.from_string("C4"), "middle_c.mid", t=1000)

   >>> # Export a chord
   >>> save_midi(Chord.from_symbol("Am7"), "am7.mid")

   >>> # Export a progression
   >>> chords = Key("C", "major").progression("I", "V", "vi", "IV")
   >>> save_midi(chords, "pop.mid", t=500, bpm=120)
