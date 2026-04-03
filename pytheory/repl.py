"""PyTheory REPL — make music interactively.

Commands mirror the Python API so there's no new vocabulary to learn.
What you type in the REPL is what you'd type in a script.

Usage:
    pytheory repl
"""

try:
    import readline
except ImportError:
    readline = None
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
    prog I V vi IV              key.progression(...)
    modes                       show all modes
    scales                      list available scales
    circle [C]                  circle of fifths/fourths
    interval C4 G4              name the interval
    identify C E G              identify a chord from notes
    identify Cmaj7              analyze a chord symbol
    system [indian]             switch musical system

  Score:
    bpm 140                     Score("4/4", bpm=140)
    time 3/4                    TimeSignature
    swing 0.5                   Score(swing=0.5)
    drums bossa nova            score.drums("bossa nova")
    drums                       list all presets

  Parts:
    part lead saw pluck         score.part("lead", synth="saw", envelope="pluck")
    part bass sine              score.part("bass", synth="sine")
    part lead instrument piano  score.part("lead", instrument="piano")
    part                        list all parts

  Notes (on active part):
    add C5 1                    part.add("C5", 1.0)
    add Am 4                    part.add(Chord.from_symbol("Am"), 4.0)
    rest 2                      part.rest(2.0)
    arp Am updown 2 2           part.arpeggio("Am", pattern="updown", bars=2, octaves=2)
    prog I V vi IV              part adds key.progression(...)
    strum Am 2 down             part.strum("Am", 2, direction="down")
    strum G 2 up 0.1            lazy strum (strum_time=0.1)
    roll C3 4                   part.roll("C3", 4) — timpani/tremolo
    roll C3 4 30 110            roll with velocity ramp
    bend C5 1 2                 part.add("C5", 1, bend=2) — bend up 2 semitones
    bend C5 1 -1                bend down a half step

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

  Guitar:
    fingering Am                guitar chord fingering
    diagram [mode] [frets]      scale diagram on guitar

  Tuning:
    temperament equal           set temperament (equal/pythagorean/meantone/just)
    temperament                 show current temperament
    reference 432               set reference pitch (default 440)
    instruments                 list all available instruments

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
        session.score.drums(preset, repeats=repeats)
        session._drum_preset = preset  # only persist after success
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

    if name not in session.parts:
        # Check if second arg is "instrument" keyword or an instrument name
        if len(args) > 1 and args[1] == "instrument" and len(args) > 2:
            instrument = args[2]
            session.parts[name] = session.score.part(name, instrument=instrument)
            print(f"  score.part(\"{name}\", instrument=\"{instrument}\")")
        elif len(args) > 1 and args[1] in _INSTRUMENT_NAMES:
            instrument = args[1]
            session.parts[name] = session.score.part(name, instrument=instrument)
            print(f"  score.part(\"{name}\", instrument=\"{instrument}\")")
        else:
            synth = args[1] if len(args) > 1 else "saw"
            envelope = args[2] if len(args) > 2 else "pluck"
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
        if part.reverb_mix > 0:
            fx.append(f"reverb={part.reverb_mix}")
        if part.delay_mix > 0:
            fx.append(f"delay={part.delay_mix}")
        if part.lowpass > 0:
            fx.append(f"lp={part.lowpass}")
        if part.distortion_mix > 0:
            fx.append(f"dist={part.distortion_mix}")
        if part.chorus_mix > 0:
            fx.append(f"chorus={part.chorus_mix}")
        if part.legato:
            fx.append("legato")
        if part.humanize > 0:
            fx.append(f"humanize={part.humanize}")
        fx_str = " " + " ".join(fx) if fx else ""
        print(f"    {name}: {part.synth}+{part.envelope} "
              f"{len(part.notes)} notes{fx_str}{active}")
    if s._drum_hits:
        print(f"    drums: {session._drum_preset} ({len(s._drum_hits)} hits)")


