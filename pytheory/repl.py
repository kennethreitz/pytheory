"""PyTheory REPL — make music interactively.

Commands mirror the Python API so there's no new vocabulary to learn.
What you type in the REPL is what you'd type in a script.

Usage:
    pytheory repl
"""

import readline
import sys

from .scales import Key, TonedScale
from .chords import Chord
from .tones import Tone
from .rhythm import Score, Pattern, Duration, Part


# ── State ──────────────────────────────────────────────────────────────────

class Session:
    """The live session state."""

    def __init__(self):
        self.key = Key("C", "major")
        self.bpm = 120
        self.time_sig = "4/4"
        self.swing = 0.0
        self.score = Score(self.time_sig, bpm=self.bpm)
        self.current_part = None
        self.parts = {}
        self._drum_preset = None

    def rebuild(self):
        """Rebuild score from settings."""
        self.score = Score(self.time_sig, bpm=self.bpm, swing=self.swing)
        self.parts = {}
        self.current_part = None
        if self._drum_preset:
            self.score.drums(self._drum_preset, repeats=4)

    def ensure_part(self, name="lead"):
        if name not in self.parts:
            self.parts[name] = self.score.part(name)
        return self.parts[name]


# ── Commands ───────────────────────────────────────────────────────────────

def cmd_help(session, args):
    print("""
  PyTheory REPL — commands mirror the Python API

  Theory:
    key Am                      Key("A", "minor")
    key G major                 Key("G", "major")
    chords                      key.chords
    progression I V vi IV       key.progression(...)
    modes                       show all modes
    scales                      list available scales

  Score:
    bpm 140                     Score("4/4", bpm=140)
    time 3/4                    TimeSignature
    swing 0.5                   Score(swing=0.5)
    drums bossa nova            score.drums("bossa nova")
    drums                       list all presets

  Parts:
    part lead saw pluck         score.part("lead", synth="saw", envelope="pluck")
    part bass sine              score.part("bass", synth="sine")
    part                        list all parts

  Notes (on active part):
    add C5 1                    part.add("C5", 1.0)
    add Am 4                    part.add(Chord.from_symbol("Am"), 4.0)
    rest 2                      part.rest(2.0)
    arp Am updown 2 2           part.arpeggio("Am", pattern="updown", bars=2, octaves=2)
    prog I V vi IV              part adds key.progression(...)

  Effects (on active part):
    reverb 0.4                  reverb=0.4
    delay 0.3 0.375             delay=0.3, delay_time=0.375
    lowpass 2000 3              lowpass=2000, lowpass_q=3
    distortion 0.5              distortion=0.5
    chorus 0.3                  chorus=0.3
    sidechain 0.8               sidechain=0.8
    humanize 0.3                humanize=0.3
    volume 0.5                  volume=0.5
    legato on                   legato=True
    glide 0.04                  glide=0.04
    set lowpass 3000            part.set(lowpass=3000)
    lfo lowpass 0.5 400 3000 8  part.lfo("lowpass", rate=0.5, ...)

  Playback:
    play_score                  play the full score
    play_pattern                play just the drums
    render sketch.wav           render to WAV
    save_midi sketch.mid        save as MIDI

  Session:
    show                        score info
    status                      current state
    clear                       reset everything
    help                        this message
    quit                        exit
""")


def cmd_key(session, args):
    if not args:
        notes = " ".join(session.key.note_names)
        print(f"  {session.key}: {notes}")
        return
    if len(args) == 1:
        name = args[0]
        if name.endswith("m") and len(name) <= 3:
            tonic, mode = name[:-1], "minor"
        else:
            tonic, mode = name, "major"
    else:
        tonic, mode = args[0], " ".join(args[1:])
    try:
        session.key = Key(tonic, mode)
        notes = " ".join(session.key.note_names)
        print(f"  {session.key}: {notes}")
    except (KeyError, ValueError) as e:
        print(f"  error: {e}")


def cmd_bpm(session, args):
    if not args:
        print(f"  bpm={session.bpm}")
        return
    session.bpm = int(args[0])
    session.score.bpm = session.bpm
    print(f"  bpm={session.bpm}")


def cmd_swing(session, args):
    if not args:
        print(f"  swing={session.swing}")
        return
    session.swing = float(args[0])
    session.score.swing = session.swing
    print(f"  swing={session.swing}")


