// The opening / closing bed sequence: lying on his side with the phone, the salary lands, his face changes, he pushes the quilt off,
// sits up, swings his legs over the edge, stands (hands pushing on the mattress) and walks off. Story time s: s = t for the hook, s = t - 20 for the loop end
// (so the state at s = 0 is the same in both and the loop is seamless). Units are metres; bed-set-local coordinates (x offset added by the caller).
import * as THREE from 'three';
import * as SLD from './sld.js';
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sst=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const rotZ=(v,th,c)=>{ const d=v.clone().sub(c), cs=Math.cos(th), sn=Math.sin(th); return V(c.x+d.x*cs-d.y*sn,c.y+d.x*sn+d.y*cs,c.z+d.z); };
const FACE_Z=SLD.yawOf(V(0,0,1));
export const BED={hipLie:V(-0.12,0.66,-1.3), hipSit:V(-0.12,0.62,-0.82)};
// keyframed scalar (linear between keys, flat outside)
const K=(ks,s)=>{ if(s<=ks[0][0]) return ks[0][1]; for(let i=1;i<ks.length;i++) if(s<=ks[i][0]){ const u=(s-ks[i-1][0])/(ks[i][0]-ks[i-1][0]); const e=u*u*(3-2*u); return lerp(ks[i-1][1],ks[i][1],e); } return ks[ks.length-1][1]; };
const legX=(P)=>{ const f=(a,k)=>Math.sin(a)*0.46+Math.sin(a-k)*0.46; return (f(P.aL,P.kL)+f(P.aR,P.kR))/2; };

