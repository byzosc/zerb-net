import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

let lenis: Lenis | undefined;
let rafId = 0;
let bound = false;
let built = false;
let revealIO: IntersectionObserver | undefined;

const reduceMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = () =>
  window.matchMedia('(hover: hover) and (pointer: fine)').matches;

function teardown() {
  cancelAnimationFrame(rafId);
  ScrollTrigger.getAll().forEach((t) => t.kill());
  revealIO?.disconnect();
  revealIO = undefined;
  lenis?.destroy();
  lenis = undefined;
}

// Cross-page #hash landing (2026-10-09). The section used to land anywhere from -88 to 147 px
// (target 96) — tools/probe-anchor-landing.mjs, 10 runs. Two scrollers raced: the router's hash
// scroll ran as a NATIVE smooth scroll (html { scroll-behavior: smooth }), and 120 ms later
// lenis.scrollTo(el) computed its target from Lenis's own scroll value, which the native animation
// had left stale — so the error depended on how far that animation had got. Now: native smooth
// scroll is off for the jump (after-swap sets inline scroll-behavior:auto), the target comes from
// the page's ACTUAL scroll position, one instant jump cancels anything in flight, and Lenis is set
// to the same value so it can't pull the page back.
const HEADER_OFFSET = 96; // = html { scroll-padding-top } in global.css: clears the fixed header
function landOnHash(el: HTMLElement) {
  const y = Math.max(0, Math.round(el.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET));
  window.scrollTo({ top: y, behavior: 'instant' as ScrollBehavior });
  lenis?.scrollTo(y, { immediate: true, force: true });
}

function build() {
  if (built) return;
  built = true;
  teardown();

  if (reduceMotion()) {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-in'));
    return;
  }

  // Damped smooth scroll
  lenis = new Lenis({ duration: 1.1, smoothWheel: true, touchMultiplier: 1.6 });
  lenis.on('scroll', ScrollTrigger.update);
  const raf = (t: number) => {
    lenis?.raf(t);
    rafId = requestAnimationFrame(raf);
  };
  rafId = requestAnimationFrame(raf);

  // Reveal-on-scroll. Deliberately NOT ScrollTrigger: after an Astro View-Transition
  // the swapped-in layout isn't settled when build() runs, so ScrollTrigger could
  // mis-measure every card as below the fold and leave them pinned at opacity:0 — the
  // works page then looked empty when reached from a homepage "View all work" CTA.
  // Reveal = add the class; the fade+rise is a pure-CSS transition (see .reveal in
  // global.css). No JS tween touches opacity, so an interrupted/throttled frame loop
  // can never leave a card pinned invisible.
  const reveal = (el: HTMLElement) => el.classList.add('is-in');

  const reveals = gsap.utils.toArray<HTMLElement>('.reveal:not(.is-in)');

  // 1) Reveal whatever is already in view, synchronously. This is the safety net that
  //    guarantees content can never get stuck invisible: it doesn't depend on
  //    IntersectionObserver or ScrollTrigger ever firing (both can silently no-op after
  //    a View-Transition / under Lenis, and IO is also suppressed while the tab is
  //    hidden). This alone keeps above-the-fold cards from ever blanking out.
  const inView = (el: HTMLElement) => {
    const r = el.getBoundingClientRect();
    return r.height > 0 && r.top < window.innerHeight && r.bottom > 0;
  };
  reveals.forEach((el) => {
    if (inView(el)) reveal(el);
  });

  // 2) Reveal the rest as they scroll in. IntersectionObserver is immune to the Lenis /
  //    View-Transition timing that makes ScrollTrigger unreliable here.
  const rest = reveals.filter((el) => !el.classList.contains('is-in'));
  if (rest.length && 'IntersectionObserver' in window) {
    revealIO = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          reveal(e.target as HTMLElement);
          obs.unobserve(e.target);
        });
      },
      // Fire a touch before fully in view, mirroring the old 'top 88%' feel.
      { rootMargin: '0px 0px -10% 0px' }
    );
    rest.forEach((el) => revealIO!.observe(el));
  } else {
    rest.forEach(reveal);
  }
}