def cmd_chords(session, args):
    chords = session.key.chords
    for i, chord in enumerate(chords):
        from .chords import Chord as ChordClass
        # Build actual chord to get proper Roman numeral analysis
        c = session.key.triad(i)
        analysis = c.analyze(session.key.tonic_name, session.key.mode)
        label = analysis or str(i + 1)
        print(f"  {label:6s}  {chord}")


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


def cmd_fingering(session, args):
    """Show guitar fingering for a chord."""
    if not args:
        print("  usage: fingering Am")
        return
    from .chords import Fretboard
    from .charts import CHARTS
    fb = Fretboard.guitar()
    name = args[0]
    chart = CHARTS.get("western", {})
    if name in chart:
        print(chart[name].tab(fretboard=fb))
    else:
        # Try from_symbol
        try:
            f = fb.chord(name)
            print(f"  {f}")
        except (ValueError, KeyError) as e:
            print(f"  error: {e}")


def cmd_diagram(session, args):
    """Show a scale diagram on guitar."""
    from .chords import Fretboard
    fb = Fretboard.guitar()
    mode = args[0] if args else session.key.mode
    frets = int(args[1]) if len(args) > 1 else 12

    ts = TonedScale(tonic=f"{session.key.tonic_name}4")
    try:
        scale = ts[mode]
        print(fb.scale_diagram(scale, frets=frets))
    except KeyError:
        print(f"  unknown scale: {mode}")


def cmd_system(session, args):
    """Switch musical system or show current."""
    if not args:
        from .systems import SYSTEMS
        for name in SYSTEMS:
            print(f"  {name}")
        return
    system = args[0]
    # Default tonics per system
    default_tonics = {
        "western": "C", "indian": "Sa", "arabic": "Do",
        "japanese": "C", "blues": "C", "gamelan": "C",
    }
    tonic = args[1] if len(args) > 1 else default_tonics.get(system, "C")
    try:
        ts = TonedScale(tonic=f"{tonic}4", system=system)
        available = list(ts.scales)[:10]
        print(f"  system: {system}")
        print(f"  scales: {', '.join(available)}")
        if available:
            first = ts[available[0]]
            print(f"  {available[0]}: {' '.join(first.note_names)}")
    except Exception as e:
        print(f"  error: {e}")


def cmd_interval(session, args):
    """Show the interval between two notes."""
    if len(args) < 2:
        print("  usage: interval C4 G4")
        return
    try:
        t1 = Tone.from_string(args[0], system="western")
        t2 = Tone.from_string(args[1], system="western")
        print(f"  {t1.full_name} → {t2.full_name}: {t1.interval_to(t2)}")
        print(f"  {abs(t1 - t2)} semitones")
    except Exception as e:
        print(f"  error: {e}")


def cmd_identify(session, args):
    """Identify a chord from notes or a symbol."""
    if not args:
        print("  usage: identify C E G   or   identify Cmaj7")
        return
    if len(args) == 1:
        try:
            chord = Chord.from_symbol(args[0])
            print(f"  {chord.identify()}")
            print(f"  symbol: {chord.symbol}")
            print(f"  tones: {' '.join(t.full_name for t in chord.tones)}")
            print(f"  intervals: {chord.intervals}")
            return
        except ValueError:
            pass
    # Try as individual notes
    try:
        tones = [Tone.from_string(f"{n}4", system="western") for n in args]
        chord = Chord(tones=tones)
        name = chord.identify() or "unknown"
        print(f"  {name}")
        if chord.symbol:
            print(f"  symbol: {chord.symbol}")
    except Exception as e:
        print(f"  error: {e}")


def cmd_strum(session, args):
    """Strum a chord on a fretboard-equipped part."""
    if not args:
        print("  usage: strum Am [beats] [down|up] [strum_time]")
        return
    part = _require_part(session)
    chord_name = args[0]
    beats = float(args[1]) if len(args) > 1 else 1.0
    direction = args[2] if len(args) > 2 else "down"
    strum_time = float(args[3]) if len(args) > 3 else 0.05
    try:
        part.strum(chord_name, beats, direction=direction, strum_time=strum_time)
        print(f"  .strum(\"{chord_name}\", {beats}, direction=\"{direction}\", "
              f"strum_time={strum_time})")
    except Exception as e:
        print(f"  error: {e}")


