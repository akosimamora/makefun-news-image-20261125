#!/usr/bin/env python3
"""Render the round-2 one-day news image: 53 stories, Wednesday 25 Nov 2026.

Fresh build, written from scratch for the round-2 rebuild. All facts come from
the verified research notes (33 round-1 stories + 19 added, Cairo included).
Draws with Pillow into entry.png, 1024x1024, under 1 MiB.
"""
import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1024, 1024
PAPER = (247, 243, 234)
PAPER_SOFT = (242, 237, 224)
INK = (24, 24, 24)
MUTED = (96, 94, 88)
NAVY = (18, 32, 62)
NAVY_SOFT = (38, 58, 96)
RED = (192, 36, 26)
RED_SOFT = (214, 74, 54)
GOLD = (176, 128, 32)
SEA = (216, 226, 232)
LAND = (232, 224, 204)
LINE = (180, 172, 156)

BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE)
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

SERIF = os.path.join(FONT_DIR, "DMSerifDisplay-Regular.ttf")
SANS = os.path.join(FONT_DIR, "Lato-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "Lato-Bold.ttf")
SANS_BLACK = os.path.join(FONT_DIR, "Lato-Black.ttf")

BADGE_FILL = {"OFFICIAL": (31, 78, 121), "REPORTED": (94, 92, 86), "CLAIM": (198, 90, 23)}
REGION_FILL = {
    "Europe": (52, 110, 178),
    "Middle East": (214, 120, 30),
    "Asia": (56, 142, 78),
    "Africa": (128, 78, 158),
    "Americas": (28, 148, 158),
    "Oceania": (206, 84, 138),
    "Global": (110, 110, 110),
}


def face(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- data
# Heroes keep the round-1 trio; each gains a one-line "why it matters".
HEROES = [
    dict(
        num=1, place="SEOUL · TOKYO · TAIPEI", field="Markets", region="Asia",
        badge="REPORTED", art="kospi",
        head="AI doubts return: Asian chip stocks crash, Kospi \u22126.2%",
        body="Seoul's Kospi falls to 4,697.51 as SK Hynix drops 11.1% and Samsung "
             "9.9%. Taiex \u22124.8%, Nikkei \u22122.8%.",
        src="Reuters \u00b7 WSJ \u00b7 Yonhap",
        why="The AI rally that lifted Asia on Tuesday is now in doubt.",
    ),
    dict(
        num=2, place="JIUQUAN, CHINA · SPACE", field="Space", region="Asia",
        badge="OFFICIAL", art="rocket",
        head="Pakistan's first astronaut docks at China's space station",
        body="Shenzhou-24 lifts off 00:18 UTC; Muhammad Zeeshan Ali, 40, is the "
             "first foreigner on Tiangong and the first Pakistani in orbit.",
        src="Xinhua \u00b7 CMSA \u00b7 Reuters",
        why="China's station takes its first foreign guest.",
    ),
    dict(
        num=3, place="WASHINGTON · TRADE", field="Trade", region="Global",
        badge="OFFICIAL", art="tariffs",
        head="US proposes tariffs of up to 20% on 14 economies",
        body="China faces the top 20% rate; EU 15%, Japan 15%. Duties would start "
             "in January after a public hearing.",
        src="Reuters \u00b7 CNN \u00b7 USTR",
        why="Fourteen economies, one salvo \u2014 the year's widest tariff move.",
    ),
]

# Tiles 4-13 are the round-1 tiles; 14-18 are new (Cairo first, as required).
TILES = [
    dict(num=4, place="SAMARA · WAR", field="War", region="Europe", badge="REPORTED",
         big="2 REFINERIES", art="refinery",
         head="Ukraine drones set two Russian refineries ablaze",
         body="Ukrainian drones hit Syzran and Kuibyshev refineries; 145 drones "
              "downed, 1 killed in Samara.",
         src="Reuters \u00b7 Kyiv Independent"),
    dict(num=5, place="HORMUZ · SHIPPING", field="Security", region="Middle East",
         badge="CLAIM", big="2 TANKERS", art="tanker",
         head="Iran says mines set two tankers on fire in Hormuz",
         body="Two tankers struck mines and caught fire; IRGC says they took an "
              "'unauthorised route'.",
         src="Reuters \u00b7 IRNA"),
    dict(num=6, place="RAS TANURA · WAR", field="War", region="Middle East",
         badge="CLAIM", big="600 km\u00b2", art="smoke",
         head="Houthis say they hit Saudi Arabia's biggest refinery",
         body="Houthis claim a Ras Tanura hit; coalition says 4 drones downed. "
              "Smoke over 600 km\u00b2.",
         src="Reuters \u00b7 Al-Monitor"),
    dict(num=7, place="HODEIDAH, YEMEN · WAR", field="War", region="Middle East",
         badge="REPORTED", big="3 GOVERNORATES", art="port",
         head="Coalition strikes Hodeidah port",
         body="Coalition hits the port's operational capabilities; civilians warned "
              "to leave first.",
         src="SPA \u00b7 Reuters"),
    dict(num=8, place="DHAKA · LABOUR", field="Labour", region="Asia",
         badge="OFFICIAL", big="+36%", art="pay",
         head="Garment workers win 36% pay rise",
         body="Wage board: 17,000 taka from 12,500, from 1 Dec; first higher pay "
              "in January.",
         src="Reuters \u00b7 Al Jazeera"),
    dict(num=9, place="SYDNEY · ECONOMY", field="Economy", region="Oceania",
         badge="OFFICIAL", big="4.9%", art="gauge",
         head="Australia inflation jumps to 4.9%",
         body="Annual CPI 4.9%, up from 4.3%; core 3.8%. Fastest in the monthly "
              "series.",
         src="ABS \u00b7 Reuters"),
    dict(num=10, place="BOGOR, JAVA · DISASTER", field="Disaster", region="Asia",
         badge="REPORTED", big="9 DEAD", art="shaft",
         head="9 dead, 17 trapped in flooded Java gold mine",
         body="9 dead, 17 trapped in a flooded unauthorised pit; 11 escaped, "
              "325 rescuers.",
         src="AP \u00b7 Reuters"),
    dict(num=11, place="LONDON · ENERGY", field="Energy", region="Europe",
         badge="OFFICIAL", big="+26%", art="bill",
         head="UK energy bills to jump 26% from January",
         body="Cap rises to \u00a32,166 a year from 1 Jan; +\u00a3443 for a typical "
              "household.",
         src="Ofgem \u00b7 Reuters"),
    dict(num=12, place="LONDON · POLICING", field="Justice", region="Europe",
         badge="REPORTED", big="0/14", art="shield",
         head="Met Police still institutionally racist, review finds",
         body="No 'good progress' on any of 14 Casey fixes; Rowley accepts 10 "
              "recommendations.",
         src="Guardian \u00b7 Standard"),
    dict(num=13, place="GAZA CITY · WAR", field="War", region="Middle East",
         badge="REPORTED", big="4 KILLED", art="ruins",
         head="Israeli strike kills Hamas official, his wife and children",
         body="Abu al-Awf, his wife and two daughters killed in a Shati camp "
              "strike.",
         src="Reuters \u00b7 Al Jazeera"),
    dict(num=14, place="GIZA, EGYPT · DISASTER", field="Disaster", region="Africa",
         badge="REPORTED", big="31 DEAD", art="firetruck",
         head="Fuel tanker fire kills at least 31 near Cairo",
         body="Tanker overturns and explodes on the Ring Road; 31 killed, "
              "21 injured.",
         src="CNN \u00b7 AP"),
    dict(num=15, place="UKRAINE · WAR", field="War", region="Europe",
         badge="REPORTED", big="5 REGIONS", art="pylon",
         head="Russian strikes kill 5, cut power in 5 regions",
         body="Strikes kill 5 and cut power in five regions; Zaporizhzhia plant "
              "on diesel.",
         src="Reuters \u00b7 Al Jazeera"),
    dict(num=16, place="CAPE TOWN · JUSTICE", field="Justice", region="Africa",
         badge="REPORTED", big="RULING", art="gavel",
         head="Court lifts 'Farmgate' ruling against Ramaphosa",
         body="Court voids the 2022 panel report that opened the way to impeach "
              "Ramaphosa.",
         src="Reuters \u00b7 Al Jazeera"),
    dict(num=17, place="CARTAGENA · CRIME", field="Crime", region="Americas",
         badge="REPORTED", big="ALL FREED", art="store",
         head="Cartagena supermarket siege ends: all hostages freed",
         body="Dawn raid frees all hostages after ~17 hours; 1 captor killed, "
              "4 arrested.",
         src="AP \u00b7 Reuters"),
    dict(num=18, place="ENUGU, NIGERIA · CRIME", field="Crime", region="Africa",
         badge="OFFICIAL", big="$227m", art="flask",
         head="Nigeria seizes $227m meth lab, arrests 5 Mexicans",
         body="NDLEA seizes 1,512 kg of meth worth $227m; 5 Mexicans arrested.",
         src="Reuters \u00b7 BBC"),
]

# One-line briefs 19-38 are the round-1 ALSO ON items; 39-52 are new.
# Tuesday-event stories are worded as reported / resolved on Wednesday.
BRIEFS = [
    (19, "Solomon Islands signs Australia pact \u2014 Canberra; no foreign bases.", "Reuters", "Oceania", "Diplomacy"),
    (20, "Morocco vows to appeal after CAS hands AFCON title to Senegal.", "AP", "Africa", "Sport"),
    (21, "China probes Politburo member Chen Jining in Shanghai.", "Reuters", "Asia", "Politics"),
    (22, "US drops business-deal lure for Ukraine peace.", "FT", "Europe", "Diplomacy"),
    (23, "Over a third of UK Muslim students face Islamophobia.", "Report", "Europe", "Rights"),
    (24, "Seoul subway strike averted by overnight wage deal.", "Report", "Asia", "Labour"),
    (25, "Nollywood legend Pete Edochie dies at 79.", "BBC", "Africa", "Culture"),
    (26, "Boakai to sign $5.7bn Bea Mountain gold deal.", "Report", "Africa", "Business"),
    (27, "Polio campaign targets 11.3m children in Ethiopia.", "Official", "Africa", "Health"),
    (28, "Pretoria won't drop empowerment laws over US tariffs.", "Report", "Africa", "Politics"),
    (29, "Zambia opposition leader indicted for treason.", "Report", "Africa", "Justice"),
    (30, "Mogadishu speaker accuses neighbours over al-Shabab.", "Claim", "Africa", "Politics"),
    (31, "UNICEF: abuse of women up in Ebola-hit DR Congo.", "UNICEF", "Africa", "Humanitarian"),
    (32, "US Army to blow up 4 tonnes of lead azide in Iowa.", "Report", "Americas", "Security"),
    (33, "Poll: 55% of US voters want Iran war ended now.", "Poll", "Americas", "Politics"),
    (34, "Ottawa military police officer faces five charges.", "Report", "Americas", "Justice"),
    (35, "Major gas leak shuts Sydney CBD streets.", "Report", "Oceania", "Disaster"),
    (36, "Australia formally apologises to LGBTQ veterans.", "Official", "Oceania", "Rights"),
    (37, "UN: 16 days against gender violence begin today.", "UN", "Global", "Rights"),
    (38, "Saudis down four Houthi drones over Ras Tanura.", "Coalition", "Middle East", "War"),
    (39, "RSF drone toll reported Wednesday: 19 killed in Blue Nile.", "Reuters", "Africa", "War"),
    (40, "North Korea expels Swiss envoy, gives 48 hours to leave.", "Reuters", "Asia", "Diplomacy"),
    (41, "Surprise Eurostar strike cancels Paris\u2013London trains.", "Reuters", "Europe", "Labour"),
    (42, "Knesset advances October 7 inquiry bill, 65\u201350.", "Reuters", "Middle East", "Politics"),
    (43, "Amnesty urges ICC probe over Gaza births.", "Amnesty", "Middle East", "Rights"),
    (44, "Malaysia sues Google for RM600m over YouTube.", "Reuters", "Asia", "Tech"),
    (45, "Hong Kong ticketing hack exposes 1.3m users.", "LCSD", "Asia", "Tech"),
    (46, "Paran\u00e1 storm toll reaches 6 on Wednesday morning.", "Civil Defense", "Americas", "Disaster"),
    (47, "Harare warrant for Mugabe's son reported Wednesday.", "BBC", "Africa", "Justice"),
    (48, "ESA's Hera finds stadium-sized crater on Dimorphos.", "ESA", "Global", "Science"),
    (49, "Ukraine says it hit 5 Russian jets at Savasleyka.", "Claim", "Europe", "War"),
    (50, "US GDP revised up to 4.3% in Q3, fastest in 3 years.", "BEA", "Americas", "Economy"),
    (51, "Poundland collapses; 11,000 jobs at risk.", "Times", "Europe", "Business"),
    (52, "FCC clears SpaceX to launch 1m data-centre satellites.", "FCC", "Americas", "Tech"),
    (53, "EU unveils Quantum Act and \u20ac50bn tech fund.", "Commission", "Europe", "Tech"),
]

# Verified UTC times only (same 8 as round 1; Cairo has no precise UTC hour).
DAY_TIMES = [
    ("00:03", "Met review"),
    ("00:18", "Shenzhou-24"),
    ("00:30", "Aus CPI"),
    ("03:56", "Shenzhou-24"),
    ("06:30", "Kospi closes"),
    ("07:14", "Ofgem +26%"),
    ("09:46", "2 tankers hit"),
    ("12:10", "Ras Tanura"),
]

KPI_CARDS = [
    ("\u22126.2%", "Kospi close \u00b7 4,697.51"),
    ("+36%", "Bangladesh pay rise"),
    ("4.9%", "Australia inflation, Oct"),
    ("9 DEAD", "17 trapped, Java gold mine"),
    ("20%", "top proposed US tariff"),
    ("14", "economies face new tariffs"),
    ("31 DEAD", "Cairo tanker fire"),
]

# Map pins: (story number, longitude, latitude, nudge-x, nudge-y).
PINS = [
    (1, 126.9, 37.5, 0, 0), (2, 98.5, 39.8, 0, 0), (3, -77.0, 38.9, 0, 0),
    (4, 50.1, 53.2, 0, 0), (5, 56.3, 26.5, 7, 0), (6, 50.1, 26.6, -7, 0),
    (7, 42.8, 14.8, 0, 0), (8, 90.4, 23.8, 0, 0), (9, 151.2, -33.9, 0, 0),
    (10, 106.8, -6.6, 0, 0), (11, -0.1, 51.5, -6, -4), (12, 2.5, 50.0, 8, 6),
    (13, 34.5, 31.5, 5, -6), (14, 31.2, 30.0, -6, 7), (15, 32.0, 49.0, 0, 0),
    (16, 18.4, -33.9, 0, 0), (17, -75.5, 10.4, 0, 0), (18, 7.5, 6.4, 0, 0),
]
PIN_REGION = {n: r for n, r in
              [(h["num"], h["region"]) for h in HEROES] +
              [(t["num"], t["region"]) for t in TILES]}


# ---------------------------------------------------------------- helpers
def measure(d, text, font):
    return d.textlength(text, font=font)


def shrink_to(d, text, path, size, max_w, floor=8):
    while size > floor and measure(d, text, face(path, size)) > max_w:
        size -= 1
    return face(path, size)


def wrap(d, text, font, max_w):
    out, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if measure(d, trial, font) <= max_w or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def paint_badge(d, x, y, label):
    f = face(SANS_BLACK, 9)
    w = int(measure(d, label, f)) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=2, fill=BADGE_FILL[label])
    d.text((x + w / 2, y + 6.5), label, font=f, fill=(255, 255, 255), anchor="mm")
    return w


def paint_num_disc(d, cx, cy, num, colour):
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=colour)
    d.text((cx, cy), str(num), font=face(SANS_BLACK, 10), fill=(255, 255, 255), anchor="mm")


