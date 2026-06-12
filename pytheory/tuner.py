"""Real-time instrument tuner.

Listens to your microphone, tracks pitch with the same YIN algorithm
behind :func:`pytheory.audio.detect_pitch`, and tells you what note
you're playing and how many cents sharp or flat you are.

Terminal::

    $ pytheory tune

Browser / JavaScript::

    $ pytheory tune --serve
    # opens http://localhost:8123 — a live tuner page

The server speaks Server-Sent Events, so any web page or JS app can
tap the pitch stream directly — no client library needed::

    const tuner = new EventSource("http://localhost:8123/stream");
    tuner.onmessage = (e) => {
        const { freq, note, octave, cents, in_tune } = JSON.parse(e.data);
        // update your UI
    };

CORS is wide open on the stream, so a page served from anywhere
(your dev server, a file:// page, CodePen) can connect.
"""

import json
import threading
import time

import numpy

from .audio import detect_pitch

SAMPLE_RATE = 44_100

_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
               'F#', 'G', 'G#', 'A', 'A#', 'B']


def analyze_frame(frame, sample_rate=SAMPLE_RATE, *,
                  reference_pitch=440.0, fmin=50.0, fmax=1500.0):
    """Analyze one audio frame: what note is this, and how far off?

    Args:
        frame: Mono float array (≥ ~2048 samples for reliable results).
        sample_rate: Sample rate in Hz.
        reference_pitch: Concert pitch for A4 (default 440; pass 442
            for orchestras that tune high, 432 for the adventurous).
        fmin/fmax: Pitch search range.

    Returns:
        Dict with ``freq``, ``note``, ``octave``, ``cents`` (signed,
        + is sharp), and ``in_tune`` (within ±5 cents) — or ``None``
        if the frame has no confident pitch.
    """
    frame = numpy.asarray(frame, dtype=numpy.float64)
    _, freqs, voiced = detect_pitch(frame, sample_rate,
                                    frame_size=min(len(frame), 4096),
                                    hop=len(frame),
                                    fmin=fmin, fmax=fmax)
    if not voiced.any():
        return None
    freq = float(freqs[voiced][0])
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
                 device=None, sample_rate=SAMPLE_RATE):
        self.reference_pitch = reference_pitch
        self.fmin = fmin
        self.fmax = fmax
        self.device = device
        self.sample_rate = sample_rate
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
                fmin=self.fmin, fmax=self.fmax)
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
         justify-content:center; height:100vh; margin:0; }
  #note { font-size:9rem; font-weight:700; line-height:1; }
  #note small { font-size:3rem; color:#888; }
  #freq { color:#888; font-size:1.2rem; margin-top:.5rem; }
  #meter { width:min(80vw,540px); height:10px; background:#333;
           border-radius:5px; margin-top:2rem; position:relative; }
  #meter::after { content:""; position:absolute; left:50%; top:-6px;
                  width:2px; height:22px; background:#666; }
  #needle { position:absolute; top:-4px; width:6px; height:18px;
            border-radius:3px; background:#e74c3c; left:50%;
            transition:left .08s linear, background .08s; }
  #cents { margin-top:1rem; font-size:1.4rem; color:#888; }
  .ok #needle { background:#2ecc71; }
  .ok #note { color:#2ecc71; }
</style></head><body>
<div id="note">&mdash;</div>
<div id="freq"></div>
<div id="meter"><div id="needle"></div></div>
<div id="cents"></div>
<script>
const es = new EventSource("/stream");
es.onmessage = (e) => {
  const d = JSON.parse(e.data);
  if (!d || !d.note) {
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
};
</script></body></html>"""


def serve(tuner, port=8123, open_browser=True):
    """Serve the tuner over HTTP: a live page at ``/`` and a
    Server-Sent Events pitch stream at ``/stream`` (CORS: any origin).

    Blocks until Ctrl-C.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == "/":
                body = _TUNER_PAGE.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/stream":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                try:
                    while True:
                        payload = json.dumps(tuner.reading)
                        self.wfile.write(f"data: {payload}\n\n".encode())
                        self.wfile.flush()
                        time.sleep(1 / 15)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.send_response(404)
                self.end_headers()

    server = ThreadingHTTPServer(("", port), Handler)
    url = f"http://localhost:{port}"
    print(f"  PyTheory Tuner — {url}")
    print(f"  JS stream:       {url}/stream  (Server-Sent Events)")
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
                line = (f"  {r['note']}{r['octave']:<2} "
                        f"{''.join(bar)} {r['cents']:+6.1f}¢ "
                        f"({r['freq']:7.2f} Hz)")
            else:
                line = "  --  " + "-" * width + "  listening…"
            print("\r" + line + " " * 4, end="", flush=True)
            time.sleep(1 / 20)
    except KeyboardInterrupt:
        print("\n  Stopped.")
