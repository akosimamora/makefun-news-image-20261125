"""Render the Wednesday 25 November 2026 front page to entry.png.

A one-page newspaper: masthead, verified UTC timeline, KPI strip, region
bar, three data-diagram heroes, ten tiles, a pinned world map, the ALSO ON
list, a DATE CHECK box, and a footer. Every fact comes from the verified
news file; every clock time on the page was checked against a live source.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
INK = (18, 18, 18)
RED = (178, 34, 28)
DARK = (20, 24, 34)
NAVY = (16, 28, 52)
TEAL = (14, 110, 110)
GREY = (110, 108, 100)
LINE = (200, 194, 182)
CREAM = (238, 232, 218)

REGION_COLOURS = {
    "EUROPE": (38, 90, 168),
    "MIDDLE EAST": (214, 110, 20),
    "ASIA": (24, 140, 90),
    "AFRICA": (128, 70, 160),
    "AMERICAS": (16, 130, 130),
    "OCEANIA": (198, 60, 130),
    "GLOBAL": (110, 108, 100),
}

BADGE_FILL = {
    "REPORTED": (232, 222, 200),
    "OFFICIAL": (34, 90, 160),
    "CLAIM": (214, 110, 20),
    "ONGOING": (120, 40, 40),
}
BADGE_TEXT = {
    "REPORTED": INK,
    "OFFICIAL": (255, 255, 255),
    "CLAIM": (255, 255, 255),
    "ONGOING": (255, 255, 255),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def serif(size):
    return font("DMSerifDisplay-Regular.ttf", size)


def black(size):
    return font("Lato-Black.ttf", size)


def bold(size):
    return font("Lato-Bold.ttf", size)


def regular(size):
    return font("Lato-Regular.ttf", size)


def wrap(draw, text, fnt, width):
    """Split text into lines that fit `width` pixels."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_badge(draw, x, y, label, size=9):
    """A small badge; returns its width."""
    fnt = bold(size)
    pad = 5
    w = int(draw.textlength(label, font=fnt)) + pad * 2
    h = size + 7
    fill = BADGE_FILL[label]
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=fill)
    draw.text((x + pad, y + 3), label, font=fnt, fill=BADGE_TEXT[label])
    return w


def draw_num_circle(draw, cx, cy, n, r=11):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    fnt = black(12)
    t = str(n)
    tw = draw.textlength(t, font=fnt)
    draw.text((cx - tw / 2, cy - 7), t, font=fnt, fill=(255, 255, 255))


# ------------------------------------------------------------------- data
KPI = [
    ("−6.2%", "Kospi close — 4,697.51"),
    ("+36%", "Bangladesh garment pay rise"),
    ("4.9%", "Australia inflation, October"),
    ("9 DEAD", "17 trapped in Java gold mine"),
    ("20%", "top proposed US tariff, China"),
    ("14", "economies face new US tariffs"),
]

REGIONS = [
    ("EUROPE", 5), ("MIDDLE EAST", 5), ("ASIA", 6), ("AFRICA", 8),
    ("AMERICAS", 4), ("OCEANIA", 4), ("GLOBAL", 1),
]

# Only these eight times may appear on the page; each was verified.
TIMELINE = [
    ("00:03", "Met review\nreported"),
    ("00:18", "Shenzhou-24\nlaunches"),
    ("00:30", "Aus CPI\n4.9%"),
    ("03:56", "Shenzhou-24\ndocks"),
    ("06:30", "Kospi closes\n−6.2%"),
    ("07:14", "Ofgem +26%\nprice cap"),
    ("09:46", "2 tankers hit\nin Hormuz"),
    ("12:10", "Ras Tanura\nclaim reported"),
]

HEROES = [
    {
        "n": 1, "region": "SEOUL · TOKYO · TAIPEI · MARKETS", "badge": "REPORTED",
        "kind": "kospi",
        "headline": "AI doubts return: Asian chip stocks crash, Kospi −6.2%",
        "deck": "Seoul's Kospi falls to 4,697.51 as SK Hynix drops 11.1% and "
                "Samsung 9.9%; Taiex −4.8%, Nikkei −2.8%.",
        "sources": "Reuters · WSJ · Yonhap",
    },
    {
        "n": 2, "region": "JIUQUAN, CHINA · SPACE", "badge": "OFFICIAL",
        "kind": "shenzhou",
        "headline": "Pakistan's first astronaut docks at China's space station",
        "deck": "Shenzhou-24 lifts off 00:18 UTC; Muhammad Zeeshan Ali, 40, is the "
                "first foreigner aboard Tiangong and the first Pakistani in orbit.",
        "sources": "Xinhua · CMSA · Reuters",
    },
    {
        "n": 3, "region": "WASHINGTON · TRADE", "badge": "OFFICIAL",
        "kind": "tariffs",
        "headline": "US proposes tariffs of up to 20% on 14 economies",
        "deck": "China faces the highest rate; EU 15%, Japan 15%. Duties would "
                "start in January after a public hearing.",
        "sources": "Reuters · CNN · USTR",
    },
]

