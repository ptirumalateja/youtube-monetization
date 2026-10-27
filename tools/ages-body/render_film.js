// node render_film.js outdir start end [step]   renders frames start..end-1 (24 fps) as outdir/f000000.jpg; server on :8777 in this folder
const {chromium} = require('playwright-core'); const fs = require('fs');
(async () => {
  const [out, a, b, step = 1] = process.argv.slice(2); fs.mkdirSync(out, {recursive: true});
  const br = await chromium.launch({executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
  const p = await br.newPage({viewport: {width: 1920, height: 1080}});
  p.on('pageerror', e => console.log('[err]', e.message.slice(0, 300)));
  await p.goto('http://localhost:8777/film.html?w=1920&h=1080');
  await p.waitForFunction('window.ready===true', {timeout: 180000});
  const fps = 24; let n = 0; const t0 = Date.now();
  for (let f = +a; f < +b; f += +step) {
    const fn = `${out}/f${String(f).padStart(6, '0')}.jpg`; if (fs.existsSync(fn)) continue;
    const d = await p.evaluate(t => window.renderAt(t), f / fps);
    fs.writeFileSync(fn, Buffer.from(d.split(',')[1], 'base64')); if (++n % 50 === 0) console.log(f, ((Date.now() - t0) / n / 1000).toFixed(2) + 's/frame');
  }
  await br.close();
})();
