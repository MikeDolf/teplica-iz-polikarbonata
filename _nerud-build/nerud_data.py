# -*- coding: utf-8 -*-
"""Данные раздела «Доставка щебня и песка» (fanline.su, 15 октября 2026).

Раздел переезжает с ursdom.ru/dostavka/ (решение владельца 15 октября):
там почти нет заявок. Тексты здесь пишутся заново — с ursdom берутся
только факты: цены, фракции, машины, расстояния.

ЦЕНЫ — «от», за кубометр материала БЕЗ доставки (владелец: «цены ursdom
как «от»»). Щебень, песок, отсев, ПГС и скальный грунт — из прайса
партнёра-поставщика по Екатеринбургу (август 2026); керамзит, гравий,
галька, ЩПС, бут и крошки на ursdom стояли ориентиром «по рынку» —
владелец 15 октября: «да, как «от»». Мраморный щебень — по заявке
(цены на ursdom не было).

ДОСТАВКА (владелец, 15 октября):
- по Екатеринбургу и до 50 км — рейс от 3 500 ₽, «как у дров»; в КамАЗ
  входит до 10 м³ (TRIP_M3), больше — следующий рейс или большой самосвал
  до 26 м³ по расчёту;
- города дальше 50 км — «цена по заявке»: на странице только цена
  материала, доставку называем под адрес и объём. На ursdom её считали
  по 95 ₽/км туда и обратно, и 10 м³ щебня в Тагил выходили в 31 450 ₽ —
  такую сумму на сайте никто не дочитывает до заявки;
- щебень — ещё и готовые объёмы с доставкой по Екатеринбургу из прайса
  партнёра (5, 8, 10 и 12 м³): на малых объёмах они дешевле расчёта
  «материал + рейс», и итог берётся меньший из двух.
Названия партнёров и карьеров на сайте не пишем: «возим с ближайшей
площадки».
"""
import math

HUB = "/dostavka-shchebnya-i-peska/"
DELIVERY = 3500     # ₽ за рейс по Екатеринбургу и до 50 км
TRIP_M3 = 10        # м³ в КамАЗе: щебень и песок тяжёлые (1,4–1,6 т/м³), 10 м³ — уже 14–16 т.
                    # У дров 12 м³ (они лёгкие). Готовый объём 12 м³ щебня у партнёра — своя цена в LOTS.
REF_VOL = 10        # «машина 10 м³ с доставкой — от …»
NEAR_KM = 50        # дальше — доставка по заявке

# Материалы: цена «от» за м³ без доставки (или за мешок/тонну — unit).
# gen — родительный («куб щебня»), acc — винительный («заказать щебень»),
# dens — насыпная плотность, т/м³ (справочные значения, None — не пишем).
M = {
    # --- щебень по фракциям (прайс партнёра ведётся по фракции, не по породе)
    "shcheben-5-20":   dict(name="Щебень 5–20", gen="щебня 5–20", acc="щебень 5–20", price=1150, dens=(1.36, 1.42), src="partner"),
    "shcheben-20-40":  dict(name="Щебень 20–40", gen="щебня 20–40", acc="щебень 20–40", price=770, dens=(1.35, 1.40), src="partner"),
    "shcheben-40-70":  dict(name="Щебень 40–70", gen="щебня 40–70", acc="щебень 40–70", price=770, dens=(1.35, 1.40), src="partner"),
    "shcheben-70-120": dict(name="Щебень 70–120", gen="щебня 70–120", acc="щебень 70–120", price=920, dens=(1.35, 1.45), src="partner"),
    "shcheben-mramornyy": dict(name="Мраморный щебень", gen="мраморного щебня", acc="мраморный щебень", price=None, dens=(1.35, 1.45), src="request"),
    # --- песок
    "pesok-karernyy":  dict(name="Песок карьерный", gen="карьерного песка", acc="карьерный песок", price=990, dens=(1.50, 1.60), src="partner"),
    "pesok-stroitelnyy": dict(name="Песок строительный", gen="строительного песка", acc="строительный песок", price=1000, dens=(1.50, 1.60), src="partner"),
    "pesok-rechnoy":   dict(name="Песок речной мытый", gen="речного песка", acc="речной песок", price=1450, dens=(1.50, 1.60), src="partner"),
    "pesok-mytyy":     dict(name="Песок мытый", gen="мытого песка", acc="мытый песок", price=1450, dens=(1.50, 1.60), src="partner"),
    "pesok-peskostruy": dict(name="Песок для пескоструя", gen="песка для пескоструя", acc="песок для пескоструя", price=990, unit="т", dens=None, src="partner"),
    # --- остальные сыпучие
    "otsev":           dict(name="Отсев 0–5", gen="отсева", acc="отсев", price=500, dens=(1.40, 1.50), src="partner"),
    "pgs":             dict(name="ПГС", gen="ПГС", acc="ПГС", price=500, dens=(1.60, 1.70), src="partner"),
    "shchps":          dict(name="ЩПС", gen="ЩПС", acc="ЩПС", price=700, dens=None, src="market"),
    "graviy":          dict(name="Гравий", gen="гравия", acc="гравий", price=900, dens=(1.40, 1.50), src="market"),
    "galka":           dict(name="Галька", gen="гальки", acc="гальку", price=900, dens=(1.40, 1.60), src="market"),
    "skalnyy-grunt":   dict(name="Скальный грунт", gen="скального грунта", acc="скальный грунт", price=400, dens=(1.60, 1.80), src="partner"),
    "keramzit":        dict(name="Керамзит", gen="керамзита", acc="керамзит", price=1500, dens=(0.25, 0.45), src="market"),
    "granitnaya-kroshka": dict(name="Гранитная крошка", gen="гранитной крошки", acc="гранитную крошку", price=1600, dens=None, src="market"),
    "asfaltovaya-kroshka": dict(name="Асфальтовая крошка", gen="асфальтовой крошки", acc="асфальтовую крошку", price=500, dens=None, src="market"),
    "butovyy-kamen":   dict(name="Бутовый камень", gen="бутового камня", acc="бутовый камень", price=1200, dens=None, src="market"),
    # --- фасовка (цена за мешок 25 кг, прайс партнёра; где цены нет — по заявке)
    "shcheben-meshok": dict(name="Щебень в мешках", gen="щебня в мешках", acc="щебень в мешках", price=90, unit="мешок", dens=None, src="partner"),
    "pesok-meshok":    dict(name="Песок в мешках", gen="песка в мешках", acc="песок в мешках", price=125, unit="мешок", dens=None, src="partner"),
    "otsev-meshok":    dict(name="Отсев в мешках", gen="отсева в мешках", acc="отсев в мешках", price=None, unit="мешок", dens=None, src="request"),
    "keramzit-meshok": dict(name="Керамзит в мешках", gen="керамзита в мешках", acc="керамзит в мешках", price=None, unit="мешок", dens=None, src="request"),
}
for _k, _m in M.items():
    _m.setdefault("unit", "м³")
    _m["key"] = _k

