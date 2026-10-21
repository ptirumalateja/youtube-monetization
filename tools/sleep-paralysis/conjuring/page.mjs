// Shared headless page for stills and the full render. CHROME_PATH and GL_ARGS pick the browser and GL backend
// (macOS default: Chrome + Metal; in the cloud: GL_ARGS="--use-angle=swiftshader --enable-unsafe-swiftshader").
import {chromium} from 'playwright-core';import {createServer} from 'node:http';import {readFile} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const mime={'.html':'text/html','.js':'text/javascript','.png':'image/png','.json':'application/json','.woff2':'font/woff2'};
export async function open(w,h,extra=''){
 const server=createServer(async(req,res)=>{try{const p=decodeURIComponent(new URL(req.url,'http://x').pathname);const f=path.resolve(root,'.'+p);if(!f.startsWith(root)){res.writeHead(403).end();return;}const d=await readFile(f);res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');res.end(d);}catch{res.writeHead(404).end();}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:[...(process.env.GL_ARGS||'--use-angle=metal').split(' '),'--ignore-gpu-blocklist']});
 const page=await browser.newPage({viewport:{width:+w,height:+h}});const errs=[];page.on('pageerror',e=>errs.push(e.message));page.on('console',m=>{if(m.type()==='error')console.log('[page]',m.text().slice(0,300));});
 await page.goto(`http://127.0.0.1:${server.address().port}/conjuring/index.html?w=${w}&h=${h}&${extra}`);
 try{await page.waitForFunction(()=>window.ready===true,{timeout:300000});}catch(e){console.log('ERR',errs.join('\n'));process.exit(1);}
 return {page,errs,close:async()=>{await browser.close();server.close();},frame:async t=>Buffer.from((await page.evaluate(t=>window.renderJpg(t),t)).split(',')[1],'base64')};
}
