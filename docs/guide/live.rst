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

Live mode needs one extra dependency::

   $ pip install "pytheory[live]"

(That installs `python-rtmidi <https://pypi.org/project/python-rtmidi/>`_,
which every live path goes through — even computer-keyboard play, so
it's required whether or not you have a MIDI controller.)

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

By default :meth:`~pytheory.live.LiveEngine.start` opens the first MIDI
input it finds. With more than one controller plugged in, list what's
connected and pick one by index or by a substring of its name:

.. code-block:: python

   engine.list_ports()              # prints the available MIDI inputs
   engine.start(port="OP-XY")       # or start(port=0)

Each channel takes the same parameters as :meth:`Score.part` — any
instrument preset, synth waveform, envelope, or effect:

.. code-block:: python

   engine.channel(1, synth="saw", envelope="pluck", lowpass=4000, reverb=0.3)
   engine.channel(2, instrument="wurlitzer", chorus=0.4)

Behind the scenes the engine pre-renders each note's waveform into a
cache when it starts, so the audio callback only has to mix — that's
what keeps latency low enough to play. Sustaining instruments
(organs, pads, strings) loop seamlessly inside their wavetables, so a
held key rings for as long as you hold it; percussive instruments
(pianos, plucks, mallets) decay naturally, just like the real thing.

Effects run on each channel's bus in real time — reverb tails,
filter sweeps, and delay feedback are computed per audio block, not
baked into the notes. Pitch bend is live too: roll your controller's
wheel and every sounding voice on that channel glides up to ±2
semitones, tracked block by block.

No MIDI Hardware? Use Your Keyboard
-----------------------------------

You don't need a controller to play live — the engine can treat your
computer keyboard as a two-octave piano. The bottom letter row is the
lower octave's white keys (``Z X C V B N M`` = C D E F G A B) with
``S D G H J`` as its black keys; the QWERTY letter row above it is the
upper octave's white keys (``Q W E R T Y U``) with the number row
(``2 3 5 6 7``) as its black keys.

The easy way in is the :ref:`live TUI <live-tui>`. Run ``pytheory live``,
type the ``kbd`` command at its prompt (``kbd 1`` targets channel 1;
``kbd 1 4`` also sets the starting octave), and play — ``Esc`` exits
keyboard mode and the ``↑``/``↓`` arrows shift the octave::

   $ pytheory live

The engine itself only translates keys into notes; it doesn't read the
keyboard for you (that's the TUI's job). To wire it into your own
program, enable a channel with
:meth:`~pytheory.live.LiveEngine.keyboard_play` and feed it keystrokes
from your own input loop:

.. code-block:: python

   engine.keyboard_play(ch=1)
   # then, from your input loop, on key down / key up:
   engine.keyboard_note("z", on=True)     # note on  (C)
   engine.keyboard_note("z", on=False)    # note off

Map Hardware Knobs to Parameters
--------------------------------

Map any MIDI CC (a knob or slider on your controller) to any channel
parameter — filter sweeps, volume, reverb sends, distortion — and turn
the knob while you play:

.. code-block:: python

   engine.cc(11, "lowpass", min_val=200, max_val=8000)
   engine.cc(12, "volume", min_val=0.0, max_val=1.0)
   engine.cc(13, "reverb", min_val=0.0, max_val=0.8)

A mapping spans every channel by default. Pass ``ch=`` to scope a knob
to one of them — handy when each hand is on a different sound:

.. code-block:: python

   engine.cc(11, "lowpass", min_val=200, max_val=8000, ch=1)

Knob turns apply on the very next audio block — about 12 ms at the
default 512-sample buffer, or ~3 ms if you drop to the smaller buffer
the TUI uses (``LiveEngine(buffer_size=128)``). Sweep the filter
mid-phrase and it responds like a hardware synth.

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

.. _live-tui:

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

Ableton Link
------------

If anything else on your network speaks `Ableton Link
<https://www.ableton.com/link/>`_ — Ableton Live, most iOS music
apps, many DJ tools — the engine can lock to the shared session::

   $ pip install "pytheory[link]"
   $ pytheory live --link

Or in Python:

.. code-block:: python

   engine = LiveEngine()
   engine.channel(1, instrument="electric_piano")
   engine.drums("house")
   engine.enable_link()
   engine.start()

Tempo follows the session (and the session follows you — Link is
peer-to-peer, nobody is the master), the drum pattern locks to the
shared beat grid so your kick lands on everyone else's downbeat, and
transport start/stop syncs with peers that support it.

:meth:`~pytheory.live.LiveEngine.enable_link` takes two optional knobs:
``quantum`` (the bar length in beats the beat grid aligns its phase to,
default ``4``) and ``start_stop_sync`` (follow the session's transport,
on by default). The TUI header shows the peer count while connected, and
outside the TUI you can read it yourself with ``engine.link_peers()``.

If you want to drive Ableton Live itself from PyTheory, see
`ableton-pytheory <https://github.com/kennethreitz/ableton-pytheory>`_,
a companion project for those interested.

Saving a Rig
------------

Engine configurations serialize to JSON, so a setup you like is one
line to save and one to restore:

.. code-block:: python

   engine.save_config("my_rig.json")

   engine = LiveEngine()
   engine.load_config("my_rig.json")
   engine.start()

Tuning Up
---------

Before you play, get in tune — ``pytheory tune`` is a real-time
tuner with instrument string presets and a browser strobe display.
It's covered with the rest of the microphone-in tools in
:doc:`listening`.
