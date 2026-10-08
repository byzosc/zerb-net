// Record the zosc signature motion (lab/osc-logo/index.html) through headless chromium (CDP).
// 2026-10-08.
//
//   node lab/osc-logo/record.mjs all                    # GIF + storyboard + two final stills
//   node lab/osc-logo/record.mjs shots 160,650,1750     # quick stills while tuning (1600x900)
//        [--v white] [--debug] [--out DIR]
//   node lab/osc-logo/record.mjs reduced [--v white]    # what prefers-reduced-motion users get
//   node lab/osc-logo/record.mjs perf                   # JS cost of render(t) per phase
//
// Output goes to ~/render-tmp/osc/ (frames/, shots/, and the deliverables under out/):
//   out/osc-logo.gif            1200 wide, 30 ms per frame (= 33.3 fps, real time), t = -240 .. 6300
//   out/osc-storyboard.png      2400 wide, one frame per step, labelled with the step and time
//   out/osc-final-orange.png    1600x900 settled lockup, ?v=orange
//   out/osc-final-white.png     1600x900 settled lockup, ?v=white
// Delete ~/render-tmp/osc/ afterwards; nothing in it is needed again (rerun to regenerate).
//
// Why it is built this way:
// - Chromium here is a snap: it cannot read /tmp, dot-directories or (reliably) /data, so the
//   page is served over HTTP by this script, the browser profile lives in ~/render-tmp/osc/,
//   and every image is written by node from the CDP screenshot, not by chromium.
// - Frames are seeked, not filmed: the page renders a pure function of time and exposes
//   window.osc.seek(ms). Each frame = seek + two rAFs (so the SVG has been painted) + capture.
//   A 30 ms step with a 3-centisecond GIF delay plays back in exactly real time (GIF delays are
//   whole centiseconds, so 1/30 s cannot be represented).
// - The GIF is assembled by ImageMagick with one shared palette (taken from a strip of
//   representative frames) and no dithering: dithered glow changes every frame, which both
//   shimmers and bloats the file. MAGICK_TMPDIR points at /data (ImageMagick spills its pixel
//   cache to disk past 1 GiB and the system disk is small).

import { spawn, execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdirSync, readFileSync, rmSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(homedir(), 'render-tmp', 'osc');
const MAGICK_TMP = '/data/Projects/zerb-net/.render-tmp/osc-magick';

const args = process.argv.slice(2);
const opt = (flag, fallback) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args.splice(i, 2)[1] : fallback;
};
const flag = (f) => { const i = args.indexOf(f); if (i >= 0) { args.splice(i, 1); return true; } return false; };
const variant = opt('--v', 'orange');
const debug = flag('--debug');
const outDir = resolve(opt('--out', join(ROOT, 'shots')));
const mode = args[0] || 'all';

