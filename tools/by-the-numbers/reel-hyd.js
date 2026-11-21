// Hyderabad by the numbers (Telugu), v1. Sources in SOURCES-hyd.md.
const KOTI=v=>v.toFixed(2)+' కోట్లు', PCT=v=>Math.round(v)+'%', YR=v=>String(Math.round(v));
const N0=v=>Math.round(v).toLocaleString('en-IN'), TN=v=>Math.round(v)+' టన్నులు', CT=v=>v.toFixed(1);
window.REEL={
  theme:{landmark:'charminar',vehicle:'auto',tree:'round'},
  header:'హైదరాబాద్  •  నంబర్స్‌లో',
  scenes:[
    {type:'stat',dur:3.4,instant:true,tag:'#1  బిర్యానీ',col:'#ffd23f',from:1.4,to:1.75,fmt:KOTI,
     cap:['బిర్యానీలు. ఒక్క ఏడాదిలో.'],chip:'రోజుకి దాదాపు 48,000 ప్లేట్లు'},
    {type:'stat',dur:3.0,tag:'#2  మన వాటా',col:'#3ff0ff',from:5,to:18,fmt:PCT,
     cap:['దేశంలో ఆర్డర్ అయిన బిర్యానీల్లో','హైదరాబాద్ వాటా'],chip:'దాదాపు ప్రతి 6 బిర్యానీల్లో ఒకటి మనదే'},
    {type:'stat',dur:3.0,tag:'#3  చార్మినార్',col:'#ff5fc0',from:1500,to:1591,fmt:YR,
     cap:['చార్మినార్ కట్టిన సంవత్సరం'],chip:'435 ఏళ్లుగా అలాగే నిలబడి ఉంది'},
    {type:'stat',dur:3.0,tag:'#4  రామోజీ',col:'#ffd23f',from:900,to:1666,fmt:N0,
     cap:['ఎకరాల్లో రామోజీ ఫిల్మ్ సిటీ','ప్రపంచంలోనే అతిపెద్ద స్టూడియో'],chip:'Guinness World Record'},
    {type:'stat',dur:3.0,tag:'#5  బుద్ధుడు',col:'#3ff0ff',from:200,to:450,fmt:TN,
     cap:['హుస్సేన్ సాగర్ బుద్ధుడి బరువు','మొత్తం ఒకే రాయి'],chip:'18 మీటర్ల ఎత్తు'},
    {type:'stat',dur:3.0,tag:'#6  కోహినూర్',col:'#ff5fc0',from:60,to:105.6,fmt:CT,
     cap:['క్యారెట్ల కోహినూర్ వజ్రం','దొరికింది మన గోల్కొండ గనుల్లో'],chip:'ఇప్పుడు ఉన్నది లండన్‌లో'},
    {type:'stat',dur:3.2,tag:'#7  నిజాం',col:'#ffd23f',from:1900,to:1937,fmt:YR,
     cap:['TIME మ్యాగజైన్ మన నిజాంని','ప్రపంచ కుబేరుడు అంది'],chip:'ఏడవ నిజాం మీర్ ఉస్మాన్ అలీ ఖాన్'},
    {type:'cta',dur:3.4,lines:['మరిన్ని విషయాల కోసం'],sub:'విషయం ఏంటంటే ని సబ్‌స్క్రైబ్ చేయండి',btn:'SUBSCRIBE'}
  ]
};
