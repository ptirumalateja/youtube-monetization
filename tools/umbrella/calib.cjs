// node calib.cjs "cx=..&cy=.." T1,T2  -> projected key points (fractions of the frame)
const { chromium } = require('playwright'); const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=__dirname; const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json'};
const srv=http.createServer((q,r)=>{const u=q.url.split('?')[0];const f=path.join(root,u==='/'?'index.html':u);fs.readFile(f,(e,d)=>{if(e)r.writeHead(404).end();else{r.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');r.end(d);}})});
(async()=>{await new Promise(r=>srv.listen(0,r));const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();
await p.goto(`http://127.0.0.1:${srv.address().port}/?w=108&h=192&${process.argv[2]||''}`);await p.waitForFunction(()=>window.ready===true);
for(const t of (process.argv[3]||'0.6').split(',').map(Number)) console.log(JSON.stringify(await p.evaluate(t=>window.metaAt(t),t)));
await b.close();srv.close();})();
