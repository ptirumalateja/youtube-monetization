// Batch-render shader plates in one headless Chromium page.
// node render.mjs jobs.json   (jobs: [{shot, out, w, h, u:{uT,uZ,...}}]); skips outputs that already exist.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
const dir = path.dirname(new URL(import.meta.url).pathname);
const frag = fs.readFileSync(path.join(dir, process.env.SHADER || 'shots.glsl'), 'utf8');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')).filter(j => !fs.existsSync(j.out));
if (!jobs.length) process.exit(0);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
page.on('pageerror', e => { console.error(e.message); process.exit(1); });
await page.setContent('<html><body style="margin:0"><canvas id=c></canvas></body></html>');
await page.evaluate((frag) => {
  const c = document.getElementById('c');
  const gl = c.getContext('webgl2', { preserveDrawingBuffer: true });
  const progs = {};
  const vs = '#version 300 es\nin vec2 p;void main(){gl_Position=vec4(p,0,1);}';
  function sh(t, s) { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; }
  const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  window.draw = async (shot, w, h, u) => {
    if (!progs[shot]) {
      const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, frag.replace('SHOT_ID', String(shot)))); gl.linkProgram(pr);
      progs[shot] = pr;
    }
    const pr = progs[shot]; gl.useProgram(pr);
    c.width = w; c.height = h; gl.viewport(0, 0, w, h);
    const l = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(gl.getUniformLocation(pr, 'R'), w, h);
    for (const k in u) { const l = gl.getUniformLocation(pr, k); if (l) gl.uniform1f(l, u[k]); }
    gl.enable(gl.SCISSOR_TEST);
    for (let y = 0; y < h; y += 64) { gl.scissor(0, y, w, 64); gl.drawArrays(gl.TRIANGLES, 0, 3); gl.finish(); await new Promise(r => setTimeout(r, 0)); }
    gl.disable(gl.SCISSOR_TEST);
    return c.toDataURL('image/png');
  };
}, frag);
for (const j of jobs) {
  const t0 = Date.now();
  const data = await page.evaluate(({ shot, w, h, u }) => window.draw(shot, w, h, u), j);
  fs.writeFileSync(j.out + '.tmp', Buffer.from(data.split(',')[1], 'base64'));
  fs.renameSync(j.out + '.tmp', j.out);
  console.log(path.basename(j.out), ((Date.now() - t0) / 1000).toFixed(1) + 's');
}
await browser.close();
