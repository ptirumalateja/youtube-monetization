// node shots.js <w> <h> <outdir> <sub> t1 t2 ...   renders frames at the given times in ONE browser session (fast look checks)
const {chromium}=require('playwright'); const fs=require('fs'); const http=require('http'); const path=require('path');
const MIME={'.html':'text/html','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.png':'image/png'};
const srv=http.createServer((rq,rs)=>{ const f=path.join(__dirname,decodeURIComponent(rq.url.split('?')[0]).replace(/^\/+/,'')||'index.html'); fs.readFile(f,(e,d)=>{ if(e){rs.statusCode=404;rs.end();return;} rs.setHeader('Content-Type',MIME[path.extname(f)]||'application/octet-stream'); rs.end(d); }); });
srv.listen(0,async()=>{ const port=srv.address().port; const [W,H,out,sub]=[+process.argv[2],+process.argv[3],process.argv[4],+process.argv[5]]; const ts=process.argv.slice(6).map(Number); fs.mkdirSync(out,{recursive:true});
  const br=await chromium.launch({args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']}); const p=await br.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
  await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:240000});
  for(const t of ts){ const r=await p.evaluate(([t,sub])=>window.renderAnim(t,sub,1/60),[t,sub]); fs.writeFileSync(`${out}/t${t.toFixed(2)}.jpg`,Buffer.from(r.img.split(',')[1],'base64')); console.log('t',t,r.depth.toFixed(0)); }
  await br.close(); srv.close(); });
