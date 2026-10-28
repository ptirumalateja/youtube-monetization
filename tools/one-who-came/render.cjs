// Look stills for the Simpsons "one is fake" reel.  SHOTS=room,tiger node render.cjs  -> $OUT/<shot>.jpg   (env W,H,SUB,OUT,T)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output'); fs.mkdirSync(out, { recursive: true });
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => { const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } }); });
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try { const W = +process.env.W || 1080, H = +process.env.H || 1920, SUB = +process.env.SUB || 1, T = +process.env.T || 2;
    for (const shot of (process.env.SHOTS || 'room').split(',')) { const t0 = Date.now();
      const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
      page.on('pageerror', e => { console.error('[pageerror]', shot, e.message); process.exit(1); }); page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
      await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}&shot=${shot}`);
      await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
      const b64 = await page.evaluate(([t, k]) => window.renderAt(t, k), [T, SUB]);
      fs.writeFileSync(path.join(out, `${shot}.jpg`), Buffer.from(b64.split(',')[1], 'base64')); await page.close();
      console.log(shot, Date.now() - t0, 'ms'); }
  } finally { await browser.close(); server.close(); } })().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
