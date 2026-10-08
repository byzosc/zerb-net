#!/usr/bin/env python3
"""Bake Montserrat 800 'o' 's' 'c' into the data block of index.html (zosc signature-motion lab, 2026-10-08).

    python3 lab/osc-logo/build-glyphs.py            # rewrite the GLYPHS block inside index.html
    python3 lab/osc-logo/build-glyphs.py --debug P  # also write an SVG of contours + rungs to P

index.html stays zero-build: it never runs this. The script only exists so the numbers baked into
the page can be regenerated and audited (where they come from, how the rungs were chosen).

What it produces, per letter, in "screen font units" (1000 / em, x right, y DOWN, baseline y = 0,
glyph origin x = 0 — the page puts the whole lockup in one group with these units):
  d       the exact outline (TrueType quadratics as SVG Q), used for the final, settled state.
  adv     advance width at wght 800.
  ctr     the pivot the morph turns around (o: centre of the ring, c: centre of the bowl,
          s: midpoint of its spine = its point of symmetry).
  L, R    N "rungs": L[i] and R[i] are matching points on the two sides of the stroke.
          L is on the traveller's LEFT when walking from rung 0 to rung N-1 (screen coords).
          Rung order = the order the wave segment is laid onto the letter:
            o  closed ring, starts and ends at the bottom (the seam where the wave closes),
               runs clockwise on screen: bottom -> left -> top -> right -> bottom. L = outer.
            s  top terminal -> bottom terminal (a wave period stood up, turned 90 deg clockwise).
            c  top terminal -> over the top -> left -> bottom -> bottom terminal. L = inner.
  The polygon L[0..N-1] + reversed R IS the glyph outline at the end of the morph (to sampling
  accuracy, < 0.05 px at the page's size); the page swaps in `d` once a letter has landed.

How the rungs are chosen (why not flubber / normalised arc length):
  o, c  rays from the pivot at evenly spaced angles: both letters are star-shaped around their
        centre and the c's terminal cuts are radial (both corners sit on the same ray, 27.2 deg),
        so every ray crosses the inner and the outer side exactly once -> rungs are radial, the
        page can interpolate in polar coordinates and the ends of the wave swing round the ring.
  s     not star-shaped. The outline is split at its two terminal cuts (the only straight
        segments in the glyph) into two rails, and the rails are aligned with dynamic time
        warping (min total rung length, monotone). That approximates medial-axis rungs; plain
        arc-length pairing skews the rungs at every bend (the outer side of a bend is longer).

Montserrat is a variable font (wght 100-900, default 100): the outlines must come from an
instance at 800 — reading the default glyf table gives the hairline weight.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
FONT = HERE / "montserrat-latin.woff2"
HTML = HERE / "index.html"
N = 161          # rungs per letter (odd -> one rung sits exactly on the middle)
FLIP = (1, 0, 0, -1, 0, 0)  # font y-up -> screen y-down


def fmt(v: float) -> str:
    s = f"{v:.1f}"
    return "0" if s in ("-0.0", "0.0") else s.rstrip("0").rstrip(".")


# ---------------------------------------------------------------- outline flattening
def flatten(ops, steps=24):
    """RecordingPen ops (already y-flipped) -> list of contours; each contour is a list of
    (x, y, kind) where kind is 'L' for the end of a straight segment, 'Q' for a curve point."""
    contours, cur, start, last = [], [], None, None
    for op, args in ops:
        if op == "moveTo":
            cur = [(*args[0], "M")]
            start = last = args[0]
        elif op == "lineTo":
            cur.append((*args[0], "L"))
            last = args[0]
        elif op == "qCurveTo":
            pts = list(args)
            offs, end = pts[:-1], pts[-1]
            # implied on-curve points between consecutive off-curve points
            segs, p0 = [], last
            for k, c in enumerate(offs):
                p2 = end if k == len(offs) - 1 else ((c[0] + offs[k + 1][0]) / 2, (c[1] + offs[k + 1][1]) / 2)
                segs.append((p0, c, p2))
                p0 = p2
            for a, c, b in segs:
                for s in range(1, steps + 1):
                    t = s / steps
                    x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0]
                    y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]
                    cur.append((x, y, "Q"))
            last = end
        elif op in ("closePath", "endPath"):
            if cur and math.dist(cur[-1][:2], cur[0][:2]) < 1e-6:
                cur.pop()
            contours.append(cur)
            cur = []
    return contours


def ray_hits(center, ang, poly, closed=True):
    """Distances along the ray (center, ang) where it crosses the polyline."""
    cx, cy = center
    dx, dy = math.cos(ang), math.sin(ang)
    hits = []
    n = len(poly)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        # center + t*d = p1 + u*e
        wx, wy = x1 - cx, y1 - cy
        t = (wx * ey - wy * ex) / den
        u = (wx * dy - wy * dx) / den
        if t > 1e-9 and -1e-9 <= u <= 1 + 1e-9:
            hits.append((t, (cx + t * dx, cy + t * dy)))
    return sorted(hits)


def resample(poly, n):
    p = np.asarray(poly, float)
    seg = np.hypot(*np.diff(p, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])], 1)


def dtw_pairs(a, b):
    n, m = len(a), len(b)
    d = np.hypot(a[:, None, 0] - b[None, :, 0], a[:, None, 1] - b[None, :, 1])
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0
    for i in range(1, n + 1):
        Di, Dp, di = D[i], D[i - 1], d[i - 1]
        for j in range(1, m + 1):
            Di[j] = di[j - 1] + min(Dp[j], Di[j - 1], Dp[j - 1])
    i, j, path = n, m, []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        k = np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]])
        if k == 0:
            i, j = i - 1, j - 1
        elif k == 1:
            i -= 1
        else:
            j -= 1
    return path[::-1]


def rungs_from_pairs(a, b, pairs, n):
    A = np.array([a[i] for i, _ in pairs])
    B = np.array([b[j] for _, j in pairs])
    M = (A + B) / 2
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(M, axis=0).T))])
    keep = np.concatenate([[True], np.diff(s) > 1e-9])  # drop zero-length steps
    A, B, s = A[keep], B[keep], s[keep]
    t = np.linspace(0, s[-1], n)
    L = np.stack([np.interp(t, s, A[:, 0]), np.interp(t, s, A[:, 1])], 1)
    R = np.stack([np.interp(t, s, B[:, 0]), np.interp(t, s, B[:, 1])], 1)
    return L, R


def left_of_travel(L, R):
    """+1 if L is on the traveller's left (screen coords) for most rungs, -1 if on the right."""
    M = (L + R) / 2
    t = np.gradient(M, axis=0)
    v = L - R
    cross = t[:, 0] * v[:, 1] - t[:, 1] * v[:, 0]
    return 1 if np.sum(cross < 0) > np.sum(cross > 0) else -1


