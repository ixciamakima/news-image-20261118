"""The World in One Day -- An Illustrated Atlas.

news-image-20261118 v3: sums up Wednesday 18 November 2026 in one
1024x1024 image. 43 verified stories, 13 illustrated scenes + world map.

Drawn with Pillow only (stdlib + Pillow), no network, deterministic:
two runs produce byte-identical PNGs.

OUTPUT CONTRACT (v1, unchanged): write entry.png ONLY to
  argv[1] if given, else MAKEFUN_OUTPUT_DIR, else /output.
Never write anything to the repo directory or anywhere else.
The grader runs `python3 -P -s /bot/main.py` as nobody on a read-only
/bot with a writable /output, 60 s, 512 MB -- this program stays inside
those limits (local runtime ~10 s).
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
S = 2  # supersampling factor; draw at 2048, downscale to 1024

# ---------------------------------------------------------------- palette
NAVY = (10, 26, 51)        # plate
PANEL = (13, 34, 66)       # dark panel
PANEL2 = (17, 42, 78)      # lighter panel
GOLD = (233, 190, 74)      # masthead / accents
GOLD_D = (201, 158, 40)
CREAM = (244, 239, 228)    # scene card background
INK = (16, 28, 48)         # dark text on cream
WHITE = (245, 247, 250)
GREY = (159, 176, 195)     # secondary text on navy
GREY2 = (200, 210, 222)    # deck text
RED = (212, 61, 42)        # pins / chips
TEAL = (18, 86, 94)        # map sea
SAND = (216, 190, 133)     # map land
LINE = (38, 74, 116)       # hairlines on navy

# ---------------------------------------------------------------- fonts
FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/noto",
]


def load_font(names, size):
    """First existing font file wins; bitmap fallback only if none exist."""
    for name in names:
        for d in FONT_DIRS:
            path = os.path.join(d, name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size * S)
    return ImageFont.load_default()


def serif_b(size):
    return load_font(["DejaVuSerif-Bold.ttf", "DejaVuSans-Bold.ttf"], size)


def sans_b(size):
    return load_font(["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"], size)


def sans(size):
    return load_font(["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"], size)


# ---------------------------------------------------------------- helpers
def X(v):
    return int(round(v * S))


def rect(d, box, fill=None, outline=None, width=1):
    d.rectangle([X(box[0]), X(box[1]), X(box[2]), X(box[3])],
                fill=fill, outline=outline, width=max(1, int(width * S)))


def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle([X(box[0]), X(box[1]), X(box[2]), X(box[3])],
                        radius=int(rad * S), fill=fill, outline=outline,
                        width=max(1, int(width * S)))


def line(d, pts, fill, width=1):
    d.line([(X(x), X(y)) for x, y in pts], fill=fill,
           width=max(1, int(width * S)))


def circle(d, cx, cy, r, fill=None, outline=None, width=1):
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)],
              fill=fill, outline=outline, width=max(1, int(width * S)))


def text(d, xy, s, font, fill, anchor="la"):
    d.text((X(xy[0]), X(xy[1])), s, font=font, fill=fill, anchor=anchor)


def text_w(d, s, font):
    return d.textlength(s, font=font) / S


def wrap(d, s, font, max_w):
    """Greedy word wrap to a max width (final-space pixels)."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def vgrad(d, box, top, bottom):
    """Vertical gradient, drawn as horizontal bands."""
    x0, y0, x1, y1 = box
    steps = int((y1 - y0) * S)
    for i in range(steps):
        t = i / max(1, steps - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        y = y0 + i / S
        d.line([(X(x0), X(y)), (X(x1), X(y))], fill=col, width=S)


def dashed_bezier(d, p0, p1, p2, fill, width=1.5, dash=7, gap=6):
    """Dashed quadratic bezier, sampled in small segments."""
    n = 90
    prev = None
    on = True
    run = 0.0
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        if prev is not None:
            run += math.dist(prev, (x, y))
            if on:
                line(d, [prev, (x, y)], fill, width)
            if on and run >= dash:
                on, run = False, 0.0
            elif not on and run >= gap:
                on, run = True, 0.0
        prev = (x, y)


def starburst(d, cx, cy, r, core, rays):
    for k in range(12):
        a = k * math.pi / 6
        line(d, [(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))],
             rays, 1.5)
    circle(d, cx, cy, r * 0.55, fill=core)
    circle(d, cx, cy, r * 0.28, fill=(255, 244, 200))


