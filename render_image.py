#!/usr/bin/env python3
"""Render the v2 magazine cover for make.fun news-image-20261121.

Dark 'WORLD ON EDGE' design: near-black background, vivid red + amber
accents, full-width hero photo with overlaid headline, 3-across and
4-across supporting bands, two-column briefs. 23 verified stories.
Deterministic: fixed layout, fixed fonts, no randomness, no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# --- palette (dark theme, red + amber) ---
BG      = (23, 19, 16)      # near-black warm charcoal
RED     = (255, 46, 31)     # vivid red accent
AMBER   = (255, 158, 0)     # amber accent / date band
INK     = (247, 242, 235)   # warm off-white text
MUTED   = (184, 174, 162)   # muted warm grey text
RULE    = (61, 51, 43)      # divider lines
DARKTXT = (23, 19, 16)      # dark text on amber
CAPTXT  = (150, 140, 128)   # photo caption grey

def font(name, size):
    return ImageFont.truetype(os.path.join(BASE, "fonts", name), size)

F_TITLE = lambda s: font("LiberationSans-Bold.ttf", s)
F_BODY  = lambda s: font("LiberationSans-Regular.ttf", s)
F_ITAL  = lambda s: font("LiberationSans-Italic.ttf", s)

def tw(draw, text, f):
    return draw.textbbox((0, 0), text, font=f)[2]

def wrap(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def cover(img, tw_, th_, vpos=0.5):
    iw, ih = img.size
    scale = max(tw_ / iw, th_ / ih)
    nw, nh = round(iw * scale), round(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - tw_) // 2
    y0 = round((nh - th_) * vpos)
    y0 = max(0, min(y0, nh - th_))
    return img.crop((x0, y0, x0 + tw_, y0 + th_))

def photo(path, tw_, th_, vpos=0.5):
    return cover(Image.open(os.path.join(BASE, "photos", path)).convert("RGB"), tw_, th_, vpos)

def scrim(img, top_frac=0.30, max_alpha=225):
    w, h = img.size
    grad = Image.new("L", (1, h))
    px = grad.load()
    for y in range(h):
        t = y / h
        if t < top_frac:
            a = 0
        else:
            a = int(max_alpha * (t - top_frac) / (1 - top_frac))
        px[0, y] = a
    grad = grad.resize((w, h))
    black = Image.new("RGB", (w, h), (10, 8, 7))
    img.paste(Image.composite(black, img, grad), (0, 0))
    return img

def kryvyi_rih(w_, h_):
    """Flat night-scene illustration for Kryvyi Rih (PIL-drawn)."""
    im = Image.new("RGB", (w_, h_), (16, 14, 26))
    d = ImageDraw.Draw(im)
    d.ellipse([w_ - 52, 8, w_ - 18, 42], fill=(255, 158, 0))
    d.rectangle([0, h_ * 0.45, w_ * 0.30, h_], fill=(8, 7, 12))
    d.rectangle([w_ * 0.28, h_ * 0.30, w_ * 0.58, h_], fill=(12, 10, 18))
    d.rectangle([w_ * 0.56, h_ * 0.52, w_ * 0.82, h_], fill=(8, 7, 12))
    d.rectangle([w_ * 0.80, h_ * 0.38, w_, h_], fill=(12, 10, 18))
    for (x, y) in [(14, 52), (34, 66), (w_ * 0.34, 40), (w_ * 0.44, 58),
                   (w_ * 0.62, 62), (w_ * 0.86, 46), (w_ * 0.92, 66)]:
        d.rectangle([x, y, x + 7, y + 9], fill=(255, 190, 60))
    d.rectangle([0, h_ - 8, w_, h_], fill=(200, 30, 18))
    return im

# ================= build =================
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
MX = 16
CW = W - 2 * MX

# ---------- masthead ----------
kick = "THE WORLD, IN ONE IMAGE"
kf = F_TITLE(15)
d.text(((W - tw(d, kick, kf)) // 2, 8), kick, font=kf, fill=AMBER)
title_f = F_TITLE(80)
p1, p2 = "WORLD ", "ON EDGE"
w1, w2 = tw(d, p1, title_f), tw(d, p2, title_f)
x = (W - w1 - w2) // 2
d.text((x, 24), p1, font=title_f, fill=INK)
d.text((x + w1, 24), p2, font=title_f, fill=RED)
d.rectangle([0, 104, W, 128], fill=AMBER)
date = "SATURDAY, 21 NOVEMBER 2026"
df = F_TITLE(21)
d.text(((W - tw(d, date, df)) // 2, 105), date, font=df, fill=DARKTXT)

# ---------- hero: full-width photo, overlaid headline ----------
HY, HH = 128, 280
hero = photo("cover_tusk.jpg", W, HH, vpos=0.50)
hero = scrim(hero, top_frac=0.30, max_alpha=225)
img.paste(hero, (0, HY))
chip = "COVER STORY — NATO UNDER FIRE"
cf = F_TITLE(16)
cw_ = tw(d, chip, cf) + 18
d.rectangle([MX, HY + 12, MX + cw_, HY + 36], fill=RED)
d.text((MX + 9, HY + 15), chip, font=cf, fill=(255, 255, 255))
hf = F_TITLE(56)
d.text((MX, HY + 110), "MISSILES LAND IN", font=hf, fill=INK)
d.text((MX, HY + 166), "NATO POLAND", font=hf, fill=INK)
dkf = F_BODY(20)
d.text((MX, HY + 228), "Two Russian Kh-101s and a drone crashed in Poland during a mass strike on Ukraine.",
       font=dkf, fill=(235, 230, 222))
qf = F_ITAL(18)
d.text((MX, HY + 252), 'Tusk: "intentional provocation"  ·  Rutte: "grave violation"',
       font=qf, fill=AMBER)
cap = "FILE PHOTO: PM Donald Tusk with President Zelenskyy, Feb 2024"
capf = F_BODY(11)
d.text((W - MX - tw(d, cap, capf), HY + HH - 16), cap, font=capf, fill=CAPTXT)

# ---------- stats bar (red) ----------
SY, SH = HY + HH, 26
d.rectangle([0, SY, W, SY + SH], fill=RED)
stats = "400+ DRONES  ·  110+ MISSILES  ·  0 HURT IN POLAND"
sf = F_TITLE(17)
d.text(((W - tw(d, stats, sf)) // 2, SY + 4), stats, font=sf, fill=(255, 255, 255))

# ---------- supporting row A: 3 photo-top stories ----------
RA_Y, RA_H = SY + SH + 10, 160
COLW = (CW - 2 * 12) // 3
rowA = [
    ("nyse.jpg", "AI BUST: NASDAQ −5.3%",
     "Worst week since 2020 — $4 trillion wiped out. Anthropic sank to $88.91. Nvidia −14%.",
     "FILE PHOTO: New York Stock Exchange floor"),
    ("cop31.jpg", "COP31 IN OVERTIME, NO DEAL",
     "Draft drops every mention of fossil fuels. A third text is due Saturday morning in Antalya.",
     "COP31, Antalya, 12 Nov 2026"),
    ("peru_lima.jpg", "PERU QUAKE 6.7, NO DEATHS",
     "Magnitude 6.7 quake shook Lima; residents fled into the streets. No deaths.",
     "FILE PHOTO: Lima skyline"),
]
for i, (ph, head, body, cap) in enumerate(rowA):
    x0 = MX + i * (COLW + 12)
    p = photo(ph, COLW, 80, vpos=0.5)
    img.paste(p, (x0, RA_Y))
    hy = RA_Y + 80 + 6
    for ln in wrap(d, head, F_TITLE(21), COLW):
        d.text((x0, hy), ln, font=F_TITLE(21), fill=INK)
        hy += 24
    by = hy + 2
    for ln in wrap(d, body, F_BODY(14), COLW)[:2]:
        d.text((x0, by), ln, font=F_BODY(14), fill=MUTED)
        by += 17
    d.text((x0, RA_Y + RA_H - 13), cap, font=F_BODY(10), fill=CAPTXT)
    if i < 2:
        d.line([x0 + COLW + 6, RA_Y, x0 + COLW + 6, RA_Y + RA_H - 4], fill=RULE, width=1)

# ---------- supporting row B: 4 narrow photo-top stories ----------
RB_Y, RB_H = RA_Y + RA_H + 8, 164
COLW2 = (CW - 3 * 10) // 4
rowB = [
    ("riyadh.jpg", "RIYADH STOPS 3 HOUTHI MISSILES",
     "Second attack on the Saudi capital in days; tallest tower hit Thursday.",
     "FILE PHOTO: Riyadh skyline", False),
    (None, "KRYVYI RIH: BOY, 7, KILLED",
     "Double-tap ballistic strike: a boy, 7, and a paramedic killed; 42 hurt.",
     "ILLUSTRATION", True),
    ("trump.jpg", "TRUMP WEIGHS IRAN STRIKES",
     "US weighs another round of strikes as Israel presses for action.",
     "FILE PHOTO: President Trump, Jan 2025", False),
    ("genz_protest.jpg", "GEN Z STRIKE SWEEPS EUROPE",
     "Youth walkouts in 25 countries over living costs, climate and rearmament.",
     "FILE PHOTO: youth climate strike, 2022", False),
]
for i, (ph, head, body, cap, illus) in enumerate(rowB):
    x0 = MX + i * (COLW2 + 10)
    if illus:
        p = kryvyi_rih(COLW2, 58)
    else:
        p = photo(ph, COLW2, 58, vpos=0.30 if ph == "trump.jpg" else 0.5)
    img.paste(p, (x0, RB_Y))
    hy = RB_Y + 58 + 5
    for ln in wrap(d, head, F_TITLE(17), COLW2):
        d.text((x0, hy), ln, font=F_TITLE(17), fill=INK)
        hy += 20
    by = hy + 1
    for ln in wrap(d, body, F_BODY(13), COLW2)[:2]:
        d.text((x0, by), ln, font=F_BODY(13), fill=MUTED)
        by += 16
    d.text((x0, RB_Y + RB_H - 12), cap, font=F_BODY(10), fill=CAPTXT)
    if i < 3:
        d.line([x0 + COLW2 + 5, RB_Y, x0 + COLW2 + 5, RB_Y + RB_H - 4], fill=RULE, width=1)

# ---------- briefs ----------
BR_Y = RB_Y + RB_H + 10
bf = F_TITLE(20)
d.text((MX, BR_Y), "THE DAY IN BRIEF", font=bf, fill=RED)
d.line([MX + tw(d, "THE DAY IN BRIEF", bf) + 10, BR_Y + 11,
        W - MX, BR_Y + 11], fill=RULE, width=1)
briefs_left = [
    ("KYIV:", "3 killed as strikes cripple bridges, cut power."),
    ("KERCH:", "Bridge hit 3rd time; Putin vows \u201cfar more painful\u201d reply."),
    ("UK:", "1,000 long-range drones for Ukraine in a \u00a3260m package."),
    ("TRUMP:", "Tells Europe to defund Ukraine after Putin summit."),
    ("AI TAX:", "\u201cTremendous tax\u201d threat on AI centres built abroad."),
    ("IRAN:", "War \u201cinto 2027\u201d; IRGC claims 58th MQ-9 downed, US silent."),
    ("N. KOREA:", "Yongbyon plant expanded; IAEA warns of \u201cserious concern\u201d."),
    ("RIKERS:", "Close Rikers by 2032; four borough jails, $16bn."),
]
briefs_right = [
    ("UFO FILES:", "43 UAP files, 3 new videos released; archive 521."),
    ("UKRAINE:", "Kyiv hit three Russian launchers; one destroyed."),
    ("EU AID:", "\u20ac1.71bn more \u2014 drones, ammunition, air defence."),
    ("GREENLAND:", "Denmark ratifies US security deal, 109\u20130."),
    ("INDIA\u2013JAPAN:", "2+2 talks deepen defence ties; live-fire in India."),
    ("CANCER PILL:", "Daraxonrasib + chemo: tumours shrank in 61%, vanished in 8%."),
    ("ANTHROPIC:", "$2tn debut, then \u22128.5% on day two."),
]
def draw_briefs(items, x0, w_, y0):
    y = y0
    lf, bf2 = F_TITLE(14), F_BODY(14)
    for lead, txt in items:
        lead_w = tw(d, lead + " ", lf)
        lines = wrap(d, txt, bf2, w_ - lead_w)
        d.rectangle([x0, y + 4, x0 + 7, y + 11], fill=RED)
        d.text((x0 + 12, y), lead, font=lf, fill=INK)
        lx = x0 + 12 + lead_w
        d.text((lx, y), lines[0], font=bf2, fill=MUTED)
        y += 16
        for ln in lines[1:2]:
            d.text((x0 + 12, y), ln, font=bf2, fill=MUTED)
            y += 16
        y += 5
    return y
by0 = BR_Y + 26
half = (CW - 20) // 2
draw_briefs(briefs_left, MX, half, by0)
draw_briefs(briefs_right, MX + half + 20, half, by0)

# ---------- footer ----------
ft = "Sources: AP \u00b7 Reuters \u00b7 WSJ \u00b7 CNN \u00b7 NYT \u00b7 ISW \u00b7 IAEA \u00b7 USGS \u00b7 European Commission  \u2014  Photos: see README"
ff = F_BODY(11)
d.text((MX, H - 15), ft, font=ff, fill=CAPTXT)

img.save(os.path.join(BASE, "entry.png"), optimize=True)
print("saved entry.png", img.size)
