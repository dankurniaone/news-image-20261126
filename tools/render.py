#!/usr/bin/env python3
"""Draw the 26 November 2026 front page as a 680x1024 PNG.

THE WORLD IN A DAY, Thursday 26 November 2026. A broadsheet front page:
a nameplate and dateline, a lead story on Thanksgiving Day in the United
States with a tall file photo of a Macy's parade balloon, two stories
below it (the Virgin Australia ground-staff strike; India marking
Constitution Day and eighteen years since 26/11) with small photos, and
an "Also today" strip of three briefs. Everything is drawn with Pillow at
double size and shrunk with LANCZOS so the small type stays sharp.

The photographs are real freely licensed file photos (none taken today);
the words are the day's verified news. Every story's event happened on
26 November 2026, checked against Reuters, ABC News and FIDE. Run from
the repository root:

    python3 tools/render.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

SCALE = 2
W, H = 680 * SCALE, 1024 * SCALE
MARGIN = 30 * SCALE
INNER = W - 2 * MARGIN

PAPER = (248, 244, 233)
INK = (17, 17, 17)
RED = (158, 28, 32)
GREY = (96, 91, 82)
LINECOL = (150, 143, 128)
SHADE = (233, 228, 215)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size * SCALE)


def wrap_lines(draw, text, face, width):
    """Greedy word wrap; returns a list of lines fitting width."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=face) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(draw, lines, face, x, y, leading, fill=INK):
    """Draw lines top to bottom; returns the y just past the last line."""
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def rule(draw, x0, x1, y, width=1):
    draw.line([(x0, y), (x1, y)], fill=LINECOL, width=width * SCALE)


def double_rule(draw, x0, x1, y):
    draw.line([(x0, y), (x1, y)], fill=INK, width=2 * SCALE)
    draw.line([(x0, y + 4 * SCALE), (x1, y + 4 * SCALE)], fill=INK, width=1 * SCALE)


