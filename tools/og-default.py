#!/usr/bin/env python3
"""Render the site's default share image: og:image / twitter:image of every page without its own
raster cover (home, about, works, 404, the older project pages, the SVG-cover products; the blog
redirects are Vercel redirects with no HTML of their own). v3 subtask H, 2026-10-08.

    python3 tools/og-default.py --work ~/render-tmp/og-default        # render both PNGs + check them
    python3 tools/og-default.py --check                                # only check the committed PNGs
    python3 tools/og-default.py --work ~/render-tmp/og-default --preview .render-tmp/og-preview
                                     # + dark / light mock-ups: search thumbnail tiles and a share card

Writes into app/public/media/images/common/brand/:
    og-default.png          1200 x 630    og:image in Layout.astro (1.91:1, the large-card ratio of
                                          X / Facebook / LinkedIn / Slack)
    og-default-square.png   1200 x 1200   the same card at 1:1. NOT referenced by any page yet (see
                                          docs/v3/H-REPORT.md: Google letterboxes its square result
                                          thumbnail with grey bars, measured 2026-10-08; only a
                                          square image fills it)

The card: flat #050505; the Z mark (the path in app/public/favicon.svg) in #f4f3ef; the lowercase
wordmark "zosc" in Montserrat 800, -0.02em like the site's headings, with the hero's accent dot
after it (the only #e7503a on the card; same geometry as .hero-dot in global.css: 0.17em wide,
0.04em after the word, standing on the baseline); under it HERO_TAGLINE from
app/src/pages/index.astro in Mulish, mist grey. Everything on one centre axis; the dot hangs
outside the centring, like hanging punctuation, so "zosc" itself sits under the mark.

Checks (exit 1 on any failure; run after every render and by --check):
  1. exact size; PNG colour type 2 (8-bit RGB, no alpha channel at all) -> every pixel is opaque
  2. all four corners exactly #050505
  3. all ink >= 80 px from every edge; on the 1200x630 card all ink is also inside the centre
     630 x 630 square, so cropping the middle square for a thumbnail cuts nothing
  4. no colour anywhere except one small blob, the accent dot (this also catches LCD subpixel
     text antialiasing, whose colour fringes run along every glyph edge)
  5. file <= 300 KB
  6. the tagline stored in the PNG (tEXt "zosc:tagline") is the current HERO_TAGLINE, and
     Layout.astro's og:image:alt quotes it -> a changed hero line can't leave a stale card behind

Why it is built this way:
  - The type is set by Chromium, on a <canvas>, from the site's own self-hosted variable fonts
    embedded as data: URIs: same shaping, kerning and weight axis as the live site, no request
    to wait for. measureText() gives the real ink box, so the spacing below is ink to ink, not
    line box to line box (an all-x-height word like "zosc" has a lot of empty line box above it).
  - The canvas is a default (alpha) one. The first render used { alpha: false }, and Chromium then
    draws text with LCD subpixel antialiasing: blue / orange fringes on every glyph edge. Check 4
    keeps it from coming back.
  - document.fonts.check() is true for a family with no @font-face at all (tested 2026-10-08:
    check() true, load() 0 faces), so it can't prove the font loaded; the page checks the FontFace
    objects that load() returns instead, and refuses to draw anything with a fallback face.
  - The pixels come back through --dump-dom as a data: URL, not through --screenshot: no
    viewport sizing or device-scale questions, the PNG is exactly the canvas.
  - Chromium here is a snap: it cannot read /tmp or dot-directories (worktrees live under
    .claude/). The page and a throwaway profile go to --work under the home directory (own
    profile dir: two Chromium runs sharing one profile collide on its lock); --work must not
    exist yet and is removed afterwards.
  - The result is re-encoded by PIL as plain RGB. A transparent PNG lets each consumer choose
    the fill: Google drew the transparent header logo on black (2026-10-08 screenshot); a
    consumer that fills with white would make white-on-transparent disappear.
"""

