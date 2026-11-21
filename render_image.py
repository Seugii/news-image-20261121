# render_image.py — Round 3 (v4) renderer for make.fun news-image-20261121
# Newspaper style modelled on the top-1 entry's palette (design only — our
# stories, facts and photos stay ours): cream paper, black serif masthead
# with the DATE as the headline, red label bars, region colour coding,
# numbered stories with region tags. Draws entry.png (1024x1024) from
# photos/ plus two PIL-drawn graphics (Bitcoin chart, Kryvyi Rih map).
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976 content width

PAPER = (246, 241, 231)
INK = (26, 26, 26)
RED = (193, 39, 45)
GREY = (96, 96, 96)
DGREY = (74, 74, 74)
LINE = (201, 193, 178)
YELLOW = (255, 214, 102)
WHITE = (255, 255, 255)
CREAM_PANEL = (252, 249, 243)

REGIONS = {
    "Europe": (31, 90, 168),
    "Asia": (192, 57, 43),
    "Middle East": (183, 121, 31),
    "Americas": (59, 74, 140),
    "Global": (74, 74, 74),
}

FONT_DIR = "/usr/share/fonts/truetype/liberation"


def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif_b(s):
    return F("LiberationSerif-Bold.ttf", s)


def serif(s):
    return F("LiberationSerif-Regular.ttf", s)


def serif_i(s):
    return F("LiberationSerif-Italic.ttf", s)


def sans(s):
    return F("LiberationSans-Regular.ttf", s)


def sans_b(s):
    return F("LiberationSans-Bold.ttf", s)


def sans_i(s):
    return F("LiberationSans-Italic.ttf", s)


def tw(f, s):
    return f.getlength(s)


def fit_size(family, text, max_w, start):
    """Largest size (<= start) at which text fits max_w."""
    size = start
    while size > 8 and family(size).getlength(text) > max_w:
        size -= 1
    return size


def wrap(f, text, max_w):
    """Word-wrap text to lines fitting max_w. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def crop_band(img, tw_, th_, y_center):
    """Crop a full-width band of aspect tw_/th_ centred at y_center
    (fraction of image height), then resize to (tw_, th_)."""
    iw, ih = img.size
    band_h = int(iw * th_ / tw_)
    band_h = min(band_h, ih)
    cy = int(ih * y_center)
    y0 = max(0, min(ih - band_h, cy - band_h // 2))
    crop = img.crop((0, y0, iw, y0 + band_h))
    return crop.resize((tw_, th_), Image.LANCZOS)


def gradient_overlay(base, box, max_alpha=175):
    """Darken the bottom of box with a vertical black gradient."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    grad = Image.new("L", (1, h))
    for y in range(h):
        a = int(max_alpha * max(0.0, (y / h - 0.25) / 0.75) ** 1.2)
        grad.putpixel((0, y), a)
    grad = grad.resize((x1 - x0, h))
    black = Image.new("RGBA", (x1 - x0, h), (0, 0, 0, 255))
    overlay = Image.merge("RGBA", (black.split()[0], black.split()[1],
                                   black.split()[2], grad))
    base.alpha_composite(overlay, (x0, y0))


