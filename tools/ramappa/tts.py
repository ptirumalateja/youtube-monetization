import json,sys,os,base64,urllib.request
text=open(sys.argv[1]).read().strip(); stab=float(sys.argv[2]); out=sys.argv[3]
body=json.dumps({"text":text,"model_id":"eleven_v3","language_code":"te","voice_settings":{"stability":stab,"similarity_boost":0.8,"style":0.6,"use_speaker_boost":True}}).encode()
r=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/zHmC4kzRhtf3P3TV41Kc/with-timestamps?output_format=mp3_44100_192",data=body,headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":"application/json"})
d=json.load(urllib.request.urlopen(r,timeout=180))
open(out+".mp3","wb").write(base64.b64decode(d["audio_base64"]))
json.dump(d.get("alignment"),open(out+".json","w"),ensure_ascii=False)
print("ok",out)
