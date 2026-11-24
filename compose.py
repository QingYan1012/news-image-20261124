#!/usr/bin/env python3
"""Compose the news-image-20261124 entry: a one-page 'world in one day'
front page for Tuesday 24 November 2026, from five generated panels.

Layout 1024x1024: date header, one lead panel, two rows of two panels,
a markets ticker footer. All text is drawn here (real font) so nothing
is garbled. Output must be <= 1 MiB and <= 1024x1024 (PNG, else JPEG).
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "panels")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
BG = (10, 22, 40)          # deep navy
PAPER = (243, 238, 226)    # off-white
AMBER = (232, 164, 62)
MUTE = (168, 182, 200)
LABEL_BG = (16, 34, 58)


def font(size, bold=True):
    pats = [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in pats:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    g = glob.glob("/usr/share/fonts/**/NotoSans*Bold*.ttf", recursive=True)
    return ImageFont.truetype(g[0], size)


def panel(name):
    g = sorted(glob.glob(os.path.join(PANELS, f"media-generation-panel-{name}-0-*.webp")))
    return Image.open(g[0]).convert("RGB")


def fill(img, box_w, box_h):
    """Center-crop img to fill box_w x box_h."""
    sw, sh = img.size
    scale = max(box_w / sw, box_h / sh)
    img = img.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    x = (img.size[0] - box_w) // 2
    y = (img.size[1] - box_h) // 2
    return img.crop((x, y, x + box_w, y + box_h))


def draw_label(d, x, y, w, head, sub, head_size, sub_size):
    d.rectangle([x, y, x + w, y + 64], fill=LABEL_BG)
    d.text((x + 14, y + 7), head, font=font(head_size), fill=PAPER)
    d.text((x + 14, y + 7 + head_size + 6), sub, font=font(sub_size, bold=False), fill=MUTE)


def main():
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    M = 20  # margin

    # ---- header ----
    d.text((M + 2, 16), "T U E S D A Y   ·   T H E   W O R L D   I N   O N E   D A Y",
           font=font(25), fill=AMBER)
    d.text((M, 46), "24 NOVEMBER 2026", font=font(74), fill=PAPER)
    d.rectangle([M, 140, W - M, 144], fill=AMBER)

    # ---- lead panel: Libya ----
    y = 160
    lead = fill(panel("libya"), W - 2 * M, 252)
    canvas.paste(lead, (M, y))
    draw_label(d, M, y + 252, W - 2 * M,
               "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
               "Sea drones strike in the Mediterranean · UN seeks probe", 31, 21)
    y += 252 + 64 + 14

    # ---- row 2: COP31 + Nvidia ----
    half = (W - 2 * M - 12) // 2
    for i, (name, head, sub) in enumerate([
        ("cop31", "COP31 CLIMATE TALKS COLLAPSE", "Antalya summit ends with no deal"),
        ("nvidia", "HUANG RETURNS TO NVIDIA", "CEO reinstated — markets soar"),
    ]):
        x = M + i * (half + 12)
        canvas.paste(fill(panel(name), half, 158), (x, y))
        draw_label(d, x, y + 158, half, head, sub, 24, 19)
    y += 158 + 64 + 14

    # ---- row 3: Hormuz + Tiangong ----
    for i, (name, head, sub) in enumerate([
        ("hormuz", "RECORD IRANIAN ATTACKS IN HORMUZ", "Britain logs record attacks in the strait"),
        ("tiangong", "FIRST FOREIGN GUEST AT TIANGONG", "Pakistani astronaut to fly to China's station"),
    ]):
        x = M + i * (half + 12)
        canvas.paste(fill(panel(name), half, 158), (x, y))
        draw_label(d, x, y + 158, half, head, sub, 24, 19)
    y += 158 + 64 + 12

    # ---- footer ticker ----
    d.rectangle([M, y, W - M, y + 3], fill=AMBER)
    ticker = "MARKETS  S&P +4.7% · NASDAQ +6.5% · NIKKEI +3.9% · BRENT $86.7 · GOLD $3,620"
    size = 24
    while size > 16 and d.textlength(ticker, font=font(size)) > W - 2 * M - 8:
        size -= 1
    f = font(size)
    tw = d.textlength(ticker, font=f)
    d.text(((W - tw) / 2, y + 14), ticker, font=f, fill=PAPER)

    canvas.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    print("PNG bytes:", size, "dims:", canvas.size)
    if size > 1_048_576:
        canvas.save(OUT, format="JPEG", quality=90, optimize=True)
        print("too big as PNG; saved as JPEG bytes:", os.path.getsize(OUT))


if __name__ == "__main__":
    main()
