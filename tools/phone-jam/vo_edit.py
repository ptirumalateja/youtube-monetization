# vo_edit.py IN_MP3 OUT_WAV : tighten the ElevenLabs read. Phrases are cut at the measured silences,
# rejoined with 0.27 s gaps (0.48 s before "But in 2020"), then sped up 10% (pitch kept).
import sys, subprocess, numpy as np, wave
SR = 48000
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
# phrase spans (s) from silencedetect at -40 dB / 0.12 s on the delivered take
PH = [(0.0, 2.10), (2.48, 3.63), (4.27, 6.31), (6.78, 8.60), (9.16, 10.55), (11.64, 18.05), (18.89, 21.06), (21.45, 23.09), (23.93, len(x) / SR)]
GAP = [0.27, 0.27, 0.27, 0.27, 0.48, 0.27, 0.27, 0.27]
pad = 0.04; out = []
for i, (a, b) in enumerate(PH):
    seg = x[max(0, int((a - pad) * SR)):int((b + pad) * SR)].copy(); f = int(0.01 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    out.append(seg)
    if i < len(GAP): out.append(np.zeros(int(GAP[i] * SR), np.float32))
y = np.concatenate(out)
tmp = sys.argv[2] + '.tmp.wav'
with wave.open(tmp, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-af', 'atempo=1.10', '-ar', str(SR), sys.argv[2]], check=True)
