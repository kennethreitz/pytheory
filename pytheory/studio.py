"""PyTheory Studio — the browser front door.

One command::

    $ pytheory studio

opens a local web app where you can:

- **Drop in any recording** (.wav, .m4a voice memo, .mp3) and watch
  it become sheet music — transcription runs in PyTheory, notation
  renders via abcjs, right on the page.
- **Hear the transcription** played back through PyTheory's synths,
  and download it as MIDI for your DAW.
- **Tune your instrument** — the live tuner streams into the same
  page.

Everything runs locally: the only network access is the abcjs
notation library loaded from a CDN. Your audio never leaves your
machine.
"""

import io
import json
import os
import tempfile
import threading
import time

SAMPLE_RATE = 44_100

_scores = {}          # id -> transcribed Score
_scores_lock = threading.Lock()
_counter = [0]


def _store(score):
    with _scores_lock:
        _counter[0] += 1
        sid = f"s{_counter[0]}-{os.urandom(4).hex()}"
        _scores[sid] = score
    return sid


def _abc_key_for(detected_key):
    """Map a detected Key to an ABC key signature string."""
    if detected_key is None:
        return "C"
    tonic = detected_key.note_names[0]
    return tonic + ("m" if detected_key.mode == "minor" else "")


def _transcribe_upload(body, name, params):
    """Run a transcription on uploaded audio bytes; return response dict."""
    from .rhythm import Score

    suffix = os.path.splitext(name)[1] or ".wav"
    fd, tmp = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(body)
        kwargs = {}
        if params.get("bpm"):
            kwargs["bpm"] = int(params["bpm"])
        if params.get("quantize"):
            kwargs["quantize"] = float(params["quantize"])
        split = params.get("split") in ("1", "true", "on")
        score = Score.from_wav(tmp, split=split, **kwargs)
    finally:
        os.unlink(tmp)

    sid = _store(score)
    title = os.path.splitext(os.path.basename(name))[0] or "Transcription"
    detected = getattr(score, "detected_key", None)
    abc = score.to_abc(title=title, key=_abc_key_for(detected))
    parts = {}
    for pname, part in score.parts.items():
        parts[pname] = sum(1 for n in part.notes if n.tone is not None)
    if score._drum_hits:
        parts["drums"] = len(score._drum_hits)
    return {
        "id": sid,
        "bpm": score.bpm,
        "key": str(detected) if detected else None,
        "parts": parts,
        "abc": abc,
    }