# Запас на уплотнение для калькулятора объёма (сколько добавить к объёму слоя):
# щебень садится на 10–30%, песок и отсев — на 10–15%, керамзит почти не садится.
COMP = {"shcheben": 1.2, "pesok": 1.12, "otsev": 1.12, "pgs": 1.2, "shchps": 1.2, "graviy": 1.15, "galka": 1.1,
        "skalnyy-grunt": 1.25, "keramzit": 1.05, "granitnaya-kroshka": 1.1, "asfaltovaya-kroshka": 1.25, "butovyy-kamen": 1.1}


def comp(key):
    return next(v for k, v in COMP.items() if key == k or key.startswith(k + "-"))

# Готовые объёмы щебня с доставкой по Екатеринбургу (прайс партнёра, август 2026).
# Две ценовые группы: 5–20 дороже остальных.
LOTS = {
    "shcheben-20-40": {5: 5800, 8: 8000, 10: 10800, 12: 12600},
    "shcheben-40-70": {5: 5800, 8: 8000, 10: 10800, 12: 12600},
    "shcheben-5-20":  {5: 5900, 8: 8200, 10: 11300, 12: 13200},
}


def total(key, vol, lots=True):
    """Итог с доставкой за vol м³: материал + рейсы (по Екатеринбургу и до 50 км).
    По Екатеринбургу у щебня с готовыми объёмами — меньшее из расчёта и ближайшего
    готового объёма не меньше vol; в городах области (lots=False) — только расчёт:
    готовые объёмы у партнёра — с доставкой по Екатеринбургу."""
    m = M[key]
    assert m["unit"] == "м³" and m["price"], key
    t = m["price"] * vol + math.ceil(vol / TRIP_M3) * DELIVERY
    ready = [p for v, p in LOTS.get(key, {}).items() if v >= vol] if lots else []
    return min([t] + ready)