def cmd_drums(session, args):
    if not args:
        presets = Pattern.list_presets()
        cols = 4
        for i in range(0, len(presets), cols):
            row = presets[i:i + cols]
            print("  " + "  ".join(f"{p:<18s}" for p in row))
        return
    preset = " ".join(args[:-1]) if args[-1].isdigit() else " ".join(args)
    repeats = int(args[-1]) if args[-1].isdigit() else 4
    try:
        session._drum_preset = preset
        session.score.drums(preset, repeats=repeats)
        print(f"  score.drums(\"{preset}\", repeats={repeats})")
    except ValueError as e:
        print(f"  error: {e}")


def cmd_time(session, args):
    if not args:
        print(f"  time={session.time_sig}")
        return
    session.time_sig = args[0]
    session.rebuild()
    print(f"  time={session.time_sig}")


def cmd_part(session, args):
    if not args:
        if session.parts:
            for name, part in session.parts.items():
                active = " ←" if part is session.current_part else ""
                print(f"  {name}: synth={part.synth} envelope={part.envelope} "
                      f"vol={part.volume}{active}")
        else:
            print("  no parts (type: part lead saw pluck)")
        return

    name = args[0]
    synth = args[1] if len(args) > 1 else "saw"
    envelope = args[2] if len(args) > 2 else "pluck"

    if name not in session.parts:
        session.parts[name] = session.score.part(name, synth=synth, envelope=envelope)
        print(f"  score.part(\"{name}\", synth=\"{synth}\", envelope=\"{envelope}\")")
    else:
        print(f"  → {name}")
    session.current_part = session.parts[name]


def _require_part(session):
    if session.current_part is None:
        session.parts["lead"] = session.score.part("lead", synth="saw", envelope="pluck")
        session.current_part = session.parts["lead"]
        print("  (auto-created lead: saw + pluck)")
    return session.current_part


def cmd_add(session, args):
    if not args:
        print("  usage: add C5 1   or   add Am 4")
        return
    part = _require_part(session)
    name = args[0]
    beats = float(args[1]) if len(args) > 1 else 1.0
    velocity = int(args[2]) if len(args) > 2 else 100

    # Try as chord first, then as note
    try:
        chord = Chord.from_symbol(name)
        part.add(chord, beats)
        print(f"  .add(Chord.from_symbol(\"{name}\"), {beats})")
        return
    except (ValueError, KeyError):
        pass

    try:
        part.add(name, beats, velocity=velocity)
        vel_str = f", velocity={velocity}" if velocity != 100 else ""
        print(f"  .add(\"{name}\", {beats}{vel_str})")
    except Exception as e:
        print(f"  error: {e}")


def cmd_rest(session, args):
    part = _require_part(session)
    beats = float(args[0]) if args else 1.0
    part.rest(beats)
    print(f"  .rest({beats})")


def cmd_arp(session, args):
    if not args:
        print("  usage: arp Am [pattern] [bars] [octaves]")
        return
    part = _require_part(session)
    chord_name = args[0]
    pattern = args[1] if len(args) > 1 else "up"
    bars = float(args[2]) if len(args) > 2 else 2
    octaves = int(args[3]) if len(args) > 3 else 1
    try:
        part.arpeggio(chord_name, bars=bars, pattern=pattern, octaves=octaves)
        print(f"  .arpeggio(\"{chord_name}\", pattern=\"{pattern}\", "
              f"bars={bars}, octaves={octaves})")
    except Exception as e:
        print(f"  error: {e}")


def cmd_prog(session, args):
    if not args:
        print("  usage: prog I V vi IV")
        return
    part = _require_part(session)
    try:
        chords = session.key.progression(*args)
        for chord in chords:
            part.add(chord, Duration.WHOLE)
        symbols = [c.symbol or str(c) for c in chords]
        print(f"  {' → '.join(symbols)}")
    except Exception as e:
        print(f"  error: {e}")


def _set_effect(session, param, args, default=0.3):
    part = _require_part(session)
    value = float(args[0]) if args else default
    attr_map = {
        "reverb": "reverb_mix", "delay": "delay_mix",
        "distortion": "distortion_mix", "chorus": "chorus_mix",
    }
    attr = attr_map.get(param, param)
    setattr(part, attr, value)
    print(f"  {part.name}: {param}={value}")

    if param == "delay" and len(args) > 1:
        part.delay_time = float(args[1])
        print(f"  {part.name}: delay_time={part.delay_time}")
    if param == "lowpass" and len(args) > 1:
        part.lowpass_q = float(args[1])
        print(f"  {part.name}: lowpass_q={part.lowpass_q}")


