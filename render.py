#!/usr/bin/env python3
"""Render the front page for news-image-20261118.

Draws 'The World in One Day' — Wednesday 18 November 2026 — as a
1024x1024 broadsheet front page with Pillow. Pure stdlib + Pillow at
build time; the entry itself is the PNG this script writes. Deterministic:
no randomness, no timestamps, no network.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 16

PAPER = (247, 243, 232)
INK = (17, 17, 17)
BLACK = (10, 10, 10)
GOLD = (242, 194, 0)
GOLD_D = (201, 158, 0)
RED = (185, 28, 28)
NAVY = (10, 22, 38)
NAVY_L = (24, 48, 80)
TEAL = (13, 92, 99)
GREEN = (46, 125, 50)
GRAY = (96, 92, 82)
LIGHT = (233, 228, 216)
WHITE = (255, 255, 255)
SKY = (18, 38, 74)
SKY2 = (44, 84, 138)

FD = "/usr/share/fonts/truetype/dejavu"


def f_bold(n):
    return ImageFont.truetype(f"{FD}/DejaVuSans-Bold.ttf", n)


def f_reg(n):
    return ImageFont.truetype(f"{FD}/DejaVuSans.ttf", n)


def f_serif(n):
    return ImageFont.truetype(f"{FD}/DejaVuSerif-Bold.ttf", n)


def tw(d, s, font):
    """Text width in pixels."""
    b = d.textbbox((0, 0), s, font=font)
    return b[2] - b[0]


def wrap(d, text, font, width):
    """Greedy wrap to lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if tw(d, trial, font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, width, fill=INK, leading=None, spacing=0):
    """Draw wrapped paragraph; return y after last line."""
    lh = leading or int(font.size * 1.28)
    for line in wrap(d, text, font, width):
        d.text((x, y), line, font=font, fill=fill)
        y += lh + spacing
    return y


def rule(d, x, y, w, fill=INK, weight=2):
    d.rectangle([x, y, x + w, y + weight - 1], fill=fill)


# ---------------------------------------------------------------- continents
# Simplified lon/lat outlines, equirectangular, lat -58..84.
NA = [(-168, 65), (-155, 58), (-145, 60), (-135, 58), (-128, 50),
      (-124, 40), (-117, 32), (-108, 25), (-100, 22), (-94, 18),
      (-88, 15), (-83, 9), (-79, 9), (-82, 13), (-87, 13), (-90, 14),
      (-94, 17), (-97, 24), (-93, 29), (-88, 29), (-83, 27),
      (-80, 26), (-79, 32), (-75, 36), (-72, 41), (-68, 44),
      (-64, 44), (-59, 47), (-55, 52), (-58, 56), (-64, 60),
      (-70, 62), (-78, 62), (-86, 66), (-94, 68), (-108, 68),
      (-125, 70), (-140, 70), (-155, 70), (-165, 68)]
SA = [(-79, 9), (-76, 7), (-72, 12), (-68, 11), (-62, 9), (-58, 6),
      (-52, 5), (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-38, -15),
      (-40, -22), (-46, -26), (-52, -32), (-58, -38), (-62, -41),
      (-66, -40), (-70, -37), (-73, -30), (-72, -20), (-70, -18),
      (-77, -12), (-80, -6), (-81, 0), (-80, 6)]
AF = [(-17, 15), (-16, 21), (-12, 27), (-9, 32), (-5, 35), (0, 36),
      (10, 37), (11, 34), (19, 32), (25, 32), (30, 31), (33, 28),
      (35, 28), (38, 22), (40, 18), (43, 12), (46, 11), (51, 12),
      (48, 7), (44, 2), (41, -2), (40, -6), (39, -12), (36, -18),
      (33, -26), (28, -33), (20, -35), (17, -29), (14, -22),
      (12, -18), (13, -12), (12, -6), (9, 4), (4, 6), (-4, 5),
      (-8, 5), (-13, 8), (-17, 12)]
