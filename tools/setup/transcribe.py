#!/usr/bin/env python3
"""Word-timed transcript with faster-whisper. Usage: transcribe.py AUDIO [--json out.json] [--model DIR]"""
import argparse, json, subprocess, numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("--json"); ap.add_argument("--model", default="/opt/models/whisper/base.en")
a = ap.parse_args()
# decode with ffmpeg (the bundled PyAV can be version-mismatched)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
segs, _ = WhisperModel(a.model, device="cpu", compute_type="int8").transcribe(pcm, word_timestamps=True)
out = []
for s in segs:
    print(f"{s.start:6.2f} {s.end:6.2f} {s.text.strip()}")
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "start": w.start, "end": w.end} for w in s.words]})
if a.json:
    json.dump(out, open(a.json, "w"), indent=1)
