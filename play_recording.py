"""Play a recorded MIDI file through pytheory's full renderer.

Takes a MIDI file captured by the live engine and plays it back
through the complete synthesis pipeline — with ensemble, effects,
reverb, and master compression.

Usage:
    python play_recording.py recording.mid
    python play_recording.py recording.mid --bpm 110
"""

import sys
import sounddevice as sd

from pytheory import Score
from pytheory.play import render_score, SAMPLE_RATE


def main():
    if len(sys.argv) < 2:
        print("  Usage: python play_recording.py <file.mid> [--bpm N]")
        return

    filename = sys.argv[1]
    bpm = None
    if "--bpm" in sys.argv:
        idx = sys.argv.index("--bpm")
        if idx + 1 < len(sys.argv):
            bpm = int(sys.argv[idx + 1])

    print(f"  Loading {filename}...")
    score = Score.from_midi(filename)

    if bpm:
        score.bpm = bpm

    print(f"  {score}")
    print(f"  Rendering...")

    buf = render_score(score)
    duration = len(buf) / SAMPLE_RATE

    print(f"  Playing ({duration:.1f}s)...")
    try:
        sd.play(buf, SAMPLE_RATE)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()
        print("\n  Stopped.")

    print("  Done.")


if __name__ == "__main__":
    main()
