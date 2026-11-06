Ableton Live Extension
======================

Prefer to stay inside Ableton Live instead of sketching in Python?
`ableton-pytheory <https://github.com/kennethreitz/ableton-pytheory>`_ is an
`Ableton Live Extension <https://ableton.github.io/extensions-sdk>`_ that runs
the real PyTheory package inside Live via WebAssembly (Pyodide). No plugins,
no system Python, no network: fully offline.

What you can do
---------------

Right-click a **MIDI clip** to analyze and transform it:

- Detect key and chords (with Roman numerals and cadence labels)
- Analyze a melody, suggest the next chord, or list substitutions
- Harmonize, arpeggiate, conform to scale, transpose by scale degree
- Smooth voicings, invert or reverse a melody, apply negative harmony
- Generate a bassline onto a new track, or render the clip to audio with
  PyTheory's synths
- Show engraved sheet music and export LilyPond

Right-click an empty **clip slot** to generate progressions, melodies,
scales, or drum patterns. Right-click a **scene** for a four-track song
sketch (chords, bass, melody, drums) or to detect the scene's key.
Audio clips get key/chord detection and Convert to MIDI; samples can be
tuned to the Set's key.

Requirements
------------

Needs an Ableton Live build with Extensions support (currently the Live
beta). Package the extension as an ``.ablx`` and drop it onto Live's
Settings → Extensions page. See the
`ableton-pytheory README <https://github.com/kennethreitz/ableton-pytheory>`_
for install and development details.

For AU/VST3 plugins that work in any host (not just Ableton), see
:doc:`vst`.
