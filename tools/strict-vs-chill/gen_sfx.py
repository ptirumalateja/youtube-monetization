# Generate the reel's foley with the ElevenLabs sound-generation API (needs ELEVENLABS_API_KEY). Skips files that exist.
import os, json, urllib.request, sys
KEY=os.environ['ELEVENLABS_API_KEY']
S={
 'room':('Quiet bedroom at night, soft distant city hum, faint crickets outside an open window, no music',11),
 'door_open':('Wooden bedroom door handle click and door swinging open with a soft creak',1.6),
 'door_close':('Wooden bedroom door closing gently with a latch click',1.2),
 'steps':('Four soft socked footsteps on a wooden floor, indoor',1.8),
 'sash':('Old wooden sash window being slid up, wood rubbing',1.2),
 'climb':('Person climbing through a window, fabric rustle and soft thump on a mattress',1.4),
 'lamp':('Bedside lamp switch click',0.5),
 'tick':('Single soft digital alarm clock beep, short',0.5),
 'rewind':('VHS tape rewinding fast, mechanical whirr and warble, short',0.7),
 'hit':('Single deep cinematic low boom hit with short tail, dramatic reveal, no music',1.5),
 'bed':('Two people sitting down on a bed, mattress creak',1.0),
}
for k,(txt,d) in S.items():
    f=f'sfx/{k}.mp3'
    if os.path.exists(f): continue
    req=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation',data=json.dumps({'text':txt,'duration_seconds':d,'prompt_influence':0.5}).encode(),
        headers={'xi-api-key':KEY,'Content-Type':'application/json'})
    try:
        open(f,'wb').write(urllib.request.urlopen(req,timeout=120).read()); print('ok',k)
    except Exception as e: print('fail',k,e, getattr(e,'read',lambda:b'')()[:300])
