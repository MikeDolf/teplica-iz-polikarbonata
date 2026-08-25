# -*- coding: utf-8 -*-
"""Сборка лид-ген страниц раздела доставки грунта.
Запуск:  python3 _ekb-build/build.py
Рендерит страницы из data/pages.py в корень репозитория (папки /slug/index.html).
Генератор нужен только для пересборки, сам сайт работает без него.
"""
import os, sys, json, re, zlib
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "data"))
from jinja2 import Environment, FileSystemLoader, select_autoescape
from site_config import SITE  # noqa
from cities import CITIES      # noqa
from pages import PAGES        # noqa
from products import PRODUCTS, GEO_PAGES, USES, USES_DEFAULT  # noqa
from articles import ARTICLES  # noqa
from blog import BLOG  # noqa
from prices import PRICES, MATERIALS_PRICE, FLEET_VIZ, PRODBAR, DENSITY, CALC_ORDER  # noqa
from tail_cities import TAIL_CITIES
from city_product import CP, CPF  # noqa
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


def ru_number(n):
    """Разряды через неразрывный тонкий пробел: 13 300, а не 13300.

    Тот же формат, что у калькулятора в JS, иначе на одной странице цифры
    выглядели бы по-разному."""
    return f"{int(n):,}".replace(",", "\u2009")


env.filters["ru"] = ru_number



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

# Нерудные материалы ведёт отдельный сайт владельца (ursdom.ru).
# Держим страницы живыми для прямых заходов, но вне индекса, чтобы два
# сайта одного владельца не конкурировали за одни запросы в одном регионе
# (риск аффилиат-фильтра Яндекса).
OTHER_SITE = {
    "shcheben-ekaterinburg", "pesok-ekaterinburg",
    "otsev-ekaterinburg", "pgs-ekaterinburg",
}

# Пусто по решению владельца от 08.08.2026: раздел доводится до полной
# сетки 11 товаров x 15 городов, включая сочетания с нулевым спросом по
# Вордстату. Прежняя чистка (14 страниц) отменена. Список слугов и причин
# сохранён в истории git, коммит d4c0d56.
LOW_DEMAND = set()

NOINDEX = OTHER_SITE | LOW_DEMAND

# Точечные внешние ссылки на профильный проект: только на 2 страницах,
# чтобы не создавать сквозной шаблонный линк со всего раздела.
CROSSLINK = {
    # Связка «товар вообще» ↔ «товар в мешках»: автоматическая перелинковка
    # их не соединяет, у них совпадают и товар, и город. Страницы фасовки
    # оставлены под запрос «в мешках», но ведут они теперь на объяснение,
    # почему возим навалом, а не на предложение мешков.
    "peregnoy-ekaterinburg": {"title":"Искали перегной в мешках?","text":"Фасовку мы не возим: поставщика по мешкам у нас нет. Минимальный заказ три куба навалом, и на отдельной странице разобрано, сколько это в мешках для тех, кто привык считать ими, во что обходится куб против фасовки в магазине и как разгрузиться, если самосвалу негде встать.","url":"/peregnoy-v-meshkah-ekaterinburg/","anchor":"Перегной в мешках: почему возим навалом"},
    "peregnoy-v-meshkah-ekaterinburg": {"title":"Готовы взять навалом?","text":"Тогда смотрите общую страницу перегноя: цены за куб, нормы внесения по культурам, расчёт объёма под теплицу и грядки и условия доставки. Минимальный заказ три куба, машину подаём к месту выгрузки.","url":"/peregnoy-ekaterinburg/","anchor":"Перегной навалом, цена за куб"},
    "opilki-ekaterinburg": {"title":"Искали опил в мешках?","text":"Фасовку мы не возим, поставщика по мешкам у нас нет. Возим навалом от трёх кубов. На отдельной странице разобран расход опила по задачам, подстилка, мульча и дорожки, и сколько это выходит в пересчёте на привычные мешки.","url":"/opilki-v-meshkah-ekaterinburg/","anchor":"Опил в мешках: почему возим навалом"},
    "opilki-v-meshkah-ekaterinburg": {"title":"Готовы взять навалом?","text":"Смотрите общую страницу: там про свежий и перепревший опил, хвойный и лиственный, чем они отличаются на подстилке и под мульчей, и цены за куб. Минимальный заказ три куба.","url":"/opilki-ekaterinburg/","anchor":"Опил и опилки навалом"},
    # Страницы под задачу: автоматическая перелинковка даёт им ссылки, но
    # не связывает с родительским товаром, у них тот же товар и тот же город.
    "plodorodnyy-grunt-ekaterinburg": {"title":"Меняете грунт в теплице?","text":"Под теплицу считают не площадь участка, а площадь теплицы и толщину слоя: три на шесть при замене 20 см это 3,6 куба. На отдельной странице разобрано, какой слой менять, что нельзя класть в закрытый грунт и сколько выходит по кубам.","url":"/grunt-dlya-teplicy-ekaterinburg/","anchor":"Грунт для теплицы, расчёт и цены"},
    "torfogrunt-ekaterinburg": {"title":"Готовите основание под газон?","text":"Газон живёт в верхних 10-15 сантиметрах, и всё решает этот слой. На отдельной странице расчёт объёма по соткам, разница подготовки под посев и под рулон и порядок работ до посева.","url":"/zemlya-pod-gazon-ekaterinburg/","anchor":"Земля под газон, расчёт объёма"},
    "grunt-dlya-teplicy-ekaterinburg": {"title":"Нужен тот же грунт под другие задачи?","text":"Под газон, клумбы, подъём участка и отсыпку берут тот же плодородный грунт, но слой и расчёт другие. Виды, цены за куб и условия доставки собраны на общей странице.","url":"/plodorodnyy-grunt-ekaterinburg/","anchor":"Плодородный грунт в Екатеринбурге"},
    "zemlya-pod-gazon-ekaterinburg": {"title":"Поднимаете участок целиком?","text":"Под газон нужен слой 10-15 см, под подъём участка от воды объёмы совсем другие и пирог делается слоями. Как считать и чем засыпать нижний слой, разобрано в отдельной статье.","url":"/dostavka-grunta/blog/chem-podnyat-uchastok/","anchor":"Чем поднять участок: расчёт и материалы"},
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
    # Страницы направлений в подвале: иначе входящих ссылок у них было бы
    # только две, из хаба. По этим двум трактам идёт основной поток рейсов,
    # и сквозная ссылка тут оправдана.
    {"url": "/dostavka-grunta-chelyabinskiy-trakt/", "text": "Челябинский тракт"},
    {"url": "/dostavka-grunta-polevskoy-trakt/", "text": "Полевской тракт"},
    {"url": "/dostavka-grunta/blog/", "text": "Блог"},
]