TILES = [
    {
        "n": 4, "region": "SAMARA · WAR", "badge": "REPORTED",
        "kind": "refinery", "big": "2", "big2": "REFINERIES",
        "headline": "Ukraine drones set two Russian refineries ablaze",
        "deck": "145 drones downed; 1 killed in Samara.",
        "sources": "Reuters · Kyiv Independent",
    },
    {
        "n": 5, "region": "HORMUZ · SHIPPING", "badge": "CLAIM",
        "kind": "tanker", "big": "2", "big2": "TANKERS",
        "headline": "Iran says mines set two tankers on fire in Hormuz",
        "deck": "Ships took an 'unauthorised route'.",
        "sources": "Reuters · IRNA",
    },
    {
        "n": 6, "region": "RAS TANURA · WAR", "badge": "CLAIM",
        "kind": "smoke", "big": "600 km²", "big2": "SMOKE",
        "headline": "Houthis say they hit Saudi Arabia's biggest refinery",
        "deck": "Coalition downed 4 drones; hit unconfirmed.",
        "sources": "Reuters · Al-Monitor",
    },
    {
        "n": 7, "region": "HODEIDAH, YEMEN · WAR", "badge": "REPORTED",
        "kind": "port", "big": "3", "big2": "GOVERNORATES",
        "headline": "Coalition strikes Hodeidah port",
        "deck": "Civilians warned to leave first.",
        "sources": "SPA · Reuters",
    },
    {
        "n": 8, "region": "DHAKA · LABOUR", "badge": "OFFICIAL",
        "kind": "wage", "big": "+36%", "big2": "PAY RISE",
        "headline": "Garment workers win 36% pay rise",
        "deck": "Minimum wage to 17,000 taka from 12,500.",
        "sources": "Reuters · Al Jazeera",
    },
    {
        "n": 9, "region": "SYDNEY · ECONOMY", "badge": "OFFICIAL",
        "kind": "cpi", "big": "4.9%", "big2": "INFLATION",
        "headline": "Australia inflation jumps to 4.9%",
        "deck": "Core 3.8%, up from 3.6%.",
        "sources": "ABS · Reuters",
    },
    {
        "n": 10, "region": "BOGOR, JAVA · DISASTER", "badge": "REPORTED",
        "kind": "mine", "big": "9", "big2": "DEAD",
        "headline": "9 dead, 17 trapped in flooded Java gold mine",
        "deck": "11 escaped; 325 rescuers at work.",
        "sources": "AP · Reuters",
    },
    {
        "n": 11, "region": "LONDON · ENERGY", "badge": "OFFICIAL",
        "kind": "energy", "big": "+26%", "big2": "BILL RISE",
        "headline": "UK energy bills to jump 26% from January",
        "deck": "Cap rises to £2,166 a year, up £443.",
        "sources": "Ofgem · Reuters",
    },
    {
        "n": 12, "region": "LONDON · POLICING", "badge": "REPORTED",
        "kind": "shield", "big": "0/14", "big2": "GOOD PROGRESS",
        "headline": "Met Police still institutionally racist, review finds",
        "deck": "No 'good progress' on any of 14.",
        "sources": "Guardian · Standard",
    },
    {
        "n": 13, "region": "GAZA CITY · WAR", "badge": "REPORTED",
        "kind": "building", "big": "4", "big2": "KILLED",
        "headline": "Israeli strike kills Hamas official, his wife and children",
        "deck": "Second such killing in 24 hours.",
        "sources": "Reuters · Al Jazeera",
    },
]

