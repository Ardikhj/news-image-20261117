#!/usr/bin/env python3
"""Draw the news-image-20261117 entry: a 1024x1024 editorial infographic
summing up world news of Tuesday 17 November 2026.

Six stories, all verified against reporting published on 17 Nov 2026
(Reuters, AP via MTPR/Bloomberg, Al Jazeera, Outlook India, Just Security,
Wall Street Journal via Reuters Trading Day). No story is invented; every
headline below traces to one of those reports. Run: python3 draw_entry.py
Writes entry.png next to this file. Fully deterministic: fixed layout,
fixed fonts, no timestamps, no randomness.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (14, 42, 71)
NAVY_DARK = (9, 30, 52)
PAPER = (246, 241, 231)
INK = (20, 32, 46)
MUTED = (90, 107, 124)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
BORDER = (214, 205, 188)

FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FI = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap by pixel width."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rrect(d, box, radius, **kw):
    d.rounded_rectangle(box, radius=radius, **kw)


# --- icons: small geometric drawings, one per story -----------------------
def icon_bridge(d, x, y, s, c):
    # deck in two halves with a collapsed gap, arch above, water below
    d.line([(x + 4, y + s * 0.52), (x + s * 0.42, y + s * 0.52)], fill=c, width=5)
    d.line([(x + s * 0.58, y + s * 0.52), (x + s - 4, y + s * 0.52)], fill=c, width=5)
    d.arc([x + 6, y + 6, x + s - 6, y + s * 0.72], start=180, end=360, fill=c, width=5)
    d.line([(x + s * 0.46, y + s * 0.52), (x + s * 0.50, y + s * 0.68)], fill=c, width=4)
    for i, yy in enumerate((0.72, 0.82, 0.92)):
        d.line([(x + 10 + i * 6, y + s * yy), (x + s - 10 - i * 6, y + s * yy)],
               fill=c, width=3)


def icon_radar(d, x, y, s, c):
    cx, cy, r = x + s // 2, y + s // 2 + 4, s // 2 - 8
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=4)
    d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
              outline=c, width=3)
    d.line([(cx, cy), (cx + r - 4, cy - r + 10)], fill=c, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=c)
    # drone above the radar
    dx, dy = x + s - 22, y + 8
    d.ellipse([dx - 8, dy - 3, dx - 1, dy + 3], outline=c, width=3)
    d.ellipse([dx + 1, dy - 3, dx + 8, dy + 3], outline=c, width=3)
    d.rectangle([dx - 6, dy + 3, dx + 6, dy + 9], fill=c)


def icon_summit(d, x, y, s, c):
    # globe + three flag poles
    cx, cy, r = x + s // 2, y + s - 22, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=4)
    d.arc([cx - r, cy - r, cx + r, cy + r], start=270, end=90, fill=c, width=3)
    d.line([(cx, cy - r), (cx, cy + r)], fill=c, width=3)
    cols = [(31, 111, 139), (180, 69, 45), (46, 125, 91)]
    for i, col in enumerate(cols):
        px = x + 12 + i * (s - 24) // 2
        d.line([(px, y + 10), (px, y + s - 30)], fill=c, width=4)
        d.polygon([(px, y + 10), (px + 20, y + 17), (px, y + 24)], fill=col)


def icon_chip(d, x, y, s, c):
    m = 14
    d.rounded_rectangle([x + m, y + m, x + s - m, y + s - m], radius=8,
                        outline=c, width=5)
    d.rounded_rectangle([x + s // 2 - 11, y + s // 2 - 11,
                         x + s // 2 + 11, y + s // 2 + 11], radius=3,
                        fill=c)
    for i in range(3):
        off = m + 10 + i * 16
        d.line([(x + off, y + 4), (x + off, y + m)], fill=c, width=4)
        d.line([(x + off, y + s - m), (x + off, y + s - 4)], fill=c, width=4)
        d.line([(x + 4, y + off), (x + m, y + off)], fill=c, width=4)
        d.line([(x + s - m, y + off), (x + s - 4, y + off)], fill=c, width=4)
    # rising chart arrow across the chip
    d.line([(x + m + 2, y + s - m - 8), (x + s // 2, y + s // 2 + 4),
            (x + s - m - 2, y + m + 6)], fill=(46, 125, 91), width=5)
    d.polygon([(x + s - m - 2, y + m + 6), (x + s - m - 14, y + m + 8),
               (x + s - m - 4, y + m + 18)], fill=(46, 125, 91))


def icon_parliament(d, x, y, s, c):
    d.polygon([(x + 8, y + 30), (x + s // 2, y + 8), (x + s - 8, y + 30)],
              fill=c)
    for i in range(4):
        cx = x + 16 + i * (s - 32) // 3
        d.rectangle([cx - 4, y + 36, cx + 4, y + s - 26], fill=c)
    d.rectangle([x + 8, y + s - 26, x + s - 8, y + s - 18], fill=c)
    d.rectangle([x + 4, y + s - 16, x + s - 4, y + s - 8], fill=c)


def icon_march(d, x, y, s, c):
    # three marchers + placards
    for i, px in enumerate((x + 16, x + s // 2, x + s - 16)):
        d.ellipse([px - 8, y + 14, px + 8, y + 30], fill=c)
        d.rectangle([px - 7, y + 34, px + 7, y + s - 16], fill=c)
    d.rectangle([x + 6, y + 44, x + 34, y + 60], outline=c, width=3)
    d.line([(x + 20, y + 60), (x + 20, y + s - 16)], fill=c, width=3)


STORIES = [
    dict(tag="UKRAINE · WAR", color=(31, 111, 139), icon=icon_bridge,
         head="Ukraine knocks out Crimea bridge road span",
         body=("Drones and missiles collapse an arch and road span of the "
               "19-km Kerch Bridge; road traffic halted, two killed. "
               "Russia hits Kyiv's bridges in reply."),
         src="Reuters · AP"),
    dict(tag="MIDDLE EAST · GULF", color=(180, 69, 45), icon=icon_radar,
         head="Iran fires drones at US radar base in Bahrain",
         body=("Tehran says its drones targeted the US radar at Sheikh Isa "
               "base; Bahrain says the attack was intercepted, no "
               "casualties. Tankers hit mines near Hormuz."),
         src="Reuters · Just Security"),
    dict(tag="ASIA · DIPLOMACY", color=(46, 125, 91), icon=icon_summit,
         head="Trump lands in Manila; Xi–Trump–Putin summit set",
         body=("Trump opens his Asia trip at the Quad summit in Manila. "
               "China confirms a first three-way meeting with Xi and "
               "Putin in Shenzhen on Thursday."),
         src="Reuters · Outlook India"),
    dict(tag="MARKETS · TECH", color=(108, 74, 176), icon=icon_chip,
         head="Nvidia beats on $115.8bn sales after CEO exit",
         body=("First results since Jensen Huang resigned: revenue up 103% "
               "and Q4 guided to $130bn. Stocks fell ahead of the report; "
               "a reported SEC probe hangs over disclosures."),
         src="Reuters · Wall Street Journal"),
    dict(tag="ISRAEL · POLITICS", color=(140, 109, 31), icon=icon_parliament,
         head="Knesset ousts Netanyahu ally as speaker",
         body=("Matan Kahana, of rival Gadi Eisenkot's bloc, wins 66–52, "
               "replacing Likud's Amir Ohana — a first step to roll back "
               "Netanyahu's agenda after a deadlocked vote."),
         src="Reuters"),
    dict(tag="EUROPE · LABOUR", color=(192, 57, 43), icon=icon_march,
         head="France strike draws 146,000 onto streets",
         body=("Public-sector workers march for pay rises in a third day "
               "of stoppages since September; turnout sharply down from "
               "575,000 on 5 November."),
         src="Reuters"),
]

TICKER = ("ALSO TODAY:  Japan scrambles jets over Russian planes  •  "
          "Canada–China tariff cuts  •  Third US carrier in Gulf")


def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 150], fill=NAVY)
    d.rectangle([0, 150, W, 154], fill=GOLD)
    f_kick = font(FB, 20)
    f_date = font(FB, 47)
    f_sub = font(FR, 21)
    d.text((24, 18), "THE WORLD IN ONE DAY  —  WORLD NEWS", font=f_kick,
           fill=GOLD)
    d.text((24, 46), "TUESDAY 17 NOVEMBER 2026", font=f_date, fill=WHITE)
    d.text((24, 108), "Six stories that defined the day — from Kyiv to Shenzhen",
           font=f_sub, fill=(205, 216, 228))

    # ---- story grid: 2 columns x 3 rows --------------------------------
    gx, gy, gap = 22, 168, 14
    pw, ph = 480, 240
    f_tag = font(FB, 15)
    f_head = font(FB, 25)
    f_body = font(FR, 19)
    f_src = font(FI, 15)
    for i, st in enumerate(STORIES):
        x0 = gx + (i % 2) * (pw + gap)
        y0 = gy + (i // 2) * (ph + gap)
        c = st["color"]
        rrect(d, [x0, y0, x0 + pw, y0 + ph], radius=10, fill=PANEL,
              outline=BORDER, width=2)
        d.rectangle([x0, y0 + 10, x0 + 7, y0 + ph - 10], fill=c)
        # tag pill
        tag = st["tag"]
        tw = d.textlength(tag, font=f_tag)
        rrect(d, [x0 + 18, y0 + 14, x0 + 30 + tw, y0 + 40], radius=13,
              fill=c)
        d.text((x0 + 24, y0 + 18), tag, font=f_tag, fill=WHITE)
        # icon box, top right
        ix, iy, isize = x0 + pw - 96, y0 + 12, 84
        tint = tuple(min(255, v + 205) for v in c)
        rrect(d, [ix, iy, ix + isize, iy + isize], radius=10, fill=tint)
        st["icon"](d, ix + 6, iy + 6, isize - 12, c)
        # headline (width stops short of the icon box)
        lines = wrap(d, st["head"], f_head, pw - 18 - 96 - 14)[:3]
        yy = y0 + 52
        for ln in lines:
            d.text((x0 + 18, yy), ln, font=f_head, fill=INK)
            yy += 30
        # body, full width under the icon
        blines = wrap(d, st["body"], f_body, pw - 36)[:3]
        yy = y0 + 146
        for ln in blines:
            d.text((x0 + 18, yy), ln, font=f_body, fill=(43, 58, 74))
            yy += 24
        d.text((x0 + 18, y0 + ph - 26), "Source: " + st["src"],
               font=f_src, fill=MUTED)

    # ---- ticker + footer ------------------------------------------------
    ty = 922
    d.rectangle([0, ty, W, ty + 52], fill=NAVY)
    f_tick = font(FR, 19)
    d.text((24, ty + 14), TICKER, font=f_tick, fill=WHITE)
    f_foot = font(FR, 15)
    foot = ("Sources: Reuters, AP, Bloomberg, Al Jazeera, Just Security — "
            "all events of Tuesday 17 November 2026")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 986), foot, font=f_foot, fill=MUTED)
    return img


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    draw().save(out, format="PNG", optimize=True)
    print("wrote", out)
