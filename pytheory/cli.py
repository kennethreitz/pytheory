"""PyTheory CLI — music theory from the command line."""
from __future__ import annotations

import argparse
import os
import sys


def _emit_json(data):
    """Print a result dict as indented JSON."""
    import json
    print(json.dumps(data, indent=2, default=str))


def _play_items(items, t=600):
    """Play a list of Tone/Chord objects in sequence (best-effort)."""
    try:
        from .play import play
        for item in items:
            play(item, t=t)
    except Exception as e:           # no audio backend, etc.
        print(f"  (could not play: {e})")


def cmd_tone(args):
    from .tones import Tone
    tone = Tone.from_string(args.note, system="western")
    freq = tone.pitch(temperament=args.temperament)
    if getattr(args, "json", False):
        _emit_json({
            "note": tone.full_name,
            "frequency": round(freq, 2),
            "temperament": args.temperament,
            "midi": tone.midi,
            "enharmonic": tone.enharmonic,
            "overtones": [round(h, 2) for h in tone.overtones(6)],
        })
    else:
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
    if getattr(args, "play", False):
        _play_items([tone], t=900)


def cmd_scale(args):
    from .scales import TonedScale
    ts = TonedScale(tonic=f"{args.tonic}4", system=args.system)
    scale = ts[args.mode]
    if getattr(args, "json", False):
        _emit_json({
            "tonic": args.tonic, "mode": args.mode,
            "notes": list(scale.note_names),
        })
    else:
        print(f"  {args.tonic} {args.mode}: {' '.join(scale.note_names)}")
        print(f"  Intervals:  {scale.tones[0].full_name}", end="")
        for i in range(1, len(scale.tones)):
            semitones = abs(scale.tones[i] - scale.tones[i-1])
            print(f" -{semitones}- {scale.tones[i].full_name}", end="")
        print()
    if getattr(args, "play", False):
        _play_items(list(scale.tones), t=400)


def cmd_chord(args):
    from .tones import Tone
    from .chords import Chord
    tones = [Tone.from_string(f"{n}4", system="western") for n in args.notes]
    chord = Chord(tones=tones)
    name = chord.identify() or "Unknown"
    if getattr(args, "json", False):
        t = chord.tension
        _emit_json({
            "chord": name,
            "tones": [t.full_name for t in chord.tones],
            "intervals": chord.intervals,
            "harmony": round(chord.harmony, 4),
            "dissonance": round(chord.dissonance, 4),
            "tension": {"score": round(t["score"], 2), "tritones": t["tritones"]},
        })
    else:
        print(f"  Chord:     {name}")
        print(f"  Tones:     {' '.join(t.full_name for t in chord.tones)}")
        print(f"  Intervals: {chord.intervals}")
        print(f"  Harmony:   {chord.harmony:.4f}")
        print(f"  Dissonance: {chord.dissonance:.4f}")
        t = chord.tension
        print(f"  Tension:   {t['score']:.2f} (tritones={t['tritones']})")
    if getattr(args, "play", False):
        _play_items([chord], t=1200)



def cmd_key(args):
    from .scales import Key
    key = Key(args.tonic, args.mode)
    sig = key.signature
    triads = key.scale.harmonize()
    if getattr(args, "json", False):
        _emit_json({
            "key": str(key),
            "signature": {"sharps": sig["sharps"], "flats": sig["flats"],
                          "accidentals": list(sig["accidentals"])},
            "scale": list(key.note_names),
            "triads": [{"roman": c.analyze(args.tonic, args.mode) or "?",
                        "chord": c.identify() or str(c)} for c in triads],
            "seventh_chords": list(key.seventh_chords),
            "relative": str(key.relative),
            "parallel": str(key.parallel),
        })
    else:
        acc = ", ".join(sig["accidentals"]) if sig["accidentals"] else "none"
        print(f"  Key: {key}")
        print(f"  Signature: {sig['sharps']} sharps, {sig['flats']} flats ({acc})")
        print(f"  Scale: {' '.join(key.note_names)}")
        print(f"  Triads:")
        for chord in triads:
            analysis = chord.analyze(args.tonic, args.mode) or "?"
            print(f"    {analysis:6s}  {chord}")
        print(f"  7th chords:")
        for name in key.seventh_chords:
            print(f"    {name}")
        print(f"  Relative: {key.relative}")
        print(f"  Parallel: {key.parallel}")
    if getattr(args, "play", False):
        _play_items(list(key.scale.tones), t=400)


def cmd_fingering(args):
    from .charts import CHARTS
    from .chords import Fretboard
    chart = CHARTS.get("western", {})
    if args.chord not in chart:
        print(f"  Unknown chord: {args.chord}")
        sys.exit(1)
    fb = Fretboard.guitar(capo=args.capo)
    tab = chart[args.chord].tab(fretboard=fb)
    if getattr(args, "json", False):
        _emit_json({"chord": args.chord, "capo": args.capo, "tab": tab})
    else:
        print(tab)
    if getattr(args, "play", False):
        from .chords import Chord
        try:
            _play_items([Chord.from_name(args.chord)], t=1500)
        except Exception:
            pass


