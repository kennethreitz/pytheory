Audio Playback
==============

PyTheory can synthesize and play tones and chords through your speakers
using basic `waveform <https://en.wikipedia.org/wiki/Waveform>`_ synthesis.

.. note::

   Audio playback requires `PortAudio <http://www.portaudio.com/>`_ to be
   installed on your system. On macOS: ``brew install portaudio``.
   On Ubuntu: ``apt install libportaudio2``.

Playing a Tone
--------------

.. code-block:: python

   from pytheory import Tone, play

   a4 = Tone.from_string("A4", system="western")
   play(a4, t=1_000)   # Play A440 for 1 second

Playing a Chord
---------------

.. code-block:: python

   from pytheory import Chord, Tone, play

   c_major = Chord(tones=[
       Tone.from_string("C4", system="western"),
       Tone.from_string("E4", system="western"),
       Tone.from_string("G4", system="western"),
   ])
   play(c_major, t=2_000)  # Play for 2 seconds

Waveform Types
--------------

The waveform shape determines the **`timbre <https://en.wikipedia.org/wiki/Timbre>`_** (tonal color) of the sound.
Different waveforms contain different combinations of **harmonics** —
integer multiples of the fundamental frequency.

- **`Sine wave <https://en.wikipedia.org/wiki/Sine_wave>`_** — the purest tone. Contains only the fundamental
  frequency with no harmonics. Sounds smooth, clear, and "electronic."
  This is the building block of all other waveforms (`Fourier's theorem <https://en.wikipedia.org/wiki/Fourier_series>`_).

- **`Sawtooth wave <https://en.wikipedia.org/wiki/Sawtooth_wave>`_** — contains all harmonics (both odd and even),
  each at amplitude 1/n. Sounds bright, buzzy, and aggressive.
  Named for its shape. Used extensively in `additive synthesis <https://en.wikipedia.org/wiki/Additive_synthesis>`_ and analog synthesizers.

- **`Triangle wave <https://en.wikipedia.org/wiki/Triangle_wave>`_** — contains only odd harmonics, each at amplitude
  1/n². Sounds softer and more mellow than sawtooth — somewhere between
  sine and sawtooth. Often described as "woody" or "hollow."

.. code-block:: python

   from pytheory import play, Synth, Tone

   tone = Tone.from_string("C4", system="western")

   play(tone, synth=Synth.SINE)      # Pure, clean
   play(tone, synth=Synth.SAW)       # Bright, buzzy
   play(tone, synth=Synth.TRIANGLE)  # Mellow, hollow

Temperaments
------------

Hear the difference between tuning systems:

.. code-block:: python

   play(tone, temperament="equal")        # Modern standard (since ~1917)
   play(tone, temperament="pythagorean")  # Pure fifths, wolf intervals
   play(tone, temperament="meantone")     # Pure thirds, Renaissance sound

Try playing a C major chord in each temperament — you'll hear subtle
differences in the "color" of the major third. Equal temperament is
a compromise; the other systems sacrifice some keys to make the good
keys sound better.
