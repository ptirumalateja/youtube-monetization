# Foley + a short piano cue via the ElevenLabs API (needs ELEVENLABS_API_KEY). Skips files that exist.
import os, json, urllib.request
KEY=os.environ['ELEVENLABS_API_KEY']
S={
 'room':('Quiet apartment living room during the day, faint birds outside a closed window, very soft distant traffic, no music',13),
 'door_close':('Front door of an apartment closing firmly with a latch click, then silence',1.4),
 'sigh':('A dog lying down on a wooden floor and letting out a long soft sad sigh through its nose',1.8),
 'ticks':('Wall clock ticking quickly, time passing fast, clean mechanical ticks',3.0),
 'swish':('Short soft paper swish transition, quick',0.5),
 'jingle':('Keys jingling outside a front door, then a key going into the lock',1.4),
 'whine':('A dog giving one short excited whimper, ears up',0.9),
 'door_open':('Front door unlocking and swinging open, warm, wooden',1.2),
 'barks':('Happy excited dog greeting its owner, two quick joyful barks then whimpers and tail thumping',2.0),
 'laugh':('A man laughing warmly and softly, surprised and happy, no words',1.4),
 'nuzzle':('Dog happily panting and sniffing close up, collar tags jingling softly, a man chuckling quietly',3.5),
}
for k,(txt,d) in S.items():
    f=f'sfx/{k}.mp3'
    if os.path.exists(f): continue
    req=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation',data=json.dumps({'text':txt,'duration_seconds':d,'prompt_influence':0.55}).encode(),
        headers={'xi-api-key':KEY,'Content-Type':'application/json'})
    try: open(f,'wb').write(urllib.request.urlopen(req,timeout=120).read()); print('ok',k)
    except Exception as e: print('fail',k,e,getattr(e,'read',lambda:b'')()[:300])
f='sfx/piano.mp3'
if not os.path.exists(f):
    req=urllib.request.Request('https://api.elevenlabs.io/v1/music',data=json.dumps({'prompt':'Tender solo felt piano, warm and emotional, a simple hopeful melody of single notes, slow, intimate, no drums, no strings, instrumental','music_length_ms':10000}).encode(),
        headers={'xi-api-key':KEY,'Content-Type':'application/json'})
    try: open(f,'wb').write(urllib.request.urlopen(req,timeout=240).read()); print('ok piano')
    except Exception as e: print('fail piano',e,getattr(e,'read',lambda:b'')()[:300])