def build_localbusiness():
    lb = {
        "@type": "LocalBusiness",
        "name": SITE["brand"],
        "url": SITE["domain"] + "/dostavka-grunta/",
        "email": SITE["contact_email"],
        "areaServed": SITE["region"],
        "openingHours": "Mo-Su 00:00-23:59",   # круглосуточно, без выходных
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
    # Product с ценой: без него цена не попадает в сниппет выдачи.
    # Цены на сайте вида «от N», поэтому AggregateOffer с lowPrice, а не
    # фиксированный Offer: так разметка не обещает точную стоимость.
    pr = PRICES.get(page.get("product"))
    if pr and page["kind"] in ("money", "geo"):
        img = None
        for key in sorted(PRODUCTS, key=len, reverse=True):
            if page["slug"] == key or page["slug"].startswith(key + "-"):
                if key in PHOTOS: img = f'{SITE["domain"]}/assets/ekb/photo/{key}-400.jpg'
                break
        offer = {
            "@type": "AggregateOffer",
            "priceCurrency": "RUB",
            "lowPrice": pr["m3"],
            "availability": "https://schema.org/InStock",
            "areaServed": CITIES[page["city"]]["name"],
            "seller": {"@type": "LocalBusiness", "name": SITE["brand"]},
            # Срок действия цены: без него поисковики помечают предложение
            # как неполное. Ставим конец следующего года, а не «сегодня плюс
            # год»: иначе разметка менялась бы при каждой пересборке и
            # сборка перестала бы быть воспроизводимой.
            "priceValidUntil": f"{date.today().year + 1}-12-31",
        }
        prod = {
            "@type": "Product",
            "name": page["h1"],
            "description": page["description"],
            "category": "Грунт и органические удобрения",
            "brand": {"@type": "Organization", "name": SITE["brand"]},
            "offers": offer,
            # Картинка обязательна для товарного сниппета. Если своего фото
            # у материала нет, отдаём общее: пустое поле хуже, чем общее.
            "image": img or f'{SITE["domain"]}/assets/ekb/photo/hero-default-1400.jpg',
        }
        # Рейтинг и отзывы. Разметка появляется ТОЛЬКО если в reviews.py есть
        # настоящие отзывы: размечать выдуманные нельзя, это и нарушение
        # правил Яндекса о достоверности разметки, и статья 5 ФЗ «О рекламе».
        # Сейчас REVIEWS пуст, поэтому блок не выводится, но проводка готова:
        # как только владелец добавит реальные отзывы, звёзды поедут в сниппет
        # сами, без правки шаблонов.
        rated = [r for r in REVIEWS if r.get("stars")]
        if rated:
            prod["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": round(sum(r["stars"] for r in rated) / len(rated), 1),
                "reviewCount": len(rated),
                "bestRating": 5, "worstRating": 1,
            }
            prod["review"] = [{
                "@type": "Review",
                "author": {"@type": "Person", "name": r["name"]},
                "datePublished": r.get("date_iso", ""),
                "reviewBody": r["text"],
                "reviewRating": {"@type": "Rating", "ratingValue": r["stars"],
                                 "bestRating": 5, "worstRating": 1},
            } for r in rated]
        graph.append(prod)

    if page.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in page["faq"]
            ],
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))




def hero_photo_for(page):
    """Фото в шапку подбираем по ключу товара, а не по слугу страницы:
    у торфа по Берёзовскому и по Екатеринбургу материал один и тот же."""
    slug = page["slug"]
    for key in sorted(PRODUCTS, key=len, reverse=True):
        if slug == key or slug.startswith(key + "-"):
            name = "hero-" + key
            if name in PHOTOS:
                return name
            break
    # у товара своего кадра нет: ставим общий с самосвалом, он честно
    # показывает услугу и лучше векторной заглушки
    return "hero-default" if "hero-default" in PHOTOS else None


def product_genitive(page):
    """Родительный падеж товара для заголовков. Берём по ключу товара, а не по
    чипу формы: у земли в мешках и общего навоза чип общий с соседним товаром,
    и по чипу подставлялся чужой материал."""
    slug = page["slug"]
    for key in sorted(PRODUCTS, key=len, reverse=True):
        if slug == key or slug.startswith(key + "-"):
            return PRODUCTS[key]["gen"]
    return "грунта"


def hero_alt_for(page):
    """Осмысленный alt для фото в шапке: «Чернозём с доставкой в Нижнем Тагиле».
    Берём имя товара по ключу, а не чип формы: у пары навоз/навоз коровий
    чип общий."""
    key = product_key_of(page)
    name = TAIL_NAME.get(key) or page.get("product", "грунт")
    name = name[0].upper() + name[1:]
    city = CITIES.get(page.get("city"), {})
    where = city.get("prep") or ""
    return f"{name} с доставкой {where}".strip()


def product_key_of(page):
    slug = page["slug"]
    for key in sorted(PRODUCTS, key=len, reverse=True):
        if slug == key or slug.startswith(key + "-"):
            return key
    return ""


def product_rates(page):
    """Таблица норм внесения, если она у товара описана. Ключ берём по слугу,
    как и фото с падежом: чип формы для этого не годится."""
    slug = page["slug"]
    for key in sorted(PRODUCTS, key=len, reverse=True):
        if slug == key or slug.startswith(key + "-"):
            return PRODUCTS[key].get("rates")
    return None


def bag_note(product_key):
    """Расшифровка минимального заказа.

    Пока возили фасовку, минимум объясняли мешками: «3 м³, это 60-75 мешков».
    Поставщика по мешкам нет, и та же фраза теперь работает против нас: она
    приглашает написать «а мне нужно десять мешков», хотя ответить на такую
    заявку нечем. При выключенном SITE["bags"] объясняем минимум машиной.
    Вес мешка пишем только там, где он известен: у торфа и опилок плотность
    в разы ниже, и 40 кг было бы враньём.
    """
    if not SITE.get("bags"):
        return "это неполный кузов самосвала"
    kg = PRODUCTS.get(product_key, {}).get("bag_kg")
    tail = f", около {kg} кг каждый" if kg else ""
    return f"это 60-75 мешков по 40-50 л{tail}"


def delivery_min_rub(city_key):
    """Минимальная стоимость рейса в город: плечо от базы, туда и обратно."""
    km = CITIES[city_key]["base_km"]
    return km * SITE["km_price"] * (2 if SITE["km_round_trip"] else 1)