// ── Hero intro ────────────────────────────────────────────────────────────────
// All three lines start near-simultaneously (small per-line stagger). Each title
// types out character by character; each ball rolls in from the left to its spot.
let introStarted = false;
let introFinished = false;
function finishIntro() {
  introFinished = true;
  document.documentElement.classList.add('intro-ready');
}
function heroIntro() {
  if (introStarted) return;
  introStarted = true;
  try {
    if (reduceMotion()) return finishIntro();
    const h1 = document.querySelector<HTMLElement>('[data-hero] h1');
    const lines = h1 ? Array.from(h1.querySelectorAll<HTMLElement>('.hl')) : [];
    if (lines.length < 3) return finishIntro();

    const sel = (line: HTMLElement, s: string) => line.querySelector<HTMLElement>(s);
    const mText = sel(lines[0], '.hl-t'), mDot = sel(lines[0], '.hero-dot-m');
    const vText = sel(lines[1], '.hl-t'), vDot = sel(lines[1], '.hero-dot-m');
    const cText = sel(lines[2], '.hl-t'), cDot = sel(lines[2], '.hero-dot-m');

    // Code is the only typewriter — split it into characters
    if (cText && !cText.dataset.split) {
      cText.dataset.split = '1';
      const text = cText.textContent || '';
      cText.textContent = '';
      for (const ch of text) {
        const s = document.createElement('span');
        s.className = 'ch';
        s.textContent = ch;
        cText.appendChild(s);
      }
    }
    const cChars = cText ? Array.from(cText.querySelectorAll('.ch')) : [];

    // Initial states. Motion: visible but masked (CSS feather mask, --mx 100% = hidden).
    // Visual: blurred + transparent. Code: container shown, chars hidden.
    gsap.set([mText, cText], { opacity: 1 });
    gsap.set(mText, { '--mx': '100%' });
    gsap.set(vText, { opacity: 0, filter: 'blur(18px)' });
    gsap.set(cChars, { opacity: 0 });
    gsap.set([mDot, vDot, cDot], { opacity: 0, x: -100, rotate: -360 });

    // back.out gives a slight overshoot/settle as the ball lands — more physical
    const dotIn = { opacity: 1, x: 0, rotate: 0, duration: 0.8, ease: 'back.out(2)' };
    const gap = 0.45; // more pronounced sequence — lines arrive distinctly one after another

    const tl = gsap.timeline({
      defaults: { ease: 'power3.out' },
      onComplete: () => {
        finishIntro(); // adds .intro-ready → CSS drops the mask + hide gate
        gsap.set([vText, cText], { clearProps: 'opacity,filter' });
        gsap.set(cChars, { clearProps: 'opacity' });
        gsap.set([mDot, vDot, cDot], { clearProps: 'transform,opacity' });
      },
    });

    // Motion — feathered mask wipes the word in (left → right)
    tl.to(mText, { '--mx': '0%', duration: 0.75 }, 0);
    tl.to(mDot, { ...dotIn }, 0);
    // Visual — gaussian blur resolves into focus
    tl.to(vText, { opacity: 1, filter: 'blur(0px)', duration: 0.7 }, gap);
    tl.to(vDot, { ...dotIn }, gap);
    // Code — types out character by character
    tl.to(cChars, { opacity: 1, duration: 0.02, stagger: 0.07 }, gap * 2);
    tl.to(cDot, { ...dotIn }, gap * 2);
  } catch {
    finishIntro();
  }
}

