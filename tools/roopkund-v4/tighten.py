#!/usr/bin/env python3
"""Tighten ElevenLabs VO pauses using Scribe word timestamps.
Usage: tighten.py in.wav stt.json out.wav out_words.json"""
import json, sys, wave, numpy as np
src, stt, out, outw = sys.argv[1:5]
w = wave.open(src); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
words = [x for x in json.load(open(stt))['words'] if x['type'] == 'word']
# gap (s) to leave BEFORE the word whose text starts with key; default 0.28
BEAT = {'this': .38, 'Roopkund': .55, 'Hundreds': .32, 'They': .75, 'Their': .55, 'A': .30,
        'And': .45, 'Some': .70, 'From': .50, 'The': .55, 'Hail': .45, 'Who': .75}
DEF, PRE, POST = .28, .05, .10
segs = []; tl = 0.0; newwords = []
# group words into phrases separated by gaps > .3
phr = [[words[0]]]
for x in words[1:]:
    (phr.append([x]) if x['start'] - phr[-1][-1]['end'] > .3 else phr[-1].append(x))
pieces = []
for i, p in enumerate(phr):
    s0 = max(0, p[0]['start'] - PRE); s1 = p[-1]['end'] + POST
    gap = 0 if i == 0 else BEAT.get(p[0]['text'].strip(',.?'), DEF) - PRE - POST
    if i: pieces.append(np.zeros(int(max(gap, 0) * sr), np.float32))
    seg = a[int(s0*sr):int(s1*sr)].copy(); f = int(.012*sr)
    seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    off = sum(len(x) for x in pieces) / sr
    for x in p: newwords.append({'text': x['text'], 'start': round(off + x['start'] - s0, 3), 'end': round(off + x['end'] - s0, 3)})
    pieces.append(seg)
y = np.concatenate(pieces + [np.zeros(int(.4*sr), np.float32)])
o = wave.open(out, 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes())
json.dump(newwords, open(outw, 'w'), indent=0); print(f'{len(a)/sr:.2f}s -> {len(y)/sr:.2f}s')
