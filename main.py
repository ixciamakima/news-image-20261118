#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - An Illustrated Atlas of Wednesday 18 November 2026.

Entry for make.fun news-image-20261118 (round 2). Unlike round 1's
broadsheet of text columns, this edition is an illustrated atlas plate:
one big hero painting of the lead story, a pinned world map, twelve
illustrated scene cards, four top stories and a numbered briefs index -
43 verified stories of the day, drawn programmatically with Pillow.

The program is deterministic: two runs write byte-identical entry.png.
Standard library only (Pillow ships with the harness image); no network.
Output: argv[1] if given, else $MAKEFUN_OUTPUT_DIR/entry.png, else
/output/entry.png.
"""

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024          # final pixels (competition cap: 1024 x 1024)
SS = 2                     # supersampling factor for smooth rendering

# ---------------------------------------------------------------- palette
INK = (9, 19, 34)          # deep atlas navy, page background
NAVY = (17, 36, 60)        # panel navy
NAVY2 = (24, 48, 78)       # lighter navy
GOLD = (216, 178, 62)      # masthead gold
GOLD_L = (240, 209, 110)   # bright gold
CREAM = (247, 241, 226)    # card cream
PAPER = (252, 248, 238)    # bright paper
CHAR = (26, 30, 40)        # dark text on cream
SLATE = (84, 96, 112)      # muted text
RED = (196, 44, 48)        # pin / accent red
TEAL = (16, 92, 104)       # ocean teal
TEAL_D = (10, 58, 74)
LAND = (222, 198, 138)     # map landmass tan
LAND_D = (198, 168, 108)
SKY_D = (24, 42, 84)       # hero night sky top
SKY_L = (88, 120, 178)     # hero night sky horizon
SEA = (18, 66, 96)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- fonts
_FONT_DIR = "/usr/share/fonts/truetype"
_PATHS = {
    "serif_b": _FONT_DIR + "/dejavu/DejaVuSerif-Bold.ttf",
    "serif": _FONT_DIR + "/dejavu/DejaVuSerif.ttf",
    "sans": _FONT_DIR + "/liberation/LiberationSans-Regular.ttf",
    "sans_b": _FONT_DIR + "/liberation/LiberationSans-Bold.ttf",
    "sans_i": _FONT_DIR + "/liberation/LiberationSans-Italic.ttf",
}
_font_cache = {}


def F(kind, size):
    """Font at a size given in final pixels (scaled for supersampling)."""
    key = (kind, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(_PATHS[kind], int(round(size * SS)))
    return _font_cache[key]


# ---------------------------------------------------------------- scaling
def X(v):
    return int(round(v * SS))


def BOX(b):
    return [X(b[0]), X(b[1]), X(b[2]), X(b[3])]


def PTS(seq):
    return [(X(a), X(b)) for a, b in seq]


# ---------------------------------------------------------------- helpers
def vgrad(d, box, top, bot):
    """Vertical gradient inside box (final-px coords)."""
    x0, y0, x1, y1 = box
    steps = max(1, int((y1 - y0) * SS))
    for i in range(steps + 1):
        t = i / steps
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        yy = y0 + (y1 - y0) * t
        d.line([X(x0), X(yy), X(x1), X(yy)], fill=c, width=max(1, X((y1 - y0) / steps) + 1))


def hgrad(d, box, left, right):
    """Horizontal gradient inside box (final-px coords)."""
    x0, y0, x1, y1 = box
    steps = max(1, int((x1 - x0) * SS))
    for i in range(steps + 1):
        t = i / steps
        c = tuple(int(left[k] + (right[k] - left[k]) * t) for k in range(3))
        xx = x0 + (x1 - x0) * t
        d.line([X(xx), X(y0), X(xx), X(y1)], fill=c, width=max(1, X((x1 - x0) / steps) + 1))


def tw(d, s, f):
    return d.textlength(s, font=f) / SS


def wrap(d, s, f, maxw):
    """Greedy word wrap; returns a list of lines that fit maxw final px."""
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if tw(d, trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def text(d, x, y, s, f, fill, anchor="la"):
    d.text((X(x), X(y)), s, font=f, fill=fill, anchor=anchor)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(BOX(box), radius=X(r), fill=fill, outline=outline,
                        width=max(1, X(width)))


def star(d, cx, cy, r, fill, ratio=0.38):
    """Four-point starburst (explosions, camera flashes, sparkle)."""
    pts = []
    for i in range(8):
        ang = i * 3.14159265 / 4.0
        rr = r if i % 2 == 0 else r * ratio
        import math
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(PTS(pts), fill=fill)


def grain(img, seed=20261118, alpha=14):
    """Deterministic fine grain: a seeded 256px tile blended over img."""
    rng = random.Random(seed)
    tile = Image.new("L", (256, 256))
    tile.putdata([rng.randint(0, 255) for _ in range(256 * 256)])
    tile = tile.resize((X(256), X(256)), Image.NEAREST)
    overlay = Image.new("L", img.size, 0)
    for yy in range(0, img.size[1], tile.size[1]):
        for xx in range(0, img.size[0], tile.size[0]):
            overlay.paste(tile, (xx, yy))
    black = Image.new("RGB", img.size, (0, 0, 0))
    white = Image.new("RGB", img.size, (255, 255, 255))
    img.paste(Image.blend(img, white, 0.5), (0, 0), overlay.point(lambda v: int(v * alpha / 255)))
    return img


def dashed_arc(d, box, start, end, fill, width=2, dash=7, gap=5):
    """Approximate a dashed arc with short chord segments."""
    import math
    steps = 60
    on = True
    acc = 0.0
    prev = None
    for i in range(steps + 1):
        t = i / steps
        ang = math.radians(start + (end - start) * t)
        cx = (box[0] + box[2]) / 2.0
        cy = (box[1] + box[3]) / 2.0
        rx = (box[2] - box[0]) / 2.0
        ry = (box[3] - box[1]) / 2.0
        p = (cx + rx * math.cos(ang), cy + ry * math.sin(ang))
        if prev is not None:
            seg = math.hypot(p[0] - prev[0], p[1] - prev[1])
            acc += seg
            if on:
                d.line([X(prev[0]), X(prev[1]), X(p[0]), X(p[1])], fill=fill, width=max(1, X(width)))
            if acc >= (dash if on else gap):
                on = not on
                acc = 0.0
        prev = p


# ---------------------------------------------------------------- content
# Every story below was reported on Wednesday 18 November 2026 and was
# verified against the named outlets (round-1 research, REPORT.md).
# Numbering: lead = 1, top stories = 2-5, scene cards = 6-17,
# briefs = 18-43. Total: 43 stories, 6 regions, 13 illustrated scenes.

LEAD = {
    "kicker": "THE LEAD - THE GULF, BEFORE DAWN",
    "headline": "IRAN STRIKES KUWAIT & BAHRAIN",
    "deck": ("Tehran says it hit US drone and missile sites in Kuwait overnight "
             "after the US struck Qeshm Island; Kuwait repelled the attack and "
             "Bahrain intercepted drones for a third time in a week."),
    "source": "Reuters / BBC / WSJ",
}

TOP = [
    ("Trump hails 'very big' Philippines trade deal",
     "Announced over a state lunch in Manila, capping a day of "
     "Asia deal-making.", "AP"),
    ("Anthropic files record $81.3bn IPO",
     "The Claude-maker is valued near $1.4 trillion in the largest "
     "AI listing yet.", "NPR / BBC"),
    ("US loses measles-elimination status",
     "A year of continuous spread ends a status held since 2000.", "AP"),
    ("Kahana elected Knesset speaker",
     "Matan Kahana takes the chair as Eisenkot's Yashar party wins.",
     "Just Security"),
]

# key = scene painter name, tag = region/beat, headline, source
SCENES = [
    ("shenzhen", "ASIA", "Xi & Putin meet in Shenzhen", "Reuters / AP"),
    ("alaska", "NORTH AMERICA", "Democrats take the Senate, 56-44", "AP / BBC"),
    ("nvidia", "TECH", "Nvidia beats forecasts, shares +5%", "Reuters"),
    ("cop31", "CLIMATE", "COP31 stocktake opens in Antalya", "UN News"),
    ("waymo", "TECH", "Waymo pulls robotaxis from freeways", "BBC"),
    ("myanmar", "ASIA", "Myanmar genocide verdict looms", "BBC"),
    ("hobart", "SPORT", "England beat Australia by 97 runs", "ESPNcricinfo"),
    ("aden", "MIDDLE EAST", "Houthis retake Bab el-Mandeb", "Reuters"),
    ("ford", "BUSINESS", "Ford ships first CATL-tech cells", "Reuters"),
    ("earthshot", "CULTURE", "Earthshot green carpet in Mumbai", "BBC"),
    ("ghana", "AFRICA", "Ghana's $60m jet sparks outrage", "BBC"),
    ("hunger", "CULTURE", "Hunger Games prequel splits opinion", "BBC"),
]

BRIEFS = [
    "Mossad chief lobbied Washington for new joint strikes on Iran (Reuters)",
    "Bahrain's Bapco refinery back above 80% capacity after attacks (Reuters)",
    "Iraq PM orders crackdown on Kataib Hezbollah oil-smuggling ring (Reuters)",
    "Vance: US will not let Gulf war become 'another forever war' (Reuters)",
    "Trump's Board of Peace: Israel and Hamas broke commitments (Just Security)",
    "Ethiopia and Eritrea mass forces along their shared border (Reuters)",
    "Myanmar's president orders ASEAN ties review over 'unfair treatment' (AP)",
    "US officer held in UK over Russia spying taken into US custody (BBC)",
    "Pakistani man jailed 27 years for Iran-backed plot to kill Trump (BBC)",
    "UK inflation hits 3.6% as fuel costs push energy bills up \u00a3443 a year (BBC)",
    "Burnham to set out EU options next month; Lammy urges rejoin pledge (BBC)",
    "Critical Java security flaw found by an AI startup (BBC)",
    "Gold falls over 2% to $3,770, its lowest since September 2025 (Morning Brief)",
    "Brent crude near $92, down 23% from its October peak (Reuters)",
    "Indian bonds draw $1.1bn of foreign inflows in November (Reuters)",
    "China to invest $15bn in Turkish renewables, 7 GW solar & wind (Weekly Anthropocene)",
    "Norway to fund 12m tonnes of emissions cuts in Indonesia (Weekly Anthropocene)",
    "BYD unveils a 1 MW solar EV charger in Abu Dhabi (Weekly Anthropocene)",
    "Yangwang U9 Xtreme tops 500 km/h in record run (Weekly Anthropocene)",
    "Chahal becomes first Indian to 400 T20 wickets (ESPNcricinfo)",
    "Bihar stun Delhi, chasing 225 in the Syed Mushtaq Ali Trophy (ESPNcricinfo)",
    "California landfill eruption spews black substance into the air (BBC)",
    "Irishman charged with destroying US military aircraft with an axe (BBC)",
    "Rubio: US not 'under systemic attack' after sweeping tech outages (BBC)",
    "Homeland chief Mullin faces House hearing after flight chaos (Level Headlines)",
    "Bezos 'heavily involved' as Pattinson is cast as the new 007 (BBC)",
]

MARKETS = ("MARKETS   Gold $3,770  -2.1%   \u00b7   Brent $92   \u00b7   "
           "Nvidia +5% after hours   \u00b7   Rupee 93.44/$   \u00b7   India bonds +$1.1bn")

SOURCES = ("Sources: Reuters \u00b7 BBC \u00b7 AP \u00b7 NPR \u00b7 ESPNcricinfo \u00b7 UN News \u00b7 "
           "Just Security \u00b7 Level Headlines \u00b7 Morning Brief \u00b7 The Weekly "
           "Anthropocene \u00b7 Bangkok Post")

# ------------------------------------------------------- drawing helpers
def sun(d, cx, cy, r, fill=(250, 197, 66), ray=(250, 197, 66)):
    import math
    for i in range(12):
        a = i * math.pi / 6.0
        x0, y0 = cx + (r + 2) * math.cos(a), cy + (r + 2) * math.sin(a)
        x1, y1 = cx + (r + 8) * math.cos(a), cy + (r + 8) * math.sin(a)
        d.line([X(x0), X(y0), X(x1), X(y1)], fill=ray, width=max(1, X(2)))
    d.ellipse(BOX((cx - r, cy - r, cx + r, cy + r)), fill=fill)


def moon(d, cx, cy, r, fill=(238, 240, 220)):
    d.ellipse(BOX((cx - r, cy - r, cx + r, cy + r)), fill=fill)
    for dx, dy, rr in ((-0.3, -0.2, 0.16), (0.25, 0.3, 0.12), (0.05, -0.45, 0.09)):
        d.ellipse(BOX((cx + dx * r - rr * r, cy + dy * r - rr * r,
                       cx + dx * r + rr * r, cy + dy * r + rr * r)),
                  fill=(214, 216, 198))


def cloud(d, x, y, s, fill=(255, 255, 255)):
    d.ellipse(BOX((x, y, x + 34 * s, y + 11 * s)), fill=fill)
    d.ellipse(BOX((x + 7 * s, y - 6 * s, x + 24 * s, y + 8 * s)), fill=fill)
    d.ellipse(BOX((x + 18 * s, y - 3 * s, x + 40 * s, y + 9 * s)), fill=fill)


def skyline(d, box, seed, base=(38, 52, 84), win=(250, 214, 120), dark=False):
    """Deterministic city skyline along the bottom of box."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    bx = x0
    while bx < x1 - 6:
        bw = rng.uniform(9, 20)
        bh = rng.uniform((y1 - y0) * 0.35, (y1 - y0) * 0.92)
        col = base if not dark else (16, 24, 40)
        d.rectangle(BOX((bx, y1 - bh, bx + bw, y1)), fill=col)
        if rng.random() < 0.4:
            d.rectangle(BOX((bx + bw * 0.3, y1 - bh - 4, bx + bw * 0.7, y1 - bh)), fill=col)
        for wy in range(int(y1 - bh) + 4, int(y1) - 4, 6):
            for wx in range(int(bx) + 2, int(bx + bw) - 2, 5):
                if rng.random() < 0.45:
                    d.rectangle(BOX((wx, wy, wx + 2, wy + 3)), fill=win)
        bx += bw + rng.uniform(1, 4)


