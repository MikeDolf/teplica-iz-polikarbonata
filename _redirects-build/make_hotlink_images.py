# -*- coding: utf-8 -*-
"""Заглушки на месте старых картинок, которые хотлинкают чужие сайты.

По выгрузке внешних ссылок Вебмастера 676 из 711 ссылок — это не текстовые
ссылки, а <img src> с наших адресов: чужие статьи про мойки воздуха
вставили наши фотографии товара напрямую. Файлов давно нет, адреса отдают
404, и на 114 чужих страницах на этом месте битая картинка.

Ранжирование это почти не двигает: <img src> — не ссылка. Но пока по
адресу 404, не работает вообще ничего, а если отдать файл, наш адрес
перестаёт быть битым и на 114 сайтах появляется наша марка.

Картинку можно заменить: перезапишите любой файл в /images/, дизайн
задаётся здесь одним местом.
"""
import os, re, urllib.parse as up
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.environ.get("LINKS_TSV", "")
W, H = 800, 600
BG, INK, ACC, SOFT = (18, 51, 31), (255, 255, 255), (109, 200, 145), (170, 200, 182)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def build_image(path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # мягкая подложка, чтобы карточка не выглядела пустым прямоугольником
    d.rounded_rectangle([40, 40, W - 40, H - 40], radius=24, outline=(38, 82, 56), width=2)
    f_big = ImageFont.truetype(FONT, 62)
    f_mid = ImageFont.truetype(FONT_R, 26)
    f_sm = ImageFont.truetype(FONT_R, 20)

    def center(text, font, y, fill):
        w = d.textbbox((0, 0), text, font=font)[2]
        d.text(((W - w) / 2, y), text, font=font, fill=fill)

    center("fanline.su", f_big, 214, INK)
    center("климатическая техника и товары для дачи", f_mid, 300, SOFT)
    d.line([(W / 2 - 90, 356), (W / 2 + 90, 356)], fill=ACC, width=3)
    center("каталог и цены на сайте", f_sm, 384, SOFT)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "JPEG", quality=88, optimize=True)


def targets():
    """Битые пути к картинкам из выгрузки внешних ссылок."""
    paths = set()
    if TSV and os.path.exists(TSV):
        for line in open(TSV, encoding="utf-8"):
            t = line.split("\t")[0].strip()
            p = up.urlparse(t).path
            if re.search(r"\.(jpe?g|png|gif)$", p, re.I):
                paths.add(p.lstrip("/"))
    return sorted(paths)


def main():
    made = skipped = 0
    for rel in targets():
        full = os.path.join(ROOT, rel)
        if os.path.exists(full):
            skipped += 1
            continue
        build_image(full)
        made += 1
    print(f"создано заглушек: {made}, пропущено (файл уже есть): {skipped}")


if __name__ == "__main__":
    main()
