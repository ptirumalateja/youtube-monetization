// node render_anim.cjs SHOT OUTDIR FRAMES FPS 'PARAMS_JSON' [START_FRAME]  -> OUTDIR/f%04d.jpg
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname; const [shot, out, NF, FPS, PJ, SF] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const mime = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => { const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } }); });
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const W = Number(process.env.W || 1080), H = Number(process.env.H || 1920), n = Number(NF), fps = Number(FPS), P = JSON.parse(PJ || '{}');
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    let t0 = Date.now(); await page.evaluate(s => window.setupShot(s), shot); console.log('setup', ((Date.now() - t0) / 1000).toFixed(1));
    for (let i = Number(SF || 0); i < n; i++) {
      const f = path.join(out, `f${String(i).padStart(4, '0')}.jpg`); if (fs.existsSync(f)) continue;
      t0 = Date.now(); const b64 = await page.evaluate(([t, u, P]) => window.renderFrame(t, u, P), [i / fps, n > 1 ? i / (n - 1) : 1, P]);
      fs.writeFileSync(f, Buffer.from(b64.split(',')[1], 'base64'));
      if (i % 10 === 0) console.log(shot, i, ((Date.now() - t0) / 1000).toFixed(2) + 's');
    }
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
