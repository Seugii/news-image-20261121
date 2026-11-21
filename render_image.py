#!/usr/bin/env python3
"""Render the revised round-2 entry.png for make.fun news-image-20261121.

Revision per Xie's feedback: only the hottest supporting stories get a
small, CLEAR thumbnail; the rest are text-only. Bitcoin added with a
PIL price chart drawn from verified Finnhub (Binance BTC/USDT) data.
Masthead, colors and layout identity kept from round 2 ("WORLD ON EDGE").

Layout (1024x1024): kicker + huge masthead + amber date band +
full-width hero cover + red stats bar + a 4-across thumbnail row
(AI bust, Trump, COP31, Bitcoin chart) + a 4-across text-only row
(Peru, Riyadh, Kryvyi Rih, Gen Z) + two-column briefs + sources footer.
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(BASE, "photos")
FONTS = os.path.join(BASE, "fonts")

W, H = 1024, 1024
BG = (23, 19, 16)
RED = (255, 46, 31)
AMBER = (255, 158, 0)
WHITE = (255, 255, 255)
BODY = (232, 226, 216)
MUTED = (154, 145, 134)
PANEL = (33, 28, 23)
BORDER = (58, 51, 43)
SCRIM_TOP = (0, 0, 0)

MARGIN = 24
CONTENT_W = W - 2 * MARGIN
COL_W = 235
COL_GAP = 12
COL_X = [MARGIN + i * (COL_W + COL_GAP) for i in range(4)]


def load_font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


F_KICK = load_font("LiberationSans-Bold.ttf", 16)
F_MAST = load_font("LiberationSans-Bold.ttf", 88)
F_DATE = load_font("LiberationSans-Bold.ttf", 20)
F_LABEL = load_font("LiberationSans-Bold.ttf", 15)
F_HERO = load_font("LiberationSans-Bold.ttf", 56)
F_DECK = load_font("LiberationSans-Regular.ttf", 19)
F_QUOTE = load_font("LiberationSans-Italic.ttf", 17)
F_CAP = load_font("LiberationSans-Regular.ttf", 11)
F_STATS = load_font("LiberationSans-Bold.ttf", 19)
F_HEAD = load_font("LiberationSans-Bold.ttf", 18)
F_BODY = load_font("LiberationSans-Regular.ttf", 14)
F_SMALL = load_font("LiberationSans-Regular.ttf", 11)
F_BRIEF_H = load_font("LiberationSans-Bold.ttf", 21)
F_BRIEF = load_font("LiberationSans-Regular.ttf", 13)
F_BRIEF_B = load_font("LiberationSans-Bold.ttf", 13)
F_FOOT = load_font("LiberationSans-Regular.ttf", 11)
F_CHART = load_font("LiberationSans-Bold.ttf", 11)
F_CHART_B = load_font("LiberationSans-Bold.ttf", 12)
F_CHART_SM = load_font("LiberationSans-Regular.ttf", 10)


def wrap_lines(draw, text, font, max_w):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, text, font, fill, max_w, line_h, max_lines=None):
    lines = wrap_lines(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_h), line, font=font, fill=fill)
    return y + len(lines) * line_h


def centered(draw, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)


def frac_crop(img, box, tw, th):
    iw, ih = img.size
    left = int(box[0] * iw)
    upper = int(box[1] * ih)
    right = int(box[2] * iw)
    lower = int(box[3] * ih)
    cropped = img.crop((left, upper, right, lower))
    return ImageOps.fit(cropped, (tw, th), method=Image.LANCZOS)


def paste_thumb(img, draw, x, y, w, h, photo, box):
    src = Image.open(os.path.join(PHOTOS, photo)).convert("RGB")
    thumb = frac_crop(src, box, w, h)
    img.paste(thumb, (x, y))
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=BORDER, width=1)


def draw_btc_chart(draw, x, y, w, h):
    # Verified Finnhub (Binance BTC/USDT): daily closes Nov 18-20 plus
    # the 21 Nov 11:19 UTC quote. Price fell below $60,000 for the
    # first time since July; lowest since September 2024.
    data = [("18", 63068), ("19", 61987), ("20", 58952), ("21", 57875)]
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=PANEL, outline=BORDER)
    left, right = x + 16, x + w - 12
    top, bottom = y + 18, y + h - 28
    lo, hi = 55000, 65000

    def px(i):
        return left + (right - left) * i / (len(data) - 1)

    def py(price):
        return bottom - (price - lo) / (hi - lo) * (bottom - top)

    # dashed $60k break line
    y60 = py(60000)
    for xx in range(left, right, 8):
        draw.line([(xx, y60), (min(xx + 4, right), y60)],
                  fill=(120, 110, 100), width=1)
    draw.text((right - 34, y60 - 13), "$60k", font=F_CHART_SM,
              fill=(150, 140, 130))
    # red line + white dots
    pts = [(px(i), py(p)) for i, (_, p) in enumerate(data)]
    draw.line(pts, fill=RED, width=3, joint="curve")
    for pxx, pyy in pts:
        draw.ellipse([pxx - 4, pyy - 4, pxx + 4, pyy + 4],
                     fill=WHITE, outline=RED, width=1)
    # value labels
    draw.text((pts[0][0] - 2, pts[0][1] - 15), "$63,068",
              font=F_CHART, fill=WHITE)
    draw.text((pts[-1][0] - 52, pts[-1][1] + 8), "$57,875",
              font=F_CHART, fill=RED)
    # 24h change tag, top right
    tag = "−6.3%"
    tw = draw.textlength(tag, font=F_CHART_B)
    draw.text((x + w - 8 - tw, y + 5), tag, font=F_CHART_B, fill=RED)
    # date labels
    for i, (d, _) in enumerate(data):
        dw = draw.textlength(d, font=F_CHART_SM)
        draw.text((px(i) - dw / 2, bottom + 5), d,
                  font=F_CHART_SM, fill=MUTED)


def scrim(img, x0, y0, w, h, a_top=60, a_bot=210):
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(h):
        a = int(a_top + (a_bot - a_top) * (i / h) ** 1.2)
        od.line([(0, i), (w, i)], fill=(0, 0, 0, a))
    img.paste(overlay, (x0, y0), overlay)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # kicker
    centered(draw, 6, "THE WORLD, IN ONE IMAGE", F_KICK, AMBER)

    # masthead: WORLD (white) + ON EDGE (red), huge and centered
    part1, part2 = "WORLD ", "ON EDGE"
    w1 = draw.textlength(part1, font=F_MAST)
    w2 = draw.textlength(part2, font=F_MAST)
    mx = (W - w1 - w2) / 2
    draw.text((mx, 24), part1, font=F_MAST, fill=WHITE)
    draw.text((mx + w1, 24), part2, font=F_MAST, fill=RED)

    # amber date band
    draw.rectangle([0, 116, W - 1, 145], fill=AMBER)
    centered(draw, 121, "SATURDAY, 21 NOVEMBER 2026", F_DATE, (0, 0, 0))

    # hero: full-width photo with overlaid headline
    hero = Image.open(os.path.join(PHOTOS, "cover_tusk.jpg")).convert("RGB")
    hero = ImageOps.fit(hero, (W, 250), method=Image.LANCZOS,
                        centering=(0.5, 0.35))
    img.paste(hero, (0, 146))
    scrim(img, 0, 146, W, 250)
    draw = ImageDraw.Draw(img)
    draw.rectangle([MARGIN, 158, MARGIN + 282, 183], fill=RED)
    lab = "COVER STORY — NATO UNDER FIRE"
    lw = draw.textlength(lab, font=F_LABEL)
    draw.text((MARGIN + (282 - lw) / 2, 164), lab, font=F_LABEL, fill=WHITE)
    draw.text((MARGIN, 206), "MISSILES LAND IN", font=F_HERO, fill=WHITE)
    draw.text((MARGIN, 270), "NATO POLAND", font=F_HERO, fill=WHITE)
    draw.text((MARGIN, 342),
              "Two Russian Kh-101s and a drone crashed in Poland during a mass strike on Ukraine.",
              font=F_DECK, fill=WHITE)
    draw.text((MARGIN, 368),
              "Tusk: “intentional provocation” · Rutte: “grave violation”",
              font=F_QUOTE, fill=AMBER)
    cap = "FILE PHOTO: PM Donald Tusk with President Zelenskyy, Feb 2024"
    cw = draw.textlength(cap, font=F_CAP)
    draw.text((W - MARGIN - cw, 382), cap, font=F_CAP, fill=(200, 195, 185))

    # red stats bar
    draw.rectangle([0, 396, W - 1, 423], fill=RED)
    centered(draw, 401, "400+ DRONES · 110+ MISSILES · 0 HURT IN POLAND",
             F_STATS, WHITE)

    # ---- thumbnail row: only the hottest 4 stories get an image ----
    thumb_y = 436
    thumb_h = 118
    thumbs = [
        dict(photo="nyse.jpg", box=(0.40, 0.15, 0.70, 0.27),
             head="AI BUST: NASDAQ −5.3%",
             body="Worst week since 2020 — $4 trillion wiped out. Anthropic sank to $88.91. Nvidia −14%.",
             cap="FILE PHOTO: NYSE sign"),
        dict(photo="trump.jpg", box=(0.06, 0.217, 0.94, 0.543),
             head="TRUMP WEIGHS IRAN STRIKES",
             body="US weighs another round of strikes as Israel presses for action.",
             cap="FILE PHOTO: President Trump, Jan 2025"),
        dict(photo="cop31.jpg", box=(0.30, 0.05, 1.0, 0.55),
             head="COP31 IN OVERTIME, NO DEAL",
             body="Draft drops every mention of fossil fuels. A third text is due Saturday morning.",
             cap="COP31, Antalya, 12 Nov 2026"),
        dict(chart=True,
             head="BITCOIN SINKS BELOW $60,000",
             body="BTC $57,875, down 6.3% in 24h — lowest since September 2024.",
             cap="CHART: Binance BTC/USDT, Nov 18–21"),
    ]
    for i, cell in enumerate(thumbs):
        x = COL_X[i]
        if cell.get("chart"):
            draw_btc_chart(draw, x, thumb_y, COL_W, thumb_h)
        else:
            paste_thumb(img, draw, x, thumb_y, COL_W, thumb_h,
                        cell["photo"], cell["box"])
        draw_lines(draw, x, thumb_y + 126, cell["head"], F_HEAD, WHITE,
                   COL_W, 21, max_lines=2)
        draw_lines(draw, x, thumb_y + 172, cell["body"], F_BODY, BODY,
                   COL_W, 16, max_lines=3)
        draw.text((x, thumb_y + 226), cell["cap"], font=F_SMALL, fill=MUTED)

    # ---- text-only row: no image, headline + body only ----
    text_y = 688
    texts = [
        ("PERU QUAKE 6.7, NO DEATHS",
         "Magnitude 6.7 quake shook Lima; residents fled into the streets. No deaths."),
        ("RIYADH STOPS 3 HOUTHI MISSILES",
         "Second attack on the Saudi capital in days; tallest tower hit Thursday."),
        ("KRYVYI RIH: BOY, 7, KILLED",
         "Double-tap ballistic strike: a boy, 7, and a paramedic killed; 42 hurt."),
        ("GEN Z STRIKE SWEEPS EUROPE",
         "Youth walkouts in 25 countries over living costs, climate and rearmament."),
    ]
    for i, (head, body) in enumerate(texts):
        x = COL_X[i]
        draw.rectangle([x, text_y, x + COL_W - 1, text_y + 2], fill=RED)
        draw_lines(draw, x, text_y + 10, head, F_HEAD, WHITE,
                   COL_W, 21, max_lines=2)
        draw_lines(draw, x, text_y + 56, body, F_BODY, BODY,
                   COL_W, 16, max_lines=3)

    # ---- briefs, two columns ----
    draw.text((MARGIN, 812), "THE DAY IN BRIEF", font=F_BRIEF_H, fill=RED)
    briefs_left = [
        "KYIV: 3 killed as strikes cripple bridges, cut power.",
        "KERCH: Bridge hit 3rd time; Putin vows 'far more painful' reply.",
        "UK: 1,000 long-range drones for Ukraine in a £260m package.",
        "TRUMP: Tells Europe to defund Ukraine after Putin summit.",
        "AI TAX: 'Tremendous tax' threat on AI centres built abroad.",
        "IRAN: War 'into 2027'; IRGC claims 58th MQ-9 downed, US silent.",
        "N. KOREA: Yongbyon expanded; IAEA warns 'serious concern'.",
        "RIKERS: Close Rikers by 2032; four borough jails, $16bn.",
    ]
    briefs_right = [
        "UFO FILES: 43 UAP files, 3 new videos released; archive 521.",
        "UKRAINE: Kyiv hit three Russian launchers; one destroyed.",
        "EU AID: €1.71bn more — drones, ammunition, air defence.",
        "GREENLAND: Denmark ratifies US security deal, 109–0.",
        "INDIA–JAPAN: 2+2 talks deepen defence ties.",
        "CANCER PILL: Daraxonrasib + chemo shrank tumours 61%.",
        "ANTHROPIC: $2tn debut, then −8.5% on day two.",
    ]
    brief_w = 476
    for col, items in ((MARGIN, briefs_left), (524, briefs_right)):
        y = 840
        for item in items:
            draw.rectangle([col, y + 5, col + 5, y + 10], fill=RED)
            label, _, rest = item.partition(": ")
            label = label + ":"
            lx = col + 14
            draw.text((lx, y), label, font=F_BRIEF_B, fill=WHITE)
            lw = draw.textlength(label, font=F_BRIEF_B)
            draw.text((lx + lw + 4, y), rest, font=F_BRIEF, fill=BODY)
            y += 18

    # footer
    centered(draw, 994,
             "Sources: AP · Reuters · WSJ · CNN · NYT · ISW · IAEA · USGS · European Commission · Finnhub / Binance · CoinMarketCap — Photos: see README",
             F_FOOT, MUTED)

    out = os.path.join(BASE, "entry.png")
    img.save(out, "PNG")
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print("entry.png", img.size, os.path.getsize(out), "bytes")
    print("sha256", digest)


if __name__ == "__main__":
    main()
