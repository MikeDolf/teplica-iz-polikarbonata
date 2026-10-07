# -*- coding: utf-8 -*-
"""Сборка раздела «Доставка дров» (fanline.su/dostavka-drov/).

Запуск:  python3 _drova-build/build.py

Шаблоны: свои в templates/, остальное берётся из сборки грунта
(_ekb-build/templates): base.html со счётчиком, целями, MAX и запасной
формой, нижняя панель, всплывающий блок. Шапка, подвал, форма заявки и
окно «Не открылся MAX?» берутся у грунта и на лету правятся под дрова
(DictLoader ниже) — так исправления в грунте приходят сюда сами.

Пишет страницы, sitemap-dostavka-drov.xml, свой блок в sitemap.xml
(чужие записи не трогает) и строку Sitemap в robots.txt.
"""
import os, re, sys, json, copy, datetime
from jinja2 import Environment, FileSystemLoader, DictLoader, ChoiceLoader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EKB = os.path.join(ROOT, "_ekb-build")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(EKB, "data"))

from site_config import SITE as _SITE
from cities import CITIES as EKB_CITIES
import drova_data as D
import drova_texts as T
from drova_more import MORE, MORE_INTENT, KOTEL as MORE_INTENT_KOTEL
from drova_fuel import F as FUELT
import drova_cities as DC
import drova_blog as BL
import drova_cities2 as DC2
D.CITIES = D.CITIES + DC2.NEW
D.CITY_SLUG.update({c[0]: f"drova-{c[0]}" for c in DC2.NEW})
DC.C.update(DC2.C)
DC.C["pervouralsk"]["villages"] += ", Новоуткинск, Прогресс, Коуровка, Слобода, Каменка, Нижнее Село, Трёка, Волыны, Староуткинск, Сабик, Чусовое, Мартьяново"
DC.C["pervouralsk"]["local"] = DC.C["pervouralsk"]["local"] + [
    "Отдельно возим дрова вверх по Чусовой — в Новоуткинск, Коуровку, Слободу, Волыны, Трёку, Староуткинск, Чусовое и Мартьяново. В этих посёлках газа почти нет, дома топят печами, и дрова нужны круглый год. Дрова для этих мест есть всегда, в том числе зимой и весной, когда у других продавцов запасы заканчиваются.",
    "Есть и пиленый горбыль — от 900 рублей за насыпной куб: для бани, летней кухни и растопки. Горбыль можно привезти одной машиной с берёзой."]
DC.C["revda"]["villages"] += ", Дружинино, Бисерть"
from drova_bereza_city import B as BZC
import drova_articles as AR
import drova_art_more as AM
for _s, (_b, _f) in AM.ADD.items():
    AR.A[_s]["body"] = AR.A[_s]["body"] + _b
    AR.A[_s]["faq"] = AR.A[_s]["faq"] + [x for x in _f if x[0] not in {q for q, _ in AR.A[_s]["faq"]}]
AR.A.update(AM.NEW)
import drova_art_more2 as AM2
import drova_art_more3 as AM3
import drova_art_more4 as AM4
import drova_art_more5 as AM5
for _s, (_b, _f) in [*AM2.ADD2.items(), *AM3.ADD3.items(), *AM4.ADD4.items(), *AM5.ADD5.items()]:
    AR.A[_s]["body"] = AR.A[_s]["body"] + _b
    AR.A[_s]["faq"] = AR.A[_s]["faq"] + [x for x in _f if x[0] not in {q for q, _ in AR.A[_s]["faq"]}]
D.ARTICLES = D.ARTICLES + list(AM.NEW)

SITE = copy.deepcopy(_SITE)
SITE["brand"] = "Дрова Доставка"
DOMAIN = SITE["domain"]
TODAY = datetime.date.today()
MONTHS = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]


def ekb_src(name):
    return open(os.path.join(EKB, "templates", name), encoding="utf-8").read()


def must_sub(pattern, repl, s, flags=0):
    s2, n = re.subn(pattern, repl, s, flags=flags)
    assert n, f"шаблон грунта поменялся, не найдено: {pattern[:60]}"
    return s2


