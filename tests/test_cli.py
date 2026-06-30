import pytest
import numpy

import pytheory
from pytheory import Tone, TonedScale, Fretboard, Chord, Key, Note, TET
from pytheory.charts import CHARTS, NamedChord, charts_for_fretboard, QUALITIES
from pytheory.systems import System, SYSTEMS
from pytheory.rhythm import Duration, TimeSignature, Note as RhythmNote, Rest, Score

from _util import (HAS_PORTAUDIO, needs_portaudio, _write_test_wav,
                   _roundtrip_melody, _render_test_mix, _chords_roundtrip,
                   _chord_buffer, _progression_score)


def test_cli_detect(capsys):
    from pytheory.cli import cmd_detect
    import argparse
    args = argparse.Namespace(notes=["C", "E", "G", "A", "D"])
    cmd_detect(args)
    out = capsys.readouterr().out
    assert "C major" in out


def test_cli_detect_no_match(capsys):
    from pytheory.cli import cmd_detect
    import argparse
    args = argparse.Namespace(notes=[])
    cmd_detect(args)
    out = capsys.readouterr().out
    assert "Could not detect" in out


def test_cli_analyze_detects_key_and_labels(capsys):
    from pytheory.cli import cmd_analyze
    import argparse
    args = argparse.Namespace(chords=["C", "D7", "G7", "C"], key=None, mode="major")
    cmd_analyze(args)
    out = capsys.readouterr().out
    assert "C major" in out and "detected" in out
    assert "V7/V" in out                       # the secondary dominant
    assert "secondary dominant" in out
    assert "Cadences:" in out


def test_cli_analyze_explicit_key(capsys):
    from pytheory.cli import cmd_analyze
    import argparse
    args = argparse.Namespace(chords=["Am", "Dm", "E", "Am"], key="A", mode="minor")
    cmd_analyze(args)
    out = capsys.readouterr().out
    assert "A minor" in out and "given" in out
    assert "iv" in out                          # Dm is iv in A minor
    assert "imperfect authentic" in out         # E -> Am


def test_cli_analyze_midi_file(capsys, tmp_path):
    from pytheory.cli import cmd_analyze
    from pytheory.rhythm import Note as RNote, _RawDuration
    import argparse

    # A I-IV-V-I in C as block chords on the default part.
    score = Score("4/4", bpm=120)
    for sym in ("C", "F", "G", "C"):
        score.notes.append(RNote(tone=Chord.from_symbol(sym), duration=_RawDuration(4.0)))
    midi_path = str(tmp_path / "prog.mid")
    score.save_midi(midi_path)

    # Text mode
    cmd_analyze(argparse.Namespace(chords=[midi_path], key=None, mode="major",
                                   json=False, play=False))
    out = capsys.readouterr().out
    assert "C major" in out
    assert "I" in out and "IV" in out and "V" in out

    # JSON mode reads back the chord timeline and key.
    cmd_analyze(argparse.Namespace(chords=[midi_path], key=None, mode="major",
                                   json=True, play=False))
    import json
    data = json.loads(capsys.readouterr().out)
    assert data["key"] == "C major"
    assert [c["roman"] for c in data["chords"]] == ["I", "IV", "V", "I"]
    assert data["chords"][0]["name"] == "C major"


def test_cli_json_output(capsys):
    import argparse, json
    from pytheory.cli import cmd_tone, cmd_scale, cmd_analyze

    cmd_tone(argparse.Namespace(note="C4", temperament="equal", json=True, play=False))
    data = json.loads(capsys.readouterr().out)
    assert data["note"] == "C4" and data["midi"] == 60

    cmd_scale(argparse.Namespace(tonic="C", mode="major", system="western",
                                 json=True, play=False))
    data = json.loads(capsys.readouterr().out)
    assert data["notes"][:3] == ["C", "D", "E"]

    cmd_analyze(argparse.Namespace(chords=["C", "D7", "G7", "C"], key=None,
                                   mode="major", json=True, play=False))
    data = json.loads(capsys.readouterr().out)
    assert data["key"] == "C major"
    assert data["chords"][1]["secondary_dominant"] == "V7/V"
    assert data["cadences"][-1]["type"] == "imperfect authentic"


def test_cli_reharmonize(capsys):
    import argparse, json
    from pytheory.cli import cmd_reharmonize
    args = argparse.Namespace(chords=["G7"], key="C", mode="major",
                              technique="secondary_dominants", json=True, play=False)
    cmd_reharmonize(args)
    data = json.loads(capsys.readouterr().out)
    assert data["chord"] == "G dominant 7th"
    techniques = {s["technique"] for s in data["suggestions"]}
    assert "tritone substitution" in techniques
    assert "negative harmony" in techniques


