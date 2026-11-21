#!/usr/bin/env python3
"""Draw the 20 November 2026 front page: 'THE WORLD TODAY'.

A 1024x1024 newspaper front page, drawn with Pillow from flat vector
shapes and DejaVu fonts only. No photos, no network, no randomness:
running this script twice produces byte-identical PNG output.

Every story was verified against wire reporting of 19-20 November 2026
(Reuters, AP via CNA, SCMP, BBC-adjacent wires, The Hindu, Ukrinform,
WHO/UN News). One candidate was dropped in verification: Kenya's last
Ebola patient went home on 11 November, nine days too early for this
front page, so the DR Congo outbreak (11,000+ cases at six months,
reported 20 November) takes its place in the briefs instead.
"""

import hashlib
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (158, 27, 27)
GRAY = (90, 86, 76)
HAIR = (201, 194, 176)
PANEL = (239, 231, 211)
DARK = (26, 26, 26)
WHITE = (255, 255, 255)
BLUE = (31, 68, 140)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SERIF = str(FONT_DIR / "DejaVuSerif.ttf")
SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def fit(path, text, max_w, start, minimum):
    """Largest font size (from start down to minimum) that fits max_w."""
    size = start
    while size > minimum and font(path, size).getlength(text) > max_w:
        size -= 1
    return font(path, size), size


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        ang = math.radians(rot + i * 180.0 / points)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def burst_points(cx, cy, r_out, r_in, spikes=8):
    return star_points(cx, cy, r_out, r_in, points=spikes, rot=-90)


# ---------------------------------------------------------------- icons
# Every icon is drawn from flat shapes inside a box (x, y, size s).
# No photos, no imported art: each one is this file's own drawing.


def icon_scales(d, x, y, s):
    """Balance scales: the world court."""
    cx = x + s // 2
    d.line([cx, y + 8, cx, y + s - 14], fill=INK, width=3)
    d.line([x + 6, y + 14, x + s - 6, y + 14], fill=INK, width=3)
    d.ellipse([cx - 4, y + 4, cx + 4, y + 12], fill=RED)
    for px in (x + 9, x + s - 9):
        d.line([px, y + 14, px, y + 25], fill=INK, width=2)
        d.polygon([(px - 11, y + 25), (px + 11, y + 25), (px, y + 38)],
                  outline=INK, width=2)
    d.line([cx - 12, y + s - 8, cx + 12, y + s - 8], fill=INK, width=3)


def icon_strike(d, x, y, s):
    """A building under a blast burst: the Kyiv barrage."""
    d.rectangle([x + 4, y + 24, x + 26, y + s - 4], fill=INK)
    for wy in (y + 30, y + 38, y + 46):
        for wx in (x + 10, x + 18):
            d.rectangle([wx, wy, wx + 3, wy + 3], fill=PAPER)
    d.polygon(burst_points(x + 40, y + 18, 15, 6), fill=RED)


def icon_tower(d, x, y, s):
    """A tapered skyscraper, hit at the top: the PIF Tower."""
    d.polygon([(x + 14, y + s - 4), (x + 20, y + 8),
               (x + s - 20, y + 8), (x + s - 14, y + s - 4)], fill=INK)
    for row in range(4):
        wy = y + 16 + row * 9
        for wx in (x + 21, x + 27, x + 33):
            d.rectangle([wx, wy, wx + 3, wy + 3], fill=PAPER)
    d.polygon(burst_points(x + s - 10, y + 10, 9, 4), fill=RED)


def icon_chart_down(d, x, y, s):
    """A falling market line on axes."""
    d.line([x + 6, y + 8, x + 6, y + s - 8], fill=INK, width=3)
    d.line([x + 6, y + s - 8, x + s - 6, y + s - 8], fill=INK, width=3)
    pts = [(x + 12, y + 14), (x + 24, y + 22), (x + 34, y + 20),
           (x + 46, y + 34)]
    d.line(pts, fill=RED, width=4, joint="curve")
    d.polygon([(x + 46, y + 34), (x + 37, y + 31), (x + 44, y + 25)],
              fill=RED)


