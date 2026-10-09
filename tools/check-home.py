#!/usr/bin/env python3
"""Check the built site for the v2 homepage order, titles, og:image and reference integrity.

    cd app && npm run build && cd ..
    python3 tools/check-home.py [--code slug,slug,...] [--online]

--code            the exact Code-section slugs expected on the homepage, in order. Default:
                  EXPECT_CODE below (the user's decision); the content entries (featured: true,
                  pillar code, by order) must produce the same list.
--online          + every external link on the homepage answers 200 (and, v3-G, the Code cards'
                  direct links answer 200 to a plain `curl -sL`)

Written for v2 subtask C (2026-10-08): Code leads the homepage (Code · Motion · Visual), the
Code section shows only `featured` products, and the title follows the same order. Any change
to section order, card selection, the header nav, titles or brand/media file names should pass
this before commit. Only reads app/src/content/projects, app/public and the build output.
Extended by subtask E (same day): Code = exactly 3 cards, hero words, old names, Back to work.

Checks (exit code 1 on any failure):
  1. homepage <main> pillar sections are #code, #motion, #visual in that order; cards per
     section follow the rule in index.astro (Code: featured only; Motion / Visual: first 3 by
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
  8. hero headline words follow HERO_ORDER (Motion · Visual · Code — kept on purpose); motion.ts animates the lines by
     POSITION, so data-mask / data-blur / data-type stay on lines 1 / 2 / 3, while each dot's
     data-dot (its personality in global.css and motion.ts) follows its word
  9. every project page's "← Back to work" points at its first pillar's homepage section

v3 subtask F (2026-10-08) — brand first, portfolio second. Check 1 looks at the pillar sections
only, and:
 10. layout: hero → "Products" label → #code → "Work" label → #motion → #visual → AI Ask; the pillar
     sections are the only <section id> in <main> (v3-G removed F's product strip; a "latest from
     the blog" block was planned and dropped by the user the same day)
 11. hero line = HERO_TAGLINE in index.astro (one constant, still open for the user to change) and
     the old job-title line is gone; the two hero buttons; their fade is opacity only
 12. v3-G (same day; user: the strip and the Code cards were the same three products in two visual
     languages). Nothing of the strip is left: no #products section, strip icon, "Details →",
     strip one-liner, strip button label or boxed-card class. Instead each Code card has its direct
     links in one row right after the card's <a> — outside it; no <a> inside an <a> anywhere on the
     page: MotionPilot → Adobe Exchange, MotionRules → motionrules.com, Cubby → App Store · Google
     Play. Each is one of the entry's `links`, opens a new tab (target=_blank, rel=noopener
     noreferrer), has the footer row's type (text-sm uppercase tracking-wide; mist, paper on hover),
     no pill border or accent fill; the row's fade is opacity only. Motion / Visual cards: no row.
     No digits in the hero copy or the rows (no counts, ever)
 13. labels in F's markup: "Products" right before #code, "Work" right before #motion
 14. footer on every page: ONE row of small links — X · GitHub · Steam · Blog · MotionRules · Cubby ·
     Email, all with the same classes (user: the sites are plain links, no emphasis;
     an earlier bold row of site names was rejected); Blog exactly once; no other footer links
 15. JSON-LD: the homepage carries exactly Organization + Person + WebSite, tied by @id
     (founder / worksFor / affiliation / publisher); the logo is a real square file; on every
     built page every @id reference resolves to a node defined on that page
 Nothing clickable in the new blocks may carry a translate / scale / rotate / animate class.
 16. --online, see above
"""
from __future__ import annotations

