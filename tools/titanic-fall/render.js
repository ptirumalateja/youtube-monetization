// node render.js <w> <h> <outdir> <f0> <f1> [port]   renders opening frames f0..f1-1 (30 fps); sub-frames and shutter widen through the snap
const {chromium}=require('playwright'); const fs=require('fs'); const http=require('http'); const path=require('path');
const MIME={'.html':'text/html','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.png':'image/png'};
function serve(){ return new Promise(res=>{ const srv=http.createServer((rq,rs)=>{ const f=path.join(__dirname,decodeURIComponent(rq.url.split('?')[0]).replace(/^\/+/,'')||'index.html'); fs.readFile(f,(e,d)=>{ if(e){rs.statusCode=404;rs.end();return;} rs.setHeader('Content-Type',MIME[path.extname(f)]||'application/octet-stream'); rs.end(d); }); }); srv.listen(0,()=>res(srv)); }); }
(async()=>{const [W,H,out,a,b]=[+process.argv[2],+process.argv[3],process.argv[4],+process.argv[5],+process.argv[6]]; const srv=await serve(); const port=srv.address().port; fs.mkdirSync(out,{recursive:true});
const br=await chromium.launch({args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await br.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:240000});
const meta=[]; for(let f=a;f<b;f++){ const t=f/30; const snap=t>1.9&&t<2.8; const base=+(process.env.SUB||3); const sub=snap?12:(t>=11.7&&t<12.8)?6:(t>=14.2&&t<18.9)?5:(t>=22.0&&t<22.5)?6:base, sh=snap?1/50:1/60; const t0=Date.now(); const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)&&process.env.SKIP){ continue; }
  const r=await p.evaluate(([t,sub,sh])=>window.renderAnim(t,sub,sh),[t,sub,sh]); fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(r.img.split(',')[1],'base64')); meta.push([f,r.depth]);
  fs.writeFileSync(`${out}/meta_${a}.json`,JSON.stringify(meta)); console.log('frame',f,r.depth.toFixed(1),((Date.now()-t0)/1000).toFixed(1)+'s'); }
await br.close(); srv.close();})();
