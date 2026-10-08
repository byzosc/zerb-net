// Layout probe + screenshots of built pages through headless chromium (CDP). v2 subtask C, 2026-10-08.
//
//   python3 -m http.server 4329 --bind 127.0.0.1 --directory app/dist/client &   # after `npm run build`
//   node tools/shoot-pages.mjs [--base http://127.0.0.1:4329] [--out ~/render-tmp/shots] \
//        [--resolve zosc.com=172.67.141.94] [--profile ~/render-tmp/chrome-profile-shoot] <shot> [<shot> ...]
//
//   <shot> = name:path:width[:flags]   flags joined with '+':
//            full     whole page (default: first viewport only)     clip=#id  just that element
//                                                                   clip=A..B from the top of A to the bottom of B
//            mobile   phone emulation (touch, coarse pointer, 844 tall; desktop is 900 tall)
//            dpr2     device scale factor 2                         jpeg      JPEG q82 instead of PNG
//            nosave   measure only, no image
//   e.g.  home-1440:/:1440:full+jpeg   home-390-code:/:390:mobile+dpr2+clip=#code   about-390:/about/:390:mobile+dpr2+full
//         code-1440:/:1440:clip=#products..#code   (selectors must not contain ':' or '+', the spec separators)
//
// Prints one JSON line per shot: document.title, scrollWidth vs clientWidth (documentElement and
// body), full scrollHeight, unclipped elements that stick out past the right edge, and every
// <main> <section> with its offset, height and the /project/<slug>/ cards inside it.
//
// Why it is built this way (each one cost a failed attempt somewhere in this repo):
// - `astro preview` is not supported by @astrojs/vercel, so serve app/dist/client statically —
//   the exact prerendered HTML that ships.
// - Chromium here is a snap: it cannot read /tmp or dot-directories (worktrees live under
//   .claude/). Its profile goes to ~/render-tmp/; pages arrive over HTTP; images are written by
//   node, not by chromium.
// - body has `overflow-x: hidden`, which can mask real overflow from a scrollWidth comparison
//   alone, so every element is also scanned for a right edge past the viewport (ignoring ones
//   inside a fixed or clipping ancestor, which cannot widen the page).
// - The site reveals cards with an IntersectionObserver and lazy-loads images, so a capture
//   without scrolling shows empty slots. prefers-reduced-motion is emulated (motion.ts then marks
//   every .reveal as shown, skips Lenis and the hero intro); the page is scrolled once top to
//   bottom so lazy images load; vh-sized boxes are pinned to pixels before a full-page capture
//   so the hero keeps its on-screen height; the custom cursor ball is hidden.
//   Animations are therefore NOT what these images show — they show layout only.
// - Production can be probed too: --resolve maps a host to an IP inside chromium (the local
//   resolver here sometimes fails on zosc.com).
// - --profile (v3-F, 2026-10-08): two runs sharing one chromium profile directory collide (profile
//   lock), so parallel sessions each pass their own. A clip taller than the viewport is captured
//   beyond it, which also grows the viewport, so vh boxes are pinned for clips as for full pages.

import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
const opt = (flag, fallback) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args.splice(i, 2)[1] : fallback;
};
const base = opt('--base', 'http://127.0.0.1:4329');
const out = opt('--out', join(homedir(), 'render-tmp', 'shots'));
const resolve = opt('--resolve', null);
const profile = opt('--profile', join(homedir(), 'render-tmp', 'chrome-profile-shoot'));
const shots = args.map((spec) => {
  const [name, path, width, flags = ''] = spec.split(':');
  const set = new Set(flags.split('+').filter(Boolean));
  const clip = [...set].find((f) => f.startsWith('clip='))?.slice(5);
  if (!name || !path || !Number(width)) throw new Error(`bad shot spec: ${spec}`);
  return {
    name, path, width: Number(width), clip,
    full: set.has('full'), mobile: set.has('mobile'), jpeg: set.has('jpeg'),
    dpr: set.has('dpr2') ? 2 : 1, save: !set.has('nosave'),
  };
});
if (!shots.length) throw new Error('no shots given — see the usage at the top of this file');
mkdirSync(out, { recursive: true });

