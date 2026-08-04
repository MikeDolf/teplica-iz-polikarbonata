# -*- coding: utf-8 -*-
"""Подключение присланных фотографий к сайту.

Запуск:  python3 _ekb-build/add_photo.py A1 /путь/к/файлу.png

Что делает:
  1. Кадрирует по центру под нужные пропорции набора (A — квадрат,
     B и D — 16:9, C — 4:3).
  2. Сохраняет WebP и JPG-запасной вариант в нужных размерах.
  3. Кладёт в assets/ekb/photo/ под именем из карты наборов.

Дальше остаётся пересобрать сайт: шаблоны сами подхватят фото,
если файл существует, иначе останется SVG-текстура.
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ekb", "photo")

# набор -> (имя файла, пропорции, ширины под srcset)
MAP = {
    # A: круглые макро материалов, в полосу товаров и каталог
    "A1":  ("chernozem",         (1, 1), [96, 200, 400]),
    "A2":  ("peregnoy",          (1, 1), [96, 200, 400]),
    "A3":  ("torf",              (1, 1), [96, 200, 400]),
    "A4":  ("kislyy-torf",       (1, 1), [96, 200, 400]),
    "A5":  ("torfogrunt",        (1, 1), [96, 200, 400]),
    "A6":  ("opilki",            (1, 1), [96, 200, 400]),
    "A7":  ("navoz",             (1, 1), [96, 200, 400]),
    "A8":  ("navoz-koroviy",     (1, 1), [96, 200, 400]),
    "A9":  ("navoz-konskiy",     (1, 1), [96, 200, 400]),
    "A10": ("plodorodnyy-grunt", (1, 1), [96, 200, 400]),
    "A11": ("zemlya-v-meshkah",  (1, 1), [96, 200, 400]),
    # B: широкие кадры материалов, в шапки товарных страниц
    "B1":  ("hero-chernozem",         (16, 9), [800, 1400]),
    "B2":  ("hero-peregnoy",          (16, 9), [800, 1400]),
    "B3":  ("hero-torf",              (16, 9), [800, 1400]),
    "B4":  ("hero-kislyy-torf",       (16, 9), [800, 1400]),
    "B5":  ("hero-torfogrunt",        (16, 9), [800, 1400]),
    "B6":  ("hero-opilki",            (16, 9), [800, 1400]),
    "B7":  ("hero-navoz",             (16, 9), [800, 1400]),
    "B8":  ("hero-navoz-koroviy",     (16, 9), [800, 1400]),
    "B9":  ("hero-navoz-konskiy",     (16, 9), [800, 1400]),
    "B10": ("hero-plodorodnyy-grunt", (16, 9), [800, 1400]),
    "B11": ("hero-zemlya-v-meshkah",  (16, 9), [800, 1400]),
    # C: техника, в блок объёмов
    "C1":  ("truck-gazel",    (4, 3), [420, 840]),
    "C2":  ("truck-samosval", (4, 3), [420, 840]),
    "C3":  ("truck-kamaz",    (4, 3), [420, 840]),
    # D: площадка и работа
    "D1":  ("yard",     (16, 9), [800, 1400]),
    "D2":  ("loading",  (16, 9), [800, 1400]),
    "D3":  ("unloading",(16, 9), [800, 1400]),
}


def crop_center(im, ratio):
    """Обрезает по центру под заданные пропорции без искажения."""
    w, h = im.size
    tw, th = ratio
    target = tw / th
    if w / h > target:
        nw = int(h * target)
        box = ((w - nw) // 2, 0, (w - nw) // 2 + nw, h)
    else:
        nh = int(w / target)
        box = (0, (h - nh) // 2, w, (h - nh) // 2 + nh)
    return im.crop(box)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("Известные наборы:", ", ".join(sorted(MAP, key=lambda k: (k[0], int(k[1:])))))
        sys.exit(1)
    key, src = sys.argv[1].upper(), sys.argv[2]
    if key not in MAP:
        sys.exit(f"Неизвестный набор {key}. Доступны: {', '.join(sorted(MAP))}")
    if not os.path.exists(src):
        sys.exit(f"Файл не найден: {src}")

    name, ratio, widths = MAP[key]
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im = crop_center(im, ratio)

    made = []
    for w in widths:
        h = int(w * ratio[1] / ratio[0])
        r = im.resize((w, h), Image.LANCZOS)
        p_webp = os.path.join(OUT, f"{name}-{w}.webp")
        r.save(p_webp, "WEBP", quality=82, method=6)
        made.append((p_webp, os.path.getsize(p_webp)))
        if w == widths[-1]:                      # запасной JPG только в макс. размере
            p_jpg = os.path.join(OUT, f"{name}-{w}.jpg")
            r.save(p_jpg, "JPEG", quality=84, optimize=True, progressive=True)
            made.append((p_jpg, os.path.getsize(p_jpg)))

    print(f"{key} -> {name}, исходник {Image.open(src).size}, кадрирование {ratio[0]}:{ratio[1]}")
    for p, s in made:
        print(f"   {os.path.basename(p):32} {s // 1024} КБ")
    print("\nДальше: python3 _ekb-build/build.py")


if __name__ == "__main__":
    main()
