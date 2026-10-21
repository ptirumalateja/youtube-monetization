// v4 cut list. Every value is a pure function of time t (seconds); shots are hard cuts keyed to the voiceover.
import {track} from '../nightmare/timeline.js';
export {track};

export const SPEC={duration:20.6,fps:30,width:1080,height:1920};
export const OFF=.2;                       // the voiceover starts at +0.2 s in the mix

// the sleeper's face on the pillow, and where the thing stands on each cut (it is closer every time)
export const FACE=[-2.88,.95,-.64];
export const P=[[2.6,-2.6],[.2,-2.3],[-.9,-1.95],[-1.5,-1.95],[-2.05,-1.8]];
const facing=(x,z)=>Math.atan2(FACE[0]-x,FACE[2]-z);
const L=(a,b,u)=>a+(b-a)*u, ease=u=>u*u*(3-2*u), easeIn=u=>u*u*u;
const lerp3=(a,b,u)=>a.map((v,i)=>L(v,b[i],u));

export function build(ts){
 const seg=ts.segments.map(s=>({...s,start:s.start+OFF,end:s.end+OFF}));
 const word=(w,n=0)=>ts.words.filter(x=>x.word.toLowerCase().replace(/[^a-z0-9']/g,'')===w)[n].start+OFF;
 const T={three:word('3'),wake:word('wake'),corner:word('corner'),sleep:word('sleep'),body:word('body'),trapped:word('trapped'),closer:word('closer'),dont:word("don't"),open:word('open'),eyes:word('eyes'),eyesEnd:seg[11].end};
 const cut=[0,seg[1].start-.12,seg[3].start-.14,seg[4].start-.12,seg[5].start-.12,seg[6].start-.1,seg[8].start-.15,seg[9].start-.1,seg[10].start-.08,seg[11].start-.04,T.eyesEnd+.04,SPEC.duration];
 T.black=cut[10];
 const W=(i,o={})=>({x:P[i][0],z:P[i][1],rot:facing(...P[i]),lean:.12,reach:.08,open:.2,claw:0,headDown:0,headTilt:.22,headTurn:0,y:0,...o});
 const shots=[
  // 1  "It's 3 A.M."  the clock on the nightstand flips to 3:00 beside a dying candle; slow push
  {cam:u=>({pos:lerp3([-2.1,.86,1.1],[-2.3,.82,.92],ease(u)),look:[-2.9,.76,.4],fov:38}),wraith:()=>W(0)},
  // 2  "You wake up... and you can't move."  his face; the eye snaps open on "wake"
  {cam:u=>({pos:lerp3([-2.68,1.02,-.16],[-2.74,1.0,-.27],ease(u)),look:[-2.87,.95,-.64],fov:38,roll:-.06}),wraith:()=>W(0)},
  // 3  "You can't scream."  tighter, tilted, trembling
  {cam:u=>({pos:lerp3([-2.79,.99,-.36],[-2.82,.98,-.42],ease(u)),look:[-2.875,.955,-.64],fov:36,roll:.16,shake:.0016}),wraith:()=>W(0)},
  // 4  "Something is standing in the corner of your room."  his point of view across the room; the eyes ignite on "corner"
  {cam:u=>({pos:[-2.74,1.04,-.42],look:lerp3([1.6,1.55,-2.4],[2.55,1.95,-2.6],ease(u)),fov:L(52,30,ease(u))}),wraith:()=>W(0,{headTilt:.3})},
  // 5  "Doctors call it sleep paralysis."  wide and high from the far corner of the room; it has come forward
  {cam:(u,c)=>({pos:lerp3([.7,2.55,4.3],[.5,2.4,3.95],ease(u)),look:lerp3([-1.4,.9,-1.2],c.head,.35),fov:64}),wraith:(u,t)=>W(1,{headTilt:.18+.05*Math.sin(t*1.7)})},
  // 6  "Your mind wakes up... but your body stays asleep."  low along the bed; it stands at the foot, the covered arm tries to lift
  {cam:(u,c)=>({pos:lerp3([-.85,1.25,2.75],[-1.05,1.2,2.35],ease(u)),look:lerp3(FACE,c.head,.5),fov:66}),wraith:(u,t)=>W(2,{lean:.2,headTilt:.35,reach:.15})},
  // 7  "And every second you're trapped..."  his face again, its silhouette behind him; heartbeat push-ins
  {cam:(u,c)=>({pos:lerp3([-3.0,.98,-.1],[-3.0,1.0,-.22],ease(u)),look:lerp3(FACE,c.head,.5),fov:62,roll:-.1,shake:.0012}),wraith:()=>W(3,{lean:.3,headTilt:.25,reach:.3,open:.5})},
  // 8  "it comes closer."  from the pillow: it glides in and bends over the bed
  {cam:(u,c)=>({pos:[-2.82,.98,-.5],look:lerp3([-1.7,1.9,-1.9],c.head,.55),fov:58,roll:.08}),wraith:u=>{const e=ease(u);return W(3,{x:L(P[3][0],P[4][0],e),z:L(P[3][1],P[4][1],e),lean:L(.3,.55,e),reach:L(.3,.8,e),open:L(.5,.95,e),headDown:.1*e,headTilt:L(.25,.4,e)});}},
  // 9  "Don't..."  the candle dies; only its eyes, right above him
  {cam:(u,c)=>({pos:lerp3([-2.75,1.0,-.62],[-2.72,1.04,-.66],u),look:c.head,fov:L(44,38,u),shake:.001}),wraith:u=>W(4,{lean:.6,reach:.9,open:.9,claw:.3,headDown:.18,headTilt:L(.4,.62,ease(u))})},
  // 10 "open your eyes."  it lunges into the lens; hard cut to black when the line ends
  {cam:(u,c)=>({pos:[-2.82,.98,-.5],look:lerp3([-2.2,1.8,-1.5],c.head,.85),fov:60,shake:.002+.012*easeIn(u)}),wraith:u=>{const e=easeIn(u);return W(4,{x:L(P[4][0],-2.62,e),z:L(P[4][1],-.92,e),y:L(0,-.55,e),lean:L(.6,1,e),reach:1,open:L(.9,1.1,e),claw:L(.3,1,e),headDown:L(.18,.32,e),headTilt:.62});}},
  // 11 black. two eyes open in the dark, then the loop
  {black:true},
 ];
 shots.forEach((s,i)=>{s.t0=cut[i];s.t1=cut[i+1];s.i=i;});
 return {shots,T,seg,words:ts.words.map(w=>({...w,start:w.start+OFF,end:w.end+OFF}))};
}

// candle: an uneven flame that gutters as it gets closer, and is snuffed on "Don't"
export function candle(t,T){const n=.62+.16*Math.sin(t*7.3)+.11*Math.sin(t*13.1+1.3)+.07*Math.sin(t*23.7+.4)+.05*Math.sin(t*41.9);
 const gutter=t>T.body&&t<T.trapped+.4?.55+.45*Math.abs(Math.sin(t*19)):1;
 const out=t<T.dont?1:Math.max(0,1-(t-T.dont)/.18);return Math.max(0,n*gutter*out);}
// the red eyes: dark until "corner", then they ignite with a stutter
export function eyes(t,T){if(t<T.corner)return 0;const u=(t-T.corner)/.45;if(u<1)return [0,1,.1,.9,.2,1][Math.floor(u*6)]*(.6+.4*u);return 1+.08*Math.sin(t*3.1)+(t>T.dont?.4:0);}
// heartbeat pulses (seconds between beats shorten as it closes in)
export function beats(T,dur){const out=[];let t=T.corner-.2,bpm=72;while(t<T.black){out.push(t);bpm=Math.min(150,bpm*1.045);t+=60/bpm;}return out;}
