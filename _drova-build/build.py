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
sys.path.insert(1, EKB)

from site_config import SITE as _SITE
import typo
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
import drova_cities3 as DC3
D.CITIES = D.CITIES + DC3.NEW
D.CITY_SLUG.update({c[0]: f"drova-{c[0]}" for c in DC3.NEW})
DC.C.update(DC3.C)
import drova_cities4 as DC4
D.CITIES = D.CITIES + DC4.NEW
D.CITY_SLUG.update({c[0]: f"drova-{c[0]}" for c in DC4.NEW})
DC.C.update(DC4.C)
import drova_cities5 as DC5   # 9 октября: дальние города (партнёры), см. докстринг
D.CITIES = D.CITIES + DC5.NEW
D.CITY_SLUG.update({c[0]: f"drova-{c[0]}" for c in DC5.NEW})
DC.C.update(DC5.C)
import drova_cities6 as DC6   # 10 октября: посёлки рядом с Екатеринбургом
D.CITIES = D.CITIES + DC6.NEW
D.CITY_SLUG.update({c[0]: f"drova-{c[0]}" for c in DC6.NEW})
DC.C.update(DC6.C)
import drova_more2 as M2
# Список городов в «Доставке» и в вопросе «Куда вы возите дрова?» — из D.CITIES,
# чтобы новый город сам попадал во все страницы.
_CITY_NAMES = ", ".join(c[1] for c in D.CITIES)
T.COMMON = [(h, [x.replace("{cities}", _CITY_NAMES) for x in ps]) for h, ps in T.COMMON]
T.COMMON_FAQ = [(q, a_.replace("{cities}", _CITY_NAMES)) for q, a_ in T.COMMON_FAQ]
DC.C["pervouralsk"]["villages"] += ", Новоуткинск, Прогресс, Коуровка, Слобода, Каменка, Нижнее Село, Трёка, Волыны, Староуткинск, Сабик, Чусовое, Мартьяново"
DC.C["pervouralsk"]["local"] = DC.C["pervouralsk"]["local"] + [
    "Отдельно возим дрова вверх по Чусовой — в Новоуткинск, Коуровку, Слободу, Волыны, Трёку, Староуткинск, Чусовое и Мартьяново. В этих посёлках газа почти нет, дома топят печами, и дрова нужны круглый год. Дрова для этих мест есть всегда, в том числе зимой и весной, когда у других продавцов запасы заканчиваются.",
    "Есть и пиленый горбыль — 3 куба с доставкой от %%gorbyl.t3%% рублей, машина 10 кубов от %%gorbyl.t10%%: для бани, летней кухни и растопки. Горбыль можно привезти одной машиной с берёзой."]
DC.C["revda"]["villages"] += ", Дружинино, Бисерть"
from drova_bereza_city import B as BZC
import drova_more4 as M4   # 10 октября: колка, лесовоз, пеллеты оптом
import drova_more3 as M3   # 9 октября: берёзовые В.Пышма/Невьянск/Арамиль, уголь/брикеты/горбыль по городам, щепа, сетки
BZC.update(M3.BZC_NEW)
T.BEREZA_CITY = list(T.BEREZA_CITY) + [k for k in M3.BZC_NEW if k not in T.BEREZA_CITY]
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
import drova_art_more6 as AM6
for _s, (_after, _secs, _f) in AM6.INS6.items():
    _i = [x[0] for x in AR.A[_s]["body"]].index(_after) + 1   # нет раздела — сборка падает
    AR.A[_s]["body"] = AR.A[_s]["body"][:_i] + _secs + AR.A[_s]["body"][_i:]
    AR.A[_s]["faq"] = AR.A[_s]["faq"] + [x for x in _f if x[0] not in {q for q, _ in AR.A[_s]["faq"]}]
import drova_art_more7 as AM7   # 9 октября: выгрузки по России — вес N кубов, складометры, хранение…
for _s, (_ins, _f) in AM7.INS7.items():
    for _after, _secs in _ins:
        _i = [x[0] for x in AR.A[_s]["body"]].index(_after) + 1
        AR.A[_s]["body"] = AR.A[_s]["body"][:_i] + _secs + AR.A[_s]["body"][_i:]
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
                 'Цены ориентировочные: дрова — за насыпной кубометр с доставкой, брикеты и пеллеты — за тонну, уголь — за мешок и тонну, без доставки. Точную стоимость назовём по заявке.</p>', f, re.S)
    o["partials/footer.html"] = f
    bs = ekb_src("base.html")
    bs = must_sub(r'imagesizes="\(max-width: 900px\) 260px, 100vw"', 'imagesizes="{{ hero_sizes|default(\'(max-width: 900px) 260px, 100vw\') }}"', bs)
    o["base.html"] = bs
    cb = ekb_src("partials/callbar.html")
    cb = must_sub(r"\{\{ cta_base\|default\(''\) \}\}#calc-title", "{{ calc_base|default(cta_base|default('')) }}#calc-title", cb)
    o["partials/callbar.html"] = cb
    lf = ekb_src("partials/lead_form.html")
    names = [D.PRODUCTS[k]["name"] for k in D.ORDER] + [D.FUEL[k]["name"] for k in D.FUEL_ORDER] + [M3.EXTRA[k]["name"] for k in M3.EXTRA_ORDER]
    lf = must_sub(r'\{%- set products = \[.*?\] %\}', "{%- set products = " + json.dumps(names, ensure_ascii=False) + " %}", lf, re.S)
    lf = must_sub(r'<form class="lead__form"', '<form class="lead__form lead__form--drova"', lf)
    lf = must_sub(r'<div class="field">(\s*<label class="field__label" for="lead-product">)', r'<div class="field field--wide">\1', lf)
    lf = must_sub(r'<div class="field">(\s*<label class="field__label" for="lead-district">)', r'<div class="field field--wide">\1', lf)
    lf = must_sub(r'"Сайт доставки грунта"', '"Сайт доставки дров"', lf)
    lf = must_sub(r'\(form\.product\.value\|\|"грунт"\)', '(form.product.value||"дрова")', lf)
    lf = must_sub(r'value="\{\{ min_volume\.split\(\' \'\)\[0\] \}\}"', 'value="3"', lf)
    units = {D.FUEL[k]["name"]: {"мешок": "мешков"}.get(D.FUEL[k]["unit"], D.FUEL[k]["unit"]) for k in D.FUEL_ORDER}
    units.update({M3.EXTRA[k]["name"]: {"сетка": "сеток"}.get(M3.EXTRA[k]["unit"], M3.EXTRA[k]["unit"]) for k in M3.EXTRA_ORDER})
    lf = must_sub(r'<label class="field__label" for="lead-volume">Объём, м³</label>',
                  '<label class="field__label" for="lead-volume">Объём, <span id="lead-unit">м³</span></label>', lf)
    lf = must_sub(r"var volumeText = form\.volume\.value \? form\.volume\.value \+ ' м³' : 'объём не указан';",
                  "var volumeText = form.volume.value ? form.volume.value + ' ' + leadUnit() : 'объём не указан';", lf)
    lf = must_sub(r"var ENDPOINT = ",
                  "var UNITS = " + json.dumps(units, ensure_ascii=False) + ";\n  function leadUnit(){ var f=document.getElementById('lead-product'); return (f && UNITS[f.value]) || 'м³'; }\n"
                  "  (function(){ var f=document.getElementById('lead-product'), u=document.getElementById('lead-unit'), v=document.getElementById('lead-volume');\n"
                  "    function sync(init){ var x=leadUnit(); if(u) u.textContent=x; if(v && (init || v.dataset.auto)){ v.value = x==='т' ? 1 : (x==='кг' || x==='мешков' ? 10 : 3); v.dataset.auto='1'; } }\n"
                  "    if(f){ f.addEventListener('change', function(){ sync(false); }); sync(true); }\n"
                  "    if(v){ v.addEventListener('input', function(){ delete v.dataset.auto; }); } })();\n  var ENDPOINT = ", lf)
    o["partials/lead_form.html"] = lf
    mf = ekb_src("partials/max_fallback.html")
    mf = must_sub(r"'Сайт доставки грунта'", "'Сайт доставки дров'", mf)
    o["partials/max_fallback.html"] = mf
    fc = ekb_src("partials/floatcta.html")
    fc = must_sub(r"Калькулятор посчитает объём и рейс до вашего адреса — можно прикинуть заранее",
                  "Калькулятор посчитает стоимость дров вместе с доставкой — можно прикинуть заранее", fc)
    o["partials/floatcta.html"] = fc
    return o


