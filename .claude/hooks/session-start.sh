#!/bin/bash
# SessionStart hook: install system + Python deps so the audio test suite
# runs in Claude Code on the web. pytheory depends on `sounddevice`, whose
# Linux wheels don't bundle PortAudio — without libportaudio2 the package
# fails to import and ~every test errors with "PortAudio library not found".
set -euo pipefail

# Only needed in the remote (web) environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# System library for sounddevice (mirrors the CI workflow's install step).
if ! ldconfig -p 2>/dev/null | grep -q 'libportaudio\.so\.2'; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq libportaudio2
fi

# Python dependencies (cached after first run; `sync` is incremental).
cd "$CLAUDE_PROJECT_DIR"
uv sync
