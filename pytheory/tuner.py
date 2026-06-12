"""Real-time instrument tuner.

Listens to your microphone, tracks pitch with the same YIN algorithm
behind :func:`pytheory.audio.detect_pitch`, and tells you what note
you're playing and how many cents sharp or flat you are.

Terminal::

    $ pytheory tune
    $ pytheory tune --instrument guitar   # lock to the six strings

Browser / JavaScript::

    $ pytheory tune --serve
    # opens http://localhost:8123 — a strobe tuner page

The served page is a strobe tuner: a segmented disc that drifts
clockwise when you're sharp, counter-clockwise when you're flat,
and freezes when you're in tune — the same display logic as a
Peterson strobe, driven by the YIN pitch track.

The server speaks Server-Sent Events *and* WebSocket, so any web
page or JS app can tap the pitch stream directly — no client
library needed::

    // SSE
    const tuner = new EventSource("http://localhost:8123/stream");
    tuner.onmessage = (e) => {
        const { freq, note, octave, cents, in_tune } = JSON.parse(e.data);
    };

    // WebSocket
    const ws = new WebSocket("ws://localhost:8123/ws");
    ws.onmessage = (e) => { const reading = JSON.parse(e.data); };

CORS is wide open on the stream, so a page served from anywhere
(your dev server, a file:// page, CodePen) can connect.

With an instrument preset, readings lock to the nearest string —
the ``target`` field says which one — so "tune the D string" never
gets misread as "you're 80 cents flat of E"::

    tuner = Tuner(instrument="guitar")
"""

import json
import threading
import time

import numpy

from .audio import detect_pitch

SAMPLE_RATE = 44_100

_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
               'F#', 'G', 'G#', 'A', 'A#', 'B']

#: Open-string targets for common instruments (low to high).
INSTRUMENT_STRINGS = {
    "guitar":   ["E2", "A2", "D3", "G3", "B3", "E4"],
    "bass":     ["E1", "A1", "D2", "G2"],
    "ukulele":  ["G4", "C4", "E4", "A4"],
    "violin":   ["G3", "D4", "A4", "E5"],
    "viola":    ["C3", "G3", "D4", "A4"],
    "cello":    ["C2", "G2", "D3", "A3"],
    "mandolin": ["G3", "D4", "A4", "E5"],
    "banjo":    ["D3", "G3", "B3", "D4", "G4"],
}


def _note_to_freq(name, reference_pitch=440.0):
    """Note name with octave ("E2", "C#4") → frequency in Hz."""
    midi = _NOTE_NAMES.index(name[:-1]) + (int(name[-1]) + 1) * 12
    return reference_pitch * 2.0 ** ((midi - 69) / 12.0)


def string_targets(instrument, reference_pitch=440.0):
    """The (name, frequency) tuning targets for an instrument preset.

    >>> string_targets("guitar")[0]
    ('E2', 82.4068...)
    """
    names = INSTRUMENT_STRINGS[instrument]
    return [(n, _note_to_freq(n, reference_pitch)) for n in names]


