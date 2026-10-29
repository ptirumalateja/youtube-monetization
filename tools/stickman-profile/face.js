// Expressive face for the pictogram hero: a glowing cream face drawn on a canvas and wrapped on the front of the head.
// An expression is a flat object of numbers so two of them blend with mix(). The canvas is 512 px; the head disc fills it.
//   eo  eye open 0..1         ec  closed-eye curve (+1 happy arch, -1 sleepy cup, 0 line)
//   es  eye scale             pr  pupil radius / eye width     px,py  gaze -1..1 (py +1 = up)
//   by  brow raise            ba  brow angle (+ worried, inner ends up; - angry)
//   mo  mouth open 0..1       mw  mouth width                  mc  mouth curve (+ smile)   mO  round "O" shape 0..1
//   tear, sweat, blush 0..1
import * as THREE from 'three';
export const NEUTRAL={eo:1,ec:0,es:1,pr:0.42,px:0,py:0,by:0,ba:0,mo:0,mw:0.8,mc:0.1,mO:0,tear:0,sweat:0,blush:0};
const X=o=>({...NEUTRAL,...o});
export const EX={
  neutral:X({}),
  content:X({eo:0,ec:-1,mc:0.7,mw:0.75,by:0.1}),
  sleepy:X({eo:0.35,mc:0.4,mw:0.6,by:-0.1}),
  yawn:X({eo:0,ec:0,mo:0.95,mO:0.55,mw:0.9,by:0.35,ba:0.3}),
  wide:X({es:1.12,pr:0.3,by:0.35,mc:-0.05,mw:0.45}),
  annoyed:X({eo:0.5,ba:-0.55,by:-0.1,mc:-0.45,mw:0.7}),
  sigh:X({eo:0.15,ec:0,ba:0.5,by:0.2,mo:0.35,mO:0.8,mw:0.55}),
  glare:X({eo:0.62,ba:-1,by:-0.15,mc:-0.6,mw:0.75,py:0.7}),
  delight:X({es:1.06,mc:0.85,mw:0.95,by:0.3,pr:0.46}),
  focus:X({eo:0.72,ba:-0.35,mc:0.05,mw:0.4,pr:0.46}),
  smirk:X({eo:0.8,mc:0.6,mw:0.8,by:0.1,ba:0.1}),
  laugh:X({eo:0,ec:1,mo:1,mc:1,mw:1.25,by:0.45,ba:0.55,tear:1,blush:1}),
  muffled:X({eo:0,ec:1,mo:0.2,mc:0.8,mw:0.9,by:0.5,ba:0.7,tear:1,blush:1}),
  frozen:X({es:1.15,pr:0.26,mo:0.55,mc:0.35,mw:1.0,by:0.55,ba:0.2}),
  shock:X({es:1.42,pr:0.2,by:1,ba:0.55,mo:0.95,mO:1,mw:0.65,sweat:1}),
};
export const mix=(a,b,u)=>{ const o={}; for(const k in NEUTRAL) o[k]=a[k]+(b[k]-a[k])*u; return o; };