env = Environment(loader=ChoiceLoader([DictLoader(overrides()),
                                      FileSystemLoader(os.path.join(HERE, "templates")),
                                      FileSystemLoader(os.path.join(EKB, "templates"))]),
                  autoescape=True, trim_blocks=False, lstrip_blocks=False)
env.filters["ru"] = lambda n: f"{int(n):,}".replace(",", " ")   # узкий неразрывный: «3 500» не рвётся
env.filters["ucfirst"] = lambda v: (v[:1].upper() + v[1:]) if v else v

PAGES = []   # (path, robots-индекс) для карты


def _price_token(m):
    """%%berezovye.t3%% — поле товара; %%sum.berezovye.18%% — итог с доставкой за 18 м³;
    %%per.berezovye.3%% — за м³ при 3 м³; %%deliv%% — рейс. Цены — только в drova_data."""
    p = m.group(1).split(".")
    if p[0] == "deliv":
        v = D.DELIVERY
    elif p[0] == "diff":   # %%diff.berezovye.churki.wood%% — насколько колотая берёза дороже чурок
        v = D.PRODUCTS[p[1]][p[3]] - D.PRODUCTS[p[2]][p[3]]
    elif p[0] == "x":   # %%x.ugol.price.40%% — 40 мешков угля; %%x.berezovye.price.1.5%% — складометр
        k = float(".".join(p[3:]))
        v = {**D.PRODUCTS, **D.FUEL, **M3.EXTRA}[p[1]][p[2]] * k
        v = int(v) if k == int(k) else round(v / 50) * 50
    elif p[0] == "sum":
        v = D.total(p[1], int(p[2]))
    elif p[0] == "per":
        v = round(D.total(p[1], int(p[2])) / int(p[2]) / 50) * 50
    elif p[0] in D.PRODUCTS:
        v = D.PRODUCTS[p[0]][p[1]]
    else:
        v = {**D.FUEL, **M3.EXTRA}[p[0]][p[1]]
    return env.filters["ru"](v)


def write(path, html):
    html = re.sub(r"%%([\w.-]+)%%", _price_token, html)
    assert "%%" not in html, path
    html = typo.glue(html)   # «50 км», «3 м³», «₽/м³» — без отрыва единиц
    full = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)
    PAGES.append(path)


def stable(s):
    import hashlib
    return hashlib.md5(s.encode()).hexdigest()


def schema(h1, path, faq, price=None, crumbs=True, high=None, count=None):
    g = []
    if crumbs:
        g.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
            {"@type": "ListItem", "position": 2, "name": h1, "item": DOMAIN + path}]})
    if price:
        g.append({"@type": "Product", "name": h1, "url": DOMAIN + path, "image": DOMAIN + "/img/og-cover.jpg",
                  "offers": {"@type": "AggregateOffer", "lowPrice": price, "priceCurrency": "RUB",
                             **({"highPrice": high} if high else {}), **({"offerCount": count} if count else {}),
                             "availability": "https://schema.org/InStock"}})
    if faq:
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                  "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)


def price_rows():
    return [dict(D.PRODUCTS[k], url=f'/{D.PRODUCTS[k]["slug"]}/') for k in D.ORDER]


def fuel_rows():
    return [{"name": D.FUEL[k]["name"], "price": D.FUEL[k]["price"], "unit": D.FUEL[k].get("unit_long", D.FUEL[k]["unit"]),
             "price_t": D.FUEL[k].get("price_t"), "url": f'/{D.FUEL[k]["slug"]}/'} for k in D.FUEL_ORDER]


MIN_PRICE = min(D.PRODUCTS[k]["price"] for k in D.ORDER if k != "gorbyl")   # дрова; горбыль отдельно
GORBYL = D.PRODUCTS["gorbyl"]["price"]
PROD_LINKS = [{"url": f'/{D.PRODUCTS[k]["slug"]}/', "text": D.PRODUCTS[k]["name"] + ", от " + env.filters["ru"](D.PRODUCTS[k]["price"]) + " ₽/м³"} for k in D.ORDER] + \
             [{"url": "/drova-kolotye-ekaterinburg/", "text": "Колотые дрова"},
              {"url": "/drova-dlya-bani-ekaterinburg/", "text": "Дрова для бани"},
              {"url": "/drova-dlya-kamina-ekaterinburg/", "text": "Дрова для камина"},
              {"url": "/drova-dlya-kotla-ekaterinburg/", "text": "Дрова для котла"},
              {"url": "/drova-dlya-pechi-ekaterinburg/", "text": "Дрова для печи"},
              {"url": "/drova-nedorogo-ekaterinburg/", "text": "Недорогие дрова"}] + \
             [{"url": f'/{D.FUEL[k]["slug"]}/', "text": D.FUEL[k]["name"] + ", от " + env.filters["ru"](D.FUEL[k]["price"]) + " ₽/" + D.FUEL[k]["unit"]} for k in D.FUEL_ORDER] + \
             [{"url": f'/{M3.EXTRA[k]["slug"]}/', "text": M3.EXTRA[k]["name"] + ", от " + env.filters["ru"](M3.EXTRA[k]["price"]) + " ₽/" + M3.EXTRA[k]["unit"]} for k in M3.EXTRA_ORDER] + \
             [{"url": "/kolka-drov-ekaterinburg/", "text": "Колка дров у вас во дворе"}, {"url": "/drova-lesovozom-ekaterinburg/", "text": "Дрова лесовозом"}]
