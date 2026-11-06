head = open('index.html').read().split("// Paper fold 103")[0]
head = head.replace('<body><script type="module">','<body><script type="module">')
imports = '''
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
const q=new URLSearchParams(location.search); const W=+(q.get('w')||1080), H=+(q.get('h')||1920);
const R=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
R.setSize(W,H); R.setPixelRatio(1); R.toneMapping=THREE.ACESFilmicToneMapping; R.toneMappingExposure=1.0;
R.shadowMap.enabled=true; R.shadowMap.type=THREE.PCFSoftShadowMap; document.body.appendChild(R.domElement);
const TL=new THREE.TextureLoader(); const load=u=>new Promise(r=>TL.load(u,t=>{t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;r(t)}));
const rnd=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(7);
'''
html = head + imports + open('helpers.part.js').read() + open('scenes.part.js').read() + "\n</script></body></html>\n"
open('reel.html','w').write(html)
print(len(html))