def cmd_roll(session, args):
    """Play a roll (rapid repeated notes with velocity ramp)."""
    if not args:
        print("  usage: roll C3 [beats] [vel_start] [vel_end]")
        return
    part = _require_part(session)
    tone = args[0]
    beats = float(args[1]) if len(args) > 1 else 4.0
    vel_start = int(args[2]) if len(args) > 2 else 40
    vel_end = int(args[3]) if len(args) > 3 else 100
    try:
        part.roll(tone, beats, velocity_start=vel_start, velocity_end=vel_end)
        print(f"  .roll(\"{tone}\", {beats}, velocity_start={vel_start}, "
              f"velocity_end={vel_end})")
    except Exception as e:
        print(f"  error: {e}")


def cmd_bend(session, args):
    """Add a note with pitch bend."""
    if len(args) < 3:
        print("  usage: bend C5 1 2       (note, beats, semitones)")
        print("         bend C5 1 -1      (bend down)")
        return
    part = _require_part(session)
    note = args[0]
    beats = float(args[1])
    bend = float(args[2])
    bend_type = args[3] if len(args) > 3 else "smooth"
    try:
        part.add(note, beats, bend=bend, bend_type=bend_type)
        print(f"  .add(\"{note}\", {beats}, bend={bend}, bend_type=\"{bend_type}\")")
    except Exception as e:
        print(f"  error: {e}")


def cmd_temperament(session, args):
    """Set or show the tuning temperament."""
    if not args:
        temp = getattr(session.score, 'temperament', 'equal')
        ref = getattr(session.score, 'reference_pitch', 440.0)
        print(f"  temperament={temp}  reference={ref} Hz")
        print(f"  available: equal, pythagorean, meantone, just")
        return
    temp = args[0]
    valid = ["equal", "pythagorean", "meantone", "just"]
    if temp not in valid:
        print(f"  unknown temperament: {temp}")
        print(f"  available: {', '.join(valid)}")
        return
    session.score.temperament = temp
    print(f"  temperament={temp}")


def cmd_reference(session, args):
    """Set the reference pitch (A4 frequency)."""
    if not args:
        ref = getattr(session.score, 'reference_pitch', 440.0)
        print(f"  reference={ref} Hz")
        return
    ref = float(args[0])
    session.score.reference_pitch = ref
    print(f"  reference={ref} Hz")


def cmd_instruments(session, args):
    """List all available instruments."""
    cols = 3
    for i in range(0, len(_INSTRUMENT_NAMES), cols):
        row = _INSTRUMENT_NAMES[i:i + cols]
        print("  " + "  ".join(f"{name:<22s}" for name in row))


def cmd_circle(session, args):
    """Show circle of fifths."""
    tonic = args[0] if args else session.key.tonic_name
    tone = Tone.from_string(f"{tonic}4", system="western")
    fifths = [t.name for t in tone.circle_of_fifths()]
    fourths = [t.name for t in tone.circle_of_fourths()]
    print(f"  fifths:  {' → '.join(fifths)}")
    print(f"  fourths: {' → '.join(fourths)}")


def cmd_clear(session, args):
    """Full reset — back to initial state."""
    session.key = Key("C", "major")
    session.bpm = 120
    session.time_sig = "4/4"
    session.swing = 0.0
    session._drum_preset = None
    session.score = Score(session.time_sig, bpm=session.bpm)
    session.parts = {}
    session.current_part = None
    print("  cleared (C major, 120 bpm)")