# уголь, брикеты, пеллеты и горбыль по городам: ссылки со страниц городов и общих страниц товара
_CF_KIND = {"ugol": "Каменный уголь", "brikety": "Топливные брикеты", "gorbyl": "Горбыль", "pellety": "Пеллеты"}
CF_BY_CITY, CF_BY_KIND = {}, {}
for _c in M3.CITY_FUEL:
    _prep = [c[2] for c in D.CITIES if c[0] == _c["city"]][0]
    _l = {"url": f'/{_c["slug"]}/', "text": f'{_CF_KIND[_c["kind"]]} {_prep}'}
    CF_BY_CITY.setdefault(_c["city"], []).append(_l); CF_BY_KIND.setdefault(_c["kind"], []).append(_l)
CITY_LINKS = [{"url": "/drova-ekaterinburg/", "text": "Дрова в Екатеринбурге"}] + \
             [{"url": f"/{D.CITY_SLUG[c[0]]}/", "text": "Дрова " + c[2]} for c in D.CITIES]
BEREZA_LINKS = [{"url": f"/drova-berezovye-{k}/", "text": "Берёзовые дрова " + [c[2] for c in D.CITIES if c[0] == k][0]} for k in T.BEREZA_CITY]
ART_LINKS = [{"url": f"{D.HUB}{s}/", "text": AR.A[s]["h1"]} for s in D.ARTICLES]
FOOTER = [{"url": D.HUB, "text": "Доставка дров"}, {"url": "/drova-ekaterinburg/", "text": "Дрова в Екатеринбурге"},
          {"url": "/drova-berezovye-ekaterinburg/", "text": "Берёзовые дрова"}, {"url": "/drova-dlya-bani-ekaterinburg/", "text": "Дрова для бани"},
          {"url": "/gorbyl-ekaterinburg/", "text": "Горбыль"}, {"url": "/toplivnye-brikety-ekaterinburg/", "text": "Топливные брикеты"},
          {"url": "/ugol-kamennyy-ekaterinburg/", "text": "Каменный уголь"}, {"url": "/dostavka-drov/blog/", "text": "Блог о дровах"}, {"url": "/dostavka-grunta/", "text": "Доставка грунта"}]


def city_secs(key, name, prep, dat):
    c = DC.C[key]
    return [(f"Зона доставки дров: {name} и посёлки вокруг", [f"Кроме самого города привозим дрова в посёлки и сёла до 50 км: {c['villages']}. Если вашего посёлка нет в списке — напишите адрес, проверим.", c["tip"]]),
            (f"Какие дрова берут {prep}", c["local"])] + c.get("extra", []) + \
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


ART_PUB = "2026-10-06"   # раздел и статьи опубликованы 6 октября
ART_UPD = "2026-10-07"   # статьи дописаны до ~1300-1500 слов
ART_UPD_X = {"skladometr-ili-nasypnoy-kub": "2026-10-09"}   # + раздел про ГАЗель и КамАЗ
ART_UPD_X.update({_s: AM7.ART_UPD_7 for _s in AM7.INS7})
ART_REL_X = {"teplota-sgoraniya-drov": [{"url": "/dostavka-drov/blog/udelnaya-teplota-sgoraniya-drov/", "text": "Удельная теплота сгорания дров: таблица и задачи"}]}


def offer_range(price, unit, ex):
    """highPrice/offerCount для AggregateOffer. Дрова: страница вида — от цены машины до цены
    одного куба этого вида (3 варианта объёма); сводные — по всем видам. Топливо — одно предложение
    (у угля — от мешка до тонны)."""
    if unit == "м³":
        p = D.PRODUCTS[ex]
        if price == p["price"]:
            return {"high": p["t1"], "count": 3}
        return {"high": max(D.PRODUCTS[k]["t1"] for k in D.ORDER), "count": len(D.ORDER)}
    f = next(v for v in [*D.FUEL.values(), *M3.EXTRA.values()] if v["price"] == price)
    return {"high": f.get("price_t") or price, "count": 2 if f.get("price_t") else 1}


def ru_d(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month-1]} {d.year}"


def price_answer(prep="в Екатеринбурге", near=True):
    """Ответ «сколько стоят дрова» в модели «цена с доставкой»."""
    b, h, g = D.PRODUCTS["berezovye"], D.PRODUCTS["hvoynye"], D.PRODUCTS["gorbyl"]
    tail = " Цена примерно та же, что в Екатеринбурге: возим с ближайшей к вам площадки." if not near else ""
    return (f"С доставкой {prep}: берёзовые колотые — 1 куб от {ru0(b['t1'])} ₽, 3 куба от {ru0(b['t3'])} ₽, "
            f"машина {D.REF_VOL} кубов от {ru0(b['t10'])} ₽ (≈{ru0(b['price'])} ₽/м³). Хвойные — машина от {ru0(h['t10'])} ₽, "
            f"горбыль — от {ru0(g['t10'])} ₽. Минимального заказа нет.{tail}")


def fuel_answer():
    u, br, pe = D.FUEL["ugol"], D.FUEL["brikety"], D.FUEL["pellety"]
    return (f"Да. Каменный уголь — от {ru0(u['price'])} ₽ за мешок 25 кг или от {ru0(u['price_t'])} ₽ за тонну, "
            f"топливные брикеты — от {ru0(br['price'])} ₽ за тонну, пеллеты — от {ru0(pe['price'])} ₽ за тонну. "
            f"Цены топлива без доставки; вместе с дровами привезём одним рейсом.")


def ins_after(sections, after, new):
    i = [h for h, _ in sections].index(after) + 1
    return sections[:i] + new + sections[i:]


def ru0(n):
    return env.filters["ru"](n)


def ctx(**kw):
    base = dict(site=SITE, robots="index, follow", hero_photo=None, ads=False, footer_links=FOOTER,
                cta_base="", city={}, preselect_product="", district_ph="Например, Сысерть или Шарташ",
                min_volume="1 м³", zone_text="Екатеринбурга и каждого города, где работаем", band_tone="tint", og_image_alt="Площадка с погрузчиком и самосвалом")
    base.update(kw)
    return base


