# -*- coding: utf-8 -*-
"""Сборка раздела «Доставка щебня и песка» (fanline.su/dostavka-shchebnya-i-peska/).

Запуск:  python3 _nerud-build/build.py

Раздел переехал с ursdom.ru/dostavka/ (15 октября 2026, решение владельца):
там почти нет заявок. Тексты написаны заново, с ursdom взяты только факты —
цены, фракции, машины. Данные — nerud_data.py, тексты — nerud_*.py.

Шаблоны как у дров: свои в templates/, остальное — из сборки грунта
(_ekb-build/templates): base.html со счётчиком, целями, MAX и запасной
формой, нижняя панель, отзывы, фото доставок. Шапка, подвал, форма заявки,
короткая заявка и окно «Не открылся MAX?» берутся у грунта и на лету
правятся под щебень (DictLoader ниже) — исправления грунта приходят сами.

Пишет страницы, sitemap-dostavka-shchebnya.xml, свой блок в sitemap.xml
(чужие записи не трогает) и строку Sitemap в robots.txt.
"""
import os, re, sys, json, copy, datetime
from jinja2 import Environment, FileSystemLoader, DictLoader, ChoiceLoader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EKB = os.path.join(ROOT, "_ekb-build")
DROVA = os.path.join(ROOT, "_drova-build")
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(EKB, "data"))
sys.path.insert(2, EKB)
sys.path.insert(3, DROVA)

from site_config import SITE as _SITE
import typo
import nerud_data as D
import nerud_works as WK
import nerud_texts as T
import nerud_products as NP
import nerud_types as NT
import nerud_cities as NC
import nerud_articles as AR
from reviews import REVIEWS as GRUNT_REVIEWS
import drova_reviews as RV   # тот же порядок отзывов, что у дров: сначала без слова «грунт»

# Отзывы: настоящие отзывы клиентов о доставке грунта — компания та же
# (владелец 15 октября: «как на дровах»). Подписи нет, в разметку Product
# они не идут: это отзывы о другом товаре.
REV = sorted(GRUNT_REVIEWS, key=lambda r: RV.ORDER_GRUNT.index(r["name"]))
assert len(REV) == len(RV.ORDER_GRUNT), "новый отзыв грунта: добавьте имя в drova_reviews.ORDER_GRUNT"

SITE = copy.deepcopy(_SITE)
SITE["brand"] = "Щебень Доставка"
DOMAIN = SITE["domain"]
TODAY = datetime.date.today()
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
LEAD_TITLE = "Рассчитаем стоимость с доставкой и согласуем время"


def ekb_src(name):
    return open(os.path.join(EKB, "templates", name), encoding="utf-8").read()


def must_sub(pattern, repl, s, flags=0):
    s2, n = re.subn(pattern, repl, s, flags=flags)
    assert n, f"шаблон грунта поменялся, не найдено: {pattern[:60]}"
    return s2


# Позиции формы заявки: материалы и фасовка (названия — как в калькуляторе,
# он переносит выбор в форму по совпадению строки).
FORM_ORDER = ["shcheben-20-40", "shcheben-5-20", "shcheben-40-70", "shcheben-70-120", "shcheben-mramornyy",
              "pesok-karernyy", "pesok-stroitelnyy", "pesok-rechnoy", "pesok-mytyy", "pesok-peskostruy",
              "otsev", "pgs", "shchps", "graviy", "galka", "skalnyy-grunt", "keramzit",
              "granitnaya-kroshka", "asfaltovaya-kroshka", "butovyy-kamen",
              "shcheben-meshok", "pesok-meshok", "otsev-meshok", "keramzit-meshok"]
assert set(FORM_ORDER) == set(D.M), set(D.M) ^ set(FORM_ORDER)