EU = [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50),
      (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62),
      (10, 64), (13, 66), (18, 69), (25, 71), (30, 70), (32, 68),
      (28, 66), (24, 64), (22, 60), (18, 56), (21, 55), (24, 58),
      (28, 59), (24, 54), (28, 54), (30, 50), (28, 46), (23, 40),
      (19, 42), (15, 44), (12, 44), (8, 44), (3, 42), (0, 39),
      (-2, 37), (-6, 36)]
AS = [(30, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73),
      (90, 75), (100, 77), (110, 76), (120, 73), (130, 72), (140, 72),
      (150, 70), (158, 66), (162, 60), (158, 55), (150, 59), (142, 54),
      (140, 46), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
      (122, 28), (118, 25), (112, 22), (108, 18), (105, 10), (103, 8),
      (100, 7), (98, 10), (95, 15), (92, 21), (88, 22), (85, 20),
      (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (62, 25),
      (58, 26), (54, 26), (50, 29), (48, 30), (44, 29), (40, 30),
      (36, 36), (32, 36), (30, 40), (28, 45), (30, 50), (32, 55),
      (35, 60), (38, 65)]
AU = [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33),
      (129, -32), (132, -32), (136, -35), (140, -38), (145, -38),
      (150, -37), (153, -32), (153, -27), (150, -23), (146, -19),
      (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
      (130, -13), (126, -14), (122, -17), (118, -20)]
CONTINENTS = [NA, SA, AF, EU, AS, AU]


def project(lon, lat, x0, y0, w, h):
    """Equirectangular, lon -180..180, lat -58..84, honest aspect."""
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (84.0 - lat) / 142.0 * h
    return (x, y)


# ------------------------------------------------------------------- scenes
def paint_gulf(d, x, y, w, h):
    """Night over the Strait of Hormuz: sky, sea, Qeshm Island, missile
    trails, searchlights. Flat vector, drawn with primitives only."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for i in range(h):
        c = int(SKY[0] + (SKY2[0] - SKY[0]) * i / h)
        g = int(SKY[1] + (SKY2[1] - SKY[1]) * i / h)
        b = int(SKY[2] + (SKY2[2] - SKY[2]) * i / h)
        d.line([(x, y + i), (x + w, y + i)], fill=(c, g, b))
    stars = [(22, 14), (70, 26), (130, 10), (190, 30), (250, 12),
             (310, 24), (360, 10), (410, 28), (46, 44), (160, 48),
             (280, 44), (390, 48)]
    for sx, sy in stars:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(235, 235, 220))
    d.ellipse([x + w - 78, y + 12, x + w - 40, y + 50], fill=(240, 232, 200))
    d.ellipse([x + w - 70, y + 20, x + w - 48, y + 42], fill=(214, 196, 150))
    sea_y = y + int(h * 0.62)
    d.rectangle([x, sea_y, x + w, y + h], fill=(16, 44, 72))
    for k in range(5):
        wy = sea_y + 10 + k * 12
        d.line([(x + 8 + k * 30, wy), (x + 90 + k * 40, wy)],
               fill=(52, 96, 140), width=2)
    d.polygon([(x + 30, sea_y), (x + 150, sea_y - 26), (x + 300, sea_y - 18),
               (x + 420, sea_y), (x + 420, sea_y + 4), (x + 30, sea_y + 4)],
              fill=(8, 20, 34))
    d.polygon([(x + 60, sea_y - 26), (x + 70, sea_y - 52),
               (x + 82, sea_y - 26)], fill=(8, 20, 34))
    d.polygon([(x + 200, sea_y - 18), (x + 208, sea_y - 40),
               (x + 218, sea_y - 18)], fill=(8, 20, 34))
    for (x1, y1, x2, y2) in [(40, 96, 120, 30), (150, 100, 210, 22),
                             (260, 98, 330, 34), (330, 100, 380, 44)]:
        d.line([(x + x1, y + y1), (x + x2, y + y2)], fill=(255, 170, 60),
               width=3)
        d.ellipse([x + x2 - 4, y + y2 - 4, x + x2 + 4, y + y2 + 4],
                  fill=(255, 220, 120))
        d.ellipse([x + x1 - 2, y + y1 - 2, x + x1 + 2, y + y1 + 2],
                  fill=(255, 120, 40))
    for bx in (90, 250):
        d.polygon([(x + bx, sea_y), (x + bx + 8, y + 14),
                   (x + bx + 14, y + 14), (x + bx + 6, sea_y)],
                  fill=(255, 250, 220))


def paint_shenzhen(d, x, y, w, h):
    """Shenzhen at dusk: skyline, three flag poles, APEC banner."""
    d.rectangle([x, y, x + w, y + h], fill=(252, 222, 130))
    d.ellipse([x + w - 52, y + 8, x + w - 16, y + 44], fill=(240, 140, 40))
    sky = [(20, 54), (44, 42), (68, 58), (92, 46), (116, 60),
           (140, 40), (164, 56), (188, 44), (212, 58)]
    for i, (bx, bh) in enumerate(sky):
        col = (52, 58, 74) if i % 2 == 0 else (34, 40, 56)
        d.rectangle([x + bx, y + h - bh, x + bx + 20, y + h], fill=col)
        for wy in range(y + h - bh + 8, y + h - 6, 14):
            d.rectangle([x + bx + 4, wy, x + bx + 8, wy + 6],
                        fill=(252, 222, 130))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(20, 24, 34))
    flags = [(250, 200, 60), (180, 60, 60), (60, 60, 180)]
    for i, (r, g, b) in enumerate(flags):
        px = x + 24 + i * 30
        d.line([(px, y + 8), (px, y + h - 26)], fill=(20, 24, 34), width=2)
        d.rectangle([px, y + 8, px + 22, y + 24], fill=(r, g, b))


def paint_alaska(d, x, y, w, h):
    """Alaska: snowy peaks, ballot box, stars."""
    d.rectangle([x, y, x + w, y + h], fill=(176, 208, 232))
    d.ellipse([x + w - 46, y + 8, x + w - 14, y + 40], fill=(255, 244, 200))
    d.polygon([(x, y + h), (x + 70, y + 18), (x + 140, y + h)],
              fill=(250, 250, 252))
    d.polygon([(x + 100, y + h), (x + 180, y + 8), (x + w, y + h)],
              fill=(228, 236, 244))
    d.polygon([(x + 56, y + 34), (x + 70, y + 18), (x + 84, y + 34)],
              fill=(200, 214, 228))
    d.polygon([(x + 166, y + 24), (x + 180, y + 8), (x + 194, y + 24)],
              fill=(190, 205, 220))
    d.rectangle([x + 78, y + h - 44, x + 160, y + h - 6], fill=(20, 32, 56))
    d.rectangle([x + 96, y + h - 54, x + 142, y + h - 44], fill=(242, 194, 0))
    d.polygon([(x + 104, y + h - 66), (x + 118, y + h - 86),
               (x + 132, y + h - 66)], fill=(255, 255, 255))
    d.rectangle([x + 104, y + h - 66, x + 132, y + h - 58], fill=(185, 28, 28))
    d.text((x + 168, y + h - 34), "56–44", font=f_bold(20),
           fill=(185, 28, 28))


def paint_nvidia(d, x, y, w, h):
    """A chip on dark green: die, pins, rising chart."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 24, 12))
    for px in range(x + 8, x + w - 8, 26):
        d.line([(px, y + 6), (px, y + 22)], fill=(118, 185, 0), width=3)
        d.line([(px, y + h - 22), (px, y + h - 6)], fill=(118, 185, 0),
               width=3)
    d.rectangle([x + 74, y + 20, x + 164, y + h - 20], fill=(24, 48, 24))
    d.rectangle([x + 74, y + 20, x + 164, y + h - 20],
                outline=(118, 185, 0), width=2)
    d.rectangle([x + 96, y + 28, x + 142, y + h - 28], fill=(118, 185, 0))
    d.text((x + 104, y + 30), "AI", font=f_bold(16), fill=(12, 24, 12))
    pts = [(x + 8, y + h - 30), (x + 60, y + h - 38), (x + 110, y + h - 34),
           (x + 160, y + h - 50), (x + 210, y + h - 56), (x + w - 10, y + 14)]
    d.line(pts, fill=(242, 194, 0), width=3)
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
              fill=(242, 194, 0))
    d.text((x + 10, y + 8), "+5%", font=f_bold(18), fill=(242, 194, 0))