def paint_big_tag(d, x, y, text):
    f = face(SANS_BLACK, 11)
    w = int(measure(d, text, f)) + 12
    d.rectangle([x, y, x + w, y + 16], fill=(24, 24, 24))
    d.text((x + 6, y + 8), text, font=f, fill=(255, 255, 255), anchor="lm")
    return w


def rule(d, x0, x1, y, colour=LINE, width=1):
    d.line([(x0, y), (x1, y)], fill=colour, width=width)


# ---------------------------------------------------------------- hero art
def paint_kospi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    pts = [(x + 12, y + h - 18), (x + 60, y + 30), (x + 110, y + 44),
           (x + 160, y + 38), (x + 210, y + 58), (x + 260, y + 52),
           (x + w - 14, y + h - 12)]
    d.line(pts, fill=(232, 76, 56), width=3)
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
    d.text((x + 10, y + 8), "KOSPI \u22126.2%", font=face(SANS_BLACK, 15), fill=(255, 255, 255))
    d.text((x + 10, y + 26), "SK HYNIX \u221211.1%", font=face(SANS_BOLD, 10), fill=(255, 196, 120))
    d.text((x + 10, y + 40), "SAMSUNG \u22129.9%", font=face(SANS_BOLD, 10), fill=(255, 196, 120))
    d.text((x + w - 10, y + h - 16), "4,697.51", font=face(SANS_BLACK, 13),
           fill=(255, 220, 90), anchor="rb")


