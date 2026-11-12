# Foley via the ElevenLabs sound-generation API (needs ELEVENLABS_API_KEY). Skips files that exist.
import os, json, urllib.request
KEY=os.environ['ELEVENLABS_API_KEY']
S={
 'slap':('A loose rubber shoe sole slapping flat on a hard stone floor, one single sharp flap slap, close up, dry',0.6),
 'step':('One soft leather shoe footstep on a stone floor, close up, single step',0.5),
 'room':('Quiet small Indian home in the early morning, faint birds and a distant street vendor far outside, no music',6),
 'rewind':('Fast tape rewind whoosh, reversing, short',0.8),
}
for k,(txt,d) in S.items():
    f=f'sfx/{k}.mp3'
    if os.path.exists(f): continue
    req=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation',data=json.dumps({'text':txt,'duration_seconds':d,'prompt_influence':0.6}).encode(),
        headers={'xi-api-key':KEY,'Content-Type':'application/json'})
    try: open(f,'wb').write(urllib.request.urlopen(req,timeout=120).read()); print('ok',k)
    except Exception as e: print('fail',k,e,getattr(e,'read',lambda:b'')()[:300])