def overrides():
    o = {}
    h = ekb_src("partials/header.html")
    h = must_sub(r'<a class="hdr__logo" href="/dostavka-grunta/">', f'<a class="hdr__logo hdr__logo--nerud" href="{D.HUB}">', h)
    o["partials/header.html"] = h
    f = ekb_src("partials/footer.html")
    f = must_sub(r'<p class="ftr__legal">.*?</p>',
                 '<p class="ftr__legal">Доставка щебня, песка, отсева, ПГС, ЩПС, гравия, керамзита и других сыпучих материалов по {{ site.region_po }}. '
                 'Цены «от»: материал — за кубометр без доставки, рейс по Екатеринбургу — отдельно. Точную стоимость назовём по заявке.</p>', f, re.S)
    o["partials/footer.html"] = f
    bs = ekb_src("base.html")
    bs = must_sub(r'imagesizes="\(max-width: 900px\) 260px, 100vw"', 'imagesizes="{{ hero_sizes|default(\'(max-width: 900px) 260px, 100vw\') }}"', bs)
    bs = must_sub(r'<link rel="preload" as="image" fetchpriority="high"\n',
                  '<link rel="preload" as="image" fetchpriority="high" href="/assets/ekb/photo/{{ hero_photo }}-m-900.webp" type="image/webp" media="(max-width: 480px)">\n'
                  '  <link rel="preload" as="image" fetchpriority="high" media="(min-width: 481px)"\n', bs)
    o["base.html"] = bs
    cb = ekb_src("partials/callbar.html")
    cb = must_sub(r"\{\{ cta_base\|default\(''\) \}\}#calc-title", "{{ calc_base|default(cta_base|default('')) }}#calc-title", cb)
    cb = must_sub(r'aria-label="Написать в MAX">', 'aria-label="Написать в MAX, скидка 5%">', cb)
    cb = must_sub(r'(<span class="callbar__short">MAX</span>)', r'\1<span class="callbar__badge" aria-hidden="true">−5%</span>', cb)
    o["partials/callbar.html"] = cb
    lf = ekb_src("partials/lead_form.html")
    names = [D.M[k]["name"] for k in FORM_ORDER]
    lf = must_sub(r'\{%- set products = \[.*?\] %\}', "{%- set products = " + json.dumps(names, ensure_ascii=False) + " %}", lf, re.S)
    lf = must_sub(r'<form class="lead__form"', '<form class="lead__form lead__form--drova"', lf)
    lf = must_sub(r'<div class="field">(\s*<label class="field__label" for="lead-product">)', r'<div class="field field--wide">\1', lf)
    lf = must_sub(r'<div class="field">(\s*<label class="field__label" for="lead-district">)', r'<div class="field field--wide">\1', lf)
    lf = must_sub(r'"Сайт доставки грунта"', '"Сайт доставки щебня и песка"', lf)
    lf = must_sub(r'\(form\.product\.value\|\|"грунт"\)', '(form.product.value||"щебень")', lf)
    lf = must_sub(r'value="\{\{ min_volume\.split\(\' \'\)\[0\] \}\}"', 'value="10"', lf)
    units = {D.M[k]["name"]: {"мешок": "мешков", "т": "т"}[D.M[k]["unit"]] for k in FORM_ORDER if D.M[k]["unit"] != "м³"}
    lf = must_sub(r'<label class="field__label" for="lead-volume">Объём, м³</label>',
                  '<label class="field__label" for="lead-volume">Объём, <span id="lead-unit">м³</span></label>', lf)
    lf = must_sub(r"var volumeText = form\.volume\.value \? form\.volume\.value \+ ' м³' : 'объём не указан';",
                  "var volumeText = form.volume.value ? form.volume.value + ' ' + leadUnit() : 'объём не указан';", lf)
    lf = must_sub(r"\{%- set c = city\|default\(\{\}\) %\}", "{%- set c = lead_city|default(city|default({})) %}", lf)
    lf = must_sub(r"\{%- if c\.local_partner %\}",
                  '{%- if lead_title %}\n      <h2 class="lead__title" id="lead-title">{{ lead_title }}</h2>\n      {%- elif c.local_partner %}', lf)
    lf = must_sub(r'<span>Написать в <b>MAX</b></span>', '<span>Написать в <b>MAX</b> — скидка 5%</span>', lf)
    lf = must_sub(r"var ENDPOINT = ",
                  "var UNITS = " + json.dumps(units, ensure_ascii=False) + ";\n  function leadUnit(){ var f=document.getElementById('lead-product'); return (f && UNITS[f.value]) || 'м³'; }\n"
                  "  (function(){ var f=document.getElementById('lead-product'), u=document.getElementById('lead-unit'), v=document.getElementById('lead-volume');\n"
                  "    function sync(init){ var x=leadUnit(); if(u) u.textContent=x; if(v && (init || v.dataset.auto)){ v.value = x==='т' ? 1 : (x==='мешков' ? 20 : 10); v.dataset.auto='1'; } }\n"
                  "    if(f){ f.addEventListener('change', function(){ sync(false); }); sync(true); }\n"
                  "    if(v){ v.addEventListener('input', function(){ delete v.dataset.auto; }); } })();\n  var ENDPOINT = ", lf)
    o["partials/lead_form.html"] = lf
    mf = ekb_src("partials/max_fallback.html")
    mf = must_sub(r"'Сайт доставки грунта'", "'Сайт доставки щебня и песка'", mf)
    o["partials/max_fallback.html"] = mf
    cm = ekb_src("partials/cta_mid.html")
    cm = must_sub(r'<h2 class="ctamid__title" id="ctamid-title">.*?</h2>',
                  '<h2 class="ctamid__title" id="ctamid-title">Напишем точную цену с доставкой до вашего адреса</h2>', cm)
    cm = must_sub(r'\{%- if city\.local_partner %\}.*?\{%- endif %\}',
                  '<p class="ctamid__sub">{% if calc %}Калькулятор выше считает по нижней цене. {% else %}В таблице — цены «от». {% endif %}'
                  'Оставьте номер — напишем точную сумму под ваш объём и адрес. Работаем {{ site.hours|lower }}, {{ site.callback_promise }}.</p>', cm, re.S)
    cm = must_sub(r'"Сайт доставки грунта"', '"Сайт доставки щебня и песка"', cm)
    cm = must_sub(r'subject: "Быстрая заявка: \{\{ preselect_product \}\}"', 'subject: "Быстрая заявка: " + {{ (preselect_product or "щебень")|tojson }}', cm)
    cm = must_sub(r'product: "\{\{ preselect_product \}\}"', 'product: {{ (preselect_product or "щебень")|tojson }}', cm)
    cm = must_sub(r'district: "\{\{ city\.name \}\}"', 'district: {{ (city_prep or "")|tojson }}', cm)
    cm = must_sub(r'<b>Заявка принята\.</b> Ответим на указанный номер\.', '<b>Заявка принята.</b> Напишем вам, {{ site.callback_promise }}.', cm)
    cm = must_sub(r'<p class="ctamid__alt">Проще в мессенджере\? (<a [^>]*>MAX</a>)</p>', r'<p class="ctamid__alt">Закажите в \1 — скидка 5%</p>', cm)
    o["partials/cta_mid.html"] = cm
    fc = ekb_src("partials/floatcta.html")
    fc = must_sub(r"Калькулятор посчитает объём и рейс до вашего адреса — можно прикинуть заранее",
                  "Калькулятор посчитает стоимость щебня или песка вместе с доставкой — можно прикинуть заранее", fc)
    o["partials/floatcta.html"] = fc
    return o


