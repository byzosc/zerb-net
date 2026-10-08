#!/usr/bin/env python3
"""Check the built site for the v2 homepage order, titles, og:image and reference integrity.

    cd app && npm run build && cd ..
    python3 tools/check-home.py [--code slug,slug,...]

--code   the exact Code-section slugs expected on the homepage, in order. Default: EXPECT_CODE
         below (the user's decision); the content entries (featured: true, pillar code, by
         order) must produce the same list.

Written for v2 subtask C (2026-10-08): Code leads the homepage (Code · Motion · Visual), the
Code section shows only `featured` products, and the title follows the same order. Any change
to section order, card selection, the header nav, titles or brand/media file names should pass
this before commit. Only reads app/src/content/projects, app/public and the build output.
Extended by subtask E (same day): Code = exactly 3 cards, hero words, old names, Back to work.

Checks (exit code 1 on any failure):
  1. homepage <main> pillar sections are #code, #motion, #visual in that order; cards per
     section follow the rule in index.astro (Code: featured only; Motion / Visual: first 5 by
     order; at most 5 each); Code = EXPECT_CODE with full grid rows (1 large + an even number of
     small cards); each large card shows the entry's coverLarge when it has one
  2. homepage <title>, og:title and twitter:title; no "Motion · Visual · Code" left in any
     built HTML (the visible title and the page-source comment both used it)
  3. header nav (desktop + mobile menu) and the /works filter buttons follow the same order;
     /works links every live entry (non-featured products live there)
  4. OLD_NAMES appear 0 times in the served static files (dist/client HTML/CSS/JS/SVG/XML/JSON);
     in the server bundle only as an entry of Astro's public-file inventory naming a file that is
     still in public/ (zerb-logo.png: media is never deleted)
  5. reference integrity: every /media/... and /fonts/... reference in built HTML/CSS — root
     relative or absolute https://zosc.com/... (og:image, JSON-LD) — is a real file under
     app/public; every other root-relative src/href/srcset/poster resolves inside dist/client
     (lesson of 2026-10-06: a rename left three favicon links pointing at missing files)
  6. og:image: product pages with a raster cover use that cover (absolute URL); SVG-cover
     products and all other pages keep the default logo
  7. about page: the intro (before the first <hr>) is three paragraphs, .lead on the first only
  8. hero headline words follow ORDER (Code · Motion · Visual); motion.ts animates the lines by
     POSITION, so data-mask / data-blur / data-type stay on lines 1 / 2 / 3, while each dot's
     data-dot (its personality in global.css and motion.ts) follows its word
  9. every project page's "← Back to work" points at its first pillar's homepage section
"""
from __future__ import annotations

from html import unescape
import re
import sys
import urllib.parse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
PUBLIC = APP / "public"
DIST = APP / "dist" / "client"
SERVER_OUT = APP / ".vercel" / "output"
ENTRIES = APP / "src" / "content" / "projects"
SITE = "https://zosc.com"
ORDER = ["code", "motion", "visual"]
FEATURED_ONLY = {"code"}
MAX_CARDS = 5
# User, 2026-10-08: Code shows 3 cards (symmetric grid); openwebui-cliproxy-gateway only on /works.
EXPECT_CODE = ["motionpilot", "motionrules", "cubby"]
TITLE = "zosc — Code · Motion · Visual"
OLD_TITLE_ORDER = "Motion · Visual · Code"
# Old file names / domain that must not ship: the pre-rename logo and favicon files, and the
# MotionSheet domain replaced by motionrules.com/app (the slug zerb-cc-cd is protected and stays).
OLD_NAMES = ("zerb-logo", "zerb-favicon", "zerb.cc.cd")
HERO_EFFECTS = ["data-mask", "data-blur", "data-type"]  # motion.ts: line 1, 2, 3 — by position
DEFAULT_OG = f"{SITE}/media/images/common/brand/cropped-logo_high2.png"
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".xml", ".json", ".txt", ".webmanifest", ".svg"}

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print("  FAIL", msg)


def ok(msg: str) -> None:
    print("  ok  ", msg)


def check(cond: bool, ok_msg: str, fail_msg: str) -> None:
    ok(ok_msg) if cond else fail(fail_msg)