def overrides():
    o = {}
    h = ekb_src("partials/header.html")
    h = must_sub(r'<a class="hdr__logo" href="/dostavka-grunta/">', '<a class="hdr__logo" href="/dostavka-drov/">', h)
    o["partials/header.html"] = h
    f = ekb_src("partials/footer.html")
    f = must_sub(r'<p class="ftr__legal">.*?</p>',
                 '<p class="ftr__legal">Доставка дров по {{ site.region_po }}: берёзовые, смешанные, хвойные, осиновые, ольховые, сухие, горбыль, топливные брикеты, пеллеты и уголь. '
                 'Цены ориентировочные: дрова за насыпной кубометр, брикеты, пеллеты и уголь за тонну; точную стоимость с доставкой назовём по заявке.</p>', f, re.S)
    o["partials/footer.html"] = f
    cb = ekb_src("partials/callbar.html")
    cb = must_sub(r"\{\{ cta_base\|default\(''\) \}\}#calc-title", "{{ calc_base|default(cta_base|default('')) }}#calc-title", cb)
    o["partials/callbar.html"] = cb
    lf = ekb_src("partials/lead_form.html")
    names = [D.PRODUCTS[k]["name"] for k in D.ORDER] + [D.FUEL[k]["name"] for k in D.FUEL_ORDER]
    lf = must_sub(r'\{%- set products = \[.*?\] %\}', "{%- set products = " + json.dumps(names, ensure_ascii=False) + " %}", lf, re.S)
    lf = must_sub(r'"Сайт доставки грунта"', '"Сайт доставки дров"', lf)
    lf = must_sub(r'\(form\.product\.value\|\|"грунт"\)', '(form.product.value||"дрова")', lf)
    lf = must_sub(r'value="\{\{ min_volume\.split\(\' \'\)\[0\] \}\}"', 'value="5"', lf)
    units = {D.FUEL[k]["name"]: D.FUEL[k]["unit"] for k in D.FUEL_ORDER}
    lf = must_sub(r'<label class="field__label" for="lead-volume">Объём, м³</label>',
                  '<label class="field__label" for="lead-volume">Объём, <span id="lead-unit">м³</span></label>', lf)
    lf = must_sub(r"var volumeText = form\.volume\.value \? form\.volume\.value \+ ' м³' : 'объём не указан';",
                  "var volumeText = form.volume.value ? form.volume.value + ' ' + leadUnit() : 'объём не указан';", lf)
    lf = must_sub(r"var ENDPOINT = ",
                  "var UNITS = " + json.dumps(units, ensure_ascii=False) + ";\n  function leadUnit(){ var f=document.getElementById('lead-product'); return (f && UNITS[f.value]) || 'м³'; }\n"
                  "  (function(){ var f=document.getElementById('lead-product'), u=document.getElementById('lead-unit'), v=document.getElementById('lead-volume');\n"
                  "    function sync(init){ var x=leadUnit(); if(u) u.textContent=x; if(v && (init || v.dataset.auto)){ v.value = x==='т' ? 1 : (x==='кг' ? 10 : 5); v.dataset.auto='1'; } }\n"
                  "    if(f){ f.addEventListener('change', function(){ sync(false); }); sync(true); }\n"
                  "    if(v){ v.addEventListener('input', function(){ delete v.dataset.auto; }); } })();\n  var ENDPOINT = ", lf)
    o["partials/lead_form.html"] = lf
    mf = ekb_src("partials/max_fallback.html")
    mf = must_sub(r"'Сайт доставки грунта'", "'Сайт доставки дров'", mf)
    o["partials/max_fallback.html"] = mf
    fc = ekb_src("partials/floatcta.html")
    fc = must_sub(r"Калькулятор посчитает объём и рейс до вашего адреса — можно прикинуть заранее",
                  "Калькулятор посчитает стоимость дров по объёму, доставку назовём в ответ на заявку", fc)
    o["partials/floatcta.html"] = fc
    return o


env = Environment(loader=ChoiceLoader([DictLoader(overrides()),
                                      FileSystemLoader(os.path.join(HERE, "templates")),
                                      FileSystemLoader(os.path.join(EKB, "templates"))]),
                  autoescape=True, trim_blocks=False, lstrip_blocks=False)
env.filters["ru"] = lambda n: f"{int(n):,}".replace(",", " ")
env.filters["ucfirst"] = lambda v: (v[:1].upper() + v[1:]) if v else v