def icon_globe_leaf(d, x, y, s):
    """A globe with a leaf: the climate talks."""
    cx, cy = x + s // 2, y + s // 2 - 2
    r = s // 2 - 4
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r],
              outline=INK, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=INK, width=2)
    d.polygon([(x + s - 18, y + s - 12), (x + s - 4, y + s - 22),
               (x + s - 2, y + s - 6), (x + s - 12, y + s - 2)],
              fill=RED)


def icon_cyclone(d, x, y, s):
    """A spiral storm with rain: Cyclone Akvan."""
    cx, cy = x + s // 2, y + s // 2 - 5
    pts = []
    for t in range(0, 541, 6):
        ang = math.radians(t)
        r = 2 + (t / 540.0) * (s // 2 - 6)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.line(pts, fill=INK, width=3, joint="curve")
    for dx in (x + 12, x + s - 18):
        d.ellipse([dx, y + s - 12, dx + 6, y + s - 6], fill=RED)


def icon_candles(d, x, y, s):
    """Three candlesticks, the last one falling: the record IPO."""
    d.line([x + 12, y + 8, x + 12, y + 44], fill=INK, width=2)
    d.rectangle([x + 8, y + 20, x + 16, y + 36], fill=INK)
    d.line([x + 27, y + 6, x + 27, y + 40], fill=INK, width=2)
    d.rectangle([x + 23, y + 14, x + 31, y + 30], fill=INK)
    d.line([x + 42, y + 14, x + 42, y + 48], fill=RED, width=2)
    d.rectangle([x + 38, y + 26, x + 46, y + 42], fill=RED)


def draw_flags(d, x, y, w, h):
    """China, Russia and the USA as flat flag icons, side by side."""
    gap = 10
    fw = (w - 2 * gap) // 3
    # China: red field, one big star and four small ones.
    fx = x
    d.rectangle([fx, y, fx + fw, y + h], fill=RED)
    d.polygon(star_points(fx + fw * 0.28, y + h * 0.32, 9, 3.6),
              fill=(255, 222, 0))
    for sx, sy in ((0.62, 0.18), (0.76, 0.30), (0.76, 0.50), (0.62, 0.60)):
        d.polygon(star_points(fx + fw * sx, y + h * sy, 3.2, 1.3),
                  fill=(255, 222, 0))
    d.rectangle([fx, y, fx + fw, y + h], outline=INK, width=1)
    # Russia: white-blue-red tricolour.
    fx = x + fw + gap
    d.rectangle([fx, y, fx + fw, y + h], fill=WHITE)
    d.rectangle([fx, y + h // 3, fx + fw, y + 2 * h // 3], fill=BLUE)
    d.rectangle([fx, y + 2 * h // 3, fx + fw, y + h], fill=RED)
    d.rectangle([fx, y, fx + fw, y + h], outline=INK, width=1)
    # USA: stripes with a canton of dots.
    fx = x + 2 * (fw + gap)
    for i in range(7):
        col = RED if i % 2 == 0 else WHITE
        d.rectangle([fx, y + i * h // 7, fx + fw, y + (i + 1) * h // 7],
                    fill=col)
    d.rectangle([fx, y, fx + int(fw * 0.42), y + 3 * h // 7], fill=BLUE)
    for r in range(2):
        for c in range(3):
            dx = fx + 6 + c * 10
            dy = y + 5 + r * 11
            d.ellipse([dx, dy, dx + 3, dy + 3], fill=WHITE)
    d.rectangle([fx, y, fx + fw, y + h], outline=INK, width=1)


# ---------------------------------------------------------------- layout


def draw_cell(d, x, y, w, icon_fn, kicker, head, body):
    """One grid story: icon left, kicker, headline, two-line body."""
    icon_fn(d, x, y + 4, 56)
    tx = x + 68
    tw = w - 68
    kf, _ = fit(SANS_B, kicker, tw, 17, 13)
    d.text((tx, y + 2), kicker, font=kf, fill=RED)
    size = 26
    hf = font(SANS_B, size)
    lines = wrap(head, hf, tw)
    while len(lines) > 2 and size > 20:
        size -= 1
        hf = font(SANS_B, size)
        lines = wrap(head, hf, tw)
    yy = y + 24
    for ln in lines[:2]:
        d.text((tx, yy), ln, font=hf, fill=INK)
        yy += size + 5
    bsize = 20
    bf = font(SANS, bsize)
    blines = wrap(body, bf, tw)
    while len(blines) > 2 and bsize > 17:
        bsize -= 1
        bf = font(SANS, bsize)
        blines = wrap(body, bf, tw)
    yy = y + 90
    for ln in blines[:2]:
        d.text((tx, yy), ln, font=bf, fill=INK)
        yy += bsize + 5


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36                      # side margin
    cw = W - 2 * mx              # content width: 952

    # Masthead.
    d.rectangle([mx, 24, mx + cw, 27], fill=INK)
    d.rectangle([mx, 31, mx + cw, 32], fill=INK)
    mf, _ = fit(SERIF_B, "THE WORLD TODAY", cw, 64, 48)
    d.text(((W - mf.getlength("THE WORLD TODAY")) / 2, 38),
           "THE WORLD TODAY", font=mf, fill=INK)
    d.rectangle([mx, 100, mx + cw, 103], fill=INK)
    d.rectangle([mx, 107, mx + cw, 108], fill=INK)

    # Dateline: the day, big and unmissable.
    df, _ = fit(SANS_B, "FRIDAY, 20 NOVEMBER 2026", cw, 30, 24)
    d.text(((W - df.getlength("FRIDAY, 20 NOVEMBER 2026")) / 2, 114),
           "FRIDAY, 20 NOVEMBER 2026", font=df, fill=RED)
    d.line([mx, 148, mx + cw, 148], fill=HAIR, width=1)

    # ---- Headline block (y 156..392).
    left_w = 664
    right_x = mx + left_w + 16          # 716
    right_w = W - mx - right_x          # 272
    kf, _ = fit(SANS_B, "SHENZHEN, CHINA - FIRST-EVER TRILATERAL SUMMIT",
                left_w, 22, 16)
    d.text((mx, 158), "SHENZHEN, CHINA - FIRST-EVER TRILATERAL SUMMIT",
           font=kf, fill=RED)
    head_lines = ["TRUMP, XI AND PUTIN", "SIGN 'PEACE DECLARATION'"]
    hf, hsize = fit(SERIF_B, head_lines[1], left_w, 54, 38)
    yy = 186
    for ln in head_lines:
        d.text((mx, yy), ln, font=hf, fill=INK)
        yy += hsize + 8
    deck = ("After an 80-minute meeting, the leaders pledge dialogue on "
            "nuclear risks, UN reform and more oil. A nuclear war "
            "'cannot be won and must never be fought'.")
    dsize = 24
    df2 = font(SERIF, dsize)
    dlines = wrap(deck, df2, left_w)
    while len(dlines) > 3 and dsize > 20:
        dsize -= 1
        df2 = font(SERIF, dsize)
        dlines = wrap(deck, df2, left_w)
    for ln in dlines[:3]:
        d.text((mx, yy), ln, font=df2, fill=INK)
        yy += dsize + 8

    # Right column: the three flags, a caption, the four points.
    draw_flags(d, right_x, 164, right_w, 56)
    cf = font(SANS, 19)
    clines = wrap("Xi, Trump and Putin in Shenzhen on Thursday.",
                  cf, right_w)
    yy = 228
    for ln in clines[:2]:
        d.text((right_x, yy), ln, font=cf, fill=GRAY)
        yy += 24
    d.rectangle([right_x, 282, right_x + right_w, 392], fill=PANEL,
                outline=HAIR, width=1)
    d.text((right_x + 12, 290), "THE FOUR POINTS",
           font=font(SANS_B, 18), fill=RED)
    pf = font(SANS, 18)
    for i, pt in enumerate(("UN reform", "More refined oil for all",
                            "Limits on ICC jurisdiction",
                            "Nuclear-risk dialogue")):
        d.text((right_x + 12, 312 + i * 20), pt, font=pf, fill=INK)

    # ---- Grid: 2 columns x 3 rows (y 414..856).
    d.rectangle([mx, 400, mx + cw, 402], fill=INK)
    col_w = 470
    rows = [414, 564, 714]
    stories = [
        (icon_scales, "THE HAGUE - WORLD COURT",
         "MYANMAR GUILTY OF ROHINGYA GENOCIDE",
         "ICJ rules 9-6 in a first-ever verdict against a state, "
         "and orders reparations."),
        (icon_strike, "KYIV - UKRAINE",
         "RUSSIA'S OVERNIGHT BARRAGE KILLS EIGHT",
         "Missiles and drones hit Kyiv; Ukraine strikes a chemical "
         "plant in Smolensk."),
        (icon_tower, "RIYADH - SAUDI ARABIA",
         "HOUTHI MISSILE HITS TALLEST TOWER",
         "The PIF Tower, home of the wealth fund, is hit across "
         "seven floors. No injuries."),
        (icon_chart_down, "MARKETS - GLOBAL SELLOFF",
         "STOCKS TUMBLE AS AI RALLY UNWINDS",
         "Nikkei -4.8%, Kospi -4.7%; the S&P 500 falls 2% for a "
         "sixth straight loss."),
        (icon_globe_leaf, "ANTALYA - COP31",
         "CLIMATE DRAFT DROPS FOSSIL-FUEL EXIT",
         "The new text omits any phase-out of coal, oil and gas; "
         "talks run into overtime."),
        (icon_cyclone, "ODISHA - INDIA",
         "CYCLONE AKVAN LANDFALL; 300,000 MOVED",
         "The storm crosses near Gopalpur at 70-80 km/h. No major "
         "damage is reported."),
    ]
    for i, (icon_fn, kicker, head, body) in enumerate(stories):
        cx = mx + (i % 2) * (col_w + 12)
        draw_cell(d, cx, rows[i // 2], col_w, icon_fn, kicker, head, body)
    d.line([mx + col_w + 6, 414, mx + col_w + 6, 856], fill=HAIR, width=1)
    for ry in (556, 706):
        d.line([mx, ry, mx + cw, ry], fill=HAIR, width=1)

    # ---- Business strip: the record IPO (y 868..950).
    d.rectangle([mx, 868, mx + cw, 950], fill=PANEL, outline=INK, width=1)
    d.rectangle([mx, 868, mx + 8, 950], fill=RED)
    icon_candles(d, mx + 20, 884, 56)
    tx = mx + 88
    tw = mx + cw - tx - 16
    head = "ANTHROPIC'S RECORD $81BN IPO POPS 17%, THEN SLIDES"
    hf2, h2 = fit(SANS_B, "TECH - " + head, tw, 27, 20)
    d.text((tx, 878), "TECH - ", font=hf2, fill=RED)
    off = hf2.getlength("TECH - ")
    d.text((tx + off, 878), head, font=hf2, fill=INK)
    bf2, _ = fit(SANS,
                 "Biggest IPO ever: shares close at $97.17 on debut, "
                 "then fall 13% on Friday.",
                 tw, 20, 16)
    d.text((tx, 912),
           "Biggest IPO ever: shares close at $97.17 on debut, "
           "then fall 13% on Friday.",
           font=bf2, fill=INK)

    # ---- Ticker band: the rest of the day (y 962..1024).
    d.rectangle([0, 962, W, H], fill=DARK)
    t1 = ("IN BRIEF  -  DR CONGO: Ebola passes 11,000 cases at six "
          "months  -  HORMUZ: Tanker hit and on fire")
    t2 = ("WASHINGTON: Cyber chief fired after outages  -  "
          "BRUSSELS: EU-UK trade deal sealed")
    for i, t in enumerate((t1, t2)):
        tf, _ = fit(SANS, t, cw, 20, 15)
        d.text(((W - tf.getlength(t)) / 2, 968 + i * 24), t,
               font=tf, fill=WHITE)
    return img


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("entry.png")
    img = draw_page()
    img.save(out, format="PNG")
    data = out.read_bytes()
    print(f"wrote {out}  {img.size[0]}x{img.size[1]}  "
          f"{len(data)} bytes")
    print(f"sha256 {hashlib.sha256(data).hexdigest()}")
    assert img.size == (1024, 1024)
    assert len(data) <= 1048576


if __name__ == "__main__":
    main()