def cmd_progression(args):
    from .scales import Key
    key = Key(args.tonic, args.mode)
    chords = key.progression(*args.numerals)
    if getattr(args, "json", False):
        _emit_json({
            "key": str(key),
            "progression": [
                {"numeral": n, "chord": chord.identify() or str(chord)}
                for n, chord in zip(args.numerals, chords)
            ],
        })
    else:
        print(f"  Key: {key}")
        print(f"  Progression: {' → '.join(args.numerals)}")
        print()
        for numeral, chord in zip(args.numerals, chords):
            print(f"    {numeral:6s}  {chord}")
    if getattr(args, "play", False):
        _play_items(chords, t=900)


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
    tension = chord.tension
    if getattr(args, "json", False):
        _emit_json({
            "chord": name, "symbol": sym,
            "tones": [t.full_name for t in chord.tones],
            "intervals": chord.intervals,
            "harmony": round(chord.harmony, 4),
            "dissonance": round(chord.dissonance, 4),
            "tension": {"score": round(tension["score"], 2),
                        "tritones": tension["tritones"],
                        "minor_2nds": tension["minor_seconds"],
                        "dominant": tension["has_dominant_function"]},
        })
    else:
        print(f"  Chord:      {name}")
        print(f"  Symbol:     {sym}")
        print(f"  Tones:      {' '.join(t.full_name for t in chord.tones)}")
        print(f"  Intervals:  {chord.intervals}")
        print(f"  Harmony:    {chord.harmony:.4f}")
        print(f"  Dissonance: {chord.dissonance:.4f}")
        print(f"  Tension:    score={tension['score']:.2f} tritones={tension['tritones']} "
              f"minor_2nds={tension['minor_seconds']} dominant={tension['has_dominant_function']}")
    if getattr(args, "play", False):
        _play_items([chord], t=1200)


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
    modes = {}
    for mode in mode_names:
        try:
            modes[mode] = list(ts[mode].note_names)
        except KeyError:
            continue
    if getattr(args, "json", False):
        _emit_json({"tonic": args.tonic, "modes": modes})
    else:
        print(f"  Modes of {args.tonic}:\n")
        for mode, notes in modes.items():
            print(f"    {mode:<12s}  {' '.join(notes)}")
    if getattr(args, "play", False):
        for mode in modes:
            _play_items(list(ts[mode].tones), t=250)


def cmd_circle(args):
    from .tones import Tone
    tone = Tone.from_string(f"{args.tonic}4", system="western")
    fifths = tone.circle_of_fifths()
    fourths = tone.circle_of_fourths()
    if getattr(args, "json", False):
        _emit_json({
            "tonic": args.tonic,
            "fifths": [t.name for t in fifths],
            "fourths": [t.name for t in fourths],
        })
    else:
        print(f"  Circle of fifths from {args.tonic}:")
        print(f"    → {' → '.join(t.name for t in fifths)}")
        print()
        print(f"  Circle of fourths from {args.tonic}:")
        print(f"    → {' → '.join(t.name for t in fourths)}")
    if getattr(args, "play", False):
        _play_items(list(fifths), t=350)


def cmd_live(args):
    from .live_tui import run_tui
    run_tui(seed=args.seed, port=args.port, channels=args.channels,
            drums=args.drums, buffer=args.buffer, link=args.link)


def cmd_studio(args):
    from .studio import serve
    serve(port=args.port, open_browser=not args.no_browser)


def cmd_tune(args):
    from .tuner import Tuner, serve, run_terminal
    tuner = Tuner(reference_pitch=args.ref, device=args.device,
                  instrument=args.instrument, chords=args.chords)
    tuner.start()
    try:
        if args.serve:
            serve(tuner, port=args.port, open_browser=not args.no_browser)
        else:
            extra = f", {args.instrument}" if args.instrument else ""
            if args.chords:
                extra += ", chord ID on"
            print(f"  PyTheory Tuner (A4 = {args.ref:g} Hz{extra})"
                  f" — Ctrl-C to stop")
            run_terminal(tuner)
    finally:
        tuner.stop()


def cmd_transcribe(args):
    from .rhythm import Score
    score = Score.from_wav(args.input, bpm=args.bpm,
                           quantize=args.quantize, split=args.split,
                           fmin=args.fmin, fmax=args.fmax)
    tempo_src = "given" if args.bpm else "estimated"
    print(f"  Tempo: {score.bpm} BPM ({tempo_src})")
    for pname, part in score.parts.items():
        notes = [n for n in part.notes if n.tone is not None]
        print(f"  {pname}: {len(notes)} notes")
        line = []
        for n in notes:
            line.append(f"{n.tone}({n.beats:g})")
            if len(line) == 8:
                print("    " + " ".join(line))
                line = []
        if line:
            print("    " + " ".join(line))
    if args.output:
        score.save_midi(args.output)
        print(f"  Saved → {args.output}")
    if args.play:
        from .play import play_score
        play_score(score)


def cmd_progressions(args):
    from .scales import Key
    key = Key(args.tonic, args.mode)
    progs = key.common_progressions()
    print(f"  Common progressions in {key}:\n")
    for name, chords in progs.items():
        symbols = [c.symbol or str(c) for c in chords]
        print(f"    {name:<20s}  {' → '.join(symbols)}")