PAGES = []   # (path, robots-индекс) для карты


def write(path, html):
    full = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)
    PAGES.append(path)


def schema(h1, path, faq, price=None, crumbs=True):
    g = []
    if crumbs:
        g.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
            {"@type": "ListItem", "position": 2, "name": h1, "item": DOMAIN + path}]})
    if price:
        g.append({"@type": "Product", "name": h1, "url": DOMAIN + path, "image": DOMAIN + "/img/og-cover.jpg",
                  "offers": {"@type": "AggregateOffer", "lowPrice": price, "priceCurrency": "RUB",
                             "availability": "https://schema.org/InStock"}})
    if faq:
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                  "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)


def price_rows():
    return [{"name": D.PRODUCTS[k]["name"], "price": D.PRODUCTS[k]["price"], "url": f'/{D.PRODUCTS[k]["slug"]}/'} for k in D.ORDER]


def fuel_rows():
    return [{"name": D.FUEL[k]["name"], "price": D.FUEL[k]["price"], "unit": D.FUEL[k]["unit"], "url": f'/{D.FUEL[k]["slug"]}/'} for k in D.FUEL_ORDER]


MIN_PRICE = min(D.PRODUCTS[k]["price"] for k in D.ORDER if k != "gorbyl")   # дрова; горбыль отдельно
GORBYL = D.PRODUCTS["gorbyl"]["price"]
PROD_LINKS = [{"url": f'/{D.PRODUCTS[k]["slug"]}/', "text": D.PRODUCTS[k]["name"] + ", от " + env.filters["ru"](D.PRODUCTS[k]["price"]) + " ₽/м³"} for k in D.ORDER] + \
             [{"url": "/drova-kolotye-ekaterinburg/", "text": "Колотые дрова"},
              {"url": "/drova-dlya-bani-ekaterinburg/", "text": "Дрова для бани"},
              {"url": "/drova-dlya-kamina-ekaterinburg/", "text": "Дрова для камина"},
              {"url": "/drova-dlya-kotla-ekaterinburg/", "text": "Дрова для котла"}] + \
             [{"url": f'/{D.FUEL[k]["slug"]}/', "text": D.FUEL[k]["name"] + ", от " + env.filters["ru"](D.FUEL[k]["price"]) + " ₽/" + D.FUEL[k]["unit"]} for k in D.FUEL_ORDER]
CITY_LINKS = [{"url": "/drova-ekaterinburg/", "text": "Дрова в Екатеринбурге"}] + \
             [{"url": f"/{D.CITY_SLUG[c[0]]}/", "text": "Дрова " + c[2]} for c in D.CITIES]
ART_LINKS = [{"url": f"{D.HUB}{s}/", "text": AR.A[s]["h1"]} for s in D.ARTICLES]
FOOTER = [{"url": D.HUB, "text": "Доставка дров"}, {"url": "/drova-ekaterinburg/", "text": "Дрова в Екатеринбурге"},
          {"url": "/drova-berezovye-ekaterinburg/", "text": "Берёзовые дрова"}, {"url": "/drova-dlya-bani-ekaterinburg/", "text": "Дрова для бани"},
          {"url": "/gorbyl-ekaterinburg/", "text": "Горбыль"}, {"url": "/toplivnye-brikety-ekaterinburg/", "text": "Топливные брикеты"},
          {"url": "/ugol-kamennyy-ekaterinburg/", "text": "Каменный уголь"}, {"url": "/dostavka-drov/blog/", "text": "Блог о дровах"}, {"url": "/dostavka-grunta/", "text": "Доставка грунта"}]


def city_secs(key, name, prep, dat):
    c = DC.C[key]
    return [(f"Зона доставки дров: {name} и посёлки вокруг", [f"Кроме самого города привозим дрова в посёлки и сёла до 50 км: {c['villages']}. Если вашего посёлка нет в списке — напишите адрес, проверим.", c["tip"]]),
            (f"Какие дрова берут {prep}", c["local"])] + \
           [(h.format(prep=prep), [x.format(prep=prep, name=name, dat=dat) for x in ps]) for h, ps in DC.GEN]


