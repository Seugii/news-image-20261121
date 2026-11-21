#!/usr/bin/env python3
"""Render the 21 November 2026 news-image entry: a magazine cover.

Layout (1024x1024): masthead + date, one dominant cover story
(Russian missiles land in NATO Poland) with a big photo and a navy
headline panel, four supporting stories with photos/illustration,
a briefs strip, and a sources footer. Pure PIL, no network.
"""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
NAVY = (20, 33, 61)
RED = (185, 28, 28)
GREY = (90, 88, 82)
LIGHT = (255, 255, 255)
RULE = (17, 17, 17)


def font(name, size):
    path = os.path.join(BASE, "fonts", name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/liberation/" + name, size)


SERIF_B = "LiberationSerif-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_I = "LiberationSans-Italic.ttf"


def wrap(text, fnt, width):
    """Greedy word wrap by pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def cover_crop(img, w, h):
    """Centre-crop an image to fill a w x h box, then resize."""
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def photo(path, box):
    img = Image.open(os.path.join(BASE, "photos", path)).convert("RGB")
    return cover_crop(img, box[2] - box[0], box[3] - box[1])


def draw_lines(d, lines, x, y, fnt, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kryvyi_rih_illustration(w, h):
    """Flat night scene: broken apartment blocks, a lit window row,
    an ambulance light glow. Captioned ILLUSTRATION in the page."""
    img = Image.new("RGB", (w, h), (28, 32, 48))
    d = ImageDraw.Draw(img)
    # sky glow
    d.rectangle([0, h - 46, w, h], fill=(58, 40, 34))
    d.ellipse([w - 70, h - 70, w - 10, h - 10], fill=(214, 110, 40))
    # buildings with jagged broken tops
    d.polygon([(8, h), (8, 52), (34, 40), (52, 58), (78, 38),
               (96, 52), (96, h)], fill=(12, 14, 24))
    d.polygon([(110, h), (110, 74), (132, 60), (150, 78), (168, 66),
               (186, h)], fill=(18, 20, 32))
    d.polygon([(200, h), (200, 44), (224, 30), (244, 48), (262, 34),
               (282, 50), (292, h)], fill=(10, 12, 22))
    # lit windows
    for (wx, wy) in [(20, 66), (40, 84), (60, 66), (122, 88),
                     (140, 104), (216, 62), (240, 80), (262, 62)]:
        d.rectangle([wx, wy, wx + 8, wy + 10], fill=(240, 190, 80))
    # ambulance light streak
    d.rectangle([8, h - 14, w - 8, h - 8], fill=(214, 60, 60))
    return img


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # ---------- masthead ----------
    mast = "THE WORLD IN ONE PAGE"
    mf = font(SERIF_B, 56)
    d.text(((W - mf.getlength(mast)) / 2, 12), mast, font=mf, fill=INK)
    d.rectangle([24, 76, 1000, 79], fill=RULE)
    d.rectangle([24, 82, 1000, 83], fill=RULE)
    date = "SATURDAY, 21 NOVEMBER 2026"
    df = font(SANS_B, 25)
    d.text(((W - df.getlength(date)) / 2, 86), date, font=df, fill=INK)
    d.text((24, 91), "No. 21", font=font(SANS, 14), fill=GREY)
    d.text((1000 - font(SANS, 14).getlength("ONE DAY, ONE PAGE"), 91),
           "ONE DAY, ONE PAGE", font=font(SANS, 14), fill=GREY)

    # ---------- cover story ----------
    cy, ch = 120, 440
    # photo, left
    pic = photo("cover_tusk.jpg", (0, 0, 592, ch))
    page.paste(pic, (8, cy))
    d.rectangle([8, cy + ch - 30, 600, cy + ch], fill=(0, 0, 0))
    cap = "FILE PHOTO: PM Donald Tusk with President Zelenskyy, Feb 2024"
    d.text((16, cy + ch - 25), cap, font=font(SANS, 14), fill=LIGHT)
    # navy headline panel, right
    d.rectangle([608, cy, 1016, cy + ch], fill=NAVY)
    px = 632
    d.text((px, cy + 18), "COVER STORY  —  NATO UNDER FIRE",
           font=font(SANS_B, 17), fill=(255, 120, 90))
    hl = ["MISSILES", "LAND IN", "NATO", "POLAND"]
    hf = font(SERIF_B, 54)
    y = cy + 48
    for line in hl:
        d.text((px, y), line, font=hf, fill=LIGHT)
        y += 60
    deck = ("Two Russian Kh-101s and a drone crashed in Poland "
            "during a mass strike on Ukraine.")
    y = draw_lines(d, wrap(deck, font(SANS, 20), 360), px, y + 6,
                   font(SANS, 20), LIGHT, 26)
    quote = "Tusk: \u201cintentional provocation\u201d"
    d.text((px, y + 4), quote, font=font(SANS_I, 17), fill=(200, 210, 235))
    d.text((px, y + 24), "Rutte: \u201cgrave violation\u201d",
           font=font(SANS_I, 17), fill=(200, 210, 235))
    stats = "400+ DRONES  \u00b7  110+ MISSILES  \u00b7  0 HURT IN POLAND"
    d.text((px, cy + ch - 22), stats, font=font(SANS_B, 13),
           fill=(255, 200, 120))

    # ---------- supporting stories ----------
    def story(x, y, w, img, headline, body, caption, illust=False):
        iw = 168
        if illust:
            thumb = kryvyi_rih_illustration(iw, 140)
        else:
            thumb = cover_crop(img, iw, 140)
        page.paste(thumb, (x, y))
        tx = x + iw + 14
        tw = x + w - tx
        hlines = wrap(headline, font(SERIF_B, 27), tw)
        by = draw_lines(d, hlines, tx, y, font(SERIF_B, 27), INK, 31)
        by = draw_lines(d, wrap(body, font(SANS, 16), tw), tx, by + 4,
                        font(SANS, 16), INK, 20)
        d.text((x, y + 142), caption, font=font(SANS, 11), fill=GREY)
        return by

    nyse = Image.open(os.path.join(BASE, "photos", "nyse.jpg")).convert("RGB")
    cop = Image.open(os.path.join(BASE, "photos", "cop31.jpg")).convert("RGB")
    riy = Image.open(os.path.join(BASE, "photos", "riyadh.jpg")).convert("RGB")

    y1 = 576
    d.rectangle([8, y1 - 8, 1016, y1 - 7], fill=RULE)
    story(8, y1, 500, nyse,
          "AI BUST: NASDAQ \u22125.3%",
          "Worst week since 2020 \u2014 $4 trillion wiped out. "
          "Anthropic sinks to $88.91, near its $83 IPO price. "
          "Nvidia \u221214%.",
          "FILE PHOTO: New York Stock Exchange floor")
    story(524, y1, 492, cop,
          "COP31 IN OVERTIME, NO DEAL",
          "Draft drops every mention of fossil fuels. A third "
          "text is due Saturday morning in Antalya.",
          "COP31, Antalya, 12 Nov 2026")

    y2 = 744
    d.rectangle([8, y2 - 8, 1016, y2 - 7], fill=RULE)
    story(8, y2, 500, riy,
          "RIYADH STOPS 3 HOUTHI MISSILES",
          "Second attack on the Saudi capital in days, after "
          "its tallest tower was hit on Thursday.",
          "FILE PHOTO: Riyadh skyline")
    story(524, y2, 492, None,
          "KRYVYI RIH: BOY, 7, KILLED",
          "Double-tap ballistic strike on central Kryvyi Rih: "
          "a boy, 7, and a paramedic killed; 42 hurt.",
          "ILLUSTRATION", illust=True)

    # ---------- briefs ----------
    by = 908
    d.rectangle([8, by - 8, 1016, by - 7], fill=RULE)
    d.text((8, by), "THE DAY IN BRIEF", font=font(SANS_B, 19), fill=RED)
    briefs_left = [
        ("TRUMP", "\u201cTremendous tax\u201d threat on AI centres "
         "abroad."),
        ("IRAN", "Strike decision off until 2027; deployments "
         "extended."),
        ("RIKERS", "Close Rikers by 2032; four borough jails, "
         "$16bn."),
        ("UFO FILES", "43 UAP files, 3 new videos released; archive "
         "521."),
    ]
    briefs_right = [
        ("UKRAINE", "Kyiv hit three Russian launchers; one "
         "destroyed."),
        ("EU AID", "\u20ac1.71bn more: drones, ammunition, air "
         "defence."),
        ("GREENLAND", "Denmark ratifies US security deal, 109\u20130."),
        ("INDIA\u2013JAPAN", "2+2 talks deepen defence ties; "
         "live-fire in India."),
    ]
    bf = font(SANS, 15)
    bl = font(SANS_B, 15)
    yy = by + 24
    for i, (lab, txt) in enumerate(briefs_left):
        d.text((8, yy + i * 19), "\u2022 " + lab + ": ",
               font=bl, fill=INK)
        off = bl.getlength("\u2022 " + lab + ": ")
        d.text((8 + off, yy + i * 19), txt, font=bf, fill=INK)
    for i, (lab, txt) in enumerate(briefs_right):
        d.text((524, yy + i * 19), "\u2022 " + lab + ": ",
               font=bl, fill=INK)
        off = bl.getlength("\u2022 " + lab + ": ")
        d.text((524 + off, yy + i * 19), txt, font=bf, fill=INK)

    # ---------- footer ----------
    d.rectangle([8, 1008, 1016, 1009], fill=RULE)
    foot = ("Sources: AP \u00b7 Reuters \u00b7 WSJ \u00b7 CNN \u00b7 ISW \u00b7 "
            "European Commission \u00b7 NYC.gov \u00b7 war.gov  \u2014  "
            "Photos: see README")
    d.text((8, 1012), foot, font=font(SANS, 11), fill=GREY)

    page.save(os.path.join(BASE, "entry.png"), "PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