def _render_wav_bytes(score):
    """Render a Score to in-memory WAV bytes."""
    import wave as wavemod

    import numpy

    from .play import render_score

    buf = render_score(score)
    data = (numpy.clip(buf, -1, 1) * 32767).astype(numpy.int16)
    out = io.BytesIO()
    with wavemod.open(out, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(data.tobytes())
    return out.getvalue()


def _midi_bytes(score):
    fd, tmp = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    try:
        score.save_midi(tmp)
        with open(tmp, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp)


_STUDIO_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>PyTheory Studio</title>
<script src="https://cdn.jsdelivr.net/npm/abcjs@6.4.3/dist/abcjs-basic-min.js"></script>
<style>
  :root { color-scheme: dark; }
  body { background:#101014; color:#eee; margin:0;
         font-family:-apple-system,system-ui,sans-serif; }
  header { padding:1.4rem 2rem .4rem; }
  h1 { margin:0; font-size:1.5rem; } h1 small { color:#777; font-weight:400; }
  main { max-width:980px; margin:0 auto; padding:1rem 2rem 4rem; }
  #drop { border:2px dashed #444; border-radius:14px; padding:3rem 1rem;
          text-align:center; color:#999; cursor:pointer; transition:.15s; }
  #drop.hot { border-color:#2ecc71; color:#2ecc71; background:#16201a; }
  .opts { display:flex; gap:1.4rem; align-items:center; margin:.9rem 0 0;
          color:#aaa; font-size:.92rem; flex-wrap:wrap; }
  .opts input[type=number] { width:5em; background:#1c1c22; color:#eee;
          border:1px solid #333; border-radius:6px; padding:.25em .4em; }
  .opts select { background:#1c1c22; color:#eee; border:1px solid #333;
          border-radius:6px; padding:.25em .4em; }
  #status { margin:1rem 0; color:#888; min-height:1.4em; }
  #meta { display:flex; gap:.6rem; flex-wrap:wrap; margin:.6rem 0 1rem; }
  .chip { background:#1d1d25; border:1px solid #333; border-radius:999px;
          padding:.3em .9em; font-size:.9rem; color:#ccc; }
  #sheet { background:#fff; border-radius:12px; padding:1rem; display:none; }
  .actions { margin:1rem 0; display:flex; gap:.8rem; }
  button { background:#26262e; color:#eee; border:1px solid #3a3a44;
           border-radius:8px; padding:.55em 1.2em; font-size:1rem;
           cursor:pointer; } button:hover { background:#32323c; }
  button.primary { background:#2ecc71; border-color:#2ecc71; color:#08130c; }
  #tuner { margin-top:3rem; border-top:1px solid #26262e; padding-top:1.4rem; }
  #tnote { font-size:3rem; font-weight:700; min-height:1.2em; }
  #tmeter { width:min(70vw,480px); height:8px; background:#333;
            border-radius:4px; position:relative; margin:.8rem 0; }
  #tmeter::after { content:""; position:absolute; left:50%; top:-5px;
            width:2px; height:18px; background:#666; }
  #tneedle { position:absolute; top:-3px; width:6px; height:14px;
            border-radius:3px; background:#e74c3c; left:50%;
            transition:left .08s linear; }
  .ok #tneedle { background:#2ecc71; } .ok #tnote { color:#2ecc71; }
</style></head><body>
<header><h1>PyTheory Studio <small>— recordings in, music out</small></h1></header>
<main>
  <div id="drop">Drop a recording here — .wav, .m4a voice memo, .mp3<br>
    <small>or click to choose a file</small></div>
  <input type="file" id="file" accept="audio/*,.m4a,.mp3,.wav" hidden>
  <div class="opts">
    <label><input type="checkbox" id="split"> full mix (split bass / melody / chords / drums)</label>
    <label>quantize <select id="quantize">
      <option value="">as performed</option>
      <option value="0.25" selected>sixteenths</option>
      <option value="0.5">eighths</option></select></label>
    <label>bpm <input type="number" id="bpm" placeholder="auto"></label>
  </div>
  <div id="status"></div>
  <div id="meta"></div>
  <div class="actions" id="actions" style="display:none">
    <button class="primary" id="play">&#9654; Play it back</button>
    <button id="stop" style="display:none">&#9632; Stop</button>
    <a id="midi"><button>Download MIDI</button></a>
  </div>
  <div id="sheet"></div>

  <div id="tuner">
    <h2 style="color:#aaa;font-size:1.05rem">Tuner</h2>
    <button id="tstart">Start tuner</button>
    <div id="tlive" style="display:none">
      <div id="tnote">&mdash;</div>
      <div id="tmeter"><div id="tneedle"></div></div>
      <div id="tcents" style="color:#888"></div>
    </div>
  </div>
</main>
<script>
const drop = document.getElementById("drop");
const fileInput = document.getElementById("file");
const status = document.getElementById("status");
let currentId = null, audio = null;

drop.onclick = () => fileInput.click();
drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("hot"); };
drop.ondragleave = () => drop.classList.remove("hot");
drop.ondrop = (e) => {
  e.preventDefault(); drop.classList.remove("hot");
  if (e.dataTransfer.files.length) upload(e.dataTransfer.files[0]);
};
fileInput.onchange = () => { if (fileInput.files.length) upload(fileInput.files[0]); };

async function upload(file) {
  status.textContent = "Transcribing " + file.name + "\\u2026";
  document.getElementById("sheet").style.display = "none";
  document.getElementById("actions").style.display = "none";
  document.getElementById("meta").innerHTML = "";
  const params = new URLSearchParams({ name: file.name });
  if (document.getElementById("split").checked) params.set("split", "1");
  const q = document.getElementById("quantize").value;
  if (q) params.set("quantize", q);
  const bpm = document.getElementById("bpm").value;
  if (bpm) params.set("bpm", bpm);
  try {
    const res = await fetch("/transcribe?" + params, {
      method: "POST", body: await file.arrayBuffer() });
    if (!res.ok) throw new Error(await res.text());
    const d = await res.json();
    currentId = d.id;
    status.textContent = "";
    const meta = document.getElementById("meta");
    const chips = [d.bpm + " BPM"];
    if (d.key) chips.push(d.key);
    for (const [p, n] of Object.entries(d.parts))
      chips.push(p + ": " + n + (p === "drums" ? " hits" : " notes"));
    meta.innerHTML = chips.map(c => "<span class='chip'>" + c + "</span>").join("");
    const sheet = document.getElementById("sheet");
    sheet.style.display = "block";
    ABCJS.renderAbc("sheet", d.abc, { responsive: "resize" });
    document.getElementById("actions").style.display = "flex";
    document.getElementById("midi").href = "/midi?id=" + d.id;
    document.getElementById("midi").download =
      file.name.replace(/\\.[^.]+$/, "") + ".mid";
  } catch (err) {
    status.textContent = "Transcription failed: " + err.message;
  }
}

document.getElementById("play").onclick = async () => {
  if (!currentId) return;
  status.textContent = "Rendering\\u2026";
  const res = await fetch("/render?id=" + currentId);
  const blob = await res.blob();
  status.textContent = "";
  if (audio) audio.pause();
  audio = new Audio(URL.createObjectURL(blob));
  audio.play();
  document.getElementById("stop").style.display = "";
  audio.onended = () => document.getElementById("stop").style.display = "none";
};
document.getElementById("stop").onclick = () => {
  if (audio) audio.pause();
  document.getElementById("stop").style.display = "none";
};

document.getElementById("tstart").onclick = () => {
  document.getElementById("tstart").style.display = "none";
  document.getElementById("tlive").style.display = "block";
  const es = new EventSource("/stream");
  es.onmessage = (e) => {
    const d = JSON.parse(e.data);
    const tuner = document.getElementById("tuner");
    if (d && d.error) {
      document.getElementById("tcents").textContent = d.error; return;
    }
    if (!d || !d.note) {
      document.getElementById("tnote").innerHTML = "&mdash;";
      document.getElementById("tcents").textContent = "listening\\u2026";
      tuner.classList.remove("ok"); return;
    }
    document.getElementById("tnote").textContent = d.note + d.octave;
    const c = Math.max(-50, Math.min(50, d.cents));
    document.getElementById("tneedle").style.left = "calc(" + (50 + c) + "% - 3px)";
    document.getElementById("tcents").textContent =
      (d.cents > 0 ? "+" : "") + d.cents.toFixed(1) + " cents \\u00b7 " +
      d.freq.toFixed(1) + " Hz";
    tuner.classList.toggle("ok", d.in_tune);
  };
};
</script></body></html>"""


def serve(port=8124, open_browser=True, host="127.0.0.1"):
    """Run the Studio server. Blocks until Ctrl-C."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, urlparse

    tuner_holder = {}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def _send(self, code, body, ctype="application/json"):
            if isinstance(body, str):
                body = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            url = urlparse(self.path)
            if url.path != "/transcribe":
                return self._send(404, "not found", "text/plain")
            params = {k: v[0] for k, v in parse_qs(url.query).items()}
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                result = _transcribe_upload(
                    body, params.get("name", "upload.wav"), params)
                self._send(200, json.dumps(result))
            except Exception as e:
                self._send(400, str(e), "text/plain")

        def do_GET(self):
            url = urlparse(self.path)
            params = {k: v[0] for k, v in parse_qs(url.query).items()}
            if url.path == "/":
                return self._send(200, _STUDIO_PAGE,
                                  "text/html; charset=utf-8")
            if url.path in ("/render", "/midi"):
                score = _scores.get(params.get("id", ""))
                if score is None:
                    return self._send(404, "unknown id", "text/plain")
                if url.path == "/render":
                    return self._send(200, _render_wav_bytes(score),
                                      "audio/wav")
                return self._send(200, _midi_bytes(score), "audio/midi")
            if url.path == "/stream":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                if "tuner" not in tuner_holder:
                    try:
                        from .tuner import Tuner
                        tuner_holder["tuner"] = Tuner().start()
                    except Exception as e:
                        tuner_holder["tuner"] = None
                        tuner_holder["error"] = str(e)
                try:
                    while True:
                        t = tuner_holder.get("tuner")
                        if t is None:
                            payload = json.dumps(
                                {"error": tuner_holder.get("error",
                                                           "no microphone")})
                        else:
                            payload = json.dumps(t.reading)
                        self.wfile.write(f"data: {payload}\n\n".encode())
                        self.wfile.flush()
                        time.sleep(1 / 15)
                except (BrokenPipeError, ConnectionResetError):
                    return
            else:
                self._send(404, "not found", "text/plain")

    server = ThreadingHTTPServer((host, port), Handler)
    display_host = "localhost" if host in ("127.0.0.1", "::1") else host
    url = f"http://{display_host}:{port}"
    print(f"  PyTheory Studio — {url}")
    print("  Drop in a recording; get sheet music, playback, and MIDI.")
    print("  Ctrl-C to stop.")
    if open_browser:
        import webbrowser
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
    finally:
        t = tuner_holder.get("tuner")
        if t:
            t.stop()
        server.shutdown()
