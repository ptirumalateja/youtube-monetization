import json,os,base64,urllib.request,sys
vid=sys.argv[1]; out=sys.argv[2]; model=sys.argv[3] if len(sys.argv)>3 else 'eleven_multilingual_v2'
text=("Your fingers wrinkle in water. But the water isn't doing it. "
"Your nerves are. "
"Five minutes in, they make the tiny blood vessels in your fingertips narrow. "
"The fingertip loses a little volume, and the skin buckles into ridges. "
"Proof? If that nerve is cut, the finger never wrinkles. "
"So why do it? Scientists think: grip. The ridges drain water away, like tyre treads in the rain. "
"Your body builds rain tyres. All by itself.")
body=json.dumps({"text":text,"model_id":model,"voice_settings":{"stability":0.45,"similarity_boost":0.8,"style":0.35,"use_speaker_boost":True,"speed":1.08}}).encode()
r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_192",data=body,headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":"application/json"})
d=json.load(urllib.request.urlopen(r))
open(out+'.mp3','wb').write(base64.b64decode(d['audio_base64']))
json.dump(d['alignment'],open(out+'.json','w'))
print('ok',d['alignment']['character_end_times_seconds'][-1])
