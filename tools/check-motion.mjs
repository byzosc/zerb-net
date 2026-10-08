// Motion-ON checks of the built site through headless chromium (CDP). v2 subtask E, 2026-10-08.
//
//   python3 -m http.server 4329 --bind 127.0.0.1 --directory app/dist/client &   # after `npm run build`
//   node tools/check-motion.mjs [--base http://127.0.0.1:4329] [--out ~/render-tmp/motion]
//
// tools/shoot-pages.mjs emulates prefers-reduced-motion, so its images show layout only. This one
// does NOT: motion.ts runs for real (hero intro, Lenis, the cross-page #hash landing). Exit 1 on
// any failure.
//   1. Hero intro (1440x900): an in-page requestAnimationFrame sampler records every frame for
//      4.5 s. motion.ts binds the effects to line POSITIONS, so the trace must show line 1 = mask
//      wipe (--mx 100% -> 0%), line 2 = blur (blur(18px) -> 0), line 3 = typewriter (.ch spans
//      appear one by one), starting in that order; <html> gets .intro-ready before the 3.5 s
//      .hero-fallback timer; every line ends opaque, unblurred, unmasked, with its word. Three
//      frames mid-intro + the final state are saved as hero-1..3.png / hero-final.png.
//   2. Anchors (real mouse clicks): the desktop header nav Code / Motion / Visual on the homepage
//      (same page: the section must sit at 96 +- 24 px, html's scroll-padding-top) and "← Back to
//      work" from one project page per pillar (cross-page: URL hash + that section at the top of
//      the viewport; the exact offset of the cross-page landing varies, see the note below).
//   The hero has no links of its own (its dots only change the cursor label); nothing to click.
//
// Same constraints as shoot-pages.mjs: chromium is a snap (no /tmp, no dot-directories), so its
// profile lives in ~/render-tmp/chrome-profile-motion (deleted at exit); node writes the images.

import { spawn } from 'node:child_process';
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
const opt = (flag, fallback) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args.splice(i, 2)[1] : fallback;
};
const base = opt('--base', 'http://127.0.0.1:4329');
const out = opt('--out', join(homedir(), 'render-tmp', 'motion'));
mkdirSync(out, { recursive: true });