def paint_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy in [(x + 30, y + 14), (x + 90, y + 10), (x + 150, y + 20),
                   (x + 210, y + 12), (x + 270, y + 18), (x + 60, y + 66),
                   (x + 250, y + 70)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    # rocket body
    rx, ry = x + 52, y + 26
    d.polygon([(rx + 8, ry), (rx + 16, ry + 12), (rx + 16, ry + 40),
               (rx, ry + 40), (rx, ry + 12)], fill=(240, 240, 240))
    d.polygon([(rx - 6, ry + 40), (rx, ry + 28), (rx, ry + 44)], fill=RED_SOFT)
    d.polygon([(rx + 22, ry + 40), (rx + 16, ry + 28), (rx + 16, ry + 44)], fill=RED_SOFT)
    d.polygon([(rx + 4, ry + 40), (rx + 8, ry + 52), (rx + 12, ry + 40)], fill=(255, 176, 32))
    d.text((x + 10, y + 6), "00:18 LAUNCH", font=face(SANS_BLACK, 10), fill=(255, 255, 255))
    # station: core + panels
    sx0, sy0 = x + 130, y + 34
    d.rectangle([sx0, sy0, sx0 + 26, sy0 + 12], fill=(210, 220, 235))
    d.rectangle([sx0 - 46, sy0 + 2, sx0, sy0 + 10], fill=(52, 110, 178))
    d.rectangle([sx0 + 26, sy0 + 2, sx0 + 72, sy0 + 10], fill=(52, 110, 178))
    d.rectangle([sx0 + 72, sy0, sx0 + 96, sy0 + 12], fill=(210, 220, 235))
    d.ellipse([sx0 + 8, sy0 + 2, sx0 + 18, sy0 + 12], fill=(255, 196, 32))
    d.text((x + w - 10, y + h - 8), "03:56 DOCK", font=face(SANS_BLACK, 10),
           fill=(255, 255, 255), anchor="rb")


def paint_tariffs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=LINE)
    rows = [("CHINA", "20%", 1.00, RED), ("VIETNAM", "20%", 1.00, (214, 120, 30)),
            ("MALAYSIA", "19%", 0.95, (176, 128, 32)), ("INDIA", "17%", 0.85, (56, 142, 78)),
            ("EU", "15%", 0.75, (52, 110, 178)), ("JAPAN", "15%", 0.75, (52, 110, 178))]
    d.text((x + 8, y + 5), "PROPOSED RATE \u2014 14 ECONOMIES", font=face(SANS_BLACK, 11), fill=INK)
    by = y + 21
    for name, pct, frac, col in rows:
        d.text((x + 8, by), name, font=face(SANS_BOLD, 10), fill=INK)
        bw = int((w - 112) * frac)
        d.rectangle([x + 78, by + 1, x + 78 + bw, by + 9], fill=col)
        d.text((x + 82 + bw, by + 5), pct, font=face(SANS_BLACK, 10), fill=INK, anchor="lm")
        by += 11