def cmd_raga(args):
    from .ragas import Raga

    # Bare `pytheory raga` (or `--list`) lists everything.
    if not args.name or args.list:
        if args.thaat:
            ragas = Raga.by_thaat(args.thaat)
        elif args.time:
            ragas = Raga.by_time(args.time)
        elif args.tradition:
            ragas = Raga.by_tradition(args.tradition)
        else:
            ragas = Raga.all()
        print(f"  {len(ragas)} ragas:\n")
        for r in ragas:
            print(f"    {r.name:<20} {r.thaat:<28} {r.time:<13} {r.rasa}")
        return

    raga = Raga.get(args.name)
    sa = args.sa
    print(f"  Raga {raga.name}"
          + (f"  (aka {', '.join(raga.aka)})" if raga.aka else ""))
    print(f"  thaat {raga.thaat} · {raga.jati} · {raga.time} · {raga.rasa}")
    print(f"  vadi {raga.vadi}  samvadi {raga.samvadi}")
    print(f"  aroha  : {' '.join(raga.aroha_swaras())}")
    print(f"  avaroha: {' '.join(raga.avaroha_swaras())}")
    if raga.pakad:
        print(f"  pakad  : {raga.pakad}")
    print(f"  scale (Sa={sa}): {' '.join(raga.note_names(sa))}")
    if args.shruti:
        print("\n  shruti intonation (just vs 12-TET):")
        for row in raga.shruti_table(sa):
            print(f"    {row['swara']:<2} {row['ratio']:>6}  {row['note']:<3} "
                  f"{row['hz']:>8.2f} Hz  {row['cents_off']:+6.1f}¢")
    if args.play:
        print(f"\n  Playing {raga.name} "
              f"({'just intonation' if not args.equal else '12-TET'}, "
              f"reverb {args.reverb:g})…")
        raga.play(f"{sa}4", just=not args.equal, reverb=args.reverb)


def cmd_maqam(args):
    from .maqam import Maqam

    if not args.name or args.list:
        maqamat = Maqam.by_family(args.family) if args.family else Maqam.all()
        print(f"  {len(maqamat)} maqamat:\n")
        for m in maqamat:
            print(f"    {m.name:<12} {m.family:<10} "
                  f"{' '.join(m.degree_names()):<34} {m.mood}")
        return

    m = Maqam.get(args.name)
    tonic = args.tonic
    print(f"  Maqam {m.name}"
          + (f"  (aka {', '.join(m.aka)})" if m.aka else ""))
    print(f"  family {m.family} · {m.mood}")
    print(f"  ajnas: {m.ajnas}")
    print(f"  seyir: {m.seyir}")
    print(f"  scale: {' '.join(m.degree_names())}")
    print(f"  ≈ 12-TET (tonic={tonic}): {' '.join(m.note_names(tonic))}")
    if args.tuning:
        print("\n  quarter-tone intonation (just vs 12-TET):")
        for row in m.maqam_table(tonic):
            print(f"    {row['degree']:<4} {row['ratio']:>6}  ~{row['note']:<3} "
                  f"{row['hz']:>8.2f} Hz  {row['cents_off']:+6.1f}¢")
    if args.play:
        print(f"\n  Playing {m.name} (just intonation, reverb {args.reverb:g})…")
        m.play(f"{tonic}4", reverb=args.reverb)


def cmd_metronome(args):
    from .metronome import Metronome

    progression = None
    if args.chords:
        # Allow a key + Roman numerals (e.g. "C major I V vi IV") or a
        # literal list of chord symbols (e.g. "Am F C G").
        toks = args.chords
        if len(toks) >= 3 and toks[1] in (
                "major", "minor", "dorian", "phrygian", "lydian",
                "mixolydian", "locrian", "aeolian", "ionian"):
            from .scales import Key
            key = Key(toks[0], toks[1])
            progression = [c.symbol or str(c)
                           for c in key.progression(*toks[2:])]
        else:
            progression = toks

    metro = Metronome(
        bpm=args.bpm, beats=args.beats, subdivide=args.subdivide,
        accent=not args.no_accent, progression=progression,
        end_bpm=args.to, step=args.step, every=args.every,
        hold=not args.no_hold)

    sig = f"{args.beats}/4"
    if args.to:
        print(f"  Tempo trainer: {args.bpm} → {args.to} BPM, "
              f"+{args.step} every {args.every} beats  ({sig})")
    else:
        print(f"  Metronome: {args.bpm} BPM  ({sig})")
    if progression:
        print(f"  Cycling: {' | '.join(progression)}")
    print("  Press Ctrl-C to stop.\n")

    last = {"bpm": None, "sym": None}

    def on_bar(index, bpm, symbol):
        # Reprint only when something changes, so the terminal stays calm.
        if bpm != last["bpm"] or symbol != last["sym"]:
            chord = f"  {symbol}" if symbol else ""
            print(f"  bar {index + 1:>3}   {bpm:>5g} BPM{chord}")
            last["bpm"], last["sym"] = bpm, symbol

    try:
        metro.start(on_bar=on_bar)
    except KeyboardInterrupt:
        pass
    print("\n  Stopped.")


