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