def cmd_set(session, args):
    """Automation: part.set() at current beat."""
    if len(args) < 2:
        print("  usage: set lowpass 3000")
        return
    part = _require_part(session)
    param = args[0]
    value = float(args[1])
    part.set(**{param: value})
    print(f"  .set({param}={value})")


def cmd_lfo(session, args):
    """LFO automation."""
    if len(args) < 4:
        print("  usage: lfo lowpass 0.5 400 3000 [bars] [shape]")
        return
    part = _require_part(session)
    param = args[0]
    rate = float(args[1])
    min_val = float(args[2])
    max_val = float(args[3])
    bars = float(args[4]) if len(args) > 4 else 4
    shape = args[5] if len(args) > 5 else "sine"
    part.lfo(param, rate=rate, min=min_val, max=max_val, bars=bars, shape=shape)
    print(f"  .lfo(\"{param}\", rate={rate}, min={min_val}, max={max_val}, "
          f"bars={bars}, shape=\"{shape}\")")


def cmd_legato(session, args):
    part = _require_part(session)
    part.legato = not (args and args[0] == "off")
    print(f"  legato={'on' if part.legato else 'off'}")


def cmd_play_score(session, args):
    try:
        from .play import play_score
        print("  ♫ play_score()")
        play_score(session.score)
    except Exception as e:
        print(f"  error: {e}")


def cmd_play_pattern(session, args):
    if not session._drum_preset:
        print("  no drums set")
        return
    try:
        from .play import play_pattern
        print(f"  ♫ play_pattern(\"{session._drum_preset}\")")
        play_pattern(Pattern.preset(session._drum_preset),
                     repeats=4, bpm=session.bpm)
    except Exception as e:
        print(f"  error: {e}")


def cmd_render(session, args):
    path = args[0] if args else "output.wav"
    try:
        from .play import render_score, SAMPLE_RATE
        import scipy.io.wavfile
        import numpy
        buf = render_score(session.score)
        pcm = (buf * 32767).astype(numpy.int16)
        scipy.io.wavfile.write(path, SAMPLE_RATE, pcm)
        print(f"  saved: {path}")
    except Exception as e:
        print(f"  error: {e}")


def cmd_save_midi(session, args):
    path = args[0] if args else "output.mid"
    session.score.save_midi(path)
    print(f"  save_midi(\"{path}\")")


def cmd_show(session, args):
    s = session.score
    print(f"  {s}")
    for name, part in session.parts.items():
        active = " ←" if part is session.current_part else ""
        fx = []
        if part.reverb_mix > 0: fx.append(f"reverb={part.reverb_mix}")
        if part.delay_mix > 0: fx.append(f"delay={part.delay_mix}")
        if part.lowpass > 0: fx.append(f"lp={part.lowpass}")
        if part.distortion_mix > 0: fx.append(f"dist={part.distortion_mix}")
        if part.chorus_mix > 0: fx.append(f"chorus={part.chorus_mix}")
        if part.legato: fx.append("legato")
        if part.humanize > 0: fx.append(f"humanize={part.humanize}")
        fx_str = " " + " ".join(fx) if fx else ""
        print(f"    {name}: {part.synth}+{part.envelope} "
              f"{len(part.notes)} notes{fx_str}{active}")
    if s._drum_hits:
        print(f"    drums: {session._drum_preset} ({len(s._drum_hits)} hits)")


def cmd_chords(session, args):
    numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    for num, chord in zip(numerals, session.key.chords):
        print(f"  {num:6s}  {chord}")


def cmd_modes(session, args):
    ts = TonedScale(tonic=f"{session.key.tonic_name}4")
    for mode in ["ionian", "dorian", "phrygian", "lydian",
                 "mixolydian", "aeolian", "locrian"]:
        try:
            print(f"  {mode:<12s}  {' '.join(ts[mode].note_names)}")
        except KeyError:
            continue


def cmd_scales(session, args):
    ts = TonedScale(tonic=f"{session.key.tonic_name}4")
    for name in ts.scales:
        print(f"  {name:<20s}  {' '.join(ts[name].note_names)}")