def flag(d, x, y, w, kind):
    """Small waving flag of width w at (x, y) top-left; pole included."""
    h = w * 0.62
    d.line([X(x), X(y), X(x), X(y + h + 12)], fill=(60, 60, 66), width=max(1, X(1.6)))
    wave = [(x + 1, y), (x + w * 0.55, y + h * 0.10), (x + w, y + h * 0.02),
            (x + w, y + h * 0.72), (x + w * 0.55, y + h * 0.82), (x + 1, y + h * 0.7)]
    if kind == "china":
        d.polygon(PTS(wave), fill=(206, 42, 44))
        star(d, x + w * 0.24, y + h * 0.3, w * 0.13, GOLD_L, ratio=0.45)
    elif kind == "russia":
        d.polygon(PTS(wave), fill=(245, 245, 245))
        d.polygon(PTS([(x + 1, y + h * 0.24), (x + w * 0.55, y + h * 0.33),
                       (x + w, y + h * 0.25), (x + w, y + h * 0.48),
                       (x + w * 0.55, y + h * 0.57), (x + 1, y + h * 0.47)]), fill=(40, 80, 170))
        d.polygon(PTS([(x + 1, y + h * 0.47), (x + w * 0.55, y + h * 0.57),
                       (x + w, y + h * 0.48), (x + w, y + h * 0.72),
                       (x + w * 0.55, y + h * 0.82), (x + 1, y + h * 0.7)]), fill=(206, 42, 44))
    elif kind == "usa":
        d.polygon(PTS(wave), fill=(178, 34, 52))
        for i in range(3):
            yy = y + h * (0.14 + 0.24 * i)
            d.line([X(x + 2), X(yy), X(x + w - 1), X(yy + h * 0.05)], fill=(245, 245, 245), width=max(1, X(1.6)))
        d.rectangle(BOX((x + 1, y, x + w * 0.42, y + h * 0.4)), fill=(40, 50, 130))
    elif kind == "turkey":
        d.polygon(PTS(wave), fill=(206, 42, 44))
        d.ellipse(BOX((x + w * 0.22, y + h * 0.22, x + w * 0.52, y + h * 0.58)), fill=(245, 245, 245))
        d.ellipse(BOX((x + w * 0.30, y + h * 0.25, x + w * 0.58, y + h * 0.55)), fill=(206, 42, 44))
    elif kind == "india":
        d.polygon(PTS(wave), fill=(238, 240, 235))
        d.polygon(PTS([(x + 1, y), (x + w * 0.55, y + h * 0.10), (x + w, y + h * 0.02),
                       (x + w, y + h * 0.26), (x + w * 0.55, y + h * 0.34), (x + 1, y + h * 0.24)]), fill=(240, 140, 50))
        d.polygon(PTS([(x + 1, y + h * 0.47), (x + w * 0.55, y + h * 0.57),
                       (x + w, y + h * 0.48), (x + w, y + h * 0.72),
                       (x + w * 0.55, y + h * 0.82), (x + 1, y + h * 0.7)]), fill=(30, 140, 70))
        d.ellipse(BOX((x + w * 0.40, y + h * 0.30, x + w * 0.52, y + h * 0.52)), outline=(30, 50, 150), width=max(1, X(1.2)))
    elif kind == "ghana":
        d.polygon(PTS(wave), fill=(240, 190, 40))
        d.polygon(PTS([(x + 1, y), (x + w * 0.55, y + h * 0.10), (x + w, y + h * 0.02),
                       (x + w, y + h * 0.26), (x + w * 0.55, y + h * 0.34), (x + 1, y + h * 0.24)]), fill=(206, 42, 44))
        d.polygon(PTS([(x + 1, y + h * 0.47), (x + w * 0.55, y + h * 0.57),
                       (x + w, y + h * 0.48), (x + w, y + h * 0.72),
                       (x + w * 0.55, y + h * 0.82), (x + 1, y + h * 0.7)]), fill=(20, 130, 70))
        star(d, x + w * 0.5, y + h * 0.42, w * 0.13, (20, 20, 20), ratio=0.45)
    else:  # generic gold banner
        d.polygon(PTS(wave), fill=GOLD)


