"""PyTheory CLI — music theory from the command line."""
from __future__ import annotations

import argparse
import sys


def cmd_tone(args):
    from .tones import Tone
    tone = Tone.from_string(args.note, system="western")
    freq = tone.pitch(temperament=args.temperament)
    print(f"  Note:        {tone.full_name}")
    print(f"  Frequency:   {freq:.2f} Hz ({args.temperament} temperament)")
    if args.temperament != "equal":
        import math
        equal_freq = tone.pitch(temperament="equal")
        diff_cents = 1200 * math.log2(freq / equal_freq) if freq > 0 else 0
        print(f"  Equal temp:  {equal_freq:.2f} Hz (diff: {diff_cents:+.1f} cents)")
    if tone.midi is not None:
        print(f"  MIDI:        {tone.midi}")
    if tone.enharmonic:
        print(f"  Enharmonic:  {tone.enharmonic}")
    print(f"  Overtones:   {', '.join(f'{h:.1f}' for h in tone.overtones(6))}")


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


def cmd_play(args):
    from .tones import Tone
    from .chords import Chord
    from .play import play, Synth, Envelope

    synth_map = {"sine": Synth.SINE, "saw": Synth.SAW, "triangle": Synth.TRIANGLE}
    synth = synth_map[args.synth]
    envelope = Envelope[args.envelope.upper()]
    duration = args.duration

    # Try chord symbol first (e.g. "Am", "Cmaj7", "F#m7b5"),
    # then chart lookup, then fall back to individual notes.
    if len(args.notes) == 1:
        note = args.notes[0]
        target = None
        # Try as chord symbol first
        try:
            target = Chord.from_symbol(note)
            name = target.identify() or note
            label = f"{name} ({' '.join(t.full_name for t in target.tones)})"
        except ValueError:
            pass
        # Try chart lookup
        if target is None:
            try:
                target = Chord.from_name(note)
                name = target.identify() or note
                label = f"{name} ({' '.join(t.full_name for t in target.tones)})"
            except (ValueError, KeyError):
                pass
        # Fall back to single tone
        if target is None:
            target = Tone.from_string(
                note if any(c.isdigit() for c in note) else f"{note}4",
                system="western")
            label = target.full_name
    else:
        tones = [Tone.from_string(n if any(c.isdigit() for c in n) else f"{n}4",
                                  system="western") for n in args.notes]
        target = Chord(tones=tones)
        name = target.identify() or "Custom"
        label = f"{name} ({' '.join(t.full_name for t in tones)})"

    print(f"  Playing: {label}")
    print(f"  Synth:   {args.synth}")
    print(f"  Envelope: {args.envelope}")
    print(f"  Duration: {duration} ms")
    play(target, temperament=args.temperament, synth=synth, t=duration,
         envelope=envelope)


def cmd_modes(args):
    from .scales import TonedScale
    ts = TonedScale(tonic=f"{args.tonic}4", system=args.system)
    mode_names = ["ionian", "dorian", "phrygian", "lydian",
                  "mixolydian", "aeolian", "locrian"]
    print(f"  Modes of {args.tonic}:\n")
    for mode in mode_names:
        try:
            scale = ts[mode]
            notes = " ".join(scale.note_names)
            print(f"    {mode:<12s}  {notes}")
        except KeyError:
            continue


def cmd_circle(args):
    from .tones import Tone
    tone = Tone.from_string(f"{args.tonic}4", system="western")
    fifths = tone.circle_of_fifths()
    fourths = tone.circle_of_fourths()

    print(f"  Circle of fifths from {args.tonic}:")
    print(f"    → {' → '.join(t.name for t in fifths)}")
    print()
    print(f"  Circle of fourths from {args.tonic}:")
    print(f"    → {' → '.join(t.name for t in fourths)}")


def cmd_progressions(args):
    from .scales import Key
    key = Key(args.tonic, args.mode)
    progs = key.common_progressions()
    print(f"  Common progressions in {key}:\n")
    for name, chords in progs.items():
        symbols = [c.symbol or str(c) for c in chords]
        print(f"    {name:<20s}  {' → '.join(symbols)}")


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
    p.add_argument("--temperament", "-t", default="equal",
                   choices=["equal", "pythagorean", "meantone"],
                   help="Tuning temperament (default: equal)")

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

    # play
    p = sub.add_parser("play", help="Play notes or chords (e.g. pytheory play C E G)")
    p.add_argument("notes", nargs="+", help="Note names, with optional octave (e.g. C4, A#3, or just C E G)")
    p.add_argument("--synth", "-s", default="sine",
                   choices=["sine", "saw", "triangle"],
                   help="Waveform (default: sine)")
    p.add_argument("--duration", "-d", type=int, default=1000,
                   help="Duration in milliseconds (default: 1000)")
    p.add_argument("--temperament", "-t", default="equal",
                   choices=["equal", "pythagorean", "meantone"],
                   help="Tuning temperament (default: equal)")
    p.add_argument("--envelope", "-e", default="piano",
                   choices=["none", "piano", "organ", "pluck", "pad",
                            "strings", "bell", "staccato"],
                   help="ADSR envelope preset (default: piano)")

    # detect
    p = sub.add_parser("detect", help="Detect key from notes (e.g. pytheory detect C E G)")
    p.add_argument("notes", nargs="+", help="Note names")

    # modes
    p = sub.add_parser("modes", help="Show all modes of a note (e.g. pytheory modes C)")
    p.add_argument("tonic", help="Tonic note (e.g. C, G)")
    p.add_argument("--system", default="western", help="Musical system (default: western)")

    # circle
    p = sub.add_parser("circle", help="Circle of fifths/fourths (e.g. pytheory circle C)")
    p.add_argument("tonic", help="Starting note (e.g. C, G)")

    # progressions
    p = sub.add_parser("progressions", help="Common progressions in a key (e.g. pytheory progressions C major)")
    p.add_argument("tonic", help="Tonic note")
    p.add_argument("mode", nargs="?", default="major", help="Mode (default: major)")

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
        "play": cmd_play,
        "detect": cmd_detect,
        "modes": cmd_modes,
        "circle": cmd_circle,
        "progressions": cmd_progressions,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