def paint_antalya(d, x, y, w, h):
    """Antalya coast: sun, sea, hills, conference hall."""
    d.rectangle([x, y, x + w, y + h], fill=(140, 196, 228))
    d.ellipse([x + 16, y + 10, x + 52, y + 46], fill=(255, 214, 90))
    d.polygon([(x, y + 58), (x + 80, y + 30), (x + 160, y + 58),
               (x + w, y + 44), (x + w, y + 58)], fill=(90, 140, 90))
    d.rectangle([x, y + 58, x + w, y + h], fill=(36, 110, 160))
    for k in range(3):
        wy = y + 72 + k * 14
        d.line([(x + 12 + k * 40, wy), (x + 90 + k * 30, wy)],
               fill=(120, 190, 220), width=2)
    d.rectangle([x + 148, y + h - 46, x + 218, y + h - 6], fill=(255, 255, 255))
    d.polygon([(x + 142, y + h - 46), (x + 183, y + h - 68),
               (x + 224, y + h - 46)], fill=(185, 28, 28))
    for i in range(4):
        d.rectangle([x + 156 + i * 16, y + h - 36, x + 164 + i * 16,
                     y + h - 14], fill=(36, 110, 160))
    d.text((x + 10, y + h - 24), "COP31", font=f_bold(16), fill=(255, 255, 255))


