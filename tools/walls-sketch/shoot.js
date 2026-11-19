// node shoot.js <outdir> <t0> <t1> [step]  -> writes jpg/png frames via playwright
const { chromium } = require('playwright');
const fs = require('fs'); const http = require('http'); const path = require('path');
const [,, outdir, a, b, step, fmt] = process.argv;
const root = __dirname;
const types = { '.js': 'text/javascript', '.html': 'text/html', '.ttf': 'font/ttf' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(p, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); });
srv.listen(0, async () => {
  const port = srv.address().port;
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await br.newPage();
  pg.on('console', m => console.log('PAGE', m.text())); pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto(`http://localhost:${port}/index.html`); await pg.waitForFunction('window.ready', null, { timeout: 60000 });
  fs.mkdirSync(outdir, { recursive: true });
  const t0 = +a, t1 = +b, st = +(step || 1 / 30); const ext = fmt || 'jpg';
  let i = 0;
  for (let t = t0; t <= t1 + 1e-6; t += st, i++) {
    const data = await pg.evaluate(([t, ext]) => R.render(t).toDataURL(ext === 'png' ? 'image/png' : 'image/jpeg', .95), [t, ext]);
    fs.writeFileSync(path.join(outdir, `f${String(i).padStart(4, '0')}.${ext}`), Buffer.from(data.split(',')[1], 'base64'));
    if (i % 30 === 0) console.log('t', t.toFixed(2));
  }
  await br.close(); srv.close();
});