from html import unescape
import json
import re
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
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
HERO_ORDER = ["motion", "visual", "code"]  # hero keeps the original cadence on purpose (user, 2026-10-08)
FEATURED_ONLY = {"code"}
MAX_CARDS = 3  # user 2026-10-08: every section shows 3 (large card + one row)
# User, 2026-10-08: Code shows 3 cards (symmetric grid); openwebui-cliproxy-gateway only on /works.
EXPECT_CODE = ["motionpilot", "motionrules", "cubby"]
TITLE = "zosc — Code · Motion · Visual"
OLD_TITLE_ORDER = "Motion · Visual · Code"
# Old file names / domain that must not ship: the pre-rename logo and favicon files, and the
# MotionSheet domain replaced by motionrules.com/app (the slug zerb-cc-cd is protected and stays).
OLD_NAMES = ("zerb-logo", "zerb-favicon", "zerb.cc.cd")
HERO_EFFECTS = ["data-mask", "data-blur", "data-type"]  # motion.ts: line 1, 2, 3 — by position
DEFAULT_OG = f"{SITE}/media/images/common/brand/og-default.png"
# Homepage only (2026-10-09): Google's search thumbnail must be square, opaque, text-free and
# not a logo, so the homepage uses a 1080x1080 crop of dynamic-weather-art for og:image and
# WebPage.primaryImageOfPage; every other non-product page keeps DEFAULT_OG.
HOME_THUMB = f"{SITE}/media/images/common/brand/home-thumb.jpg"

# v3-F (2026-10-08) — the brand-first homepage.
OLD_HERO_LINE = "zosc is a motion designer, visual artist & creative developer. Ask the AI anything."
EXPECT_HERO_ACTIONS = [
    ("Get MotionPilot", "https://exchange.adobe.com/apps/cc/205857"),
    ("Open MotionRules", "https://motionrules.com/"),
]
# v3-G (2026-10-08): the product strip is gone; each Code card carries its direct links instead.
# In card order: slug -> (label, url). The labels and urls are the entries' own `links`.
EXPECT_DIRECT = {
    "motionpilot": [("Adobe Exchange", "https://exchange.adobe.com/apps/cc/205857")],
    "motionrules": [("motionrules.com", "https://motionrules.com/")],
    "cubby": [
        ("App Store", "https://apps.apple.com/app/id6804703410"),
        ("Google Play", "https://play.google.com/store/apps/details?id=com.zerblion.findly"),
    ],
}
# What F's strip put on the page (5ea1709) — none of it may come back.
STRIP_LEFTOVERS = {
    "#products section": r'<section id="products"',
    "strip icons": r"/media/images/products/",
    '"Details →" links': r"Details\s*→",
    "strip buttons": r"Get on Adobe Exchange|Open motionrules\.com",
    "boxed-card classes": r"rounded-2xl border border-line bg-ink-soft",
    "strip one-liners": r"applies your motion spec to keyframes|from definition to Lottie handoff|note it in one line, find it later",
}
ROW_TYPE = {"text-sm"}  # the footer link row's type classes (2026-10-09: no uppercase — names keep their casing, generic words lowercase)
LABEL_CLASS = "mx-auto max-w-[1400px] text-xs uppercase tracking-widest text-mist"  # F's "Work" label
# a card's direct links follow the card's <a> immediately, outside it (CardLinks.astro)
CARD_RE = re.compile(r'<a href="/project/([^/"]+)/"[^>]*>.*?</a>(\s*<p class="([^"]*\bcard-links\b[^"]*)"[^>]*>(.*?)</p>)?', re.S)
BLOG = "https://blog.zosc.com"
# The footer's single row, in order (MakerLion removed at the user's request, 2026-10-08).
EXPECT_FOOTER = [
    ("X", "https://x.com/byzosc"),
    ("GitHub", "https://github.com/byzosc"),
    ("Behance", "https://www.behance.net/zosc"),  # 2026-10-09: in sameAs, was missing from the footer
    ("Steam", "https://steamcommunity.com/id/byzosc"),
    ("blog", f"{BLOG}/"),
    ("MotionRules", "https://motionrules.com/"),
    ("Cubby", "https://byzosc.github.io/findly-site/"),
    ("email", "mailto:hi@zosc.com"),
]
ORG_ID, PERSON_ID, WEBSITE_ID = f"{SITE}/#organization", f"{SITE}/#person", f"{SITE}/#website"
# classes that move an element; AGENTS.md: a link that moves between mousedown and mouseup loses the click
MOVING = re.compile(r"(?:^|[\s:])-?(?:translate|scale|rotate|skew)-|(?:^|[\s:])animate-")
UA = "Mozilla/5.0 (X11; Linux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
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


