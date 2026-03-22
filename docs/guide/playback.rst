Audio Playback
==============

PyTheory can synthesize and play tones and chords through your speakers.

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

Choose between sine, sawtooth, and triangle wave synthesis:

.. code-block:: python

   from pytheory import play, Synth, Tone

   tone = Tone.from_string("C4", system="western")

   play(tone, synth=Synth.SINE)      # Smooth, pure tone
   play(tone, synth=Synth.SAW)       # Bright, buzzy
   play(tone, synth=Synth.TRIANGLE)  # Softer than sawtooth

Temperaments
------------

Play in different tuning systems:

.. code-block:: python

   play(tone, temperament="equal")        # Default, modern tuning
   play(tone, temperament="pythagorean")  # Ancient Greek tuning
   play(tone, temperament="meantone")     # Renaissance tuning