def ship(d, x, y, s, hull=(30, 38, 52), accent=(196, 44, 48)):
    """Cargo ship silhouette; (x, y) = waterline left, s = length scale."""
    L, Hh = 62 * s, 13 * s
    d.polygon(PTS([(x, y - Hh * 0.5), (x + L * 0.12, y), (x + L * 0.9, y),
                   (x + L, y - Hh * 0.5), (x + L * 0.96, y - Hh * 0.95),
                   (x + L * 0.05, y - Hh * 0.95)]), fill=hull)
    for i, c in enumerate([(70, 110, 160), accent, (90, 140, 90), (200, 160, 60)]):
        d.rectangle(BOX((x + L * (0.16 + 0.15 * i), y - Hh * (1.5 + (0.35 if i % 2 else 0)),
                         x + L * (0.29 + 0.15 * i), y - Hh * 0.95)), fill=c)
    d.rectangle(BOX((x + L * 0.8, y - Hh * 2.1, x + L * 0.9, y - Hh * 0.95)), fill=(225, 228, 232))
    d.rectangle(BOX((x + L * 0.83, y - Hh * 2.5, x + L * 0.87, y - Hh * 2.1)), fill=hull)


def waves(d, box, color, n=4, amp=2.2, seed=7):
    import math
    rng = random.Random(seed)
    x0, y0, x1, y1 = box
    for i in range(n):
        yy = y0 + (y1 - y0) * (i + 0.5) / n + rng.uniform(-1.5, 1.5)
        pts = []
        for xx in range(int(x0), int(x1), 7):
            pts.append((xx, yy + amp * math.sin((xx - x0) / 16.0 + i * 1.7)))
        d.line(PTS(pts), fill=color, width=max(1, X(1.3)))


def palm(d, x, y, s, col=(24, 90, 52)):
    import math
    d.line([X(x), X(y), X(x + 3 * s), X(y - 16 * s)], fill=(110, 82, 50), width=max(1, X(2.2 * s)))
    cx, cy = x + 3 * s, y - 16 * s
    for a in (-160, -115, -70, -25, 15):
        ex = cx + 11 * s * math.cos(math.radians(a))
        ey = cy + 6.5 * s * math.sin(math.radians(a)) + 2.5 * s
        d.arc(BOX((cx - 11 * s, cy - 4 * s, cx + 11 * s, cy + 8 * s)),
              start=a, end=a + 55, fill=col, width=max(1, X(2 * s)))
        d.line([X(cx), X(cy), X(ex), X(ey)], fill=col, width=max(1, X(1.6 * s)))


def person(d, cx, base, h, col=(20, 26, 38), accent=None):
    """Simple standing figure: head + coat body. base = feet y."""
    r = h * 0.13
    d.ellipse(BOX((cx - r, base - h, cx + r, base - h + 2 * r)), fill=col)
    d.polygon(PTS([(cx - h * 0.16, base), (cx - h * 0.10, base - h * 0.72),
                   (cx + h * 0.10, base - h * 0.72), (cx + h * 0.16, base)]), fill=col)
    if accent:
        d.rectangle(BOX((cx - h * 0.10, base - h * 0.66, cx + h * 0.10, base - h * 0.55)), fill=accent)


def explosion(d, cx, cy, r):
    star(d, cx, cy, r, (240, 120, 30))
    star(d, cx, cy, r * 0.62, (250, 190, 60))
    star(d, cx, cy, r * 0.3, (255, 240, 200))


