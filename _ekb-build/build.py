# -*- coding: utf-8 -*-
"""Сборка лид-ген страниц раздела доставки грунта.
Запуск:  python3 _ekb-build/build.py
Рендерит страницы из data/pages.py в корень репозитория (папки /slug/index.html).
Генератор нужен только для пересборки, сам сайт работает без него.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "data"))
from jinja2 import Environment, FileSystemLoader, select_autoescape
from site_config import SITE  # noqa
from cities import CITIES      # noqa
from pages import PAGES        # noqa
from products import PRODUCTS, GEO_PAGES  # noqa

ROOT = os.path.dirname(HERE)   # корень репо
env = Environment(
    loader=FileSystemLoader(os.path.join(HERE, "templates")),
    autoescape=select_autoescape(["html"]),
    trim_blocks=False, lstrip_blocks=False,
)

FOOTER_LINKS = [
    {"url": "/dostavka-grunta/", "text": "Доставка грунта"},
    {"url": "/chernozem-ekaterinburg/", "text": "Чернозём, Екатеринбург"},
]

def build_localbusiness():
    return {
        "@type": "LocalBusiness",
        "name": SITE["brand"],
        "url": SITE["domain"] + "/dostavka-grunta/",
        "telephone": SITE["phone_display"],
        "areaServed": SITE["region"],
        "openingHours": "Mo-Sa 08:00-20:00",
    }

def build_schema(page, canonical):
    graph = [build_localbusiness(), {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": SITE["domain"] + "/dostavka-grunta/"},
            {"@type": "ListItem", "position": 3, "name": page["h1"], "item": canonical},
        ],
    }]
    if page.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in page["faq"]
            ],
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def compose_geo(product_key, city_key):
    pr = PRODUCTS[product_key]
    city = CITIES[city_key]
    if city_key == "ekaterinburg":
        slug = f'{product_key}-ekaterinburg'
    else:
        slug = f'{product_key}-{city_key}'
    h1 = f'{pr["name"]} {city["prep"]} с доставкой'
    # город-специфичный вопрос впереди общих: уникальность FAQ
    hint = city.get("order_hint", "По объёму возим и мешками, и самосвалом, срок согласуем при заявке.")
    city_q = (f'Сколько стоит доставка {city["to"]}?',
              f'{hint} Точную цену за куб и за мешок с доставкой называем по телефону под ваш объём и адрес.')
    faq = [city_q] + pr["faq_base"]
    return {
        "slug": slug, "city": city_key, "product": pr["chip"], "kind": "geo",
        "h1": h1,
        "title": pr["title_tpl"].format(prep=city["prep"], to=city["to"]),
        "description": pr["desc_tpl"].format(prep=city["prep"], to=city["to"]),
        "hero_sub": pr["hero_sub"],
        "about": pr["intro"],
        "faq": faq,
    }

def render(page):
    city = CITIES[page["city"]]
    canonical = f'{SITE["domain"]}/{page["slug"]}/'
    tpl = env.get_template("money.html" if page["kind"] in ("money", "geo") else "money.html")
    html = tpl.render(
        site=SITE, city=city, canonical=canonical,
        title=page["title"], description=page["description"], h1=page["h1"],
        hero_sub=page["hero_sub"], about=page.get("about", []), faq=page.get("faq", []),
        preselect_product=page["product"],
        district_ph=f'Напр. {city["name"]}, район или адрес',
        footer_links=FOOTER_LINKS,
        schema_json=build_schema(page, canonical),
        metrika_placeholder=True,
    )
    outdir = os.path.join(ROOT, page["slug"])
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return page["slug"], canonical

if __name__ == "__main__":
    only = sys.argv[1:] or None
    done = []
    all_pages = list(PAGES) + [compose_geo(pk, ck) for pk, ck in GEO_PAGES]
    seen = set()
    for p in all_pages:
        if p["slug"] in seen:
            raise SystemExit(f'ДУБЛЬ слага: {p["slug"]}')
        seen.add(p["slug"])
        if only and p["slug"] not in only:
            continue
        done.append(render(p))
    for slug, url in done:
        print("built:", slug, "->", url)
    print(f"Готово: {len(done)} страниц")