env = Environment(loader=ChoiceLoader([DictLoader(overrides()),
                                      FileSystemLoader(os.path.join(HERE, "templates")),
                                      FileSystemLoader(os.path.join(EKB, "templates"))]),
                  autoescape=True, trim_blocks=False, lstrip_blocks=False)
env.filters["ru"] = lambda n: f"{int(n):,}".replace(",", " ")   # узкий неразрывный: «3 500» не рвётся
env.filters["ucfirst"] = lambda v: (v[:1].upper() + v[1:]) if v else v


def ru(n):
    return env.filters["ru"](n)


PAGES = []   # пути записанных страниц, для карты сайта


def _token(m):
    """Цены в текстах — только токенами, числа живут в nerud_data:
    %%m.KEY.price%% — цена материала; %%sum.KEY.V%% — V м³ с доставкой по Екатеринбургу
    (с готовыми объёмами щебня); %%sumc.KEY.V%% — то же в городах до 50 км (без них);
    %%per.KEY.V%% — за м³ при V м³ с доставкой; %%lot.KEY.V%% — готовый объём щебня;
    %%deliv%% — рейс; %%x.KEY.price.K%% — цена × K (мешки, тонны)."""
    p = m.group(1).split(".")
    if p[0] == "deliv":
        v = D.DELIVERY
    elif p[0] == "m":
        v = D.M[p[1]][p[2]]
    elif p[0] == "sum":
        v = D.total(p[1], int(p[2]))
    elif p[0] == "sumc":
        v = D.total(p[1], int(p[2]), lots=False)
    elif p[0] == "per":
        v = round(D.total(p[1], int(p[2])) / int(p[2]) / 10) * 10
    elif p[0] == "perc":   # за м³ с доставкой в городе до 50 км (без готовых объёмов Екатеринбурга)
        v = round(D.total(p[1], int(p[2]), lots=False) / int(p[2]) / 10) * 10
    elif p[0] == "lot":
        v = D.LOTS[p[1]][int(p[2])]
    elif p[0] == "x":
        k = float(".".join(p[3:]))
        v = D.M[p[1]][p[2]] * k
        v = int(v) if k == int(k) else round(v / 10) * 10
    else:
        raise KeyError(m.group(0))
    return ru(v)


