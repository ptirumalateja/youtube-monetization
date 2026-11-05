import json, os, sys, urllib.request
text = open(os.path.join(os.path.dirname(__file__), 'script.txt')).read()
stab = float(sys.argv[1]); out = sys.argv[2]
body = json.dumps({"text": text, "model_id": "eleven_v3", "voice_settings": {"stability": stab, "similarity_boost": 0.8}}).encode()
req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/Nop7al81LlzhZRWb7j3W?output_format=mp3_44100_192",
    data=body, headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
open(out, 'wb').write(urllib.request.urlopen(req, timeout=300).read())
