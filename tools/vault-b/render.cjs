// node render.cjs SHOT[,SHOT...]  -> $OUT/raw-<shot>.png   (env W H, OUT)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output'); fs.mkdirSync(out, { recursive: true });
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } });
});
(async () => {
  const shots = (process.argv[2] || 'gold').split(',');
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const W = Number(process.env.W || 1080), H = Number(process.env.H || 1920);
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    page.on('console', m => console.error('[console]', m.text()));
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    for (const s of shots) {
      const t0 = Date.now();
      const b64 = await page.evaluate(([s, t]) => window.renderShot(s, t), [s, Number(process.env.T || 0)]);
      fs.writeFileSync(path.join(out, `raw-${s}.png`), Buffer.from(b64.split(',')[1], 'base64'));
      console.log('shot', s, ((Date.now() - t0) / 1000).toFixed(1) + 's');
    }
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
