import sys, json, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('/tmp/claude-0/kokoro/kokoro-v1.0.onnx', '/tmp/claude-0/kokoro/voices-v1.0.bin')
tl = json.load(open('' + __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'timeline.json') + ''))
V = {0: 'am_fenrir', 1: 'bm_george', 2: 'am_onyx'}
lines = [(f'w{i:02d}', tl['throwers'][i], w.capitalize().replace("can't", "can't") + '!') for i, w in enumerate(tl['words'])]
lines.append(('red', 2, "You'll NEVER make it!"))
lines += [('laugh0', 0, 'Ha! Ha ha!'), ('laugh1', 1, 'Hah! Ha ha ha!'), ('hey', 1, 'Hey! Loser!'), ('look', 0, 'Look at him!')]
for name, who, text in lines:
    s, sr = k.create(text, voice=V[who], speed=1.15, lang='en-us')
    sf.write(f'' + __import__('os').path.dirname(__import__('os').path.abspath(__file__)) + '/{name}.wav', s, sr); print(name, text, round(len(s)/sr, 2))