def paint_map(d, x, y, w, h, places):
    """World map, equirectangular, honest aspect, with numbered places."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for lat in (-40, 0, 40, 80):
        _, ly = project(0, lat, x, y, w, h)
        d.line([(x, ly), (x + w, ly)], fill=(28, 52, 84), width=1)
    for lon in (-120, -60, 0, 60, 120):
        lx, _ = project(lon, 0, x, y, w, h)
        d.line([(lx, y), (lx, y + h)], fill=(28, 52, 84), width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, x, y, w, h) for lon, lat in poly]
        d.polygon(pts, fill=(214, 204, 178))
    for (num, lon, lat, name, dx, dy) in places:
        px, py = project(lon, lat, x, y, w, h)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=GOLD)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], outline=INK, width=1)
        d.text((px - 3, py - 6), str(num), font=f_bold(11), fill=INK)
        lx = px + dx
        ly = py + dy
        d.text((lx, ly), name, font=f_bold(12), fill=WHITE,
               stroke_width=2, stroke_fill=NAVY)


# ------------------------------------------------------------------- stories
LEAD_KICKER = "THE GULF · WAR WIDENS"
LEAD_HEAD = "Iran strikes Kuwait and Bahrain after US hits Qeshm Island"
LEAD_DECK = ("Tehran says it hit US drone and missile sites overnight. "
             "Kuwait repelled the attack; Bahrain logged its third "
             "interception in a week.")
LEAD_BYLINE = "Reuters · BBC · The Wall Street Journal"

SCENES = [
    (paint_shenzhen, "SHENZHEN · THREE LEADERS"),
    (paint_alaska, "ALASKA · SENATE FLIPS 56–44"),
    (paint_nvidia, "NVIDIA BEATS THE STREET"),
    (paint_antalya, "COP31 · STOCKTAKE BEGINS"),
]

PLACES = [
    (1, 48, 29, "Gulf", -14, -22),
    (2, 114, 22, "Shenzhen", -32, -22),
    (3, 121, 15, "Manila", 10, 12),
    (4, -150, 64, "Alaska", -16, 10),
    (5, -77, 39, "Washington", -36, -22),
    (6, 31, 37, "Antalya", -14, 10),
    (7, 0, 51, "London", -14, -22),
    (8, 73, 19, "Mumbai", -12, 10),
    (9, 147, -43, "Hobart", -32, -22),
    (10, 0, 6, "Accra", -12, 10),
]

REGIONS = [
    "Middle East — Gulf war widens",
    "Asia-Pacific — APEC in Shenzhen",
    "Europe — COP31, EU debate",
    "North America — Senate flips",
    "South America — Amazon science",
    "Africa — Ethiopia–Eritrea tensions",
    "Oceania — England win in Hobart",
]

NUMBERS = [
    "42 stories in one image",
    "56–44 Senate majority",
    "$81.3bn Anthropic IPO",
    "Nvidia shares +5%",
    "Gold $3,770, down 2%",
    "97 runs — Duckett 133",
]

TOP6 = [
    ("Trump hails 'very big' Philippines trade deal",
     "Manila calls it an economic understanding instead"),
    ("US loses measles-elimination status",
     "A year of continuous spread ends the status"),
    ("Waymo pulls driverless taxis off US freeways",
     "Driverless taxis leave every US freeway"),
    ("Houthis retake Bab el-Mandeb strait",
     "Saudis expect the war to last six more months"),
    ("Anthropic IPO raises a record $81.3bn",
     "Claude-maker valued near $1.4 trillion"),
    ("Myanmar faces genocide verdict at UN court",
     "Historic ruling due over Rohingya massacres"),
]

BRIEFS = [
    "Mossad chief lobbied US for new Iran strikes",
    "Bapco refinery back above 80% capacity",
    "Iraq cracks down on oil-smuggling ring",
    "Vance: no 'forever war' in the Gulf",
    "Kahana elected speaker of Israel's Knesset",
    "Board of Peace faults Israel and Hamas",
    "Ethiopia, Eritrea mass forces at border",
    "Myanmar to review ASEAN relationship",
    "US officer held in UK over spying taken home",
    "27 years for Iran-backed Trump murder plot",
    "UK inflation 3.6%; bills to rise £443 a year",
    "Burnham to set out EU options next month",
    "Ford ships first CATL-tech battery cells",
    "Critical Java flaw found by AI start-up",
    "Gold falls over 2% to $3,770 an ounce",
    "Brent crude $92, down 23% from October",
    "India bonds draw $1.1bn foreign inflows",
    "China to invest $15bn in Türkiye renewables",
    "Norway pays for 12m tonnes of CO2 cuts",
    "BYD 1 MW solar charger debuts in Abu Dhabi",
    "Yangwang U9 Xtreme tops 500 km/h",
    "England win Hobart ODI by 97 runs",
    "Duckett's 133 seals Hobart ODI win",
    "Chahal first Indian to 400 T20 wickets",
    "Bihar stun Delhi chasing 225 in SMAT",
    "Ghana's $60m presidential jet sparks anger",
    "Earthshot green carpet rolls out in Mumbai",
    "Hunger Games prequel splits opinion",
    "Bezos 'heavily involved' in new 007 casting",
    "California landfill eruption spews black ash",
    "Man charged with axe attack on US jet",
]

MARKETS = ("MARKETS   Gold $3,770  -2.1%    Brent $92    Nvidia +5%    "
           "Rupee 93.44/$    India bonds +$1.1bn")
FOOTER = ("Sources: Reuters · BBC · AP · NPR · ESPNcricinfo · UN News · "
          "The Weekly Anthropocene · Morning Brief — All events of "
          "Wednesday 18 November 2026")


def build(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 76], fill=BLACK)
    title = "THE WORLD IN ONE DAY"
    tf = f_serif(62)
    d.text(((W - tw(d, title, tf)) // 2, 6), title, font=tf, fill=WHITE)
    rule(d, 0, 76, W, fill=GOLD, weight=3)

    # Date ribbon
    d.rectangle([0, 79, W, 112], fill=GOLD)
    d.text((M, 85), "WEDNESDAY 18 NOVEMBER 2026", font=f_bold(30), fill=INK)
    rt = "42 STORIES · 7 REGIONS"
    d.text((W - M - tw(d, rt, f_bold(16)), 92), rt, font=f_bold(16),
           fill=INK)

    # Lead row
    d.text((M, 122), LEAD_KICKER, font=f_bold(15), fill=RED)
    y = 144
    y = para(d, M, y, LEAD_HEAD, f_bold(29), 540, leading=37)
    y += 4
    y = para(d, M, y, LEAD_DECK, f_reg(16), 540, leading=20)
    d.text((M, 272), LEAD_BYLINE, font=f_reg(12), fill=GRAY)
    paint_gulf(d, 568, 118, 440, 188)

    # Scene row: four illustrated panels with one-line labels
    for i, (painter, label) in enumerate(SCENES):
        px = M + i * 246
        painter(d, px, 312, 238, 78)
        d.rectangle([px, 390, px + 238, 420], fill=BLACK)
        d.text((px + 8, 397), label, font=f_bold(13), fill=WHITE)

    # Map band: correct-aspect world map, regions left, numbers right
    map_h = 186
    map_w = int(map_h * 360 / 142)
    mx = (W - map_w) // 2
    paint_map(d, mx, 420, map_w, map_h, PLACES)
    d.text((M, 428), "SEVEN REGIONS", font=f_bold(14), fill=INK)
    rule(d, M, 448, 240, fill=RED, weight=2)
    yy = 456
    for r in REGIONS:
        d.text((M, yy), r, font=f_reg(13), fill=INK)
        yy += 20
    d.text((756, 428), "THE DAY IN NUMBERS", font=f_bold(14), fill=INK)
    rule(d, 756, 448, 236, fill=RED, weight=2)
    yy = 456
    for n in NUMBERS:
        d.text((756, yy), n, font=f_reg(13), fill=INK)
        yy += 20

    # Top stories: two columns, three rows
    d.text((M, 612), "TOP STORIES", font=f_bold(15), fill=INK)
    rule(d, M, 632, W - 2 * M, fill=INK, weight=2)
    for i, (head, deck) in enumerate(TOP6):
        col = i % 2
        row = i // 2
        cx = M + col * 512
        cy = 640 + row * 38
        d.text((cx, cy), head, font=f_bold(18), fill=INK)
        d.text((cx, cy + 21), deck, font=f_reg(13), fill=GRAY)

    # Numbered briefs: three columns
    d.text((M, 752), "THE DAY IN BRIEF — 31 MORE STORIES", font=f_bold(14),
           fill=INK)
    rule(d, M, 772, W - 2 * M, fill=INK, weight=2)
    cols_x = [M, 350, 684]
    for i, b in enumerate(BRIEFS):
        col = i // 11
        row = i % 11
        cx = cols_x[col]
        cy = 780 + row * 16
        num = f"{i + 12}"
        d.text((cx, cy), num, font=f_bold(13), fill=RED)
        d.text((cx + 26, cy), b, font=f_reg(13), fill=INK)

    # Markets strip
    d.rectangle([0, 954, W, 992], fill=GOLD)
    d.text(((W - tw(d, MARKETS, f_bold(15))) // 2, 966), MARKETS,
           font=f_bold(15), fill=INK)

    # Footer
    d.text((M, 1000), FOOTER, font=f_reg(11), fill=GRAY)

    img.save(path, format="PNG")
    return img


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(out)
    print("wrote", out)