# ---------------------------------------------------------------- tiles
# (num, label, place, topic, region, headline, body, caption, kind, src, y_frac)
TILES = [
    (2, "AI BUST", "NEW YORK", "MARKETS", "Global",
     "Nasdaq \u22125.3% in worst week since 2020",
     "$4T wiped out. Anthropic $88.91. Nvidia \u221214%.",
     "FILE PHOTO: NYSE sign", "photo", "photos/nyse.jpg", 0.30),
    (3, "TRUMP: IRAN", "WASHINGTON", "WAR", "Middle East",
     "Trump weighs Iran strikes",
     "US weighs another round of strikes as Israel presses for action.",
     "FILE PHOTO: President Trump, Jan 2025", "photo", "photos/trump.jpg", 0.50),
    (4, "COP31: OVERTIME", "ANTALYA", "CLIMATE", "Europe",
     "Climate summit runs into Saturday with no deal",
     "Draft drops every mention of fossil fuels. Third text due Saturday.",
     "COP31, Antalya, 12 Nov 2026", "photo", "photos/cop31.jpg", 0.38),
    (5, "BITCOIN: $57,875", "WORLD", "MARKETS", "Global",
     "Bitcoin sinks below $60,000",
     "BTC $57,875, down 6.3% in 24h \u2014 lowest since September 2024.",
     "CHART: Binance BTC/USDT, Nov 18\u201321", "chart", None, None),
    (6, "PERU: QUAKE 6.7", "JUN\u00cdN", "EARTHQUAKE", "Americas",
     "Magnitude 6.7 earthquake shakes Peru",
     "Quake shook Lima; residents fled to the streets. No deaths.",
     "FILE PHOTO: Lima coastline", "photo", "photos/peru_lima.jpg", 0.45),
    (7, "RIYADH: MISSILES", "RIYADH", "WAR", "Middle East",
     "Riyadh stops 3 Houthi missiles",
     "Second attack on the Saudi capital in days; tallest tower hit Thursday.",
     "FILE PHOTO: Riyadh skyline", "photo", "photos/riyadh.jpg", 0.30),
    (8, "KRYVYI RIH", "KRYVYI RIH", "WAR", "Europe",
     "Boy, 7, killed in double-tap strike",
     "A boy, 7, and a paramedic killed; 42 hurt.",
     "GRAPHIC: Kryvyi Rih, Ukraine", "map", None, None),
    (9, "GEN Z STRIKE", "EUROPE", "PROTEST", "Europe",
     "Gen Z strike sweeps Europe",
     "Youth walkouts in 25 countries over living costs, climate, rearmament.",
     "FILE PHOTO: youth climate strike, 2022", "photo", "photos/genz_protest.jpg", 0.42),
]

# (num, place, region, text, source)
BRIEFS = [
    (10, "KYIV", "Europe", "3 killed as strikes cripple bridges, cut power.", "ISW"),
    (11, "KERCH", "Europe", "Bridge hit 3rd time; Putin vows \u2018far more painful\u2019 reply.", "ISW"),
    (12, "UK", "Europe", "1,000 long-range drones for Ukraine in a \u00a3260m package.", "UK gov"),
    (13, "TRUMP", "Americas", "Tells Europe to defund Ukraine after Putin summit.", "WSJ"),
    (14, "AI TAX", "Global", "\u201cTremendous tax\u201d threat on AI centres built abroad.", "Reuters"),
    (15, "IRAN", "Middle East", "War \u201cinto 2027\u201d; IRGC claims 58th MQ-9 downed, US silent.", "ISW"),
    (16, "N. KOREA", "Asia", "Yongbyon expanded; IAEA warns of \u201cserious concern\u201d.", "IAEA"),
    (17, "RIKERS", "Americas", "Close Rikers by 2032; four borough jails, $16bn.", "NYT"),
    (18, "UFO FILES", "Global", "43 UAP files, 3 new videos released; archive 521.", "NARA"),
    (19, "UKRAINE", "Europe", "Kyiv hit three Russian launchers; one destroyed.", "ISW"),
    (20, "EU AID", "Europe", "\u20ac1.71bn more \u2014 drones, ammunition, air defence.", "EU"),
    (21, "GREENLAND", "Europe", "Denmark ratifies US security deal, 109\u20130.", "Reuters"),
    (22, "INDIA\u2013JAPAN", "Asia", "2+2 talks deepen defence ties.", "MEA"),
    (23, "CANCER PILL", "Global", "Daraxonrasib + chemo shrank tumours 61%.", "ASCO"),
    (24, "ANTHROPIC", "Global", "$2tn debut, then \u22128.5% on day two.", "WSJ"),
]