// ── Hero dot cursor-magnet ────────────────────────────────────────────────────
// A continuous rAF loop lerps each dot toward its target. The resting centre is
// derived as (current rect − currently-applied transform); because we own the
// transform every frame (no CSS transition on it) that reading is exact, so the
// displacement can never feed back on itself and stall. Motion is repelled.
let dotsBound = false;
function setupHeroDots() {
  if (dotsBound || !finePointer() || reduceMotion()) return;
  dotsBound = true;

  const cur = new WeakMap<HTMLElement, { tx: number; ty: number }>();
  let mx = -9999,
    my = -9999;
  const RADIUS = 150;

  window.addEventListener(
    'pointermove',
    (e) => {
      mx = e.clientX;
      my = e.clientY;
    },
    { passive: true }
  );

  const loop = () => {
    if (introFinished) {
      document.querySelectorAll<HTMLElement>('.hero-dot').forEach((wrap) => {
        const m = wrap.querySelector<HTMLElement>('.hero-dot-m');
        if (!m) return;
        // Measure the wrapper — it is NEVER transformed, so this is always the
        // exact resting centre. No subtraction, no feedback, no stall.
        const r = wrap.getBoundingClientRect();
        if (!r.width || r.bottom < 0 || r.top > window.innerHeight) return;
        const dx = mx - (r.left + r.width / 2);
        const dy = my - (r.top + r.height / 2);
        const dist = Math.hypot(dx, dy);
        let tgx = 0,
          tgy = 0;
        if (dist < RADIUS) {
          const repel = wrap.dataset.dot === 'motion'; // Motion bounces away (collision)
          const sign = repel ? -1 : 1;
          const f = (1 - dist / RADIUS) * (repel ? 0.5 : 0.4) * sign;
          tgx = dx * f;
          tgy = dy * f;
        }
        const c = cur.get(m) || { tx: 0, ty: 0 };
        c.tx += (tgx - c.tx) * 0.2;
        c.ty += (tgy - c.ty) * 0.2;
        if (Math.abs(c.tx) < 0.1 && Math.abs(c.ty) < 0.1) {
          c.tx = 0;
          c.ty = 0;
        }
        m.style.transform = c.tx || c.ty ? `translate(${c.tx}px, ${c.ty}px)` : '';
        cur.set(m, c);
      });
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}

// ── Custom ball cursor (desktop only) ─────────────────────────────────────────
let cursorBound = false;
function setupCursor() {
  if (cursorBound || !finePointer()) return;
  cursorBound = true;
  document.documentElement.classList.add('cursor-on');

  let cx = window.innerWidth / 2,
    cy = window.innerHeight / 2,
    tx = cx,
    ty = cy;

  window.addEventListener(
    'pointermove',
    (e) => {
      tx = e.clientX;
      ty = e.clientY;
    },
    { passive: true }
  );

  // Re-acquire #cursor every frame so the loop keeps working even if the element
  // is re-created across an Astro View Transition (back/forward navigation).
  const loop = () => {
    const el = document.getElementById('cursor');
    if (el) {
      // tight follow so the visible ball stays close to the true pointer (avoids
      // mis-clicks where the ball lags behind where you actually click)
      cx += (tx - cx) * 0.35;
      cy += (ty - cy) * 0.35;
      el.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);

  const hoverSel = 'a, button, input, textarea, [data-dot], .filter-btn, [data-suggestion]';
  const setHover = (e: Event, on: boolean) => {
    const hit = (e.target as Element).closest?.(hoverSel);
    if (!hit) return;
    const c = document.getElementById('cursor');
    if (!c) return;
    if (on) {
      const labelled = hit.closest('[data-cursor]') as HTMLElement | null;
      const link = hit.closest('a') as HTMLAnchorElement | null;
      const label =
        labelled?.dataset.cursor || (link && link.target === '_blank' ? 'Link' : 'Go');
      const span = c.querySelector('.cursor-label');
      if (span) span.textContent = label;
    }
    c.classList.toggle('is-hover', on);
  };
  document.addEventListener('pointerover', (e) => setHover(e, true));
  document.addEventListener('pointerout', (e) => setHover(e, false));
}

// Never let a motion error bubble into Astro's View Transition lifecycle — a
// throw there can leave the router wedged so clicks stop navigating.
const safe = (fn: () => void) => {
  try {
    fn();
  } catch (e) {
    console.error('motion', e);
  }
};

export function setupMotion() {
  safe(build);
  safe(heroIntro);
  safe(setupHeroDots);
  safe(setupCursor);
  if (bound) return;
  bound = true;
  document.addEventListener('astro:before-swap', () =>
    safe(() => {
      teardown();
      built = false;
    })
  );
  // Reset scroll on navigation — but NOT when the URL has a hash, so links like
  // /#motion from a sub-page land on that section instead of the page top.
  document.addEventListener('astro:after-swap', () =>
    safe(() => {
      if (!location.hash) window.scrollTo(0, 0);
      // Cross-page #hash jump: no native smooth scroll this time (see landOnHash below).
      // Set here, not in before-swap: the swap copies the new <html>'s attributes and would
      // drop an inline style set earlier.
      else document.documentElement.style.scrollBehavior = 'auto';
    })
  );
  document.addEventListener('astro:page-load', () =>
    safe(() => {
      build();
      // honor a #hash target after a cross-page navigation. Lenis owns scroll, so
      // use lenis.scrollTo (native scrollIntoView gets reset by Lenis to 0). The
      // short delay lets Lenis finish initialising after build().
      if (location.hash) {
        const el = document.querySelector<HTMLElement>(location.hash);
        if (el) {
          setTimeout(() => landOnHash(el), 120);
          // re-check once the page has settled; correct only if it is visibly off
          setTimeout(() => {
            if (Math.abs(el.getBoundingClientRect().top - HEADER_OFFSET) > 4) landOnHash(el);
            document.documentElement.style.scrollBehavior = '';
          }, 470);
        } else document.documentElement.style.scrollBehavior = '';
      }
      if (cursorBound) {
        document.documentElement.classList.add('cursor-on');
        // the element that triggered navigation never fired pointerout, so the
        // cursor can be stuck in its hover (filled-ball) state — reset it.
        const c = document.getElementById('cursor');
        c?.classList.remove('is-hover');
        const span = c?.querySelector('.cursor-label');
        if (span) span.textContent = '';
      }
    })
  );
}
