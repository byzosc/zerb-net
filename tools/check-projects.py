#!/usr/bin/env python3
"""Reference-integrity and link check for the project / product pages.

    python3 tools/check-projects.py            # local files only (offline, fast)
    python3 tools/check-projects.py --online   # + external links of kind: product entries -> HTTP 200
    python3 tools/check-projects.py --dist     # + built pages carry SoftwareApplication JSON-LD
                                               #   (run `cd app && npm run build` first)
    python3 tools/check-projects.py --dist --schema   # + every JSON-LD property name/domain is
                                               #   valid per the live schema.org vocabulary

Why it exists: on 2026-10-06 a brand rename pointed three favicon references at files that
did not exist and nobody noticed the 404s. Any change that touches covers, media paths or
project slugs must pass this before commit.

Checks (exit code 1 on any failure):
  1. every entry's cover / coverLarge exists under app/public
  2. every /media/... src, srcset, poster and href in app/src/project-bodies exists (paths are
     percent-decoded: several WordPress-era files have CJK names)
  3. every internal /project/<slug>/ link in a body points to an existing entry
  4. --online: frontmatter `links`, `externalUrl` and body <a href="http..."> of kind: product
     entries answer 200 after redirects (older entries' Behance/Vimeo links are not checked:
     those sites answer bots inconsistently and are not this tool's business)
  5. --dist: each kind: product page has exactly one SoftwareApplication block whose `url` equals
     the page's canonical, and no other page has one
  6. --schema (with --dist): every property in those blocks (and nested Person / Offer) exists in
     the schema.org vocabulary and its domain includes the type or a supertype — the same
     vocabulary validator.schema.org uses, so a misspelt field name fails here, not in Search Console
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

APP = Path(__file__).resolve().parents[1] / "app"
PUBLIC = APP / "public"
ENTRIES = APP / "src" / "content" / "projects"
BODIES = APP / "src" / "project-bodies"
DIST = APP / "dist" / "client" / "project"
UA = "Mozilla/5.0 (X11; Linux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print("  FAIL", msg)


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, flags=re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def public_file(url_path: str) -> Path:
    clean = urllib.parse.unquote(url_path.split("?")[0].split("#")[0])
    return PUBLIC / clean.lstrip("/")


def body_refs(html: str) -> tuple[list[str], list[str], list[str]]:
    """(local /media refs, internal /project/ links, external http(s) hrefs)."""
    media, internal, external = [], [], []
    for attr, value in re.findall(r'\b(src|srcset|poster|href)="([^"]+)"', html):
        candidates = [v.strip().split(" ")[0] for v in value.split(",")] if attr == "srcset" else [value]
        for c in candidates:
            if c.startswith("/media/"):
                media.append(c)
            elif c.startswith("/project/"):
                internal.append(c)
            elif attr == "href" and c.startswith(("http://", "https://")):
                external.append(c)
    return media, internal, external


def http_status(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            res.read(2048)
            return f"{res.status} {res.url if res.url != url else ''}".strip()
    except urllib.error.HTTPError as e:
        return f"{e.code}"
    except Exception as e:  # noqa: BLE001 - report, don't crash
        return f"ERR {type(e).__name__}: {e}"


SCHEMA_VOCAB = "https://schema.org/version/latest/schemaorg-current-https.jsonld"


def schema_problems(obj: dict, vocab: dict, path: str) -> list[str]:
    def ids(v):
        return [x["@id"] for x in (v if isinstance(v, list) else [v])] if v else []

    def lineage(t: str) -> set[str]:
        seen, todo = {t}, [t]
        while todo:
            for parent in ids(vocab.get(todo.pop(), {}).get("rdfs:subClassOf")):
                if parent not in seen:
                    seen.add(parent)
                    todo.append(parent)
        return seen

    types = lineage("schema:" + obj["@type"])
    bad = []
    for key, value in obj.items():
        if key.startswith("@"):
            continue
        prop = vocab.get("schema:" + key)
        if not prop:
            bad.append(f"{path}.{key}: not a schema.org property")
            continue
        if not set(ids(prop.get("schema:domainIncludes"))) & types:
            bad.append(f"{path}.{key}: not valid on {obj['@type']}")
        if isinstance(value, dict) and "@type" in value:
            bad += schema_problems(value, vocab, f"{path}.{key}")
    return bad


def main() -> int:
    online, dist, schema = "--online" in sys.argv, "--dist" in sys.argv, "--schema" in sys.argv
    vocab = {}
    if schema:
        req = urllib.request.Request(SCHEMA_VOCAB, headers={"User-Agent": UA})
        vocab = {n["@id"]: n for n in json.load(urllib.request.urlopen(req, timeout=60))["@graph"]}
    entries = {p.stem: frontmatter(p) for p in sorted(ENTRIES.glob("*.md"))}
    products = [s for s, d in entries.items() if d.get("kind") == "product"]
    print(f"{len(entries)} entries, {len(products)} of kind: product")

    print("1. covers")
    for slug, d in entries.items():
        for key in ("cover", "coverLarge"):
            if d.get(key) and not public_file(d[key]).is_file():
                fail(f"{slug}: {key} {d[key]} missing")
    print("2./3. body media + internal links")
    n_media = 0
    for body in sorted(BODIES.glob("*.html")):
        media, internal, _ = body_refs(body.read_text(encoding="utf-8"))
        n_media += len(media)
        for ref in media:
            if not public_file(ref).is_file():
                fail(f"{body.name}: {ref} missing")
        for ref in internal:
            slug = ref.strip("/").split("/")[1] if ref.count("/") >= 2 else ""
            if slug and slug not in entries:
                fail(f"{body.name}: link {ref} -> no entry '{slug}'")
    print(f"   {n_media} /media refs checked")

    if online:
        print("4. external links of product entries")
        for slug in products:
            d = entries[slug]
            urls = [l["url"] for l in d.get("links", [])] + ([d["externalUrl"]] if d.get("externalUrl") else [])
            body = BODIES / f"{slug}.html"
            if body.exists():
                urls += body_refs(body.read_text(encoding="utf-8"))[2]
            for url in dict.fromkeys(urls):
                status = http_status(url)
                print(f"   {status.split()[0]:>4}  {slug:28s} {url}" + (f"  -> {status.split(' ', 1)[1]}" if " " in status else ""))
                if not status.startswith("200"):
                    fail(f"{slug}: {url} -> {status}")

    if dist:
        print("5. built pages: SoftwareApplication JSON-LD")
        for slug in entries:
            page = DIST / slug / "index.html"
            if not page.exists():
                fail(f"{slug}: no built page at {page}")
                continue
            html = page.read_text(encoding="utf-8")
            blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S)]
            apps = [b for b in blocks if b.get("@type") == "SoftwareApplication"]
            canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            if slug in products:
                if len(apps) != 1:
                    fail(f"{slug}: {len(apps)} SoftwareApplication blocks (want 1)")
                elif not canonical or apps[0].get("url") != canonical.group(1):
                    fail(f"{slug}: JSON-LD url {apps[0].get('url')} != canonical")
                else:
                    print(f"   ok  {slug}: {apps[0].get('applicationCategory')}, url == canonical")
                if schema and apps:
                    for problem in schema_problems(apps[0], vocab, slug):
                        fail(problem)
            elif apps:
                fail(f"{slug}: is not a product but has SoftwareApplication JSON-LD")
        if schema:
            print(f"6. schema.org vocabulary ({len(vocab)} terms): property names + domains checked")

    print(f"\n{'OK' if not failures else f'{len(failures)} FAILURE(S)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
