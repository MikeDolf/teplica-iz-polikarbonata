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
from articles import ARTICLES  # noqa
from prices import PRICES, MATERIALS_PRICE  # noqa

ROOT = os.path.dirname(HERE)   # корень репо
env = Environment(
    loader=FileSystemLoader(os.path.join(HERE, "templates")),
    autoescape=select_autoescape(["html"]),
    trim_blocks=False, lstrip_blocks=False,
)


PRODUCT_GEN = {"Чернозём":"чернозём","Перегной":"перегной","Навоз конский":"конский навоз","Навоз коровий":"коровий навоз"}

NOINDEX = {
    "chernozem-nizhniy-tagil", "chernozem-revda", "chernozem-verhnyaya-pyshma",
    "chernozem-sysert", "chernozem-sredneuralsk", "peregnoy-aramil",
}

FOOTER_LINKS = [
    {"url": "/dostavka-grunta/", "text": "Доставка грунта"},
    {"url": "/chernozem-ekaterinburg/", "text": "Чернозём, Екатеринбург"},
]

def build_localbusiness():
    return {
        "@type": "LocalBusiness",
        "name": SITE["brand"],
        "url": SITE["domain"] + "/dostavka-grunta/",
        "email": SITE["contact_email"],
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


def attach_related(pages):
    """Проставляет каждой странице перелинковку: другие города того же продукта + другие продукты того же города."""
    by_slug = {p["slug"]: p for p in pages}
    for p in pages:
        rel = []
        prod = p.get("product")
        city_key = p.get("city")
        city_name = CITIES[city_key]["name"] if city_key in CITIES else ""
        # другие города того же продукта
        for q in pages:
            if q is p: continue
            if q.get("product") == prod and q.get("city") != city_key:
                rel.append({"url": f'/{q["slug"]}/', "text": f'{prod}, {CITIES[q["city"]]["name"]}'})
        # другие продукты в том же городе
        for q in pages:
            if q is p: continue
            if q.get("city") == city_key and q.get("product") != prod:
                rel.append({"url": f'/{q["slug"]}/', "text": f'{q["product"]}, {city_name}'})
        p["related"] = rel[:8]

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
        robots=("noindex, follow" if page["slug"] in NOINDEX else "index, follow"),
        related=page.get("related", []),
        product_gen=PRODUCT_GEN.get(page.get("product",""), "грунт"),
        price=PRICES.get(page.get("product","")),
    )
    outdir = os.path.join(ROOT, page["slug"])
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return page["slug"], canonical, page["slug"] not in NOINDEX


def render_hub(all_pages):
    from articles import ARTICLES as _A
    hub_articles = [{"url": f'/dostavka-grunta/{a["slug"]}/', "text": a["short"]} for a in _A]
    canonical = f'{SITE["domain"]}/dostavka-grunta/'
    catalog = [
        {"name": "Чернозём", "note": "под грядки, газон и теплицу", "url": "/chernozem-ekaterinburg/"},
        {"name": "Перегной", "note": "перепревший, под посадку", "url": "/peregnoy-ekaterinburg/"},
        {"name": "Навоз коровий", "note": "перепревший и свежий", "url": "/navoz-koroviy-ekaterinburg/"},
        {"name": "Навоз конский", "note": "для тёплых грядок и теплиц", "url": "/navoz-konskiy-ekaterinburg/"},
    ]
    geo = [{"url": f'/{p["slug"]}/', "text": f'{p["product"]}, {CITIES[p["city"]]["name"]}'}
           for p in all_pages if p["slug"] not in NOINDEX]
    faq = [
        ("Какие города вы обслуживаете?", "Возим по Екатеринбургу и всей Свердловской области. По городу и ближнему пригороду чаще всего успеваем в день заказа, в дальние города планируем доставку на ближайшие дни."),
        ("В каком объёме возите?", "И мешками для точечных работ, и кубами или самосвалом под отсыпку участка целиком. Подскажем, что выгоднее под вашу задачу и район."),
        ("Как узнать цену?", "Назовите продукт, объём и адрес по телефону или в заявке, назовём точную цену за куб и за мешок с доставкой в ваш район. Скрытых доплат нет."),
    ]
    schema = json.dumps({"@context": "https://schema.org", "@graph": [
        build_localbusiness(),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": canonical}]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
    ]}, ensure_ascii=False, indent=2)
    html = env.get_template("hub.html").render(
        site=SITE, canonical=canonical, robots="index, follow",
        title="Доставка чернозёма, перегноя и навоза по Екатеринбургу и области",
        description="Доставка чернозёма, перегноя, коровьего и конского навоза по Екатеринбургу и Свердловской области. Мешками и самосвалом, цену называем под ваш объём и район. Оставьте заявку.",
        h1="Доставка грунта, перегноя и навоза по Екатеринбургу",
        hero_sub="Чернозём, перегной и навоз с доставкой по городу и области. В мешках и самосвалом, в день заказа. Скажите объём и адрес, назовём точную цену.",
        catalog=catalog, geo=geo, faq=faq, articles=hub_articles, preselect_product="Пока не решил",
        district_ph="Напр. Академический, Верхняя Пышма, Сысерть",
        footer_links=FOOTER_LINKS, schema_json=schema, metrika_placeholder=True, related=[])
    outdir = os.path.join(ROOT, "dostavka-grunta")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    return canonical


