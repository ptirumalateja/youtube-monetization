import json, os, sys, urllib.request
text = open(os.path.join(os.path.dirname(__file__), 'script.txt')).read()
voice, model, out = sys.argv[1], sys.argv[2], sys.argv[3]
vs = {"stability": 0.42, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": 1.06}
body = json.dumps({"text": text, "model_id": model, "voice_settings": vs}).encode()
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_192",
    data=body, headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
open(out, 'wb').write(urllib.request.urlopen(req, timeout=300).read())