def output_dir():
    """argv[1] wins, then MAKEFUN_OUTPUT_DIR, then /output."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"

# ---------------------------------------------------------------- data
# Every story below was first reported on Wednesday 18 November 2026
# (Reuters, BBC, AP, NPR, ESPNcricinfo, UN News, Just Security, Level
# Headlines, Morning Brief, The Weekly Anthropocene, Bangkok Post).

LEAD = {
    "n": 1,
    "kicker": "THE LEAD — THE GULF, BEFORE DAWN",
    "source": "Reuters / BBC / WSJ",
    "headline": "IRAN STRIKES KUWAIT & BAHRAIN",
    "deck": [
        "Tehran says it hit US drone and missile sites in Kuwait overnight after the US struck Qeshm Island;",
        "Kuwait repelled it; Bahrain intercepted drones for a third time in a week.",
    ],
}

TOP = [
    {"n": 2, "headline": "Trump hails 'very big' Philippines trade deal",
     "deck": "State lunch in Manila caps a day of Asia deal-making.",
     "source": "AP"},
    {"n": 3, "headline": "Anthropic files record $81.3bn IPO",
     "deck": "Valued near $1.4 trillion in the largest AI listing yet.",
     "source": "NPR / BBC"},
    {"n": 4, "headline": "US loses measles-elimination status",
     "deck": "A year of continuous spread ends a status held since 2000.",
     "source": "AP"},
    {"n": 5, "headline": "Kahana elected Knesset speaker",
     "deck": "Matan Kahana takes the chair as Eisenkot's Yashar party wins.",
     "source": "Just Security"},
]

# Scene cards: (number, region tag, headline, art kind, in-art label)
SCENES = [
    (6, "ASIA", "Xi & Putin meet in Shenzhen", "shenzhen", "SHENZHEN"),
    (7, "NORTH AMERICA", "Democrats take Senate, 56–44", "senate", "56–44"),
    (8, "TECH", "Nvidia beats forecasts, +5%", "nvidia", "+5%"),
    (9, "CLIMATE", "COP31 stocktake in Antalya", "cop31", "COP31"),
    (10, "TECH", "Waymo quits US freeways", "waymo", "WAYMO"),
    (11, "ASIA", "Myanmar genocide verdict looms", "scales", "THE HAGUE"),
    (12, "SPORT", "England win by 97 runs", "cricket", "ENG +97"),
    (13, "MIDDLE EAST", "Houthis retake Bab el-Mandeb", "strait", "ARABIA"),
    (14, "BUSINESS", "Ford ships first CATL-tech cells", "ford", "MICHIGAN PLANT"),
    (15, "CULTURE", "Earthshot carpet in Mumbai", "earthshot", "MUMBAI"),
    (16, "AFRICA", "Ghana's $60M jet sparks outrage", "jet", "$60M"),
    (17, "CULTURE", "New Hunger Games splits fans", "prequel", "THE PREQUEL"),
]

BRIEFS = [
    (18, "Mossad chief lobbied Washington for new joint strikes on Iran", "Reuters"),
    (19, "Bahrain's Bapco refinery back above 80% capacity after attacks", "Reuters"),
    (20, "Iraq PM orders crackdown on Kataib Hezbollah oil-smuggling ring", "Reuters"),
    (21, "Vance: US will not let Gulf become 'another forever war'", "Reuters"),
    (22, "Trump's Board of Peace: Israel and Hamas broke commitments", "Just Security"),
    (23, "Ethiopia and Eritrea mass forces along their shared border", "Reuters"),
    (24, "Myanmar's president orders ASEAN ties review over 'unfair treatment'", "AP"),
    (25, "US officer held in UK over Russia spying taken into US custody", "BBC"),
    (26, "Pakistani man jailed 27 years for Iran-backed plot to kill Trump", "BBC"),
    (27, "UK inflation hits 3.6% as fuel costs push energy bills up £443 a year", "BBC"),
    (28, "Burnham to set out EU options next month; Lammy urges rejoin pledge", "BBC"),
    (29, "Critical Java security flaw found by an AI startup", "BBC"),
    (30, "Gold falls over 2% to $3,770, its lowest since September 2025", "Morning Brief"),
    (31, "Brent crude near $92, down 23% from its October peak", "Reuters"),
    (32, "Indian bonds draw $1.1bn of foreign inflows in November", "Reuters"),
    (33, "China to invest $15bn in Turkish renewables, 7 GW solar & wind", "Weekly Anthropocene"),
    (34, "Norway to fund 12m tonnes of emissions cuts in Indonesia", "Weekly Anthropocene"),
    (35, "BYD unveils a 1 MW solar EV charger in Abu Dhabi", "Weekly Anthropocene"),
    (36, "Yangwang U9 Xtreme tops 500 km/h in record run", "Weekly Anthropocene"),
    (37, "Chahal becomes first Indian to 400 T20 wickets", "ESPNcricinfo"),
    (38, "Bihar stun Delhi, chasing 225 in the Syed Mushtaq Ali Trophy", "ESPNcricinfo"),
    (39, "Irish landfill eruption spews black substance into the air", "BBC"),
    (40, "Irishman charged with destroying US military aircraft with an axe", "BBC"),
    (41, "Rubio: US not 'under systemic attack' after sweeping tech outages", "Level Headlines"),
    (42, "Greenland chief Múlin faces House hearing after flight chaos", "Level Headlines"),
    (43, "Bezos 'heavily involved' as Pattinson is cast as the new 007", "BBC"),
]

MARKETS = [
    ("Gold $3,770", "-2.1%"),
    ("Brent $92", None),
    ("Nvidia +5% after hours", None),
    ("Rupee 93.44/$", None),
    ("India bonds +$1.1bn", None),
]

SOURCES = ("Sources: Reuters · BBC · AP · NPR · ESPNcricinfo · UN News · "
           "Just Security · Level Headlines · Morning Brief · "
           "The Weekly Anthropocene · Bangkok Post")
CREDIT = ("Drawn by program in Python + Pillow · every story first "
          "reported on the day named above")

# Map pins: (story number, lon, lat, dx, dy) -- dx/dy nudge the pin circle
# away from its true spot (leader line drawn) where stories cluster.
PINS = [
    (1, 48.0, 29.0, 0, 0), (2, 121.0, 14.6, 12, 10),
    (3, -122.4, 37.8, 0, 0), (4, -77.0, 38.9, 0, 0),
    (5, 35.2, 31.8, 0, 0), (6, 114.1, 22.5, 0, 0),
    (7, -150.0, 64.0, 0, 0), (8, -121.0, 37.4, 14, -12),
    (9, 30.7, 36.9, 16, -14), (10, -122.4, 37.8, 16, 12),
    (11, 96.0, 20.0, 0, 0), (12, 147.3, -42.9, 0, 0),
    (13, 43.5, 12.6, 0, 0), (14, -83.7, 42.3, -16, 10),
]

# Simplified continent outlines (lon, lat), equirectangular projection.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-115, 72), (-100, 73), (-90, 74),
     (-80, 73), (-70, 62), (-60, 55), (-55, 47), (-60, 44), (-68, 44),
     (-70, 41), (-74, 39), (-76, 35), (-80, 32), (-81, 26), (-84, 30),
     (-89, 29), (-93, 29), (-97, 26), (-97, 22), (-100, 20), (-105, 20),
     (-108, 23), (-110, 25), (-114, 29), (-118, 33), (-122, 37), (-124, 42),
     (-124, 48), (-130, 55), (-140, 60), (-150, 59), (-158, 58), (-165, 60),
     (-168, 66)],
    # Greenland
    [(-58, 64), (-50, 60), (-43, 60), (-40, 65), (-32, 68), (-25, 70),
     (-30, 74), (-40, 76), (-55, 76), (-60, 74), (-62, 70), (-58, 64)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-65, -50), (-62, -41), (-58, -35), (-52, -33), (-48, -28),
     (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-52, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
     (-77, 8), (-79, 9)],
    # Africa
    [(-17, 15), (-16, 21), (-15, 27), (-10, 31), (-6, 35), (0, 36),
     (10, 37), (11, 34), (19, 32), (25, 32), (30, 31), (32, 31),
     (34, 28), (37, 22), (39, 18), (43, 12), (48, 11), (51, 11),
     (51, 2), (46, -2), (41, -5), (40, -11), (36, -18), (33, -26),
     (28, -33), (20, -35), (18, -32), (16, -28), (14, -22), (12, -18),
     (13, -12), (9, -1), (9, 4), (4, 6), (-3, 5), (-8, 4), (-13, 8),
     (-17, 11), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 39), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
     (0, 50), (2, 51), (5, 53), (7, 54), (8, 57), (10, 58), (12, 56),
     (18, 56), (21, 55), (24, 58), (24, 60), (27, 61), (30, 62),
     (30, 66), (28, 70), (25, 71), (20, 70), (16, 69), (12, 66),
     (12, 62), (8, 61), (5, 59), (5, 58), (0, 54), (-3, 54), (-5, 50),
     (-5, 48), (-2, 47), (-2, 44), (-6, 43), (-9, 43), (-9, 39), (-10, 36)],
    # Asia
    [(28, 36), (30, 37), (34, 36), (36, 36), (36, 39), (38, 41),
     (41, 42), (43, 45), (46, 46), (49, 46), (51, 47), (54, 47),
     (57, 48), (60, 51), (62, 52), (65, 54), (68, 57), (70, 60),
     (68, 65), (70, 68), (72, 71), (75, 72), (80, 73), (85, 74),
     (90, 75), (95, 76), (100, 76), (105, 77), (110, 74), (115, 73),
     (120, 73), (125, 72), (130, 71), (135, 72), (140, 72), (145, 72),
     (150, 71), (155, 70), (160, 69), (165, 67), (170, 67), (175, 66),
     (178, 65), (173, 64), (170, 60), (162, 58), (158, 54), (156, 51),
     (152, 47), (148, 44), (142, 40), (141, 38), (140, 35), (137, 34),
     (134, 34), (131, 33), (129, 32), (127, 34), (127, 37), (126, 39),
     (124, 40), (122, 38), (121, 35), (120, 31), (119, 28), (118, 25),
     (115, 23), (112, 22), (109, 18), (108, 14), (106, 10), (104, 9),
     (102, 8), (100, 7), (99, 10), (98, 14), (97, 16), (94, 17),
     (92, 21), (91, 22), (89, 22), (88, 22), (86, 20), (84, 19),
     (82, 17), (80, 14), (80, 10), (77, 8), (76, 10), (75, 13),
     (73, 17), (72, 20), (70, 21), (68, 22), (66, 25), (63, 25),
     (61, 25), (59, 26), (57, 27), (56, 27), (54, 27), (52, 27),
     (50, 29), (49, 30), (48, 30), (47, 30), (44, 29), (43, 29),
     (41, 29), (39, 30), (38, 31), (36, 33), (35, 33), (33, 35),
     (31, 36), (28, 36)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (115, -35), (118, -35), (122, -34),
     (126, -32), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (144, -38), (147, -39), (150, -37), (153, -32), (153, -27), (152, -24),
     (150, -22), (148, -20), (146, -19), (143, -15), (142, -11), (141, -13),
     (138, -15), (136, -12), (135, -15), (132, -12), (130, -13), (128, -14),
     (125, -14), (122, -17), (120, -20), (117, -20), (114, -22), (113, -22)],
]

# ---------------------------------------------------------------- hero
def paint_hero(d, box):
    """Night scene over the Strait of Hormuz: sky, missile arcs, sea."""
    x0, y0, x1, y1 = box
    horizon = y0 + (y1 - y0) * 0.62
    sea_top = horizon
    # sky gradient
    vgrad(d, (x0, y0, x1, horizon), (9, 28, 62), (26, 60, 100))
    # stars (deterministic)
    rnd = random.Random(20261118)
    for _ in range(90):
        sx = x0 + rnd.random() * (x1 - x0)
        sy = y0 + rnd.random() * (horizon - y0 - 8)
        r = 0.6 + rnd.random() * 1.1
        a = 140 + int(rnd.random() * 115)
        circle(d, sx, sy, r, fill=(255, 255, 255))
    # moon + glow
    mx, my = x1 - 90, y0 + 26
    circle(d, mx, my, 22, fill=(240, 225, 190))
    circle(d, mx, my, 13, fill=(250, 244, 220))
    circle(d, mx - 4, my - 3, 3, fill=(225, 210, 175))
    # missile arcs (dashed) + bursts
    dashed_bezier(d, (x0 + 90, horizon - 6), (x0 + 330, y0 + 6),
                  (x0 + 640, horizon - 22), (255, 176, 66), 2)
    dashed_bezier(d, (x1 - 130, horizon - 8), (x1 - 360, y0 + 14),
                  (x0 + 380, horizon - 18), (235, 90, 70), 2)
    starburst(d, x0 + 640, horizon - 22, 11, (255, 150, 40), (255, 200, 90))
    starburst(d, x0 + 380, horizon - 18, 8, (255, 170, 60), (255, 210, 110))
    # drone silhouette
    dx, dy = x0 + 520, y0 + 16
    d.ellipse([X(dx - 14), X(dy - 3), X(dx + 14), X(dy + 3)], fill=(8, 14, 28))
    line(d, [(dx - 22, dy - 6), (dx + 22, dy - 6)], (8, 14, 28), 2)
    circle(d, dx, dy - 5, 2, fill=(255, 80, 60))
    # coast skylines (left and right) with lit windows
    for base_x, wdt in ((x0 + 10, 300), (x1 - 320, 300)):
        bx = base_x
        while bx < base_x + wdt:
            bw = 14 + rnd.random() * 26
            bh = 8 + rnd.random() * 20
            rect(d, (bx, horizon - bh, bx + bw, horizon), fill=(6, 12, 24))
            for _ in range(int(bw * bh / 90)):
                wx = bx + 3 + rnd.random() * (bw - 6)
                wy = horizon - bh + 3 + rnd.random() * (bh - 6)
                circle(d, wx, wy, 0.8, fill=(255, 205, 90))
            bx += bw + 3
    # sea gradient + wave lines
    vgrad(d, (x0, sea_top, x1, y1), (16, 62, 98), (8, 38, 66))
    for k in range(6):
        wy = sea_top + 8 + k * 7
        pts = []
        for xx in range(int(x0), int(x1) + 1, 24):
            pts.append((xx, wy + 1.6 * math.sin(xx / 55.0 + k)))
        line(d, pts, (90, 150, 195), 1)
    # two ships with tiny flags
    for sx, flag in ((x0 + 300, (200, 60, 50)), (x0 + 700, (240, 240, 240))):
        sy = sea_top + 26
        d.polygon([(X(sx - 22), X(sy)), (X(sx + 22), X(sy)),
                   (X(sx + 16), X(sy + 8)), (X(sx - 16), X(sy + 8))],
                  fill=(10, 20, 36))
        line(d, [(sx, sy - 14), (sx, sy)], (10, 20, 36), 2)
        d.polygon([(X(sx), X(sy - 14)), (X(sx + 9), X(sy - 11)),
                   (X(sx), X(sy - 8))], fill=flag)

# ---------------------------------------------------------------- map + top stories
def paint_map(d, box):
    """World map, equirectangular, with 14 numbered pins."""
    x0, y0, x1, y1 = box
    rect(d, box, fill=TEAL)
    # faint graticule
    for gx in range(int(x0) + 24, int(x1), 24):
        line(d, [(gx, y0), (gx, y1)], (28, 105, 112), 0.5)
    for gy in range(int(y0) + 22, int(y1), 22):
        line(d, [(x0, gy), (x1, gy)], (28, 105, 112), 0.5)
    lon0, lon1 = -180.0, 180.0
    lat0, lat1 = 78.0, -58.0

    def proj(lon, lat):
        px = x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0)
        py = y0 + (lat0 - lat) / (lat0 - lat1) * (y1 - y0)
        return (px, py)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon([(X(px), X(py)) for px, py in pts], fill=SAND,
                  outline=(190, 165, 105))
    # small islands the polygons skip: Japan, UK, Indonesia, NZ
    for lon, lat, r in ((139, 37, 4), (140, 39, 3), (-2, 54, 3),
                        (103, 1, 3), (107, -3, 3), (114, -3, 3),
                        (120, -2, 3), (172, -41, 3)):
        px, py = proj(lon, lat)
        circle(d, px, py, r, fill=SAND)
    # pins (nudged ones get a leader line from their true spot)
    f_pin = sans_b(9)
    for n, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        if dx or dy:
            line(d, [(px, py), (cx, cy)], WHITE, 1)
            circle(d, px, py, 2, fill=WHITE)
        circle(d, cx, cy, 7.5, fill=RED, outline=WHITE, width=1.5)
        text(d, (cx, cy), str(n), f_pin, WHITE, anchor="mm")
    text(d, (x0 + 8, y1 - 18), "WHERE IT HAPPENED", sans_b(11), WHITE)


def paint_top(d, box):
    """Top Stories column (stories 2-5) beside the map."""
    x0, y0, x1, y1 = box
    text(d, (x0, y0), "TOP STORIES", sans_b(18), GOLD)
    line(d, [(x0, y0 + 24), (x1, y0 + 24)], GOLD_D, 1.5)
    y = y0 + 32
    for item in TOP:
        n = item["n"]
        circle(d, x0 + 11, y + 10, 10.5, fill=RED)
        text(d, (x0 + 11, y + 10), str(n), sans_b(12), WHITE, anchor="mm")
        hx = x0 + 28
        f_h = sans_b(16)
        f_d = sans(12)
        reserve = text_w(d, item["source"], sans(11)) + 8
        hl = wrap(d, item["headline"], f_h, (x1 - hx) - reserve)
        for k, ln in enumerate(hl):
            text(d, (hx, y + k * 18), ln, f_h, WHITE)
        sw = text_w(d, item["source"], sans(11))
        text(d, (x1 - sw, y + 2), item["source"], sans(11), GREY, anchor="la")
        dy = y + len(hl) * 18
        for k, ln in enumerate(wrap(d, item["deck"], f_d, x1 - hx)):
            text(d, (hx, dy + k * 13), ln, f_d, GREY)
        y = dy + 13 + 7

# ---------------------------------------------------------------- scene art
def art_shenzhen(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (245, 190, 90), (220, 120, 60))
    rnd = random.Random(6)
    bx = x0 + 6
    while bx < x1 - 8:
        bw = 12 + rnd.random() * 18
        bh = 14 + rnd.random() * 20
        rect(d, (bx, y1 - bh, bx + bw, y1), fill=(30, 42, 68))
        for _ in range(int(bw * bh / 120)):
            wx = bx + 2 + rnd.random() * (bw - 4)
            wy = y1 - bh + 2 + rnd.random() * (bh - 4)
            circle(d, wx, wy, 0.8, fill=(255, 210, 110))
        bx += bw + 2
    for fx, col in ((x0 + 26, (200, 40, 40)), (x0 + 44, (240, 200, 60)),
                    (x0 + 62, (40, 90, 160))):
        d.polygon([(X(fx), X(y0 + 6)), (X(fx + 12), X(y0 + 9)),
                   (X(fx), X(y0 + 12))], fill=col)
        line(d, [(fx, y0 + 6), (fx, y0 + 20)], (40, 40, 40), 1)


def art_senate(d, box):
    x0, y0, x1, y1 = box
    rect(d, box, fill=(232, 228, 218))
    cx = (x0 + x1) / 2
    rect(d, (cx - 26, y0 + 12, cx + 26, y1 - 6), fill=(250, 248, 242),
         outline=(120, 110, 95), width=1)
    rect(d, (cx - 12, y0 + 16, cx + 12, y0 + 20), fill=(40, 60, 110))
    # folded ballot slip with a check mark
    line(d, [(cx - 8, y0 + 28), (cx - 1, y0 + 35)], (30, 90, 50), 2)
    line(d, [(cx - 1, y0 + 35), (cx + 10, y0 + 23)], (30, 90, 50), 2)
    rect(d, (x0 + 8, y1 - 12, x0 + 60, y1 - 6), fill=(40, 80, 170))
    rect(d, (x0 + 64, y1 - 12, x0 + 100, y1 - 6), fill=(190, 50, 40))


def art_nvidia(d, box):
    x0, y0, x1, y1 = box
    rect(d, box, fill=(12, 24, 16))
    cx, cy = (x0 + x1) / 2 - 14, (y0 + y1) / 2
    rrect(d, (cx - 20, cy - 13, cx + 20, cy + 13), 4, fill=(118, 185, 0))
    text(d, (cx, cy), "AI", sans_b(15), WHITE, anchor="mm")
    pts = [(x1 - 62, y1 - 8), (x1 - 46, y1 - 20), (x1 - 32, y1 - 14),
           (x1 - 18, y1 - 28), (x1 - 6, y1 - 34)]
    line(d, pts, (118, 185, 0), 2)
    for px, py in pts:
        circle(d, px, py, 2, fill=(200, 240, 120))


def art_cop31(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (150, 205, 235), (225, 240, 245))
    circle(d, x1 - 18, y0 + 10, 7, fill=(255, 205, 80))
    bx0, bx1 = x0 + 30, x1 - 30
    rect(d, (bx0, y0 + 20, bx1, y1 - 4), fill=(250, 250, 248),
         outline=(150, 160, 170), width=1)
    rect(d, (bx0 - 6, y0 + 16, bx1 + 6, y0 + 20), fill=(40, 90, 130))
    for cx in range(int(bx0) + 10, int(bx1) - 6, 12):
        rect(d, (cx, y0 + 26, cx + 5, y1 - 8), fill=(170, 190, 205))
    text(d, ((x0 + x1) / 2, y0 + 4), "COP31", sans_b(9), (30, 70, 110),
         anchor="ma")


def art_waymo(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (120, 150, 190), (200, 215, 230))
    rect(d, (x0, y1 - 12, x1, y1), fill=(70, 78, 88))
    for wx in range(int(x0) + 8, int(x1) - 8, 26):
        line(d, [(wx, y1 - 6), (wx + 12, y1 - 6)], (240, 230, 120), 1.5)
    cx = (x0 + x1) / 2
    rrect(d, (cx - 34, y0 + 12, cx + 34, y0 + 30), 6, fill=(245, 245, 245),
          outline=(60, 70, 85), width=1)
    rect(d, (cx - 24, y0 + 16, cx - 2, y0 + 24), fill=(140, 190, 220))
    rect(d, (cx + 2, y0 + 16, cx + 24, y0 + 24), fill=(140, 190, 220))
    circle(d, cx - 18, y0 + 32, 5, fill=(30, 30, 35))
    circle(d, cx + 18, y0 + 32, 5, fill=(30, 30, 35))
    text(d, (cx, y0 + 2), "WAYMO", sans_b(8), (30, 60, 110), anchor="ma")


def art_scales(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (200, 205, 210), (235, 235, 232))
    cx = (x0 + x1) / 2
    rect(d, (x0 + 16, y0 + 8, x1 - 16, y0 + 14), fill=(120, 125, 130))
    for px in range(int(x0) + 22, int(x1) - 18, 12):
        rect(d, (px, y0 + 14, px + 5, y1 - 6), fill=(150, 155, 160))
    line(d, [(cx, y0 + 14), (cx, y0 + 30)], (60, 60, 65), 2)
    line(d, [(cx - 20, y0 + 18), (cx + 20, y0 + 18)], (60, 60, 65), 2)
    for ex in (cx - 20, cx + 20):
        line(d, [(ex, y0 + 18), (ex, y0 + 28)], (60, 60, 65), 1.5)
        d.pieslice([X(ex - 8), X(y0 + 26), X(ex + 8), X(y0 + 36)],
                   0, 180, fill=(190, 160, 60))


def art_cricket(d, box):
    x0, y0, x1, y1 = box
    rect(d, box, fill=(90, 160, 90))
    rect(d, (x0 + 60, y0 + 6, x0 + 120, y1 - 4), fill=(215, 190, 140))
    line(d, [(x0 + 66, y0 + 12), (x0 + 114, y0 + 12)], WHITE, 1.5)
    line(d, [(x0 + 66, y1 - 10), (x0 + 114, y1 - 10)], WHITE, 1.5)
    for sx in (x0 + 74, x0 + 106):
        line(d, [(sx, y0 + 6), (sx, y0 + 12)], (230, 200, 80), 2)
    dashed_bezier(d, (x0 + 150, y0 + 8), (x0 + 185, y0 + 22),
                  (x1 - 12, y1 - 10), (255, 240, 200), 1.5)
    circle(d, x1 - 10, y1 - 10, 3, fill=(200, 40, 40))


def art_strait(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (250, 200, 110), (235, 160, 70))
    d.polygon([(X(x0), X(y1)), (X(x0 + 46), X(y0 + 10)),
               (X(x0 + 70), X(y1))], fill=(120, 90, 60))
    d.polygon([(X(x1), X(y1)), (X(x1 - 46), X(y0 + 14)),
               (X(x1 - 70), X(y1))], fill=(120, 90, 60))
    rect(d, (x0, y1 - 12, x1, y1), fill=(20, 70, 110))
    cx = (x0 + x1) / 2
    d.polygon([(X(cx - 16), X(y1 - 12)), (X(cx + 16), X(y1 - 12)),
               (X(cx + 11), X(y1 - 5)), (X(cx - 11), X(y1 - 5))],
              fill=(25, 35, 50))
    line(d, [(cx, y1 - 22), (cx, y1 - 12)], (25, 35, 50), 2)
    starburst(d, cx + 30, y0 + 12, 6, (255, 150, 40), (255, 210, 110))


def art_ford(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (200, 210, 220), (235, 238, 240))
    rect(d, (x0 + 10, y0 + 16, x1 - 40, y1 - 4), fill=(150, 158, 168))
    for kx in range(int(x0) + 12, int(x1) - 44, 14):
        d.polygon([(X(kx), X(y0 + 16)), (X(kx + 7), X(y0 + 8)),
                   (X(kx + 14), X(y0 + 16))], fill=(120, 128, 138))
    rect(d, (x1 - 36, y0 + 4, x1 - 28, y1 - 4), fill=(110, 115, 120))
    for i, bx in enumerate((x0 + 90, x0 + 118, x0 + 146)):
        rrect(d, (bx, y0 + 22, bx + 22, y0 + 38), 3, fill=(60, 160, 70))
        bx2, by2 = bx + 11, y0 + 30
        d.polygon([(X(bx2 + 2), X(by2 - 6)), (X(bx2 - 3), X(by2 + 1)),
                   (X(bx2), X(by2 + 1)), (X(bx2 - 2), X(by2 + 6)),
                   (X(bx2 + 3), X(by2 - 1)), (X(bx2), X(by2 - 1))],
                  fill=WHITE)


def art_earthshot(d, box):
    x0, y0, x1, y1 = box
    rect(d, box, fill=(14, 20, 34))
    text(d, ((x0 + x1) / 2, y0 + 4), "EARTHSHOT", sans_b(12),
         (200, 170, 70), anchor="ma")
    d.polygon([(X(x0 + 30), X(y1)), (X(x0 + 90), X(y0 + 18)),
               (X(x0 + 150), X(y0 + 18)), (X(x0 + 90), X(y1))],
              fill=(30, 140, 70))
    for fx, fy in ((x0 + 30, y0 + 10), (x1 - 30, y0 + 8), (x0 + 60, y0 + 6)):
        starburst(d, fx, fy, 4, (255, 240, 180), (255, 220, 120))


def art_jet(d, box):
    x0, y0, x1, y1 = box
    vgrad(d, box, (130, 180, 225), (215, 232, 245))
    circle(d, x1 - 24, y0 + 10, 8, fill=(255, 210, 90))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 2
    d.polygon([(X(cx - 42), X(cy)), (X(cx + 42), X(cy - 2)),
               (X(cx + 48), X(cy + 2)), (X(cx - 30), X(cy + 6))],
              fill=(245, 245, 245), outline=(90, 100, 115))
    d.polygon([(X(cx - 6), X(cy - 2)), (X(cx + 6), X(cy - 16)),
               (X(cx + 12), X(cy - 2))], fill=(220, 225, 230))
    d.polygon([(X(cx - 10), X(cy + 4)), (X(cx - 2), X(cy + 16)),
               (X(cx + 4), X(cy + 4))], fill=(220, 225, 230))


def art_prequel(d, box):
    x0, y0, x1, y1 = box
    rect(d, box, fill=(24, 16, 20))
    d.polygon([(X(x0), X(y0)), (X(x0 + 26), X(y0)),
               (X(x0 + 18), X(y1)), (X(x0), X(y1))], fill=(140, 30, 35))
    d.polygon([(X(x1), X(y0)), (X(x1 - 26), X(y0)),
               (X(x1 - 18), X(y1)), (X(x1), X(y1))], fill=(140, 30, 35))
    rrect(d, (x0 + 34, y0 + 8, x1 - 34, y0 + 26), 3, fill=(250, 220, 130))
    text(d, ((x0 + x1) / 2, y0 + 17), "THE PREQUEL", sans_b(10),
         (90, 20, 25), anchor="mm")
    rnd = random.Random(17)
    for _ in range(8):
        sx = x0 + 30 + rnd.random() * (x1 - x0 - 60)
        sy = y0 + 30 + rnd.random() * (y1 - y0 - 34)
        circle(d, sx, sy, 1, fill=(255, 240, 180))


ART = {
    "shenzhen": art_shenzhen, "senate": art_senate, "nvidia": art_nvidia,
    "cop31": art_cop31, "waymo": art_waymo, "scales": art_scales,
    "cricket": art_cricket, "strait": art_strait, "ford": art_ford,
    "earthshot": art_earthshot, "jet": art_jet, "prequel": art_prequel,
}

# ---------------------------------------------------------------- sections
def paint_cards(d, y0, card_h):
    """4x3 grid of illustrated scene cards."""
    gap_x, gap_y = 8, 4
    cw = (976 - 3 * gap_x) / 4.0
    for i, (n, tag, headline, kind, label) in enumerate(SCENES):
        row, col = divmod(i, 4)
        x0 = 24 + col * (cw + gap_x)
        y = y0 + row * (card_h + gap_y)
        x1, y1 = x0 + cw, y + card_h
        art_h = card_h - 26
        rect(d, (x0, y, x1, y1), fill=CREAM)
        ART[kind](d, (x0, y, x1, y + art_h))
        # region tag, top-left of the art
        f_tag = sans_b(9)
        tw = text_w(d, tag, f_tag) + 8
        rect(d, (x0 + 3, y + 3, x0 + 3 + tw, y + 15), fill=(16, 28, 48))
        text(d, (x0 + 7, y + 9), tag, f_tag, WHITE)
        # number chip, top-right of the art
        circle(d, x1 - 11, y + 11, 9.5, fill=RED, outline=WHITE, width=1.5)
        text(d, (x1 - 11, y + 11), str(n), sans_b(10), WHITE, anchor="mm")
        # in-art label, bottom-right of the art
        f_lab = sans_b(9)
        lw = text_w(d, label, f_lab) + 8
        rect(d, (x1 - 4 - lw, y + art_h - 14, x1 - 4, y + art_h - 2),
             fill=(16, 28, 48))
        text(d, (x1 - 8, y + art_h - 8), label, f_lab, WHITE, anchor="ra")
        # headline below the art (one 12px line by design)
        f_h = sans_b(12)
        hl = wrap(d, headline, f_h, cw - 10)
        for k, ln in enumerate(hl[:2]):
            text(d, (x0 + 5, y + art_h + 4 + k * 13), ln, f_h, INK)


def paint_briefs(d, y0, y1):
    """26 numbered briefs in three columns (8/9/9)."""
    text(d, (24, y0), "IN BRIEF — THE REST OF THE DAY", sans_b(15), GOLD)
    rt = "STORIES 18–43 · SIX REGIONS, EVERY BEAT"
    text(d, (1000 - text_w(d, rt, sans_b(11)), y0 + 2), rt, sans_b(11), GREY)
    line(d, [(24, y0 + 20), (1000, y0 + 20)], LINE, 1)
    cols = [BRIEFS[0:8], BRIEFS[8:17], BRIEFS[17:26]]
    col_x = [24, 354, 684]
    col_w = 310
    f_n = sans_b(12)
    f_b = sans(12)
    y = y0 + 26
    for ci, items in enumerate(cols):
        cy = y
        for n, txt, src in items:
            full = txt + " (" + src + ")"
            lines = wrap(d, full, f_b, col_w - 26)
            text(d, (col_x[ci], cy), str(n) + ".", f_n, GOLD)
            for k, ln in enumerate(lines):
                text(d, (col_x[ci] + 26, cy + k * 13), ln, f_b, WHITE)
            cy += len(lines) * 13 + 2
        # column bottom is whatever the tallest column reaches; keep going


def paint_markets(d, y0, y1):
    rect(d, (24, y0, 1000, y1), fill=PANEL2)
    x = 40
    text(d, (x, (y0 + y1) / 2), "MARKETS", sans_b(13), GOLD, anchor="lm")
    x += text_w(d, "MARKETS", sans_b(13)) + 18
    f_m = sans_b(13)
    for i, (label, change) in enumerate(MARKETS):
        text(d, (x, (y0 + y1) / 2), label, f_m, WHITE, anchor="lm")
        x += text_w(d, label, f_m) + 4
        if change:
            text(d, (x, (y0 + y1) / 2), change, f_m, (255, 110, 90),
                 anchor="lm")
            x += text_w(d, change, f_m) + 6
        if i < len(MARKETS) - 1:
            text(d, (x, (y0 + y1) / 2), "·", f_m, GOLD, anchor="lm")
            x += 14


def paint_footer(d, y0):
    text(d, (512, y0), SOURCES, sans(11), GREY, anchor="ma")
    text(d, (512, y0 + 13), CREDIT, sans(10), (120, 135, 155), anchor="ma")


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W * S, H * S), NAVY)
    d = ImageDraw.Draw(img)
    # masthead
    text(d, (512, 8), "THE WORLD IN ONE DAY", serif_b(50), GOLD, anchor="ma")
    # date ribbon
    rect(d, (24, 60, 1000, 86), fill=GOLD)
    text(d, (36, 73), "43 STORIES", sans_b(13), INK, anchor="lm")
    text(d, (512, 73), "WEDNESDAY 18 NOVEMBER 2026", sans_b(16), INK,
         anchor="mm")
    rt = "13 ILLUSTRATED SCENES + WORLD MAP"
    text(d, (988, 73), rt, sans_b(13), INK, anchor="rm")
    # hero painting
    paint_hero(d, (24, 90, 1000, 204))
    # lead
    text(d, (24, 210), LEAD["kicker"], sans_b(13), GOLD)
    sw = text_w(d, str(LEAD["n"]) + " · " + LEAD["source"], sans(12))
    text(d, (1000 - sw, 211), str(LEAD["n"]) + " · " + LEAD["source"],
         sans(12), GREY)
    text(d, (24, 224), LEAD["headline"], sans_b(30), WHITE)
    for k, ln in enumerate(LEAD["deck"]):
        text(d, (24, 250 + k * 13), ln, sans(13), GREY2)
    # map + top stories
    paint_map(d, (24, 280, 512, 466))
    paint_top(d, (524, 280, 1000, 466))
    # scene cards
    paint_cards(d, 474, 64)
    # briefs
    paint_briefs(d, 680, 955)
    # markets + footer
    paint_markets(d, 962, 986)
    paint_footer(d, 991)
    return img.resize((W, H), Image.LANCZOS)


def main():
    img = build()
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    img.save(path, format="PNG", optimize=True, compress_level=9)
    print("wrote " + path)


if __name__ == "__main__":
    main()
