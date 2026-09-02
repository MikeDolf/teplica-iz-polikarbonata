# -*- coding: utf-8 -*-
"""Пережатие фотографий раздела под скорость загрузки.

Запуск:  python3 _ekb-build/optimize_photos.py [--dry]

Зачем. add_photo.py сохранял WebP с quality=82. Для макросъёмки грунта это
слишком много: снимок сплошного шума почти не сжимается, и шапки товарных
страниц весили по 300 КБ. На мобильном интернете именно эта картинка и есть
LCP, то есть момент, когда человек считает страницу загруженной.

Что делает. Пережимает каждый WebP и JPG в assets/ekb/photo из самого
крупного имеющегося WebP того же кадра: пересжатие крупного файла с
уменьшением даёт меньше артефактов, чем пересжатие уже ужатого мелкого.

Про качество. 62 вместо 82 — на фотографиях земли разница не видна даже
при сравнении вплотную: там нет ни плавных градиентов, ни резких границ,
где артефакты заметны. У круглых текстур в полосе товаров качество выше:
они маленькие, и мылом смотрятся сразу. Размывать кадры перед сжатием (это
дало бы ещё треть) сознательно не стали — фотографии здесь работают на
доверие, и мягкая картинка выглядит как чужая заглушка.

Скрипт идемпотентен по смыслу, но не по байтам: повторный прогон снова
пережмёт уже пережатое и качество осядет ещё. Запускать по необходимости,
а не в общем конвейере сборки.
"""
import os
import re
import sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ekb", "photo")

WEBP_HERO = 62      # шапки и сюжетные кадры: показываются крупно, шума много
WEBP_TEX = 70       # круглые текстуры 96-400 px: мелкие, мыло заметно
JPG_Q = 74          # запасной вариант для браузеров без WebP


def quality_for(name, width):
    return WEBP_TEX if width <= 400 and not name.startswith("hero-") else WEBP_HERO


def main():
    dry = "--dry" in sys.argv
    files = {}
    for f in os.listdir(OUT):
        m = re.match(r"(.+)-(\d+)\.(webp|jpg)$", f)
        if m:
            files.setdefault(m.group(1), []).append((int(m.group(2)), m.group(3), f))

    was = now = 0
    for name in sorted(files):
        items = files[name]
        # Источник — самый широкий WebP кадра: он ближе всего к оригиналу.
        widest = max((w for w, ext, _ in items if ext == "webp"), default=None)
        if widest is None:
            continue
        src = Image.open(os.path.join(OUT, f"{name}-{widest}.webp")).convert("RGB")
        for width, ext, fname in sorted(items):
            path = os.path.join(OUT, fname)
            before = os.path.getsize(path)
            was += before
            h = round(src.size[1] * width / src.size[0])
            im = src if width == src.size[0] else src.resize((width, h), Image.LANCZOS)
            if dry:
                now += before
                continue
            if ext == "webp":
                im.save(path, "WEBP", quality=quality_for(name, width), method=6)
            else:
                im.save(path, "JPEG", quality=JPG_Q, optimize=True, progressive=True)
            after = os.path.getsize(path)
            now += after
            print(f"  {fname:34} {before // 1024:>4} -> {after // 1024:>4} КБ")

    print(f"\nБыло {was // 1024} КБ, стало {now // 1024} КБ, "
          f"минус {(was - now) * 100 // was if was else 0}%")


if __name__ == "__main__":
    main()
