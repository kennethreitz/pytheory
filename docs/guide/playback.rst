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
   >>> score.drums("bossa nova", repeats=4)
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
   >>> score.drums("bossa nova", repeats=4)

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
   >>> score.drums("salsa", repeats=4)
   >>> chords = score.part("chords", synth="sine", envelope="pad")
   >>> lead = score.part("lead", synth="saw", envelope="pluck", volume=0.4)
   >>> for chord in Key("C", "major").progression("ii", "V", "I", "I") * 2:
   ...     chords.add(chord, Duration.WHOLE)
   >>> lead.add("D5", 0.67).add("F5", 0.33).add("A5", 1.0)
   >>> play_score(score)

   >>> # Jazz ballad — triangle lead, walking bass
   >>> score = Score("4/4", bpm=90)
   >>> score.drums("jazz", repeats=8)
   >>> pads = score.part("pads", synth="sine", envelope="pad", volume=0.3)
   >>> lead = score.part("lead", synth="triangle", envelope="pluck", volume=0.5)
   >>> bass = score.part("bass", synth="sine", envelope="pluck", volume=0.4)
   >>> for chord in Key("Bb", "major").progression("I", "vi", "ii", "V") * 2:
   ...     pads.add(chord, Duration.WHOLE)
   >>> play_score(score)

Per-Part Effects
----------------

Each part can have its own effects chain — reverb, delay, lowpass filter,
and distortion. Effects are set at part creation and applied per-part
before mixing, so every voice gets independent processing.

The Effect Chain
~~~~~~~~~~~~~~~~

Effects are applied in this order, matching a real signal chain::

    Signal → Distortion → Lowpass Filter → Delay → Reverb → Mix

- **Distortion** first: drives the raw signal before filtering (like
  plugging a guitar into a fuzz pedal before the amp)
- **Lowpass** second: shapes the tone of the distorted signal (like
  the tone knob on an amp)
- **Delay** third: echoes the shaped signal (tap delay / tape echo)
- **Reverb** last: places everything in a space (room / hall)

Reverb
~~~~~~

`Schroeder reverb <https://en.wikipedia.org/wiki/Schroeder_reverberator>`_
using 4 parallel comb filters + 2 series allpass filters:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", envelope="pluck",
   ...                   reverb=0.3, reverb_decay=1.5)

- ``reverb``: Wet/dry mix, 0.0–1.0. Try 0.2–0.4 for subtle space,
  0.5–0.8 for ambient/dub.
- ``reverb_decay``: Tail length in seconds. 0.5 = small room,
  1.5 = hall, 3.0+ = cathedral/dub.

Delay
~~~~~

Tempo-synced echoes with feedback:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="triangle", envelope="strings",
   ...                   delay=0.3, delay_time=0.375, delay_feedback=0.4)

- ``delay``: Wet/dry mix, 0.0–1.0.
- ``delay_time``: Time between echoes in seconds. Musically useful
  values at 120 bpm: 0.25 (8th note), 0.375 (dotted 8th),
  0.5 (quarter note).
- ``delay_feedback``: How much each echo feeds back (0.0–1.0).
  0.3 = a few repeats, 0.5 = many, 0.7+ = runaway (dub style).

Lowpass Filter
~~~~~~~~~~~~~~

12 dB/octave `biquad lowpass <https://en.wikipedia.org/wiki/Low-pass_filter>`_
with resonance — the sound of analog synthesizers:

.. code-block:: pycon

   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   lowpass=400, lowpass_q=1.5)

- ``lowpass``: Cutoff frequency in Hz (0 = off). Reference points:
  200–400 Hz = deep sub bass, 800–1500 Hz = warm/muffled,
  2000–4000 Hz = present lead, 5000+ = subtle rolloff.
- ``lowpass_q``: Resonance / Q factor (default 0.707 = Butterworth flat).
  1.0 = slight peak, 2.0 = pronounced, 5.0+ = aggressive acid squelch.

Distortion
~~~~~~~~~~

Soft-clip `waveshaping <https://en.wikipedia.org/wiki/Waveshaper>`_ using
tanh — models the warm saturation of an overdriven tube amplifier:

.. code-block:: pycon

   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   distortion=0.5, distortion_drive=4.0)

- ``distortion``: Wet/dry mix, 0.0–1.0.
- ``distortion_drive``: Gain before clipping (default 3.0).
  0.5–2 = subtle warmth (tube preamp), 3–8 = overdrive (cranked amp),
  10+ = fuzz.

Combining Effects
~~~~~~~~~~~~~~~~~

Effects stack naturally. A dub-style part might use all four:

.. code-block:: pycon

   >>> # Dub melodica: distortion warmth → filtered → delay echoes → reverb space
   >>> melodica = score.part("melodica", synth="triangle", envelope="pluck",
   ...                       distortion=0.2, distortion_drive=2.0,
   ...                       lowpass=2000, lowpass_q=1.2,
   ...                       delay=0.5, delay_time=0.66, delay_feedback=0.55,
   ...                       reverb=0.4, reverb_decay=2.5)

A Drake-style 808 bass with subtle saturation:

.. code-block:: pycon

   >>> bass = score.part("bass", synth="sine", envelope="pluck",
   ...                   lowpass=200, lowpass_q=1.8,
   ...                   distortion=0.4, distortion_drive=2.0)

An acid lead with resonant filter and delay:

.. code-block:: pycon

   >>> lead = score.part("lead", synth="saw", envelope="staccato",
   ...                   lowpass=1500, lowpass_q=3.0,
   ...                   delay=0.3, delay_time=0.242, delay_feedback=0.4)

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
