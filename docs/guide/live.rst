Live Performance
================

Everything else in PyTheory renders music ahead of time: you describe a
Score, it computes the audio, you hear the result. Live mode is the
opposite — you play, and PyTheory is the instrument. Plug in a MIDI
keyboard (or just use your computer keyboard), assign synths to
channels, and notes sound as you press keys.

Why would you want this? Because the fastest way to find a melody is
to play one. Sketching in code is great for arrangement and structure,
but noodling on keys is how you discover the part worth writing down.
Live mode closes that loop: improvise until something clicks, record
it, export it as MIDI or a Score, and keep composing in code.

Live MIDI needs one extra dependency::

   $ pip install "pytheory[live]"

(That installs `python-rtmidi <https://pypi.org/project/python-rtmidi/>`_.
Keyboard-only mode works without it.)

The Live Engine
---------------

:class:`~pytheory.live.LiveEngine` maps MIDI channels to PyTheory
instruments and synthesizes audio in real time:

.. code-block:: python

   from pytheory.live import LiveEngine

   engine = LiveEngine()
   engine.channel(1, instrument="electric_piano")
   engine.channel(2, instrument="bass_guitar")
   engine.channel(10, drums=True)        # channel 10 = drums, per MIDI convention
   engine.start()                        # blocks until Ctrl-C

Each channel takes the same parameters as :meth:`Score.part` — any
instrument preset, synth waveform, envelope, or effect:

.. code-block:: python

   engine.channel(1, synth="saw", envelope="pluck", lowpass=4000, reverb=0.3)
   engine.channel(2, instrument="rhodes", chorus=0.4)

Behind the scenes the engine pre-renders each note's waveform into a
cache when it starts, so the audio callback only has to mix — that's
what keeps latency low enough to play. Sustaining instruments
(organs, pads, strings) loop seamlessly inside their wavetables, so a
held key rings for as long as you hold it; percussive instruments
(pianos, plucks, mallets) decay naturally, just like the real thing.

Effects run on each channel's bus in real time — reverb tails,
filter sweeps, and delay feedback are computed per audio block, not
baked into the notes.

No MIDI Hardware? Use Your Keyboard
-----------------------------------

The engine can treat your computer keyboard as a two-octave piano —
bottom letter rows are the lower octave, number rows the upper, laid
out like piano keys (``Z X C V B N M`` are the white keys, ``S D G H J``
the black keys):

.. code-block:: python

   engine.keyboard_play(ch=1)
   engine.start()

Map Hardware Knobs to Parameters
--------------------------------

Map any MIDI CC (a knob or slider on your controller) to any channel
parameter — filter sweeps, volume, reverb sends, distortion — and turn
the knob while you play:

.. code-block:: python

   engine.cc(11, "lowpass", min_val=200, max_val=8000)
   engine.cc(12, "volume", min_val=0.0, max_val=1.0)
   engine.cc(13, "reverb", min_val=0.0, max_val=0.8)

Knob turns apply on the very next audio block (~3ms at the default
buffer size) — sweep the filter mid-phrase and it responds like a
hardware synth.

Drums Synced to MIDI Clock
--------------------------

If your controller or groovebox sends MIDI clock (an OP-XY, a
Digitakt, most hardware sequencers), the engine can run a drum
pattern locked to its transport — start, stop, and tempo all follow
the hardware:

.. code-block:: python

   engine.drums("house", volume=0.5)
   engine.start()

Any of the 100 :class:`Pattern` presets works — see :doc:`drums`.

Record What You Play
--------------------

The whole point of improvising is keeping the good take. The engine
records incoming MIDI and exports it as a file or a
:class:`~pytheory.rhythm.Score`:

.. code-block:: python

   engine.start_recording()
   # ... play ...
   engine.stop_recording()

   engine.export_recording("take1.mid")        # save as MIDI
   score = engine.export_recording(filename=None)   # or get a Score back

A recording that comes back as a Score drops you into the rest of
PyTheory — change the synths, add effects, layer more parts, export to
sheet music. Improvise first, arrange after.

The Live TUI
------------

For a ready-made performance setup, the live TUI builds an
8-channel rig with randomly chosen instruments, a drum pattern, and a
terminal dashboard showing what's playing::

   $ pytheory live

Every run picks a different instrument combination (the seed is
printed so you can resume a setup you liked). Inside the TUI you can
swap instruments per channel, change the drum pattern, record, and
export — without leaving the keyboard.

Saving a Rig
------------

Engine configurations serialize to JSON, so a setup you like is one
line to save and one to restore:

.. code-block:: python

   engine.save_config("my_rig.json")

   engine = LiveEngine()
   engine.load_config("my_rig.json")
   engine.start()
