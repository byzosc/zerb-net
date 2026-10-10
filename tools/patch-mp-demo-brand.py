#!/usr/bin/env python3
"""Replace the old 'by ZERB LION' credit in the MotionPilot demo video with 'by zosc' (2026-10-10).

The demo (keyframe_sheet/public/motionpilot-demo.mp4, 1280x652, 69.6 s, silent audio) was recorded
with the pre-rename panel, whose header reads 'MotionPilot by ZERB LION'. Re-recording wasn't an option
(user), so the credit is painted over frame by frame: fill the text box with the header's own
background colour, then draw 'by zosc' in Mulish (the site's body font; the panel's Segoe UI isn't
available here) at the same height and grey.

Static shots use measured boxes (STATIC); a frame is only patched when its header region matches a
still from the middle of that shot (settled()). The camera zooms between shots (MOVES): frames whose
header doesn't match the shot they leave or enter get a full Gaussian blur (reads as motion blur;
the moving credit becomes illegible). Template matching was tried for the transitions and dropped:
too much small UI text, it locked onto the wrong labels. Audit: LOG=1 prints patch/blur/none per frame;
the 'none' spans (14.9-19.9, 31.6-34.7, 49.9-53.4, 55-69.6 s) were checked to have no header in frame.

Inputs it expects (REF_DIR, default .render-tmp/mpv):
  m_0.5.png m_6.0.png m_25.0.png m_41.0.png   ffmpeg -ss <t> -i IN -frames:v 1 m_<t>.png
  mulish-400.ttf                              app/public/fonts/mulish-latin.woff2 instanced at wght 400
                                              (fontTools varLib.instancer), via MULISH_TTF
Output in use: app/public/media/clips/motionpilot/motionpilot-demo.mp4 (audio dropped: it was silent).

  ffmpeg -v error -i IN -f rawvideo -pix_fmt rgb24 - | python3 tools/patch-mp-demo-brand.py | \
    ffmpeg -v error -y -f rawvideo -pix_fmt rgb24 -s 1280x652 -r 30000/1001 -i - \
      -c:v libx264 -crf 22 -preset slow -pix_fmt yuv420p -movflags +faststart OUT.mp4
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1280, 652, 30000 / 1001
FONT = os.environ.get('MULISH_TTF', '/data/Projects/zerb-net/.render-tmp/mpv/mulish-400.ttf')
# (t0, t1, x0, y0, x1, y1): the 'by ZERB LION' box in each static shot, measured on stills.
STATIC = [
    (0.00, 1.03, 973, 156, 1024, 170),
    (1.74, 14.01, 771, 39, 857, 59),
    (20.89, 30.66, 973, 156, 1024, 170),
    (35.80, 48.42, 865, 0, 934, 15),
]
# Zoom transitions between shots (measured: frame-difference spans). The header moves and scales
# there and template matching proved unreliable (too much small UI text), so: a soft whole-frame blur
# that reads as motion blur makes the moving credit illegible, and the first/last 30 % of each
# transition's frames whose header still matches the leaving shot / already matches the entering
# one are patched and kept sharp instead (see settled()).
MOVES = [(1.03, 1.74), (14.01, 14.88), (19.89, 20.89), (30.66, 31.63), (34.70, 35.80), (48.42, 49.88), (53.45, 54.99)]
BLUR = 2.4

# A still from the middle of each static shot (same order as STATIC). A frame inside a shot is
# only patched when its header region matches the still; otherwise the camera is still settling
# (the frame-difference spans miss the slow end of an ease-out: at 1.71-1.75 s a fixed box landed on
# 'MotionPilot') and the frame is blurred like a transition instead.
REF_DIR = os.environ.get('REF_DIR', '/data/Projects/zerb-net/.render-tmp/mpv')
REFS = ['m_0.5.png', 'm_6.0.png', 'm_25.0.png', 'm_41.0.png']
def _region(b):
    x0, y0, x1, y1 = b[2:]
    return (max(0, int(x0 - (x1 - x0) * 1.2)), max(0, y0), min(W, x1 + 4), min(H, y1))
_refs = []
for b, f in zip(STATIC, REFS):
    r = _region(b)
    g = np.asarray(Image.open(os.path.join(REF_DIR, f)).convert('L'), dtype=np.float32)
    _refs.append(g[r[1]:r[3], r[0]:r[2]])
def settled(frame_rgb, k):
    r = _region(STATIC[k])
    g = frame_rgb[r[1]:r[3], r[0]:r[2]].astype(np.float32).mean(axis=2)
    return float(np.abs(g - _refs[k]).mean()) < 4.5

_fonts = {}
def font(px):
    px = max(6, int(round(px)))
    if px not in _fonts:
        _fonts[px] = ImageFont.truetype(FONT, px)
    return _fonts[px]

def patch(img, box):
    x0, y0, x1, y1 = box
    a = np.asarray(img)
    # background: header colour just right of the box (past 'LION'); text grey: brightest-ish pixels inside
    ring = a[max(0, y0):y1, min(W - 1, x1 + 2):min(W, x1 + 10)].reshape(-1, 3)
    bg = tuple(int(v) for v in np.median(ring, axis=0)) if len(ring) else (39, 39, 39)
    inside = a[max(0, y0):y1, x0:x1].reshape(-1, 3).astype(int)
    lum = inside.mean(axis=1)
    txt = tuple(int(v) for v in np.median(inside[lum >= np.percentile(lum, 85)], axis=0)) if len(inside) else (110, 110, 110)
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=bg)
    h = y1 - y0
    # Calibrated on the close-up (box 20 px tall): the original's caps are ~10 px and its baseline sits
    # at 70 % of the box. Mulish caps are ~0.705 em, so size = 0.70 h; draw from the baseline.
    # Rendered 4x and downsampled: at the wide shots' 9-10 px a direct PIL raster hints the letters
    # apart ("zo sc"); supersampling keeps the spacing even.
    S = 4
    f = font(h * 0.70 * S)
    lw, lh = (x1 - x0 + 4) * S, (h + 4) * S
    layer = Image.new('L', (lw, lh), 0)
    ImageDraw.Draw(layer).text((1 * S, (h * 0.70 + 2) * S), 'by zosc', font=f, fill=255, anchor='ls')
    mask = layer.resize((lw // S, lh // S), Image.LANCZOS)
    img.paste(Image.new('RGB', mask.size, txt), (x0, y0 - 2), mask)

def main():
    n = W * H * 3
    i = 0
    out = sys.stdout.buffer
    src = sys.stdin.buffer
    while True:
        buf = src.read(n)
        if len(buf) < n:
            break
        t = i / FPS
        fr = None
        boxes, unsettled = [], False
        for k, b in enumerate(STATIC):
            if b[0] <= t <= b[1]:
                fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
                if settled(fr, k): boxes.append(b[2:])
                else: unsettled = True
        move = next((m for m in MOVES if m[0] < t < m[1]), None)
        if move:
            # In a transition: if the header still matches the shot it is leaving (camera not moving
            # yet) or already matches the one it is entering (landed), patch that box and keep the
            # frame sharp; otherwise full blur. No ramp: a ramp left the last/first frames of a zoom
            # almost sharp with the old credit readable (1.71 s, 14.02 s in v4).
            fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            prev = next((b for b in STATIC if abs(b[1] - move[0]) < 0.05), None)
            nxt = next((b for b in STATIC if abs(b[0] - move[1]) < 0.05), None)
            if prev and settled(fr, STATIC.index(prev)): boxes.append(prev[2:]); move = None
            elif nxt and settled(fr, STATIC.index(nxt)): boxes.append(nxt[2:]); move = None
        if os.environ.get('LOG'):
            print(f"{i}\t{t:.3f}\t{'patch' if boxes else ('blur' if (move or unsettled) else 'none')}", file=sys.stderr)
        if boxes or move or unsettled:
            img = Image.frombytes('RGB', (W, H), buf)
            for b in boxes:
                patch(img, tuple(int(v) for v in b))
            if unsettled:
                img = img.filter(ImageFilter.GaussianBlur(BLUR))
            elif move:
                img = img.filter(ImageFilter.GaussianBlur(BLUR))
            buf = img.tobytes()
        out.write(buf)
        i += 1

if __name__ == '__main__':
    main()