def money(path, h1, title, desc, hero_sub, price, sections, faq, preselect="", city_prep="", city_text="",
          links=None, links_title="Какие дрова привезём", links2=None, links2_title="", is_hub=False, unit="м³", price_note=None, calc=True, min_text=None, ex="berezovye", deliv_po=None, xtables=None,
          hero_min=None, common_faq=True):
    # price=None — цена по заявке (услуги): в герое «по заявке», в разметке без Product/Offer
    if calc and "₽/м³" in title and "доставк" not in title.lower() and len(title) + 12 <= 70:
        title = title.replace("₽/м³", "₽/м³ с доставкой")
    faq = faq + ([x for x in T.COMMON_FAQ if x[0] not in {q for q, _ in faq}] if common_faq else [])
    _seen = set(); faq = [x for x in faq if not (x[0] in _seen or _seen.add(x[0]))]
    html = env.get_template("drova_page.html").render(**ctx(
        hero_photo="hero-drova", hero_alt="Поленница колотых берёзовых дров на опушке леса",
        hero_sizes="(max-width: 900px) 800px, 100vw",
        title=title, description=desc, canonical=DOMAIN + path, h1=h1, hero_sub=hero_sub, price=price,
        sections=sections, faq=faq, price_rows=price_rows(), fuel_rows=fuel_rows(), unit=unit, calc=calc,
        ex=D.PRODUCTS[ex], ref_vol=D.REF_VOL, delivery=D.DELIVERY, trip_m3=D.TRIP_M3, **({"deliv_po": deliv_po} if deliv_po else {}),
        **({"price_note": price_note} if price_note else {}), **({} if calc else {"calc_base": "/drova-ekaterinburg/"}), **({"min_text": min_text} if min_text else {}), **({"hero_min": hero_min} if hero_min else {}), self_path=path, preselect_product=preselect,
        city_prep=city_prep, city_text=city_text, links=links or PROD_LINKS, links_title=links_title,
        links2=links2, links2_title=links2_title, is_hub=is_hub, xtables=xtables or [],
        schema_json=schema(h1, path, faq, price, crumbs=not is_hub, **(offer_range(price, unit, ex) if price else {}))))
    write(path, html)