ART_MONEY = {
    "drova-dlya-kotla-dlitelnogo-goreniya": {"url": "/drova-dlya-kotla-ekaterinburg/", "text": "Купить дрова для котла"},
    "kakie-drova-luchshe-dlya-bani": {"url": "/drova-dlya-bani-ekaterinburg/", "text": "Купить дрова для бани"},
    "vlazhnost-drov": {"url": "/drova-suhie-ekaterinburg/", "text": "Купить сухие дрова"},
    "skolko-gorbylya-v-kube": {"url": "/gorbyl-ekaterinburg/", "text": "Купить горбыль"},
    "teplota-sgoraniya-drov": {"url": "/toplivnye-brikety-ekaterinburg/", "text": "Топливные брикеты"},
    "kakie-drova-luchshe-dlya-otopleniya": {"url": "/drova-berezovye-ekaterinburg/", "text": "Купить берёзовые дрова"},
    "pochemu-drova-treshchat": {"url": "/drova-dlya-kamina-ekaterinburg/", "text": "Дрова для камина"},
}


def ru0(n):
    return env.filters["ru"](n)


def ctx(**kw):
    base = dict(site=SITE, robots="index, follow", hero_photo=None, ads=False, footer_links=FOOTER,
                cta_base="", city={}, preselect_product="", district_ph="Например, Сысерть или Шарташ",
                min_volume="1 м³", zone_text="Екатеринбурга и каждого города, где работаем", band_tone="tint", og_image_alt="Площадка с погрузчиком и самосвалом")
    base.update(kw)
    return base


def money(path, h1, title, desc, hero_sub, price, sections, faq, preselect="", city_prep="", city_text="",
          links=None, links_title="Какие дрова привезём", links2=None, links2_title="", is_hub=False, unit="м³", price_note=None, calc=True, min_text=None):
    faq = faq + [x for x in T.COMMON_FAQ if x[0] not in {q for q, _ in faq}]
    _seen = set(); faq = [x for x in faq if not (x[0] in _seen or _seen.add(x[0]))]
    html = env.get_template("drova_page.html").render(**ctx(
        title=title, description=desc, canonical=DOMAIN + path, h1=h1, hero_sub=hero_sub, price=price,
        sections=sections, faq=faq, price_rows=price_rows(), fuel_rows=fuel_rows(), unit=unit, calc=calc,
        **({"price_note": price_note} if price_note else {}), **({} if calc else {"calc_base": "/drova-ekaterinburg/"}), **({"min_text": min_text} if min_text else {}), self_path=path, preselect_product=preselect,
        city_prep=city_prep, city_text=city_text, links=links or PROD_LINKS, links_title=links_title,
        links2=links2, links2_title=links2_title, is_hub=is_hub,
        schema_json=schema(h1, path, faq, price, crumbs=not is_hub)))
    write(path, html)


