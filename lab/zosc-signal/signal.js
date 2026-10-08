// Oscillator study 03: an actual periodic signal becomes the letter strokes.
// The O retains a circle-and-sine cue for a periodic signal source.
export const duration=2520;
const ns='http://www.w3.org/2000/svg';
const PI=Math.PI;
const clamp=n=>Math.max(0,Math.min(1,n));
const ease=n=>{n=clamp(n);return n*n*(3-2*n)};
const mix=(a,b,t)=>a+(b-a)*t;
const paths=[
  'M 176 120 C 176 84.654 204.654 56 240 56 C 275.346 56 304 84.654 304 120 C 304 155.346 275.346 184 240 184 C 204.654 184 176 155.346 176 120',
  'M 432 65 L 378 65 C 354 65 338 76 338 94 C 338 111 355 120 378 120 L 403 120 C 426 120 444 129 444 147 C 444 165 428 175 404 175 L 349 175',
  'M 594 70 C 581 61 566 56 550 56 C 514.654 56 486 84.654 486 120 C 486 155.346 514.654 184 550 184 C 566 184 581 179 594 170',
];
const sine='M 204 120 C 210 120 214 108 222 108 C 230 108 233 120 240 120 C 247 120 250 132 258 132 C 266 132 270 120 276 120';
export function svgMarkup(color='currentColor'){
  return `<svg xmlns="${ns}" viewBox="0 0 624 240" role="img" aria-label="zosc — z · oscillator"><g fill="none" stroke="${color}" stroke-width="13" stroke-linecap="butt" stroke-linejoin="round"><path data-z d="M 22 62 L 128 62 L 22 178 L 132 178"/>${paths.map(d=>`<path data-letter d="${d}"/>`).join('')}<path data-sine d="${sine}" stroke="#e7503a" stroke-width="5.5" stroke-linecap="round"/></g></svg>`;
}
const cache=new WeakMap();
function setup(svg){
  if(cache.has(svg))return cache.get(svg);
  const letters=[...svg.querySelectorAll('[data-letter]')];
  const targets=letters.map((p,index)=>{
    p.setAttribute('d',paths[index]);const len=p.getTotalLength();
    return Array.from({length:161},(_,i)=>{
      const fraction=index===0?1-i/160:i/160;
      const pt=p.getPointAtLength(len*fraction);return [pt.x,pt.y];
    });
  });
  const result={letters,targets,sine:svg.querySelector('[data-sine]')};
  cache.set(svg,result);return result;
}
// Smooth Bezier reconstruction avoids seams from densely joined SVG lines.
const tracePath=points=>{
  const knots=points.filter((_,i)=>i%4===0);
  const fmt=p=>p.map(v=>v.toFixed(3)).join(' ');
  let d=`M ${fmt(knots[0])}`;
  for(let i=0;i<knots.length-1;i++){
    const p0=knots[Math.max(0,i-1)],p1=knots[i],p2=knots[i+1],p3=knots[Math.min(knots.length-1,i+2)];
    const a=p1.map((v,k)=>v+(p2[k]-p0[k])/6),b=p2.map((v,k)=>v-(p3[k]-p1[k])/6);
    d+=` C ${fmt(a)} ${fmt(b)} ${fmt(p2)}`;
  }
  return d;
};
export function render(svg,ms){
  const {letters,targets,sine:core}=setup(svg);
  const t=Math.max(0,ms);
  // 420 units = 2.5 periods; each segment is part of the same sine.
  const sourceRanges=[[176,344],[344,512],[512,596]];
  const startTimes=[1380,1500,1620];
  const phase=t<1200?(1-ease(t/1200))*PI*2.7:0;
  const amplitude=60*ease(t/400);
  let final=true;
  letters.forEach((path,k)=>{
    const progress=clamp((t-startTimes[k])/780);
    const amount=k===0?ease(progress):ease((progress-.45)/.55);
    const [left,right]=sourceRanges[k];
    const periods=k===2?.5:1;
    if(amount===1){path.setAttribute('d',paths[k]);path.setAttribute('stroke','currentColor');return}
    final=false;
    const pivot=[(left+right)/2,120];
    const turn=k===0?0:ease(progress/.55);
    const rotation=PI/2*turn;
    const points=targets[k].map((target,i)=>{
      const u=i/160;
      let x=mix(left,right,u),y=120+amplitude*Math.sin(u*periods*2*PI-phase);
      // S and C stand the sine upright before adopting the final curve.
      const scale=k===1?mix(1,.66,turn):1;
      const dx=(x-pivot[0])*scale,dy=(y-pivot[1])*scale;
      const center=k===1?mix(pivot[0],391,turn):k===2?mix(pivot[0],550,turn):pivot[0];
      x=center+dx*Math.cos(rotation)-dy*Math.sin(rotation);
      y=pivot[1]+dx*Math.sin(rotation)+dy*Math.cos(rotation);
      return [mix(x,target[0],amount),mix(y,target[1],amount)];
    });
    path.setAttribute('d',tracePath(points));
    const ink=ease((amount-.58)/.42);
    path.setAttribute('stroke',`rgb(${mix(231,244,ink).toFixed(0)} ${mix(80,243,ink).toFixed(0)} ${mix(58,239,ink).toFixed(0)})`);
  });
  // One uninterrupted stroke before splitting into letter arcs.
  if(t<=1380){
    letters[0].setAttribute('d',letters.map((p,i)=>i?p.getAttribute('d').replace(/^M/,'L'):p.getAttribute('d')).join(' '));
    letters[1].setAttribute('d','');letters[2].setAttribute('d','');
  }
  // The source still lives inside O after the outer signal has become type.
  const reveal=ease((t-1980)/540);
  core.setAttribute('stroke-dasharray','90');core.setAttribute('stroke-dashoffset',(90*(1-reveal)).toFixed(3));
  return {final,phase,amplitude,reveal};
}
