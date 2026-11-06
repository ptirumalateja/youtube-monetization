"""v4 voiceover: one tense take + character timestamps. python3 vo4.py outdir"""
import os, sys, json, base64, urllib.request
VOICE = 'tSVwqkJGEKjLklhiN0Nx'
TEXT = ("[tense, hushed] What if you folded a sheet of paper in half... one hundred and three times? "
        "[ominous] Every fold doubles it. "
        "[faster, uneasy] Fourteen folds. Taller than you. Twenty-two. The Eiffel Tower. Twenty-three. Higher than the Burj Khalifa. "
        "[rising panic] Thirty. It's in space. Forty-two. Past the Moon. Fifty-one. Past the Sun. "
        "Sixty-nine. Past the nearest star. Eighty-three. Wider than our galaxy. "
        "[breathless] One hundred and three. Wider than the universe. "
        "[quiet, grim] In real life... the record is twelve.")
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
body = json.dumps({'text': TEXT, 'model_id': 'eleven_v3', 'voice_settings': {'stability': 0.3, 'similarity_boost': 0.8, 'style': 0.6}}).encode()
rq = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128", data=body,
                            headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json'})
r = json.loads(urllib.request.urlopen(rq, timeout=180).read())
open(out + '/take.mp3', 'wb').write(base64.b64decode(r['audio_base64']))
json.dump({'text': TEXT, 'alignment': r.get('alignment')}, open(out + '/align.json', 'w'))
print('ok', list(r.keys()))