const flags = [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
  '--no-default-browser-check', `--user-data-dir=${profile}`, '--remote-debugging-port=0',
];
if (resolve) {
  const [host, ip] = resolve.split('=');
  flags.push(`--host-resolver-rules=MAP ${host} ${ip}`);
}
const chrome = spawn('chromium', [...flags, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
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

const PROBE = `(() => {
  const de = document.documentElement, b = document.body, vw = de.clientWidth;
  const contained = (el) => {
    for (let p = el; p && p !== b && p !== de; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (cs.position === 'fixed') return true;
      if (p !== el && /hidden|clip|auto|scroll/.test(cs.overflowX)) return true;
    }
    return false;
  };
  const sticking = [];
  for (const el of b.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if ((r.width || r.height) && r.right > vw + 1 && !contained(el))
      sticking.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ' right=' + Math.round(r.right));
  }
  const sections = [...document.querySelectorAll('main section')].map((s) => {
    const r = s.getBoundingClientRect();
    return {
      id: s.id || '', top: Math.round(r.top + scrollY), height: Math.round(r.height),
      cards: [...s.querySelectorAll('a[href^="/project/"]')].map((a) => a.getAttribute('href').split('/')[2]),
    };
  });
  return {
    title: document.title, innerWidth,
    docScrollWidth: de.scrollWidth, docClientWidth: de.clientWidth,
    bodyScrollWidth: b.scrollWidth, bodyClientWidth: b.clientWidth,
    scrollHeight: de.scrollHeight, sticking: sticking.slice(0, 15), stickingCount: sticking.length,
    sections,
  };
})()`;

const SETTLE = `(async () => {
  await document.fonts.ready;
  const st = document.createElement('style');
  st.textContent = '#cursor{display:none!important}';
  document.head.appendChild(st);
  for (let y = 0; y < document.documentElement.scrollHeight; y += Math.round(innerHeight / 2)) {
    scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 60));
  }
  scrollTo(0, 0);
  await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
  await new Promise((r) => setTimeout(r, 400));
  return [...document.images].filter((i) => !i.naturalWidth).map((i) => i.getAttribute('src'));
})()`;

// Freeze vh-based heights before a full-page capture (the capture grows the viewport, which
// would stretch the min-h-screen hero to the whole page height). As of 2026-10-08 the only
// viewport-height boxes in app/src are `min-h-screen` (home hero, 404).
const PIN_VH = `(() => {
  const els = document.querySelectorAll('.min-h-screen, .h-screen');
  els.forEach((el) => { el.style.minHeight = el.getBoundingClientRect().height + 'px'; });
  return els.length;
})()`;

const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId: s } = await send('Target.attachToTarget', { targetId, flatten: true });
await send('Page.enable', {}, s);
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, s);
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 800));
  return r.result.value;
};

let failed = false;
try {
  for (const shot of shots) {
    const height = shot.mobile ? 844 : 900;
    await send('Emulation.setDeviceMetricsOverride', { width: shot.width, height, deviceScaleFactor: shot.dpr, mobile: shot.mobile }, s);
    await send('Emulation.setTouchEmulationEnabled', { enabled: shot.mobile, maxTouchPoints: shot.mobile ? 5 : 1 }, s);
    await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] }, s);
    const loaded = once('Page.loadEventFired', s);
    const url = new URL(shot.path, base).href;
    await send('Page.navigate', { url }, s);
    await loaded;
    const brokenImages = await evaluate(SETTLE);
    const probe = await evaluate(PROBE);
    let file = null;
    if (shot.save) {
      let clip;
      if (shot.clip) {
        await evaluate(PIN_VH);
        const [from, to = from] = shot.clip.split('..');
        const r = await evaluate(`(() => { const a = document.querySelector(${JSON.stringify(from)}), b = document.querySelector(${JSON.stringify(to)}); if (!a || !b) return null; const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect(); return { x: 0, y: ra.top + scrollY, width: document.documentElement.clientWidth, height: rb.bottom - ra.top }; })()`);
        if (!r) throw new Error(`${shot.name}: ${shot.clip} not found`);
        clip = { ...r, scale: 1 };
      } else if (shot.full) {
        await evaluate(PIN_VH);
        const { cssContentSize } = await send('Page.getLayoutMetrics', {}, s);
        clip = { x: 0, y: 0, width: cssContentSize.width, height: cssContentSize.height, scale: 1 };
      }
      const { data } = await send('Page.captureScreenshot', {
        format: shot.jpeg ? 'jpeg' : 'png', ...(shot.jpeg ? { quality: 82 } : {}),
        ...(clip ? { clip, captureBeyondViewport: true } : {}),
      }, s);
      file = join(out, `${shot.name}.${shot.jpeg ? 'jpg' : 'png'}`);
      writeFileSync(file, Buffer.from(data, 'base64'));
    }
    const overflow = probe.docScrollWidth > probe.docClientWidth || probe.bodyScrollWidth > probe.bodyClientWidth || probe.stickingCount > 0;
    if (overflow || brokenImages.length) failed = true;
    console.log(JSON.stringify({ shot: shot.name, url, overflow, brokenImages, ...probe, file }));
  }
} finally {
  ws.close();
  chrome.kill();
}
process.exit(failed ? 1 : 0);