def cmd_demo(args):
    import random
    from .rhythm import Score, Pattern, Duration
    from .chords import Chord
    from .scales import Key
    from .play import play_score

    moods = [
        {"name": "Bossa Nova", "key": ("A", "minor"), "drums": "bossa nova",
         "fill": "bossa nova", "bpm": 140,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("pluck_synth", "none", 0.2, -0.1),
         "pad": ("fm", "pad", -0.2),
         "bass_lp": 600, "reverb_type": "plate"},
        {"name": "Jazz Club", "key": ("Bb", "major"), "drums": "jazz",
         "fill": "jazz", "bpm": 108,
         "prog": ("I", "vi", "ii", "V"),
         "lead": ("triangle", "strings", 0.3, 0.2),
         "pad": ("fm", "piano", -0.3),
         "bass_lp": 700, "reverb_type": "plate"},
        {"name": "Afrobeat", "key": ("E", "minor"), "drums": "afrobeat",
         "fill": "afrobeat", "bpm": 115,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("saw", "pluck", 0.15, 0.3),
         "pad": ("supersaw", "pad", 0.0),
         "bass_lp": 500, "reverb_type": "cathedral"},
        {"name": "House", "key": ("C", "minor"), "drums": "house",
         "fill": "house", "bpm": 124,
         "prog": ("i", "IV", "V", "i"),
         "lead": ("saw", "staccato", 0.2, 0.4),
         "pad": ("supersaw", "pad", 0.0),
         "bass_lp": 300, "reverb_type": "plate"},
        {"name": "Reggae", "key": ("G", "major"), "drums": "reggae",
         "fill": "reggae", "bpm": 80,
         "prog": ("I", "IV", "V", "IV"),
         "lead": ("pluck_synth", "none", 0.25, 0.15),
         "pad": ("organ_synth", "organ", -0.3),
         "bass_lp": 400, "reverb_type": "cathedral"},
        {"name": "Funk", "key": ("E", "minor"), "drums": "funk",
         "fill": "funk", "bpm": 100,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("saw", "pluck", 0.15, 0.3),
         "pad": ("square", "staccato", -0.4),
         "bass_lp": 500, "reverb_type": "plate"},
        {"name": "Dub", "key": ("A", "minor"), "drums": "dub",
         "fill": "reggae", "bpm": 72,
         "prog": ("i", "iv", "i", "V"),
         "lead": ("triangle", "strings", 0.4, 0.2),
         "pad": ("pwm_slow", "pad", -0.3),
         "bass_lp": 350, "reverb_type": "cathedral"},
        {"name": "Temple", "key": ("E", "minor"), "drums": "bolero",
         "fill": "bossa nova", "bpm": 65,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("pluck_synth", "none", 0.3, 0.2),
         "pad": ("strings_synth", "pad", 0.0),
         "bass_lp": 200, "reverb_type": "taj_mahal"},
        {"name": "Classical", "key": ("D", "minor"), "drums": "bolero",
         "fill": "bossa nova", "bpm": 72,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("flute_synth", "strings", 0.35, 0.2),
         "pad": ("cello_synth", "bowed", -0.2),
         "bass_lp": 400, "reverb_type": "cathedral"},
        {"name": "Harpsichord Suite", "key": ("A", "minor"), "drums": "bolero",
         "fill": "bossa nova", "bpm": 92,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("harpsichord_synth", "none", 0.2, 0.1),
         "pad": ("strings_synth", "pad", -0.3),
         "bass_lp": 500, "reverb_type": "plate"},
        {"name": "Bhangra", "key": ("G", "minor"), "drums": "bhangra",
         "fill": "rock", "bpm": 140,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("sitar_synth", "none", 0.3, 0.2),
         "pad": ("strings_synth", "pad", 0.0),
         "bass_lp": 400, "reverb_type": "taj_mahal"},
        {"name": "Jazz Trio", "key": ("F", "major"), "drums": "swing",
         "fill": "jazz", "bpm": 100,
         "prog": ("I", "vi", "ii", "V"),
         "lead": ("trumpet_synth", "bowed", 0.3, 0.2),
         "pad": ("piano_synth", "none", -0.2),
         "bass_lp": 600, "reverb_type": "plate"},
        {"name": "Theremin Noir", "key": ("A", "minor"), "drums": "hip hop",
         "fill": "rock", "bpm": 85,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("theremin_synth", "pad", 0.4, 0.0),
         "pad": ("strings_synth", "pad", 0.0),
         "bass_lp": 300, "reverb_type": "cave"},
        {"name": "Caribbean", "key": ("C", "major"), "drums": "reggae",
         "fill": "reggae", "bpm": 110,
         "prog": ("I", "IV", "V", "IV"),
         "lead": ("steel_drum_synth", "none", 0.25, 0.3),
         "pad": ("acoustic_guitar_synth", "none", -0.3),
         "bass_lp": 500, "reverb_type": "plate"},
        {"name": "Accordion Waltz", "key": ("D", "minor"), "drums": "waltz",
         "fill": "jazz", "bpm": 88,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("accordion_synth", "organ", 0.2, 0.1),
         "pad": ("strings_synth", "pad", -0.2),
         "bass_lp": 500, "reverb_type": "plate"},
        {"name": "Kalimba Dreams", "key": ("G", "major"), "drums": "cajon folk",
         "fill": "bossa nova", "bpm": 95,
         "prog": ("I", "vi", "IV", "V"),
         "lead": ("kalimba_synth", "none", 0.35, 0.2),
         "pad": ("piano_synth", "none", -0.2),
         "bass_lp": 400, "reverb_type": "taj_mahal"},
        {"name": "Outback Drone", "key": ("E", "minor"), "drums": "djembe",
         "fill": "afrobeat", "bpm": 70,
         "prog": ("i", "iv", "i", "V"),
         "lead": ("didgeridoo_synth", "pad", 0.3, 0.0),
         "pad": ("granular_synth", "pad", 0.0),
         "bass_lp": 200, "reverb_type": "cave"},
        {"name": "Highland", "key": ("A", "minor"), "drums": "flamenco",
         "fill": "rock", "bpm": 95,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("bagpipe_synth", "organ", 0.15, 0.0),
         "pad": ("strings_synth", "pad", -0.2),
         "bass_lp": 400, "reverb_type": "cathedral"},
        {"name": "Nashville Tears", "key": ("G", "major"), "drums": "country",
         "fill": "rock", "bpm": 85,
         "prog": ("I", "IV", "V", "IV"),
         "lead": ("pedal_steel_synth", "strings", 0.35, 0.2),
         "pad": ("piano_synth", "none", -0.3),
         "bass_lp": 500, "reverb_type": "spring"},
        {"name": "Tabla Fusion", "key": ("E", "minor"), "drums": "teental",
         "fill": "rock", "bpm": 120,
         "prog": ("i", "iv", "V", "i"),
         "lead": ("sitar_synth", "none", 0.3, 0.2),
         "pad": ("vocal_synth", "pad", 0.0),
         "bass_lp": 400, "reverb_type": "taj_mahal"},
    ]

    mood = random.choice(moods)
    tonic, mode = mood["key"]
    key = Key(tonic, mode)
    chords = key.progression(*mood["prog"])
    lead_synth, lead_env, lead_reverb, lead_pan = mood["lead"]
    pad_synth, pad_env, pad_pan = mood["pad"]

    score = Score("4/4", bpm=mood["bpm"], drum_humanize=0.15)
    score.drums(mood["drums"], repeats=4, fill=mood["fill"])

    pad = score.part(
        "pad", synth=pad_synth, envelope=pad_env,
        volume=0.2, pan=pad_pan,
        detune=10, spread=0.5,
        reverb=0.4, reverb_type=mood["reverb_type"],
        chorus=0.2,
        sidechain=0.4 if mood["bpm"] > 100 else 0.0,
    )
    lead = score.part(
        "lead", synth=lead_synth, envelope=lead_env,
        volume=0.4, pan=lead_pan,
        delay=0.2, delay_time=round(30 / mood["bpm"], 3),
        delay_feedback=0.35,
        reverb=lead_reverb, reverb_type=mood["reverb_type"],
        lowpass=3500,
        humanize=0.2,
    )
    bass = score.part(
        "bass", synth="sine", envelope="pluck",
        volume=0.45, pan=0.0,
        lowpass=mood["bass_lp"],
        humanize=0.15,
    )

    for chord in chords * 2:
        pad.add(chord, Duration.WHOLE)

    # Melody: chord tones with passing tones, rests for breathing
    scale_tones = [t.name for t in key.scale.tones[:-1]]
    for i, chord in enumerate(chords):
        chord_tones = [t.name for t in chord.tones]
        beats_left = 4.0
        while beats_left > 0.5:
            if random.random() < 0.25:
                r = random.choice([0.5, 1.0, 1.5])
                r = min(r, beats_left)
                lead.rest(r)
                beats_left -= r
            else:
                n = random.choice(chord_tones if random.random() < 0.65 else scale_tones)
                oct = 5 if random.random() < 0.6 else 4
                dur = random.choice([0.67, 1.0, 1.5, 2.0])
                dur = min(dur, beats_left)
                vel = random.randint(65, 105)
                lead.add(f"{n}{oct}", dur, velocity=vel)
                beats_left -= dur

    # Bass: root-fifth with velocity accents
    for chord in chords * 2:
        r = chord.root
        if r:
            fifth = r.add(7)
            bass.add(f"{r.name}2", Duration.QUARTER, velocity=95)
            bass.add(f"{r.name}2", Duration.QUARTER, velocity=55)
            bass.add(f"{fifth.name}2", Duration.QUARTER, velocity=65)
            bass.add(f"{r.name}2", Duration.QUARTER, velocity=75)

    prog_str = " → ".join(c.symbol or str(c) for c in chords)
    print(f"  ♫  {mood['name']}")
    print(f"     {tonic} {mode} | {mood['bpm']} bpm")
    print(f"     {prog_str}")
    print(f"     {mood['drums']} | {lead_synth} lead | {pad_synth} pad | {mood['reverb_type']} reverb")
    print()

    try:
        play_score(score)
    except KeyboardInterrupt:
        pass
    print("  ♫")