// ------------------------------------------------------------------ static server
const TYPES = { '.html': 'text/html; charset=utf-8', '.woff2': 'font/woff2', '.png': 'image/png', '.js': 'text/javascript' };
const extraPages = new Map();
const server = createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  if (extraPages.has(url.pathname)) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    return res.end(extraPages.get(url.pathname));
  }
  let file;
  if (url.pathname.startsWith('/rt/')) file = join(ROOT, decodeURIComponent(url.pathname.slice(4)));
  else file = join(HERE, decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname));
  if (!existsSync(file) || !statSync(file).isFile()) { res.writeHead(404); return res.end('404'); }
  res.writeHead(200, { 'content-type': TYPES[extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
  res.end(readFileSync(file));
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}`;

// ------------------------------------------------------------------ chromium + CDP
mkdirSync(ROOT, { recursive: true });
const chrome = spawn('chromium', [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
  '--no-default-browser-check', '--force-color-profile=srgb', '--font-render-hinting=none',
  `--user-data-dir=${join(ROOT, 'profile')}`, '--remote-debugging-port=0', 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });
const wsUrl = await new Promise((res, rej) => {
  let log = '';
  chrome.stderr.on('data', (d) => {
    log += d;
    const m = log.match(/DevTools listening on (ws:\/\/\S+)/);
    if (m) res(m[1]);
  });
  chrome.on('exit', (code) => rej(new Error(`chromium exited ${code}\n${log.slice(-800)}`)));
  setTimeout(() => rej(new Error(`no DevTools endpoint after 30s\n${log.slice(-800)}`)), 30000);
});
const ws = new WebSocket(wsUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let seq = 0;
const pending = new Map();
const waiters = [];
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { res, rej } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? rej(new Error(JSON.stringify(msg.error))) : res(msg.result);
  } else if (msg.method) {
    for (const w of [...waiters]) if (w.method === msg.method && w.sessionId === msg.sessionId) {
      waiters.splice(waiters.indexOf(w), 1);
      w.res(msg.params);
    }
  }
};
const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
  const id = ++seq;
  pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
});
const once = (method, sessionId, ms = 30000) => new Promise((res, rej) => {
  waiters.push({ method, sessionId, res });
  setTimeout(() => rej(new Error(`timeout waiting for ${method}`)), ms);
});

async function openPage(url, width, height) {
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false }, sessionId);
  const loaded = once('Page.loadEventFired', sessionId);
  await send('Page.navigate', { url }, sessionId);
  await loaded;
  const ev = (expression) => send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, sessionId)
    .then((r) => { if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 600)); return r.result.value; });
  await ev('document.fonts.ready.then(() => true)');
  const shot = async (file, clip) => {
    const { data } = await send('Page.captureScreenshot', { format: 'png', ...(clip ? { clip: { ...clip, scale: 1 } } : {}) }, sessionId);
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, Buffer.from(data, 'base64'));
  };
  const close = () => send('Target.closeTarget', { targetId });
  const resize = (w, h) => send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false }, sessionId);
  return { ev, shot, close, resize };
}
const frameReady = 'new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))';

async function stills(times, v, width, height, dir, prefix = 't') {
  const page = await openPage(`${BASE}/index.html?capture=1&v=${v}${debug ? '&debug=1' : ''}`, width, height);
  const files = [];
  for (const t of times) {
    await page.ev(`osc.seek(${t}); ${frameReady}`);
    const f = join(dir, `${prefix}${String(t).replace('-', 'm')}-${v}.png`);
    await page.shot(f);
    files.push(f);
  }
  await page.close();
  return files;
}

function magick(argv) {
  mkdirSync(MAGICK_TMP, { recursive: true });
  return execFileSync('convert', argv, { env: { ...process.env, MAGICK_TMPDIR: MAGICK_TMP }, stdio: ['ignore', 'pipe', 'inherit'] });
}

// ------------------------------------------------------------------ storyboard
const STEPS = [
  { t: 240, n: '01', zh: 'Z 放电', en: 'discharge' },
  { t: 760, n: '02', zh: '波形起振', en: 'start-up' },
  { t: 1180, n: '03', zh: '锁相', en: 'phase lock' },
  { t: 1810, n: '04', zh: '落成 o·s·c', en: 'the wave becomes the word' },
  { t: 2800, n: '05', zh: '心跳', en: 'heartbeat' },
];
function storyboardHtml(files) {
  const panels = STEPS.map((s, i) => `
    <figure>
      <div class="img" style="background-image:url('/rt/${files[i].slice(ROOT.length + 1)}')"></div>
      <figcaption><span class="n">${s.n}</span><span class="zh">${s.zh}</span><span class="t">${s.t} ms</span>
      <span class="en">${s.en}</span></figcaption>
    </figure>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  @font-face{font-family:"Montserrat";font-weight:100 900;src:url("/montserrat-latin.woff2") format("woff2")}
  html,body{margin:0;background:#050505}
  body{width:2400px;padding:56px 40px 48px;box-sizing:border-box;color:#f4f3ef;
    font-family:"Montserrat","Noto Sans CJK SC",sans-serif}
  h1{margin:0 0 6px;font-weight:800;font-size:30px;letter-spacing:-.01em}
  h1 em{font-style:normal;color:#e7503a}
  p.sub{margin:0 0 34px;font:500 17px/1.4 "Montserrat","Noto Sans CJK SC",sans-serif;color:rgba(244,243,239,.5)}
  .row{display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
  figure{margin:0}
  .img{aspect-ratio:16/9;background-color:#050505;background-repeat:no-repeat;
    background-size:142.86% auto;background-position:50% 50%;
    border:1px solid rgba(244,243,239,.1);border-radius:6px}
  figcaption{display:flex;align-items:baseline;flex-wrap:wrap;gap:10px;margin-top:16px}
  .n{font:700 15px/1 "Montserrat";color:#e7503a;letter-spacing:.06em}
  .zh{font:700 24px/1.1 "Noto Sans CJK SC","Montserrat",sans-serif}
  .t{margin-left:auto;font:600 15px/1 "Montserrat";color:rgba(244,243,239,.55);font-variant-numeric:tabular-nums}
  .en{flex-basis:100%;font:500 14px/1 "Montserrat";color:rgba(244,243,239,.42);letter-spacing:.08em;text-transform:uppercase}
  .arrow{color:rgba(244,243,239,.35)}
  </style></head><body>
  <h1>zosc <span class="arrow">—</span> Z + <em>osc</em></h1>
  <p class="sub">Z 放电 → 波形起振 → 锁相 → 落成 o·s·c → 心跳 · 每格是该步骤的一帧，时间为动画内的毫秒</p>
  <div class="row">${panels}</div></body></html>`;
}

// ------------------------------------------------------------------ main
try {
  if (mode === 'shots') {
    const times = (args[1] || '0,500,1000,1500,2000').split(',').map(Number);
    const files = await stills(times, variant, 1600, 900, outDir);
    console.log(files.join('\n'));
  } else if (mode === 'perf') {
    // JS cost of one render(t) per phase (paint/filter cost is not included)
    const page = await openPage(`${BASE}/index.html?capture=1`, 1600, 900);
    const r = await page.ev(`(() => { const out = {}; for (const [k, a, b] of [['z', 0, 340], ['trace', 345, 1530], ['morph', 1540, 2120], ['beat', 2550, 3450]]) {
      const t0 = performance.now(); let n = 0; for (let i = 0; i < 20; i++) for (let t = a; t < b; t += 16) { osc.render(t); n++; }
      out[k] = +((performance.now() - t0) / n).toFixed(3); } return out; })()`);
    await page.close();
    console.log('ms per render(t):', JSON.stringify(r));
  } else if (mode === 'reduced') {
    // prefers-reduced-motion: the page must draw the settled lockup at once (no capture flags)
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    await send('Page.enable', {}, sessionId);
    await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false }, sessionId);
    await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] }, sessionId);
    const loaded = once('Page.loadEventFired', sessionId);
    await send('Page.navigate', { url: `${BASE}/index.html?v=${variant}` }, sessionId);
    await loaded;
    await new Promise((r) => setTimeout(r, 400));
    const { data } = await send('Page.captureScreenshot', { format: 'png' }, sessionId);
    mkdirSync(outDir, { recursive: true });
    const f = join(outDir, `reduced-${variant}.png`);
    writeFileSync(f, Buffer.from(data, 'base64'));
    console.log(f);
  } else if (mode === 'all') {
    const out = join(ROOT, 'out');
    mkdirSync(out, { recursive: true });
    // 1. GIF frames, rendered straight at 1200x675
    const frames = join(ROOT, 'frames');
    rmSync(frames, { recursive: true, force: true });
    mkdirSync(frames, { recursive: true });
    const page = await openPage(`${BASE}/index.html?capture=1&v=${variant}`, 1200, 675);
    const T0 = -240, T1 = 6300, STEP = 30;
    let k = 0;
    for (let t = T0; t <= T1; t += STEP, k++) {
      await page.ev(`osc.seek(${t}); ${frameReady}`);
      await page.shot(join(frames, `f${String(k).padStart(4, '0')}.png`));
    }
    await page.close();
    console.log(`frames: ${k}`);
    // shared palette from a strip of representative frames, then remap without dithering
    const pick = [8, 12, 20, 30, 45, 52, 60, 70, 80, 90, 100, 120].map((i) => join(frames, `f${String(i).padStart(4, '0')}.png`)).filter(existsSync);
    const pal = join(ROOT, 'palette.png');
    magick([...pick, '-append', '+dither', '-colors', '96', '-unique-colors', pal]);
    const gif = join(out, 'osc-logo.gif');
    magick(['-delay', '3', '-loop', '0', join(frames, 'f*.png'), '+dither', '-remap', pal, '-layers', 'OptimizePlus', gif]);
    console.log(`gif: ${gif} ${(statSync(gif).size / 1048576).toFixed(2)} MB`);
    // 2. final stills
    for (const v of ['orange', 'white']) {
      const [f] = await stills([2300], v, 1600, 900, join(ROOT, 'stills'));
      execFileSync('cp', [f, join(out, `osc-final-${v}.png`)]);
    }
    // 3. storyboard: one 1600x900 frame per step, cropped to the lockup, labelled
    const sb = await stills(STEPS.map((s) => s.t), variant, 1600, 900, join(ROOT, 'storyboard'), 'sb');
    extraPages.set('/storyboard.html', storyboardHtml(sb));
    const page2 = await openPage(`${BASE}/storyboard.html`, 2400, 600);
    const h = await page2.ev('Math.ceil(document.body.getBoundingClientRect().height)');
    await page2.resize(2400, h);
    await page2.ev(frameReady);
    await page2.shot(join(out, 'osc-storyboard.png'), { x: 0, y: 0, width: 2400, height: h });
    await page2.close();
    console.log(`storyboard: 2400x${h}`);
    console.log(out);
  } else {
    throw new Error(`unknown mode ${mode}`);
  }
} finally {
  ws.close();
  chrome.kill();
  server.close();
}
