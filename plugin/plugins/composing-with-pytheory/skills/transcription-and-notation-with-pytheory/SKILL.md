---
name: transcription-and-notation-with-pytheory
description: >-
  Transcribe audio and convert between music formats with PyTheory. Use when the
  user wants to turn a recording (WAV/hum/melody) into notes or MIDI, identify
  the chord in an audio clip, import a MIDI file, or export a score/melody to
  MIDI, sheet music (MusicXML, LilyPond, ABC), or guitar tab.
license: MIT
allowed-tools: Write, Read, Bash(python3:*), Bash(uv run:*)
---

# Transcription & Notation

Getting music *into* PyTheory from audio/MIDI, and *out* to MIDI, sheet music,
and tab.

## Transcribe a recording → notes / MIDI

```python
from pytheory import Score

score = Score.from_wav("hum.wav", bpm=80)        # estimates tempo if bpm omitted
for name, part in score.parts.items():
    print(name, len(part.notes), "notes")
score.save_midi("hum.mid")
```

- `Score.from_wav(path, *, bpm=None, quantize=None, split=False, fmin=50, fmax=1500)`.
  `quantize=0.25` snaps to sixteenths; `split=True` separates a full mix into
  bass + melody (and drums) instead of one monophonic `melody` part.
- `.m4a`/`.mp3` work if `afconvert`/`ffmpeg` is available; WAV always works.
- CLI equivalent: `pytheory transcribe hum.m4a out.mid` (add `--split`,
  `--quantize 0.25`, `--bpm 90`).

## Identify the chord in an audio buffer

```python
from pytheory.audio import identify_chord
import scipy.io.wavfile
sr, data = scipy.io.wavfile.read("clip.wav")
identify_chord(data, sr)
# {'symbol': 'D7', 'confidence': 0.76, 'notes': ['D', 'F#', 'A', 'C']}  (or None)
```

Returns a best-guess `symbol` with a `confidence` (0..1) and the detected
`notes`, or `None` if it can't tell. Works best on clean, sustained chords; it's
a real-time recognizer, not a perfect oracle. (The live version is
`pytheory tune --chords`, in the guitar skill.)

## Import MIDI

```python
from pytheory import Score
score = Score.from_midi("song.mid")
```

## Export to every format

```python
score.save_midi("song.mid")                                  # MIDI (drums ch 10)
open("song.abc", "w").write(score.to_abc(title="Song", key="C"))
open("song.xml", "w").write(score.to_musicxml(title="Song"))   # MusicXML for notation apps
open("song.ly",  "w").write(score.to_lilypond(title="Song", key="C"))
print(score.to_tab("part_name"))                             # ASCII guitar tab for a part
```

- `to_tab(part_name, tuning="guitar", frets=24)` turns a single part into tab.
- `to_musicxml` opens in MuseScore/Finale/Sibelius; `to_lilypond` engraves to PDF
  via LilyPond; `to_abc` is compact plain-text notation.

## A complete round-trip

```python
from pytheory import Score, Key
score = Score.from_wav("melody.wav", quantize=0.25)          # hum -> notes
key = Key.detect(*[n.tone.name for n in score.parts["melody"].notes if n.tone])
score.save_midi("melody.mid")                                # -> DAW
open("melody.xml", "w").write(score.to_musicxml(title="My Melody"))   # -> sheet music
print("Detected key:", key)
```

## Tips

- Transcription is monophonic by default — one note at a time. Use `split=True`
  for full mixes.
- Pass `bpm=` if you know the tempo; otherwise it's estimated and timing/quantize
  is interpreted against that estimate.
- `identify_chord` returns a dict (or `None`) — check `confidence` before trusting
  the `symbol`.
- NumPy/SciPy ship as PyTheory dependencies, so `scipy.io.wavfile` (for reading
  the audio buffer) needs no extra install.