def analyze_frame(frame, sample_rate=SAMPLE_RATE, *,
                  reference_pitch=440.0, fmin=50.0, fmax=1500.0,
                  targets=None):
    """Analyze one audio frame: what note is this, and how far off?

    Args:
        frame: Mono float array (≥ ~2048 samples for reliable results).
        sample_rate: Sample rate in Hz.
        reference_pitch: Concert pitch for A4 (default 440; pass 442
            for orchestras that tune high, 432 for the adventurous).
        fmin/fmax: Pitch search range.
        targets: Optional list of (name, freq) tuning targets (e.g.
            from :func:`string_targets`). The reading then reports
            cents relative to the *nearest target* instead of the
            nearest chromatic note, with the matched name in
            ``target``.

    Returns:
        Dict with ``freq``, ``note``, ``octave``, ``cents`` (signed,
        + is sharp), and ``in_tune`` (within ±5 cents) — or ``None``
        if the frame has no confident pitch. With targets, also
        ``target`` and ``target_freq``.
    """
    frame = numpy.asarray(frame, dtype=numpy.float64)
    _, freqs, voiced = detect_pitch(frame, sample_rate,
                                    frame_size=min(len(frame), 4096),
                                    hop=len(frame),
                                    fmin=fmin, fmax=fmax)
    if not voiced.any():
        return None
    freq = float(freqs[voiced][0])

    if targets:
        name, target_freq = min(
            targets, key=lambda t: abs(numpy.log2(freq / t[1])))
        cents = 1200.0 * float(numpy.log2(freq / target_freq))
        return {
            "freq": round(freq, 2),
            "note": name[:-1],
            "octave": int(name[-1]),
            "cents": round(cents, 1),
            "in_tune": bool(abs(cents) < 5.0),
            "target": name,
            "target_freq": round(target_freq, 2),
        }

    midi_float = 69 + 12 * float(numpy.log2(freq / reference_pitch))
    nearest = int(round(midi_float))
    cents = (midi_float - nearest) * 100.0
    return {
        "freq": round(freq, 2),
        "note": _NOTE_NAMES[nearest % 12],
        "octave": nearest // 12 - 1,
        "cents": round(cents, 1),
        "in_tune": bool(abs(cents) < 5.0),  # plain bool — JSON-safe
    }


class Tuner:
    """Microphone-driven tuner — keeps the latest pitch reading.

    Example::

        tuner = Tuner()
        tuner.start()
        while True:
            reading = tuner.reading  # dict or None, updated live
    """

    def __init__(self, *, reference_pitch=440.0, fmin=50.0, fmax=1500.0,
                 device=None, sample_rate=SAMPLE_RATE, instrument=None):
        self.reference_pitch = reference_pitch
        self.fmin = fmin
        self.fmax = fmax
        self.device = device
        self.sample_rate = sample_rate
        self.instrument = instrument
        self.targets = None
        if instrument:
            if instrument not in INSTRUMENT_STRINGS:
                raise ValueError(
                    f"Unknown instrument {instrument!r} — choose from: "
                    + ", ".join(sorted(INSTRUMENT_STRINGS)))
            self.targets = string_targets(instrument, reference_pitch)
            # Widen the search range around the strings (bass E1 is
            # 41 Hz, below the chromatic default)
            self.fmin = min(self.fmin, self.targets[0][1] * 0.7)
            self.fmax = min(self.fmax, self.targets[-1][1] * 2.5)
        self.reading = None          # latest analysis dict (or None)
        self._buf = numpy.zeros(4096, dtype=numpy.float64)
        self._lock = threading.Lock()
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        mono = indata[:, 0].astype(numpy.float64)
        with self._lock:
            self._buf = numpy.concatenate([self._buf, mono])[-4096:]

    def start(self):
        """Open the microphone and start analyzing."""
        import sounddevice as sd
        self._stream = sd.InputStream(
            samplerate=self.sample_rate, channels=1,
            blocksize=1024, device=self.device,
            callback=self._callback)
        self._stream.start()
        self._analyzing = True
        t = threading.Thread(target=self._analyze_loop, daemon=True)
        t.start()
        return self

    def _analyze_loop(self):
        while self._analyzing:
            with self._lock:
                frame = self._buf.copy()
            self.reading = analyze_frame(
                frame, self.sample_rate,
                reference_pitch=self.reference_pitch,
                fmin=self.fmin, fmax=self.fmax,
                targets=self.targets)
            time.sleep(1 / 20)

    def stop(self):
        self._analyzing = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None