STATS = [
    ("400+", "drones in the mass strike on Ukraine"),
    ("110+", "missiles fired in the same strike"),
    ("6.7", "magnitude of the quake in Peru"),
    ("$57,875", "bitcoin, down 6.3% in 24 hours"),
    ("0", "hurt in Poland as missiles land in NATO"),
]

REGION_COUNTS = [("Europe", 10), ("Global", 6), ("Middle East", 3),
                 ("Americas", 3), ("Asia", 2)]


def draw_bitcoin_chart(w, h):
    """PIL price chart: Finnhub/Binance BTC/USDT daily closes Nov 18-21."""
    img = Image.new("RGB", (w, h), CREAM_PANEL)
    d = ImageDraw.Draw(img)
    closes = [63068, 61987, 58952, 57875]
    lo, hi = 56000, 64000
    pad_l, pad_r, pad_t, pad_b = 6, 6, 20, 16
    pw, ph = w - pad_l - pad_r, h - pad_t - pad_b

    def px(i):
        return pad_l + pw * i / 3.0

    def py(v):
        return pad_t + ph * (1 - (v - lo) / (hi - lo))

    y60 = py(60000)
    for x in range(pad_l, w - pad_r, 8):
        d.line([(x, y60), (min(x + 4, w - pad_r), y60)],
               fill=(70, 90, 140), width=1)
    d.text((pad_l + 2, y60 - 11), "$60k", font=sans_b(9), fill=(70, 90, 140))
    pts = [(px(i), py(v)) for i, v in enumerate(closes)]
    d.line(pts, fill=RED, width=2)
    for x, y in pts:
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=RED)
    d.text((pad_l, 4), "$63,068", font=sans_b(11), fill=INK)
    d.text((w - pad_r - 52, 4), "\u22126.3%", font=sans_b(11), fill=RED)
    d.text((pad_l + 2, h - pad_b + 3), "18", font=sans(9), fill=GREY)
    d.text((w - pad_r - 12, h - pad_b + 3), "21", font=sans(9), fill=GREY)
    d.text((w - pad_r - 54, h - 13), "$57,875", font=sans_b(10), fill=RED)
    return img


def draw_kryvyi_map(w, h):
    """Stylised Ukraine map with Kryvyi Rih marked (no photo available)."""
    img = Image.new("RGB", (w, h), CREAM_PANEL)
    d = ImageDraw.Draw(img)
    outline = [(18, 34), (30, 18), (62, 12), (104, 10), (150, 14),
               (196, 8), (222, 22), (214, 40), (196, 52), (176, 48),
               (158, 62), (120, 70), (84, 66), (52, 72), (30, 58),
               (16, 46)]
    d.polygon(outline, fill=(205, 226, 240), outline=(70, 110, 160))
    d.ellipse([128 - 3, 26 - 3, 128 + 3, 26 + 3], fill=INK)
    d.text((134, 20), "KYIV", font=sans_b(9), fill=INK)
    d.ellipse([118 - 5, 52 - 5, 118 + 5, 52 + 5], fill=RED,
              outline=WHITE, width=1)
    d.text((128, 46), "KRYVYI RIH", font=sans_b(11), fill=RED)
    d.text((128, 60), "UKRAINE", font=sans_b(9), fill=GREY)
    return img


