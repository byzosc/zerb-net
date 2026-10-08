// Verify the compressed about page and the AI prompt that reads it (v2 subtask A, 2026-10-08).
// Run from the repo root AFTER a build (`cd app && npm run build`):
//
//   node tools/check-about.mjs [--before <old-about-fragment.html>] [--private-deny <file>]
//
// --before        counts words of an older about.html fragment the same way, for a before/after
//                 comparison (e.g. `git show <rev>:app/src/migrated/about.html > scratch/file.html`).
// --private-deny  a file OUTSIDE this repo whose first non-# line is a regex of terms that must
//                 never be public (current employer, real name, city). They can't live in this
//                 file: the repo is public, and a deny-list advertises exactly what it protects.
//                 Only match COUNTS are printed, never the terms, so the output is safe to paste.
//
// Checks (each prints its evidence; exit code 1 if any fails):
//  1. years   no 20xx year in app/src/migrated/about.html — the job timeline must not be
//             inferable from the public page (user decision 2026-10-08).
//  2. deny    no old Gmail / old brand / location wording in about.html (generic terms that
//             are already public in this repo's docs); plus, with --private-deny, the private
//             terms in about.html, the whole built about page, and (step 5) the AI prompt.
//  3. refs    every root-relative src/href in about.html (→ app/public) and in the built
//             about page (→ app/dist/client) is a real file. Lesson from 2026-10-06, when a
//             rename left three favicon references pointing at files that did not exist.
//  4. words   word count of the built about article (<article class="entry-content">);
//             target 120–260 (one ~120–180-word paragraph + skills + certifications + contact).
//             A "word" is a whitespace token with at least one letter or digit, so "—" and "·"
//             separators don't count but "hi@zosc.com", "C#" and "10+" do.
//  5. prompt  imports the BUILT /api/chat handler with a stubbed fetch and a fake key (no
//             network, nothing leaves the machine), captures the exact system prompt it would
//             send to the provider, and checks: the whole about text is in it untruncated,
//             contact is hi@zosc.com, no old Gmail, no "vivo ’s"-style tag-gap artifacts.
//             Testing the built bundle rather than re-implementing buildSystemPrompt() means
//             we test the code that ships, including the astro:content data it bundles.

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const APP = join(ROOT, 'app');
const ABOUT_SRC = join(APP, 'src/migrated/about.html');
const ABOUT_BUILT = join(APP, 'dist/client/about/index.html');
const CHUNKS = join(APP, '.vercel/output/functions/_render.func/dist/server/chunks');

let failed = false;
const fail = (msg) => { failed = true; console.log('  FAIL ' + msg); };
const pass = (msg) => console.log('  ok   ' + msg);

const ENT = { amp: '&', nbsp: ' ', mdash: '—', ndash: '–', middot: '·', lsquo: '‘', rsquo: '’', ldquo: '“', rdquo: '”', hellip: '…', quot: '"', apos: "'", lt: '<', gt: '>' };
const htmlToText = (html) => html
  .replace(/<(script|style)\b[\s\S]*?<\/\1>/gi, ' ')
  .replace(/<\/?(strong|em|b|i|a|span|code)\b[^>]*>/gi, '')
  .replace(/<[^>]+>/g, ' ')
  .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
  .replace(/&([a-z]+);/gi, (m, n) => ENT[n.toLowerCase()] ?? ' ')
  .replace(/\s+/g, ' ')
  .trim();
const words = (text) => text.split(/\s+/).filter((t) => /[\p{L}\p{N}]/u.test(t));

const args = process.argv.slice(2);
const argOf = (flag) => (args.includes(flag) ? args[args.indexOf(flag) + 1] : null);
const beforePath = argOf('--before');
const privateDenyPath = argOf('--private-deny');
const PRIVATE_DENY = privateDenyPath
  ? new RegExp(
      readFileSync(privateDenyPath, 'utf8').split('\n').map((l) => l.trim()).find((l) => l && !l.startsWith('#')),
      'gi'
    )
  : null;
const privateHits = (text) => (PRIVATE_DENY ? (text.match(PRIVATE_DENY) || []).length : 0);

const src = readFileSync(ABOUT_SRC, 'utf8');

console.log('1. years in about.html');
const years = src.match(/\b20[12][0-9]\b/g) || [];
years.length ? fail(`found ${years.length}: ${years.join(' ')}`) : pass('0 matches for \\b20[12][0-9]\\b');

console.log('2. generic deny-list in about.html');
const DENY = /zcbgood|zerb|china-based|mainland|国内/gi;
const denied = src.match(DENY) || [];
denied.length ? fail(`found: ${denied.join(', ')}`) : pass(`0 matches for ${DENY}`);
if (PRIVATE_DENY) {
  const n = privateHits(src);
  n ? fail(`about.html: ${n} private-term match(es) — inspect privately, terms not printed`)
    : pass('about.html: 0 private-term matches (--private-deny)');
} else {
  console.log('  skip private-term scan (no --private-deny file given)');
}
const caps = src.match(/\bZOSC\b|\bZosc\b/g) || [];
caps.length ? fail(`non-lowercase name: ${caps.join(', ')}`) : pass('name only appears lowercase (no ZOSC / Zosc)');