def cmd_status(session, args):
    parts = ", ".join(session.parts.keys()) if session.parts else "none"
    active = session.current_part.name if session.current_part else "none"
    temp = getattr(session.score, 'temperament', 'equal')
    ref = getattr(session.score, 'reference_pitch', 440.0)
    print(f"  key={session.key}  bpm={session.bpm}  swing={session.swing}")
    print(f"  temperament={temp}  reference={ref} Hz")
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
    "prog": cmd_prog, "progression": cmd_prog,
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
    "fingering": cmd_fingering, "f": cmd_fingering,
    "diagram": cmd_diagram,
    "system": cmd_system,
    "interval": cmd_interval,
    "identify": cmd_identify, "id": cmd_identify,
    "circle": cmd_circle,
    "strum": cmd_strum,
    "roll": cmd_roll,
    "bend": cmd_bend,
    "temperament": cmd_temperament, "temp": cmd_temperament,
    "reference": cmd_reference, "ref": cmd_reference,
    "instruments": cmd_instruments,
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
        if p.reverb_mix > 0:
            fx.append(f"rev={p.reverb_mix}")
        if p.delay_mix > 0:
            fx.append(f"del={p.delay_mix}")
        if p.lowpass > 0:
            fx.append(f"lp={int(p.lowpass)}")
        if p.distortion_mix > 0:
            fx.append(f"dist={p.distortion_mix}")
        if p.legato:
            fx.append("legato")
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


# ── Tab completion ─────────────────────────────────────────────────────────

_SYNTH_NAMES = ["sine", "saw", "triangle", "square", "pulse", "fm",
                "noise", "supersaw", "pwm_slow", "pwm_fast",
                "pedal_steel_synth", "theremin_synth", "kalimba_synth",
                "steel_drum_synth", "accordion_synth", "didgeridoo_synth",
                "bagpipe_synth", "banjo_synth", "mandolin_synth",
                "ukulele_synth", "vocal_synth", "granular_synth",
                "piano_synth", "organ_synth", "harpsichord_synth",
                "strings_synth", "cello_synth", "flute_synth",
                "clarinet_synth", "oboe_synth", "trumpet_synth",
                "acoustic_guitar_synth", "electric_guitar_synth",
                "bass_guitar_synth", "upright_bass_synth", "harp_synth",
                "sitar_synth", "pluck_synth", "saxophone_synth",
                "marimba_synth", "timpani_synth"]
_INSTRUMENT_NAMES = [
    # Keys
    "piano", "electric_piano", "organ", "harpsichord", "celesta", "music_box",
    # Strings
    "violin", "viola", "cello", "contrabass", "string_ensemble",
    # Woodwinds
    "flute", "clarinet", "oboe", "bassoon",
    # Brass
    "trumpet", "trombone", "french_horn", "tuba", "brass_ensemble",
    # Plucked
    "acoustic_guitar", "electric_guitar", "clean_guitar", "crunch_guitar",
    "distorted_guitar", "orange_crunch", "metal_guitar", "bass_guitar",
    "upright_bass", "harp", "sitar", "pedal_steel", "theremin", "kalimba",
    "steel_drum", "accordion", "didgeridoo", "bagpipe", "banjo", "mandolin",
    "mandola", "ukulele", "koto",
    # Synth presets
    "synth_lead", "synth_pad", "synth_bass", "acid_bass",
    "granular_pad", "vocal", "choir", "granular_texture", "808_bass",
    # Mellotron
    "mellotron", "mellotron_strings", "mellotron_flute", "mellotron_choir",
    # Analog
    "sync_lead", "sync_lead_bright", "ring_mod_bell", "ring_mod_metallic",
    "wavefold_warm", "wavefold_gnarly", "drift_saw", "drift_square",
    "analog_pad", "analog_bass",
    # Percussion / Mallet
    "vibraphone", "marimba", "xylophone", "glockenspiel", "tubular_bells", "timpani",
    # Woodwinds (continued)
    "saxophone", "alto_sax", "tenor_sax", "bari_sax",
]
_ENVELOPE_NAMES = ["piano", "pluck", "pad", "organ", "bell", "strings",
                   "staccato", "bowed", "mallet", "none"]
_ARP_PATTERNS = ["up", "down", "updown", "downup", "random"]
_LFO_SHAPES = ["sine", "triangle", "saw", "square"]
_SYSTEMS = ["western", "indian", "arabic", "japanese", "blues", "gamelan"]
_NOTE_NAMES = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb",
               "G", "G#", "Ab", "A", "A#", "Bb", "B"]
