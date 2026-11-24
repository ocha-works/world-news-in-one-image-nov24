#!/usr/bin/env python3
"""Draw the front page of 24 November 2026's world news as one image.

Everything is drawn with Pillow primitives: no photographs, no copied
artwork, no text rendered from any outside image. Run it to produce
entry.png (1024 x 1024).
"""

import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (18, 18, 20)
PAPER = (250, 247, 238)
NAVY = (16, 32, 64)
RED = (178, 34, 34)
GREY = (90, 90, 92)
SKY = (168, 200, 224)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, xy, text, fnt, width, fill=INK, leading=None):
    """Draw wrapped text; return the y just below the last line."""
    x, y = xy
    leading = leading or int(fnt.size * 1.30)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, xy, text, fill=RED):
    draw.text(xy, text, font=font(SANS_B, 17), fill=fill)
    return xy[1] + 24


def rule(draw, x0, y, x1, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_korea_panel(draw, x0, y0, x1, y1):
    """Stylised East Sea scene: Korea's east coast, Ulleung Island, jets."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY, outline=INK, width=2)
    # Korean east coastline (left edge landmass)
    land = [(x0, y0), (x0 + 150, y0), (x0 + 120, y0 + 90),
            (x0 + 150, y0 + 170), (x0 + 110, y0 + 260),
            (x0 + 130, y1), (x0, y1)]
    draw.polygon(land, fill=(196, 178, 140), outline=INK)
    draw.text((x0 + 14, y0 + 200), "KOREA", font=font(SANS_B, 20),
              fill=(70, 60, 40))
    # Ulleung Island
    ix, iy = x0 + 235, y0 + 120
    draw.ellipse([ix - 26, iy - 16, ix + 26, iy + 16], fill=(120, 150, 90),
                 outline=INK, width=2)
    draw.text((ix - 34, iy + 22), "ULLEUNG", font=font(SANS_B, 16), fill=INK)
    # air-defence zone ring (dashed ellipse)
    r = 95
    for a in range(0, 360, 12):
        x_a = ix + r * math.cos(math.radians(a))
        y_a = iy + r * math.sin(math.radians(a)) * 0.75
        x_b = ix + r * math.cos(math.radians(a + 6))
        y_b = iy + r * math.sin(math.radians(a + 6)) * 0.75
        draw.line([(x_a, y_a), (x_b, y_b)], fill=RED, width=3)
    draw.text((ix - 68, y0 + 10), "AIR DEFENCE ZONE",
              font=font(SANS_B, 15), fill=RED)
    # jets: simple delta silhouettes pointing right
    for jx, jy in [(x0 + 250, y0 + 52), (x0 + 300, y0 + 84)]:
        draw.polygon([(jx, jy), (jx + 34, jy + 9), (jx, jy + 15),
                      (jx + 5, jy + 7)], fill=(40, 44, 52))
        draw.polygon([(jx + 8, jy + 2), (jx + 14, jy + 7), (jx + 6, jy + 7)],
                     fill=(40, 44, 52))
    # alert banner inside panel
    draw.rectangle([x0 + 8, y1 - 44, x1 - 8, y1 - 8], fill=RED)
    draw.text((x0 + 20, y1 - 38), "ALERT SENT — THEN CORRECTED",
              font=font(SANS_B, 18), fill=(255, 255, 255))


def draw_gaza_panel(draw, x0, y0, x1, y1):
    """Stylised skyline at dusk with a small smoke column."""
    pw, ph = x1 - x0, y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(238, 214, 170), outline=INK,
                   width=2)
    heights = [int(ph * f) for f in (0.42, 0.62, 0.50, 0.72, 0.55, 0.66)]
    bx = x0 + 8
    for hgt in heights:
        bw = (pw - 16) // 6
        draw.rectangle([bx, y1 - hgt - 6, bx + bw - 4, y1 - 6],
                       fill=(120, 100, 84), outline=INK, width=1)
        for wy in range(y1 - hgt + 4, y1 - 12, 14):
            draw.rectangle([bx + 3, wy, bx + 8, wy + 5],
                           fill=(250, 230, 150))
        bx += bw
    sx = x0 + pw * 0.68
    for i, r in enumerate([9, 12, 15]):
        yy = y0 + 14 + i * 12
        shade = 150 - i * 12
        draw.ellipse([sx - r, yy - r // 2, sx + r, yy + r // 2],
                     fill=(shade, shade, shade))
    draw.text((x0 + 6, y0 + 4), "GAZA", font=font(SANS_B, 14), fill=INK)


def draw_talks_panel(draw, x0, y0, x1, y1):
    """Four seats around a table; Europe's seat is unconfirmed."""
    draw.rectangle([x0, y0, x1, y1], fill=(214, 226, 238), outline=INK,
                   width=2)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 6
    draw.ellipse([cx - 30, cy - 18, cx + 30, cy + 18], fill=(150, 110, 70),
                 outline=INK, width=2)
    seats = [(cx - 52, cy - 30, "UKR", False),
             (cx + 24, cy - 30, "RUS", False),
             (cx - 52, cy + 16, "USA", False),
             (cx + 24, cy + 16, "EU?", True)]
    for sx, sy, label, empty in seats:
        col = (200, 200, 200) if empty else (60, 90, 130)
        draw.rectangle([sx, sy, sx + 28, sy + 16], fill=col, outline=INK,
                       width=1)
        draw.text((sx + 2, sy + 2), label, font=font(SANS_B, 10),
                  fill=INK if empty else (255, 255, 255))
    draw.text((x0 + 6, y0 + 4), "NO DATE SET", font=font(SANS_B, 13),
              fill=RED)


def draw_oil_panel(draw, x0, y0, x1, y1):
    """Oil derrick."""
    draw.rectangle([x0, y0, x1, y1], fill=(226, 214, 190), outline=INK,
                   width=2)
    cx = x0 + (x1 - x0) // 2
    top = y0 + 22
    draw.polygon([(cx - 30, y1 - 8), (cx + 30, y1 - 8), (cx + 8, top),
                  (cx - 8, top)], outline=INK, width=2)
    draw.line([(cx - 22, y1 - 34), (cx + 22, y1 - 34)], fill=INK, width=2)
    draw.line([(cx - 13, y1 - 58), (cx + 13, y1 - 58)], fill=INK, width=2)
    draw.text((x0 + 6, y0 + 4), "OIL", font=font(SANS_B, 14), fill=INK)


def draw_return_panel(draw, x0, y0, x1, y1):
    """A jet on a runway, heading home."""
    draw.rectangle([x0, y0, x1, y1], fill=(210, 226, 210), outline=INK,
                   width=2)
    draw.rectangle([x0, y1 - 22, x1, y1 - 14], fill=(80, 80, 84))
    for dx in range(8, x1 - x0 - 8, 18):
        draw.line([(x0 + dx, y1 - 18), (x0 + dx + 8, y1 - 18)],
                  fill=(255, 255, 255), width=2)
    px, py = x0 + 12, y0 + 46
    draw.polygon([(px, py), (px + 88, py - 4), (px + 98, py + 1),
                  (px + 88, py + 6), (px + 36, py + 8),
                  (px + 28, py + 16), (px + 20, py + 8),
                  (px - 4, py + 9), (px - 8, py + 4)],
                 fill=(50, 60, 80))
    draw.text((x0 + 6, y0 + 4), "16 DECEMBER", font=font(SANS_B, 14),
              fill=INK)


PANELS = {
    "gaza": draw_gaza_panel,
    "talks": draw_talks_panel,
    "oil": draw_oil_panel,
    "return": draw_return_panel,
}


def story_cell(draw, x0, y0, x1, y1, kick, head, body, panel):
    """One secondary story: kicker, headline, body, small drawn panel."""
    y = kicker(draw, (x0, y0), kick)
    text_w = (x1 - x0) - 130  # leave room for the panel on the right
    y = para(draw, (x0, y + 2), head, font(SERIF_B, 26), text_w, leading=30)
    PANELS[panel](draw, x1 - 122, y0 + 4, x1, y0 + 100)
    y = max(y + 4, y0 + 104)  # body starts below the panel
    y = para(draw, (x0, y), body, font(SERIF, 19), x1 - x0,
             leading=24)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.text((512, 10), "THE WORLD IN ONE PAGE",
           font=font(SERIF_B, 52), fill=(255, 255, 255), anchor="ma")
    d.text((512, 70), "TUESDAY 24 NOVEMBER 2026",
           font=font(SANS_B, 30), fill=(255, 214, 90), anchor="ma")
    d.line([(0, 118), (W, 118)], fill=RED, width=6)

    # ---- lead story: Korea ----
    y = 132
    kicker(d, (40, y), "KOREA  •  AIR DEFENCE SCARE")
    y = para(d, (40, 158), "Russian jets spark false alarm off Korea",
             font(SERIF_B, 42), 560, leading=46)
    y = para(d, (40, y + 8),
             "Several Russian warplanes entered South Korea's air "
             "defence zone near Ulleung Island early on Tuesday. "
             "Seoul scrambled jets; the planes left without entering "
             "South Korean airspace.",
             font(SERIF, 20), 560, leading=26)
    y = para(d, (40, y + 6),
             "An alert told islanders a Russian aircraft had violated "
             "their airspace. A second message wrongly named North "
             "Korean aircraft — a training phrase sent by mistake.",
             font(SERIF, 20), 560, leading=26)
    assert y <= 474, f"lead text overflows: y={y}"
    draw_korea_panel(d, 624, 132, 984, 452)

    rule(d, 40, 478, 984, width=2)

    # ---- secondary stories: 2 x 2 grid ----
    # row 1
    end = story_cell(
        d, 40, 496, 492, 710,
        "GAZA  •  CEASEFIRE",
        "Israeli strikes kill six in Gaza",
        "At least six Palestinians, including two police officers, "
        "were killed in Israeli strikes on Tuesday, medics said, "
        "despite the ceasefire in force since 2025.",
        "gaza")
    assert end <= 710, f"gaza cell overflows: y={end}"
    end = story_cell(
        d, 524, 496, 984, 710,
        "UKRAINE  •  PEACE TALKS",
        "Kremlin doubts Europe's role in talks",
        "Moscow said it saw no added value in European states "
        "joining Ukraine peace talks, and confirmed no date has "
        "been set for a new round. Kyiv wants a four-party meeting.",
        "talks")
    assert end <= 710, f"talks cell overflows: y={end}"

    rule(d, 40, 726, 984, width=2)

    # row 2
    end = story_cell(
        d, 40, 744, 492, 948,
        "IRAQ  •  OIL AND BORDERS",
        "Baghdad moves on Kurdish oilfields",
        "Iraq's prime minister ordered the federal oil ministry "
        "to run oilfields under Kurdish security control and take "
        "over the region's border crossings, after a smuggling "
        "inquiry.",
        "oil")
    assert end <= 948, f"iraq cell overflows: y={end}"
    end = story_cell(
        d, 524, 744, 984, 948,
        "BANGLADESH  •  EXILED LEADER",
        "Hasina plans return; Dhaka vows arrest",
        "Ousted prime minister Sheikh Hasina plans to return to "
        "Bangladesh on 16 December and has asked Dhaka to arrange "
        "a flight. Ministers say she will be arrested and jailed "
        "on arrival.",
        "return")
    assert end <= 948, f"bangladesh cell overflows: y={end}"

    # ---- ticker ----
    d.rectangle([0, 962, W, 1000], fill=NAVY)
    d.text((16, 970), "ALSO TODAY:",
           font=font(SANS_B, 18), fill=(255, 214, 90))
    d.text((158, 970),
           "UN seeks probe into Benghazi attacks  •  Tajikistan quits the ICC",
           font=font(SANS, 18), fill=(255, 255, 255))

    # ---- footer ----
    d.text((512, 1006),
           "Drawn by code — no photographs. Sources: Yonhap, Reuters, AFP, Al Jazeera, Ukrainska Pravda, Dawn.",
           font=font(SANS, 13), fill=GREY, anchor="ma")

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