import argparse
import base64
import html
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
BRAND = APP / "public" / "media" / "images" / "common" / "brand"
FONTS = APP / "public" / "fonts"
OUT_WIDE = BRAND / "og-default.png"
OUT_SQUARE = BRAND / "og-default-square.png"

INK, PAPER, MIST, ACCENT = "#050505", "#f4f3ef", "#a1a1aa", "#e7503a"  # global.css @theme tokens
INK_RGB, ACCENT_RGB = (5, 5, 5), (231, 80, 58)
SAFE = 80          # px kept clear on every edge
MAX_BYTES = 300 * 1024
TAG_KEY = "zosc:tagline"

# Wide card, in px. Gaps are ink to ink: mark bottom -> top of the x-height; baseline of "zosc" ->
# top of the tagline's tallest glyph. Sized so the tagline (24.1 em wide in Mulish) stays inside
# the centre 630 px square.
WIDE = {"w": 1200, "h": 630, "mark": 168, "gap1": 50, "word": 148, "gap2": 56, "tag": 24}
# Square card: the same card scaled by 5/3 (tagline 40 px: ~956 px of ink, ~122 px from each side).
SQUARE = {k: (v if k == "w" else round(v * 5 / 3)) for k, v in WIDE.items()} | {"h": 1200}

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><style>
@font-face { font-family: "OG Display"; font-weight: 100 900; src: url(data:font/woff2;base64,__DISPLAY__) format("woff2"); }
@font-face { font-family: "OG Body"; font-weight: 100 1000; src: url(data:font/woff2;base64,__BODY__) format("woff2"); }
</style></head><body><pre id="out">PENDING</pre><script>
const SPEC = __SPEC__;
(async () => {
  const out = document.getElementById("out");
  try {
    const word = `800 ${SPEC.word}px "OG Display"`, tag = `400 ${SPEC.tag}px "OG Body"`;
    const faces = [...await document.fonts.load(word, "zosc"), ...await document.fonts.load(tag, SPEC.tagline)];
    if (faces.length !== 2 || faces.some((f) => f.status !== "loaded")) throw new Error("web fonts did not load");

    const c = document.createElement("canvas");
    c.width = SPEC.w; c.height = SPEC.h;
    // Default (alpha) canvas on purpose: an opaque { alpha: false } canvas makes Chromium draw text
    // with LCD subpixel antialiasing -> blue / orange fringes on every glyph edge (first render).
    const ctx = c.getContext("2d");
    ctx.fillStyle = SPEC.ink; ctx.fillRect(0, 0, SPEC.w, SPEC.h);
    ctx.textBaseline = "alphabetic"; ctx.textAlign = "left"; ctx.fontKerning = "normal";

    ctx.font = word; ctx.letterSpacing = `${-0.02 * SPEC.word}px`;
    const mw = ctx.measureText("zosc");
    ctx.font = tag; ctx.letterSpacing = "0px";
    const mt = ctx.measureText(SPEC.tagline);

    const markW = SPEC.mark * SPEC.vbW / SPEC.vbH;
    const groupH = SPEC.mark + SPEC.gap1 + mw.actualBoundingBoxAscent + SPEC.gap2
      + mt.actualBoundingBoxAscent + mt.actualBoundingBoxDescent;
    const top = Math.round((SPEC.h - groupH) / 2);

    // Z mark: favicon.svg's path, scaled from its viewBox; whole-pixel top and height keep the
    // flat top and bottom edges crisp.
    const s = SPEC.mark / SPEC.vbH;
    ctx.save(); ctx.translate(SPEC.w / 2 - markW / 2, top); ctx.scale(s, s);
    ctx.fillStyle = SPEC.paper; ctx.fill(new Path2D(SPEC.d), SPEC.rule); ctx.restore();

    // Wordmark: the ink of "zosc" centred on the axis (actualBoundingBoxLeft is negative when the
    // ink starts right of the origin).
    const wordBase = Math.round(top + SPEC.mark + SPEC.gap1 + mw.actualBoundingBoxAscent);
    const wordInk = mw.actualBoundingBoxLeft + mw.actualBoundingBoxRight;
    const wx = SPEC.w / 2 - wordInk / 2 + mw.actualBoundingBoxLeft;
    ctx.font = word; ctx.letterSpacing = `${-0.02 * SPEC.word}px`;
    ctx.fillStyle = SPEC.paper; ctx.fillText("zosc", wx, wordBase);

    // The hero dot: left edge 0.04em after the advance of the word, 0.17em across, on the baseline.
    const d = 0.17 * SPEC.word, dl = wx + mw.width + 0.04 * SPEC.word;
    ctx.fillStyle = SPEC.accent; ctx.beginPath();
    ctx.arc(dl + d / 2, wordBase - d / 2, d / 2, 0, Math.PI * 2); ctx.fill();

    // Tagline.
    const tagBase = Math.round(wordBase + SPEC.gap2 + mt.actualBoundingBoxAscent);
    const tagInk = mt.actualBoundingBoxLeft + mt.actualBoundingBoxRight;
    ctx.font = tag; ctx.letterSpacing = "0px"; ctx.fillStyle = SPEC.mist;
    ctx.fillText(SPEC.tagline, SPEC.w / 2 - tagInk / 2 + mt.actualBoundingBoxLeft, tagBase);

    out.textContent = JSON.stringify({ ok: true, png: c.toDataURL("image/png"), layout: {
      top, wordBase, tagBase, markW: +markW.toFixed(1), wordInk: +wordInk.toFixed(1),
      tagInk: +tagInk.toFixed(1), dot: [+(dl + d / 2).toFixed(1), +(wordBase - d / 2).toFixed(1), +d.toFixed(1)],
      faces: faces.map((f) => `${f.family} ${f.weight} ${f.status}`) } });
  } catch (e) {
    out.textContent = JSON.stringify({ ok: false, error: String(e) });
  }
})();
</script></body></html>
"""


def fail(msg):
    print(f"  FAIL {msg}")
    return False


def ok(msg):
    print(f"  ok   {msg}")
    return True


def hero_tagline():
    src = (APP / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    m = re.search(r"""const HERO_TAGLINE\s*=\s*(['"])(.*?)\1;""", src)
    if not m:
        sys.exit("HERO_TAGLINE not found in app/src/pages/index.astro")
    return m.group(2)


def z_mark():
    svg = (APP / "public" / "favicon.svg").read_text(encoding="utf-8")
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    d = re.search(r'\sd="([^"]+)"', svg).group(1)
    rule = "evenodd" if 'fill-rule="evenodd"' in svg else "nonzero"
    if vb[:2] != [0, 0]:
        sys.exit(f"favicon.svg viewBox {vb} does not start at 0 0; the placement maths assumes it does")
    return vb[2], vb[3], d, rule


def chromium():
    exe = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    if not exe:
        sys.exit("no chromium on PATH")
    return exe


def render(spec, work):
    """Draw one card in headless Chromium; return (PIL RGB image, layout numbers)."""
    page = (PAGE.replace("__DISPLAY__", base64.b64encode((FONTS / "montserrat-latin.woff2").read_bytes()).decode())
                .replace("__BODY__", base64.b64encode((FONTS / "mulish-latin.woff2").read_bytes()).decode())
                .replace("__SPEC__", json.dumps(spec)))
    f = work / f"card-{spec['w']}x{spec['h']}.html"
    f.write_text(page, encoding="utf-8")
    run = subprocess.run(
        [chromium(), "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
         f"--user-data-dir={work / 'profile'}", "--virtual-time-budget=15000", "--dump-dom", f.as_uri()],
        capture_output=True, text=True, timeout=180)
    m = re.search(r'<pre id="out">(.*?)</pre>', run.stdout, re.S)
    if not m:
        sys.exit(f"chromium returned no result (exit {run.returncode}):\n{run.stderr[-2000:]}")
    res = json.loads(html.unescape(m.group(1)))
    if not res.get("ok"):
        sys.exit(f"render failed: {res.get('error')}")
    raw = work / f"raw-{spec['w']}x{spec['h']}.png"
    raw.write_bytes(base64.b64decode(res["png"].split(",", 1)[1]))
    im = Image.open(raw)
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        im = Image.alpha_composite(Image.new("RGBA", im.size, INK_RGB + (255,)), im.convert("RGBA"))
    return im.convert("RGB"), res["layout"]


def save(im, path, tagline):
    meta = PngInfo()
    meta.add_text(TAG_KEY, tagline)
    im.save(path, format="PNG", optimize=True, pnginfo=meta)


def check(path, spec, tagline, centre_square):
    print(f"{path.relative_to(ROOT)}")
    w, h = spec["w"], spec["h"]
    good = True
    raw = path.read_bytes()
    # IHDR: width, height, bit depth, colour type at fixed offsets after the 8-byte signature.
    pw, ph, depth, ctype = struct.unpack(">IIBB", raw[16:26])
    good &= (ok if (pw, ph) == (w, h) else fail)(f"size {pw}x{ph} (want {w}x{h})")
    good &= (ok if (depth, ctype) == (8, 2) else fail)(
        f"PNG bit depth {depth}, colour type {ctype} (want 8 / 2 = RGB, no alpha channel)")
    good &= (ok if len(raw) <= MAX_BYTES else fail)(f"{len(raw) / 1024:.1f} KB (limit {MAX_BYTES // 1024} KB)")
    im = Image.open(path)
    stored = im.text.get(TAG_KEY) if hasattr(im, "text") else None
    im = im.convert("RGB")
    corners = {im.getpixel(p) for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]}
    good &= (ok if corners == {INK_RGB} else fail)(f"corners {sorted(corners)} (want {INK_RGB})")
    box = ImageChops.difference(im, Image.new("RGB", im.size, INK_RGB)).getbbox()
    if not box:
        return fail("no ink at all")
    l, t, r, b = box[0], box[1], w - box[2], h - box[3]
    good &= (ok if min(l, t, r, b) >= SAFE else fail)(
        f"ink box x {box[0]}-{box[2]}, y {box[1]}-{box[3]}; clear edges left {l} top {t} right {r} bottom {b} (min {SAFE})")
    if centre_square:
        x0, x1 = (w - h) // 2, (w + h) // 2
        good &= (ok if box[0] >= x0 and box[2] <= x1 else fail)(
            f"ink inside the centre square x {x0}-{x1}: {box[0] - x0} / {x1 - box[2]} px to spare")
    # Colour: everything is neutral grey except the accent dot. Any pixel whose channels differ by
    # more than 12 must belong to one compact blob, the dot (its antialiased rim included); this
    # also catches LCD subpixel text, whose colour fringes run along every glyph. (Mist #a1a1aa
    # itself differs by 9, its antialiased edges by less.)
    px = im.load()
    hot = [(x, y) for y in range(h) for x in range(w) if max(px[x, y]) - min(px[x, y]) > 12]
    exact = sum(1 for x, y in hot if px[x, y] == ACCENT_RGB)
    if hot:
        xs, ys = [p[0] for p in hot], [p[1] for p in hot]
        span = (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
        # one dot = at most its diameter (0.17em of the wordmark) plus antialiased edge pixels
        good &= (ok if exact and max(span) <= 0.17 * spec["word"] + 3 else fail)(
            f"colour only in one blob {span[0]}x{span[1]} px at x {min(xs)}-{max(xs)}, y {min(ys)}-{max(ys)} "
            f"(the dot, {exact} px exactly {ACCENT}); {len(hot)} non-grey px in all")
    else:
        good &= fail("no accent dot")
    good &= (ok if stored == tagline else fail)(f"tagline in PNG = HERO_TAGLINE: {stored!r}")
    return good


def check_layout_alt(tagline):
    src = (APP / "src" / "layouts" / "Layout.astro").read_text(encoding="utf-8")
    print("app/src/layouts/Layout.astro")
    m = re.search(r"""const ogImageAlt\s*=\s*(['"`])(.*?)\1""", src)
    good = (ok if m and tagline in m.group(2) else fail)(
        f"og:image:alt quotes the tagline: {m.group(2) if m else 'ogImageAlt not found'!r}")
    good &= (ok if "/media/images/common/brand/og-default.png" in src else fail)("default og:image is og-default.png")
    return good


def preview(work, outdir):
    """Dark and light mock-ups: search-result thumbnail tiles + a large share card."""
    def uri(p):
        return "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()

    # The current header logo, as Google drew it on 2026-10-08: transparent filled black.
    logo = Image.open(BRAND / "zosc-logo.png").convert("RGBA")
    flat = Image.alpha_composite(Image.new("RGBA", logo.size, (0, 0, 0, 255)), logo).convert("RGB")
    flat.save(work / "logo-on-black.png")
    imgs = {"now": uri(work / "logo-on-black.png"), "wide": uri(OUT_WIDE), "square": uri(OUT_SQUARE)}
    themes = {
        # dark: page and letterbox grey sampled from the user's screenshot (clip 0kzyncb5z0);
        # light: neutral stand-ins, not measured.
        "dark": {"label": "深色底", "bg": "#22242a", "fg": "#e8eaed", "sub": "#bdc1c6", "link": "#99c3ff",
                 "band": "#43444d", "card": "#000000", "cardline": "#2f3336", "measured": True},
        "light": {"label": "浅色底", "bg": "#ffffff", "fg": "#202124", "sub": "#4d5156", "link": "#1a0dab",
                  "band": "#e8eaed", "card": "#ffffff", "cardline": "#cfd9de", "measured": False},
    }
    shots = []
    for name, th in themes.items():
        note = "深色灰条色 #43444d 取自截图" if th["measured"] else "浅色模式灰条色为示意，未实测"
        tiles = [
            ("now", "contain", "现在：页头 logo<br>（即截图里那张）"),
            ("wide", "contain", "新横版 1200×630<br>若同样等比缩入"),
            ("wide", "cover", "新横版<br>若改为居中裁方"),
            ("square", "contain", "新方版 1200×1200<br>（未被引用，声明后才可能被取）"),
        ]
        tile_html = "".join(
            f'<figure><div class="t"><img src="{imgs[k]}" style="object-fit:{fit}"></div>'
            f"<figcaption>{cap}</figcaption></figure>" for k, fit, cap in tiles)
        page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:{th['bg']};color:{th['fg']};font-family:"Noto Sans CJK SC",Arial,sans-serif}}