def cmd_clear(session, args):
    session.rebuild()
    print("  cleared")


def cmd_status(session, args):
    parts = ", ".join(session.parts.keys()) if session.parts else "none"
    active = session.current_part.name if session.current_part else "none"
    print(f"  key={session.key}  bpm={session.bpm}  swing={session.swing}")
    print(f"  drums={session._drum_preset or 'none'}  parts=[{parts}]  active={active}")


# ── Dispatch ───────────────────────────────────────────────────────────────

COMMANDS = {
    "help": cmd_help, "?": cmd_help,
    "key": cmd_key,
    "bpm": cmd_bpm,
    "swing": cmd_swing,
    "drums": cmd_drums,
    "time": cmd_time,
    "part": cmd_part,
    "add": cmd_add,
    "rest": cmd_rest,
    "arp": cmd_arp,
    "prog": cmd_prog,
    "reverb": lambda s, a: _set_effect(s, "reverb", a),
    "delay": lambda s, a: _set_effect(s, "delay", a),
    "lowpass": lambda s, a: _set_effect(s, "lowpass", a, 2000),
    "lp": lambda s, a: _set_effect(s, "lowpass", a, 2000),
    "distortion": lambda s, a: _set_effect(s, "distortion", a),
    "dist": lambda s, a: _set_effect(s, "distortion", a),
    "chorus": lambda s, a: _set_effect(s, "chorus", a),
    "sidechain": lambda s, a: _set_effect(s, "sidechain", a),
    "humanize": lambda s, a: _set_effect(s, "humanize", a),
    "volume": lambda s, a: _set_effect(s, "volume", a, 0.5),
    "vol": lambda s, a: _set_effect(s, "volume", a, 0.5),
    "glide": lambda s, a: _set_effect(s, "glide", a, 0.04),
    "legato": cmd_legato,
    "set": cmd_set,
    "lfo": cmd_lfo,
    "play_score": cmd_play_score,
    "play_pattern": cmd_play_pattern,
    "render": cmd_render,
    "save_midi": cmd_save_midi,
    "show": cmd_show,
    "chords": cmd_chords,
    "modes": cmd_modes,
    "scales": cmd_scales,
    "clear": cmd_clear,
    "status": cmd_status,
}


# ── Main ───────────────────────────────────────────────────────────────────

def _prompt(session):
    """Build a context-aware multiline prompt."""
    key_str = f"{session.key.tonic_name}{('m' if session.key.mode == 'minor' else '')}"
    ctx = [f"key={key_str}", f"bpm={session.bpm}"]
    if session.swing > 0:
        ctx.append(f"swing={session.swing}")
    if session._drum_preset:
        ctx.append(f"drums={session._drum_preset}")
    if session.current_part is not None:
        p = session.current_part
        fx = []
        if p.reverb_mix > 0: fx.append(f"rev={p.reverb_mix}")
        if p.delay_mix > 0: fx.append(f"del={p.delay_mix}")
        if p.lowpass > 0: fx.append(f"lp={int(p.lowpass)}")
        if p.distortion_mix > 0: fx.append(f"dist={p.distortion_mix}")
        if p.legato: fx.append("legato")
        part_str = f"{p.name}({p.synth})"
        if fx:
            part_str += f" {' '.join(fx)}"
        ctx.append(f"→{part_str}")

    # Single line if short, multiline if long
    oneline = f"pytheory[{' | '.join(ctx)}]> "
    if len(oneline) <= 60:
        return oneline

    # Multiline
    lines = "  " + " | ".join(ctx)
    return f"{lines}\n♫> "


def main():
    session = Session()

    print()
    print("  ♫  PyTheory REPL")
    print("  ════════════════════════════════════════")
    print("  type 'help' for commands, 'quit' to exit")
    print()

    while True:
        try:
            line = input(_prompt(session)).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  ♫")
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            print("  ♫")
            break

        tokens = line.split()
        cmd = tokens[0].lower()
        args = tokens[1:]

        if cmd in COMMANDS:
            try:
                COMMANDS[cmd](session, args)
            except Exception:
                import traceback
                traceback.print_exc()
        else:
            print(f"  unknown: {cmd} (type 'help')")


if __name__ == "__main__":
    main()
