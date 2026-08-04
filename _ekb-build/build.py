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
from prices import PRICES, MATERIALS_PRICE, FLEET_VIZ, PRODBAR  # noqa
from tail_cities import TAIL_CITIES  # noqa
try:
    from reviews import REVIEWS  # noqa
except ImportError:
    REVIEWS = []

ROOT = os.path.dirname(HERE)   # корень репо
env = Environment(
    loader=FileSystemLoader(os.path.join(HERE, "templates")),
    autoescape=select_autoescape(["html"]),
    trim_blocks=False, lstrip_blocks=False,
)



def available_photos():
    """Какие фото уже загружены. Шаблоны берут фото, если оно есть,
    иначе показывают SVG-текстуру, поэтому можно подключать по одной."""
    d = os.path.join(ROOT, "assets", "ekb", "photo")
    if not os.path.isdir(d):
        return set()
    return {f.rsplit("-", 1)[0] for f in os.listdir(d) if f.endswith(".webp")}


PHOTOS = available_photos()

PRODUCT_GEN = {"Чернозём":"чернозём","Перегной":"перегной","Навоз конский":"конский навоз","Навоз коровий":"коровий навоз"}
# в блоке хвостовых городов нужно имя самого товара, а не чипа формы:
# у земли в мешках и кислого торфа чип общий с соседним товаром
TAIL_NAME = {
    "chernozem":"чернозём", "peregnoy":"перегной", "torf":"торф", "opilki":"опилки",
    "navoz":"навоз", "navoz-koroviy":"коровий навоз", "navoz-konskiy":"конский навоз",
    "plodorodnyy-grunt":"плодородный грунт", "torfogrunt":"торфогрунт",
    "kislyy-torf":"кислый торф", "zemlya-v-meshkah":"землю в мешках",
}

NOINDEX = {
    # Тагил 53, Сысерть 48, Ревда 21, Арамиль 23, Пышма 5, Среднеуральск 9 по
    # Вордстату: спрос подтверждён, страницы возвращены в индекс.
    # Нерудные материалы ведёт отдельный сайт владельца (ursdom.ru).
    # Держим страницы живыми для прямых заходов, но вне индекса, чтобы два
    # сайта одного владельца не конкурировали за одни запросы в одном регионе
    # (риск аффилиат-фильтра Яндекса).
    "shcheben-ekaterinburg", "pesok-ekaterinburg",
    "otsev-ekaterinburg", "pgs-ekaterinburg",
}

# Точечные внешние ссылки на профильный проект: только на 2 страницах,
# чтобы не создавать сквозной шаблонный линк со всего раздела.
CROSSLINK = {
    "torf-ekaterinburg": {"title":"Сажаете голубику?","text":"Голубике нужен верховой торф с кислотностью pH 2,6-3,5, низинный ей не подходит. Под эту задачу у нас отдельная страница: там состав смеси, размер ямы и расчёт объёма на куст.","url":"/torf-dlya-golubiki/","anchor":"Кислый торф для голубики"},
    "torf-dlya-golubiki": {"title":"Нужен торф под другие задачи?","text":"Под грядки, теплицы и почвосмеси берут низинный торф, он почти нейтральный. Виды, кислотность и цены за куб собраны на общей странице торфа.","url":"/torf-ekaterinburg/","anchor":"Весь торф в Екатеринбурге"},
    "chernozem-ekaterinburg": {"title":"Участок подтапливает?","text":"Если весной на участке стоит вода, плодородный слой в ней просто закиснет. Сначала делают водоотвод, потом завозят чернозём. Как устроить дренаж, разобрано в отдельном справочнике.","url":"https://ursdom.ru/drenazh/","anchor":"Дренаж участка: трубы, колодцы, укладка"},
}

MOVED_TO = {
    "shcheben-ekaterinburg": {"title":"Щебень возит наш профильный проект","text":"Мы сосредоточились на органике: чернозём, перегной, навоз и торф. Щебень всех фракций, песок, ПГС и отсев с доставкой по Екатеринбургу и области возит наш второй проект «Щебень-Урал».","url":"https://ursdom.ru/dostavka/shcheben/","anchor":"Цены на щебень за куб"},
    "pesok-ekaterinburg": {"title":"Песок возит наш профильный проект","text":"На этом сайте мы возим органику для грядок и газона. Карьерный и мытый речной песок с доставкой смотрите у нашего проекта «Щебень-Урал».","url":"https://ursdom.ru/dostavka/","anchor":"Песок и другие нерудные материалы"},
    "otsev-ekaterinburg": {"title":"Отсев возит наш профильный проект","text":"Мы возим чернозём, перегной, навоз и торф. Отсев под дорожки и площадки с доставкой по области возит наш проект «Щебень-Урал».","url":"https://ursdom.ru/dostavka/","anchor":"Отсев и нерудные материалы"},
    "pgs-ekaterinburg": {"title":"ПГС возит наш профильный проект","text":"На этом сайте органика для участка. Песчано-гравийную смесь под основания и отсыпку возит наш проект «Щебень-Урал».","url":"https://ursdom.ru/dostavka/","anchor":"ПГС и нерудные материалы"},
}