def money_meta(product_key, city_key):
    """Title и description с ценой. По Вебмастеру запросы со словом «недорого»
    дают показы и ноль кликов: в сниппете стояло обещание назвать цену, а не
    сама цена. Цифру ставим в title, слово «недорого» уводим в description,
    чтобы не занимать место в заголовке."""
    pr = PRODUCTS[product_key]
    city = CITIES[city_key]
    price = PRICES.get(pr["chip"])
    if not price:
        return None, None
    # Товар может забрать сниппет себе: у страниц под запрос «в мешках»
    # шаблонная строка с ценой за куб не объясняет главного, что фасовки
    # нет, а это и нужно сказать до клика. Тогда берутся title_tpl/desc_tpl.
    if pr.get("meta_override"):
        return None, None
    # seo_name нужен там, где в регионе в ходу другое слово: «опил» и
    # «опилки» для поиска — разные леммы, и в title нужны обе.
    label = pr.get("seo_name", pr["name"])
    title = f'{label} {city["prep"]} — от {price["m3"]} ₽/м³'
    if SITE.get("bags") and price.get("bag"):
        wide = f'{title} и {price["bag"]} ₽/мешок'
        title = wide if len(wide) <= 68 else f"{title} с доставкой"
    else:
        # Минимум уводим в title: запрос «от 3 м³» никто не набирает, но
        # сниппет читают до клика, и человек с задачей на пару вёдер
        # отсеивается ещё в выдаче, а не в переписке.
        wide = f"{title}, от 3 м³"
        title = wide if len(wide) <= 68 else f"{title} с доставкой"
    if SITE.get("bags") and price.get("bag"):
        bag = f' и {price["bag"]} ₽/мешок'
        kg = PRODUCTS[product_key].get("bag_kg")
        mini = 'Минимальный заказ 3 м³ — 60-75 мешков' + (f' по {kg} кг.' if kg else ' по 40-50 л.')
    else:
        bag = ""
        mini = (f'Минимальный заказ 3 м³, возим только навалом. '
                f'Доставка {SITE["km_price"]} ₽/км {SITE["base_city_iz"]}.')
    desc = (f'{label} с доставкой {city["to"]} недорого: от {price["m3"]} ₽/м³{bag} '
            f'за материал, {pr.get("desc_hook", "")}. {mini}')
    return title, " ".join(desc.split())


REPEAT_SEEN = set()


def publisher_node():
    """Издатель для Article. Логотип обязателен для расширенных сниппетов:
    без него Google помечает разметку как неполную."""
    return {
        "@type": "Organization",
        "name": SITE["brand"],
        "url": SITE["domain"] + "/dostavka-grunta/",
        "logo": {"@type": "ImageObject",
                 "url": SITE["domain"] + "/assets/ekb/photo/hero-default-1400.jpg"},
    }


def article_node(a, canonical, cover, kind="Article"):
    """Узел Article с датами, картинкой и автором.

    Без datePublished в сниппете нет даты, а для информационных статей
    свежесть заметно влияет на клик. Автором ставим организацию: живого
    подписанта у текстов нет, и выдумывать его нельзя.
    """
    img = (SITE["domain"] + f"/assets/ekb/photo/{cover}-1400.jpg") if cover else \
          (SITE["domain"] + "/assets/ekb/photo/hero-default-1400.jpg")
    node = {
        "@type": kind,
        "headline": a["h1"],
        "description": a["description"],
        "inLanguage": "ru-RU",
        "mainEntityOfPage": canonical,
        "image": img,
        "author": {"@type": "Organization", "name": SITE["brand"],
                   "url": SITE["domain"] + "/dostavka-grunta/"},
        "publisher": publisher_node(),
    }
    if a.get("date"):
        node["datePublished"] = a["date"]
        node["dateModified"] = a.get("updated", a["date"])
    return node


def check_repeats(html, slug, seen=REPEAT_SEEN):
    """Ищем задвоенные фразы в готовой странице.

    Ловушка возникает, когда значение из конфига уже содержит фразу, а
    шаблон дописывает её ещё раз: «меньше не возим, меньше не возим, рейс
    не окупается». В шаблоне это не видно, потому что подстановка одна.
    Проверяем результат, а не исходник, и печатаем предупреждение: правило
    не должно ронять сборку, но и молчать о таком нельзя.
    """
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
    for m in re.finditer(r"\b([А-Яа-яЁё\w]+(?:\s+[А-Яа-яЁё\w]+){2,})\s*[.,;:!?—-]?\s+\1\b",
                         text, re.IGNORECASE):
        phrase = " ".join(m.group(1).split())
        if phrase in seen:
            continue
        seen.add(phrase)
        print(f"ПОВТОР ФРАЗЫ: «{phrase}» — {slug}")


def price_rows(page):
    """Строки прайс-таблицы: цена за куб и полная сумма минимального заказа.

    Последняя колонка считается под город страницы, поэтому таблица у
    каждого города своя и отвечает на вопрос «сколько это будет стоить
    мне», а не «сколько стоит куб вообще».
    """
    city_key = page.get("city", "ekaterinburg")
    ride = delivery_min_rub(city_key)
    cur = product_key_of(page)
    rows = []
    # zemlya-v-meshkah, это тот же плодородный грунт: общий чип, одна цена,
    # одна плотность. В полосе товаров он оправдан, там он ловит запрос
    # «в мешках», а в таблице цен читался бы как дубль строки.
    for p in PRODBAR:
        key = p["tex"]
        if key == "zemlya-v-meshkah":
            continue
        pr = PRICES.get(PRODUCTS.get(key, {}).get("chip"))
        if not pr:
            continue
        rows.append({"name": p["name"], "url": p["url"], "m3": pr["m3"],
                     "min_total": pr["m3"] * 3 + ride, "current": key == cur})
    return rows


def direction_cities(page):
    """Список пунктов направления для страницы тракта.

    Ссылку ведём на чернозём: это самый частый товарный запрос по каждому
    посёлку, и с него человек попадает во всю сетку через перелинковку.
    """
    keys = page.get("direction")
    if not keys:
        return []
    out = []
    for k in keys:
        out.append({"name": CITIES[k]["name"], "km": CITIES[k]["base_km"],
                    "ride": delivery_min_rub(k), "url": f"/chernozem-{k}/"})
    return sorted(out, key=lambda d: d["km"])