const CREAM='#fff0d4', DARK='#1c0a07';
export function createFace(scene,{size=512}={}){
  const cv=document.createElement('canvas'); cv.width=cv.height=size; const g=cv.getContext('2d');
  const tex=new THREE.CanvasTexture(cv); tex.colorSpace=THREE.SRGBColorSpace; tex.anisotropy=8;
  // front half of a sphere, planar-mapped so the canvas reads undistorted from the front
  const geo=new THREE.SphereGeometry(1,64,40,0,Math.PI*2,0,Math.PI*0.5); geo.rotateX(Math.PI/2);
  const p=geo.attributes.position, uv=geo.attributes.uv; for(let i=0;i<p.count;i++) uv.setXY(i,0.5+p.getX(i)*0.5,0.5+p.getY(i)*0.5);
  const mat=new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false,fog:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
  const mesh=new THREE.Mesh(geo,mat); mesh.frustumCulled=false; mesh.renderOrder=3; scene.add(mesh);
  let last='';
  function draw(E){ const key=JSON.stringify(E,(k,v)=>typeof v==='number'?+v.toFixed(3):v); if(key===last) return; last=key;
    const s=size/512; g.setTransform(s,0,0,s,0,0); g.clearRect(0,0,512,512);
    g.lineCap='round'; g.lineJoin='round'; g.shadowColor='rgba(255,226,180,0.9)';
    const cy=226, ex=84;
    // eyes
    for(const sd of [-1,1]){ const cx=256+sd*ex, rx=42*E.es, ry=52*E.es;
      if(E.eo>0.07){ const top=cy-ry+(1-E.eo)*2*ry*0.92;
        g.save(); g.beginPath(); g.ellipse(cx,cy,rx,ry,0,0,7); g.clip(); g.beginPath(); g.rect(cx-rx-2,top,rx*2+4,ry*2+4); g.clip();
        g.shadowBlur=0; g.fillStyle=CREAM; g.fillRect(cx-rx-2,cy-ry-2,rx*2+4,ry*2+4);
        const pr=E.pr*rx, ppx=cx+E.px*(rx-pr)*0.85, ppy=cy-E.py*(ry-pr)*0.8;
        g.fillStyle='#120806'; g.beginPath(); g.arc(ppx,ppy,pr,0,7); g.fill();
        g.fillStyle=CREAM; g.beginPath(); g.arc(ppx-pr*0.35,ppy-pr*0.38,Math.max(3,pr*0.26),0,7); g.fill(); g.restore();
        if(E.eo<0.97){ g.shadowBlur=10; g.strokeStyle=CREAM; g.lineWidth=7; const hw=rx*Math.sqrt(Math.max(0,1-Math.pow((top-cy)/ry,2)));
          g.beginPath(); g.moveTo(cx-hw-3,top); g.lineTo(cx+hw+3,top); g.stroke(); }
      } else { g.shadowBlur=12; g.strokeStyle=CREAM; g.lineWidth=10; const w=rx*0.95, c=E.ec;
        g.beginPath(); g.moveTo(cx-w,cy+c*12); g.quadraticCurveTo(cx,cy-c*34,cx+w,cy+c*12); g.stroke(); }
      // brows
      const by=cy-52*E.es-30-E.by*26, inner=256+sd*34, outer=256+sd*132;
      g.shadowBlur=10; g.strokeStyle=CREAM; g.lineWidth=15;
      g.beginPath(); g.moveTo(inner,by-E.ba*24+6); g.quadraticCurveTo((inner+outer)/2,by-12-E.ba*4,outer,by+E.ba*10+8); g.stroke();
      if(E.blush>0.01){ g.shadowBlur=0; const rg=g.createRadialGradient(cx+sd*20,cy+78,2,cx+sd*20,cy+78,46); rg.addColorStop(0,`rgba(255,120,110,${0.55*E.blush})`); rg.addColorStop(1,'rgba(255,120,110,0)'); g.fillStyle=rg; g.fillRect(cx+sd*20-50,cy+28,100,100); }
      if(E.tear>0.01){ g.shadowBlur=14; g.shadowColor='rgba(150,210,255,0.9)'; g.fillStyle=`rgba(170,220,255,${0.95*E.tear})`;
        for(let k=0;k<3;k++){ const tx=cx+sd*(rx+6+k*7), ty=cy+8+k*30*E.tear; g.beginPath(); g.moveTo(tx,ty-14); g.quadraticCurveTo(tx+9,ty+2,tx,ty+10); g.quadraticCurveTo(tx-9,ty+2,tx,ty-14); g.fill(); }
        g.shadowColor='rgba(255,226,180,0.9)'; }
    }
    // mouth
    const my=356, w=68*E.mw;
    g.shadowBlur=12; g.strokeStyle=CREAM; g.lineWidth=10;
    if(E.mo<0.06){ g.beginPath(); g.moveTo(256-w,my-E.mc*14); g.quadraticCurveTo(256,my+E.mc*44,256+w,my-E.mc*14); g.stroke(); }
    else { const h=16+E.mo*92;
      g.beginPath();
      if(E.mO>0.5){ const ow=w*(1-0.35*E.mO), oh=h*0.62; g.ellipse(256,my+oh*0.25,ow,oh,0,0,7); }
      else { const ty=my-h*0.18-E.mc*10; g.moveTo(256-w,ty); g.quadraticCurveTo(256,ty+E.mc*18,256+w,ty); g.quadraticCurveTo(256+w*0.95,ty+h*1.25,256,ty+h*1.2); g.quadraticCurveTo(256-w*0.95,ty+h*1.25,256-w,ty); }
      g.closePath(); g.save(); g.shadowBlur=0; g.fillStyle=DARK; g.fill(); g.clip();
      if(E.mO<=0.5){ const ty=my-h*0.18-E.mc*10; g.fillStyle='#e8a090'; g.beginPath(); g.ellipse(256,ty+h*1.05,w*0.55,h*0.38,0,0,7); g.fill();
        if(E.mc>0.5){ g.fillStyle=CREAM; g.fillRect(256-w,ty-4,w*2,12+h*0.08); } }
      else { g.fillStyle='#b86a5c'; g.beginPath(); g.ellipse(256,my+h*0.55,w*0.4,h*0.2,0,0,7); g.fill(); }
      g.restore(); g.stroke(); }
    if(E.sweat>0.01){ g.shadowBlur=14; g.shadowColor='rgba(150,210,255,0.9)'; g.fillStyle=`rgba(170,220,255,${E.sweat})`; const sx=410, sy=150;
      g.beginPath(); g.moveTo(sx,sy-26); g.quadraticCurveTo(sx+18,sy+6,sx,sy+16); g.quadraticCurveTo(sx-18,sy+6,sx,sy-26); g.fill(); }
    tex.needsUpdate=true; }
  // head centre, face direction f, head up u, head radius r
  function place(head,f,u,r,vis=true){ mesh.visible=vis; if(!vis) return; const x=u.clone().cross(f).normalize(), y=f.clone().cross(x).normalize();
    mesh.position.copy(head); mesh.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x,y,f)); mesh.scale.setScalar(r*1.012); }
  return {draw,place,mesh}; }
