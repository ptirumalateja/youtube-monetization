// Full render: node render.mjs <framesDir> [fps=60] [from] [to]  -> JPEG frames; encode separately with ffmpeg.
import {chromium} from 'playwright-core';import {createServer} from 'node:http';import {readFile,mkdir,writeFile} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {SPEC} from './timeline.js';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'..');
const [out,fpsA,fromA,toA]=process.argv.slice(2);const fps=+fpsA||60,N=Math.round(SPEC.duration*fps),from=+fromA||0,to=toA?+toA:N;await mkdir(out,{recursive:true});
const mime={'.html':'text/html','.js':'text/javascript','.png':'image/png'};
const server=createServer(async(req,res)=>{try{const p=decodeURIComponent(new URL(req.url,'http://x').pathname);const f=path.resolve(root,'.'+p);if(!f.startsWith(root)){res.writeHead(403).end();return;}const d=await readFile(f);res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');res.end(d);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-angle=metal','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:SPEC.width,height:SPEC.height}});const errs=[];page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/nightmare/index.html?w=${SPEC.width}&h=${SPEC.height}`);await page.waitForFunction(()=>window.ready===true,{timeout:180000});
const t0=Date.now();
for(let f=from;f<to;f++){const d=await page.evaluate(t=>window.renderJpg(t),f/fps);await writeFile(path.join(out,`f${String(f).padStart(5,'0')}.jpg`),Buffer.from(d.split(',')[1],'base64'));if(f%60===0)console.log('frame',f,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');}
if(errs.length)console.log('ERRORS',errs.join('\n'));await browser.close();server.close();console.log('done');
