"""Generate the English voiceover, one clip per line (ElevenLabs, Viraj, eleven_v3). python3 vo.py outdir"""
import os, sys, json, urllib.request
VOICE = 'tSVwqkJGEKjLklhiN0Nx'
LINES = [
 ('A', "What if you folded a sheet of paper in half... one hundred and three times?"),
 ('B', "Every fold doubles its thickness."),
 ('C', "Fourteen folds: as tall as you."),
 ('D', "Twenty-two: the Eiffel Tower."),
 ('E', "Twenty-three: the Burj Khalifa."),
 ('F', "Thirty folds: it reaches space."),
 ('G', "Forty-two: the Moon. Fifty-one: the Sun."),
 ('H', "Sixty-nine: the nearest star."),
 ('I', "Eighty-three: our whole galaxy."),
 ('J', "A hundred and three. Taller than the universe is wide."),
 ('K', "In real life... the record is twelve."),
]
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
key = os.environ['ELEVENLABS_API_KEY']
for k, tx in LINES:
    fn = f"{out}/{k}.mp3"
    if os.path.exists(fn): continue
    body = json.dumps({'text': tx, 'model_id': 'eleven_v3', 'voice_settings': {'stability': 0.5, 'similarity_boost': 0.8}}).encode()
    rq = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128", data=body,
                                headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
    with urllib.request.urlopen(rq, timeout=120) as r: open(fn, 'wb').write(r.read())
    print(k, os.path.getsize(fn))
