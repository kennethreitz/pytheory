"""PyTheory Live — interactive MIDI synthesizer with TUI."""

import curses
import random
import sys
import threading
import time
import os

from pytheory.live import LiveEngine
from pytheory.rhythm import INSTRUMENTS, Pattern


NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_name(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


class LiveTUI:
    def __init__(self, seed=None, port="OP-XY"):
        self.seed = seed or random.randint(0, 9999)
        self.port = port
        self.engine = None
        self.log_lines = []
        self.max_log = 500
        self.running = True
        self.instruments = sorted([k for k in INSTRUMENTS.keys()
                                   if k not in ("808_bass",)])
        self.drum_patterns = sorted(Pattern.list_presets())
        self.current_drum = "rock"
        self.picks = []
        self.bpm = "—"
        self.status = "Init"
        self.status_color = 3  # yellow
        self._build_engine()

    def _build_engine(self):
        rng = random.Random(self.seed)
        self.picks = rng.sample(self.instruments, 8)
        self.engine = LiveEngine(buffer_size=128)
        for i, inst in enumerate(self.picks, 1):
            self.engine.channel(i, instrument=inst, reverb=0.3)
        self.engine.drums(self.current_drum, volume=0.5)
        self.engine.cc(0, "lowpass", min_val=300, max_val=8000)

    def log(self, msg, color=0):
        self.log_lines.append((time.time(), msg, color))
        if len(self.log_lines) > self.max_log:
            self.log_lines = self.log_lines[-self.max_log:]

    def _patch_engine_logging(self):
        original_cb = self.engine._midi_callback

        def logging_cb(event, data=None):
            msg, _ = event
            if len(msg) == 0:
                return
            if msg[0] == 0xF8:
                if self.engine._bpm > 10:
                    self.bpm = f"{self.engine._bpm:.0f}"
            elif msg[0] == 0xFA:
                self.log("▶ Start", 5)
                self.status = "Playing"
                self.status_color = 1
            elif msg[0] == 0xFC:
                self.log("■ Stop", 4)
                self.status = "Stopped"
                self.status_color = 4
            elif msg[0] == 0xFB:
                self.log("▶ Continue", 5)
                self.status = "Playing"
                self.status_color = 1
            elif len(msg) >= 3:
                status = msg[0]
                ch = (status & 0x0F) + 1
                msg_type = status & 0xF0
                if msg_type == 0x90 and msg[2] > 0:
                    inst = self.picks[ch - 1] if 1 <= ch <= 8 else "?"
                    self.log(f"♪ {ch}:{inst} {note_name(msg[1])} v={msg[2]}", 1)
                elif msg_type == 0xB0:
                    self.log(f"⚙ CC{msg[1]}={msg[2]}", 3)
                elif msg_type == 0xE0:
                    bend = ((msg[2] << 7) | msg[1]) - 8192
                    self.log(f"↕ Bend ch{ch} {bend:+d}", 3)
            original_cb(event, data)

        self.engine._midi_callback = logging_cb

    def run(self, stdscr):
        curses.curs_set(0)
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_RED)
        stdscr.nodelay(True)
        stdscr.timeout(60)

        self._patch_engine_logging()

        # Pre-render with progress
        self.status = "Rendering"
        self.status_color = 3
        stdscr.erase()
        stdscr.addstr(1, 2, "PyTheory Live", curses.A_BOLD)
        stdscr.addstr(2, 2, "Pre-rendering wavetables...", curses.color_pair(3))
        stdscr.refresh()

        n_samples = 44100 * 3
        count = 0
        for _, channel in self.engine.channels.items():
            if channel.is_drums:
                continue
            for midi_note in range(36, 97):
                channel._get_wave(midi_note, n_samples)
                count += 1
                if count % 50 == 0:
                    stdscr.addstr(3, 2, f"  {count} wavetables...", curses.color_pair(2))
                    stdscr.refresh()

        self.log(f"Cached {count} wavetables", 1)
        self.status = "Listening"
        self.status_color = 2

        # Start engine
        def run_engine():
            devnull = open(os.devnull, 'w')
            old = sys.stdout
            sys.stdout = devnull
            try:
                self.engine.start(port=self.port)
            except Exception as e:
                sys.stdout = old
                self.log(f"Error: {e}", 4)
            finally:
                sys.stdout = old
                devnull.close()

        engine_thread = threading.Thread(target=run_engine, daemon=True)
        engine_thread.start()

        cmd_buf = ""
        cursor_pos = 0
        cmd_history = []
        history_idx = -1
        tab_matches = []
        tab_idx = -1
        tab_prefix = ""

        while self.running:
            try:
                h, w = stdscr.getmaxyx()
                if h < 10 or w < 40:
                    time.sleep(0.1)
                    continue
                stdscr.erase()

                div = max(30, w * 3 // 5)
                cfg_x = div + 2

                # ═══ HEADER BAR ═══
                header = f" PyTheory Live "
                stdscr.addstr(0, 0, header, curses.color_pair(6) | curses.A_BOLD)

                # Status badge
                badge_colors = {1: 7, 2: 6, 3: 8, 4: 9}
                badge_cp = badge_colors.get(self.status_color, 6)
                badge = f" {self.status} "
                x = len(header)
                stdscr.addstr(0, x, badge, curses.color_pair(badge_cp) | curses.A_BOLD)
                x += len(badge)

                info = f"  BPM:{self.bpm}  drums:{self.current_drum}  seed:{self.seed}"
                try:
                    stdscr.addstr(0, x, info[:w - x], curses.color_pair(6))
                    # Fill rest of header
                    remaining = w - x - len(info)
                    if remaining > 0:
                        stdscr.addstr(0, x + len(info), " " * remaining, curses.color_pair(6))
                except curses.error:
                    pass

                # ═══ DIVIDER ═══
                for y in range(1, h - 2):
                    try:
                        stdscr.addch(y, div, '│', curses.color_pair(2) | curses.A_DIM)
                    except curses.error:
                        pass

                # ═══ LEFT: EVENTS ═══
                try:
                    stdscr.addstr(1, 1, " Events ", curses.color_pair(2) | curses.A_BOLD)
                except curses.error:
                    pass

                log_h = h - 5
                visible = self.log_lines[-log_h:] if log_h > 0 else []
                for i, (ts, msg, color) in enumerate(visible):
                    ly = 2 + i
                    if ly >= h - 3:
                        break
                    # Fade old messages
                    age = time.time() - ts
                    attr = curses.A_DIM if age > 8 else 0
                    try:
                        stdscr.addstr(ly, 1, msg[:div - 2],
                                      curses.color_pair(color) | attr)
                    except curses.error:
                        pass

                # ═══ RIGHT: CONFIG ═══
                try:
                    stdscr.addstr(1, cfg_x, " Config ",
                                  curses.color_pair(2) | curses.A_BOLD)
                except curses.error:
                    pass

                y = 3
                rw = w - cfg_x - 1
                for i, inst in enumerate(self.picks, 1):
                    try:
                        stdscr.addstr(y, cfg_x, f"{i}", curses.A_BOLD)
                        stdscr.addstr(y, cfg_x + 1, ":", curses.A_DIM)
                        stdscr.addstr(y, cfg_x + 2, inst[:rw - 2],
                                      curses.color_pair(1))
                    except curses.error:
                        pass
                    y += 1

                y += 1
                pairs = [
                    ("Drums", self.current_drum, 5),
                    ("BPM", str(self.bpm), 0),
                    ("Latency", f"{self.engine.buffer_size / 44100 * 1000:.1f}ms", 0),
                    ("MIDI", self.port, 0),
                    ("Seed", str(self.seed), 2),
                ]
                for label, val, cp in pairs:
                    try:
                        stdscr.addstr(y, cfg_x, f"{label}:", curses.A_BOLD)
                        stdscr.addstr(y, cfg_x + len(label) + 1, f" {val}"[:rw],
                                      curses.color_pair(cp))
                    except curses.error:
                        pass
                    y += 1

                y += 1
                cmds = [
                    "ch <n> [inst]",
                    "fx <n> <param> <val>",
                    "drums [pattern|-]",
                    "seed [n]",
                    "list  patterns",
                    "exit",
                ]
                try:
                    stdscr.addstr(y, cfg_x, "Commands:", curses.color_pair(3))
                except curses.error:
                    pass
                for i, c in enumerate(cmds):
                    try:
                        stdscr.addstr(y + 1 + i, cfg_x + 1, c[:rw],
                                      curses.color_pair(2) | curses.A_DIM)
                    except curses.error:
                        pass

                # ═══ INPUT BAR ═══
                iy = h - 2
                try:
                    stdscr.addstr(iy - 1, 0, "─" * (w - 1), curses.A_DIM)
                    stdscr.addstr(iy, 0, " $ ",
                                  curses.color_pair(1) | curses.A_BOLD)
                    stdscr.addstr(iy, 3, cmd_buf[:w - 5])
                    # Cursor at position
                    cx = 3 + cursor_pos
                    if cx < w - 1:
                        # Show character under cursor inverted, or block at end
                        if cursor_pos < len(cmd_buf):
                            stdscr.addstr(iy, cx, cmd_buf[cursor_pos],
                                          curses.A_REVERSE)
                        else:
                            stdscr.addstr(iy, cx, " ", curses.A_REVERSE)
                except curses.error:
                    pass

                stdscr.refresh()

                # ═══ INPUT ═══
                ch = stdscr.getch()
                if ch == -1:
                    continue
                elif ch == 10 or ch == 13:
                    if cmd_buf.strip():
                        cmd_history.append(cmd_buf)
                        self._handle_command(cmd_buf.strip())
                        cmd_buf = ""
                        cursor_pos = 0
                        history_idx = -1
                elif ch == 27:
                    cmd_buf = ""
                    cursor_pos = 0
                elif ch == curses.KEY_BACKSPACE or ch == 127:
                    if cursor_pos > 0:
                        cmd_buf = cmd_buf[:cursor_pos - 1] + cmd_buf[cursor_pos:]
                        cursor_pos -= 1
                elif ch == curses.KEY_LEFT:
                    cursor_pos = max(0, cursor_pos - 1)
                elif ch == curses.KEY_RIGHT:
                    cursor_pos = min(len(cmd_buf), cursor_pos + 1)
                elif ch == curses.KEY_HOME or ch == 1:  # Ctrl-A
                    cursor_pos = 0
                elif ch == curses.KEY_END or ch == 5:  # Ctrl-E
                    cursor_pos = len(cmd_buf)
                elif ch == curses.KEY_UP:
                    if cmd_history and history_idx < len(cmd_history) - 1:
                        history_idx += 1
                        cmd_buf = cmd_history[-(history_idx + 1)]
                        cursor_pos = len(cmd_buf)
                elif ch == curses.KEY_DOWN:
                    if history_idx > 0:
                        history_idx -= 1
                        cmd_buf = cmd_history[-(history_idx + 1)]
                        cursor_pos = len(cmd_buf)
                    else:
                        history_idx = -1
                        cmd_buf = ""
                        cursor_pos = 0
                elif ch == 9:  # Tab
                    if tab_matches and tab_prefix == cmd_buf:
                        tab_idx = (tab_idx + 1) % len(tab_matches)
                        cmd_buf = tab_matches[tab_idx]
                    else:
                        tab_matches = self._complete(cmd_buf)
                        tab_prefix = cmd_buf
                        if len(tab_matches) == 1:
                            cmd_buf = tab_matches[0]
                            tab_matches = []
                        elif tab_matches:
                            tab_idx = 0
                            cmd_buf = tab_matches[0]
                        else:
                            tab_matches = []
                    cursor_pos = len(cmd_buf)
                elif 32 <= ch < 127:
                    cmd_buf = cmd_buf[:cursor_pos] + chr(ch) + cmd_buf[cursor_pos:]
                    cursor_pos += 1
                    tab_matches = []
                    tab_idx = -1

            except KeyboardInterrupt:
                self.running = False

        self.engine.stop()

    def _complete(self, text):
        """Return list of completions for current input."""
        parts = text.split()
        commands = ["ch", "fx", "drums", "seed", "list", "patterns", "help", "exit"]
        fx_params = ["volume", "lowpass", "reverb", "chorus", "detune", "spread",
                     "analog", "distortion", "delay", "tremolo_depth",
                     "saturation", "phaser", "sub_osc", "noise_mix"]

        if not parts:
            return [c + " " for c in commands]

        # Completing first word
        if len(parts) == 1 and not text.endswith(" "):
            prefix = parts[0].lower()
            return [c + " " for c in commands if c.startswith(prefix)]

        verb = parts[0].lower()

        # ch <n> <instrument>
        if verb == "ch" and len(parts) == 3 and not text.endswith(" "):
            prefix = parts[2].lower()
            return [f"ch {parts[1]} {i} " for i in self.instruments
                    if i.startswith(prefix)]
        if verb == "ch" and len(parts) == 2 and text.endswith(" "):
            return [f"ch {parts[1]} {i} " for i in self.instruments]

        # drums <pattern>
        if verb == "drums" and len(parts) == 2 and not text.endswith(" "):
            prefix = parts[1].lower()
            matches = [p for p in self.drum_patterns if p.startswith(prefix)]
            return [f"drums {m} " for m in matches]
        if verb == "drums" and len(parts) == 1 and text.endswith(" "):
            return [f"drums {p} " for p in self.drum_patterns]

        # fx <n> <param> <val>
        if verb == "fx" and len(parts) == 3 and not text.endswith(" "):
            prefix = parts[2].lower()
            return [f"fx {parts[1]} {p} " for p in fx_params
                    if p.startswith(prefix)]
        if verb == "fx" and len(parts) == 2 and text.endswith(" "):
            return [f"fx {parts[1]} {p} " for p in fx_params]

        return []

    def _handle_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return
        verb = parts[0].lower()

        if verb in ("quit", "q", "exit"):
            self.running = False
        elif verb in ("help", "h"):
            self.log("ch <n> [inst] | fx <n> <param> <val> | drums [pat|-]", 2)
            self.log("seed [n] | list | patterns | exit", 2)
        elif verb == "ch" and len(parts) == 2:
            try:
                n = int(parts[1])
                if 1 <= n <= 8:
                    self.log(f"Ch {n}: {self.picks[n-1]}", 2)
                else:
                    self.log("Channel 1-8", 4)
            except ValueError:
                self.log("ch <1-8> [instrument]", 4)
        elif verb == "ch" and len(parts) >= 3:
            try:
                n = int(parts[1])
                inst = parts[2]
                if inst not in INSTRUMENTS:
                    self.log(f"Unknown: {inst}", 4)
                    return
                if not (1 <= n <= 8):
                    self.log("Channel 1-8", 4)
                    return
                self.picks[n - 1] = inst
                self.engine.channel(n, instrument=inst, reverb=0.3)
                self.log(f"Ch {n} → {inst}", 1)
            except (ValueError, IndexError):
                self.log("ch <1-8> <instrument>", 4)
        elif verb == "fx" and len(parts) >= 4:
            try:
                n = int(parts[1])
                param = parts[2]
                val = float(parts[3])
                if not (1 <= n <= 8):
                    self.log("Channel 1-8", 4)
                    return
                if n not in self.engine.channels:
                    self.log(f"Channel {n} not active", 4)
                    return
                channel = self.engine.channels[n]
                if param == "reverb":
                    channel.reverb = val
                    channel._cache.clear()
                elif param == "lowpass":
                    channel.lowpass = val
                    channel._cache.clear()
                elif param == "volume":
                    channel.volume = val
                elif hasattr(channel, param):
                    setattr(channel, param, val)
                    channel._cache.clear()
                else:
                    self.log(f"Unknown param: {param}", 4)
                    return
                self.log(f"Ch {n} {param}={val}", 1)
            except (ValueError, IndexError):
                self.log("fx <1-8> <param> <value>", 4)
        elif verb == "fx" and len(parts) == 2:
            try:
                n = int(parts[1])
                if n in self.engine.channels:
                    ch = self.engine.channels[n]
                    self.log(f"Ch {n}: vol={ch.volume} lp={ch.lowpass} rev={ch.reverb}", 2)
                else:
                    self.log(f"Channel {n} not active", 4)
            except ValueError:
                self.log("fx <ch> <param> <value>", 4)
        elif verb == "fx" and len(parts) <= 1:
            self.log("Params: volume lowpass reverb", 2)
            self.log("  chorus detune spread analog", 2)
            self.log("  distortion delay tremolo_depth", 2)
            self.log("  saturation phaser sub_osc noise_mix", 2)
            self.log("fx <ch> <param> <value>", 2)
        elif verb == "drums" and len(parts) == 1:
            self.log(f"Current: {self.current_drum}", 5)
            for i in range(0, len(self.drum_patterns), 4):
                row = " ".join(f"{x:17s}" for x in self.drum_patterns[i:i+4])
                self.log(f" {row}", 2)
        elif verb == "drums" and len(parts) >= 2:
            pat = " ".join(parts[1:])
            if pat in ("none", "off", "mute", "-"):
                self.current_drum = "none"
                self.engine._drum_pattern = None
                self.engine._drum_channel = None
                self.log("Drums off", 4)
            else:
                try:
                    self.current_drum = pat
                    self.engine.drums(pat, volume=0.5)
                    self.log(f"Drums → {pat}", 5)
                except Exception as e:
                    self.log(f"Error: {e}", 4)
        elif verb == "seed" and len(parts) == 1:
            self.log(f"Seed: {self.seed}", 2)
        elif verb == "seed" and len(parts) >= 2:
            try:
                self.seed = int(parts[1])
                rng = random.Random(self.seed)
                self.picks = rng.sample(self.instruments, 8)
                for i, inst in enumerate(self.picks, 1):
                    self.engine.channel(i, instrument=inst, reverb=0.3)
                self.log(f"Seed → {self.seed}", 1)
            except ValueError:
                self.log("seed <number>", 4)
        elif verb == "list":
            for i in range(0, len(self.instruments), 3):
                row = " ".join(f"{x:22s}" for x in self.instruments[i:i+3])
                self.log(f" {row}", 2)
        elif verb == "patterns":
            for i in range(0, len(self.drum_patterns), 4):
                row = " ".join(f"{x:17s}" for x in self.drum_patterns[i:i+4])
                self.log(f" {row}", 2)
        else:
            self.log(f"? {cmd}", 4)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    port = sys.argv[2] if len(sys.argv) > 2 else "OP-XY"
    tui = LiveTUI(seed=seed, port=port)
    curses.wrapper(tui.run)


if __name__ == "__main__":
    main()