console.log('3. reference integrity');
const rootRelative = (html) =>
  [...html.matchAll(/\s(?:src|href|poster|content)="(\/[^"#?]*)/g)]
    .map((m) => m[1])
    .filter((p) => !p.startsWith('//'));
const srcRefs = rootRelative(src);
if (!srcRefs.length) pass('about.html has 0 root-relative src/href (only mailto: and https:// links)');
for (const p of srcRefs) {
  existsSync(join(APP, 'public', decodeURIComponent(p))) ? pass(`public${p}`) : fail(`missing public${p}`);
}
if (!existsSync(ABOUT_BUILT)) {
  fail(`no built page at ${ABOUT_BUILT} — run the build first`);
} else {
  const built = readFileSync(ABOUT_BUILT, 'utf8');
  const builtRefs = [...new Set(rootRelative(built))];
  let ok = 0;
  for (const p of builtRefs) {
    const f = join(APP, 'dist/client', decodeURIComponent(p));
    if (existsSync(f) && !f.endsWith('/')) ok++;
    else if (existsSync(join(f, 'index.html'))) ok++;
    else fail(`built about page references ${p}, not found in dist/client`);
  }
  pass(`built about page: ${ok}/${builtRefs.length} root-relative references resolve to real files`);
  if (PRIVATE_DENY) {
    const n = privateHits(built);
    n ? fail(`built about page: ${n} private-term match(es) — terms not printed`)
      : pass('built about page (whole HTML incl. header/footer/JSON-LD): 0 private-term matches');
  }

  console.log('4. word count (built about article)');
  const m = built.match(/<article[^>]*class="[^"]*entry-content[^"]*"[^>]*>([\s\S]*?)<\/article>/);
  if (!m) fail('could not find <article class="entry-content"> in the built page');
  else {
    const w = words(htmlToText(m[1])).length;
    const wSrc = words(htmlToText(src)).length;
    const lead = src.match(/<p class="lead">([\s\S]*?)<\/p>/);
    console.log(`  built article: ${w} words  (source fragment: ${wSrc}; must match since set:html injects it verbatim)`);
    if (lead) console.log(`  intro paragraph (.lead): ${words(htmlToText(lead[1])).length} words  (target ~120–180)`);
    w >= 120 && w <= 260 ? pass('article word count within 120–260') : fail(`article word count ${w} outside 120–260`);
    if (w !== wSrc) fail('built article and source fragment counts differ');
    if (beforePath) {
      const before = words(htmlToText(readFileSync(beforePath, 'utf8'))).length;
      console.log(`  before (${beforePath.split('/').pop()}): ${before} words  →  after: ${w} words`);
    }
  }
}

console.log('5. AI system prompt (built /api/chat, fetch stubbed, fake key)');
const chunk = existsSync(CHUNKS) && readdirSync(CHUNKS).find((f) => /^chat_.*\.mjs$/.test(f));
if (!chunk) {
  fail(`no chat_*.mjs under ${CHUNKS} — run the build first`);
} else {
  process.env.GEMINI_API_KEY = 'stub-key-local-test';
  delete process.env.AI_PROVIDER;
  delete process.env.AI_MODEL;
  const captured = [];
  globalThis.fetch = async (url, init) => {
    captured.push({ url: String(url), body: init?.body });
    const sse = 'data: {"candidates":[{"content":{"parts":[{"text":"stub-ok"}]}}]}\n\n';
    return new Response(sse, { status: 200, headers: { 'Content-Type': 'text/event-stream' } });
  };
  const { page } = await import(pathToFileURL(join(CHUNKS, chunk)).href);
  const req = new Request('https://zosc.com/api/chat', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: 'How can I get in touch?' }] }),
  });
  const res = await page().POST({ request: req, clientAddress: '127.0.0.1' });
  const reply = await res.text();
  res.status === 200 && reply === 'stub-ok'
    ? pass(`handler streamed the stub reply (status ${res.status}, body "${reply}")`)
    : fail(`handler returned status ${res.status}, body ${JSON.stringify(reply)}`);
  if (!captured.length) fail('handler never called the provider');
  else {
    const host = new URL(captured[0].url).host;
    const system = JSON.parse(captured[0].body).systemInstruction.parts[0].text;
    console.log(`  provider host: ${host} (stubbed)   system prompt: ${system.length} chars`);
    const marker = 'ABOUT / BACKGROUND (extracted text):\n';
    const at = system.indexOf(marker);
    const aboutPart = at >= 0 ? system.slice(at + marker.length).split('\n')[0] : '';
    const expected = htmlToText(src);
    console.log(`  about text inside prompt: ${aboutPart.length} chars (slice cap 4000)`);
    aboutPart === expected
      ? pass('about text in prompt == full about.html text (nothing truncated or dropped)')
      : fail('about text in prompt differs from about.html text');
    /hi@zosc\.com/.test(system) ? pass('contact hi@zosc.com present') : fail('hi@zosc.com missing');
    /zcbgood/.test(system) ? fail('old Gmail still in prompt') : pass('no old Gmail in prompt');
    / ’s\b/.test(system) ? fail('tag-gap artifact (" ’s") in prompt') : pass('no tag-gap artifacts (" ’s")');
    if (PRIVATE_DENY) {
      const n = privateHits(system);
      n ? fail(`AI system prompt: ${n} private-term match(es) — terms not printed`)
        : pass('AI system prompt (incl. all project summaries + blog list): 0 private-term matches');
    }
    console.log('  --- prompt head (up to the PROJECTS list) ---');
    console.log(system.slice(0, system.indexOf('PROJECTS:')).trimEnd().replace(/^/gm, '  | '));
    console.log('  --- about section as the model sees it ---');
    console.log('  | ' + aboutPart);
  }
}

console.log(failed ? '\nRESULT: FAIL' : '\nRESULT: PASS');
process.exit(failed ? 1 : 0);