A_RE = re.compile(r"<a\s([^>]*)>(.*?)</a>", re.S)


def anchors(html: str) -> list[dict]:
    """Every <a> in html: href, visible text (the arrow glyphs → and ↗ dropped), raw attributes, class, inner HTML."""
    out = []
    for attrs, inner in A_RE.findall(html):
        href = re.search(r'href="([^"]*)"', attrs)
        cls = re.search(r'class="([^"]*)"', attrs)
        text = unescape(re.sub(r"<[^>]+>", "", inner)).replace("→", "").replace("↗", "")
        out.append({"href": unescape(href.group(1)) if href else None, "text": " ".join(text.split()),
                    "attrs": attrs, "cls": cls.group(1) if cls else "", "inner": inner})
    return out


def opens_safely(a: dict) -> bool:
    return 'target="_blank"' in a["attrs"] and bool(re.search(r'rel="[^"]*\bnoopener\b', a["attrs"]))


def block(html: str, start_marker: str, end_tag: str = "</section>") -> str:
    i = html.find(start_marker)
    return html[i: html.find(end_tag, i)] if i >= 0 else ""


def visible_text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", " ", html, flags=re.S))).split())


def ld_blocks(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S)]


def id_refs(node, top: bool = True) -> list[str]:
    """Every @id used as a reference inside a JSON-LD node (its own top-level @id excluded)."""
    found = []
    if isinstance(node, dict):
        if not top and "@id" in node:
            found.append(node["@id"])
        for k, v in node.items():
            if k != "@id":
                found += id_refs(v, top=False)
    elif isinstance(node, list):
        for v in node:
            found += id_refs(v, top=False)
    return found


def png_size(path: Path) -> tuple[int, int] | None:
    head = path.read_bytes()[:24]
    return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else None


def http_status(url: str) -> str:
    """Final status after redirects (GET, browser UA). One retry on 429 — Steam rate-limits bots."""
    for attempt in range(2):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                res.read(2048)
                return f"{res.status}" + (f" -> {res.url}" if res.url != url else "")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(8)
                continue
            return f"{e.code}"
        except Exception as e:  # noqa: BLE001 - report, don't crash
            return f"ERR {type(e).__name__}: {e}"
    return "ERR"


