// node render.cjs [--gpu] [--stills]   (stills: review frames + monotonic/loop checks; default: full MP4)
const { chromium } = require('playwright-core');
const { spawn } = require('node:child_process');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, output = path.join(root, 'output'); fs.mkdirSync(output, { recursive: true });
const spec = JSON.parse(fs.readFileSync(path.join(root, 'timeline.json'), 'utf8'));
const total = Math.round(spec.duration * spec.fps);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const file = path.resolve(root, '.' + decodeURIComponent(req.url.split('?')[0] === '/' ? '/index.html' : req.url.split('?')[0]));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } });
});
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true,
    args: process.argv.includes('--gpu') ? ['--use-angle=metal'] : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  try {
    const w = Number(process.env.RENDER_W || 720);
    const page = await browser.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${w}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 120000 });
    // counters must never go backwards inside one loop
    const mono = await page.evaluate(({ total, fps }) => { let prev = { n: 0, pairs: 0, p: 0 }; for (let f = 0; f < total; f++) { const s = window.stateAt(f / fps);
      if (s.n < prev.n || s.pairs < prev.pairs || s.p < prev.p - 1e-12) return `backwards at frame ${f}`; prev = s; } return 'ok'; }, { total, fps: spec.fps });
    console.log('monotonic counters:', mono); if (mono !== 'ok') throw Error(mono);
    if (process.argv.includes('--stills')) {
      const times = process.env.TIMES ? process.env.TIMES.split(',').map(Number) : spec.reviewTimes;
      for (const t of times) {
        const b64 = await page.evaluate(t => window.captureFrame(t, Math.round(t * 30)), t);
        fs.writeFileSync(path.join(output, `still-${t.toFixed(2).padStart(5, '0')}.jpg`), Buffer.from(b64, 'base64'));
      }
      console.log('stills written');
    } else {
      const name = process.env.OUT || 'birthday-paradox-21.5s.mp4';
      const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'warning', '-f', 'image2pipe', '-framerate', String(spec.fps), '-i', 'pipe:0',
        '-i', path.join(output, 'sound.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-t', String(spec.duration), '-movflags', '+faststart', path.join(output, name)], { stdio: ['pipe', 'ignore', 'inherit'] });
      const t0 = Date.now();
      for (let f = 0; f < total; f++) {
        const b64 = await page.evaluate(f => window.captureFrame(f / 30, f), f);
        if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
        if (f % 60 === 0) console.log(`frame ${f}/${total} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
      ff.stdin.end(); await new Promise((res, rej) => ff.on('exit', c => c ? rej(Error('ffmpeg ' + c)) : res()));
      console.log('wrote', name);
    }
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