ALSO_ON = [
    (14, "Solomon Islands", "signs Australia pact — Canberra; no foreign bases.", "Reuters"),
    (15, "Morocco", "vows fight over AFCON title — to appeal CAS ruling.", "AP"),
    (16, "Shanghai", "China probes Politburo member Chen Jining.", "Reuters"),
    (17, "Moscow", "US drops business-deal lure for Ukraine peace.", "FT"),
    (18, "London", "over a third of UK Muslim students face Islamophobia.", ""),
    (19, "Seoul", "subway strike averted by overnight wage deal.", ""),
    (20, "Lagos", "Nollywood legend Pete Edochie dies at 79.", "BBC"),
    (21, "Monrovia", "Boakai to sign $5.7bn Bea Mountain gold deal.", ""),
    (22, "Addis Ababa", "polio campaign targets 11.3m children.", ""),
    (23, "Pretoria", "won't drop empowerment laws over US tariffs.", ""),
    (24, "Lusaka", "opposition leader indicted for treason.", ""),
    (25, "Mogadishu", "speaker accuses neighbours over al-Shabab.", ""),
    (26, "Ituri", "UNICEF — abuse of women up in Ebola-hit DR Congo.", ""),
    (27, "Iowa", "Army to blow up 4 tonnes of lead azide.", ""),
    (28, "Washington", "poll — 55% of voters want Iran war ended now.", ""),
    (29, "Ottawa", "military police officer faces five service charges.", ""),
    (30, "Sydney", "major gas leak shuts CBD streets.", ""),
    (31, "Canberra", "formal apology to LGBTQ veterans.", ""),
    (32, "UN", "16 days against gender violence begin today.", ""),
    (33, "Ras Tanura", "Saudis down four Houthi drones.", "Coalition"),
]

DATE_CHECK_LEFT = [
    ("MON 23 NOV", "Huang reinstated as Nvidia CEO"),
    ("SUN 22 NOV", "COP31 collapses in Antalya — no deal"),
    ("MON 23 NOV", "3 tankers hit mines in Hormuz (announced)"),
    ("TUE 24 NOV", "Riyadh PIF tower strike, 11 injured"),
    ("TUE 24 NOV", "Zaporizhzhia night strike"),
    ("TUE 24 NOV", "Huawei convicted in Brooklyn"),
    ("TUE 24 NOV", "CAS ruling gave Senegal AFCON title back"),
]
DATE_CHECK_NOTYET = [
    ("THU 26 NOV", "US Thanksgiving"),
    ("THU 26 NOV", "Special European Council"),
]

