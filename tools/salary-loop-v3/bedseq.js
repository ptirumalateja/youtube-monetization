// The opening / closing bed sequence. He is asleep on his side, the phone by his pillow. The bell makes him open his eyes, turn his head and reach for the phone;
// the screen faces him; the salary lands; he smiles, pulls the blanket down, sits up, swings his legs over the edge, finds the floor, stands (hands pushing on the
// mattress) and walks off. Story time s: s = t for the hook, s = t - 20 for the loop end (asleep again, so the end frame matches the first frame).
import * as THREE from 'three';
import * as SLD from './sld.js';
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sst=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const rotZ=(v,th,c)=>{ const d=v.clone().sub(c), cs=Math.cos(th), sn=Math.sin(th); return V(c.x+d.x*cs-d.y*sn,c.y+d.x*sn+d.y*cs,c.z+d.z); };
const FACE_Z=SLD.yawOf(V(0,0,1));
export const BED={hipLie:V(-0.12,0.66,-1.3), hipSit:V(-0.12,0.62,-0.82)};
const K=(ks,s)=>{ if(s<=ks[0][0]) return ks[0][1]; for(let i=1;i<ks.length;i++) if(s<=ks[i][0]){ const u=(s-ks[i-1][0])/(ks[i][0]-ks[i-1][0]); const e=u*u*(3-2*u); return lerp(ks[i-1][1],ks[i][1],e); } return ks[ks.length-1][1]; };
const legX=(P)=>{ const f=(a,k)=>Math.sin(a)*0.46+Math.sin(a-k)*0.46; return (f(P.aL,P.kL)+f(P.aR,P.kR))/2; };
// beats (story seconds)
export const BEAT={bell:0.3, eyes:0.55, reach:[0.85,1.5], card:1.0, smile:[1.4,2.1], putDown:[2.15,2.5], pull:[2.3,3.0], sit:[2.9,3.8], seated:3.8, stand:[4.05,4.7], walk:4.45, end:5.0};