def cmd_detect(args):
    from .scales import Key
    key = Key.detect(*args.notes)
    if getattr(args, "json", False):
        _emit_json({"key": str(key) if key else None,
                    "scale": list(key.note_names) if key else None})
    elif key:
        print(f"  Detected key: {key}")
        print(f"  Scale: {' '.join(key.note_names)}")
    else:
        print("  Could not detect key")
    if key and getattr(args, "play", False):
        _play_items(list(key.scale.tones), t=400)


def cmd_analyze(args):
    from .chords import (Chord, analyze_progression, find_cadences,
                         detect_secondary_dominant)
    from .scales import Key

    try:
        chords = [Chord.from_symbol(s) for s in args.chords]
    except Exception as e:
        print(f"  Could not parse chords: {e}")
        return

    # Determine the key — given, or detected from all the notes.
    if args.key:
        tonic, mode, source = args.key, args.mode, "given"
    else:
        all_notes = [t.name for c in chords for t in c.tones]
        detected = Key.detect(*all_notes)
        if detected is None:
            print("  Could not detect a key — pass --key.")
            return
        tonic, mode, source = detected.tonic_name, detected.mode, "detected"

    romans = analyze_progression(chords, tonic, mode, secondary_dominants=True)
    cadences = dict(find_cadences(chords, tonic, mode))

    if getattr(args, "json", False):
        _emit_json({
            "key": f"{tonic} {mode}", "key_source": source,
            "chords": [
                {"symbol": sym, "roman": roman,
                 "name": chord.identify() or sym,
                 "secondary_dominant": detect_secondary_dominant(chord, tonic, mode)}
                for sym, chord, roman in zip(args.chords, chords, romans)
            ],
            "cadences": [
                {"from": args.chords[idx - 1], "to": args.chords[idx], "type": cad}
                for idx, cad in cadences.items()
            ],
        })
    else:
        print(f"  Key: {tonic} {mode}  ({source})")
        print()
        for symbol, chord, roman in zip(args.chords, chords, romans):
            name = chord.identify() or symbol
            applied = detect_secondary_dominant(chord, tonic, mode)
            note = "  (secondary dominant)" if applied else ""
            print(f"    {symbol:8s} {(roman or '?'):8s} {name}{note}")
        print()
        if cadences:
            print("  Cadences:")
            for idx, cadence in cadences.items():
                print(f"    {args.chords[idx - 1]} → {args.chords[idx]}: {cadence}")
        else:
            print("  No cadences detected.")
    if getattr(args, "play", False):
        _play_items(chords, t=900)


