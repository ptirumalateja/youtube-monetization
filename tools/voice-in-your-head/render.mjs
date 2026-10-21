// node render.mjs <outDir> frames [fps=30] [worker=0] [workers=1]   -> JPEG frames f00000.jpg...
// node render.mjs <outDir> stills t1 t2 ...                          -> s_<t>.jpg
import {chromium} from 'playwright-core';import {createServer} from 'node:http';import {readFile,mkdir,writeFile} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const DUR=20,root=path.dirname(fileURLToPath(import.meta.url));
const [outDir,mode,...rest]=process.argv.slice(2);await mkdir(outDir,{recursive:true});
const mime={'.html':'text/html','.js':'text/javascript','.ttf':'font/ttf'};
const server=createServer(async(req,res)=>{try{const f=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://x').pathname));if(!f.startsWith(root))return res.writeHead(403).end();res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');res.end(await readFile(f));}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const exe=process.env.CHROME_PATH||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const browser=await chromium.launch({executablePath:exe,headless:true});
const page=await browser.newPage({viewport:{width:1080,height:1920}});const errs=[];page.on('pageerror',e=>errs.push(e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);await page.waitForFunction(()=>window.ready===true,{timeout:60000});
const save=async(t,name)=>{const d=await page.evaluate(t=>window.renderAt(t),t);await writeFile(path.join(outDir,name),Buffer.from(d.split(',')[1],'base64'));};
const t0=Date.now();
if(mode==='stills'){for(const t of rest)await save(+t,`s_${(+t).toFixed(2)}.jpg`);}
else{const fps=+rest[0]||30,wk=+rest[1]||0,nw=+rest[2]||1,N=Math.round(DUR*fps);
 for(let f=wk;f<N;f+=nw){await save(f/fps,`f${String(f).padStart(5,'0')}.jpg`);if(f%60===wk)console.log('w'+wk,'frame',f,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');}}
if(errs.length)console.log('ERRORS',errs.join('\n'));await browser.close();server.close();console.log('done',((Date.now()-t0)/1000).toFixed(1)+'s');
