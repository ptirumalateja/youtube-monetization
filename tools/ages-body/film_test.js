// node film_test.js outdir W H t1 t2 ...   (server on :8777 in this folder)
const {chromium} = require('playwright-core'); const fs = require('fs');
(async () => {
  const [out, W, H, ...ts] = process.argv.slice(2); fs.mkdirSync(out, {recursive: true});
  const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
  const p = await b.newPage({viewport: {width: +W, height: +H}});
  p.on('console', m => { if (m.type()==='error'||m.type()==='warning') console.log('[page]', m.text().slice(0,300)); });
  p.on('pageerror', e => console.log('[err]', e.message.slice(0,400)));
  await p.goto(`http://localhost:8777/film.html?w=${W}&h=${H}`);
  await p.waitForFunction('window.ready===true', {timeout: 180000});
  for (const t of ts) { const t0=Date.now(); const d = await p.evaluate(t => window.renderAt(t), +t);
    fs.writeFileSync(`${out}/t${String(t).padStart(6,'0')}.jpg`, Buffer.from(d.split(',')[1],'base64')); console.log(t, ((Date.now()-t0)/1000).toFixed(1)+'s'); }
  await b.close();
})();