def cmd_reharmonize(args):
    from .chords import Chord, reharmonize, reharmonize_progression
    try:
        chords = [Chord.from_symbol(s) for s in args.chords]
    except Exception as e:
        print(f"  Could not parse chords: {e}")
        return

    # One chord -> list substitution ideas. Several -> reharmonize the whole
    # progression with the chosen technique.
    if len(chords) == 1:
        chord = chords[0]
        subs = reharmonize(chord, args.key, args.mode)
        if getattr(args, "json", False):
            _emit_json({
                "chord": chord.identify() or args.chords[0],
                "key": f"{args.key} {args.mode}",
                "suggestions": [
                    {"technique": s["technique"],
                     "chord": s["chord"].identify() or str(s["chord"]),
                     "description": s["description"]}
                    for s in subs
                ],
            })
        else:
            print(f"  Reharmonizing {chord.identify() or args.chords[0]} "
                  f"in {args.key} {args.mode}:\n")
            for s in subs:
                print(f"    {s['technique']:22s} "
                      f"{s['chord'].identify() or str(s['chord'])}")
                print(f"      {s['description']}")
        if getattr(args, "play", False):
            _play_items([chord] + [s["chord"] for s in subs], t=1100)
        return

    new = reharmonize_progression(chords, args.key, args.mode, args.technique)

    def labels(seq):
        return [c.symbol or (c.identify() or str(c)) for c in seq]

    if getattr(args, "json", False):
        _emit_json({
            "key": f"{args.key} {args.mode}", "technique": args.technique,
            "original": labels(chords), "reharmonized": labels(new),
        })
    else:
        print(f"  Reharmonizing in {args.key} {args.mode} "
              f"({args.technique}):\n")
        print(f"    original:      {' → '.join(labels(chords))}")
        print(f"    reharmonized:  {' → '.join(labels(new))}")
    if getattr(args, "play", False):
        _play_items(new, t=900)