export function createBedSeq(R){
  const L=R.L;
  const P_SIT={...R.P0,p:0.22,tilt:0.08,aL:1.3,aR:1.3,kL:1.3,kR:1.3,sL:0.1,sR:0.1,eL:0.5,eR:0.5};
  const P_STAND={...R.P0,p:0.05,tilt:-0.02};
  const J_sit=R.skel(P_SIT,V(0,0,0),FACE_Z); // hip height of the sitting pose (feet on the floor)
  const rootSit=V(BED.hipSit.x-J_sit.hip.x,0,BED.hipSit.z-J_sit.hip.z); BED.hipSit.y=J_sit.hip.y;
  const feetSit=0.4*legX(P_SIT);
  const walkDir=V(1,0,0.18).normalize(), yawWalk=SLD.yawOf(walkDir);
  // distance walked by story time s
  const dist=s=>s<3.65?0:(s<4.25?0.9*(s-3.65)*(s-3.65):0.324+1.1*(s-4.25));

  function face(s){ // mood 0..1, brow, wide (eyes), open (mouth)
    const mood=K([[-2,0.28],[-1.2,0.28],[-1.0,0.45],[0,0.58],[0.5,0.78],[1.1,0.9],[2.2,0.85],[3.4,0.78]],s);
    const brow=K([[-2,0],[-1.15,0],[-0.95,0.8],[-0.4,0.6],[0.2,0.9],[1.5,0.5],[2.6,0.15]],s);
    const wide=K([[-1.1,0],[-0.9,0.8],[-0.2,0.45],[0.4,0.7],[1.6,0.2],[2.6,0]],s);
    const open=K([[0.7,0],[1.0,0.18],[1.5,0.1],[1.9,0]],s);
    return {mood,brow,wide,open}; }

  // the lying-to-sitting body (rotated about the hip around the world z axis), and the standing / walking body after it
  function pose(s){
    const out={phone:null,quilt:0,phoneLight:0};
    const t=s; const breathe=0.012*Math.sin(s*2.3);
    const th=Math.PI/2*(1-sst(2.35,3.15,s));
    const stand=sst(3.1,3.95,s);
    if(s<3.1){
      const uSit=sst(2.3,3.05,s);
      // hook beat: the head lifts and the shoulders come up with the smile, a small nod
      const lift=sst(-1.0,0.7,s)*(1-sst(2.0,2.4,s));
      const nod=0.07*Math.sin((s-0.5)*9)*sst(0.5,0.7,s)*(1-sst(1.5,1.8,s));
      const P={...R.P0,p:lerp(0.28,P_SIT.p,uSit)+0.05*lift+breathe,tilt:lerp(0.12+0.1*lift+nod,0.08,uSit),hy:0.0,
        aL:lerp(1.25,1.3,uSit),aR:lerp(1.05,1.3,uSit),kL:lerp(2.1,1.3,uSit),kR:lerp(1.9,1.3,uSit),sL:0.1,sR:0.1,eL:0.5,eR:0.5};
      const hipT=BED.hipLie.clone().lerp(BED.hipSit,uSit); hipT.y=lerp(BED.hipLie.y,BED.hipSit.y,uSit)+0.015*Math.sin(s*2.3);
      // targets (world) -> body frame (undo the lying rotation about the hip)
      const J0=R.skel({...P},V(0,0,0),FACE_Z); const hipS=J0.hip;
      const toBody=w=>rotZ(w.clone().sub(hipT),-th,V(0,0,0)).add(hipS);
      // the phone: in front of his face, below it, tilted up to it
      const J1=R.skel({...P},V(0,0,0),FACE_Z);
      const Jw0=(()=>{ const o={}; for(const k in J1) if(J1[k].isVector3) o[k]=rotZ(J1[k].clone().sub(hipS).add(hipT),th,hipT); return o; })();
      const pump=sst(0.9,1.2,s)*(1-sst(1.5,1.8,s)); const pumpY=0.06*pump*Math.abs(Math.sin((s-0.9)*7));
      const phHold=Jw0.head.clone().add(V(0.10,-0.12+pumpY,0.27));
      const place=sst(1.85,2.25,s); const phRest=V(hipT.x-0.1,0.57,hipT.z+0.1);
      const ph=phHold.clone().lerp(phRest,place);
      const hold=1-sst(2.0,2.3,s);
      // R (upper) hand holds the phone, L (lower) hand tucked under the pillow, then both push on the mattress
      const push=sst(2.3,2.6,s)*(1-sst(3.3,3.5,s));
      const Rt_hold=ph.clone().add(V(0.05,0.03,0.0)); const Rt_push=V(hipT.x+0.14,0.545,hipT.z+0.12);
      const Lt_tuck=Jw0.head.clone().add(V(0.02,-0.12,0.06)); const Lt_push=V(hipT.x-0.14,0.545,hipT.z+0.12);
      const Rt=Rt_hold.clone().lerp(Rt_push,sst(2.0,2.5,s)); const Lt=Lt_tuck.clone().lerp(Lt_push,sst(2.1,2.6,s));
      P.tR=toBody(Rt); P.wR=1; P.pR=V(0,-0.9,-0.5); P.tL=toBody(Lt); P.wL=1; P.pL=V(0,-0.9,0.5);
      const J=R.skel(P,V(0,0,0),FACE_Z); const W={}; for(const k in J) if(J[k].isVector3) W[k]=rotZ(J[k].clone().sub(hipS).add(hipT),th,hipT); W.fwd=V(0,0,1);
      out.J=W; out.phone={pos:ph,n:W.head.clone().sub(ph).normalize(),held:hold}; out.phoneLight=1-sst(2.1,2.4,s);
      out.quilt=sst(1.95,2.7,s); out.hip=hipT; out.roll=-1.15*(th/(Math.PI/2));
      out.cam=cam(s,W);
      return out; }
    // standing up and walking: feet planted at rootSit until he steps off
    const u=stand; const P=R.blend(P_SIT,P_STAND,u); P.p=lerp(P_SIT.p,P_STAND.p,u)+0.38*Math.sin(Math.PI*Math.min(1,u*1.15))*(1-u); P.tilt=lerp(P_SIT.tilt,-0.02,u);
    const walk=sst(3.65,4.0,s); const d=dist(s);
    const ph=d/1.3*2*Math.PI; Object.assign(P,R.gait({...P},ph,walk*0.95,0.34,0.62,0.2));
    P.fx=feetSit-0.4*legX(P)*(1-walk); // keep the feet from sliding while he rises
    const yaw=lerp(FACE_Z,yawWalk,sst(3.6,4.15,s)); const dir=V(Math.cos(yaw),0,-Math.sin(yaw));
    const root=rootSit.clone().add(walkDir.clone().multiplyScalar(d));
    const hands=sst(3.1,3.3,s)*(1-sst(3.5,3.8,s)); // still pushing on the mattress while he straightens
    const hipNow=R.skel(P,root,yaw).hip;
    if(hands>0){ P.tR=V(BED.hipSit.x+0.14,0.545,BED.hipSit.z+0.12); P.wR=hands; P.pR=V(0,-0.9,-0.5); P.tL=V(BED.hipSit.x-0.14,0.545,BED.hipSit.z+0.12); P.wL=hands; P.pL=V(0,-0.9,0.5); }
    else { P.sL=0.12-0.3*Math.sin(ph)*walk*0.7; P.sR=-0.05+0.3*Math.sin(ph)*walk*0.7; }
    const J=R.skel(P,root,yaw);
    out.J=J; out.quilt=1; out.phone={pos:V(BED.hipSit.x-0.1,0.57,BED.hipSit.z+0.1),n:V(0,1,0.3).normalize(),held:0}; out.phoneLight=0;
    out.cam=cam(s,J);
    return out; }

  // camera: start on the bed, then follow him up and out
  function cam(s,J){ const u=sst(2.2,3.4,s), w=sst(3.4,4.5,s);
    const hc=J.hip.clone().lerp(J.neck,0.5);
    const p0=V(0.1,1.3,2.55), l0=V(-0.42,0.72,-1.1);
    const p1=V(0.55,1.4,3.5), l1=V(0.05,hc.y*0.9+0.2,-0.4);
    const p2=V(hc.x+0.5,1.4,3.6), l2=V(hc.x+0.4,1.0,-0.4);
    const pos=p0.clone().lerp(p1,u).lerp(p2,w), look=l0.clone().lerp(l1,u).lerp(l2,w);
    return {pos,look}; }
  return {pose,face,P_SIT,rootSit};
}
