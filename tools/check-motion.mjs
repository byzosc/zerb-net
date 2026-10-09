// Motion-ON checks of the built site through headless chromium (CDP). v2 subtask E, 2026-10-08.
//
//   python3 -m http.server 4329 --bind 127.0.0.1 --directory app/dist/client &   # after `npm run build`
//   node tools/check-motion.mjs [--base http://127.0.0.1:4329] [--out ~/render-tmp/motion] \
//        [--profile ~/render-tmp/chrome-profile-motion]
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
//      v3-F (2026-10-08): the hero buttons ([data-hero-cta]) fade in after the headline, opacity
//      only — while visible they never move (AGENTS.md: a link that moves can lose the click).
//   2. Anchors (real mouse clicks): the desktop header nav Code / Motion / Visual on the homepage
//      (same page: the section must sit at 96 +- 24 px, html's scroll-padding-top) and "← Back to
//      work" from one project page per pillar (cross-page: URL hash + that section at the top of
//      the viewport; the exact offset of the cross-page landing varies, see the note below).
//   The hero has no links of its own (its dots only change the cursor label); nothing to click.
//   3. v3-G (2026-10-08) Code cards: each carries a row of direct links right after the card's <a>
//      (components/CardLinks.astro). a) Frames while the header nav scrolls #code in: the large
//      card's row fades in with the card's reveal and never moves (its document position is one
//      point in every frame). b) Real clicks: a direct link (Adobe Exchange on the large card,
//      Google Play on the Cubby card) opens a NEW tab — no opener access (rel=noopener) — and the
//      homepage stays where it is; the card itself (large: MotionPilot, small: Cubby) opens its
//      product page.
//
// Same constraints as shoot-pages.mjs: chromium is a snap (no /tmp, no dot-directories), so its
// profile lives in ~/render-tmp/chrome-profile-motion (deleted at exit); node writes the images.
// --profile (v3-F, 2026-10-08): the profile is deleted at exit, so a run that shares the default
// path with another session would delete that session's live profile — give each run its own.

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