# ------------------------------------------------------- hero diagrams
def hero_kospi(draw, x, y, w, h):
    """Falling Kospi line over a dark panel, with the three stock falls."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    for gy in range(1, 4):
        yy = y + h * gy / 4
        draw.line([x + 8, yy, x + w - 8, yy], fill=(52, 66, 92), width=1)
    pts = [(x + 14, y + 22), (x + 60, y + 30), (x + 105, y + 26),
           (x + 150, y + 44), (x + 195, y + 52), (x + 235, y + 68),
           (x + 275, y + 82)]
    draw.line(pts, fill=(235, 70, 55), width=3, joint="curve")
    for px, py in pts[::2]:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(235, 70, 55))
    draw.polygon([(x + 275, y + 82), (x + 290, y + 76), (x + 290, y + 92)],
                 fill=(235, 70, 55))
    draw.text((x + 12, y + 8), "KOSPI  −6.2%", font=black(20),
              fill=(255, 255, 255))
    draw.text((x + 12, y + h - 40), "SK HYNIX  −11.1%", font=bold(12),
              fill=(255, 170, 150))
    draw.text((x + 12, y + h - 22), "SAMSUNG  −9.9%   ·   TAIEX −4.8%   ·   NIKKEI −2.8%",
              font=bold(10), fill=(190, 200, 220))


def hero_shenzhou(draw, x, y, w, h):
    """Launch-to-dock timeline: rocket at 00:18, station at 03:56."""
    draw.rectangle([x, y, x + w, y + h], fill=(10, 18, 44))
    import random
    rng = random.Random(25)
    wi, hi = int(w), int(h)
    for _ in range(46):
        sx = x + rng.randint(4, wi - 4)
        sy = y + rng.randint(4, hi - 4)
        r = rng.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 225, 240))
    # ground + launch pad (left)
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(38, 44, 60))
    # rocket
    rx, ry = x + 42, y + h - 66
    draw.polygon([(rx, ry - 26), (rx - 9, ry), (rx + 9, ry)], fill=(235, 70, 55))
    draw.rectangle([rx - 9, ry, rx + 9, ry + 26], fill=(240, 240, 235))
    draw.rectangle([rx - 14, ry + 16, rx - 9, ry + 30], fill=(200, 60, 50))
    draw.rectangle([rx + 9, ry + 16, rx + 14, ry + 30], fill=(200, 60, 50))
    draw.polygon([(rx - 5, ry + 30), (rx + 5, ry + 30), (rx, ry + 40)],
                 fill=(255, 180, 60))
    # dashed flight arc
    for i in range(9):
        t = i / 8
        ax = x + 66 + t * 150
        ay = y + h - 52 - (38 * (1 - (2 * t - 1) ** 2))
        draw.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill=(255, 200, 90))
    # station (right): core module + solar wings
    sx, sy = x + w - 96, y + 30
    draw.rectangle([sx, sy, sx + 14, sy + 44], fill=(235, 235, 230))
    draw.rectangle([sx - 52, sy + 8, sx, sy + 20], fill=(52, 110, 200))
    draw.rectangle([sx + 14, sy + 8, sx + 66, sy + 20], fill=(52, 110, 200))
    draw.rectangle([sx - 52, sy + 24, sx, sy + 36], fill=(52, 110, 200))
    draw.rectangle([sx + 14, sy + 24, sx + 66, sy + 36], fill=(52, 110, 200))
    draw.ellipse([sx - 4, sy + 18, sx + 18, sy + 26], fill=(255, 200, 90))
    draw.text((x + 10, y + 6), "00:18  LAUNCH", font=black(11),
              fill=(255, 255, 255))
    draw.text((x + w - 118, y + h - 22), "03:56  DOCK", font=black(11),
              fill=(255, 255, 255))


def hero_tariffs(draw, x, y, w, h):
    """Horizontal bars: proposed tariff rate by economy."""
    draw.rectangle([x, y, x + w, y + h], fill=(246, 240, 226))
    draw.text((x + 10, y + 6), "PROPOSED RATE", font=black(11), fill=INK)
    bars = [("CHINA", 20, RED), ("VIETNAM", 20, RED), ("MALAYSIA", 19, (214, 110, 20)),
            ("INDIA", 17, (214, 110, 20)), ("EU", 15, (38, 90, 168)),
            ("JAPAN", 15, (38, 90, 168))]
    top = y + 22
    row_h = 11
    for i, (name, val, col) in enumerate(bars):
        by = top + i * row_h
        draw.text((x + 10, by + 1), name, font=bold(10), fill=INK)
        bx = x + 78
        bw = (w - 118) * val / 20.0
        draw.rectangle([bx, by + 2, bx + bw, by + row_h - 5], fill=col)
        draw.text((bx + bw + 5, by + 1), "%d%%" % val, font=black(11), fill=INK)
    draw.text((x + 10, y + h - 14), "14 ECONOMIES · MEXICO + NORWAY EXCLUDED",
              font=bold(9), fill=GREY)


# ------------------------------------------------------- tile mini-visuals
def tile_visual(draw, kind, x, y, w, h):
    x, y, w, h = int(x), int(y), int(w), int(h)
    if kind == "refinery":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 26, 22))
        for bx in (x + 12, x + 34, x + 56):
            draw.rectangle([bx, y + 16, bx + 12, y + h], fill=(90, 84, 76))
            draw.polygon([(bx + 6, y + 4), (bx + 1, y + 16), (bx + 11, y + 16)],
                         fill=(255, 140, 40))
        draw.ellipse([x + w - 26, y + 6, x + w - 8, y + 22], fill=(255, 180, 60))
    elif kind == "tanker":
        draw.rectangle([x, y, x + w, y + h], fill=(18, 60, 110))
        draw.rectangle([x + 14, y + 14, x + w - 14, y + 26], fill=(20, 24, 34))
        draw.rectangle([x + 30, y + 6, x + 44, y + 14], fill=(240, 240, 235))
        draw.polygon([(x + 60, y + 2), (x + 55, y + 14), (x + 65, y + 14)],
                     fill=(255, 140, 40))
        for wx in range(x + 6, x + w - 6, 14):
            draw.arc([wx, y + h - 10, wx + 12, y + h - 2], 180, 360,
                     fill=(140, 190, 230), width=2)
    elif kind == "smoke":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 22, 20))
        for bx in (x + 10, x + 30, x + 50):
            draw.rectangle([bx, y + 18, bx + 12, y + h], fill=(110, 104, 96))
        draw.ellipse([x + 16, y + 2, x + 34, y + 16], fill=(150, 148, 142))
        draw.ellipse([x + 34, y - 2, x + 56, y + 14], fill=(120, 118, 112))
        draw.ellipse([x + 52, y + 4, x + 70, y + 18], fill=(150, 148, 142))
    elif kind == "port":
        draw.rectangle([x, y, x + w, y + h], fill=(16, 90, 96))
        draw.line([x + 14, y + h - 6, x + 14, y + 6], fill=(240, 240, 235), width=3)
        draw.line([x + 14, y + 8, x + 44, y + 8], fill=(240, 240, 235), width=3)
        draw.line([x + 44, y + 8, x + 44, y + 20], fill=(240, 240, 235), width=2)
        for cx in (x + 52, x + 66):
            draw.rectangle([cx, y + h - 12, cx + 10, y + h - 4], fill=(255, 170, 60))
        draw.rectangle([x + w - 24, y + h - 14, x + w - 10, y + h - 4],
                       fill=(200, 60, 50))
    elif kind == "wage":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 120, 80))
        draw.text((x + 8, y + 6), "+36%", font=black(20), fill=(255, 255, 255))
        for i in range(3):
            draw.rectangle([x + 10 + i * 24, y + h - 12 - i * 4, x + 28 + i * 24,
                            y + h - 6], fill=(255, 210, 90))
    elif kind == "cpi":
        draw.rectangle([x, y, x + w, y + h], fill=(70, 50, 130))
        bars = [10, 16, 22, 30]
        for i, bh in enumerate(bars):
            draw.rectangle([x + 10 + i * 20, y + h - 6 - bh, x + 26 + i * 20,
                            y + h - 6], fill=(255, 200, 90) if i == 3 else (200, 190, 230))
    elif kind == "mine":
        draw.rectangle([x, y, x + w, y + h], fill=(52, 40, 26))
        draw.rectangle([x + 30, y + 4, x + 54, y + h], fill=(16, 12, 8))
        for ly in range(y + 10, y + h - 4, 8):
            draw.line([x + 32, ly, x + 52, ly], fill=(120, 110, 95), width=2)
        draw.rectangle([x + 6, y + h - 8, x + w - 6, y + h], fill=(40, 110, 160))
    elif kind == "energy":
        draw.rectangle([x, y, x + w, y + h], fill=(214, 110, 20))
        draw.polygon([(x + 46, y + 4), (x + 34, y + 22), (x + 44, y + 22),
                      (x + 38, y + 36), (x + 52, y + 16), (x + 42, y + 16)],
                     fill=(255, 240, 150))
        draw.text((x + 8, y + h - 16), "£2,166", font=black(12), fill=(255, 255, 255))
    elif kind == "shield":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 40, 80))
        draw.polygon([(x + 44, y + 4), (x + 66, y + 10), (x + 66, y + 24),
                      (x + 44, y + 38), (x + 22, y + 24), (x + 22, y + 10)],
                     fill=(200, 210, 235))
        draw.text((x + 40, y + 12), "!", font=black(16), fill=NAVY)
    elif kind == "building":
        draw.rectangle([x, y, x + w, y + h], fill=(90, 88, 84))
        draw.rectangle([x + 16, y + 8, x + 44, y + h], fill=(60, 58, 54))
        draw.rectangle([x + 48, y + 16, x + 72, y + h], fill=(74, 72, 68))
        for wy in (y + 14, y + 24):
            for wx in (x + 21, x + 31):
                draw.rectangle([wx, wy, wx + 6, wy + 5], fill=(255, 210, 120))
        draw.line([x + 62, y + 4, x + 78, y + 18], fill=(255, 90, 60), width=3)
        draw.line([x + 78, y + 4, x + 62, y + 18], fill=(255, 90, 60), width=3)


# ------------------------------------------------------------------- map
# Rough continent outlines (lon, lat), equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-55, 47), (-60, 45), (-75, 35), (-80, 25), (-90, 20), (-97, 16),
     (-105, 20), (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-155, 58),
     (-165, 60)],
    [(-55, 60), (-45, 60), (-30, 68), (-20, 70), (-30, 76), (-55, 76), (-60, 70)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-55, -35), (-65, -45), (-70, -55), (-73, -40), (-75, -20),
     (-80, -5), (-82, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (25, 65),
     (20, 70), (15, 70), (5, 60), (-5, 58), (-10, 55), (-10, 43)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (48, 11), (51, 10), (40, 0), (35, -15), (30, -25), (25, -35),
     (18, -35), (12, -18), (8, 0), (-8, 5), (-15, 10)],
    [(30, 62), (40, 68), (60, 70), (80, 73), (110, 77), (140, 72), (160, 70),
     (180, 66), (170, 60), (160, 55), (140, 45), (130, 40), (127, 35),
     (120, 30), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (80, 15),
     (75, 8), (70, 20), (60, 25), (50, 25), (45, 30), (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (125, -32), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (146, -19), (142, -11),
     (136, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
]

# story number -> (lon, lat, region)
PINS = {
    1: (127, 37, "ASIA"), 2: (99, 40, "ASIA"), 3: (-77, 39, "AMERICAS"),
    4: (50, 53, "EUROPE"), 5: (56, 26, "MIDDLE EAST"), 6: (50, 26, "MIDDLE EAST"),
    7: (43, 15, "MIDDLE EAST"), 8: (90, 24, "ASIA"), 9: (151, -34, "OCEANIA"),
    10: (107, -7, "ASIA"), 11: (-0.5, 51.5, "EUROPE"), 12: (1.5, 50.5, "EUROPE"),
    13: (34, 31, "MIDDLE EAST"), 14: (160, -9, "OCEANIA"), 15: (-7, 32, "AFRICA"),
    16: (121, 31, "ASIA"), 17: (37, 56, "EUROPE"), 18: (0, 51, "EUROPE"),
    19: (129, 36, "ASIA"), 20: (3, 6, "AFRICA"), 21: (-11, 6, "AFRICA"),
    22: (39, 9, "AFRICA"), 23: (28, -26, "AFRICA"), 24: (28, -15, "AFRICA"),
    25: (45, 2, "AFRICA"), 26: (30, 2, "AFRICA"), 27: (-93, 42, "AMERICAS"),
    28: (-79, 38, "AMERICAS"), 29: (-76, 45, "AMERICAS"), 30: (153, -33, "OCEANIA"),
    31: (149, -35, "OCEANIA"), 32: (-74, 41, "GLOBAL"), 33: (52, 24, "MIDDLE EAST"),
}

# ------------------------------------------------------- page sections
def section_topbar(draw):
    draw.rectangle([0, 0, W, 20], fill=DARK)
    draw.text((18, 4), "THE WORLD IN ONE DAY", font=black(11), fill=(255, 255, 255))
    mid = "DAY 329 OF 2026"
    draw.text((W / 2 - draw.textlength(mid, font=black(11)) / 2, 4), mid,
              font=black(11), fill=(255, 90, 70))
    right = "ALL TIMES UTC · RANKED BY CONSEQUENCE"
    draw.text((W - 18 - draw.textlength(right, font=bold(9)), 5), right,
              font=bold(9), fill=(200, 200, 200))


def section_masthead(draw):
    title = "Wednesday 25 November 2026"
    fnt = serif(56)
    tw = draw.textlength(title, font=fnt)
    draw.text(((W - tw) / 2, 24), title, font=fnt, fill=INK)
    sub = "33 STORIES · 7 REGIONS · EVERY ONE DATED WEDNESDAY 25 NOVEMBER 2026"
    fnt2 = black(13)
    tw2 = draw.textlength(sub, font=fnt2)
    draw.text(((W - tw2) / 2, 84), sub, font=fnt2, fill=RED)
    draw.line([18, 100, W - 18, 100], fill=RED, width=2)


def section_timeline(draw, y0=106, y1=146):
    draw.rectangle([18, y0, 122, y0 + 18], fill=DARK)
    draw.text((26, y0 + 3), "THE DAY IN UTC", font=black(10), fill=(255, 255, 255))
    note = "ALL TIMES VERIFIED"
    draw.text((W - 18 - draw.textlength(note, font=bold(8)), y0 + 4), note,
              font=bold(8), fill=GREY)
    chip_w = (W - 36 - 122) / len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = 122 + chip_w * i + chip_w / 2
        draw.text((cx - draw.textlength(t, font=black(12)) / 2, y0 + 22), t,
                  font=black(12), fill=RED)
        for j, ln in enumerate(label.split("\n")):
            draw.text((cx - draw.textlength(ln, font=regular(9)) / 2,
                       y0 + 22 + 14 + j * 11), ln, font=regular(9), fill=INK)
        if i:
            draw.line([122 + chip_w * i, y0 + 26, 122 + chip_w * i, y0 + 38],
                      fill=LINE, width=1)


def section_kpi(draw, y0=152, y1=196):
    n = len(KPI)
    gap = 6
    bw = (W - 36 - gap * (n - 1)) / n
    for i, (big, cap) in enumerate(KPI):
        x = 18 + i * (bw + gap)
        draw.rectangle([x, y0, x + bw, y1], outline=LINE, width=1, fill=(255, 255, 255))
        fnt = black(22)
        tw = draw.textlength(big, font=fnt)
        draw.text((x + (bw - tw) / 2, y0 + 4), big, font=fnt,
                  fill=RED if big.startswith(("−", "+")) else INK)
        for j, ln in enumerate(wrap(draw, cap, regular(8), bw - 10)):
            draw.text((x + (bw - draw.textlength(ln, font=regular(8))) / 2,
                       y0 + 27 + j * 10), ln, font=regular(8), fill=GREY)


def section_regions(draw, y0=202):
    draw.text((18, y0), "STORIES BY REGION", font=black(10), fill=INK)
    x = 150
    for name, count in REGIONS:
        col = REGION_COLOURS[name]
        draw.rectangle([x, y0 + 1, x + 9, y0 + 10], fill=col)
        label = "%s %d" % (name, count)
        draw.text((x + 12, y0), label, font=bold(10), fill=INK)
        x += 12 + draw.textlength(label, font=bold(10)) + 16


def draw_hero(draw, hero, x, y, w):
    diag_h = 100
    if hero["kind"] == "kospi":
        hero_kospi(draw, x, y, w, diag_h)
    elif hero["kind"] == "shenzhou":
        hero_shenzhou(draw, x, y, w, diag_h)
    else:
        hero_tariffs(draw, x, y, w, diag_h)
    ty = y + diag_h + 8
    draw_num_circle(draw, x + 11, ty + 8, hero["n"])
    draw.text((x + 26, ty + 1), hero["region"], font=black(10), fill=RED)
    draw_badge(draw, x + w - 62, ty, hero["badge"], size=9)
    hy = ty + 20
    for j, ln in enumerate(wrap(draw, hero["headline"], serif(19), w)):
        draw.text((x, hy + j * 22), ln, font=serif(19), fill=INK)
    dy = hy + 22 * len(wrap(draw, hero["headline"], serif(19), w)) + 4
    for j, ln in enumerate(wrap(draw, hero["deck"], regular(10.5), w)):
        draw.text((x, dy + j * 13), ln, font=regular(10.5), fill=(50, 50, 48))
    sy = dy + 13 * len(wrap(draw, hero["deck"], regular(10.5), w)) + 4
    draw.text((x, sy), hero["sources"], font=regular(8.5), fill=GREY)


def section_heroes(draw, y0=218):
    n = 3
    gap = 10
    hw = (W - 36 - gap * (n - 1)) / n
    for i, hero in enumerate(HEROES):
        x = 18 + i * (hw + gap)
        draw_hero(draw, hero, x, y0, hw)
        if i:
            draw.line([x - gap / 2, y0, x - gap / 2, y0 + 218], fill=LINE, width=1)


def draw_tile(draw, tile, x, y, w, h):
    # visual strip (30px), then a compact row, big number, headline, deck.
    tile_visual(draw, tile["kind"], x, y, w, 30)
    draw_num_circle(draw, x + 11, y + 40, tile["n"], r=8)
    draw.text((x + 23, y + 33), tile["region"], font=black(8.5), fill=RED)
    draw_badge(draw, x + w - 56, y + 32, tile["badge"], size=8)
    # big number
    by = y + 48
    fnt = black(19)
    draw.text((x, by), tile["big"], font=fnt, fill=INK)
    tw = draw.textlength(tile["big"], font=fnt)
    draw.text((x + tw + 5, by + 6), tile["big2"], font=bold(9), fill=GREY)
    hy = by + 26
    lines = wrap(draw, tile["headline"], serif(12.5), w)
    for j, ln in enumerate(lines[:2]):
        draw.text((x, hy + j * 14), ln, font=serif(12.5), fill=INK)
    dy = hy + 14 * min(len(lines), 2) + 2
    deck = tile["deck"] + " (" + tile["sources"] + ")"
    dlines = wrap(draw, deck, regular(9), w)
    for j, ln in enumerate(dlines[:2]):
        draw.text((x, dy + j * 11), ln, font=regular(9), fill=(60, 60, 58))


def section_tiles(draw, y0=440):
    n = 5
    gap = 6
    tw = (W - 36 - gap * (n - 1)) / n
    row_h = 124
    for row in range(2):
        yy = y0 + row * (row_h + 6)
        for col in range(5):
            tile = TILES[row * 5 + col]
            x = 18 + col * (tw + gap)
            draw_tile(draw, tile, x, yy, tw, row_h)
            if col:
                draw.line([x - gap / 2, yy, x - gap / 2, yy + row_h], fill=LINE, width=1)
        if row == 0:
            draw.line([18, yy + row_h + 3, W - 18, yy + row_h + 3], fill=LINE, width=1)

# ------------------------------------------------------- map + date check
def section_map(draw, x0=18, y0=700, w=582, h=136):
    draw.text((x0, y0), "WHERE IT HAPPENED — PIN NUMBERS MATCH THE STORIES; PIN COLOUR IS THE REGION",
              font=black(9), fill=INK)
    mx, my, mw, mh = x0, y0 + 14, w, h - 30
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(214, 228, 238))
    # graticule
    for gx in range(mx + 40, mx + mw, 40):
        draw.line([gx, my, gx, my + mh], fill=(190, 205, 220), width=1)
    for gy in range(my + 20, my + mh, 20):
        draw.line([mx, gy, mx + mw, gy], fill=(190, 205, 220), width=1)

    def project(lon, lat):
        px = mx + (lon + 170) / 360.0 * mw
        py = my + (75 - lat) / 130.0 * mh
        return px, py

    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(232, 222, 196), outline=(150, 140, 118))
    # pins
    for n, (lon, lat, region) in sorted(PINS.items()):
        px, py = project(lon, lat)
        col = REGION_COLOURS[region]
        r = 7
        draw.ellipse([px - r, py - r, px + r, py + r], fill=col,
                     outline=(255, 255, 255), width=1)
        fnt = bold(7)
        t = str(n)
        tw = draw.textlength(t, font=fnt)
        draw.text((px - tw / 2, py - 5), t, font=fnt, fill=(255, 255, 255))
    # legend
    lx = mx
    ly = my + mh + 4
    for name, _ in REGIONS:
        col = REGION_COLOURS[name]
        draw.ellipse([lx, ly, lx + 8, ly + 8], fill=col)
        draw.text((lx + 10, ly - 1), name, font=bold(8), fill=INK)
        lx += 10 + draw.textlength(name, font=bold(8)) + 10


def section_date_check(draw, x0=612, y0=700, w=394, h=136):
    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=RED, width=2, fill=(255, 255, 255))
    draw.text((x0 + 10, y0 + 4), "DATE CHECK", font=black(13), fill=RED)
    draw.text((x0 + 108, y0 + 6), "— what we left out, and why", font=regular(10),
              fill=GREY)
    yy = y0 + 22
    draw.text((x0 + 10, yy), "LEFT OUT — OTHER DAYS", font=black(9), fill=INK)
    yy += 11
    for day, what in DATE_CHECK_LEFT:
        draw.text((x0 + 10, yy), day, font=bold(8.5), fill=RED)
        draw.text((x0 + 92, yy), what, font=regular(8.5), fill=INK)
        yy += 10
    yy += 1
    draw.text((x0 + 10, yy), "NOT YET", font=black(9), fill=INK)
    yy += 11
    for day, what in DATE_CHECK_NOTYET:
        draw.text((x0 + 10, yy), day, font=bold(8.5), fill=RED)
        draw.text((x0 + 92, yy), what, font=regular(8.5), fill=INK)
        yy += 10


# ------------------------------------------------------- also on + footer
def section_also_on(draw, y0=846):
    draw.text((18, y0), "ALSO ON WEDNESDAY 25 NOVEMBER", font=black(12), fill=INK)
    draw.line([18, y0 + 16, W - 18, y0 + 16], fill=INK, width=1)
    col_w = (W - 36 - 24) / 2
    for side in range(2):
        items = ALSO_ON[side * 10:(side + 1) * 10]
        x = 18 + side * (col_w + 24)
        yy = y0 + 22
        for n, city, headline, src in items:
            draw.text((x, yy), str(n), font=black(9.5), fill=RED)
            cx = x + 22
            draw.text((cx, yy), city, font=bold(9.5), fill=INK)
            cw = draw.textlength(city, font=bold(9.5))
            rest = headline + (" (%s)" % src if src else "")
            for ln in wrap(draw, rest, regular(9.5), col_w - 22 - cw - 8):
                draw.text((cx + cw + 4, yy), ln, font=regular(9.5), fill=INK)
                break
            yy += 11


def section_footer(draw, y0=982):
    draw.line([18, y0, W - 18, y0], fill=INK, width=1)
    yy = y0 + 6
    draw.text((18, yy), "HOW WE CHECKED", font=black(10), fill=INK)
    legend = ("REPORTED  carried by the day's wires  ·  OFFICIAL  an authority's own word  ·  "
              "CLAIM  one side's account  ·  ONGOING  still unfolding")
    draw.text((150, yy + 1), legend, font=regular(9), fill=INK)
    yy += 15
    srcs = ("Sources: Reuters · AP · AFP · Xinhua · Yonhap · Al Jazeera · ABS · Ofgem · "
            "Guardian · Kyiv Independent · BBC · IRNA · SPA · CMSA")
    draw.text((18, yy), srcs, font=regular(8.5), fill=GREY)
    yy += 13
    draw.text((18, yy),
              "Every story happened or was first reported on Wednesday 25 November 2026 (UTC). "
              "No story from another day is shown as today's news.",
              font=regular(9), fill=INK)


# ------------------------------------------------------------------ render
def render_page():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    section_topbar(draw)
    section_masthead(draw)
    section_timeline(draw)
    section_kpi(draw)
    section_regions(draw)
    section_heroes(draw)
    section_tiles(draw)
    section_map(draw)
    section_date_check(draw)
    section_also_on(draw)
    section_footer(draw)
    return img


if __name__ == "__main__":
    page = render_page()
    out = os.path.join(ROOT, "entry.png")
    page.save(out, format="PNG")
    print("wrote", out)
