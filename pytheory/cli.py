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

    synth_map = {
        "sine": Synth.SINE, "saw": Synth.SAW, "triangle": Synth.TRIANGLE,
        "square": Synth.SQUARE, "pulse": Synth.PULSE, "fm": Synth.FM,
        "noise": Synth.NOISE, "supersaw": Synth.SUPERSAW,
        "pwm_slow": Synth.PWM_SLOW, "pwm_fast": Synth.PWM_FAST,
    }
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


def cmd_identify(args):
    from .chords import Chord
    chord = Chord.from_symbol(args.symbol)
    name = chord.identify() or "Unknown"
    sym = chord.symbol or args.symbol
    tones_str = " ".join(t.full_name for t in chord.tones)
    intervals = chord.intervals
    harmony = chord.harmony
    dissonance = chord.dissonance
    tension = chord.tension

    print(f"  Chord:      {name}")
    print(f"  Symbol:     {sym}")
    print(f"  Tones:      {tones_str}")
    print(f"  Intervals:  {intervals}")
    print(f"  Harmony:    {harmony:.4f}")
    print(f"  Dissonance: {dissonance:.4f}")
    print(f"  Tension:    score={tension['score']:.2f} tritones={tension['tritones']} "
          f"minor_2nds={tension['minor_seconds']} dominant={tension['has_dominant_function']}")


def cmd_midi(args):
    from .scales import Key
    from .play import save_midi
    key = Key(args.tonic, args.mode)
    chords = key.progression(*args.numerals)
    save_midi(chords, args.output, t=args.duration, bpm=args.bpm)
    print(f"  Key:        {key}")
    print(f"  Progression: {' '.join(args.numerals)}")
    print(f"  BPM:        {args.bpm}")
    print(f"  Duration:   {args.duration} ms")
    print(f"  Output:     {args.output}")


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


def cmd_demo(args):
    import random
    from .rhythm import Score, Pattern, Duration
    from .chords import Chord
    from .scales import Key
    from .play import play_score

    moods = [
        {"name": "Bossa Nova", "key": ("A", "minor"), "drums": "bossa nova",
         "bpm": 140, "prog": ("i", "iv", "V", "i"),
         "lead_synth": "triangle", "pad_synth": "fm"},
        {"name": "Jazz Club", "key": ("Bb", "major"), "drums": "jazz",
         "bpm": 105, "prog": ("I", "vi", "ii", "V"),
         "lead_synth": "saw", "pad_synth": "fm"},
        {"name": "Afrobeat Groove", "key": ("E", "minor"), "drums": "afrobeat",
         "bpm": 115, "prog": ("i", "iv", "V", "i"),
         "lead_synth": "saw", "pad_synth": "supersaw"},
        {"name": "House Pump", "key": ("C", "minor"), "drums": "house",
         "bpm": 124, "prog": ("i", "IV", "V", "i"),
         "lead_synth": "saw", "pad_synth": "supersaw"},
        {"name": "Reggae One-Drop", "key": ("G", "major"), "drums": "reggae",
         "bpm": 80, "prog": ("I", "IV", "V", "IV"),
         "lead_synth": "triangle", "pad_synth": "pwm_slow"},
        {"name": "Funk Workout", "key": ("E", "minor"), "drums": "funk",
         "bpm": 100, "prog": ("i", "iv", "V", "i"),
         "lead_synth": "saw", "pad_synth": "square"},
    ]

    mood = random.choice(moods)
    tonic, mode = mood["key"]
    key = Key(tonic, mode)
    chords = key.progression(*mood["prog"])

    score = Score("4/4", bpm=mood["bpm"], swing=random.uniform(0.1, 0.4))
    score.drums(mood["drums"], repeats=4, fill=random.choice(Pattern.list_fills()))

    pad = score.part("pad", synth=mood["pad_synth"], envelope="pad",
                     volume=0.25, reverb=0.4, reverb_decay=2.0,
                     chorus=0.2)
    lead = score.part("lead", synth=mood["lead_synth"], envelope="pluck",
                      volume=0.4, delay=0.25, delay_time=0.375,
                      delay_feedback=0.35, reverb=0.2,
                      lowpass=3000, humanize=0.2)
    bass = score.part("bass", synth="sine", envelope="pluck",
                      volume=0.45, lowpass=500)

    for chord in chords * 2:
        pad.add(chord, Duration.WHOLE)

    # Generate a melody from scale tones
    scale_tones = [t.name for t in key.scale.tones[:-1]]
    for chord in chords:
        chord_tones = [t.name for t in chord.tones]
        for _ in range(4):
            if random.random() < 0.2:
                lead.rest(random.choice([0.5, 1.0]))
            else:
                n = random.choice(chord_tones if random.random() < 0.6 else scale_tones)
                oct = random.choice([4, 5])
                dur = random.choice([0.5, 0.67, 1.0])
                lead.add(f"{n}{oct}", dur, velocity=random.randint(60, 120))

    root = chords[0].root
    if root:
        for chord in chords * 2:
            r = chord.root
            if r:
                bass.add(f"{r.name}2", Duration.QUARTER, velocity=100)
                bass.add(f"{r.name}2", Duration.QUARTER, velocity=60)
                fifth = r.add(7)
                bass.add(f"{fifth.name}2", Duration.QUARTER, velocity=70)
                bass.add(f"{r.name}2", Duration.QUARTER, velocity=80)

    prog_str = " → ".join(c.symbol or str(c) for c in chords)
    print(f"  ♫  {mood['name']}")
    print(f"     {tonic} {mode} | {mood['bpm']} bpm")
    print(f"     {prog_str}")
    print(f"     {mood['drums']} drums | {mood['lead_synth']} lead | {mood['pad_synth']} pad")
    print()

    play_score(score)
    print("  ♫")


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
                   choices=["sine", "saw", "triangle", "square", "pulse",
                            "fm", "noise", "supersaw", "pwm_slow", "pwm_fast"],
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

    # identify
    p = sub.add_parser("identify", help="Identify a chord symbol (e.g. pytheory identify Cmaj7)")
    p.add_argument("symbol", help="Chord symbol (e.g. Cmaj7, Am, F#m7b5)")

    # midi
    p = sub.add_parser("midi", help="Export a progression to MIDI (e.g. pytheory midi C major I V vi IV)")
    p.add_argument("tonic", help="Tonic note")
    p.add_argument("mode", help="Mode (e.g. major, minor)")
    p.add_argument("numerals", nargs="+", help="Roman numerals (e.g. I V vi IV)")
    p.add_argument("-o", "--output", default="output.mid", help="Output file (default: output.mid)")
    p.add_argument("--bpm", type=int, default=120, help="BPM (default: 120)")
    p.add_argument("--duration", type=int, default=500, help="Duration per chord in ms (default: 500)")

    # demo
    sub.add_parser("demo", help="Play a randomly generated track (different every time)")

    # repl
    sub.add_parser("repl", help="Interactive music theory scratchpad")

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
        "identify": cmd_identify,
        "midi": cmd_midi,
        "demo": cmd_demo,
        "repl": lambda args: __import__('pytheory.repl', fromlist=['main']).main(),
        "detect": cmd_detect,
        "modes": cmd_modes,
        "circle": cmd_circle,
        "progressions": cmd_progressions,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