FOOTER_LINKS = [
    {"url": "/dostavka-grunta/", "text": "Доставка грунта"},
    {"url": "/chernozem-ekaterinburg/", "text": "Чернозём, Екатеринбург"},
]

def build_localbusiness():
    lb = {
        "@type": "LocalBusiness",
        "name": SITE["brand"],
        "url": SITE["domain"] + "/dostavka-grunta/",
        "email": SITE["contact_email"],
        "areaServed": SITE["region"],
        "openingHours": "Mo-Sa 08:00-20:00",
        "priceRange": "₽₽",
    }
    if SITE.get("phone_tel"):
        lb["telephone"] = SITE["phone_tel"]
    return lb

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



def product_genitive(page):
    """Родительный падеж товара для заголовков. Берём по ключу товара, а не по
    чипу формы: у земли в мешках и общего навоза чип общий с соседним товаром,
    и по чипу подставлялся чужой материал."""
    slug = page["slug"]
    for key in sorted(PRODUCTS, key=len, reverse=True):
        if slug == key or slug.startswith(key + "-"):
            return PRODUCTS[key]["gen"]
    return "грунта"


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
        # уникальный городской текст идёт первым: он задаёт непохожесть страниц
        "about": city.get("about_extra", []) + pr["intro"],
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
        reviews=REVIEWS, moved_to=MOVED_TO.get(page["slug"]) or CROSSLINK.get(page["slug"]),
        tail_cities=(TAIL_CITIES.get(page["slug"][:-len("-ekaterinburg")]) if page["slug"].endswith("-ekaterinburg") else None),
        fleet_viz=FLEET_VIZ, prodbar=PRODBAR, current_slug=page["slug"], photos=PHOTOS,
        product_genitive=product_genitive(page),
        tail_name=TAIL_NAME.get(page["slug"][:-len("-ekaterinburg")] if page["slug"].endswith("-ekaterinburg") else ""),
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
        {"name": "Торф", "note": "верховой кислый и низинный", "url": "/torf-ekaterinburg/"},
        {"name": "Торф для голубики", "note": "верховой, pH 2,6-3,5", "url": "/torf-dlya-golubiki/"},
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
        title="Доставка грунта, перегноя и навоза по Екатеринбургу",
        description="Доставка чернозёма, перегноя и навоза по Екатеринбургу и Свердловской области. Мешками и самосвалом, цену называем под ваш объём и район.",
        h1="Доставка грунта, перегноя и навоза по Екатеринбургу",
        hero_sub="Чернозём, перегной и навоз с доставкой по городу и области. В мешках и самосвалом, в день заказа. Скажите объём и адрес, назовём точную цену.",
        catalog=catalog, geo=geo, faq=faq, articles=hub_articles, preselect_product="Пока не решил",
        district_ph="Напр. Академический, Верхняя Пышма, Сысерть",
        footer_links=FOOTER_LINKS, schema_json=schema, metrika_placeholder=True, related=[],
        prodbar=PRODBAR, current_slug="", photos=PHOTOS)
    outdir = os.path.join(ROOT, "dostavka-grunta")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    return canonical


def render_articles():
    """Инфо-статьи из articles.py под /dostavka-grunta/<slug>/. Все index/follow."""
    urls = []
    base = "dostavka-grunta"
    PRICE_BY_URL = {
        "/chernozem-ekaterinburg/": PRICES.get("Чернозём"),
        "/peregnoy-ekaterinburg/": PRICES.get("Перегной"),
        "/navoz-konskiy-ekaterinburg/": PRICES.get("Навоз конский"),
        "/navoz-koroviy-ekaterinburg/": PRICES.get("Навоз коровий"),
        "/torf-ekaterinburg/": PRICES.get("Торф"),
        "/torf-dlya-golubiki/": PRICES.get("Торф"),
    }

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
            cta_price=PRICE_BY_URL.get(a["cta"]["url"]),
            preselect_product="Пока не решил", district_ph="Напр. Академический, Верхняя Пышма",
            schema_json=schema, metrika_placeholder=True, og_type="article",
            prodbar=PRODBAR, current_slug="", photos=PHOTOS)
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
