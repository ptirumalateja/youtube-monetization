import json,os,base64,urllib.request,sys
TEXT="One second. That's all you've got.\nYour brain saw the car before you did.\nYour legs move. You never decided that.\nYour heart slams into high gear.\nPupils blow wide open.\nYour liver dumps sugar into your blood. Fuel.\nAnd this slow motion? Not real. Your brain just recorded every frame.\nThat's why it felt like forever.\nEver had one?"
for name,vid in [('mark','UgBBYS2sOqTuMpoF3BR0'),('jessica','cgSgspJ2msm6clMCkdW9')]:
  body=json.dumps({"text":TEXT,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.35,"use_speaker_boost":True,"speed":1.1}}).encode()
  r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_192",data=body,headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":"application/json"})
  d=json.load(urllib.request.urlopen(r))
  open(f"{name}_raw11.mp3","wb").write(base64.b64decode(d["audio_base64"]));json.dump(d["alignment"],open(f"{name}_align11.json","w"))
  print(name,"ok")