_TUNER_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>PyTheory Tuner</title>
<style>
  body { background:#111; color:#eee; font-family:-apple-system,system-ui,sans-serif;
         display:flex; flex-direction:column; align-items:center;
         justify-content:center; min-height:100vh; margin:0; }
  #note { font-size:6rem; font-weight:700; line-height:1; }
  #note small { font-size:2.2rem; color:#888; }
  #freq { color:#888; font-size:1.1rem; margin-top:.3rem; }
  #strobe { margin-top:1.2rem; }
  #strings { display:flex; gap:.5rem; margin-top:1rem; }
  #strings span { padding:.3rem .8rem; border-radius:6px; background:#222;
                  color:#888; font-size:1.1rem; border:1px solid #333; }
  #strings span.hot { background:#2a2a2a; color:#eee; border-color:#e74c3c; }
  .ok #strings span.hot { border-color:#2ecc71; color:#2ecc71; }
  #meter { width:min(80vw,440px); height:8px; background:#333;
           border-radius:4px; margin-top:1.4rem; position:relative; }
  #meter::after { content:""; position:absolute; left:50%; top:-5px;
                  width:2px; height:18px; background:#666; }
  #needle { position:absolute; top:-3px; width:6px; height:14px;
            border-radius:3px; background:#e74c3c; left:50%;
            transition:left .08s linear, background .08s; }
  #cents { margin-top:.8rem; font-size:1.2rem; color:#888; }
  .ok #needle { background:#2ecc71; }
  .ok #note { color:#2ecc71; }
</style></head><body>
<div id="note">&mdash;</div>
<div id="freq"></div>
<canvas id="strobe" width="340" height="340"></canvas>
<div id="strings"></div>
<div id="meter"><div id="needle"></div></div>
<div id="cents"></div>
<script>
const CONFIG = __CONFIG__;

// String buttons for instrument presets
const stringsDiv = document.getElementById("strings");
if (CONFIG.strings) {
  for (const s of CONFIG.strings) {
    const el = document.createElement("span");
    el.textContent = s;
    el.id = "str-" + s;
    stringsDiv.appendChild(el);
  }
}

let reading = null;
const es = new EventSource("/stream");
es.onmessage = (e) => {
  const d = JSON.parse(e.data);
  reading = (d && d.note) ? d : null;
  if (!reading) {
    document.getElementById("note").innerHTML = "&mdash;";
    document.getElementById("freq").textContent = "";
    document.getElementById("cents").textContent = "listening\\u2026";
    document.body.classList.remove("ok");
    return;
  }
  document.getElementById("note").innerHTML =
    d.note + "<small>" + d.octave + "</small>";
  document.getElementById("freq").textContent = d.freq.toFixed(1) + " Hz";
  const clamped = Math.max(-50, Math.min(50, d.cents));
  document.getElementById("needle").style.left =
    "calc(" + (50 + clamped) + "% - 3px)";
  document.getElementById("cents").textContent =
    (d.cents > 0 ? "+" : "") + d.cents.toFixed(1) + " cents";
  document.body.classList.toggle("ok", d.in_tune);
  if (CONFIG.strings) {
    for (const s of CONFIG.strings)
      document.getElementById("str-" + s)
        .classList.toggle("hot", d.target === s);
  }
};