def compose_geo(product_key, city_key):
    pr = PRODUCTS[product_key]
    city = CITIES[city_key]
    if city_key == "ekaterinburg":
        slug = f'{product_key}-ekaterinburg'
    else:
        slug = f'{product_key}-{city_key}'
    # h1_tpl нужен там, где заголовок «<товар> <город> с доставкой» обещал бы
    # не то, что мы возим: страницы под запрос «в мешках» ловят спрос, но
    # фасовки у нас нет, и заголовок должен говорить это сразу.
    if pr.get("h1_tpl"):
        h1 = pr["h1_tpl"].format(prep=city["prep"], to=city["to"], name=city["name"])
    else:
        h1 = f'{pr.get("seo_name", pr["name"])} {city["prep"]} с доставкой'
    # город-специфичный вопрос впереди общих: уникальность FAQ
    hint = city.get("order_hint", "Возим навалом самосвалом, от трёх кубов, срок согласуем при заявке.")
    km = city["base_km"]
    ride = delivery_min_rub(city_key)
    city_q = (f'Сколько стоит доставка {city["to"]}?',
              f'{hint} Доставка считается отдельно от материала: {SITE["km_price"]} ₽ за километр '
              f'{SITE["base_city_iz"]}, рейс туда и обратно. До {city["name"]} это около {km} км, '
              f'то есть примерно {ride} ₽ за рейс независимо от того, три куба в кузове или десять. '
              f'Поэтому на большом объёме доставка в пересчёте на куб выходит заметно дешевле. '
              f'Точную цену называем в ответ на заявку под ваш объём и адрес.')
    # Вопрос под пару «город + товар» идёт первым, за ним городской, дальше
    # общие по товару: так уникальный текст стоит в начале блока.
    faq = CPF.get((city_key, product_key), []) + [city_q] + pr["faq_base"]
    mt, md = money_meta(product_key, city_key)
    return {
        "slug": slug, "city": city_key, "product": pr["chip"], "kind": "geo",
        "h1": h1,
        "title": mt or pr["title_tpl"].format(prep=city["prep"], to=city["to"]),
        "description": md or pr["desc_tpl"].format(prep=city["prep"], to=city["to"]),
        "hero_sub": pr["hero_sub"],
        # уникальный городской текст идёт первым: он задаёт непохожесть страниц
        # Уникальный для пары «город + товар» абзац идёт первым: именно он
        # отличает эту страницу от одиннадцати соседних по городу и от
        # четырнадцати соседних по товару.
        "about": ([CP[(city_key, product_key)]] if (city_key, product_key) in CP else [])
                 + city.get("about_extra", []) + pr["intro"],
        "faq": faq,
    }


# Материалы для калькулятора объёма: имя, плотность и цена «от» за куб.
def calc_materials():
    out = []
    for key in CALC_ORDER:
        pr = PRICES.get(PRODUCTS.get(key, {}).get("chip"))
        if not pr or key not in DENSITY:
            continue
        # TAIL_NAME хранит винительный падеж («землю в мешках»),
        # в списке нужен именительный.
        name = {"zemlya-v-meshkah": "земля в мешках"}.get(key, TAIL_NAME.get(key, key))
        out.append({"key": key, "name": name[0].upper() + name[1:],
                    "density": DENSITY[key], "m3": pr["m3"]})
    return out


CALC_MATERIALS = calc_materials()

# Города для калькулятора доставки: плечо в один конец от базы. Порядок по
# расстоянию, а не по алфавиту: так видно, что цена рейса зависит именно от
# километров, и ближний город не приходится искать в конце списка.
CALC_CITIES = [{"key": k, "name": CITIES[k]["name"], "km": CITIES[k]["base_km"]}
               for k in sorted(CITIES, key=lambda k: CITIES[k]["base_km"])]


def nav_label(page):
    """Подпись ссылки на страницу: «Коровий навоз, Берёзовский».

    Раньше и хаб, и перелинковка брали page["product"], а это чип формы —
    он общий у пар навоз/навоз коровий, торф/кислый торф, плодородный
    грунт/земля в мешках. В итоге ссылка на /navoz-berezovskiy/ (навоз
    вообще) подписывалась «Навоз коровий», то есть анкорный текст
    отправлял поисковику неверный сигнал и стравливал два своих URL за
    одну фразу. Имя берём по ключу товара.
    """
    if page.get("nav_text"):
        return page["nav_text"]
    name = TAIL_NAME.get(product_key_of(page))
    name = (name[0].upper() + name[1:]) if name else page.get("product", "Грунт")
    city = CITIES.get(page.get("city"), {}).get("name", "")
    return f"{name}, {city}" if city else name


def stable_hash(s):
    """Хеш, стабильный между запусками.

    Встроенный hash() для строк солится случайным PYTHONHASHSEED, поэтому
    порядок перелинковки менялся при каждой сборке: все 174 страницы
    попадали в diff, хотя контент оставался тем же.
    """
    return zlib.crc32(s.encode("utf-8"))


def attach_related(pages):
    """Проставляет каждой странице перелинковку: другие города того же продукта + другие продукты того же города."""
    by_slug = {p["slug"]: p for p in pages}
    for p in pages:
        rel = []
        # Группируем по ключу товара, а не по чипу формы: иначе навоз и
        # навоз коровий считались одним товаром и не ссылались друг на друга,
        # зато получали одинаковые анкоры.
        prod = product_key_of(p)
        city_key = p.get("city")
        # другие города того же товара
        for q in pages:
            if q is p or q["slug"] in NOINDEX: continue
            if product_key_of(q) == prod and q.get("city") != city_key:
                rel.append({"url": f'/{q["slug"]}/', "text": nav_label(q)})
        # другие товары в том же городе
        for q in pages:
            if q is p or q["slug"] in NOINDEX: continue
            if q.get("city") == city_key and product_key_of(q) != prod:
                rel.append({"url": f'/{q["slug"]}/', "text": nav_label(q)})
        # Раньше связи резались до 8 и новые страницы получали по одной
        # входящей ссылке. Показываем больше и перемешиваем порядок по слугу,
        # чтобы ссылочный вес расходился равномерно, а не на первые по алфавиту.
        rel.sort(key=lambda r: stable_hash(p["slug"] + r["url"]))
        p["related"] = rel[:14]

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
        reviews=REVIEWS,
        # «переехало» остаётся вверху: на странице щебня посетителю надо
        # сразу сказать, что мы это не возим. Тематическая же ссылка
        # уходит вниз, чтобы не уводить покупателя до знакомства с товаром.
        moved_to=MOVED_TO.get(page["slug"]),
        crosslink=CROSSLINK.get(page["slug"]),
        tail_cities=(TAIL_CITIES.get(page["slug"][:-len("-ekaterinburg")]) if page["slug"].endswith("-ekaterinburg") else None),
        rates=product_rates(page),
        # у страниц-исключений слаг не отражает товар: torf-dlya-golubiki
        # по префиксу попадает в обычный торф, поэтому список можно
        # переопределить прямо в pages.py
        uses=page.get("uses") or USES.get(product_key_of(page), USES_DEFAULT),
        calc_materials=CALC_MATERIALS,
        calc_preselect=product_key_of(page),
        direction_cities=direction_cities(page), direction_name=page.get("direction_name", ""),
        price_rows=price_rows(page),
        calc_cities=CALC_CITIES, calc_city=page.get("city", "ekaterinburg"),
        calc_km=CITIES[page.get("city", "ekaterinburg")]["base_km"],
        delivery_min=delivery_min_rub(page.get("city", "ekaterinburg")),
        bag_note=bag_note(product_key_of(page)),
        bag_kg=PRODUCTS.get(product_key_of(page), {}).get("bag_kg"),
        fleet_viz=FLEET_VIZ, prodbar=PRODBAR, current_slug=page["slug"], photos=PHOTOS,
        hero_photo=hero_photo_for(page),
        hero_alt=hero_alt_for(page),
        product_genitive=product_genitive(page),
        tail_name=TAIL_NAME.get(page["slug"][:-len("-ekaterinburg")] if page["slug"].endswith("-ekaterinburg") else ""),
    )
    outdir = os.path.join(ROOT, page["slug"])
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
        check_repeats(html, canonical)
    return page["slug"], canonical, page["slug"] not in NOINDEX