const profile = opt('--profile', join(homedir(), 'render-tmp', 'chrome-profile-motion'));
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
const targets = new Map(); // targetId -> latest TargetInfo (Target.setDiscoverTargets, section 3)
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.method === 'Target.targetCreated' || msg.method === 'Target.targetInfoChanged') {
    const info = msg.params.targetInfo;
    targets.set(info.targetId, { ...targets.get(info.targetId), ...info,
      urls: [...(targets.get(info.targetId)?.urls ?? []), info.url].filter((u, i, a) => u && a.indexOf(u) === i) });
  }
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
const HERO_WORDS = ['Motion', 'Visual', 'Code']; // line 1, 2, 3 (user decision 2026-10-08, see below)

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
      cta: (() => {
        const c = document.querySelector('[data-hero-cta]'), a = c && c.querySelector('a');
        if (!a) return null;
        const r = a.getBoundingClientRect();
        return { op: +getComputedStyle(c).opacity, x: Math.round(r.left * 10) / 10, y: Math.round((r.top + scrollY) * 10) / 10 };
      })(),
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
  // Hero words = Motion / Visual / Code: the user reverted the hero to its original cadence the same
  // day (a3d7400, 2026-10-08) while the sections stay Code-first; this line still expected the v2-E
  // order and failed on an unchanged tree. Same order as HERO_ORDER in tools/check-home.py.
  check(last.map((l) => l.text).join(' / ') === HERO_WORDS.join(' / '), `words: ${last.map((l) => l.text).join(' / ')}`,
    `hero words ${last.map((l) => l.text).join(' / ')}, expected ${HERO_WORDS.join(' / ')}`);
  check(last.map((l) => l.fx).join() === 'mask,blur,type', 'effect markers by line: mask, blur, type',
    `effect markers ${last.map((l) => l.fx)}`);
  check(last.map((l) => l.dot).join() === HERO_WORDS.map((w) => w.toLowerCase()).join(),
    `dots follow the words: ${last.map((l) => l.dot).join(', ')}`, `dots ${last.map((l) => l.dot)}`);
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
  const ctaSeen = trace.filter((x) => x.cta && x.cta.op > 0.01);
  const ctaPos = new Set(ctaSeen.map((x) => `${x.cta.x},${x.cta.y}`));
  const ctaMid = ctaSeen.find((x) => x.cta.op < 0.99);
  const ctaLast = trace[trace.length - 1].cta;
  check(ctaSeen.length > 0 && !!ctaMid && ctaLast?.op === 1 && ctaPos.size === 1 && rel(ctaSeen[0]) > (tType ?? 0),
    `hero buttons: fade in from ${rel(ctaSeen[0])} ms (after line 3), opacity ${ctaMid?.cta.op.toFixed(2)} mid-way, end 1; `
      + `position fixed at ${[...ctaPos][0]} across ${ctaSeen.length} visible frames`,
    `hero buttons: ${ctaSeen.length} visible frames, mid ${!!ctaMid}, end ${ctaLast?.op}, positions ${[...ctaPos].join(' | ')}`);

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

  console.log('3. Code cards (v3-G): direct-link rows, real clicks, motion on');
  await send('Target.setDiscoverTargets', { discover: true });
  const toCode = async () => {
    await goto('/');
    await sleep(2200);
    await click(`document.querySelector('#masthead nav a[href="/#code"]')`);
  };
  const linkJs = (label) => `[...document.querySelectorAll('#code .card-links a')].find((a) => a.textContent.includes(${JSON.stringify(label)}))`;
  // a) 1440x900: #code starts below the fold, so the nav click scrolls the large card in and reveals
  //    it while this sampler (started just before the click) records its row every frame.
  await goto('/');
  await sleep(2200);
  await evaluate(`(() => {
    const row = document.querySelector('#code .card-links'), card = row && row.previousElementSibling;
    const trace = (window.__rowTrace = []), t0 = performance.now();
    const sample = () => {
      const r = row.getBoundingClientRect();
      trace.push({ t: Math.round(performance.now() - t0), op: +getComputedStyle(row).opacity, cardOp: +getComputedStyle(card).opacity,
        pos: Math.round(r.left) + ',' + Math.round(r.top + scrollY), inView: r.top < innerHeight && r.bottom > 0 });
      if (performance.now() - t0 < 3000) requestAnimationFrame(sample);
    };
    requestAnimationFrame(sample);
  })()`);
  await click(`document.querySelector('#masthead nav a[href="/#code"]')`);
  await sleep(3200);
  const rowTrace = await evaluate('window.__rowTrace');
  const firstSeen = (key, v) => rowTrace.find((x) => x[key] > v)?.t ?? null;
  const rowPos = new Set(rowTrace.map((x) => x.pos));
  const rowMid = rowTrace.find((x) => x.op > 0.01 && x.op < 0.99);
  const [rowIn, cardIn] = [firstSeen('op', 0.01), firstSeen('cardOp', 0.01)];
  check(rowTrace[0]?.op === 0 && !!rowMid && rowTrace[rowTrace.length - 1].op === 1 && rowPos.size === 1
      && rowIn !== null && cardIn !== null && Math.abs(rowIn - cardIn) <= 100,
    `large card row: hidden until its card reveals, fades in with it (row from ${rowIn} ms, card from ${cardIn} ms, `
      + `opacity ${rowMid?.op.toFixed(2)} mid-way, end 1); document position ${[...rowPos][0]} in all ${rowTrace.length} frames`,
    `large card row: start ${rowTrace[0]?.op}, mid ${!!rowMid}, end ${rowTrace[rowTrace.length - 1]?.op}, row in ${rowIn} / card in ${cardIn} ms, positions ${[...rowPos].join(' | ')}`);
  // b) real clicks. A direct link: a new tab on its store, no opener access, the homepage stays put.
  //    The card: its product page. 1440x1700 for the small cards, so all of #code is in view.
  for (const [height, slug, label, host] of [[900, 'motionpilot', 'Adobe Exchange', 'exchange.adobe.com'], [1700, 'cubby', 'Google Play', 'play.google.com']]) {
    await send('Emulation.setDeviceMetricsOverride', { width: 1440, height, deviceScaleFactor: 1, mobile: false }, s);
    await toCode();
    await sleep(2200);
    const mark = await evaluate('(window.__stay = Math.random())');
    const known = new Set(targets.keys());
    await click(linkJs(label));
    let tab = null;
    for (let i = 0; i < 40 && !tab; i++) {
      await sleep(250);
      tab = [...targets.values()].find((t) => !known.has(t.targetId) && t.type === 'page' && t.urls.some((u) => new URL(u, 'about:blank').host === host)) ?? null;
    }
    const here = await evaluate(`({ at: location.pathname + location.hash, same: window.__stay === ${mark} })`);
    check(!!tab && tab.canAccessOpener === false && here.same && here.at === '/#code',
      `"${label} ↗" (${slug}): new tab ${tab?.urls.join(' -> ')}, opener access ${tab?.canAccessOpener}; homepage stays at ${here.at}, not reloaded`,
      `"${label} ↗": tab ${JSON.stringify(tab)}, homepage ${JSON.stringify(here)}`);
    if (tab) await send('Target.closeTarget', { targetId: tab.targetId }).catch(() => {});
    await goto('/');
    await sleep(2200);
    await click(`document.querySelector('#masthead nav a[href="/#code"]')`);
    await sleep(2200);
    await click(`document.querySelector('#code a[href="/project/${slug}/"]')`);
    await sleep(2000);
    const page = await evaluate(`({ path: location.pathname, h1: document.querySelector('main h1')?.textContent.trim() })`);
    check(page.path === `/project/${slug}/`, `${slug} card: opens ${page.path} ("${page.h1}")`, `${slug} card: at ${JSON.stringify(page)}`);
  }
} finally {
  ws.close();
  chrome.kill();
  await sleep(500);
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
console.log(`\n${failures.length ? `${failures.length} FAILURE(S)` : 'OK'}`);
process.exit(failures.length ? 1 : 0);
