# PyTheory for Claude Code

Compose music straight from a conversation. This is the official [Claude
Code](https://claude.com/claude-code) plugin marketplace for
[PyTheory](https://pytheory.org) — say *"write me a bossa nova in G minor"* and
Claude builds it, plays it, and exports MIDI or WAV, all in pure Python with no
samples, plugins, or DAW required.

> This repository is generated from the [pytheory](https://github.com/kennethreitz/pytheory)
> repo (the source of truth) via `make sync-skill`. Edit the skill there, not here.

## Install

In Claude Code:

```
/plugin marketplace add kennethreitz/pytheory-skill
/plugin install composing-with-pytheory@pytheory
```

Then just ask for music — *"make a four-chord pop loop"*, *"lay down a funk
beat with ghost-note snares"*, *"turn ii–V–I in D minor into a short
arrangement and save the MIDI"*.

You'll also want PyTheory itself available where Claude runs:

```
pip install pytheory
```

## What's inside

| Plugin | What it does |
| --- | --- |
| **composing-with-pytheory** | A skill that teaches Claude PyTheory's composition API — `Score`, parts, progressions, melodies, drums, layering — plus the house style (subtle detune, 0.2 humanize, sine/triangle love) and how to render to audio/MIDI/MusicXML/LilyPond/tab. |

## Links

- PyTheory docs — https://pytheory.org
- PyTheory source — https://github.com/kennethreitz/pytheory
- Try it in your browser — https://playground.pytheory.org

## Privacy

This plugin collects no data — see [PRIVACY.md](PRIVACY.md).

## License

MIT © Kenneth Reitz
