#!/usr/bin/env python3
"""
Generates torrent_search.ico: an original horseshoe-magnet + magnifying-glass
mark (nothing traced or copied — plain geometric shapes drawn with PIL).
Run once to (re)produce the .ico; not needed at app runtime.
"""
import math
import os

from PIL import Image, ImageDraw

SIZE = 1024
CX, CY = SIZE // 2, SIZE // 2 + 60
R = 300
ARM_W = 110

BODY = (142, 152, 168, 255)      # steel-grey magnet body
BODY_DARK = (96, 104, 118, 255)  # outline shade
RED = (223, 64, 68, 255)         # left pole tip
BLUE = (52, 108, 178, 255)       # right pole tip
GLASS_RIM = (29, 39, 51, 255)    # magnifying glass


def point(angle_deg, radius, cx=CX, cy=CY):
    a = math.radians(angle_deg)
    return (cx + radius * math.cos(a), cy + radius * math.sin(a))


def draw_horseshoe(d: ImageDraw.ImageDraw):
    # Horseshoe body: thick arc leaving a gap at the top (270deg).
    bbox = [CX - R, CY - R, CX + R, CY + R]
    d.arc(bbox, start=290, end=250 + 360, fill=BODY, width=ARM_W)
    # Rounded outline pass for a slightly cleaner edge.
    d.arc(bbox, start=290, end=250 + 360, fill=BODY_DARK, width=ARM_W + 14)
    d.arc(bbox, start=290, end=250 + 360, fill=BODY, width=ARM_W)

    leg_len = 230
    leg_half = ARM_W // 2

    for angle, tip_color in ((290, RED), (250, BLUE)):
        x, y = point(angle, R)
        top_y = y - leg_len
        # leg
        d.rounded_rectangle(
            [x - leg_half, top_y, x + leg_half, y + 20],
            radius=leg_half,
            fill=BODY,
        )
        # colored pole tip
        d.rounded_rectangle(
            [x - leg_half, top_y, x + leg_half, top_y + 130],
            radius=leg_half,
            fill=tip_color,
        )


def draw_magnifier(d: ImageDraw.ImageDraw):
    gx, gy = CX + 235, CY + 210
    g_r = 150
    rim_w = 56
    d.ellipse([gx - g_r, gy - g_r, gx + g_r, gy + g_r], outline=GLASS_RIM, width=rim_w)
    # handle
    hx1, hy1 = point(45, g_r - rim_w // 2, gx, gy)
    hx2, hy2 = point(45, g_r + 150, gx, gy)
    d.line([hx1, hy1, hx2, hy2], fill=GLASS_RIM, width=rim_w)
    d.ellipse([hx2 - rim_w / 2, hy2 - rim_w / 2, hx2 + rim_w / 2, hy2 + rim_w / 2], fill=GLASS_RIM)


def main():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_horseshoe(d)
    draw_magnifier(d)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(out_dir, "torrent_search_preview.png")
    ico_path = os.path.join(out_dir, "torrent_search.ico")

    img.save(png_path)
    img.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")


if __name__ == "__main__":
    main()
