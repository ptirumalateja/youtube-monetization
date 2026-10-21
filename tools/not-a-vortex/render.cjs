// node render.cjs [--gpu] [--stills]   (stills: review frames + fact checks; default: frames for the MP4)
// FROM/TO pick a frame range (parallel workers); OUT_DIR collects JPEG frames; ffmpeg assembly is in build.sh
const { chromium } = require('playwright-core');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, output = path.join(root, 'output'); fs.mkdirSync(output, { recursive: true });
const spec = JSON.parse(fs.readFileSync(path.join(root, 'timeline.json'), 'utf8'));
const total = Math.round(spec.duration * spec.fps);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const file = path.resolve(root, '.' + decodeURIComponent(req.url.split('?')[0] === '/' ? '/index.html' : req.url.split('?')[0]));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } });
});
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', headless: true,
    args: process.argv.includes('--gpu') ? ['--use-angle=metal'] : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  try {
    const w = Number(process.env.RENDER_W || 720);
    const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[console]', m.text().slice(0, 400)); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${w}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 300000 });
    const mono = await page.evaluate(({ total, fps }) => { let prev = 0; for (let f = 0; f < total; f++) { const s = window.stateAt(f / fps); s.km = s.myr;
      if (s.km < prev) return `backwards at frame ${f}`; prev = s.km; } return 'ok'; }, { total, fps: spec.fps });
    console.log('monotonic lap counter:', mono); if (mono !== 'ok') throw Error(mono);
    const fc = await page.evaluate(() => window.factCheck()); console.log('fact check:', JSON.stringify(fc));
    if (Math.abs(fc.eclipticToGalacticPlaneDeg - 60.2) > 0.3 || fc.earthAheadFraction < 0.45 || fc.earthAheadFraction > 0.55) throw Error('fact check failed');
    if (process.argv.includes('--stills')) {
      const times = process.env.TIMES ? process.env.TIMES.split(',').map(Number) : spec.reviewTimes;
      for (const t of times) {
        const t0 = Date.now(); const b64 = await page.evaluate(t => window.captureFrame(t, Math.round(t * 30)), t);
        fs.writeFileSync(path.join(output, `still-${t.toFixed(2).padStart(5, '0')}.jpg`), Buffer.from(b64, 'base64')); console.log('still', t, Date.now() - t0, 'ms');
      }
    } else {
      const dir = process.env.OUT_DIR || path.join(output, 'frames'); fs.mkdirSync(dir, { recursive: true });
      const from = Number(process.env.FROM || 0), to = Math.min(total, Number(process.env.TO || total)), t0 = Date.now();
      for (let f = from; f < to; f++) {
        const file = path.join(dir, `f${String(f).padStart(4, '0')}.jpg`); if (fs.existsSync(file)) continue;
        const b64 = await page.evaluate(f => window.captureFrame(f / 30, f), f); fs.writeFileSync(file, Buffer.from(b64, 'base64'));
        if (f % 20 === 0) console.log(`frame ${f} (${from}-${to}) ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    }
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
