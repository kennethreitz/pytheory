"""PyTheory CLI — music theory from the command line."""
from __future__ import annotations

import argparse
import sys


def cmd_tone(args):
    from .tones import Tone
    tone = Tone.from_string(args.note, system="western")
    print(f"  Note:      {tone.full_name}")
    print(f"  Frequency: {tone.frequency:.2f} Hz")
    if tone.midi is not None:
        print(f"  MIDI:      {tone.midi}")
    if tone.enharmonic:
        print(f"  Enharmonic: {tone.enharmonic}")
    print(f"  Overtones: {', '.join(f'{h:.1f}' for h in tone.overtones(6))}")


def cmd_scale(args):
    from .scales import TonedScale
    ts = TonedScale(tonic=f"{args.tonic}4", system=args.system)
    scale = ts[args.mode]
    print(f"  {args.tonic} {args.mode}: {' '.join(scale.note_names)}")
    print(f"  Intervals:  {scale.tones[0].full_name}", end="")
    for i in range(1, len(scale.tones)):
        semitones = abs(scale.tones[i] - scale.tones[i-1])
        print(f" -{semitones}- {scale.tones[i].full_name}", end="")
    print()


def cmd_chord(args):
    from .tones import Tone
    from .chords import Chord
    tones = [Tone.from_string(f"{n}4", system="western") for n in args.notes]
    chord = Chord(tones=tones)
    name = chord.identify() or "Unknown"
    print(f"  Chord:     {name}")
    print(f"  Tones:     {' '.join(t.full_name for t in chord.tones)}")
    print(f"  Intervals: {chord.intervals}")
    print(f"  Harmony:   {chord.harmony:.4f}")
    print(f"  Dissonance: {chord.dissonance:.4f}")
    t = chord.tension
    print(f"  Tension:   {t['score']:.2f} (tritones={t['tritones']})")


def cmd_key(args):
    from .scales import Key
    key = Key(args.tonic, args.mode)
    sig = key.signature
    acc = ", ".join(sig["accidentals"]) if sig["accidentals"] else "none"
    print(f"  Key: {key}")
    print(f"  Signature: {sig['sharps']} sharps, {sig['flats']} flats ({acc})")
    print(f"  Scale: {' '.join(key.note_names)}")
    print(f"  Triads:")
    for chord in key.scale.harmonize():
        analysis = chord.analyze(args.tonic, args.mode) or "?"
        print(f"    {analysis:6s}  {chord}")
    print(f"  7th chords:")
    for name in key.seventh_chords:
        print(f"    {name}")
    print(f"  Relative: {key.relative}")
    print(f"  Parallel: {key.parallel}")


def cmd_fingering(args):
    from .charts import CHARTS
    from .chords import Fretboard
    chart = CHARTS.get("western", {})
    if args.chord not in chart:
        print(f"  Unknown chord: {args.chord}")
        sys.exit(1)
    fb = Fretboard.guitar(capo=args.capo)
    print(chart[args.chord].tab(fretboard=fb))


def cmd_progression(args):
    from .scales import Key
    key = Key(args.tonic, args.mode)
    chords = key.progression(*args.numerals)
    print(f"  Key: {key}")
    print(f"  Progression: {' → '.join(args.numerals)}")
    print()
    for numeral, chord in zip(args.numerals, chords):
        print(f"    {numeral:6s}  {chord}")


def cmd_detect(args):
    from .scales import Key
    key = Key.detect(*args.notes)
    if key:
        print(f"  Detected key: {key}")
        print(f"  Scale: {' '.join(key.note_names)}")
    else:
        print("  Could not detect key")


def main():
    parser = argparse.ArgumentParser(
        prog="pytheory",
        description="Music Theory for Humans — from the command line",
    )
    sub = parser.add_subparsers(dest="command")

    # tone
    p = sub.add_parser("tone", help="Look up a tone (e.g. pytheory tone C4)")
    p.add_argument("note", help="Note name with octave (e.g. C4, A#3)")

    # scale
    p = sub.add_parser("scale", help="Show a scale (e.g. pytheory scale C major)")
    p.add_argument("tonic", help="Tonic note (e.g. C, G, Sa)")
    p.add_argument("mode", help="Scale/mode name (e.g. major, minor, dorian)")
    p.add_argument("--system", default="western", help="Musical system (default: western)")

    # chord
    p = sub.add_parser("chord", help="Identify a chord (e.g. pytheory chord C E G)")
    p.add_argument("notes", nargs="+", help="Note names (e.g. C E G)")

    # key
    p = sub.add_parser("key", help="Explore a key (e.g. pytheory key C major)")
    p.add_argument("tonic", help="Tonic note (e.g. C, G)")
    p.add_argument("mode", nargs="?", default="major", help="Mode (default: major)")

    # fingering
    p = sub.add_parser("fingering", help="Guitar fingering (e.g. pytheory fingering Am)")
    p.add_argument("chord", help="Chord name (e.g. C, Am, G7)")
    p.add_argument("--capo", type=int, default=0, help="Capo fret (default: 0)")

    # progression
    p = sub.add_parser("progression", help="Build a progression (e.g. pytheory progression C major I V vi IV)")
    p.add_argument("tonic", help="Tonic note")
    p.add_argument("mode", help="Mode (e.g. major, minor)")
    p.add_argument("numerals", nargs="+", help="Roman numerals (e.g. I V vi IV)")

    # detect
    p = sub.add_parser("detect", help="Detect key from notes (e.g. pytheory detect C E G)")
    p.add_argument("notes", nargs="+", help="Note names")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "tone": cmd_tone,
        "scale": cmd_scale,
        "chord": cmd_chord,
        "key": cmd_key,
        "fingering": cmd_fingering,
        "progression": cmd_progression,
        "detect": cmd_detect,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