def render_hub(all_pages):
    from articles import ARTICLES as _A
    from blog import BLOG as _B
    hub_articles = [{"url": "/dostavka-grunta/blog/", "text": "Блог: расчёт объёмов, вес куба, вместимость машины"}]
    hub_articles += [{"url": f'/dostavka-grunta/blog/{b["slug"]}/', "text": b["short"]} for b in _B]
    hub_articles += [{"url": f'/dostavka-grunta/{a["slug"]}/', "text": a["short"]} for a in _A]
    canonical = f'{SITE["domain"]}/dostavka-grunta/'
    catalog = [
        {"name": "Чернозём", "note": "под грядки, газон и теплицу", "url": "/chernozem-ekaterinburg/"},
        {"name": "Перегной", "note": "перепревший, под посадку", "url": "/peregnoy-ekaterinburg/"},
        {"name": "Навоз коровий", "note": "перепревший и свежий", "url": "/navoz-koroviy-ekaterinburg/"},
        {"name": "Навоз конский", "note": "для тёплых грядок и теплиц", "url": "/navoz-konskiy-ekaterinburg/"},
        {"name": "Торф", "note": "верховой кислый и низинный", "url": "/torf-ekaterinburg/"},
        {"name": "Торф для голубики", "note": "верховой, pH 2,6-3,5", "url": "/torf-dlya-golubiki/"},
    ]
    # У страниц под задачу (грунт для теплицы, земля под газон) чип товара
    # общий с плодородным грунтом, и в списке получались три одинаковых
    # пункта. Имя для навигации можно задать в pages.py.
    # Подпись берём по ключу товара, а не по чипу формы. Чип общий у пар
    # навоз/навоз коровий, торф/кислый торф, плодородный грунт/земля в
    # мешках, поэтому в списке получались одинаковые на вид пункты,
    # ведущие на разные страницы, и так по всем 15 городам.
    geo = [{"url": f'/{p["slug"]}/', "text": nav_label(p)}
           for p in all_pages if p["slug"] not in NOINDEX]
    # Хаб был чисто навигационным: 875 слов, из них почти всё — списки
    # ссылок. По общему запросу «доставка грунта екатеринбург» ему нечем
    # было ранжироваться, тогда как товарные страницы держат по 2-3 тысячи
    # слов. Ниже текст именно про грунт как категорию, а не про товары.
    about = [
        "Грунт, земля, плодородный слой: под этими словами покупатели обычно имеют в виду одно и то же, материал, которым поднимают плодородие участка или его уровень. Но материалы за ними стоят разные, и от выбора зависит и цена, и результат. Разберём, что когда брать, а точный объём под вашу задачу посчитаем по заявке.",
        "Если нужен готовый вариант «привезли и сажаем», берут плодородный грунт или торфогрунт. Это смеси, в которых уже сбалансированы питание и рыхлость: их сыпят слоем 10-20 сантиметров под газон, в теплицу, в короба и на грядки, и сразу сажают. Чернозём самый питательный, но он плотный, и одним слоем его кладут редко: под поливом без дождей он заплывает и берётся коркой, поэтому его обычно разбавляют торфом и песком.",
        "Если земля на участке в целом нормальная и её надо просто оживить, грунт целиком везти незачем. Дешевле взять перегной или перепревший навоз и заправить ими то, что есть: перегной вносят прямо под посадку, он не жжёт корни. Свежий навоз идёт только с осени под перекопку или вниз тёплой грядки как биотопливо.",
        "Если задача не плодородие, а уровень, то есть поднять участок от воды или засыпать яму, плодородный грунт в основание не кладут: он просядет и закиснет. Насыпь делают слоями, снизу песок или ПГС на объём, сверху 10-20 сантиметров плодородного слоя. Нерудные материалы для нижнего слоя мы не возим, их берут у профильных поставщиков.",
        "Объём считается одинаково для любого материала: площадь умножить на толщину слоя. Куб на сотку даёт слой в один сантиметр, значит сотка под слой 10 сантиметров это 10 кубов, теплица три на шесть при замене 20 сантиметров это 3,6 куба. К расчёту добавляют примерно пятую часть на усадку: свежая насыпь садится после первого полива. Посчитать можно калькулятором выше, он же покажет стоимость рейса до вашего адреса.",
        "Возим только навалом, самосвалом, и минимальный заказ у нас три кубометра. Это кузов малого самосвала: хватает на теплицу целиком, десяток грядок или закладку ягодника. Меньше не возим, и дело не в жадности: машина выезжает, грузится и едет одинаково что под три куба, что под десять, поэтому рейс за полкуба не окупается ни нам, ни вам. Фасовки в мешках у нас нет, поставщика по ней мы не нашли и обещать её не будем.",
        "Работаем по Екатеринбургу и области примерно до 100 километров от базы в Верхней Пышме. По городу и ближнему пригороду чаще всего успеваем в день заказа, в дальние города планируем на ближайшие дни. Материал и доставка считаются отдельно: доставка 95 ₽ за километр, рейс туда и обратно, поэтому чем больше объём в кузове, тем дешевле выходит куб. Точную цену называем сразу по заявке, оплата после выгрузки.",
    ]
    faq = [
        ("Какие города вы обслуживаете?", "Екатеринбург и ближняя область, примерно до 100 км от города: Берёзовский, Верхняя Пышма, Среднеуральск, Арамиль, Верхнее Дуброво, Белоярский, Заречный, Сысерть, Первоуральск, Ревда, Дегтярск, Полевской, а из дальних, Каменск-Уральский и Нижний Тагил. По городу и ближнему пригороду чаще всего успеваем в день заказа, в дальние города планируем доставку на ближайшие дни. Дальше по области доставку не берём: плечо съедает смысл заказа."),
        ("В каком объёме возите?", "Только навалом, самосвалом, от трёх кубов. Самосвал 5 т берёт 3-7 кубов, КамАЗ от 10 и выше. Мешками и меньшим объёмом не возим: поставщика по фасовке у нас нет, а рейс под полкуба не окупается. Подскажем, какая машина пройдёт к вашему участку."),
        ("Как узнать цену?", "Назовите продукт, объём и адрес в заявке или в мессенджере, назовём цену материала за куб и стоимость рейса отдельными цифрами. Прикинуть можно и самому калькулятором на этой странице. Скрытых доплат нет."),
        ('Работаете с юридическими лицами?', 'Да, возим и частникам, и организациям. Физлица рассчитываются наличными, картой или переводом после выгрузки. Для организаций работаем по безналичному расчёту: договор, счёт и закрывающие документы оформляем через партнёрскую организацию. Скажите при заявке, что нужен безнал, и мы пришлём счёт.'),
        ("Чем плодородный грунт отличается от чернозёма?", "Чернозём питательнее, но плотнее: под поливом он заплывает и берётся коркой. Плодородный грунт, это смесь, в которой к питанию добавлена рыхлость, поэтому под газон, теплицу и короба чаще берут именно его. Чернозём хорош как основа, которую разбавляют торфом и песком."),
        ("Сколько грунта нужно на сотку?", "Куб на сотку даёт слой в один сантиметр. На слой 10 сантиметров нужно 10 кубов, на 20 сантиметров, двадцать. К расчёту добавьте примерно пятую часть на усадку. Посчитать можно калькулятором на этой странице."),
        ("Какой минимальный заказ?", "Три кубометра, это кузов малого самосвала. Меньше не возим: машина всё равно выезжает, грузится и проезжает то же расстояние, и рейс под полкуба не окупается ни нам, ни вам. Если нужно совсем немного, в садовых товариществах обычно скидываются с соседями на одну машину и делят её на несколько участков."),
        ("Сколько стоит доставка?", "95 рублей за километр, рейс считается туда и обратно от базы в Верхней Пышме. До Екатеринбурга это около 15 км, до Берёзовского 25, до Сысерти 65, до Каменска-Уральского 110. Цифра не зависит от загрузки кузова, поэтому на большом объёме доставка в пересчёте на куб выходит заметно дешевле. Посчитать под свой адрес можно калькулятором выше."),
        ("Можно ли поднять участок плодородным грунтом?", "Плодородный слой в основание насыпи не кладут, он просядет и закиснет. Подъём делают слоями: снизу песок или ПГС на объём, сверху 10-20 сантиметров плодородного грунта. Нерудные материалы для нижнего слоя мы не возим."),
        ("Когда лучше заказывать?", "Пик приходится на апрель-май и на конец лета, в это время машины расписаны на несколько дней вперёд. Если нужна конкретная дата, скажите заранее. Зимой и ранней весной возим быстрее."),
    ]
    org = {
        "@type": "Organization",
        "@id": SITE["domain"] + "/dostavka-grunta/#org",
        "name": SITE["brand"],
        "url": SITE["domain"] + "/dostavka-grunta/",
        "email": SITE["contact_email"],
        "areaServed": SITE["region"],
    }
    catalog_list = {
        "@type": "ItemList",
        "name": "Материалы с доставкой",
        "numberOfItems": len(PRODBAR),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": p["name"],
             "url": SITE["domain"] + p["url"]}
            for i, p in enumerate(PRODBAR)
        ],
    }
    schema = json.dumps({"@context": "https://schema.org", "@graph": [org, catalog_list,
        build_localbusiness(),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": canonical}]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
    ]}, ensure_ascii=False, separators=(",", ":"))
    html = env.get_template("hub.html").render(
        site=SITE, canonical=canonical, robots="index, follow",
        title="Доставка грунта по Екатеринбургу — чернозём от 850 ₽/м³",
        description="Доставка чернозёма, перегноя и навоза по Екатеринбургу и Свердловской области. Минимальный заказ 3 м³, возим навалом самосвалом. Доставка 95 ₽/км из Верхней Пышмы.",
        h1="Доставка грунта, перегноя и навоза по Екатеринбургу",
        hero_sub="Чернозём, перегной и навоз с доставкой по городу и области, в день заказа. Возим навалом, минимальный заказ 3 м³. Скажите объём и адрес, назовём цену материала и рейса.",
        catalog=catalog, geo=geo, faq=faq, articles=hub_articles, about=about,
        calc_materials=CALC_MATERIALS, calc_preselect="chernozem",
        calc_cities=CALC_CITIES, calc_city="ekaterinburg", calc_km=CITIES["ekaterinburg"]["base_km"],
        delivery_min=delivery_min_rub("ekaterinburg"),
        bag_note=bag_note("chernozem"),
        preselect_product="Пока не решил",
        district_ph="Напр. Академический, Верхняя Пышма, Сысерть",
        footer_links=FOOTER_LINKS, schema_json=schema, metrika_placeholder=True, related=[],
        hero_photo=("yard" if "yard" in PHOTOS else None),
        prodbar=PRODBAR, current_slug="", photos=PHOTOS)
    outdir = os.path.join(ROOT, "dostavka-grunta")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
        check_repeats(html, canonical)
    return canonical



