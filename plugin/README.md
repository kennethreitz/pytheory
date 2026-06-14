# PyTheory for Claude Code

Make music — and music theory — straight from a conversation. This is the
official [Claude Code](https://claude.com/claude-code) plugin marketplace for
[PyTheory](https://pytheory.org). Say *"write me a bossa nova in G minor"*, *"what
chord is x32010?"*, *"give me a DADGAD Cmaj7"*, or *"what key are these notes
in?"* and Claude answers in pure Python — composing, analyzing, and exporting
MIDI/WAV/sheet music with no samples, plugins, or DAW required.

> This repository is generated from the [pytheory](https://github.com/kennethreitz/pytheory)
> repo (the source of truth) via `make sync-skill`. Edit the skill there, not here.

## Install

In Claude Code:

```
/plugin marketplace add kennethreitz/pytheory-skill
/plugin install composing-with-pytheory@pytheory
```

One plugin, six skills — installing it gives Claude all of them. Each triggers on
its own kind of request, so just ask: *"make a four-chord pop loop"*, *"lay down
a funk beat with ghost-note snares"*, *"what's the fingering for F#m7b5?"*, *"tune
my guitar to drop D"*, *"what key are C E G B D in?"*, *"voice-lead Cmaj7 to
Fmaj7"*, or *"turn this hum into MIDI and a lead sheet"*.

You'll also want PyTheory itself available where Claude runs (prefer uv if you
have it):

```
uv pip install pytheory      # or: pip install pytheory
```

## What's inside

Six skills, all in one plugin:

| Skill | What it does |
| --- | --- |
| **composing-with-pytheory** | Full arrangements — `Score`, parts, progressions, melodies, drums, layering — plus the house style (subtle detune, 0.2 humanize, sine/triangle love) and rendering to audio/MIDI. |
| **playing-guitar-with-pytheory** | Fretboard fingerings, chord shapes & tab, chord identification, scale diagrams, alternate tunings + capo, ~20 stringed instruments, Nashville charts, and the real-time tuner. |
| **chord-lab-with-pytheory** | A single chord's notes, voicings (inversions, drop-2/3, open), tension/dissonance, Forte number, tritone sub, and voice leading. |
| **keys-and-harmony-with-pytheory** | Keys and progressions — diatonic chords, Roman-numeral analysis, key detection, secondary dominants, borrowed chords, and modulation. |
| **scales-modes-and-tunings-with-pytheory** | Scales and modes, "what scale fits these notes?", intervals, overtones, the circle of fifths, and 16 tuning systems / temperaments. |
| **transcription-and-notation-with-pytheory** | Audio → notes/MIDI, chord recognition, MIDI import, and export to MusicXML / LilyPond (incl. guitar lead sheets) / ABC / tab. |

## Links

- PyTheory docs — https://pytheory.org
- PyTheory source — https://github.com/kennethreitz/pytheory
- Try it in your browser — https://playground.pytheory.org

## Privacy

This plugin collects no data — see [PRIVACY.md](PRIVACY.md).

## License

MIT © Kenneth Reitz