// Strobe disc: segment pattern drifts clockwise when sharp,
// counter-clockwise when flat, freezes when in tune. The inner
// ring moves at half rate for fine reading near zero.
const canvas = document.getElementById("strobe");
const ctx = canvas.getContext("2d");
const CX = canvas.width / 2, CY = canvas.height / 2;
const RINGS = [
  { n: 24, r0: 118, r1: 162, mult: 1.0 },
  { n: 12, r0: 68,  r1: 112, mult: 0.5 },
  { n: 6,  r0: 22,  r1: 62,  mult: 0.25 },
];
let angle = 0, lastT = performance.now();
function draw(now) {
  const dt = Math.min((now - lastT) / 1000, 0.1);
  lastT = now;
  const active = reading !== null;
  if (active) angle += reading.cents * dt * 0.06 * 2 * Math.PI;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const inTune = active && reading.in_tune;
  ctx.fillStyle = !active ? "#2a2a2a" : (inTune ? "#2ecc71" : "#e74c3c");
  for (const ring of RINGS) {
    const seg = 2 * Math.PI / ring.n;
    for (let i = 0; i < ring.n; i++) {
      const a0 = angle * ring.mult + i * seg;
      ctx.beginPath();
      ctx.arc(CX, CY, ring.r1, a0, a0 + seg / 2);
      ctx.arc(CX, CY, ring.r0, a0 + seg / 2, a0, true);
      ctx.closePath();
      ctx.fill();
    }
  }
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);
</script></body></html>"""


def _ws_frame(payload):
    """Wrap bytes in a single server-to-client WebSocket text frame."""
    n = len(payload)
    if n < 126:
        header = bytes([0x81, n])
    elif n < 65536:
        header = bytes([0x81, 126]) + n.to_bytes(2, "big")
    else:
        header = bytes([0x81, 127]) + n.to_bytes(8, "big")
    return header + payload


def serve(tuner, port=8123, open_browser=True):
    """Serve the tuner over HTTP: a live strobe page at ``/``, a
    Server-Sent Events pitch stream at ``/stream`` (CORS: any
    origin), and the same stream over WebSocket at ``/ws``.

    Blocks until Ctrl-C.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    config = {
        "instrument": tuner.instrument,
        "strings": ([name for name, _ in tuner.targets]
                    if tuner.targets else None),
        "reference_pitch": tuner.reference_pitch,
    }
    page = _TUNER_PAGE.replace("__CONFIG__", json.dumps(config)).encode()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"   # WebSocket needs 1.1

        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif self.path == "/stream":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.close_connection = True
                try:
                    while True:
                        payload = json.dumps(tuner.reading)
                        self.wfile.write(f"data: {payload}\n\n".encode())
                        self.wfile.flush()
                        time.sleep(1 / 15)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            elif self.path == "/ws":
                self._serve_websocket()
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

        def _serve_websocket(self):
            import base64
            import hashlib
            key = self.headers.get("Sec-WebSocket-Key")
            if not key:
                self.send_response(400)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            accept = base64.b64encode(hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
            ).digest()).decode()
            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept)
            self.end_headers()
            self.close_connection = True
            try:
                while True:
                    payload = json.dumps(tuner.reading).encode()
                    self.wfile.write(_ws_frame(payload))
                    self.wfile.flush()
                    time.sleep(1 / 15)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass

    server = ThreadingHTTPServer(("", port), Handler)
    url = f"http://localhost:{port}"
    print(f"  PyTheory Tuner — {url}")
    if tuner.instrument:
        strings = " ".join(name for name, _ in tuner.targets)
        print(f"  Instrument:      {tuner.instrument} ({strings})")
    print(f"  JS stream:       {url}/stream  (Server-Sent Events)")
    print(f"  WebSocket:       ws://localhost:{port}/ws")
    print("  Ctrl-C to stop.")
    if open_browser:
        import webbrowser
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
    finally:
        server.shutdown()


def run_terminal(tuner):
    """ASCII needle tuner in the terminal. Blocks until Ctrl-C."""
    width = 61
    center = width // 2
    try:
        while True:
            r = tuner.reading
            if r:
                pos = int(numpy.clip(r["cents"], -50, 50) / 50 * center) + center
                bar = ["-"] * width
                bar[center] = "|"
                marker = "\033[92m●\033[0m" if r["in_tune"] else "\033[91m●\033[0m"
                bar[pos] = marker
                label = (f"→ {r['target']}" if "target" in r
                         else f"{r['note']}{r['octave']:<2}")
                line = (f"  {label} "
                        f"{''.join(bar)} {r['cents']:+6.1f}¢ "
                        f"({r['freq']:7.2f} Hz)")
            else:
                line = "  --  " + "-" * width + "  listening…"
            print("\r" + line + " " * 4, end="", flush=True)
            time.sleep(1 / 20)
    except KeyboardInterrupt:
        print("\n  Stopped.")
