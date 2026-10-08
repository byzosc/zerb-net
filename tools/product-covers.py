#!/usr/bin/env python3
"""Rebuild the cover / body images of the Code-pillar product pages (v2 subtask B, 2026-10-08).

    python3 tools/product-covers.py                    # every product below
    python3 tools/product-covers.py cubby motionrules  # just these
    python3 tools/product-covers.py --keep             # keep ~/render-tmp/product-covers

Writes into app/public/media/images/projects/<slug>/ and prints size + bytes per file.
windows-never-sleep and s25edge-usa have hand-written cover.svg files instead (no image to use).

Decisions and pitfalls (read before "simplifying" this):
- Covers are banners at ~2.96:1 like the existing 950x320 cards, <= 1600 px wide, <= 400 KB.
- GitHub's *auto-generated* og:image (opengraph.githubassets.com) bakes live contributor /
  issue / STAR / fork counts into the picture: stale numbers on the portfolio (the brief bans
  star counts) and a white GitHub card on a dark grid. Only a *custom* social preview
  (repository-images.githubusercontent.com) is used as-is; otherwise a real product
  screenshot, or a hand-made SVG.
- MotionPilot: Adobe Exchange screenshots 1/3/5 and both motionrules.com posters show the
  panel header "MotionPilot by ZERB LION" (old brand; the CEP UI is not re-published yet).
  Only store shots 2 ("Spec" tab) and 4 ("Native AE controls") are clean; #2 is used (body
  figure + framed in the cover). A plain crop of #4 was tried as the cover: mostly empty AE chrome.
- zero-build-blog: the README screenshot AND the live blog header both still read
  "Zerb's Blog" / "Zerb's Notebook" -> cover = live blog cropped *below* the header.
- nas-monitoring: only the THERMALS band of the README dashboard is used. The lower panels
  (volume / CPU load / memory / UPS / fan) are roadmap metrics in the README, not what the
  JSON API serves today.
- Headless chromium here is a snap: it cannot read /tmp or dot-directories (this worktree
  lives under .claude/), so every render is written to ~/render-tmp/ and post-processed by
  Python. "Page load failed" in stderr = give up, don't loop.
- motionrules.com picks light/dark by *local time* (19:00-06:59 = dark), not by
  prefers-color-scheme -> chromium runs with TZ set to a zone where it is night.
- blog.zosc.com follows prefers-color-scheme -> --force-dark-mode + preferredColorScheme=0.
- Source URLs below are content-hashed; if the store listing / social preview is replaced,
  re-read the page and update them (the old ones may keep serving the old image).
"""
from __future__ import annotations

import datetime as _dt
import io
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "app" / "public" / "media" / "images" / "projects"
TMP = Path.home() / "render-tmp" / "product-covers"  # snap chromium can write here
MAX_BYTES = 400 * 1024
UA = {"User-Agent": "Mozilla/5.0 (zosc product-covers)"}

ADOBE_SHOTS = "https://d3awf6rem6b5na.cloudfront.net/distribute/media/205857/screenshots/"
MP_SHOT_SPEC = ADOBE_SHOTS + "205857-09c6115d-bde2-42a0-9b82-ab87900a8490.png"    # store #2
GATEWAY_OG = (  # custom social preview == social-preview.png in the repo
    "https://repository-images.githubusercontent.com/1282295508/73f9b25c-502e-47f7-9a69-ccde4b34f1e0"
)
NAS_DASHBOARD = "https://raw.githubusercontent.com/byzosc/nas-monitoring/main/docs/dashboard-preview.png"
CUBBY_DIR = Path("/data/Projects/Findly/exports/zosc-site")  # handed over by the Findly session


