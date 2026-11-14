import json,sys,os,base64,urllib.request
text=open(sys.argv[1]).read().strip(); model=sys.argv[2]; out=sys.argv[3]; vs=json.loads(sys.argv[4])
body=json.dumps({"text":text,"model_id":model,"language_code":"te","voice_settings":vs}).encode()
r=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/zHmC4kzRhtf3P3TV41Kc/with-timestamps?output_format=mp3_44100_192",data=body,headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":"application/json"})
try:
    d=json.load(urllib.request.urlopen(r,timeout=240))
except urllib.error.HTTPError as e: print(e.code,e.read()[:400]); sys.exit(1)
open(out+".mp3","wb").write(base64.b64decode(d["audio_base64"])); print("ok",out)