def render_articles():
    """Инфо-статьи из articles.py под /dostavka-grunta/<slug>/. Все index/follow."""
    urls = []
    base = "dostavka-grunta"
    # перелинковка между статьями
    for a in ARTICLES:
        related = []
        for b in ARTICLES:
            if b is a: continue
            related.append({"url": f'/{base}/{b["slug"]}/', "text": b["short"]})
        a["_related"] = related[:6]
    for a in ARTICLES:
        canonical = f'{SITE["domain"]}/{base}/{a["slug"]}/'
        schema = json.dumps({"@context": "https://schema.org", "@graph": [
            {"@type": "Article", "headline": a["h1"], "description": a["description"],
             "inLanguage": "ru-RU", "mainEntityOfPage": canonical,
             "publisher": {"@type": "Organization", "name": SITE["brand"], "url": SITE["domain"] + "/dostavka-grunta/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
                {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": SITE["domain"] + "/dostavka-grunta/"},
                {"@type": "ListItem", "position": 3, "name": a["short"], "item": canonical}]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]},
        ]}, ensure_ascii=False, indent=2)
        html = env.get_template("article.html").render(
            site=SITE, canonical=canonical, robots="index, follow",
            title=a["title"], description=a["description"], h1=a["h1"], short=a["short"],
            lede=a["lede"], body=a["body"], faq=a["faq"], cta=a["cta"],
            related=a["_related"], footer_links=FOOTER_LINKS,
            preselect_product="Пока не решил", district_ph="Напр. Академический, Верхняя Пышма",
            schema_json=schema, metrika_placeholder=True)
        outdir = os.path.join(ROOT, base, a["slug"])
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        urls.append(canonical)
    return urls

if __name__ == "__main__":
    only = sys.argv[1:] or None
    done = []
    all_pages = list(PAGES) + [compose_geo(pk, ck) for pk, ck in GEO_PAGES]
    attach_related(all_pages)
    seen = set()
    for p in all_pages:
        if p["slug"] in seen:
            raise SystemExit(f'ДУБЛЬ слага: {p["slug"]}')
        seen.add(p["slug"])
        if only and p["slug"] not in only:
            continue
        done.append(render(p))
    hub_url = render_hub(all_pages) if not only else None
    article_urls = render_articles() if not only else []
    index_urls = [u for (sl, u, idx) in done if idx]
    if hub_url: index_urls.insert(0, hub_url)
    index_urls += article_urls
    for slug, url, idx in done:
        print(("index " if idx else "NOIDX "), slug, "->", url)
    print(f"Готово: {len(done)} страниц, в индекс: {len(index_urls)}")
    # список индексируемых URL для sitemap (Фаза 4)
    with open(os.path.join(HERE, "index_urls.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(index_urls))