# Обложки статей: берём уже загруженные фотографии по теме, отдельная
# съёмка под каждую статью не нужна. Ключ — слуг статьи.
ARTICLE_COVER = {
    "kak-primenyat-konskiy-navoz":   "hero-navoz-konskiy",
    "konskiy-navoz-dlya-klubniki":   "hero-navoz-konskiy",
    "kak-primenyat-koroviy-navoz":   "hero-navoz-koroviy",
    "kakoy-navoz-luchshe":           "hero-navoz",
    "kogda-vnosit-navoz":            "hero-navoz",
    "granulirovannyy-navoz":         "hero-navoz",
    "nastoy-iz-navoza":              "hero-navoz-koroviy",
    "kuriny-pomet-kak-udobrenie":    "hero-navoz",
    "navoz-ili-peregnoy-chto-luchshe":"hero-peregnoy",
    "skolko-stoit-peregnoy":         "loading",
    "skolko-stoit-navoz":            "loading",
    "skolko-stoit-chernozem":        "loading",
    "chernozem-ili-plodorodnyy-grunt":"hero-chernozem",
    "kakoy-grunt-nuzhen-dlya-teplicy":"hero-plodorodnyy-grunt",
}

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
        # Раньше брали первые шесть по порядку списка, и ссылки доставались
        # одним и тем же статьям: шесть штук собирали по 14 входящих, а семь
        # получали одну, только из хаба. Перемешиваем детерминированно.
        related.sort(key=lambda r: stable_hash(a["slug"] + r["url"]))
        a["_related"] = related[:6]
    for a in ARTICLES:
        canonical = f'{SITE["domain"]}/{base}/{a["slug"]}/'
        cover_key = (lambda c: c if c in PHOTOS else None)(ARTICLE_COVER.get(a["slug"]))
        schema = json.dumps({"@context": "https://schema.org", "@graph": [
            article_node(a, canonical, cover_key),
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
                {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": SITE["domain"] + "/dostavka-grunta/"},
                {"@type": "ListItem", "position": 3, "name": a["short"], "item": canonical}]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]},
        ]}, ensure_ascii=False, separators=(",", ":"))
        html = env.get_template("article.html").render(
            site=SITE, canonical=canonical, robots="index, follow",
            title=a["title"], description=a["description"], h1=a["h1"], short=a["short"],
            lede=a["lede"], body=a["body"], faq=a["faq"], cta=a["cta"],
            related=a["_related"], footer_links=FOOTER_LINKS,
            cta_price=PRICE_BY_URL.get(a["cta"]["url"]),
            # Блок «переход к соседней статье» был только у блога, хотя
            # шаблон общий. Он нужен там, где две статьи стоят рядом по
            # теме и их надо развести, чтобы они не тянули один запрос.
            crosslink=a.get("crosslink"),
            preselect_product="Пока не решил", district_ph="Напр. Академический, Верхняя Пышма",
            schema_json=schema, metrika_placeholder=True, og_type="article",
            prodbar=PRODBAR, current_slug="", photos=PHOTOS,
            calc_materials=CALC_MATERIALS, calc_preselect="chernozem",
            calc_cities=CALC_CITIES, calc_city="ekaterinburg", calc_km=CITIES["ekaterinburg"]["base_km"],
            delivery_min=delivery_min_rub("ekaterinburg"), bag_note=bag_note("chernozem"),
            cover=(lambda c: c if c in PHOTOS else None)(ARTICLE_COVER.get(a["slug"])),
            hero_photo=(lambda c: c if c in PHOTOS else None)(ARTICLE_COVER.get(a["slug"])))
        outdir = os.path.join(ROOT, base, a["slug"])
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
            check_repeats(html, canonical)
        urls.append(canonical)
    return urls

