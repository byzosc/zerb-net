// Repeat one cross-page anchor jump N times and record where the section lands (v3-F, 2026-10-08).
//
//   python3 -m http.server <port> --bind 127.0.0.1 --directory app/dist/client &   # after `npm run build`
//   node tools/probe-anchor-landing.mjs [--base http://127.0.0.1:4329] [--from /project/cubby/] \
//        [--id code] [--runs 12] [--profile ~/render-tmp/chrome-profile-anchor]
//
// Why: tools/check-motion.mjs clicks "← Back to work" once per pillar and only checks that the
// section ends up "at the top" (0–200 px). The landing offset is known to float (docs/DONE.md
// 2026-10-08: 21–160 px, cause unknown) and now and then lands ABOVE the viewport top, i.e. the
// section heading hides under the fixed header. One run can't tell whether a change made that
// better or worse; this repeats the same real click N times and prints the distribution, plus the
// scroll trace (every 50 ms for 2.5 s after the click) of the worst run, so the timing of the jump
// can be read off directly.
//
// Same chromium constraints as shoot-pages.mjs / check-motion.mjs (snap: no /tmp, no dot-dirs; the
// profile directory is deleted at exit, so pass your own --profile when sessions run in parallel).
// Exit code 0 always: this measures, it does not judge.

import { spawn } from 'node:child_process';
import { rmSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
const opt = (flag, fallback) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args.splice(i, 2)[1] : fallback;
};
const base = opt('--base', 'http://127.0.0.1:4329');
const from = opt('--from', '/project/cubby/');
const id = opt('--id', 'code');
const runs = Number(opt('--runs', '12'));
const profile = opt('--profile', join(homedir(), 'render-tmp', 'chrome-profile-anchor'));

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
  setTimeout(() => rej(new Error('no DevTools endpoint after 30s')), 30000);
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
  const n = ++seq;
  pending.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method, params, ...(sessionId ? { sessionId } : {}) }));
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
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
};

const results = [];
try {
  for (let i = 0; i < runs; i++) {
    const loaded = once('Page.loadEventFired', s);
    await send('Page.navigate', { url: new URL(from, base).href }, s);
    await loaded;
    await sleep(800);
    const c = await evaluate(`(() => { const a = [...document.querySelectorAll('main a')].find((x) => x.textContent.includes('Back to work')); if (!a) return null; const r = a.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    if (!c) throw new Error(`no "Back to work" link on ${from}`);
    // Sampler lives in the page that is current at each tick, so it is re-armed from node.
    const t0 = Date.now();
    for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased'])
      await send('Input.dispatchMouseEvent', { type, x: c.x, y: c.y, button: 'left', clickCount: 1 }, s);
    const trace = [];
    while (Date.now() - t0 < 2500) {
      const v = await evaluate(`(() => { const e = document.getElementById(${JSON.stringify(id)}); return { y: Math.round(scrollY), top: e ? Math.round(e.getBoundingClientRect().top) : null, path: location.pathname + location.hash }; })()`).catch(() => null);
      if (v) trace.push({ t: Date.now() - t0, ...v });
      await sleep(50);
    }
    const last = trace[trace.length - 1];
    results.push({ run: i + 1, top: last?.top, path: last?.path, trace });
    console.log(`run ${String(i + 1).padStart(2)}: ${last?.path}  #${id} top ${last?.top}px  scrollY ${last?.y}`);
  }
} finally {
  ws.close();
  chrome.kill();
  await sleep(500);
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
const tops = results.map((r) => r.top).filter((t) => t !== null && t !== undefined);
const above = tops.filter((t) => t < 0).length;
console.log(`\n#${id} landing after "Back to work" from ${from}: min ${Math.min(...tops)} / max ${Math.max(...tops)} px; ` +
  `above the viewport top in ${above} of ${tops.length} runs; outside 0–200 px in ${tops.filter((t) => t < 0 || t > 200).length}`);
const worst = results.reduce((w, r) => (Math.abs((r.top ?? 0) - 96) > Math.abs((w.top ?? 0) - 96) ? r : w), results[0]);
console.log(`worst run ${worst.run} (top ${worst.top}px), scroll trace t:scrollY/top —`);
console.log('  ' + worst.trace.map((x) => `${x.t}:${x.y}/${x.top}`).join('  '));
