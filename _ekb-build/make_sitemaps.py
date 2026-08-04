# -*- coding: utf-8 -*-
"""Пересборка карт сайта по результатам build.py.

Запуск:  python3 _ekb-build/build.py && python3 _ekb-build/make_sitemaps.py

Что делает:
  1. Спрашивает у build.py полный список URL раздела доставки грунта:
     и те, что идут в индекс, и те, что закрыты в NOINDEX.
  2. sitemap-dostavka-grunta.xml пересобирает целиком из индексируемых.
  3. sitemap.xml правит точечно: чужие URL (сайт про теплицы, прайс)
     остаются как есть со своими датами, блок раздела заменяется.

Так карты не расходятся с NOINDEX: раньше их правили руками и страницы,
убранные из индекса, оставались в sitemap.
"""
import os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "data"))

import build as B

SECTION = os.path.join(ROOT, "sitemap-dostavka-grunta.xml")
MAIN = os.path.join(ROOT, "sitemap.xml")
TODAY = datetime.date.today().isoformat()


def section_urls():
    """(все URL раздела, индексируемые URL) — в порядке карты сайта."""
    pages = list(B.PAGES) + [B.compose_geo(pk, ck) for pk, ck in B.GEO_PAGES]
    every = [f'{B.SITE["domain"]}/dostavka-grunta/']
    index = list(every)
    for p in sorted(pages, key=lambda p: p["slug"]):
        u = f'{B.SITE["domain"]}/{p["slug"]}/'
        every.append(u)
        if p["slug"] not in B.NOINDEX:
            index.append(u)
    from articles import ARTICLES
    for a in ARTICLES:
        u = f'{B.SITE["domain"]}/dostavka-grunta/{a["slug"]}/'
        every.append(u)
        index.append(u)
    return set(every), index


def block(url, priority):
    return (f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n    <priority>{priority}</priority>\n  </url>")


def priority_of(url):
    if url.endswith("/dostavka-grunta/"): return "0.9"
    if "/dostavka-grunta/" in url: return "0.6"
    return "0.7"


def main():
    every, index = section_urls()

    head = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    body = "\n".join(block(u, priority_of(u)) for u in index)
    with open(SECTION, "w", encoding="utf-8") as fh:
        fh.write(head + body + "\n</urlset>\n")

    # В общей карте трогаем только блок раздела, чужие записи не переписываем:
    # у страниц про теплицы свои lastmod, обнулять их незачем.
    src = open(MAIN, encoding="utf-8").read()
    blocks = re.findall(r"  <url>.*?</url>", src, re.S)
    foreign = [b for b in blocks if re.search(r"<loc>(.*?)</loc>", b).group(1) not in every]
    with open(MAIN, "w", encoding="utf-8") as fh:
        fh.write(head + "\n".join(foreign + [block(u, priority_of(u)) for u in index]) + "\n</urlset>\n")

    dropped = len(blocks) - len(foreign) - len(index)
    print(f"sitemap-dostavka-grunta.xml: {len(index)} URL")
    print(f"sitemap.xml: {len(foreign)} чужих + {len(index)} раздела = {len(foreign) + len(index)}")
    print(f"вне индекса: {len(every) - len(index)} страниц, из общей карты убрано {dropped}")


if __name__ == "__main__":
    main()