def write(path, html):
    html = re.sub(r"%%([\w.-]+)%%", _token, html)
    assert "%%" not in html, path
    html = typo.glue(html)
    full = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(html)
    PAGES.append(path)


def schema(h1, path, faq, low=None, high=None, count=None, crumbs=True, parent=None):
    g = []
    if crumbs:
        items = [{"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB}]
        if parent:
            items.append({"@type": "ListItem", "position": 2, "name": parent["text"], "item": DOMAIN + parent["url"]})
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": h1, "item": DOMAIN + path})
        g.append({"@type": "BreadcrumbList", "itemListElement": items})
    if low:
        g.append({"@type": "Product", "name": h1, "url": DOMAIN + path, "image": DOMAIN + "/assets/ekb/photo/hero-shcheben-1400.jpg",
                  "offers": {"@type": "AggregateOffer", "lowPrice": low, "priceCurrency": "RUB",
                             **({"highPrice": high} if high else {}), **({"offerCount": count} if count else {}),
                             "availability": "https://schema.org/InStock"}})
    if faq:
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                  "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)


# ---------------------------------------------------------------- адреса
def url_of(key):
    """Страница позиции прайса: вид/фракция, если у неё своя страница, иначе материал."""
    if key in D.TYPES:
        return f"/{D.TYPES[key]}/"
    for pk, pg in D.PAGES.items():
        if pg["ref"] == key:
            return f"/{pg['slug']}/"
    return None


PRICE_ROWS = ["shcheben-20-40", "shcheben-5-20", "shcheben-40-70", "shcheben-70-120", "pesok-karernyy", "pesok-stroitelnyy",
              "pesok-rechnoy", "otsev", "pgs", "shchps", "graviy", "galka", "skalnyy-grunt", "keramzit",
              "granitnaya-kroshka", "asfaltovaya-kroshka", "butovyy-kamen"]
CALC_ITEMS = [k for k in FORM_ORDER if D.M[k]["unit"] == "м³" and D.M[k]["price"]]
LOTS_JSON = json.dumps({k: {str(v): p for v, p in lots.items()} for k, lots in D.LOTS.items()})


def price_rows(mode="ekb"):
    """mode: ekb — 10 м³ с доставкой по Екатеринбургу (с готовыми объёмами щебня);
    near — то же в городе до 50 км (без них); far — доставка по заявке."""
    rows = []
    for k in PRICE_ROWS:
        m = D.M[k]
        t10 = {"ekb": lambda: f"от {ru(D.total(k, 10))} ₽", "near": lambda: f"от {ru(D.total(k, 10, lots=False))} ₽",
               "far": lambda: "по заявке"}[mode]()
        rows.append({"name": m["name"], "url": url_of(k), "price_text": f"от {ru(m['price'])} ₽/м³", "t10_text": t10})
    return rows


PROD_LINKS = [{"url": f"/{D.PAGES[k]['slug']}/", "text": f"{D.PAGES[k]['name']} — от {ru(D.M[D.PAGES[k]['ref']]['price'])} ₽/м³"} for k in D.PAGE_ORDER]
TYPE_LINKS = [{"url": f"/{D.TYPES[k]}/", "text": D.M[k]["name"]} for k in D.TYPES]
CITY_LINKS = {pk: [{"url": f"/{D.city_slug(pk, c)}/", "text": f"{D.PAGES[pk]['name']} {D.CITIES[c][1]}"} for c in cs]
              for pk, cs in D.CITY_PAGES.items()}
ART_LINKS = [{"url": f"{D.HUB}{s}/", "text": AR.A[s]["h1"]} for s in AR.ORDER]
CALC_LINK = {"url": f"{D.HUB}{AR.CALC['slug']}/", "text": AR.CALC["h1"]}
FOOTER = [{"url": D.HUB, "text": "Доставка щебня и песка"}, {"url": "/shcheben-ekaterinburg/", "text": "Щебень в Екатеринбурге"},
          {"url": "/pesok-ekaterinburg/", "text": "Песок в Екатеринбурге"}, {"url": "/otsev-ekaterinburg/", "text": "Отсев"},
          {"url": "/keramzit-ekaterinburg/", "text": "Керамзит"}, {"url": CALC_LINK["url"], "text": "Калькулятор щебня и песка"},
          {"url": "/dostavka-grunta/", "text": "Доставка грунта"}, {"url": "/dostavka-drov/", "text": "Доставка дров"}]


def ctx(**kw):
    base = dict(site=SITE, robots="index, follow", hero_photo="hero-shcheben", ads=False, footer_links=FOOTER,
                cta_base="", city={}, preselect_product="", district_ph="Например, Берёзовский или Уралмаш",
                min_volume="10 м³", zone_text="Екатеринбурга", band_tone="tint",
                og_image_alt="Самосвал высыпает щебень у забора участка")
    base.update(kw)
    return base


def hero_price(ref, mode="ekb", city_dat=None):
    """Крупно на первом экране: «Куб щебня 20–40 — от 770 ₽» и итоги с доставкой."""
    m = D.M[ref]
    if not m["price"] and m["unit"] == "мешок":
        return {"label": "Мешок", "num": "по заявке",
                "note": "Цену мешка назовём под фракцию и количество. Навалом заметно дешевле, по Екатеринбургу рейс от %%deliv%% ₽."}
    if not m["price"]:
        return {"label": m["name"], "num": "по заявке",
                "note": "Цену назовём по фракции, цвету и объёму. Доставка по Екатеринбургу — от %%deliv%% ₽ за рейс."}
    if m["unit"] == "мешок":
        return {"label": "Мешок 25 кг", "num": f"от {ru(m['price'])} ₽",
                "note": "Без доставки. Рейс по Екатеринбургу — от %%deliv%% ₽; мешки удобно занести во двор, куда не заедет самосвал."}
    if m["unit"] == "т":
        return {"label": "Тонна навалом", "num": f"от {ru(m['price'])} ₽",
                "note": "Без доставки. Доставку по Екатеринбургу — от %%deliv%% ₽ за рейс — посчитаем под объём."}
    label = "Куб " + m["gen"]
    if mode == "far":
        return {"label": label, "num": f"от {ru(m['price'])} ₽",
                "note": f"Без доставки. Доставку по {city_dat} назовём по заявке: она зависит от объёма и машины, возим с ближайшей площадки."}
    lots = mode == "ekb"
    where = "по Екатеринбургу" if mode == "ekb" else f"по {city_dat}"
    return {"label": label, "num": f"от {ru(m['price'])} ₽",
            "note": f"Без доставки. С доставкой {where}: 5 м³ — от {ru(D.total(ref, 5, lots))} ₽, КамАЗ {D.TRIP_M3} м³ — от {ru(D.total(ref, D.TRIP_M3, lots))} ₽. "
                    f"Рейс — от {ru(D.DELIVERY)} ₽."}


def tok(s):
    return re.sub(r"%%([\w.-]+)%%", _token, s)


def money(path, h1, title, desc, hero_sub, ref, sections, faq, preselect="", mode="ekb", city=None,
          links=None, links_title="Материалы с доставкой", links2=None, links2_title="", is_hub=False, xtables=None,
          parent=None, offer=None, city_text=None, city_text_title="", hero_min=None, calc=None, calc_vol=10,
          price_title=None, price_note=None, compare_line=None, common_faq=True, dims_calc=False):
    title, desc = tok(title), tok(desc)
    assert len(title) <= 75, (path, len(title), title)
    assert 110 <= len(desc) <= 200, (path, len(desc), desc)
    faq = faq + ([x for x in T.COMMON_FAQ if x[0] not in {q for q, _ in faq}] if common_faq else [])
    _seen = set(); faq = [x for x in faq if not (x[0] in _seen or _seen.add(x[0]))]
    cname, cprep, cdat = (D.CITIES[city][:3] if city else ("Екатеринбург", "в Екатеринбурге", "Екатеринбургу"))
    m = D.M[ref]
    if calc is None:
        calc = mode != "far" and m["unit"] == "м³" and bool(m["price"])
    low = (offer or {}).get("low", m["price"])
    if price_note is None:
        price_note = {"ekb": "Цены «от»: материал — за кубометр без доставки, в третьей колонке — 10 м³ с доставкой по Екатеринбургу. "
                             "Рейс по городу и до 50 км — от %%deliv%% ₽, в КамАЗ входит до 10 м³. Точную цену назовём под объём, фракцию и адрес.",
                      "near": f"Цены «от»: материал — за кубометр без доставки, в третьей колонке — 10 м³ с доставкой по {cdat}. "
                              f"Рейс до 50 км от Екатеринбурга — от %%deliv%% ₽. Точную цену назовём под объём, фракцию и адрес.",
                      "far": f"Цены «от» — за кубометр материала без доставки. Доставку по {cdat} назовём по заявке: она зависит от объёма, "
                             f"машины и площадки, с которой повезём. Скажите материал, объём и адрес — посчитаем итог."}[mode]
    if compare_line is None:
        compare_line = ("У нас итог виден сразу: 10 м³ щебня 20–40 с доставкой по Екатеринбургу — от %%sum.shcheben-20-40.10%% ₽."
                        if mode == "ekb" else
                        f"У нас итог виден сразу: 10 м³ щебня 20–40 с доставкой по {cdat} — от %%sumc.shcheben-20-40.10%% ₽."
                        if mode == "near" else
                        f"Доставку по {cdat} назовём сразу по заявке, под ваш объём, — без «сюрпризов» на месте.")
    html = env.get_template("nerud_page.html").render(**ctx(
        hero_alt="Самосвал высыпает гранитный щебень у забора участка",
        hero_sizes="(max-width: 900px) 800px, 100vw",
        title=title, description=desc, canonical=DOMAIN + path, h1=h1, hero_sub=hero_sub,
        hero_price=hero_price(ref, mode, cdat),
        hero_min=hero_min or ((f"Рейс {cprep} — в согласованный день", "чем больше кубов в машине, тем дешевле каждый: доставка делится на весь кузов")
                              if mode == "far" else
                              ("Малый объём тоже привезём", "рейс оплачивается целиком, поэтому выгоднее сразу КамАЗ до 10 м³; совсем немного — в мешках")),
        sections=sections, faq=faq, price_rows=price_rows(mode), price_title=price_title or (f"Цены на щебень, песок и сыпучие материалы {cprep}"),
        price_col3=("10 м³ с доставкой" if mode != "far" else "Доставка"), price_note=price_note, compare_line=compare_line,
        dims_calc=dims_calc, dims_items=[{"key": k, "name": D.M[k]["name"], "comp": D.comp(k),
                                          "dens": round(sum(D.M[k]["dens"]) / 2, 2) if D.M[k]["dens"] else ""} for k in CALC_ITEMS],
        calc=calc, calc_items=[{"key": k, "name": D.M[k]["name"], "price": D.M[k]["price"]} for k in CALC_ITEMS],
        calc_pre=ref if ref in CALC_ITEMS else "shcheben-20-40", calc_vol=calc_vol,
        # готовые объёмы щебня — с доставкой по Екатеринбургу, в городах области калькулятор считает материал + рейс
        lots_json=LOTS_JSON if mode == "ekb" else "{}", calc_lots=mode == "ekb",
        delivery=D.DELIVERY, trip_m3=D.TRIP_M3, **({} if calc else {"calc_base": "/shcheben-ekaterinburg/"}),
        self_path=path, preselect_product=preselect or m["name"], city_prep=cprep if city else "",
        city_text=city_text or [], city_text_title=city_text_title,
        links=links or PROD_LINKS, links_title=links_title, links2=links2, links2_title=links2_title,
        is_hub=is_hub, xtables=xtables or [], parent=parent,
        lead_city={"distance_km": D.CITIES[city][3]} if city else {}, lead_title=LEAD_TITLE,
        works=WK.WORKS, works_title=WK.TITLE, works_video=WK.video_for(path),
        reviews=REV, reviews_title=RV.TITLE_GRUNT, reviews_note="",
        schema_json=schema(h1, path, faq, low, (offer or {}).get("high"), (offer or {}).get("count"), crumbs=not is_hub, parent=parent)))
    write(path, html)


def lots_table(key):
    lots = D.LOTS[key]
    return {"title": f"Готовые объёмы: {D.M[key]['name'].lower()} с доставкой по Екатеринбургу",
            "head": ["Объём", "Цена с доставкой", "За куб"],
            "rows": [[f"{v} м³", f"от {ru(p)} ₽", f"от {ru(round(p / v / 10) * 10)} ₽"] for v, p in lots.items()],
            "note": "Фиксированная цена за машину целиком: материал и рейс по Екатеринбургу уже внутри. Объём проверяете по кузову до выгрузки."}


def ru_d(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


ART_PUB = "2026-10-15"


def main():
    # Главная раздела
    h = T.HUB
    money(D.HUB, h["h1"], h["title"], h["desc"], h["sub"], "shcheben-20-40", h["sections"] + T.COMMON, h["faq"],
          links=PROD_LINKS, links_title="Материалы и цены", is_hub=True,
          links2=TYPE_LINKS + [l for v in CITY_LINKS.values() for l in v] + [CALC_LINK] + ART_LINKS,
          links2_title="Фракции, города и статьи", xtables=[lots_table("shcheben-20-40")],
          offer={"low": min(D.M[k]["price"] for k in PRICE_ROWS), "high": max(D.M[k]["price"] for k in PRICE_ROWS), "count": len(PRICE_ROWS)})
    # Материалы по Екатеринбургу
    for pk in D.PAGE_ORDER:
        pg = D.PAGES[pk]; t = NP.P[pk]; path = f"/{pg['slug']}/"
        types = [l for l in TYPE_LINKS if l["url"].startswith(f"/{pk}-")]
        xt = [lots_table("shcheben-20-40"), lots_table("shcheben-5-20")] if pk == "shcheben" else []
        money(path, t["h1"], t["title"], t["desc"], t["sub"], pg["ref"], t["sections"] + T.COMMON, t["faq"],
              links=[l for l in PROD_LINKS if l["url"] != path], links_title="Другие материалы",
              links2=types + CITY_LINKS.get(pk, []) + [CALC_LINK] + [ART_LINKS[i] for i in t.get("arts", [])],
              links2_title=t.get("links2_title", "Виды, города и статьи"), xtables=xt, calc_vol=t.get("calc_vol", 10),
              offer=t.get("offer"))
    # Виды и фракции
    for k, slug in D.TYPES.items():
        t = NT.P[k]; path = f"/{slug}/"
        pk = t["parent"]; parent = {"url": f"/{D.PAGES[pk]['slug']}/", "text": f"{D.PAGES[pk]['name']} в Екатеринбурге"}
        sib = [l for l in TYPE_LINKS if l["url"] != path and l["url"].startswith(f"/{pk}-")]
        xt = [lots_table(k)] if k in D.LOTS else []
        money(path, t["h1"], t["title"], t["desc"], t["sub"], k, t["sections"] + T.COMMON, t["faq"],
              links=[parent] + sib + [l for l in PROD_LINKS if l["url"] != parent["url"]], links_title="Другие виды и материалы",
              links2=CITY_LINKS.get(pk, []) + [CALC_LINK] + [ART_LINKS[i] for i in t.get("arts", [])], links2_title="Города и статьи",
              parent=parent, xtables=xt, calc=t.get("calc"), calc_vol=t.get("calc_vol", 10),
              hero_min=t.get("hero_min"), offer=t.get("offer"))
    # Города
    for pk, cities in D.CITY_PAGES.items():
        for c in cities:
            t = NC.C[(pk, c)]; path = f"/{D.city_slug(pk, c)}/"; name, prep, dat, km = D.CITIES[c]
            mode = "near" if D.is_near(c) else "far"
            parent = {"url": f"/{D.PAGES[pk]['slug']}/", "text": f"{D.PAGES[pk]['name']} в Екатеринбурге"}
            other = [l for p2, ls in CITY_LINKS.items() for l in ls if p2 != pk and l["url"].endswith(f"-{c}/")]
            money(path, t["h1"], t["title"], t["desc"], t["sub"], D.PAGES[pk]["ref"], t["sections"] + T.COMMON, t["faq"],
                  mode=mode, city=c, city_text=t["intro"], city_text_title=t.get("intro_title", f"{D.PAGES[pk]['name']} {prep}"),
                  links=other + [parent] + [l for l in PROD_LINKS if l["url"] != parent["url"]], links_title=f"Ещё {prep}",
                  links2=[l for l in CITY_LINKS[pk] if l["url"] != path], links2_title="Другие города",
                  parent=parent)
    # Калькулятор
    t = AR.CALC; path = f"{D.HUB}{t['slug']}/"
    money(path, t["h1"], t["title"], t["desc"], t["sub"], "shcheben-20-40", t["sections"], t["faq"],
          links=PROD_LINKS, links_title="Материалы и цены", links2=ART_LINKS, links2_title="Статьи",
          calc_vol=10, common_faq=False, price_title="Цены на материалы для расчёта", dims_calc=True)
    # Статьи
    for s in AR.ORDER:
        a = AR.A[s]; path = f"{D.HUB}{s}/"
        html = env.get_template("nerud_article.html").render(**ctx(
            title=a["title"], description=a["desc"], canonical=DOMAIN + path, h1=a["h1"], lede=a["lede"],
            body=a["body"], faq=a["faq"], og_type="article", delivery=D.DELIVERY, cta_base="/shcheben-ekaterinburg/",
            cta_url=a.get("cta", ("/shcheben-ekaterinburg/", "Цены на щебень"))[0], cta_text=a.get("cta", ("/shcheben-ekaterinburg/", "Цены на щебень"))[1],
            date_iso=ART_PUB, date_ru=ru_d(ART_PUB), upd_iso=ART_PUB, upd_ru=ru_d(ART_PUB),
            related=a.get("related", []) + [l for l in ART_LINKS if l["url"] != path] + [CALC_LINK, {"url": D.HUB, "text": "Доставка щебня и песка"}],
            schema_json=json.dumps({"@context": "https://schema.org", "@graph": [
                {"@type": "Article", "headline": a["h1"], "description": a["desc"], "datePublished": ART_PUB, "dateModified": ART_PUB,
                 "mainEntityOfPage": DOMAIN + path, "author": {"@type": "Organization", "name": SITE["brand"]},
                 "publisher": {"@type": "Organization", "name": SITE["brand"]}, "image": DOMAIN + "/assets/ekb/photo/hero-shcheben-1400.jpg"},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Главная", "item": DOMAIN + D.HUB},
                    {"@type": "ListItem", "position": 2, "name": a["h1"], "item": DOMAIN + path}]},
                {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in a["faq"]]}]},
                ensure_ascii=False)))
        write(path, html)
    sitemaps()
    print(f"Щебень и песок: {len(PAGES)} страниц")


