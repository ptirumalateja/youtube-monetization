// Full render: node render.mjs <framesDir> [fps=30] [from] [to]  -> JPEG frames f00000.jpg...; run several ranges in parallel if you like.
import {mkdir,writeFile} from 'node:fs/promises';import path from 'node:path';import {open} from './page.mjs';import {SPEC} from './timeline.js';
const [out,fpsA,fromA,toA]=process.argv.slice(2);const fps=+fpsA||30,N=Math.round(SPEC.duration*fps),from=+fromA||0,to=toA?+toA:N;await mkdir(out,{recursive:true});
const P=await open(SPEC.width,SPEC.height);const t0=Date.now();
for(let f=from;f<to;f++){await writeFile(path.join(out,`f${String(f).padStart(5,'0')}.jpg`),await P.frame(f/fps));if(f%30===0)console.log('frame',f,'/',to,((Date.now()-t0)/1000).toFixed(0)+'s');}
if(P.errs.length)console.log('ERRORS',P.errs.join('\n'));await P.close();console.log('done');