def main() -> int:
    expect_code = EXPECT_CODE
    online = "--online" in sys.argv
    if "--code" in sys.argv:
        expect_code = sys.argv[sys.argv.index("--code") + 1].split(",")

    entries = {p.stem: frontmatter(p) for p in sorted(ENTRIES.glob("*.md"))}
    live = sorted(((s, d) for s, d in entries.items() if not d.get("draft")), key=lambda sd: sd[1].get("order", 100))
    home = (DIST / "index.html").read_text(encoding="utf-8")

    print("1. homepage section order + cards")
    main_html = home[home.find("<main"): home.find("</main>")]
    sections = [(m.group(1), m.end()) for m in re.finditer(r'<section id="([a-z]+)"', main_html)]
    ids = [s for s, _ in sections]
    pillar_ids = [s for s in ids if s in ORDER]  # check 10: and nothing else
    check(pillar_ids == ORDER, f"pillar sections: {' → '.join('#' + i for i in pillar_ids)}",
          f"pillar sections {pillar_ids} != {ORDER}")
    for sid, start in sections:
        if sid not in ORDER:
            continue
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
    # Header logo is inline SVG since 2026-10-09: an <img> logo was picked by Google as the
    # homepage's search thumbnail (letterboxed, grey bars). No logo <img> may come back.
    head = home[home.find('<header id="masthead"'): home.find("</header>")]
    check("<svg" in head and 'aria-label="zosc"' in head and "<img" not in head,
          "header logo is inline SVG (no <img> in the masthead — Google can't pick it as thumbnail)",
          "header logo is not inline SVG, or the masthead contains an <img>")

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
    want_og = lambda p: HOME_THUMB if p.relative_to(DIST).as_posix() == "index.html" else DEFAULT_OG
    bad = [str(p.relative_to(DIST)) for p in others if meta(p.read_text(encoding="utf-8"), "property", "og:image") != want_og(p)]
    older = sum(1 for _, d in live if d.get("kind") != "product")
    check(not bad, f"homepage og:image = home-thumb; {len(others) - 1} other non-project pages + {older} older project pages keep the default",
          f"non-project pages with the wrong og:image: {bad}")
    thumb = PUBLIC / "media/images/common/brand/home-thumb.jpg"
    check(thumb.is_file(), "home-thumb.jpg present in public/", "home-thumb.jpg missing")

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
    check([w.lower() for w in words] == HERO_ORDER, f"words: {' / '.join(words)}", f"hero words {words}, expected {HERO_ORDER}")
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

    # ── v3-F (2026-10-08): brand first, portfolio second ────────────────────────────────────────
    moving: list[str] = []  # clickable elements in the new blocks that carry a motion class

    print("10. v3 homepage layout")
    want_ids = list(ORDER)  # v3-G: no #products section any more
    check(ids == want_ids, f"sections: {' → '.join('#' + i for i in ids)} (nothing else)", f"sections {ids}, expected {want_ids}")
    marks = {
        "hero": main_html.find("data-hero"),
        "Products label": main_html.find('<div id="products"'),
        "#code": main_html.find('<section id="code"'),
        "Work label": main_html.find('<div id="work"'),
        "#motion": main_html.find('<section id="motion"'),
        "#visual": main_html.find('<section id="visual"'),
        "AI Ask": main_html.find("data-ask-ai"),
    }
    pos = list(marks.values())
    check(all(p >= 0 for p in pos) and pos == sorted(pos), "order: " + " → ".join(marks),
          f"block positions {marks}")

    print("11. hero line + actions")
    src = (APP / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    m = re.search(r"const HERO_TAGLINE = '([^']+)';", src)
    tagline = m.group(1) if m else None
    hero = block(main_html, "data-hero")
    line = re.findall(r"</h1>\s*<p[^>]*>([^<]*)</p>", hero)
    check(bool(tagline) and line == [tagline], f'line under the headline = HERO_TAGLINE "{tagline}"',
          f"hero line {line}, HERO_TAGLINE {tagline!r}")
    check(OLD_HERO_LINE not in home, "old job-title line gone", "old hero line still on the homepage")
    cta = re.search(r"<div data-hero-cta[^>]*>(.*?)</div>", hero, re.S)
    acts = anchors(cta.group(1)) if cta else []
    got = [(a["text"], a["href"]) for a in acts]
    check(got == EXPECT_HERO_ACTIONS, f"buttons: {got}", f"hero buttons {got}, expected {EXPECT_HERO_ACTIONS}")
    check(bool(acts) and all(opens_safely(a) for a in acts), 'both open in a new tab (target=_blank, rel=noopener)',
          "a hero button lacks target=_blank / rel=noopener")
    moving += [f"hero {a['text']}" for a in acts if MOVING.search(a["cls"])]
    css = "".join(p.read_text(encoding="utf-8") for p in DIST.rglob("*.css"))
    fade = re.search(r"@keyframes heroFade\{(.*?)\}\}", css)
    rule = re.search(r"\[data-hero\]>\[data-hero-cta\]\{([^}]*)\}", css)
    check(bool(fade) and "transform" not in fade.group(1) and bool(rule) and "heroFade" in rule.group(1),
          f"buttons fade in, opacity only: {{{rule.group(1) if rule else ''}}} / heroFade{{{fade.group(1) if fade else ''}}}}}",
          f"hero button fade: rule {rule.group(1) if rule else None}, keyframes {fade.group(1) if fade else None}")

    print("12. no product strip; the Code cards carry the direct links (v3-G)")
    left = [k for k, rx in STRIP_LEFTOVERS.items() if re.search(rx, home)]
    check(not left, "nothing of the strip on the homepage: " + ", ".join(STRIP_LEFTOVERS),
          f"strip leftovers on the homepage: {left}")
    page = re.sub(r"<script\b.*?</script>", "", home, flags=re.S)
    depth = deepest = 0
    for m in re.finditer(r"<a\b|</a>", page):
        depth += 1 if m.group(0) == "<a" else -1
        deepest = max(deepest, depth)
    check(deepest == 1 and depth == 0, f"no <a> inside an <a> ({page.count('</a>')} links on the page)",
          f"nested or unbalanced <a>: deepest {deepest}, final depth {depth}")

    def pill_or_fill(token: str) -> bool:
        base = token.split(":")[-1]
        return base == "border" or base.startswith(("border-", "bg-", "rounded")) or base == "text-accent"

    rows_html = ""
    for sid, start in sections:
        if sid not in ORDER:
            continue
        body = main_html[start: main_html.find("</section>", start)]
        cards = [(m.group(1), m.group(3) or "", m.group(4)) for m in CARD_RE.finditer(body)]
        if sid != "code":
            with_row = [slug for slug, _, row in cards if row is not None]
            ext = [a["href"] for a in anchors(body) if (a["href"] or "").startswith("http")]
            check(not with_row and "card-links" not in body and not ext,
                  f"#{sid}: {len(cards)} cards, no direct-link row (their entries have no `links`)",
                  f"#{sid}: rows on {with_row}, external links {ext}")
            continue
        check([c[0] for c in cards] == list(EXPECT_DIRECT), f"#code cards: {[c[0] for c in cards]}",
              f"#code cards {[c[0] for c in cards]}, expected {list(EXPECT_DIRECT)}")
        for slug, row_cls, row in cards:
            if row is None:
                fail(f"#code {slug}: no direct-link row right after the card's <a>")
                continue
            rows_html += row
            problems = []
            acts = anchors(row)
            got = [(a["text"], a["href"]) for a in acts]
            if got != EXPECT_DIRECT.get(slug):
                problems.append(f"links {got}, expected {EXPECT_DIRECT.get(slug)}")
            known = {l["url"] for l in (entries.get(slug, {}).get("links") or [])}
            if any(h not in known for _, h in got):
                problems.append(f"a link is not in {slug}.md links")
            if not all(opens_safely(a) and re.search(r'rel="[^"]*\bnoreferrer\b', a["attrs"]) for a in acts):
                problems.append("a link lacks target=_blank / rel=noopener noreferrer")
            if not all("↗" in a["inner"] for a in acts):
                problems.append("a link lacks its ↗")
            row_tokens = set(row_cls.split())
            # 2026-10-09 (user: the old quiet text row "didn't look like buttons"): each link is a
            # small pill in the hero secondary button's language — no accent FILL (bg-accent stays
            # the hero primary's alone), and no motion classes.
            # later on 2026-10-09 (user: no hierarchy vs the title — dim them): mist text, faint border
            PILL = {"rounded-full", "border", "border-white/10", "text-mist", "hover:border-white/40",
                    "hover:text-paper", "transition-colors", "uppercase", "tracking-wide"}
            for a in acts:
                miss = PILL - set(a["cls"].split())
                if miss:
                    problems.append(f"{a['text']!r} lacks pill classes {sorted(miss)}")
                if re.search(r"(?<![\w:-])bg-accent\b", a["cls"]):
                    problems.append(f"{a['text']!r} has an accent fill")
            if "reveal" in row_tokens or MOVING.search(row_cls):
                problems.append(f"the row itself moves: {row_cls!r}")
            moving.extend(f"{slug} {a['text']}" for a in acts if MOVING.search(a["cls"]))
            if problems:
                fail(f"#code {slug}: {'; '.join(problems)}")
            else:
                ok(f"#code {slug}: " + " · ".join(f"{t} ↗ {h}" for t, h in got)
                   + " (after the card's </a>, new tab, noopener noreferrer, small outline pill, no fill)")
    foot_row = re.search(r'<div class="([^"]*)">\s*(?:<a\s[^>]*>[^<]*</a>\s*)+</div>', block(home, "<footer", "</footer>"))
    foot_type = set(foot_row.group(1).split()) & ROW_TYPE if foot_row else set()
    check(foot_row is not None and not {"uppercase", "tracking-wide"} & set(foot_row.group(1).split()),
          "footer row: no uppercase / tracking-wide (names keep their casing)", "footer row still forces uppercase")
    check(foot_type == ROW_TYPE, f"row type = the footer link row's ({' '.join(sorted(ROW_TYPE))}; mist, paper on hover)",
          f"footer row type {sorted(foot_type)} != ROW_TYPE {sorted(ROW_TYPE)}")
    fades = re.findall(r"([^{}]*\.card-links[^{}]*)\{([^}]*)\}", css)
    # the minifier writes "@media(prefers-reduced-motion:no-preference){"
    gated = re.search(r"@media\s*\(prefers-reduced-motion:\s*no-preference\)\{[^@]*\.card-links", css)
    still = all("opacity" in b and not re.search(r"transform|translate|scale|rotate|animation", b) and ".reveal" in sel
                for sel, b in fades)
    check(len(fades) == 2 and still and bool(gated),
          "row fade = its card's reveal, opacity only, motion-allowed only: "
          + " / ".join(f"{sel.strip()}{{{b}}}" for sel, b in fades),
          f"card-links CSS {fades}, gated by no-preference: {bool(gated)}")
    digits = re.findall(r"\d[\d,.]*\s*\S*", visible_text(hero + rows_html))
    check(not digits, "no digits in the hero copy or the rows (no counts)", f"digits in hero / row copy: {digits}")

    print("13. section labels (F's markup)")
    label_cls = []
    for text, eid, sid in [("Products", "products", "code"), ("Work", "work", "motion")]:
        m = re.search(rf'<div id="{eid}"[^>]*>\s*<p class="([^"]*)">\s*{text}\s*</p>\s*</div>\s*(?:<!--.*?-->\s*)*<section id="{sid}"',
                      main_html, re.S)
        label_cls.append(m.group(1) if m else None)
        check(bool(m), f'"{text}" label (#{eid}) directly before #{sid}', f'"{text}" label missing or not directly before #{sid}')
    check(label_cls == [LABEL_CLASS, LABEL_CLASS], f'both labels: class "{LABEL_CLASS}" (uppercase on screen)',
          f"label classes {label_cls}, want F's {LABEL_CLASS!r}")

    print("14. footer: one row of plain links (every page)")
    pages, bad_footer = 0, []
    for p in html_files:
        html = p.read_text(encoding="utf-8")
        foot = block(html, "<footer", "</footer>")
        if not foot:
            continue
        pages += 1
        links = anchors(foot)
        rows = re.findall(r'<div class="([^"]*)">\s*((?:<a\s[^>]*>[^<]*</a>\s*)+)</div>', foot)
        why = []
        if [(a["text"], a["href"]) for a in links] != EXPECT_FOOTER:
            why.append(f"links {[(a['text'], a['href']) for a in links]}")
        if len(rows) != 1 or len(anchors(rows[0][1])) != len(EXPECT_FOOTER):
            why.append(f"{len(rows)} link rows (want one row holding all {len(EXPECT_FOOTER)})")
        if len({a["cls"] for a in links}) != 1:
            why.append(f"links styled differently: {sorted({a['cls'] for a in links})}")
        if not all(opens_safely(a) for a in links if (a["href"] or "").startswith("http")):
            why.append("an external link lacks target=_blank / rel=noopener")
        moving += [f"footer {a['text']}" for a in links if MOVING.search(a["cls"])]
        if why:
            bad_footer.append(f"{p.relative_to(DIST)}: {'; '.join(why)}")
    check(pages > 0 and not bad_footer,
          f"{pages} pages: one row, same style: {' · '.join(t for t, _ in EXPECT_FOOTER)} (Blog once)",
          f"footer: {bad_footer[:3]}")
    check(not moving, "no translate / scale / rotate / animate class on any new link or button",
          f"moving clickable elements: {moving}")

    print("15. JSON-LD entities")
    blocks = ld_blocks(home)
    by_type = {b.get("@type"): b for b in blocks}
    types = sorted(str(b.get("@type")) for b in blocks)
    check(types == ["Organization", "Person", "WebPage", "WebSite"], f"homepage blocks: {types}", f"homepage JSON-LD blocks {types}")
    wp = by_type.get("WebPage", {})
    pi = (wp.get("primaryImageOfPage") or {}).get("url")
    check(pi == HOME_THUMB and wp.get("isPartOf") == {"@id": WEBSITE_ID},
          f"WebPage.primaryImageOfPage = {pi.replace(SITE, '') if pi else pi}, isPartOf WebSite",
          f"WebPage.primaryImageOfPage {pi} / isPartOf {wp.get('isPartOf')}")
    org, person, site = by_type.get("Organization", {}), by_type.get("Person", {}), by_type.get("WebSite", {})
    check((org.get("@id"), person.get("@id"), site.get("@id")) == (ORG_ID, PERSON_ID, WEBSITE_ID),
          f"@id {ORG_ID} / {PERSON_ID} / {WEBSITE_ID}",
          f"@ids {org.get('@id')} / {person.get('@id')} / {site.get('@id')}")
    links = {
        "Organization.founder": (org.get("founder"), PERSON_ID),
        "Person.worksFor": (person.get("worksFor"), ORG_ID),
        "Person.affiliation": (person.get("affiliation"), ORG_ID),
        "WebSite.publisher": (site.get("publisher"), ORG_ID),
    }
    wrong = [k for k, (v, want) in links.items() if v != {"@id": want}]
    check(not wrong, "references by @id only: " + ", ".join(f"{k} → {want.split('/')[-1]}" for k, (_, want) in links.items()),
          f"wrong or missing references: {wrong}")
    logo = str(org.get("logo", ""))
    logo_file = PUBLIC / logo.replace(SITE, "", 1).lstrip("/") if logo.startswith(SITE + "/") else None
    size = png_size(logo_file) if logo_file and logo_file.is_file() else None
    check(bool(size) and size[0] == size[1] >= 112, f"Organization.logo {logo.replace(SITE, '')} {size} (square, >= 112 px)",
          f"Organization.logo {logo!r}: {size}")
    check(org.get("name") == person.get("name") == "zosc" and org.get("sameAs") == person.get("sameAs")
          and len(person.get("sameAs") or []) == 5,
          "Organization and Person: name zosc, the same 5 sameAs", "Organization / Person name or sameAs differ")
    dangling, entity_pages = [], 0
    for p in html_files:
        bl = ld_blocks(p.read_text(encoding="utf-8"))
        if not bl:
            continue
        entity_pages += 1
        defined = {b.get("@id") for b in bl if "@id" in b}
        missing = sorted({r for b in bl for r in id_refs(b)} - defined)
        if missing or not {ORG_ID, PERSON_ID, WEBSITE_ID} <= defined:
            dangling.append(f"{p.relative_to(DIST)}: missing {missing or sorted({ORG_ID, PERSON_ID, WEBSITE_ID} - defined)}")
    check(not dangling, f"{entity_pages} pages define the three entities and every @id reference resolves on its page",
          f"dangling @id references: {dangling[:3]}")

    if online:
        print("16. online: every external link on the homepage (GET, redirects followed)")
        urls = list(dict.fromkeys(a["href"] for a in anchors(home) if a["href"] and a["href"].startswith("http")))
        for url in urls:
            status = http_status(url)
            print(f"   {status.split()[0]:>4}  {url}" + (f"  {status.split(' ', 1)[1]}" if " " in status else ""))
            if not status.startswith("200"):
                fail(f"{url} -> {status}")
        print("    v3-G: the Code cards' direct links, plain `curl -sL` (curl's own user agent)")
        for slug, pairs in EXPECT_DIRECT.items():
            for label, url in pairs:
                try:
                    r = subprocess.run(["curl", "-sL", "-o", "/dev/null", "--max-time", "30", "-w", "%{http_code} %{url_effective}", url],
                                       capture_output=True, text=True, timeout=60)
                    code, _, final = r.stdout.partition(" ")
                except Exception as e:  # noqa: BLE001 - report, don't crash
                    code, final = f"ERR {type(e).__name__}", ""
                print(f"   {code:>4}  {slug} · {label}: {url}" + (f"  -> {final}" if final and final != url else ""))
                if code != "200":
                    fail(f"curl -sL {url} -> {code}")

    print(f"\n{'OK' if not failures else f'{len(failures)} FAILURE(S)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