export function createBedSeq(R){
  const P_SIT={...R.P0,p:0.22,tilt:0.08,aL:1.3,aR:1.3,kL:1.3,kR:1.3,sL:0.1,sR:0.1,eL:0.5,eR:0.5};
  const P_STAND={...R.P0,p:0.05,tilt:-0.02};
  const J_sit=R.skel(P_SIT,V(0,0,0),FACE_Z);
  const rootSit=V(BED.hipSit.x-J_sit.hip.x,0,BED.hipSit.z-J_sit.hip.z); BED.hipSit.y=J_sit.hip.y;
  const feetSit=0.4*legX(P_SIT);
  const walkDir=V(1,0,0.18).normalize(), yawWalk=SLD.yawOf(walkDir);
  const W0=BEAT.walk; const dist=s=>s<W0?0:(s<W0+0.6?0.9*(s-W0)*(s-W0):0.324+1.1*(s-W0-0.6));
  const phoneRest=V(-0.58,0.585,-0.9);

  function face(s){
    const sleep=s<BEAT.eyes?1:0;
    const mood=K([[-2,0.52],[0.4,0.52],[0.9,0.55],[1.5,0.78],[2.1,0.95],[3.2,0.9],[4.8,0.8]],s);
    const brow=K([[-2,0],[0.5,0],[0.75,0.9],[1.2,0.5],[1.6,0.85],[2.4,0.5],[3.4,0.15]],s);
    const wide=K([[0.5,0],[0.7,0.9],[1.2,0.35],[1.7,0.6],[2.5,0.1]],s);
    const open=K([[1.5,0],[1.8,0.35],[2.2,0.15],[2.6,0]],s);
    return {mood,brow,wide,open,sleep}; }

  function pose(s){
    const out={phone:null,quilt:0,phoneLight:0};
    const breathe=0.012*Math.sin(s*2.1);
    const th=Math.PI/2*(1-sst(BEAT.sit[0],BEAT.sit[1],s));
    if(s<BEAT.stand[0]-0.3){
      const uSit=sst(BEAT.sit[0]-0.1,BEAT.sit[1]-0.1,s);
      const awake=sst(BEAT.eyes-0.1,BEAT.eyes+0.35,s);      // head comes up off the pillow
      const happy=sst(BEAT.smile[0],BEAT.smile[1],s)*(1-sst(2.6,3.0,s));
      const shake=0.014*Math.sin(s*43)*(s>BEAT.bell&&s<BEAT.bell+0.45?1:0);
      const wig=0.05*happy*Math.sin(s*14);                  // shoulders bounce with the smile
      const P={...R.P0,p:lerp(0.24,P_SIT.p,uSit)+0.05*awake+0.02*happy+breathe+wig*0.5,tilt:lerp(0.22-0.12*awake+0.04*happy,0.08,uSit),
        aL:lerp(1.2,1.3,uSit),aR:lerp(1.0,1.3,uSit)+0.1*wig,kL:lerp(2.1,1.3,uSit),kR:lerp(1.9,1.3,uSit)-0.12*wig,sL:0.1,sR:0.1,eL:0.5,eR:0.5};
      const hipT=BED.hipLie.clone().lerp(BED.hipSit,uSit); hipT.y=lerp(BED.hipLie.y,BED.hipSit.y,uSit)+0.012*Math.sin(s*2.1)+0.012*wig;
      const J0=R.skel({...P},V(0,0,0),FACE_Z); const hipS=J0.hip;
      const toBody=w=>rotZ(w.clone().sub(hipT),-th,V(0,0,0)).add(hipS);
      const toWorld=J=>{ const o={}; for(const k in J) if(J[k].isVector3) o[k]=rotZ(J[k].clone().sub(hipS).add(hipT),th,hipT); return o; };
      const Jw0=toWorld(J0);
      // phone: on the mattress by the pillow (it buzzes at the bell), then in his hand facing him, then back down
      const rest=phoneRest.clone().add(V(shake,0,shake*0.5));
      const hold=Jw0.head.clone().add(V(0.24,0.0,0.34));
      const grab=sst(BEAT.reach[0]+0.25,BEAT.reach[1],s); const arc=Math.sin(Math.PI*grab)*0.07;
      let ph=rest.clone().lerp(hold,grab); ph.y+=arc;
      const down=sst(BEAT.putDown[0],BEAT.putDown[1],s); ph.lerp(phoneRest,down);
      const hasHand=sst(BEAT.reach[0],BEAT.reach[0]+0.3,s)*(1-sst(BEAT.putDown[1]-0.1,BEAT.putDown[1]+0.2,s));
      // R (upper) arm: lies on the blanket, reaches the phone, holds it, puts it down, then pulls the blanket and pushes on the mattress
      const Rt_rest=V(-0.52,0.7,-0.98);
      let Rt=Rt_rest.clone().lerp(ph.clone().add(V(0.05,0.0,-0.08)),sst(BEAT.reach[0]-0.05,BEAT.reach[0]+0.35,s));
      const pullA=sst(BEAT.pull[0],BEAT.pull[0]+0.3,s), pullB=sst(BEAT.pull[0]+0.3,BEAT.pull[1],s);
      Rt=Rt.lerp(V(-0.45,0.8,-1.0),pullA).lerp(V(hipT.x+0.05,0.74,hipT.z+0.22),pullB).lerp(V(hipT.x+0.14,0.545,hipT.z+0.12),sst(BEAT.sit[0]-0.2,BEAT.sit[0]+0.2,s));
      const Lt_tuck=Jw0.head.clone().add(V(0.08,-0.2,-0.04)); const Lt_push=V(hipT.x-0.14,0.545,hipT.z+0.12);
      const Lt=Lt_tuck.clone().lerp(Lt_push,sst(BEAT.sit[0]-0.3,BEAT.sit[0]+0.1,s));
      P.tR=toBody(Rt); P.wR=1; P.pR=V(0,-0.9,-0.5); P.tL=toBody(Lt); P.wL=1; P.pL=V(0,-0.9,0.5);
      const J=R.skel(P,V(0,0,0),FACE_Z); const Wj=toWorld(J); Wj.fwd=V(0,0,1);
      // V3: the phone is propped against the pillow FACING HIM (the viewer sees its back); held, it faces his eyes
      const toHead=Wj.head.clone().sub(ph).normalize(); ph.y+=0.045*(1-grab*(1-down));
      out.J=Wj; out.phone={pos:ph,n:toHead.clone().lerp(V(0,1,0),0.15*(1-grab*(1-down))).normalize(),held:hasHand};
      out.phoneLight=sst(BEAT.bell,BEAT.bell+0.08,s)*(1-sst(BEAT.putDown[1]+0.1,BEAT.putDown[1]+0.35,s));
      out.quilt=sst(BEAT.pull[0]+0.2,BEAT.pull[1]+0.5,s); out.hip=hipT; out.roll=-1.15*(th/(Math.PI/2));
      // the face is turned a little down into the pillow while he sleeps, and comes round to the phone when he wakes
      out.faceFwd=V(0,lerp(-0.12,0.12,awake),1).normalize();
      out.cam=cam(s,Wj);
      return out; }
    // sitting on the bed edge, then standing up and walking: feet planted at rootSit until he steps off
    const u=sst(BEAT.stand[0],BEAT.stand[1],s); const P=R.blend(P_SIT,P_STAND,u);
    P.p=lerp(P_SIT.p,P_STAND.p,u)+0.4*Math.sin(Math.PI*Math.min(1,u*1.1))*(1-u); P.tilt=lerp(P_SIT.tilt,-0.02,u);
    const walk=sst(W0,W0+0.4,s); const d=dist(s); const ph=d/1.3*2*Math.PI;
    Object.assign(P,R.gait({...P},ph,walk*0.95,0.34,0.62,0.2));
    P.fx=feetSit-0.4*legX(P)*(1-walk);
    const yaw=lerp(FACE_Z,yawWalk,sst(4.3,4.85,s)); const root=rootSit.clone().add(walkDir.clone().multiplyScalar(d));
    const hands=sst(4.0,4.1,s)*(1-sst(4.3,4.6,s))+ (1-sst(4.0,4.05,s));
    const hh=clamp(hands);
    if(hh>0.01){ P.tR=V(BED.hipSit.x+0.14,0.545,BED.hipSit.z+0.12); P.wR=hh; P.pR=V(0,-0.9,-0.5); P.tL=V(BED.hipSit.x-0.14,0.545,BED.hipSit.z+0.12); P.wL=hh; P.pL=V(0,-0.9,0.5); }
    else { P.sL=0.12-0.3*Math.sin(ph)*walk*0.7; P.sR=-0.05+0.3*Math.sin(ph)*walk*0.7; }
    const J=R.skel(P,root,yaw);
    out.J=J; out.quilt=1; out.phone={pos:phoneRest.clone(),n:V(0,1,0.3).normalize(),held:0}; out.phoneLight=0; out.roll=0; out.faceFwd=J.fwd;
    out.cam=cam(s,J);
    return out; }

  function cam(s,J){ const u=sst(2.6,3.9,s), w=sst(4.1,4.95,s);
    const hc=J.hip.clone().lerp(J.neck,0.5);
    const p0=V(-1.05,1.3,1.55), l0=V(-0.62,0.74,-1.08);   /* V3: from his head side so the propped phone sits beside his face, not in front of it; the wall calendar is in frame */
    const p1=V(0.55,1.4,3.5), l1=V(0.05,hc.y*0.9+0.2,-0.4);
    const p2=V(hc.x+0.5,1.4,3.6), l2=V(hc.x+0.4,1.0,-0.4);
    const pos=p0.clone().lerp(p1,u).lerp(p2,w), look=l0.clone().lerp(l1,u).lerp(l2,w);
    return {pos,look}; }
  return {pose,face,P_SIT,rootSit};
}