def main():
    # Хаб
    money(D.HUB, "Доставка дров по Екатеринбургу и Свердловской области",
          f"Доставка дров по Свердловской области — купить от {ru0(MIN_PRICE)} ₽/м³",
          f"Дрова с доставкой: берёза, смешанные, хвойные, осина, ольха, сухие, горбыль. От {ru0(MIN_PRICE)} ₽/м³ с доставкой, 3 куба берёзы — от {ru0(D.PRODUCTS['berezovye']['t3'])} ₽. Без минимального объёма.",
          "Свои дрова всех видов: колотые и чурками, естественной влажности и сухие. Возим самосвалами, без минимального объёма — от одного куба до полной машины.",
          MIN_PRICE, MORE_INTENT["hub"] + [x for x in T.COMMON if x[0] != "Насыпной куб и складометр"], [], links_title="Дрова по видам", links2=CITY_LINKS + BEREZA_LINKS + [l for v in CF_BY_KIND.values() for l in v] + ART_LINKS + [{"url": "/dostavka-drov/blog/", "text": "Блог: топка, колка, заготовка, копчение"}], links2_title="Города и статьи", is_hub=True)
    # Екатеринбург, главная коммерческая. 9 октября: под «куб дров» (2,6 тыс.), «цена куба»,
    # «где купить», «заказать», «ГАЗель дров» — таблица по объёмам и новые разделы; «недорого»
    # из заголовка ушло на отдельную страницу «Недорогие дрова», чтобы страницы не спорили.
    _ekb = dict(M2.EKB_NEW, **{h: ps for h, ps in MORE_INTENT["ekb"] if h not in M2.EKB_NEW})
    _bz = D.PRODUCTS["berezovye"]
    _kub = lambda v: f"{v} " + ("куб" if v % 10 == 1 and v % 100 != 11 else "куба" if v % 10 in (2, 3, 4) and v % 100 not in (12, 13, 14) else "кубов")
    cubes = {"title": "Сколько стоит 1, 3, 5 и 10 кубов дров с доставкой",
             "head": ["Объём", "Берёзовые колотые", "Смешанные колотые"],
             "rows": [[_kub(v), f"от {ru0(D.total('berezovye', v))} ₽", f"от {ru0(D.total('smeshannye', v))} ₽"] for v in M2.CUBE_VOLS],
             "note": f"Цены с доставкой по Екатеринбургу. В одну машину входит до {D.TRIP_M3} кубов, и до этого объёма рейс один, поэтому каждый следующий куб дешевле: "
                     f"1 куб берёзы — от {ru0(_bz['t1'])} ₽, а в машине {D.REF_VOL} кубов — около {ru0(_bz['price'])} ₽ за куб. Больше {D.TRIP_M3} кубов везём двумя рейсами."}
    money("/drova-ekaterinburg/", "Купить дрова в Екатеринбурге с доставкой",
          f"Купить дрова в Екатеринбурге: цена за куб от {ru0(MIN_PRICE)} ₽ с доставкой",
          f"Дрова с доставкой по Екатеринбургу: 1 куб берёзы — от {ru0(_bz['t1'])} ₽, 3 куба — от {ru0(_bz['t3'])} ₽, машина — от {ru0(_bz['price'])} ₽/м³. Смешанные, хвойные, ольха, сухие. Без минимального объёма.",
          "Берёзовые, смешанные, хвойные, осиновые, ольховые и сухие дрова, горбыль. Привезём по городу и пригороду до 50 км — и один куб, и полную машину.",
          MIN_PRICE, [(h, _ekb[h]) for h in M2.EKB_ORDER] + T.COMMON,
          [("Сколько стоит куб дров в Екатеринбурге?", price_answer()),
           ("Какие дрова лучше купить?", "Для отопления дома — берёзовые или смешанные, для бани — берёза, ольха или осина, для камина — сухие берёзовые.")] + M2.EKB_FAQ + M2.EKB_FAQ_ADD,
          city_prep="в Екатеринбурге", links2=CITY_LINKS[1:] + ART_LINKS, links2_title="Другие города и статьи", xtables=[cubes])
    # Товары по Екатеринбургу
    for k in D.ORDER:
        pr = D.PRODUCTS[k]
        t = dict(T.EXTRA["suhie_obsh"] if k == "suhie" else T.P[k], **M2.PRODUCT_META.get(k, {}))
        f = lambda s: s.format(p=env.filters["ru"](pr["price"]), b=env.filters["ru"](D.PRODUCTS["berezovye"]["price"]),
                               **{x: env.filters["ru"](pr[x]) for x in ("t1", "t3", "t10")})
        money(f'/{pr["slug"]}/', t["h1"], f(t["title"]), f(t["desc"]), t["sub"], pr["price"],
              (ins_after(t["about"] + MORE[k]["sections"], *M2.PRODUCT_ADD[k][:2]) if k in M2.PRODUCT_ADD else t["about"] + MORE[k]["sections"]) + T.COMMON,
              [(q, f(a)) for q, a in t["faq"]] + MORE[k]["faq"] + (M2.PRODUCT_ADD[k][2] if k in M2.PRODUCT_ADD else []), preselect=pr["name"], ex=k,
              links=[l for l in PROD_LINKS if l["url"] != f'/{pr["slug"]}/'],
              links2=(BEREZA_LINKS if k == "berezovye" else []) + CF_BY_KIND.get(k, []) + CITY_LINKS,
              links2_title="Берёзовые дрова в городах и другие города" if k == "berezovye" else "Возим и в другие города")
    # Колотые дрова (общая) и дрова для камина
    ru = env.filters["ru"]
    t = T.EXTRA["kolotye"]; pk = D.PRODUCTS[t["price_from"]]["price"]
    _pf = D.PRODUCTS[t["price_from"]]
    f = lambda x: x.format(p=ru(pk), b=ru(D.PRODUCTS["berezovye"]["price"]), **{y: ru(_pf[y]) for y in ("t1", "t3", "t10")})
    money(f'/{t["slug"]}/', t["h1"], f(t["title"]), f(t["desc"]), t["sub"], pk, t["about"] + MORE_INTENT["kolotye"] + T.COMMON,
          [(q, f(a)) for q, a in t["faq"]], preselect=D.PRODUCTS[t["preselect"]]["name"], ex=t["price_from"],
          links=[l for l in PROD_LINKS if l["url"] != f'/{t["slug"]}/'], links2=CITY_LINKS, links2_title="Возим и в другие города")
    t = T.P["suhie"]; pk = D.PRODUCTS["suhie"]["price"]
    f = lambda x: x.format(p=ru(pk), **{y: ru(D.PRODUCTS["suhie"][y]) for y in ("t1", "t3", "t10")})
    money("/drova-dlya-kamina-ekaterinburg/", t["h1"], f(t["title"]), f(t["desc"]), t["sub"], pk, t["about"] + MORE_INTENT["kamin"] + T.COMMON,
          [(q, f(a)) for q, a in t["faq"]] + [("Какие дрова нельзя для камина?", "Хвойные — стреляют искрами и коптят, и любые сырые — дымят и пачкают стекло.")] + M2.KAMIN_FAQ_ADD,
          preselect=D.PRODUCTS["suhie"]["name"], ex="suhie", links=[l for l in PROD_LINKS if l["url"] != "/drova-dlya-kamina-ekaterinburg/"],
          links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Брикеты, пеллеты, уголь
    for k in D.FUEL_ORDER:
        fu = D.FUEL[k]; t = dict(FUELT[k], **M2.FUEL_META.get(k, {})); f = lambda x: x.format(p=ru(fu["price"]), pt=ru(fu.get("price_t") or 0))
        if k in M2.FUEL_ADD:   # 9 октября: уголь для мангала, RUF и Pini-Kay, уголь в мешках
            _after, _secs, _faq = M2.FUEL_ADD[k]
            t["sections"] = ins_after(t["sections"], _after, _secs); t["faq"] = t["faq"] + _faq
        if k == "pellety":   # 10 октября: оптом от поддона (владелец), «от производителя» не пишем
            t["sections"] = ins_after(t["sections"], M4.PELLETY_OPT[0], M4.PELLETY_OPT[1]); t["faq"] = t["faq"] + M4.PELLETY_OPT[2]; t["h1"] = M4.PELLETY_H1
        if k == "brikety":   # евродрова — другое название древесных брикетов
            t["desc"] = t["desc"].replace("Топливные брикеты RUF", "Топливные брикеты (евродрова) RUF", 1); t["faq"] = t["faq"] + M3.BRIKETY_EVRO_FAQ
        note = {"т": "Цена за тонну, без доставки.", "кг": "Цена за килограмм, без доставки.",
                "мешок": f"Цена за мешок 25 кг, без доставки. Тонна навалом — от {ru0(fu.get('price_t') or 0)} ₽."}[fu["unit"]]
        note += " Доставку назовём по адресу, вместе с дровами привезём одним рейсом."
        money(f'/{fu["slug"]}/', t["h1"], f(t["title"]), f(t["desc"]), t["sub"], fu["price"], t["sections"] + T.COMMON[1:],
              [(q, f(a)) for q, a in t["faq"]], preselect=fu["name"], unit=fu["unit"], price_note=note, calc=False, min_text="и мешок, и полную машину",
              links=[l for l in PROD_LINKS if l["url"] != f'/{fu["slug"]}/'], links_title="Дрова и другое топливо",
              links2=CF_BY_KIND.get(k, []) + CITY_LINKS, links2_title="Возим и в другие города")
    # Уголь, брикеты, пеллеты и горбыль по городам (9 октября, M3.CITY_FUEL)
    for c in M3.CITY_FUEL:
        name, prep, dat = [(x[1], x[2], x[3]) for x in D.CITIES if x[0] == c["city"]][0]
        city_l = [{"url": f'/{D.CITY_SLUG[c["city"]]}/', "text": f"Все дрова {prep}"}] + [l for l in CF_BY_CITY[c["city"]] if l["url"] != f'/{c["slug"]}/'] + \
                 ([{"url": f'/drova-berezovye-{c["city"]}/', "text": f"Берёзовые колотые {prep}"}] if c["city"] in T.BEREZA_CITY else [])
        if c["kind"] == "gorbyl":
            g = D.PRODUCTS["gorbyl"]; fmt = lambda x: x.format(p=ru(g["price"]), t3=ru(g["t3"]), t10=ru(g["t10"]))
            money(f'/{c["slug"]}/', c["h1"], fmt(c["title"]), fmt(c["desc"]), c["sub"], g["price"],
                  [(f"Горбыль {prep}", [c["intro"]])] + c["sections"] + T.COMMON, c["faq"], preselect=g["name"], ex="gorbyl",
                  city_prep=prep, deliv_po=dat, links=city_l + [{"url": "/gorbyl-ekaterinburg/", "text": "Горбыль в Екатеринбурге"}] + PROD_LINKS,
                  links_title="Ещё дрова", links2=[l for l in CITY_LINKS if l["url"] != city_l[0]["url"]], links2_title="Другие города")
        else:
            fu = D.FUEL[c["kind"]]; fmt = lambda x: x.format(p=ru(fu["price"]), pt=ru(fu.get("price_t") or 0))
            note = {"т": "Цена за тонну, без доставки.", "мешок": f"Цена за мешок 25 кг, без доставки. Тонна навалом — от {ru0(fu.get('price_t') or 0)} ₽."}[fu["unit"]]
            note += " Доставку назовём по адресу, вместе с дровами привезём одним рейсом."
            money(f'/{c["slug"]}/', c["h1"], fmt(c["title"]), fmt(c["desc"]), c["sub"], fu["price"],
                  [(f'{_CF_KIND[c["kind"]]} {prep}', [c["intro"]])] + c["sections"] + T.COMMON[1:], c["faq"], preselect=fu["name"],
                  unit=fu["unit"], price_note=note, calc=False, min_text="и мешок, и полную машину", city_prep=prep,
                  links=city_l + [{"url": f'/{fu["slug"]}/', "text": f'{fu["name"]} в Екатеринбурге'}] + PROD_LINKS, links_title="Дрова и другое топливо",
                  links2=[l for l in CITY_LINKS if l["url"] != city_l[0]["url"]], links2_title="Другие города")
    # Щепа для копчения и дрова в сетках
    for k in M3.EXTRA_ORDER:
        ex_ = M3.EXTRA[k]; t = M3.EXTRA_PAGES[k]; fmt = lambda x: x.format(p=ru(ex_["price"]))
        note = {"кг": "Цена за килограмм в мешках, без доставки.", "сетка": "Цена за сетку около 10 кг, без доставки."}[ex_["unit"]]
        note += " Доставку назовём по адресу, вместе с дровами привезём одним рейсом."
        money(f'/{ex_["slug"]}/', t["h1"], fmt(t["title"]), fmt(t["desc"]), t["sub"], ex_["price"], t["sections"] + T.COMMON[1:], t["faq"],
              preselect=ex_["name"], unit=ex_["unit"], price_note=note, calc=False, min_text={"кг": "и мешок, и оптом", "сетка": "и пару сеток, и оптом"}[ex_["unit"]],
              links=[l for l in PROD_LINKS if l["url"] != f'/{ex_["slug"]}/'], links_title="Дрова и другое топливо",
              links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Колка дров и дрова лесовозом — услуги с ценой по заявке (10 октября, M4)
    for k in M4.SERVICE_ORDER:
        t = M4.SERVICES[k]; path = f'/{t["slug"]}/'
        kl = [{"url": "/drova-churkami-ekaterinburg/", "text": "Берёзовые дрова чурками"}, {"url": "/drova-kolotye-ekaterinburg/", "text": "Колотые дрова"}]
        money(path, t["h1"], t["title"], t["desc"], t["sub"], None, t["sections"], t["faq"], price_note=t["price_note"], calc=False,
              hero_min=t["hero_min"], common_faq=False, links=kl + [l for l in PROD_LINKS if l["url"] != path and l["url"] not in {x["url"] for x in kl}],
              links_title="Дрова и услуги", links2=[{"url": f"{D.HUB}blog/skolko-stoit-raskolot-drova/", "text": "Сколько стоит расколоть дрова"},
              {"url": f"{D.HUB}blog/kak-pravilno-kolot-drova/", "text": "Как правильно колоть дрова"}, {"url": f"{D.HUB}blog/kak-slozhit-polennitsu/", "text": "Как сложить поленницу"},
              {"url": f"{D.HUB}skladometr-ili-nasypnoy-kub/", "text": "Складометр и насыпной куб"}] + CITY_LINKS, links2_title="Статьи и города")
    # Берёзовые колотые в крупных городах
    bz = D.PRODUCTS["berezovye"]["price"]
    for key in T.BEREZA_CITY:
        text = BZC[key]["intro"]
        name, prep, dat = [(c[1], c[2], c[3]) for c in D.CITIES if c[0] == key][0]
        money(f"/drova-berezovye-{key}/", f"Берёзовые дрова колотые {prep} с доставкой",
              next(t for t in (f"Купить берёзовые дрова {prep} — колотые, цена от {ru(bz)} ₽/м³", f"Купить берёзовые дрова {prep} — цена от {ru(bz)} ₽/м³") if len(t) <= 70),
              f"Берёзовые колотые дрова с доставкой {prep} и вокруг: 3 куба — от {ru(D.PRODUCTS['berezovye']['t3'])} ₽, машина — от {ru(bz)} ₽/м³. Естественной влажности и сухие, от одного куба.",
              f"Берёза колотая, полено 30-40 см — жаркие дрова для печи, бани и котла. Привезём по {dat} и окрестностям, от одного куба.",
              bz, BZC[key]["sections"] + T.COMMON,
              BZC[key]["faq"] + [(f"Сколько стоят берёзовые дрова {prep}?", f"С доставкой {prep}: 1 куб — от {ru(D.PRODUCTS['berezovye']['t1'])} ₽, 3 куба — от {ru(D.PRODUCTS['berezovye']['t3'])} ₽, машина {D.REF_VOL} кубов — от {ru(D.PRODUCTS['berezovye']['t10'])} ₽ (≈{ru(bz)} ₽/м³). Цена примерно та же, что в Екатеринбурге: возим с ближайшей площадки."),
               ("Есть ли сухие берёзовые дрова?", f"Да, 3 куба сухих с доставкой — от {ru(D.PRODUCTS['suhie']['t3'])} ₽.")],
              preselect=D.PRODUCTS["berezovye"]["name"], city_prep=prep, city_text=text, deliv_po=dat,
              links=[{"url": f"/{D.CITY_SLUG[key]}/", "text": f"Все дрова {prep}"}] + CF_BY_CITY.get(key, []) + PROD_LINKS, links_title="Ещё дрова",
              links2=[l for l in CITY_LINKS if l["url"] != f"/{D.CITY_SLUG[key]}/"], links2_title="Другие города")
    # Дрова для бани
    bk_ = min(("berezovye", "osina", "olha"), key=lambda k: D.PRODUCTS[k]["price"]); bp = D.PRODUCTS[bk_]["price"]
    money("/drova-dlya-bani-ekaterinburg/", "Дрова для бани с доставкой в Екатеринбурге",
          f"Купить дрова для бани в Екатеринбурге — от {ru0(bp)} ₽/м³",
          f"Дрова для бани: берёза, ольха, осина — колотые и сухие. От {ru0(bp)} ₽/м³ с доставкой по Екатеринбургу и области, без минимального объёма.",
          "Берёза для жара и углей, ольха и осина для чистого горения без копоти. Подскажем, что взять под вашу печь.",
          bp, [("Какие дрова лучше для бани", ["Берёзовые дают жар и угли, ольховые горят без копоти и с лёгким ароматом, осиновые чистят дымоход и не темнят стены парной. Удобная схема: прогреть печь берёзой, а последнюю закладку сделать ольхой или осиной. Хвойные для бани не советуем: смола даёт копоть и искры. Подробное сравнение — в статье «Какие дрова лучше для бани»."]),
               ("Сколько дров нужно на баню", ["На одну топку средней бани уходит 0,08-0,12 насыпного куба берёзы. При топке раз в неделю — 4-7 насыпных кубов за год. Для бани берут сухие дрова: сырые долго разгораются и коптят."])] + MORE_INTENT["bani"][:3] + T.COMMON,
          [("Какие дрова лучше для бани?", "Берёза для жара, ольха и осина для чистого горения. Хвойные — только на растопку."),
           ("Сколько кубов дров нужно для бани на год?", "При топке раз в неделю — 4-7 насыпных кубов.")],
          preselect=D.PRODUCTS["berezovye"]["name"], ex=bk_, links2=CITY_LINKS, links2_title="Возим и в другие города")
    # Дрова для котла
    bk = D.PRODUCTS["smeshannye"]["price"]
    money("/drova-dlya-kotla-ekaterinburg/", "Дрова для котла с доставкой в Екатеринбурге",
          f"Дрова для котла длительного горения — купить от {ru0(bk)} ₽/м³",
          f"Дрова для котлов длительного горения: берёза и смешанные, сухие и естественной влажности, полено под вашу топку. От {ru0(bk)} ₽/м³ с доставкой.",
          "Берёза и смешанные дрова для пиролизных котлов и котлов верхнего горения. Подберём длину полена под вашу камеру загрузки и привезём по Екатеринбургу и области.",
          bk, MORE_INTENT_KOTEL + T.COMMON,
          [("Какие дрова лучше для котла?", "Сухая берёза или смешанные с преобладанием берёзы. Для пиролизного котла — только сухие, до 20%."),
           ("Можно подобрать длину полена под котёл?", "Да, назовите глубину загрузочной камеры или модель котла."),
           ("Сколько дров нужно котлу на зиму?", "Для дома 100 м² — 15-18 насыпных кубов берёзы за сезон."),
           ("Можно ли топить котёл хвойными дровами?", "Можно, если они сухие, но теплообменник придётся чистить чаще.")],
          preselect=D.PRODUCTS["berezovye"]["name"], ex="smeshannye", links=[l for l in PROD_LINKS], links2=CITY_LINKS + [{"url": f"{D.HUB}drova-dlya-kotla-dlitelnogo-goreniya/", "text": "Статья: дрова для котла длительного горения"}], links2_title="Города и статьи")
    # Дрова для печи (9 октября: «дрова для печи купить» 507, «…екатеринбург» 181)
    sm = D.PRODUCTS["smeshannye"]["price"]
    blog = lambda slug, text: {"url": f"{D.HUB}blog/{slug}/", "text": text}
    art = lambda slug: {"url": f"{D.HUB}{slug}/", "text": AR.A[slug]["h1"]}
    money("/drova-dlya-pechi-ekaterinburg/", "Дрова для печи с доставкой в Екатеринбурге",
          f"Купить дрова для печи в Екатеринбурге — от {ru0(sm)} ₽/м³",
          f"Дрова для печи с доставкой по Екатеринбургу: берёзовые колотые 3 куба — от {ru0(D.PRODUCTS['berezovye']['t3'])} ₽, смешанные — от {ru0(sm)} ₽/м³. Полено под вашу топку, без минимального объёма.",
          "Берёзовые и смешанные колотые дрова для кирпичных и русских печей, металлических печек и буржуек. Подберём длину полена под топку и привезём по Екатеринбургу и области.",
          sm, M2.PECH + T.COMMON, M2.PECH_FAQ + M2.PECH_FAQ_ADD, preselect=D.PRODUCTS["berezovye"]["name"],
          links=[l for l in PROD_LINKS if l["url"] != "/drova-dlya-pechi-ekaterinburg/"],
          links2=[art("kakie-drova-luchshe-dlya-otopleniya"), art("vlazhnost-drov"), art("skolko-drov-nuzhno-na-zimu"),
                  blog("kak-pravilno-topit-pech", "Как правильно топить печь дровами"), blog("kak-razzhech-pech-i-kamin", "Как разжечь печь и камин"),
                  blog("pochemu-dymit-pech", "Почему дымит печь"), blog("kreozot-v-dymohode", "Креозот в дымоходе")] + CITY_LINKS,
          links2_title="Статьи о печи и другие города")
    # Недорогие дрова (9 октября: «дрова недорого» 568, «купить дрова недорого» 532,
    # «дрова дёшево с доставкой» 509). Таблица «цена тепла» — из долей тепла M2.HEAT.
    hv = D.PRODUCTS["hvoynye"]["price"]
    heat = {"title": "Недорогие дрова: цена куба и цена тепла",
            "head": ["Дрова", "Машина 10 м³ с доставкой", "Тепло куба к берёзе", "Цена тепла*"],
            "rows": [[{"url": f'/{D.PRODUCTS[k]["slug"]}/', "text": D.PRODUCTS[k]["name"]}, f"от {ru0(D.PRODUCTS[k]['t10'])} ₽",
                      f"{round(lo * 100)}%" if lo == hi else f"{round(lo * 100)}-{round(hi * 100)}%",
                      f"≈ {ru0(round(D.PRODUCTS[k]['price'] / ((lo + hi) / 2) / 50) * 50)} ₽"] for k, lo, hi in M2.HEAT],
            "note": "* Сколько стоят дрова, которые дадут столько же тепла, сколько насыпной куб берёзовых колотых, при заказе машины 10 кубов. "
                    "Это ориентир: тепло зависит от влажности и от того, как плотно дрова легли в кузове. Чурки нужно колоть самим."}
    money("/drova-nedorogo-ekaterinburg/", "Недорогие дрова с доставкой в Екатеринбурге",
          f"Дрова недорого в Екатеринбурге — дёшево с доставкой, от {ru0(hv)} ₽/м³",
          f"Недорогие дрова с доставкой по Екатеринбургу: горбыль — от {ru0(GORBYL)} ₽/м³, хвойные и смешанные колотые — от {ru0(hv)}, берёзовые — от {ru0(D.PRODUCTS['berezovye']['price'])} ₽/м³. Как купить дрова дёшево.",
          "Горбыль, хвойные и смешанные колотые дрова, берёзовые чурки — и способы купить подешевле даже берёзу. Привезём по Екатеринбургу, подскажем, что выгоднее под вашу печь.",
          hv, ins_after(M2.NEDOROGO, *M2.NEDOROGO_ADD) + T.COMMON, M2.NEDOROGO_FAQ + M2.NEDOROGO_FAQ_ADD, preselect=D.PRODUCTS["smeshannye"]["name"], ex="hvoynye",
          links=[l for l in PROD_LINKS if l["url"] != "/drova-nedorogo-ekaterinburg/"],
          links2=[art("skolko-stoit-kub-drov"), art("skladometr-ili-nasypnoy-kub"), art("skolko-gorbylya-v-kube")] + CITY_LINKS,
          links2_title="Статьи и города", xtables=[heat])
    # Города
    for key, name, prep, dat, text in D.CITIES:
        money(f"/{D.CITY_SLUG[key]}/", f"Купить дрова {prep} с доставкой",
              DC.C[key].get("title", "Купить дрова {prep} с доставкой — цена от {p} ₽/м³").format(prep=prep, p=ru0(MIN_PRICE)),
              f"Дрова с доставкой {prep} и до 50 км вокруг: 3 куба берёзовых колотых — от {ru0(D.PRODUCTS['berezovye']['t3'])} ₽, смешанные, ольха, осина, сухие, горбыль. От одного куба.",
              f"Берёзовые, смешанные, хвойные, ольховые, осиновые и сухие дрова, горбыль — привезём по {dat} и до 50 км вокруг. От одного куба.",
              MIN_PRICE, city_secs(key, name, prep, dat) + T.COMMON,
              DC.C[key]["faq"] + [(f"Сколько стоят дрова {prep}?", price_answer(prep, near=False)),
               (f"Возите дрова {prep} без минимального объёма?", "Да, привезём и один куб, и полную машину."),
               (f"Можно заказать {prep} уголь, брикеты или пеллеты?", fuel_answer())],
              city_prep=prep, city_text=text, deliv_po=dat,
              links=([{"url": f"/drova-berezovye-{key}/", "text": f"Берёзовые колотые {prep}"}] if key in T.BEREZA_CITY else []) + CF_BY_CITY.get(key, []) + PROD_LINKS,
              links2=[l for l in CITY_LINKS if l["url"] != f"/{D.CITY_SLUG[key]}/"],
              links2_title="Другие города", **{})
    # Статьи
    for i, s in enumerate(D.ARTICLES):
        a = AR.A[s]; path = f"{D.HUB}{s}/"
        html = env.get_template("drova_article.html").render(**ctx(
            title=a["title"], description=a["desc"], canonical=DOMAIN + path, h1=a["h1"], lede=a["lede"],
            body=a["body"], faq=a["faq"], min_price=MIN_PRICE, cta_base="/drova-ekaterinburg/", og_type="article",
            date_iso=ART_PUB, date_ru=ru_d(ART_PUB), upd_iso=ART_UPD_X.get(s, ART_UPD), upd_ru=ru_d(ART_UPD_X.get(s, ART_UPD)),
            related=ART_REL_X.get(s, []) + ([ART_MONEY[s]] if s in ART_MONEY else []) + [l for l in ART_LINKS if l["url"] != path] + [{"url": "/drova-ekaterinburg/", "text": "Цены на дрова в Екатеринбурге"}],
            schema_json=json.dumps({"@context": "https://schema.org", "@graph": [
                {"@type": "Article", "headline": a["h1"], "description": a["desc"], "datePublished": ART_PUB, "dateModified": ART_UPD_X.get(s, ART_UPD),
                 "mainEntityOfPage": DOMAIN + path, "author": {"@type": "Organization", "name": SITE["brand"]},
                 "publisher": {"@type": "Organization", "name": SITE["brand"]}, "image": DOMAIN + "/img/og-cover.jpg"},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
                    {"@type": "ListItem", "position": 2, "name": a["h1"], "item": DOMAIN + path}]},
                {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in a["faq"]]}]},
                ensure_ascii=False)))
        write(path, html)
    render_blog()
    gone()
    sitemaps()
    print(f"Дрова: {len(PAGES)} страниц")