def build():
    img = Image.new("RGB", (W, H), PAPER)
    rgba = img.convert("RGBA")
    d = ImageDraw.Draw(rgba)
    x0, x1 = MARGIN, W - MARGIN

    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)

    # ---- kicker
    d.text((x0, 14), "THE WORLD IN ONE DAY", font=sans_b(13), fill=RED)
    right = "24 STORIES \u00b7 5 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((x1 - tw(sans_b(11), right), 15), right, font=sans_b(11), fill=INK)
    d.line([(x0, 34), (x1, 34)], fill=INK, width=1)

    # ---- masthead: the DATE as the headline
    date_text = "Saturday 21 November 2026"
    size = fit_size(serif_b, date_text, CW, 76)
    f_date = serif_b(size)
    dw = tw(f_date, date_text)
    d.text(((W - dw) / 2, 40), date_text, font=f_date, fill=INK)
    print("masthead size", size, "width", round(dw))

    # ---- italic deck naming the three top stories
    deck = ("Missiles land in NATO Poland \u00b7 Climate summit runs past its "
            "deadline \u00b7 Houthi missiles shot down over Saudi Arabia")
    dsize = fit_size(serif_i, deck, CW, 19)
    f_deck = serif_i(dsize)
    d.text(((W - tw(f_deck, deck)) / 2, 112), deck, font=f_deck, fill=INK)
    print("deck size", dsize, "width", round(tw(f_deck, deck)))

    # ---- stats strip
    d.line([(x0, 134), (x1, 134)], fill=INK, width=1)
    cell_w = CW / 5.0
    for i, (num, cap) in enumerate(STATS):
        cx = x0 + i * cell_w
        if i:
            d.line([(cx, 138), (cx, 180)], fill=LINE, width=1)
        d.text((cx + 8, 138), num, font=serif_b(22), fill=INK)
        for j, line in enumerate(wrap(sans(10), cap, cell_w - 16)):
            d.text((cx + 8, 162 + j * 11), line, font=sans(10), fill=GREY)
    d.line([(x0, 184), (x1, 184)], fill=INK, width=1)

    # ---- region bar
    bx, by, bh = x0, 188, 15
    total = sum(c for _, c in REGION_COUNTS)
    for k, (name, count) in enumerate(REGION_COUNTS):
        if k == len(REGION_COUNTS) - 1:
            seg_w = x1 - bx
        else:
            seg_w = int(round(CW * count / total))
        d.rectangle([bx, by, bx + seg_w - 1, by + bh - 1], fill=REGIONS[name])
        label = "%s %d" % (name.upper(), count)
        lf = sans_b(10)
        d.text((bx + (seg_w - tw(lf, label)) / 2, by + 2), label,
               font=lf, fill=WHITE)
        bx += seg_w

    # ---- cover story: banner photo, headline below it (newspaper style)
    cy0, cy1 = 208, 348
    hero = Image.open("photos/cover_tusk.jpg").convert("RGB")
    hero = crop_band(hero, CW, cy1 - cy0, 0.433)
    rgba.paste(hero, (x0, cy0))
    d = ImageDraw.Draw(rgba)
    label = "1 \u00b7 COVER STORY \u2014 NATO UNDER FIRE"
    lf = sans_b(12)
    lw = tw(lf, label) + 18
    d.rectangle([x0, cy0 + 8, x0 + lw, cy0 + 30], fill=RED)
    d.text((x0 + 9, cy0 + 11), label, font=lf, fill=WHITE)
    cap = "FILE PHOTO: PM Donald Tusk with President Zelenskyy, Feb 2024"
    cap_w = tw(sans(9), cap) + 12
    d.rectangle([x1 - cap_w, cy1 - 20, x1, cy1], fill=(0, 0, 0))
    d.text((x1 - cap_w + 6, cy1 - 17), cap, font=sans(9), fill=WHITE)
    # headline (serif, black on cream), deck, quotes
    chead = "MISSILES LAND IN NATO POLAND"
    csize = fit_size(serif_b, chead, CW, 46)
    print("cover headline size", csize)
    d.text((x0, 354), chead, font=serif_b(csize), fill=INK)
    d.text((x0, 404),
           "Two Russian Kh-101s and a drone crashed in Poland during a mass strike on Ukraine.",
           font=sans(13), fill=INK)
    d.text((x0, 420),
           "Tusk: \u201cintentional provocation\u201d \u00b7 Rutte: \u201cgrave violation\u201d",
           font=serif_i(14), fill=RED)

    # ---- tiles: two rows of four
    tile_w = (CW - 3 * 12) // 4  # 235
    tile_h = 174
    thumb_h = 80
    rows_y = [442, 624]
    for row, y0 in enumerate(rows_y):
        for col in range(4):
            t = TILES[row * 4 + col]
            (num, label, place, topic, region, headline, body, caption,
             kind, src, y_frac) = t
            tx = x0 + col * (tile_w + 12)
            colr = REGIONS[region]
            if kind == "photo":
                im = Image.open(src).convert("RGB")
                thumb = crop_band(im, tile_w, thumb_h, y_frac)
            elif kind == "chart":
                thumb = draw_bitcoin_chart(tile_w, thumb_h)
            else:
                thumb = draw_kryvyi_map(tile_w, thumb_h)
            rgba.paste(thumb, (tx, y0))
            d = ImageDraw.Draw(rgba)
            lf = sans_b(11)
            d.rectangle([tx, y0, tx + tile_w - 1, y0 + 19], fill=RED)
            d.text((tx + 6, y0 + 3), label, font=lf, fill=WHITE)
            tag = "%d \u00b7 %s \u00b7 %s" % (num, place, topic)
            d.text((tx, y0 + thumb_h + 4), tag, font=sans_b(10), fill=colr)
            hy = y0 + thumb_h + 18
            for j, line in enumerate(wrap(sans_b(15), headline, tile_w)[:2]):
                d.text((tx, hy + j * 17), line, font=sans_b(15), fill=INK)
            byy = hy + 36
            for j, line in enumerate(wrap(sans(11), body, tile_w)[:2]):
                d.text((tx, byy + j * 13), line, font=sans(11), fill=DGREY)
            d.text((tx, y0 + tile_h - 11), caption, font=sans(9), fill=GREY)

    # ---- briefs
    by0 = 806
    d.line([(x0, by0), (x1, by0)], fill=RED, width=2)
    d.text((x0, by0 + 6), "ALSO ON SATURDAY 21 NOVEMBER 2026 \u00b7 15 MORE STORIES",
           font=sans_b(12), fill=INK)
    col_w = (CW - 24) // 2
    for i, (num, place, region, text, source) in enumerate(BRIEFS):
        col = 0 if i < 8 else 1
        row = i if i < 8 else i - 8
        bx = x0 + col * (col_w + 24)
        byy = by0 + 28 + row * 18
        colr = REGIONS[region]
        numplace = "%d  %s  " % (num, place)
        rest = "%s (%s)" % (text, source)
        full_w = tw(sans_b(12), numplace) + tw(sans(12), rest)
        if full_w > col_w:
            print("BRIEF OVERFLOW #%d width %.0f > %d" % (num, full_w, col_w))
        d.text((bx, byy), numplace, font=sans_b(12), fill=colr)
        d.text((bx + tw(sans_b(12), numplace), byy), rest, font=sans(12), fill=INK)

    # ---- date check box + footer
    box_y = 978
    d.rectangle([x0, box_y, x1, box_y + 20], outline=RED, width=1)
    dc = ("DATE CHECK  Left out: ICJ genocide ruling on Myanmar (19 Nov). Every "
          "story here happened, or was first reported, on Saturday 21 November 2026.")
    d.text((x0 + 8, box_y + 5), dc, font=sans(11), fill=INK)
    foot = ("Sources: AP \u00b7 Reuters \u00b7 WSJ \u00b7 CNN \u00b7 NYT \u00b7 ISW \u00b7 IAEA \u00b7 "
            "USGS \u00b7 European Commission \u00b7 Finnhub / Binance \u00b7 CoinMarketCap")
    d.text((x0, 1004), foot, font=sans(9), fill=GREY)

    return rgba.convert("RGB")


if __name__ == "__main__":
    out = build()
    out.save("entry.png", optimize=True)
    raw = open("entry.png", "rb").read()
    print("entry.png %d bytes sha256 %s" % (len(raw), hashlib.sha256(raw).hexdigest()))