def test_cli_reharmonize_progression(capsys):
    import argparse, json
    from pytheory.cli import cmd_reharmonize
    args = argparse.Namespace(chords=["C", "Am", "Dm", "G7", "C"], key="C",
                              mode="major", technique="secondary_dominants",
                              json=True, play=False)
    cmd_reharmonize(args)
    data = json.loads(capsys.readouterr().out)
    assert data["original"] == ["C", "Am", "Dm", "G7", "C"]
    assert data["reharmonized"] == ["C", "E7", "Am", "A7", "Dm", "D7", "G7", "C"]


def test_cli_main_no_args(capsys):
    from pytheory.cli import main
    import sys
    old_argv = sys.argv
    sys.argv = ["pytheory"]
    try:
        main()
    except SystemExit:
        pass
    sys.argv = old_argv


def test_cli_main_version(capsys):
    import pytheory
    from pytheory.cli import main
    import sys
    old_argv = sys.argv
    sys.argv = ["pytheory", "--version"]
    try:
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
    finally:
        sys.argv = old_argv
    out = capsys.readouterr().out
    assert pytheory.__version__ in out


def test_cli_identify_cmaj7(capsys):
    from pytheory.cli import cmd_identify
    import argparse
    args = argparse.Namespace(symbol="Cmaj7")
    cmd_identify(args)
    out = capsys.readouterr().out
    assert "C major 7th" in out
    assert "Symbol" in out
    assert "Tones" in out
    assert "Harmony" in out


def test_cli_identify_am(capsys):
    from pytheory.cli import cmd_identify
    import argparse
    args = argparse.Namespace(symbol="Am")
    cmd_identify(args)
    out = capsys.readouterr().out
    assert "A minor" in out


def test_cli_identify_g7(capsys):
    from pytheory.cli import cmd_identify
    import argparse
    args = argparse.Namespace(symbol="G7")
    cmd_identify(args)
    out = capsys.readouterr().out
    assert "G dominant 7th" in out
    assert "Tension" in out
    assert "Dissonance" in out


def test_repl_session_defaults():
    from pytheory.repl import Session
    s = Session()
    assert str(s.key) == "C major"
    assert s.bpm == 120
    assert s.current_part is None
    assert s._drum_preset is None


def test_repl_cmd_add_note():
    from pytheory.repl import Session, cmd_add
    s = Session()
    cmd_add(s, ["C5", "1"])
    assert s.current_part is not None  # auto-created
    assert len(s.current_part.notes) == 1


def test_repl_cmd_arp():
    from pytheory.repl import Session, cmd_part, cmd_arp
    s = Session()
    cmd_part(s, ["lead"])
    cmd_arp(s, ["Am", "updown", "2", "2"])
    assert len(s.current_part.notes) > 0


def test_repl_cmd_prog():
    from pytheory.repl import Session, cmd_key, cmd_prog
    s = Session()
    cmd_key(s, ["Am"])
    cmd_prog(s, ["i", "iv", "V", "i"])
    assert len(s.current_part.notes) == 4


def test_repl_cmd_legato():
    from pytheory.repl import Session, cmd_part, cmd_legato
    s = Session()
    cmd_part(s, ["lead"])
    cmd_legato(s, [])
    assert s.current_part.legato is True
    cmd_legato(s, ["off"])
    assert s.current_part.legato is False


def test_repl_cmd_set():
    from pytheory.repl import Session, cmd_part, cmd_add, cmd_set
    s = Session()
    cmd_part(s, ["lead"])
    cmd_add(s, ["C5", "4"])
    cmd_set(s, ["lowpass", "3000"])
    assert len(s.current_part._automation) == 1


def test_repl_prompt_compact():
    from pytheory.repl import Session, _prompt
    s = Session()
    p = _prompt(s)
    assert "key=C" in p
    assert "bpm=120" in p


def test_repl_prompt_multiline():
    from pytheory.repl import Session, cmd_part, cmd_drums, _prompt, _set_effect
    s = Session()
    cmd_drums(s, ["bossa", "nova"])
    cmd_part(s, ["lead", "saw"])
    _set_effect(s, "reverb", ["0.4"])
    _set_effect(s, "lowpass", ["2000"])
    _set_effect(s, "distortion", ["0.5"])
    p = _prompt(s)
    assert "♫>" in p  # should be multiline


def test_repl_clear():
    from pytheory.repl import Session, cmd_part, cmd_drums, cmd_clear
    s = Session()
    cmd_drums(s, ["rock"])
    cmd_part(s, ["lead"])
    cmd_clear(s, [])
    assert len(s.parts) == 0
    assert s.current_part is None
