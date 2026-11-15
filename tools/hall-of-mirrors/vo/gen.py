import json, os, sys, urllib.request
H=os.path.dirname(os.path.abspath(__file__)); L=[l.strip() for l in open(H+"/lines.txt") if l.strip()]
V='UgBBYS2sOqTuMpoF3BR0'; only=set(map(int,sys.argv[1:])) if len(sys.argv)>1 else None
for i,t in enumerate(L,1):
    f=f'{H}/l{i:02d}.mp3'
    if only and i not in only: continue
    if os.path.exists(f) and not only: continue
    body={'text':t,'model_id':'eleven_multilingual_v2','previous_text':L[i-2] if i>1 else None,'next_text':L[i] if i<len(L) else None,
          'voice_settings':{'stability':0.5,'similarity_boost':0.8,'style':0.35,'use_speaker_boost':True,'speed':1.08}}
    r=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{V}?output_format=mp3_44100_192',json.dumps(body).encode(),{'xi-api-key':os.environ['ELEVENLABS_API_KEY'],'Content-Type':'application/json'})
    open(f,'wb').write(urllib.request.urlopen(r).read()); print(i, os.path.getsize(f))