# ------------------------------------------------------- scene painters
def paint_hero(d, box):
    """LEAD: night over the Strait of Hormuz - strikes and interceptions."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, SKY_D, SKY_L)
    rng = random.Random(18)
    for _ in range(90):
        sx, sy = rng.uniform(x0, x1), rng.uniform(y0, y0 + h * 0.5)
        r = rng.uniform(0.5, 1.3)
        d.ellipse(BOX((sx - r, sy - r, sx + r, sy + r)), fill=(230, 235, 250))
    moon(d, x1 - w * 0.09, y0 + h * 0.2, h * 0.11)
    sea_y = y0 + h * 0.66
    vgrad(d, (x0, sea_y, x1, y1), (26, 78, 116), SEA)
    # coast silhouettes: Kuwait side left, Qeshm / Iran side right
    d.polygon(PTS([(x0, sea_y + 4), (x0 + w * 0.16, sea_y - h * 0.1),
                   (x0 + w * 0.3, sea_y + 2), (x0 + w * 0.34, sea_y + 6),
                   (x0, sea_y + 10)]), fill=(13, 22, 38))
    d.polygon(PTS([(x1, sea_y + 2), (x1 - w * 0.14, sea_y - h * 0.13),
                   (x1 - w * 0.28, sea_y), (x1 - w * 0.33, sea_y + 6),
                   (x1, sea_y + 10)]), fill=(13, 22, 38))
    skyline(d, (x0, sea_y - h * 0.16, x0 + w * 0.2, sea_y + 4), 41, dark=True)
    # missile arcs both ways + interception bursts
    dashed_arc(d, (x0 + w * 0.3, y0 + h * 0.02, x0 + w * 0.78, y0 + h * 0.62),
               200, 330, (255, 170, 80), width=2.2)
    dashed_arc(d, (x0 + w * 0.24, y0 + h * 0.1, x0 + w * 0.66, y0 + h * 0.6),
               30, 150, (255, 120, 90), width=2.2)
    explosion(d, x0 + w * 0.13, sea_y - h * 0.05, h * 0.075)
    explosion(d, x0 + w * 0.47, y0 + h * 0.3, h * 0.06)
    explosion(d, x0 + w * 0.6, y0 + h * 0.42, h * 0.05)
    # drone silhouette, centre top
    dx, dy = x0 + w * 0.52, y0 + h * 0.16
    d.rectangle(BOX((dx - 9, dy - 3, dx + 9, dy + 3)), fill=(10, 14, 22))
    for sx in (-14, 14):
        d.line([X(dx + sx * 0.5), X(dy), X(dx + sx), X(dy - 4)], fill=(10, 14, 22), width=max(1, X(2)))
        d.line([X(dx + sx - 5), X(dy - 5), X(dx + sx + 5), X(dy - 5)], fill=(10, 14, 22), width=max(1, X(2)))
    # ships on the strait
    ship(d, x0 + w * 0.34, y0 + h * 0.86, 0.62)
    ship(d, x0 + w * 0.68, y0 + h * 0.93, 0.45)
    waves(d, (x0, sea_y + 3, x1, y1), (90, 140, 180), n=4, seed=3)


def paint_shenzhen(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (96, 150, 205), (196, 224, 240))
    sun(d, x0 + (x1 - x0) * 0.84, y0 + (y1 - y0) * 0.24, 7)
    skyline(d, box, 99, base=(52, 74, 110), win=(250, 226, 150))
    gy = y1
    for i, kind in enumerate(("china", "russia", "usa")):
        flag(d, x0 + (x1 - x0) * (0.3 + 0.17 * i), gy - 34, 24, kind)


def paint_alaska(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, (168, 196, 224), (232, 240, 248))
    d.polygon(PTS([(x0, y1 - h * 0.42), (x0 + w * 0.2, y0 + h * 0.2),
                   (x0 + w * 0.42, y1 - h * 0.42)]), fill=(240, 244, 250))
    d.polygon(PTS([(x0 + w * 0.3, y1 - h * 0.42), (x0 + w * 0.55, y0 + h * 0.1),
                   (x0 + w * 0.8, y1 - h * 0.42)]), fill=(226, 234, 244))
    d.rectangle(BOX((x0, y1 - h * 0.42, x1, y1)), fill=(248, 250, 252))
    # ballot box with paper going in
    bx, by = x0 + w * 0.1, y1 - h * 0.62
    d.rectangle(BOX((bx, by, bx + w * 0.26, by + h * 0.44)), fill=(150, 42, 48))
    d.rectangle(BOX((bx - 2, by - 4, bx + w * 0.26 + 2, by)), fill=(110, 30, 36))
    d.polygon(PTS([(bx + w * 0.05, by - 4), (bx + w * 0.1, by - h * 0.3),
                   (bx + w * 0.22, by - h * 0.26), (bx + w * 0.17, by - 2)]), fill=(255, 255, 255))
    d.line([X(bx + w * 0.08), X(by - h * 0.2), X(bx + w * 0.12), X(by - h * 0.12)],
           fill=(30, 130, 70), width=max(1, X(2.4)))
    d.line([X(bx + w * 0.12), X(by - h * 0.12), X(bx + w * 0.19), X(by - h * 0.24)],
           fill=(30, 130, 70), width=max(1, X(2.4)))
    text(d, x0 + w * 0.44, y0 + h * 0.16, "56-44", F("sans_b", 25), (18, 40, 84))
    text(d, x0 + w * 0.44, y0 + h * 0.52, "SENATE", F("sans_b", 10.5), (90, 104, 128))


def paint_nvidia(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(BOX(box), fill=(12, 20, 18))
    # circuit traces
    for i, (tx, ty) in enumerate(((0.08, 0.3), (0.08, 0.7), (0.92, 0.25), (0.92, 0.75), (0.5, 0.06))):
        ex, ey = x0 + w * tx, y0 + h * ty
        cx, cy = x0 + w * 0.36, y0 + h * 0.5
        d.line([X(ex), X(ey), X(cx if tx < 0.5 else ex), X(ey)], fill=(46, 120, 84), width=max(1, X(1.4)))
        d.line([X(cx if tx < 0.5 else ex), X(ey), X(x0 + w * (0.3 if tx < 0.5 else 0.62)), X(cy)], fill=(46, 120, 84), width=max(1, X(1.4)))
        d.ellipse(BOX((ex - 2, ey - 2, ex + 2, ey + 2)), fill=(120, 220, 160))
    # the chip
    cw, ch = w * 0.34, h * 0.72
    cx0, cy0 = x0 + w * 0.28, y0 + h * 0.14
    for i in range(6):
        px = cx0 + cw * (i + 0.5) / 6
        d.line([X(px), X(cy0 - 5), X(px), X(cy0)], fill=(180, 190, 200), width=max(1, X(2)))
        d.line([X(px), X(cy0 + ch), X(px), X(cy0 + ch + 5)], fill=(180, 190, 200), width=max(1, X(2)))
    for i in range(3):
        py = cy0 + ch * (i + 0.5) / 3
        d.line([X(cx0 - 5), X(py), X(cx0), X(py)], fill=(180, 190, 200), width=max(1, X(2)))
        d.line([X(cx0 + cw), X(py), X(cx0 + cw + 5), X(py)], fill=(180, 190, 200), width=max(1, X(2)))
    rrect(d, (cx0, cy0, cx0 + cw, cy0 + ch), 4, fill=(118, 186, 60))
    rrect(d, (cx0 + cw * 0.18, cy0 + ch * 0.18, cx0 + cw * 0.82, cy0 + ch * 0.82), 3, fill=(88, 148, 44))
    text(d, cx0 + cw / 2, cy0 + ch / 2, "AI", F("sans_b", 15), (255, 255, 255), anchor="mm")
    # rising bars + gain
    base = y1 - 4
    for i, bh in enumerate((0.18, 0.3, 0.26, 0.44, 0.62)):
        bx = x0 + w * (0.68 + 0.055 * i)
        d.rectangle(BOX((bx, base - h * bh, bx + w * 0.04, base)), fill=(118, 186, 60))
    text(d, x0 + w * 0.7, y0 + h * 0.06, "+5%", F("sans_b", 14), (140, 230, 120))


def paint_cop31(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, (x0, y0, x1, y0 + h * 0.62), (110, 170, 215), (205, 232, 244))
    sun(d, x0 + w * 0.12, y0 + h * 0.2, 6.5)
    d.rectangle(BOX((x0, y0 + h * 0.52, x1, y0 + h * 0.72)), fill=(64, 140, 165))
    waves(d, (x0, y0 + h * 0.54, x1, y0 + h * 0.7), (170, 215, 225), n=2, seed=11)
    d.rectangle(BOX((x0, y0 + h * 0.72, x1, y1)), fill=(238, 214, 160))
    # conference hall
    hx, hy, hw, hh = x0 + w * 0.3, y0 + h * 0.3, w * 0.44, h * 0.42
    d.rectangle(BOX((hx, hy, hx + hw, hy + hh)), fill=(246, 248, 250))
    d.polygon(PTS([(hx - 4, hy), (hx + hw + 4, hy), (hx + hw * 0.78, hy - h * 0.12),
                   (hx + hw * 0.22, hy - h * 0.12)]), fill=(52, 110, 140))
    for i in range(5):
        d.rectangle(BOX((hx + 5 + i * hw * 0.18, hy + hh * 0.2, hx + 5 + (i + 0.6) * hw * 0.18, hy + hh * 0.8)), fill=(150, 190, 215))
    text(d, hx + hw / 2, hy + hh * 0.46, "COP31", F("sans_b", 12), (24, 70, 100), anchor="mm")
    flag(d, hx + hw * 0.44, hy - h * 0.3, 17, "turkey")
    palm(d, x0 + w * 0.1, y1 - 2, 0.85)
    palm(d, x0 + w * 0.9, y1 - 2, 0.7)


def paint_waymo(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, (x0, y0, x1, y0 + h * 0.55), (120, 165, 210), (205, 228, 240))
    skyline(d, (x0, y0, x0 + w * 0.3, y0 + h * 0.55), 5, base=(70, 92, 124), win=(250, 226, 150))
    skyline(d, (x0 + w * 0.7, y0, x1, y0 + h * 0.55), 6, base=(70, 92, 124), win=(250, 226, 150))
    d.rectangle(BOX((x0, y0 + h * 0.55, x1, y1)), fill=(86, 92, 102))
    d.polygon(PTS([(x0 + w * 0.42, y1), (x0 + w * 0.485, y0 + h * 0.55),
                   (x0 + w * 0.515, y0 + h * 0.55), (x0 + w * 0.58, y1)]), fill=(240, 240, 240))
    # robotaxi
    cx, cy, s = x0 + w * 0.5, y0 + h * 0.78, w / 232.0
    d.rectangle(BOX((cx - 30 * s, cy - 4 * s, cx + 30 * s, cy)), fill=(40, 44, 52))
    rrect(d, (cx - 34 * s, cy - 16 * s, cx + 34 * s, cy - 2 * s), 5 * s, fill=(240, 242, 245))
    rrect(d, (cx - 22 * s, cy - 27 * s, cx + 22 * s, cy - 14 * s), 5 * s, fill=(240, 242, 245))
    d.rectangle(BOX((cx - 19 * s, cy - 25 * s, cx - 2 * s, cy - 16 * s)), fill=(90, 130, 170))
    d.rectangle(BOX((cx + 3 * s, cy - 25 * s, cx + 19 * s, cy - 16 * s)), fill=(90, 130, 170))
    d.rectangle(BOX((cx - 6 * s, cy - 33 * s, cx + 6 * s, cy - 27 * s)), fill=(60, 66, 76))
    d.ellipse(BOX((cx - 3 * s, cy - 36 * s, cx + 3 * s, cy - 31 * s)), fill=(120, 200, 235))
    for wx in (-22, 22):
        d.ellipse(BOX((cx + (wx - 6) * s, cy - 8 * s, cx + (wx + 6) * s, cy + 4 * s)), fill=(24, 26, 32))
        d.ellipse(BOX((cx + (wx - 2.5) * s, cy - 4.5 * s, cx + (wx + 2.5) * s, cy + 0.5 * s)), fill=(150, 156, 164))
    for rr in (10, 15):
        d.ellipse(BOX((cx - rr * s, cy - 33 * s - rr * s * 0.4, cx + rr * s, cy - 33 * s + rr * s * 0.4)),
                  outline=(120, 200, 235), width=max(1, X(1)))


def paint_myanmar(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, (150, 158, 170), (214, 216, 210))
    # courthouse: pediment, columns, steps
    cx = x0 + w * 0.5
    d.polygon(PTS([(x0 + w * 0.14, y0 + h * 0.3), (cx, y0 + h * 0.06), (x1 - w * 0.14, y0 + h * 0.3)]), fill=(96, 100, 110))
    d.rectangle(BOX((x0 + w * 0.14, y0 + h * 0.3, x1 - w * 0.14, y0 + h * 0.36)), fill=(110, 114, 124))
    for i in range(5):
        cxx = x0 + w * (0.2 + 0.13 * i)
        d.rectangle(BOX((cxx, y0 + h * 0.36, cxx + w * 0.055, y0 + h * 0.78)), fill=(232, 234, 236))
    d.rectangle(BOX((x0 + w * 0.12, y0 + h * 0.78, x1 - w * 0.12, y0 + h * 0.84)), fill=(120, 124, 134))
    d.rectangle(BOX((x0 + w * 0.08, y0 + h * 0.84, x1 - w * 0.08, y0 + h * 0.9)), fill=(104, 108, 118))
    d.rectangle(BOX((x0, y1 - h * 0.1, x1, y1)), fill=(88, 92, 102))
    # scales of justice in front
    sx, sy = cx, y0 + h * 0.47
    d.line([X(sx), X(sy - 12), X(sx), X(sy + 13)], fill=(58, 50, 30), width=max(1, X(2.4)))
    d.line([X(sx - 15), X(sy - 9), X(sx + 15), X(sy - 9)], fill=(58, 50, 30), width=max(1, X(2)))
    for sgn in (-1, 1):
        px = sx + 15 * sgn
        d.line([X(px), X(sy - 9), X(px - 4), X(sy + 2)], fill=(58, 50, 30), width=max(1, X(1.2)))
        d.line([X(px), X(sy - 9), X(px + 4), X(sy + 2)], fill=(58, 50, 30), width=max(1, X(1.2)))
        d.arc(BOX((px - 6, sy - 1, px + 6, sy + 8)), start=0, end=180, fill=(58, 50, 30), width=max(1, X(1.8)))
    d.rectangle(BOX((sx - 6, sy + 13, sx + 6, sy + 15.5)), fill=(58, 50, 30))


def paint_hobart(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, (x0, y0, x1, y0 + h * 0.5), (116, 172, 216), (208, 232, 244))
    d.rectangle(BOX((x0, y0 + h * 0.5, x1, y1)), fill=(52, 138, 66))
    d.rectangle(BOX((x0, y0 + h * 0.78, x1, y1)), fill=(46, 122, 58))
    # pitch
    d.polygon(PTS([(x0 + w * 0.36, y1), (x0 + w * 0.44, y0 + h * 0.52),
                   (x0 + w * 0.56, y0 + h * 0.52), (x0 + w * 0.64, y1)]), fill=(226, 204, 160))
    # stumps + bails
    for sx in (0.465, 0.5, 0.535):
        d.line([X(x0 + w * sx), X(y0 + h * 0.52), X(x0 + w * sx), X(y0 + h * 0.62)], fill=(240, 200, 60), width=max(1, X(1.8)))
    # batsman
    bx, by = x0 + w * 0.6, y0 + h * 0.86
    person(d, bx, by, h * 0.42, col=(24, 40, 92))
    d.polygon(PTS([(bx + 3, by - h * 0.24), (bx + w * 0.09, by - h * 0.05),
                   (bx + w * 0.105, by - h * 0.02), (bx + 5, by - h * 0.2)]), fill=(216, 190, 130))
    dashed_arc(d, (x0 + w * 0.55, y0 + h * 0.3, x0 + w * 0.97, y0 + h * 0.8), 160, 300, (255, 255, 255), width=1.6, dash=4, gap=4)
    d.ellipse(BOX((x0 + w * 0.9, y0 + h * 0.34, x0 + w * 0.9 + 5, y0 + h * 0.34 + 5)), fill=(200, 40, 40))
    # scoreboard
    d.rectangle(BOX((x0 + w * 0.03, y0 + h * 0.08, x0 + w * 0.3, y0 + h * 0.3)), fill=(16, 26, 40))
    text(d, x0 + w * 0.055, y0 + h * 0.115, "ENG +97", F("sans_b", 10.5), (250, 214, 120))
    text(d, x0 + w * 0.055, y0 + h * 0.21, "DUCKETT 133", F("sans", 8), (220, 228, 238))


def paint_aden(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(BOX(box), fill=(30, 96, 128))
    # two landmasses leaving a narrow strait
    d.polygon(PTS([(x0, y0), (x0 + w * 0.52, y0), (x0 + w * 0.44, y0 + h * 0.4),
                   (x0 + w * 0.5, y0 + h * 0.72), (x0 + w * 0.3, y1), (x0, y1)]), fill=LAND)
    d.polygon(PTS([(x1, y0 + h * 0.3), (x1, y1), (x0 + w * 0.62, y1),
                   (x0 + w * 0.58, y0 + h * 0.62), (x0 + w * 0.66, y0 + h * 0.34)]), fill=LAND_D)
    dashed_arc(d, (x0 + w * 0.3, y0 + h * 0.1, x0 + w * 0.85, y0 + h * 0.95), 60, 160, (255, 255, 255), width=1.6, dash=5, gap=4)
    ship(d, x0 + w * 0.42, y0 + h * 0.62, 0.5)
    star(d, x0 + w * 0.86, y0 + h * 0.18, 8, GOLD_L, ratio=0.3)
    text(d, x0 + w * 0.07, y0 + h * 0.1, "AFRICA", F("sans_b", 8.5), (120, 92, 40))
    text(d, x0 + w * 0.68, y0 + h * 0.82, "ARABIA", F("sans_b", 8.5), (110, 84, 36))


def paint_ford(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, (140, 164, 190), (214, 224, 232))
    d.rectangle(BOX((x0, y1 - h * 0.16, x1, y1)), fill=(96, 104, 114))
    # factory with sawtooth roof + chimney
    fx, fy, fw, fh = x0 + w * 0.04, y0 + h * 0.34, w * 0.52, h * 0.5
    d.rectangle(BOX((fx, fy, fx + fw, fy + fh)), fill=(104, 122, 144))
    for i in range(3):
        tx = fx + fw * i / 3
        d.polygon(PTS([(tx, fy), (tx + fw / 6, fy - h * 0.13), (tx + fw / 3, fy)]), fill=(80, 96, 116))
    d.rectangle(BOX((fx + fw * 0.78, fy - h * 0.34, fx + fw * 0.9, fy)), fill=(90, 100, 114))
    for i in range(4):
        d.rectangle(BOX((fx + 5 + i * fw * 0.22, fy + fh * 0.25, fx + 5 + (i + 0.6) * fw * 0.22, fy + fh * 0.62)), fill=(170, 205, 228))
    # battery cells rolling out
    for i, bx in enumerate((0.6, 0.74, 0.88)):
        cx, cy = x0 + w * bx, y0 + h * 0.52
        rrect(d, (cx, cy, cx + w * 0.1, cy + h * 0.3), 2.5, fill=(52, 160, 90))
        d.rectangle(BOX((cx + w * 0.03, cy - 3, cx + w * 0.07, cy)), fill=(52, 160, 90))
        d.polygon(PTS([(cx + w * 0.055, cy + h * 0.05), (cx + w * 0.03, cy + h * 0.16),
                       (cx + w * 0.05, cy + h * 0.16), (cx + w * 0.045, cy + h * 0.26)]), fill=(250, 230, 120))
    text(d, x0 + w * 0.06, y0 + h * 0.06, "MICHIGAN PLANT", F("sans_b", 9.5), (52, 72, 96))


def paint_earthshot(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(BOX(box), fill=(18, 34, 44))
    # step-and-repeat backdrop + arch title
    d.rectangle(BOX((x0 + w * 0.06, y0 + h * 0.08, x1 - w * 0.06, y0 + h * 0.66)), fill=(24, 52, 62))
    text(d, x0 + w * 0.5, y0 + h * 0.16, "EARTHSHOT", F("serif_b", 13), GOLD_L, anchor="ma")
    text(d, x0 + w * 0.5, y0 + h * 0.36, "MUMBAI", F("sans_b", 8.5), (170, 205, 190), anchor="ma")
    # green carpet
    d.polygon(PTS([(x0 + w * 0.22, y1), (x0 + w * 0.4, y0 + h * 0.62),
                   (x0 + w * 0.6, y0 + h * 0.62), (x0 + w * 0.78, y1)]), fill=(28, 140, 74))
    person(d, x0 + w * 0.44, y1 - h * 0.04, h * 0.5, col=(12, 16, 24), accent=(70, 110, 180))
    person(d, x0 + w * 0.57, y1 - h * 0.04, h * 0.47, col=(30, 20, 34), accent=(196, 44, 84))
    # camera flashes
    for fx, fy, fr in ((0.1, 0.24, 6), (0.9, 0.2, 7), (0.84, 0.52, 5), (0.14, 0.55, 5)):
        star(d, x0 + w * fx, y0 + h * fy, fr, (255, 250, 220))
    for fx in (0.08, 0.92):
        d.rectangle(BOX((x0 + w * fx - 4, y1 - h * 0.3, x0 + w * fx + 4, y1 - h * 0.16)), fill=(8, 10, 14))


def paint_ghana(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    vgrad(d, box, (104, 158, 208), (208, 230, 244))
    cloud(d, x0 + w * 0.06, y0 + h * 0.14, 0.5)
    cloud(d, x0 + w * 0.62, y0 + h * 0.6, 0.42)
    # presidential jet, nose right, climbing
    cx, cy = x0 + w * 0.47, y0 + h * 0.46
    s = w / 232.0
    d.polygon(PTS([(cx - 62 * s, cy + 2 * s), (cx - 20 * s, cy - 8 * s), (cx + 34 * s, cy - 9 * s),
                   (cx + 58 * s, cy - 3 * s), (cx + 62 * s, cy + 2 * s), (cx + 30 * s, cy + 7 * s),
                   (cx - 40 * s, cy + 7 * s)]), fill=(242, 244, 247))
    d.polygon(PTS([(cx - 58 * s, cy), (cx - 72 * s, cy - 14 * s), (cx - 62 * s, cy - 15 * s),
                   (cx - 44 * s, cy - 4 * s)]), fill=(230, 232, 236))
    flag(d, cx - 66 * s, cy - 21 * s, 13, "ghana")
    d.polygon(PTS([(cx - 6 * s, cy + 5 * s), (cx + 16 * s, cy + 16 * s), (cx + 24 * s, cy + 16 * s),
                   (cx + 8 * s, cy + 4 * s)]), fill=(200, 206, 214))
    for i in range(6):
        d.ellipse(BOX((cx + (-30 + i * 11) * s, cy - 4.5 * s, cx + (-26 + i * 11) * s, cy - 1 * s)), fill=(90, 130, 170))
    d.line([X(cx - 62 * s), X(cy + 12 * s), X(cx - 84 * s), X(cy + 20 * s)], fill=(120, 120, 126), width=max(1, X(1.2)))
    # price tag
    tx, ty = x0 + w * 0.78, y0 + h * 0.66
    d.polygon(PTS([(tx, ty), (tx + w * 0.19, ty), (tx + w * 0.22, ty + h * 0.13),
                   (tx + w * 0.19, ty + h * 0.26), (tx, ty + h * 0.26), (tx - w * 0.03, ty + h * 0.13)]), fill=(250, 214, 90))
    d.ellipse(BOX((tx + 3, ty + h * 0.1, tx + 7, ty + h * 0.16)), fill=(250, 250, 250))
    text(d, tx + w * 0.095, ty + h * 0.125, "$60M", F("sans_b", 12.5), (120, 70, 10), anchor="mm")


def paint_hunger(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(BOX(box), fill=(16, 12, 26))
    # cinema marquee with bulbs
    mx0, my0, mx1, my1 = x0 + w * 0.06, y0 + h * 0.1, x1 - w * 0.06, y0 + h * 0.52
    rrect(d, (mx0, my0, mx1, my1), 4, fill=(120, 26, 34))
    rrect(d, (mx0 + 4, my0 + 4, mx1 - 4, my1 - 4), 3, fill=(250, 240, 214))
    import math
    per = 2 * ((mx1 - mx0) + (my1 - my0))
    n = 26
    for i in range(n):
        t = per * i / n
        if t < (mx1 - mx0):
            px, py = mx0 + t, my0
        elif t < (mx1 - mx0) + (my1 - my0):
            px, py = mx1, my0 + (t - (mx1 - mx0))
        elif t < 2 * (mx1 - mx0) + (my1 - my0):
            px, py = mx1 - (t - (mx1 - mx0) - (my1 - my0)), my1
        else:
            px, py = mx0, my1 - (t - 2 * (mx1 - mx0) - (my1 - my0))
        col = (255, 196, 60) if i % 2 == 0 else (255, 226, 150)
        d.ellipse(BOX((px - 1.8, py - 1.8, px + 1.8, py + 1.8)), fill=col)
    text(d, x0 + w * 0.5, (my0 + my1) / 2, "THE PREQUEL", F("serif_b", 12.5), (120, 26, 34), anchor="mm")
    # split opinion: gold stars vs grey stars
    for i in range(3):
        star(d, x0 + w * (0.2 + 0.11 * i), y0 + h * 0.76, 7, GOLD_L, ratio=0.45)
    for i in range(3):
        star(d, x0 + w * (0.58 + 0.11 * i), y0 + h * 0.76, 7, (110, 110, 122), ratio=0.45)
    text(d, x0 + w * 0.36, y0 + h * 0.88, "LOVED IT", F("sans_b", 8), (240, 209, 110), anchor="ma")
    text(d, x0 + w * 0.68, y0 + h * 0.88, "HATED IT", F("sans_b", 8), (170, 170, 182), anchor="ma")


PAINTERS = {
    "shenzhen": paint_shenzhen,
    "alaska": paint_alaska,
    "nvidia": paint_nvidia,
    "cop31": paint_cop31,
    "waymo": paint_waymo,
    "myanmar": paint_myanmar,
    "hobart": paint_hobart,
    "aden": paint_aden,
    "ford": paint_ford,
    "earthshot": paint_earthshot,
    "ghana": paint_ghana,
    "hunger": paint_hunger,
}

# ------------------------------------------------------- the world map
# Coarse continent outlines in (lon, lat); equirectangular projection,
# honest proportions (lat window +82..-58 over the map's height).
NORTH_AMERICA = [(-165, 68), (-150, 70), (-135, 69), (-125, 71), (-110, 72),
                 (-95, 79), (-88, 74), (-82, 72), (-78, 69), (-70, 66), (-65, 62),
                 (-60, 58), (-55, 52), (-53, 49), (-58, 46), (-64, 44), (-68, 44),
                 (-71, 42), (-74, 39), (-76, 35), (-79, 32), (-80, 29), (-81, 25),
                 (-83, 22), (-87, 21), (-90, 20), (-94, 17), (-96, 15), (-97, 19),
                 (-100, 21), (-105, 22), (-109, 24), (-113, 28), (-117, 32),
                 (-121, 34), (-124, 40), (-124, 46), (-129, 52), (-136, 57),
                 (-148, 60), (-156, 58), (-162, 60), (-166, 64)]
GREENLAND = [(-46, 60), (-40, 62), (-32, 68), (-23, 70), (-19, 74), (-26, 79),
             (-44, 79), (-52, 76), (-54, 70), (-52, 63)]
SOUTH_AMERICA = [(-77, 7), (-72, 11), (-64, 10), (-56, 6), (-51, 4), (-50, 1),
                 (-44, -2), (-38, -5), (-35, -8), (-38, -12), (-40, -18),
                 (-41, -22), (-46, -25), (-50, -29), (-53, -33), (-57, 38 * -1),
                 (-60, -40), (-63, -43), (-65, -46), (-67, -50), (-69, -54),
                 (-71, -54), (-73, -48), (-74, -42), (-73, -35), (-71, -29),
                 (-70, -21), (-72, -16), (-76, -13), (-79, -8), (-81, -3),
                 (-80, 1), (-77, 4)]
AFRICA = [(-17, 15), (-15, 23), (-12, 28), (-9, 31), (-6, 34), (-2, 35),
          (4, 37), (10, 37), (12, 33), (19, 32), (27, 31), (32, 31), (34, 27),
          (37, 21), (39, 16), (42, 12), (47, 11), (51, 11), (48, 5), (43, 0),
          (40, -7), (40, -13), (38, -19), (36, -24), (34, -28), (30, -30),
          (25, -34), (20, -35), (18, -33), (16, -28), (14, -21), (13, -14),
          (12, -8), (13, -3), (9, 1), (8, 4), (2, 6), (-4, 5), (-9, 4),
          (-13, 7), (-16, 11)]
MADAGASCAR = [(44, -13), (48, -14), (50, -18), (48, -22), (45, -25), (44, -21), (43, -16)]
EUROPE = [(-9, 37), (-3, 36), (2, 37), (4, 39), (7, 43), (10, 44), (12, 42),
          (16, 40), (20, 40), (23, 36), (26, 38), (25, 41), (28, 41), (30, 46),
          (28, 48), (31, 50), (30, 52), (26, 54), (23, 55), (21, 57), (23, 59),
          (21, 61), (19, 63), (21, 65), (25, 66), (29, 69), (35, 68), (41, 67),
          (43, 64), (37, 62), (31, 60), (27, 59), (24, 58), (21, 56), (18, 55),
          (14, 54), (10, 53), (7, 51), (2, 51), (-1, 49), (-4, 48), (-2, 45),
          (-9, 43)]
UK = [(-5, 50), (-2, 52), (-1, 55), (-3, 57), (-5, 58), (-6, 56), (-5, 53), (-6, 51)]
ASIA = [(30, 46), (36, 42), (41, 40), (45, 38), (49, 38), (52, 42), (55, 46),
        (58, 50), (64, 54), (72, 56), (80, 58), (88, 61), (96, 64), (104, 66),
        (112, 70), (120, 72), (128, 71), (136, 71), (144, 71), (152, 70),
        (160, 69), (168, 67), (176, 65), (178, 64), (170, 62), (163, 60),
        (159, 55), (157, 51), (153, 47), (149, 44), (144, 42), (141, 40),
        (139, 37), (136, 35), (133, 34), (129, 33), (126, 34), (123, 37),
        (121, 39), (122, 41), (119, 41), (118, 38), (120, 34), (122, 30),
        (120, 26), (116, 23), (112, 22), (109, 19), (108, 14), (107, 9),
        (105, 4), (103, 1), (100, 4), (98, 8), (97, 13), (95, 16), (92, 16),
        (91, 21), (89, 22), (86, 20), (84, 18), (81, 15), (80, 13), (77, 8),
        (75, 11), (73, 16), (72, 20), (69, 22), (66, 25), (61, 25), (59, 22),
        (57, 25), (54, 25), (51, 27), (49, 30), (48, 29), (50, 27), (52, 25),
        (54, 24), (56, 26), (58, 24), (59, 22), (61, 25), (64, 25), (66, 25),
        (68, 24), (70, 23), (72, 21), (73, 17), (75, 12), (77, 8), (79, 10),
        (80, 13), (82, 16), (85, 19), (88, 22), (90, 22), (92, 18), (94, 17),
        (96, 15), (98, 10), (100, 6), (102, 2), (104, 3), (106, 8), (108, 12),
        (108, 16), (110, 20), (113, 22), (117, 24), (120, 27), (121, 30),
        (122, 33), (121, 36), (119, 38), (117, 40), (119, 41), (121, 40),
        (123, 38), (125, 35), (127, 34), (129, 33), (131, 34), (134, 35),
        (137, 37), (139, 39), (141, 41), (143, 42), (146, 43), (149, 45),
        (152, 48), (155, 50), (157, 53), (159, 56), (161, 59), (164, 61),
        (169, 63), (174, 65), (178, 65), (178, 67), (170, 68), (162, 69),
        (155, 69), (148, 71), (140, 72), (132, 71), (124, 71), (116, 71),
        (108, 69), (100, 66), (92, 63), (84, 60), (76, 57), (68, 55),
        (60, 52), (54, 47), (50, 42), (46, 39), (41, 40), (36, 42), (31, 45)]
SUMATRA = [(95, 5), (99, 2), (102, -1), (105, -4), (106, -6), (103, -4), (100, 0), (97, 3)]
BORNEO = [(109, 1), (112, 3), (116, 4), (119, 2), (118, -1), (115, -3), (111, -3), (109, -1)]
JAVA = [(106, -6), (110, -6), (114, -7), (114, -9), (108, -8), (106, -7)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9), (142, -7), (137, -5), (132, -3)]
AUSTRALIA = [(113, -22), (112, -27), (114, -32), (115, -35), (119, -34),
             (125, -33), (130, -32), (133, -32), (135, -35), (138, -36),
             (140, -38), (144, -38), (147, -38), (150, -36), (151, -33),
             (153, -29), (153, -25), (151, -20), (147, -18), (143, -14),
             (142, -11), (141, -15), (140, -18), (137, -16), (136, -12),
             (134, -11), (131, -12), (128, -13), (125, -15), (122, -17),
             (119, -20), (116, -21)]
NEW_ZEALAND = [(167, -45), (170, -43), (172, -41), (174, -39), (176, -37),
               (174, -37), (172, -40), (170, -43), (168, -46)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
         (141, 42), (143, 44), (144, 43), (142, 41), (140, 39), (139, 36),
         (136, 34), (133, 33), (131, 32)]

LANDMASSES = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, MADAGASCAR,
              EUROPE, UK, ASIA, SUMATRA, BORNEO, JAVA, NEW_GUINEA, AUSTRALIA,
              NEW_ZEALAND, JAPAN]

# (lon, lat, story number)
PINS = [(57, 28, "1"), (121, 14, "2"), (-122, 37, "8"), (114, 23, "6"),
        (-152, 64, "7"), (30, 37, "9"), (-99, 39, "10"), (96, 21, "11"),
        (147, -43, "12"), (44, 13, "13"), (-84, 43, "14"), (73, 19, "15"),
        (-1, 8, "16"), (-118, 34, "17"), (139, 36, "")]


def paint_map(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    rrect(d, box, 6, fill=TEAL_D)
    vgrad(d, box, TEAL, TEAL_D)
    # graticule
    for lon in range(-150, 181, 30):
        gx = x0 + (lon + 180) / 360.0 * w
        d.line([X(gx), X(y0 + 3), X(gx), X(y1 - 3)], fill=(28, 110, 126), width=max(1, X(0.7)))
    for lat in (60, 30, 0, -30):
        gy = y0 + (82 - lat) / 140.0 * h
        d.line([X(x0 + 3), X(gy), X(x1 - 3), X(gy)], fill=(28, 110, 126), width=max(1, X(0.7)))

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360.0 * w, y0 + (82 - lat) / 140.0 * h)

    for land in LANDMASSES:
        d.polygon(PTS([proj(a, b) for a, b in land]), fill=LAND, outline=LAND_D)
    for lon, lat, num in PINS:
        if not num:
            continue
        px, py = proj(lon, lat)
        d.ellipse(BOX((px - 6.5, py - 6.5, px + 6.5, py + 6.5)), fill=RED, outline=(255, 240, 220), width=max(1, X(1.2)))
        text(d, px, py - 0.5, num, F("sans_b", 8), (255, 255, 255), anchor="mm")


# ------------------------------------------------------------- layout
M = 40                     # page margin
CW = W - 2 * M             # content width = 944


def section_label(d, x, y, s, fill=GOLD):
    text(d, x, y, s, F("sans_b", 11), fill)


def build():
    img = Image.new("RGB", (X(W), X(H)), INK)
    d = ImageDraw.Draw(img)
    vgrad(d, (0, 0, W, H), (13, 26, 46), INK)

    # ---- masthead -------------------------------------------------
    text(d, W / 2, 10, "THE WORLD IN ONE DAY", F("serif_b", 43), GOLD_L, anchor="ma")
    d.rectangle(BOX((M, 62, W - M, 88)), fill=GOLD)
    text(d, W / 2, 75, "WEDNESDAY 18 NOVEMBER 2026", F("sans_b", 19), (24, 26, 20), anchor="mm")
    text(d, M + 10, 75, "43 STORIES", F("sans_b", 11.5), (24, 26, 20), anchor="lm")
    text(d, W - M - 10, 75, "13 ILLUSTRATED SCENES + WORLD MAP", F("sans_b", 11.5), (24, 26, 20), anchor="rm")

    # ---- hero: the lead -------------------------------------------
    rrect(d, (M, 94, W - M, 276), 8, fill=NAVY2)
    paint_hero(d, (M + 6, 100, W - M - 6, 200))
    text(d, M + 14, 206, LEAD["kicker"], F("sans_b", 12), GOLD_L)
    text(d, W - M - 14, 206, "1  \u00b7  " + LEAD["source"], F("sans_b", 11), (170, 190, 220), anchor="ra")
    text(d, M + 14, 222, LEAD["headline"], F("serif_b", 24), (255, 255, 255))
    deck = wrap(d, LEAD["deck"], F("sans", 13.5), CW - 28)
    for i, line in enumerate(deck[:2]):
        text(d, M + 14, 246 + i * 14.5, line, F("sans", 13.5), (214, 224, 238))

    # ---- map + top stories ----------------------------------------
    paint_map(d, (M, 282, M + 452, 468))
    text(d, M + 10, 448, "WHERE IT HAPPENED", F("sans_b", 10.5), (240, 225, 170))
    tx = M + 468
    text(d, tx, 284, "TOP STORIES", F("serif_b", 15.5), GOLD_L)
    d.line([X(tx), X(306), X(W - M), X(306)], fill=GOLD, width=max(1, X(1.2)))
    yy = 312
    for i, (head, deck, src) in enumerate(TOP):
        num = str(i + 2)
        d.ellipse(BOX((tx, yy + 1, tx + 15, yy + 16)), fill=RED)
        text(d, tx + 7.5, yy + 8.5, num, F("sans_b", 9.5), (255, 255, 255), anchor="mm")
        text(d, tx + 21, yy, head, F("sans_b", 14), (245, 247, 250))
        text(d, tx + 21, yy + 17.5, deck, F("sans", 11.5), (178, 192, 210))
        text(d, W - M, yy, src, F("sans_i", 10), (140, 156, 178), anchor="ra")
        yy += 39.5

    # ---- illustrated scene grid (stories 6-17) ---------------------
    col_w, row_h = 224, 88
    for idx, (key, tag, head, src) in enumerate(SCENES):
        cx = M + (idx % 4) * (col_w + 16)
        cy = 476 + (idx // 4) * row_h
        rrect(d, (cx, cy, cx + col_w, cy + row_h - 4), 5, fill=CREAM)
        PAINTERS[key](d, (cx + 3, cy + 3, cx + col_w - 3, cy + 55))
        d.rectangle(BOX((cx + 3, cy + 36, cx + 3 + 8 + tw(d, tag, F("sans_b", 8.5)) + 6, cy + 52)), fill=NAVY)
        text(d, cx + 10, cy + 44, tag, F("sans_b", 8.5), GOLD_L, anchor="lm")
        num = str(idx + 6)
        d.ellipse(BOX((cx + col_w - 21, cy + 5, cx + col_w - 5, cy + 21)), fill=RED, outline=(255, 240, 220), width=max(1, X(1)))
        text(d, cx + col_w - 13, cy + 13.5, num, F("sans_b", 9), (255, 255, 255), anchor="mm")
        lines = wrap(d, head, F("sans_b", 12.5), col_w - 14)
        for j, line in enumerate(lines[:2]):
            text(d, cx + 7, cy + 58 + j * 13, line, F("sans_b", 12.5), CHAR)

    # ---- briefs (stories 18-43) ------------------------------------
    by = 744
    text(d, M, by, "IN BRIEF - THE REST OF THE DAY", F("serif_b", 14.5), GOLD_L)
    text(d, W - M, by + 2, "STORIES 18-43  \u00b7  SIX REGIONS, EVERY BEAT", F("sans_b", 10.5), (150, 166, 188), anchor="ra")
    d.line([X(M), X(by + 20), X(W - M), X(by + 20)], fill=GOLD, width=max(1, X(1.2)))
    bf = F("sans", 10.5)
    wrapped = [(i, wrap(d, b, bf, 294)) for i, b in enumerate(BRIEFS)]
    hs = [len(ls) * 10.6 + 1.8 for _, ls in wrapped]
    pref = [0.0]
    for h in hs:
        pref.append(pref[-1] + h)
    best = None
    for a in range(1, len(hs) - 1):
        for bb in range(a + 1, len(hs)):
            m = max(pref[a], pref[bb] - pref[a], pref[-1] - pref[bb])
            if best is None or m < best[0]:
                best = (m, a, bb)
    _, sp1, sp2 = best
    cols = [wrapped[:sp1], wrapped[sp1:sp2], wrapped[sp2:]]
    for c, col in enumerate(cols):
        cx = M + c * 322
        yy = by + 24
        for i, lines in col:
            text(d, cx, yy, str(i + 18) + ".", F("sans_b", 10.5), GOLD_L)
            for j, line in enumerate(lines):
                text(d, cx + 22, yy + j * 10.6, line, bf, (206, 214, 226))
            yy += len(lines) * 10.6 + 1.8

    # ---- markets + sources -----------------------------------------
    d.rectangle(BOX((M, 972, W - M, 996)), fill=NAVY2)
    text(d, W / 2, 984, MARKETS, F("sans_b", 12.5), GOLD_L, anchor="mm")
    text(d, W / 2, 1002, SOURCES, F("sans", 10.5), (140, 156, 178), anchor="ma")
    text(d, W / 2, 1014, "Drawn by program in Python + Pillow \u00b7 every story first reported on the day named above",
         F("sans_i", 9.5), (110, 124, 146), anchor="ma")

    img = img.resize((W, H), Image.LANCZOS)
    return grain(img, alpha=1)


def main():
    if len(sys.argv) > 1:
        out = sys.argv[1]
    else:
        outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
        out = os.path.join(outdir, "entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    build().save(out, format="PNG", optimize=True, compress_level=9)


if __name__ == "__main__":
    main()
