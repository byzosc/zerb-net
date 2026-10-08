// Log every outbound HTTP(S) request a Node process makes — e.g. during `npm run build` (v3-F, 2026-10-08).
//
//   cd app
//   FETCH_TRAP_LOG=$PWD/../.render-tmp/build-requests.log \
//     NODE_OPTIONS="--import $PWD/../tools/trace-build-requests.mjs" npm run build
//   grep -v ' init ' ../.render-tmp/build-requests.log      # one line per request: pid, kind, URL
//
// Why: the homepage must stay a plain static build — the user dropped a build-time blog fetch the
// same day it was written ("no gain"), and "no request to blog.zosc.com during the build" should be
// shown, not assumed from reading the source. NODE_OPTIONS carries the hook into every child process
// (npm → astro build → the postbuild redirect patch); each process logs an `init` line, so a missing
// process is visible. Covered: global fetch (undici's diagnostics channel) and node:http / node:https.
// Seen on 2026-10-08: the only request a build makes is Astro's own telemetry
// (telemetry.astro.build) — set ASTRO_TELEMETRY_DISABLED=1 to drop that too.
import dc from 'node:diagnostics_channel';
import http from 'node:http';
import https from 'node:https';
import { appendFileSync } from 'node:fs';

const LOG = process.env.FETCH_TRAP_LOG;
const log = (kind, what) => {
  try {
    appendFileSync(LOG, `${process.pid} ${kind} ${what}\n`);
  } catch {}
};

dc.subscribe('undici:request:create', ({ request }) => log('undici', `${request.origin}${request.path}`));
for (const [name, mod] of [['http', http], ['https', https]]) {
  for (const fn of ['request', 'get']) {
    const orig = mod[fn];
    mod[fn] = function (...args) {
      const a = args[0];
      const url = typeof a === 'string' ? a : a instanceof URL ? a.href : `${name}://${a?.hostname ?? a?.host}${a?.path ?? ''}`;
      log(name, url);
      return orig.apply(this, args);
    };
  }
}
log('init', process.argv.slice(1).join(' ').slice(0, 160));