def main():
    parser = argparse.ArgumentParser(
        prog="pytheory",
        description="Music Theory for Humans — from the command line",
    )
    sub = parser.add_subparsers(dest="command")

    # Shared flags for the theory/music commands.
    io = argparse.ArgumentParser(add_help=False)
    io.add_argument("--json", action="store_true", help="Output as JSON")
    io.add_argument("--play", action="store_true", help="Play the result as audio")

    # tone
    p = sub.add_parser("tone", parents=[io], help="Look up a tone (e.g. pytheory tone C4)")
    p.add_argument("note", help="Note name with octave (e.g. C4, A#3)")
    p.add_argument("--temperament", "-t", default="equal",
                   choices=["equal", "pythagorean", "meantone"],
                   help="Tuning temperament (default: equal)")

    # scale
    p = sub.add_parser("scale", parents=[io], help="Show a scale (e.g. pytheory scale C major)")
    p.add_argument("tonic", help="Tonic note (e.g. C, G, Sa)")
    p.add_argument("mode", help="Scale/mode name (e.g. major, minor, dorian)")
    p.add_argument("--system", default="western", help="Musical system (default: western)")

    # chord
    p = sub.add_parser("chord", parents=[io], help="Identify a chord (e.g. pytheory chord C E G)")
    p.add_argument("notes", nargs="+", help="Note names (e.g. C E G)")

    # key
    p = sub.add_parser("key", parents=[io], help="Explore a key (e.g. pytheory key C major)")
    p.add_argument("tonic", help="Tonic note (e.g. C, G)")
    p.add_argument("mode", nargs="?", default="major", help="Mode (default: major)")

    # fingering
    p = sub.add_parser("fingering", parents=[io], help="Guitar fingering (e.g. pytheory fingering Am)")
    p.add_argument("chord", help="Chord name (e.g. C, Am, G7)")
    p.add_argument("--capo", type=int, default=0, help="Capo fret (default: 0)")

    # progression
    p = sub.add_parser("progression", parents=[io], help="Build a progression (e.g. pytheory progression C major I V vi IV)")
    p.add_argument("tonic", help="Tonic note")
    p.add_argument("mode", help="Mode (e.g. major, minor)")
    p.add_argument("numerals", nargs="+", help="Roman numerals (e.g. I V vi IV)")

    # analyze
    p = sub.add_parser("analyze", parents=[io], help="Analyze a chord progression (e.g. pytheory analyze C D7 G7 C)")
    p.add_argument("chords", nargs="+", help="Chord symbols (e.g. C D7 G7 C)")
    p.add_argument("--key", help="Key tonic (e.g. C). Auto-detected if omitted.")
    p.add_argument("--mode", default="major", help="major or minor (default: major)")

    # reharmonize
    p = sub.add_parser("reharmonize", aliases=["reharm"], parents=[io],
                       help="Reharmonize a chord or progression (e.g. pytheory reharmonize G7 --key C)")
    p.add_argument("chords", nargs="+",
                   help="One chord for substitution ideas, or several to reharmonize the progression")
    p.add_argument("--key", default="C", help="Key tonic (default: C)")
    p.add_argument("--mode", default="major", help="major or minor (default: major)")
    p.add_argument("--technique", default="secondary_dominants",
                   choices=["secondary_dominants", "tritone", "diatonic"],
                   help="Progression reharmonization technique (default: secondary_dominants)")

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
    p = sub.add_parser("identify", parents=[io], help="Identify a chord symbol (e.g. pytheory identify Cmaj7)")
    p.add_argument("symbol", help="Chord symbol (e.g. Cmaj7, Am, F#m7b5)")

    # midi
    p = sub.add_parser("midi", help="Export a progression to MIDI (e.g. pytheory midi C major I V vi IV)")
    p.add_argument("tonic", help="Tonic note")
    p.add_argument("mode", help="Mode (e.g. major, minor)")
    p.add_argument("numerals", nargs="+", help="Roman numerals (e.g. I V vi IV)")
    p.add_argument("-o", "--output", default="output.mid", help="Output file (default: output.mid)")
    p.add_argument("--bpm", type=int, default=120, help="BPM (default: 120)")
    p.add_argument("--duration", type=int, default=500, help="Duration per chord in ms (default: 500)")

    # raga
    p = sub.add_parser("raga",
                       help="Explore a Hindustani raga (e.g. pytheory raga yaman)")
    p.add_argument("name", nargs="?", default=None,
                   help="Raga name (e.g. yaman, bhairav, malkauns); omit to list all")
    p.add_argument("--sa", default="C", help="Tonic note for Sa (default: C)")
    p.add_argument("--shruti", action="store_true",
                   help="Show just-intonation shruti detail (cents off 12-TET)")
    p.add_argument("--play", action="store_true", help="Play the aroha/avaroha")
    p.add_argument("--reverb", type=float, default=0.35,
                   help="Reverb wet mix 0..1 for --play (default: 0.35)")
    p.add_argument("--equal", action="store_true",
                   help="Play in 12-TET instead of just intonation")
    p.add_argument("--list", action="store_true", help="List all ragas")
    p.add_argument("--thaat", default=None, help="Filter the list by thaat")
    p.add_argument("--tradition", default=None,
                   help="Filter the list by tradition (hindustani / carnatic)")
    p.add_argument("--time", default=None, help="Filter the list by time of day")

    # maqam
    p = sub.add_parser("maqam",
                       help="Explore an Arabic maqam (e.g. pytheory maqam rast)")
    p.add_argument("name", nargs="?", default=None,
                   help="Maqam name (e.g. rast, bayati, hijaz, saba); omit to list all")
    p.add_argument("--tonic", default="C", help="Tonic note (default: C)")
    p.add_argument("--tuning", action="store_true",
                   help="Show quarter-tone (just) intonation, cents off 12-TET")
    p.add_argument("--play", action="store_true", help="Play the maqam ascending/descending")
    p.add_argument("--reverb", type=float, default=0.3,
                   help="Reverb wet mix 0..1 for --play (default: 0.3)")
    p.add_argument("--list", action="store_true", help="List all maqamat")
    p.add_argument("--family", default=None, help="Filter the list by family")

    # metronome
    p = sub.add_parser("metronome", aliases=["metro"],
                       help="Metronome, chord-practice click, and tempo trainer")
    p.add_argument("bpm", nargs="?", type=float, default=120,
                   help="Tempo in BPM (default: 120)")
    p.add_argument("--beats", "-b", type=int, default=4,
                   help="Beats per bar (default: 4)")
    p.add_argument("--subdivide", "-s", type=int, default=1,
                   help="Clicks per beat: 2=eighths, 3=triplets, 4=sixteenths (default: 1)")
    p.add_argument("--no-accent", action="store_true",
                   help="Don't accent the downbeat")
    p.add_argument("--chords", "-c", nargs="+", default=None,
                   metavar="CHORD",
                   help="Cycle chords under the click — symbols (Am F C G) "
                        "or a key + numerals (C major I V vi IV)")
    p.add_argument("--to", type=float, default=None,
                   help="Tempo-trainer target BPM — ramp from BPM to this")
    p.add_argument("--step", type=float, default=5,
                   help="BPM change per ramp step (default: 5)")
    p.add_argument("--every", type=int, default=8,
                   help="Beats between ramp steps (default: 8)")
    p.add_argument("--no-hold", action="store_true",
                   help="Stop when the trainer reaches the target (default: keep going)")

    # demo
    sub.add_parser("demo", help="Play a randomly generated track (different every time)")

    # repl
    sub.add_parser("repl", help="Interactive music theory scratchpad")

    # live
    p = sub.add_parser("live", help="Real-time MIDI synth rig (e.g. pytheory live --port OP-XY)")
    p.add_argument("seed", nargs="?", type=int, default=None,
                   help="Random seed for instrument picks")
    p.add_argument("--port", "-p", default="OP-XY",
                   help="MIDI port name (default: OP-XY)")
    p.add_argument("--channels", "-c", type=int, default=8,
                   help="Number of channels (default: 8)")
    p.add_argument("--drums", "-d", default="rock",
                   help="Drum pattern (default: rock, 'none' to disable)")
    p.add_argument("--buffer", "-b", type=int, default=128,
                   help="Audio buffer size (default: 128)")
    p.add_argument("--link", action="store_true",
                   help="Sync tempo/beat/transport with an Ableton Link session (needs pytheory[link])")

    # studio
    p = sub.add_parser("studio", help="Browser studio: drop in a recording, get sheet music, playback, and MIDI")
    p.add_argument("--port", type=int, default=8124, help="Port (default: 8124)")
    p.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")

    # tune
    p = sub.add_parser("tune", help="Real-time instrument tuner (e.g. pytheory tune, or --serve for browser/JS)")
    p.add_argument("--serve", action="store_true", help="Serve a browser strobe tuner page + JS pitch stream (SSE + WebSocket)")
    p.add_argument("--instrument", "-i", default=None,
                   choices=["guitar", "bass", "ukulele", "violin", "viola",
                            "cello", "mandolin", "banjo"],
                   help="Lock readings to this instrument's open strings")
    p.add_argument("--chords", action="store_true",
                   help="Identify chords too — strum and see the chord name")
    p.add_argument("--port", type=int, default=8123, help="Port for --serve (default: 8123)")
    p.add_argument("--ref", type=float, default=440.0, help="Reference pitch for A4 in Hz (default: 440)")
    p.add_argument("--device", type=int, default=None, help="Input device index (default: system default)")
    p.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser with --serve")

    # transcribe
    p = sub.add_parser("transcribe", help="Transcribe a recording to notes/MIDI (e.g. pytheory transcribe hum.m4a out.mid)")
    p.add_argument("input", help="Input audio file (WAV directly; .m4a/.mp3 via afconvert/ffmpeg)")
    p.add_argument("output", nargs="?", default=None, help="Optional output MIDI file")
    p.add_argument("--bpm", type=int, default=None, help="Tempo to interpret timing against (default: estimate from the recording)")
    p.add_argument("--split", action="store_true", help="Separate drums out and transcribe bass + melody parts (for full mixes)")
    p.add_argument("--quantize", type=float, default=None, help="Snap to grid in beats (e.g. 0.25 = sixteenths)")
    p.add_argument("--fmin", type=float, default=50.0, help="Lowest pitch to search, Hz (default: 50)")
    p.add_argument("--fmax", type=float, default=1500.0, help="Highest pitch to search, Hz (default: 1500)")
    p.add_argument("--play", action="store_true", help="Play the transcription back")

    # detect
    p = sub.add_parser("detect", parents=[io], help="Detect key from notes (e.g. pytheory detect C E G)")
    p.add_argument("notes", nargs="+", help="Note names")

    # modes
    p = sub.add_parser("modes", parents=[io], help="Show all modes of a note (e.g. pytheory modes C)")
    p.add_argument("tonic", help="Tonic note (e.g. C, G)")
    p.add_argument("--system", default="western", help="Musical system (default: western)")

    # circle
    p = sub.add_parser("circle", parents=[io], help="Circle of fifths/fourths (e.g. pytheory circle C)")
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
        "raga": cmd_raga,
        "maqam": cmd_maqam,
        "metronome": cmd_metronome,
        "metro": cmd_metronome,
        "identify": cmd_identify,
        "midi": cmd_midi,
        "demo": cmd_demo,
        "repl": lambda args: __import__('pytheory.repl', fromlist=['main']).main(),
        "live": cmd_live,
        "transcribe": cmd_transcribe,
        "tune": cmd_tune,
        "studio": cmd_studio,
        "detect": cmd_detect,
        "analyze": cmd_analyze,
        "reharmonize": cmd_reharmonize,
        "reharm": cmd_reharmonize,
        "modes": cmd_modes,
        "circle": cmd_circle,
        "progressions": cmd_progressions,
    }
    try:
        commands[args.command](args)
    except (KeyError, ValueError) as e:
        # Bad user input (unknown raga/maqam/chord, malformed numeral, …):
        # a friendly one-liner, not a raw traceback. Set PYTHEORY_DEBUG=1
        # to re-raise and see the stack.
        if os.environ.get("PYTHEORY_DEBUG"):
            raise
        msg = e.args[0] if e.args else str(e)
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
