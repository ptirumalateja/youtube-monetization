// GTA 6 by the numbers, v4 (Teja's order, 21 Nov 2026). Every figure is sourced in SOURCES.md.
const B=v=>'$'+v.toFixed(2)+'B', M2=v=>v.toFixed(2)+'M', M0=v=>Math.round(v)+'M';
const P=v=>'+'+Math.round(v)+'%', USD=v=>'$'+Math.round(v).toLocaleString('en-US');
window.REEL={
  header:'GTA 6  •  BY THE NUMBERS',
  scenes:[
    {type:'title',dur:2.0,big:'GTA 6',lines:['JUST BROKE','THE INTERNET'],small:'6 numbers that prove it'},
    {type:'stat',dur:3.2,tag:'#1  PRE-ORDERS',col:'#3ff0ff',from:20,to:32.5,fmt:v=>v.toFixed(1)+'M',
     cap:['COPIES SOLD BEFORE','THE GAME EVEN LAUNCHED'],chip:'New all-time record (Rockstar)'},
    {type:'vs',dur:3.8,tag:'#2  LAUNCH DAY',col:'#ffd23f',title:'DAY ONE: GTA 5 vs GTA 6',fmt:B,
     a:{label:'GTA 5 (2013)',v:0.8,sub:'first-day sales'},
     b:{label:'GTA 6 (2026)',v:3.79,sub:'first-day sales'},chip:'Nearly 5x bigger'},
    {type:'stat',dur:3.4,tag:'#3  STREAMS',col:'#ff5fc0',from:60,to:125,fmt:M0,
     cap:['HOURS OF GTA 6 STREAMS','WATCHED IN 24 HOURS'],chip:'7.9M watching at the same time'},
    {type:'stat',dur:3.0,tag:'#4  INDIA',col:'#ffd23f',from:10,to:60,fmt:P,
     cap:['MORE INDIANS TOOK LEAVE','ON LAUNCH DAY'],chip:'Worldwide: +32%'},
    {type:'stat',dur:3.2,tag:'#5  ISHOWSPEED',col:'#3ff0ff',from:2,to:4.47,fmt:M2,
     cap:["HOURS OF ISHOWSPEED'S GTA 6","STREAM WATCHED. MOST OF ANYONE."],chip:'Clippers paid $1 per 1,000 views'},
    {type:'stat',dur:3.2,tag:'#6  DREAM JOB',col:'#ff5fc0',from:90000,to:120000,fmt:USD,
     cap:['KALSHI HIRED ONE PERSON','TO PLAY GTA 6 FOR A YEAR'],chip:'≈ ₹1 crore. To play a game.'},
    {type:'cta',dur:3.4,lines:['WHICH NUMBER','SHOCKED YOU?'],sub:'Drop it in the comments',btn:'FOLLOW FOR MORE'}
  ]
};