def render_blog():
    """Блог под /dostavka-grunta/blog/: хаб плюс посты /dostavka-grunta/blog/<slug>/.

    Корневой /blog/ занят блогом сайта про теплицы, поэтому наш раздел живёт
    внутри /dostavka-grunta/.

    Статьи из articles.py остаются на своих URL под /dostavka-grunta/, у них
    уже есть позиции, переезд их обнулит. Блог, это отдельная ветка под
    информационные запросы, связаны разделы перекрёстными ссылками.
    """
    urls = []
    posts_nav = [{"url": f'/dostavka-grunta/blog/{p["slug"]}/', "text": p["short"]} for p in BLOG]
    art_nav = [{"url": f'/dostavka-grunta/{a["slug"]}/', "text": a["short"]} for a in ARTICLES]

    hub_canonical = f'{SITE["domain"]}/dostavka-grunta/blog/'
    hub_schema = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "Blog", "name": "Блог о грунте и органике", "url": hub_canonical,
         "inLanguage": "ru-RU",
         "publisher": {"@type": "Organization", "name": SITE["brand"], "url": SITE["domain"] + "/dostavka-grunta/"}},
        {"@type": "ItemList", "numberOfItems": len(BLOG) + len(ARTICLES),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["text"],
                              "url": SITE["domain"] + x["url"]}
                             for i, x in enumerate(posts_nav + art_nav)]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": SITE["domain"] + "/dostavka-grunta/"},
            {"@type": "ListItem", "position": 3, "name": "Блог", "item": hub_canonical}]},
    ]}, ensure_ascii=False, separators=(",", ":"))
    html = env.get_template("blog_index.html").render(
        site=SITE, canonical=hub_canonical, robots="index, follow",
        title="Блог: расчёт объёмов грунта, вес куба, доставка",
        description="Справочник по грунту и органике: сколько весит куб земли, чернозёма и торфа, сколько кубов в КамАЗе, как посчитать объём на сотку и на грядку.",
        h1="Блог о грунте, органике и расчёте объёмов",
        lede="Собрали здесь то, что спрашивают до заказа: сколько весит кубометр каждого материала, "
             "как перевести кубы в тонны, сколько входит в машину и сколько нужно на сотку. "
             "Всё с таблицами и готовыми примерами расчёта.",
        posts=posts_nav, articles=art_nav, footer_links=FOOTER_LINKS,
        calc_materials=CALC_MATERIALS, calc_preselect="chernozem",
        calc_cities=CALC_CITIES, calc_city="ekaterinburg", calc_km=CITIES["ekaterinburg"]["base_km"],
        delivery_min=delivery_min_rub("ekaterinburg"), bag_note=bag_note("chernozem"),
        preselect_product="Пока не решил", district_ph="Напр. Академический, Верхняя Пышма",
        schema_json=hub_schema, metrika_placeholder=True, related=[],
        prodbar=PRODBAR, current_slug="", photos=PHOTOS, hero_photo=None)
    outdir = os.path.join(ROOT, "dostavka-grunta", "blog")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
        check_repeats(html, hub_canonical)
    urls.append(hub_canonical)

    for p in BLOG:
        canonical = f'{SITE["domain"]}/dostavka-grunta/blog/{p["slug"]}/'
        # Родственное: остальные посты блога плюс статьи по применению,
        # чтобы информационный трафик уходил в сторону товарных страниц.
        related = [x for x in posts_nav if x["url"] != f'/dostavka-grunta/blog/{p["slug"]}/']
        pool = list(art_nav)
        pool.sort(key=lambda r: stable_hash(p["slug"] + r["url"]))
        related += pool[: max(0, 6 - len(related))]
        schema = json.dumps({"@context": "https://schema.org", "@graph": [
            dict(article_node(p, canonical, None, kind="BlogPosting"),
                 isPartOf={"@type": "Blog", "name": "Блог о грунте и органике", "url": hub_canonical}),
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE["domain"] + "/"},
                {"@type": "ListItem", "position": 2, "name": "Доставка грунта", "item": SITE["domain"] + "/dostavka-grunta/"},
                {"@type": "ListItem", "position": 3, "name": "Блог", "item": hub_canonical},
                {"@type": "ListItem", "position": 4, "name": p["short"], "item": canonical}]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
        ]}, ensure_ascii=False, separators=(",", ":"))
        html = env.get_template("article.html").render(
            site=SITE, canonical=canonical, robots="index, follow",
            section_url="/dostavka-grunta/blog/", section_name="Блог",
            title=p["title"], description=p["description"], h1=p["h1"], short=p["short"],
            lede=p["lede"], body=p["body"], faq=p["faq"], cta=p["cta"],
            related=related, footer_links=FOOTER_LINKS, cta_price=None,
            preselect_product="Пока не решил", district_ph="Напр. Академический, Верхняя Пышма",
            schema_json=schema, metrika_placeholder=True, og_type="article",
            crosslink=p.get("crosslink"),
            calc_materials=CALC_MATERIALS, calc_preselect="chernozem",
            calc_cities=CALC_CITIES, calc_city="ekaterinburg", calc_km=CITIES["ekaterinburg"]["base_km"],
            delivery_min=delivery_min_rub("ekaterinburg"), bag_note=bag_note("chernozem"),
            prodbar=PRODBAR, current_slug="", photos=PHOTOS, cover=None, hero_photo=None)
        outdir = os.path.join(ROOT, "dostavka-grunta", "blog", p["slug"])
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
            check_repeats(html, canonical)
        urls.append(canonical)
    return urls


