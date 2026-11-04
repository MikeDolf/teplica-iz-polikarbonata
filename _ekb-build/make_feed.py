# -*- coding: utf-8 -*-
"""Прайс для карточки в Яндекс Бизнесе: /price/yandex-business.xml (4 ноября 2026).

Запуск:  python3 _ekb-build/make_feed.py   (сам вызывается в конце сборок
грунта, дров и щебня — файл не может разойтись с ценами на сайте).

Зачем. Владелец: «делай файл с ценами». Яндекс Товары нам не подходят: им нужна
корзина («форма заявки не заменяет корзину»), а проверяющий звонит на телефон
сайта — владелец звонков не принимает. Фиды Вебмастера — для услуг
(«Исполнители»), а мы продаём материал с доставкой. Подходит прайс карточки
Яндекс Бизнеса: товары с ценами показываются в карточке в Поиске и на Картах,
его можно подключить YML-фидом по ссылке, и он обновляется сам.

Требования прайса (справка Яндекс Бизнеса «Прайс-лист компании»): обязательны
category, categoryId, name, vendor, offer id, price, currencyId; цена — одно
число, без диапазонов; available="unknown" не показывается; до 10 000 позиций,
в Картах — около 500. Цены — те же, что на страницах («от»), условия — в описании.
vendor — «Без бренда»: мы не производитель и так не пишем.
Фото — только настоящие, с наших доставок (raboty/), и только там, где на снимке
именно этот материал; у остальных позиций фото нет.

Файл переписывается, только если изменились позиции (дата в шапке не в счёт),
чтобы каждая сборка не плодила изменений в git.
"""
import os
import re
import sys
import datetime
from xml.sax.saxutils import escape, quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(HERE, "data"), os.path.join(ROOT, "_drova-build"), os.path.join(ROOT, "_nerud-build")):
    if p not in sys.path:
        sys.path.append(p)

import drova_data as DR          # noqa: E402
import nerud_data as NR          # noqa: E402
from prices import PRODBAR, PRICES  # noqa: E402
from site_config import SITE     # noqa: E402

OUT = os.path.join(ROOT, "price", "yandex-business.xml")
DOMAIN = SITE["domain"]
PHOTO = DOMAIN + "/assets/ekb/photo/raboty/{}-800.jpg"
VENDOR = "Без бренда"

CATS = [(1, "Дрова"), (2, "Брикеты, пеллеты и уголь"), (3, "Грунт и органика"),
        (4, "Щебень"), (5, "Песок"), (6, "Другие сыпучие материалы")]

# Реальные снимки, где виден именно этот материал (подписи — drova_works.py, works.py).
PICS = {
    "berezovye": "drova-berezovye-churki-ploshchadka",   # «Берёзовые чурки и колотые дрова на площадке»
    "churki": "drova-berezovye-churki-ploshchadka",
    "brikety": "brikety-v-gazeli",                       # «Упаковки брикетов RUF в кузове ГАЗели»
    "Чернозём": "vygruzka-uchastok",                     # «Самосвал выгружает чернозём у ворот»
    "Перегной": "dve-kuchi-uchastok",                    # «перегной и плодородный грунт»
    "Плодородный грунт": "dve-kuchi-uchastok",
}

NO_EXTRA = "Оплата после выгрузки, на месте ничего не добавляем."


def ru(n):
    return f"{int(n):,}".replace(",", " ")


def page_exists(url):
    return os.path.exists(os.path.join(ROOT, url.strip("/"), "index.html"))