def frontmatter(path: Path) -> dict:
    m = re.match(r"^---\n(.*?)\n---", path.read_text(encoding="utf-8"), flags=re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def meta(html: str, attr: str, name: str) -> str | None:
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', html)
    return m.group(1) if m else None


def main() -> int:
    expect_code = EXPECT_CODE
    if "--code" in sys.argv:
        expect_code = sys.argv[sys.argv.index("--code") + 1].split(",")

    entries = {p.stem: frontmatter(p) for p in sorted(ENTRIES.glob("*.md"))}
    live = sorted(((s, d) for s, d in entries.items() if not d.get("draft")), key=lambda sd: sd[1].get("order", 100))
    home = (DIST / "index.html").read_text(encoding="utf-8")

    print("1. homepage section order + cards")
    main_html = home[home.find("<main"): home.find("</main>")]
    sections = [(m.group(1), m.end()) for m in re.finditer(r'<section id="([a-z]+)"', main_html)]
    ids = [s for s, _ in sections]
    check(ids == ORDER, f"sections: {' → '.join('#' + i for i in ids)}", f"sections {ids} != {ORDER}")
    for sid, start in sections:
        body = main_html[start: main_html.find("</section>", start)]
        cards = re.findall(r'href="/project/([^/"]+)/"', body)
        pool = [s for s, d in live if sid in d.get("pillars", ["visual"])]
        rule = "featured only" if sid in FEATURED_ONLY else f"first {MAX_CARDS} by order"
        want = ([s for s in pool if entries[s].get("featured")] if sid in FEATURED_ONLY else pool)[:MAX_CARDS]
        if sid == "code" and want != expect_code:
            fail(f"#code: entries say {want}, expected {expect_code}")
        if cards == want:
            ok(f"#{sid} ({rule}, {len(pool)} in pillar): {len(cards)} cards {cards}")
        else:
            fail(f"#{sid} ({rule}): built {cards}, expected {want}")
        if sid == "code":
            small = len(cards) - 1  # the rest sit in a two-column grid under the large card
            check(small > 0 and small % 2 == 0, f"#code grid: 1 large + {small} small cards, rows full",
                  f"#code grid: 1 large + {small} small cards leaves a half-empty row")
        if cards:  # index.astro: the large card uses coverLarge when the entry has one
            img = re.search(r'<img src="([^"]+)"', body)
            want_img = entries[cards[0]].get("coverLarge") or entries[cards[0]]["cover"]
            check(bool(img) and img.group(1) == want_img, f"#{sid} large card image {want_img}",
                  f"#{sid} large card image {img.group(1) if img else None}, expected {want_img}")

    print("2. titles")
    title = re.search(r"<title>(.*?)</title>", home).group(1)
    for label, value in [("<title>", title), ("og:title", meta(home, "property", "og:title")),
                         ("twitter:title", meta(home, "name", "twitter:title"))]:
        check(value == TITLE, f"{label} = {value}", f"{label} = {value!r}")
    print(f"       description = {meta(home, 'name', 'description')}")
    html_files = sorted(DIST.rglob("*.html"))
    stale = [str(p.relative_to(DIST)) for p in html_files if OLD_TITLE_ORDER in p.read_text(encoding="utf-8")]
    check(not stale, f'"{OLD_TITLE_ORDER}" in 0 of {len(html_files)} built HTML files', f'"{OLD_TITLE_ORDER}" still in {stale}')

    print("3. nav + /works filter order")
    nav = re.findall(r'href="/#(code|motion|visual)"', home)
    check(nav == ORDER * 2, f"header + mobile menu: {nav}", f"nav order {nav}")
    works = (DIST / "works" / "index.html").read_text(encoding="utf-8")
    filters = re.findall(r'data-filter="([a-z]+)"', works)
    check(filters == ["all", *ORDER], f"/works filters: {filters}", f"/works filters {filters}")
    listed_works = set(re.findall(r'href="/project/([^/"]+)/"', works))
    unlisted = [s for s, _ in live if s not in listed_works]
    check(not unlisted, f"/works links all {len(live)} live entries (non-featured products included)",
          f"/works does not link {unlisted}")

    print(f"4. old names in built text files: {', '.join(OLD_NAMES)}")
    scanned, hits = 0, []
    for p in DIST.rglob("*"):
        if p.is_file() and p.suffix in TEXT_SUFFIXES:
            scanned += 1
            text = p.read_text(encoding="utf-8", errors="replace")
            hits += [f"{p.relative_to(APP)} {name}×{text.count(name)}" for name in OLD_NAMES if name in text]
    check(not hits, f"0 occurrences in {scanned} served static text files (dist/client: HTML/CSS/JS/SVG/XML/JSON)",
          f"old names in served files: {hits}")
    # The server bundle carries Astro's inventory of every file in public/ — a JSON list of paths.
    # A kept old file (zerb-logo.png) is listed there on purpose; any other occurrence in the
    # bundle is a real reference (e.g. a server-rendered page or the content data) and fails.
    inventory = re.compile(r'(?<=[\[,])"(/[^"]+)"(?=[,\]])')
    server_hits, listed = [], 0
    for p in SERVER_OUT.rglob("*"):
        if p.is_file() and p.suffix in TEXT_SUFFIXES and "node_modules" not in p.parts and "static" not in p.relative_to(SERVER_OUT).parts[:1]:
            text = p.read_text(encoding="utf-8", errors="replace")
            kept = [u for u in inventory.findall(text) if (PUBLIC / u.lstrip("/")).is_file()]
            for name in OLD_NAMES:
                n, inv = text.count(name), sum(u.count(name) for u in kept)
                listed += inv
                if n > inv:
                    server_hits.append(f"{p.relative_to(APP)} {name}×{n - inv}")
    check(not server_hits, f"server bundle: 0 references ({listed} public-file inventory entries — kept old files, not references)",
          f"server bundle references old names: {server_hits}")
    new_logo = "/media/images/common/brand/zosc-logo.png"
    check(new_logo in home and (PUBLIC / new_logo.lstrip("/")).is_file(),
          f"header logo {new_logo} referenced and present", f"header logo {new_logo} not referenced or missing")

    print("5. reference integrity (built HTML + CSS)")
    refs: dict[str, set[str]] = {}
    attr_re = re.compile(r'\b(?:src|href|poster|content|srcset)="([^"]+)"')
    for p in list(DIST.rglob("*.html")) + list(DIST.rglob("*.css")):
        text = p.read_text(encoding="utf-8")
        values = attr_re.findall(text) if p.suffix == ".html" else []
        values += re.findall(r"url\(\s*['\"]?([^'\")]+)", text)
        values += re.findall(rf'"({re.escape(SITE)}/[^"]+)"', text)  # JSON-LD image / url
        for v in values:
            for part in (v.split(",") if " " in v and "," in v else [v]):  # srcset candidates
                url = part.strip().split(" ")[0]
                if url.startswith(SITE + "/"):
                    url = url[len(SITE):]
                if url.startswith("/") and not url.startswith("//"):
                    refs.setdefault(urllib.parse.unquote(url.split("#")[0].split("?")[0]), set()).add(str(p.relative_to(DIST)))
    media = {u for u in refs if u.startswith(("/media/", "/fonts/"))}
    missing_media = [u for u in sorted(media) if not (PUBLIC / u.lstrip("/")).is_file()]
    for u in missing_media:
        fail(f"{u} (used in {sorted(refs[u])[:3]}) missing under app/public")
    if not missing_media:
        ok(f"{len(media)} distinct /media + /fonts references, all present under app/public")
    other_missing = []
    for u in sorted(set(refs) - media):
        f = DIST / u.lstrip("/")
        # a route resolves to <route>/index.html, or <route>.html (404.html — its own canonical is /404/)
        if not (f.is_file() or (f / "index.html").is_file() or f.with_name(f.name + ".html").is_file()):
            other_missing.append(u)
    # Redirect-only routes (astro.config.mjs `redirects`) are served by Vercel, not as files.
    redirects = set(re.findall(r"'(/[^']+/)':", (APP / "astro.config.mjs").read_text(encoding="utf-8")))
    real_missing = [u for u in other_missing if u not in redirects and u.rstrip("/") + "/" not in redirects]
    for u in real_missing:
        fail(f"{u} (used in {sorted(refs[u])[:3]}) not in dist/client")
    if not real_missing:
        ok(f"{len(set(refs) - media)} other root-relative references resolve in dist/client"
           + (f" ({len(other_missing)} are configured redirects)" if other_missing else ""))

    print("6. og:image per page")
    for slug, d in live:
        page = DIST / "project" / slug / "index.html"
        html = page.read_text(encoding="utf-8")
        og, tw = meta(html, "property", "og:image"), meta(html, "name", "twitter:image")
        raster = d.get("kind") == "product" and re.search(r"\.(jpe?g|png|webp|gif)$", d["cover"], re.I)
        want = f"{SITE}{d['cover']}" if raster else DEFAULT_OG
        if og == want and tw == want:
            if d.get("kind") == "product":
                ok(f"{slug}: {'cover' if raster else 'default (SVG cover)'} {og.replace(SITE, '')}")
        else:
            fail(f"{slug}: og:image {og} / twitter:image {tw}, expected {want}")
    others = [p for p in html_files if "project" not in p.relative_to(DIST).parts]
    bad = [str(p.relative_to(DIST)) for p in others if meta(p.read_text(encoding="utf-8"), "property", "og:image") != DEFAULT_OG]
    older = sum(1 for _, d in live if d.get("kind") != "product")
    check(not bad, f"{len(others)} non-project pages + {older} older project pages keep the default og:image",
          f"non-project pages without the default og:image: {bad}")

    print("7. about intro paragraphs")
    about = (DIST / "about" / "index.html").read_text(encoding="utf-8")
    art = re.search(r'<article[^>]*class="[^"]*entry-content[^"]*"[^>]*>([\s\S]*?)</article>', about).group(1)
    paras = re.findall(r"<p([^>]*)>([\s\S]*?)</p>", art.split("<hr>")[0])
    # same word rule as tools/check-about.mjs: entities decoded, a token needs a letter or digit
    words = [len([t for t in unescape(re.sub(r"<[^>]+>", "", b)).split() if re.search(r"[^\W_]", t)]) for _, b in paras]
    leads = [i + 1 for i, (a, _) in enumerate(paras) if 'class="lead"' in a]
    if len(paras) == 3 and leads == [1]:
        ok(f"3 paragraphs, words {words}, .lead on paragraph 1 only")
    else:
        fail(f"{len(paras)} intro paragraphs, .lead on {leads} (want 3, [1])")

    print("8. hero headline")
    hero = home[home.find("data-hero"): home.find("</h1>", home.find("data-hero"))]
    lines = re.findall(r'<span class="hl"><span class="hl-t" (data-[a-z]+)>([^<]*)</span>'
                       r'<span class="hero-dot" data-dot="([a-z]+)"', hero)
    words, effects, dots = [w for _, w, _ in lines], [e for e, _, _ in lines], [d for _, _, d in lines]
    check([w.lower() for w in words] == ORDER, f"words: {' / '.join(words)}", f"hero words {words}, expected {ORDER}")
    check(effects == HERO_EFFECTS, f"effects by line position: {effects} (mask wipe / blur / typewriter)",
          f"hero effect markers {effects}, expected {HERO_EFFECTS} — motion.ts binds them by line position")
    check(dots == [w.lower() for w in words], f"data-dot follows the word: {dots}", f"hero data-dot {dots} != words {words}")

    print("9. project pages: '← Back to work' -> the entry's first pillar section")
    wrong, targets = [], {}
    for slug, d in live:
        html = (DIST / "project" / slug / "index.html").read_text(encoding="utf-8")
        m = re.search(r'<a href="/#([a-z]+)"[^>]*>← Back to work</a>', html)
        want = (d.get("pillars") or ["visual"])[0]
        if not m or m.group(1) != want or want not in ids:
            wrong.append(f"{slug}: {m.group(1) if m else None} (want #{want})")
        else:
            targets[want] = targets.get(want, 0) + 1
    check(not wrong, f"{len(live)} pages: " + ", ".join(f"#{k}×{v}" for k, v in sorted(targets.items())),
          f"Back to work: {wrong}")

    print(f"\n{'OK' if not failures else f'{len(failures)} FAILURE(S)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
