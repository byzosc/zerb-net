// A single geometry system for the four letters. No font outlines or stock Z mark.
// All positions are on the same 116-unit cap height, with a 20-unit stroke.
export const glyphs = [
  { name: 'z', start: [14,22], curves: [
    ['L',118,22], ['Q',125,22,120,28], ['L',19,132], ['Q',13,138,21,138], ['L',124,138],
  ] },
  { name: 'o', start: [220,22], curves: [
    ['C',255,22,278,46,278,80], ['C',278,114,255,138,220,138],
    ['C',185,138,162,114,162,80], ['C',162,46,185,22,220,22],
  ], closed: true },
  { name: 's', start: [429,22], curves: [
    ['L',366,22], ['C',344,22,329,34,329,51], ['C',329,68,344,80,366,80],
    ['L',393,80], ['C',415,80,430,92,430,109], ['C',430,126,415,138,393,138], ['L',330,138],
  ] },
  { name: 'c', start: [581,33], curves: [
    ['C',569,26,555,22,538,22], ['C',503,22,480,46,480,80],
    ['C',480,114,503,138,538,138], ['C',555,138,569,134,581,127],
  ] },
];

export const SVG_NS = 'http://www.w3.org/2000/svg';
export function svgMarkup(color='currentColor') {
  return `<svg xmlns="${SVG_NS}" viewBox="0 0 600 160" fill="none" stroke="${color}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="zosc">${glyphs.map(g=>`<path d="M ${g.start.join(' ')} ${g.curves.map(c=>c.join(' ')).join(' ')}${g.closed?' Z':''}"/>`).join('')}</svg>`;
}

// 1.04 seconds: smoothly enter, two damped oscillations, exact rest.
// One deformation field acts on the entire word, so glyphs remain one system.
export function render(svg,ms) {
  const t = ms/1000, active = t>0 && t<1.04;
  const amplitude = active ? 12*(1-Math.exp(-t*32))*Math.exp(-t*3.8)*Math.pow(Math.max(0,1-t/1.04),.65) : 0;
  const phase = t*2*Math.PI*2.2;
  const deform = ([x,y]) => {
    const signal = Math.sin(x/600*Math.PI*2-phase);
    return [x + amplitude*.13*Math.cos(x/600*Math.PI*2-phase),y+amplitude*signal];
  };
  const paths = svg.querySelectorAll('path');
  glyphs.forEach((glyph,i)=>{
    if (!active) {
      paths[i].setAttribute('d',`M ${glyph.start.join(' ')} ${glyph.curves.map(c=>c.join(' ')).join(' ')}${glyph.closed?' Z':''}`);
      return;
    }
    // Deform the Bezier controls directly: keep smooth curves and avoid the
    // subpixel stroke seams that a dense, rounded polyline produces in Chromium.
    const coord=p=>deform(p).map(n=>n.toFixed(3)).join(' ');
    const curves=glyph.curves.map(([kind,...p])=>{
      const coords=[];
      for(let k=0;k<p.length;k+=2) coords.push(coord([p[k],p[k+1]]));
      return `${kind} ${coords.join(' ')}`;
    });
    paths[i].setAttribute('d',`M ${coord(glyph.start)} ${curves.join(' ')}${glyph.closed?' Z':''}`);
  });
  return { active, amplitude };
}