def fetch(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    return Image.open(io.BytesIO(data))


def night_tz() -> str:
    """An IANA zone where the local hour is currently 21-23 (motionrules -> dark theme)."""
    now = _dt.datetime.now(_dt.timezone.utc)
    for name in ("America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo",
                 "Pacific/Auckland", "Asia/Kolkata", "America/Sao_Paulo"):
        if 21 <= now.astimezone(ZoneInfo(name)).hour <= 23:
            return name
    for off in range(-12, 15):  # fall back to any fixed offset that lands at night
        if 21 <= (now + _dt.timedelta(hours=off)).hour <= 23:
            return f"Etc/GMT{'-' if off >= 0 else '+'}{abs(off)}"  # POSIX sign is inverted
    return "UTC"


def shot(url: str, name: str, width: int, height: int, scale: float = 1.0,
         dark_scheme: bool = False, tz: str | None = None) -> Image.Image:
    TMP.mkdir(parents=True, exist_ok=True)
    dest = TMP / name
    cmd = ["chromium", "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
           "--virtual-time-budget=10000", f"--screenshot={dest}", url]
    if dark_scheme:
        cmd[1:1] = ["--force-dark-mode", "--blink-settings=preferredColorScheme=0"]
    env = dict(os.environ, **({"TZ": tz} if tz else {}))
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
    if "Page load failed" in res.stderr or not dest.exists():
        sys.exit(f"chromium could not load {url}:\n{res.stderr[-800:]}")
    return Image.open(dest)


def save(im: Image.Image, slug: str, filename: str, quality: int = 86) -> None:
    folder = OUT / slug
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    if filename.endswith(".png"):
        im.save(path, optimize=True)
    else:
        im = im.convert("RGB")
        while True:
            im.save(path, quality=quality, optimize=True, progressive=True)
            if path.stat().st_size <= MAX_BYTES or quality <= 60:
                break
            quality -= 4
    size = path.stat().st_size
    flag = "" if size <= MAX_BYTES else "   <-- OVER 400 KB"
    print(f"{path.relative_to(REPO)}  {im.width}x{im.height}  {size // 1024} KB{flag}")


def crop_ratio(im: Image.Image, top: int, ratio: float = 2.96, left: int = 0, right: int | None = None):
    right = im.width if right is None else right
    width = right - left
    return im.crop((left, top, right, top + round(width / ratio)))


MP_COVER_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"Montserrat";font-weight:100 900;src:url("montserrat-latin.woff2") format("woff2")}
html,body{margin:0;width:1600px;height:540px;overflow:hidden;background:#050505}
.c{position:relative;width:1600px;height:540px;background:
  radial-gradient(ellipse 60% 95% at 76% 18%,rgba(231,80,58,.17),rgba(231,80,58,0) 70%),
  linear-gradient(135deg,#0e0e11,#050505)}
.g{position:absolute;inset:0;background-size:57px 57px;background-image:
  linear-gradient(to right,rgba(255,255,255,.035) 1px,transparent 1px),
  linear-gradient(to bottom,rgba(255,255,255,.035) 1px,transparent 1px)}
.m{font-family:ui-monospace,"DejaVu Sans Mono",Menlo,monospace}
.l{position:absolute;left:94px;top:126px;font-size:21px;letter-spacing:8px;color:#e7503a}
.w{position:absolute;left:88px;top:166px;font:800 96px/1 "Montserrat";letter-spacing:-2.5px;color:#f4f3ef}
.w b{color:#e7503a}
.s{position:absolute;left:96px;top:298px;font-size:23px;line-height:1.65;color:#a1a1aa}
.k{position:absolute;left:94px;top:428px;font-size:21px;letter-spacing:1.5px;color:#ff6f59}
.f{position:absolute;right:64px;top:70px;width:800px;height:400px;border-radius:22px;overflow:hidden;
  border:1px solid #26262b;box-shadow:0 30px 90px rgba(0,0,0,.65)}
.f img{display:block;width:100%;height:100%;object-fit:cover}
</style></head><body><div class="c"><div class="g"></div>
<div class="l m">AFTER EFFECTS · CODE</div>
<div class="w">MotionPilot<b>.</b></div>
<div class="s m">motion spec &rarr; AE keyframes<br>curves + durations, one token</div>
<div class="k m">Adobe Exchange &#8599;</div>
<div class="f"><img src="mp-frame.png" alt=""></div>
</div></body></html>"""


def motionpilot() -> None:
    spec = fetch(MP_SHOT_SPEC)  # 1360x800: Spec tab + selected keyframes, no old-brand header
    save(spec, "motionpilot", "spec-tab.jpg")
    # Cover = MotionSheet-style banner (same tokens as zerb-cc-cd/cover.svg) around a real
    # store screenshot; rendered by chromium so the wordmark uses the site's own Montserrat.
    TMP.mkdir(parents=True, exist_ok=True)
    spec.convert("RGB").crop((370, 262, 1360, 757)).save(TMP / "mp-frame.png")  # 2:1 = frame
    shutil.copy(REPO / "app" / "public" / "fonts" / "montserrat-latin.woff2", TMP)
    (TMP / "mp-cover.html").write_text(MP_COVER_HTML, encoding="utf-8")
    im = shot((TMP / "mp-cover.html").as_uri(), "mp-cover.png", 1600, 540)
    save(im, "motionpilot", "cover.jpg", quality=90)


def motionrules() -> None:
    im = shot("https://motionrules.com/", "motionrules.png", 1600, 900, tz=night_tz())
    # right 16 px = unpainted scrollbar gutter in headless mode
    save(crop_ratio(im, top=0, right=1584), "motionrules", "cover.jpg")


def cubby() -> None:
    cover = Image.open(CUBBY_DIR / "cover-dark-2400x900.png")  # composed for zosc.com; keep 2.67:1
    save(cover, "cubby", "cover.jpg")
    for name in ("screen-2-find-grid", "screen-3-rooms"):
        im = Image.open(CUBBY_DIR / f"{name}.png").convert("RGB")
        im = im.resize((600, round(im.height * 600 / im.width)), Image.LANCZOS)
        save(im, "cubby", f"{name}.jpg", quality=88)


def gateway() -> None:
    save(fetch(GATEWAY_OG), "openwebui-cliproxy-gateway", "cover.png")  # designed 2:1 card, keep whole


def nas() -> None:
    dash = fetch(NAS_DASHBOARD)  # 1420x1375
    save(crop_ratio(dash, top=130, left=40, right=1380), "nas-monitoring", "cover.jpg")


def blog() -> None:
    im = shot("https://blog.zosc.com/", "blog.png", 1000, 900, scale=1.6, dark_scheme=True)
    save(crop_ratio(im, top=290), "zero-build-blog", "cover.jpg")  # below the "Zerb's Blog" header


JOBS = {"motionpilot": motionpilot, "motionrules": motionrules, "cubby": cubby,
        "openwebui-cliproxy-gateway": gateway, "nas-monitoring": nas, "zero-build-blog": blog}

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for slug in args or JOBS:
        if slug not in JOBS:
            sys.exit(f"unknown slug {slug!r}; known: {', '.join(JOBS)}")
        JOBS[slug]()
    if "--keep" not in sys.argv and TMP.exists():
        shutil.rmtree(TMP)
