// Usage:
//   node render.js stills <outdir> t1 t2 ...        -> PNG stills
//   node render.js video <out.mp4> [fps] [workers]  -> silent H.264 video
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const SCENE = 'file://' + path.join(__dirname, 'scene.html') + '?v=' + (process.env.V || 'A') + '&style=' + (process.env.STYLE || 'blueprint');

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(SCENE);
  await page.waitForFunction(() => window.READY === true);
  return page;
}

async function grab(page, t, type) {
  await page.evaluate((t) => window.renderAt(t), t);
  const el = await page.$('#c');
  return el.screenshot({ type, quality: type === 'jpeg' ? 95 : undefined });
}

async function stills(outdir, times) {
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch();
  const page = await openPage(browser);
  for (const t of times) {
    const buf = await grab(page, parseFloat(t), 'png');
    fs.writeFileSync(path.join(outdir, `t${parseFloat(t).toFixed(2)}.png`), buf);
  }
  await browser.close();
}

async function chunk(browser, out, fps, f0, f1) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = f0; f < f1; f++) {
    const buf = await grab(page, f / fps, 'jpeg');
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
}

async function video(out, fps = 30, workers = 3) {
  const browser = await chromium.launch();
  const dur = await (async () => { const p = await openPage(browser); const d = await p.evaluate(() => window.DUR); await p.close(); return d; })();
  const total = Math.round(dur * fps);
  const per = Math.ceil(total / workers);
  const parts = [];
  const jobs = [];
  for (let w = 0; w < workers; w++) {
    const f0 = w * per, f1 = Math.min(total, f0 + per);
    const p = out.replace(/\.mp4$/, `.part${w}.mp4`);
    parts.push(p);
    jobs.push(chunk(browser, p, fps, f0, f1));
  }
  await Promise.all(jobs);
  await browser.close();
  const list = out + '.txt';
  fs.writeFileSync(list, parts.map((p) => `file '${p}'`).join('\n'));
  await new Promise((r) => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out], { stdio: 'inherit' }).on('close', r));
  parts.forEach((p) => fs.unlinkSync(p));
  fs.unlinkSync(list);
}

const [mode, a, ...rest] = process.argv.slice(2);
if (mode === 'stills') stills(a, rest);
else video(a, parseInt(rest[0] || '30'), parseInt(rest[1] || '3'));