# Снятые страницы: адрес уже в поиске, поэтому не 404, а закрытая от индекса
# заглушка с переходом туда, где человеку помогут. В карту сайта не попадает.
GONE = {
    "/drova-mihaylovsk/": "/dostavka-drov/",   # 9 октября: в Михайловск не возим
}


def gone():
    for path, to in GONE.items():
        html = (f'<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">\n'
                f'<meta name="robots" content="noindex, follow">\n'
                f'<link rel="canonical" href="{DOMAIN}{to}">\n'
                f'<meta http-equiv="refresh" content="0; url={to}">\n'
                f'<title>Дрова с доставкой по Екатеринбургу и области</title>\n'
                f'<script>location.replace("{to}")</script></head>\n'
                f'<body><p><a href="{to}">Доставка дров по Екатеринбургу и области</a></p></body></html>\n')
        full = os.path.join(ROOT, path.strip("/"), "index.html")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(html)


BLOG_URL = f"{D.HUB}blog/"
BLOG_DATE = "2026-10-07"


def render_blog():
    """Блог дров: /dostavka-drov/blog/ и посты. Реклама РСЯ — только здесь (ads=True)."""
    nav = [{"url": f"{BLOG_URL}{p['slug']}/", "text": p["short"], "desc": re.split(r"(?<=[.!?])\s", p["lede"])[0], "group": p["group"]} for p in BL.POSTS]
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
    for p in BL.POSTS:
        path = f"{BLOG_URL}{p['slug']}/"
        pd = p.get("date", BLOG_DATE); d = datetime.date.fromisoformat(pd)
        # По кругу: следующие посты той же рубрики, затем следующие из других —
        # так каждый пост получает примерно поровну входящих ссылок.
        i = [x["url"] for x in nav].index(path)
        ring = nav[i + 1:] + nav[:i]
        same = [x for x in ring if x["group"] == p["group"]][:3]
        rel = (same + [x for x in ring if x not in same])[:6] + [{"url": p["money"][0], "text": p["money"][1]}]
        html = env.get_template("drova_article.html").render(**ctx(
            title=p["title"], description=p["desc"], canonical=DOMAIN + path, h1=p["h1"], lede=p["lede"],
            body=p["body"], faq=p["faq"], min_price=MIN_PRICE, cta_base="/drova-ekaterinburg/", og_type="article",
            ads=True, section_url=BLOG_URL, section_name="Блог",
            extra_cta={"url": p["money"][0], "text": p["money"][1] + " →"},
            date_iso=pd, date_ru=f"{d.day} {MONTHS[d.month-1]} {d.year}", related=rel,
            schema_json=json.dumps({"@context": "https://schema.org", "@graph": [
                {"@type": "BlogPosting", "headline": p["h1"], "description": p["desc"], "datePublished": pd, "dateModified": pd,
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
    drop = set(urls) | {DOMAIN + g for g in GONE}   # снятые страницы — вон из карты
    foreign = [b for b in blocks if re.search(r"<loc>(.*?)</loc>", b).group(1) not in drop]
    open(main_p, "w", encoding="utf-8").write(head + "\n".join(foreign + [block(u) for u in urls]) + "\n</urlset>\n")
    rb = os.path.join(ROOT, "robots.txt"); r = open(rb, encoding="utf-8").read()
    line = f"Sitemap: {DOMAIN}/sitemap-dostavka-drov.xml"
    if line not in r:
        open(rb, "w", encoding="utf-8").write(r.rstrip("\n") + "\n" + line + "\n")


if __name__ == "__main__":
    main()
