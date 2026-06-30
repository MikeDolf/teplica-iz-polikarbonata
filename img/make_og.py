#!/usr/bin/env python3
"""Генерация обложки для соцсетей (og:image) 1200x630."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = "#f4f8f5"
GREEN = "#2d5a3d"
DARK = "#444444"
MUTED = "#6b8c78"
BAR = "#3a7d54"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Верхняя зелёная полоса
d.rectangle([0, 0, W, 12], fill=BAR)

# ---- Левая часть: иконка теплицы ----
# Область под иконку: x 70..330
cx, base = 200, 360
half_w, wall_h, roof_h = 120, 150, 90
left, right = cx - half_w, cx + half_w
top_wall = base - wall_h
roof_top = top_wall - roof_h
LW = 7
# каркас теплицы (арочно-домик)
d.line([left, base, left, top_wall], fill=GREEN, width=LW)
d.line([right, base, right, top_wall], fill=GREEN, width=LW)
d.line([left, base, right, base], fill=GREEN, width=LW)
d.line([left, top_wall, cx, roof_top], fill=GREEN, width=LW)
d.line([right, top_wall, cx, roof_top], fill=GREEN, width=LW)
d.line([left, top_wall, right, top_wall], fill=GREEN, width=LW)
# вертикальная стойка по центру
d.line([cx, roof_top, cx, base], fill=MUTED, width=4)
# горизонтальные рёбра
d.line([left, top_wall - 50, right, top_wall - 50], fill=MUTED, width=3)
# дверь
dw = 34
d.rectangle([cx - dw, base - 80, cx + dw, base], outline=GREEN, width=5)

# ---- Правая часть: текст ----
tx = 380
f_logo = ImageFont.truetype(FONT_BOLD, 88)
f_main = ImageFont.truetype(FONT_REG, 40)
f_tag = ImageFont.truetype(FONT_REG, 34)

lines = [
    (f_logo, "Fanline.su", GREEN, 24),
    (f_main, "Поликарбонат и теплицы:", DARK, 14),
    (f_main, "монтаж · выбор · комплектующие", DARK, 30),
    (f_tag, "Справочник дачника", MUTED, 0),
]

# измеряем суммарную высоту блока для вертикального центрирования
total = 0
heights = []
for f, t, c, gap in lines:
    bb = d.textbbox((0, 0), t, font=f)
    h = bb[3] - bb[1]
    heights.append((bb, h))
    total += h + gap

y = (H - total) // 2
for (f, t, c, gap), (bb, h) in zip(lines, heights):
    d.text((tx, y - bb[1]), t, font=f, fill=c)
    y += h + gap

img.save("/home/user/teplica-iz-polikarbonata/img/og-cover.png", "PNG")
print("saved")