const profile = join(homedir(), 'render-tmp', 'chrome-profile-motion');
const chrome = spawn('chromium', [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
  '--no-default-browser-check', `--user-data-dir=${profile}`, '--remote-debugging-port=0', 'about:blank',
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
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId: s } = await send('Target.attachToTarget', { targetId, flatten: true });
await send('Page.enable', {}, s);
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false }, s);
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, s);
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 800));
  return r.result.value;
};
const goto = async (path) => {
  const loaded = once('Page.loadEventFired', s);
  await send('Page.navigate', { url: new URL(path, base).href }, s);
  await loaded;
};
const click = async (selectorJs) => {
  const c = await evaluate(`(() => { const e = ${selectorJs}; if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
  if (!c) throw new Error(`nothing to click: ${selectorJs}`);
  for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased'])
    await send('Input.dispatchMouseEvent', { type, x: c.x, y: c.y, button: 'left', clickCount: 1 }, s);
};

const failures = [];
const check = (cond, okMsg, failMsg) => {
  console.log(cond ? `  ok   ${okMsg}` : `  FAIL ${failMsg}`);
  if (!cond) failures.push(failMsg);
};

// Records the three hero lines every animation frame, from document creation for 4.5 s.
const SAMPLER = `(() => {
  const trace = (window.__heroTrace = []);
  const sample = () => {
    const lines = [...document.querySelectorAll('[data-hero] h1 .hl')];
    if (lines.length) trace.push({
      t: Math.round(performance.now()),
      ready: document.documentElement.classList.contains('intro-ready'),
      fallback: document.documentElement.classList.contains('hero-fallback'),
      lines: lines.map((l) => {
        const t = l.querySelector('.hl-t'), cs = getComputedStyle(t), d = l.querySelector('.hero-dot-m');
        const chars = [...t.querySelectorAll('.ch')];
        return {
          text: t.textContent, fx: ['mask', 'blur', 'type'].find((k) => t.hasAttribute('data-' + k)),
          dot: l.querySelector('.hero-dot')?.dataset.dot, op: +cs.opacity, filter: cs.filter,
          mask: cs.webkitMaskImage || cs.maskImage, mx: cs.getPropertyValue('--mx').trim(),
          chars: chars.length, shown: chars.filter((c) => +getComputedStyle(c).opacity > 0.5).length,
          dotOp: d ? +getComputedStyle(d).opacity : null,
        };
      }),
    });
    if (performance.now() < 4500) requestAnimationFrame(sample);
  };
  requestAnimationFrame(sample);
})()`;

try {
  console.log('1. hero intro (motion on, 1440x900)');
  const { identifier } = await send('Page.addScriptToEvaluateOnNewDocument', { source: SAMPLER }, s);
  // Two loads: a capture stalls the renderer for ~100-250 ms, so the trace comes from a load
  // without captures and the frames from a second one.
  const introStart = async () => {
    await send('Page.navigate', { url: new URL('/', base).href }, s);
    // The intro starts when motion.ts runs; line 3's text is split into .ch spans at that moment.
    for (let i = 0; i < 300; i++) {
      const t = await evaluate(`(() => { const t = (window.__heroTrace || []).find((x) => x.lines[2] && x.lines[2].chars > 0); return t ? t.t : null; })()`).catch(() => null);
      if (t !== null) return t;
      await sleep(15);
    }
    throw new Error('hero intro never started (no .ch spans on line 3)');
  };
  const start = await introStart();
  await sleep(Math.max(0, start + 4600 - (await evaluate('performance.now()'))));
  const trace = await evaluate('window.__heroTrace');
  const frameStart = await introStart();
  const box = await evaluate(`(() => { const r = document.querySelector('[data-hero] h1').getBoundingClientRect(); return { x: Math.max(0, r.left - 24), y: Math.max(0, r.top - 24), width: r.width + 48, height: r.height + 48 }; })()`);
  const frames = [];
  for (const [name, at] of [['hero-1', 300], ['hero-2', 700], ['hero-3', 1150], ['hero-final', 2600]]) {
    while ((await evaluate('performance.now()')) < frameStart + at) await sleep(5);
    const t = Math.round((await evaluate('performance.now()')) - frameStart);
    const { data } = await send('Page.captureScreenshot', { format: 'png', clip: { ...box, scale: 1 } }, s);
    writeFileSync(join(out, `${name}.png`), Buffer.from(data, 'base64'));
    frames.push(`${name}.png @${t}ms`);
  }
  await send('Page.removeScriptToEvaluateOnNewDocument', { identifier }, s);
  console.log(`       frames (ms after intro start): ${frames.join(', ')}  in ${out}`);

  const last = trace[trace.length - 1].lines;
  const during = trace.filter((x) => x.t >= start && !x.ready);
  const rel = (x) => (x ? x.t - start : null);
  check(last.map((l) => l.text).join(' / ') === 'Code / Motion / Visual', `words: ${last.map((l) => l.text).join(' / ')}`,
    `hero words ${last.map((l) => l.text).join(' / ')}`);
  check(last.map((l) => l.fx).join() === 'mask,blur,type', 'effect markers by line: mask, blur, type',
    `effect markers ${last.map((l) => l.fx)}`);
  check(last.map((l) => l.dot).join() === 'code,motion,visual', 'dots follow the words: code, motion, visual',
    `dots ${last.map((l) => l.dot)}`);
  const maskMid = during.find((x) => /^([1-9]\d?(\.\d+)?)%$/.test(x.lines[0].mx) && x.lines[0].mask !== 'none');
  const blurMid = during.find((x) => { const b = +(x.lines[1].filter.match(/blur\(([\d.]+)px\)/) || [])[1]; return b > 0.5 && b < 17.5; });
  const shownSeq = during.map((x) => x.lines[2].shown);
  const typedSteps = new Set(shownSeq.filter((n) => n > 0 && n < last[2].chars)).size;
  const monotonic = shownSeq.every((n, i) => i === 0 || n >= shownSeq[i - 1]);
  check(!!maskMid, `line 1 "${last[0].text}": mask wipe seen mid-way (--mx ${maskMid?.lines[0].mx} at ${rel(maskMid)} ms)`,
    'line 1: no intermediate mask position recorded');
  check(!!blurMid, `line 2 "${last[1].text}": blur resolving seen mid-way (${blurMid?.lines[1].filter} at ${rel(blurMid)} ms)`,
    'line 2: no intermediate blur recorded');
  check(last[2].chars === last[2].text.length && typedSteps >= last[2].chars - 2 && monotonic,
    `line 3 "${last[2].text}": typewriter, ${last[2].chars} chars appear one by one (${typedSteps} partial states, never backwards)`,
    `line 3: chars ${last[2].chars}, partial states ${typedSteps}, monotonic ${monotonic}`);
  const tMask = rel(during.find((x) => x.lines[0].mx && x.lines[0].mx !== '100%'));
  const tBlur = rel(during.find((x) => x.lines[1].op > 0.02));
  const tType = rel(during.find((x) => x.lines[2].shown > 0));
  check(tMask !== null && tBlur !== null && tType !== null && tMask < tBlur && tBlur < tType,
    `lines start in order: 1 @${tMask} ms, 2 @${tBlur} ms, 3 @${tType} ms (motion.ts: 0 / 450 / 900)`,
    `start order 1 @${tMask}, 2 @${tBlur}, 3 @${tType}`);
  const ready = trace.find((x) => x.ready);
  check(!!ready && !trace.some((x) => x.fallback), `intro-ready at ${rel(ready)} ms after start; .hero-fallback never set`,
    `intro-ready ${ready ? rel(ready) : 'never'}; fallback ${trace.some((x) => x.fallback)}`);
  const settled = last.every((l) => l.op === 1 && l.filter === 'none' && l.mask === 'none' && l.dotOp === 1)
    && last[2].shown === last[2].chars;
  check(settled, 'final: all three lines opaque, unblurred, unmasked; all chars and dots visible',
    `final state ${JSON.stringify(last)}`);

  console.log('2. anchors (real clicks, motion on)');
  const landed = (id) => evaluate(`(() => {
    const secs = [...document.querySelectorAll('main section[id]')].map((e) => ({ id: e.id, top: Math.round(e.getBoundingClientRect().top) }));
    const atTop = secs.filter((x) => x.top <= 200).pop();
    return { path: location.pathname, hash: location.hash, top: secs.find((x) => x.id === ${JSON.stringify(id)})?.top ?? null, atTop: atTop?.id ?? null };
  })()`);
  for (const id of ['code', 'motion', 'visual']) {
    await goto('/');
    await sleep(2200); // let the hero intro and Lenis settle
    await click(`document.querySelector('#masthead nav a[href="/#${id}"]')`);
    await sleep(2200);
    const r = await landed(id);
    check(r.hash === `#${id}` && r.atTop === id && Math.abs(r.top - 96) <= 24,
      `header nav "${id}": ${r.path}${r.hash}, #${id} top ${r.top}px`, `header nav ${id}: ${JSON.stringify(r)}`);
  }
  for (const [slug, id] of [['cubby', 'code'], ['vivo-xr', 'motion'], ['dynamic-weather-art', 'visual']]) {
    await goto(`/project/${slug}/`);
    await sleep(800);
    await click(`[...document.querySelectorAll('main a')].find((a) => a.textContent.includes('Back to work'))`);
    await sleep(2500);
    const r = await landed(id);
    // Cross-page landing (motion.ts: lenis.scrollTo(el, { offset: -96 }) 120 ms after page-load)
    // varies run to run — 29 to 160 px measured 2026-10-08, the header nav from a project page
    // too, i.e. not specific to this link — so only "this section is the one at the top" is checked.
    check(r.path === '/' && r.hash === `#${id}` && r.atTop === id && r.top >= 0 && r.top <= 200,
      `/project/${slug}/ "← Back to work": ${r.path}${r.hash}, #${id} at the top (${r.top}px)`, `back from ${slug}: ${JSON.stringify(r)}`);
  }
} finally {
  ws.close();
  chrome.kill();
  await sleep(500);
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
console.log(`\n${failures.length ? `${failures.length} FAILURE(S)` : 'OK'}`);
process.exit(failures.length ? 1 : 0);
