import json,sys,os,urllib.request,uuid
f=sys.argv[1]; b=uuid.uuid4().hex
data=open(f,'rb').read()
parts=[]
for k,v in [("model_id","scribe_v1"),("language_code","te"),("timestamps_granularity","word")]:
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode()+data+b'\r\n')
parts.append(f'--{b}--\r\n'.encode())
r=urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text",data=b''.join(parts),headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":f"multipart/form-data; boundary={b}"})
d=json.load(urllib.request.urlopen(r,timeout=180))
json.dump(d,open(f+".stt.json","w"),ensure_ascii=False)
print(d["text"])
ws=[w for w in d["words"] if w["type"]=="word"]
prev=0
for w in ws:
    gap=w["start"]-prev
    print(f'{w["start"]:6.2f}-{w["end"]:6.2f} {"GAP%.2f"%gap if gap>0.3 else ""} {w["text"]}')
    prev=w["end"]