_CHORD_SUFFIXES = ["", "m", "7", "m7", "maj7", "dim", "aug", "sus2", "sus4",
                   "m7b5", "dim7", "9", "m9", "maj9"]

# Context-aware completions for the second word
_ARG_COMPLETIONS = {
    "drums": lambda: Pattern.list_presets(),
    "part": lambda: _SYNTH_NAMES + _INSTRUMENT_NAMES,
    "key": lambda: [f"{n}m" for n in _NOTE_NAMES[:12]] + _NOTE_NAMES[:12],
    "arp": lambda: [f"{n}{s}" for n in _NOTE_NAMES[:7] for s in _CHORD_SUFFIXES[:6]],
    "add": lambda: [f"{n}{o}" for n in _NOTE_NAMES[:12] for o in ["3", "4", "5"]],
    "chord": lambda: [f"{n}{s}" for n in _NOTE_NAMES[:7] for s in _CHORD_SUFFIXES[:6]],
    "fingering": lambda: [f"{n}{s}" for n in _NOTE_NAMES[:7] for s in _CHORD_SUFFIXES[:4]],
    "system": lambda: _SYSTEMS,
    "lfo": lambda: ["lowpass", "reverb", "delay", "distortion", "chorus", "volume"],
    "set": lambda: ["lowpass", "reverb", "delay", "distortion", "chorus", "volume",
                    "lowpass_q", "reverb_decay", "delay_time", "delay_feedback",
                    "distortion_drive"],
    "identify": lambda: [f"{n}{s}" for n in _NOTE_NAMES[:7] for s in _CHORD_SUFFIXES[:6]],
    "strum": lambda: [f"{n}{s}" for n in _NOTE_NAMES[:7] for s in _CHORD_SUFFIXES[:6]],
    "roll": lambda: [f"{n}{o}" for n in _NOTE_NAMES[:12] for o in ["2", "3", "4", "5"]],
    "bend": lambda: [f"{n}{o}" for n in _NOTE_NAMES[:12] for o in ["3", "4", "5"]],
    "temperament": lambda: ["equal", "pythagorean", "meantone", "just"],
    "reference": lambda: ["440", "432", "415", "444"],
    "instruments": lambda: _INSTRUMENT_NAMES,
}


def _completer(text, state):
    """Tab completion for the REPL."""
    line = readline.get_line_buffer() if readline else ""
    tokens = line.split()

    if len(tokens) <= 1:
        # First word: complete command names
        options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    else:
        # Second+ word: context-aware
        cmd = tokens[0].lower()
        if cmd in _ARG_COMPLETIONS:
            try:
                candidates = _ARG_COMPLETIONS[cmd]()
                options = [c for c in candidates if c.startswith(text)]
            except Exception:
                options = []
        elif cmd == "part" and len(tokens) == 3:
            # Third arg for part is envelope
            options = [e for e in _ENVELOPE_NAMES if e.startswith(text)]
        elif cmd == "arp" and len(tokens) == 3:
            # Pattern for arp
            options = [p for p in _ARP_PATTERNS if p.startswith(text)]
        elif cmd == "strum" and len(tokens) == 4:
            # Direction for strum
            options = [d for d in ["down", "up"] if d.startswith(text)]
        elif cmd == "bend" and len(tokens) == 5:
            # Bend type
            options = [t for t in ["smooth", "linear", "late"] if t.startswith(text)]
        elif cmd == "lfo" and len(tokens) >= 7:
            # Shape for lfo
            options = [s for s in _LFO_SHAPES if s.startswith(text)]
        else:
            options = []

    if state < len(options):
        return options[state] + " "
    return None


def main():
    session = Session()

    # Set up tab completion
    if readline:
        readline.set_completer(_completer)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims(" ")

    print()
    print("  ♫  PyTheory REPL")
    print("  ════════════════════════════════════════")
    print()
    print("  try:  key Am          — set a key")
    print("        chords          — see its chords")
    print("        prog I V vi IV  — hear a progression")
    print("        drums bossa nova")
    print("        play_score      — hear it all")
    print()
    print("  help for all commands, quit to exit")
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