def sitemaps():
    urls = [DOMAIN + p for p in PAGES]
    def block(u):
        pr = "0.9" if u.endswith(D.HUB) else ("0.6" if D.HUB in u else "0.8")
        return f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY.isoformat()}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
    head = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    open(os.path.join(ROOT, "sitemap-dostavka-shchebnya.xml"), "w", encoding="utf-8").write(head + "\n".join(block(u) for u in urls) + "\n</urlset>\n")
    main_p = os.path.join(ROOT, "sitemap.xml"); src = open(main_p, encoding="utf-8").read()
    blocks = re.findall(r"  <url>.*?</url>", src, re.S)
    foreign = [b for b in blocks if re.search(r"<loc>(.*?)</loc>", b).group(1) not in set(urls)]
    open(main_p, "w", encoding="utf-8").write(head + "\n".join(foreign + [block(u) for u in urls]) + "\n</urlset>\n")
    rb = os.path.join(ROOT, "robots.txt"); r = open(rb, encoding="utf-8").read()
    line = f"Sitemap: {DOMAIN}/sitemap-dostavka-shchebnya.xml"
    if line not in r:
        open(rb, "w", encoding="utf-8").write(r.rstrip("\n") + "\n" + line + "\n")


if __name__ == "__main__":
    main()
