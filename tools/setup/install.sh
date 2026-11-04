#!/usr/bin/env bash
# Reinstall the video/audio toolkit in a fresh cloud session (or on a Mac).
# Usage: bash tools/setup/install.sh          (everything; Teja approved earshot + sound on 4 Nov 2026)
#        bash tools/setup/install.sh core     (skip earshot + sfx skill)
set -e
MODELS=${MODELS:-/opt/models}
GH=${GH:-/opt/gh}
mkdir -p "$MODELS/whisper" "$GH"

echo "== hyperframes (heygen-com/hyperframes, HTML -> video)"
npm i -g hyperframes@0.9.10
# jsdelivr is blocked in the cloud: projects must load gsap locally.
# Copy it next to index.html with: bash tools/setup/hf-gsap.sh <project-dir>

echo "== yt-dlp + faster-whisper"
pip install -q -U "yt-dlp[default]" faster-whisper   # [default] adds yt-dlp-ejs, the YouTube JS challenge solver (run with --js-runtimes node)

echo "== whisper base.en model (GitHub mirror: jianchang512/stt; HF is blocked)"
if [ ! -s "$MODELS/whisper/base.en/model.bin" ]; then
  pip install -q py7zr
  tmp=$(mktemp -d)
  curl -sSLf -o "$tmp/m.7z" https://github.com/jianchang512/stt/releases/download/0.0/faster-base.en.7z
  python3 -I -c "import py7zr,sys;py7zr.SevenZipFile(sys.argv[1]).extractall(sys.argv[2])" "$tmp/m.7z" "$tmp/x"
  # the archive's HF-cache symlinks come out empty, so rebuild the folder from the blobs
  b=$(echo "$tmp"/x/models--*/blobs); d="$MODELS/whisper/base.en"; mkdir -p "$d"
  for f in "$b"/*; do
    h=$(head -c 40 "$f")
    case "$h" in
      *WhisperSpec*|*decoder*) cp "$f" "$d/model.bin";;
      *alignment_heads*) cp "$f" "$d/config.json";;
      *'"version"'*) cp "$f" "$d/tokenizer.json";;
      *) cp "$f" "$d/vocabulary.txt";;
    esac
  done
  rm -rf "$tmp"
fi

if [ "$1" != "core" ]; then
  echo "== earshot (Leonxlnx/earshot: hear/measure/make SFX; describe/match fetch CLAP models from HF on first use)"
  # CPU wheel avoids the huge CUDA one; download.pytorch.org is blocked in the cloud, so fall back to PyPI there
  python3 -c "import torch" 2>/dev/null || pip install -q torch --index-url https://download.pytorch.org/whl/cpu || pip install -q torch
  pip install -q "git+https://github.com/Leonxlnx/earshot.git"
  echo "== real SFX skill (vibe-motion/sound: Freesound search+download)"
  [ -d "$GH/sound" ] || git clone --depth 1 https://github.com/vibe-motion/sound.git "$GH/sound"
fi

echo "== check"
hyperframes --version; yt-dlp --version
python3 -c "import faster_whisper; print('faster-whisper', faster_whisper.__version__)"
command -v earshot >/dev/null && earshot --help | head -1 || true
