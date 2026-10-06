<div align="center">

# ⚡ ZOSC — Motion · Visual · Code

**English** · [中文](README.zh-CN.md)

**A motion designer & visual artist's portfolio — a long-scroll, cinematic site with a built-in multi-provider AI that answers questions about the work.**

[![Live](https://img.shields.io/badge/live-zosc.com-e7503a)](https://zosc.com)
![Stack](https://img.shields.io/badge/stack-Astro%206%20%2B%20Tailwind%20v4-ff5d01)
![Motion](https://img.shields.io/badge/motion-GSAP%20%2B%20Lenis-88ce02)
![AI](https://img.shields.io/badge/Ask%20AI-Gemini%20%2F%20OpenAI%20%2F%20Claude-7c3aed)
![Hosting](https://img.shields.io/badge/hosting-Vercel-000000)
![Media](https://img.shields.io/badge/media-Cloudflare%20R2-f38020)

</div>

---

## 🤔 What this is

The personal portfolio of **ZOSC (Zosc Lion)** — motion design, visual art, and code under one roof. It began as a WordPress export and was rebuilt from scratch into a fast, motion-first **Astro** site, organized around three pillars:

- **Motion** — systems of movement, interfaces that breathe.
- **Visual** — worlds, surfaces and light.
- **Code** — things built, not just designed.

Instead of a stiff nav-and-short-pages layout, it's one long, scroll-driven page with anchored sections — plus an **"AI Ask"** panel that answers questions about any project, the process, or how to get in touch.

## ✨ Highlights

- 🎬 **Motion-first** — Lenis smooth scroll + GSAP, a per-line hero intro (mask-wipe / blur / typewriter), a difference-blend custom cursor with contextual labels, and cursor-magnet accent dots.
- 🤖 **Ask AI** — a slide-in assistant that streams from a multi-provider endpoint (Gemini → OpenAI → Claude), grounded in a knowledge base compiled from the project content. Rate-limited and quota-guarded.
- 🖼 **Image-forward grid** — featured-first pillar sections; covers rest under a neutral veil and resolve to full colour on hover (desktop), stay bright on touch.
- 🎞 **R2-hosted video** — heavy media lives on Cloudflare R2 (free egress), kept out of Git.
- 🔤 **Self-hosted fonts** — Montserrat (display) + Mulish (body), preloaded, no FOUT, no third-party Google Fonts requests.
- ⚡ **Astro + View Transitions** — static-fast pages, with the header / cursor / AI panel persisted across navigations.

## 🧭 Stack

```
Astro 6  +  Tailwind v4          →  the site            (app/)
GSAP  +  Lenis                   →  motion & smooth scroll
/api/chat  (serverless)          →  multi-provider AI, streamed
Cloudflare R2                    →  video hosting
Vercel  (root: app/)             →  deploy  ·  zosc.com
```

The live site is the Astro rebuild in `app/`. The original WordPress static export that used to sit at the repo root was removed on 2026-07-04 (still recoverable from git history); the root now only keeps the R2 media tooling (`tools/`, `media-manifest.json`) and docs.

## 🚀 Run it locally

```bash
cd app
npm install
npm run dev            # http://localhost:4321
```

```bash
cp .env.example .env   # add a GEMINI_API_KEY (or OpenAI / Anthropic) for the AI panel
npm run build          # production build
```

> Media + AI keys live in `.env` (gitignored). The Ask AI panel degrades gracefully without a key.

## 🗺 Roadmap

- [ ] Reliable global media delivery (CDN / mirror)
- [ ] Hi-res covers for the Motion pillar
- [ ] More work in the Code pillar
- [ ] Cross-instance AI rate-limiting via Upstash

## 📜 License — All Rights Reserved

This repo is **public for reference, not open source.** Everything — the code **and** the creative work (images, video, text, brand) — is **© 2026 ZOSC LION, all rights reserved**. You're welcome to read and learn from it; you may **not** copy, reuse, or republish any part without permission. See [LICENSE](LICENSE).

---

<div align="center">

Designed, written and built by [**ZOSC**](https://github.com/zerbLion) · [zosc.com](https://zosc.com)

</div>