def offers():
    out = []

    def add(oid, cat, name, price, url, desc, pic=None):
        assert price and int(price) > 0, oid
        assert page_exists(url), (oid, url)
        assert len(name) <= 250 and len(desc) <= 3000, oid
        out.append(dict(id=oid, cat=cat, name=name, price=int(price), url=DOMAIN + url, desc=desc,
                        pic=PHOTO.format(pic) if pic else None))

    # Дрова: цены с доставкой по Екатеринбургу — 1, 3 и 10 м³, как на странице.
    for k in DR.ORDER:
        p = DR.PRODUCTS[k]; url = f"/{p['slug']}/"
        base = (f"В плотной укладке, с доставкой и выгрузкой по Екатеринбургу. 1 м³ — от {ru(p['t1'])} ₽, "
                f"3 м³ — от {ru(p['t3'])} ₽, машина {DR.REF_VOL} м³ — от {ru(p['t10'])} ₽. {NO_EXTRA}")
        add(f"{k}-1", 1, f"{p['name']}, 1 м³ с доставкой", p["t1"], url, base, PICS.get(k))
        add(f"{k}-3", 1, f"{p['name']}, 3 м³ с доставкой", p["t3"], url, base, PICS.get(k))
        add(f"{k}-{DR.REF_VOL}", 1, f"{p['name']}, {DR.REF_VOL} м³ с доставкой", p["t10"], url, base, PICS.get(k))

    # Брикеты, пеллеты, уголь — без доставки, как на странице.
    unit_name = {"brikety": "упаковка 12 шт.", "pellety": "мешок 30 кг", "ugol": "мешок 25 кг", "drev-ugol": "1 кг"}
    for k in DR.FUEL_ORDER:
        f = DR.FUEL[k]; url = f"/{f['slug']}/"
        note = f.get("note") or {"мешок": "Цена за мешок 25 кг, без доставки.", "кг": "Цена за килограмм, без доставки."}[f["unit"]]
        desc = note + " Доставку назовём по адресу, вместе с дровами привезём одним рейсом."
        add(k, 2, f"{f['name']}, {unit_name[k]}", f["price"], url, desc, PICS.get(k))
        if f.get("price_t"):
            add(f"{k}-t", 2, f"{f['name']}, 1 тонна навалом", f["price_t"], url, "Тонна навалом, без доставки. " +
                "Доставку назовём по адресу, вместе с дровами привезём одним рейсом.")

    # Грунт и органика — цена материала, доставка отдельно (как на странице).
    g_desc = ("Цена за материал навалом, за 1 м³. Доставку считаем отдельно, по расстоянию до адреса: "
              "точную сумму покажет калькулятор на странице. " + NO_EXTRA)
    for b in PRODBAR:
        if b["name"] == "Навоз":
            continue   # навоз — двумя позициями ниже, коровий и конский
        price = int(re.sub(r"\D", "", b["price"].split("₽")[0]))
        bag = "мешок" in b["price"]
        name = f"{b['name']}, 1 мешок" if bag else f"{b['name']}, 1 м³"
        desc = ("Цена за мешок. Доставку считаем отдельно, по расстоянию до адреса. " + NO_EXTRA) if bag else g_desc
        add(b["slug"], 3, name, price, b["url"], desc, PICS.get(b["name"]))
    for nm, url in (("Навоз коровий", "/navoz-koroviy-ekaterinburg/"), ("Навоз конский", "/navoz-konskiy-ekaterinburg/")):
        add(url.strip("/"), 3, f"{nm}, 1 м³", PRICES[nm]["m3"], url, g_desc)

    # Щебень, песок и другие сыпучие — цена материала без доставки + КамАЗ 10 м³ с доставкой.
    special = {"shcheben-meshok": "/shcheben-v-meshkah-ekaterinburg/", "pesok-meshok": "/pesok-v-meshkah-ekaterinburg/",
               "pesok-peskostruy": "/pesok-dlya-peskostruya-ekaterinburg/"}
    unit_txt = {"м³": "1 м³", "мешок": "1 мешок", "т": "1 тонна"}
    for k, m in NR.M.items():
        if not m["price"]:
            continue
        url = special.get(k, f"/{k}-ekaterinburg/")
        cat = 4 if k.startswith("shcheben") else 5 if k.startswith("pesok") else 6
        if m["unit"] == "м³":
            desc = (f"Цена за 1 м³ без доставки. С доставкой по Екатеринбургу: 10 м³ — от {ru(NR.total(k, 10))} ₽, "
                    f"рейс — от {ru(NR.DELIVERY)} ₽. {NO_EXTRA}")
        else:
            desc = f"Цена за {({'мешок': 'мешок', 'т': 'тонну'})[m['unit']]}, без доставки. Доставку назовём по адресу. {NO_EXTRA}"
        add(k, cat, f"{m['name']}, {unit_txt[m['unit']]}", m["price"], url, desc)
    for k in ("shcheben-20-40", "shcheben-5-20", "shcheben-40-70", "pesok-karernyy", "pgs", "otsev"):
        m = NR.M[k]
        add(f"{k}-10", 4 if k.startswith("shcheben") else 5 if k.startswith("pesok") else 6,
            f"{m['name']}, 10 м³ (КамАЗ) с доставкой", NR.total(k, 10), f"/{k}-ekaterinburg/",
            f"Полный КамАЗ, 10 м³, с доставкой по Екатеринбургу. Объём видно по кузову до выгрузки. {NO_EXTRA}")
    ids = [o["id"] for o in out]
    assert len(ids) == len(set(ids)), "повтор id в фиде"
    return out


def render(items, stamp):
    L = ['<?xml version="1.0" encoding="UTF-8"?>', f'<yml_catalog date="{stamp}">', "  <shop>",
         "    <name>Доставка дров, грунта, щебня и песка</name>",
         f"    <company>{escape(SITE['legal_name'])}</company>",
         f"    <url>{DOMAIN}/</url>",
         '    <currencies><currency id="RUB" rate="1"/></currencies>', "    <categories>"]
    L += [f'      <category id="{i}">{escape(n)}</category>' for i, n in CATS]
    L += ["    </categories>", "    <offers>"]
    for o in items:
        L += [f'      <offer id={quoteattr(o["id"])} available="true">',
              f"        <name>{escape(o['name'])}</name>",
              f"        <vendor>{VENDOR}</vendor>",
              f"        <url>{escape(o['url'])}</url>",
              f"        <price>{o['price']}</price>",
              "        <currencyId>RUB</currencyId>",
              f"        <categoryId>{o['cat']}</categoryId>"]
        if o["pic"]:
            L.append(f"        <picture>{escape(o['pic'])}</picture>")
        L += [f"        <description>{escape(o['desc'])}</description>", "      </offer>"]
    L += ["    </offers>", "  </shop>", "</yml_catalog>", ""]
    return "\n".join(L)


def main():
    items = offers()
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5))).strftime("%Y-%m-%dT%H:%M:%S+05:00")
    new = render(items, stamp)
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    strip = lambda s: re.sub(r'<yml_catalog date="[^"]*">', "", s)
    if strip(old) != strip(new):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        open(OUT, "w", encoding="utf-8").write(new)
        print(f"Фид Яндекс Бизнеса: {len(items)} позиций → /price/yandex-business.xml")
    return len(items)


if __name__ == "__main__":
    main()