body{{width:1000px;padding:36px 40px;box-sizing:border-box}}
h2{{font-size:20px;font-weight:600;margin:0 0 6px}} .n{{color:{th['sub']};font-size:14px;margin:0 0 20px}}
.row{{display:flex;gap:28px;align-items:flex-start;margin-bottom:40px}}
.res{{width:380px;font-family:Arial,sans-serif}} .res .u{{font-size:14px;color:{th['sub']}}}
.res .ti{{font-size:21px;color:{th['link']};margin:4px 0}} .res .s{{font-size:14px;color:{th['sub']};line-height:1.5}}
figure{{margin:0;width:120px;text-align:center}} figcaption{{font-size:12px;color:{th['sub']};margin-top:8px;line-height:1.4}}
.t{{width:92px;height:92px;margin:0 auto;border-radius:8px;overflow:hidden;background:{th['band']}}}
.t img{{width:100%;height:100%;display:block}}
.card{{width:506px;border:1px solid {th['cardline']};border-radius:16px;overflow:hidden;background:{th['card']}}}
.card img{{width:100%;display:block}} .card .m{{padding:10px 14px;font-family:Arial,sans-serif;font-size:14px;color:{th['sub']}}}
.card .m b{{display:block;color:{th['fg']};font-weight:400;margin-top:2px}}
.side{{font-size:13px;color:{th['sub']};line-height:1.6;width:380px}}
</style></head><body>
<h2>搜索结果缩略图（92×92 方框）· {th['label']}</h2>
<p class="n">10-08 截图实测：Google 把图等比缩进方框，空处补灰条（{note}）</p>
<div class="row"><div class="res"><div class="u">zosc.com · https://zosc.com</div>
<div class="ti">zosc — Code · Motion · Visual</div>
<div class="s">zosc — a motion designer, visual artist &amp; developer. Living interactive interfaces, motion, and visual art…</div></div>
{tile_html}</div>
<h2>分享卡（X / Slack 大图卡，约 506px 宽）</h2>
<p class="n">og:image = og-default.png，按 1.91:1 原样显示</p>
<div class="row"><div class="card"><img src="{imgs['wide']}"><div class="m">zosc.com<b>zosc — Code · Motion · Visual</b></div></div>
<div class="side">旧的默认 og:image 是 253×83 的透明 “ZERB” 字标（旧身份）；按 og:image / twitter:image 出卡的平台（X、Slack 等）取的就是它。</div></div>
</body></html>"""
        f = work / f"preview-{name}.html"
        f.write_text(page, encoding="utf-8")
        shot = work / f"og-preview-{name}.png"
        subprocess.run(
            [chromium(), "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
             "--hide-scrollbars", f"--user-data-dir={work / 'profile'}", "--force-device-scale-factor=2",
             "--window-size=1000,780", "--virtual-time-budget=8000", f"--screenshot={shot}", f.as_uri()],
            capture_output=True, text=True, timeout=180)
        if not shot.exists():
            sys.exit(f"preview screenshot {shot} was not written")
        outdir.mkdir(parents=True, exist_ok=True)
        shutil.copy(shot, outdir / shot.name)
        shots.append(outdir / shot.name)
    return shots


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", type=Path, help="scratch dir under $HOME (snap Chromium); must not exist; removed after")
    ap.add_argument("--check", action="store_true", help="only check the committed PNGs and Layout.astro")
    ap.add_argument("--preview", type=Path, help="also write dark / light mock-ups into this directory")
    ap.add_argument("--keep", action="store_true", help="keep --work (HTML, raw canvas PNGs) for inspection")
    a = ap.parse_args()
    tagline = hero_tagline()
    print(f"HERO_TAGLINE: {tagline}")

    if not a.check:
        if not a.work:
            sys.exit("--work is required to render (a new directory under your home directory)")
        work = a.work.expanduser().resolve()
        if work.exists():
            sys.exit(f"{work} already exists; pass a new directory (it is deleted afterwards)")
        work.mkdir(parents=True)
        try:
            vb_w, vb_h, d, rule = z_mark()
            for spec, out in ((WIDE, OUT_WIDE), (SQUARE, OUT_SQUARE)):
                spec = dict(spec, tagline=tagline, d=d, rule=rule, vbW=vb_w, vbH=vb_h,
                            ink=INK, paper=PAPER, mist=MIST, accent=ACCENT)
                im, layout = render(spec, work)
                save(im, out, tagline)
                print(f"rendered {out.relative_to(ROOT)}: {json.dumps(layout)}")
            if a.preview:
                for p in preview(work, a.preview.expanduser().resolve()):
                    print(f"preview {p}")
        finally:
            if a.keep:
                print(f"kept {work}")
            else:
                shutil.rmtree(work)

    good = check(OUT_WIDE, WIDE, tagline, centre_square=True)
    good &= check(OUT_SQUARE, SQUARE, tagline, centre_square=False)
    good &= check_layout_alt(tagline)
    print("ALL OK" if good else "FAILED")
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
