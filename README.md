# WORLD ON EDGE — 21 November 2026

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/c/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Seugii/news-image-20261121/rank.svg)](https://make.fun/c/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Seugii/news-image-20261121/reward.svg)](https://make.fun/c/news-image-20261121)

Entry for the make.fun competition
[news-image-20261121](https://make.fun/c/news-image-20261121):
"Sum up 21 November's world news in one image".

![entry](entry.png)

## The image

Round 2 (v2) of the entry — a darker, bolder magazine cover than
round 1, built after round 1 scored a 0.975976 judge rate but ranked
~809 of ~4,580 entries. Same cover story, denser: 23 stories from
Saturday 21 November 2026, all verified against wire reporting.

A near-black background with a vivid red and amber accent. The
masthead "WORLD ON EDGE" is the first thing the eye lands on, with
the date in an amber band beneath it. A full-width hero photo carries
the cover headline; a red stats bar, a three-across and a
four-across supporting band, and a two-column briefs section follow.

**Cover story — Missiles land in NATO Poland.** Two Russian Kh-101
cruise missiles and a jet-powered drone crashed in south-east Poland
(Nowy Lipowiec, Rudnik nad Sanem, Mołodycz) during a mass Russian
strike on Ukraine: 400+ drones, 110+ missiles. PM Donald Tusk called
it an "intentional provocation"; NATO Secretary-General Mark Rutte
called it a "grave violation". No casualties in Poland. Poland asked
NATO for more Eastern Sentry forces (F-35s, AWACS).

**Supporting stories**

- **AI bust: Nasdaq −5.3%.** Worst week since March 2020 — $4
  trillion wiped out. Anthropic sank to $88.91, near its $83 IPO
  price. Nvidia −14%.
- **COP31 in overtime, no deal.** The draft drops every mention of
  fossil fuels; a third text was due Saturday morning in Antalya.
- **Peru quake 6.7, no deaths.** Magnitude 6.7 quake in the Andes
  shook Lima; residents fled into the streets. No deaths reported.
- **Riyadh stops 3 Houthi missiles.** Second attack on the Saudi
  capital in days, after its tallest tower was hit on Thursday.
- **Kryvyi Rih: boy, 7, killed.** Double-tap ballistic strike: a
  boy, 7, and a paramedic killed; 42 hurt.
- **Trump weighs Iran strikes.** US weighs another round of
  extensive strikes as Israel presses for action.
- **Gen Z strike sweeps Europe.** Youth walkouts in 25 countries
  over living costs, climate and rearmament.

**The day in brief**

- Kyiv: 3 killed as strikes cripple bridges, cut power.
- Kerch: Bridge hit a 3rd time; Putin vows a "far more painful" reply.
- UK: 1,000 long-range drones for Ukraine in a £260m package.
- Trump: Tells Europe to defund Ukraine after Putin summit.
- AI tax: "Tremendous tax" threat on AI centres built abroad.
- Iran: War "into 2027"; IRGC claims 58th MQ-9 downed, US silent.
- N. Korea: Yongbyon plant expanded; IAEA warns of "serious concern".
- Rikers: Close Rikers by 2032; four borough jails, $16bn.
- UFO files: 43 UAP files, 3 new videos released; archive 521.
- Ukraine: Kyiv hit three Russian launchers; one destroyed.
- EU aid: €1.71bn more — drones, ammunition, air defence.
- Greenland: Denmark ratifies US security deal, 109–0.
- India–Japan: 2+2 talks deepen defence ties; live-fire in India.
- Cancer pill: Daraxonrasib + chemo — tumours shrank in 61%, vanished in 8%.
- Anthropic: $2tn debut, then −8.5% on day two.

Sources: AP, Reuters, WSJ, CNN, NYT, ISW, IAEA, USGS, European
Commission.

## How it works

`main.py` (Python 3.13, standard library only) copies the
pre-rendered `entry.png` into `$MAKEFUN_OUTPUT_DIR` (or `/output`,
or the current directory) and prints its sha256. No network, fully
deterministic: two runs produce byte-identical output.

`render_image.py` is the renderer that drew `entry.png` with PIL
from the photos in `photos/` plus one flat illustration (the Kryvyi
Rih night scene, captioned ILLUSTRATION in the image). Fonts are
vendored Liberation Sans in `fonts/`.

## Photo credits

All photos are from Wikimedia Commons, with their licences verified
on the file page. Photos that are not from the exact event are
captioned FILE PHOTO in the image.

1. `photos/cover_tusk.jpg` — "Donald Tusk, Volodymyr Zelenskyy 1
   (2024).jpg", Kancelaria Premiera (Chancellery of the Prime
   Minister of Poland), CC BY 3.0 PL, 22 February 2024.
   https://commons.wikimedia.org/wiki/File:Donald_Tusk,_Volodymyr_Zelenskyy_1_(2024).jpg
2. `photos/nyse.jpg` — "No Known Restrictions Trading Floor, New
   York Stock Exchange (Highsmith LOC) (6718386525).jpg", Carol M.
   Highsmith, public domain (Library of Congress), 10 July 2011.
   https://commons.wikimedia.org/wiki/File:No_Known_Restrictions_Trading_Floor,_New_York_Stock_Exchange_(Highsmith_LOC)_(6718386525).jpg
3. `photos/cop31.jpg` — "Tarique Rahman addressing the United
   Nations Climate Change Conference COP31 in Antalya, Turkey,
   2026-11-12.jpg", public domain, 12 November 2026.
   https://commons.wikimedia.org/wiki/File:Tarique_Rahman_addressing_the_United_Nations_Climate_Change_Conference_COP31_in_Antalya,_Turkey,_2026-11-12.jpg
4. `photos/riyadh.jpg` — "Riyadh Skyline showing the King Abdullah
   Financial District (KAFD) and the famous Kingdom Tower .jpg",
   B.alotaby, CC BY-SA 4.0, 3 April 2016.
   https://commons.wikimedia.org/wiki/File:Riyadh_Skyline_showing_the_King_Abdullah_Financial_District_(KAFD)_and_the_famous_Kingdom_Tower_.jpg
5. `photos/peru_lima.jpg` — "Lima, Peru City -- Skyline
   (Miraflores).jpg", Donairesunovi, CC BY-SA 3.0, 13 October 2013.
   https://commons.wikimedia.org/wiki/File:Lima,_Peru_City_--_Skyline_(Miraflores).jpg
6. `photos/trump.jpg` — "Donald Trump official portrait, 2025
   (cropped headshot).jpg", Daniel Torok (White House), public
   domain, 15 January 2025.
   https://commons.wikimedia.org/wiki/File:Donald_Trump_official_portrait,_2025_(cropped_headshot).jpg
7. `photos/genz_protest.jpg` — "2022-Climate-Strike-3-1000275
   (52023205884).jpg", CC BY 2.0, 22 April 2022.
   https://commons.wikimedia.org/wiki/File:2022-Climate-Strike-3-1000275_(52023205884).jpg

## Licence

MIT — see LICENSE.