def main():
    # Хаб
    money(D.HUB, "Доставка дров по Екатеринбургу и Свердловской области",
          f"Доставка дров по Свердловской области — от {ru0(MIN_PRICE)} ₽/м³",
          f"Дрова с доставкой: берёзовые, смешанные, хвойные, осиновые, ольховые, сухие и горбыль. От {MIN_PRICE} ₽ за насыпной куб, без минимального объёма, до 50 км от каждого города.",
          "Свои дрова всех видов: колотые и чурками, естественной влажности и сухие. Возим самосвалами, без минимального объёма — от одного куба до полной машины.",
          MIN_PRICE, MORE_INTENT["hub"] + T.COMMON, [], links_title="Дрова по видам", links2=CITY_LINKS + ART_LINKS + [{"url": "/dostavka-drov/blog/", "text": "Блог: топка, колка, заготовка, копчение"}], links2_title="Города и статьи", is_hub=True)
    # Екатеринбург, главная коммерческая
    money("/drova-ekaterinburg/", "Купить дрова в Екатеринбурге с доставкой",
          f"Купить дрова в Екатеринбурге недорого — от {ru0(MIN_PRICE)} ₽/м³",
          f"Дрова с доставкой по Екатеринбургу: берёзовые колотые от {D.PRODUCTS['berezovye']['price']} ₽, смешанные, хвойные, ольха, осина, сухие для камина. Без минимального объёма.",
          "Берёзовые, смешанные, хвойные, осиновые, ольховые и сухие дрова, горбыль. Привезём по городу и пригороду до 50 км — и один куб, и полную машину.",
          MIN_PRICE, MORE_INTENT["ekb"] + T.COMMON, [("Сколько стоят дрова в Екатеринбурге?", f"Колотые дрова — от {MIN_PRICE} рублей за насыпной куб, берёзовые — от {D.PRODUCTS['berezovye']['price']}, горбыль — от {GORBYL}. Доставку считаем по километрам."),
                                ("Какие дрова лучше купить?", "Для отопления дома — берёзовые или смешанные, для бани — берёза, ольха или осина, для камина — сухие берёзовые.")],
          city_prep="в Екатеринбурге", links2=CITY_LINKS[1:] + ART_LINKS, links2_title="Другие города и статьи")
    # Товары по Екатеринбургу
    for k in D.ORDER:
        pr = D.PRODUCTS[k]
        t = T.EXTRA["suhie_obsh"] if k == "suhie" else T.P[k]
        f = lambda s: s.format(p=env.filters["ru"](pr["price"]), b=env.filters["ru"](D.PRODUCTS["berezovye"]["price"]))
        money(f'/{pr["slug"]}/', t["h1"], f(t["title"]), f(t["desc"]), t["sub"], pr["price"],
              t["about"] + MORE[k]["sections"] + T.COMMON, [(q, f(a)) for q, a in t["faq"]] + MORE[k]["faq"], preselect=pr["name"],
              links=[l for l in PROD_LINKS if l["url"] != f'/{pr["slug"]}/'], links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Колотые дрова (общая) и дрова для камина
    ru = env.filters["ru"]
    t = T.EXTRA["kolotye"]; pk = D.PRODUCTS[t["price_from"]]["price"]
    f = lambda x: x.format(p=ru(pk), b=ru(D.PRODUCTS["berezovye"]["price"]))
    money(f'/{t["slug"]}/', t["h1"], f(t["title"]), f(t["desc"]), t["sub"], pk, t["about"] + MORE_INTENT["kolotye"] + T.COMMON,
          [(q, f(a)) for q, a in t["faq"]], preselect=D.PRODUCTS[t["preselect"]]["name"],
          links=[l for l in PROD_LINKS if l["url"] != f'/{t["slug"]}/'], links2=CITY_LINKS, links2_title="Возим и в другие города")
    t = T.P["suhie"]; pk = D.PRODUCTS["suhie"]["price"]
    f = lambda x: x.format(p=ru(pk))
    money("/drova-dlya-kamina-ekaterinburg/", t["h1"], f(t["title"]), f(t["desc"]), t["sub"], pk, t["about"] + MORE_INTENT["kamin"] + T.COMMON,
          [(q, f(a)) for q, a in t["faq"]] + [("Какие дрова нельзя для камина?", "Хвойные — стреляют искрами и коптят, и любые сырые — дымят и пачкают стекло.")],
          preselect=D.PRODUCTS["suhie"]["name"], links=[l for l in PROD_LINKS if l["url"] != "/drova-dlya-kamina-ekaterinburg/"],
          links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Брикеты, пеллеты, уголь
    for k in D.FUEL_ORDER:
        fu = D.FUEL[k]; t = FUELT[k]; f = lambda x: x.format(p=ru(fu["price"]))
        note = "Цена за тонну." if fu["unit"] == "т" else "Цена за килограмм."
        money(f'/{fu["slug"]}/', t["h1"], f(t["title"]), f(t["desc"]), t["sub"], fu["price"], t["sections"] + T.COMMON[1:],
              [(q, f(a)) for q, a in t["faq"]], preselect=fu["name"], unit=fu["unit"], price_note=note, calc=False, min_text="и мешок, и полную машину",
              links=[l for l in PROD_LINKS if l["url"] != f'/{fu["slug"]}/'], links_title="Дрова и другое топливо",
              links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Берёзовые колотые в крупных городах
    bz = D.PRODUCTS["berezovye"]["price"]
    for key in T.BEREZA_CITY:
        text = BZC[key]["intro"]
        name, prep, dat = [(c[1], c[2], c[3]) for c in D.CITIES if c[0] == key][0]
        money(f"/drova-berezovye-{key}/", f"Берёзовые дрова колотые {prep} с доставкой",
              f"Берёзовые дрова {prep} — колотые, от {ru(bz)} ₽/м³",
              f"Берёзовые колотые дрова с доставкой {prep} и до 50 км вокруг: от {ru(bz)} ₽ за насыпной куб, естественной влажности и сухие, без минимального объёма.",
              f"Берёза колотая, полено 30-40 см — жаркие дрова для печи, бани и котла. Привезём по {dat} и окрестностям, от одного куба.",
              bz, BZC[key]["sections"] + T.COMMON,
              BZC[key]["faq"] + [(f"Сколько стоят берёзовые дрова {prep}?", f"От {ru(bz)} рублей за насыпной куб колотых, доставку считаем по километрам."),
               ("Есть ли сухие берёзовые дрова?", f"Да, от {ru(D.PRODUCTS['suhie']['price'])} рублей за насыпной куб.")],
              preselect=D.PRODUCTS["berezovye"]["name"], city_prep=prep, city_text=text,
              links=[{"url": f"/{D.CITY_SLUG[key]}/", "text": f"Все дрова {prep}"}] + PROD_LINKS, links_title="Ещё дрова",
              links2=[l for l in CITY_LINKS if l["url"] != f"/{D.CITY_SLUG[key]}/"], links2_title="Другие города")
    # Дрова для бани
    bp = min(D.PRODUCTS[k]["price"] for k in ("berezovye", "osina", "olha"))
    money("/drova-dlya-bani-ekaterinburg/", "Дрова для бани с доставкой в Екатеринбурге",
          f"Купить дрова для бани в Екатеринбурге — от {bp} ₽/м³",
          f"Дрова для бани: берёза, ольха, осина — колотые и сухие. От {bp} ₽ за насыпной куб, доставка по Екатеринбургу и области до 50 км, без минимального объёма.",
          "Берёза для жара и углей, ольха и осина для чистого горения без копоти. Подскажем, что взять под вашу печь.",
          bp, [("Какие дрова лучше для бани", ["Берёзовые дают жар и угли, ольховые горят без копоти и с лёгким ароматом, осиновые чистят дымоход и не темнят стены парной. Удобная схема: прогреть печь берёзой, а последнюю закладку сделать ольхой или осиной. Хвойные для бани не советуем: смола даёт копоть и искры. Подробное сравнение — в статье «Какие дрова лучше для бани»."]),
               ("Сколько дров нужно на баню", ["На одну топку средней бани уходит 0,08-0,12 насыпного куба берёзы. При топке раз в неделю — 4-7 насыпных кубов за год. Для бани берут сухие дрова: сырые долго разгораются и коптят."])] + MORE_INTENT["bani"][:3] + T.COMMON,
          [("Какие дрова лучше для бани?", "Берёза для жара, ольха и осина для чистого горения. Хвойные — только на растопку."),
           ("Сколько кубов дров нужно для бани на год?", "При топке раз в неделю — 4-7 насыпных кубов.")],
          preselect=D.PRODUCTS["berezovye"]["name"], links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Дрова для котла
    bk = D.PRODUCTS["smeshannye"]["price"]
    money("/drova-dlya-kotla-ekaterinburg/", "Дрова для котла с доставкой в Екатеринбурге",
          f"Дрова для котла длительного горения — купить от {ru0(bk)} ₽/м³",
          f"Дрова для твердотопливных котлов и котлов длительного горения: берёза и смешанные, сухие и естественной влажности, полено под вашу топку. От {ru0(bk)} ₽ за насыпной куб.",
          "Берёза и смешанные дрова для пиролизных котлов и котлов верхнего горения. Подберём длину полена под вашу камеру загрузки и привезём по Екатеринбургу и области.",
          bk, MORE_INTENT_KOTEL + T.COMMON,
          [("Какие дрова лучше для котла?", "Сухая берёза или смешанные с преобладанием берёзы. Для пиролизного котла — только сухие, до 20%."),
           ("Можно подобрать длину полена под котёл?", "Да, назовите глубину загрузочной камеры или модель котла."),
           ("Сколько дров нужно котлу на зиму?", "Для дома 100 м² — 15-18 насыпных кубов берёзы за сезон."),
           ("Можно ли топить котёл хвойными дровами?", "Можно, если они сухие, но теплообменник придётся чистить чаще.")],
          preselect=D.PRODUCTS["berezovye"]["name"], links=[l for l in PROD_LINKS], links2=CITY_LINKS + [{"url": f"{D.HUB}drova-dlya-kotla-dlitelnogo-goreniya/", "text": "Статья: дрова для котла длительного горения"}], links2_title="Города и статьи")
    # Города
    for key, name, prep, dat, text in D.CITIES:
        money(f"/{D.CITY_SLUG[key]}/", f"Купить дрова {prep} с доставкой",
              f"Купить дрова {prep} с доставкой — от {ru0(MIN_PRICE)} ₽/м³",
              f"Дрова с доставкой {prep} и до 50 км вокруг: берёзовые колотые от {D.PRODUCTS['berezovye']['price']} ₽, смешанные, ольха, осина, сухие, горбыль. Без минимального объёма.",
              f"Берёзовые, смешанные, хвойные, ольховые, осиновые и сухие дрова, горбыль — привезём по {dat} и до 50 км вокруг. От одного куба.",
              MIN_PRICE, city_secs(key, name, prep, dat) + T.COMMON,
              DC.C[key]["faq"] + [(f"Сколько стоят дрова {prep}?", f"Колотые дрова — от {MIN_PRICE} рублей за насыпной куб, берёзовые — от {D.PRODUCTS['berezovye']['price']}, горбыль — от {GORBYL}. Доставку {prep} считаем по километрам."),
               (f"Возите дрова {prep} без минимального объёма?", "Да, привезём и один куб, и полную машину."),
               (f"Можно заказать {prep} уголь, брикеты или горбыль?", f"Да. Каменный уголь — от {ru0(D.FUEL['ugol']['price'])} ₽ за тонну, топливные брикеты — от {ru0(D.FUEL['brikety']['price'])} ₽ за тонну, пеллеты — от {ru0(D.FUEL['pellety']['price'])} ₽ за тонну, горбыль — от {GORBYL} ₽ за насыпной куб. Можно в одной машине с дровами.")],
              city_prep=prep, city_text=text,
              links=([{"url": f"/drova-berezovye-{key}/", "text": f"Берёзовые колотые {prep}"}] if key in T.BEREZA_CITY else []) + PROD_LINKS,
              links2=[l for l in CITY_LINKS if l["url"] != f"/{D.CITY_SLUG[key]}/"],
              links2_title="Другие города", **{})
    # Статьи
    for i, s in enumerate(D.ARTICLES):
        a = AR.A[s]; path = f"{D.HUB}{s}/"
        html = env.get_template("drova_article.html").render(**ctx(
            title=a["title"], description=a["desc"], canonical=DOMAIN + path, h1=a["h1"], lede=a["lede"],
            body=a["body"], faq=a["faq"], min_price=MIN_PRICE, cta_base="/drova-ekaterinburg/", og_type="article",
            date_iso=TODAY.isoformat(), date_ru=f"{TODAY.day} {MONTHS[TODAY.month-1]} {TODAY.year}",
            related=([ART_MONEY[s]] if s in ART_MONEY else []) + [l for l in ART_LINKS if l["url"] != path] + [{"url": "/drova-ekaterinburg/", "text": "Цены на дрова в Екатеринбурге"}],
            schema_json=json.dumps({"@context": "https://schema.org", "@graph": [
                {"@type": "Article", "headline": a["h1"], "description": a["desc"], "datePublished": TODAY.isoformat(),
                 "mainEntityOfPage": DOMAIN + path, "author": {"@type": "Organization", "name": SITE["brand"]},
                 "publisher": {"@type": "Organization", "name": SITE["brand"]}, "image": DOMAIN + "/img/og-cover.jpg"},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
                    {"@type": "ListItem", "position": 2, "name": a["h1"], "item": DOMAIN + path}]},
                {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in a["faq"]]}]},
                ensure_ascii=False)))
        write(path, html)
    render_blog()
    sitemaps()
    print(f"Дрова: {len(PAGES)} страниц")


BLOG_URL = f"{D.HUB}blog/"
BLOG_DATE = "2026-10-07"


def render_blog():
    """Блог дров: /dostavka-drov/blog/ и посты. Реклама РСЯ — только здесь (ads=True)."""
    nav = [{"url": f"{BLOG_URL}{p['slug']}/", "text": p["short"], "desc": p["desc"].split(".")[0], "group": p["group"]} for p in BL.POSTS]
    groups = [{"title": t, "links": [x for x in nav if x["group"] == g]} for g, t in BL.GROUPS]
    groups = [g for g in groups if g["links"]] + [{"title": "Статьи о выборе и покупке дров", "links": ART_LINKS}]
    hub = DOMAIN + BLOG_URL
    html = env.get_template("drova_blog_index.html").render(**ctx(
        title="Блог о дровах: топка, колка, заготовка, копчение", ads=True,
        description="Статьи о дровах и печах: как топить печь, колоть и пилить дрова, можно ли собирать валежник, чем разжечь мангал и какая щепа лучше для копчения.",
        canonical=hub, h1="Блог о дровах, печах и заготовке", groups=groups,
        lede="Практические статьи для тех, кто топит печь, баню или камин: как колоть и пилить дрова, как правильно топить, что говорит закон о валежнике, чем разжечь мангал и как коптить.",
        schema_json=json.dumps({"@context": "https://schema.org", "@graph": [
            {"@type": "Blog", "name": "Блог о дровах", "url": hub, "inLanguage": "ru-RU"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
                {"@type": "ListItem", "position": 2, "name": "Блог", "item": hub}]}]}, ensure_ascii=False)))
    write(BLOG_URL, html)
    d = datetime.date.fromisoformat(BLOG_DATE)
    for p in BL.POSTS:
        path = f"{BLOG_URL}{p['slug']}/"
        rel = [x for x in nav if x["url"] != path] + ART_LINKS[:4]
        html = env.get_template("drova_article.html").render(**ctx(
            title=p["title"], description=p["desc"], canonical=DOMAIN + path, h1=p["h1"], lede=p["lede"],
            body=p["body"], faq=p["faq"], min_price=MIN_PRICE, cta_base="/drova-ekaterinburg/", og_type="article",
            ads=True, section_url=BLOG_URL, section_name="Блог",
            extra_cta={"url": p["money"][0], "text": p["money"][1] + " →"},
            date_iso=BLOG_DATE, date_ru=f"{d.day} {MONTHS[d.month-1]} {d.year}", related=rel,
            schema_json=json.dumps({"@context": "https://schema.org", "@graph": [
                {"@type": "BlogPosting", "headline": p["h1"], "description": p["desc"], "datePublished": BLOG_DATE,
                 "mainEntityOfPage": DOMAIN + path, "author": {"@type": "Organization", "name": SITE["brand"]},
                 "publisher": {"@type": "Organization", "name": SITE["brand"]}, "image": DOMAIN + "/img/og-cover.jpg",
                 "isPartOf": {"@type": "Blog", "name": "Блог о дровах", "url": DOMAIN + BLOG_URL}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
                    {"@type": "ListItem", "position": 2, "name": "Блог", "item": DOMAIN + BLOG_URL},
                    {"@type": "ListItem", "position": 3, "name": p["short"], "item": DOMAIN + path}]},
                {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in p["faq"]]}]},
                ensure_ascii=False)))
        write(path, html)


def sitemaps():
    urls = [DOMAIN + p for p in PAGES]
    def block(u):
        pr = "0.9" if u.endswith(D.HUB) else ("0.6" if D.HUB in u else "0.8")
        return f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY.isoformat()}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
    head = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    open(os.path.join(ROOT, "sitemap-dostavka-drov.xml"), "w", encoding="utf-8").write(head + "\n".join(block(u) for u in urls) + "\n</urlset>\n")
    main_p = os.path.join(ROOT, "sitemap.xml"); src = open(main_p, encoding="utf-8").read()
    blocks = re.findall(r"  <url>.*?</url>", src, re.S)
    foreign = [b for b in blocks if re.search(r"<loc>(.*?)</loc>", b).group(1) not in urls]
    open(main_p, "w", encoding="utf-8").write(head + "\n".join(foreign + [block(u) for u in urls]) + "\n</urlset>\n")
    rb = os.path.join(ROOT, "robots.txt"); r = open(rb, encoding="utf-8").read()
    line = f"Sitemap: {DOMAIN}/sitemap-dostavka-drov.xml"
    if line not in r:
        open(rb, "w", encoding="utf-8").write(r.rstrip("\n") + "\n" + line + "\n")


if __name__ == "__main__":
    main()
