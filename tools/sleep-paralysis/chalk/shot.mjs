// Stills: node shot.mjs <outdir> <w> <h> t1 t2 ... [--q "cam=..&look=.."]
import {chromium} from 'playwright-core';import {createServer} from 'node:http';import {readFile,mkdir,writeFile} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'..');
const args=process.argv.slice(2);const qi=args.indexOf('--q');const extra=qi>=0?args.splice(qi,2)[1]:'';const [out,w,h,...ts]=args;await mkdir(out,{recursive:true});
const mime={'.html':'text/html','.js':'text/javascript','.png':'image/png','.json':'application/json'};
const server=createServer(async(req,res)=>{try{const p=decodeURIComponent(new URL(req.url,'http://x').pathname);const f=path.resolve(root,'.'+p);if(!f.startsWith(root)){res.writeHead(403).end();return;}const d=await readFile(f);res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');res.end(d);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-angle=metal','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:+w,height:+h}});const errs=[];page.on('pageerror',e=>errs.push(e.message));page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')console.log('[page]',m.text().slice(0,400));});
await page.goto(`http://127.0.0.1:${server.address().port}/chalk/index.html?${extra}`);
try{await page.waitForFunction(()=>window.ready===true,{timeout:180000});}catch(e){console.log('ERR',errs.join('\n'));process.exit(1);}
for(const t of ts){const t0=Date.now();const d=await page.evaluate(t=>window.renderAt(+t),t);await writeFile(path.join(out,`s_${t}.jpg`),Buffer.from(d.split(',')[1],'base64'));console.log(t,(Date.now()-t0)+'ms');}
console.log(await page.evaluate(()=>window.TLsrc));if(errs.length)console.log('ERRORS',errs.join('\n'));
await browser.close();server.close();