# ---------------------------------------------------------------- per letter
def build(inst):
    gs = inst.getGlyphSet()
    cmap = inst.getBestCmap()
    out = {}
    for ch in "osc":
        g = cmap[ord(ch)]
        adv = inst["hmtx"][g][0]
        sp = SVGPathPen(gs, ntos=fmt)
        gs[g].draw(TransformPen(sp, FLIP))
        rp = RecordingPen()
        gs[g].draw(TransformPen(rp, FLIP))
        contours = flatten(rp.value)
        polys = [[(x, y) for x, y, _ in c] for c in contours]

        if ch == "o":
            outer, inner = sorted(polys, key=lambda p: -np.ptp(np.array(p)[:, 0]))
            xs, ys = np.array(outer)[:, 0], np.array(outer)[:, 1]
            ctr = ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)
            L, R = [], []
            for i in range(N):
                a = math.radians(90 + 360 * i / (N - 1))       # bottom, clockwise on screen
                L.append(ray_hits(ctr, a, outer)[-1][1])
                R.append(ray_hits(ctr, a, inner)[-1][1])
            L, R = np.array(L), np.array(R)

        elif ch == "c":
            c = contours[0]
            pts = [(x, y) for x, y, _ in c]
            line_ends = [k for k, (_, _, kind) in enumerate(c) if kind == "L"]
            assert len(line_ends) == 2, line_ends
            # each straight segment = one terminal cut: (start corner, end corner)
            cuts = [(pts[k - 1], pts[k]) for k in line_ends]
            xs, ys = np.array(pts)[:, 0], np.array(pts)[:, 1]
            top_x = pts[int(np.argmin(ys))][0]
            ctr = (top_x, (ys.min() + ys.max()) / 2)
            # arcs = contour minus the two cut segments, as open polylines
            n = len(pts)
            arcs, k0 = [], line_ends[0]
            for k1 in line_ends[1:] + [line_ends[0] + n]:
                seg = [pts[(k0 + j) % n] for j in range(0, k1 - 1 - k0 + 1)]
                arcs.append(seg)
                k0 = k1
            ang = lambda p: math.atan2(p[1] - ctr[1], p[0] - ctr[0])
            cut_top = min(cuts, key=lambda cc: cc[0][1] + cc[1][1])   # smaller y = higher
            cut_bot = max(cuts, key=lambda cc: cc[0][1] + cc[1][1])
            a_top = ang(((cut_top[0][0] + cut_top[1][0]) / 2, (cut_top[0][1] + cut_top[1][1]) / 2))
            a_bot = ang(((cut_bot[0][0] + cut_bot[1][0]) / 2, (cut_bot[0][1] + cut_bot[1][1]) / 2))
            a0 = a_top % (2 * math.pi)                       # ~332.8 deg
            a1 = a_bot % (2 * math.pi)                       # ~27.2 deg
            L, R = [], []
            for i in range(N):
                if i == 0 or i == N - 1:
                    cut = cut_top if i == 0 else cut_bot
                    near, far = sorted(cut, key=lambda p: math.dist(p, ctr))
                    L.append(near), R.append(far)
                    continue
                a = a0 + (a1 - a0) * i / (N - 1)              # decreasing: counter-clockwise on screen
                hits = []
                for arc in arcs:
                    hits += ray_hits(ctr, a, arc, closed=False)
                hits.sort()
                L.append(hits[0][1])     # inner = nearest
                R.append(hits[-1][1])    # outer = farthest
            L, R = np.array(L), np.array(R)

        else:  # s
            c = contours[0]
            pts = [(x, y) for x, y, _ in c]
            n = len(pts)
            line_ends = [k for k, (_, _, kind) in enumerate(c) if kind == "L"]
            assert len(line_ends) == 2, line_ends
            # corners: (k-1) -> k is a cut
            k_a, k_b = line_ends
            cut1 = (k_a - 1, k_a)
            cut2 = (k_b - 1, k_b)
            # chain1: from end of cut1 to start of cut2 ; chain2: from end of cut2 to start of cut1
            chain1 = [pts[j % n] for j in range(cut1[1], cut2[0] + 1)]
            chain2 = [pts[j % n] for j in range(cut2[1], cut1[0] + n + 1)]
            # orient both from the TOP terminal to the bottom terminal
            top_cut = min((cut1, cut2), key=lambda cc: pts[cc[0]][1] + pts[cc[1]][1])
            if top_cut == cut2:          # chain1 ends at cut2 (top) -> reverse it; chain2 starts at cut2
                X, Y = chain1[::-1], chain2
            else:
                X, Y = chain2[::-1], chain1
            Xr, Yr = resample(X, 700), resample(Y, 700)
            pairs = dtw_pairs(Xr, Yr)
            L, R = rungs_from_pairs(Xr, Yr, pairs, N)
            M = (L + R) / 2
            mid = M[(N - 1) // 2]
            ctr = (float(mid[0]), float(mid[1]))

        side = left_of_travel(L, R)
        if side < 0:
            L, R = R, L
        assert left_of_travel(L, R) > 0
        out[ch] = {
            "adv": adv,
            "ctr": [round(ctr[0], 2), round(ctr[1], 2)],
            "d": sp.getCommands(),
            "L": [round(v, 1) for v in L.flatten().tolist()],
            "R": [round(v, 1) for v in R.flatten().tolist()],
        }
        print(f"{ch}: adv {adv}  ctr ({ctr[0]:.1f},{ctr[1]:.1f})  rungs {N}  "
              f"width min/max {np.hypot(*(L - R).T).min():.0f}/{np.hypot(*(L - R).T).max():.0f}", file=sys.stderr)
    return out


def debug_svg(data, path):
    parts = []
    x0 = 0
    for ch in "osc":
        g = data[ch]
        L = np.array(g["L"]).reshape(-1, 2)
        R = np.array(g["R"]).reshape(-1, 2)
        parts.append(f'<g transform="translate({x0},0)"><path d="{g["d"]}" fill="#333"/>')
        for i in range(0, N, 4):
            parts.append(f'<line x1="{L[i,0]}" y1="{L[i,1]}" x2="{R[i,0]}" y2="{R[i,1]}" stroke="#e7503a" stroke-width="2"/>')
        poly = " ".join(f"{x},{y}" for x, y in np.vstack([L, R[::-1]]))
        parts.append(f'<polygon points="{poly}" fill="none" stroke="#7fd" stroke-width="1.5"/>')
        parts.append(f'<circle cx="{L[0,0]}" cy="{L[0,1]}" r="9" fill="#ff0"/><circle cx="{R[0,0]}" cy="{R[0,1]}" r="9" fill="#0af"/>')
        parts.append(f'<circle cx="{g["ctr"][0]}" cy="{g["ctr"][1]}" r="7" fill="#fff"/></g>')
        x0 += g["adv"]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -620 {x0 + 80} 700" width="{(x0 + 80)}" height="700">'
           f'<rect x="-40" y="-620" width="{x0 + 80}" height="700" fill="#050505"/>{"".join(parts)}</svg>')
    Path(path).write_text(svg)


def main():
    inst = instantiateVariableFont(TTFont(FONT), {"wght": 800}, inplace=False)
    data = build(inst)
    os2 = inst["OS/2"]
    payload = {"upem": inst["head"].unitsPerEm, "xHeight": os2.sxHeight, "capHeight": os2.sCapHeight,
               "N": N, "glyphs": data}
    blob = json.dumps(payload, separators=(",", ":"))
    if "--debug" in sys.argv:
        debug_svg(data, sys.argv[sys.argv.index("--debug") + 1])
    html = HTML.read_text()
    pat = re.compile(r"(/\*@@GLYPHS\*/).*?(/\*@@END\*/)", re.S)
    if not pat.search(html):
        sys.exit("index.html has no /*@@GLYPHS*/ ... /*@@END*/ block")
    HTML.write_text(pat.sub(lambda m: m.group(1) + blob + m.group(2), html))
    print(f"wrote {len(blob)} bytes of glyph data into {HTML.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