def crop_to(img, target_w, target_h):
    """Centre-crop an image to the target aspect ratio, then resize."""
    tw, th = target_w, target_h
    iw, ih = img.size
    want = tw / th
    have = iw / ih
    if have > want:
        cut = int(iw - ih * want)
        img = img.crop((cut // 2, 0, iw - cut // 2, ih))
    else:
        cut = int(ih - iw / want)
        img = img.crop((0, cut // 2, iw, ih - cut // 2))
    return img.resize((tw, th), Image.LANCZOS)


def main():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    y = 22 * SCALE

    # Nameplate.
    name = font(SERIF_B, 52)
    title = "THE WORLD IN A DAY"
    tw = draw.textlength(title, font=name)
    draw.text(((W - tw) / 2, y), title, font=name, fill=INK)
    y += 62 * SCALE

    # Dateline.
    small = font(SANS, 11)
    date_line = "THURSDAY 26 NOVEMBER 2026  ·  No. 330  ·  ONE DAY, ONE PAGE"
    tw = draw.textlength(date_line, font=small)
    draw.text(((W - tw) / 2, y), date_line, font=small, fill=GREY)
    y += 18 * SCALE
    double_rule(draw, MARGIN, W - MARGIN, y)
    y += 12 * SCALE

    # --- Lead story: Thanksgiving. ---
    kicker = font(SANS_B, 11)
    draw.text((MARGIN, y), "UNITED STATES", font=kicker, fill=RED)
    y += 16 * SCALE

    head = font(SERIF_B, 40)
    y = text_block(draw,
                   wrap_lines(draw, "AMERICA GIVES THANKS", head, INNER),
                   head, MARGIN, y, 46 * SCALE)
    y += 2 * SCALE

    deck = font(SERIF_I, 15)
    y = text_block(
        draw,
        wrap_lines(draw,
                   "Parades, football and full tables as the United States "
                   "pauses for Thanksgiving — Wall Street shut, airports "
                   "braced for the year's busiest travel day.",
                   deck, INNER),
        deck, MARGIN, y, 19 * SCALE, fill=(52, 48, 44))
    y += 6 * SCALE

    photo = Image.open(os.path.join(ASSETS, "parade.jpg")).convert("RGB")
    photo = crop_to(photo, INNER, 238 * SCALE)
    page.paste(photo, (MARGIN, y))
    y += 238 * SCALE + 5 * SCALE

    cap = font(SANS_I, 9)
    y = text_block(
        draw,
        wrap_lines(draw,
                   "File photo: a balloon is inflated on the eve of the "
                   "Macy's Thanksgiving Day Parade in New York. "
                   "(Rhododendrites / Wikimedia Commons)",
                   cap, INNER),
        cap, MARGIN, y, 12 * SCALE, fill=GREY)
    y += 6 * SCALE

    body = font(SERIF, 12)
    lead_text = (
        "NEW YORK — The balloons were up over Manhattan this morning as the "
        "Macy's Thanksgiving Day Parade stepped off down Sixth Avenue, "
        "opening a day that stops the country in its tracks. Millions lined "
        "the route and millions more watched from home as the giant balloons "
        "drifted past, the curtain-raiser for an afternoon of NFL football "
        "and the year's biggest family meal. Wall Street is closed for the "
        "holiday and trading resumes tomorrow. Airports reported the "
        "Thanksgiving rush moving, after a week in which technology outages "
        "rattled travellers. For most Americans, though, the day is simpler "
        "than that: turkey, family, and football.")
    half = INNER // 2 - 6 * SCALE
    first_half = wrap_lines(draw, lead_text, body, half)
    mid = (len(first_half) + 1) // 2
    col_a, col_b = first_half[:mid], first_half[mid:]
    ya = text_block(draw, col_a, body, MARGIN, y, 16 * SCALE)
    yb = text_block(draw, col_b, body, MARGIN + half + 12 * SCALE, y,
                    16 * SCALE)
    y = max(ya, yb) + 8 * SCALE
    rule(draw, MARGIN, W - MARGIN, y)
    y += 10 * SCALE

    # --- Second row: two stories side by side. ---
    col_w = (INNER - 14 * SCALE) // 2
    sub_head = font(SERIF_B, 18)
    sub_body = font(SERIF, 11)
    sub_cap = font(SANS_I, 8)

    def side_story(x, img_name, headline, text, caption):
        yy = y
        img = Image.open(os.path.join(ASSETS, img_name)).convert("RGB")
        img = crop_to(img, col_w, 132 * SCALE)
        page.paste(img, (x, yy))
        yy += 132 * SCALE + 4 * SCALE
        yy = text_block(draw,
                        wrap_lines(draw, caption, sub_cap, col_w),
                        sub_cap, x, yy, 11 * SCALE, fill=GREY)
        yy += 4 * SCALE
        yy = text_block(draw,
                        wrap_lines(draw, headline, sub_head, col_w),
                        sub_head, x, yy, 21 * SCALE)
        yy += 2 * SCALE
        yy = text_block(draw,
                        wrap_lines(draw, text, sub_body, col_w),
                        sub_body, x, yy, 14 * SCALE)
        return yy

    y_left = side_story(
        MARGIN, "virgin.jpg",
        "VIRGIN GROUND STAFF WALK OUT AT FOUR AIRPORTS",
        "SYDNEY — Virgin Australia ground staff walked off the job at four "
        "airports today in a pay dispute, with the longest stoppage in "
        "Adelaide running from 3.30pm to 6.30pm. The Australian Services "
        "Union says the airline's offer of rises of 17% to 28.9% over three "
        "years still leaves ground crews behind. Virgin says it expects no "
        "disruption to flights. (ABC News)",
        "File photo: a Virgin Australia Boeing 737 at Adelaide Airport. "
        "(Bahnfrend / Wikimedia Commons)")
    y_right = side_story(
        MARGIN + col_w + 14 * SCALE, "indiagate.jpg",
        "INDIA MARKS CONSTITUTION DAY — AND 18 YEARS SINCE 26/11",
        "NEW DELHI — India marked Constitution Day today, 77 years after "
        "the Constituent Assembly adopted the Constitution on 26 November "
        "1949, with ceremonies in the capital. The date carries a second "
        "weight in Mumbai, which remembers the 2008 attacks on this day "
        "eighteen years ago, when 166 people were killed in the three-day "
        "siege. (Reuters)",
        "File photo: India Gate, New Delhi, lit in the colours of the "
        "Indian flag. (Yash Seth / Wikimedia Commons)")
    y = max(y_left, y_right) + 8 * SCALE
    rule(draw, MARGIN, W - MARGIN, y)
    y += 8 * SCALE

    # --- Also today. ---
    label = font(SANS_B, 11)
    draw.text((MARGIN, y), "ALSO TODAY", font=label, fill=RED)
    y += 15 * SCALE
    brief = font(SERIF, 10)
    third = (INNER - 2 * 12 * SCALE) // 3
    briefs = [
        "GENEVA — Game 3 of the World Chess Championship is played today, "
        "champion Gukesh Dommaraju and challenger Javokhir Sindarov level "
        "at 1–1 after two draws.",
        "SYDNEY — Ferry workers on Sydney's Pittwater walked out from "
        "7.30am today, shutting Palm Beach services for the day.",
        "NEW YORK — Wall Street is closed for Thanksgiving. Trading "
        "resumes on Friday for a shortened session.",
    ]
    ends = []
    for i, text in enumerate(briefs):
        x = MARGIN + i * (third + 12 * SCALE)
        ends.append(text_block(draw, wrap_lines(draw, text, brief, third),
                               brief, x, y, 13 * SCALE))
    y = max(ends) + 8 * SCALE
    double_rule(draw, MARGIN, W - MARGIN, y)
    y += 8 * SCALE

    foot = font(SANS, 8)
    y = text_block(
        draw,
        wrap_lines(draw,
                   "Words: Reuters, ABC News, FIDE. Photos are file photos, "
                   "freely licensed via Wikimedia Commons (CC BY-SA). "
                   "The World in a Day — a make.fun news-image entry.",
                   foot, INNER),
        foot, MARGIN, y, 11 * SCALE, fill=GREY)

    page = page.resize((680, 1024), Image.LANCZOS)
    out = os.path.join(HERE, "entry.png")
    page.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
