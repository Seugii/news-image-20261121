#!/usr/bin/env python3
"""Render WORLD ON EDGE — 21 November 2026, bright palette (revision 3).

Clean white background, bold red masthead accent, electric-blue secondary,
vivid-yellow highlight, dark text. Magazine cover, 1024x1024, deterministic.
Reads photos from photos/, fonts from fonts/, writes entry.png next to itself.
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 24
GAP = 16
COLW = (W - 2 * MARGIN - 3 * GAP) // 4  # 232

# ---- bright palette (option a) ----
WHITE = (255, 255, 255)
INK = (18, 18, 18)
BODY = (52, 52, 52)
MUTED = (110, 110, 110)
RED = (227, 6, 19)        # vivid red
BLUE = (0, 87, 255)       # electric blue
YELLOW = (255, 200, 0)    # vivid yellow
PANEL = (247, 247, 242)   # very light warm grey (briefs panel)
RULE = (222, 222, 216)
MAP_FILL = (214, 230, 244)
MAP_LINE = (90, 127, 166)


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


F_BOLD = lambda s: font("LiberationSans-Bold.ttf", s)
F_REG = lambda s: font("LiberationSans-Regular.ttf", s)
F_IT = lambda s: font("LiberationSans-Italic.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Word-wrap text to fit max_w; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def cover_crop(img, box, tw, th):
    """Crop img to fractional box, then centre-crop to tw:th and resize."""
    sw, sh = img.size
    x0, y0, x1, y1 = box
    region = img.crop((int(x0 * sw), int(y0 * sh), int(x1 * sw), int(y1 * sh)))
    rw, rh = region.size
    target = tw / th
    if rw / rh > target:
        nw = int(rh * target)
        x = (rw - nw) // 2
        region = region.crop((x, 0, x + nw, rh))
    else:
        nh = int(rw / target)
        y = (rh - nh) // 2
        region = region.crop((0, y, rw, y + nh))
    return region.resize((tw, th), Image.LANCZOS)


def bottom_gradient(base, top_y, bottom_y, max_alpha=205):
    """Darken the bottom of a photo so white overlay text stays legible."""
    grad = Image.new("L", (1, bottom_y - top_y))
    for i in range(bottom_y - top_y):
        grad.putpixel((0, i), int(max_alpha * (i / (bottom_y - top_y)) ** 1.4))
    grad = grad.resize((base.size[0], bottom_y - top_y))
    black = Image.new("RGB", base.size, (0, 0, 0))
    mask = Image.new("L", base.size, 0)
    mask.paste(grad, (0, top_y))
    return Image.composite(black, base, mask)


# ---------- Bitcoin chart (PIL, white background) ----------
def draw_chart(draw, x, y, w, h):
    closes = [63068, 61987, 58952, 57875]
    days = ["18", "19", "20", "21"]
    lo, hi = 56500, 64500
    pad_l, pad_r, pad_t, pad_b = 4, 4, 16, 14
    px = lambda i: x + pad_l + i * (w - pad_l - pad_r) / 3
    py = lambda v: y + pad_t + (hi - v) * (h - pad_t - pad_b) / (hi - lo)
    # $60k dashed line (electric blue)
    y60 = py(60000)
    for dx in range(x + pad_l, x + w - pad_r, 8):
        draw.line([(dx, y60), (min(dx + 5, x + w - pad_r), y60)], fill=BLUE, width=2)
    draw.text((x + pad_l + 2, y60 - 13), "$60k", font=F_BOLD(10), fill=BLUE)
    # gridline at top value
    draw.text((x + pad_l, y + 1), "$63,068", font=F_BOLD(11), fill=INK)
    draw.text((x + w - pad_r - 42, y + 1), "-6.3%", font=F_BOLD(12), fill=RED)
    # red price line
    pts = [(px(i), py(v)) for i, v in enumerate(closes)]
    for a, b in zip(pts, pts[1:]):
        draw.line([a, b], fill=RED, width=3)
    for pxi, pyi in pts:
        draw.ellipse([pxi - 3, pyi - 3, pxi + 3, pyi + 3], fill=RED)
    draw.text((px(3) - 46, py(closes[3]) - 20), "$57,875",
              font=F_BOLD(12), fill=RED)
    # day labels along the bottom (x-axis)
    for i, d in enumerate(days):
        draw.text((px(i) - 6, y + h - 12), d, font=F_REG(10), fill=MUTED)


# ---------- Kryvyi Rih: stylised Ukraine map graphic ----------
UKRAINE = [
    (0.03, 0.52), (0.08, 0.38), (0.18, 0.28), (0.32, 0.20), (0.48, 0.17),
    (0.64, 0.20), (0.78, 0.28), (0.90, 0.38), (0.96, 0.50), (0.93, 0.62),
    (0.86, 0.70), (0.78, 0.74), (0.70, 0.78), (0.66, 0.92), (0.60, 0.98),
    (0.56, 0.85), (0.50, 0.78), (0.38, 0.76), (0.25, 0.72), (0.12, 0.66),
    (0.04, 0.60),
]


def draw_map(draw, x, y, w, h):
    # uniform-scale Ukraine outline on the left, bold red label on the right
    span_x, span_y = 0.93, 0.81
    scale = min((w * 0.46) / span_x, (h - 4) / span_y)
    mw, mh = span_x * scale, span_y * scale
    mx = x + 4
    my = y + (h - mh) / 2 - 0.17 * scale
    poly = [(mx + px * scale, my + py * scale) for px, py in UKRAINE]
    draw.polygon(poly, fill=MAP_FILL, outline=MAP_LINE, width=2)
    kx, ky = mx + 0.48 * scale, my + 0.30 * scale
    rx, ry = mx + 0.55 * scale, my + 0.68 * scale
    draw.ellipse([kx - 2, ky - 2, kx + 2, ky + 2], fill=INK)
    draw.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=RED)
    draw.ellipse([rx - 8, ry - 8, rx + 8, ry + 8], outline=RED, width=2)
    draw.text((kx + 5, ky - 6), "KYIV", font=F_BOLD(9), fill=INK)
    tx = x + int(w * 0.50)
    draw.text((tx, y + 24), "KRYVYI", font=F_BOLD(16), fill=RED)
    draw.text((tx, y + 42), "RIH", font=F_BOLD(16), fill=RED)
    draw.text((tx, y + 62), "UKRAINE", font=F_BOLD(10), fill=MUTED)


# ---------- story data (same 24 stories) ----------
ROW1 = [
    dict(head="AI BUST: NASDAQ -5.3%",
         body="Worst week since 2020 - $4T wiped out. Anthropic $88.91. Nvidia -14%.",
         cap="FILE PHOTO: NYSE sign",
         thumb=("photo", "photos/nyse.jpg", (0.44, 0.14, 0.76, 0.28))),
    dict(head="TRUMP WEIGHS IRAN STRIKES",
         body="US weighs another round of strikes as Israel presses for action.",
         cap="FILE PHOTO: President Trump, Jan 2025",
         thumb=("photo", "photos/trump.jpg", (0.05, 0.34, 0.95, 0.68))),
    dict(head="COP31 IN OVERTIME, NO DEAL",
         body="Draft drops every mention of fossil fuels. Third text due Saturday.",
         cap="COP31, Antalya, 12 Nov 2026",
         thumb=("photo", "photos/cop31.jpg", (0.12, 0.08, 0.92, 0.68))),
    dict(head="BITCOIN SINKS BELOW $60,000",
         body="BTC $57,875, down 6.3% in 24h - lowest since September 2024.",
         cap="CHART: Binance BTC/USDT, Nov 18-21",
         thumb=("chart",)),
]
ROW2 = [
    dict(head="PERU QUAKE 6.7, NO DEATHS",
         body="Magnitude 6.7 quake shook Lima; residents fled to the streets.",
         cap="FILE PHOTO: Lima coastline",
         thumb=("photo", "photos/peru_lima.jpg", (0.00, 0.50, 0.60, 1.00))),
    dict(head="RIYADH STOPS 3 HOUTHI MISSILES",
         body="Second attack on the Saudi capital in days; tallest tower hit Thursday.",
         cap="FILE PHOTO: Riyadh skyline",
         thumb=("photo", "photos/riyadh.jpg", (0.42, 0.22, 0.82, 0.55))),
    dict(head="KRYVYI RIH: BOY, 7, KILLED",
         body="Double-tap ballistic strike: a boy, 7, and a paramedic killed; 42 hurt.",
         cap="GRAPHIC: Kryvyi Rih, Ukraine",
         thumb=("map",)),
    dict(head="GEN Z STRIKE SWEEPS EUROPE",
         body="Youth walkouts in 25 countries over living costs, climate, rearmament.",
         cap="FILE PHOTO: youth climate strike, 2022",
         thumb=("photo", "photos/genz_protest.jpg", (0.36, 0.54, 0.84, 0.94))),
]

BRIEFS_L = [
    ("KYIV:", "3 killed in overnight Russian strikes."),
    ("KERCH:", "Bridge hit a third time."),
    ("UK:", "1,000 drones for Ukraine, GBP 260m."),
    ("TRUMP:", "Tells Europe to defund Ukraine."),
    ("AI TAX:", "'Tremendous tax' on AI giants."),
    ("IRAN:", "War 'into 2027', IRGC 58th MQ-9 claim."),
    ("N. KOREA:", "Yongbyon expanded, IAEA 'serious concern'."),
    ("RIKERS:", "Closure by 2032."),
]
BRIEFS_R = [
    ("UFO FILES:", "43 files released."),
    ("UKRAINE:", "Hit 3 Russian launchers."),
    ("EU AID:", "EUR 1.71bn for Ukraine."),
    ("GREENLAND:", "Denmark ratifies US deal 109-0."),
    ("INDIA-JAPAN:", "2+2 ties."),
    ("CANCER PILL:", "Daraxonrasib + chemo shrank tumours 61%."),
    ("ANTHROPIC:", "$2tn debut, then -8.5%."),
]


def draw_story_row(img, draw, y, stories, thumb_h=96):
    row_h = thumb_h + 100
    for i, st in enumerate(stories):
        x = MARGIN + i * (COLW + GAP)
        spec = st["thumb"]
        if spec[0] == "photo":
            src = Image.open(os.path.join(HERE, spec[1])).convert("RGB")
            img.paste(cover_crop(src, spec[2], COLW, thumb_h), (x, y))
        elif spec[0] == "chart":
            draw.rectangle([x, y, x + COLW, y + thumb_h], fill=WHITE,
                           outline=RULE, width=1)
            draw_chart(draw, x, y, COLW, thumb_h)
        else:  # map
            draw.rectangle([x, y, x + COLW, y + thumb_h], fill=WHITE,
                           outline=RULE, width=1)
            draw_map(draw, x, y, COLW, thumb_h)
        ty = y + thumb_h + 6
        for line in wrap(draw, st["head"], F_BOLD(19), COLW)[:2]:
            draw.text((x, ty), line, font=F_BOLD(19), fill=INK)
            ty += 22
        ty = y + thumb_h + 6 + 44 + 2
        for line in wrap(draw, st["body"], F_REG(12), COLW)[:2]:
            draw.text((x, ty), line, font=F_REG(12), fill=BODY)
            ty += 15
        draw.text((x, y + thumb_h + 90), st["cap"],
                  font=F_REG(10), fill=MUTED)
    return y + row_h


def main():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # ---- kicker ----
    draw.text((W // 2, 8), "THE WORLD, IN ONE IMAGE", font=F_BOLD(16),
              fill=RED, anchor="ma")

    # ---- masthead: WORLD (black) + ON EDGE (red), auto-fit ----
    size = 78
    while size > 60:
        f = F_BOLD(size)
        if draw.textlength("WORLD ON EDGE", font=f) <= W - 2 * MARGIN:
            break
        size -= 2
    f = F_BOLD(size)
    w_world = draw.textlength("WORLD ", font=f)
    w_edge = draw.textlength("ON EDGE", font=f)
    total = w_world + w_edge
    x0 = (W - total) // 2
    draw.text((x0, 26), "WORLD ", font=f, fill=INK)
    draw.text((x0 + w_world, 26), "ON EDGE", font=f, fill=RED)
    mast_bottom = 26 + size + 6

    # ---- date band: vivid yellow, black text ----
    band_y = mast_bottom + 4
    draw.rectangle([MARGIN, band_y, W - MARGIN, band_y + 28], fill=YELLOW)
    draw.text((W // 2, band_y + 4), "SATURDAY, 21 NOVEMBER 2026",
              font=F_BOLD(19), fill=INK, anchor="ma")

    # ---- hero photo ----
    hero_y = band_y + 28 + 6
    hero_h = 252
    hero = Image.open(os.path.join(HERE, "photos/cover_tusk.jpg")).convert("RGB")
    hero = cover_crop(hero, (0.00, 0.22, 1.00, 0.63), W - 2 * MARGIN, hero_h)
    hero = bottom_gradient(hero, int(hero_h * 0.42), hero_h)
    img.paste(hero, (MARGIN, hero_y))
    d2 = ImageDraw.Draw(img)
    # cover-story label (red, white text) on the photo
    label = "COVER STORY - NATO UNDER FIRE"
    lw = d2.textlength(label, font=F_BOLD(15)) + 20
    d2.rectangle([MARGIN + 10, hero_y + 10, MARGIN + 10 + lw, hero_y + 36],
                 fill=RED)
    d2.text((MARGIN + 20, hero_y + 14), label, font=F_BOLD(15), fill=WHITE)
    # headline over the gradient (white, two lines)
    hy = hero_y + hero_h - 140
    d2.text((MARGIN + 12, hy), "MISSILES LAND IN", font=F_BOLD(42), fill=WHITE)
    d2.text((MARGIN + 12, hy + 48), "NATO POLAND", font=F_BOLD(42), fill=WHITE)
    d2.text((MARGIN + 12, hy + 100),
            "Two Russian Kh-101s and a drone crashed in Poland during a mass strike on Ukraine.",
            font=F_REG(16), fill=(235, 235, 235))
    d2.text((MARGIN + 12, hy + 121),
            "Tusk: \u201cintentional provocation\u201d  \u00b7  Rutte: \u201cgrave violation\u201d",
            font=F_IT(15), fill=YELLOW)
    d2.text((W - MARGIN - 12, hero_y + hero_h - 18),
            "FILE PHOTO: PM Donald Tusk with President Zelenskyy, Feb 2024",
            font=F_REG(11), fill=(210, 210, 210), anchor="ra")

    # ---- red stats bar ----
    stats_y = hero_y + hero_h + 6
    draw.rectangle([MARGIN, stats_y, W - MARGIN, stats_y + 28], fill=RED)
    draw.text((W // 2, stats_y + 4),
              "400+ DRONES  \u00b7  110+ MISSILES  \u00b7  0 HURT IN POLAND",
              font=F_BOLD(17), fill=WHITE, anchor="ma")

    # ---- supporting rows (all 8 with thumbnails) ----
    y = draw_story_row(img, draw, stats_y + 28 + 6, ROW1)
    y = draw_story_row(img, draw, y + 4, ROW2)

    # ---- briefs panel ----
    by = y + 4
    draw.rectangle([MARGIN, by, W - MARGIN, by + 164], fill=PANEL)
    draw.text((MARGIN + 12, by + 6), "THE DAY IN BRIEF", font=F_BOLD(20),
              fill=RED)
    draw.rectangle([MARGIN + 12, by + 32, W - MARGIN - 12, by + 34], fill=RED)
    col_w = (W - 2 * MARGIN - 24 - 20) // 2
    for col, items in enumerate([BRIEFS_L, BRIEFS_R]):
        bx = MARGIN + 12 + col * (col_w + 20)
        iy = by + 40
        for lead, text in items:
            draw.rectangle([bx, iy + 3, bx + 8, iy + 11], fill=RED)
            draw.text((bx + 14, iy), lead, font=F_BOLD(12), fill=INK)
            tw = draw.textlength(lead + " ", font=F_BOLD(12))
            draw.text((bx + 14 + tw, iy), text, font=F_REG(12), fill=BODY)
            iy += 15
    foot_y = by + 164 + 4

    # ---- footer ----
    draw.text((W // 2, foot_y),
              "Sources: AP \u00b7 Reuters \u00b7 WSJ \u00b7 CNN \u00b7 NYT \u00b7 ISW \u00b7 IAEA \u00b7 USGS \u00b7 European Commission \u00b7 Finnhub / Binance \u00b7 CoinMarketCap",
              font=F_REG(11), fill=MUTED, anchor="ma")
    assert foot_y + 14 <= H, f"layout overflow: footer ends {foot_y + 14}"

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    with open(out, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    print(f"wrote {out} {os.path.getsize(out)} bytes sha256={sha}")


if __name__ == "__main__":
    main()