def render_privacy():
    """Политика обработки данных для раздела доставки грунта.

    Политика основного сайта (/politika-konfidentsialnosti.html) утверждает,
    что сайт статический и форм не имеет. Для этого раздела это неверно:
    здесь три формы собирают имя, телефон и комментарий, поэтому раздел
    ссылается на собственную политику.
    """
    canonical = f'{SITE["domain"]}/dostavka-grunta/politika/'
    body = [
      {"h": "Кто обрабатывает данные",
       "p": [f'Оператором обработки является владелец сайта {SITE["domain"]}, раздел доставки грунта и органики по региону «{SITE["region"]}». '
             f'Связаться по любым вопросам об обработке данных можно по адресу {SITE["contact_email"]}.',
             'Политика распространяется на страницы раздела доставки грунта и на формы, размещённые на них.']},
      {"h": "Какие данные мы собираем",
       "p": ['На страницах раздела есть формы заявки. Данные в них вы вводите добровольно, и передаются только те поля, которые вы заполнили:'],
       "list": ['номер телефона, обязательное поле, нужен чтобы ответить на заявку;',
                'имя или обращение, если вы его указали;',
                'район или город доставки, выбранный материал, объём и желаемый срок;',
                'комментарий, если вы его написали;',
                'служебные сведения: адрес страницы, с которой отправлена заявка, источник перехода и время отправки.'],
       },
      {"h": "Зачем мы их собираем",
       "p": ['Единственная цель, ответить на ваше обращение: рассчитать стоимость, согласовать объём, срок и адрес доставки. '
             'Мы не используем контакты для рассылок и не передаём их третьим лицам для рекламы.',
             'Правовое основание, ваше согласие, которое вы даёте отметкой в форме перед отправкой (пункт 1 части 1 статьи 6 Федерального закона № 152-ФЗ «О персональных данных»).']},
      {"h": "Кому данные передаются",
       "p": ['Заявка с формы отправляется через сервис доставки писем Web3Forms, который пересылает её на нашу электронную почту. '
             'Сервис работает на зарубежных серверах, то есть при отправке заявки происходит трансграничная передача данных. '
             'Отправляя форму, вы соглашаетесь в том числе с этим.',
             'Если вы не хотите пользоваться формой, напишите нам напрямую на почту или в мессенджер, ссылки есть на каждой странице раздела.']},
      {"h": "Обезличенная статистика и cookie",
       "p": ['На страницах установлен счётчик Яндекс.Метрики. Он собирает обезличенные данные о посещениях: страницы, время, устройство, источник перехода, '
             'и использует cookie. Эти сведения не позволяют нас идентифицировать вас лично и используются только для оценки того, какие страницы полезны посетителям.',
             'Отключить сбор можно в настройках браузера, запретив cookie, либо через официальный блокировщик Яндекс.Метрики.']},
      {"h": "Сколько храним и как защищаем",
       "p": ['Заявки хранятся в почте оператора столько, сколько нужно для обработки обращения и связанных с ним вопросов, но не дольше срока, пока сохраняется цель обработки. '
             'После этого они удаляются. Доступ к почте есть только у оператора.',
             'Мы не собираем специальные категории данных, не собираем данные несовершеннолетних намеренно и не проводим автоматизированного принятия решений на основе ваших данных.']},
      {"h": "Ваши права",
       "p": ['Вы вправе получить сведения об обработке своих данных, потребовать их уточнения, блокирования или уничтожения, а также отозвать согласие в любой момент.',
             f'Для этого напишите на {SITE["contact_email"]} с описанием требования. Мы ответим и, если требование обоснованно, исполним его в сроки, установленные законом. '
             'Если ответ вас не устроит, вы вправе обратиться в Роскомнадзор.']},
      {"h": "Изменения политики",
       "p": ['Мы можем обновлять эту политику. Действующая редакция всегда доступна по этому адресу, дата обновления указана ниже. '
             'Существенные изменения вступают в силу с момента публикации на этой странице.',
             'Редакция от 10 августа 2026 года.']},
    ]
    html = env.get_template("legal.html").render(
        site=SITE, canonical=canonical, robots="noindex, follow",
        title="Политика обработки персональных данных — доставка грунта",
        description="Как раздел доставки грунта обрабатывает данные из форм заявки: какие поля собираем, зачем, кому передаём и как отозвать согласие.",
        h1="Политика обработки персональных данных",
        short="Обработка данных",
        lede="Раздел доставки грунта собирает контакты через формы заявки, поэтому у него отдельная политика: "
             "политика основного сайта описывает статические страницы без форм и к этому разделу не подходит.",
        body=body, footer_links=FOOTER_LINKS, metrika_placeholder=True,
        prodbar=PRODBAR, current_slug="", photos=PHOTOS, related=[])
    outdir = os.path.join(ROOT, "dostavka-grunta", "politika")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
        check_repeats(html, canonical)
    return canonical


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
    article_urls += render_blog() if not only else []
    if not only:
        render_privacy()   # noindex, в карту сайта не идёт
    index_urls = [u for (sl, u, idx) in done if idx]
    if hub_url: index_urls.insert(0, hub_url)
    index_urls += article_urls
    for slug, url, idx in done:
        print(("index " if idx else "NOIDX "), slug, "->", url)
    print(f"Готово: {len(done)} страниц, в индекс: {len(index_urls)}")
    # список индексируемых URL для sitemap (Фаза 4)
    with open(os.path.join(HERE, "index_urls.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(index_urls))
