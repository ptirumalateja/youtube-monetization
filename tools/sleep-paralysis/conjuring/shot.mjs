// Stills: node shot.mjs <outdir> <w> <h> t1 t2 ...
import {mkdir,writeFile} from 'node:fs/promises';import path from 'node:path';import {open} from './page.mjs';
const [out,w,h,...ts]=process.argv.slice(2);await mkdir(out,{recursive:true});const P=await open(w,h);
console.log('cuts',JSON.stringify(await P.page.evaluate(()=>window.cuts)));
for(const t of ts){const t0=Date.now();await writeFile(path.join(out,`s_${t}.jpg`),await P.frame(+t));console.log(t,(Date.now()-t0)+'ms');}
console.log(JSON.stringify(await P.page.evaluate(()=>window.diag())));if(P.errs.length)console.log('ERRORS',P.errs.join('\n'));await P.close();
