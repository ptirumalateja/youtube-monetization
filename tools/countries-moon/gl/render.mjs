// node render.mjs jobs.json  — jobs: [{out,w,h,f:{uT:..}, v:{uCamP:[x,y,z]}, a:{uMC:[...]}, sdf:[isoA, isoB]}]; skips existing outputs.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
const dir = path.dirname(new URL(import.meta.url).pathname);
const frag = ['head.glsl', 'lib.glsl', 'tiles.glsl', 'main.glsl'].map(f => fs.readFileSync(path.join(dir, f), 'utf8')).join('\n');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')).filter(j => !fs.existsSync(j.out));
if (!jobs.length) process.exit(0);
const texs = { tEarth: 'earth_atmos_2048.jpg', tSpec: 'earth_specular_2048.jpg', tCloud: 'earth_clouds_2048.png', tLights: 'earth_lights_2048.png', tMoon: 'moon_1024.jpg' };
const texData = {};
for (const k in texs) { const f = path.join(dir, '../tex', texs[k]); texData[k] = 'data:image/' + (f.endsWith('png') ? 'png' : 'jpeg') + ';base64,' + fs.readFileSync(f).toString('base64'); }
const SDFS = ['india', 'IND', 'PAK', 'BGD', 'NPL', 'LKA', 'BTN'];
const sdf = Object.fromEntries(SDFS.map(k => [k, fs.readFileSync(path.join(dir, '../tex/' + (k === 'india' ? 'india_sdf' : 'sdf_' + k) + '.f32')).toString('base64')]));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
page.on('pageerror', e => { console.error(e.message); process.exit(1); });
page.on('console', m => { if (m.type() === 'error') console.error(m.text()); });
await page.setContent('<html><body style="margin:0"><canvas id=c></canvas></body></html>');
await page.evaluate(async ({ frag, texData, sdf }) => {
  const c = document.getElementById('c');
  const gl = c.getContext('webgl2', { preserveDrawingBuffer: true, alpha: true, premultipliedAlpha: false });
  const vs = '#version 300 es\nin vec2 p;void main(){gl_Position=vec4(p,0,1);}';
  function sh(t, s) { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; }
  const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, frag)); gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
  gl.useProgram(pr);
  const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const l = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 2, gl.FLOAT, false, 0, 0);
  let unit = 0;
  for (const k in texData) {
    const img = new Image(); img.src = texData[k]; await img.decode();
    const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img); gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.uniform1i(gl.getUniformLocation(pr, k), unit++);
  }
  window.sdfUnit = {};
  for (const k in sdf) { // country SDFs: R16F, linear
    const bin = atob(sdf[k]); const u8 = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    const f = new Float32Array(u8.buffer); const S = Math.round(Math.sqrt(f.length));
    const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.R16F, S, S, 0, gl.RED, gl.FLOAT, f);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    window.sdfUnit[k] = unit++;
  }
  gl.uniform1i(gl.getUniformLocation(pr, 'tIndia'), window.sdfUnit['india']);
  window.draw = async (w, h, f, v, a, sd) => {
    gl.uniform1i(gl.getUniformLocation(pr, 'tA'), window.sdfUnit[sd[0]]); gl.uniform1i(gl.getUniformLocation(pr, 'tB'), window.sdfUnit[sd[1]]);
    c.width = w; c.height = h; gl.viewport(0, 0, w, h);
    gl.uniform2f(gl.getUniformLocation(pr, 'R'), w, h);
    for (const k in f) gl.uniform1f(gl.getUniformLocation(pr, k), f[k]);
    for (const k in v) { if (v[k].length > 3) gl.uniform4fv(gl.getUniformLocation(pr, k), v[k]); else gl.uniform3fv(gl.getUniformLocation(pr, k), v[k]); }
    for (const k in (a || {})) gl.uniform4fv(gl.getUniformLocation(pr, k + '[0]'), new Float32Array(a[k]));
    gl.enable(gl.SCISSOR_TEST);
    for (let y = 0; y < h; y += 32) { gl.scissor(0, y, w, 32); gl.drawArrays(gl.TRIANGLES, 0, 3); gl.finish(); await new Promise(r => setTimeout(r, 0)); }
    gl.disable(gl.SCISSOR_TEST);
    return c.toDataURL('image/png');
  };
}, { frag, texData, sdf });
for (const j of jobs) {
  const t0 = Date.now();
  const data = await page.evaluate(({ w, h, f, v, a, sdf }) => window.draw(w, h, f, v, a, sdf), j);
  fs.writeFileSync(j.out + '.tmp', Buffer.from(data.split(',')[1], 'base64'));
  fs.renameSync(j.out + '.tmp', j.out);
  console.log(path.basename(j.out), ((Date.now() - t0) / 1000).toFixed(1) + 's');
}
await browser.close();
