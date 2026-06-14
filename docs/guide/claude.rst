PyTheory + Claude Code
======================

PyTheory ships an official `Claude Code <https://claude.com/claude-code>`_
plugin, so you can make and analyze music just by *talking* to Claude. Ask in
plain language and Claude writes and runs PyTheory for you — composing
arrangements, working out chord voicings, naming the key of a melody, building
guitar fingerings, or transcribing a recording.

Install
-------

In Claude Code, add the marketplace and install the plugin::

   /plugin marketplace add kennethreitz/pytheory-skill
   /plugin install composing-with-pytheory@pytheory

That one plugin bundles six skills (below) — installing it gives Claude all of
them. You also need PyTheory itself available wherever Claude runs (prefer uv if
you have it)::

   uv pip install pytheory      # or: pip install pytheory

Then just talk to it
--------------------

Each skill triggers on its own kind of request, so you don't pick one — you just
ask:

- *"Write me a bossa nova in G minor and save the MIDI."*
- *"Make a four-chord lo-fi loop and let me hear it."*
- *"What's the fingering for F#m7b5? And show me a DADGAD Cmaj7."*
- *"Tune my guitar to drop D."*
- *"What key are C E G B D in, and what chord comes after G?"*
- *"Voice-lead Cmaj7 to Fmaj7 and give me the tritone sub of G7."*
- *"Turn this hum into MIDI and a guitar lead sheet."*

Claude composes, plays, analyzes, and exports — to WAV, MIDI, MusicXML,
LilyPond, ABC, or guitar tab — all from the same PyTheory you'd use in a script.

Heard in the wild
-----------------

`Interpretations <https://interpretations.kennethreitz.org>`_ is a full 24-track
album composed entirely in PyTheory — Indian ragas colliding with trap beats,
singing bowls ringing over 808 sub bass, microtonal shruti tunings, a string
quartet ambushed by drum & bass. Every sound is generated from code: each track
is a ``.py`` file, with no samples and no DAW. It's a real, published example of
where this code-first workflow can go.

Listen on `Apple Music <https://music.apple.com/us/album/interpretations/1890986989>`_,
`Spotify <https://open.spotify.com/album/1jYjggrr6HEKfV4FchcJWD>`_, or the
`web player <https://interpretations.kennethreitz.org>`_ — and read the source
(every track as Python you can run) at
https://github.com/kennethreitz/interpretations.

The skills
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Skill
     - What it does
   * - ``composing-with-pytheory``
     - Full arrangements — progressions, melodies, basslines, drums, layering —
       rendered to audio or MIDI, with PyTheory's house style baked in.
   * - ``playing-guitar-with-pytheory``
     - Fingerings, chord shapes and tab, chord identification, scale diagrams,
       alternate tunings and capo, ~20 stringed instruments, Nashville charts,
       and the real-time tuner.
   * - ``chord-lab-with-pytheory``
     - A single chord's notes, voicings (inversions, drop-2/3, open), tension,
       tritone substitution, and voice leading.
   * - ``keys-and-harmony-with-pytheory``
     - Keys and progressions — diatonic chords, Roman-numeral analysis, key
       detection, secondary dominants, borrowed chords, and modulation.
   * - ``scales-modes-and-tunings-with-pytheory``
     - Scales and modes, "what scale fits these notes?", intervals, overtones,
       the circle of fifths, and 16 tuning systems.
   * - ``transcription-and-notation-with-pytheory``
     - Audio → notes/MIDI, chord recognition, MIDI import, and export to
       MusicXML / LilyPond lead sheets / ABC / tab.

How it works
------------

A `skill <https://code.claude.com/docs/en/skills>`_ is a set of instructions
Claude reads on demand. These skills teach Claude PyTheory's API — and its taste
(subtle detune, gentle humanization, sensible voices) — so the music it writes
is intentional, not random. Claude then writes and runs ordinary PyTheory Python
on your machine; nothing is sent anywhere, and the files it produces are yours.

The plugin is open source and generated from the PyTheory repo:
https://github.com/kennethreitz/pytheory-skill