# Страницы материалов по Екатеринбургу. ref — по какой позиции показывать
# «куб … от …» на первом экране и считать итог с доставкой.
PAGES = {
    "shcheben":       dict(slug="shcheben-ekaterinburg", name="Щебень", gen="щебня", acc="щебень", ref="shcheben-20-40"),
    "pesok":          dict(slug="pesok-ekaterinburg", name="Песок", gen="песка", acc="песок", ref="pesok-karernyy"),
    "otsev":          dict(slug="otsev-ekaterinburg", name="Отсев", gen="отсева", acc="отсев", ref="otsev"),
    "pgs":            dict(slug="pgs-ekaterinburg", name="ПГС", gen="ПГС", acc="ПГС", ref="pgs"),
    "shchps":         dict(slug="shchps-ekaterinburg", name="ЩПС", gen="ЩПС", acc="ЩПС", ref="shchps"),
    "graviy":         dict(slug="graviy-ekaterinburg", name="Гравий", gen="гравия", acc="гравий", ref="graviy"),
    "galka":          dict(slug="galka-ekaterinburg", name="Галька", gen="гальки", acc="гальку", ref="galka"),
    "skalnyy-grunt":  dict(slug="skalnyy-grunt-ekaterinburg", name="Скальный грунт", gen="скального грунта", acc="скальный грунт", ref="skalnyy-grunt"),
    "keramzit":       dict(slug="keramzit-ekaterinburg", name="Керамзит", gen="керамзита", acc="керамзит", ref="keramzit"),
    "granitnaya-kroshka": dict(slug="granitnaya-kroshka-ekaterinburg", name="Гранитная крошка", gen="гранитной крошки", acc="гранитную крошку", ref="granitnaya-kroshka"),
    "asfaltovaya-kroshka": dict(slug="asfaltovaya-kroshka-ekaterinburg", name="Асфальтовая крошка", gen="асфальтовой крошки", acc="асфальтовую крошку", ref="asfaltovaya-kroshka"),
    "butovyy-kamen":  dict(slug="butovyy-kamen-ekaterinburg", name="Бутовый камень", gen="бутового камня", acc="бутовый камень", ref="butovyy-kamen"),
}
PAGE_ORDER = list(PAGES)

# Виды и фракции со своим спросом — отдельные страницы (ключ M → slug).
TYPES = {
    "shcheben-5-20": "shcheben-5-20-ekaterinburg",
    "shcheben-20-40": "shcheben-20-40-ekaterinburg",
    "shcheben-40-70": "shcheben-40-70-ekaterinburg",
    "shcheben-70-120": "shcheben-70-120-ekaterinburg",
    "shcheben-mramornyy": "shcheben-mramornyy-ekaterinburg",
    "pesok-rechnoy": "pesok-rechnoy-ekaterinburg",
    "pesok-stroitelnyy": "pesok-stroitelnyy-ekaterinburg",
    "pesok-karernyy": "pesok-karernyy-ekaterinburg",
    "pesok-mytyy": "pesok-mytyy-ekaterinburg",
    "pesok-peskostruy": "pesok-dlya-peskostruya-ekaterinburg",
    "shcheben-meshok": "shcheben-v-meshkah-ekaterinburg",
    "pesok-meshok": "pesok-v-meshkah-ekaterinburg",
    "otsev-meshok": "otsev-v-meshkah-ekaterinburg",
    "keramzit-meshok": "keramzit-v-meshkah-ekaterinburg",
}

# Города: ключ, название, «в …», «по …», км от Екатеринбурга (как у грунта и дров).
CITIES = {
    "nizhniy-tagil":    ("Нижний Тагил", "в Нижнем Тагиле", "Нижнему Тагилу", 140),
    "pervouralsk":      ("Первоуральск", "в Первоуральске", "Первоуральску", 45),
    "kamensk-uralskiy": ("Каменск-Уральский", "в Каменске-Уральском", "Каменску-Уральскому", 100),
    "polevskoy":        ("Полевской", "в Полевском", "Полевскому", 55),
    "revda":            ("Ревда", "в Ревде", "Ревде", 45),
    "asbest":           ("Асбест", "в Асбесте", "Асбесту", 85),
    "novouralsk":       ("Новоуральск", "в Новоуральске", "Новоуральску", 70),
    "berezovskiy":      ("Берёзовский", "в Берёзовском", "Берёзовскому", 15),
    "verhnyaya-pyshma": ("Верхняя Пышма", "в Верхней Пышме", "Верхней Пышме", 15),
    "rezh":             ("Реж", "в Реже", "Режу", 85),
    "sysert":           ("Сысерть", "в Сысерти", "Сысерти", 50),
    "aramil":           ("Арамиль", "в Арамиле", "Арамилю", 25),
}

# Какие материалы по каким городам — только там, где есть спрос (Вордстат,
# ursdom/audit: dostavka-sverdlovsk.csv, bukvarix-geo.csv).
CITY_PAGES = {
    "shcheben": ["nizhniy-tagil", "pervouralsk", "kamensk-uralskiy", "polevskoy", "revda", "asbest",
                 "novouralsk", "berezovskiy", "verhnyaya-pyshma", "rezh", "sysert", "aramil"],
    "pesok":    ["nizhniy-tagil", "kamensk-uralskiy", "berezovskiy", "asbest", "pervouralsk", "polevskoy", "revda"],
    "otsev":    ["nizhniy-tagil", "berezovskiy", "pervouralsk"],
    "keramzit": ["nizhniy-tagil", "pervouralsk", "kamensk-uralskiy"],
}


def is_near(city):
    return CITIES[city][3] <= NEAR_KM


def city_slug(page_key, city):
    return f"{page_key}-{city}"
