// Usage: node render.mjs stills <outdir> t1 t2 ...   |   node render.mjs video <out.mp4> [fromFrame toFrame]   |   node render.mjs events <out.json>
// Extra page params via env Q (e.g. Q="pb=300&pu=60").
import {chromium} from 'playwright-core';
import {createServer} from 'node:http'; import {readFile,mkdir,writeFile} from 'node:fs/promises'; import {spawn} from 'node:child_process'; import path from 'node:path'; import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url)); const [mode,outp,...rest]=process.argv.slice(2);
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json'};
const server=createServer(async(req,res)=>{try{const p=decodeURIComponent(new URL(req.url,'http://x').pathname); const f=path.resolve(root,'.'+(p==='/'?'/index.html':p)); const d=await readFile(f); res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream'); res.end(d);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const W=+(process.env.W||1080), H=+(process.env.H||1920), FPS=30;
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-angle=metal','--ignore-gpu-blocklist']});
try{
 const page=await browser.newPage({viewport:{width:W,height:H},deviceScaleFactor:1});
 page.on('pageerror',e=>console.log('[err]',e.message)); page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')console.log('[page]',m.text().slice(0,300));});
 await page.goto(`http://127.0.0.1:${server.address().port}/index.html?w=${W}&h=${H}&${process.env.Q||''}`); await page.waitForFunction(()=>window.ready===true,{timeout:120000});
 if(mode==='events'){ await writeFile(outp,JSON.stringify(await page.evaluate(()=>window.EVENTS),null,1)); }
 else if(mode==='stills'){ await mkdir(outp,{recursive:true}); for(const ts of rest){ const t=+ts, t0=Date.now(); const d=await page.evaluate(([t,o])=>window.renderAt(t,o),[t,{noblur:!!process.env.NOBLUR}]); await writeFile(`${outp}/t${t.toFixed(2).padStart(5,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log(t,((Date.now()-t0)/1000).toFixed(2)+'s'); } }
 else if(mode==='video'){ const a=+(rest[0]||0), b=+(rest[1]||Math.round(22.5*FPS));
  const ff=spawn('ffmpeg',['-y','-hide_banner','-loglevel','warning','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','pipe:0','-c:v','libx264','-preset','slow','-crf','15','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',outp],{stdio:['pipe','inherit','inherit']});
  const done=new Promise((res,rej)=>ff.on('exit',c=>c?rej(Error('ffmpeg '+c)):res()));
  const t0=Date.now(); for(let f=a;f<b;f++){ const d=await page.evaluate(t=>window.renderAt(t),f/FPS); if(!ff.stdin.write(Buffer.from(d.split(',')[1],'base64'))) await new Promise(r=>ff.stdin.once('drain',r)); if(f%30===0) console.log('frame',f,((Date.now()-t0)/1000).toFixed(0)+'s'); }
  ff.stdin.end(); await done; }
}finally{ await browser.close(); server.close(); }