HERO_PAINT = {"kospi": paint_kospi, "rocket": paint_rocket, "tariffs": paint_tariffs}


# ---------------------------------------------------------------- tile art
def paint_mini(d, kind, x, y, w, h):
    if kind == "refinery":
        d.rectangle([x, y, x + w, y + h], fill=(42, 44, 52))
        for bx in (x + 14, x + 46, x + 78):
            d.rectangle([bx, y + 12, bx + 18, y + h - 4], fill=(120, 122, 132))
            d.rectangle([bx + 6, y + 4, bx + 12, y + 12], fill=(120, 122, 132))
        for fx in (x + 20, x + 52, x + 84):
            d.polygon([(fx, y + 4), (fx + 5, y + 14), (fx + 10, y + 4)], fill=(255, 140, 32))
    elif kind == "tanker":
        d.rectangle([x, y, x + w, y + h], fill=(28, 68, 110))
        d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 5], fill=(24, 24, 24))
        for cx in (x + 22, x + 52, x + 82):
            d.rectangle([cx, y + 8, cx + 22, y + h - 14], fill=(255, 196, 32))
        d.polygon([(x + w - 26, y + 2), (x + w - 18, y + 12), (x + w - 10, y + 2)], fill=(255, 140, 32))
    elif kind == "smoke":
        d.rectangle([x, y, x + w, y + h], fill=(42, 44, 52))
        for bx in (x + 16, x + 52, x + 88):
            d.rectangle([bx, y + 16, bx + 20, y + h - 4], fill=(120, 122, 132))
        for cx, cy, r in [(x + 40, y + 8, 9), (x + 62, y + 5, 11), (x + 86, y + 9, 8)]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 148, 142))
    elif kind == "port":
        d.rectangle([x, y, x + w, y + h], fill=(206, 216, 224))
        d.line([(x + 20, y + h - 4), (x + 20, y + 6), (x + 60, y + 6)], fill=(60, 60, 60), width=3)
        d.line([(x + 60, y + 6), (x + 60, y + 16)], fill=(60, 60, 60), width=2)
        for cx, col in [(x + 70, (198, 90, 23)), (x + 92, (52, 110, 178)), (x + 114, (56, 142, 78))]:
            d.rectangle([cx, y + h - 14, cx + 18, y + h - 4], fill=col)
    elif kind == "pay":
        d.rectangle([x, y, x + w, y + h], fill=(34, 110, 62))
        for i, off in enumerate((0, 6, 12)):
            d.rectangle([x + 16 + off, y + 8 + off, x + 66 + off, y + 22 + off],
                        fill=(214, 228, 190), outline=(120, 140, 90))
    elif kind == "gauge":
        d.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
        d.arc([x + 26, y + 2, x + w - 26, y + h + 14], 180, 360, fill=(52, 110, 178), width=5)
        d.line([(x + w // 2, y + h - 8), (x + w - 30, y + 10)], fill=RED, width=3)
        d.ellipse([x + w // 2 - 4, y + h - 12, x + w // 2 + 4, y + h - 4], fill=INK)
    elif kind == "shaft":
        d.rectangle([x, y, x + w, y + h], fill=(122, 92, 60))
        d.rectangle([x + w // 2 - 12, y + 4, x + w // 2 + 12, y + h - 4], fill=(30, 26, 22))
        for ly in range(y + 8, y + h - 6, 6):
            d.line([(x + w // 2 - 12, ly), (x + w // 2 + 12, ly)], fill=(150, 130, 100), width=1)
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(52, 110, 178))
    elif kind == "bill":
        d.rectangle([x, y, x + w, y + h], fill=(214, 120, 30))
        d.rectangle([x + 18, y + 6, x + w - 18, y + h - 6], fill=(255, 255, 255))
        d.text((x + w // 2, y + 12), "\u00a32,166", font=face(SANS_BLACK, 13), fill=INK, anchor="ma")
        d.line([(x + 26, y + 22), (x + w - 26, y + 22)], fill=LINE, width=1)
        d.line([(x + 26, y + 27), (x + w - 40, y + 27)], fill=LINE, width=1)
    elif kind == "shield":
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        cx, cy = x + w // 2, y + h // 2
        d.polygon([(cx - 13, cy - 10), (cx + 13, cy - 10), (cx + 13, cy + 2),
                   (cx, cy + 13), (cx - 13, cy + 2)], outline=(255, 255, 255), width=2)
        d.line([(cx - 6, cy - 4), (cx + 6, cy + 6)], fill=RED_SOFT, width=3)
        d.line([(cx + 6, cy - 4), (cx - 6, cy + 6)], fill=RED_SOFT, width=3)
    elif kind == "ruins":
        d.rectangle([x, y, x + w, y + h], fill=(196, 192, 184))
        d.rectangle([x + 14, y + 10, x + 46, y + h - 4], fill=(120, 118, 112))
        d.polygon([(x + 52, y + 16), (x + 84, y + 8), (x + 92, y + h - 4),
                   (x + 60, y + h - 4)], fill=(96, 94, 90))
        d.line([(x + 96, y + 6), (x + 108, y + 18)], fill=RED, width=3)
        d.line([(x + 108, y + 6), (x + 96, y + 18)], fill=RED, width=3)
    elif kind == "firetruck":
        d.rectangle([x, y, x + w, y + h], fill=(42, 44, 52))
        d.rectangle([x + 12, y + 16, x + 62, y + h - 8], fill=(198, 36, 26))
        d.rectangle([x + 62, y + 20, x + 84, y + h - 8], fill=(120, 122, 132))
        for wx in (x + 22, x + 70):
            d.ellipse([wx, y + h - 10, wx + 10, y + h], fill=(20, 20, 20))
        for fx in (x + 92, x + 104):
            d.polygon([(fx, y + 6), (fx + 5, y + 16), (fx + 10, y + 6)], fill=(255, 140, 32))
    elif kind == "pylon":
        d.rectangle([x, y, x + w, y + h], fill=(42, 44, 52))
        d.line([(x + w // 2, y + 4), (x + w // 2 - 14, y + h - 4)], fill=(150, 148, 142), width=2)
        d.line([(x + w // 2, y + 4), (x + w // 2 + 14, y + h - 4)], fill=(150, 148, 142), width=2)
        d.line([(x + w // 2 - 20, y + 8), (x + w // 2 + 20, y + 8)], fill=(150, 148, 142), width=2)
        d.polygon([(x + w - 26, y + 4), (x + w - 34, y + 18), (x + w - 26, y + 18),
                   (x + w - 34, y + 32), (x + w - 16, y + 12), (x + w - 24, y + 12)],
                  fill=(255, 220, 60))
    elif kind == "gavel":
        d.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
        d.rectangle([x + 18, y + 8, x + 58, y + 18], fill=(122, 92, 60))
        d.rectangle([x + 62, y + 6, x + 72, y + 30], fill=(96, 72, 46))
        d.rectangle([x + 24, y + 26, x + 92, y + 30], fill=(150, 148, 142))
    elif kind == "store":
        d.rectangle([x, y, x + w, y + h], fill=(206, 216, 224))
        d.rectangle([x + 16, y + 10, x + w - 16, y + h - 4], fill=(255, 255, 255), outline=(120, 120, 120))
        for i, col in enumerate(((198, 36, 26), (255, 255, 255), (56, 142, 78), (255, 255, 255))):
            d.rectangle([x + 16 + i * 20, y + 10, x + 36 + i * 20, y + 18], fill=col)
        d.rectangle([x + w - 44, y + 6, x + w - 8, y + 16], fill=(34, 110, 62))
        d.text((x + w - 26, y + 11), "EXIT", font=face(SANS_BLACK, 8),
               fill=(255, 255, 255), anchor="mm")
    elif kind == "flask":
        d.rectangle([x, y, x + w, y + h], fill=(42, 44, 52))
        d.polygon([(x + 46, y + 6), (x + 54, y + 6), (x + 54, y + 16),
                   (x + 72, y + h - 6), (x + 28, y + h - 6), (x + 46, y + 16)],
                  fill=(150, 200, 220))
        d.rectangle([x + 30, y + h - 12, x + 70, y + h - 6], fill=(56, 142, 78))
        d.ellipse([x + 82, y + 8, x + 96, y + 22], fill=(255, 196, 32))
        d.ellipse([x + 88, y + 20, x + 100, y + 32], fill=(255, 140, 32))


# ---------------------------------------------------------------- world map
LAND_POLYS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-80, 73),
     (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35), (-80, 32), (-85, 30),
     (-90, 21), (-95, 19), (-100, 16), (-105, 20), (-110, 23), (-115, 30),
     (-120, 34), (-125, 40), (-130, 48), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10), (-35, -20),
     (-40, -30), (-50, -35), (-60, -40), (-65, -50), (-70, -55), (-75, -45),
     (-75, -30), (-70, -20), (-75, -15), (-80, -5)],
    [(-10, 36), (-5, 44), (0, 48), (5, 53), (10, 57), (15, 55), (20, 60),
     (25, 65), (30, 70), (35, 68), (30, 60), (25, 55), (20, 50), (15, 45),
     (10, 40), (5, 38), (0, 36), (-5, 36)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 20), (45, 11), (50, 10), (48, 0), (40, -10), (35, -20), (30, -30),
     (25, -35), (18, -35), (12, -20), (10, -5), (5, 5), (-5, 5), (-12, 8)],
    [(30, 70), (40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 66),
     (170, 66), (175, 62), (170, 60), (162, 58), (158, 52), (150, 60), (142, 55),
     (140, 45), (135, 35), (130, 33), (127, 35), (122, 38), (120, 30), (115, 22),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 15),
     (75, 10), (70, 20), (65, 25), (60, 25), (55, 28), (50, 30), (45, 30),
     (40, 35), (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41), (142, 44),
     (144, 44), (141, 40), (139, 37), (136, 35), (133, 34)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -5), (135, -4), (140, -8), (138, -7), (130, -3), (120, -2), (110, 0), (100, 3)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25), (44, -25), (43, -20)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (178, -37), (174, -41), (170, -44)],
]


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    py = y0 + (85.0 - lat) / 145.0 * (y1 - y0)
    return px, py


def paint_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    for gx in range(int(x0), int(x1) + 1, 32):
        d.line([(gx, y0), (gx, y1)], fill=(226, 233, 238), width=1)
    for gy in range(int(y0), int(y1) + 1, 24):
        d.line([(x0, gy), (x1, gy)], fill=(226, 233, 238), width=1)
    for poly in LAND_POLYS:
        pts = [project(lon, lat, box) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
    for num, lon, lat, dx, dy in PINS:
        px, py = project(lon, lat, box)
        px += dx
        py += dy
        col = REGION_FILL[PIN_REGION[num]]
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col, outline=(255, 255, 255))
        d.text((px, py), str(num), font=face(SANS_BLACK, 8), fill=(255, 255, 255), anchor="mm")


# ---------------------------------------------------------------- composition
def fit_block(d, text, path, size, max_w, max_lines, floor=8):
    """Wrap text, shrinking the font until it fits in max_lines."""
    while size > floor:
        f = face(path, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 0.5
    f = face(path, floor)
    return f, wrap(d, text, f, max_w)[:max_lines]


def draw_top_strip(d):
    d.rectangle([0, 0, CANVAS_W, 20], fill=NAVY)
    d.text((8, 10), "THE WORLD IN ONE DAY", font=face(SANS_BLACK, 11),
           fill=(255, 255, 255), anchor="lm")
    d.text((CANVAS_W // 2, 10), "DAY 329 OF 2026", font=face(SANS_BLACK, 11),
           fill=(255, 120, 100), anchor="mm")
    d.text((CANVAS_W - 8, 10), "ALL TIMES UTC \u00b7 RANKED BY CONSEQUENCE",
           font=face(SANS_BOLD, 10), fill=(255, 255, 255), anchor="rm")


def draw_masthead(d):
    f = shrink_to(d, "Wednesday 25 November 2026", SERIF, 54, CANVAS_W - 40)
    d.text((CANVAS_W // 2, 52), "Wednesday 25 November 2026", font=f, fill=INK, anchor="mm")


def draw_subline(d, total, n_regions, n_fields):
    rule(d, 8, CANVAS_W - 8, 80, RED, 2)
    text = ("%d STORIES \u00b7 %d REGIONS \u00b7 %d FIELDS \u00b7 EVERY ONE DATED "
            "WEDNESDAY 25 NOVEMBER 2026" % (total, n_regions, n_fields))
    f = shrink_to(d, text, SANS_BLACK, 13, CANVAS_W - 30)
    d.text((CANVAS_W // 2, 89), text, font=f, fill=RED, anchor="mm")


def draw_fields_bar(d, field_counts):
    items = sorted(field_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    n_fields = len(items)
    head = "%d FIELDS \u2014 " % n_fields
    rest = " \u00b7 ".join("%s %d" % (name, c) for name, c in items)
    f_head = face(SANS_BLACK, 11)
    f_rest = face(SANS, 11)
    total_w = measure(d, head, f_head) + measure(d, rest, f_rest)
    size = 11
    while total_w > CANVAS_W - 24 and size > 8:
        size -= 0.5
        f_head, f_rest = face(SANS_BLACK, size), face(SANS, size)
        total_w = measure(d, head, f_head) + measure(d, rest, f_rest)
    x = (CANVAS_W - total_w) / 2
    d.text((x, 105), head, font=f_head, fill=INK, anchor="lm")
    d.text((x + measure(d, head, f_head), 105), rest, font=f_rest, fill=INK, anchor="lm")
    rule(d, 8, CANVAS_W - 8, 113, LINE)


def draw_timeline(d):
    d.rectangle([8, 121, 108, 147], fill=NAVY)
    d.text((58, 134), "THE DAY IN UTC", font=face(SANS_BLACK, 10),
           fill=(255, 255, 255), anchor="mm")
    col_w = (CANVAS_W - 8 - 116) / len(DAY_TIMES)
    for i, (t, label) in enumerate(DAY_TIMES):
        cx = 116 + col_w * i + col_w / 2
        d.text((cx, 126), t, font=face(SANS_BLACK, 14), fill=RED, anchor="ma")
        d.text((cx, 143), label, font=face(SANS, 9), fill=MUTED, anchor="ma")
        if i:
            d.line([(116 + col_w * i, 120), (116 + col_w * i, 150)], fill=LINE, width=1)
    rule(d, 8, CANVAS_W - 8, 159, LINE)


def draw_kpi_strip(d):
    n = len(KPI_CARDS)
    gap, margin = 4, 8
    bw = (CANVAS_W - 2 * margin - (n - 1) * gap) / n
    for i, (big, label) in enumerate(KPI_CARDS):
        x = margin + i * (bw + gap)
        d.rectangle([x, 163, x + bw, 207], fill=(255, 255, 255), outline=LINE)
        f = shrink_to(d, big, SANS_BLACK, 23, bw - 10)
        d.text((x + bw / 2, 181), big, font=f, fill=INK, anchor="mm")
        lf = shrink_to(d, label, SANS, 9, bw - 8)
        d.text((x + bw / 2, 199), label, font=lf, fill=MUTED, anchor="mm")


def draw_region_bar(d, region_counts):
    order = ["Europe", "Middle East", "Asia", "Africa", "Americas", "Oceania", "Global"]
    d.text((8, 219), "STORIES BY REGION", font=face(SANS_BLACK, 10), fill=INK, anchor="lm")
    x = 150
    for name in order:
        if name not in region_counts:
            continue
        col = REGION_FILL[name]
        d.rectangle([x, 214, x + 9, 223], fill=col)
        text = "%s %d" % (name.upper(), region_counts[name])
        d.text((x + 13, 219), text, font=face(SANS_BOLD, 11), fill=INK, anchor="lm")
        x += 13 + int(measure(d, text, face(SANS_BOLD, 11))) + 16
    rule(d, 8, CANVAS_W - 8, 227, LINE)


def draw_hero(d, hero, x, y, w):
    HERO_PAINT[hero["art"]](d, x, y, w, 90)
    hy = y + 90
    paint_num_disc(d, x + 8, hy + 8, hero["num"], RED)
    place = hero["place"]
    d.text((x + 20, hy + 8), place, font=face(SANS_BLACK, 10), fill=INK, anchor="lm")
    bw = paint_badge(d, x + w - 62, hy + 2, hero["badge"])
    d.text((x + w - 62 + bw + 4, hy + 8), "", font=face(SANS, 9), fill=INK, anchor="lm")
    f, lines = fit_block(d, hero["head"], SERIF, 18, w, 2)
    ty = hy + 20
    for ln in lines:
        d.text((x, ty), ln, font=f, fill=INK, anchor="la")
        ty += 20
    body_f, body_lines = fit_block(d, hero["body"], SANS, 10, w, 3)
    for ln in body_lines:
        d.text((x, ty), ln, font=body_f, fill=INK, anchor="la")
        ty += 12
    ty += 2
    label = "WHY IT MATTERS  "
    lab_f = face(SANS_BLACK, 10)
    lab_w = measure(d, label, lab_f)
    why_lines = wrap(d, hero["why"], face(SANS, 10), w - lab_w)
    for li, ln in enumerate(why_lines[:2]):
        if li == 0:
            d.text((x, ty), label, font=lab_f, fill=RED, anchor="la")
            d.text((x + lab_w, ty), ln, font=face(SANS, 10), fill=INK, anchor="la")
        else:
            d.text((x, ty), ln, font=face(SANS, 10), fill=INK, anchor="la")
        ty += 12
    d.text((x, y + 210), hero["src"], font=face(SANS, 8), fill=MUTED, anchor="la")


def draw_tile(d, tile, x, y, w, h):
    paint_mini(d, tile["art"], x, y, w, 32)
    paint_big_tag(d, x + 3, y + 32 - 17, tile["big"])
    hy = y + 34
    paint_num_disc(d, x + 7, hy + 6, tile["num"], RED)
    d.text((x + 17, hy + 6), tile["place"], font=face(SANS_BOLD, 9), fill=INK, anchor="lm")
    blab = tile["badge"]
    bf = face(SANS_BLACK, 8)
    bw = int(measure(d, blab, bf)) + 8
    d.rounded_rectangle([x + w - bw - 2, hy, x + w - 2, hy + 12], radius=2,
                        fill=BADGE_FILL[blab])
    d.text((x + w - bw / 2 - 2, hy + 6), blab, font=bf, fill=(255, 255, 255), anchor="mm")
    f, lines = fit_block(d, tile["head"], SERIF, 12.5, w, 2)
    ty = hy + 16
    for ln in lines:
        d.text((x, ty), ln, font=f, fill=INK, anchor="la")
        ty += 13
    full = tile["body"] + " (" + tile["src"] + ")"
    bf2, blines = fit_block(d, full, SANS, 9, w, 3, floor=8)
    for ln in blines:
        d.text((x, ty), ln, font=bf2, fill=(60, 60, 60), anchor="la")
        ty += 10


def draw_map_panel(d, y0, y1):
    d.text((8, y0 + 2), "WHERE IT HAPPENED \u2014 PIN NUMBERS MATCH THE STORIES, "
                        "PIN COLOUR IS THE REGION",
           font=face(SANS_BLACK, 10), fill=INK, anchor="la")
    paint_map(d, (8, y0 + 16, 636, y1 - 12))
    lx = 8
    for name in ["Europe", "Middle East", "Asia", "Africa", "Americas", "Oceania", "Global"]:
        d.ellipse([lx, y1 - 8, lx + 7, y1 - 1], fill=REGION_FILL[name])
        d.text((lx + 10, y1 - 4), name.upper(), font=face(SANS_BOLD, 8), fill=INK, anchor="lm")
        lx += 10 + int(measure(d, name.upper(), face(SANS_BOLD, 8))) + 12


def draw_date_check(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(255, 252, 246), outline=RED, width=2)
    d.text((x0 + 8, y0 + 4), "DATE CHECK \u2014 what we left out, and why",
           font=face(SANS_BLACK, 11), fill=RED, anchor="la")
    lines = [
        ("LEFT OUT \u2014 OTHER DAYS", True),
        ("MON 23 NOV   Huang back at Nvidia", False),
        ("SUN 22 NOV   COP31 ends with no deal", False),
        ("TUE 24 NOV   Riyadh PIF tower strike, 11 injured", False),
        ("TUE 24 NOV   Zaporizhzhia night strike", False),
        ("TUE 24 NOV   Huawei convicted in Brooklyn", False),
        ("TUE 24 NOV   CAS gave Senegal AFCON title back", False),
        ("23\u201324 NOV   3 Hormuz tankers hit mines (2 on Wed are new)", False),
        ("NOT YET \u2014 THU 26 NOV", True),
        ("US Thanksgiving \u00b7 Special European Council", False),
    ]
    ty = y0 + 20
    for text, bold in lines:
        f = face(SANS_BLACK if bold else SANS, 9)
        d.text((x0 + 8, ty), text, font=f, fill=INK if not bold else RED, anchor="la")
        ty += 9.4


def draw_also_on(d, y0, y1):
    d.text((8, y0), "ALSO ON WEDNESDAY 25 NOVEMBER",
           font=face(SANS_BLACK, 12), fill=INK, anchor="la")
    d.text((330, y0), "\u2014 %d MORE STORIES" % len(BRIEFS),
           font=face(SANS_BLACK, 12), fill=RED, anchor="la")
    cols = [BRIEFS[i:i + 12] for i in (0, 12, 24)]
    col_x = [8, 350, 692]
    col_w = 324
    num_f = face(SANS_BLACK, 9)
    txt_f = face(SANS, 9)
    src_f = face(SANS, 9)
    for cx, items in zip(col_x, cols):
        ty = y0 + 16
        for num, text, src, _region, _field in items:
            label = "%d" % num
            d.text((cx, ty), label, font=num_f, fill=RED, anchor="la")
            nx = cx + int(measure(d, label, num_f)) + 5
            tail = " (" + src + ")"
            avail = col_w - (nx - cx)
            shown = text
            while measure(d, shown + tail, txt_f) > avail and len(shown) > 12:
                shown = shown[:-1].rstrip(".,;: ")
            if shown != text:
                shown = shown.rstrip(".,;: ") + "\u2026"
            d.text((nx, ty), shown, font=txt_f, fill=INK, anchor="la")
            d.text((nx + measure(d, shown, txt_f), ty), tail, font=src_f, fill=MUTED, anchor="la")
            ty += 9.2


def draw_footer(d):
    rule(d, 8, CANVAS_W - 8, 993, LINE)
    d.text((8, 999), "HOW WE CHECKED \u2014 REPORTED carried by the day's wires \u00b7 "
                     "OFFICIAL an authority's own word \u00b7 CLAIM one side's account \u00b7 "
                     "ONGOING still unfolding",
           font=face(SANS, 9), fill=INK, anchor="la")
    d.text((8, 1011), "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Xinhua \u00b7 Yonhap \u00b7 "
                      "Al Jazeera \u00b7 ABS \u00b7 Ofgem \u00b7 Guardian \u00b7 Kyiv Independent "
                      "\u00b7 BBC \u00b7 IRNA \u00b7 SPA \u00b7 CMSA \u2014 Every story happened or "
                      "was first reported on Wednesday 25 November 2026 (UTC).",
           font=face(SANS, 8), fill=MUTED, anchor="la")


def compose():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    d = ImageDraw.Draw(img)
    all_items = HEROES + TILES + [
        dict(num=n, region=r, field=f) for n, _t, _s, r, f in BRIEFS
    ]
    total = len(all_items)
    region_counts = Counter(it["region"] for it in all_items)
    field_counts = Counter(it["field"] for it in all_items)
    assert total == 53, total
    assert sum(region_counts.values()) == 53
    assert sum(field_counts.values()) == 53

    draw_top_strip(d)
    draw_masthead(d)
    draw_subline(d, total, len(region_counts), len(field_counts))
    draw_fields_bar(d, field_counts)
    draw_timeline(d)
    draw_kpi_strip(d)
    draw_region_bar(d, region_counts)

    hero_w = (CANVAS_W - 16 - 12) // 3
    for i, hero in enumerate(HEROES):
        draw_hero(d, hero, 8 + i * (hero_w + 6), 227, hero_w)

    tile_w = (CANVAS_W - 12 - 4 * 6) // 5
    tile_h = 100
    for row in range(3):
        for col in range(5):
            tile = TILES[row * 5 + col]
            draw_tile(d, tile, 6 + col * (tile_w + 6), 447 + row * tile_h, tile_w, tile_h)

    draw_map_panel(d, 747, 863)
    draw_date_check(d, 644, 747, 1016, 863)
    draw_also_on(d, 867, 993)
    draw_footer(d)
    return img


def main():
    img = compose()
    out = os.path.join(os.path.dirname(BASE), "entry.png")
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s (%dx%d, %d bytes)" % (out, img.width, img.height, size))


if __name__ == "__main__":
    main()
