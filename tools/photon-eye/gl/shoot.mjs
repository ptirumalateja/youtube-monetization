// Render a fragment-shader shot to PNG in headless Chromium.
// node shoot.mjs SHOT OUT.png [W H] [extra uniforms json]
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
const [shot, out, w = '1080', h = '1920', extra = '{}'] = process.argv.slice(2);
const dir = path.dirname(new URL(import.meta.url).pathname);
const frag = fs.readFileSync(path.join(dir, 'shots.glsl'), 'utf8');
const html = `<html><body style="margin:0;background:#000"><canvas id=c width=${w} height=${h}></canvas><script>
const c=document.getElementById('c');const gl=c.getContext('webgl2',{preserveDrawingBuffer:true});
const vs='#version 300 es\\nin vec2 p;void main(){gl_Position=vec4(p,0,1);}';
const fs=${JSON.stringify(frag)}.replace('SHOT_ID', String(${JSON.stringify(shot)}));
function sh(t,s){const o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(o));return o;}
const pr=gl.createProgram();gl.attachShader(pr,sh(gl.VERTEX_SHADER,vs));gl.attachShader(pr,sh(gl.FRAGMENT_SHADER,fs));gl.linkProgram(pr);gl.useProgram(pr);
const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
const l=gl.getAttribLocation(pr,'p');gl.enableVertexAttribArray(l);gl.vertexAttribPointer(l,2,gl.FLOAT,false,0,0);
gl.uniform2f(gl.getUniformLocation(pr,'R'),${w},${h});
const ex=${extra};for(const k in ex){const u=gl.getUniformLocation(pr,k);if(u)gl.uniform1f(u,ex[k]);}
// draw in horizontal strips so the software rasteriser never hits a watchdog
gl.enable(gl.SCISSOR_TEST);const S=64;let y=0;
function step(){if(y>=${h}){gl.finish();window.done=true;return;}gl.scissor(0,y,${w},S);gl.drawArrays(gl.TRIANGLES,0,3);gl.finish();y+=S;setTimeout(step,0);}step();
</script></body></html>`;
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
page.on('console', m => console.log(m.text())); page.on('pageerror', e => { console.error(e.message); process.exit(1); });
await page.setContent(html);
await page.waitForFunction('window.done===true', null, { timeout: 0, polling: 500 });
const data = await page.evaluate(() => document.getElementById('c').toDataURL('image/png'));
fs.writeFileSync(out, Buffer.from(data.split(',')[1], 'base64'));
await browser.close();
