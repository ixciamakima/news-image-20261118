#!/usr/bin/env python3
"""The World in One Day - An Illustrated Atlas.

Sums up Wednesday 18 November 2026 in one 1024x1024 image: an atlas plate
on deep navy with a gold masthead - a night painting of the Hormuz lead
story, a hand-drawn world map with 14 numbered pins, a Top Stories column,
12 illustrated scene cards and 26 numbered briefs. 43 verified stories.

Drawn programmatically with Pillow only (stdlib + Pillow, no network).
Deterministic: fixed seed, no timestamps, no clock, no cwd dependence.

Usage: python3 main.py [output_dir]
Output goes to argv[1] if given, else MAKEFUN_OUTPUT_DIR, else /output.
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

SS = 2  # supersample factor: draw at 2048, downscale to 1024
W, H = 1024, 1024

# --- palette -------------------------------------------------------------
NAVY = (13, 27, 46)
NAVY2 = (20, 39, 62)
PANEL = (20, 39, 62)
PANEL_LINE = (42, 67, 100)
GOLD = (201, 162, 39)
GOLD_SOFT = (216, 184, 92)
GOLD_DIM = (150, 122, 38)
CREAM = (238, 232, 214)
CREAM_DIM = (196, 190, 168)
MUTED = (148, 162, 180)
LAND = (200, 162, 94)
LAND_LINE = (125, 101, 48)
INK = (16, 24, 38)
WHITE = (245, 245, 240)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

RNG = random.Random(20261118)


def px(v):
    return int(round(v * SS))


def font(path, size):
    return ImageFont.truetype(path, px(size))


def output_dir():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt) / SS


def wrap(draw, text, fnt, max_w):
    """Greedy wrap to at most the given final-pixel width."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_n(draw, text, fnt, max_w, n):
    """Wrap to at most n lines, adding an ellipsis if it still overflows."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= n:
        return lines
    out = lines[:n]
    while out and text_w(draw, out[-1] + " ...", fnt) > max_w:
        out[-1] = out[-1].rsplit(" ", 1)[0] if " " in out[-1] else out[-1][:-1]
    out[-1] = out[-1] + " ..."
    return out


def rect(d, x0, y0, x1, y1, **kw):
    d.rectangle([px(x0), px(y0), px(x1), px(y1)], **kw)


def line(d, pts, **kw):
    d.line([(px(x), px(y)) for x, y in pts], **kw)


def ell(d, x0, y0, x1, y1, **kw):
    d.ellipse([px(x0), px(y0), px(x1), px(y1)], **kw)


def poly(d, pts, **kw):
    d.polygon([(px(x), px(y)) for x, y in pts], **kw)


def txt(d, x, y, s, fnt, fill, anchor="la"):
    d.text((px(x), px(y)), s, font=fnt, fill=fill, anchor=anchor)


def centre(d, x, y, s, fnt, fill):
    txt(d, x, y, s, fnt, fill, anchor="ma")


def jitter_poly(pts, amp=1.2):
    out = []
    for lon, lat in pts:
        out.append((lon + RNG.uniform(-amp, amp) * 0.6,
                    lat + RNG.uniform(-amp, amp) * 0.6))
    return out

# --- content -------------------------------------------------------------
# Every event below was verified from Reuters, BBC, AP, NPR, ESPNcricinfo,
# UN News, Just Security, Morning Brief, The Weekly Anthropocene and
# Bangkok Post on 19 Nov 2026. Numbering: 1 lead, 2-5 top stories,
# 6-17 scene cards, 18-43 briefs.

LEAD_HEAD = ["Iran strikes Kuwait & Bahrain",
             "as Gulf war widens"]
LEAD_DECK = ["Kuwait repelled it; Bahrain intercepted for a 3rd time in a week.",
             "First Iranian attack on Kuwait since September. — Reuters / BBC"]
LEAD_KICKER = "LEAD STORY · STRAIT OF HORMUZ"

TOPS = [
    ("2", "Trump hails 'very big' Philippines trade deal",
     "Manila state lunch seals the pact; details still thin. (AP)"),
    ("3", "US loses measles-elimination status",
     "A year of continuous spread ends the 2000 milestone. (AP)"),
    ("4", "Houthis retake Bab el-Mandeb, near Aden",
     "Saudi war may last six more months, analysts warn. (Reuters)"),
    ("5", "Anthropic's record $81.3bn IPO",
     "Claude-maker valued near $1.4tn in market debut. (NPR / BBC)"),
]

# (number, headline, deck line 1, deck line 2, source, scene kind, chip)
CARDS = [
    ("6", "Xi, Putin meet at APEC",
     "Xi & Putin meet a day before", "first Trump–Xi–Putin trilateral.",
     "Reuters / AP", "shenzhen", ""),
    ("7", "Democrats flip Senate",
     "Peltola beats Sullivan; biggest", "Senate flip since 1958.",
     "AP / BBC", "alaska", "56–44"),
    ("8", "Nvidia beats forecasts",
     "First report since Huang's exit;", "shares +5% after the bell.",
     "Reuters", "nvidia", "+5%"),
    ("9", "COP31 opens Stocktake",
     "Global Stocktake launches as", "talks stall; 21 issues open.",
     "UN News", "cop31", ""),
    ("10", "US loses measles status",
     "A year of spread ends the", "elimination status from 2000.",
     "AP", "measles", ""),
    ("11", "Waymo quits US freeways",
     "Driverless taxis pulled from", "all US freeways.",
     "BBC", "waymo", ""),
    ("12", "Houthis retake strait",
     "Strait retaken; forces close", "on Aden; war may last months.",
     "Reuters", "houthis", ""),
    ("13", "Anthropic's $81.3bn IPO",
     "Claude-maker valued near", "$1.4tn in market debut.",
     "NPR / BBC", "anthropic", "$81.3bn"),
    ("14", "Myanmar verdict nears",
     "Historic genocide verdict due", "at UN court over Rohingya.",
     "BBC", "myanmar", ""),
    ("15", "England win by 97 runs",
     "Duckett 133; England win", "Hobart ODI by 97 runs.",
     "ESPNcricinfo", "cricket", ""),
    ("16", "Hunger Games splits fans",
     "Prequel splits opinion", "among fans and critics.",
     "BBC", "hunger", ""),
    ("17", "Ghana jet row over $60m",
     "Presidential jet sparks", "public outrage.",
     "BBC", "jet", "$60M"),
]

BRIEFS = [
    "Mossad chief lobbied US for new joint strikes on Iran",
    "Bahrain refinery back above 80% capacity; full restore by year-end",
    "Iraq PM cracks down on oil-smuggling ring run by Kataib Hezbollah",
    "Vance: US won't let Gulf war become 'another forever war'",
    "Israel elects Matan Kahana speaker; Eisenkot's Yashar party wins",
    "Trump's Board of Peace accuses Israel and Hamas of failing pledges",
    "Ethiopia & Eritrea amass forces along their shared border",
    "Myanmar president: review ASEAN ties over 'unfair treatment'",
    "US officer held in UK over Russia spying taken into US custody",
    "Pakistani man jailed 27 years for Iran-backed plot to kill Trump",
    "UK inflation hits 3.6% on higher fuel; energy bills forecast +£443/yr",
    "PM Burnham to set out EU options; Lammy urges rejoin pledge",
    "Ford ships first battery cells using CATL tech from Michigan plant",
    "Java hit by critical security flaw found by AI startup",
    "Gold falls >2% to ~$3,770, lowest since September 2025",
    "Brent crude ~$92, down 23% from October peak",
    "Indian bonds draw $1.1bn foreign inflows in November",
    "China to invest $15bn in renewables in Türkiye — 7 GW solar & wind",
    "Norway to pay for 12m tonnes of emissions cuts in Indonesia",
    "BYD unveils 1 MW solar EV charger; U9 Xtreme tops 500 km/h",
    "Chahal first Indian to 400 T20 wickets",
    "Bihar stun Delhi chasing 225 in Syed Mushtaq Ali Trophy",
    "Bezos 'heavily involved' in casting Pattinson as new 007",
    "William & Kate walk Earthshot green carpet in Mumbai",
    "Rubio: US not 'under systemic attack' after tech outages",
    "Homeland Security chief Mullin faces House hearing after flight chaos",
]

MARKETS = ("MARKETS  —  Gold $3,770  −2.1%   ·   Brent $92   ·   "
           "Nvidia +5%   ·   Rupee 93.44/$   ·   India bonds +$1.1bn")
SOURCES = ("Sources: Reuters · BBC · AP · NPR · ESPNcricinfo · UN News · "
           "Just Security · Morning Brief · Bangkok Post · The Weekly "
           "Anthropocene · Level Headlines")
CREDIT = ("All events of Wednesday 18 November 2026  ·  Drawn "
          "programmatically  ·  The World in One Day")

# --- world map -----------------------------------------------------------
# Simplified equirectangular continent outlines (lon, lat). Drawn with a
# small deterministic wobble so the coast looks hand-drawn, not clipped.
N_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
             (-85, 76), (-80, 73), (-76, 62), (-70, 58), (-65, 60),
             (-60, 52), (-55, 47), (-70, 44), (-75, 38), (-80, 32),
             (-81, 26), (-84, 30), (-90, 29), (-97, 26), (-105, 22),
             (-110, 24), (-115, 28), (-120, 34), (-125, 40), (-124, 48),
             (-130, 55), (-140, 60), (-155, 58), (-165, 60)]
GREENLAND = [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70),
             (-25, 76), (-40, 78), (-55, 76), (-60, 72)]
S_AMERICA = [(-80, 9), (-75, 10), (-70, 12), (-62, 10), (-52, 5),
             (-50, 0), (-44, -3), (-35, -8), (-40, -20), (-48, -28),
             (-55, -35), (-65, -41), (-70, -50), (-73, -53), (-72, -40),
             (-72, -25), (-77, -15), (-80, -5), (-81, 0)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
          (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
          (32, 68), (40, 68), (45, 65), (40, 60), (35, 55), (30, 50),
          (28, 45), (23, 40), (20, 40), (15, 38), (10, 37), (3, 37),
          (-2, 36), (-6, 36)]
AFRICA = [(-17, 15), (-15, 27), (-10, 31), (-5, 35), (10, 37), (20, 32),
          (30, 31), (32, 27), (35, 28), (38, 22), (40, 15), (43, 11),
          (48, 11), (51, 10), (46, 0), (40, -10), (35, -20), (32, -28),
          (25, -34), (18, -35), (15, -27), (12, -18), (12, -6), (8, 4),
          (4, 6), (-8, 5), (-13, 8)]
ASIA = [(30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 77),
        (130, 72), (150, 70), (170, 66), (178, 65), (170, 60),
        (160, 55), (150, 60), (140, 55), (135, 45), (130, 40),
        (127, 38), (122, 32), (120, 25), (115, 20), (108, 12),
        (105, 8), (100, 8), (98, 15), (95, 20), (90, 22), (85, 20),
        (80, 15), (77, 8), (75, 12), (70, 20), (65, 25), (60, 25),
        (55, 26), (50, 28), (48, 30), (45, 30), (42, 35), (38, 40),
        (35, 42), (30, 45), (28, 50)]
JAPAN = [(130, 31), (133, 34), (137, 36), (140, 38), (141, 42), (143, 44),
         (141, 44), (138, 38), (134, 34), (130, 33)]
INDONESIA = [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8),
             (120, -10), (125, -9), (130, -4), (135, -3), (140, -8),
             (138, -5), (130, -1), (120, -3), (110, -2), (100, 2)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
             (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
             (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
             (126, -14), (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-2, 57), (-4, 58), (-6, 56)]
CONTINENTS = [N_AMERICA, GREENLAND, S_AMERICA, EUROPE, AFRICA, ASIA,
              JAPAN, INDONESIA, AUSTRALIA, UK]

# (number, lon, lat, display offset dx, dy in final px; 0,0 = true spot)
PINS = [
    ("1", 48, 29, 0, 0),       # Strait of Hormuz / Kuwait
    ("2", 121, 14.6, 14, 6),   # Manila
    ("3", -122, 37.7, -14, -14),  # San Francisco (Waymo)
    ("4", -77, 38.9, 10, 8),   # Washington DC
    ("5", 34.8, 32, 0, 0),     # Israel
    ("6", 96, 21, 0, 10),      # Myanmar
    ("7", -150, 64, 0, 0),     # Alaska
    ("8", -122.4, 37.8, -16, 12),  # San Francisco (Anthropic)
    ("9", 45, 12.8, 12, 8),    # Aden / Yemen
    ("10", -121, 37.4, 14, -14),  # Santa Clara (Nvidia)
    ("11", 30.7, 36.9, -16, 4),  # Antalya (COP31)
    ("12", -0.1, 51.5, 0, 0),  # London
    ("13", 72.8, 19, 0, 0),    # Mumbai
    ("14", -74, 40.7, -14, -12),  # New York
]

# --- hero painting -------------------------------------------------------
def draw_hero(d, x0, y0, x1, y1):
    """Night painting of the Strait of Hormuz lead story."""
    w, h = x1 - x0, y1 - y0
    # sky gradient: deep indigo to burnt-orange horizon
    top = (8, 14, 38)
    mid = (24, 38, 76)
    hor = (146, 74, 34)
    for yy in range(y1 - y0):
        t = yy / max(1, y1 - y0 - 1)
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            c = tuple(int(mid[i] + (hor[i] - mid[i]) * k) for i in range(3))
        line(d, [(x0, y0 + yy), (x1, y0 + yy)], fill=c, width=px(1))
    # stars in the upper sky
    for _ in range(70):
        sx = x0 + RNG.uniform(6, w - 6)
        sy = y0 + RNG.uniform(4, h * 0.52)
        r = RNG.uniform(0.5, 1.4)
        a = RNG.randint(120, 235)
        ell(d, sx - r, sy - r, sx + r, sy + r, fill=(235, 230, 210, a))
    # moon with glow (solid blends: RGB canvas ignores alpha)
    mx, my, mr = x0 + w * 0.78, y0 + 30, 15
    sky_here = (15, 24, 54)
    pale = (232, 222, 180)
    for rr, a in ((28, 0.12), (22, 0.25), (17, 0.45)):
        c = tuple(int(sky_here[i] + (pale[i] - sky_here[i]) * a)
                  for i in range(3))
        ell(d, mx - rr, my - rr, mx + rr, my + rr, fill=c)
    ell(d, mx - mr, my - mr, mx + mr, my + mr, fill=(240, 234, 205))
    ell(d, mx - 5, my - 3, mx + 2, my + 4, fill=(214, 206, 172))
    # sea: dark water from the horizon down
    sea_y = y0 + int(h * 0.72)
    rect(d, x0, sea_y, x1, y1, fill=(7, 20, 38))
    # moon reflection: shimmering gold dashes under the moon
    for i in range(9):
        yy = sea_y + 4 + i * 4
        ww = 26 - i * 2
        xx = mx + RNG.uniform(-6, 6)
        line(d, [(xx - ww / 2, yy), (xx + ww / 2, yy)],
             fill=(216, 178, 92), width=px(1))
    # distant shoreline with city lights (Kuwait) on the right
    shore_y = sea_y
    poly(d, [(x0 + w * 0.60, shore_y), (x1, shore_y - 6), (x1, shore_y),
             (x0 + w * 0.60, shore_y)], fill=(10, 16, 30))
    for i in range(16):
        lx = x0 + w * 0.62 + i * (w * 0.36 / 15) + RNG.uniform(-2, 2)
        ly = shore_y - RNG.uniform(1, 9)
        ell(d, lx - 1, ly - 1, lx + 1, ly + 1, fill=(255, 196, 110))
    # two Kuwait towers, thin silhouettes with lights
    for tx in (x0 + w * 0.86, x0 + w * 0.92):
        line(d, [(tx, shore_y), (tx, shore_y - 26)], fill=(8, 12, 24),
             width=px(3))
        ell(d, tx - 3, shore_y - 30, tx + 3, shore_y - 24,
            fill=(8, 12, 24))
        ell(d, tx - 1, shore_y - 28, tx + 1, shore_y - 26,
            fill=(255, 210, 130))
    # tanker silhouettes on the horizon, lit windows
    for tx, tw in ((x0 + w * 0.08, 92), (x0 + w * 0.30, 70)):
        poly(d, [(tx, sea_y), (tx + tw, sea_y), (tx + tw - 8, sea_y - 10),
                 (tx + 6, sea_y - 10)], fill=(5, 10, 20))
        line(d, [(tx + tw * 0.55, sea_y - 10), (tx + tw * 0.55, sea_y - 20)],
             fill=(5, 10, 20), width=px(2))
        for wx in range(4):
            lx = tx + 10 + wx * 18
            ell(d, lx - 1, sea_y - 7, lx + 1, sea_y - 5,
                fill=(255, 190, 100))
    # missile arcs: thin gold trails rising from the lower left
    arcs = [((x0 + 30, y1 - 8), (x0 + 250, y0 + 52), (x0 + 420, y0 + 30)),
            ((x0 + 60, y1 - 4), (x0 + 280, y0 + 66), (x0 + 470, y0 + 44)),
            ((x0 + 12, y1 - 14), (x0 + 200, y0 + 78), (x0 + 330, y0 + 62))]
    for p0, p1, p2 in arcs:
        pts = []
        for k in range(21):
            t = k / 20.0
            bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
            by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
            pts.append((bx, by))
        line(d, pts, fill=(238, 150, 60), width=px(1))
        hx, hy = pts[-1]
        ell(d, hx - 3, hy - 3, hx + 3, hy + 3, fill=(255, 214, 130))
    # frame
    d.rectangle([px(x0), px(y0), px(x1), px(y1)], outline=(90, 74, 32),
                width=px(1))


def draw_masthead(d):
    centre(d, 512, 10, "THE WORLD IN ONE DAY",
           font(SERIF_B, 38), GOLD)
    txt(d, 16, 52, "WEDNESDAY  ·  18 NOVEMBER 2026",
        font(SANS_B, 12), GOLD_SOFT)
    txt(d, 1008, 52, "43 STORIES  ·  6 REGIONS",
        font(SANS_B, 12), GOLD_SOFT, anchor="ra")
    line(d, [(16, 66), (1008, 66)], fill=GOLD, width=px(2))


def draw_lead(d):
    txt(d, 16, 72, LEAD_KICKER, font(SANS_B, 11), GOLD_SOFT)
    draw_hero(d, 16, 88, 616, 214)
    y = 218
    for ln in LEAD_HEAD:
        txt(d, 16, y, ln, font(SERIF_B, 23), CREAM)
        y += 27
    y = 274
    for ln in LEAD_DECK:
        txt(d, 16, y, ln, font(SANS, 12), CREAM_DIM)
        y += 13


def draw_tops(d):
    x0, x1 = 632, 1008
    txt(d, x0, 72, "TOP STORIES", font(SANS_B, 13), GOLD)
    line(d, [(x0, 90), (x1, 90)], fill=GOLD_DIM, width=px(1))
    y = 96
    for num, head, deck in TOPS:
        ell(d, x0, y + 2, x0 + 17, y + 19, fill=GOLD)
        centre(d, x0 + 8.5, y + 4, num, font(SANS_B, 11), INK)
        tx = x0 + 26
        tw = x1 - tx
        lines = wrap_n(d, head, font(SANS_B, 14), tw, 2)
        ly = y
        for ln in lines:
            txt(d, tx, ly, ln, font(SANS_B, 14), CREAM)
            ly += 17
        txt(d, tx, ly + 1, deck, font(SANS, 11), CREAM_DIM)
        y += 49

# --- world map -----------------------------------------------------------
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 16, 328, 1008, 448


def lonlat_to_xy(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (84.0 - lat) / 144.0 * (MAP_Y1 - MAP_Y0)
    return x, y


def draw_map(d):
    txt(d, 16, 308, "THE WORLD AT A GLANCE",
        font(SANS_B, 13), GOLD)
    txt(d, 1008, 310, "14 PLACES THAT MADE THE DAY",
        font(SANS_B, 10), MUTED, anchor="ra")
    rect(d, MAP_X0, MAP_Y0, MAP_X1, MAP_Y1, fill=(16, 32, 54))
    # graticule every 30 degrees
    for lon in range(-180, 181, 30):
        x, _ = lonlat_to_xy(lon, 0)
        line(d, [(x, MAP_Y0), (x, MAP_Y1)], fill=(29, 52, 82), width=px(1))
    for lat in range(-60, 76, 30):
        _, y = lonlat_to_xy(0, lat)
        line(d, [(MAP_X0, y), (MAP_X1, y)], fill=(29, 52, 82), width=px(1))
    # equator, dashed
    _, eq = lonlat_to_xy(0, 0)
    for xx in range(MAP_X0, MAP_X1, 12):
        line(d, [(xx, eq), (xx + 6, eq)], fill=(90, 110, 140), width=px(1))
    txt(d, MAP_X1 - 4, eq - 12, "EQUATOR", font(SANS_B, 8), MUTED,
        anchor="ra")
    # continents, hand-drawn wobble
    for cont in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat) for lon, lat in jitter_poly(cont)]
        poly(d, pts, fill=LAND, outline=LAND_LINE)
    # pins: leader line from the true spot, then the numbered disc
    for num, lon, lat, dx, dy in PINS:
        tx, ty = lonlat_to_xy(lon, lat)
        px_, py = tx + dx, ty + dy
        if dx or dy:
            line(d, [(tx, ty), (px_, py)], fill=GOLD_SOFT, width=px(1))
            ell(d, tx - 2, ty - 2, tx + 2, ty + 2, fill=GOLD_SOFT)
        ell(d, px_ - 7.5, py - 7.5, px_ + 7.5, py + 7.5, fill=GOLD,
            outline=(90, 74, 32))
        centre(d, px_, py - 5, num, font(SANS_B, 9), INK)
    d.rectangle([px(MAP_X0), px(MAP_Y0), px(MAP_X1), px(MAP_Y1)],
                outline=PANEL_LINE, width=px(1))


# --- scene card art ------------------------------------------------------
def art_bg(d, x0, y0, x1, y1, top, bot):
    for yy in range(y1 - y0):
        t = yy / max(1, y1 - y0 - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        line(d, [(x0, y0 + yy), (x1, y0 + yy)], fill=c, width=px(1))


def draw_scene(d, kind, x0, y0, x1, y1):
    """One small painted scene per card, drawn from primitives."""
    w, h = x1 - x0, y1 - y0
    if kind == "shenzhen":
        art_bg(d, x0, y0, x1, y1, (38, 52, 92), (214, 116, 44))
        for i, bh in enumerate((34, 52, 44, 60, 38)):
            bx = x0 + 4 + i * 11
            rect(d, bx, y1 - bh, bx + 8, y1, fill=(12, 18, 34))
            for wy in range(3):
                ell(d, bx + 2, y1 - bh + 5 + wy * 9, bx + 4,
                    y1 - bh + 7 + wy * 9, fill=(255, 206, 110))
        # three flags on the tallest tower
        for i, col in enumerate(((200, 40, 40), (30, 60, 160),
                                 (200, 40, 40))):
            fx = x0 + 30 + i * 8
            line(d, [(fx, y0 + 6), (fx, y0 + 16)], fill=CREAM, width=px(1))
            poly(d, [(fx, y0 + 6), (fx + 6, y0 + 8), (fx, y0 + 11)],
                 fill=col)
    elif kind == "alaska":
        art_bg(d, x0, y0, x1, y1, (52, 74, 110), (16, 28, 50))
        poly(d, [(x0, y1), (x0 + w, y1), (x0 + w, y1 - 12), (x0, y1 - 12)],
             fill=(228, 228, 220))
        rect(d, x0 + 16, y1 - 44, x0 + 40, y1 - 12, fill=(120, 40, 40))
        rect(d, x0 + 20, y1 - 40, x0 + 36, y1 - 30, fill=(240, 240, 235))
        line(d, [(x0 + 24, y1 - 26), (x0 + 28, y1 - 20), (x0 + 36, y1 - 34)],
             fill=(40, 140, 70), width=px(2))
        ell(d, x0 + 44, y0 + 8, x0 + 52, y0 + 16, fill=(255, 214, 130))
    elif kind == "nvidia":
        art_bg(d, x0, y0, x1, y1, (18, 30, 22), (30, 70, 40))
        rect(d, x0 + 12, y1 - 40, x0 + 36, y1 - 16, fill=(24, 24, 20),
             outline=(118, 185, 0))
        for i in range(3):
            line(d, [(x0 + 17 + i * 6, y1 - 35), (x0 + 17 + i * 6, y1 - 21)],
                 fill=(118, 185, 0), width=px(1))
        line(d, [(x0 + 4, y1 - 14), (x0 + 18, y1 - 22), (x0 + 30, y1 - 16),
                 (x0 + 44, y1 - 30), (x0 + 54, y1 - 34)],
             fill=(140, 230, 90), width=px(2))
        poly(d, [(x0 + 54, y1 - 34), (x0 + 48, y1 - 33), (x0 + 54, y1 - 28)],
             fill=(140, 230, 90))
    elif kind == "cop31":
        art_bg(d, x0, y0, x1, y1, (70, 110, 150), (232, 176, 92))
        ell(d, x0 + 34, y0 + 6, x0 + 50, y0 + 22, fill=(255, 220, 140))
        rect(d, x0, y1 - 16, x1, y1, fill=(24, 90, 110))
        for i in range(4):
            cx = x0 + 8 + i * 12
            rect(d, cx, y1 - 34, cx + 5, y1 - 16, fill=(240, 234, 214))
        rect(d, x0 + 4, y1 - 38, x0 + 52, y1 - 34, fill=(240, 234, 214))
    elif kind == "measles":
        art_bg(d, x0, y0, x1, y1, (238, 232, 214), (214, 196, 160))
        for _ in range(26):
            sx = x0 + RNG.uniform(4, w - 4)
            sy = y0 + RNG.uniform(4, h - 4)
            r = RNG.uniform(1.5, 4)
            ell(d, sx - r, sy - r, sx + r, sy + r, fill=(178, 34, 34))
        poly(d, [(x0 + 28, y0 + 10), (x0 + 44, y0 + 38), (x0 + 12, y0 + 38)],
             outline=(140, 24, 24))
        txt(d, x0 + 28, y0 + 22, "!", font(SANS_B, 16), (140, 24, 24),
            anchor="ma")
    elif kind == "waymo":
        art_bg(d, x0, y0, x1, y1, (70, 90, 120), (30, 44, 66))
        poly(d, [(x0 + 18, y1), (x0 + 26, y0 + 18), (x0 + 30, y0 + 18),
                 (x0 + 38, y1)], fill=(40, 44, 52))
        poly(d, [(x0 + 38, y1), (x0 + 30, y0 + 18), (x0 + 34, y0 + 18),
                 (x0 + 46, y1)], fill=(52, 56, 66))
        for k in range(4):
            yy = y0 + 22 + k * 10
            ww = 2 + k
            line(d, [(x0 + 28 - ww, yy), (x0 + 28 + ww, yy)],
                 fill=(240, 200, 80), width=px(1))
        rect(d, x0 + 14, y1 - 22, x0 + 42, y1 - 12, fill=(16, 22, 34))
        ell(d, x0 + 18, y1 - 12, x0 + 23, y1 - 7, fill=(10, 12, 18))
        ell(d, x0 + 33, y1 - 12, x0 + 38, y1 - 7, fill=(10, 12, 18))
        ell(d, x0 + 16, y1 - 20, x0 + 19, y1 - 17, fill=(255, 220, 120))
    elif kind == "houthis":
        art_bg(d, x0, y0, x1, y1, (56, 84, 110), (20, 40, 62))
        poly(d, [(x0, y0), (x0 + 18, y0), (x0 + 12, y1), (x0, y1)],
             fill=(150, 120, 70))
        poly(d, [(x1, y0), (x1 - 16, y0), (x1 - 10, y1), (x1, y1)],
             fill=(150, 120, 70))
        rect(d, x0 + 20, y1 - 22, x0 + 36, y1 - 12, fill=(14, 20, 32))
        line(d, [(x0 + 26, y1 - 22), (x0 + 26, y1 - 32)], fill=(14, 20, 32),
             width=px(2))
        for k in range(3):
            line(d, [(x0 + 16, y1 - 8 + k * 3), (x0 + 40, y1 - 8 + k * 3)],
                 fill=(90, 130, 170), width=px(1))
    elif kind == "anthropic":
        art_bg(d, x0, y0, x1, y1, (240, 236, 220), (200, 180, 130))
        for i, bh in enumerate((12, 20, 16, 30, 42)):
            bx = x0 + 6 + i * 10
            rect(d, bx, y1 - 8 - bh, bx + 7, y1 - 8, fill=(170, 90, 40))
        line(d, [(x0 + 4, y1 - 12), (x0 + 52, y1 - 52)],
             fill=(120, 60, 20), width=px(2))
        poly(d, [(x0 + 52, y1 - 52), (x0 + 46, y1 - 51), (x0 + 51, y1 - 46)],
             fill=(120, 60, 20))
    elif kind == "myanmar":
        art_bg(d, x0, y0, x1, y1, (90, 100, 120), (40, 48, 66))
        poly(d, [(x0 + 6, y0 + 16), (x0 + 28, y0 + 4), (x0 + 50, y0 + 16)],
             fill=(228, 222, 200))
        for i in range(4):
            cx = x0 + 9 + i * 11
            rect(d, cx, y0 + 16, cx + 5, y1 - 12, fill=(228, 222, 200))
        rect(d, x0 + 4, y1 - 12, x0 + 52, y1 - 8, fill=(228, 222, 200))
        line(d, [(x0 + 28, y0 + 20), (x0 + 28, y0 + 30)], fill=(200, 170, 90),
             width=px(1))
    elif kind == "cricket":
        art_bg(d, x0, y0, x1, y1, (120, 160, 200), (40, 110, 60))
        rect(d, x0, y1 - 22, x1, y1, fill=(46, 120, 66))
        line(d, [(x0 + 8, y1 - 34), (x0 + 30, y1 - 52), (x0 + 34, y1 - 50)],
             fill=(190, 150, 90), width=px(3))
        ell(d, x0 + 40, y1 - 40, x0 + 46, y1 - 34, fill=(200, 40, 40))
        for k in range(3):
            sx = x0 + 40 + k * 4
            line(d, [(sx, y1 - 16), (sx, y1 - 22)],
                 fill=(240, 240, 230), width=px(1))
    elif kind == "hunger":
        art_bg(d, x0, y0, x1, y1, (30, 20, 40), (120, 50, 20))
        for rr, col in ((22, (120, 66, 32)), (16, (170, 84, 32)),
                        (10, (220, 110, 40))):
            ell(d, x0 + 28 - rr, y1 - 18 - rr, x0 + 28 + rr, y1 - 18 + rr,
                fill=col)
        poly(d, [(x0 + 28, y0 + 34), (x0 + 20, y1 - 14), (x0 + 36, y1 - 14)],
             fill=(255, 190, 80))
        line(d, [(x0 + 10, y0 + 12), (x0 + 46, y0 + 30)],
             fill=(220, 200, 160), width=px(2))
        poly(d, [(x0 + 46, y0 + 30), (x0 + 40, y0 + 29), (x0 + 45, y0 + 24)],
             fill=(220, 200, 160))
    elif kind == "jet":
        art_bg(d, x0, y0, x1, y1, (80, 110, 150), (200, 180, 140))
        ell(d, x0 + 30, y0 + 6, x0 + 50, y0 + 26, fill=(255, 220, 140))
        poly(d, [(x0 + 8, y1 - 24), (x0 + 44, y1 - 30), (x0 + 48, y1 - 24),
                 (x0 + 12, y1 - 18)], fill=(240, 240, 235))
        poly(d, [(x0 + 40, y1 - 30), (x0 + 48, y1 - 44), (x0 + 50, y1 - 30)],
             fill=(200, 40, 40))
        for k in range(3):
            line(d, [(x0 + 10, y1 - 8 + k * 4), (x0 + 46, y1 - 8 + k * 4)],
                 fill=(120, 140, 160), width=px(1))
    d.rectangle([px(x0), px(y0), px(x1), px(y1)], outline=(90, 74, 32),
                width=px(1))

# --- cards, briefs, footer -------------------------------------------------
def draw_cards(d):
    txt(d, 16, 460, "TWELVE SCENES", font(SANS_B, 13), GOLD)
    txt(d, 1008, 462, "ILLUSTRATED FROM THE DAY'S REPORTING",
        font(SANS_B, 10), MUTED, anchor="ra")
    cw, chh, gx, gy = 242, 64, 8, 6
    for i, (num, head, d1, d2, src, kind, chip) in enumerate(CARDS):
        col, row = i % 4, i // 4
        x0 = 16 + col * (cw + gx)
        y0 = 482 + row * (chh + gy)
        x1, y1 = x0 + cw, y0 + chh
        rect(d, x0, y0, x1, y1, fill=PANEL)
        d.rectangle([px(x0), px(y0), px(x1), px(y1)], outline=PANEL_LINE,
                    width=px(1))
        draw_scene(d, kind, x0 + 1, y0 + 1, x0 + 57, y1 - 1)
        tx = x0 + 63
        tw = x1 - tx - 6
        txt(d, tx, y0 + 5, head, font(SANS_B, 11), CREAM)
        txt(d, tx, y0 + 21, d1, font(SANS, 9.5), CREAM_DIM)
        if chip:
            # label chip bottom-right; deck line 2 shortens to clear it
            cw2 = text_w(d, chip, font(SANS_B, 9)) + 10
            cx1 = x1 - 5
            cx0 = cx1 - cw2
            rect(d, cx0, y1 - 17, cx1, y1 - 5, outline=GOLD, fill=None)
            centre(d, (cx0 + cx1) / 2, y1 - 15, chip, font(SANS_B, 9), GOLD)
            d2w = tw - cw2 - 6
        else:
            d2w = tw
        lines = wrap_n(d, d2, font(SANS, 9.5), d2w, 1)
        txt(d, tx, y0 + 33, lines[0], font(SANS, 9.5), CREAM_DIM)
        txt(d, tx, y0 + 50, num + "  ·  " + src.upper(),
            font(SANS_B, 8.5), GOLD_SOFT)


def draw_briefs(d):
    txt(d, 16, 692, "THE DAY IN BRIEF", font(SANS_B, 13), GOLD)
    txt(d, 1008, 694, "26 MORE STORIES, NUMBERED",
        font(SANS_B, 10), MUTED, anchor="ra")
    for i, text in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        x0 = 16 if col == 0 else 520
        y = 712 + row * 19
        num = str(18 + i)
        txt(d, x0, y, num, font(SANS_B, 11), GOLD)
        txt(d, x0 + 24, y, text, font(SANS, 11), CREAM)


def draw_footer(d):
    rect(d, 16, 962, 1008, 986, fill=GOLD)
    centre(d, 512, 968, MARKETS, font(SANS_B, 12), INK)
    txt(d, 16, 991, SOURCES, font(SANS, 9.5), MUTED)
    centre(d, 512, 1004, CREDIT, font(SANS, 9.5), MUTED)


def build():
    img = Image.new("RGB", (px(W), px(H)), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([px(6), px(6), px(1018), px(1018)], outline=GOLD,
                width=px(2))
    draw_masthead(d)
    draw_lead(d)
    draw_tops(d)
    line(d, [(16, 302), (1008, 302)], fill=GOLD_DIM, width=px(1))
    draw_map(d)
    line(d, [(16, 454), (1008, 454)], fill=GOLD_DIM, width=px(1))
    draw_cards(d)
    draw_briefs(d)
    draw_footer(d)
    return img.resize((W, H), Image.LANCZOS)


def main():
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    img = build()
    img.save(os.path.join(out, "entry.png"), format="PNG")
    return 0


if __name__ == "__main__":
    sys.exit(main())
